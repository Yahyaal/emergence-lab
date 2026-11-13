"""E-75 phase 4b (exploratory, not pre-registered; J-082): are "frozen" soups a state the soup reaches, or just its
random start? For every rule of phase 3 (24) and phase 4 pool A (24), soup 0 is replayed (same seed as the
original run) and the population is measured at rounds 0 (the random start), 50 and 200, unless it has
jumped by then (steps per pair > 100 at a checkpoint).

Per checkpoint: steps per pair of the last round (round 0: one round run on a copy), distinct programs, share of
the most common program and first instruction, and on 2,000 random pairs: median steps, fraction <= 4 steps,
fraction of runs that write into the partner, and copy hits (an 8-byte block of the runner appears in the partner,
as the census pre-filter).

    PYTHONPATH=. python scripts/sq_inert.py --workers 11 --out docs/data/experiments/2026-11-13-e75-inert.json
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))
from emergence.programs import subleq as Q  # noqa: E402

P3 = Path("docs/data/experiments/2026-11-13-e75-phase3.json")
P4 = Path("docs/data/experiments/2026-11-13-e75-phase4.json")
CHECK = (0, 50, 200)


def block_hit(p: np.ndarray, before: np.ndarray, after: np.ndarray, m: int = 8) -> bool:
    blocks = {p[i:i + m].tobytes() for i in range(len(p) - m + 1)}
    for i in range(len(after) - m + 1):
        w = after[i:i + m].tobytes()
        if w != before[i:i + m].tobytes() and w in blocks:
            return True
    return False


def measure(P: np.ndarray, R, seed: int) -> dict:
    _, cnt = np.unique(P, axis=0, return_counts=True)
    _, c4 = np.unique(P[:, :4], axis=0, return_counts=True)
    rng = np.random.default_rng(seed)
    idx, part = rng.choice(len(P), 2000, replace=False), rng.choice(len(P), 2000)
    st, wr, hit = [], 0, 0
    for i, j in zip(idx, part):
        t = np.concatenate([P[i], P[j]])
        t2, n = Q.run(t, R)
        st.append(n)
        wr += bool((t2[64:] != t[64:]).any())
        hit += block_hit(P[i], t[64:], t2[64:])
    st = np.array(st)
    return {"distinct": int(len(cnt)), "top_share": float(cnt.max() / len(P)), "top_first4_share": float(c4.max() / len(P)),
            "median_steps": float(np.median(st)), "frac_le4": float(np.mean(st <= 4)), "writes_partner": wr / 2000,
            "copy_hits": hit / 2000}


def job(arg) -> dict:
    phase, group, seed, code, jumped = arg
    R = Q.Rule.from_code(code)
    s = Q.Soup(R, n=2 ** 14, seed=seed)
    out = {"phase": phase, "group": group, "rule": str(R), "code": code, "seed": seed, "jumped_of_6": jumped, "at": {}}
    pre = Q.Soup(R, n=2 ** 14, seed=seed, programs=s.programs)
    pre.epoch()
    out["at"]["0"] = {"steps_pair": pre.last_steps / (pre.n // 2), **measure(s.programs, R, seed)}
    for e in range(1, max(CHECK) + 1):
        s.epoch()
        if e in CHECK:
            sp = s.last_steps / (s.n // 2)
            out["at"][str(e)] = {"steps_pair": sp, **measure(s.programs, R, seed + e)}
            if sp > 100:
                out["jumped_by"] = e
                break
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = []
    for k, q in enumerate(json.load(open(P3))["summary"]["rules"]):
        jobs.append((3, q["group"], 77000 + 10 * k, q["code"], q["jumped"]))
    for k, q in enumerate(json.load(open(P4))["summary"]["rules"]):
        if q["pool"] == "A":
            jobs.append((4, q["group"], 78000 + 10 * k, q["code"], q["jumped"]))
    with Pool(a.workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    json.dump({"experiment": "E-75", "phase": "4b-inert", "checkpoints": CHECK, "soups": res}, open(a.out, "w"), indent=1)
    for r in res:
        print(r["phase"], r["group"], r["rule"], r["jumped_of_6"],
              {e: (round(v["steps_pair"], 1), v["distinct"], round(v["frac_le4"], 2), v["copy_hits"]) for e, v in r["at"].items()})


if __name__ == "__main__":
    main()
