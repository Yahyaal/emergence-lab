"""E-30: reproduction and heredity in fed Flow-Lenia worlds with localized parameters.

Pre-registered in docs/data/e30-preregistration.md. For each random FlowLeniaPL rule (2-3
kernels, the paper's ranges, R 13) and each food level: a 128x128 world with N_PATCH patches
of random matter (side 20, A ~ U[0, 1]), each patch carrying its own kernel weights (the rule's
weights times U[0.5, 1.5] per kernel, a different "species" per patch), on a uniform food layer.
Run STEPS steps, then

* the birth detector (`births.scan`, 2 most common object types, two generations alone in a
  fed vacuum, background null = food alone);
* the heredity test (`heredity.test`, transplanted offspring vs parent, permutation null) on
  every world with a reproducer (none expected).

Pipeline positive: GrayScottTracer ("carried") worlds through the same births + heredity path.

Usage: python scripts/pl_scan.py --rules 100 --out docs/data/experiments/2026-11-07-e30-flow-lenia-pl.json --workers 11
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

from emergence.observatory import births as B
from emergence.observatory import heredity as H
from emergence.physics import FlowLeniaPL, GrayScottTracer

SIDE, STEPS, N_PATCH, PATCH = 128, 1500, 6, 20
FOODS = (0.0, 0.05)


def start(ph: FlowLeniaPL, rng: np.random.Generator) -> np.ndarray:
    A = np.full((SIDE, SIDE), ph.food)
    h = np.ones((len(ph.kernels), SIDE, SIDE)) * ph._h[:, None, None]
    for r, c in rng.integers(0, SIDE - PATCH, size=(N_PATCH, 2)):
        A[r:r + PATCH, c:c + PATCH] = rng.random((PATCH, PATCH))
        h[:, r:r + PATCH, c:c + PATCH] = (ph._h * rng.uniform(0.5, 1.5, len(ph._h)))[:, None, None]
    return ph.localize(A, h)


def _brief(r):
    return {k: r.get(k) for k in ("verdict", "parent_mass", "background_copies", "attractor")} | (
        {"gen1": {k: v for k, v in r["gen1"].items() if k != "series"}} if r.get("gen1") else {})


def world(ph, s, rng):
    objs = B.find(ph, s)
    f = B.field(ph, s)
    out = {"objects": len(objs), "occupied": round(float((f >= 26).mean()), 4),
           "masses": sorted((round(o["mass"], 1) for o in objs), reverse=True)[:8]}
    if not objs:
        return out | {"verdicts": [], "reproducers": 0}
    res = B.scan(ph, s, rng, max_candidates=2)
    out |= {"verdicts": res["verdicts"], "reproducers": res["reproducers"],
            "hits": [_brief(r) for r in res["results"] if r["verdict"] != "no reproduction"]}
    if res["reproducers"]:
        h = H.test(ph, s, rng)
        out["heredity"] = {k: v for k, v in h.items() if k != "family_data"}
    return out


def pl_job(args):
    i, food, seed = args
    t0 = time.time()
    rng = np.random.default_rng([seed, i])
    base = FlowLeniaPL.random(rng)  # the rule and the start depend on i only, not on food
    ph = FlowLeniaPL(base.kernels, base.R, food)
    s = start(ph, rng)
    m0 = float(s[0].sum())
    for _ in range(STEPS):
        s = ph.step(s)
    out = {"i": i, "food": food, "rule": ph.label(), "mass_drift": float(s[0].sum() / m0 - 1)}
    return out | world(ph, s, rng) | {"seconds": round(time.time() - t0, 1)}


def gs_job(seed):
    ph = GrayScottTracer(mode="carried")
    rng = np.random.default_rng([seed, 30])
    s = ph.vacuum((SIDE, SIDE))
    for j, (r, c) in enumerate(rng.integers(0, SIDE - 12, size=(6, 2))):
        v = 0.25 + 0.01 * rng.random((12, 12))
        s[0, r:r + 12, c:c + 12], s[1, r:r + 12, c:c + 12] = 0.5, v
        s[2, r:r + 12, c:c + 12] = v * (0.1 + 0.16 * j)
    for _ in range(STEPS):
        s = ph.step(s)
    return {"seed": seed} | world(ph, s, rng)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", type=int, default=100)
    ap.add_argument("--seed", type=int, default=30)
    ap.add_argument("--gs", type=int, default=4)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    with Pool(a.workers or None) as p:
        gs = p.map(gs_job, range(a.gs), chunksize=1)
        print("pipeline positive (Gray-Scott tracer): reproducer in", sum(g["reproducers"] > 0 for g in gs), "/", a.gs,
              "; heredity in", sum((g.get("heredity") or {}).get("verdict") == "heredity" for g in gs), flush=True)
        jobs = [(i, f, a.seed) for i in range(a.rules) for f in FOODS]
        res = []
        for k, r in enumerate(p.imap_unordered(pl_job, jobs, chunksize=1)):
            res.append(r)
            if (k + 1) % 20 == 0:
                print(k + 1, "worlds,", round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: (r["i"], r["food"]))
    summary = {}
    for f in FOODS:
        rr = [r for r in res if r["food"] == f]
        summary[str(f)] = {"worlds": len(rr), "with_reproducer": sum(r["reproducers"] > 0 for r in rr),
                           "verdicts": dict(Counter(v for r in rr for v in r["verdicts"])),
                           "heredity": dict(Counter(r["heredity"]["verdict"] for r in rr if r.get("heredity"))),
                           "max_mass_drift": max(abs(r["mass_drift"]) for r in rr) if f == 0 else None}
        print("food", f, summary[str(f)], flush=True)
    json.dump({"experiment": "E-30", "seed": a.seed, "rules": a.rules, "foods": FOODS, "side": SIDE, "steps": STEPS,
               "pipeline_positive": gs, "worlds": res, "summary": summary, "seconds": round(time.time() - t0)},
              open(a.out, "w"), indent=1)
    print("E30 DONE", flush=True)


if __name__ == "__main__":
    main()
