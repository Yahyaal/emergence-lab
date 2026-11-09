"""Exploratory follow-up to E-60 (not pre-registered, J-061): soup 6031 (head1 starts at 7) reached high HOE and
execution with no aligned copier. Replay it deterministically to round 14,750 (= T + 1,000) and ask whether its
common programs copy themselves to a SHIFTED position in the partner, or shifted within the pair.

    python scripts/e60_shifted.py --out docs/data/experiments/2026-11-08-e60-shifted.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402

SEED, H1, END = 6031, 7, 14750


def best_match(prog: np.ndarray, half: np.ndarray) -> tuple[int, int, str]:
    """Best agreement of `half` (64 bytes) with `prog` rotated by d, forwards or reversed."""
    best = (0, 0, "")
    for d in range(64):
        for name, q in (("fwd", prog), ("rev", prog[::-1])):
            m = int((np.roll(q, d) == half).sum())
            if m > best[0]:
                best = (m, d, name)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C.H1 = H1
    soup = C.CounterfactualSoup(n=2 ** 14, seed=SEED)
    while soup.epochs < END:
        soup.epoch()
    np.save(f"runs/e60/{SEED}-{END}.npy", soup.programs)
    X = C.distinct_top(soup.programs)
    rng = np.random.default_rng(61)
    rows = []
    for x in X:
        res = []
        for _ in range(4):
            tape = np.concatenate([x, rng.integers(0, 256, 64, dtype=np.uint8)]).astype(np.uint8)
            K.lib().run_tape(tape.ctypes.data, 128, K.STEPS, H1)
            pm = best_match(x, tape[64:])
            sm = best_match(x, tape[:64])
            res.append({"partner_best": pm, "self_best": sm})
        n_copy = sum(r["partner_best"][0] >= 56 for r in res)
        rows.append({"program": x.tobytes().hex(), "partner_copies_ge56": n_copy,
                     "partner_best": [r["partner_best"] for r in res], "self_best": [r["self_best"] for r in res],
                     "aligned_label": K.label(K.classify(x[None], H1, 4, 62)[0])})
    shifted = [r for r in rows if r["partner_copies_ge56"] >= 3]
    out = {"seed": SEED, "h1": H1, "round": END, "programs": len(rows), "shifted_copiers": len(shifted),
           "aligned_copiers": sum(r["aligned_label"] != "none" for r in rows),
           "offsets": sorted({(b[1], b[2]) for r in shifted for b in r["partner_best"]}), "rows": rows}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, default=str))
    for r in rows[:8]:
        print(r["aligned_label"], r["partner_copies_ge56"], r["partner_best"][0], r["self_best"][0])


if __name__ == "__main__":
    main()
