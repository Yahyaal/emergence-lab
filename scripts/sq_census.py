"""E-75 phase 1 (docs/data/e75-phase1-protocol.md): census of sampled SUBLEQ-family rules.

Per rule: 10^7 random 64-byte programs, each run once with a random partner (512 steps); a *hit* passes an
8-byte block of itself to the partner (`subleq.census_hits`). Up to 2,000 hits are verified with the
inheritance test (D-055, 8,192 steps). Classes:
  F        at least one verified hit is an inheritance replicator
  C        hits (one-generation copying) but no replicator among the verified ones  (the 'non-F' of phase 3)
  none     no hits
Rules: 600 drawn uniformly from the 16,416 (seed 75), plus the anchors SUBLEQ and RSUBLEQ4. The first 40
rules are censused again with another seed (stability check).

    PYTHONPATH=. python scripts/sq_census.py --workers 11 --out docs/data/experiments/2026-11-12-e75-census.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))
from emergence.programs import inherit as I  # noqa: E402
from emergence.programs import subleq as Q  # noqa: E402

NPROG, MAXHITS, NRULES, NSTAB = 10_000_000, 2000, 600, 40


def all_rules() -> list[Q.Rule]:
    out = []
    for n in (3, 4):
        for j in range(4):
            for s in Q.S_VALUES:
                out.append(Q.Rule(n=n, j=j, s=s, W=128, o=0))
                for W in Q.W_VALUES[1:]:
                    for o in range(128):
                        out.append(Q.Rule(n=n, j=j, s=s, W=W, o=o))
    return out


def sample() -> list[Q.Rule]:
    rules = all_rules()
    idx = np.random.default_rng(75).permutation(len(rules))[:NRULES]
    return [rules[i] for i in idx]


def census_rule(arg) -> dict:
    code, seed = arg
    R = Q.Rule.from_code(code)
    t0 = time.time()
    n, hits = Q.census_hits(R, NPROG, seed, maxhits=MAXHITS)
    rng = np.random.default_rng([75, code, seed])
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    reps = [h for h in hits if I.inherits(h, run, rng)[0]]
    cls = "F" if reps else "C" if n else "none"
    return {"code": code, "rule": str(R), "n": R.n, "j": R.j, "s": R.s, "W": R.W, "o": R.o, "absolute": R.absolute,
            "seed": seed, "hits": n, "verified": len(hits), "replicators": len(reps),
            "density_per_1e7": (len(reps) / len(hits) * n) * 1e7 / NPROG if len(hits) else 0.0,
            "class": cls, "examples": [r.tobytes().hex() for r in reps[:3]], "sec": round(time.time() - t0, 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    rules = sample()
    jobs = [(R.code, 1) for R in rules] + [(Q.SUBLEQ.code, 1), (Q.RSUBLEQ4.code, 1)]
    jobs += [(R.code, 2) for R in rules[:NSTAB]]
    with Pool(a.workers) as pool:
        res = pool.map(census_rule, jobs, chunksize=1)
    main_ = res[:len(rules)]
    anchors = {"SUBLEQ": res[len(rules)], "RSUBLEQ4": res[len(rules) + 1]}
    stab = res[len(rules) + 2:]
    agree = sum(x["class"] == y["class"] for x, y in zip(main_[:NSTAB], stab))
    by = lambda key: {str(k): {c: sum(1 for r in main_ if r[key] == k and r["class"] == c) for c in ("F", "C", "none")}  # noqa: E731
                      for k in sorted({r[key] for r in main_})}
    summary = {"rules": len(main_), "classes": {c: sum(r["class"] == c for r in main_) for c in ("F", "C", "none")},
               "anchors": {k: v["class"] for k, v in anchors.items()},
               "stability": {"agree": agree, "of": NSTAB, "pass": agree >= 0.95 * NSTAB},
               "by_n": by("n"), "by_j": by("j"), "by_s": by("s"), "by_W": by("W")}
    summary["gate"] = summary["classes"]["F"] >= 16 and summary["classes"]["C"] >= 16
    out = {"experiment": "E-75", "phase": 1, "nprog": NPROG, "maxhits": MAXHITS, "summary": summary,
           "anchors": anchors, "rules": main_, "stability_rerun": stab, "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== SENTINEL e75 census DONE", flush=True)


if __name__ == "__main__":
    main()
