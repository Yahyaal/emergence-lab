"""E-75 phase 4 (pre-registered, docs/data/e75-phase4-preregistration.md; D-058): does tile-replicator density
predict soups when rules jump only on <= 0 (pool A) or < 0 (pool B)?

Pools: n4 / s = +1 or -1 / W in {64, 32, 16, 8} / o 0..127, jump <= 0 (A) or < 0 (B), minus the 600 phase-1 rules.
  Stage 1  10^6-tile census of each pool rule. HIGH: D_T >= 20. LOW: D_T <= 5 and >= 50 tile hits per 10^6.
  Stage 2  seed-78 order per group: no replicator in the random-program census at 10^7, none at 10^8, and a
           10^7-tile re-census keeps the group. A: 12 HIGH + 12 LOW. B: 6 LOW + up to 6 HIGH.
  Stage 3  6 soups per rule, exactly as phase 3 (scripts/sq_phase3.soup_job), cache runs/e75-phase4.

    PYTHONPATH=. python scripts/sq_phase4.py --workers 11 --out docs/data/experiments/2026-11-13-e75-phase4.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parent))
from emergence.programs import inherit as I  # noqa: E402
from emergence.programs import subleq as Q  # noqa: E402
import sq_phase3 as P3  # noqa: E402
import sq_tiles as TL  # noqa: E402

RUN = Path("runs/e75-phase4")
HIGH, LOW, TILE_FLOOR, SOUPS = 20.0, 5.0, 50.0, 6
WANT = {("A", "HIGH"): 12, ("A", "LOW"): 12, ("B", "HIGH"): 6, ("B", "LOW"): 6}
JUMP = {"A": 0, "B": 1}  # J_NAMES: 0 '<=0', 1 '<0'


def pool_rules(j: int) -> list[int]:
    used = {r["code"] for r in json.load(open(P3.CENSUS))["rules"]}
    return [c for s in (1, -1) for W in (64, 32, 16, 8) for o in range(128)
            if (c := Q.Rule(n=4, j=j, s=s, W=W, o=o).code) not in used]


def group(t: dict) -> str | None:
    d = P3.dt(t)
    if d >= HIGH:
        return "HIGH"
    if d <= LOW and t["tile_hits"] * 1e6 / t["ntile"] >= TILE_FLOOR:
        return "LOW"
    return None


def screen(arg) -> dict:
    """No replicator in the random-program census at 10^7 and 10^8; the 10^7-tile re-census keeps the group."""
    code, pool, g = arg
    R = Q.Rule.from_code(code)
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    rng = np.random.default_rng([78, code])
    out = {"code": code, "rule": str(R), "pool": pool, "group": g, "pass": False}
    n7, h7 = Q.census_hits(R, 10 ** 7, 1, maxhits=2000)
    r7 = sum(I.inherits(h, run, rng)[0] for h in h7)
    out.update(hits7=n7, reps7=int(r7))
    if r7:
        return out
    n8, h8 = Q.census_hits(R, 10 ** 8, 3, maxhits=5000)
    r8 = sum(I.inherits(h, run, rng)[0] for h in h8)
    out.update(hits8=n8, verified8=len(h8), reps8=int(r8))
    if r8:
        return out
    t = TL.tile_rule((code, 2, 10 ** 7))
    out.update(dt2=P3.dt(t), tile2=t)
    out["pass"] = group(t) == g
    return out


def soup_job(arg) -> dict:
    P3.RUN = RUN
    return P3.soup_job(arg)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    pools = {p: pool_rules(j) for p, j in JUMP.items()}
    with Pool(a.workers) as pool:
        tiles = {p: pool.map(TL.tile_rule, [(c, 1, TL.NTILE) for c in v], chunksize=1) for p, v in pools.items()}
        groups = {}
        for p, ts in tiles.items():
            for t in ts:
                t["D_T"], t["group"] = P3.dt(t), group(t)
            for g in ("HIGH", "LOW"):
                groups[(p, g)] = [t["code"] for t in ts if t["group"] == g]
        print(json.dumps({f"{p}/{g}": len(v) for (p, g), v in groups.items()}), flush=True)
        rng = np.random.default_rng(78)
        sel, screened = {}, []
        for key in WANT:
            v = groups[key]
            order = [v[i] for i in rng.permutation(len(v))]
            sel[key], k = [], 0
            while len(sel[key]) < WANT[key] and k < len(order):
                batch = order[k:k + a.workers]
                k += len(batch)
                for r in pool.map(screen, [(c, *key) for c in batch], chunksize=1):
                    screened.append(r)
                    if r["pass"] and len(sel[key]) < WANT[key]:
                        sel[key].append(r["code"])
            print(json.dumps({"/".join(key): len(sel[key]), "screened": k}), flush=True)
        ranked = [(key, c) for key in WANT for c in sel[key]]
        jobs = [(78000 + 10 * k + i, c) for k, (_, c) in enumerate(ranked) for i in range(SOUPS)]
        res = pool.map(soup_job, jobs, chunksize=1)
    by = {r["seed"]: r for r in res}
    per = []
    for k, ((p, g), c) in enumerate(ranked):
        S = [by[78000 + 10 * k + i] for i in range(SOUPS)]
        per.append({"pool": p, "group": g, "code": c, "rule": str(Q.Rule.from_code(c)), "T": [s["T"] for s in S],
                    "jumped": sum(s["T"] is not None for s in S), "frozen": sum(s["frozen"] for s in S),
                    "steps_per_pair": [round(s["steps_per_pair"], 1) for s in S]})

    def stats(p: str) -> dict:
        rows = {g: [q for q in per if q["pool"] == p and q["group"] == g] for g in ("HIGH", "LOW")}
        j = {g: sum(q["jumped"] for q in v) for g, v in rows.items()}
        n = {g: SOUPS * len(v) for g, v in rows.items()}
        nonjump_low = [(q["jumped"], q["frozen"]) for q in rows["LOW"]]
        Ts = {g: [t for q in v for t in q["T"] if t is not None] for g, v in rows.items()}
        return {"rules": {g: len(v) for g, v in rows.items()}, "jumped": j, "of": n,
                "fisher_p": float(fisher_exact([[j["HIGH"], n["HIGH"] - j["HIGH"]], [j["LOW"], n["LOW"] - j["LOW"]]],
                                               alternative="greater").pvalue) if n["HIGH"] and n["LOW"] else None,
                "rules_jumping_4of6": {g: sum(q["jumped"] >= 4 for q in v) for g, v in rows.items()},
                "low_frozen_of_nonjumping": [sum(f for _, f in nonjump_low), sum(SOUPS - jj for jj, _ in nonjump_low)],
                "median_T": {g: float(np.median(v)) if v else None for g, v in Ts.items()}}

    A, B = stats("A"), stats("B")
    enough = A["rules"]["HIGH"] >= 6 and A["rules"]["LOW"] >= 6
    A["primary"] = ("undecided" if not enough else "pass" if (
        A["jumped"]["HIGH"] >= 0.75 * A["of"]["HIGH"] and A["jumped"]["LOW"] <= 0.25 * A["of"]["LOW"]
        and A["fisher_p"] < 0.01) else "fail")
    B["high_fraction_of_pool"] = len(groups[("B", "HIGH")]) / len(pools["B"])
    summary = {"pools": {p: len(v) for p, v in pools.items()},
               "groups": {f"{p}/{g}": len(v) for (p, g), v in groups.items()}, "A": A, "B": B, "rules": per}
    out = {"experiment": "E-75", "phase": 4, "tiles": tiles, "screened": screened, "summary": summary, "soups": res,
           "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "rules"}, indent=1))
    print("=== SENTINEL e75 phase4 DONE", flush=True)


if __name__ == "__main__":
    main()
