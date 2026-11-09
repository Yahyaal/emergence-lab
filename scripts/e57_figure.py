"""Figure for E-56/E-57: when soups jump under the standard rule and the counterfactual, and why
(self-sufficient copiers; shortest replicator).

    python scripts/e57_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREY = "#2f6db5", "#e08a1e", "#8a8f98"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
E56 = json.load(open("docs/data/experiments/2026-11-08-e56-counterfactual-soups.json"))
E57S = json.load(open("docs/data/experiments/2026-11-08-e57-soups.json"))
E57C = json.load(open("docs/data/experiments/2026-11-08-e57-census.json"))

# Standard-rule jump rounds (D-045 criterion). 2^16: E-50 (10 soups) + E-54 new soups (12), horizon 24,000.
# 2^14: E-40, 12 soups, none by 16,000 rounds.
STD16 = [12500, 13750, 21750, 10250, 22250, 16750, 750]
STD16_N, STD14_N = 22, 12
arms = [
    ("standard rule\n16,384 programs", [], STD14_N, 16000, ORANGE),
    ("counterfactual\n16,384 programs", [r["T"] for r in E57S["results"] if r["jumped"]], len(E57S["results"]), 16000, BLUE),
    ("standard rule\n65,536 programs", STD16, STD16_N, 24000, ORANGE),
    ("counterfactual\n65,536 programs", [r["T"] for r in E56["results"] if r["jumped"]], len(E56["results"]), 24000, BLUE),
]
fig = plt.figure(figsize=(11, 4.4))
ax = fig.add_axes([0.06, 0.16, 0.5, 0.72])
rng = np.random.default_rng(3)
for i, (name, T, n, hor, c) in enumerate(arms):
    x = i + rng.uniform(-0.15, 0.15, len(T))
    ax.scatter(x, T, s=28, color=c, zorder=3)
    nj = n - len(T)
    if nj:
        ax.scatter(i + rng.uniform(-0.15, 0.15, nj), np.full(nj, hor * 1.06), s=28, marker="^", facecolor="none",
                   edgecolor=GREY, zorder=3)
    ax.text(i, 52000, f"{len(T)} of {n} jumped", ha="center", fontsize=9, fontweight="bold")
ax.set_yscale("log")
ax.set_ylim(150, 75000)
ax.set_xticks(range(4), [a[0] for a in arms], fontsize=8)
ax.set_ylabel("round of the jump (log scale)")
ax.set_title("When soups jump (grey triangles: no jump by the end of the run)", fontsize=10)

ax2 = fig.add_axes([0.66, 0.16, 0.32, 0.72])
v = [E57C["standard"]["fraction"], E57C["counterfactual"]["fraction"]]
ax2.bar([0, 1], [100 * x for x in v], 0.5, color=[ORANGE, BLUE])
for xi, (vi, r) in enumerate(zip(v, ("standard", "counterfactual"))):
    ax2.text(xi, 100 * vi + 2, f"{E57C[r]['self_sufficient']} of {E57C[r]['copiers']}", ha="center", fontsize=9)
ax2.set_xticks([0, 1], ["standard rule\n(backward copiers)", "counterfactual\n(forward copiers)"], fontsize=8.5)
ax2.set_ylabel("% of short copiers whose copy also copies")
ax2.set_ylim(0, 100)
ax2.set_title("Shortest replicator: 10 vs 5 instructions", fontsize=10)
fig.savefig("docs/assets/report/e57-counterfactual-jumps.png")
print("saved docs/assets/report/e57-counterfactual-jumps.png")
