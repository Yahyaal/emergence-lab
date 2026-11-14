"""E-75 phase 6 analysis: the product census against the pre-registered predictions
(docs/data/e75-phase6-preregistration.md).

    PYTHONPATH=. python scripts/sq_products_report.py docs/data/experiments/2026-11-13-e75-products.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

P3 = Path("docs/data/experiments/2026-11-13-e75-phase3.json")
P4 = Path("docs/data/experiments/2026-11-13-e75-phase4.json")


def rho(x, y, alt="two-sided"):
    r = spearmanr(x, y, alternative=alt)
    return float(r.statistic), float(r.pvalue)


def main(path: str) -> dict:
    d = json.load(open(path))
    rs = d["rules"]
    T = {}
    for f in (P3, P4):
        for q in json.load(open(f))["summary"]["rules"]:
            T[q["code"]] = [t for t in q["T"] if t is not None]
    out = {"table": [], "pred": {}}
    for r in sorted(rs, key=lambda r: (r["pool"], -r["R_P"])):
        out["table"].append({k: r[k] for k in ("pool", "group", "rule", "jumped", "D_T", "R_P", "R_null",
                                               "informative", "null", "from_replicator", "side", "hits",
                                               "tested")})
    pools = {p: [r for r in rs if r["pool"] == p] for p in ("always", "A", "B")}
    cor = {}
    for name, x in [("all", rs)] + list(pools.items()):
        cor[name] = {"R_P": rho([r["R_P"] for r in x], [r["jumped"] for r in x], "greater"),
                     "D_T": rho([r["D_T"] for r in x], [r["jumped"] for r in x], "greater"), "n": len(x)}
    out["correlations"] = cor
    p = out["pred"]
    p["1_poolA"] = {"rho": cor["A"]["R_P"], "pass": cor["A"]["R_P"][0] >= 0.5 and cor["A"]["R_P"][1] < 0.01}
    p["2_all_beats_DT"] = {"rho": cor["all"]["R_P"][0], "D_T": cor["all"]["D_T"][0],
                           "pass": cor["all"]["R_P"][0] > cor["all"]["D_T"][0]}
    p["3_always"] = {"rho": cor["always"]["R_P"][0], "pass": cor["always"]["R_P"][0] >= 0.6}
    p["3_B"] = {"rho": cor["B"]["R_P"][0], "pass": cor["B"]["R_P"][0] >= 0.7}
    zero = [r for r in rs if r["informative"] == 0]
    zj = sum(r["jumped"] for r in zero)
    p["4_zero"] = {"rules": len(zero), "soups_jumped": zj, "of": 6 * len(zero),
                   "rules_jumping": [(r["rule"], r["jumped"]) for r in zero if r["jumped"]],
                   "pass": bool(zero) and zj <= 0.1 * 6 * len(zero)}
    fast = [r for r in rs if r["jumped"] >= 4]
    mt = [float(np.median(T[r["code"]])) for r in fast]
    p["5_speed"] = {"n": len(fast), "rho": rho([r["R_P"] for r in fast], mt, "less"),
                    "pass": rho([r["R_P"] for r in fast], mt, "less")[1] < 0.05}
    nz = [r for r in rs if r["informative"] > 0]
    out["nonzero"] = {"rules": len(nz), "soups_jumped": sum(r["jumped"] for r in nz), "of": 6 * len(nz)}
    out["side"] = [sum(r["side"][i] for r in rs) for i in (0, 1)]
    out["null_by_pool"] = {k: sum(r["null"] for r in v) for k, v in pools.items()}
    out["from_replicator_by_pool"] = {k: sum(r["from_replicator"] for r in v) for k, v in pools.items()}
    out["untested_rules"] = [(r["rule"], r["hits"], r["tested"]) for r in rs if r["tested"] < r["hits"]]
    return out


if __name__ == "__main__":
    res = main(sys.argv[1])
    for t in res.pop("table"):
        print(json.dumps(t))
    print(json.dumps(res, indent=1, default=str))
