"""E-32: does any random multi-channel Lenia rule turn a lone lump into a reproducer?

E-29 (J-034) found no reproducer among 3000 random single-channel Lenia rules. Chan (2020)
reported self-replicating creatures only once Lenia had several channels and kernels. This scan
repeats E-29 unchanged on `MultiLenia.random` (2 or 3 channels, 1 self-kernel per channel plus
1 to 2C cross kernels): each rule, each lump radius, a lump whose channels are independent smooth
noise in the same disk, alone in a 128x128 vacuum, settled 300 steps (or the last checkpoint
before the world filled), then the birth detector (D-028 + D-030) on the 2 most common object
types. Pre-registered in docs/data/e32-preregistration.md.

Pipeline positive: Gray-Scott lumps (lump_scan.gs_job).

Usage: python scripts/mlenia_lump_scan.py --rules 1000 --out docs/data/experiments/2026-11-08-e32-mlenia-lumps.json --workers 11
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

from emergence.physics import MultiLenia

import lump_scan as L


def mlump(ph: MultiLenia, rng: np.random.Generator, r: int) -> np.ndarray:
    return np.stack([L.lump(rng, r) for _ in range(ph.C)]).astype(np.float32) / 255.0


def job(args):
    i, seed = args
    t0 = time.time()
    rng = np.random.default_rng([seed, i])
    ph = MultiLenia.random(rng)
    out = {"i": i, "rule": ph.label(), "channels": ph.C, "kernels": len(ph.kernels), "lumps": []}
    for r in L.RADII:
        out["lumps"].append({"radius": r} | L.outcome(ph, mlump(ph, rng, r), rng))
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=32)
    ap.add_argument("--gs", type=int, default=4)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    with Pool(a.workers or None) as p:
        gs = p.map(L.gs_job, range(a.gs), chunksize=1)
        print("Gray-Scott pipeline positive:", sum(any(l.get("reproducers") for l in g["lumps"]) for g in gs),
              "/", a.gs, flush=True)
        res = []
        for k, r in enumerate(p.imap_unordered(job, [(i, a.seed) for i in range(a.rules)], chunksize=2)):
            res.append(r)
            if (k + 1) % 50 == 0:
                print(k + 1, "rules,", round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: r["i"])
    settled = Counter(l["settled"] for r in res for l in r["lumps"])
    verdicts = Counter(v for r in res for l in r["lumps"] for v in l["verdicts"])
    repro = sorted({r["rule"] for r in res for l in r["lumps"] if l.get("reproducers")})
    decided = sum(any("no reproduction" in l["verdicts"] or l.get("reproducers") for l in r["lumps"]) for r in res)
    print("settled:", dict(settled))
    print("verdicts:", dict(verdicts))
    print("rules decided:", decided, "/", len(res))
    print("rules with a reproducer:", len(repro), repro)
    json.dump({"experiment": "E-32", "seed": a.seed, "rules": a.rules, "radii": L.RADII, "side": L.SIDE,
               "settle": L.SETTLE, "gray_scott_positive": gs, "mlenia": res,
               "summary": {"settled": dict(settled), "verdicts": dict(verdicts), "decided_rules": decided,
                           "reproducer_rules": repro},
               "seconds": round(time.time() - t0)}, open(a.out, "w"), indent=1)
    print("E32 DONE", flush=True)


if __name__ == "__main__":
    main()
