"""E-66 (docs/data/e66-preregistration.md): (A) the replicator test repeated 10 times on all E-54 top-40 programs
(and a pre-transition null); (B) the parasite test on programs whose generation 1 never grew.

    python scripts/bff_parasites.py --workers 11 --out docs/data/experiments/2026-11-09-e66-parasites.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_long_analysis as LA  # noqa: E402

from emergence.observatory import program_parasites as PP  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

E54 = Path("docs/data/experiments/2026-11-08-e54-long-soups.json")
REPEATS = 10
NULL_SEEDS, NULL_EPOCHS, NULL_N = (6601, 6602), 2000, 2 ** 14
CACHE = Path("runs/e66-partA.jsonl")


def prog(h: str) -> np.ndarray:
    return np.frombuffer(bytes.fromhex(h), np.uint8).copy()


def alone(arg):
    key, h = arg
    r = PP.alone_test(prog(h), np.random.default_rng([66] + list(key)), REPEATS)
    return key, r["gen1_ok"], r["verdicts"]


def null_soup(seed: int) -> dict:
    f = Path(f"runs/e66-null-{seed}.npy")
    if f.exists():
        P = np.load(f)
    else:
        s = B.Soup(n=NULL_N, seed=seed)
        for _ in range(NULL_EPOCHS):
            s.epoch()
        P = s.programs
        np.save(f, P)
    return {"seed": seed, "hoe": round(B.high_order_entropy(P), 3),
            "top": [bytes(x).hex() for x in LA.distinct_top(P)]}


def para(arg):
    seed, e, rank, h, copier_hex = arg
    P = LA.snap(seed, e)
    x = prog(h)
    r = PP.parasite_test(x, P, np.random.default_rng([660, seed, e, rank]), alone="no replication")
    cop = [prog(c) for c in copier_hex]
    hosts = r.pop("hosts")
    hc = sum(any(PP.like(P[j], c)[0] for c in cop) for j in hosts)
    return {"soup": seed, "epoch": e, "rank": rank, "program": h, **r, "n_hosts": len(hosts),
            "hosts_self_copiers": hc}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    rows = json.load(open(E54))["verdicts"]
    with Pool(a.workers) as pool:
        nulls = pool.map(null_soup, NULL_SEEDS)
        print("null soups", [(n["seed"], n["hoe"], len(n["top"])) for n in nulls], flush=True)
        jobs = [((n["seed"], 0, i), h) for n in nulls for i, h in enumerate(n["top"])]
        jobs += [((r[0], r[1], r[2]), r[3]) for r in rows]
        res = {}
        if CACHE.exists():
            for line in CACHE.read_text().splitlines():
                k_, g1_, vs_ = json.loads(line)
                res[tuple(k_)] = (g1_, vs_)
        todo = [j for j in jobs if j[0] not in res]
        print(f"part A: {len(res)} cached, {len(todo)} to run", flush=True)
        cache = CACHE.open("a")
        for k, (key, g1, vs) in enumerate(pool.imap_unordered(alone, todo, chunksize=4)):
            res[key] = (g1, vs)
            cache.write(json.dumps([list(key), g1, vs]) + "\n")
            cache.flush()
            if k % 200 == 0:
                print(f"part A {k}/{len(todo)} {time.time() - t0:.0f}s", flush=True)
        A = [{"soup": r[0], "epoch": r[1], "rank": r[2], "program": r[3], "e54": r[4],
              "gen1_ok": res[(r[0], r[1], r[2])][0], "verdicts": res[(r[0], r[1], r[2])][1]} for r in rows]
        N = [{"soup": n["seed"], "rank": i, "program": h, "gen1_ok": res[(n["seed"], 0, i)][0]}
             for n in nulls for i, h in enumerate(n["top"])]
        snaps = {}
        for r in A:
            if r["gen1_ok"] > 0:
                snaps.setdefault((r["soup"], r["epoch"]), []).append(r["program"])
        bj = [(r["soup"], r["epoch"], r["rank"], r["program"], snaps.get((r["soup"], r["epoch"]), []))
              for r in A if r["gen1_ok"] == 0 and r["e54"] == "no replication"]
        print(f"part B: {len(bj)} candidates", flush=True)
        Bres = list(pool.imap_unordered(para, bj, chunksize=2))

    nr = [r for r in A if r["e54"] == "no replication"]
    by_soup = {}
    for s in sorted({r["soup"] for r in A}):
        ns = [r for r in nr if r["soup"] == s]
        al = [r for r in A if r["soup"] == s]
        by_soup[s] = {"no_rep_rows": len(ns), "no_rep_grew": sum(r["gen1_ok"] > 0 for r in ns),
                      "frac_no_rep_grew": round(sum(r["gen1_ok"] > 0 for r in ns) / max(len(ns), 1), 3),
                      "self_copier_frac": round(sum(r["gen1_ok"] > 0 for r in al) / len(al), 3),
                      "e54_replicator_frac": round(sum(r["e54"] == "replicator" for r in al) / len(al), 3)}
    pooled = sum(r["gen1_ok"] > 0 for r in nr) / len(nr)
    soups_ok = sum(v["frac_no_rep_grew"] >= 0.5 for v in by_soup.values())
    sc = sum(r["gen1_ok"] > 0 for r in A) / len(A)
    nonc = len(bj) / len(A)
    vc = Counter(r["verdict"] for r in Bres)
    summary = {
        "P1": {"pooled_frac_no_rep_grew": round(pooled, 3), "soups_ge_50": soups_ok, "soups": len(by_soup),
               "pass": bool(pooled >= 0.6 and soups_ok >= 5)},
        "P2": {"self_copier_frac": round(sc, 3), "e54_replicator_frac": round(sum(r['e54'] == 'replicator' for r in A) / len(A), 3),
               "pass": bool(sc >= 0.85)},
        "P3": {"null_self_copiers": sum(r["gen1_ok"] > 0 for r in N), "null_programs": len(N),
               "null_hoe": [n["hoe"] for n in nulls], "pass": sum(r["gen1_ok"] > 0 for r in N) == 0},
        "P4": {"non_copier_frac": round(nonc, 4), "verdicts": dict(vc),
               "parasite_or_byproduct_frac": round((vc["parasite"] + vc["by-product"]) / max(len(Bres), 1), 3),
               "pass": bool(nonc <= 0.1 and (vc["parasite"] + vc["by-product"]) >= 0.5 * max(len(Bres), 1))},
        "gen1_ok_hist": dict(Counter(r["gen1_ok"] for r in A)),
        "gen1_ok_hist_by_e54": {v: dict(Counter(r["gen1_ok"] for r in A if r["e54"] == v))
                                for v in ("replicator", "one generation", "no replication")},
        "by_soup": by_soup, "seconds": round(time.time() - t0)}
    out = {"experiment": "E-66", "summary": summary, "partA": A, "null": N, "partB": Bres}
    Path(a.out).write_text(json.dumps(out, indent=1, default=int))
    print(json.dumps(summary, indent=1, default=int))
    print("=== SENTINEL e66")


if __name__ == "__main__":
    main()
