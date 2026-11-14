"""Figure for E-68 and E-69: the tape-length family. Left: census per program length L (rows) of every head1 start
(x = h1 / L, so 1 = half a tape apart), coloured by class. Right: soups, jumped / run per rule class and L.

    python scripts/e68_figure.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, GREEN, LIGHT, GREY = "#2f6db5", "#2e8b57", "#d5d8dd", "#8a8f98"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
C = json.load(open("docs/data/experiments/2026-11-09-e68-census.json"))
S = json.load(open("docs/data/experiments/2026-11-09-e68-soups.json"))["summary"]
LS = (16, 32, 64, 128)
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.3, 1.1], "wspace": 0.3})
for row, L in enumerate(LS):
    rs = [r for r in C["rules"] if r["L"] == L]
    for r in rs:
        x = r["h"] / L
        if r["class"] == "F":
            ax.scatter(x, row, s=120, marker="*", color=GREEN, zorder=3)
        elif r["copiers"] > 0:
            ax.scatter(x, row, s=14, color=BLUE, zorder=2)
        else:
            ax.scatter(x, row, s=6, color=LIGHT, zorder=1)
    nF = sum(r["class"] == "F" for r in rs)
    ax.text(2.03, row, f"{nF} F of {len(rs)}", va="center", fontsize=8, color=GREEN)
ax.set_yticks(range(len(LS)), [f"L = {L}" for L in LS])
ax.set_xlim(-0.05, 2.25)
ax.set_xticks([0, 0.5, 1, 1.5, 2], ["0", "L/2", "L\n(half a tape)", "3L/2", "2L"])
ax.set_xlabel("byte where pointer 2 starts (tape = 2L bytes)")
ax.set_title("Census of every start, per program length", fontsize=10)
ax.scatter([], [], marker="*", s=80, color=GREEN, label="a short copier whose copy copies (F)")
ax.scatter([], [], s=14, color=BLUE, label="short copiers, none like that")
ax.scatter([], [], s=6, color=LIGHT, label="no short copier")
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
by = S["by_L"]
B69 = json.load(open("docs/data/experiments/2026-11-09-e69-bytes.json"))["summary"]["by_L"]
x = range(len(LS))
w = 0.2
for i, L in enumerate(LS):
    bars = [("F", by[str(L)]["F"], GREEN, None, -1.5 * w)]
    if str(L) in B69:
        bars.append(("F69", B69[str(L)]["F"], GREEN, "///", -0.5 * w))
    else:
        bars.append(("F69", by[str(L)]["F"] if L == 128 else None, GREEN, "///", -0.5 * w))
    bars.append(("N", by[str(L)]["N"] if by[str(L)]["N"][1] else None, BLUE, None, 0.5 * w))
    if str(L) in B69:
        bars.append(("N69", B69[str(L)]["N"], BLUE, "///", 1.5 * w))
    for k, v, col, hatch, off in bars:
        if v is None:
            if k == "N":
                ax2.text(i + off, 0.02, "not\nrun", ha="center", fontsize=6.5, color=GREY)
            continue
        f = v[0] / v[1]
        ax2.bar(i + off, f, w, color=col if hatch is None else "white", edgecolor=col, hatch=hatch, lw=1.2)
        ax2.text(i + off, f + 0.02, f"{v[0]}/{v[1]}", ha="center", fontsize=6, rotation=90, va="bottom")
from matplotlib.patches import Patch
hand = [Patch(color=GREEN, label="F rules, 2^14 programs (E-68)"),
        Patch(facecolor="white", edgecolor=GREEN, hatch="///", label="F rules, 2^21 bytes (E-69; at L = 128 both)"),
        Patch(color=BLUE, label="other rules, 2^14 programs (E-68)"),
        Patch(facecolor="white", edgecolor=BLUE, hatch="///", label="other rules, 2^21 bytes (E-69)")]
ax2.set_xticks(list(x), [f"L = {L}" for L in LS])
ax2.set_ylim(0, 1.45)
ax2.set_yticks([0, 0.25, 0.5, 0.75, 1], ["0", "25%", "50%", "75%", "100%"])
ax2.set_ylabel("soups that made replicators\nwithin 16,000 rounds")
ax2.set_title("Soups: same number of programs vs same number of bytes", fontsize=10)
ax2.legend(handles=hand, frameon=False, fontsize=7, loc="upper left")
fig.savefig("docs/assets/report/e68-tapelength.png")
print("saved docs/assets/report/e68-tapelength.png")
