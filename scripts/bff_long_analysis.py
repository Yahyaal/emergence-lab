"""E-54 analysis (docs/data/e54-preregistration.md): early (T+2000) vs late (T+18000) verified replicators
of each jumped soup, invading kin-free backgrounds at T+10000 (primary) and T+20000 (secondary).

    python scripts/bff_long_analysis.py --workers 11 --out docs/data/experiments/2026-11-08-e54-long-soups.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from emergence.observatory import program_fitness as F
from emergence.observatory import replicators as RP
from emergence.programs import bff as B

RUN = Path("runs/e54")
K, MAX_TRY, EARLY, LATE, BGS, KIN_MAX, MIN_GROUP, REPS_INV, NPERM = 6, 40, 2000, 18000, (10000, 20000), 0.001, 2, 16, 10000


def same(p, q) -> bool:
    return bool((p == q).mean() >= 0.9 or (p == q[::-1]).mean() >= 0.9)


def kin(x: np.ndarray, P: np.ndarray) -> float:
    return float((((P == x).mean(1) >= 0.9) | ((P == x[::-1]).mean(1) >= 0.9)).mean())


def snap(seed: int, e: int) -> np.ndarray:
    return np.load(RUN / f"{seed}-{e}.npy")


def distinct_top(P: np.ndarray) -> list[np.ndarray]:
    out = []
    for prog, _ in B.top_programs(P, 3000):
        x = np.frombuffer(prog, np.uint8).copy()
        if not any(same(x, y) for y in out):
            out.append(x)
        if len(out) == MAX_TRY:
            break
    return out


def test(arg):
    seed, e, rank, h = arg
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    return arg, RP.replication_test(x, np.random.default_rng([54, seed, e, rank]))["verdict"]


def invade(arg):
    seed, group, idx, h, bg_e = arg
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    P = snap(seed, bg_e)
    r = F.invasion(x, P, np.random.default_rng([541, seed, int(group == "late"), idx, bg_e]), alts=[x[::-1]], reps=REPS_INV)
    return {"seed": seed, "group": group, "index": idx, "program": h, "background": bg_e, "kin": kin(x, P)} | r


def perm_D(cells: dict, rng) -> tuple[float, float]:
    D = sum(np.mean(l) - np.mean(e) for e, l in cells.values())
    null = []
    for _ in range(NPERM):
        tot = 0.0
        for e, l in cells.values():
            z = rng.permutation(np.concatenate([e, l]))
            tot += z[len(e):].mean() - z[:len(e)].mean()
        null.append(tot)
    return float(D), float((np.sum(np.array(null) >= D - 1e-12) + 1) / (NPERM + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    recs = [json.loads(p.read_text()) for p in sorted(RUN.glob("*.json"))]
    jumped = [(r["seed"], r["T"]) for r in recs if r["jumped"] and r["end"] >= r["T"] + 20000]
    # descriptive: replicator share among the top 40 distinct programs at every snapshot
    jobs = []
    for seed, T in jumped:
        for dt in range(2000, 20001, 2000):
            for rank, x in enumerate(distinct_top(snap(seed, T + dt))):
                jobs.append((seed, T + dt, rank, bytes(x).hex()))
    with Pool(a.workers) as pool:
        verdicts = pool.map(test, jobs, chunksize=4)
    share, cand = {}, {}
    for (seed, e, rank, h), v in verdicts:
        T = dict(jumped)[seed]
        d = share.setdefault(f"{seed}/{e - T}", [0, 0])
        d[0] += v == "replicator"
        d[1] += 1
        for g, dt in (("early", EARLY), ("late", LATE)):
            if e - T == dt and v == "replicator" and len(cand.setdefault((seed, g), [])) < K:
                cand[(seed, g)].append(h)
    inv_jobs = [(seed, g, i, h, T + b) for seed, T in jumped for g in ("early", "late")
                for i, h in enumerate(cand.get((seed, g), [])) for b in BGS]
    with Pool(a.workers) as pool:
        res = pool.map(invade, inv_jobs, chunksize=1)
    rng = np.random.default_rng(5400)
    out = {}
    for b in BGS:
        cells, dropped, excluded = {}, 0, []
        for seed, T in jumped:
            rr = [r for r in res if r["seed"] == seed and r["background"] == T + b]
            dropped += sum(r["kin"] >= KIN_MAX for r in rr)
            e = np.array([r["s"] for r in rr if r["group"] == "early" and r["kin"] < KIN_MAX])
            l = np.array([r["s"] for r in rr if r["group"] == "late" and r["kin"] < KIN_MAX])
            if len(e) >= MIN_GROUP and len(l) >= MIN_GROUP:
                cells[seed] = (e, l)
            else:
                excluded.append(seed)
        D, p = perm_D(cells, rng) if cells else (None, None)
        out[f"bg+{b}"] = {"D": D, "p": p, "soups": len(cells), "excluded_soups": excluded, "kin_dropped": dropped,
                          "delta": {str(s): round(float(np.mean(l) - np.mean(e)), 3) for s, (e, l) in cells.items()},
                          "mean_early": {str(s): round(float(np.mean(e)), 3) for s, (e, l) in cells.items()},
                          "mean_late": {str(s): round(float(np.mean(l)), 3) for s, (e, l) in cells.items()}}
    summary = {"jumped": dict(jumped), "new_soups_jumped": sum(1 for r in recs if r["jumped"] and r["seed"] >= 5400),
               "new_soups": sum(1 for r in recs if r["seed"] >= 5400), "primary": out["bg+10000"],
               "secondary_future": out["bg+20000"],
               "replicator_share_top40": {k: round(v[0] / v[1], 3) for k, v in share.items()},
               "candidates": {f"{s}/{g}": len(v) for (s, g), v in cand.items()}}
    json.dump({"experiment": "E-54", "summary": summary, "invasion": res,
               "verdicts": [[s, e, r, h, v] for (s, e, r, h), v in verdicts]}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E54 ANALYSIS DONE", flush=True)


if __name__ == "__main__":
    main()
