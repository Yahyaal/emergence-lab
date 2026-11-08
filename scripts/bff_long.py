"""E-54 run phase: 2^16-program BFF soups run 20,000 rounds past their jump (docs/data/e54-preregistration.md).

New soups (seeds 5400-5411) run up to 24,000 rounds waiting for the jump (D-045: HOE >= 1.0 at 3 consecutive
checkpoints; T = the first of them); the three soups that jumped in E-50 (5301, 5302, 5308) continue from
their saved snapshots with fresh random streams. After the jump every soup runs to T + 20,000 and is saved
every 2,000 rounds to runs/e54/<seed>-<T+dt>.npy. Per-soup records in runs/e54/<seed>.json (resumable).

    python scripts/bff_long.py --workers 11
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from emergence.programs import bff as B

RUN = Path("runs/e54")
N, WAIT, AFTER, EVERY, SNAP, THRESH, PERSIST = 2 ** 16, 24000, 20000, 250, 2000, 1.0, 3
# E-50 soups that jumped: (seed, snapshot epoch, jump epoch T)
CONTINUE = [(5301, 22750, 21750), (5302, 14750, 13750), (5308, 12750, 12500)]


def job(spec: tuple) -> dict:
    seed, start, T = spec
    out_path = RUN / f"{seed}.json"
    if out_path.exists():
        return json.loads(out_path.read_text())
    t0 = time.time()
    if start:
        soup = B.Soup(n=N, seed=seed + 1000, programs=np.load(f"runs/e50/{N}-{seed}-{start}.npy"))
        soup.epochs = start
    else:
        soup = B.Soup(n=N, seed=seed)
    series, run = [], 0
    while True:
        st = soup.epoch()
        e = soup.epochs
        if e % EVERY == 0:
            hoe = B.high_order_entropy(soup.programs)
            series.append({"epoch": e, "hoe": round(hoe, 3), "steps_per_pair": round(st / (N / 2), 1)})
            if T is None:
                run = run + 1 if hoe >= THRESH else 0
                if run == PERSIST:
                    T = e - EVERY * (PERSIST - 1)
            if e % 2000 == 0:
                print(json.dumps({"seed": seed, "T": T} | series[-1] | {"sec": round(time.time() - t0)}), flush=True)
        if T is not None and e > T and (e - T) % SNAP == 0:
            np.save(RUN / f"{seed}-{e}.npy", soup.programs)
        if (T is None and e >= WAIT) or (T is not None and e >= T + AFTER):
            break
    res = {"seed": seed, "continued_from": start or None, "T": T, "jumped": T is not None, "end": soup.epochs,
           "series": series, "sec": round(time.time() - t0)}
    out_path.write_text(json.dumps(res))
    print(json.dumps({"done": seed, "T": T, "end": soup.epochs, "sec": res["sec"]}), flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    a = ap.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    specs = CONTINUE + [(s, 0, None) for s in range(5400, 5412)]
    with Pool(a.workers) as pool:
        res = pool.map(job, specs, chunksize=1)
    print(json.dumps({"jumped": [r["seed"] for r in res if r["jumped"]], "T": {r["seed"]: r["T"] for r in res}}))
    print("=== E54 RUN DONE", flush=True)


if __name__ == "__main__":
    main()
