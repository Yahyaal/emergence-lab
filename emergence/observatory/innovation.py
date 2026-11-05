"""Innovation over time: does a universe keep producing NEW kinds of persistent
structure, or does it only keep moving?

Continued activity is not continued novelty: a glider gun is active forever but
makes the same glider forever. This probe re-runs a universe from its spec (a
passive re-observation, no intervention), samples a short burst of frames every
``every`` steps, and records the persistent shapes seen in each burst
(orientation-free). It reports:

* ``shapes_total``        distinct persistent shapes over the whole run
* ``new_second_half``     shapes first seen in the second half of the run
* ``established_late``    shapes first seen in the third quarter that are seen
                          AGAIN in the last quarter. One-off coincidences in a busy
                          or noisy universe rarely recur; established new types do.
* ``new_per_sample``      the innovation curve

This is in the spirit of Bedau & Packard's evolutionary-activity statistics,
much simplified: it measures the appearance of new *types* over time.
"""
from __future__ import annotations

from ..engine import Universe
from .shapes import persistent_shapes
from .structures import MAX_TAU


def innovation_profile(u: Universe, steps: int = 3200, every: int = 100) -> dict:
    burst = 2 * MAX_TAU + 1
    first_seen: dict[bytes, list[int]] = {}
    curve = []
    for t0 in range(0, steps, every):
        u.step(t0 - u.t)
        frames = []
        for _ in range(burst):
            frames.append(u.state.copy())
            u.step()
        shapes = persistent_shapes(frames)
        curve.append(sum(1 for k in shapes if k not in first_seen))
        for k in shapes:
            first_seen.setdefault(k, []).append(t0)
    half, q3 = steps // 2, 3 * steps // 4
    return {
        "steps": steps,
        "every": every,
        "shapes_total": len(first_seen),
        "new_second_half": sum(1 for ts in first_seen.values() if ts[0] >= half),
        "established_late": sum(1 for ts in first_seen.values() if half <= ts[0] < q3 and any(t >= q3 for t in ts)),
        "new_per_sample": curve,
    }
