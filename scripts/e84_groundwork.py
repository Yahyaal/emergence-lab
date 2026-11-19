"""E-84 groundwork (J-103, D-076, D-077): fixed-length BFF-X on demes (scripts/bffxf.py). Exploratory; pilot seeds only.

  --pilot    emergence from random code: seeds x arms (deme64/mixed x neighbour/none/live), census every 50 epochs
             (hosts among the 40 commonest programs, host share, resistance of each host to the inert parasite),
             snapshots every 1,000 epochs.
  --compete  the decisive races (controls a and b): R against S and R against H, deme64 and mixed, with and without
             borrowing, with and without mutation.
  --seeded   the seeded arm: designed H, R, P in random code under deme64, mutation on; time-shift statistic on the
             E-84 sampler at fixed epochs.

    PYTHONPATH=.:scripts python scripts/e84_groundwork.py --pilot --seeds 9801-9805 --epochs 10000
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bffxf as F  # noqa: E402
import bffxf_assay as FA  # noqa: E402

OUT = Path("runs/e84")


def census(s, key: int) -> dict:
    top = F.top_distinct(s, 40)
    hs = [(b, c) for i, (b, c) in enumerate(top) if F.is_copier(np.frombuffer(b, np.uint8), key * 1000 + i)]
    share = 0.0
    if hs:
        fam = np.zeros(s.n, bool)
        for b, _ in hs[:10]:
            fam |= F.members(s.buf, s.lens, np.frombuffer(b, np.uint8))
        share = float(fam.mean())
    P = FA.parasite()
    res = []
    for b, c in hs[:10]:
        h = np.frombuffer(b, np.uint8)
        res.append({"hex": b.hex(), "count": c, "q": round(FA.q_pair(P, h, key + 7, 16), 3),
                    "w": round(FA.w_pair(P, h, key + 9, 16), 3)})
    return {"epoch": s.epochs, "share": round(share, 4), "nhost": len(hs), "hosts": res,
            "steps_pair": round(s.last_steps / max(1, s.n // 2), 1), "top1": top[0][1]}


def pilot_job(arg) -> dict:
    seed, geo, lm, epochs = arg
    d = OUT / "pilot"
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{seed}-{geo}-{lm}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    s = F.make(geo, rng=np.random.default_rng([84, seed]), libmode=lm)
    traj = []
    while s.epochs <= epochs:
        if s.epochs % 50 == 0:
            traj.append(census(s, seed * 100003 + s.epochs))
        if s.epochs % 1000 == 0 and s.epochs > 0:
            np.savez_compressed(d / f"{seed}-{geo}-{lm}-{s.epochs}.npz", buf=s.buf, lens=s.lens)
        if s.epochs == epochs:
            break
        s.epoch()
    first = next((t["epoch"] for t in traj if t["share"] >= 0.05), None)
    res = {"seed": seed, "geometry": geo, "libmode": lm, "first_share05": first, "traj": traj,
           "seconds": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    return res


def snap_job(path: str) -> dict:
    """Census of a pilot snapshot: hosts, host share, hosts refusing the inert parasite; the E-84 sampler (verified
    parasites among the 40 commonest non-hosts)."""
    f = Path(path)
    seed, geo, lm, ep = f.stem.split("-")
    d = np.load(f)
    s = F.make(geo, buf=d["buf"], lens=d["lens"], libmode=lm)
    s.epochs = int(ep)
    c = census(s, int(seed) * 7 + int(ep))
    smp = FA.sample(s, int(seed), int(ep), exp=842) if lm == "neighbour" else None
    return {"seed": int(seed), "geometry": geo, "libmode": lm, "epoch": int(ep), "share": c["share"],
            "nhost": c["nhost"], "refusing": sum(h["q"] < 0.5 for h in c["hosts"]),
            "parasites": len(smp["parasites"]) if smp else None, "verdicts": smp["verdicts"] if smp else None,
            "distinct": len(set(map(bytes, s.buf.reshape(-1, F.L))))}


def compete_job(arg) -> dict:
    return FA.compete(**arg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--compete", action="store_true")
    ap.add_argument("--seeded", action="store_true")
    ap.add_argument("--snapshots", action="store_true")
    ap.add_argument("--export", default=None)
    ap.add_argument("--seeds", default="9801-9805")
    ap.add_argument("--arms", default="deme64:neighbour,mixed:neighbour,mixed:live,deme64:none")
    ap.add_argument("--epochs", type=int, default=10000)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    OUT.mkdir(parents=True, exist_ok=True)
    if a.pilot:
        arms = [tuple(x.split(":")) for x in a.arms.split(",")]
        jobs = [(sd, g, lm, a.epochs) for sd in seeds for g, lm in arms]
        with Pool(a.workers) as p:
            for r in p.imap_unordered(pilot_job, jobs):
                last = r["traj"][-1]
                print(f"{r['seed']} {r['geometry']} {r['libmode']}: first share>=0.05 at {r['first_share05']}, "
                      f"final share {last['share']} nhost {last['nhost']} "
                      f"resistant {[h['q'] for h in last['hosts'] if h['q'] < 0.5]} {r['seconds']}s", flush=True)
    if a.compete:
        jobs = []
        for sd in seeds:
            for geo in ("deme64", "mixed"):
                for lm in ("neighbour", "none"):
                    jobs.append(dict(seed=sd, geometry=geo, libmode=lm, shares={"R": 0.1, "S": 0.1, "P": 0.05},
                                     focal="R", rival="S"))
                    jobs.append(dict(seed=sd, geometry=geo, libmode=lm, shares={"R": 0.1, "H": 0.1},
                                     focal="R", rival="H", mutation=F.MUT, horizons=(25, 50, 100, 200, 400)))
        with Pool(a.workers) as p:
            rr = p.map(compete_job, jobs)
        Path(a.out or OUT / "compete.json").write_text(json.dumps(rr))
        for r in rr:
            print(r["seed"], r["geometry"], r["libmode"], r["focal"], "vs", r["rival"], r["scores"], flush=True)
    if a.snapshots:
        files = sorted(str(f) for f in (OUT / "pilot").glob("*.npz"))
        with Pool(a.workers) as p:
            rr = p.map(snap_job, files)
        (OUT / "snapshots.json").write_text(json.dumps(rr))
        for r in sorted(rr, key=lambda r: (r["geometry"], r["libmode"], r["seed"], r["epoch"])):
            print(r, flush=True)
    if a.export:
        import subprocess
        ex = {"experiment": "E-84 groundwork", "status": "decisive control (a) failed; not pre-registered",
              "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
              "controls": [(n, bool(o), d) for n, o, d in FA.controls()]}
        for k in ("compete", "extra", "snapshots"):
            fp = OUT / f"{k}.json"
            if fp.exists():
                rr = json.loads(fp.read_text())
                for r in rr:
                    r.pop("traj", None) if k == "snapshots" else None
                ex[k] = rr
        Path(a.export).write_text(json.dumps(ex, indent=1))
    if a.seeded:
        with Pool(a.workers) as p:
            rr = p.map(FA.seeded_job, [(sd, g) for sd in seeds for g in ("deme64", "mixed")])
        Path(a.out or OUT / "seeded.json").write_text(json.dumps(rr))
        for r in rr:
            print(r["seed"], r["geometry"], r["RQ"], r["RQ_w"], r["bytes"], flush=True)


if __name__ == "__main__":
    main()
