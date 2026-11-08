"""E-45: the mirror replicator species vs other emergent replicators (docs/data/e45-preregistration.md).

    python scripts/bff_mirror_contests.py --workers 11 --out docs/data/experiments/2026-11-08-e45-mirror-contests.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np
from scipy.stats import binomtest

from emergence.observatory import program_selection as PS
from emergence.programs import bff as B

E42 = "docs/data/experiments/2026-11-08-e42-bff-heredity.json"
REPS = 64


def pairs() -> list[dict]:
    P = [r["program"] for r in json.load(open(E42))["results"]]
    rev = lambda h: bytes(bytes.fromhex(h)[::-1]).hex()
    assert rev(P[5]) == P[6]
    H = bytes(B.REPLICATOR).hex()
    out = [{"kind": "primary", "a": P[5], "a_alt": [P[6]], "b": P[j], "b_alt": [], "j": j} for j in (0, 1, 2, 3)]
    out += [{"kind": "secondary", "a": P[5], "a_alt": [P[6]], "b": P[j], "b_alt": [], "j": j} for j in (4, 7, 8)]
    out += [{"kind": "secondary", "a": P[5], "a_alt": [P[6]], "b": H, "b_alt": [], "j": -1}]
    rng = np.random.default_rng(4501)
    for t in range(4):
        y = bytes(PS.retail(B.REPLICATOR, rng)).hex()
        out.append({"kind": "null", "a": H, "a_alt": [], "b": y, "b_alt": [rev(y)], "j": -2 - t})
    return out


def job(arg):
    k, p = arg
    h = lambda x: np.frombuffer(bytes.fromhex(x), np.uint8).copy()
    r = PS.compete_families(h(p["a"]), h(p["b"]), np.random.default_rng([45, k]), reps=REPS,
                            a_alt=[h(x) for x in p["a_alt"]], b_alt=[h(x) for x in p["b_alt"]])
    return {"pair": k} | p | r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with Pool(a.workers) as pool:
        res = pool.map(job, list(enumerate(pairs())), chunksize=1)
    summary = {}
    for kind in ("primary", "secondary", "null"):
        s = [v for r in res if r["kind"] == kind for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
        w = sum(v < 0 for v in s)
        summary[kind] = {"verdicts": [r["verdict"] for r in res if r["kind"] == kind], "a_wins": w, "n": len(s),
                         "share": round(w / max(len(s), 1), 3),
                         "p_greater": float(binomtest(w, len(s), alternative="greater").pvalue) if s else 1.0}
    json.dump({"experiment": "E-45", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E45 DONE", flush=True)


if __name__ == "__main__":
    main()
