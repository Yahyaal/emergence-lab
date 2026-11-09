"""E-58 (docs/data/e58-preregistration.md): a matched control rule, head1 starts at byte 127 (backward copiers,
as many shortest ones as the fast head1 = 64 rule). Slow like the standard rule, or fast like head1 = 64?

    python scripts/bff_h127.py --part census --out docs/data/experiments/2026-11-08-e58-census.json
    python scripts/bff_h127.py --part soups --workers 4 --out docs/data/experiments/2026-11-08-e58-soups.json
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

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402
import bff_mirror as M  # noqa: E402

H1 = 127
E57_REF = (8, 8)  # head1 = 64 soups of 2^14 jumped by 16,000 rounds (E-57)


def census() -> dict:
    rng = np.random.default_rng(580)
    hits = []
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            P = K.programs(k, lo, min(lo + K.CHUNK, 10 ** k), False)
            scr = np.nonzero(K.classify(P, H1, 1, 0x5801 + k))[0]
            if len(scr):
                conf = K.classify(P[scr], H1, 4, 0x5802 + k)
                hits += [(bytes(P[i, :k]).decode(), P[i].copy(), K.label(c)) for i, c in zip(scr, conf) if c]
    rows = [{"kernel": h, "orientation": lab, "self_sufficient": M.self_sufficient(x, H1, rng)} for h, x, lab in hits]
    n = len(rows)
    cnt = {lab: sum(r["orientation"] == lab for r in rows) for lab in ("forward", "reverse", "both")}
    ss = sum(r["self_sufficient"] for r in rows)
    out = {"copiers": n, **cnt, "self_sufficient": ss, "fraction_self_sufficient": round(ss / max(n, 1), 3),
           "shortest": {lab: min((len(r["kernel"]) for r in rows if r["orientation"] == lab), default=None)
                        for lab in ("forward", "reverse")},
           "examples": [r["kernel"] for r in rows][:12], "rows": rows}
    out["primary_B"] = {"reverse_ge_90pct": n > 0 and cnt["reverse"] >= 0.9 * n,
                        "self_sufficient_le_5pct": out["fraction_self_sufficient"] <= 0.05}
    out["primary_B"]["pass"] = all(out["primary_B"].values())
    return out


def soups(workers: int) -> dict:
    C.H1, C.N, C.WAIT, C.AFTER, C.RUN, C.SEEDS = H1, 2 ** 14, 16000, 1000, Path("runs/e58"), range(5800, 5808)
    C.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(C.job, list(C.SEEDS), chunksize=1)
    jumped = [r for r in res if r["jumped"]]
    # one-sided: is the head1 = 127 jump count LOWER than E-57's? P(X <= a) with X hypergeometric
    a, n1 = len(jumped), len(res)
    b, n2 = E57_REF
    m, tot = a + b, n1 + n2
    p = sum(comb(m, x) * comb(tot - m, n1 - x) for x in range(0, a + 1)) / comb(tot, n1)
    rev_ok = [r["orientation"]["reverse"] >= 1 and r["orientation"]["reverse"] >= 0.9 * (
        r["orientation"]["forward"] + r["orientation"]["reverse"] + r["orientation"]["both"]) for r in jumped]
    return {"summary": {"jumped": a, "of": n1, "T": {r["seed"]: r["T"] for r in res},
                        "reference_E57": {"jumped": E57_REF[0], "of": E57_REF[1]}, "fisher_p_lower": p,
                        "primary_A": "pass" if a <= 2 and p < 0.01 else "fail",
                        "secondary_reverse": ("undecided (no jump)" if not jumped else
                                              ("pass" if all(rev_ok) else "fail")),
                        "orientation": {r["seed"]: {k: v for k, v in r["orientation"].items() if k != "copiers"}
                                        for r in jumped},
                        "max_hoe": {r["seed"]: max(s["hoe"] for s in r["series"]) for r in res}},
            "results": res}


def rerun(workers: int, seeds: list[int]) -> dict:
    """Follow-up (not pre-registered; see J-058): replay the given seeds from scratch with the HOE stop disabled,
    to 16,000 rounds, and classify the 40 most common programs at the end. Deterministic: the first rounds equal
    the Part A run."""
    C.H1, C.N, C.WAIT, C.RUN, C.THRESH = H1, 2 ** 14, 16000, Path("runs/e58b"), float("inf")
    C.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(C.job, seeds, chunksize=1)
    return {"summary": {"seeds": seeds,
                        "end_orientation": {r["seed"]: {k: v for k, v in r["orientation"].items() if k != "copiers"}
                                            for r in res},
                        "max_steps_per_pair": {r["seed"]: max(s["steps_per_pair"] for s in r["series"]) for r in res},
                        "max_hoe": {r["seed"]: max(s["hoe"] for s in r["series"]) for r in res}},
            "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups", "rerun"), required=True)
    ap.add_argument("--seeds", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-58", "part": a.part, "h1": H1} | (census() if a.part == "census" else soups(a.workers) if a.part == "soups"
                                                        else rerun(a.workers, [int(x) for x in a.seeds.split(",")]))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rows")}, indent=1, default=str))
    print(f"=== E58 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
