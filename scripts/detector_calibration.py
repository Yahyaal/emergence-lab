"""E-25: calibrate the continuous mover detector for slow, turning movers (pre-registered,
docs/data/e25-preregistration.md).

Every stored universe is re-simulated; its last 100 frames are tracked as the observer does.
Every persistent track with net displacement >= MIN_TRAVEL (any straightness) is a candidate;
up to 12 per world (largest displacement first) are isolated with the 100-step test and the
extended SLOW test (300 steps), and every detection is checked against a 1000-step ground truth.

Usage: python scripts/detector_calibration.py --out runs/e25.json [--workers 8] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool

import numpy as np

from emergence.engine import Universe, UniverseSpec
from emergence.observatory import continuous as C
from emergence.storage import Store

POOLS = {  # pool -> (db, experiment ids)
    "slow_e18a": ("runs/e18.db", [1]), "slow_e18b": ("runs/e18.db", [2]),
    "glider_e14": ("runs/e14.db", [1, 2]),
    "neg_e19b": ("runs/e19.db", list(range(3, 13))),
    "neg_e12_random": ("runs/e12.db", [2]), "neg_e17_random": ("runs/e17.db", [2]),
}
VARIANTS = {"V0": (0.5, 100), "V1": (0.5, 300), "V2": (0.25, 300), "V3": (0.0, 300)}
MAX_TESTS = 6


def ground_truth(ph, state, obj) -> dict:
    alone = C.isolate(state, obj)
    rr, cc = np.nonzero(alone)
    sub = alone[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    world = np.zeros((256, 256), alone.dtype)
    world[128 - sub.shape[0] // 2:128 - sub.shape[0] // 2 + sub.shape[0],
          128 - sub.shape[1] // 2:128 - sub.shape[1] // 2 + sub.shape[1]] = sub
    o0 = max(C.objects(world), key=lambda x: x["mass"])
    m0, c, paths = o0["mass"], o0["c"], []
    for _ in range(40):
        for _ in range(25):
            world = ph.step(world)
        obs = C.objects(world)
        if len(obs) != 1 or not (1 / C.MASS_TOL <= obs[0]["mass"] / m0 <= C.MASS_TOL):
            return {"ok": False, "why": f"objects {len(obs)}" if len(obs) != 1 else "mass", "steps": 25 * (len(paths) + 1)}
        paths.append(float(np.hypot(*C._torus_delta(c, obs[0]["c"], world.shape))))
        c = obs[0]["c"]
    path, late = sum(paths), sum(paths[20:])
    return {"ok": path >= 20 and late >= 10, "why": "" if path >= 20 and late >= 10 else "static",
            "path": round(path, 1), "late_path": round(late, 1), "mass": round(m0, 1)}


def world(args):
    pool, db, uid = args
    u = Store(db).universe(uid)
    w = Universe.from_spec(UniverseSpec.from_dict(u["spec"]))
    ph = w.physics
    w.step(u["steps"] - 100)
    fr = []
    for _ in range(100):
        fr.append(w.state.copy())
        w.step()
    tracks, per = C.track(fr)
    cands = [t for t in tracks if t["length"] >= 0.8 * len(fr) and np.hypot(*t["disp"]) >= C.MIN_TRAVEL]
    cands = sorted(cands, key=lambda t: -np.hypot(*t["disp"]))[:12]
    out = []
    for t in cands:
        tt, j = t["last"]
        o = per[tt][j]
        net = float(np.hypot(*t["disp"]))
        c = {"straight": round(net / max(t["path"], 1e-9), 3), "net": round(net, 2), "mass": round(o["mass"], 1),
             "iso100": bool(C.self_propelled(ph, fr[tt], o, slow_steps=100)),
             "iso300": bool(C.self_propelled(ph, fr[tt], o, slow_steps=300))}
        if c["iso300"]:
            c["truth"] = ground_truth(ph, fr[tt], o)
        out.append(c)
    return {"pool": pool, "uid": uid, "rule": u["rule"], "init": (u["spec"].get("init") or {}).get("kind", "uniform"),
            "stored_self_propelled": (u["metrics"] or {}).get("self_propelled_shapes"), "cands": out}


def detect(w, straight, steps):
    """Variant verdict for one world: the observer tests the MAX_TESTS largest-displacement movers."""
    ms = [c for c in w["cands"] if c["straight"] >= straight][:MAX_TESTS]
    hits = [c for c in ms if c["iso100" if steps == 100 else "iso300"]]
    return hits


def summarise(worlds):
    res = {}
    for pool in POOLS:
        ws = [w for w in worlds if w["pool"] == pool]
        row = {"worlds": len(ws),  # V0 must reproduce the stored observer verdicts
               "V0_agrees_with_stored": sum(bool(detect(w, *VARIANTS["V0"])) == bool(w.get("stored_self_propelled")) for w in ws)}
        base = {w["uid"] for w in ws if detect(w, *VARIANTS["V0"])}
        for v, (s, n) in VARIANTS.items():
            det = [(w, detect(w, s, n)) for w in ws]
            det = [(w, h) for w, h in det if h]
            fp = [w["uid"] for w, h in det if not any(c.get("truth", {}).get("ok") for c in h)]
            row[v] = {"detected": len(det), "confirmed": len(det) - len(fp), "false_positive_worlds": fp,
                      "false_positives_among_new": [u for u in fp if u not in base],  # decision rule (amendment 1)
                      "new_vs_V0": len({w["uid"] for w, _ in det} - base),
                      "lost_vs_V0": len(base - {w["uid"] for w, _ in det})}
        res[pool] = row
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resummarise", help="recompute the summary of an earlier --out file")
    a = ap.parse_args()
    if a.resummarise:
        d = json.load(open(a.resummarise))
        d["summary"] = summarise(d["worlds"])
        print(json.dumps(d["summary"], indent=1))
        json.dump(d, open(a.out, "w"))
        return
    jobs = []
    for pool, (db, exps) in POOLS.items():
        s = Store(db)
        ids = [u["id"] for e in exps for u in s.universes(e)]
        jobs += [(pool, db, i) for i in (ids[:a.limit] if a.limit else ids)]
    t0 = time.time()
    with Pool(a.workers or None) as p:
        worlds = p.map(world, jobs, chunksize=4)
    summary = summarise(worlds)
    print(json.dumps(summary, indent=1))
    json.dump({"summary": summary, "seconds": round(time.time() - t0), "worlds": worlds}, open(a.out, "w"))


if __name__ == "__main__":
    main()
