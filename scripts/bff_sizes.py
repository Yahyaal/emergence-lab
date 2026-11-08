"""E-50: transition rate vs soup size (docs/data/e50-preregistration.md).

Runs BFF soups of 2^13, 2^15 and 2^16 programs; a soup that reaches the transition (first HOE >= 1.0
checkpoint) is scanned with the replicator detector 1000 epochs later and stopped; others are scanned
at the end. Per-soup results in runs/e50/<n>-<seed>.json (resumable). Then a Poisson waiting-time
model (hazard ∝ N^beta, with the E-40/E-41 2^14 arm) is fitted.

    python scripts/bff_sizes.py --workers 10 --out docs/data/experiments/2026-11-08-e50-soup-size.json
    python scripts/bff_sizes.py --analyse --out ...   # fit only, from runs/e50/
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import chi2

from emergence.observatory import replicators as RP
from emergence.programs import bff as B

RUN = Path("runs/e50")
EVERY, THRESH, AFTER = 250, 1.0, 1000
ARMS = {2 ** 13: (range(5100, 5112), 48000), 2 ** 15: (range(5200, 5212), 32000), 2 ** 16: (range(5300, 5310), 24000)}
# E-40/E-41 2^14 arm as run: exposures (epochs until transition or end) and events
E41 = [(48000, 0)] * 10 + [(43250, 1), (32000, 1)]


def brief(scan: dict) -> dict:
    keep = ("verdict", "count", "program", "pair_copy_rate", "random_replicating", "child_differs")
    return {"replicators": scan["replicators"], "verdicts": scan["verdicts"],
            "results": [{k: r.get(k) for k in keep} for r in scan["results"]]}


def job(spec: tuple) -> dict:
    n, seed, epochs = spec
    out_path = RUN / f"{n}-{seed}.json"
    if out_path.exists():
        return json.loads(out_path.read_text())
    t0 = time.time()
    soup = B.Soup(n=n, seed=seed)
    series, first, stop = [], None, epochs
    for e in range(1, epochs + 1):
        st = soup.epoch()
        if e % EVERY == 0:
            hoe = B.high_order_entropy(soup.programs)
            series.append({"epoch": e, "hoe": round(hoe, 3), "ops": round(B.ops_fraction(soup.programs), 3),
                           "steps_per_pair": round(st / (n / 2), 1)})
            if first is None and hoe >= THRESH:
                first, stop = e, min(epochs, e + AFTER)
            if e % 2000 == 0 or first == e:
                print(json.dumps({"n": n, "seed": seed} | series[-1] | {"sec": round(time.time() - t0)}), flush=True)
        if e == stop:
            break
    np.save(RUN / f"{n}-{seed}-{soup.epochs}.npy", soup.programs)
    scan = brief(RP.scan(soup.programs, np.random.default_rng(seed + soup.epochs)))
    res = {"n": n, "seed": seed, "horizon": epochs, "run_epochs": soup.epochs, "transition_epoch": first,
           "exposure": first if first is not None else epochs, "transitioned": first is not None,
           "scan_epoch": soup.epochs, "scan": scan, "replicator": scan["replicators"] > 0, "series": series,
           "sec": round(time.time() - t0)}
    out_path.write_text(json.dumps(res))
    print(json.dumps({"done": n, "seed": seed, "transition_epoch": first, "verdicts": scan["verdicts"],
                      "sec": res["sec"]}), flush=True)
    return res


def fit(rows: list[tuple[int, float, int]]) -> dict:
    """rows: (n, exposure, event). Hazard = lam0 * (n / 2^14)^beta; lam0 profiled out analytically."""
    n = np.array([r[0] for r in rows], float)
    t = np.array([r[1] for r in rows], float)
    d = np.array([r[2] for r in rows], float)
    x = np.log2(n / 2 ** 14)

    def nll(beta):
        w = t * 2.0 ** (beta * x)
        lam0 = d.sum() / w.sum()
        return -(d * np.log(lam0 * 2.0 ** (beta * x))).sum() + lam0 * w.sum()

    res = minimize_scalar(nll, bounds=(-6, 8), method="bounded")
    b, l1 = float(res.x), float(res.fun)
    lr = 2 * (nll(0.0) - l1)
    p_one = float(0.5 * chi2.sf(lr, 1)) if b > 0 else float(1 - 0.5 * chi2.sf(lr, 1))
    grid = np.linspace(-6, 8, 2801)
    ok = [g for g in grid if 2 * (nll(g) - l1) <= chi2.ppf(0.95, 1)]
    return {"beta": round(b, 3), "ci95": [round(float(min(ok)), 2), round(float(max(ok)), 2)], "lr": round(float(lr), 3),
            "p_one_sided": round(p_one, 5), "events": int(d.sum()), "exposure": float(t.sum())}


def analyse(results: list[dict]) -> dict:
    rows = [(2 ** 14, e, d) for e, d in E41]
    arms = {}
    for n in sorted({r["n"] for r in results}):
        rs = [r for r in results if r["n"] == n]
        rows += [(n, r["exposure"], int(r["transitioned"])) for r in rs]
        arms[str(n)] = {"soups": len(rs), "transitioned": sum(r["transitioned"] for r in rs),
                        "transition_epochs": sorted(r["transition_epoch"] for r in rs if r["transitioned"]),
                        "exposure": sum(r["exposure"] for r in rs),
                        "replicator_in_transitioned": sum(r["replicator"] for r in rs if r["transitioned"]),
                        "replicator_in_untransitioned": sum(r["replicator"] for r in rs if not r["transitioned"]),
                        "median_early_hoe": float(np.median([s["hoe"] for r in rs for s in r["series"][:4]]))}
    arms[str(2 ** 14)] = {"soups": 12, "transitioned": 2, "exposure": sum(e for e, _ in E41), "source": "E-40/E-41"}
    return {"arms": arms, "fit": fit(rows)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--out", required=True)
    ap.add_argument("--analyse", action="store_true")
    a = ap.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    specs = [(n, s, ep) for n, (seeds, ep) in sorted(ARMS.items(), reverse=True) for s in seeds]
    if a.analyse:
        results = [json.loads((RUN / f"{n}-{s}.json").read_text()) for n, s, _ in specs
                   if (RUN / f"{n}-{s}.json").exists()]
    else:
        with Pool(a.workers) as pool:
            results = pool.map(job, specs, chunksize=1)
    out = {"experiment": "E-50", "analysis": analyse(results),
           "soups": [{k: v for k, v in r.items() if k != "series"} | {"hoe": [s["hoe"] for s in r["series"]]}
                     for r in results]}
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["analysis"]), flush=True)
    print("=== E50 DONE", flush=True)


if __name__ == "__main__":
    main()
