"""E-27 follow-up: look at a birth-detector hit. Replays a stored world, re-runs the scan with
the same rng, and for each candidate that passed generation 1 saves a strip of its isolated
test world (t = 0 ... steps) and runs the test once more on a grandchild (generation 3).

Usage: python scripts/birth_inspect.py runs/e14.db 441 --out docs/assets/report/e27-441.png
"""
from __future__ import annotations

import argparse
import json

import numpy as np

from emergence.engine import Universe, UniverseSpec
from emergence.observatory import births as B
from emergence.storage import Store


def strip(ph, world, steps, n=9):
    frames, w = [], world
    every = steps // (n - 1)
    for t in range(steps + 1):
        if t % every == 0:
            frames.append(B.field(ph, w))
        if t < steps:
            w = ph.step(w)
    return frames


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("uid", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    u = Store(a.db).universe(a.uid)
    w = Universe.from_spec(UniverseSpec.from_dict(u["spec"]))
    ph = w.physics
    w.step(u["steps"] - 1)  # the state birth_scan.py scanned (last of its 100 frames)
    state = np.array(w.state)
    rng = np.random.default_rng(a.uid)
    res = B.scan(ph, state, rng)
    out = []
    objs = [o for o in B.find(ph, state) if o["mass"] >= 1]
    for r in res["results"]:
        if r["verdict"] not in ("reproducer", "one generation"):
            continue
        pm = r["parent_mass"]
        o = min(objs, key=lambda o: abs(o["mass"] - pm))
        w0 = B.alone(ph, state, o["mask"], B.CONTINUOUS["side"], 4)
        fr = strip(ph, w0, B.CONTINUOUS["steps"])
        # third generation: walk down the lineage twice more
        gens, cur = [], w0
        for g in range(3):
            p = max(B.find(ph, cur), key=lambda o: o["mass"])
            res_g = B.generation(ph, cur, p, B.CONTINUOUS["steps"], B.CONTINUOUS["every"])
            gens.append({k: v for k, v in res_g.items() if k not in ("snap", "series")} | {"parent_mass": round(p["mass"], 1)})
            if not res_g["ok"]:
                break
            copies, snapw = res_g["snap"][2], res_g["snap"][3]
            child = sorted(copies, key=lambda o: o["mass"])[len(copies) // 2]
            cur = B.alone(ph, snapw, child["mask"], B.CONTINUOUS["side"], 4)
        out.append({"verdict": r["verdict"], "parent_mass": pm, "generations": gens})
        print(json.dumps(out[-1]))
        if a.out:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, len(fr), figsize=(2 * len(fr), 2.3))
            for i, (x, f) in enumerate(zip(ax, fr)):
                x.imshow(f, cmap="magma", vmin=0, vmax=255)
                x.set_title(f"t={i * B.CONTINUOUS['steps'] // (len(fr) - 1)}", fontsize=8)
                x.axis("off")
            fig.suptitle(f"{u['rule']} ({u['spec'].get('init') or 'soup'}), one object alone, mass {pm}", fontsize=9)
            fig.tight_layout()
            fig.savefig(a.out.replace(".png", f"-{len(out)}.png"), dpi=90)
            plt.close(fig)


if __name__ == "__main__":
    main()
