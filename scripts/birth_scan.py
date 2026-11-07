"""E-27: scan stored worlds for reproducers with the birth detector (observatory/births.py).

For each world: replay its spec to the final step, test the 6 most common object types
(`births.scan`) plus every in-world mover track of the last 100 steps (verify_movers criteria).
Also runs the pipeline positive: Gray-Scott random soups, scanned the same way.

Usage: python scripts/birth_scan.py --out docs/data/experiments/2026-11-07-e27-births.json --workers 10
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool

import numpy as np

from emergence.engine import Universe, UniverseSpec
from emergence.observatory import births as B
from emergence.observatory import continuous as C
from emergence.physics import GrayScott
from emergence.storage import Store

POOL_A = [("runs/e14.db", 1), ("runs/e14.db", 2), ("runs/e18.db", 1), ("runs/e26.db", 1), ("runs/e26.db", 2),
          ("runs/e24.db", 1)]


def _summary(r):
    return {k: r.get(k) for k in ("verdict", "parent_mass", "gen1", "gen2", "background_copies", "attractor")
            if k in r} | ({"gen1": {k: v for k, v in r["gen1"].items() if k != "series"}} if r.get("gen1") else {})


def scan_world(args):
    db, uid = args
    t0 = time.time()
    u = Store(db).universe(uid)
    w = Universe.from_spec(UniverseSpec.from_dict(u["spec"]))
    ph = w.physics
    w.step(u["steps"] - 100)
    fr = []
    for _ in range(100):
        fr.append(w.state.copy())
        w.step()
    rng = np.random.default_rng(uid)
    res = B.scan(ph, fr[-1], rng)
    tracks, per = C.track(fr)
    labels = {}
    movers = []
    for tr in tracks:
        disp = np.hypot(*tr["disp"])
        if tr["length"] < 80 or disp < C.MIN_TRAVEL or disp < 0.5 * max(tr["path"], 1e-9):
            continue
        t, j = tr["last"]
        if t not in labels:
            labels[t] = C.label_torus(fr[t] >= C._thr(fr[t]))[0]
        o = dict(per[t][j], mask=labels[t] == per[t][j]["label"])
        movers.append(B.reproduction_test(ph, fr[t], o, rng))
    verdicts = res["verdicts"] + [m["verdict"] for m in movers]
    return {"db": db, "uid": uid, "rule": u["rule"], "init": (u.get("aggregate") or {}).get("init"),
            "movers_in_world": (u["metrics"].get("self_propelled_shapes") or 0),
            "candidates": len(verdicts), "mover_candidates": len(movers),
            "reproducers": sum(v == "reproducer" for v in verdicts),
            "verdicts": verdicts,
            "hits": [_summary(r) for r in res["results"] + movers if r["verdict"] not in ("no reproduction",)],
            "seconds": round(time.time() - t0, 1)}


def gs_world(seed):
    # Pearson-style start (E-27 amendment): 4 perturbed 12x12 squares (U 0.5, V 0.25) at random places
    ph = GrayScott()
    rng = np.random.default_rng(seed)
    s = ph.vacuum((128, 128))
    for r, c in rng.integers(0, 116, size=(4, 2)):
        s[0, r:r + 12, c:c + 12] = 0.5
        s[1, r:r + 12, c:c + 12] = 0.25 + 0.01 * rng.random((12, 12))
    for _ in range(2000):
        s = ph.step(s)
    res = B.scan(ph, s, np.random.default_rng(seed))
    return {"seed": seed, "objects": len(B.find(ph, s)), "candidates": res["tested"],
            "reproducers": res["reproducers"], "verdicts": res["verdicts"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--n-blob", type=int, default=100)
    a = ap.parse_args()
    pool_a, rest = [], []
    for db, e in POOL_A:
        for u in Store(db).universes(e):
            ((pool_a if (u["metrics"].get("self_propelled_shapes") or 0) > 0 else rest)
             .append((db, u["id"])))
    rng = np.random.default_rng(27)
    pool_b = [rest[i] for i in sorted(rng.choice(len(rest), size=min(a.n_blob, len(rest)), replace=False))]
    print(f"pool A {len(pool_a)} mover worlds, pool B {len(pool_b)} of {len(rest)} worlds without movers", flush=True)
    with Pool(a.workers or None) as p:
        gs = p.map(gs_world, range(1, 11), chunksize=1)
        print("Gray-Scott pipeline positive:", sum(g["reproducers"] > 0 for g in gs), "/ 10 worlds", flush=True)
        ra = p.map(scan_world, pool_a, chunksize=1)
        print("pool A:", sum(r["reproducers"] > 0 for r in ra), "/", len(ra), "worlds with a reproducer", flush=True)
        rb = p.map(scan_world, pool_b, chunksize=1)
        print("pool B:", sum(r["reproducers"] > 0 for r in rb), "/", len(rb), "worlds with a reproducer", flush=True)
    from collections import Counter
    for name, rr in (("A", ra), ("B", rb)):
        print(name, dict(Counter(v for r in rr for v in r["verdicts"])))
    json.dump({"experiment": "E-27", "gray_scott_positive": gs, "pool_a": ra, "pool_b": rb}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
