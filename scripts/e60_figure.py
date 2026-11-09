"""Figure for E-60: short copiers under every head-start rule, and how often soups jumped in the tested rules.

    python scripts/e60_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREY, GREEN = "#2f6db5", "#e08a1e", "#8a8f98", "#2e8b57"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = json.load(open("docs/data/experiments/2026-11-08-e60-census.json"))
S60 = json.load(open("docs/data/experiments/2026-11-08-e60-soups.json"))["summary"]["per_rule"]
# Jumps by 16,000 rounds at 2^14 from earlier experiments: h=0 E-40, h=64 E-57+E-59, h=127 E-58+E-59.
jumps = {0: (0, 12), 64: (16, 16), 127: (3, 24)}
for h, v in S60.items():
    jumps[int(h)] = (v["jumped"], len(v["T"]))
h = np.arange(128)
fw = np.array([r["forward"] for r in C["rules"]])
rv = np.array([r["reverse"] for r in C["rules"]])
ss = np.array([r["self_sufficient"] for r in C["rules"]])
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(11, 5.6), sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
ax.bar(h, fw, 0.9, color=BLUE, label="forward copiers")
ax.bar(h, rv, 0.9, bottom=fw, color=ORANGE, label="backward copiers")
ax.scatter(h[ss > 0], (fw + rv)[ss > 0] + 8, marker="*", s=70, color=GREEN, label="has a self-sufficient copier (F)",
           zorder=3)
ax.set_ylabel("copiers of 5–6\ninstructions")
ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0.12, 1))
ax.set_title("Every rule 'pointer 2 starts at byte h': short copiers (top) and soups that made replicators (bottom)",
             fontsize=10)
for k, (j, n) in sorted(jumps.items()):
    f = (ss[k] > 0)
    ax2.bar(k, 100 * j / n, 1.6, color=GREEN if f else GREY)
    if k not in (62, 63, 64, 65):
        ax2.text(k + (-2.5 if k == 125 else 2.5 if k == 127 else 0), 100 * j / n + 3, f"{j}/{n}", ha="center", fontsize=7.5)
ax2.text(63.5, 104, "h = 62–65: every soup jumped\n(4/4, 4/4, 16/16, 4/4)", ha="center", fontsize=8)
ax2.set_ylim(0, 125)
ax2.set_ylabel("% of soups that\njumped by 16,000")
ax2.set_xlabel("h: byte where pointer 2 starts (0 = the normal rule; 64 = the partner's first byte)")
ax2.set_xticks([0, 7, 32, 62, 96, 120, 127])
fig.savefig("docs/assets/report/e60-headstart.png")
print("saved docs/assets/report/e60-headstart.png")
