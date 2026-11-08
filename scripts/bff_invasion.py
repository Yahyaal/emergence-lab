"""E-52: invasion of E-49 replicators into their own soup at two times (docs/data/e52-preregistration.md).
E-53 (--e53): the same early (T+2000) and late (T+12000) candidates in kin-free backgrounds at T+4000,
T+9000 and a later time (T+20000; soup 5006: T+12500, its last snapshot) (docs/data/e53-preregistration.md).

    python scripts/bff_invasion.py --workers 2 --out docs/data/experiments/2026-11-08-e52-invasion.json
    python scripts/bff_invasion.py --e53 --workers 2 --out docs/data/experiments/2026-11-08-e53-invasion-kinfree.json
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
BGS, NULLS, NPERM, EXP = (2000, 12000), 6, 10000, 52


FUTURE = {901: 20000, 5006: 12500, 5010: 20000}


def bg(seed: int, dt: int) -> np.ndarray:
    if dt == -1:  # E-53 "future" background
        dt = FUTURE[seed]
    return np.load(f"runs/e47/{seed}-{T0[seed] + dt}.npy")


def kin(x: np.ndarray, P: np.ndarray) -> float:
    return float((((P == x).mean(1) >= 0.9) | ((P == x[::-1]).mean(1) >= 0.9)).mean())


def job(arg):
    kind, seed, t, idx, h, b = arg
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    P = bg(seed, b)
    r = F.invasion(x, P, np.random.default_rng([EXP, seed, t, idx, b % 100000, kind == "null"]), alts=[x[::-1]])
    return {"kind": kind, "seed": seed, "time": t, "index": idx, "background": b, "program": h, "kin": kin(x, P)} | r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", required=True)
    ap.add_argument("--e53", action="store_true")
    a = ap.parse_args()
    global BGS, NULLS, EXP
    if a.e53:
        BGS, NULLS, EXP = (4000, 9000, -1), 3, 53
    smp = {k: v for k, v in samples().items() if not a.e53 or k[1] in (2000, 12000)}
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
    kins = [r["kin"] for r in C]
    summary = {"max_candidate_kin": max(kins), "primary": {"D": round(float(D), 3), "p": p,
                           "delta": {f"{s}/bg{b}": round(float(l.mean() - e.mean()), 3) for (s, b), (e, l) in cells.items()}},
               "validity": {"races": len(races), "rho": round(float(v.statistic), 3), "p": float(v.pvalue)},
               "table": table}
    json.dump({"experiment": "E-53" if a.e53 else "E-52", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E52/E53 DONE", flush=True)


if __name__ == "__main__":
    main()
