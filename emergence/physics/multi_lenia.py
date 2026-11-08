"""Multi-channel Lenia (Chan 2020, "Lenia and Expanded Universe"), float32 states.

C channels A_0..A_{C-1}, each in [0, 1]. Each kernel k reads one source channel and writes to
one target channel:

    U_k = K_k * A_{src(k)}                       (ring kernel of radius round(R r_k), sum 1)
    A_c <- clip(A_c + (1/T) sum_{k: tgt(k)=c} h_k G_k(U_k) / sum_{k: tgt(k)=c} h_k, 0, 1)
    G_k(u) = 2 exp(-(u - mu_k)^2 / (2 sigma_k^2)) - 1

Dividing by the summed weights keeps each channel's growth in [-1, 1], as in single-channel
Lenia; with one channel and one kernel (r = 1, h = 1) this IS Lenia, in float instead of 256
levels. Chan reported self-replicating creatures in multi-channel, multi-kernel Lenia; this
physics exists to test whether the lack of reproduction in our single-channel scans (E-27 to
E-29) is a limit of the single channel.

State: float32 array (C, h, w); vacuum = 0. ``view`` is the largest channel value as uint8
(objects are found where ANY channel has matter). Like Gray-Scott, only the birth detector and
scripts use it; the discovery engine assumes 2D states.

Rule label: MLENIA/C2/R13/T10/k0>0,r1,m0.150,s0.0150,h1,b1+k1>0,r0.7,m0.200,s0.0300,h0.5,b1,0.5
(k<src>><tgt>, then r, m, s, h and the ring heights b).
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np

from .base import Physics, register
from .lenia import kernel_fft

_HEAD = re.compile(r"^MLENIA/C(\d+)/R(\d+)/T(\d+)/(.+)$", re.IGNORECASE)
_KER = re.compile(r"^k(\d+)>(\d+),r([\d.]+),m([\d.]+),s([\d.]+),h([\d.]+),b([\d.,]+)$", re.IGNORECASE)


class MKernel:
    def __init__(self, src: int, tgt: int, r: float, mu: float, sigma: float, h: float, peaks):
        self.src, self.tgt = int(src), int(tgt)
        self.r, self.mu, self.sigma, self.h = round(float(r), 2), round(float(mu), 3), round(float(sigma), 4), round(float(h), 2)
        self.peaks = tuple(round(float(p), 3) for p in peaks)
        if not (0.2 <= self.r <= 1 and self.sigma > 0 and self.h > 0 and self.peaks and max(self.peaks) > 0):
            raise ValueError("invalid multi-channel Lenia kernel")

    def label(self) -> str:
        b = ",".join(f"{p:g}" for p in self.peaks)
        return f"k{self.src}>{self.tgt},r{self.r:g},m{self.mu:.3f},s{self.sigma:.4f},h{self.h:g},b{b}"


@register
class MultiLenia(Physics):
    kind = "multi_lenia"
    num_states = 256
    continuous = True
    dtype = np.float32

    def __init__(self, C: int, kernels, R: int = 13, T: int = 10):
        self.C, self.R, self.T = int(C), int(R), int(T)
        self.kernels = tuple(kernels)
        if not (1 <= self.C <= 4 and 2 <= self.R <= 40 and 1 <= self.T <= 100 and self.kernels):
            raise ValueError("invalid multi-channel Lenia parameters")
        if any(not (0 <= k.src < self.C and 0 <= k.tgt < self.C) for k in self.kernels):
            raise ValueError("kernel channel out of range")
        if {k.tgt for k in self.kernels} != set(range(self.C)):
            raise ValueError("every channel needs at least one kernel writing to it")
        self._hsum = np.array([sum(k.h for k in self.kernels if k.tgt == c) for c in range(self.C)])
        self._kf: dict[tuple[int, int], list[np.ndarray]] = {}

    def _kernels(self, shape):
        if shape not in self._kf:
            self._kf[shape] = [kernel_fft(shape, max(2, int(round(self.R * k.r))), k.peaks) for k in self.kernels]
        return self._kf[shape]

    def step(self, state: np.ndarray) -> np.ndarray:
        a = state.astype(np.float64)
        shape = a.shape[1:]
        fa = [np.fft.rfft2(a[c]) if any(k.src == c for k in self.kernels) else None for c in range(self.C)]
        growth = np.zeros_like(a)
        for k, kf in zip(self.kernels, self._kernels(shape)):
            u = np.fft.irfft2(fa[k.src] * kf, s=shape)
            growth[k.tgt] += k.h * (2.0 * np.exp(-((u - k.mu) ** 2) / (2 * k.sigma ** 2)) - 1.0)
        a = np.clip(a + growth / self._hsum[:, None, None] / self.T, 0.0, 1.0)
        return a.astype(np.float32)

    def vacuum(self, shape: tuple[int, int]) -> np.ndarray:
        return np.zeros((self.C, *shape), np.float32)

    def view(self, state: np.ndarray) -> np.ndarray:
        return np.rint(np.clip(state.max(axis=0), 0, 1) * 255).astype(np.uint8)

    def from_levels(self, levels: np.ndarray) -> np.ndarray:
        """Every channel gets level / 255."""
        return np.repeat((levels.astype(np.float32) / 255.0)[None], self.C, axis=0)

    def random_state(self, rng: np.random.Generator, shape: tuple[int, int], density: float) -> np.ndarray:
        occ = rng.random((self.C, *shape)) < density
        return np.where(occ, rng.random((self.C, *shape)), 0).astype(np.float32)

    # --------------------------------------------------------------- serialisation
    def label(self) -> str:
        return f"MLENIA/C{self.C}/R{self.R}/T{self.T}/" + "+".join(k.label() for k in self.kernels)

    @classmethod
    def parse(cls, rule: str) -> "MultiLenia":
        m = _HEAD.match(rule.strip())
        if not m:
            raise ValueError(f"cannot parse multi-channel Lenia rule {rule!r}")
        C, R, T, body = m.groups()
        ks = []
        for part in body.split("+"):
            km = _KER.match(part)
            if not km:
                raise ValueError(f"cannot parse kernel {part!r}")
            s, t, r, mu, sg, h, b = km.groups()
            ks.append(MKernel(int(s), int(t), float(r), float(mu), float(sg), float(h), [float(x) for x in b.split(",") if x]))
        return cls(int(C), ks, int(R), int(T))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.label()}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "MultiLenia":
        return cls.parse(d["rule"])

    # ----------------------------------------------------------------- exploration
    # C in {2, 3}; one self-kernel per channel (c > c) plus 1-2*C extra kernels between random
    # channels, so channels interact. mu, sigma and rings follow Lenia.random; r ~ U[0.5, 1]
    # (Chan 2020 varies kernel radii); h ~ U[0.2, 1].
    @classmethod
    def random(cls, rng: np.random.Generator, C: int | None = None) -> "MultiLenia":
        C = int(C or rng.choice([2, 3]))
        pairs = [(c, c) for c in range(C)] + [tuple(int(x) for x in rng.integers(0, C, 2))
                                               for _ in range(int(rng.integers(1, 2 * C + 1)))]
        ks = []
        for s, t in pairs:
            mu = float(rng.uniform(0.08, 0.40))
            n = int(rng.choice([1, 1, 2, 3]))
            peaks = [1.0] if n == 1 else [float(rng.choice([0.25, 0.5, 0.75, 1.0])) for _ in range(n)]
            if max(peaks) < 1.0:
                peaks[int(rng.integers(n))] = 1.0
            ks.append(MKernel(s, t, rng.uniform(0.5, 1.0), mu, mu * rng.uniform(0.05, 0.30), rng.uniform(0.2, 1.0), peaks))
        return cls(C, ks)

    def mutate(self, rng: np.random.Generator) -> "MultiLenia":
        """One kernel's mu, sigma or h changed; always a different label."""
        for _ in range(100):
            ks = list(self.kernels)
            j = int(rng.integers(len(ks)))
            k = ks[j]
            mu, sg, h = k.mu, k.sigma, k.h
            x = rng.random()
            if x < 0.4:
                mu = float(np.clip(mu * rng.normal(1, 0.06), 0.03, 0.6))
            elif x < 0.8:
                sg = float(np.clip(sg * rng.normal(1, 0.12), 0.002, 0.2))
            else:
                h = float(np.clip(h * rng.normal(1, 0.2), 0.05, 1.0))
            ks[j] = MKernel(k.src, k.tgt, k.r, mu, sg, h, k.peaks)
            child = MultiLenia(self.C, ks, self.R, self.T)
            if child.label() != self.label():
                return child
        raise RuntimeError(f"could not mutate {self.label()}")

    def rule_features(self) -> dict[str, float]:
        return {"channels": float(self.C), "kernels": float(len(self.kernels))}
