"""E-29: does any random Lenia rule turn a lone lump of matter into a reproducer?

Rule-level birth scan (Track D route 2, docs/data/e29-preregistration.md). For each rule drawn
with `Lenia.random` and each lump radius: a smooth random lump (Gaussian-blurred noise, width 3,
scaled to [0, 1], inside a disk) is placed alone in a 128x128 vacuum and run SETTLE steps. The
settled state is then given to the validated birth detector (`births.scan`, 2 most common
object types, two generations in isolation, background null). Unlike E-27/E-28 no world is
selected first: every rule drawn is tested, so the detector's own nulls are the only nulls needed.

Pipeline positive: Gray-Scott (Pearson's dividing spots) lumps, scanned the same way.

Usage: python scripts/lump_scan.py --rules 1500 --out docs/data/experiments/2026-11-07-e29-lump-scan.json --workers 11
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

from emergence.observatory import births as B
from emergence.observatory import continuous as C
from emergence.physics import GrayScott, Lenia

SIDE, SETTLE = 128, 300
RADII = (13, 26)


def lump(rng: np.random.Generator, r: int, side: int = SIDE) -> np.ndarray:
    """Levels 0..255: smooth noise in a disk of radius r at the centre of an empty world."""
    n = rng.normal(size=(2 * r + 1, 2 * r + 1))
    n = ndimage.gaussian_filter(n, 3, mode="wrap")
    n = (n - n.min()) / (n.max() - n.min() + 1e-12)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    patch = np.where(yy ** 2 + xx ** 2 <= r * r, n, 0)
    out = np.zeros((side, side))
    c = side // 2
    out[c - r:c + r + 1, c - r:c + r + 1] = patch
    return np.rint(out * 255).astype(np.uint8)


def _occ(ph, s):
    f = B.field(ph, s)
    return float((f >= C._thr(f)).mean())


def settle(ph, s: np.ndarray) -> tuple[np.ndarray, int, bool]:
    """Run SETTLE steps. If the world fills up (a fast divider or a spreading front), return the
    last checkpoint (every 25 steps, from step 50) that was not yet full, so its objects are still tested."""
    last, t_last = None, 0
    for t in range(1, SETTLE + 1):
        s = ph.step(s)
        if t % 25 == 0 and t >= 50:
            if _occ(ph, s) > B.FILL_FRACTION:
                return (last, t_last, True) if last is not None else (s, t, True)
            last, t_last = s, t
    return s, SETTLE, False


def outcome(ph, s: np.ndarray, rng: np.random.Generator) -> dict:
    s, t, filled = settle(ph, s)
    occ = _occ(ph, s)
    objs = B.find(ph, s)
    base = {"filled": filled, "tested_at": t, "objects": len(objs), "occupied": round(occ, 4)}
    if not objs:
        return base | {"settled": "extinct", "verdicts": []}
    if occ > B.FILL_FRACTION:
        return base | {"settled": "filled", "verdicts": []}
    res = B.scan(ph, s, rng, max_candidates=2)
    hits = [{k: r.get(k) for k in ("verdict", "parent_mass", "background_copies", "attractor")}
            | ({"gen1": {k: v for k, v in r["gen1"].items() if k != "series"}} if r.get("gen1") else {})
            | ({"gen2": {k: v for k, v in r["gen2"].items() if k != "series"}} if r.get("gen2") else {})
            for r in res["results"] if r["verdict"] != "no reproduction"]
    return base | {"settled": "objects", "verdicts": res["verdicts"], "reproducers": res["reproducers"], "hits": hits}


def lenia_job(args):
    i, seed = args
    t0 = time.time()
    rng = np.random.default_rng([seed, i])
    ph = Lenia.random(rng)
    out = {"i": i, "rule": ph.label(), "lumps": []}
    for r in RADII:
        s = lump(rng, r)
        out["lumps"].append({"radius": r} | outcome(ph, s, rng))
    out["seconds"] = round(time.time() - t0, 1)
    return out


def gs_job(seed):
    ph = GrayScott()
    rng = np.random.default_rng([seed, 29])
    out = {"seed": seed, "lumps": []}
    for r in RADII:
        s = ph.from_levels(lump(rng, r // 2))  # V up to its display maximum inside a disk
        out["lumps"].append({"radius": r // 2} | outcome(ph, s, rng))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=29)
    ap.add_argument("--gs", type=int, default=10)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    with Pool(a.workers or None) as p:
        gs = p.map(gs_job, range(a.gs), chunksize=1)
        print("Gray-Scott pipeline positive:", sum(any(l.get("reproducers") for l in g["lumps"]) for g in gs),
              "/", a.gs, flush=True)
        res = []
        for k, r in enumerate(p.imap_unordered(lenia_job, [(i, a.seed) for i in range(a.rules)], chunksize=2)):
            res.append(r)
            if (k + 1) % 100 == 0:
                print(k + 1, "rules,", round(time.time() - t0), "s", flush=True)
    res.sort(key=lambda r: r["i"])
    settled = Counter(l["settled"] for r in res for l in r["lumps"])
    verdicts = Counter(v for r in res for l in r["lumps"] for v in l["verdicts"])
    repro = sorted({r["rule"] for r in res for l in r["lumps"] if l.get("reproducers")})
    print("settled:", dict(settled))
    print("verdicts:", dict(verdicts))
    print("rules with a reproducer:", len(repro), repro)
    json.dump({"experiment": "E-29", "seed": a.seed, "rules": a.rules, "radii": RADII, "side": SIDE,
               "settle": SETTLE, "gray_scott_positive": gs, "lenia": res,
               "summary": {"settled": dict(settled), "verdicts": dict(verdicts), "reproducer_rules": repro},
               "seconds": round(time.time() - t0)}, open(a.out, "w"), indent=1)
    print("E29 DONE", flush=True)


if __name__ == "__main__":
    main()
