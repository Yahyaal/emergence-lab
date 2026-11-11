"""E-73 part B (docs/data/e73-preregistration.md): replay every soup of E-70, E-71 and E-72 from its seed and score
it with both copy tests at the experiment's own checkpoints: the D-050 test (shift-aware, 60/64) and the D-053 test
(58/64 + instruction-fidelity guard, scripts/bff_fidelity.py). The soup trajectory does not depend on detection,
so the D-050 copier series must reproduce the stored one exactly (equivalence check). Same jump rule for both:
T = first checkpoint with >= 1 copier whose checkpoint 1,000 rounds later has >= 10; up to 16,000 rounds.

    PYTHONPATH=scripts python scripts/bff_rescore.py --workers 11 --out docs/data/experiments/2026-11-11-e73-rescore.json
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
import bff_counterfactual as C  # noqa: E402
import bff_fidelity as FID  # noqa: E402
import bff_kernels as K  # noqa: E402

N, WAIT, AFTER, MIN_COP = 2 ** 14, 16000, 1000, 10
EXPS = {"E-70": ("runs/e70", 250), "E-71": ("runs/e71", 50), "E-72": ("runs/e72", 50)}
RUN = Path("runs/e73")


def jump(cop: dict, e: int):
    return e - AFTER if cop[e] >= MIN_COP and cop.get(e - AFTER, 0) >= 1 else None


def job(arg) -> dict:
    exp, seed, code, every, stored_T, stored = arg
    path = RUN / f"{exp}-{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    C.H1 = code
    soup = C.CounterfactualSoup(n=N, length=64, seed=seed)
    old, new, To, Tn, eq = {}, {}, None, None, True
    while soup.epochs < WAIT and (To is None or Tn is None):
        soup.epoch()
        e = soup.epochs
        if e % every:
            continue
        X = np.array(C.distinct_top(soup.programs))
        s = 680 + seed + e
        c0, _ = K.classify_shift(X, code, 4, s)
        c1, _ = K.classify_fid(X, code, 4, s, thr=FID.THR, opmin=FID.OPMIN)
        old[e], new[e] = int((c0 > 0).sum()), int((c1 > 0).sum())
        if e in stored and stored[e] != old[e]:
            eq = False
        if To is None:
            To = jump(old, e)
        if Tn is None:
            Tn = jump(new, e)
    res = {"exp": exp, "seed": seed, "code": code, "v": code >> 16, "g": (code >> 8) & 255, "h": code & 255,
           "T_d050": To, "T_d053": Tn, "stored_T": stored_T,
           "equivalent": eq and (To == stored_T or (stored_T is None and To is None)),
           "end": soup.epochs, "series": [[e, old[e], new[e]] for e in sorted(old)], "sec": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    print(json.dumps({k: res[k] for k in ("exp", "seed", "v", "g", "h", "T_d050", "T_d053", "equivalent", "sec")}),
          flush=True)
    return res


def jobs() -> list:
    out = []
    for exp, (d, every) in EXPS.items():
        for f in sorted(Path(d).glob("*.json")):
            r = json.loads(f.read_text())
            stored = {x["epoch"]: x["copiers"] for x in r["series"]}
            out.append((exp, r["seed"], r["h1"], every, r["T"], stored))
    # long (non-jumped) soups first so the pool stays busy
    return sorted(out, key=lambda j: j[4] is not None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(job, jobs(), chunksize=1)
    out = {"experiment": "E-73", "part": "rescore", "thr": FID.THR, "opmin": FID.OPMIN, "results": res,
           "equivalent_all": all(r["equivalent"] for r in res), "seconds": round(time.time() - t0)}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({"n": len(res), "equivalent_all": out["equivalent_all"], "seconds": out["seconds"]}))
    print("=== SENTINEL e73 rescore DONE", flush=True)


if __name__ == "__main__":
    main()
