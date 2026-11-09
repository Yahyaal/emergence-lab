"""E-61 (docs/data/e61-preregistration.md): E-60's census of all 128 head-start rules with a shift-aware copy
classifier (copies up to 16 bytes off byte 64), and soups in any newly self-sufficient rules.

    python scripts/bff_shift_census.py --part census --workers 9 --out docs/data/experiments/2026-11-08-e61-census.json
    python scripts/bff_shift_census.py --part soups --workers 9 --out docs/data/experiments/2026-11-08-e61-soups.json
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
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402
import bff_orient_confirm as E  # noqa: E402

E60 = "docs/data/experiments/2026-11-08-e60-census.json"
OLD_F = (62, 63, 64, 65)
E60_S = (2, 16)  # E-60 S-rule soups: jumped, of


def product(P: np.ndarray, h1: int, rng) -> np.ndarray:
    tape = np.concatenate([P, rng.integers(0, 256, K.L, dtype=np.uint8)]).astype(np.uint8)
    K.lib().run_tape(tape.ctypes.data, 2 * K.L, K.STEPS, h1)
    return tape[K.L:].copy()


def self_sufficient(P: np.ndarray, h1: int, rng, runs: int = 4) -> bool:
    prods = np.array([product(P, h1, rng) for _ in range(runs)])
    ok, _ = K.classify_shift(prods, h1, 4, int(rng.integers(1 << 62)))
    return int((ok > 0).sum()) >= 3


def census_rule(h: int) -> dict:
    rng = np.random.default_rng([61, h])
    rows = []
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            P = K.programs(k, lo, min(lo + K.CHUNK, 10 ** k), False)
            scr = np.nonzero(K.classify_shift(P, h, 1, 0x6101 + k)[0])[0]
            if len(scr):
                conf, sh = K.classify_shift(P[scr], h, 4, 0x6102 + k)
                for i, c, d in zip(scr, conf, sh):
                    if c:
                        rows.append({"kernel": bytes(P[i, :k]).decode(), "orientation": K.label(c), "shift": int(d),
                                     "self_sufficient": self_sufficient(P[i].copy(), h, rng)})
    ss = [r for r in rows if r["self_sufficient"]]
    return {"h": h, "copiers": len(rows), "aligned": sum(r["shift"] == 0 for r in rows),
            **{lab: sum(r["orientation"] == lab for r in rows) for lab in ("forward", "reverse", "both")},
            "shifts": dict(Counter(r["shift"] for r in rows)), "self_sufficient": len(ss),
            "self_sufficient_orientation": dict(Counter(r["orientation"] for r in ss)),
            "class": "F" if ss else "S", "examples_self_sufficient": [(r["kernel"], r["shift"]) for r in ss][:6]}


def census(workers: int) -> dict:
    with Pool(workers) as pool:
        res = pool.map(census_rule, range(128), chunksize=1)
    old = {r["h"]: r for r in json.load(open(E60))["rules"]}
    F = [r["h"] for r in res if r["class"] == "F"]
    checks = {"aligned_ge_e60": all(r["copiers"] >= old[r["h"]]["copiers"] for r in res),
              "F_contains_62_65": set(OLD_F) <= set(F)}
    p1 = all(48 <= h <= 80 for h in F) and all(set(r["self_sufficient_orientation"]) <= {"forward"}
                                               for r in res if r["class"] == "F")
    return {"rules": res, "F": F, "S": [r["h"] for r in res if r["class"] == "S"], "new_F": [h for h in F if h not in OLD_F],
            "rules_with_copiers": sum(r["copiers"] > 0 for r in res),
            "e60_rules_with_copiers": sum(old[h]["copiers"] > 0 for h in old), "checks": checks,
            "primary1": "pass" if p1 else "fail",
            "e60_S_rules": {h: {k: res[h][k] for k in ("class", "copiers", "aligned", "shifts")} for h in (7, 120, 125, 126)}}


def orient_shift(P: np.ndarray, h1: int, seed: int) -> dict:
    X = np.array(C.distinct_top(P))
    c, sh = K.classify_shift(X, h1, 4, seed)
    labs = [K.label(x) for x in c]
    return {lab: labs.count(lab) for lab in ("forward", "reverse", "both", "none")} | {
        "shifts": dict(Counter(int(d) for d, x in zip(sh, c) if x)),
        "copiers": [X[i].tobytes().hex() for i, l in enumerate(labs) if l != "none"][:10]}


def soups(workers: int, census_path: str) -> dict:
    c = json.load(open(census_path))
    new = c["new_F"]
    if not new:
        return {"summary": {"primary2": "undecided (no new F rules)"}, "results": []}
    rng = np.random.default_rng(61)
    pick = sorted(int(x) for x in rng.choice(new, min(4, len(new)), replace=False))
    jobs = [(6100 + 10 * rank + i, h) for rank, h in enumerate(pick) for i in range(4)]
    C.orient = orient_shift  # D-046 copier check, shift-aware (E.job calls C.orient)
    E.RUN = Path("runs/e61")
    E.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(E.job, jobs, chunksize=1)
    j, n = sum(r["jumped"] for r in res), len(res)
    a, b = E60_S
    m, tot = j + a, n + b
    p = sum(comb(m, x) * comb(tot - m, n - x) for x in range(j, min(m, n) + 1)) / comb(tot, n)
    return {"summary": {"picked": pick, "jumped": j, "of": n, "fisher_p_vs_e60_S": p,
                        "primary2": "pass" if j >= 0.75 * n and p < 0.01 else "fail",
                        "per_rule": {h: {"jumped": sum(r["jumped"] for r in res if r["h1"] == h),
                                         "T": [r["T"] for r in res if r["h1"] == h]} for h in pick}},
            "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=9)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-08-e61-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-61", "part": a.part} | (census(a.workers) if a.part == "census" else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rules")}, indent=1, default=str))
    print(f"=== E61 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
