"""E-48: do later programs out-compete earlier ones from the same soup? (docs/data/e48-preregistration.md)

    python scripts/bff_time_races.py --workers 11 --out docs/data/experiments/2026-11-08-e48-time-races.json
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from multiprocessing import Pool

import numpy as np
from scipy.stats import binomtest

from emergence.observatory import program_selection as PS
from emergence.programs import bff as B

E47 = "docs/data/experiments/2026-11-08-e47-turnover.json"
K, EARLY, LATE, REPS = 6, 1000, 10000, 32


def same(p, q) -> bool:
    return bool((p == q).mean() >= 0.9 or (p == q[::-1]).mean() >= 0.9)


def sample(seed: int, epoch: int) -> list[np.ndarray]:
    P = np.load(f"runs/e47/{seed}-{epoch}.npy")
    out = []
    for prog, _ in B.top_programs(P, 400):
        x = np.frombuffer(prog, np.uint8).copy()
        if not any(same(x, y) for y in out):
            out.append(x)
        if len(out) == K:
            break
    return out


def pairs() -> list[dict]:
    out, skipped = [], 0
    for q in json.load(open(E47))["sequences"]:
        seed, t = q["seed"], q["species"][0]["first"]
        early, late = sample(seed, t + EARLY), sample(seed, t + LATE)
        for i, a in enumerate(early):
            for j, b in enumerate(late):
                if same(a, b):
                    skipped += 1
                    continue
                out.append({"kind": "cross", "seed": seed, "a": bytes(a).hex(), "b": bytes(b).hex(), "i": i, "j": j})
        for name, smp in (("same_early", early), ("same_late", late)):
            for i, j in combinations(range(len(smp)), 2):
                out.append({"kind": name, "seed": seed, "a": bytes(smp[i]).hex(), "b": bytes(smp[j]).hex(), "i": i, "j": j})
    print(f"{len(out)} pairs, {skipped} cross pairs skipped (same family)", flush=True)
    return out


def job(arg):
    k, p = arg
    h = lambda x: np.frombuffer(bytes.fromhex(x), np.uint8).copy()
    a, b = h(p["a"]), h(p["b"])
    r = PS.compete_families(a, b, np.random.default_rng([48, k]), reps=REPS, a_alt=[a[::-1]], b_alt=[b[::-1]])
    s = [v for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    return {"pair": k} | p | r | {"b_share": round(sum(v > 0 for v in s) / len(s), 3) if s else None, "n": len(s)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ps = pairs()
    with Pool(a.workers) as pool:
        res = []
        for n, r in enumerate(pool.imap_unordered(job, list(enumerate(ps))), 1):
            res.append(r)
            if n % 10 == 0:
                print(f"{n}/{len(ps)}", flush=True)
    res.sort(key=lambda r: r["pair"])
    summary = {}
    for kind in ("cross", "same_early", "same_late"):
        for seed in (None, 901, 5006, 5010):
            rr = [r for r in res if r["kind"] == kind and (seed is None or r["seed"] == seed) and r["n"] >= 8]
            ahead = sum(r["b_share"] > 0.5 for r in rr)
            w = sum(round(r["b_share"] * r["n"]) for r in rr)
            n = sum(r["n"] for r in rr)
            summary[f"{kind}/{seed or 'all'}"] = {
                "pairs": len(rr), "b_ahead": ahead,
                "sign_p": float(binomtest(ahead, len(rr), alternative="greater").pvalue) if rr else None,
                "pooled_b_share": round(w / n, 3) if n else None,
                "mean_abs_dev": round(float(np.mean([abs(r["b_share"] - 0.5) for r in rr])), 3) if rr else None}
    json.dump({"experiment": "E-48", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E48 DONE", flush=True)


if __name__ == "__main__":
    main()
