"""Figure for E-70: the instruction-set family. Left: census per variant (rows) of every head1 start, coloured by
class. Right: soups per variant, jumped / run for F and other rules.

    python scripts/e70_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

BLUE, GREEN, LIGHT = "#2f6db5", "#2e8b57", "#d5d8dd"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = json.load(open("docs/data/experiments/2026-11-09-e70-census.json"))
S = json.load(open("docs/data/experiments/2026-11-09-e70-soups.json"))["summary"]
NAMES = {0: "standard", 1: "'.' then heads +1", 2: "'.' then heads −1", 3: "',' then heads +1",
         4: "loops test head 1", 5: "'+' '−' on head 1"}
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.3, 1.1], "wspace": 0.45})
for row, v in enumerate(range(6)):
    rs = [r for r in C["rules"] if r["v"] == v]
    for r in rs:
        if r["class"] == "F":
            ax.scatter(r["h"], row, s=120, marker="*", color=GREEN, zorder=3)
        elif r["copiers"] > 0:
            ax.scatter(r["h"], row, s=14, color=BLUE, zorder=2)
        else:
            ax.scatter(r["h"], row, s=6, color=LIGHT, zorder=1)
    ax.text(131, row, f"{sum(r['class'] == 'F' for r in rs)} F", va="center", fontsize=8, color=GREEN)
ax.set_yticks(range(6), [NAMES[v] for v in range(6)])
ax.invert_yaxis()
ax.set_xlim(-3, 140)
ax.set_xticks([0, 32, 64, 96, 127], ["0", "32", "64\n(half a tape)", "96", "127"])
ax.set_xlabel("byte where pointer 2 starts (tape = 128 bytes)")
ax.set_title("Census of every start, per instruction set", fontsize=10)
ax.scatter([], [], marker="*", s=80, color=GREEN, label="a short copier whose copy copies (F)")
ax.scatter([], [], s=14, color=BLUE, label="short copiers, none like that")
ax.scatter([], [], s=6, color=LIGHT, label="no short copier")
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
by = S["by_v"]
w = 0.36
for i, v in enumerate(range(1, 6)):
    for k, col, off in (("F", GREEN, -w / 2), ("N", BLUE, w / 2)):
        j, n = by[str(v)][k]
        if not n:
            continue
        ax2.bar(i + off, j / n, w, color=col)
        ax2.text(i + off, j / n + 0.02, f"{j}/{n}", ha="center", fontsize=7)
ax2.set_xticks(range(5), ["'.'\nheads +1", "'.'\nheads −1", "','\nheads +1", "loops\non head 1", "'+' '−'\non head 1"],
               fontsize=8)
ax2.set_ylim(0, 1.15)
ax2.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0", "25%", "50%", "75%", "100%"])
ax2.set_ylabel("soups that made replicators\nwithin 16,000 rounds")
ax2.set_title("Soups (2^14 programs, 4 per rule)", fontsize=10)
ax2.legend(handles=[Patch(color=GREEN, label="F rules"), Patch(color=BLUE, label="other rules")], frameon=False,
           fontsize=8, loc="upper right", bbox_to_anchor=(1.0, 1.12), ncol=2)
fig.savefig("docs/assets/report/e70-instrset.png")
print("saved docs/assets/report/e70-instrset.png")
