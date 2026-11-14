"""Picture for E-70: 48 random programs of two soups of the auto-advancing copy variant (v1: '.' then both heads
+1), one in an F rule (h1 = 64) and one in a rule with copiers but none self-sufficient (h1 = 69), at the start and
after 500 rounds. Replays E-70 seeds 7000 and 7030 (soups are deterministic given the seed).

    python scripts/e70_soup_picture.py
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

OPS = b"<>{}-+.,[]"
COLS = ["#4c72b0", "#4c72b0", "#55a868", "#55a868", "#c44e52", "#c44e52", "#e8a33d", "#e8a33d", "#222222", "#222222"]


def picture(P):
    img = np.full(P.shape, 10)
    for i, o in enumerate(OPS):
        img[P == o] = i
    return img

ROUNDS = 500


def soup_rows(code, seed):
    C.H1 = code
    s = C.CounterfactualSoup(n=2 ** 14, length=64, seed=seed)
    idx = np.random.default_rng(1).choice(2 ** 14, 48, replace=False)
    start = s.programs[idx].copy()
    for _ in range(ROUNDS):
        s.epoch()
    return start, s.programs[idx].copy()


cmap = ListedColormap(COLS + ["#e6e6e6"])
fig, axes = plt.subplots(1, 4, figsize=(14, 4.2), gridspec_kw={"wspace": 0.1})
for (h, seed, name), pair in zip(((64, 7000, "pointer 2 at byte 64 (F)"), (69, 7030, "pointer 2 at byte 69 (other)")),
                                 ((0, 1), (2, 3))):
    a, b = soup_rows(h + 65536, seed)
    for ax, P, t in ((axes[pair[0]], a, "start"), (axes[pair[1]], b, f"after {ROUNDS} rounds")):
        ax.imshow(picture(P), cmap=cmap, vmin=0, vmax=10, aspect="auto", interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(f"{name}\n{t}", fontsize=9)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in COLS[::2]] + [plt.Rectangle((0, 0), 1, 1, color="#e6e6e6")]
fig.legend(handles, ["move pointer 1 (< >)", "move pointer 2 ({ })", "add / subtract (+ -)", "copy (. ,)", "loop ([ ])",
                     "not an instruction"], loc="lower center", ncol=6, frameon=False, fontsize=8, bbox_to_anchor=(0.5, -0.04))
fig.savefig("docs/assets/report/e70-soups.png", dpi=130, bbox_inches="tight")
print("saved docs/assets/report/e70-soups.png")
