"""E-52: invasion of E-49 replicators into their own soup at two times (docs/data/e52-preregistration.md).

    python scripts/bff_invasion.py --workers 2 --out docs/data/experiments/2026-11-08-e52-invasion.json
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from bff_fitness import E49, samples  # noqa: E402

from emergence.observatory import program_fitness as F  # noqa: E402

T0 = {901: 8750, 5006: 27500, 5010: 16750}
BGS, NULLS, NPERM = (2000, 12000), 6, 10000


def bg(seed: int, dt: int) -> np.ndarray:
    return np.load(f"runs/e47/{seed}-{T0[seed] + dt}.npy")


def job(arg):
    kind, seed, t, idx, h, b = arg
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    r = F.invasion(x, bg(seed, b), np.random.default_rng([52, seed, t, idx, b, kind == "null"]), alts=[x[::-1]])
    return {"kind": kind, "seed": seed, "time": t, "index": idx, "background": b, "program": h} | r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    smp = samples()
    jobs = [("cand", s, t, i, h, b) for (s, t, i), h in sorted(smp.items()) for b in BGS]
    nrng = np.random.default_rng(5200)
    for s in T0:
        for b in BGS:
            P = bg(s, b)
            for i, j in enumerate(nrng.choice(len(P), NULLS, replace=False)):
                jobs.append(("null", s, b, i, bytes(P[j]).hex(), b))
    with Pool(a.workers) as pool:
        res = []
        for n, r in enumerate(pool.imap_unordered(job, jobs), 1):
            res.append(r)
            print(json.dumps({"n": n, "of": len(jobs), "kind": r["kind"], "seed": r["seed"], "time": r["time"],
                              "bg": r["background"], "s": r["s"], "se": r["se"]}), flush=True)
    C = [r for r in res if r["kind"] == "cand"]
    cells = {}
    for s in T0:
        for b in BGS:
            e = np.array([r["s"] for r in C if r["seed"] == s and r["background"] == b and r["time"] == 2000])
            l = np.array([r["s"] for r in C if r["seed"] == s and r["background"] == b and r["time"] == 12000])
            cells[(s, b)] = (e, l)
    D = sum(l.mean() - e.mean() for e, l in cells.values())
    prng = np.random.default_rng(5201)
    null = []
    for _ in range(NPERM):
        tot = 0.0
        for e, l in cells.values():
            z = prng.permutation(np.concatenate([e, l]))
            tot += z[len(e):].mean() - z[:len(e)].mean()
        null.append(tot)
    p = float((np.sum(np.array(null) >= D - 1e-12) + 1) / (NPERM + 1))
    score = {}
    for r in C:
        score.setdefault(r["program"], []).append(r["s"])
    races = [r for r in json.load(open(E49))["results"] if r["n"] >= 8]
    dv = [np.mean(score[r["b"]]) - np.mean(score[r["a"]]) for r in races]
    v = spearmanr(dv, [r["b_share"] for r in races], alternative="greater")
    table = {}
    for s in T0:
        for b in BGS:
            for t in (2000, 6000, 12000):
                vals = [r["s"] for r in C if r["seed"] == s and r["background"] == b and r["time"] == t]
                if vals:
                    table[f"{s}/bg{b}/cand{t}"] = {"n": len(vals), "mean_s": round(float(np.mean(vals)), 3)}
            nv = [r["s"] for r in res if r["kind"] == "null" and r["seed"] == s and r["background"] == b]
            table[f"{s}/bg{b}/null"] = {"n": len(nv), "mean_s": round(float(np.mean(nv)), 3)}
    summary = {"primary": {"D": round(float(D), 3), "p": p,
                           "delta": {f"{s}/bg{b}": round(float(l.mean() - e.mean()), 3) for (s, b), (e, l) in cells.items()}},
               "validity": {"races": len(races), "rho": round(float(v.statistic), 3), "p": float(v.pvalue)},
               "table": table}
    json.dump({"experiment": "E-52", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E52 DONE", flush=True)


if __name__ == "__main__":
    main()
