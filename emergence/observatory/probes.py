"""Damage spreading (a discrete analogue of the Lyapunov exponent).

A *forked twin* of the universe is created from a snapshot, a single cell is
flipped in the twin, and both evolve under the same rule. The original universe
is never touched; the twin is a separate, controlled side-experiment.

* ordered systems heal the damage (-> 0)
* chaotic systems spread it until twins are as different as two random states (-> 1)
* complex systems sit in between, with slow, localised spreading
"""
from __future__ import annotations

import numpy as np

from ..engine import Universe
from ..physics import Physics
from .measures import pairwise_difference_baseline


def damage_spreading(physics: Physics, snapshot: np.ndarray, reference: list[np.ndarray],
                     rng: np.random.Generator, trials: int = 3) -> dict[str, float]:
    steps = len(reference)
    if steps == 0:
        return {"damage": 0.0, "damage_norm": 0.0}
    curves = np.zeros((trials, steps))
    view = physics.view  # identity for uint8 physics; float physics compare their uint8 views
    ref_views = [view(r) for r in reference]
    for k in range(trials):
        twin_state = np.array(snapshot, copy=True)
        r, c = int(rng.integers(snapshot.shape[0])), int(rng.integers(snapshot.shape[1]))
        twin_state[r, c] = 0 if twin_state[r, c] else 1  # float physics: a unit of matter
        twin = Universe(physics, twin_state)
        for i in range(steps):
            twin.step()
            curves[k, i] = np.count_nonzero(view(twin.state) != ref_views[i]) / snapshot.size
    final = float(curves[:, -max(1, steps // 8):].mean())
    baseline = pairwise_difference_baseline(ref_views[-1], physics.num_states)
    return {
        "damage": final,
        "damage_norm": final / baseline if baseline > 0 else 0.0,
        "damage_curve": [round(float(x), 5) for x in curves.mean(axis=0)],
    }
