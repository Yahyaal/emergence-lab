"""Figure for E-68: the tape-length family. Left: census per program length L (rows) of every head1 start
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
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw={"width_ratios": [1.4, 1], "wspace": 0.3})
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
x = range(len(LS))
fF = [by[str(L)]["F"][0] / max(by[str(L)]["F"][1], 1) for L in LS]
fN = [by[str(L)]["N"][0] / by[str(L)]["N"][1] if by[str(L)]["N"][1] else None for L in LS]
ax2.bar([i - 0.2 for i in x], fF, 0.4, color=GREEN, label="F rules")
ax2.bar([i + 0.2 for i in x if fN[i] is not None], [v for v in fN if v is not None], 0.4, color=BLUE, label="other rules")
for i, L in enumerate(LS):
    ax2.text(i - 0.2, fF[i] + 0.02, f"{by[str(L)]['F'][0]}/{by[str(L)]['F'][1]}", ha="center", fontsize=8)
    if fN[i] is not None:
        ax2.text(i + 0.2, fN[i] + 0.02, f"{by[str(L)]['N'][0]}/{by[str(L)]['N'][1]}", ha="center", fontsize=8)
    else:
        ax2.text(i + 0.2, 0.02, "not run\n(E-61–E-63)", ha="center", fontsize=7, color=GREY)
ax2.set_xticks(list(x), [f"L = {L}" for L in LS])
ax2.set_ylim(0, 1.12)
ax2.set_ylabel("soups that made replicators\nwithin 16,000 rounds")
ax2.set_title(f"Soups (2^14 programs): F {S['jumped']['F']}/{S['of']['F']}, other {S['jumped']['N']}/{S['of']['N']} "
              f"(L ≠ 64), p = {S['fisher_p']:.0e}", fontsize=10)
ax2.legend(frameon=False, fontsize=8)
fig.savefig("docs/assets/report/e68-tapelength.png")
print("saved docs/assets/report/e68-tapelength.png")
