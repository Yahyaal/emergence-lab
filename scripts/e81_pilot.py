"""E-81 groundwork, exploratory pilot (J-097): BFF-VL soups from random code (and seeded / control soups).

Logs every `--every` epochs: programs, mean and byte-weighted mean length, HOE, steps per pair, and a census of the
40 most common distinct programs (copy screen `bffvl.is_copier`, 4 random 128-byte partners): how many copy, the
shortest copier, and the byte share held by copiers' families. Snapshots (buf, lens) go to runs/e81/pilot/.

    PYTHONPATH=.:scripts python scripts/e81_pilot.py --seeds 9001-9006 --epochs 6000 --workers 6
    PYTHONPATH=.:scripts python scripts/e81_pilot.py --seeds 9101-9102 --mode noexec --epochs 6000
    PYTHONPATH=.:scripts python scripts/e81_pilot.py --seeds 9201-9204 --seeded 120 --epochs 4000
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import bffvl as V

OUT = Path("runs/e81/pilot")


def census(s: V.Soup, seed: int, k: int = 40) -> dict:
    progs = s.programs()
    top = Counter(map(bytes, progs)).most_common(k)
    cop = []
    for i, (b, c) in enumerate(top):
        x = np.frombuffer(b, np.uint8)
        if V.is_copier(x, seed * 1000 + i):
            cop.append((len(x), c, b))
    share = 0.0
    if cop:
        fam = np.zeros(s.n, bool)
        for L, c, b in cop[:10]:
            fam |= s.members(np.frombuffer(b, np.uint8))
        share = float(s.lens[fam].sum() / s.lens.sum())
    return {"copiers": len(cop), "shortest": min((c[0] for c in cop), default=None),
            "lens_copiers": sorted(c[0] for c in cop),
            "top": [(len(b), c) for b, c in top[:5]], "copier_share10": round(share, 3),
            "top_copier": cop[0][2].hex() if cop else None}


def job(arg):
    seed, mode, epochs, every, seeded, w = arg
    rng = np.random.default_rng(seed)
    s = V.Soup(w=w, rng=rng, mode=mode)
    if seeded:
        # Tierra-like seeded arm: the hand-written copier padded with random no-ops to `seeded` bytes replaces
        # 1/64 of the soup's programs (random ones)
        anc = V.hand_copier(seeded, rng, fill=None)
        progs = s.programs()
        idx = set(rng.choice(len(progs), max(1, len(progs) // 64), replace=False).tolist())
        progs = [anc.copy() if i in idx else p for i, p in enumerate(progs)]
        # keep the byte budget: drop random programs until the budget is back at w
        tot = sum(len(p) for p in progs)
        order = [i for i in rng.permutation(len(progs)) if i not in idx]
        drop = set()
        for i in order:
            if tot <= w:
                break
            drop.add(i)
            tot -= len(progs[i])
        progs = [p for i, p in enumerate(progs) if i not in drop]
        s = V.Soup.from_programs(progs, rng=rng, mode=mode)
    tag = f"{mode}-{'seed' + str(seeded) + '-' if seeded else ''}{seed}"
    log = OUT / f"{tag}.jsonl"
    t0 = time.time()
    with open(log, "w") as f:
        for e in range(epochs + 1):
            if e % every == 0:
                rec = {"epoch": e, "n": s.n, "mean_len": round(float(s.lens.mean()), 2),
                       "byte_mean_len": round(float((s.lens.astype(float) ** 2).sum() / s.lens.sum()), 2),
                       "hoe": round(V.hoe(s.buf), 3), "steps_pair": round(s.last_steps / max(1, s.n // 2), 1),
                       "sec": round(time.time() - t0, 1)}
                rec.update(census(s, seed * 100000 + e))
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if e % (every * 10) == 0 or e == epochs:
                    np.savez_compressed(OUT / f"{tag}-e{e}.npz", buf=s.buf, lens=s.lens)
            if e < epochs:
                s.epoch()
    return tag, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True, help="a-b or comma list")
    ap.add_argument("--mode", default="bff")
    ap.add_argument("--epochs", type=int, default=6000)
    ap.add_argument("--every", type=int, default=100)
    ap.add_argument("--seeded", type=int, default=0, help="seed with the hand copier padded to this length")
    ap.add_argument("--w", type=int, default=V.W)
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()
    seeds = (list(range(int(a.seeds.split("-")[0]), int(a.seeds.split("-")[1]) + 1)) if "-" in a.seeds
             else [int(x) for x in a.seeds.split(",")])
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(sd, a.mode, a.epochs, a.every, a.seeded, a.w) for sd in seeds]
    with Pool(a.workers) as p:
        for tag, sec in p.imap_unordered(job, jobs):
            print(tag, f"{sec:.0f}s", flush=True)
    print("E-81 PILOT DONE", flush=True)


if __name__ == "__main__":
    main()
