"""Analysis of E-75 phase 5 (scripts/sq_nucleation.py) against docs/data/e75-phase5-preregistration.md."""
import collections
import json
import sys

import numpy as np
from scipy.stats import mannwhitneyu

d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "docs/data/experiments/2026-11-13-e75-nucleation.json"))
P3 = json.load(open("docs/data/experiments/2026-11-13-e75-phase3.json"))["summary"]["rules"]
P4 = json.load(open("docs/data/experiments/2026-11-13-e75-phase4.json"))["summary"]["rules"]
jumps = {q["code"]: q["jumped"] for q in P3 + P4}
S = d["soups"]
out = {}
# 1 controls
pos = [s for s in S if s["kind"] == "positive"]
neg = [s for s in S if s["kind"] == "negative"]
out["positive"] = [{"rule": s["rule"], "first": s["lineages"][0]["round"] if s["lineages"] else None,
                    "cause": s["lineages"][0]["cause"] if s["lineages"] else None, "established": s["established"]}
                   for s in pos]
out["negative"] = [{"rule": s["rule"], "origins": len(s["lineages"]), "established": s["established"]} for s in neg]
M = [s for s in S if s["kind"] == "main"]
# 2 agreement
J = [s for s in M if s["T_original"] is not None]
NJ = [s for s in M if s["T_original"] is None]
out["agree"] = {"jumped_established": [sum(s["established"] is not None for s in J), len(J)],
                "nonjumped_informative_first": [sum(bool(s["established"]) and not s["established"]["null"] for s in NJ), len(NJ)],
                "nonjumped_any": [sum(s["established"] is not None for s in NJ), len(NJ)],
                "est_minus_T": sorted(s["established"]["round"] - s["T_original"] for s in J if s["established"])}
# 3 null first
for ph, name in ((4, "le0"), (3, "always")):
    E = [s for s in M if s["phase"] == ph and s["established"]]
    out[f"null_first_{name}"] = [sum(s["established"]["null"] for s in E), len(E)]
out["informative_after_null"] = [(s["rule"], s["established"]["round"], s.get("informative_after", {}).get("round"))
                                 for s in M if s["established"] and s["established"]["null"]]


# 4 origin rate and establishment fraction
def rate(s):
    rounds = s["rounds"]
    return 1000 * len(s["lineages"]) / rounds


def est_frac(s):
    L = s["lineages"]
    return np.mean([lg["peak"] >= 10 for lg in L]) if L else None


hi = [s for s in M if jumps[s["code"]] >= 4]
lo = [s for s in M if jumps[s["code"]] <= 1]
rh, rl = [rate(s) for s in hi], [rate(s) for s in lo]
out["rate"] = {"often_n": len(hi), "rarely_n": len(lo), "often_median": float(np.median(rh)), "rarely_median": float(np.median(rl)),
               "p_one_sided": float(mannwhitneyu(rh, rl, alternative="greater").pvalue),
               "rarely_soups_with_0_origins": sum(len(s["lineages"]) == 0 for s in lo),
               "often_soups_with_0_origins": sum(len(s["lineages"]) == 0 for s in hi)}
eh, el = [x for x in map(est_frac, hi) if x is not None], [x for x in map(est_frac, lo) if x is not None]
out["est_frac"] = {"often": [float(np.median(eh)) if eh else None, len(eh)], "rarely": [float(np.median(el)) if el else None, len(el)],
                   "p_two_sided": float(mannwhitneyu(eh, el).pvalue) if eh and el else None}
# 5 cause of founders
F = [s["lineages"][s["established"]["lineage"]] for s in M if s["established"]]
out["founder_cause"] = dict(collections.Counter(f["cause"] for f in F))
out["founder_null"] = [sum(f["null"] for f in F), len(F)]
# extra: origins before the founder, and waiting from first origin to establishment
out["origins_before_est"] = sorted(s["established"]["lineage"] for s in M if s["established"])
out["first_origin_to_est"] = sorted(s["established"]["round"] - s["lineages"][0]["round"] for s in M if s["established"])
out["nonjumped_origins"] = sorted(len(s["lineages"]) for s in NJ)
print(json.dumps(out, indent=1))
