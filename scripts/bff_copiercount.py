"""E-71 (docs/data/e71-preregistration.md): does the number of self-sufficient copiers of an F rule predict how
fast its soups make replicators? Confirmation of E-70's exploratory rho = -0.80 on fresh rules: every F rule of
the E-70 census (variants v1-v5) that E-70 did not run soups in. 8 soups per rule, D-050 jump criterion with
checkpoints every 50 rounds (E-70: 250) for a finer jump time; everything else as E-70.

    python scripts/bff_copiercount.py --workers 11 --out docs/data/experiments/2026-11-10-e71-copiercount.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import bff_tapelength as T  # noqa: E402

CENSUS = "docs/data/experiments/2026-11-09-e70-census.json"
E70 = "docs/data/experiments/2026-11-09-e70-soups.json"
SOUPS, EVERY, NPERM = 8, 50, 100_000


def fresh_rules() -> list[dict]:
    c = json.load(open(CENSUS))
    used = {(v, h) for _, v, h in json.load(open(E70))["rules"]}
    return [r for r in c["rules"] if r["class"] == "F" and r["v"] >= 1 and (r["v"], r["h"]) not in used]


def code(v: int, h: int) -> int:
    return h + 65536 * v


def med_T(ts: list) -> float:
    return float(np.median([t if t is not None else T.WAIT for t in ts]))


def within_stat(x, y, groups) -> float:
    """Sum over variants of the within-variant Spearman rho (variants with >= 3 rules and some spread)."""
    s = 0.0
    for g in sorted(set(groups)):
        i = [k for k, gg in enumerate(groups) if gg == g]
        if len(i) >= 3 and len({x[k] for k in i}) > 1 and len({y[k] for k in i}) > 1:
            s += spearmanr([x[k] for k in i], [y[k] for k in i])[0]
    return s


def perm_tests(x, y, groups, seed=71) -> dict:
    rng = np.random.default_rng(seed)
    rho = spearmanr(x, y)[0]
    w = within_stat(x, y, groups)
    y = np.asarray(y, float)
    idx = {g: [k for k, gg in enumerate(groups) if gg == g] for g in set(groups)}
    pooled_le = within_le = 0
    for _ in range(NPERM):
        yp = rng.permutation(y)
        pooled_le += spearmanr(x, yp)[0] <= rho
        yw = y.copy()
        for i in idx.values():
            yw[i] = rng.permutation(y[i])
        within_le += within_stat(x, list(yw), groups) <= w
    return {"rho": float(rho), "p_one_sided_perm": (pooled_le + 1) / (NPERM + 1),
            "within_sum_rho": float(w), "within_p_one_sided_perm": (within_le + 1) / (NPERM + 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    rules = fresh_rules()
    T.RUN, T.EVERY = Path("runs/e71"), EVERY
    T.RUN.mkdir(parents=True, exist_ok=True)
    jobs = [(7100 + 10 * k + i, 64, code(r["v"], r["h"])) for k, r in enumerate(rules) for i in range(SOUPS)]
    with Pool(a.workers) as pool:
        res = pool.map(T.soup_job, jobs, chunksize=1)
    per = []
    for r in rules:
        ts = [s["T"] for s in res if s["h1"] == code(r["v"], r["h"])]
        per.append({"v": r["v"], "h": r["h"], "self_sufficient": r["self_sufficient"], "copiers": r["copiers"],
                    "T": ts, "jumped": sum(t is not None for t in ts), "median_T": med_T(ts)})
    ss = [p["self_sufficient"] for p in per]
    cp = [p["copiers"] for p in per]
    mt = [p["median_T"] for p in per]
    g = [p["v"] for p in per]
    prim = perm_tests(ss, mt, g)
    sec_cop = perm_tests(cp, mt, g, seed=72)
    frac = [p["self_sufficient"] / p["copiers"] for p in per]
    sec_frac = perm_tests(frac, mt, g, seed=73)
    v1 = {p["h"]: p for p in per if p["v"] == 1}
    low = [v1[h]["median_T"] for h in (60, 68) if h in v1]
    high = [v1[h]["median_T"] for h in (63, 65, 66, 67) if h in v1]
    nj, ns = sum(p["jumped"] for p in per), SOUPS * len(per)
    summary = {
        "rules": len(per), "soups": ns, "jumped": nj,
        "primary1_pooled": prim | {"pass": prim["rho"] <= -0.4 and prim["p_one_sided_perm"] < 0.01},
        "primary2_within_variant": {"within_sum_rho": prim["within_sum_rho"],
                                    "p_one_sided_perm": prim["within_p_one_sided_perm"],
                                    "pass": prim["within_sum_rho"] < 0 and prim["within_p_one_sided_perm"] < 0.05},
        "secondary_jump_rate_ge_75pct": nj >= 0.75 * ns,
        "secondary_all_copiers": sec_cop, "secondary_selfsufficient_fraction": sec_frac,
        "secondary_v1_low_vs_high": {"low_60_68": low, "high_63_67": high,
                                     "low_slower": bool(low and high and min(low) > max(high))},
        "seconds": round(time.time() - t0)}
    json.dump({"experiment": "E-71", "summary": summary, "per_rule": per, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== SENTINEL e71 DONE", flush=True)


if __name__ == "__main__":
    main()
