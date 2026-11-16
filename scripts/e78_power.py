"""E-78 planning numbers (draft pre-registration docs/data/e78-preregistration.md):

1. Detectable effect at n = 7 soups for the between-arm statistic d_k = mean s(late, S) - mean s(late, M)
   (kin-free invasion, E-53/E-54 assay), tested by the exact one-sided sign-flip permutation test
   (2^7 = 128 sign patterns, alpha 0.05). Three noise models, all from the E-54 export:
   (a) "assay only": d_k ~ N(delta, sigma^2), sigma = sqrt(2) x the typical standard error of a 6-candidate
       group mean (median over the 14 E-54 groups in the T+10000 background);
   (b) "E-54 normal": sigma = sqrt(2) x the SD over soups of E-54's late - early delta (T+10000 background);
   (c) "E-54 resampled": d_k = delta + (D_i - D_j), D drawn with replacement from the 14 centred E-54 deltas
       (both backgrounds), heavy-tailed like soup 5401.
2. Wall-time projection for 7 soups x 2 or 3 arms on 11 workers, from the E-54 logged steps per pair after
   T + 2000 and the cost per step measured under an 11-process load (runs/e78/load-11.json).

    python scripts/e78_power.py --e54 /path/to/runs/e54 [--out runs/e78/planning.json]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

E54_EXPORT = Path("docs/data/experiments/2026-11-08-e54-long-soups.json")
JUMPED = {5301: 21750, 5302: 13750, 5308: 12500, 5401: 10250, 5402: 22250, 5406: 16750, 5410: 750}
SIGNS = np.array(list(itertools.product([-1, 1], repeat=7)))


def perm_p(d: np.ndarray) -> float:
    """Exact one-sided sign-flip p for sum(d) > 0 (n = 7)."""
    tot = (SIGNS * np.abs(d)).sum(1)
    return float((tot >= d.sum() - 1e-12).mean())


def power(delta: float, draw, reps: int, rng) -> float:
    return float(np.mean([perm_p(delta + draw(rng)) <= 0.05 for _ in range(reps)]))


def noise_models() -> dict:
    d = json.load(open(E54_EXPORT))
    inv = d["invasion"]
    ses, deltas = [], {}
    for bg in (10000, 20000):
        for s, T in JUMPED.items():
            m = {}
            for g in ("early", "late"):
                v = np.array([x["s"] for x in inv if x["seed"] == s and x["group"] == g and x["background"] == T + bg])
                m[g] = v.mean()
                if bg == 10000:
                    ses.append(v.std(ddof=1) / math.sqrt(len(v)))
            deltas[(s, bg)] = m["late"] - m["early"]
    d10 = np.array([deltas[(s, 10000)] for s in JUMPED])
    pool = np.array(list(deltas.values()))
    pool = pool - pool.mean()
    sig_a = math.sqrt(2) * float(np.median(ses))
    sig_b = math.sqrt(2) * float(d10.std(ddof=1))
    return {"se_group_median": float(np.median(ses)), "sd_delta_e54": float(d10.std(ddof=1)),
            "sd_delta_e54_without_5401": float(np.delete(d10, list(JUMPED).index(5401)).std(ddof=1)),
            "models": {"assay only": lambda r: r.normal(0, sig_a, 7),
                       "E-54 normal": lambda r: r.normal(0, sig_b, 7),
                       "E-54 resampled": lambda r: r.choice(pool, 7) - r.choice(pool, 7)},
            "sigma": {"assay only": sig_a, "E-54 normal": sig_b, "E-54 resampled": float(math.sqrt(2) * pool.std())}}


def detectable(reps: int = 2000, seed: int = 78) -> dict:
    nm = noise_models()
    rng = np.random.default_rng(seed)
    out = {k: v for k, v in nm.items() if k != "models"}
    grid = np.round(np.arange(0.0, 1.01, 0.02), 2)
    out["power"] = {}
    for name, draw in nm["models"].items():
        pw = {float(g): power(float(g), draw, reps, rng) for g in grid}
        d80 = next((g for g in grid if pw[float(g)] >= 0.8), None)
        d50 = next((g for g in grid if pw[float(g)] >= 0.5), None)
        out["power"][name] = {"size_at_0": pw[0.0], "delta_50pct": d50, "delta_80pct": d80,
                              "curve": {str(g): pw[float(g)] for g in grid[::5]}}
    return out


def projection(e54: Path, load: Path, horizons=(5000, 10000, 20000), workers: int = 11) -> dict:
    L = json.loads(load.read_text())
    c = float(np.median([r["sec_per_round"] / r["steps_per_pair"] for r in L]))  # sec per (step per pair) per round
    per_soup = {}
    for s, T in JUMPED.items():
        ser = sorted((r["epoch"], r["steps_per_pair"]) for r in json.loads((e54 / f"{s}.json").read_text())["series"]
                     if r["epoch"] > T + 2000)
        ep, spp = np.array(ser, float).T
        row = {}
        for H in horizons:
            t = np.arange(T + 2001, T + 2001 + H)
            v = np.interp(t, ep, spp)          # beyond the E-54 log (T + 20000): last logged value
            row[H] = float(c * v.sum())
        per_soup[s] = row
    out = {"sec_per_step_per_pair_round_under_load": c, "per_soup_hours": {s: {H: round(v / 3600, 2) for H, v in r.items()}
                                                                         for s, r in per_soup.items()}}
    for arms in (2, 3):
        out[f"{arms}_arms"] = {}
        for H in horizons:
            jobs = sorted([per_soup[s][H] for s in JUMPED for _ in range(arms)], reverse=True)
            ws = [0.0] * workers          # longest job first onto the least-loaded worker
            for j in jobs:
                ws[int(np.argmin(ws))] += j
            out[f"{arms}_arms"][H] = {"wall_hours": round(max(ws) / 3600, 1), "cpu_hours": round(sum(jobs) / 3600, 1)}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--e54", default="runs/e54")
    ap.add_argument("--load", default="runs/e78/load-11.json")
    ap.add_argument("--out", default="runs/e78/planning.json")
    a = ap.parse_args()
    res = {"detectable": detectable(), "projection": projection(Path(a.e54), Path(a.load))}
    Path(a.out).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
