"""Figure for E-54: early (T+2000) vs late (T+18000) verified replicators invading kin-free soup samples at T+10000,
and the share of verified replicators among the 40 most common distinct programs over time.

    python scripts/e54_figure.py
"""
import collections
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREY = "#2f6db5", "#d9822b", "#8a8f98"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
d = json.load(open("docs/data/experiments/2026-11-08-e54-long-soups.json"))
S, inv = d["summary"], d["invasion"]
seeds = sorted(S["jumped"], key=int)
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
for i, s in enumerate(seeds):
    bg = S["jumped"][s] + 10000
    for g, col, dx in (("early", BLUE, -0.15), ("late", ORANGE, 0.15)):
        v = [r["s"] for r in inv if str(r["seed"]) == s and r["group"] == g and r["background"] == bg]
        ax.scatter(np.full(len(v), i + dx) + np.random.default_rng(i).uniform(-0.05, 0.05, len(v)), v, s=14, color=col, alpha=0.6,
                   label=("T+2,000 replicators" if g == "early" else "T+18,000 replicators") if i == 0 else None)
        ax.plot([i + dx - 0.1, i + dx + 0.1], [np.mean(v)] * 2, color=col, lw=2.5)
ax.axhline(0, color=GREY, lw=0.8, ls=":")
ax.set_xticks(range(len(seeds)))
ax.set_xticklabels(seeds, fontsize=8)
ax.set_xlabel("soup (65,536 programs)")
ax.set_ylabel("invasion score s\n(into the soup at T+10,000)")
p = S["primary"]
ax.set_title(f"Later replicators are not fitter: D = {p['D']:.2f}, p = {p['p']:.2f}", fontsize=10)
ax.legend(frameon=False, fontsize=8)
by = collections.defaultdict(dict)
for k, v in S["replicator_share_top40"].items():
    s, dt = k.split("/")
    by[s][int(dt)] = v
for s in seeds:
    t = sorted(by[s])
    ax2.plot(np.array(t) / 1000, [100 * by[s][x] for x in t], marker="o", ms=3, lw=1.2, label=s)
ax2.set_ylim(0, 100)
ax2.set_xlabel("thousands of rounds after the jump")
ax2.set_ylabel("% of the 40 most common programs\nthat are verified replicators")
ax2.set_title("Soups stay full of programs that do not copy", fontsize=10)
ax2.legend(frameon=False, fontsize=7, ncol=2)
fig.savefig("docs/assets/report/e54-long-soups.png")
print("saved docs/assets/report/e54-long-soups.png")
