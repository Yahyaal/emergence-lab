"""Picture for E-68: 48 random programs of a 16-byte soup and of a 128-byte soup (both F rules, h1 = L), at the start
and after 2,000 rounds. Each row is a program, each cell a byte: instructions coloured, other bytes grey.
Replays E-68 seeds (soups are deterministic given the seed).

    python scripts/e68_soup_picture.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402

OPS = b"<>{}-+.,[]"
COLS = ["#4c72b0", "#4c72b0", "#55a868", "#55a868", "#c44e52", "#c44e52", "#e8a33d", "#e8a33d", "#222222", "#222222"]


def picture(P):
    img = np.full(P.shape, 10)
    for i, o in enumerate(OPS):
        img[P == o] = i
    return img


def soup_rows(L, seed, rounds):
    K.set_length(L)
    C.H1 = L
    s = C.CounterfactualSoup(n=2 ** 14, length=L, seed=seed)
    rng = np.random.default_rng(1)
    idx = rng.choice(2 ** 14, 48, replace=False)
    start = s.programs[idx].copy()
    for _ in range(rounds):
        s.epoch()
    return start, s.programs[idx].copy()


cmap = ListedColormap(COLS + ["#e6e6e6"])
fig, axes = plt.subplots(1, 4, figsize=(14, 4.2), gridspec_kw={"width_ratios": [40, 40, 128, 128], "wspace": 0.1})
# E-68 seeds: L = 16, h1 = 16 is 6800 (no jump); L = 128, h1 = 128 is 6930 (jumped at 250)
for (L, seed), pair in zip(((16, 6800), (128, 6930)), ((0, 1), (2, 3))):
    a, b = soup_rows(L, seed, 2000)
    for ax, P, t in ((axes[pair[0]], a, "start"), (axes[pair[1]], b, "after 2,000 rounds")):
        ax.imshow(picture(P), cmap=cmap, vmin=0, vmax=10, aspect="auto", interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{L}-byte programs\n{t}", fontsize=9)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLS[::2]] + [plt.Rectangle((0, 0), 1, 1, color="#e6e6e6")]
fig.legend(handles, ["move pointer 1 (< >)", "move pointer 2 ({ })", "add / subtract (+ -)", "copy (. ,)", "loop ([ ])",
                     "not an instruction"], loc="lower center", ncol=6, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.04))
fig.savefig("docs/assets/report/e68-soups.png", dpi=130, bbox_inches="tight")
print("saved docs/assets/report/e68-soups.png")
