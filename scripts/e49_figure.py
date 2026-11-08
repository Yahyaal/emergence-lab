"""E-49 figure: mean share of races won by the later replicator, by soup and by time gap, with the same-round control."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

d = json.load(open("docs/data/experiments/2026-11-08-e49-time-races.json"))
R = [r for r in d["results"] if r["n"] >= 8]
fig, ax = plt.subplots(1, 2, figsize=(11, 4))


def bar(axx, groups, title):
    for x, (lab, rr, c) in enumerate(groups):
        v = [r["b_share"] for r in rr]
        m, se = np.mean(v), np.std(v) / np.sqrt(len(v))
        axx.bar(x, m - 0.5, bottom=0.5, color=c, yerr=2 * se, capsize=3)
        axx.text(x, 0.425, f"{len(v)} pairs", ha="center", fontsize=7)
    axx.axhline(0.5, c="k", lw=0.6)
    axx.set_xticks(range(len(groups)), [g[0] for g in groups], fontsize=8)
    axx.set_ylim(0.42, 0.6)
    axx.set_ylabel("mean share of races won by the later replicator")
    axx.set_title(title, fontsize=9)


cross = [r for r in R if r["kind"] == "cross"]
same = [r for r in R if r["kind"] == "same"]
bar(ax[0], [(f"soup {s}", [r for r in cross if r["seed"] == s], "#1f77b4") for s in (901, 5006, 5010)]
    + [("same round\n(control)", same, "#7f7f7f")], "By soup (all gaps)")
bar(ax[1], [(g.replace("->", " → "), [r for r in cross if r["gap"] == g], "#1f77b4") for g in ("2000->6000", "6000->12000", "2000->12000")]
    + [("same round\n(control)", same, "#7f7f7f")], "By time gap (rounds after the jump)")
fig.suptitle("E-49: later vs earlier verified replicators of the same soup (bars: ±2 s.e.)", fontsize=10)
fig.tight_layout()
fig.savefig("docs/assets/report/e49-time-races.png", dpi=130)
