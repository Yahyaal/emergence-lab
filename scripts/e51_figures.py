"""Figures for D-044 (growth-rate assay calibration) and E-51 (growth rates of the E-49 replicators).

    python scripts/e51_figures.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREY, GREEN, RED = "#2f6db5", "#e08a1e", "#8a8f98", "#3a9a5b", "#c8453c"
OUT = "docs/assets/report/"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})

c = json.load(open("docs/data/experiments/2026-11-08-d044-calibration.json"))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
p = np.linspace(0, 1, 100)
ax[0].plot(p, np.log(1 + p / 2), c=GREY, lw=1.5, label="theory: ln(1 + p/2)")
L = c["ladder"]
ax[0].errorbar([x["p"] for x in L], [x["r"] for x in L], yerr=[2 * x["se"] for x in L], fmt="o", c=BLUE,
               label="measured (24 runs each)")
for x in L:
    ax[0].annotate(f"trap k={x['k']}" if x["k"] else "no trap", (x["p"], x["r"]), xytext=(6, -10),
                   textcoords="offset points", fontsize=8)
ax[0].set_xlabel("probability p that the variant copies itself (built in, known)")
ax[0].set_ylabel("growth rate r per round")
ax[0].set_title("Calibration: variants with known copying odds", fontsize=10)
ax[0].legend(frameon=False, fontsize=8)
R = c["replicators"]
names = [r["name"] for r in R]
y = np.arange(len(R))
ax[1].barh(y - 0.2, [r["halting"]["r"] for r in R], 0.4, color=GREY, label="harmless background")
ax[1].barh(y + 0.2, [r["random"]["r"] for r in R], 0.4, color=[ORANGE if i == 0 else BLUE for i in range(len(R))],
           label="random-code background")
ax[1].set_yticks(y, names, fontsize=8)
ax[1].invert_yaxis()
ax[1].set_xlabel("growth rate r per round")
ax[1].set_title("Hand-written vs the 9 emergent replicators", fontsize=10)
from matplotlib.patches import Patch
ax[1].legend(handles=[Patch(color=GREY, label="harmless (halting) background"),
                      Patch(color=ORANGE, label="random code, hand-written"), Patch(color=BLUE, label="random code, emergent")],
             frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
fig.savefig(OUT + "d044-calibration.png")
plt.close(fig)

d = json.load(open("docs/data/experiments/2026-11-08-e51-growth-rates.json"))
P = [q for q in d["programs"] if q["seed"] != "hand"]
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
rng = np.random.default_rng(0)
for i, s in enumerate((901, 5006, 5010)):
    for j, t in enumerate((2000, 6000, 12000)):
        v = [q["random"]["r"] for q in P if q["seed"] == s and q["time"] == t]
        x = i * 4 + j
        ax[0].scatter(x + rng.uniform(-0.15, 0.15, len(v)), v, s=14, c=[BLUE, ORANGE, GREEN][j], alpha=0.8)
        if v:
            ax[0].plot([x - 0.3, x + 0.3], [np.mean(v)] * 2, c="k", lw=1.5)
ax[0].set_xticks([1, 5, 9], ["soup 901\nρ = −0.09", "soup 5006\nρ = +0.64", "soup 5010\nρ = −0.41"])
ax[0].set_ylabel("growth rate r (random-code background)")
ax[0].set_title("Rounds after the jump: blue 2,000 · orange 6,000 · green 12,000", fontsize=9)
R49 = {(q["seed"], q["program"]): q["random"]["r"] for q in P}
e49 = [r for r in json.load(open("docs/data/experiments/2026-11-08-e49-time-races.json"))["results"] if r["n"] >= 8]
dr = [R49[(r["seed"], r["b"])] - R49[(r["seed"], r["a"])] for r in e49]
sh = [r["b_share"] for r in e49]
ax[1].scatter(dr, sh, s=10, c=BLUE, alpha=0.5)
ax[1].axhline(0.5, c=GREY, lw=0.7)
ax[1].axvline(0, c=GREY, lw=0.7)
ax[1].set_xlabel("difference in growth rate, r(b) − r(a)")
ax[1].set_ylabel("share of 32 races won by b")
ax[1].set_title(f"Growth rate predicts races only weakly (Spearman ρ = {d['summary']['validity']['rho']}, 347 pairs)", fontsize=9)
fig.savefig(OUT + "e51-growth-rates.png")
plt.close(fig)
print("ok")
