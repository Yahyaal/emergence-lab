"""E-48 figure: late-vs-early race shares per soup, with same-time pairs as the drift control."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("docs/data/experiments/2026-11-08-e48-time-races.json"))
R = [r for r in d["results"] if r["n"] >= 8]
fig, ax = plt.subplots(1, 2, figsize=(12, 5))
rng = np.random.default_rng(0)
for x, seed in enumerate((901, 5006, 5010)):
    for off, kind, c in ((-0.2, "cross", "#1f77b4"), (0.2, "same", "#7f7f7f")):
        v = [r["b_share"] if kind == "cross" else 1 - r["b_share"] for r in R if r["seed"] == seed and r["kind"].startswith(kind)]
        ax[0].scatter(x + off + rng.uniform(-0.07, 0.07, len(v)), v, s=12, c=c, alpha=0.7)
        ax[0].plot([x + off - 0.12, x + off + 0.12], [np.mean(v)] * 2, c="k", lw=2)
ax[0].axhline(0.5, c="k", lw=0.6, ls="--")
ax[0].set_xticks(range(3), ["soup 901", "soup 5006", "soup 5010"])
ax[0].set_ylabel("share of races won")
ax[0].scatter([], [], c="#1f77b4", label="late program vs early program (10,000 vs 1,000 rounds after the jump)")
ax[0].scatter([], [], c="#7f7f7f", label="more common vs less common program, same round")
ax[0].legend(fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=1)
ax[0].set_title("Is later code fitter? It depends on the soup", fontsize=9)
same = [r for r in R if r["kind"] != "cross"]
gaps = range(1, 6)
ax[1].bar(list(gaps), [np.mean([1 - r["b_share"] for r in same if r["j"] - r["i"] == g]) for g in gaps], color="#7f7f7f")
ax[1].axhline(0.5, c="k", lw=0.6, ls="--")
ax[1].set_ylim(0.4, 0.7)
ax[1].set_xlabel("gap in abundance rank between the two contemporaries")
ax[1].set_ylabel("mean share of races won by the more common one")
ax[1].set_title("Post hoc: among contemporaries, commoner programs tend to win", fontsize=9)
fig.tight_layout()
fig.savefig("docs/assets/report/e48-time-races.png", dpi=130)
