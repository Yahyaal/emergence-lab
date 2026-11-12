"""E-75 phase 2 (docs/data/e75-phase2-protocol.md): re-census of candidate rules at 10^8 programs (D-056), then
pilot soups in 4 F and 4 C rules, 2 soups each.

    PYTHONPATH=. python scripts/sq_pilot.py --workers 11 --out docs/data/experiments/2026-11-12-e75-pilot.json

Stage 1 (re-census): 6 F candidates (F at 10^7 with >= 3 replicators) and 6 C candidates (C at 10^7 with >= 100
hits; n = 4 and jump 'always', matched to the F rules) are drawn in a seed-76 order and censused again at 10^8
random programs (seed 3, up to 5,000 hits verified). The first 4 of each that keep their class are used.
Stage 2 (soups): 2^14 programs of 64 bytes, 8,192 steps, mutation 0.00024, up to 16,000 rounds; every 50 rounds,
the 40 most common programs are tested by inheritance (D-055, primary), by the whole-program copy test with
guard (`subleq.classify`) and HOE (reported beside it). Jump T = first checkpoint with >= 1 inheriting program
whose checkpoint 1,000 rounds later has >= 10 (the D-050 rule with the D-055 test). A soup stops once T is known.
Soups are cached in runs/e75-pilot/.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))
from emergence.programs import inherit as I  # noqa: E402
from emergence.programs import subleq as Q  # noqa: E402

CENSUS = Path("docs/data/experiments/2026-11-12-e75-census.json")
RUN = Path("runs/e75-pilot")
NPROG2, MAXHITS2, CAND, USE = 100_000_000, 5000, 6, 4
N, WAIT, EVERY, AFTER, MIN_COP = 2 ** 14, 16_000, 50, 1000, 10
SOUPS = 2


def candidates() -> dict:
    rules = json.load(open(CENSUS))["rules"]
    F = [r for r in rules if r["class"] == "F" and r["replicators"] >= 3]
    C = [r for r in rules if r["class"] == "C" and r["hits"] >= 100 and r["n"] == 4 and r["j"] == 3]
    rng = np.random.default_rng(76)
    return {"F": [F[i] for i in rng.permutation(len(F))[:CAND]], "C": [C[i] for i in rng.permutation(len(C))[:CAND]]}


def recensus(code: int) -> dict:
    R = Q.Rule.from_code(code)
    t0 = time.time()
    n, hits = Q.census_hits(R, NPROG2, 3, maxhits=MAXHITS2)
    rng = np.random.default_rng([76, code])
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    reps = sum(I.inherits(h, run, rng)[0] for h in hits)
    return {"code": code, "rule": str(R), "hits": n, "verified": len(hits), "replicators": int(reps),
            "class": "F" if reps else "C" if n else "none", "sec": round(time.time() - t0)}


def soup_job(arg) -> dict:
    seed, code = arg
    path = RUN / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    R = Q.Rule.from_code(code)
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    soup = Q.Soup(R, n=N, seed=seed)
    inh, series, T = {}, [], None
    while soup.epochs < WAIT and T is None:
        soup.epoch()
        e = soup.epochs
        if e % EVERY:
            continue
        X = Q.distinct_top(soup.programs)
        inh[e] = I.count(X, run, 7600 + seed + e)
        wp = int((Q.classify(X, R, seed=seed + e)[0] > 0).sum())
        h = float(Q.high_order_entropy(soup.programs))
        series.append([e, inh[e], wp, round(h, 3)])
        if inh[e] >= MIN_COP and inh.get(e - AFTER, 0) >= 1:
            T = e - AFTER
    top = [p.tobytes().hex() for p in Q.distinct_top(soup.programs, 3)]
    res = {"seed": seed, "code": code, "rule": str(R), "T": T, "end": soup.epochs, "series": series, "top3": top,
           "sec": round(time.time() - t0)}
    RUN.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res))
    print(json.dumps({"seed": seed, "rule": str(R), "T": T, "end": soup.epochs, "sec": res["sec"]}), flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    cand = candidates()
    order = [r["code"] for r in cand["F"] + cand["C"]]
    with Pool(a.workers) as pool:
        rc = dict(zip(order, pool.map(recensus, order, chunksize=1)))
        print(json.dumps({k: [(r["rule"], rc[r["code"]]["class"], rc[r["code"]]["replicators"]) for r in v]
                          for k, v in cand.items()}), flush=True)
        sel = {k: [r["code"] for r in v if rc[r["code"]]["class"] == k][:USE] for k, v in cand.items()}
        jobs = [(7600 + 10 * k + i, code) for k, code in enumerate(sel["F"] + sel["C"]) for i in range(SOUPS)]
        res = pool.map(soup_job, jobs, chunksize=1)
    by = {r["seed"]: r for r in res}
    per = []
    for k, code in enumerate(sel["F"] + sel["C"]):
        Ts = [by[7600 + 10 * k + i]["T"] for i in range(SOUPS)]
        per.append({"class": "F" if code in sel["F"] else "C", "code": code, "rule": str(Q.Rule.from_code(code)),
                    "T": Ts})
    jumped = {c: sum(t is not None for p in per if p["class"] == c for t in p["T"]) for c in ("F", "C")}
    summary = {"selected": {k: [str(Q.Rule.from_code(c)) for c in v] for k, v in sel.items()}, "jumped": jumped,
               "of": {c: SOUPS * len(sel[c]) for c in ("F", "C")}, "gate": jumped["F"] >= 1, "rules": per}
    out = {"experiment": "E-75", "phase": 2, "candidates": {k: [r["code"] for r in v] for k, v in cand.items()},
           "recensus": list(rc.values()), "summary": summary, "soups": res, "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== SENTINEL e75 pilot DONE", flush=True)


if __name__ == "__main__":
    main()
