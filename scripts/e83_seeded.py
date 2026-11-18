"""E-83 groundwork (J-101): the seeded positive arm. Random code (2^20 bytes) plus designed plain hosts S (the 11-byte sham
host, `bffxr_assay.sham_host`), a few designed resistant hosts R (`bffx_assay.resistant_host(1)`, 11 bytes, the same
length) and designed 4-byte parasites P, mutation on, in a random order. Questions: does R spread at S's expense, do
key-matched parasites (first byte 1) appear and spread on R, and does the E-83 sampler plus the time-shift statistic
see it (RQ > 0; RQ < 0 with the time labels reversed)? Arms: deme64 (BFF-XR, the E-83 geometry) and mixed (E-82's bffx.Soup).

    PYTHONPATH=.:scripts python scripts/e83_seeded.py --seeds 9851-9854 --epochs 2000 --workers 8
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
import bffx_assay as A  # noqa: E402
import bffxr as R_  # noqa: E402
import bffxr_assay as RA  # noqa: E402

OUT = Path("runs/e83/seeded")
SHARES = {"S": 0.10, "R": 0.01, "P": 0.05}
TRACK = {"H": X.hand_copier(6), "S": RA.sham_host(), "R": A.resistant_host(1, 11), "P": A.parasite(4),
         "Pk": A.parasite(4, key=1)}


def key_share(s: X.Soup, key: int = 1, maxlen: int = 8) -> float:
    """Bytes of short programs (<= maxlen) whose first byte is `key` (key-matched parasites of any body), over W."""
    offs = np.cumsum(s.lens) - s.lens
    m = (s.buf[offs] == key) & (s.lens <= maxlen)
    return round(float(s.lens[m].sum() / s.lens.sum()), 5)


def run(arg) -> dict:
    seed, geo, epochs, samples, every = arg
    import e83_run as E
    progs = RA.start(seed, SHARES)
    s = RA.soup(progs, seed, geo, "neighbour", mutation=X.MUT)
    traj, smp, t0 = [], {}, time.time()
    while True:
        e = s.epochs
        if e % every == 0:
            traj.append({"epoch": e, **{k: RA.fam_bytes(s, x) for k, x in TRACK.items()}, "key1": key_share(s),
                         "mean_len": round(float(s.lens.mean()), 2)})
        if e in samples:
            smp[e] = E.sample(s, seed, samples.index(e) + 1)
            smp[e].pop("tests", None)
        if e >= epochs:
            break
        s.epoch()
    ks = sorted(smp)
    hist = [([np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in smp[k]["parasites"]],
             [np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in smp[k]["hosts"]]) for k in ks]
    ts = A.timeshift(hist, seed * 31 + 5, 32)
    rev = A.timeshift(hist[::-1], seed * 31 + 5, 32)
    return {"seed": seed, "geometry": geo, "traj": traj, "samples": smp, "RQ": ts["RQ"], "Q": ts["Q"],
            "RQ_reversed": rev["RQ"], "sec": round(time.time() - t0)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="9851-9854")
    ap.add_argument("--epochs", type=int, default=2000)
    ap.add_argument("--samples", default="100,500,2000")
    ap.add_argument("--geometries", default="deme64,mixed")
    ap.add_argument("--every", type=int, default=50)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tag", default="seeded")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    lo, hi = map(int, a.seeds.split("-"))
    samples = [int(x) for x in a.samples.split(",")]
    jobs = [(sd, g, a.epochs, samples, a.every) for g in a.geometries.split(",") for sd in range(lo, hi + 1)]
    with Pool(a.workers) as p:
        res = p.map(run, jobs)
    (OUT / f"{a.tag}.json").write_text(json.dumps(res, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    for r in res:
        print(r["geometry"], r["seed"], "RQ", r["RQ"], "reversed", r["RQ_reversed"], r["sec"], "s")
        for t in r["traj"][::max(1, len(r["traj"]) // 8)] + [r["traj"][-1]]:
            print("   ", t)
        for k, v in r["samples"].items():
            print("    sample", k, "hosts", [(bytes.fromhex(h), c) for h, c in v["hosts"]][:3], "paras",
                  [(bytes.fromhex(h), c) for h, c in v["parasites"]][:3])


if __name__ == "__main__":
    main()
