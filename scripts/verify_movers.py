"""Re-isolate every self-propelled structure in a conditions/explore database and test that
it survives 1000 steps alone (mass within the tracker's tolerance, one object), as the
E-13/E-14/E-17/E-18 pre-registrations require. Also measures speed and turning.

Usage: python scripts/verify_movers.py runs/e18.db 1 [2 ...] --out runs/e18-verified.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from emergence.engine import Universe, UniverseSpec
from emergence.observatory import continuous as C
from emergence.storage import Store


def verify(args):
    db, uid = args
    u = Store(db).universe(uid)
    w = Universe.from_spec(UniverseSpec.from_dict(u["spec"]))
    ph = w.physics
    w.step(u["steps"] - 100)
    fr = []
    for _ in range(100):
        fr.append(w.state.copy())
        w.step()
    tracks, per = C.track(fr)
    out = []
    for t in tracks:
        disp = np.hypot(*t["disp"])
        if t["length"] < 80 or disp < C.MIN_TRAVEL or disp < 0.5 * max(t["path"], 1e-9):
            continue
        tt, j = t["last"]
        o = per[tt][j]
        if not C.self_propelled(ph, fr[tt], o):
            continue
        alone = C.isolate(fr[tt], o)
        rr, cc = np.nonzero(alone)
        sub = alone[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
        world = np.zeros((256, 256), alone.dtype)
        world[128 - sub.shape[0] // 2:128 - sub.shape[0] // 2 + sub.shape[0],
              128 - sub.shape[1] // 2:128 - sub.shape[1] // 2 + sub.shape[1]] = sub
        o0 = max(C.objects(world), key=lambda x: x["mass"])
        m0, c, net, path, ok, legs = o0["mass"], o0["c"], np.zeros(2), 0.0, True, []
        for _ in range(40):
            for _ in range(25):
                world = ph.step(world)
            obs = C.objects(world)
            if len(obs) != 1 or not (1 / C.MASS_TOL <= obs[0]["mass"] / m0 <= C.MASS_TOL):
                ok = False
                break
            d = C._torus_delta(c, obs[0]["c"], world.shape)
            net += d
            path += float(np.hypot(*d))
            legs.append(d)
            c = obs[0]["c"]
        turn = None
        if ok and len(legs) > 2:
            L = np.array(legs)
            cos = [float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)) for a, b in zip(L[:-1], L[1:])]
            turn = round(float(np.mean(cos)), 2)
        out.append({"mass": round(m0, 1), "survives_1000": ok, "speed": round(path / 1000, 3) if ok else None,
                    "net_over_path": round(float(np.hypot(*net)) / max(path, 1e-9), 2) if ok else None,
                    "direction_persistence": turn})
    return {"uid": uid, "rule": u["rule"], "init": (u.get("aggregate") or {}).get("init"), "movers": out}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("experiments", type=int, nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--workers", type=int, default=0)
    a = ap.parse_args()
    st = Store(a.db)
    uids = [u["id"] for e in a.experiments for u in st.universes(e)
            if (u["metrics"].get("self_propelled_shapes") or 0) > 0]
    with Pool(a.workers or None) as p:
        res = p.map(verify, [(a.db, uid) for uid in uids], chunksize=1)
    n = sum(len(r["movers"]) for r in res)
    ok = sum(m["survives_1000"] for r in res for m in r["movers"])
    print(f"{len(uids)} universes with self-propelled structures; {n} movers re-isolated, {ok} survive 1000 steps alone")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
