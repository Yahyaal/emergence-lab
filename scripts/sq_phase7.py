"""E-75 phase 7 (pre-registered, docs/data/e75-phase7-preregistration.md; D-062): a prospective test of the product
census. New rules are chosen by their product rate R_P (J-084) before any soup is run; then 6 soups each.

Pools: n4 / s = +1 or -1 / W in {64, 32, 16, 8} / o 0..127, per jump rule (always, <= 0, < 0), minus the 600 phase-1
census rules and the 60 rules of phases 3-4. Candidates are taken in a seed-82 random order per jump rule, in batches
of 11, at most CAP per jump rule.
  Stage 1  10^8 random pairs (sq_products.census, seed base 82). HIGH candidate: >= 1 informative product
           (>= 5 under always); ZERO candidate: none.
  Stage 2  2 x 10^8 more pairs (seed base 83). Over all 3 x 10^8: HIGH needs >= 15 products under always (R_P >= 5)
           or >= 2 under <= 0 / < 0 (R_P >= 0.67); ZERO needs 0. As in phases 3-4 (D-056), no replicator may be
           found among random programs (census at 10^7 and 10^8).
  Wanted   4 HIGH + 4 ZERO per jump rule, in candidate order.
  Soups    6 per rule, exactly as phases 3-4 (sq_phase3.soup_job), seeds 82000 + 10 k + i, cache runs/e75-phase7.

    PYTHONPATH=. python scripts/sq_phase7.py --workers 11 --out docs/data/experiments/2026-11-14-e75-phase7.json
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
from emergence.programs import inherit as I  # noqa: E402
from emergence.programs import subleq as Q  # noqa: E402
import sq_phase3 as P3  # noqa: E402
import sq_products as PC  # noqa: E402

RUN = Path("runs/e75-phase7")
JUMPS = {"always": 3, "<=0": 0, "<0": 1}
WANT, CAP, SOUPS, BATCH = 4, 44, 6, 11
S1, S2 = 10, 20  # chunks of 10^7 pairs in stage 1 and stage 2
HIGH_MIN = {"always": 15, "<=0": 2, "<0": 2}  # products in 3 x 10^8 pairs
S1_MIN = {"always": 5, "<=0": 1, "<0": 1}     # products in the first 10^8


def used() -> set[int]:
    u = {r["code"] for r in json.load(open(P3.CENSUS))["rules"]}
    for f in (PC.P3, PC.P4):
        u |= {q["code"] for q in json.load(open(f))["summary"]["rules"]}
    return u


def pool_rules(j: int, u: set[int]) -> list[int]:
    return [c for s in (1, -1) for W in (64, 32, 16, 8) for o in range(128)
            if (c := Q.Rule(n=4, j=j, s=s, W=W, o=o).code) not in u]


def tile_dt() -> dict[int, float]:
    out = {}
    for f in (PC.P3, PC.P4):
        d = json.load(open(f))
        ts = d["tiles"] if isinstance(d["tiles"], list) else [t for v in d["tiles"].values() for t in v]
        out.update({t["code"]: t["D_T"] for t in ts})
    return out


def random_replicators(code: int) -> dict:
    """D-056 screen, as phases 3-4: inheritance test on random-program census hits at 10^7 and 10^8."""
    R = Q.Rule.from_code(code)
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    rng = np.random.default_rng([82, code])
    n7, h7 = Q.census_hits(R, 10 ** 7, 1, maxhits=2000)
    r7 = int(sum(I.inherits(h, run, rng)[0] for h in h7))
    if r7:
        return {"code": code, "hits7": n7, "reps7": r7, "pass": False}
    n8, h8 = Q.census_hits(R, 10 ** 8, 3, maxhits=5000)
    r8 = int(sum(I.inherits(h, run, rng)[0] for h in h8))
    return {"code": code, "hits7": n7, "reps7": r7, "hits8": n8, "verified8": len(h8), "reps8": r8, "pass": r8 == 0}


def job(arg):
    kind, x = arg
    if kind == "chunk":
        return PC.census(x)
    if kind == "screen":
        return random_replicators(x)
    P3.RUN = RUN
    return P3.soup_job(x)


def tally(chunks: list[dict]) -> dict:
    return {k: sum(c[k] for c in chunks) for k in ("pairs", "hits", "tested", "informative", "null",
                                                   "from_replicator")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--want", type=int, default=WANT)
    ap.add_argument("--no-soups", action="store_true", help="selection only (development)")
    a = ap.parse_args()
    t0 = time.time()
    u, dt = used(), tile_dt()
    log, sel = [], []
    with Pool(a.workers) as pool:
        for jn, j in JUMPS.items():
            v = pool_rules(j, u)
            rng = np.random.default_rng([82, j])
            order = [v[i] for i in rng.permutation(len(v))]
            got = {"HIGH": [], "ZERO": []}
            k = 0
            while k < min(a.cap, len(order)) and (len(got["HIGH"]) < a.want or len(got["ZERO"]) < a.want):
                batch = order[k:k + BATCH]
                k += len(batch)
                res = pool.map(job, [("chunk", (c, ch, 82)) for c in batch for ch in range(S1)], chunksize=1)
                s1 = {c: tally([r for r in res if r["code"] == c]) for c in batch}
                cand = []
                for c in batch:
                    n = s1[c]["informative"]
                    g = "HIGH" if n >= S1_MIN[jn] else "ZERO" if n == 0 else None
                    log.append({"jump": jn, "code": c, "rule": str(Q.Rule.from_code(c)), "D_T": dt.get(c),
                                "stage1": s1[c], "candidate": g})
                    if g:
                        cand.append((c, g))
                # stage 2 and the random-program screen, only for candidates that could still be used
                need = {g: a.want - len(got[g]) for g in got}
                todo = []
                for c, g in cand:
                    if need[g] > 0:
                        todo.append((c, g))
                        need[g] -= 1
                if not todo:
                    continue
                jobs = [("chunk", (c, ch, 83)) for c, _ in todo for ch in range(S2)] + [("screen", c) for c, _ in todo]
                res = pool.map(job, jobs, chunksize=1)
                chunks = [r for r in res if "chunk" in r]
                scr = {r["code"]: r for r in res if "chunk" not in r}
                for c, g in todo:
                    tot = tally([r for r in chunks if r["code"] == c])
                    n = s1[c]["informative"] + tot["informative"]
                    ok = (n >= HIGH_MIN[jn]) if g == "HIGH" else (n == 0)
                    ok = ok and scr[c]["pass"]
                    e = next(x for x in log if x["code"] == c)
                    e.update(stage2=tot, products=n, R_P=n / 3, screen=scr[c], selected=ok and len(got[g]) < a.want)
                    if e["selected"]:
                        got[g].append(c)
                        sel.append({"jump": jn, "group": g, "code": c, "rule": str(Q.Rule.from_code(c)),
                                    "R_P": n / 3, "D_T": dt.get(c)})
                print(json.dumps({"jump": jn, "screened": k, "HIGH": len(got["HIGH"]), "ZERO": len(got["ZERO"])}),
                      flush=True)
        soups = []
        if not a.no_soups:
            jobs = [("soup", (82000 + 10 * k + i, q["code"])) for k, q in enumerate(sel) for i in range(SOUPS)]
            soups = pool.map(job, jobs, chunksize=1)
    by = {s["seed"]: s for s in soups}
    for k, q in enumerate(sel):
        S = [by[82000 + 10 * k + i] for i in range(SOUPS) if 82000 + 10 * k + i in by]
        q.update(T=[s["T"] for s in S], jumped=sum(s["T"] is not None for s in S))
    out = {"experiment": "E-75", "phase": 7, "selected": sel, "screened": log, "soups": soups,
           "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(sel))
    print("=== SENTINEL e75 phase7 DONE", flush=True)


if __name__ == "__main__":
    main()
