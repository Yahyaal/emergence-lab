"""Glider population dynamics in large Lenia worlds (E-15, descriptive; J-014).

E-13 showed that smooth starts in glider-viable rules first produce several gliders, which
then disappear until at most one is left in a 128x128 world. Here: larger worlds, longer
runs, and a census of glider-like objects over time, to see how gliders are lost (decay,
collisions) and whether a NEW glider ever appears after the initial collapse (a "birth",
e.g. from a collision). Births are candidates only: frames around each one are saved for
inspection and must be checked by eye and by the isolation test before any claim.

Glider-like object: mass within [GL_MIN, GL_MAX] (the E-13a/E-13 gliders have mass 64-78)
and centroid moved >= 3 cells since the previous census (10 steps; gliders move ~6).

Usage:
    python scripts/glider_population.py --out docs/data/experiments/2026-11-07-e15-glider-population.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image

from emergence.engine import Universe, UniverseSpec
from emergence.observatory import continuous as C
from emergence.physics import parse_rule

GL_MIN, GL_MAX = 55.0, 95.0
EVERY = 10
RULES = ["LENIA/R13/T10/m0.150/s0.0150/b1", "LENIA/R13/T10/m0.140/s0.0140/b1", "LENIA/R13/T10/m0.160/s0.0160/b1"]


def gliders(prev: list[dict], cur: list[dict], shape) -> list[dict]:
    out = []
    for o in cur:
        if not GL_MIN <= o["mass"] <= GL_MAX or not prev:
            continue
        d = min(np.hypot(*C._torus_delta(p["c"], o["c"], shape)) for p in prev)
        if 3.0 <= d <= 12.0:
            out.append(o)
    return out


def run(args) -> dict:
    rule, seed, size, steps, ell, density, frames_dir = args
    spec = UniverseSpec(parse_rule(rule).to_dict(), seed, size, size, density, init={"kind": "smooth", "ell": ell})
    u = Universe.from_spec(spec)
    prev_objs = C.objects(u.state)
    series, events, history = [], [], []
    last_n = 0
    for t in range(EVERY, steps + 1, EVERY):
        u.step(EVERY)
        objs = C.objects(u.state)
        g = gliders(prev_objs, objs, u.state.shape)
        n = len(g)
        series.append({"t": t, "gliders": n, "objects": len(objs), "mass": round(float(u.state.sum()) / 255, 1)})
        history.append(u.state.copy())
        history = history[-6:]
        if t > 500 and n > last_n:
            ev = {"t": t, "type": "gain", "from": last_n, "to": n}
            if frames_dir:
                strip = np.concatenate(history, 1)
                name = f"{rule.split('/')[3]}-{seed}-t{t}.png"
                Image.fromarray(strip).save(Path(frames_dir) / name)
                ev["frames"] = name
            events.append(ev)
        elif n < last_n:
            events.append({"t": t, "type": "loss", "from": last_n, "to": n})
        last_n = n
        prev_objs = objs
    return {"rule": rule, "seed": seed, "size": size, "steps": steps, "ell": ell, "density": density,
            "series": series, "events": events}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=384)
    ap.add_argument("--steps", type=int, default=5000)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--ell", type=float, default=3.0)
    ap.add_argument("--density", type=float, default=0.10)
    ap.add_argument("--frames", default="runs/e15-frames")
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    Path(a.frames).mkdir(parents=True, exist_ok=True)
    jobs = [(r, 15_000 + s, a.size, a.steps, a.ell, a.density, a.frames) for r in RULES for s in range(a.seeds)]
    with Pool(a.workers or None) as p:
        res = p.map(run, jobs, chunksize=1)
    for r in res:
        g = [s["gliders"] for s in r["series"]]
        gains = [e for e in r["events"] if e["type"] == "gain"]
        print(f"{r['rule']} seed {r['seed']}: gliders max {max(g)} at t={r['series'][int(np.argmax(g))]['t']}, "
              f"t=1000: {g[99]}, end: {g[-1]}; late gains (t>500): {[(e['t'], e['from'], e['to']) for e in gains]}")
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"glider_mass": [GL_MIN, GL_MAX], "every": EVERY, "runs": res}, fh)


if __name__ == "__main__":
    main()
