"""Outer-totalistic 2D cellular automata on a torus (Moore neighbourhood).

Covers the classic "Life-like" family (2 states, e.g. B3/S23 = Conway's Life)
and the "Generations" family (C > 2 states: 1 = alive, 2..C-1 = refractory /
dying states that do not count as neighbours and cannot be reborn until they
decay back to 0).

Rule string: ``B<digits>/S<digits>`` for 2 states, ``B../S../C<n>`` otherwise.
"""
from __future__ import annotations

import re
from typing import Any

import numpy as np

from .base import Physics, register

_RULE_RE = re.compile(r"^B([0-8]*)/S([0-8]*)(?:/C(\d+))?$", re.IGNORECASE)


@register
class OuterTotalistic(Physics):
    kind = "outer_totalistic"

    def __init__(self, birth: frozenset[int] | set[int], survive: frozenset[int] | set[int], num_states: int = 2):
        birth, survive = frozenset(birth), frozenset(survive)
        if not all(0 <= n <= 8 for n in birth | survive):
            raise ValueError("neighbour counts must be in 0..8")
        if not 2 <= num_states <= 255:
            raise ValueError("num_states must be in 2..255")
        self.birth = birth
        self.survive = survive
        self.num_states = int(num_states)
        self._bmask = np.array([n in birth for n in range(9)], dtype=bool)
        self._smask = np.array([n in survive for n in range(9)], dtype=bool)

    # ------------------------------------------------------------------ dynamics
    @staticmethod
    def neighbour_count(alive: np.ndarray) -> np.ndarray:
        a = alive.astype(np.uint8)
        p = np.pad(a, 1, mode="wrap")
        h, w = a.shape
        n = (
            p[0:h, 0:w] + p[0:h, 1:w + 1] + p[0:h, 2:w + 2]
            + p[1:h + 1, 0:w] + p[1:h + 1, 2:w + 2]
            + p[2:h + 2, 0:w] + p[2:h + 2, 1:w + 1] + p[2:h + 2, 2:w + 2]
        )
        return n

    def step(self, state: np.ndarray) -> np.ndarray:
        alive = state == 1
        n = self.neighbour_count(alive)
        born = (state == 0) & self._bmask[n]
        surv = alive & self._smask[n]
        if self.num_states == 2:
            return (born | surv).astype(np.uint8)
        # every non-vacuum cell ages by one (alive -> first dying state) ...
        nxt = np.where(state > 0, state.astype(np.int16) + 1, 0)
        nxt[nxt >= self.num_states] = 0
        nxt = nxt.astype(np.uint8)
        # ... unless it survives or is born
        nxt[surv] = 1
        nxt[born] = 1
        return nxt

    def random_state(self, rng: np.random.Generator, shape: tuple[int, int], density: float) -> np.ndarray:
        return (rng.random(shape) < density).astype(np.uint8)

    # ------------------------------------------------------------- serialisation
    def label(self) -> str:
        b = "".join(str(n) for n in sorted(self.birth))
        s = "".join(str(n) for n in sorted(self.survive))
        base = f"B{b}/S{s}"
        return base if self.num_states == 2 else f"{base}/C{self.num_states}"

    @classmethod
    def parse(cls, rule: str) -> "OuterTotalistic":
        m = _RULE_RE.match(rule.strip())
        if not m:
            raise ValueError(f"cannot parse rule {rule!r}; expected e.g. B3/S23 or B2/S/C3")
        b, s, c = m.groups()
        return cls({int(x) for x in b}, {int(x) for x in s}, int(c) if c else 2)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "rule": self.label()}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "OuterTotalistic":
        return cls.parse(d["rule"])

    # ------------------------------------------------------------- exploration
    # B0 rules are excluded from random sampling: with B0 the vacuum itself is
    # unstable and every universe strobes, which is a known degenerate case.
    @classmethod
    def random(cls, rng: np.random.Generator) -> "OuterTotalistic":
        p_b, p_s = rng.uniform(0.1, 0.45), rng.uniform(0.1, 0.6)
        birth = {n for n in range(1, 9) if rng.random() < p_b}
        if not birth:
            birth = {int(rng.integers(1, 9))}
        survive = {n for n in range(0, 9) if rng.random() < p_s}
        num_states = 2 if rng.random() < 0.7 else int(rng.integers(3, 9))
        return cls(birth, survive, num_states)

    def mutate(self, rng: np.random.Generator) -> "OuterTotalistic":
        birth, survive, c = set(self.birth), set(self.survive), self.num_states
        for _ in range(1 + int(rng.random() < 0.35)):
            r = rng.random()
            if r < 0.45:
                birth ^= {int(rng.integers(1, 9))}
            elif r < 0.9:
                survive ^= {int(rng.integers(0, 9))}
            else:
                c = int(np.clip(c + rng.choice([-1, 1]), 2, 8))
        if not birth:
            birth = {int(rng.integers(1, 9))}
        return OuterTotalistic(birth, survive, c)

    def rule_features(self) -> dict[str, float]:
        # Langton's lambda for an outer-totalistic rule: fraction of
        # (state, neighbour-count) configurations, weighted by how many
        # neighbourhoods produce that count, that map to a non-vacuum state.
        from math import comb
        w = np.array([comb(8, n) for n in range(9)], dtype=float) / 256.0
        lam = 0.5 * float(w[self._bmask].sum()) + 0.5 * float(w[self._smask].sum())
        return {"langton_lambda": round(lam, 6), "num_states": float(self.num_states)}
