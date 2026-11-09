"""Figure for E-64 + E-65: the two-head-start family. Left: census classes of 1,024 random rules (E-64 and E-65).
Right: per tested E-65 rule, median jump round vs number of self-sufficient short copiers (F rules) and C rules.

    python scripts/e65_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, GREEN, LIGHT, GREY = "#2f6db5", "#2e8b57", "#d5d8dd", "#8a8f98"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = (json.load(open("docs/data/experiments/2026-11-09-e64-census.json"))["rules"]
     + json.load(open("docs/data/experiments/2026-11-09-e65-census.json"))["rules"])
S = json.load(open("docs/data/experiments/2026-11-09-e65-soups.json"))["summary"]
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.1, 1], "wspace": 0.35})
for cls, col, lab, s, m in (("0", LIGHT, "no short copier", 8, "o"), ("C", BLUE, "short copiers, none whose copy copies (C)", 16, "o"),
                            ("F", GREEN, "a short copier whose copy copies (F)", 110, "*")):
    pts = [(r["g"], r["h"]) for r in C if r["class"] == cls]
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=s, color=col, marker=m, label=f"{lab}: {len(pts)}", zorder=3 if cls == "F" else 2)
ax.set_xlabel("g: byte where pointer 1 starts")
ax.set_ylabel("h: byte where pointer 2 starts")
ax.set_title(f"Census: {len(C)} random rule versions (E-64 + E-65)", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14))
per = S["per_rule"]
ci = 0
for k, v in per.items():
    x = v["self_sufficient"] if v["class"] == "F" else 0.45 + 0.08 * ci
    ci += v["class"] == "C"
    ax2.scatter(x, v["median_T"], s=30 + 25 * v["jumped"], color=GREEN if v["class"] == "F" else BLUE, alpha=0.8, zorder=3)
    if v["class"] == "F":
        ax2.annotate(f"{v['jumped']}/4", (x, v["median_T"]), textcoords="offset points", xytext=(6, 4), fontsize=7.5)
ax2.text(0.5, 15000, f"4 C rules: {S['jumped']['C']}/{S['of']['C']} soups", fontsize=8, color=BLUE)
ax2.set_xscale("log")
ax2.axhline(16000, color=GREY, lw=0.8, ls=":")
ax2.set_xlabel("self-sufficient short copiers in the rule (C rules at left)")
ax2.set_ylabel("median round of the jump\n(16,000 = no jump)")
j, n = S["jumped"], S["of"]
sp = S["secondary_spearman"]
ax2.set_title(f"Soups: F {j['F']}/{n['F']}, C {j['C']}/{n['C']}; ρ = {sp['rho']:.2f}" if sp["rho"] is not None else "Soups", fontsize=10)
fig.savefig("docs/assets/report/e65-twoheads.png")
print("saved docs/assets/report/e65-twoheads.png")
