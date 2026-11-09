"""Figure for E-61-E-63: shift-aware short copiers in the forward band of head-start rules, and real replicator
soups under the strict D-047 criterion.

    python scripts/e63_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, GREY, GREEN = "#2f6db5", "#8a8f98", "#2e8b57"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = json.load(open("docs/data/experiments/2026-11-08-e61-census.json"))["rules"]
jumps = {}
for f in ("docs/data/experiments/2026-11-09-e62-soups.json", "docs/data/experiments/2026-11-09-e63-outside.json"):
    for r in json.load(open(f))["results"]:
        j, n = jumps.get(r["h1"], (0, 0))
        jumps[r["h1"]] = (j + r["jumped"], n + 1)
lo, hi = 52, 90
h = np.arange(lo, hi + 1)
fw = np.array([C[k]["forward"] for k in h])
ss = np.array([C[k]["self_sufficient"] for k in h])
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 5.4), sharex=True, gridspec_kw={"height_ratios": [1.2, 1]})
for a in (ax, ax2):
    a.axvspan(60.5, 68.5, color=GREEN, alpha=0.08, lw=0)
ax.bar(h, fw, 0.85, color=BLUE, label="short forward copiers (any shift up to 16 bytes)")
ax.scatter(h[ss > 0], fw[ss > 0] + 10, marker="*", s=70, color=GREEN, zorder=3,
           label="one of them makes a copy that copies again (F′)")
ax.set_ylabel("copiers of 5–6\ninstructions")
ax.legend(frameon=False, fontsize=8.5, loc="upper right")
ax.set_title("Near byte 64: which rules have a short copier whose copy copies (top), and which make replicators (bottom)",
             fontsize=10)
for k, (j, n) in sorted(jumps.items()):
    inside = C[k]["self_sufficient"] > 0
    ax2.bar(k, 100 * j / n, 0.85, color=GREEN if inside else GREY)
    if not inside:
        ax2.text(k, 100 * j / n + 3, f"{j}/{n}", ha="center", fontsize=7.5)
inside_j = [jumps[k] for k in jumps if C[k]["self_sufficient"] > 0]
ax2.text(64.5, 104, f"every soup: {sum(j for j, _ in inside_j)}/{sum(n for _, n in inside_j)}", ha="center", fontsize=8)
ax2.set_ylim(0, 120)
ax2.set_ylabel("% of soups with real\nreplicators by 16,000")
ax2.set_xlabel("h: byte where pointer 2 starts (64 = the partner's first byte)")
ax2.set_xticks([52, 56, 60, 64, 68, 72, 76, 80, 84, 88])
fig.savefig("docs/assets/report/e63-boundary.png")
print("saved docs/assets/report/e63-boundary.png")
