"""Figure for E-78: per-soup fitness change (late - early, kin-free invasion into the original run's T+10000 soup)
in the three arms, and the coexistence / clustering trajectories.

    python scripts/e78_figure.py docs/data/experiments/<date>-e78-spatial.json docs/data/experiments/<date>-e78-explore.json

The third panel is post hoc (scripts/e78_explore.py): the pre-registered clustering statistic needs families
holding >= 1% of the soup, and S has none after 2,000 rounds.
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREY = "#2f6db5", "#d9822b", "#8a8f98"
COL = {"M": BLUE, "S": ORANGE, "Mp": GREY}
LAB = {"M": "M (well mixed)", "S": "S (neighbours only)", "Mp": "M′ (well mixed, other seed)"}
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
d = json.load(open(sys.argv[1]))
S = d["summary"]
P = S["primary"]
soups = [int(s) for s in P["delta"]]
fig, (ax, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.4))
for i, s in enumerate(soups):
    for arm, dx in (("M", -0.2), ("S", 0.0), ("Mp", 0.2)):
        v = P["delta"][str(s)][arm]
        if v is not None:
            ax.scatter(i + dx, v, s=30, color=COL[arm], label=LAB[arm] if i == 0 else None, zorder=3)
    if P["delta"][str(s)]["M"] is not None and P["delta"][str(s)]["S"] is not None:
        ax.plot([i - 0.2, i], [P["delta"][str(s)]["M"], P["delta"][str(s)]["S"]], color=GREY, lw=0.8)
ax.axhline(0, color=GREY, lw=0.8, ls=":")
ax.set_xticks(range(len(soups)))
ax.set_xticklabels(soups, fontsize=8)
ax.set_xlabel("soup (65,536 programs)")
ax.set_ylabel("Δ = invasion score, late − early\n(into the original soup at T+10,000)")
t = P["test"]
ax.set_title(f"Space vs mixing: mean d = {t['mean_d']:+.2f}, p = {t['p_one_sided']:.2f} ({t['verdict']})", fontsize=10)
ax.legend(frameon=False, fontsize=8)
tr = S["trajectories"]
X = json.load(open(sys.argv[2]))["rows"]
for arm in ("M", "S", "Mp"):
    rows = []
    for s in soups:
        sm = tr[f"{s}/{arm}"]["summaries"]
        x = (np.array([r["epoch"] for r in sm]) - sm[0]["epoch"]) / 1000
        fam = [r["families_ge1pct"] for r in sm]
        ex = sorted((r["dt"], r["kin_nbr"]) for r in X if r["seed"] == s and r["arm"] == arm)
        nbr = [100 * v for _, v in ex]
        ax2.plot(x, fam, color=COL[arm], lw=0.6, alpha=0.4)
        ax3.plot(x, nbr, color=COL[arm], lw=0.6, alpha=0.4)
        rows.append((fam, nbr))
    ax2.plot(x, np.median([r[0] for r in rows], 0), color=COL[arm], lw=2.2, label=LAB[arm])
    ax3.plot(x, np.median([r[1] for r in rows], 0), color=COL[arm], lw=2.2, label=LAB[arm])
ax2.set_xlabel("thousands of rounds after the fork (T+2,000)")
ax2.set_ylabel("families (≥ 90% identical)\nholding ≥ 1% of the soup")
ax2.set_title("Coexisting families (thin: soups, thick: median)", fontsize=10)
ax2.legend(frameon=False, fontsize=8)
ax3.set_xlabel("thousands of rounds after the fork (T+2,000)")
ax3.set_ylabel("% of grid-neighbour pairs ≥ 90% identical\n(random pairs: 0.1–0.4%)")
ax3.set_title("S becomes a mosaic of small local families (post hoc)", fontsize=10)
fig.savefig("docs/assets/report/e78-spatial.png")
print("saved docs/assets/report/e78-spatial.png")
