"""E-59 (docs/data/e59-preregistration.md): confirmation of E-58 with the D-046 jump criterion fixed in advance.
16 soups of 2^14 with head1 = 127 (backward copiers) and 8 with head1 = 64 (forward copiers), new seeds.

    python scripts/bff_orient_confirm.py --workers 4 --out docs/data/experiments/2026-11-08-e59-orientation-confirm.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

RUN = Path("runs/e59")
N, WAIT, AFTER, EVERY, THRESH, PERSIST = 2 ** 14, 16000, 1000, 250, 1.0, 3
JOBS = [(s, 127) for s in range(5900, 5916)] + [(s, 64) for s in range(5920, 5928)]


class Soup(C.CounterfactualSoup):
    def __init__(self, h1: int, **kw):
        super().__init__(**kw)
        self.h1 = h1

    def epoch(self) -> int:
        C.H1 = self.h1  # CounterfactualSoup.epoch reads the module global
        return super().epoch()


def job(arg) -> dict:
    seed, h1 = arg
    path = RUN / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    soup = Soup(h1, n=N, seed=seed)
    series, run, T, checks = [], 0, None, []
    while True:
        st = soup.epoch()
        e = soup.epochs
        if e % EVERY == 0:
            hoe = B.high_order_entropy(soup.programs)
            series.append({"epoch": e, "hoe": round(hoe, 3), "steps_per_pair": round(st / (N / 2), 1)})
            if T is None:
                run = run + 1 if hoe >= THRESH else 0
                if run >= PERSIST:
                    o = C.orient(soup.programs, h1, 590 + seed + e)
                    ncop = o["forward"] + o["reverse"] + o["both"]
                    checks.append({"epoch": e, "copiers": ncop})
                    if ncop >= 1:
                        T = e - EVERY * (PERSIST - 1)
            if e % 2000 == 0:
                print(json.dumps({"seed": seed, "h1": h1, "T": T} | series[-1] | {"sec": round(time.time() - t0)}),
                      flush=True)
        if (T is None and e >= WAIT) or (T is not None and e >= T + AFTER):
            break
    res = {"seed": seed, "h1": h1, "T": T, "jumped": T is not None, "end": soup.epochs, "series": series,
           "hoe_only_checks": checks, "sec": round(time.time() - t0)}
    res["orientation"] = C.orient(soup.programs, h1, 591 + seed)
    res["end_steps_per_pair"] = series[-1]["steps_per_pair"]
    path.write_text(json.dumps(res))
    print(json.dumps({"done": seed, "h1": h1, "T": T, "end": soup.epochs,
                      "orientation": {k: v for k, v in res["orientation"].items() if k != "copiers"}}), flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(job, JOBS, chunksize=1)
    by = {h: [r for r in res if r["h1"] == h] for h in (127, 64)}
    j = {h: sum(r["jumped"] for r in by[h]) for h in by}
    n = {h: len(by[h]) for h in by}
    m, tot = j[127] + j[64], n[127] + n[64]
    p = sum(comb(m, x) * comb(tot - m, n[127] - x) for x in range(0, j[127] + 1)) / comb(tot, n[127])

    def oriented(r, lab):
        o = r["orientation"]
        c = o["forward"] + o["reverse"] + o["both"]
        return c >= 1 and o[lab] >= 0.9 * c
    summary = {"jumped": {str(h): j[h] for h in j}, "of": {str(h): n[h] for h in n}, "fisher_p": p,
               "T": {str(h): {r["seed"]: r["T"] for r in by[h]} for h in by},
               "primary": "pass" if j[127] <= 4 and j[64] >= 7 and p < 0.01 else "fail",
               "secondary_orientation": all(oriented(r, "reverse") for r in by[127] if r["jumped"]) and
               all(oriented(r, "forward") for r in by[64] if r["jumped"]),
               "secondary_steps_gt_3000": all(r["end_steps_per_pair"] > 3000 for r in res if r["jumped"]),
               "hoe_only_crossings": {r["seed"]: len(r["hoe_only_checks"]) - (1 if r["jumped"] else 0)
                                      for r in res if r["hoe_only_checks"]},
               "seconds": round(time.time() - t0)}
    json.dump({"experiment": "E-59", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E59 DONE", flush=True)


if __name__ == "__main__":
    main()
