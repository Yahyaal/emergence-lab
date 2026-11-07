"""Where does the 'free activity' of rankable static-looking Lenia fields come from? (J-028)

For rules of the held-out cut-off check (scripts/lenia_static_fields.py --seed 8) that are not
quasi-static although >= 90% of their persistent objects are still, re-run the universe (96x96,
seed 1, 500 steps, last 100 frames as the observer sees them) and measure how far each freely
changing cell lies from the nearest still object: within the excluded margin + 3 more cells
(creeping edges just outside the margin) or further out (activity of its own).

Usage: python scripts/heldout_free_activity.py runs/heldout-uniform.json [...] --out X.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

from emergence.conditions import init_of
from emergence.engine import Universe, UniverseSpec
from emergence.observatory import continuous as C
from emergence.physics import Lenia


def where(args):
    rule, init, free = args
    u = Universe.from_spec(UniverseSpec(Lenia.parse(rule).to_dict(), 1, 96, 96, 0.35, init=init_of(init)))
    u.step(400)
    frames = []
    for _ in range(100):
        frames.append(u.state.copy())
        u.step()
    tracks, per = C.track(frames)
    still = [tr for tr in tracks if tr["length"] >= C.MIN_STILL_FRAMES and np.hypot(*tr["disp"]) < 1.0]
    mask = np.zeros(frames[0].shape, bool)
    for tr in still:
        for t, j in (tr["first"], tr["last"]):
            mask |= C.label_torus(frames[t] >= C.THRESHOLD)[0] == per[t][j]["label"]
    dist = ndimage.distance_transform_edt(~np.tile(mask, (3, 3)))[96:192, 96:192]  # torus distance
    st = np.stack(frames).astype(np.int16)
    changed = (np.abs(np.diff(st, axis=0)) > C.VALUE_TOL).sum(0)
    free = dist > C.STILL_MARGIN
    tot = changed[free].sum()
    near = changed[free & (dist <= C.STILL_MARGIN + 3)].sum()
    lone = [tr for tr in tracks if tr["length"] < C.MIN_STILL_FRAMES]
    return {"rule": rule, "init": init, "free_activity": free, "still_objects": len(still),
            "free_changes_within_3_cells_of_margin": round(float(near / max(tot, 1)), 3),
            "short_tracks_lt_10_frames": len(lone)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args()
    jobs = []
    for f in a.files:
        d = json.load(open(f))["part2_random_rules"]
        for r in d["per_rule"]:
            w = r["new"]
            if (w["class"] not in ("extinct", "chaotic") and not w["self_propelled"] and not w["quasi_static"]
                    and w["persistent"] >= 5 and w["still"] >= 0.9 * w["persistent"]):
                jobs.append((r["rule"], d["init"], w["free_activity"]))
    with Pool() as p:
        res = p.map(where, jobs)
    for r, (_, _, fa) in zip(res, jobs):
        r["free_activity"] = fa
        print(r)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
