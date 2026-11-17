"""E-81 groundwork (J-097; exploratory, pilot seeds only): the P3 pilot and the groundwork export.

  --extend   continues each pilot soup's T + 10,000 snapshot (runs/e81/pilot2/soups/<seed>-late.npz) another 10,000
             epochs with a fresh generator ([81, seed, 99]; the pilot did not save generator state), takes the
             copiers at the end ("late2") and races them against the T + 10,000 copiers as P3 will: noise of d3.
  --export   writes docs/data/experiments/<date>-e81-groundwork.json: the first pilot (wrapping vs halting heads,
             noexec, copyall, seeded 120-byte ancestor), the E-81 protocol pilot (runs/e81/pilot2/out.json), the P3
             pilot, the controls and the power calculation.

    PYTHONPATH=.:scripts python scripts/e81_groundwork.py --extend --workers 10
    PYTHONPATH=.:scripts python scripts/e81_groundwork.py --export docs/data/experiments/2026-11-17-e81-groundwork.json
"""
from __future__ import annotations

import argparse
import glob
import json
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import norm

import bffvl as V
import bffvl_assay as A
import e81_run as R

P2DIR = Path("runs/e81/pilot2")


def extend(seed: int) -> dict:
    path = P2DIR / "extend" / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    d = np.load(P2DIR / "soups" / f"{seed}-late.npz")
    s = V.Soup(buf=d["buf"], lens=d["lens"], rng=np.random.default_rng([81, seed, 99]))
    for _ in range(10000):
        s.epoch()
    c = R.census(s, seed * 100003 + 99)
    res = json.loads((P2DIR / "soups" / f"{seed}.json").read_text())
    la = [h for h, _ in res["late"]["copiers"][:R.K]]
    l2 = [h for h, _ in c["copiers"][:R.K]]
    races = [R.race_job(((seed, "late2", "late", i, j), a, b, [81, seed, 3, i, j]))[1]
             for i, a in enumerate(l2) for j, b in enumerate(la)]
    out = {"seed": seed, "late2": c, "d3": float(np.mean([r["s"] for r in races])) if races else None,
           "identical": sum(r["identical"] for r in races), "pairs": len(races), "seconds": round(time.time() - t0),
           "fecundity_late2": R.fecundity(l2, seed)}
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out))
    return out


def power(sd: float, n: int, effect: float, alpha: float) -> float:
    """Normal approximation to the one-sided test of a mean (sign-flip tests are close to t tests here)."""
    return float(norm.sf(norm.isf(alpha) - effect / (sd / np.sqrt(n))))


def export(out_path: str) -> None:
    pilot1 = {}
    for d in ("runs/e81/pilot-wrap", "runs/e81/pilot"):
        for f in sorted(glob.glob(f"{d}/*.jsonl")):
            rows = [json.loads(l) for l in open(f)]
            first = next((r for r in rows if r["copiers"] > 0), None)
            take = next((r for r in rows if r["copier_share10"] >= 0.25), None)
            pilot1[f"{Path(d).name}/{Path(f).stem}"] = {
                "epochs": rows[-1]["epoch"], "first_copier_epoch": first and first["epoch"],
                "first_copier_lengths": first and first["lens_copiers"][:5],
                "share_ge_025_epoch": take and take["epoch"], "shortest_at_takeover": take and take["shortest"],
                "takeover_checkpoints": sum(r["copier_share10"] >= 0.25 for r in rows),
                "final": {k: rows[-1][k] for k in ("n", "mean_len", "hoe", "copier_share10", "shortest",
                                                    "top_copier")},
                "mean_len_trace": [(r["epoch"], r["mean_len"]) for r in rows[:: max(1, len(rows) // 25)]]}
    p2 = json.loads((P2DIR / "out.json").read_text())
    ext = [json.loads(Path(f).read_text()) for f in sorted(glob.glob(str(P2DIR / "extend" / "*.json")))]
    d1 = np.array([p["d1"] for p in p2["per_soup"]])
    d2 = np.array([p["d2"] for p in p2["per_soup"]])
    d3 = np.array([e["d3"] for e in ext if e["d3"] is not None])
    sd = {"d1": float(d1.std(ddof=1)), "d2": float(d2.std(ddof=1)),
          "d3": float(d3.std(ddof=1)) if len(d3) > 1 else None}
    seeded_d = [s["d"] for s in p2["seeded"]]
    alpha_holm = 0.05 / 49  # worst Holm rank in a family of 44 + E-81's 3 (+2 slack)
    pw = {}
    for n in (8, 16, 24, 32, 40):
        pw[n] = {"P1_at_seeded_effect_nominal": power(sd["d1"], n, float(np.mean(seeded_d)), 0.05),
                 "P2_at_delta_nominal": power(sd["d2"], n, R.DELTA, 0.05),
                 "P2_at_delta_holm_worst": power(sd["d2"], n, R.DELTA, alpha_holm),
                 "P3_at_delta_holm_worst": power(sd["d3"], n, R.DELTA, alpha_holm) if sd["d3"] else None,
                 "ci_half_width_P2": float(2.04 * sd["d2"] / np.sqrt(n)),
                 "ci_half_width_P3": float(2.04 * sd["d3"] / np.sqrt(n)) if sd["d3"] else None,
                 "min_p_signflip": 2.0 ** -n}
    ctrl = A.controls()
    res = {"experiment": "E-81 groundwork", "journal": "J-097", "decisions": ["D-070", "D-071"],
           "status": "exploratory pilots on pilot seeds; no confirmatory data",
           "pilot1": pilot1, "protocol_pilot": {k: p2[k] for k in ("P1", "P2", "per_soup", "seeded", "gate",
                                                                    "secondary", "seconds")},
           "p3_pilot": ext, "noise_sd": sd, "seeded_d": seeded_d, "power": pw, "delta": R.DELTA,
           "controls": [{"name": n, "ok": bool(o), "detail": d} for n, o, d in ctrl]}
    Path(out_path).write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({"sd": sd, "seeded_d": seeded_d, "power": pw}, indent=1, default=float))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extend", action="store_true")
    ap.add_argument("--export", default=None)
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.extend:
        seeds = sorted(int(Path(f).stem) for f in glob.glob(str(P2DIR / "soups" / "*.json")))
        R.OUT = P2DIR
        with Pool(a.workers) as p:
            for r in p.imap_unordered(extend, seeds):
                print(r["seed"], "d3", r["d3"], "identical", r["identical"], "/", r["pairs"], f"{r['seconds']}s",
                      flush=True)
    if a.export:
        export(a.export)


if __name__ == "__main__":
    main()
