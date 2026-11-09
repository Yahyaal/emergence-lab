"""Figure for E-55: copy kernels under the standard rule and the counterfactual, plus a tape picture.

    python scripts/e55_figure.py
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, "scripts")
import bff_kernels as K  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

BLUE, ORANGE, GREY = "#2f6db5", "#e08a1e", "#8a8f98"
plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
d = json.load(open("docs/data/experiments/2026-11-08-e55-kernels.json"))
fig = plt.figure(figsize=(11, 4.6))
ax = fig.add_axes([0.05, 0.14, 0.27, 0.72])
x = np.arange(2)
for j, (lab, c) in enumerate((("reverse", ORANGE), ("forward", BLUE))):
    v = [d["totals_main"][p][lab] for p in ("standard", "counterfactual")]
    ax.bar(x + (j - 0.5) * 0.36, v, 0.34, color=c, label=f"{lab} copiers")
    for xi, vi in zip(x, v):
        ax.text(xi + (j - 0.5) * 0.36, vi + 2, str(vi), ha="center", fontsize=9)
ax.set_xticks(x, ["standard rule\n(head1 starts at 0)", "counterfactual\n(head1 starts at 64)"], fontsize=8.5)
ax.set_ylabel("copy kernels of ≤ 6 instructions")
ax.legend(frameon=False, fontsize=8.5)
ax.set_title("All 1.1 million short kernels", fontsize=10)

rng = np.random.default_rng(7)
f = K.NONOP_NZ[rng.integers(0, len(K.NONOP_NZ), 64)]
partner = rng.integers(0, 256, 64, dtype=np.uint8)
cmap = plt.get_cmap("viridis")
rows = []
for code, h1 in ((b"[{.>]", 0), (b"[.>}]", 64)):
    a = f.copy(); a[:5] = np.frombuffer(code, np.uint8)
    tape = np.concatenate([a, partner])
    rows.append((code.decode(), h1, tape))
ax2 = fig.add_axes([0.38, 0.1, 0.6, 0.8])
ax2.axis("off")


def run_h(tape, h1start):
    t = bytearray(bytes(tape)); n = len(t); ip = h0 = 0; h1 = h1start; s = 0
    while 0 <= ip < n and s < 8192:
        c = t[ip]
        if c == 60: h0 = (h0 - 1) % n
        elif c == 62: h0 = (h0 + 1) % n
        elif c == 123: h1 = (h1 - 1) % n
        elif c == 125: h1 = (h1 + 1) % n
        elif c == 45: t[h0] = (t[h0] - 1) % 256
        elif c == 43: t[h0] = (t[h0] + 1) % 256
        elif c == 46: t[h1] = t[h0]
        elif c == 44: t[h0] = t[h1]
        elif c == 91 and t[h0] == 0:
            dd, j = 1, ip + 1
            while j < n:
                dd += (t[j] == 91) - (t[j] == 93)
                if dd == 0: break
                j += 1
            if j >= n: break
            ip = j
        elif c == 93 and t[h0] != 0:
            dd, j = 1, ip - 1
            while j >= 0:
                dd += (t[j] == 93) - (t[j] == 91)
                if dd == 0: break
                j -= 1
            if j < 0: break
            ip = j
        ip += 1; s += 1
    return np.frombuffer(bytes(t), np.uint8)


y = 0
for code, h1, tape in rows:
    y0 = y
    after = run_h(tape, h1)
    for lab, tp in (("before", tape), ("after", after)):
        ax2.imshow(cmap(tp[None, :] / 255.0), extent=(0, 128, y, y + 1), aspect="auto")
        ax2.text(-1.5, y + 0.5, lab, ha="right", va="center", fontsize=8.5)
        y -= 1.35
    ax2.text(0, y0 + 1.12, f"kernel {code}  ({'standard rule' if h1 == 0 else 'counterfactual'}):  "
             + ("the partner becomes the program REVERSED" if h1 == 0 else "the partner becomes an exact copy"),
             fontsize=9, va="bottom")
    y -= 1.9
ax2.axvline(64, c="k", lw=1)
ax2.set_xlim(-14, 129); ax2.set_ylim(y + 1.4, 2.6)
ax2.text(32, 2.2, "program (bytes 0–63)", ha="center", fontsize=8.5)
ax2.text(96, 2.2, "partner (bytes 64–127)", ha="center", fontsize=8.5)
fig.suptitle("E-55: backwards copying is the easy kind because heads wrap around the tape", fontsize=11)
fig.savefig("docs/assets/report/e55-copy-kernels.png")
print("ok")
