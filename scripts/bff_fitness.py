"""E-51: growth-rate fitness of the E-49 verified replicators (docs/data/e51-preregistration.md).

    python scripts/bff_fitness.py --workers 2 --out docs/data/experiments/2026-11-08-e51-growth-rates.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np
from scipy.stats import spearmanr

from emergence.observatory import program_fitness as F
from emergence.programs import bff as B

E49 = "docs/data/experiments/2026-11-08-e49-time-races.json"
TIMES = (2000, 6000, 12000)
REPS_R, REPS_H, NPERM = 24, 8, 10000


def samples() -> dict:
    """(seed, time, index) -> hex, from the E-49 race list."""
    out = {}
    for r in json.load(open(E49))["results"]:
        if r["kind"] == "cross":
            t0, t1 = map(int, r["gap"].split("->"))
            out[(r["seed"], t0, r["i"])] = r["a"]
            out[(r["seed"], t1, r["j"])] = r["b"]
        else:
            t = int(r["gap"])
            out[(r["seed"], t, r["i"])] = r["a"]
            out[(r["seed"], t, r["j"])] = r["b"]
    return out


def assay(arg):
    key, h = arg
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    rng = np.random.default_rng([51, *[int(k) for k in key[:3]]] if key[0] != "hand" else [51, 0])
    gr = F.growth_rate(x, rng, alts=[x[::-1]], bg="random", reps=REPS_R)
    gh = F.growth_rate(x, rng, alts=[x[::-1]], bg="halting", reps=REPS_H)
    return key, h, gr, gh


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    smp = samples()
    jobs = sorted(smp.items()) + [(("hand", 0, 0), bytes(B.REPLICATOR).hex())]
    with Pool(a.workers) as pool:
        res = pool.map(assay, jobs, chunksize=1)
    R = {k: (h, gr, gh) for k, h, gr, gh in res}
    seeds = sorted({k[0] for k in smp})
    # primary: S = sum of per-soup Spearman rho(time, r), within-soup permutation
    data = {s: (np.array([k[1] for k in smp if k[0] == s]), np.array([R[k][1]["r"] for k in smp if k[0] == s]))
            for s in seeds}
    rho = {s: float(spearmanr(t, r).statistic) for s, (t, r) in data.items()}
    S = sum(rho.values())
    prng = np.random.default_rng(5100)
    null = [sum(float(spearmanr(prng.permutation(t), r).statistic) for t, r in data.values()) for _ in range(NPERM)]
    p_primary = float((np.sum(np.array(null) >= S - 1e-12) + 1) / (NPERM + 1))
    # validity: delta r vs race share
    races = [r for r in json.load(open(E49))["results"] if r["n"] >= 8]
    key_of = {h: k for k, h in smp.items()}
    dr = [R[key_of[r["b"]]][1]["r"] - R[key_of[r["a"]]][1]["r"] for r in races]
    share = [r["b_share"] for r in races]
    v = spearmanr(dr, share, alternative="greater")
    # secondary: pairwise differences, same vs cross time
    diff = {"same": [0, 0], "cross": [0, 0]}
    for s in seeds:
        ks = sorted(k for k in smp if k[0] == s)
        for i, k1 in enumerate(ks):
            for k2 in ks[i + 1:]:
                c = F.compare(R[k1][1], R[k2][1])
                d = diff["same" if k1[1] == k2[1] else "cross"]
                d[0] += c["p"] < 0.05
                d[1] += 1
    per_time = {f"{s}/{t}": {"n": int(np.sum(data[s][0] == t)),
                             "mean_r": round(float(np.mean(data[s][1][data[s][0] == t])), 4)} for s in seeds for t in TIMES}
    summary = {"primary": {"S": round(S, 3), "rho": {str(s): round(v_, 3) for s, v_ in rho.items()}, "p": p_primary},
               "validity": {"races": len(races), "rho": round(float(v.statistic), 3), "p": float(v.pvalue)},
               "pairs_differ_p05": {k: {"differ": d[0], "pairs": d[1]} for k, d in diff.items()},
               "per_time": per_time, "hand_written": {"r_random": R[("hand", 0, 0)][1]["r"],
                                                     "r_halting": R[("hand", 0, 0)][2]["r"]},
               "halting_r_range": [min(g[2]["r"] for g in R.values()), max(g[2]["r"] for g in R.values())]}
    json.dump({"experiment": "E-51", "summary": summary,
               "programs": [{"seed": k[0], "time": k[1], "index": k[2], "program": h, "random": gr, "halting": gh}
                            for k, (h, gr, gh) in sorted(R.items(), key=lambda z: str(z[0]))]},
              open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E51 DONE", flush=True)


if __name__ == "__main__":
    main()
