"""E-69 (docs/data/e69-preregistration.md): is E-68's length effect a soup-size effect? The E-68 rules at L = 16 and
L = 32 (3 F + 3 other each), 4 soups each, with the number of programs raised so every soup holds 2^21 bytes, as
the L = 128 soups of E-68 did (L = 16: 2^17 programs; L = 32: 2^16). Same D-050 job as E-68.

    python scripts/bff_tapelength_bytes.py --workers 11 --out docs/data/experiments/2026-11-09-e69-bytes.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bff_tapelength as T  # noqa: E402

BYTES = 2 ** 21
E68 = "docs/data/experiments/2026-11-09-e68-soups.json"


def job(arg) -> dict:
    seed, L, h1 = arg
    T.N = BYTES // L
    T.RUN = Path("runs/e69")
    return T.soup_job((seed, L, h1)) | {"n_programs": T.N}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    rules = [r for r in json.load(open(E68))["rules"] if r[1] in (16, 32)]
    jobs = [(6900 + 10 * r + i, L, h) for r, (_, L, h) in enumerate(rules) for i in range(4)]
    Path("runs/e69").mkdir(parents=True, exist_ok=True)
    with Pool(a.workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    cls = {(L, h): k for k, L, h in rules}
    by = {L: {k: [sum(r["jumped"] for r in res if r["L"] == L and cls[(L, r["h1"])] == k),
                  sum(r["L"] == L and cls[(L, r["h1"])] == k for r in res)] for k in ("F", "N")} for L in (16, 32)}
    f16, f32 = by[16]["F"][0] / by[16]["F"][1], by[32]["F"][0] / by[32]["F"][1]
    verdict = ("soup size explains" if f16 >= 0.5 and f32 >= 0.75 else
               "length itself matters" if f16 <= 0.25 else "undecided")
    out = {"experiment": "E-69", "rules": rules, "summary": {"by_L": by, "primary": verdict,
           "T": {f"L{L}h{h}": [r["T"] for r in res if r["L"] == L and r["h1"] == h] for _, L, h in rules}},
           "results": res, "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["summary"], indent=1))
    print("=== SENTINEL e69 DONE", flush=True)


if __name__ == "__main__":
    main()
