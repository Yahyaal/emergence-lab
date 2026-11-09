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
E58C = json.load(open("docs/data/experiments/2026-11-08-e58-census.json"))
# E-58 (head1 = 127): real jumps only (D-045 in full: copiers present; the 4 HOE-only crossings had none and,
# replayed to 16,000 rounds, still none). See J-058.
E58S = json.load(open("docs/data/experiments/2026-11-08-e58-soups.json"))
H127 = [r["T"] for r in E58S["results"] if r["jumped"] and r["orientation"]["reverse"] > 0]
# E-59 (confirmation, D-046 criterion built in): pooled with E-57 (head1 = 64) and E-58 (head1 = 127).
E59 = json.load(open("docs/data/experiments/2026-11-08-e59-orientation-confirm.json"))
H127 += [r["T"] for r in E59["results"] if r["h1"] == 127 and r["jumped"]]
H64_14 = [r["T"] for r in E57S["results"] if r["jumped"]] + [r["T"] for r in E59["results"] if r["h1"] == 64 and r["jumped"]]
N127 = len(E58S["results"]) + sum(r["h1"] == 127 for r in E59["results"])
N64_14 = len(E57S["results"]) + sum(r["h1"] == 64 for r in E59["results"])

# Standard-rule jump rounds (D-045 criterion). 2^16: E-50 (10 soups) + E-54 new soups (12), horizon 24,000.
# 2^14: E-40, 12 soups, none by 16,000 rounds.
STD16 = [12500, 13750, 21750, 10250, 22250, 16750, 750]
STD16_N, STD14_N = 22, 12
arms = [
    ("standard rule\n16,384 programs", [], STD14_N, 16000, ORANGE),
    ("head1 at 64\n16,384 programs", H64_14, N64_14, 16000, BLUE),
    ("head1 at 127\n16,384 programs", H127, N127, 16000, "#7a4fb0"),
    ("standard rule\n65,536 programs", STD16, STD16_N, 24000, ORANGE),
    ("head1 at 64\n65,536 programs", [r["T"] for r in E56["results"] if r["jumped"]], len(E56["results"]), 24000, BLUE),
]
fig = plt.figure(figsize=(12.5, 4.6))
ax = fig.add_axes([0.06, 0.16, 0.55, 0.72])
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
ax.set_xticks(range(5), [a[0] for a in arms], fontsize=7.5)
ax.set_ylabel("round of the jump (log scale)")
ax.set_title("When soups jump (grey triangles: no jump by the end of the run)", fontsize=10)

ax2 = fig.add_axes([0.69, 0.16, 0.3, 0.72])
bars = [(E57C["standard"]["self_sufficient"], E57C["standard"]["copiers"], ORANGE, "standard\n(backward)"),
        (E57C["counterfactual"]["self_sufficient"], E57C["counterfactual"]["copiers"], BLUE, "head1 at 64\n(forward)"),
        (E58C["self_sufficient"], E58C["copiers"], "#7a4fb0", "head1 at 127\n(backward)")]
for xi, (k, n, c, _) in enumerate(bars):
    ax2.bar(xi, 100 * k / n, 0.55, color=c)
    ax2.text(xi, 100 * k / n + 2, f"{k} of {n}", ha="center", fontsize=9)
ax2.set_xticks(range(3), [b[3] for b in bars], fontsize=8)
ax2.set_ylabel("% of short copiers whose copy also copies")
ax2.set_ylim(0, 100)
ax2.set_title("Short copiers whose copy can copy again", fontsize=10)
fig.savefig("docs/assets/report/e57-counterfactual-jumps.png")
print("saved docs/assets/report/e57-counterfactual-jumps.png")
