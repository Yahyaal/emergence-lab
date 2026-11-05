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
    # Optional initial-condition generator (see INIT_KINDS). None = uniform random soup
    # at `density`, generated exactly as in v0.1-v0.3 so old specs stay bit-identical.
    init: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if d["init"] is None:
            del d["init"]  # keeps stored specs and caches identical to earlier versions
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UniverseSpec":
        return cls(physics=dict(d["physics"]), seed=int(d["seed"]), width=int(d["width"]),
                   height=int(d["height"]), density=float(d["density"]),
                   init=dict(d["init"]) if d.get("init") else None)


# Initial conditions: the same rule can be started from structurally different worlds.
# Every generator puts only state-1 cells into vacuum, like the default soup; they differ
# in WHERE matter is, not in what it is. `density` is the mean density for uniform and
# gradient; patch and spots use their own local density and are otherwise vacuum.
INIT_KINDS = {
    "uniform": "random soup at `density` everywhere (explicit form of the default)",
    "gradient": "density rises linearly across x from 0 to 2*density (same mean as uniform)",
    "patch": "soup at local density `local` (0.5) in a centred square covering `area` (0.25) of the world; vacuum elsewhere",
    "spots": "`n` (8) round blobs of radius `r` (5) at local density `local` (0.6) in vacuum",
}


def initial_state(spec: "UniverseSpec", rng: np.random.Generator) -> np.ndarray:
    h, w = spec.height, spec.width
    init = spec.init or {}
    kind = init.get("kind", "uniform")
    if kind == "uniform":
        dmap = np.full((h, w), spec.density)
    elif kind == "gradient":
        dmap = np.tile(np.linspace(0.0, min(1.0, 2 * spec.density), w), (h, 1))
    elif kind == "patch":
        side_h, side_w = int(round(h * init.get("area", 0.25) ** 0.5)), int(round(w * init.get("area", 0.25) ** 0.5))
        dmap = np.zeros((h, w))
        r0, c0 = (h - side_h) // 2, (w - side_w) // 2
        dmap[r0:r0 + side_h, c0:c0 + side_w] = init.get("local", 0.5)
    elif kind == "spots":
        n, r, local = int(init.get("n", 8)), float(init.get("r", 5)), float(init.get("local", 0.6))
        centres = rng.integers(0, [h, w], size=(n, 2))
        yy, xx = np.mgrid[0:h, 0:w]
        dmap = np.zeros((h, w))
        for cy, cx in centres:
            dy = np.minimum(np.abs(yy - cy), h - np.abs(yy - cy))  # torus distance
            dx = np.minimum(np.abs(xx - cx), w - np.abs(xx - cx))
            dmap[dy * dy + dx * dx <= r * r] = local
    else:
        raise ValueError(f"unknown init kind {kind!r}; known: {sorted(INIT_KINDS)}")
    return (rng.random((h, w)) < dmap).astype(np.uint8)


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
        if spec.init is not None:
            return cls(physics, initial_state(spec, rng))
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
