"""E-73 part B analysis (docs/data/e73-preregistration.md): re-apply the pre-registered tests of E-70 (P2), E-71
(P1, P2) and E-72 (primary) with jump times from the D-053 copy test, beside the D-050 ones, from the re-score
(docs/data/experiments/2026-11-11-e73-rescore.json). The D-052 HOE timing does not depend on the copy test and is
not recomputed here.

    PYTHONPATH=scripts python scripts/e73_analysis.py --out docs/data/experiments/2026-11-11-e73-analysis.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import bff_copiercount as CC  # noqa: E402
import bff_tapelength as TL  # noqa: E402

D = Path("docs/data/experiments")
WAIT = 16000


def med(ts):
    return float(np.median([t if t is not None else WAIT for t in ts]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(D / "2026-11-11-e73-rescore.json"))
    by = {(r["exp"], r["seed"]): r for r in R["results"]}
    out = {"experiment": "E-73", "part": "analysis", "equivalent_all": R["equivalent_all"]}

    # changes
    ch = Counter()
    for r in R["results"]:
        a0, a1 = r["T_d050"], r["T_d053"]
        k = ("same" if a0 == a1 else "new jump" if a0 is None else "lost jump" if a1 is None
             else "earlier" if a1 < a0 else "later")
        ch[(r["exp"], k)] += 1
    out["changes"] = {f"{e} {k}": n for (e, k), n in sorted(ch.items())}
    out["changed_soups"] = [[r["exp"], r["seed"], r["v"], r["g"], r["h"], r["T_d050"], r["T_d053"]]
                            for r in R["results"] if r["T_d050"] != r["T_d053"]]

    # E-70 P2
    e70 = json.load(open(D / "2026-11-09-e70-soups.json"))
    cls = {(r["v"], r["h"]): r["class"] for v, vd in e70["summary"]["by_v"].items()
           for h, r in vd["per_rule"].items() for r in [dict(r, v=int(v), h=int(h))]}
    res70 = {}
    for key in ("T_d050", "T_d053"):
        j = {"F": [0, 0], "N": [0, 0]}
        byv = {}
        for r in R["results"]:
            if r["exp"] != "E-70":
                continue
            c = cls[(r["v"], r["h"])]
            jumped = r[key] is not None
            j[c][0] += jumped
            j[c][1] += 1
            byv.setdefault(r["v"], {"F": [0, 0], "N": [0, 0]})[c][0] += jumped
            byv[r["v"]][c][1] += 1
        p = TL.fisher(j["F"][0], j["F"][1], j["N"][0], j["N"][1])
        each = all(b["F"][0] / b["F"][1] >= b["N"][0] / b["N"][1] for b in byv.values())
        ok = j["F"][0] / j["F"][1] >= 0.75 and j["N"][0] / j["N"][1] <= 0.25 and p < 0.01 and each
        res70[key] = {"jumped": j, "fisher_p": p, "F_ge_N_each_v": each, "P2": "pass" if ok else "fail"}
    out["E-70_P2"] = res70

    # E-71 P1/P2
    e71 = json.load(open(D / "2026-11-10-e71-copiercount.json"))
    res71 = {}
    for key in ("T_d050", "T_d053"):
        per = []
        for k, p in enumerate(e71["per_rule"]):
            ts = [by[("E-71", 7100 + 10 * k + i)][key] for i in range(CC.SOUPS)]
            assert key == "T_d053" or ts == p["T"], (k, ts, p["T"])
            per.append((p["self_sufficient"], med(ts), p["v"], sum(t is not None for t in ts)))
        t = CC.perm_tests([x[0] for x in per], [x[1] for x in per], [x[2] for x in per])
        t["P1"] = "pass" if t["rho"] <= -0.4 and t["p_one_sided_perm"] < 0.01 else "fail"
        t["P2"] = "pass" if t["within_p_one_sided_perm"] < 0.05 else "fail"
        t["v1_68_jumped"] = [x[3] for x, p in zip(per, e71["per_rule"]) if (p["v"], p["h"]) == (1, 68)][0]
        t["median_T"] = [x[1] for x in per]
        res71[key] = t
    out["E-71"] = res71

    # E-72 primary
    e72 = json.load(open(D / "2026-11-10-e72-soups.json"))
    res72 = {}
    for key in ("T_d050", "T_d053"):
        per = []
        for k, p in enumerate(e72["per_rule"]):
            ts = [by[("E-72", 7200 + 10 * k + i)][key] for i in range(6)]
            assert key == "T_d053" or ts == p["T"], (k, ts, p["T"])
            per.append({"class": p["class"], "v": p["v"], "g": p["g"], "h": p["h"], "deep_est": p["deep_est"],
                        "self_sufficient": p["self_sufficient"], "median_T": med(ts),
                        "jumped": sum(t is not None for t in ts)})
        md = [p["median_T"] for p in per if p["class"] == "deep"]
        ms = [p["median_T"] for p in per if p["class"] == "shallow"]
        mw = float(mannwhitneyu(ms, md, alternative="greater").pvalue)
        ratio = float(np.median(ms) / np.median(md))
        res72[key] = {"median_of_median_T": {"deep": float(np.median(md)), "shallow": float(np.median(ms))},
                      "ratio": ratio, "mannwhitney_p": mw, "primary": "pass" if mw < 0.01 and ratio >= 3 else "fail",
                      "deep_est_vs_T": [float(x) for x in spearmanr([p["deep_est"] for p in per],
                                                                    [p["median_T"] for p in per])],
                      "ss_vs_T": [float(x) for x in spearmanr([p["self_sufficient"] for p in per],
                                                              [p["median_T"] for p in per])],
                      "jumped": {c: sum(p["jumped"] for p in per if p["class"] == c) for c in ("deep", "shallow")},
                      "per_rule": per}
    out["E-72"] = res72
    json.dump(out, open(a.out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    s = {k: v for k, v in out.items() if k not in ("changed_soups",)}
    for e in ("T_d050", "T_d053"):
        s["E-72"][e] = {k: v for k, v in s["E-72"][e].items() if k != "per_rule"}
        s["E-71"][e] = {k: v for k, v in s["E-71"][e].items() if k != "median_T"}
    print(json.dumps(s, indent=1, default=str))


if __name__ == "__main__":
    main()
