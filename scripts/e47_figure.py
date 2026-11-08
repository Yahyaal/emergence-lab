"""E-47 figure: after the transition, the most common program's family share and its identity to the founder."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open("docs/data/experiments/2026-11-08-e47-turnover.json"))
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for q, c in zip(d["sequences"], ("#1f77b4", "#d62728", "#2ca02c")):
    tr = [r for r in q["track"] if r["identity_to_first"] is not None]
    ep = [r["epoch"] - q["species"][0]["first"] for r in tr]
    ax[0].plot(ep, [r["top_species_share"] * 100 for r in tr], c=c, lw=1, label=f"soup {q['seed']}")
    ax[1].plot(ep, [r["identity_to_first"] * 100 for r in tr], c=c, lw=1, label=f"soup {q['seed']}")
ax[0].axhline(5, c="k", lw=0.6, ls="--")
ax[0].text(0, 5.5, "pre-registered 5% threshold for a 'dominant species'", fontsize=7)
ax[0].set_ylabel("% of soup in the most common program's family")
ax[1].set_ylabel("% of bytes shared with the first dominant program")
for a in ax:
    a.set_xlabel("rounds after the transition")
    a.legend(fontsize=8)
ax[0].set_title("No family dominates: the most common one holds ~2%", fontsize=9)
ax[1].set_title("The most common program drifts away from the founder", fontsize=9)
fig.tight_layout()
fig.savefig("docs/assets/report/e47-turnover.png", dpi=130)
