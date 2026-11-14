"""E-73 fixtures: top-40 distinct programs of soups with known status, for validating a looser copy threshold.
Soups replay deterministically from their seeds (the soup RNG is independent of detection).

    PYTHONPATH=scripts python scripts/bff_fidelity_fixtures.py
"""
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402

OUT = Path(__file__).parent / "fixtures"
# name: (code, seed, rounds, status)
SOUPS = {
    "sloppy_v2_g57": (122 + 256 * 57 + 65536 * 2, 7220, 600, "sloppy replicators (E-72; HOE 6.4, D-050 0 copiers)"),
    "sloppy_v2_g58": (122 + 256 * 58 + 65536 * 2, 7230, 600, "sloppy replicators (E-72; HOE 6.5, D-050 0 copiers)"),
    "exact_v1_h64": (64 + 65536 * 1, 7000, 600, "exact replicators (E-70; D-050 jump at 250)"),
    "exact_v2_h64": (64 + 65536 * 2, 7060, 600, "exact replicators (E-70 v2/64; D-050 jump at 250)"),
    "exact_v3_h64": (64 + 65536 * 3, 7120, 600, "exact replicators (E-70 v3/64; D-050 jump at 250)"),
    "transient_v4_g64": (124 + 256 * 64 + 65536 * 4, 7351, 2000, "E-72: HOE 2.7 at 2,000 then falls; no D-050 jump"),
    "null_v1_h68": (68 + 65536 * 1, 7150, 2000, "no replicators (E-71; HOE <= 0.6 for 16,000 rounds)"),
    "null_v0_h0": (0, 7, 2000, "standard BFF before any transition"),
    "null_v4_h124_g58": (58 + 256 * 124 + 65536 * 4, 7250, 600, "E-72 deep rule, early (no jump before 1,200)"),
}


def job(name):
    code, seed, rounds, status = SOUPS[name]
    C.H1 = code
    s = C.CounterfactualSoup(n=2 ** 14, seed=seed)
    while s.epochs < rounds:
        s.epoch()
    X = np.array(C.distinct_top(s.programs))
    np.save(OUT / f"e73-{name}.npy", X)
    return name, len(X)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    with Pool(7) as p:
        for r in p.imap_unordered(job, list(SOUPS)):
            print(r, flush=True)
