"""E-23: can a double glider and a glider fuse into a triple? (docs/data/e23-preregistration.md)

Usage: python scripts/chain_scan.py --out docs/data/experiments/2026-11-07-e23-chain.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from emergence.observatory import continuous as C
from emergence.physics import parse_rule

RULE = "LENIA/R13/T10/m0.150/s0.0150/b1"
SIDE = 224


def crop(state, o):
    a = C.isolate(state, o)
    rr, cc = np.nonzero(a)
    return a[rr.min():rr.max() + 1, cc.min():cc.max() + 1]


def place(w, p, cy, cx):
    ys = (np.arange(p.shape[0]) + int(round(cy)) - p.shape[0] // 2) % w.shape[0]
    xs = (np.arange(p.shape[1]) + int(round(cx)) - p.shape[1] // 2) % w.shape[1]
    w[np.ix_(ys, xs)] = np.maximum(w[np.ix_(ys, xs)], p)


def patterns():
    phys = parse_rule(RULE)
    g = crop(C.emergent_glider(phys), max(C.objects(C.emergent_glider(phys)), key=lambda x: x["mass"]))
    w = np.zeros((192, 192), np.uint8)
    place(w, g, 96, 51)
    place(w, g.T, 51, 94)
    for _ in range(1000):
        w = phys.step(w)
    o = max(C.objects(w), key=lambda x: x["mass"])
    dbl = crop(w, o)
    # direction of the double: measure over 50 steps alone
    t = np.zeros((192, 192), np.uint8)
    place(t, dbl, 96, 96)
    c0 = max(C.objects(t), key=lambda x: x["mass"])["c"]
    for _ in range(50):
        t = phys.step(t)
    v = C._torus_delta(c0, max(C.objects(t), key=lambda x: x["mass"])["c"], t.shape) / 50
    return g, dbl, v


def sym(p, k):
    q = np.rot90(p, k % 4)
    return np.fliplr(q) if k >= 4 else q


def run(args):
    k, off, phase, steps, g, dbl, v = args
    phys = parse_rule(RULE)
    s = sym(g, k)
    # velocity of the transformed glider
    t = np.zeros((128, 128), np.uint8)
    place(t, s, 64, 64)
    c0 = max(C.objects(t), key=lambda x: x["mass"])["c"]
    for _ in range(40):
        t = phys.step(t)
    vs = C._torus_delta(c0, max(C.objects(t), key=lambda x: x["mass"])["c"], t.shape) / 40
    for _ in range(phase):
        t = phys.step(t)
    s = crop(t, max(C.objects(t), key=lambda x: x["mass"]))
    # place so both would reach the meeting point M after ~T steps: start = M - T * velocity
    T = 90
    M = np.array([SIDE / 2, SIDE / 2])
    perp = np.array([-vs[1], vs[0]]) / (np.hypot(*vs) + 1e-9)
    w = np.zeros((SIDE, SIDE), np.uint8)
    place(w, dbl, *(M - T * v))
    place(w, s, *(M - T * vs + off * perp))
    for _ in range(steps):
        w = phys.step(w)
    objs = C.objects(w)
    total = float(w.sum()) / 255
    res = {"sym": k, "offset": off, "phase": phase, "total_mass": round(total, 1),
           "masses": sorted(round(o["mass"], 1) for o in objs), "triple": None}
    trip = [o for o in objs if 180 <= o["mass"] <= 240]
    if total <= 1000 and trip:
        o = trip[0]
        a = crop(w, o)
        z = np.zeros((256, 256), np.uint8)
        place(z, a, 128, 128)
        m0 = max(C.objects(z), key=lambda x: x["mass"])["mass"]
        c = max(C.objects(z), key=lambda x: x["mass"])["c"]
        net, ok = np.zeros(2), True
        for _ in range(40):
            for _ in range(25):
                z = phys.step(z)
            ob = C.objects(z)
            if len(ob) != 1 or not 1 / C.MASS_TOL <= ob[0]["mass"] / m0 <= C.MASS_TOL:
                ok = False
                break
            net += C._torus_delta(c, ob[0]["c"], z.shape)
            c = ob[0]["c"]
        res["triple"] = {"mass": round(m0, 1), "persists": ok, "net_1000": round(float(np.hypot(*net)), 1)}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--out")
    a = ap.parse_args()
    g, dbl, v = patterns()
    print("double glider mass %.1f, velocity %s" % (dbl.sum() / 255, np.round(v, 3)))
    jobs = [(k, off, ph, a.steps, g, dbl, v) for k in range(8) for off in range(-12, 13, 2) for ph in (0, 10, 20)]
    with Pool() as p:
        res = p.map(run, jobs, chunksize=2)
    from collections import Counter
    def cat(r):
        if r["total_mass"] > 1000:
            return "world filled"
        if r["triple"] and r["triple"]["persists"] and r["triple"]["net_1000"] >= 20:
            return "TRIPLE"
        m = r["masses"]
        return "+".join("double" if 120 <= x <= 170 else "single" if 55 <= x <= 95 else f"other{x:.0f}" for x in m) or "nothing"
    print(dict(Counter(cat(r) for r in res).most_common()))
    if a.out:
        json.dump({"double_velocity": v.tolist(), "runs": res}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
