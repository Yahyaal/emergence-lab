"""Figure for E-66: the replicator test repeated 10 times on the 2,800 E-54 top programs, and the parasite test.
Left: how many of 10 repeats grew, by the single-test E-54 verdict. Middle: per soup, share of top programs that copy
themselves, single test (E-54) vs repeated test. Right: parasite-test verdicts of the programs that never grew.

    python scripts/e66_figure.py
"""
import json
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BLUE, ORANGE, GREEN, GREY, LIGHT = "#2f6db5", "#e07b28", "#2e8b57", "#8a8f98", "#d5d8dd"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
D = json.load(open("docs/data/experiments/2026-11-09-e66-parasites.json"))
A, S = D["partA"], D["summary"]
fig, axs = plt.subplots(1, 3, figsize=(14, 4.4), gridspec_kw={"width_ratios": [1.2, 1, 1], "wspace": 0.4})
ax = axs[0]
xs = np.arange(11)
bottom = np.zeros(11)
for v, col, lab in (("replicator", GREEN, "E-54 said: replicator"), ("one generation", BLUE, "E-54 said: one generation"),
                    ("no replication", ORANGE, "E-54 said: no replication")):
    c = Counter(r["gen1_ok"] for r in A if r["e54"] == v)
    h = np.array([c.get(k, 0) for k in xs])
    ax.bar(xs, h, bottom=bottom, color=col, label=lab, width=0.8)
    bottom += h
ax.set_xticks(xs)
ax.set_xlabel("repeats (of 10) in which the program's copies grew")
ax.set_ylabel("programs (of 2,800)")
ax.set_title("Same programs, tested 10 more times", fontsize=10)
ax.legend(frameon=False, fontsize=8)
ax = axs[1]
bs = S["by_soup"]
soups = list(bs)
y = np.arange(len(soups))
ax.barh(y + 0.2, [100 * bs[s]["e54_replicator_frac"] for s in soups], 0.4, color=LIGHT, label="one test: 'replicator' (E-54)")
ax.barh(y - 0.2, [100 * bs[s]["self_copier_frac"] for s in soups], 0.4, color=GREEN, label="grew in any of 10 tests (E-66)")
ax.set_yticks(y, [f"soup {s}" for s in soups])
ax.set_xlim(0, 100)
ax.set_xlabel("% of the 40 most common programs (all snapshots)")
ax.set_title("Most common programs that copy themselves", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.17))
ax = axs[2]
vc = Counter(r["verdict"] for r in D["partB"])
vr = Counter(r["verdict"] for r in json.load(open("docs/data/experiments/2026-11-09-e66-rescore.json"))["rows"])
order = ["parasite", "context self-copier", "not copied"]
xs = np.arange(len(order))
ax.bar(xs - 0.2, [vc.get(k, 0) for k in order], 0.4, color=LIGHT, label="first version of the test")
ax.bar(xs + 0.2, [vr.get(k, 0) for k in order], 0.4, color=ORANGE, label="with the self-copy check")
ax.set_xticks(xs, ["parasite", "copies itself,\ndies when second", "not copied"], fontsize=8)
ax.set_yticks(range(0, 4))
ax.set_ylabel("programs")
ax.set_title(f"The {sum(vc.values())} of 2,800 that never grew", fontsize=10)
ax.legend(frameon=False, fontsize=8)
fig.savefig("docs/assets/report/e66-parasites.png")
print("saved docs/assets/report/e66-parasites.png")
