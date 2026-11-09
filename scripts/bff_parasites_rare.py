"""E-67 (docs/data/e67-preregistration.md): parasites further down the abundance ranking of the final E-54 snapshots.

    python scripts/bff_parasites_rare.py --workers 11 --out docs/data/experiments/2026-11-09-e67-rare.json
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from emergence.observatory import program_parasites as PP

E54 = Path("docs/data/experiments/2026-11-08-e54-long-soups.json")
STRATA = {"mid": (6, 40), "rare": (2, 5), "single": (1, 1)}
PER = 20
CACHE = Path("runs/e67.jsonl")


def snap(s, e):
    return np.load(f"runs/e54/{s}-{e}.npy")


def job(arg):
    soup, epoch, stratum, i, h, tops = arg
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    si = list(STRATA).index(stratum)
    a = PP.alone_test(x, np.random.default_rng([67, soup, si, i]), 10)
    out = {"soup": soup, "epoch": epoch, "stratum": stratum, "i": i, "program": h, "gen1_ok": a["gen1_ok"]}
    T = np.array([np.frombuffer(bytes.fromhex(t), np.uint8) for t in tops])
    out["dist_top40"] = int(min(np.minimum((T != x).sum(1), (T != x[::-1]).sum(1))))
    if a["gen1_ok"] == 0:
        r = PP.parasite_test(x, snap(soup, epoch), np.random.default_rng([670, soup, si, i]), alone="no replication")
        r.pop("hosts")
        out["parasite_test"] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    rows = json.load(open(E54))["verdicts"]
    final = {}
    for r in rows:
        final[r[0]] = max(final.get(r[0], 0), r[1])
    jobs = []
    for soup, e in sorted(final.items()):
        tops = [r[3] for r in rows if r[0] == soup and r[1] == e]
        P = snap(soup, e)
        vals, counts = np.unique(P, axis=0, return_counts=True)
        rng = np.random.default_rng([67, soup])
        for st, (lo, hi) in STRATA.items():
            idx = np.flatnonzero((counts >= lo) & (counts <= hi))
            for i, k in enumerate(rng.choice(idx, PER, replace=False)):
                jobs.append((soup, e, st, i, bytes(vals[k]).hex(), tops))
    done = {}
    if CACHE.exists():
        for line in CACHE.read_text().splitlines():
            d = json.loads(line)
            done[(d["soup"], d["stratum"], d["i"])] = d
    todo = [j for j in jobs if (j[0], j[2], j[3]) not in done]
    print(f"{len(jobs)} programs, {len(done)} cached", flush=True)
    with Pool(a.workers) as pool, CACHE.open("a") as f:
        for k, d in enumerate(pool.imap_unordered(job, todo)):
            done[(d["soup"], d["stratum"], d["i"])] = d
            f.write(json.dumps(d) + "\n")
            f.flush()
            if k % 50 == 0:
                print(f"{k}/{len(todo)} {time.time() - t0:.0f}s", flush=True)
    res = list(done.values())
    summ = {"P1": {"parasites": sum(r.get("parasite_test", {}).get("verdict") == "parasite" for r in res),
                   "programs": len(res)}}
    summ["P1"]["pass"] = summ["P1"]["parasites"] <= 2
    sc = {st: round(sum(r["gen1_ok"] > 0 for r in res if r["stratum"] == st) / sum(r["stratum"] == st for r in res), 3)
          for st in STRATA}
    summ["P2"] = {"self_copier_frac": sc, "pass": sc["mid"] >= 0.9 and sc["rare"] >= 0.7 and sc["single"] >= 0.5}
    summ["P3"] = {st: {"verdicts": dict(Counter(r["parasite_test"]["verdict"] for r in res
                                                if r["stratum"] == st and "parasite_test" in r)),
                       "median_dist_top40_self": float(np.median([r["dist_top40"] for r in res if r["stratum"] == st and r["gen1_ok"] > 0] or [-1])),
                       "median_dist_top40_non": float(np.median([r["dist_top40"] for r in res if r["stratum"] == st and r["gen1_ok"] == 0] or [-1]))}
                  for st in STRATA}
    summ["by_soup"] = {s: {st: sum(r["gen1_ok"] > 0 for r in res if r["soup"] == s and r["stratum"] == st) for st in STRATA}
                       for s in sorted(final)}
    summ["seconds"] = round(time.time() - t0)
    Path(a.out).write_text(json.dumps({"experiment": "E-67", "summary": summ, "rows": res}, indent=1))
    print(json.dumps(summ, indent=1))
    print("=== SENTINEL e67")


if __name__ == "__main__":
    main()
