"""E-70 (docs/data/e70-preregistration.md): the instruction-set family. Five one-instruction changes to BFF
(scripts/bff_kernels.c run(), code = h1 + 65536 * v), each crossed with every head1 start h1 in 0..127
(64-byte programs, head0 at 0). Does the 'copy that copies' predictor (F rules, E-61-E-68) carry over when the
language itself changes?

  v1 '.' then both heads +1     v2 '.' then both heads -1     v3 ',' then both heads +1
  v4 '[' ']' test head1's byte  v5 '+' '-' act on head1's byte          (v0 = standard BFF)

Part A: E-61 census (bff_shift_census.census_rule, unchanged) for every (v, h1); v = 0 replays E-61 (equivalence).
Part B: soups of 2^14 programs in F and non-F rules, copier-only jump criterion D-050 (as E-68).

    python scripts/bff_instrset.py --part census --workers 11 --out docs/data/experiments/2026-11-09-e70-census.json
    python scripts/bff_instrset.py --part soups --workers 11 --out docs/data/experiments/2026-11-09-e70-soups.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import bff_shift_census as S  # noqa: E402
import bff_tapelength as T  # noqa: E402

VARIANTS = {1: "'.' then both heads +1", 2: "'.' then both heads -1", 3: "',' then both heads +1",
            4: "'[' ']' test head1's byte", 5: "'+' '-' act on head1's byte"}
E61 = "docs/data/experiments/2026-11-08-e61-census.json"
SOUPS, NF, NS = 4, 3, 3


def code(v: int, h1: int) -> int:
    return h1 + 65536 * v


def census_job(arg) -> dict:
    v, h = arg
    return {"v": v} | S.census_rule(code(v, h)) | {"h": h}


def census(workers: int) -> dict:
    jobs = [(v, h) for v in range(6) for h in range(128)]
    with Pool(workers) as pool:
        res = sorted(pool.map(census_job, jobs, chunksize=1), key=lambda r: (r["v"], r["h"]))
    old = {r["h"]: r for r in json.load(open(E61))["rules"]}
    eq = all((r["copiers"], r["self_sufficient"], r["class"]) == (old[r["h"]]["copiers"], old[r["h"]]["self_sufficient"],
                                                                  old[r["h"]]["class"]) for r in res if r["v"] == 0)
    per = {}
    for v in range(6):
        rs = [r for r in res if r["v"] == v]
        F = [r["h"] for r in rs if r["class"] == "F"]
        per[v] = {"F": F, "S": [r["h"] for r in rs if r["class"] == "S" and r["copiers"] > 0],
                  "none": [r["h"] for r in rs if r["copiers"] == 0], "h64_is_F": 64 in F,
                  "F_in_48_80": all(48 <= h <= 80 for h in F),
                  "self_sufficient_at_64": next(r["self_sufficient"] for r in rs if r["h"] == 64),
                  "self_sufficient_orientation": sorted({o for r in rs if r["class"] == "F"
                                                         for o in r["self_sufficient_orientation"]})}
    p1 = all(per[v]["h64_is_F"] and per[v]["F_in_48_80"] for v in VARIANTS)
    return {"variants": VARIANTS, "rules": res, "per_v": per, "equivalence_v0_vs_E61": eq,
            "primary1": "pass" if p1 else "fail"}


def pick(census_path: str) -> list[tuple[str, int, int]]:
    c = json.load(open(census_path))
    rng = np.random.default_rng(700)
    rules = []
    for v in VARIANTS:
        p = c["per_v"][str(v)]
        F = list(p["F"])
        f = [64] if 64 in F else []
        rest = [h for h in F if h != 64]
        f += sorted(int(x) for x in rng.choice(rest, min(NF - len(f), len(rest)), replace=False)) if rest else []
        s = list(p["S"])
        sel = sorted(int(x) for x in rng.choice(s, min(NS, len(s)), replace=False)) if s else []
        if len(sel) < NS and p["none"]:
            sel += sorted(int(x) for x in rng.choice(p["none"], min(NS - len(sel), len(p["none"])), replace=False))
        rules += [("F", v, h) for h in f] + [("N", v, h) for h in sel]
    return rules


def soups(workers: int, census_path: str) -> dict:
    rules = pick(census_path)
    jobs = [(7000 + 10 * r + i, 64, code(v, h)) for r, (_, v, h) in enumerate(rules) for i in range(SOUPS)]
    T.RUN = Path("runs/e70")
    T.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(T.soup_job, jobs, chunksize=1)
    for r in res:
        r["v"], r["h"] = r["h1"] >> 16, r["h1"] & 255
    cls = {(v, h): k for k, v, h in rules}
    c = json.load(open(census_path))
    nss = {(r["v"], r["h"]): r["self_sufficient"] for r in c["rules"]}
    j = {k: sum(r["jumped"] for r in res if cls[(r["v"], r["h"])] == k) for k in ("F", "N")}
    n = {k: sum(cls[(r["v"], r["h"])] == k for r in res) for k in ("F", "N")}
    p = T.fisher(j["F"], n["F"], j["N"], n["N"])
    by_v = {}
    for v in VARIANTS:
        rv = [r for r in res if r["v"] == v]
        by_v[v] = {k: [sum(r["jumped"] for r in rv if cls[(v, r["h"])] == k), sum(cls[(v, r["h"])] == k for r in rv)]
                   for k in ("F", "N")}
        by_v[v]["per_rule"] = {h: {"class": cls[(v, h)], "self_sufficient": nss[(v, h)],
                                   "T": [r["T"] for r in rv if r["h"] == h]} for h in sorted({r["h"] for r in rv})}
    each = all(by_v[v]["F"][0] >= by_v[v]["N"][0] for v in VARIANTS)
    ok = j["F"] >= 0.75 * n["F"] and j["N"] <= 0.25 * n["N"] and p < 0.01 and each
    Fr = [(v, h) for k, v, h in rules if k == "F"]
    med = [float(np.median([r["T"] if r["jumped"] else T.WAIT for r in res if (r["v"], r["h"]) == q])) for q in Fr]
    rho, prho = spearmanr([nss[q] for q in Fr], med) if len(Fr) > 2 else (float("nan"), float("nan"))
    return {"rules": [list(r) for r in rules],
            "summary": {"jumped": j, "of": n, "fisher_p": p, "F_ge_N_each_v": each, "primary2": "pass" if ok else "fail",
                        "by_v": by_v, "secondary_selfsufficient_vs_medianT": {"rho": float(rho), "p_two_sided": float(prho),
                                                                             "rules": [list(q) for q in Fr], "median_T": med}},
            "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-09-e70-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-70", "part": a.part} | (census(a.workers) if a.part == "census" else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rules")}, indent=1, default=str))
    print(f"=== SENTINEL e70 {a.part} DONE", flush=True)


if __name__ == "__main__":
    main()
