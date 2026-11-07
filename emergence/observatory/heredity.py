"""Heredity test: do offspring resemble their own parent, wherever they are? (J-033)

Needs a physics with a per-cell trait: ``physics.trait(state) -> (weight, weighted trait)``;
an object's trait is sum(weighted trait) / sum(weight) over its cells. (GrayScottTracer has
one; Flow-Lenia with localized parameters will.) Like the birth detector, this is an
intervention on isolated clones, never on the original universe.

Method (a transplant, as in cross-fostering experiments): for up to MAX_PARENTS objects of
the most common mass class in a world,

1. measure the parent's trait in its own world;
2. copy it alone into the centre of the physics' vacuum (births.alone) and run STEPS steps;
3. its offspring are the objects at the end with a mass within births.COPY_TOL of the
   parent's; a parent that leaves fewer than 2 has not reproduced and is dropped;
4. record the offspring's mean trait.

Heredity = the correlation between parent and offspring traits across parents. Moving
offspring to a common place removes "common environment" resemblance (a trait set by
position makes neighbours alike without inheritance). Selection-aware null: the same
parents and offspring with parents shuffled (N_PERM permutations); this accounts for how
parents were chosen (only those that reproduced are kept).

Verdicts: "heredity" (>= MIN_FAMILIES families, r >= MIN_R, permutation p < ALPHA),
"no heredity", "no variation" (parent traits spread less than MIN_SPREAD: copies are
identical, as in plain Gray-Scott), "too few families" (fewer than MIN_FAMILIES parents
reproduced). Not shown: selection or evolution (that needs traits that change fitness).
"""
from __future__ import annotations

import numpy as np

from . import births as B

STEPS = 1500
MAX_PARENTS = 16
MIN_FAMILIES = 6
MIN_R = 0.5
ALPHA = 0.01
MIN_SPREAD = 0.05
N_PERM = 2000


def object_trait(physics, state: np.ndarray, mask: np.ndarray) -> float:
    w, wt = physics.trait(state)
    s = w[mask].sum()
    return float(wt[mask].sum() / s) if s > 0 else float("nan")


def family(physics, state: np.ndarray, obj: dict, steps: int = STEPS, side: int = 128) -> dict:
    """Transplant one parent and return its trait and its offspring's traits."""
    parent_trait = object_trait(physics, state, obj["mask"])
    try:
        w = B.alone(physics, state, obj["mask"], side)
    except ValueError:
        return {"parent": parent_trait, "offspring": [], "too_large": True}
    for _ in range(steps):
        w = physics.step(w)
    pm = obj["mass"]
    kids = [o for o in B.find(physics, w) if pm / B.COPY_TOL <= o["mass"] <= pm * B.COPY_TOL]
    return {"parent": parent_trait, "parent_mass": round(pm, 2),
            "offspring": [round(object_trait(physics, w, o["mask"]), 4) for o in kids]}


def test(physics, state: np.ndarray, rng: np.random.Generator, max_parents: int = MAX_PARENTS,
         steps: int = STEPS, side: int = 128) -> dict:
    objs = [o for o in B.find(physics, state) if o["mass"] >= 1]
    if not objs:
        return {"verdict": "too few families", "families": 0}
    groups: dict = {}
    for o in objs:
        groups.setdefault(int(np.floor(2 * np.log2(o["mass"]))), []).append(o)
    cand = max(groups.values(), key=len)
    if len(cand) > max_parents:
        cand = [cand[i] for i in sorted(rng.choice(len(cand), max_parents, replace=False))]
    fams = [family(physics, state, o, steps, side) for o in cand]
    ok = [f for f in fams if len(f["offspring"]) >= 2]
    out = {"candidates": len(cand), "families": len(ok), "family_data": fams}
    if len(ok) < MIN_FAMILIES:
        return out | {"verdict": "too few families"}
    par = np.array([f["parent"] for f in ok])
    off = np.array([np.mean(f["offspring"]) for f in ok])
    out["parent_spread"] = round(float(par.max() - par.min()), 4)
    if out["parent_spread"] < MIN_SPREAD:
        return out | {"verdict": "no variation"}
    r = float(np.corrcoef(par, off)[0, 1]) if off.std() > 0 else 0.0
    null = np.array([np.corrcoef(rng.permutation(par), off)[0, 1] if off.std() > 0 else 0.0 for _ in range(N_PERM)])
    p = float((1 + (null >= r).sum()) / (N_PERM + 1))
    slope = float(np.polyfit(par, off, 1)[0])
    out |= {"r": round(r, 3), "slope": round(slope, 3), "p": round(p, 5),
            "null_r95": round(float(np.quantile(null, 0.95)), 3)}
    out["verdict"] = "heredity" if r >= MIN_R and p < ALPHA else "no heredity"
    return out
