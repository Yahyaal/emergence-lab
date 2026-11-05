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


@register
class SmoothNoiseControl(Physics):
    """Deceptive control for continuous-state detectors: every step is a fresh, spatially
    smoothed random field (blob-like, Lenia-sized correlations) with no dynamics at all.
    Deterministic (seeded from the current state), so it is reproducible. Any persistent
    object or mover reported here is a false positive of the tracker."""

    kind = "smooth_noise_control"
    num_states = 256
    continuous = True

    def __init__(self, scale: float = 4.0):
        self.scale = float(scale)

    def step(self, state: np.ndarray) -> np.ndarray:
        from scipy import ndimage
        seed = int.from_bytes(hashlib.blake2b(state.tobytes(), digest_size=8).digest(), "little")
        f = ndimage.gaussian_filter(np.random.default_rng(seed).random(state.shape), self.scale, mode="wrap")
        f = (f - f.mean()) / (f.std() + 1e-12)
        # ~16% of cells above the 0.1 detection threshold, in blobs of ~`scale` cells:
        # sparse, Lenia-sized "objects" that appear and vanish at random
        return np.rint(np.clip(0.1 + 0.25 * (f - 1.0), 0, 1) * 255).astype(np.uint8)

    def random_state(self, rng, shape, density):
        return self.step((rng.random(shape) * 255).astype(np.uint8))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.label(), "scale": self.scale}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("scale", 4.0))

    @classmethod
    def random(cls, rng):
        return cls(float(rng.uniform(2, 8)))

    def mutate(self, rng):
        return SmoothNoiseControl(float(np.clip(self.scale * rng.normal(1, 0.1), 1, 12)))

    def label(self) -> str:
        return f"SMOOTHNOISE/{self.scale:g}"
