"""E-31: held-out fed FlowLeniaPL scan on rules whose food layer is stable.

Pre-registered in docs/data/e31-preregistration.md. E-30 (J-035) found that uniform food is an
unstable fixed point in 68 of 100 rules, and every apparent reproducer was food condensing. The
perturbed-vacuum null (D-030) was added after the fact. This scan tests it on new rules (seed 31):

1. Screen SCREEN random rules at each food level: the perturbed food layer alone, 160x160, 4000
   steps (as in e30_rescore.stability). Stable = no object at any 500-step checkpoint.
2. For the first CAP stable rules at each food level, run the E-30 world (pl_scan.start, 1500
   steps) and the current birth detector (with the perturbed-vacuum null) and, where it finds a
   reproducer, the heredity test.

Pipeline positive: GrayScottTracer worlds through the same path (pl_scan.gs_job).

Usage: python scripts/pl_heldout.py --out docs/data/experiments/2026-11-08-e31-stable-food.json --workers 11
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

from emergence.physics import FlowLeniaPL

import e30_rescore as R
import pl_scan as P

FOODS = (0.05, 0.08)
SCREEN, CAP = 200, 50


def rule(i: int, seed: int, food: float) -> FlowLeniaPL:
    base = FlowLeniaPL.random(np.random.default_rng([seed, i]))
    return FlowLeniaPL(base.kernels, base.R, food)


def screen_job(args):
    i, seed, food = args
    return {"i": i, "food": food} | R.stability((i, rule(i, seed, food).label()))


def scan_job(args):
    i, seed, food = args
    t0 = time.time()
    rng = np.random.default_rng([seed, i])
    FlowLeniaPL.random(rng)  # same rng stream as pl_scan.pl_job: the start follows the rule draw
    ph = rule(i, seed, food)
    s = P.start(ph, rng)
    for _ in range(P.STEPS):
        s = ph.step(s)
    return {"i": i, "food": food, "rule": ph.label()} | P.world(ph, s, rng) | {"seconds": round(time.time() - t0, 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--screen", type=int, default=SCREEN)
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--gs", type=int, default=4)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    with Pool(a.workers or None) as p:
        gs = p.map(P.gs_job, range(a.gs), chunksize=1)
        print("pipeline positive (Gray-Scott tracer): reproducer in", sum(g["reproducers"] > 0 for g in gs), "/", a.gs,
              "; heredity in", sum((g.get("heredity") or {}).get("verdict") == "heredity" for g in gs), flush=True)
        st = p.map(screen_job, [(i, a.seed, f) for f in FOODS for i in range(a.screen)], chunksize=2)
        chosen = []
        for f in FOODS:
            ok = [x["i"] for x in st if x["food"] == f and x["stable"]]
            print("food", f, "stable:", len(ok), "/", a.screen, round(time.time() - t0), "s", flush=True)
            chosen += [(i, a.seed, f) for i in ok[:a.cap]]
        res = []
        for k, r in enumerate(p.imap_unordered(scan_job, chosen, chunksize=1)):
            res.append(r)
            if (k + 1) % 10 == 0:
                print(k + 1, "/", len(chosen), "worlds,", round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["food"], r["i"]))
    summary = {}
    for f in FOODS:
        rr = [r for r in res if r["food"] == f]
        summary[str(f)] = {"screened": a.screen, "stable": sum(x["stable"] for x in st if x["food"] == f),
                           "worlds": len(rr), "with_reproducer": sum(r["reproducers"] > 0 for r in rr),
                           "verdicts": dict(Counter(v for r in rr for v in r["verdicts"])),
                           "heredity": dict(Counter(r["heredity"]["verdict"] for r in rr if r.get("heredity")))}
        print("food", f, summary[str(f)], flush=True)
    json.dump({"experiment": "E-31", "seed": a.seed, "foods": FOODS, "screen": a.screen, "cap": a.cap,
               "side": P.SIDE, "steps": P.STEPS, "pipeline_positive": gs, "stability": st, "worlds": res,
               "summary": summary, "seconds": round(time.time() - t0)}, open(a.out, "w"), indent=1)
    print("E31 DONE", flush=True)


if __name__ == "__main__":
    main()
