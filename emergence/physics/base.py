"""Abstract interface every kind of "physics" must implement.

The rest of the system (engine, observatory, discovery, dashboard) only talks to
physics through this interface. A state is always a 2D ``numpy.uint8`` array of
discrete cell states, where 0 means "vacuum". New physics (e.g. continuous
automata, particle systems rasterised to a grid) can be added by subclassing
``Physics`` and registering it with ``@register``.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

REGISTRY: dict[str, type["Physics"]] = {}


def register(cls: type["Physics"]) -> type["Physics"]:
    REGISTRY[cls.kind] = cls
    return cls


def physics_from_dict(d: dict[str, Any]) -> "Physics":
    try:
        cls = REGISTRY[d["kind"]]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"unknown physics kind: {d.get('kind')!r}") from exc
    return cls.from_dict(d)


class Physics(ABC):
    """A fixed, deterministic local update rule."""

    kind: str = "abstract"
    num_states: int = 2

    @abstractmethod
    def step(self, state: np.ndarray) -> np.ndarray:
        """Return the next state. Must not modify ``state`` in place."""

    @abstractmethod
    def random_state(self, rng: np.random.Generator, shape: tuple[int, int], density: float) -> np.ndarray:
        """Random initial condition with roughly ``density`` non-vacuum cells."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable full description (must round-trip via from_dict)."""

    @classmethod
    @abstractmethod
    def from_dict(cls, d: dict[str, Any]) -> "Physics": ...

    @classmethod
    @abstractmethod
    def random(cls, rng: np.random.Generator) -> "Physics":
        """Sample a random rule from this family."""

    @abstractmethod
    def mutate(self, rng: np.random.Generator) -> "Physics":
        """Return a nearby rule (used by the discovery engine)."""

    @abstractmethod
    def label(self) -> str:
        """Short human-readable rule name."""

    def rule_features(self) -> dict[str, float]:
        """Static properties of the rule itself (not of its behaviour)."""
        return {}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Physics) and self.to_dict() == other.to_dict()

    def __hash__(self) -> int:
        return hash(self.label())
