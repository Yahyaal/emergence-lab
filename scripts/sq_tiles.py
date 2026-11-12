"""E-75 phase 3a (D-057, development): tile census of the 600 phase-1 rules.

A *tile* program is one instruction's worth of random bytes (period = the rule's operand count n) repeated to 64
bytes. Per rule, 10^6 random tiles are run once with a random partner (512 steps); hits (an 8-byte block passed)
are verified with the inheritance test (D-055, up to 2,000). T-F = at least one tile replicator. Also records the
fraction of runs that halt within 2 steps. Motivated by E-75 phase 2 (J-079), where fast take-overs were tiles.

    PYTHONPATH=. python scripts/sq_tiles.py --workers 11 --out docs/data/experiments/2026-11-13-e75-tiles-dev.json
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

CENSUS = Path("docs/data/experiments/2026-11-12-e75-census.json")
NTILE, MAXHITS = 1_000_000, 2000


def tile_rule(arg) -> dict:
    code, seed, ntile = arg
    R = Q.Rule.from_code(code)
    t0 = time.time()
    n, hits, halt = Q.census_period(R, ntile, seed, R.n, maxhits=MAXHITS)
    rng = np.random.default_rng([57, code, seed])
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    reps = [h for h in hits if I.inherits(h, run, rng)[0]]
    return {"code": code, "rule": str(R), "seed": seed, "ntile": ntile, "tile_hits": n, "tile_verified": len(hits),
            "tile_replicators": len(reps), "tile_class": "TF" if reps else "TC" if n else "Tnone",
            "halt2": halt / ntile, "examples": [r[:R.n].tobytes().hex() for r in reps[:3]],
            "sec": round(time.time() - t0, 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    rules = json.load(open(CENSUS))["rules"]
    with Pool(a.workers) as pool:
        res = pool.map(tile_rule, [(r["code"], 1, NTILE) for r in rules], chunksize=1)
    tab = {}
    for r, t in zip(rules, res):
        r.update({k: t[k] for k in ("tile_hits", "tile_verified", "tile_replicators", "tile_class", "halt2")})
        key = f'{r["class"]}/{t["tile_class"]}'
        tab[key] = tab.get(key, 0) + 1
    out = {"experiment": "E-75", "phase": "3a-dev", "ntile": NTILE, "crosstab": tab, "rules": rules,
           "tiles": res, "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(tab, indent=1))
    print("=== SENTINEL e75 tiles DONE", flush=True)


if __name__ == "__main__":
    main()
