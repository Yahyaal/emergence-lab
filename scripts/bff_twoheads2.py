"""E-65 (docs/data/e65-preregistration.md): replication of E-64 with more F rules. Census of 768 new random (g, h)
rules of the two-head-start family (none from E-64's sample); soups in every F rule found (4 each) and in 4 random
C rules; strict D-047 criterion. Secondary: does the number of self-sufficient short copiers predict jump time?

    python scripts/bff_twoheads2.py --part census --workers 10 --out docs/data/experiments/2026-11-09-e65-census.json
    python scripts/bff_twoheads2.py --part soups --workers 10 --out docs/data/experiments/2026-11-09-e65-soups.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import bff_lineage as Lg  # noqa: E402
import bff_twoheads as TH  # noqa: E402

NRULES, MAX_F, NC, SOUPS = 768, 16, 4, 4


def sample() -> list[tuple[int, int]]:
    old = set(TH.sample())
    rng = np.random.default_rng(65)
    seen, out = set(old), []
    while len(out) < NRULES:
        g, h = int(rng.integers(1, 128)), int(rng.integers(0, 128))
        if (g, h) not in seen:
            seen.add((g, h))
            out.append((g, h))
    return out


def census(workers: int) -> dict:
    with Pool(workers) as pool:
        res = pool.map(TH.census_rule, sample(), chunksize=1)
    return {"rules": res, "F": [(r["g"], r["h"]) for r in res if r["class"] == "F"],
            "C": [(r["g"], r["h"]) for r in res if r["class"] == "C"],
            "n_none": sum(r["class"] == "0" for r in res)}


def soups(workers: int, census_path: str) -> dict:
    c = json.load(open(census_path))
    rng = np.random.default_rng(650)
    F = [tuple(x) for x in c["F"]]
    if len(F) > MAX_F:
        F = [F[i] for i in sorted(rng.choice(len(F), MAX_F, replace=False))]
    Cp = [tuple(x) for x in c["C"]]
    Cs = sorted(Cp[i] for i in rng.choice(len(Cp), min(NC, len(Cp)), replace=False))
    if len(F) < 2 or len(Cs) < 2:
        return {"summary": {"primary": "undecided (fewer than 2 rules in a class)", "picked": {"F": F, "C": Cs}}, "results": []}
    rules = [("F", g, h) for g, h in sorted(F)] + [("C", g, h) for g, h in Cs]
    jobs = [(6500 + 10 * r + i, h + 256 * g) for r, (_, g, h) in enumerate(rules) for i in range(SOUPS)]
    Lg.RUN = Path("runs/e65")
    Lg.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(Lg.job, jobs, chunksize=1)
    cls_of = {h + 256 * g: cls for cls, g, h in rules}
    j = {k: sum(r["jumped"] for r in res if cls_of[r["h1"]] == k) for k in ("F", "C")}
    n = {k: sum(cls_of[r["h1"]] == k for r in res) for k in ("F", "C")}
    m, tot = j["F"] + j["C"], n["F"] + n["C"]
    p = sum(comb(m, x) * comb(tot - m, n["F"] - x) for x in range(j["F"], min(m, n["F"]) + 1)) / comb(tot, n["F"])
    per = {}
    ss = {(r["g"], r["h"]): r["self_sufficient"] for r in c["rules"]}
    for cls, g, h in rules:
        T = [r["T"] if r["jumped"] else 16000 for r in res if r["h1"] == h + 256 * g]
        per[f"g{g}h{h}"] = {"class": cls, "self_sufficient": ss[(g, h)], "jumped": sum(t < 16000 for t in T),
                            "T": T, "median_T": float(np.median(T))}
    Fr = [v for v in per.values() if v["class"] == "F"]
    rule_ok = sum(v["jumped"] >= 2 for v in Fr)
    ok = j["F"] >= 0.75 * n["F"] and j["C"] <= 0.25 * n["C"] and p < 0.01 and rule_ok >= 0.75 * len(Fr)
    rho, prho = spearmanr([v["self_sufficient"] for v in Fr], [v["median_T"] for v in Fr]) if len(Fr) >= 3 else (None, None)
    one_sided = None if rho is None or np.isnan(rho) else (prho / 2 if rho < 0 else 1 - prho / 2)
    return {"summary": {"picked": {"F": F, "C": Cs}, "jumped": j, "of": n, "fisher_p": p,
                        "F_rules_with_2_of_4": rule_ok, "F_rules": len(Fr), "primary": "pass" if ok else "fail",
                        "secondary_spearman": {"rho": None if rho is None else float(rho), "p_one_sided": one_sided},
                        "per_rule": per}, "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-09-e65-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-65", "part": a.part} | (census(a.workers) if a.part == "census" else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rules")}, indent=1, default=str))
    print(f"=== E65 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
