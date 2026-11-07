"""Flow-Lenia: a mass-conserving continuous cellular automaton (Plantec et al. 2022/2023,
arXiv 2212.07906), single channel, reimplemented from the paper's equations.

Matter A >= 0 is never created or destroyed; it is moved along a flow field.

Per step (torus, FFT convolution, NumPy + SciPy):
    U     = sum_i h_i G_i(K_i * A)          affinity; G(x) = 2 exp(-(x - mu)^2 / (2 sigma^2)) - 1
    F     = (1 - alpha) grad U - alpha grad A,   alpha = clip((A / theta_A)^n, 0, 1), n = 2, theta_A = 1
    A'    = reintegration tracking of A along F (dt = 0.2, s = 0.65, dd = 5)

Kernels are rings: K_i(r) = sum_j b_ij exp(-((r / (r_i R)) - a_ij)^2 / (2 w_ij^2)) for
r < r_i R, normalised to sum 1. Gradients are 3x3 Sobel filters with wrap-around, used
unnormalised (weights 1-2-1 / -1-0-1), as in the paper's description of the flow.

Reintegration tracking: the mass of cell p moves to a square of side 2s centred at
p + clip(dt F(p), -(dd - s), dd - s); each cell receives that mass times the overlap
area / (2s)^2. The overlaps of one square sum exactly to (2s)^2, so float mass is
conserved to rounding precision.

Storage (D-026): float32 states in physical units (dtype = np.float32). Each step is
computed in float64 and stored as float32, so mass is conserved to float32 rounding.
An earlier uint8 version (largest-remainder rounding, exact integer mass) was dropped:
rounding friction removed every flow below about half a level per step, so slow dynamics
froze (pure diffusion of the paper's patch stopped spreading after < 50 steps).
`view` quantizes A to uint8 on [0, DISPLAY_MAX] for the observer's frame measures and the
dashboard only; the structure census uses the float state.

Rule label (one or more kernels joined by '+'):
    FLENIA/R13/m0.150/s0.0150/h1/r1/a0.5/b1/w0.15
    m mu, s sigma, h weight, r relative radius, a/b/w ring centres/heights/widths
    (comma-separated, one value per ring). R is fixed at 13 for constant cost.
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np

from .base import Physics, register

DISPLAY_MAX = 2.0     # A shown as level 255 in the uint8 view (display and frame measures only)
THETA_A, N_ALPHA = 1.0, 2.0
DT, S_SPREAD, DD = 0.2, 0.65, 5

_KERNEL = re.compile(r"^m([\d.]+)/s([\d.]+)/h([\d.]+)/r([\d.]+)/a([\d.,]+)/b([\d.,]+)/w([\d.,]+)$")


def _floats(s: str) -> tuple[float, ...]:
    return tuple(float(x) for x in s.split(",") if x)


class Kernel:
    """One ring kernel with its growth function."""

    __slots__ = ("mu", "sigma", "h", "r", "a", "b", "w")

    def __init__(self, mu, sigma, h=1.0, r=1.0, a=(0.5,), b=(1.0,), w=(0.15,)):
        self.mu, self.sigma = round(float(mu), 3), round(float(sigma), 4)
        self.h, self.r = round(float(h), 2), round(float(r), 2)
        self.a = tuple(round(float(x), 2) for x in a)
        self.b = tuple(round(float(x), 2) for x in b)
        self.w = tuple(round(float(x), 3) for x in w)
        if not (len(self.a) == len(self.b) == len(self.w) >= 1):
            raise ValueError("a, b, w must have one value per ring")
        if not (self.sigma > 0 and self.h > 0 and 0 < self.r <= 1 and min(self.w) > 0 and max(self.b) > 0):
            raise ValueError("invalid Flow-Lenia kernel parameters")

    def label(self) -> str:
        j = lambda xs: ",".join(f"{x:g}" for x in xs)  # noqa: E731
        return (f"m{self.mu:.3f}/s{self.sigma:.4f}/h{self.h:g}/r{self.r:g}"
                f"/a{j(self.a)}/b{j(self.b)}/w{j(self.w)}")

    @classmethod
    def parse(cls, s: str) -> "Kernel":
        m = _KERNEL.match(s)
        if not m:
            raise ValueError(f"cannot parse Flow-Lenia kernel {s!r}")
        mu, sg, h, r, a, b, w = m.groups()
        return cls(float(mu), float(sg), float(h), float(r), _floats(a), _floats(b), _floats(w))

    def fft(self, shape: tuple[int, int], R: int) -> np.ndarray:
        hh, ww = shape
        y = np.minimum(np.arange(hh), hh - np.arange(hh))[:, None]
        x = np.minimum(np.arange(ww), ww - np.arange(ww))[None, :]
        d = np.sqrt(y * y + x * x)
        rr = d / (self.r * R)
        k = sum(b * np.exp(-((rr - a) ** 2) / (2 * w * w)) for a, b, w in zip(self.a, self.b, self.w))
        k = np.where(rr < 1, k, 0.0)
        k /= k.sum()
        return np.fft.rfft2(k)


def sobel(f: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Unnormalised 3x3 Sobel gradient (d/dy, d/dx) on the torus."""
    from scipy import ndimage
    return ndimage.sobel(f, axis=0, mode="wrap"), ndimage.sobel(f, axis=1, mode="wrap")


def reintegrate(A: np.ndarray, dy: np.ndarray, dx: np.ndarray, s: float = S_SPREAD) -> np.ndarray:
    """Reintegration tracking on the torus: the mass of each cell p lands on a square of side
    2s centred at p + (dy, dx); every cell receives mass x overlap area / (2s)^2."""
    reach = int(np.ceil(max(np.abs(dy).max(), np.abs(dx).max()) + s + 0.5))
    out = np.zeros_like(A)
    norm = 1.0 / (4 * s * s)

    def overlap(rel):  # length of [rel - s, rel + s] inside [-0.5, 0.5]
        return np.clip(np.minimum(0.5, rel + s) - np.maximum(-0.5, rel - s), 0.0, None)

    wy = {o: overlap(dy - o) for o in range(-reach, reach + 1)}
    wx = {o: overlap(dx - o) for o in range(-reach, reach + 1)}
    for oy in range(-reach, reach + 1):
        my = A * wy[oy]
        if not my.any():
            continue
        for ox in range(-reach, reach + 1):
            m = my * wx[ox]
            if m.any():
                out += np.roll(m, (oy, ox), axis=(0, 1))  # source p sends to p + (oy, ox)
    return out * norm


@register
class FlowLenia(Physics):
    kind = "flow_lenia"
    num_states = 256      # of the uint8 view
    dtype = np.float32
    continuous = True  # observatory: tolerant structure detector and continuous label rules

    def __init__(self, kernels: list[Kernel] | tuple[Kernel, ...], R: int = 13, diffusion_only: bool = False):
        self.R = int(R)
        self.kernels = tuple(kernels)
        # deceptive control: U = 0, the flow is only -alpha grad A (spreading)
        self.diffusion_only = bool(diffusion_only)
        if not (2 <= self.R <= 40 and 1 <= len(self.kernels) <= 10):
            raise ValueError("invalid Flow-Lenia parameters")
        self._kf: dict[tuple[int, int], list[np.ndarray]] = {}

    def _kernels(self, shape):
        if shape not in self._kf:
            self._kf[shape] = [k.fft(shape, self.R) for k in self.kernels]
        return self._kf[shape]

    # ------------------------------------------------------------------ dynamics
    def affinity(self, A: np.ndarray) -> np.ndarray:
        if self.diffusion_only:
            return np.zeros_like(A)
        fa = np.fft.rfft2(A)
        U = np.zeros_like(A)
        for k, kf in zip(self.kernels, self._kernels(A.shape)):
            u = np.fft.irfft2(fa * kf, s=A.shape)
            U += k.h * (2.0 * np.exp(-((u - k.mu) ** 2) / (2 * k.sigma ** 2)) - 1.0)
        return U

    def flow(self, A: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        U = self.affinity(A)
        gUy, gUx = sobel(U)
        gAy, gAx = sobel(A)
        alpha = np.clip((A / THETA_A) ** N_ALPHA, 0.0, 1.0)
        return (1 - alpha) * gUy - alpha * gAy, (1 - alpha) * gUx - alpha * gAx

    def step_float(self, A: np.ndarray) -> np.ndarray:
        """One step on a float field (no quantization); conserves A.sum() to rounding."""
        Fy, Fx = self.flow(A)
        lim = DD - S_SPREAD
        return reintegrate(A, np.clip(DT * Fy, -lim, lim), np.clip(DT * Fx, -lim, lim))

    def step(self, state: np.ndarray) -> np.ndarray:
        return self.step_float(state.astype(np.float64)).astype(np.float32)

    def view(self, state: np.ndarray) -> np.ndarray:
        if state.dtype == np.uint8:
            return state
        return np.rint(np.clip(state / DISPLAY_MAX, 0.0, 1.0) * 255).astype(np.uint8)

    def from_levels(self, levels: np.ndarray) -> np.ndarray:
        """uint8 initial conditions (0..255) -> A in [0, 1], the paper's range of initial matter."""
        return (levels.astype(np.float64) / 255.0).astype(np.float32)

    def random_state(self, rng: np.random.Generator, shape: tuple[int, int], density: float) -> np.ndarray:
        """Soup: each cell is occupied with probability `density`, A uniform in [0, 1]."""
        occ = rng.random(shape) < density
        return np.where(occ, rng.random(shape), 0.0).astype(np.float32)

    @staticmethod
    def patch_state(rng: np.random.Generator, shape: tuple[int, int], side: int = 40) -> np.ndarray:
        """The paper's initial condition: a central side x side patch of uniform random
        matter A ~ U[0, 1]; vacuum elsewhere."""
        s = np.zeros(shape, np.float32)
        r0, c0 = (shape[0] - side) // 2, (shape[1] - side) // 2
        s[r0:r0 + side, c0:c0 + side] = rng.random((side, side))
        return s

    # ------------------------------------------------------------- serialisation
    def label(self) -> str:
        if self.diffusion_only:
            return f"FLENIA/R{self.R}/diffusion"
        return f"FLENIA/R{self.R}/" + "+".join(k.label() for k in self.kernels)

    @classmethod
    def parse(cls, rule: str) -> "FlowLenia":
        r = rule.strip()
        m = re.match(r"^FLENIA/R(\d+)/(.+)$", r, re.IGNORECASE)
        if not m:
            raise ValueError(f"cannot parse Flow-Lenia rule {rule!r}; expected e.g. "
                             "FLENIA/R13/m0.150/s0.0150/h1/r1/a0.5/b1/w0.15")
        R, body = int(m.group(1)), m.group(2)
        if body.lower() == "diffusion":
            return cls([Kernel(0.15, 0.015)], R, diffusion_only=True)
        return cls([Kernel.parse(k) for k in body.split("+")], R)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.label()}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FlowLenia":
        return cls.parse(d["rule"])

    # --------------------------------------------------------------- exploration
    # Ranges follow the paper's random-parameter sampling (mu in [0.05, 0.5], sigma in
    # [0.001, 0.2], h in [0.01, 1], r in [0.2, 1], ring a in [0, 1], b in [0.001, 1],
    # w in [0.01, 0.5], 3 rings per kernel), with R fixed at 13 and 1-3 kernels so the
    # label stays readable and the cost constant.
    @staticmethod
    def _random_kernel(rng: np.random.Generator) -> Kernel:
        return Kernel(rng.uniform(0.05, 0.5), rng.uniform(0.001, 0.2), rng.uniform(0.01, 1.0),
                      rng.uniform(0.2, 1.0), rng.uniform(0, 1, 3), rng.uniform(0.001, 1, 3),
                      rng.uniform(0.01, 0.5, 3))

    @classmethod
    def random(cls, rng: np.random.Generator) -> "FlowLenia":
        return cls([cls._random_kernel(rng) for _ in range(int(rng.integers(1, 4)))], 13)

    def mutate(self, rng: np.random.Generator) -> "FlowLenia":
        """One random change to one kernel (or add / drop a kernel); always changes the label."""
        if self.diffusion_only:
            raise RuntimeError("the diffusion control has no rule parameters to mutate")
        for _ in range(100):
            ks = list(self.kernels)
            r = rng.random()
            if r < 0.08 and len(ks) < 3:
                ks.append(self._random_kernel(rng))
            elif r < 0.16 and len(ks) > 1:
                ks.pop(int(rng.integers(len(ks))))
            else:
                i = int(rng.integers(len(ks)))
                k = ks[i]
                p = dict(mu=k.mu, sigma=k.sigma, h=k.h, r=k.r, a=list(k.a), b=list(k.b), w=list(k.w))
                f = str(rng.choice(["mu", "sigma", "h", "r", "a", "b", "w"]))
                if f in ("a", "b", "w"):
                    j = int(rng.integers(len(p[f])))
                    lo, hi = {"a": (0.0, 1.0), "b": (0.001, 1.0), "w": (0.01, 0.5)}[f]
                    p[f][j] = float(np.clip(p[f][j] + rng.normal(0, 0.05 * (hi - lo)), lo, hi))
                else:
                    lo, hi = {"mu": (0.05, 0.5), "sigma": (0.001, 0.2), "h": (0.01, 1.0), "r": (0.2, 1.0)}[f]
                    p[f] = float(np.clip(p[f] * rng.normal(1, 0.08), lo, hi))
                try:
                    ks[i] = Kernel(**p)
                except ValueError:
                    continue
            child = FlowLenia(ks, self.R)
            if child.label() != self.label():
                return child
        raise RuntimeError(f"could not mutate {self.label()}")

    def rule_features(self) -> dict[str, float]:
        hs = np.array([k.h for k in self.kernels])
        return {"kernels": float(len(self.kernels)),
                "mu": float(np.average([k.mu for k in self.kernels], weights=hs)),
                "sigma": float(np.average([k.sigma for k in self.kernels], weights=hs)),
                "radius": float(np.average([k.r for k in self.kernels], weights=hs))}
