"""E-60 (docs/data/e60-preregistration.md): across all head-start rules (head1 starts at byte h), does having a
self-sufficient short copier (F) vs not (S) predict fast replicator emergence?

    python scripts/bff_headstart.py --part census --workers 5 --out docs/data/experiments/2026-11-08-e60-census.json
    python scripts/bff_headstart.py --part soups --workers 5 --census docs/data/experiments/2026-11-08-e60-census.json \
        --out docs/data/experiments/2026-11-08-e60-soups.json
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
import bff_kernels as K  # noqa: E402
import bff_mirror as M  # noqa: E402
import bff_orient_confirm as E  # noqa: E402

KNOWN = (0, 64, 127)


def census_rule(h: int) -> dict:
    rng = np.random.default_rng([60, h])
    rows = []
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            P = K.programs(k, lo, min(lo + K.CHUNK, 10 ** k), False)
            scr = np.nonzero(K.classify(P, h, 1, 0x6001 + k))[0]
            if len(scr):
                conf = K.classify(P[scr], h, 4, 0x6002 + k)
                for i, c in zip(scr, conf):
                    if c:
                        rows.append({"kernel": bytes(P[i, :k]).decode(), "orientation": K.label(c),
                                     "self_sufficient": M.self_sufficient(P[i].copy(), h, rng)})
    ss = [r for r in rows if r["self_sufficient"]]
    return {"h": h, "copiers": len(rows),
            **{lab: sum(r["orientation"] == lab for r in rows) for lab in ("forward", "reverse", "both")},
            "self_sufficient": len(ss), "class": "F" if ss else "S",
            "shortest_self_sufficient": min((len(r["kernel"]) for r in ss), default=None),
            "examples_self_sufficient": [r["kernel"] for r in ss][:6]}


def census(workers: int) -> dict:
    with Pool(workers) as pool:
        res = pool.map(census_rule, range(128), chunksize=1)
    F = [r["h"] for r in res if r["class"] == "F"]
    known_ok = {0: "S", 64: "F", 127: "S"}
    return {"rules": res, "F": F, "S": [r["h"] for r in res if r["class"] == "S"],
            "known_agree": all(res[h]["class"] == c for h, c in known_ok.items())}


def soups(workers: int, census_path: str) -> dict:
    c = json.load(open(census_path))
    rng = np.random.default_rng(60)
    pick = {}
    for cls in ("F", "S"):
        pool_ = [h for h in c[cls] if h not in KNOWN]
        pick[cls] = sorted(int(x) for x in rng.choice(pool_, min(4, len(pool_)), replace=False)) if pool_ else []
    rules = [(cls, h) for cls in ("F", "S") for h in pick[cls]]
    jobs = [(6000 + 10 * rank + i, h) for rank, (_, h) in enumerate(rules) for i in range(4)]
    E.RUN = Path("runs/e60")
    E.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(E.job, jobs, chunksize=1)
    cls_of = {h: cls for cls, h in rules}
    j = {cls: sum(r["jumped"] for r in res if cls_of[r["h1"]] == cls) for cls in ("F", "S")}
    n = {cls: sum(cls_of[r["h1"]] == cls for r in res) for cls in ("F", "S")}
    if n["F"] and n["S"]:
        m, tot = j["F"] + j["S"], n["F"] + n["S"]
        p = sum(comb(m, x) * comb(tot - m, n["F"] - x) for x in range(j["F"], min(m, n["F"]) + 1)) / comb(tot, n["F"])
        primary = "pass" if j["F"] >= 0.75 * n["F"] and j["S"] <= 0.25 * n["S"] and p < 0.01 else "fail"
    else:
        p, primary = None, "undecided (a class is empty)"
    per_rule = {h: {"class": cls_of[h], "jumped": sum(r["jumped"] for r in res if r["h1"] == h),
                    "T": [r["T"] for r in res if r["h1"] == h],
                    "copiers_in_census": next(x["copiers"] for x in c["rules"] if x["h"] == h),
                    "orientation_jumped": [{k: v for k, v in r["orientation"].items() if k != "copiers"}
                                           for r in res if r["h1"] == h and r["jumped"]]} for _, h in rules}
    return {"summary": {"picked": pick, "jumped": j, "of": n, "fisher_p": p, "primary": primary,
                        "per_rule": per_rule}, "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-08-e60-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-60", "part": a.part} | (census(a.workers) if a.part == "census"
                                                       else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    show = {k: v for k, v in out.items() if k not in ("results", "rules")}
    print(json.dumps(show, indent=1, default=str))
    print(f"=== E60 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
