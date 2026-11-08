"""E-44 analysis: pre-registered outcomes, post-hoc checks, the mirror replicator, figures.

    python scripts/e44_analysis.py   # reads and annotates docs/data/experiments/2026-11-08-e44-bff-contests.json
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binomtest, fisher_exact, spearmanr

from emergence.observatory import replicators as RP
from emergence.programs import bff as B

OUT = "docs/data/experiments/2026-11-08-e44-bff-contests.json"
E42 = "docs/data/experiments/2026-11-08-e42-bff-heredity.json"
FIG = "docs/assets/report/"
INSTR = "<>{}+-.,[]"


def main() -> None:
    d = json.load(open(OUT))
    R = d["results"]
    A = {r["pair"]: r for r in R if r["batch"] == "A"}
    Bb = {r["pair"]: r for r in R if r["batch"] == "B"}
    fav = lambda r: r["verdict"] in ("a favoured", "b favoured")
    em = [r for r in A.values() if r["kind"] == "emergent"]
    nl = [r for r in A.values() if r["kind"].startswith("null")]
    k1, k2 = sum(map(fav, em)), sum(map(fav, nl))
    an = {"primary": {"emergent_favoured": k1, "emergent_n": len(em), "null_favoured": k2, "null_n": len(nl),
                      "fisher_p": float(fisher_exact([[k1, len(em) - k1], [k2, len(nl) - k2]], alternative="greater")[1])}}
    # post hoc: do batch A and batch B agree on the direction / size of the effect?
    for kind in ("emergent", "handwritten", "null_designed", "null_emergent"):
        ks = [k for k in A if A[k]["kind"] == kind]
        rho, p = spearmanr([A[k]["mean_s"] for k in ks], [Bb[k]["mean_s"] for k in ks])
        an[f"posthoc_AB_spearman_{kind}"] = {"rho": round(float(rho), 3), "p": round(float(p), 3), "n": len(ks)}
    s = [v for r in R if r["kind"] == "handwritten" for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    # s > 0 means b (the emergent replicator) ended more common, so hand-written wins are s < 0
    an["handwritten_replicate_wins"] = {"wins": int(sum(v < 0 for v in s)), "n": len(s),
                                        "p": float(binomtest(sum(v < 0 for v in s), len(s)).pvalue)}
    # post hoc pattern seen in the matrix: the mirror pair (#5, #6, soup 5006) against the soup-901 replicators.
    # Caveat: each mirror replicator's family counts only its own orientation (half of the species).
    s = [v for r in R if r["kind"] == "emergent" and r["i"] in (0, 1, 2, 3) and r["j"] in (5, 6)
         for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    an["posthoc_mirror_vs_901_replicate_wins"] = {"wins": int(sum(v > 0 for v in s)), "n": len(s),
                                                 "p": float(binomtest(sum(v > 0 for v in s), len(s)).pvalue)}
    # the mirror pair: replicators 5 and 6 of E-42 are exact byte reversals of each other
    P = [np.frombuffer(bytes.fromhex(r["program"]), np.uint8).copy() for r in json.load(open(E42))["results"]]
    rev = [[round(float((P[i] == P[j][::-1]).mean()), 3) for j in range(9)] for i in range(9)]
    rng = np.random.default_rng(7)
    first = []
    for _ in range(32):
        z = rng.integers(0, 256, 64, dtype=np.uint8)
        a, b = B.interact(P[5], z)
        first.append([bool((a == P[5]).all()), bool((b == P[5][::-1]).all())])
    alone = []
    for rep in range(8):
        g = np.random.default_rng([99, 5, rep])
        progs = g.integers(0, 256, (1024, 64), dtype=np.uint8)
        progs[g.permutation(1024)[:8]] = P[5]
        soup = B.Soup(n=1024, length=64, mutation=0.0, seed=int(g.integers(2 ** 31)), programs=progs)
        for _ in range(96):
            soup.epoch()
        alone.append([int(RP.similar(soup.programs, P[5]).sum()), int(RP.similar(soup.programs, P[6]).sum())])
    an["mirror"] = {"reverse_identity": rev, "p5_first_keeps_self_and_writes_reverse": [sum(x[0] for x in first), sum(x[1] for x in first), 32],
                    "p5_alone_counts_p5_p6": alone}
    d["analysis"] = an
    json.dump(d, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in an.items() if k != "mirror"}, indent=1))
    print("mirror", an["mirror"]["p5_first_keeps_self_and_writes_reverse"], alone)

    # figure 1: mean s matrix (A and B pooled) for the 9 emergent + hand-written
    labels = [f"{r['soup']}\n@{r['epoch']//1000}k" for r in json.load(open(E42))["results"]] + ["hand-\nwritten"]
    M = np.full((10, 10), np.nan)
    for r in R:
        if r["kind"] not in ("emergent", "handwritten"):
            continue
        i = r["i"] if r["i"] >= 0 else 9
        j = r["j"]
        v = np.nanmean([M[i, j], -r["mean_s"]]) if not np.isnan(M[i, j]) else -r["mean_s"]
        M[i, j], M[j, i] = v, -v
    fig, ax = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})
    im = ax[0].imshow(M, cmap="RdBu", vmin=-3, vmax=3)
    ax[0].set_xticks(range(10), labels, fontsize=7)
    ax[0].set_yticks(range(10), labels, fontsize=7)
    for (i, j), v in np.ndenumerate(M):
        if not np.isnan(v):
            ax[0].text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=6)
    ax[0].set_title("Row vs column: mean log-ratio (blue = row ends more common)\n16 + 16 replicate races per pair", fontsize=9)
    plt.colorbar(im, ax=ax[0], fraction=0.046)
    ks = [k for k in A if A[k]["kind"] in ("emergent", "handwritten", "null_designed", "null_emergent")]
    col = {"emergent": "#1f77b4", "handwritten": "#d62728", "null_designed": "#7f7f7f", "null_emergent": "#bcbd22"}
    for kind in col:
        kk = [k for k in ks if A[k]["kind"] == kind]
        ax[1].scatter([A[k]["mean_s"] for k in kk], [Bb[k]["mean_s"] for k in kk], c=col[kind], s=22,
                      label=kind.replace("_", " "))
    ax[1].axhline(0, c="k", lw=0.5)
    ax[1].axvline(0, c="k", lw=0.5)
    ax[1].set_xlabel("batch A mean log-ratio")
    ax[1].set_ylabel("batch B (fresh soups) mean log-ratio")
    ax[1].set_title(f"Does a pair's result repeat? emergent pairs: Spearman "
                    f"{an['posthoc_AB_spearman_emergent']['rho']} (p {an['posthoc_AB_spearman_emergent']['p']})", fontsize=9)
    ax[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG + "e44-bff-contests.png", dpi=130)

    # figure 2: the mirror replicator
    z = np.random.default_rng(3).integers(0, 256, 64, dtype=np.uint8)
    a, b = B.interact(P[5], z)
    rows = [("replicator #5", P[5]), ("random partner", z), ("partner after one interaction", b),
            ("#5 read backwards", P[5][::-1]), ("replicator #6 (found in the soup)", P[6])]
    fig, axs = plt.subplots(len(rows), 1, figsize=(12, 3.6))
    for axx, (name, prog) in zip(axs, rows):
        axx.imshow(prog[None, :], cmap="viridis", aspect="auto", vmin=0, vmax=255)
        for k, v in enumerate(prog):
            ch = chr(v)
            if ch in INSTR:
                axx.text(k, 0, ch, ha="center", va="center", color="white", fontsize=8, fontweight="bold")
        axx.set_yticks([])
        axx.set_xticks([])
        axx.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=8)
    fig.suptitle("A mirror replicator (soup 5006): it writes its own reverse into its partner; the reverse does the same", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG + "e44-mirror-replicator.png", dpi=130)


if __name__ == "__main__":
    main()
