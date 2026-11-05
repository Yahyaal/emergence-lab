"""Knockout probe: do earlier innovations ENABLE later ones?

Cumulative innovation means new kinds of structure build on earlier ones. That's a
causal claim, so it's tested by intervention, on forked clones only, never on the
original universe:

1. Run the universe to time t1, when a new persistent shape type K first appears.
2. Fork three kinds of world from the state at t1:
   * original     unchanged
   * knockout     every structure of type K deleted
   * control(s)   the same number of cells deleted, but from structures of OLD types
                  (already seen before t1); several different random choices
3. Run all of them for `horizon` steps and record which persistent shape types appear.
4. Later novelties L = types the original makes after t1 that were never seen before.
   lost(world) = fraction of L that never appears in that world.
   dependency  = lost(knockout) - mean lost(controls)

Why the controls matter: in a chaotic universe ANY deletion changes the whole future
(damage spreading), so the knockout loses most of L whatever K was. The controls
measure that baseline. Verdicts:

* "untestable"     fewer than `min_later` later novelties
* "inconclusive"   the controls alone lose >= 50% of L (any perturbation rewrites the future)
* "depends"        dependency >= 0.3: later novelty specifically needs K
* "independent"    otherwise

A second, rate-based reading is reported alongside, because in chaotic universes the
set comparison is hopeless: any deletion reshuffles WHICH rare shapes appear, so
`lost` is high for knockout and controls alike (that's "inconclusive"). The rate-based
question is whether deleting K reduces HOW MANY new types appear afterwards:

  drop(world)      = 1 - (new types after t1 in world) / (new types after t1 in original)
  rate_dependency  = drop(knockout) - mean drop(controls)
  rate_verdict     = "depends" only if the knockout really lowers novelty (drop >= 0.3),
                     by more than EVERY control deletion, and rate_dependency >= 0.5;
                     "no rate effect" otherwise

The 0.5 cut is the 95th percentile of the PLACEBO distribution measured in E-10/E-11:
each control deletion treated as if it were the target, compared with the other controls.
A single test is weak evidence. The right population-level test compares real knockouts
with placebos (conditions.summarize reports P(real > placebo); 0.5 = no effect).

In a statistically stationary chaotic universe, random deletions leave the rate of
novelty unchanged; deleting a genuine enabler lowers it.

Thresholds are heuristics, validated against the controls in benchmark_probes.py.
This tests whether K is *necessary* for later novelty, not *how* it causes it.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from ..engine import Universe
from .shapes import canonical, persistent_shapes
from .structures import MAX_CELLS, MAX_TAU, MIN_CELLS

BURST = 2 * MAX_TAU + 1
_STRUCT = np.ones((3, 3), dtype=bool)


def types_over(u: Universe, steps: int, every: int) -> dict[bytes, int]:
    """Advance u by `steps`, sampling bursts every `every` steps. Returns type -> first time seen."""
    first: dict[bytes, int] = {}
    t_end = u.t + steps
    while u.t + BURST <= t_end:
        t0 = u.t
        frames = []
        for _ in range(BURST):
            frames.append(u.state.copy())
            u.step()
        for k in persistent_shapes(frames):
            first.setdefault(k, t0)
        u.step(max(0, min(every - BURST, t_end - u.t)))
    return first


def component_masks(state: np.ndarray) -> list[tuple[bytes, np.ndarray]]:
    """(canonical type, cell mask) for every census-sized component (same rules as census())."""
    labels, n = ndimage.label(state > 0, structure=_STRUCT)
    if n == 0:
        return []
    sizes = np.bincount(labels.ravel())
    out = []
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None or not (MIN_CELLS <= sizes[i] <= MAX_CELLS):
            continue
        sub = labels[sl] == i
        patch = np.where(sub, state[sl], 0).astype(np.uint8)
        m = np.zeros(state.shape, bool)
        m[sl] = sub
        out.append((canonical(bytes(patch.shape) + patch.tobytes()), m))
    return out


def knockout_compare(physics, state: np.ndarray, target: np.ndarray, controls: list[np.ndarray],
                     before: set[bytes], horizon: int, every: int, min_later: int = 3) -> dict:
    """Core comparison from a given state, with explicit masks (also used by the controls)."""
    def run(mask: np.ndarray | None) -> set[bytes]:
        s = state.copy()
        if mask is not None:
            s[mask] = 0
        return set(types_over(Universe(physics, s), horizon, every))

    orig = run(None)
    later = orig - before
    if len(later) < min_later:
        return {"verdict": "untestable", "rate_verdict": "untestable", "later_novelties": len(later)}
    lost = lambda seen: len(later - seen) / len(later)  # noqa: E731
    drop = lambda seen: 1 - len(seen - before) / len(later)  # noqa: E731
    seen_k = run(target)
    seen_c = [run(m) for m in controls]
    lost_k, lost_c = lost(seen_k), [lost(x) for x in seen_c]
    mean_c = float(np.mean(lost_c)) if lost_c else 0.0
    dep = lost_k - mean_c
    verdict = ("inconclusive" if mean_c >= 0.5 else "depends" if dep >= 0.3 else "independent")
    drop_k, drop_c = drop(seen_k), [drop(x) for x in seen_c]
    mean_dc = float(np.mean(drop_c)) if drop_c else 0.0
    rate_dep = drop_k - mean_dc
    rate_verdict = ("depends" if drop_k >= 0.3 and drop_k > max(drop_c, default=0.0) and rate_dep >= 0.5
                    else "no rate effect")
    return {"verdict": verdict, "later_novelties": len(later), "lost_knockout": round(lost_k, 3),
            "lost_controls": [round(x, 3) for x in lost_c], "dependency": round(dep, 3),
            "rate_verdict": rate_verdict, "drop_knockout": round(drop_k, 3),
            "drop_controls": [round(x, 3) for x in drop_c], "rate_dependency": round(rate_dep, 3),
            "cells_removed": int(target.sum())}


def knockout_experiment(u: Universe, t1: int, horizon: int, every: int, rng: np.random.Generator,
                        n_controls: int = 3) -> dict:
    """Find the types that are new at t1 in universe u (advanced from its current time),
    and test whether later novelty depends on them. u is a fresh universe; it is advanced."""
    before = set(types_over(u, t1 - u.t, every)) if t1 > u.t else set()
    # new types: persistent in the burst starting at t1 and never seen before. A type can
    # form a few steps into the burst, so knock out at the first frame where it is present.
    frames, probe = [], Universe(u.physics, u.state.copy())
    for _ in range(BURST):
        frames.append(probe.state.copy())
        probe.step()
    new_types = persistent_shapes(frames) - before
    state, comps, target, offset = None, [], None, 0
    for i, f in enumerate(frames):
        cs = component_masks(f)
        hit = [m for k, m in cs if k in new_types]
        if hit:
            state, comps, offset = f.copy(), cs, i
            target = np.logical_or.reduce(hit)
            break
    if target is None:
        return {"verdict": "untestable", "reason": "no new type present at t1", "t1": t1}
    old = [m for k, m in comps if k in before]
    controls = []
    for _ in range(n_controls):
        mask = np.zeros(state.shape, bool)
        for i in rng.permutation(len(old)):
            if mask.sum() >= target.sum():
                break
            if not (old[i] & target).any():
                mask |= old[i]
        if mask.sum() < target.sum():  # not enough old structure: add random occupied cells
            occ = np.flatnonzero((state > 0) & ~target & ~mask)
            need = int(target.sum() - mask.sum())
            if len(occ) >= need:
                mask.flat[rng.choice(occ, size=need, replace=False)] = True
        controls.append(mask)
    res = knockout_compare(u.physics, state, target, controls, before | new_types, horizon, every)
    res.update({"t1": t1 + offset, "new_types_at_t1": len(new_types)})
    return res
