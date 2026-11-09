"""Figure for E-64: the two-head-start family (head0 starts at g, head1 at h). Left: census classes of 256 random
rules. Right: soups with real replicators (D-047) per tested rule.

    python scripts/e64_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, GREY, GREEN, LIGHT = "#2f6db5", "#8a8f98", "#2e8b57", "#d5d8dd"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = json.load(open("docs/data/experiments/2026-11-09-e64-census.json"))["rules"]
S = json.load(open("docs/data/experiments/2026-11-09-e64-soups.json"))["summary"]["per_rule"]
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.1, 1]})
for cls, col, lab, s, m in (("0", LIGHT, "no short copier", 14, "o"), ("C", BLUE, "short copiers, none whose copy copies (C)", 22, "o"),
                            ("F", GREEN, "a short copier whose copy copies (F)", 140, "*")):
    pts = [(r["g"], r["h"]) for r in C if r["class"] == cls]
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=s, color=col, marker=m, label=f"{lab}: {len(pts)}", zorder=3 if cls == "F" else 2)
ax.set_xlabel("g: byte where pointer 1 starts")
ax.set_ylabel("h: byte where pointer 2 starts")
ax.set_title("Census: 256 random rule versions", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=1)
names = list(S)
vals = [100 * S[k]["jumped"] / len(S[k]["T"]) for k in names]
cols = [GREEN if S[k]["class"] == "F" else BLUE for k in names]
ax2.bar(range(len(names)), vals, color=cols)
for i, k in enumerate(names):
    ax2.text(i, vals[i] + 3, f"{S[k]['jumped']}/{len(S[k]['T'])}", ha="center", fontsize=8.5)
ax2.set_xticks(range(len(names)))
ax2.set_xticklabels([k.replace("g", "g=").replace("h", "\nh=") for k in names], fontsize=8)
ax2.set_ylim(0, 115)
ax2.set_ylabel("% of soups with real\nreplicators by 16,000 rounds")
ax2.set_title("Soups (pre-registered): F 10/12, C 1/16, p = 5e-5", fontsize=10)
fig.savefig("docs/assets/report/e64-twoheads.png")
print("saved docs/assets/report/e64-twoheads.png")
