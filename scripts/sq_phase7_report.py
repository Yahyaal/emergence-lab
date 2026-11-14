"""E-75 phase 7 analysis against the pre-registered predictions (docs/data/e75-phase7-preregistration.md).

    PYTHONPATH=. python scripts/sq_phase7_report.py docs/data/experiments/2026-11-14-e75-phase7.json
"""
from __future__ import annotations

import json
import sys

import numpy as np
from scipy.stats import fisher_exact, spearmanr


def main(path: str) -> dict:
    d = json.load(open(path))
    sel = d["selected"]
    g = {k: [q for q in sel if q["group"] == k] for k in ("HIGH", "ZERO")}
    j = {k: sum(q["jumped"] for q in v) for k, v in g.items()}
    n = {k: 6 * len(v) for k, v in g.items()}
    out = {"rules": {k: len(v) for k, v in g.items()}, "jumped": j, "of": n,
           "by_jump": {jn: {k: [len([q for q in v if q["jump"] == jn]),
                                sum(q["jumped"] for q in v if q["jump"] == jn)] for k, v in g.items()}
                       for jn in ("always", "<=0", "<0")}}
    p = {}
    fp = (float(fisher_exact([[j["HIGH"], n["HIGH"] - j["HIGH"]], [j["ZERO"], n["ZERO"] - j["ZERO"]]],
                             alternative="greater").pvalue) if n["HIGH"] and n["ZERO"] else None)
    ok = (n["HIGH"] and j["HIGH"] >= 0.75 * n["HIGH"] and j["ZERO"] <= 0.25 * n["ZERO"] and fp < 0.001)
    p["1_primary"] = {"fisher_p": fp, "verdict": "undecided" if len(g["HIGH"]) < 8 or len(g["ZERO"]) < 8
                      else "pass" if ok else "fail",
                      "would_pass_criteria": bool(ok)}
    h4 = sum(q["jumped"] >= 4 for q in g["HIGH"])
    p["2_high_rules"] = {"ge4": h4, "of": len(g["HIGH"]), "pass": bool(g["HIGH"]) and h4 >= 0.8 * len(g["HIGH"])}
    za = [q for q in g["ZERO"] if q["jump"] == "always"]
    zo = [q for q in g["ZERO"] if q["jump"] != "always"]
    p["3_zero_always"] = {"jumped": sum(q["jumped"] for q in za), "of": 6 * len(za),
                          "pass": bool(za) and sum(q["jumped"] for q in za) <= 0.10 * 6 * len(za)}
    p["3_zero_other"] = {"jumped": sum(q["jumped"] for q in zo), "of": 6 * len(zo),
                         "pass": bool(zo) and sum(q["jumped"] for q in zo) <= 0.35 * 6 * len(zo)}
    hs = [q for q in g["HIGH"] if any(t is not None for t in q["T"])]
    if len(hs) >= 3:
        r = spearmanr([q["R_P"] for q in hs], [np.median([t for t in q["T"] if t is not None]) for q in hs],
                      alternative="less")
        p["4_speed"] = {"n": len(hs), "rho": float(r.statistic), "p": float(r.pvalue), "pass": r.pvalue < 0.05}
    else:
        p["4_speed"] = {"n": len(hs), "pass": None}
    dt = [q for q in sel if q["D_T"] is not None]
    rp = spearmanr([q["R_P"] for q in dt], [q["jumped"] for q in dt])
    rd = spearmanr([q["D_T"] for q in dt], [q["jumped"] for q in dt])
    p["5_vs_DT"] = {"rho_RP": float(rp.statistic), "rho_DT": float(rd.statistic), "n": len(dt),
                    "pass": float(rp.statistic) > float(rd.statistic)}
    out["pred"] = p
    out["table"] = [{k: q[k] for k in ("jump", "group", "rule", "R_P", "D_T", "jumped", "T")} for q in sel]
    out["screened"] = len(d["screened"])
    out["stage1_candidates"] = {jn: {c: sum(1 for x in d["screened"] if x["jump"] == jn and x["candidate"] == c)
                                     for c in ("HIGH", "ZERO", None)} for jn in ("always", "<=0", "<0")}
    out["stage2_rejected"] = [(x["rule"], x["candidate"], x.get("products"), x["screen"].get("pass"))
                              for x in d["screened"] if "stage2" in x and not x["selected"]]
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1, default=str))
