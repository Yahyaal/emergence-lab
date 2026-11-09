"""E-63 (docs/data/e63-preregistration.md): soups in rules just outside F' (forward short copiers whose single
copy cannot copy), strict D-047 criterion, with a concurrent positive control (h = 64).

    python scripts/bff_outside.py --workers 10 --out docs/data/experiments/2026-11-09-e63-outside.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_lineage as Lg  # noqa: E402

POOL = [59, 60] + list(range(69, 83))
F_PRIOR = (28, 28)  # E-62 F' soups under D-047: jumped, of


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    pick = sorted(int(x) for x in np.random.default_rng(63).choice(POOL, 4, replace=False))
    jobs = [(6300 + 10 * r + i, h) for r, h in enumerate(pick) for i in range(4)] + [(6390 + i, 64) for i in range(4)]
    Lg.RUN = Path("runs/e63")
    Lg.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(a.workers) as pool:
        res = pool.map(Lg.job, jobs, chunksize=1)
    out_ = [r for r in res if r["h1"] != 64]
    j, n = sum(r["jumped"] for r in out_), len(out_)
    fj, fn = F_PRIOR
    m, tot = j + fj, n + fn
    p = sum(comb(m, x) * comb(tot - m, fn - x) for x in range(fj, min(m, fn) + 1)) / comb(tot, fn)
    ctl = sum(r["jumped"] for r in res if r["h1"] == 64)
    summary = {"picked": pick, "jumped": j, "of": n, "fisher_p_vs_e62": p, "control_h64": f"{ctl}/4",
               "primary": "pass" if j <= 4 and p < 0.01 else "fail",
               "per_rule": {h: {"jumped": sum(r["jumped"] for r in res if r["h1"] == h),
                                "T": [r["T"] for r in res if r["h1"] == h],
                                "dropped": sum(len(r["dropped"]) for r in res if r["h1"] == h)} for h in pick + [64]}}
    json.dump({"experiment": "E-63", "summary": summary, "results": res, "seconds": round(time.time() - t0)},
              open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E63 DONE", flush=True)


if __name__ == "__main__":
    main()
