"""E-21: how do double gliders arise? (pre-registered, docs/data/e21-preregistration.md)

Runs smooth-start worlds, records every 10 steps the number of glider-sized (mass 55-95) and
double-sized (120-170) objects, verifies the final movers alone for 1000 steps, and classifies
the origin of each double glider as fusion / direct / unclear.

Usage: python scripts/double_glider_trace.py --out docs/data/experiments/2026-11-07-e21-double-gliders.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from emergence.engine import Universe, UniverseSpec
from emergence.observatory import continuous as C
from emergence.physics import parse_rule

ROOT_PANEL = "docs/data/rule-panel-e13.txt"


def alone_1000(phys, state, o) -> bool:
    a = C.isolate(state, o)
    rr, cc = np.nonzero(a)
    sub = a[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    w = np.zeros((256, 256), a.dtype)
    w[128 - sub.shape[0] // 2:128 - sub.shape[0] // 2 + sub.shape[0],
      128 - sub.shape[1] // 2:128 - sub.shape[1] // 2 + sub.shape[1]] = sub
    m0, c0 = max(C.objects(w), key=lambda x: x["mass"])["mass"], max(C.objects(w), key=lambda x: x["mass"])["c"]
    net = np.zeros(2)
    for _ in range(40):
        for _ in range(25):
            w = phys.step(w)
        ob = C.objects(w)
        if len(ob) != 1 or not 1 / C.MASS_TOL <= ob[0]["mass"] / m0 <= C.MASS_TOL:
            return False
        net += C._torus_delta(c0, ob[0]["c"], w.shape)
        c0 = ob[0]["c"]
    return bool(np.hypot(*net) >= C.MIN_TRAVEL)


def classify(series: list[tuple[int, int, int]]) -> tuple[str, int | None]:
    """t_d = start of the FINAL uninterrupted run of double-sized objects (the double that
    persists to the end); early double-sized lumps of the smooth start do not count."""
    if not series or series[-1][2] < 1:
        return "none", None
    i = len(series) - 1
    while i > 0 and series[i - 1][2] >= 1:
        i -= 1
    td = series[i][0]
    if td <= 100:
        return "direct", td
    before = [(t, g) for t, g, d in series if td - 100 <= t < td]
    g_before = min((g for _, g in before), default=0)
    g_at = [g for t, g, d in series if td - 30 <= t <= td + 30]
    if g_before >= 2 and g_at and max(g_at) - min(g_at) >= 2:
        return "fusion", td
    return "unclear", td


def run(args) -> dict:
    rule, seed = args
    phys = parse_rule(rule)
    u = Universe.from_spec(UniverseSpec(phys.to_dict(), seed, 128, 128, 0.10, init={"kind": "smooth", "ell": 3.0}))
    series = []
    for t in range(0, 2001, 10):
        objs = C.objects(u.state)
        series.append((t, sum(55 <= o["mass"] <= 95 for o in objs), sum(120 <= o["mass"] <= 170 for o in objs)))
        if t < 2000:
            u.step(10)
    final = C.objects(u.state)
    doubles = [o for o in final if 120 <= o["mass"] <= 170 and C.self_propelled(phys, u.state, o)]
    singles = [o for o in final if 55 <= o["mass"] <= 95 and C.self_propelled(phys, u.state, o)]
    d_ok = sum(alone_1000(phys, u.state, o) for o in doubles)
    s_ok = sum(alone_1000(phys, u.state, o) for o in singles)
    origin, td = classify(series) if d_ok else ("none", None)
    return {"rule": rule, "seed": seed, "verified_doubles": d_ok, "verified_singles": s_ok,
            "origin": origin, "t_double": td, "series": series}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=40)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    rules = [r.strip() for r in open(ROOT_PANEL) if r.strip()]
    rng = np.random.default_rng(21)
    jobs = [(r, int(s)) for r in rules for s in rng.integers(0, 2**62, size=a.seeds)]
    with Pool(a.workers or None) as p:
        res = p.map(run, jobs, chunksize=1)
    from collections import Counter
    print("worlds:", len(res), "| with verified double glider:", sum(r["verified_doubles"] > 0 for r in res),
          "| origins:", dict(Counter(r["origin"] for r in res if r["verified_doubles"])),
          "| with verified single glider(s):", sum(r["verified_singles"] > 0 for r in res))
    if a.out:
        json.dump({"runs": res}, open(a.out, "w"))


if __name__ == "__main__":
    main()
