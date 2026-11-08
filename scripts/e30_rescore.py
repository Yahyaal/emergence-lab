"""E-30 follow-up (J-035, post hoc): is the fed vacuum stable, and what does the fixed birth
detector (perturbed-vacuum null) say about E-30's hit worlds?

For each of the 100 E-30 rules at food 0.05: the food layer perturbed as in births.perturbed_vacuum, alone, 160x160,
4000 steps; record the object count every 500 steps (stable food = no objects). Then every E-30
fed world with a reproducer is rebuilt (same seed) and rescanned with the current detector.

Usage: python scripts/e30_rescore.py --out docs/data/experiments/2026-11-07-e30-rescore.json --workers 11
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from multiprocessing import Pool

import numpy as np

from emergence.observatory import births as B
from emergence.physics import FlowLeniaPL, parse_rule

import pl_scan as P

SRC = "docs/data/experiments/2026-11-07-e30-flow-lenia-pl.json"


def stability(args):
    i, rule = args
    ph = parse_rule(rule)
    s = B.perturbed_vacuum(ph, (160, 160), ph.vacuum((2, 2)))
    counts = []
    for t in range(4001):
        if t % 500 == 0:
            counts.append(len(B.find(ph, s)))
        if t < 4000:
            s = ph.step(s)
    return {"i": i, "counts": counts, "stable": max(counts) == 0}


def rescan(i):
    rng = np.random.default_rng([30, i])
    base = FlowLeniaPL.random(rng)
    ph = FlowLeniaPL(base.kernels, base.R, 0.05)
    s = P.start(ph, rng)
    for _ in range(P.STEPS):
        s = ph.step(s)
    return {"i": i} | P.world(ph, s, rng)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = json.load(open(SRC))
    fed = [w for w in d["worlds"] if w["food"] > 0]
    hits = [w["i"] for w in fed if w["reproducers"]]
    with Pool(a.workers or None) as p:
        st = p.map(stability, [(w["i"], w["rule"]) for w in fed], chunksize=1)
        print("stable food:", sum(x["stable"] for x in st), "/", len(st), flush=True)
        rs = p.map(rescan, hits, chunksize=1)
    stable = {x["i"]: x["stable"] for x in st}
    print("hit worlds rescanned:", len(rs), "with a reproducer now:", sum(r["reproducers"] > 0 for r in rs),
          dict(Counter(v for r in rs for v in r["verdicts"])), flush=True)
    print("hit worlds on stable food:", sum(stable[i] for i in hits), "/", len(hits))
    ok = [w for w in fed if stable[w["i"]]]
    print("stable-food worlds:", len(ok), "with a reproducer (original scan):", sum(w["reproducers"] > 0 for w in ok),
          dict(Counter(v for w in ok for v in w["verdicts"])))
    json.dump({"experiment": "E-30 rescore", "stability": st, "rescan": rs}, open(a.out, "w"), indent=1)
    print("RESCORE DONE", flush=True)


if __name__ == "__main__":
    main()
