"""E-78 exploratory (post hoc, NOT pre-registered): the pre-registered clustering statistic is defined only for
families holding >= 1% of the soup, and after 2,000 rounds the S arms have none, so it is undefined there. This
script measures structure without that threshold, at every snapshot of every arm:

* kin_nbr: share of lattice-neighbour pairs (right and down neighbours, on the arm's storage grid) that are
  >= 90% identical in either orientation; kin_rand: the same for 65,536 random pairs (seeded). In M the storage
  order has no meaning, so kin_nbr ~ kin_rand there (the null).
* families at a lower threshold (>= 0.1% of the soup = 66 programs), greedy as bff_spatial.families; top share.

    python scripts/e78_explore.py --workers 11 --out docs/data/experiments/2026-11-15-e78-explore.json
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_spatial as BS  # noqa: E402
import e78_run as R  # noqa: E402


def kin_pairs(A: np.ndarray, Bm: np.ndarray) -> float:
    return float((((A == Bm).mean(1) >= 0.9) | ((A == Bm[:, ::-1]).mean(1) >= 0.9)).mean())


def one(arg):
    seed, arm, e = arg
    P = np.load(R.RUN / f"{seed}-{arm}-{e}.npy")
    w = BS.SIDE
    G = P.reshape(w, w, 64)
    right = kin_pairs(P, np.roll(G, -1, 1).reshape(-1, 64))
    down = kin_pairs(P, np.roll(G, -1, 0).reshape(-1, 64))
    rng = np.random.default_rng([78, 9, seed, e])
    i, j = rng.integers(0, len(P), len(P)), rng.integers(0, len(P), len(P))
    fam = BS.families(P, min_share=0.001, max_reps=400)
    return {"seed": seed, "arm": arm, "epoch": e, "dt": e - BS.JUMPED[seed] - BS.FORK_DT,
            "kin_nbr": round((right + down) / 2, 4), "kin_rand": round(kin_pairs(P[i], P[j]), 4),
            "families_ge01pct": len(fam), "top_share": round(fam[0]["count"] / len(P), 4) if fam else 0.0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = [(s, arm, BS.JUMPED[s] + BS.FORK_DT + dt) for s in BS.JUMPED for arm in ("M", "S", "Mp")
            for dt in range(0, R.H + 1, R.SNAP)]
    with Pool(a.workers) as pool:
        res = pool.map(one, jobs, chunksize=2)
    summ = {}
    for arm in ("M", "S", "Mp"):
        fin = [r for r in res if r["arm"] == arm and r["dt"] == R.H]
        summ[arm] = {k: [r[k] for r in fin] for k in ("seed", "kin_nbr", "kin_rand", "families_ge01pct", "top_share")}
    Path(a.out).write_text(json.dumps({"experiment": "E-78 exploratory structure (post hoc)", "final": summ,
                                       "rows": res}, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
