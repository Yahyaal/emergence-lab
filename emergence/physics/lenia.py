"""Lenia: a continuous-state cellular automaton (Chan 2019), quantized to 256 levels.

Each cell holds a value A in [0, 1], stored as uint8 (A = state / 255) so the rest of
the system (hashing, compression, storage, dashboard, clones) works unchanged. This is
Lenia "with P = 255 discrete states", a variant described in the Lenia papers.

Update (torus, FFT convolution):
    U      = K * A                       (K: smooth ring kernel of radius R, sum 1)
    A_next = clip(A + G(U) / T, 0, 1)    G(u) = 2 exp(-(u - mu)^2 / (2 sigma^2)) - 1

Kernel: radius r in [0, 1) (distance / R) is split into len(peaks) concentric rings;
ring i has height peaks[i] and the exponential bump shape core(x) = exp(4 - 1/(x(1-x))).

Rule label: LENIA/R13/T10/m0.150/s0.0150/b1  (b = ring heights, comma-separated)
Reference parameters: mu=0.15, sigma=0.015, R=13, T=10, b=[1] are those of the
well-known glider "Orbium" (Chan 2019).
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np

from .base import Physics, register

_LABEL = re.compile(r"^LENIA/R(\d+)/T(\d+)/m([\d.]+)/s([\d.]+)/b([\d.,/]+)$", re.IGNORECASE)


def kernel_fft(shape: tuple[int, int], R: int, peaks: tuple[float, ...]) -> np.ndarray:
    h, w = shape
    y = np.minimum(np.arange(h), h - np.arange(h))[:, None]
    x = np.minimum(np.arange(w), w - np.arange(w))[None, :]
    r = np.sqrt(y * y + x * x) / R
    B = len(peaks)
    br = r * B
    idx = np.minimum(br.astype(int), B - 1)
    frac = br - np.floor(br)
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        core = np.where((frac > 0) & (frac < 1), np.exp(4 - 1 / (frac * (1 - frac))), 0.0)
    k = np.where(r < 1, np.asarray(peaks)[idx] * core, 0.0)
    k /= k.sum()
    return np.fft.rfft2(k)


@register
class Lenia(Physics):
    kind = "lenia"
    num_states = 256
    continuous = True  # observatory: use the tolerant (continuous) structure detector

    def __init__(self, R: int = 13, T: int = 10, mu: float = 0.15, sigma: float = 0.015,
                 peaks: tuple[float, ...] | list[float] = (1.0,)):
        self.R, self.T = int(R), int(T)
        # rounded to the label's precision, so a rule and its stored label are the same rule
        self.mu, self.sigma = round(float(mu), 3), round(float(sigma), 4)
        self.peaks = tuple(round(float(p), 3) for p in peaks)
        if not (2 <= self.R <= 40 and 1 <= self.T <= 100 and self.sigma > 0 and self.peaks):
            raise ValueError("invalid Lenia parameters")
        self._kf: dict[tuple[int, int], np.ndarray] = {}

    def _kernel(self, shape):
        if shape not in self._kf:
            self._kf[shape] = kernel_fft(shape, self.R, self.peaks)
        return self._kf[shape]

    def step(self, state: np.ndarray) -> np.ndarray:
        a = state.astype(np.float64) / 255.0
        u = np.fft.irfft2(np.fft.rfft2(a) * self._kernel(state.shape), s=state.shape)
        g = 2.0 * np.exp(-((u - self.mu) ** 2) / (2 * self.sigma ** 2)) - 1.0
        a = np.clip(a + g / self.T, 0.0, 1.0)
        return np.rint(a * 255.0).astype(np.uint8)

    def random_state(self, rng: np.random.Generator, shape: tuple[int, int], density: float) -> np.ndarray:
        """Soup: each cell is occupied with probability `density`, with a uniform random value."""
        occ = rng.random(shape) < density
        vals = rng.random(shape)
        return np.where(occ, np.rint(vals * 255), 0).astype(np.uint8)

    # --------------------------------------------------------------- serialisation
    def label(self) -> str:
        b = ",".join(f"{p:g}" for p in self.peaks)
        return f"LENIA/R{self.R}/T{self.T}/m{self.mu:.3f}/s{self.sigma:.4f}/b{b}"

    @classmethod
    def parse(cls, rule: str) -> "Lenia":
        m = _LABEL.match(rule.strip())
        if not m:
            raise ValueError(f"cannot parse Lenia rule {rule!r}; expected e.g. LENIA/R13/T10/m0.150/s0.0150/b1")
        R, T, mu, s, b = m.groups()
        return cls(int(R), int(T), float(mu), float(s), [float(x) for x in b.replace("/", ",").split(",") if x])

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.label()}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Lenia":
        return cls.parse(d["rule"])

    # ----------------------------------------------------------------- exploration
    # R and T are kept fixed (13, 10) so cost is constant and rules are comparable;
    # mu, sigma and the ring structure are explored. Ranges follow the region of
    # parameter space where Lenia's documented life-forms live (mu ~ 0.1-0.4,
    # sigma a small fraction of mu).
    @classmethod
    def random(cls, rng: np.random.Generator) -> "Lenia":
        mu = float(rng.uniform(0.08, 0.40))
        sigma = float(mu * rng.uniform(0.05, 0.30))
        n = int(rng.choice([1, 1, 2, 3]))
        peaks = [1.0] if n == 1 else [float(rng.choice([0.25, 0.5, 0.75, 1.0])) for _ in range(n)]
        if max(peaks) < 1.0:
            peaks[int(rng.integers(n))] = 1.0
        return cls(13, 10, mu, sigma, peaks)

    def mutate(self, rng: np.random.Generator) -> "Lenia":
        """One random change; always returns a different rule (label). Redraws when a
        small change rounds back to the same label."""
        for _ in range(100):
            mu, sigma, peaks = self.mu, self.sigma, list(self.peaks)
            r = rng.random()
            if r < 0.4:
                mu = float(np.clip(mu * rng.normal(1, 0.06), 0.03, 0.6))
            elif r < 0.8:
                sigma = float(np.clip(sigma * rng.normal(1, 0.12), 0.002, 0.2))
            elif len(peaks) == 1 or (len(peaks) < 3 and rng.random() < 0.5):
                peaks.append(float(rng.choice([0.25, 0.5, 0.75, 1.0])))
            else:
                peaks.pop(int(rng.integers(len(peaks))))
                if max(peaks) < 1.0:
                    peaks[0] = 1.0
            child = Lenia(self.R, self.T, mu, sigma, peaks)
            if child.label() != self.label():
                return child
        raise RuntimeError(f"could not mutate {self.label()}")

    def rule_features(self) -> dict[str, float]:
        return {"mu": self.mu, "sigma": self.sigma, "rings": float(len(self.peaks))}
