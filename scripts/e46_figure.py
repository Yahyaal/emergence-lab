"""E-46 figure: win shares between replicator species (both forms counted), and the null distribution."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("docs/data/experiments/2026-11-08-e46-species-contests.json"))
order = [0, 1, 2, 3, 4, 5, 7, 8, -1]
lab = {0: "901@9.75k a", 1: "901@9.75k b", 2: "901@16k a", 3: "901@16k b", 4: "5006@28k\n(replaced)",
       5: "5006@32k\n(strongest)", 7: "5010@17k", 8: "5010@32k", -1: "hand-\nwritten"}
idx = {k: n for n, k in enumerate(order)}
M = np.full((9, 9), np.nan)
null = []
for r in d["results"]:
    s = [v for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    sh_a = sum(v < 0 for v in s) / len(s)
    if r["kind"] == "null":
        null.append(sh_a)
        continue
    i, j = idx[r["i"]], idx[r["j"]]
    M[i, j], M[j, i] = sh_a, 1 - sh_a
fig, ax = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.3, 1]})
im = ax[0].imshow(M, cmap="RdBu", vmin=0.2, vmax=0.8)
ax[0].set_xticks(range(9), [lab[k] for k in order], fontsize=7, rotation=60, ha="right")
ax[0].set_yticks(range(9), [lab[k] for k in order], fontsize=7)
for (i, j), v in np.ndenumerate(M):
    if not np.isnan(v):
        ax[0].text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6.5)
ax[0].set_title("Share of 64 races won by the row species (both forms counted)", fontsize=9)
plt.colorbar(im, ax=ax[0], fraction=0.046)
em = [M[i, j] for i in range(8) for j in range(8) if i < j]
ax[1].hist(null, bins=np.linspace(0.2, 0.8, 25), color="#7f7f7f", alpha=0.7, label="24 neutral controls")
ax[1].hist([max(v, 1 - v) for v in em], bins=np.linspace(0.2, 0.8, 25), histtype="step", color="#1f77b4", lw=2,
           label="28 emergent pairs (winner's share)")
for j in (0, 1, 2, 3, 4, 7, 8):
    ax[1].axvline(M[idx[5], idx[j]], color="#d62728", lw=1, alpha=0.7)
ax[1].plot([], [], color="#d62728", label="5006@32k species vs each other emergent species")
ax[1].set_xlabel("share of races won")
ax[1].set_title("Neutral controls sit near 0.5; the 5006@32k species is ahead of all 7 others", fontsize=9)
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig("docs/assets/report/e46-species-contests.png", dpi=130)
