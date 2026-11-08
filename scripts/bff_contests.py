"""E-44: contests between unrelated emergent BFF replicators (docs/data/e44-preregistration.md).

    python scripts/bff_contests.py --workers 11 --out docs/data/experiments/2026-11-08-e44-bff-contests.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from multiprocessing import Pool

import numpy as np

from emergence.observatory import program_selection as PS
from emergence.programs import bff as B

E42 = "docs/data/experiments/2026-11-08-e42-bff-heredity.json"
E43 = "docs/data/experiments/2026-11-08-e43-bff-selection.json"


def pairs() -> list[dict]:
    reps = json.load(open(E42))["results"]
    progs = [r["program"] for r in reps]
    meta = [{"soup": r["soup"], "epoch": r["epoch"]} for r in reps]
    H = bytes(B.REPLICATOR).hex()
    out = [{"kind": "emergent", "i": i, "j": j, "a": progs[i], "b": progs[j], "a_meta": meta[i], "b_meta": meta[j]}
           for i, j in combinations(range(len(progs)), 2)]
    out += [{"kind": "handwritten", "i": -1, "j": j, "a": H, "b": progs[j], "b_meta": meta[j]} for j in range(len(progs))]
    rng = np.random.default_rng(4401)
    for t in range(12):
        out.append({"kind": "null_designed", "i": -1, "j": -2 - t, "a": H,
                    "b": bytes(PS.retail(B.REPLICATOR, rng)).hex()})
    e43 = [r for r in json.load(open(E43))["results"] if r["kind"] == "emergent" and r["verdict"] == "no difference"]
    for c in range(len(progs)):
        best = min((r for r in e43 if r["candidate"] == c), key=lambda r: abs(r["mean_s"]))
        out.append({"kind": "null_emergent", "i": c, "j": c, "a": progs[c], "pos": best["pos"], "val": best["val"]})
    return out


def job(arg):
    k, batch, p = arg
    rng = np.random.default_rng([44 if batch == "A" else 4400, k])
    a = np.frombuffer(bytes.fromhex(p["a"]), np.uint8).copy()
    if p["kind"] == "null_emergent":
        r = PS.compete_marked(a, PS.mutant(a, p["pos"], p["val"]), p["pos"], rng)
    else:
        r = PS.compete_families(a, np.frombuffer(bytes.fromhex(p["b"]), np.uint8).copy(), rng)
    return {"pair": k, "batch": batch} | p | r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ps = pairs()
    jobs = [(k, b, p) for b in ("A", "B") for k, p in enumerate(ps)]
    with Pool(a.workers) as pool:
        res = []
        for n, r in enumerate(pool.imap_unordered(job, jobs), 1):
            res.append(r)
            if n % 20 == 0:
                print(f"{n}/{len(jobs)}", flush=True)
    res.sort(key=lambda r: (r["batch"], r["pair"]))
    summary = {f"{k}/{b}": dict(Counter(r["verdict"] for r in res if r["kind"] == k and r["batch"] == b))
               for k in ("emergent", "handwritten", "null_designed", "null_emergent") for b in ("A", "B")}
    json.dump({"experiment": "E-44", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E44 DONE", flush=True)


if __name__ == "__main__":
    main()
