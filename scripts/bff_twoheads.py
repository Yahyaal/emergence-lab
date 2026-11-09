"""E-64 (docs/data/e64-preregistration.md): does the 'copy that copies' predictor (F', E-61-E-63) carry over to a
new family of rule variants, where head0 starts at byte g and head1 at byte h (code = h + 256 g)?

    python scripts/bff_twoheads.py --part census --workers 10 --out docs/data/experiments/2026-11-09-e64-census.json
    python scripts/bff_twoheads.py --part soups --workers 10 --out docs/data/experiments/2026-11-09-e64-soups.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_kernels as K  # noqa: E402
import bff_lineage as Lg  # noqa: E402
import bff_shift_census as S  # noqa: E402

NRULES = 256


def sample() -> list[tuple[int, int]]:
    rng = np.random.default_rng(64)
    seen, out = set(), []
    while len(out) < NRULES:
        g, h = int(rng.integers(1, 128)), int(rng.integers(0, 128))
        if (g, h) not in seen:
            seen.add((g, h))
            out.append((g, h))
    return out


def census_rule(gh: tuple[int, int]) -> dict:
    g, h = gh
    code = h + 256 * g
    rng = np.random.default_rng([64, g, h])
    rows = []
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            P = K.programs(k, lo, min(lo + K.CHUNK, 10 ** k), False)
            scr = np.nonzero(K.classify_shift(P, code, 1, 0x6401 + k)[0])[0]
            if len(scr):
                conf, sh = K.classify_shift(P[scr], code, 4, 0x6402 + k)
                for i, c, d in zip(scr, conf, sh):
                    if c:
                        rows.append({"kernel": bytes(P[i, :k]).decode(), "orientation": K.label(c), "shift": int(d),
                                     "self_sufficient": S.self_sufficient(P[i].copy(), code, rng)})
    ss = [r for r in rows if r["self_sufficient"]]
    return {"g": g, "h": h, "code": code, "copiers": len(rows),
            **{lab: sum(r["orientation"] == lab for r in rows) for lab in ("forward", "reverse", "both")},
            "self_sufficient": len(ss), "class": "F" if ss else ("C" if rows else "0"),
            "self_sufficient_orientation": dict(Counter(r["orientation"] for r in ss)),
            "examples_self_sufficient": [(r["kernel"], r["shift"]) for r in ss][:6]}


def census(workers: int) -> dict:
    with Pool(workers) as pool:
        res = pool.map(census_rule, sample(), chunksize=1)
    return {"rules": res, "F": [(r["g"], r["h"]) for r in res if r["class"] == "F"],
            "C": [(r["g"], r["h"]) for r in res if r["class"] == "C"],
            "n_none": sum(r["class"] == "0" for r in res)}


def soups(workers: int, census_path: str) -> dict:
    c = json.load(open(census_path))
    rng = np.random.default_rng(640)
    pick = {}
    for cls in ("F", "C"):
        pool_ = [tuple(x) for x in c[cls]]
        idx = rng.choice(len(pool_), min(4, len(pool_)), replace=False) if pool_ else []
        pick[cls] = sorted(pool_[i] for i in idx)
    if len(pick["F"]) < 2 or len(pick["C"]) < 2:
        return {"summary": {"primary": "undecided (fewer than 2 rules in a class)", "picked": pick}, "results": []}
    rules = [(cls, g, h) for cls in ("F", "C") for g, h in pick[cls]]
    jobs = [(6400 + 10 * r + i, h + 256 * g) for r, (_, g, h) in enumerate(rules) for i in range(4)]
    Lg.RUN = Path("runs/e64")
    Lg.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(Lg.job, jobs, chunksize=1)
    cls_of = {h + 256 * g: cls for cls, g, h in rules}
    j = {k: sum(r["jumped"] for r in res if cls_of[r["h1"]] == k) for k in ("F", "C")}
    n = {k: sum(cls_of[r["h1"]] == k for r in res) for k in ("F", "C")}
    m, tot = j["F"] + j["C"], n["F"] + n["C"]
    p = sum(comb(m, x) * comb(tot - m, n["F"] - x) for x in range(j["F"], min(m, n["F"]) + 1)) / comb(tot, n["F"])
    ok = j["F"] >= 0.75 * n["F"] and j["C"] <= 0.25 * n["C"] and p < 0.01
    return {"summary": {"picked": pick, "jumped": j, "of": n, "fisher_p": p, "primary": "pass" if ok else "fail",
                        "per_rule": {f"g{g}h{h}": {"class": cls, "jumped": sum(r["jumped"] for r in res if r["h1"] == h + 256 * g),
                                                   "T": [r["T"] for r in res if r["h1"] == h + 256 * g]}
                                     for cls, g, h in rules}},
            "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-09-e64-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-64", "part": a.part} | (census(a.workers) if a.part == "census" else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rules")}, indent=1, default=str))
    print(f"=== E64 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
