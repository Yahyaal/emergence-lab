"""E-45 figure: share of races won by the mirror replicator species, per opponent, with the null."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta

d = json.load(open("docs/data/experiments/2026-11-08-e45-mirror-contests.json"))
names = {0: "901@9.75k #0", 1: "901@9.75k #1", 2: "901@16k #2", 3: "901@16k #3", 4: "5006@28k #4", 7: "5010@17k #7",
         8: "5010@32k #8", -1: "hand-written"}
rows = []
for r in d["results"]:
    s = [v for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    w, n = sum(v < 0 for v in s), len(s)
    lab = names.get(r["j"], f"null {-r['j'] - 1}") if r["kind"] != "null" else f"null: H vs redrawn tail {-r['j'] - 1}"
    rows.append((r["kind"], lab, w / n, beta.ppf(0.025, w + .5, n - w + .5), beta.ppf(0.975, w + .5, n - w + .5), r["verdict"]))
col = {"primary": "#1f77b4", "secondary": "#9467bd", "null": "#7f7f7f"}
fig, ax = plt.subplots(figsize=(8, 4.6))
for y, (k, lab, sh, lo, hi, v) in enumerate(rows):
    ax.errorbar(sh, y, xerr=[[sh - lo], [hi - sh]], fmt="o", c=col[k], capsize=3)
    ax.text(1.01, y, v, va="center", fontsize=7, transform=ax.get_yaxis_transform())
ax.axvline(0.5, c="k", lw=0.6, ls="--")
ax.set_yticks(range(len(rows)), [("mirror vs " if k != "null" else "") + lab for k, lab, *_ in rows], fontsize=8)
ax.invert_yaxis()
ax.set_xlim(0.25, 0.9)
ax.set_xlabel("share of races won by the first-named side (64 races each, 95% interval)")
ax.set_title("E-45: the mirror replicator species beats other emergent replicators", fontsize=10)
fig.tight_layout()
fig.savefig("docs/assets/report/e45-mirror-contests.png", dpi=130)
