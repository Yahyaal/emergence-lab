"""Synthetic control "physics" with known answers, used to validate the observatory.

``NoiseControl`` produces a fresh i.i.d. random grid every step. It is still a
deterministic function of the current state (the next grid is seeded by a hash
of the current one), so it is reproducible and runs through the exact same
pipeline as real physics. It has no structure by construction, so any moving or
persistent object the observatory reports here is a false positive.
"""
from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from .base import Physics, register


@register
class NoiseControl(Physics):
    kind = "noise_control"
    num_states = 2

    def __init__(self, density: float = 0.3):
        self.density = float(density)

    def step(self, state: np.ndarray) -> np.ndarray:
        seed = int.from_bytes(hashlib.blake2b(state.tobytes(), digest_size=8).digest(), "little")
        return (np.random.default_rng(seed).random(state.shape) < self.density).astype(np.uint8)

    def random_state(self, rng, shape, density):
        return (rng.random(shape) < self.density).astype(np.uint8)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.label(), "density": self.density}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("density", 0.3))

    @classmethod
    def random(cls, rng):
        return cls(float(rng.uniform(0.1, 0.5)))

    def mutate(self, rng):
        return NoiseControl(float(np.clip(self.density + rng.normal(0, 0.05), 0.05, 0.95)))

    def label(self) -> str:
        return f"NOISE/{self.density:g}"
