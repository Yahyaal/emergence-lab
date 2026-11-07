"""E-22: two wanderers placed near each other (pre-registered, docs/data/e22-preregistration.md).

Usage: python scripts/wanderer_encounters.py --out docs/data/experiments/2026-11-07-e22-wanderer-encounters.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from emergence.engine import Universe, UniverseSpec
from emergence.lab import study_universe
from emergence.observatory import continuous as C
from emergence.physics import parse_rule

RULE = "LENIA/R13/T10/m0.243/s0.0224/b1,0.5,0.5"
SPEC81 = UniverseSpec({"kind": "lenia", "rule": RULE}, 1909909783107617907, 128, 128, 0.18,
                      init={"kind": "smooth", "ell": 6.0})
SIDE = 160


def wanderer() -> np.ndarray:
    u = Universe.from_spec(SPEC81)
    u.step(2000)
    o = min(C.objects(u.state), key=lambda x: abs(x["mass"] - 115))
    a = C.isolate(u.state, o)
    rr, cc = np.nonzero(a)
    return a[rr.min():rr.max() + 1, cc.min():cc.max() + 1]


def sym(p: np.ndarray, k: int) -> np.ndarray:
    q = np.rot90(p, k % 4)
    return np.fliplr(q) if k >= 4 else q


def place(w, p, cy, cx):
    ys = (np.arange(p.shape[0]) + int(cy) - p.shape[0] // 2) % SIDE
    xs = (np.arange(p.shape[1]) + int(cx) - p.shape[1] // 2) % SIDE
    w[np.ix_(ys, xs)] = np.maximum(w[np.ix_(ys, xs)], p)


def run(args) -> dict:
    i, k, d, ang, phase, steps = args
    phys = parse_rule(RULE)
    p = WANDERER
    b = sym(p, k)
    if phase:
        tmp = np.zeros((SIDE, SIDE), np.uint8)
        place(tmp, b, SIDE // 2, SIDE // 2)
        for _ in range(phase):
            tmp = phys.step(tmp)
        o = max(C.objects(tmp), key=lambda x: x["mass"])
        a = C.isolate(tmp, o)
        rr, cc = np.nonzero(a)
        b = a[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    w = np.zeros((SIDE, SIDE), np.uint8)
    place(w, p, SIDE // 2, SIDE // 2)
    place(w, b, SIDE // 2 + d * np.sin(ang), SIDE // 2 + d * np.cos(ang))
    obs = study_universe(Universe(phys, w), i, steps=steps)
    u = Universe(phys, w)
    u.step(steps)
    masses = sorted(round(o["mass"], 1) for o in C.objects(u.state))
    return {"trial": i, "sym": k, "d": d, "angle": round(float(ang), 3), "phase": phase,
            "self_propelled": obs.metrics["self_propelled_shapes"], "class": obs.cls,
            "persistent": obs.metrics["vocabulary"], "masses": masses}


def init(p):
    global WANDERER
    WANDERER = p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    rng = np.random.default_rng(22)
    jobs = [(i, int(rng.integers(8)), int(rng.choice([20, 25, 30, 35, 40])), float(rng.uniform(0, 2 * np.pi)),
             int(rng.integers(0, 41)), a.steps) for i in range(a.trials)]
    p = wanderer()
    with Pool(a.workers or None, initializer=init, initargs=(p,)) as pool:
        res = pool.map(run, jobs, chunksize=1)
    from collections import Counter
    def cat(r):
        m = r["masses"]
        if not m:
            return "both destroyed"
        if any(not 90 <= x <= 145 for x in m):
            return "new object"
        return {1: "one wanderer", 2: "two wanderers"}.get(len(m), "more than two")
    print(dict(Counter(cat(r) for r in res)), "| self-propelled counts:", dict(Counter(r["self_propelled"] for r in res)))
    if a.out:
        json.dump({"rule": RULE, "side": SIDE, "steps": a.steps, "runs": res}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
