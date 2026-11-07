"""E-20: controlled glider-glider collisions (pre-registered, docs/data/e20-preregistration.md).

Two copies of the rule's emergent glider (continuous.emergent_glider, moving +x) are placed on
a torus: the partner is flipped (head-on, moving -x) or transposed (perpendicular, moving +y),
shifted sideways by `offset` cells and advanced `phase` steps. After `steps` steps, objects of
glider mass are counted and each is checked with the observatory's isolation test.

Usage: python scripts/collision_scan.py --out docs/data/experiments/2026-11-07-e20-collisions.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from emergence.observatory import continuous as C
from emergence.physics import parse_rule

RULES = ["LENIA/R13/T10/m0.150/s0.0150/b1", "LENIA/R13/T10/m0.140/s0.0140/b1"]
SIDE = 192
_GLIDERS: dict[str, np.ndarray] = {}


def glider(rule: str) -> np.ndarray:
    """The rule's emergent glider, cropped to its bounding box (moves +x)."""
    if rule not in _GLIDERS:
        g = C.emergent_glider(parse_rule(rule))
        o = max(C.objects(g), key=lambda x: x["mass"])
        a = C.isolate(g, o)
        rr, cc = np.nonzero(a)
        _GLIDERS[rule] = a[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    return _GLIDERS[rule]


def place(world: np.ndarray, pat: np.ndarray, cy: int, cx: int) -> None:
    h, w = pat.shape
    ys = (np.arange(h) + cy - h // 2) % SIDE
    xs = (np.arange(w) + cx - w // 2) % SIDE
    world[np.ix_(ys, xs)] = np.maximum(world[np.ix_(ys, xs)], pat)


def run(args) -> dict:
    rule, geometry, offset, phase, steps = args
    phys = parse_rule(rule)
    g = glider(rule)
    partner = np.flip(g, axis=1) if geometry == "head-on" else g.T  # moves -x / +y
    if phase:
        tmp = np.zeros((SIDE, SIDE), np.uint8)
        place(tmp, partner, SIDE // 2, SIDE // 2)
        for _ in range(phase):
            tmp = phys.step(tmp)
        o = max(C.objects(tmp), key=lambda x: x["mass"])
        a = C.isolate(tmp, o)
        rr, cc = np.nonzero(a)
        partner = a[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    world = np.zeros((SIDE, SIDE), np.uint8)
    c = SIDE // 2
    place(world, g, c, c - 45)                         # A moves +x towards the centre
    if geometry == "head-on":
        place(world, partner, c + offset, c + 45)      # B moves -x
    else:
        place(world, partner, c - 45, c + offset)      # B moves +y, crossing A's path
    for _ in range(steps):
        world = phys.step(world)
    objs = C.objects(world)
    gl = [o for o in objs if 50 <= o["mass"] <= 100]
    verified = sum(C.self_propelled(phys, world, o) for o in gl)
    other = [round(o["mass"], 1) for o in objs if not 50 <= o["mass"] <= 100]
    return {"rule": rule, "geometry": geometry, "offset": offset, "phase": phase, "gliders": verified,
            "glider_sized": len(gl), "other_objects": other, "mass": round(float(world.sum()) / 255, 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    jobs = [(r, geo, off, ph, a.steps) for r in RULES for geo in ("head-on", "perpendicular")
            for off in range(-24, 25, 2) for ph in range(0, 21, 5)]
    with Pool(a.workers or None) as p:
        res = p.map(run, jobs, chunksize=2)
    from collections import Counter
    for r in RULES:
        for geo in ("head-on", "perpendicular"):
            sub = [x for x in res if x["rule"] == r and x["geometry"] == geo]
            print(r.split("/")[3], geo, "gliders after:", dict(sorted(Counter(x["gliders"] for x in sub).items())),
                  "| runs with other objects:", sum(bool(x["other_objects"]) for x in sub))
    if a.out:
        json.dump({"side": SIDE, "steps": a.steps, "runs": res}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
