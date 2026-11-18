"""E-82 emergence pilot (exploratory, J-099): do replicators arise from random code under BFF-X (scripts/bffx.py), and
do parasites appear? Pilot seeds only.

Census every EVERY epochs on the 40 most common distinct programs:
  copier     copies itself into 4 of 4 random 128-byte partners with random libraries (bffx.is_copier)
  parasite?  not a copier, never copied alone (4 random partner/library pairs), and copied in >= 3 of 4 runs when
             it runs first with the soup's commonest copier as the borrowed code (library in neighbour mode; partner
             in snapshot mode). Candidates only: the full detector is scripts/bffx_assay.parasite_test.
Byte shares of the families (bffx.members) of the first 10 copiers and of the parasite candidates.

    PYTHONPATH=.:scripts python scripts/e82_pilot.py --libmodes neighbour,snapshot,none --seeds 9501-9505 \
        --epochs 4000 --workers 11 --out runs/e82/pilot/out.json
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
import bffx as X  # noqa: E402

EVERY, TOPK = 100, 40


def classify(s: X.Soup, key: int) -> dict:
    top = X.top_distinct(s, TOPK)
    progs = [(np.frombuffer(b, np.uint8).copy(), c) for b, c in top]
    cop = [i for i, (x, _) in enumerate(progs) if X.is_copier(x, key * 1000 + i, libmode=s.libmode)]
    par = []
    if cop and s.libmode in ("neighbour", "snapshot"):
        host = progs[cop[0]][0]
        for i, (x, _) in enumerate(progs):
            if i in cop:
                continue
            kw = {"host_c": host} if s.libmode == "neighbour" else {"host_b": host}
            if X.screen(x, key * 1000 + 500 + i, 4, libmode=s.libmode)[0] > 0:
                continue
            if X.screen(x, key * 1000 + 700 + i, 4, libmode=s.libmode, **kw)[0] >= 3:
                par.append(i)

    def share(idx):
        fam = np.zeros(s.n, bool)
        for i in idx[:10]:
            fam |= X.members(s.buf, s.lens, progs[i][0])
        return round(float(s.lens[fam].sum() / s.lens.sum()), 4)

    return {"epoch": s.epochs, "n": s.n, "mean_len": round(float(s.lens.mean()), 2),
            "steps_pair": round(s.last_steps / max(1, s.n // 2), 1),
            "copiers": [(progs[i][0].tobytes().hex(), progs[i][1]) for i in cop[:10]],
            "parasites": [(progs[i][0].tobytes().hex(), progs[i][1]) for i in par[:10]],
            "cop_share": share(cop), "par_share": share(par), "ncop": len(cop), "npar": len(par)}


def job(arg):
    libmode, seed, epochs, outdir = arg
    path = Path(outdir) / f"{libmode}-{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    s = X.Soup(rng=np.random.default_rng([82, seed]), libmode=libmode)
    traj = []
    while s.epochs <= epochs:
        if s.epochs % EVERY == 0:
            traj.append(classify(s, seed * 100003 + s.epochs))
        s.epoch()
    np.savez_compressed(Path(outdir) / f"{libmode}-{seed}-final.npz", buf=s.buf, lens=s.lens)
    res = {"libmode": libmode, "seed": seed, "traj": traj, "seconds": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--libmodes", default="neighbour,snapshot,none")
    ap.add_argument("--seeds", default="9501-9505")
    ap.add_argument("--epochs", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split("-"))
    outdir = Path(a.out).parent
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = [(m, sd, a.epochs, str(outdir)) for sd in range(lo, hi + 1) for m in a.libmodes.split(",")]
    with Pool(a.workers) as p:
        res = []
        for r in p.imap_unordered(job, jobs):
            first = next((t["epoch"] for t in r["traj"] if t["cop_share"] >= 0.25), None)
            pmax = max(t["par_share"] for t in r["traj"])
            print(f"{r['libmode']:9s} {r['seed']} take-over {first} max parasite share {pmax} "
                  f"final cop {r['traj'][-1]['cop_share']} par {r['traj'][-1]['par_share']} "
                  f"len {r['traj'][-1]['mean_len']} {r['seconds']}s", flush=True)
            res.append(r)
    Path(a.out).write_text(json.dumps(res))
    print("=== SENTINEL e82 pilot")


if __name__ == "__main__":
    main()
