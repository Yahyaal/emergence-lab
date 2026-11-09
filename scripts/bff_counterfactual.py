"""E-56 (docs/data/e56-preregistration.md): BFF soups under the counterfactual rule (head1 starts at byte 64).
Do they evolve forward copiers? Per-soup records in runs/e56/<seed>.json (resumable).

    python scripts/bff_counterfactual.py --workers 4 --out docs/data/experiments/2026-11-08-e56-counterfactual-soups.json
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
import bff_kernels as K  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

RUN = Path("runs/e56")
N, WAIT, AFTER, EVERY, THRESH, PERSIST, H1 = 2 ** 16, 24000, 2000, 250, 1.0, 3, 64
SEEDS = range(5600, 5604)


class CounterfactualSoup(B.Soup):
    def epoch(self) -> int:
        pairs = self.rng.permutation(self.n).astype(np.int32)
        self.last_steps = int(K.lib().epoch_h(self.programs.ctypes.data, self.length, pairs.ctypes.data,
                                              self.n // 2, self.max_steps, H1))
        if self.mutation > 0:
            k = self.rng.binomial(self.programs.size, self.mutation)
            idx = self.rng.integers(0, self.programs.size, k)
            self.programs.reshape(-1)[idx] = self.rng.integers(0, 256, k, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps


def same(p, q) -> bool:
    return bool((p == q).mean() >= 0.9 or (p == q[::-1]).mean() >= 0.9)


def distinct_top(P: np.ndarray, m: int = 40) -> list[np.ndarray]:
    out = []
    for prog, _ in B.top_programs(P, 3000):
        x = np.frombuffer(prog, np.uint8).copy()
        if not any(same(x, y) for y in out):
            out.append(x)
        if len(out) == m:
            break
    return out


def orient(P: np.ndarray, h1: int, seed: int) -> dict:
    X = np.array(distinct_top(P))
    labs = [K.label(c) for c in K.classify(X, h1, 4, seed)]
    return {lab: labs.count(lab) for lab in ("forward", "reverse", "both", "none")} | {
        "copiers": [X[i].tobytes().hex() for i, l in enumerate(labs) if l != "none"][:10]}


def job(seed: int) -> dict:
    path = RUN / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    soup = CounterfactualSoup(n=N, seed=seed)
    series, run, T = [], 0, None
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
        if (T is None and e >= WAIT) or (T is not None and e >= T + AFTER):
            break
    np.save(RUN / f"{seed}-{soup.epochs}.npy", soup.programs)
    res = {"seed": seed, "T": T, "jumped": T is not None, "end": soup.epochs, "series": series,
           "sec": round(time.time() - t0)}
    res["orientation"] = orient(soup.programs, H1, 560 + seed)
    path.write_text(json.dumps(res))
    print(json.dumps({"done": seed, "T": T, "end": soup.epochs, "orientation": res["orientation"]}), flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    with Pool(a.workers) as pool:
        res = pool.map(job, list(SEEDS), chunksize=1)
    jumped = [r for r in res if r["jumped"]]
    ok = [r["orientation"]["forward"] >= 1 and r["orientation"]["forward"] >= 0.9 * (
        r["orientation"]["forward"] + r["orientation"]["reverse"] + r["orientation"]["both"]) for r in jumped]
    summary = {"jumped": len(jumped), "of": len(res), "T": {r["seed"]: r["T"] for r in res},
               "orientation": {r["seed"]: {k: v for k, v in r["orientation"].items() if k != "copiers"} for r in jumped},
               "primary": ("undecided (no jump)" if not jumped else ("pass" if all(ok) else "fail"))}
    json.dump({"experiment": "E-56", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E56 DONE", flush=True)


if __name__ == "__main__":
    main()
