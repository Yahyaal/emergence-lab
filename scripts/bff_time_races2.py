"""E-49: later vs earlier verified replicators of the same soup (docs/data/e49-preregistration.md).

    python scripts/bff_time_races2.py --workers 11 --out docs/data/experiments/2026-11-08-e49-time-races.json
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from multiprocessing import Pool

import numpy as np
from scipy.stats import binomtest

from emergence.observatory import program_selection as PS
from emergence.observatory import replicators as RP
from emergence.programs import bff as B

E47 = "docs/data/experiments/2026-11-08-e47-turnover.json"
K, MAX_TRY, TIMES, REPS = 6, 40, (2000, 6000, 12000), 32
GAPS = ((2000, 6000), (6000, 12000), (2000, 12000))


def same(p, q) -> bool:
    return bool((p == q).mean() >= 0.9 or (p == q[::-1]).mean() >= 0.9)


def candidates(seed: int, epoch: int) -> list[np.ndarray]:
    P = np.load(f"runs/e47/{seed}-{epoch}.npy")
    out = []
    for prog, _ in B.top_programs(P, 2000):
        x = np.frombuffer(prog, np.uint8).copy()
        if not any(same(x, y) for y in out):
            out.append(x)
        if len(out) == MAX_TRY:
            break
    return out


def test(arg):
    seed, epoch, rank, hexp = arg
    x = np.frombuffer(bytes.fromhex(hexp), np.uint8).copy()
    return arg, RP.replication_test(x, np.random.default_rng([49, seed, epoch, rank]))["verdict"]


def race(arg):
    k, p = arg
    h = lambda x: np.frombuffer(bytes.fromhex(x), np.uint8).copy()
    a, b = h(p["a"]), h(p["b"])
    r = PS.compete_families(a, b, np.random.default_rng([49, k]), reps=REPS, a_alt=[a[::-1]], b_alt=[b[::-1]])
    s = [v for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    return {"pair": k} | p | r | {"b_share": round(sum(v > 0 for v in s) / len(s), 3) if s else None, "n": len(s)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    soups = [(q["seed"], q["species"][0]["first"]) for q in json.load(open(E47))["sequences"]]
    jobs = []
    for seed, T in soups:
        for dt in TIMES:
            for rank, x in enumerate(candidates(seed, T + dt)):
                jobs.append((seed, dt, rank, bytes(x).hex(), T))
    with Pool(a.workers) as pool:
        verdicts = pool.map(test, [(s, T + dt, r, h) for s, dt, r, h, T in jobs], chunksize=1)
    samples, tested = {}, {}
    for (s, dt, r, h, _T), (_, v) in zip(jobs, verdicts):
        tested.setdefault(f"{s}/{dt}", []).append(v)
        smp = samples.setdefault(f"{s}/{dt}", [])
        if v == "replicator" and len(smp) < K:
            smp.append(h)
    print(json.dumps({k: len(v) for k, v in samples.items()}), flush=True)
    pairs, orng = [], np.random.default_rng(4900)
    for seed, _ in soups:
        for t0, t1 in GAPS:
            for i, e in enumerate(samples[f"{seed}/{t0}"]):
                for j, l in enumerate(samples[f"{seed}/{t1}"]):
                    if not same(*(np.frombuffer(bytes.fromhex(z), np.uint8) for z in (e, l))):
                        pairs.append({"kind": "cross", "seed": seed, "gap": f"{t0}->{t1}", "a": e, "b": l, "i": i, "j": j})
        for dt in TIMES:
            smp = samples[f"{seed}/{dt}"]
            for i, j in combinations(range(len(smp)), 2):
                if orng.random() < 0.5:
                    i, j = j, i
                pairs.append({"kind": "same", "seed": seed, "gap": str(dt), "a": smp[i], "b": smp[j], "i": i, "j": j})
    print(f"{len(pairs)} pairs", flush=True)
    with Pool(a.workers) as pool:
        res = []
        for n, r in enumerate(pool.imap_unordered(race, list(enumerate(pairs))), 1):
            res.append(r)
            if n % 20 == 0:
                print(f"{n}/{len(pairs)}", flush=True)
    res.sort(key=lambda r: r["pair"])
    R = [r for r in res if r["n"] >= 8]
    prog = {}
    for r in R:
        if r["kind"] == "cross":
            prog.setdefault((r["seed"], r["gap"], r["j"]), []).append(r["b_share"])
    pm = {k: float(np.mean(v)) for k, v in prog.items()}
    up = sum(v > 0.5 for v in pm.values())
    summary = {"samples": {k: len(v) for k, v in samples.items()}, "tested": tested,
               "primary_program_level": {"later_ahead": up, "n": len(pm),
                                         "p": float(binomtest(up, len(pm), alternative="greater").pvalue) if pm else None}}
    for kind in ("cross", "same"):
        for key in [None] + [s for s, _ in soups] + ([g for g in (f"{x}->{y}" for x, y in GAPS)] if kind == "cross" else []):
            rr = [r for r in R if r["kind"] == kind and (key is None or r["seed"] == key or r["gap"] == key)]
            k = sum(r["b_share"] > 0.5 for r in rr)
            summary[f"{kind}/{key or 'all'}"] = {"pairs": len(rr), "b_ahead": k,
                                                 "p": float(binomtest(k, len(rr), alternative="greater").pvalue) if rr else None,
                                                 "mean_b_share": round(float(np.mean([r["b_share"] for r in rr])), 3) if rr else None}
    json.dump({"experiment": "E-49", "summary": summary, "program_means": {f"{k[0]}/{k[1]}/{k[2]}": round(v, 3) for k, v in pm.items()},
               "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "tested"}, indent=1))
    print("=== E49 DONE", flush=True)


if __name__ == "__main__":
    main()
