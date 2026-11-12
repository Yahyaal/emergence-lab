"""E-75 phase 3 (pre-registered, docs/data/e75-phase3-preregistration.md): does tile-replicator density predict
which copying SUBLEQ-family rules make replicators in soups (D-057)?

Pool: rules n4 / jump always / s = +1 or -1 / W in {64, 32, 16, 8} / o 0..127 (1,024 rules), minus the 600
phase-1 census rules (which include the 8 pilot rules).
  Stage 1  tile census of the pool (10^6 tiles each; scripts/sq_tiles.tile_rule). D_T = estimated tile
           replicators per 10^6 tiles. HIGH: D_T >= 20; LOW: D_T <= 5 (0 included).
  Stage 2  candidates in a seed-77 order per group are screened with the random-program census at 10^7
           (must be C with >= 100 hits), then confirmed at 10^8 (must stay C; D-056) and by a second tile
           census at 10^7 tiles (must stay in its group). The first 12 per group that pass are used.
  Stage 3  6 soups per rule (144): as the phase-2 pilot (2^14 programs, 8,192 steps, <= 16,000 rounds,
           inheritance on the top 40 every 50 rounds, jump T as D-050 with D-055). Also recorded: mean steps
           per pair (a soup is *frozen* at the end if <= 4).

    PYTHONPATH=. python scripts/sq_phase3.py --workers 11 --out docs/data/experiments/2026-11-13-e75-phase3.json
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
import sq_tiles as TL  # noqa: E402

CENSUS = Path("docs/data/experiments/2026-11-12-e75-census.json")
RUN = Path("runs/e75-phase3")
HIGH, LOW, PER, SOUPS = 20.0, 5.0, 12, 6
N, WAIT, EVERY, AFTER, MIN_COP, FROZEN = 2 ** 14, 16_000, 50, 1000, 10, 4.0


def pool_rules() -> list[int]:
    used = {r["code"] for r in json.load(open(CENSUS))["rules"]}
    out = []
    for s in (1, -1):
        for W in (64, 32, 16, 8):
            for o in range(128):
                c = Q.Rule(n=4, j=3, s=s, W=W, o=o).code
                if c not in used:
                    out.append(c)
    return out


def dt(t: dict) -> float:
    return (t["tile_replicators"] / t["tile_verified"] * t["tile_hits"] * 1e6 / t["ntile"]) if t["tile_verified"] else 0.0


def screen(arg) -> dict:
    """Random-program census at 10^7 (then 10^8 if C with >= 100 hits) and a 10^7-tile re-census."""
    code, group = arg
    R = Q.Rule.from_code(code)
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    rng = np.random.default_rng([77, code])
    out = {"code": code, "rule": str(R), "group": group, "pass": False}
    n7, h7 = Q.census_hits(R, 10 ** 7, 1, maxhits=2000)
    r7 = sum(I.inherits(h, run, rng)[0] for h in h7)
    out.update(hits7=n7, reps7=int(r7))
    if r7 or n7 < 100:
        return out
    n8, h8 = Q.census_hits(R, 10 ** 8, 3, maxhits=5000)
    r8 = sum(I.inherits(h, run, rng)[0] for h in h8)
    out.update(hits8=n8, verified8=len(h8), reps8=int(r8))
    if r8:
        return out
    t = TL.tile_rule((code, 2, 10 ** 7))
    out.update(dt2=dt(t), tile2=t)
    out["pass"] = (dt(t) >= HIGH) if group == "HIGH" else (dt(t) <= LOW)
    return out


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
        inh[e] = I.count(X, run, 7700 + seed + e)
        wp = int((Q.classify(X, R, seed=seed + e)[0] > 0).sum())
        series.append([e, inh[e], wp, round(soup.last_steps / (N // 2), 1)])
        if inh[e] >= MIN_COP and inh.get(e - AFTER, 0) >= 1:
            T = e - AFTER
    steps = soup.last_steps / (N // 2)
    res = {"seed": seed, "code": code, "rule": str(R), "T": T, "end": soup.epochs, "steps_per_pair": steps,
           "frozen": T is None and steps <= FROZEN, "series": series,
           "top3": [p.tobytes().hex() for p in Q.distinct_top(soup.programs, 3)], "sec": round(time.time() - t0)}
    RUN.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res))
    print(json.dumps({k: res[k] for k in ("seed", "rule", "T", "end", "frozen", "sec")}), flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    codes = pool_rules()
    with Pool(a.workers) as pool:
        tiles = pool.map(TL.tile_rule, [(c, 1, TL.NTILE) for c in codes], chunksize=1)
        for t in tiles:
            t["D_T"] = dt(t)
        groups = {"HIGH": [t["code"] for t in tiles if t["D_T"] >= HIGH],
                  "LOW": [t["code"] for t in tiles if t["D_T"] <= LOW]}
        rng = np.random.default_rng(77)
        order = {g: [v[i] for i in rng.permutation(len(v))] for g, v in groups.items()}
        print(json.dumps({"pool": len(codes), **{g: len(v) for g, v in groups.items()}}), flush=True)
        sel, screened = {"HIGH": [], "LOW": []}, []
        for g in ("HIGH", "LOW"):
            k = 0
            while len(sel[g]) < PER and k < len(order[g]):
                batch = order[g][k:k + a.workers]
                k += len(batch)
                for r in pool.map(screen, [(c, g) for c in batch], chunksize=1):
                    screened.append(r)
                    if r["pass"] and len(sel[g]) < PER:
                        sel[g].append(r["code"])
            print(json.dumps({g: len(sel[g]), "screened": k}), flush=True)
        ranked = sel["HIGH"] + sel["LOW"]
        jobs = [(77000 + 10 * k + i, c) for k, c in enumerate(ranked) for i in range(SOUPS)]
        res = pool.map(soup_job, jobs, chunksize=1)
    by = {r["seed"]: r for r in res}
    per = []
    for k, c in enumerate(ranked):
        S = [by[77000 + 10 * k + i] for i in range(SOUPS)]
        per.append({"group": "HIGH" if c in sel["HIGH"] else "LOW", "code": c, "rule": str(Q.Rule.from_code(c)),
                    "T": [s["T"] for s in S], "jumped": sum(s["T"] is not None for s in S),
                    "frozen": sum(s["frozen"] for s in S)})
    j = {g: sum(p["jumped"] for p in per if p["group"] == g) for g in ("HIGH", "LOW")}
    n = {g: SOUPS * len(sel[g]) for g in ("HIGH", "LOW")}
    p = float(fisher_exact([[j["HIGH"], n["HIGH"] - j["HIGH"]], [j["LOW"], n["LOW"] - j["LOW"]]],
                           alternative="greater").pvalue) if n["HIGH"] and n["LOW"] else None
    enough = len(sel["HIGH"]) >= 6 and len(sel["LOW"]) >= 6
    primary = {"jumped": j, "of": n, "fisher_p": p, "enough_rules": enough,
               "pass": bool(enough and j["HIGH"] >= 0.75 * n["HIGH"] and j["LOW"] <= 0.25 * n["LOW"] and p < 0.01)}
    rules_jump = {g: sum(q["jumped"] >= 4 for q in per if q["group"] == g) for g in ("HIGH", "LOW")}
    nonjump = [s for s in res if s["T"] is None]
    summary = {"pool": len(codes), "groups": {g: len(v) for g, v in groups.items()}, "selected": {g: len(v) for g, v in sel.items()},
               "primary": primary, "rules_jumping_4of6": rules_jump,
               "frozen_of_nonjumping": [sum(s["frozen"] for s in nonjump), len(nonjump)],
               "median_T": {g: float(np.median([t for q in per if q["group"] == g for t in q["T"] if t is not None] or [np.nan]))
                            for g in ("HIGH", "LOW")}, "rules": per}
    out = {"experiment": "E-75", "phase": 3, "tiles": tiles, "screened": screened, "summary": summary, "soups": res,
           "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "rules"}, indent=1))
    print("=== SENTINEL e75 phase3 DONE", flush=True)


if __name__ == "__main__":
    main()
