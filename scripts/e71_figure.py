"""Figure for E-71: within F rules, number of self-sufficient copiers in the census (log x) against the median
jump time of 8 soups (log y), one panel per variant; E-70's rules shown as hollow points for reference.

    python scripts/e71_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GREEN, GREY = "#2e8b57", "#9aa0a6"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
D = json.load(open("docs/data/experiments/2026-11-10-e71-copiercount.json"))
E70 = json.load(open("docs/data/experiments/2026-11-09-e70-soups.json"))["summary"]["secondary_selfsufficient_vs_medianT"]
C = {(r["v"], r["h"]): r for r in json.load(open("docs/data/experiments/2026-11-09-e70-census.json"))["rules"]}
NAMES = {1: "'.' then heads +1", 2: "'.' then heads −1", 3: "',' then heads +1", 4: "loops test head 1",
         5: "'+' '−' on head 1"}
fig, axes = plt.subplots(1, 5, figsize=(14, 3.4), sharey=True, gridspec_kw={"wspace": 0.12})
for ax, v in zip(axes, range(1, 6)):
    old = [(C[tuple(q)]["self_sufficient"], t) for q, t in zip(E70["rules"], E70["median_T"]) if q[0] == v]
    ax.scatter([x for x, _ in old], [t for _, t in old], s=30, facecolors="none", edgecolors=GREY, label="E-70 rules")
    new = [p for p in D["per_rule"] if p["v"] == v]
    for p in new:
        ax.scatter(p["self_sufficient"], p["median_T"], s=34, color=GREEN, zorder=3)
        ax.annotate(f"{p['h']}", (p["self_sufficient"], p["median_T"]), xytext=(4, 3), textcoords="offset points",
                    fontsize=7)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_title(NAMES[v], fontsize=9)
    ax.set_xlim(0.6, 8000)
    ax.axhline(16000, color=GREY, lw=0.6, ls=":")
axes[0].set_ylabel("median jump time (rounds)\n16,000 = no jump")
axes[0].scatter([], [], s=34, color=GREEN, label="E-71 rules (new, 8 soups)")
axes[0].legend(frameon=False, fontsize=7, loc="lower left")
fig.supxlabel("self-sufficient short copiers in the census (log)", fontsize=9, y=-0.04)
fig.savefig("docs/assets/report/e71-copiercount.png")
print("saved docs/assets/report/e71-copiercount.png")
