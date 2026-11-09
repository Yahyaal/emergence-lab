"""E-54 resume after a power loss (22:19 CST, 2026-11-08; J-062). Two jumped soups had not reached T + 20,000:
5302 (T = 13,750; last snapshot 31,750) and 5402 (T = 22,250; last snapshot 32,250). Each continues from its
last saved snapshot with a fresh random stream (seed + 2000), as E-54 continued the E-50 soups, and saves the
same snapshots (every 2,000 rounds after T) and per-soup record runs/e54/<seed>.json. The analysis uses only the
snapshots. Deviation from the pre-registration: the rounds after the snapshot differ from an uninterrupted run.

    python scripts/bff_long_resume.py
"""
from __future__ import annotations

import json
import time
from multiprocessing import Pool

import numpy as np

from emergence.programs import bff as B
from bff_long import AFTER, EVERY, N, RUN, SNAP

SPECS = [(5302, 13750, 31750), (5402, 22250, 32250)]


def job(spec):
    seed, T, start = spec
    out = RUN / f"{seed}.json"
    if out.exists():
        return json.loads(out.read_text())
    t0 = time.time()
    soup = B.Soup(n=N, seed=seed + 2000, programs=np.load(RUN / f"{seed}-{start}.npy"))
    soup.epochs = start
    old = [json.loads(l) for l in open("runs/e54.log") if l.startswith('{"seed": %d,' % seed)]
    series = [{k: r[k] for k in ("epoch", "hoe", "steps_per_pair")} for r in old if r["epoch"] <= start]
    while soup.epochs < T + AFTER:
        st = soup.epoch()
        e = soup.epochs
        if e % EVERY == 0:
            series.append({"epoch": e, "hoe": round(B.high_order_entropy(soup.programs), 3),
                           "steps_per_pair": round(st / (N / 2), 1)})
            if e % 2000 == 0:
                print(json.dumps({"seed": seed, "T": T} | series[-1] | {"sec": round(time.time() - t0)}), flush=True)
        if (e - T) % SNAP == 0:
            np.save(RUN / f"{seed}-{e}.npy", soup.programs)
    res = {"seed": seed, "continued_from": None, "resumed_from": start, "resume_seed": seed + 2000, "T": T,
           "jumped": True, "end": soup.epochs, "series": series, "series_note": "before the resume: 2000-round log "
           "checkpoints only (the 250-round series was lost in the power cut)", "sec": round(time.time() - t0)}
    out.write_text(json.dumps(res))
    print(json.dumps({"done": seed, "T": T, "end": soup.epochs, "sec": res["sec"]}), flush=True)
    return res


if __name__ == "__main__":
    with Pool(2) as p:
        p.map(job, SPECS, chunksize=1)
    print("=== E54 RESUME DONE", flush=True)
