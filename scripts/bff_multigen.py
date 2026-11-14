"""E-72 (docs/data/e72-preregistration.md): a multi-generation version of the F test. The census (E-61) calls a
short copier self-sufficient when 3 of 4 of its single copies copy again (one generation). Here each
self-sufficient kernel starts lineages: copy it into a fresh random partner, test whether the copy copies
(shift-aware, 4 partners), continue with that copy, for G generations. A kernel is 'deep' when at least half
its lineages still copy at generation G.

    python scripts/bff_multigen.py --part census --workers 11 --out docs/data/experiments/2026-11-10-e72-multigen.json
    python scripts/bff_multigen.py --part fresh --workers 11 --out docs/data/experiments/2026-11-10-e72-fresh-census.json
    python scripts/bff_multigen.py --part soups --workers 11 --out docs/data/experiments/2026-11-10-e72-soups.json

Part A (census): the 44 F rules of the E-70 census (soups already seen: explanatory only).
Part B (fresh, pre-registered): 240 untested rules, variant v in 1..5 with head0 starting at g in 1..127 and head1
at h = g + d (d in 60..68, mod 128); 1-generation census plus depth; then soups in up to 8 F-deep and 8 F-shallow
rules (6 soups each, E-71's D-050 settings).
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
import bff_shift_census as S  # noqa: E402

G, LINEAGES, CAP = 5, 8, 300


def ss_kernels(code: int) -> tuple[list[np.ndarray], int]:
    """Exactly census_rule's enumeration and RNG sequence; returns the self-sufficient programs and the copier count."""
    rng = np.random.default_rng([61, code])
    out, ncop = [], 0
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            P = K.programs(k, lo, min(lo + K.CHUNK, 10 ** k), False)
            scr = np.nonzero(K.classify_shift(P, code, 1, 0x6101 + k)[0])[0]
            if len(scr):
                conf, _ = K.classify_shift(P[scr], code, 4, 0x6102 + k)
                for i, c in zip(scr, conf):
                    if c:
                        ncop += 1
                        if S.self_sufficient(P[i].copy(), code, rng):
                            out.append(P[i].copy())
    return out, ncop


def lineage(P: np.ndarray, code: int, rng) -> int:
    """Generations (0..G) for which the line of single copies keeps copying."""
    x = P
    for g in range(1, G + 1):
        x = S.product(x, code, rng)
        ok, _ = K.classify_shift(x[None, :], code, 4, int(rng.integers(1 << 62)))
        if not ok[0]:
            return g - 1
    return G


def rule_job(arg) -> dict:
    v, h, L = arg[:3]
    g = arg[3] if len(arg) > 3 else 0
    K.set_length(L)
    code = h + 256 * g + 65536 * v
    t0 = time.time()
    ks, ncop = ss_kernels(code)
    rng = np.random.default_rng([72, code])
    idx = rng.permutation(len(ks))[:CAP]
    surv = [[lineage(ks[i], code, rng) for _ in range(LINEAGES)] for i in idx]
    deep = [sum(s == G for s in row) >= LINEAGES / 2 for row in surv]
    n = len(ks)
    hist = np.bincount([s for row in surv for s in row], minlength=G + 1).tolist() if surv else [0] * (G + 1)
    frac_deep = float(np.mean(deep)) if deep else 0.0
    return {"v": v, "g": g, "h": h, "L": L, "code": code, "copiers": ncop, "self_sufficient": n, "tested": len(idx),
            "deep_share_of_ss": frac_deep, "deep_est": round(frac_deep * n, 1),
            "deep_fraction_of_copiers": frac_deep * n / ncop if ncop else 0.0,
            "survival_hist": hist, "sec": round(time.time() - t0)}


NFRESH, NPICK, SOUPS_B, EVERY_B = 240, 8, 6, 50


def fresh_rules() -> list[tuple[int, int, int, int]]:
    rng = np.random.default_rng(72)
    out = set()
    while len(out) < NFRESH:
        v, g, d = int(rng.integers(1, 6)), int(rng.integers(1, 128)), int(rng.integers(60, 69))
        out.add((v, (g + d) % 128, 64, g))
    return sorted(out)


def pick(census: list[dict]) -> list[tuple[str, dict]]:
    rng = np.random.default_rng(720)
    F = [r for r in census if r["self_sufficient"] > 0]
    deep = [r for r in F if r["deep_est"] >= 1]
    shallow = [r for r in F if r["deep_est"] < 1]
    sel = []
    for lab, grp in (("deep", deep), ("shallow", shallow)):
        for i in sorted(rng.permutation(len(grp))[:NPICK]):
            sel.append((lab, grp[int(i)]))
    return sel


def soups(workers: int, census_path: str) -> dict:
    from math import comb
    from scipy.stats import mannwhitneyu, spearmanr
    import bff_tapelength as T
    c = json.load(open(census_path))["rules"]
    sel = pick(c)
    T.RUN, T.EVERY = Path("runs/e72"), EVERY_B
    T.RUN.mkdir(parents=True, exist_ok=True)
    jobs = [(7200 + 10 * k + i, 64, r["code"]) for k, (_, r) in enumerate(sel) for i in range(SOUPS_B)]
    with Pool(workers) as pool:
        res = pool.map(T.soup_job, jobs, chunksize=1)
    per = []
    for lab, r in sel:
        ts = [s["T"] for s in res if s["h1"] == r["code"]]
        per.append({"class": lab, "v": r["v"], "g": r["g"], "h": r["h"], "self_sufficient": r["self_sufficient"],
                    "deep_est": r["deep_est"], "copiers": r["copiers"], "T": ts,
                    "jumped": sum(t is not None for t in ts),
                    "median_T": float(np.median([t if t is not None else T.WAIT for t in ts]))})
    md = [p["median_T"] for p in per if p["class"] == "deep"]
    ms = [p["median_T"] for p in per if p["class"] == "shallow"]
    enough = len(md) >= 4 and len(ms) >= 4
    mw = float(mannwhitneyu(ms, md, alternative="greater").pvalue) if enough else float("nan")
    ratio = float(np.median(ms) / np.median(md)) if enough else float("nan")
    jd, nd = sum(p["jumped"] for p in per if p["class"] == "deep"), SOUPS_B * len(md)
    js, ns = sum(p["jumped"] for p in per if p["class"] == "shallow"), SOUPS_B * len(ms)
    rho, prho = spearmanr([p["deep_est"] for p in per], [p["median_T"] for p in per])
    rho1, prho1 = spearmanr([p["self_sufficient"] for p in per], [p["median_T"] for p in per])
    summary = {"rules": {"deep": len(md), "shallow": len(ms)},
               "primary": ("undecided (fewer than 4 rules in a class)" if not enough else
                           "pass" if mw < 0.01 and ratio >= 3 else "fail"),
               "mannwhitney_p_shallow_slower": mw, "median_of_median_T": {"deep": float(np.median(md)) if md else None,
                                                                          "shallow": float(np.median(ms)) if ms else None},
               "ratio": ratio, "jumped": {"deep": [jd, nd], "shallow": [js, ns]},
               "secondary_deep_est_vs_T": {"rho": float(rho), "p": float(prho)},
               "secondary_selfsufficient_vs_T": {"rho": float(rho1), "p": float(prho1)}}
    return {"summary": summary, "per_rule": per, "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "pilot", "fresh", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-10-e72-fresh-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    if a.part == "soups":
        out = {"experiment": "E-72", "part": "soups"} | soups(a.workers, a.census)
        out["seconds"] = round(time.time() - t0)
        json.dump(out, open(a.out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
        print(json.dumps(out["summary"], indent=1, default=str))
        print("=== SENTINEL e72 soups DONE", flush=True)
        return
    if a.part == "pilot":
        jobs = [(1, h, 64) for h in (60, 64, 67, 68)]
    elif a.part == "fresh":
        jobs = fresh_rules()
    else:
        c = json.load(open("docs/data/experiments/2026-11-09-e70-census.json"))
        jobs = [(r["v"], r["h"], 64) for r in c["rules"] if r["class"] == "F"]
    with Pool(a.workers) as pool:
        res = pool.map(rule_job, jobs, chunksize=1)
    out = {"experiment": "E-72", "part": a.part, "G": G, "lineages": LINEAGES, "cap": CAP, "rules": res,
           "seconds": round(time.time() - t0)}
    if a.part == "fresh":
        out["picked"] = [[lab, r["v"], r["g"], r["h"]] for lab, r in pick(res)]
        out["F"] = sum(r["self_sufficient"] > 0 for r in res)
    json.dump(out, open(a.out, "w"), indent=1)
    for r in res:
        if r["self_sufficient"] or a.part != "fresh":
            print(json.dumps(r), flush=True)
    print(f"=== SENTINEL e72 {a.part} DONE", flush=True)


if __name__ == "__main__":
    main()
