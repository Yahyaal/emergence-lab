"""E-56 comparison arm (docs/data/e56-preregistration.md): copier orientation of E-54's jumped standard-rule soups
at T + 2,000, classified with the standard interpreter (head1 = 0), same method as the counterfactual arm.

    python scripts/e56_comparison.py --out docs/data/experiments/2026-11-08-e56-comparison.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402

SOUPS = {5301: 21750, 5302: 13750, 5308: 12500, 5401: 10250, 5402: 22250, 5406: 16750, 5410: 750}
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()
res = {}
for s, T in SOUPS.items():
    P = np.load(f"runs/e54/{s}-{T + 2000}.npy")
    o = C.orient(P, 0, 5600 + s)
    res[s] = {"T": T, **{k: v for k, v in o.items() if k != "copiers"}}
    print(s, res[s], flush=True)
tot = {k: sum(r[k] for r in res.values()) for k in ("forward", "reverse", "both", "none")}
json.dump({"experiment": "E-56 comparison", "soups": res, "total": tot}, open(a.out, "w"), indent=1)
print(tot)
