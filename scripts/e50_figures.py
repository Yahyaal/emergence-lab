"""Figure for E-50: transition rate vs soup size, and real jumps vs brief spikes.

    python scripts/e50_figures.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2

BLUE, ORANGE, GREY, RED = "#2f6db5", "#e08a1e", "#8a8f98", "#c8453c"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
d = json.load(open("docs/data/experiments/2026-11-08-e50-soup-size.json"))
A, fit = d["analysis"]["arms"], d["analysis"]["fit"]
# verified-only (post hoc): E-41 2^14 events were verified; E-50 counts soups with a replicator at the scan
ver = {16384: 2}
for r in d["soups"]:
    ver[r["n"]] = ver.get(r["n"], 0) + int(r["transitioned"] and r["replicator"])


def ci(k, t):
    lo = chi2.ppf(0.025, 2 * k) / 2 if k else 0.0
    hi = chi2.ppf(0.975, 2 * k + 2) / 2
    return lo / t, hi / t


fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ns = sorted(int(n) for n in A)
for off, key, c, lab in ((-0.04, "all", BLUE, "HOE ≥ 1 (pre-registered)"), (0.04, "ver", ORANGE, "with a verified replicator (post hoc)")):
    for n in ns:
        k = A[str(n)]["transitioned"] if key == "all" else ver[n]
        t = A[str(n)]["exposure"]
        lo, hi = ci(k, t)
        x = np.log2(n) + off
        y = max(k / t, 2e-7)
        ax[0].errorbar(x, y * 1e6, yerr=[[(y - lo) * 1e6 if k else 0], [(hi - y) * 1e6]], fmt="o" if k else "v", c=c,
                       label=lab if n == ns[0] else None, capsize=3)
ax[0].annotate("0 of 12\n(upper bound)", (15, 0.2), xytext=(8, 4), textcoords="offset points", fontsize=7.5)
xs = np.linspace(12.8, 16.2, 50)
lam0 = sum(A[str(n)]["transitioned"] for n in ns) / sum(A[str(n)]["exposure"] * (n / 2 ** 14) ** fit["beta"] for n in ns)
ax[0].plot(xs, lam0 * 2 ** (fit["beta"] * (xs - 14)) * 1e6, c=GREY, lw=1, label=f"fit: rate ∝ size^{fit['beta']:.2f}")
ax[0].set_yscale("log")
ax[0].set_xticks([13, 14, 15, 16], ["8,192", "16,384\n(E-40/41)", "32,768", "65,536"])
ax[0].set_xlabel("programs in the soup")
ax[0].set_ylabel("jumps per million rounds (95% CI)")
ax[0].set_title("Bigger soups jump sooner (β = %.2f, p = %.3f)" % (fit["beta"], fit["p_one_sided"]), fontsize=10)
ax[0].legend(frameon=False, fontsize=7.5, loc="lower right")
for r in d["soups"]:
    if r["n"] == 65536 and r["transitioned"]:
        i = r["transition_epoch"] // 250 - 1
        e = np.arange(len(r["hoe"])) * 250 + 250
        sl = slice(max(0, i - 8), None)
        ax[1].plot(e[sl] - r["transition_epoch"], r["hoe"][sl], c=ORANGE if r["replicator"] else RED,
                   lw=1.5 if r["replicator"] else 1, ls="-" if r["replicator"] else "--")
ax[1].axhline(1.0, c=GREY, lw=0.8, ls=":")
ax[1].set_xlabel("rounds after first crossing HOE = 1")
ax[1].set_ylabel("order in the soup (HOE)")
ax[1].set_title("Largest soups: 3 real jumps (orange), 2 brief spikes (red)", fontsize=10)
fig.savefig("docs/assets/report/e50-soup-size.png")
print("ok")
