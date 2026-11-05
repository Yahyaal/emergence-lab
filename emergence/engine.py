"""Simulation engine: owns universes and advances them. Knows nothing about
measurement. Everything is deterministic given a ``UniverseSpec``.
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Iterator

import numpy as np

from .physics import Physics, physics_from_dict


@dataclass(frozen=True)
class UniverseSpec:
    """Everything needed to reproduce a universe bit-for-bit."""

    physics: dict[str, Any]
    seed: int
    width: int = 64
    height: int = 64
    density: float = 0.35

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniverseSpec":
        return cls(physics=dict(d["physics"]), seed=int(d["seed"]), width=int(d["width"]),
                   height=int(d["height"]), density=float(d["density"]))


def state_hash(state: np.ndarray) -> str:
    h = hashlib.blake2b(digest_size=16)
    h.update(np.asarray(state.shape, dtype=np.int64).tobytes())
    h.update(np.ascontiguousarray(state, dtype=np.uint8).tobytes())
    return h.hexdigest()


class Universe:
    def __init__(self, physics: Physics, state: np.ndarray, t: int = 0):
        self.physics = physics
        self._state = np.ascontiguousarray(state, dtype=np.uint8)
        self.t = t

    @classmethod
    def from_spec(cls, spec: UniverseSpec) -> "Universe":
        physics = physics_from_dict(spec.physics)
        rng = np.random.default_rng(spec.seed)
        state = physics.random_state(rng, (spec.height, spec.width), spec.density)
        return cls(physics, state)

    @property
    def state(self) -> np.ndarray:
        """Read-only view: observers can look but cannot touch."""
        v = self._state.view()
        v.flags.writeable = False
        return v

    def step(self, n: int = 1) -> None:
        for _ in range(n):
            self._state = self.physics.step(self._state)
            self.t += 1

    def fork(self, state: np.ndarray | None = None) -> "Universe":
        """An independent copy (optionally with a different state) under the same physics.
        Used for controlled side-experiments; never affects this universe."""
        return Universe(self.physics, np.array(self._state if state is None else state, copy=True), self.t)


def run(spec: UniverseSpec, steps: int) -> Iterator[tuple[int, np.ndarray]]:
    """Yield (t, read-only state) for t = 0..steps."""
    u = Universe.from_spec(spec)
    yield u.t, u.state
    for _ in range(steps):
        u.step()
        yield u.t, u.state
