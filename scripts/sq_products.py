"""E-75 phase 6 (pre-registered, docs/data/e75-phase6-preregistration.md; D-061): the product census. How often
does one run of a random pair WRITE a replicator?

Phase 5 (J-083) found that rules differ in how often replicators originate in a soup (53 of 54 soups of rarely-
jumping rules had no origin in 4,000 rounds), and that each founder was written in a single pair run. This census
measures that rate outside any soup:
  - NPAIRS random pairs (A, B) of 64-byte programs are each run once (8,192 steps, as in the soups);
  - each half that changed is a *product*; products pass a cheap C pre-filter (subleq.sq_prefilter: some
    non-constant 4-byte block of it survives 2 generations with random partners in >= 1 of 2 lineages);
  - pre-filter hits get the inheritance test (D-055) confirmed with a second RNG (sq_nucleation.Tester), and the
    two inputs are tested too.
R_P = informative replicator products whose inputs are both non-replicators, per 10^8 pairs (null products, whose
inherited block is all zeros, are counted apart).

    PYTHONPATH=. python scripts/sq_products.py --workers 11 --out docs/data/experiments/2026-11-13-e75-products.json
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
sys.path.insert(0, str(Path(__file__).parent))
from emergence.programs import subleq as Q  # noqa: E402
from sq_nucleation import Tester  # noqa: E402

P3 = Path("docs/data/experiments/2026-11-13-e75-phase3.json")
P4 = Path("docs/data/experiments/2026-11-13-e75-phase4.json")
L, NPAIRS, CHUNK, MAXHITS = 64, 3 * 10 ** 8, 10 ** 7, 5000


def census(arg) -> dict:
    """One chunk of CHUNK pairs of one rule (seed = [base, code, chunk])."""
    code, chunk, base = arg
    R = Q.Rule.from_code(code)
    t0 = time.time()
    seed = int(np.random.SeedSequence([base, code, chunk]).generate_state(1, np.uint64)[0])
    n, X, S, st = Q.products(R, CHUNK, seed, maxhits=MAXHITS)
    test = Tester(R)
    out = {"code": code, "chunk": chunk, "pairs": CHUNK, "hits": n, "tested": len(X), **st,
           "informative": 0, "null": 0, "from_replicator": 0, "side": [0, 0], "examples": []}
    for x, s in zip(X, S):
        k = test(x[:L])
        if not k:
            continue
        if test(x[L:2 * L]) or test(x[2 * L:]):
            out["from_replicator"] += 1
            continue
        if k == 1:
            out["null"] += 1
            continue
        out["informative"] += 1
        out["side"][int(s)] += 1
        if len(out["examples"]) < 5:
            out["examples"].append({"product": x[:L].tobytes().hex(), "A": x[L:2 * L].tobytes().hex(),
                                    "B": x[2 * L:].tobytes().hex(), "side": int(s)})
    out["sec"] = round(time.time() - t0, 1)
    return out


def rules() -> list[dict]:
    out = []
    for phase, f in ((3, P3), (4, P4)):
        d = json.load(open(f))
        tiles = d["tiles"] if isinstance(d["tiles"], list) else [t for v in d["tiles"].values() for t in v]
        dt = {t["code"]: t["D_T"] for t in tiles}
        for q in d["summary"]["rules"]:
            out.append({"phase": phase, "pool": q.get("pool", "always"), "group": q["group"], "code": q["code"],
                        "rule": q["rule"], "jumped": q["jumped"], "D_T": dt.get(q["code"])})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--npairs", type=float, default=NPAIRS)
    ap.add_argument("--codes", default="", help="comma-separated rule codes (development runs)")
    ap.add_argument("--seed", type=int, default=80)
    a = ap.parse_args()
    t0 = time.time()
    rs = rules()
    if a.codes:
        rs = [r for r in rs if str(r["code"]) in a.codes.split(",")]
    jobs = [(r["code"], c, a.seed) for r in rs for c in range(int(a.npairs) // CHUNK)]
    with Pool(a.workers) as pool:
        res = []
        for r in pool.imap_unordered(census, jobs, chunksize=1):
            res.append(r)
            print(json.dumps({k: r[k] for k in ("code", "chunk", "hits", "informative", "null", "from_replicator",
                                                "sec")}), flush=True)
    for r in rs:
        ch = [x for x in res if x["code"] == r["code"]]
        tot = {k: sum(x[k] for x in ch) for k in ("pairs", "hits", "tested", "products", "steps", "maxed",
                                                    "informative", "null", "from_replicator")}
        frac = tot["tested"] / tot["hits"] if tot["hits"] else 1.0  # hits beyond MAXHITS were not tested
        r.update(tot, side=[sum(x["side"][i] for x in ch) for i in (0, 1)],
                 R_P=tot["informative"] / frac * 1e8 / tot["pairs"], R_null=tot["null"] / frac * 1e8 / tot["pairs"],
                 examples=[e for x in ch for e in x["examples"]][:5])
    json.dump({"experiment": "E-75", "phase": 6, "npairs": int(a.npairs), "seed": a.seed, "prefilter": Q.PRE, "rules": rs, "chunks": res,
               "seconds": round(time.time() - t0)}, open(a.out, "w"), indent=1)
    print("=== SENTINEL e75 products DONE", flush=True)


if __name__ == "__main__":
    main()
