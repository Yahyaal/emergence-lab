"""E-40: do self-replicators emerge in BFF program soups? (docs/data/e40-preregistration.md)

Runs BFF soups and controls in parallel, records the high-order entropy (HOE) every 250 epochs,
and runs the replicator detector (observatory/replicators.py) 1000 epochs after a soup's first
transition checkpoint (HOE >= 1.0) and at the end of every soup. Each soup's result goes to
runs/e40/<mode>-<seed>.json (resumable: finished soups are skipped); snapshots to
runs/e40/<mode>-<seed>-<epoch>.npy; the summary to --out.

    python scripts/bff_soups.py --workers 11 --out docs/data/experiments/2026-11-08-e40-bff-soups.json
"""
from __future__ import annotations

import argparse
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from emergence.observatory import replicators as RP
from emergence.programs import bff as B

RUN = Path("runs/e40")
N, EPOCHS, CTRL_EPOCHS, EVERY, THRESH, AFTER = 16384, 16000, 4000, 250, 1.0, 1000


def brief(scan: dict) -> dict:
    keep = ("verdict", "count", "program", "pair_copy_rate", "random_replicating", "child_differs")
    return {"replicators": scan["replicators"], "verdicts": scan["verdicts"],
            "results": [{k: r.get(k) for k in keep} | {"gen1": [r["gen1"]["start"], r["gen1"]["late"]],
                                                       "gen2": (r.get("gen2") or {}).get("late")}
                        for r in scan["results"]]}


def job(spec: tuple[str, int, int]) -> dict:
    mode, seed, epochs = spec
    out_path = RUN / f"{mode}-{seed}.json"
    if out_path.exists():
        return json.loads(out_path.read_text())
    t0 = time.time()
    soup = B.Soup(n=N, mode=mode, seed=seed)
    series, first, scans = [], None, {}
    scan_at = None
    for e in range(1, epochs + 1):
        st = soup.epoch()
        if e % EVERY == 0:
            hoe = B.high_order_entropy(soup.programs)
            series.append({"epoch": e, "hoe": round(hoe, 3), "ops": round(B.ops_fraction(soup.programs), 3),
                           "steps_per_pair": round(st / (N / 2), 1),
                           "top": B.top_programs(soup.programs, 1)[0][1]})
            if first is None and hoe >= THRESH:
                first, scan_at = e, e + AFTER
            print(json.dumps({"mode": mode, "seed": seed} | series[-1] | {"sec": round(time.time() - t0)}),
                  flush=True)
        if e == scan_at and e < epochs:
            np.save(RUN / f"{mode}-{seed}-{e}.npy", soup.programs)
            scans[str(e)] = brief(RP.scan(soup.programs, np.random.default_rng(seed + e), mode=mode))
    np.save(RUN / f"{mode}-{seed}-{epochs}.npy", soup.programs)
    scans[str(epochs)] = brief(RP.scan(soup.programs, np.random.default_rng(seed + epochs), mode=mode))
    res = {"mode": mode, "seed": seed, "epochs": epochs, "transition_epoch": first,
           "transitioned": first is not None, "replicator_at_end": scans[str(epochs)]["replicators"] > 0,
           "scans": scans, "series": series, "top_end": [[p.hex(), c] for p, c in B.top_programs(soup.programs, 5)],
           "sec": round(time.time() - t0)}
    out_path.write_text(json.dumps(res))
    print(json.dumps({"done": mode, "seed": seed, "transition_epoch": first,
                      "verdicts_end": scans[str(epochs)]["verdicts"], "sec": res["sec"]}), flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pilot", action="store_true", help="tiny run to check the script (not the experiment)")
    a = ap.parse_args()
    global RUN, N, EPOCHS, CTRL_EPOCHS
    if a.pilot:
        RUN, N, EPOCHS, CTRL_EPOCHS = Path("runs/e40-pilot"), 2048, 500, 250
        specs = [("bff", 1, EPOCHS), ("noexec", 2, CTRL_EPOCHS), ("copyall", 3, CTRL_EPOCHS)]
    else:
        specs = ([("bff", s, EPOCHS) for s in range(4000, 4012)]
                 + [(m, s, CTRL_EPOCHS) for m in ("noexec", "copyall") for s in (4100, 4101)])
    RUN.mkdir(parents=True, exist_ok=True)
    with Pool(a.workers) as pool:
        results = pool.map(job, specs, chunksize=1)
    summary = {}
    for mode in ("bff", "noexec", "copyall"):
        rs = [r for r in results if r["mode"] == mode]
        summary[mode] = {"soups": len(rs), "transitioned": sum(r["transitioned"] for r in rs),
                         "replicator_at_end": sum(r["replicator_at_end"] for r in rs),
                         "replicator_in_untransitioned": sum(r["replicator_at_end"] and not r["transitioned"]
                                                             for r in rs)}
    Path(a.out).write_text(json.dumps({"experiment": "E-40", "summary": summary, "soups": results}, indent=1))
    print(json.dumps(summary), flush=True)
    print("=== E40 DONE", flush=True)


if __name__ == "__main__":
    main()
