"""E-43: do emergent BFF replicator variants differ in how well they spread? (docs/data/e43-preregistration.md)

Competition assay (observatory/program_selection.py, D-042) on every viable E-42 mutant against
its parent, plus 24 neutral pairs of the hand-written replicator as a null.

    python scripts/bff_selection.py --workers 11 --out docs/data/experiments/2026-11-08-e43-bff-selection.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from multiprocessing import Pool

import numpy as np

from emergence.observatory import program_selection as PS
from emergence.programs import bff as B

E42 = "docs/data/experiments/2026-11-08-e42-bff-heredity.json"


def pairs() -> list[dict]:
    out = []
    for c, r in enumerate(json.load(open(E42))["results"]):
        for m in r["mutants"]:
            if m["viable"]:
                out.append({"kind": "emergent", "parent": r["program"], "candidate": c, "pos": m["pos"], "val": m["val"]})
    rng = np.random.default_rng(4300)
    for _ in range(24):
        out.append({"kind": "neutral", "parent": bytes(B.REPLICATOR).hex(), "candidate": -1,
                    "pos": int(rng.integers(27, 64)), "val": int(rng.integers(1, 256))})
    return [p for p in out if p["kind"] == "emergent" or p["val"] != 0x80]


def job(arg):
    i, p = arg
    x = np.frombuffer(bytes.fromhex(p["parent"]), np.uint8).copy()
    r = PS.compete(x, PS.mutant(x, p["pos"], p["val"]), p["pos"], np.random.default_rng([43, i]))
    return p | r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ps = pairs()
    with Pool(a.workers) as pool:
        res = pool.map(job, list(enumerate(ps)), chunksize=2)
    summary = {k: dict(Counter(r["verdict"] for r in res if r["kind"] == k)) for k in ("emergent", "neutral")}
    json.dump({"experiment": "E-43", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary))
    print("=== E43 DONE", flush=True)


if __name__ == "__main__":
    main()
