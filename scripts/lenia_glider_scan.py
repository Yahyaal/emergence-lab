"""Glider viability scan (E-13 panel selection, J-013): for which Lenia rules does a
self-propelled structure EXIST at all, independently of whether soups produce one?

For each single-ring rule on a mu x sigma grid (R=13, T=10), a few asymmetric seeds
(elliptical discs with a value gradient, as in continuous.emergent_glider, at several
radii, slopes and elongations) are left to settle alone in an empty 128x128 world for
`settle` steps. A rule is glider-viable if any seed then passes the same self-propulsion
test the observatory uses (alone, keeps its mass within MASS_TOL and travels >=
MIN_TRAVEL cells in 100 steps) and is still one object of similar mass after a further
`hold` steps. Speed is measured over short legs so the torus never wraps.

This separates two questions that the discovery runs mix: "can a glider exist under this
rule?" (viability) and "does one arise from a random start?" (emergence).

Usage:
    python scripts/lenia_glider_scan.py --out docs/data/experiments/2026-11-07-e13a-glider-viability.json
"""
from __future__ import annotations

import argparse
import itertools
import json
from multiprocessing import Pool

import numpy as np

from emergence.observatory import continuous as C
from emergence.physics import Lenia

SEEDS = [dict(rad=r, slope=s, ecc=e) for r, s, e in itertools.product((7, 10, 13), (0.5, 1.0), (0.6, 0.85))]


def seed_world(side: int, rad: float, slope: float, ecc: float) -> np.ndarray:
    yy, xx = np.mgrid[0:side, 0:side]
    cy = cx = side // 2
    r = np.hypot((yy - cy) / ecc, xx - cx)
    g = np.clip(0.5 + slope * (xx - cx) / (2 * rad), 0, 1)
    a = np.where(r <= rad, g * np.clip(1 - (r / rad) ** 2, 0, 1) * 1.6, 0)
    return np.rint(np.clip(a, 0, 1) * 255).astype(np.uint8)


def viable(args) -> dict:
    mu, sigma, settle, hold = args
    phys = Lenia(13, 10, mu, sigma, [1.0])
    for sd in SEEDS:
        w = seed_world(128, **sd)
        for _ in range(settle):
            w = phys.step(w)
        objs = C.objects(w)
        if len(objs) != 1:
            continue
        o = objs[0]
        if not C.self_propelled(phys, w, o):
            continue
        m0, c, path = o["mass"], o["c"], np.zeros(2)
        ok = True
        for _ in range(hold // 25):
            for _ in range(25):
                w = phys.step(w)
            objs = C.objects(w)
            if len(objs) != 1 or not (1 / C.MASS_TOL <= objs[0]["mass"] / m0 <= C.MASS_TOL):
                ok = False
                break
            path += C._torus_delta(c, objs[0]["c"], w.shape)
            c = objs[0]["c"]
        if ok:
            return {"rule": phys.label(), "mu": phys.mu, "sigma": phys.sigma, "viable": True, "seed": sd,
                    "mass": round(m0, 1), "speed": round(float(np.hypot(*path)) / hold, 3)}
    return {"rule": phys.label(), "mu": phys.mu, "sigma": phys.sigma, "viable": False}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mus", default="0.10,0.12,0.14,0.15,0.16,0.18,0.20,0.22,0.25,0.28,0.32")
    ap.add_argument("--ratios", default="0.05,0.07,0.09,0.10,0.11,0.13,0.15,0.18,0.22")
    ap.add_argument("--settle", type=int, default=300)
    ap.add_argument("--hold", type=int, default=400)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    grid = [(float(m), float(m) * float(r), a.settle, a.hold)
            for m in a.mus.split(",") for r in a.ratios.split(",")]
    with Pool(a.workers or None) as p:
        res = p.map(viable, grid, chunksize=1)
    v = [r for r in res if r["viable"]]
    print(f"{len(v)} of {len(res)} single-ring rules glider-viable")
    for r in v:
        print(f"  {r['rule']}  speed {r['speed']}  mass {r['mass']}  seed {r['seed']}")
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"settle": a.settle, "hold": a.hold, "seeds": SEEDS, "grid": res}, fh, indent=1)


if __name__ == "__main__":
    main()
