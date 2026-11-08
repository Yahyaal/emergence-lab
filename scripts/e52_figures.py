"""Figure for E-52/E-53: late minus early invasion score per soup and background.

    python scripts/e52_figures.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREEN, GREY = "#2f6db5", "#e08a1e", "#3a9a5b", "#8a8f98"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
e52 = json.load(open("docs/data/experiments/2026-11-08-e52-invasion.json"))["summary"]["primary"]
e53 = json.load(open("docs/data/experiments/2026-11-08-e53-invasion-kinfree.json"))["summary"]["primary"]
groups = [("own soup, early\n(early has kin)", e52["delta"], "bg2000", GREY),
          ("own soup, late\n(late has kin)", e52["delta"], "bg12000", ORANGE),
          ("no kin: +4,000", e53["delta"], "bg4000", BLUE),
          ("no kin: +9,000", e53["delta"], "bg9000", BLUE),
          ("no kin: later", e53["delta"], "bg-1", BLUE)]
fig, ax = plt.subplots(figsize=(10, 3.8))
w = 0.26
for j, (soup, mk) in enumerate(((901, "o"), (5006, "s"), (5010, "^"))):
    for i, (lab, d, b, c) in enumerate(groups):
        v = d[f"{soup}/{b}"]
        ax.bar(i + (j - 1) * w, v, w * 0.9, color=c, alpha=0.55 + 0.15 * j)
        ax.text(i + (j - 1) * w, v + (0.012 if v >= 0 else -0.035), str(soup), ha="center", fontsize=6.5)
ax.axhline(0, c="k", lw=0.7)
ax.set_ylim(-0.21, 0.25)
ax.axvline(1.5, c=GREY, lw=0.8, ls="--")
ax.set_xticks(range(len(groups)), [g[0] for g in groups], fontsize=8)
ax.set_ylabel("late − early invasion score")
ax.set_title(f"E-52 (left of the line): later code ahead only where it has relatives (p = {e52['p']:.3f}).  "
             f"E-53 (right): no relatives, no advantage (p = {e53['p']:.2f})", fontsize=9)
fig.savefig("docs/assets/report/e52-e53-invasion.png")
print("ok")
