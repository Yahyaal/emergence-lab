"""Gray-Scott reaction-diffusion (Pearson 1993), a positive control for the birth detector.

Two chemicals on a torus: U is fed in, V eats U to make more of itself (U + 2V -> 3V)
and is removed. Per step (explicit Euler, dt = 1, 5-point Laplacian, Pearson's units):

    U' = U + Du lap(U) - U V^2 + F (1 - U)
    V' = V + Dv lap(V) + U V^2 - (F + k) V

With Du = 0.16, Dv = 0.08, F = 0.0367, k = 0.0649 (the default, Pearson's "self-replicating
spots" regime) a single spot of V grows and divides in two, and its daughters divide in
turn until the world is full. Spots are identical, so this is reproduction WITHOUT
heredity: it is used to check that the birth detector sees reproduction when it happens,
not as a candidate for emergent life (the rule was chosen because it does this).

State: float32 array of shape (2, h, w), channel 0 = U, channel 1 = V. Vacuum is U = 1,
V = 0 (``vacuum``). ``view`` shows V on [0, DISPLAY_MAX] as uint8. Only the birth
detector (observatory/births.py) and simple runs use this physics; the discovery engine
and the conditions study assume 2D states and do not support it.

Rule label: GS/F0.0367/k0.0649 (Du, Dv fixed).
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np

from .base import Physics, register

DU, DV = 0.16, 0.08
DISPLAY_MAX = 0.5
_LABEL = re.compile(r"^GS/F([\d.]+)/k([\d.]+)$", re.IGNORECASE)


def _lap(x: np.ndarray) -> np.ndarray:
    return np.roll(x, 1, 0) + np.roll(x, -1, 0) + np.roll(x, 1, 1) + np.roll(x, -1, 1) - 4 * x


@register
class GrayScott(Physics):
    kind = "gray_scott"
    num_states = 256
    continuous = True
    dtype = np.float32

    def __init__(self, F: float = 0.0367, k: float = 0.0649):
        self.F, self.k = round(float(F), 4), round(float(k), 4)
        if not (0 < self.F < 0.2 and 0 < self.k < 0.2):
            raise ValueError("invalid Gray-Scott parameters")

    def step(self, state: np.ndarray) -> np.ndarray:
        u, v = state.astype(np.float64)
        uvv = u * v * v
        nu = u + DU * _lap(u) - uvv + self.F * (1 - u)
        nv = v + DV * _lap(v) + uvv - (self.F + self.k) * v
        return np.stack([nu, nv]).astype(np.float32)

    def vacuum(self, shape: tuple[int, int]) -> np.ndarray:
        return np.stack([np.ones(shape), np.zeros(shape)]).astype(np.float32)

    def view(self, state: np.ndarray) -> np.ndarray:
        return np.rint(np.clip(state[1] / DISPLAY_MAX, 0, 1) * 255).astype(np.uint8)

    def from_levels(self, levels: np.ndarray) -> np.ndarray:
        """V = level / 255 * DISPLAY_MAX, with U lowered where V is present (U = 1 - 2V)."""
        v = levels.astype(np.float64) / 255.0 * DISPLAY_MAX
        return np.stack([np.clip(1 - 2 * v, 0, 1), v]).astype(np.float32)

    def seed_spot(self, shape: tuple[int, int], side: int = 12, rng: np.random.Generator | None = None) -> np.ndarray:
        """Pearson's seed: a square with U = 0.5, V = 0.25 (+1% noise) in the middle of vacuum."""
        s = self.vacuum(shape)
        r0, c0 = shape[0] // 2 - side // 2, shape[1] // 2 - side // 2
        rng = rng or np.random.default_rng(0)
        s[0, r0:r0 + side, c0:c0 + side] = 0.5
        s[1, r0:r0 + side, c0:c0 + side] = 0.25 + 0.01 * rng.random((side, side))
        return s

    def random_state(self, rng: np.random.Generator, shape: tuple[int, int], density: float) -> np.ndarray:
        return self.from_levels(np.where(rng.random(shape) < density, np.rint(rng.random(shape) * 255), 0))

    def label(self) -> str:
        return f"GS/F{self.F:.4f}/k{self.k:.4f}"

    @classmethod
    def parse(cls, rule: str) -> "GrayScott":
        m = _LABEL.match(rule.strip())
        if not m:
            raise ValueError(f"cannot parse Gray-Scott rule {rule!r}; expected e.g. GS/F0.0367/k0.0649")
        return cls(float(m.group(1)), float(m.group(2)))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "F": self.F, "k": self.k}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GrayScott":
        return cls(d["F"], d["k"])

    @classmethod
    def random(cls, rng: np.random.Generator) -> "GrayScott":
        return cls(rng.uniform(0.01, 0.08), rng.uniform(0.04, 0.07))

    def mutate(self, rng: np.random.Generator) -> "GrayScott":
        while True:
            m = GrayScott(self.F + rng.normal(0, 0.002), self.k + rng.normal(0, 0.001))
            if m.label() != self.label():
                return m


_TLABEL = re.compile(r"^GST/F([\d.]+)/k([\d.]+)/(carried|redrawn|position)$", re.IGNORECASE)


@register
class GrayScottTracer(GrayScott):
    """Gray-Scott spots that carry a trait p in [0, 1]: controls for the heredity test (J-033).

    State (3, h, w) float32: U, V and Q = p V (the trait, weighted by V so mixing is exact).
    The trait never changes the chemistry (U, V evolve exactly as in GrayScott). Modes:

    * carried   p moves with V: Q' = Q + Dv lap(Q) + p U V^2 - (F + k) Q, where new V made
                by the reaction takes the local p. Daughters inherit their parent's p (positive).
    * redrawn   p is replaced every step by a hash of the local state (deterministic noise):
                nothing is inherited (negative).
    * position  p = column / width, recomputed every step: neighbours resemble each other
                because they share a place, not a parent (deceptive "common environment").
    """
    kind = "gray_scott_tracer"

    def __init__(self, F: float = 0.0367, k: float = 0.0649, mode: str = "carried"):
        super().__init__(F, k)
        if mode not in ("carried", "redrawn", "position"):
            raise ValueError(f"unknown tracer mode {mode!r}")
        self.mode = mode

    def step(self, state: np.ndarray) -> np.ndarray:
        u, v, q = state.astype(np.float64)
        uvv = u * v * v
        nu = u + DU * _lap(u) - uvv + self.F * (1 - u)
        nv = v + DV * _lap(v) + uvv - (self.F + self.k) * v
        if self.mode == "carried":
            p = np.clip(q / np.maximum(v, 1e-9), 0, 1)
            nq = q + DV * _lap(q) + p * uvv - (self.F + self.k) * q
        elif self.mode == "redrawn":
            nq = (np.sin(nu * 12989.8 + nv * 78233.0) * 43758.5453 % 1.0) * nv
        else:
            nq = (np.arange(v.shape[1]) / v.shape[1])[None, :] * nv
        return np.stack([nu, nv, np.clip(nq, 0, nv)]).astype(np.float32)

    def vacuum(self, shape: tuple[int, int]) -> np.ndarray:
        return np.stack([np.ones(shape), np.zeros(shape), np.zeros(shape)]).astype(np.float32)

    def from_levels(self, levels: np.ndarray, p: float | np.ndarray = 0.5) -> np.ndarray:
        u, v = super().from_levels(levels)
        return np.stack([u, v, v * p]).astype(np.float32)

    def trait(self, state: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """(weight, weighted trait): an object's trait is sum(Q) / sum(V) over its cells."""
        return state[1].astype(np.float64), state[2].astype(np.float64)

    def label(self) -> str:
        return f"GST/F{self.F:.4f}/k{self.k:.4f}/{self.mode}"

    @classmethod
    def parse(cls, rule: str) -> "GrayScottTracer":
        m = _TLABEL.match(rule.strip())
        if not m:
            raise ValueError(f"cannot parse rule {rule!r}; expected e.g. GST/F0.0367/k0.0649/carried")
        return cls(float(m.group(1)), float(m.group(2)), m.group(3).lower())

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "F": self.F, "k": self.k, "mode": self.mode}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GrayScottTracer":
        return cls(d["F"], d["k"], d.get("mode", "carried"))

    @classmethod
    def random(cls, rng: np.random.Generator) -> "GrayScottTracer":
        return cls(mode=str(rng.choice(["carried", "redrawn", "position"])))

    def mutate(self, rng: np.random.Generator) -> "GrayScottTracer":
        return GrayScottTracer(self.F, self.k, next(m for m in ("carried", "redrawn", "position") if m != self.mode))
