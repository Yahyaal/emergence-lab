"""E-74 (docs/data/e74-preregistration.md): a larger, fresh confirmatory test of the five-generation F test (E-72).
Fresh rules from the E-72 family (variant v 1..5, head0 at g 1..127, head1 at g + 60..68 mod 128) that no earlier
census or soup used; one-generation census plus 5-generation depth (bff_multigen.rule_job); up to 12 F-deep and 12
F-shallow rules, 6 soups each. Each soup is timed three ways at checkpoints every 50 rounds:
  D-050  copiers (classify_shift, 60/64) among the 40 most common distinct programs: T = first checkpoint with >= 1
         copier whose checkpoint 1,000 rounds later has >= 10
  D-053  the same with classify_fid (58/64 + 75% instruction-fidelity guard)
  HOE    T = first of 3 consecutive checkpoints with high-order entropy >= 2 (D-052)
up to 16,000 rounds (a soup stops when all three are found).

    PYTHONPATH=scripts python scripts/bff_deepconfirm.py --part census --workers 11 --out docs/data/experiments/2026-11-11-e74-census.json
    PYTHONPATH=scripts python scripts/bff_deepconfirm.py --part soups --workers 11 --out docs/data/experiments/2026-11-12-e74-soups.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_fidelity as FID  # noqa: E402
import bff_kernels as K  # noqa: E402
import bff_multigen as MG  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

N, WAIT, AFTER, MIN_COP, EVERY, HOE_MIN, HOE_RUN = 2 ** 14, 16000, 1000, 10, 50, 2.0, 3
NFRESH, NPICK, SOUPS = 600, 12, 6
RUN = Path("runs/e74")
CENSUS = "docs/data/experiments/2026-11-11-e74-census.json"
E72_CENSUS = "docs/data/experiments/2026-11-10-e72-fresh-census.json"


def fresh_rules() -> list[tuple[int, int, int, int]]:
    """NFRESH rules of the E-72 family, none in the E-72 census (which holds every earlier g > 0 rule)."""
    used = {(r["v"], r["h"], r["g"]) for r in json.load(open(E72_CENSUS))["rules"]}
    rng = np.random.default_rng(74)
    out = set()
    while len(out) < NFRESH:
        v, g, d = int(rng.integers(1, 6)), int(rng.integers(1, 128)), int(rng.integers(60, 69))
        h = (g + d) % 128
        if (v, h, g) not in used:
            out.add((v, h, 64, g))
    return sorted(out)


def pick(census: list[dict]) -> list[tuple[str, dict]]:
    rng = np.random.default_rng(740)
    F = [r for r in census if r["self_sufficient"] > 0]
    sel = []
    for lab, grp in (("deep", [r for r in F if r["deep_est"] >= 1]), ("shallow", [r for r in F if r["deep_est"] < 1])):
        for i in sorted(rng.permutation(len(grp))[:NPICK]):
            sel.append((lab, grp[int(i)]))
    return sel


def copy_jump(cop: dict, e: int):
    return e - AFTER if cop[e] >= MIN_COP and cop.get(e - AFTER, 0) >= 1 else None


def soup_job(arg) -> dict:
    seed, code = arg
    path = RUN / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    C.H1 = code
    soup = C.CounterfactualSoup(n=N, length=64, seed=seed)
    old, new, hoe, series = {}, {}, [], []
    T = {"d050": None, "d053": None, "hoe": None}
    while soup.epochs < WAIT and None in T.values():
        soup.epoch()
        e = soup.epochs
        if e % EVERY:
            continue
        X = np.array(C.distinct_top(soup.programs))
        s = 680 + seed + e
        old[e] = int((K.classify_shift(X, code, 4, s)[0] > 0).sum())
        new[e] = int((K.classify_fid(X, code, 4, s, thr=FID.THR, opmin=FID.OPMIN)[0] > 0).sum())
        h = float(B.high_order_entropy(soup.programs))
        hoe.append((e, h))
        series.append([e, old[e], new[e], round(h, 3)])
        if T["d050"] is None:
            T["d050"] = copy_jump(old, e)
        if T["d053"] is None:
            T["d053"] = copy_jump(new, e)
        if T["hoe"] is None and len(hoe) >= HOE_RUN and all(x >= HOE_MIN for _, x in hoe[-HOE_RUN:]):
            T["hoe"] = hoe[-HOE_RUN][0]
    res = {"seed": seed, "code": code, "T": T, "end": soup.epochs, "series": series, "sec": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    print(json.dumps({"seed": seed, "code": code, "T": T, "sec": res["sec"]}), flush=True)
    return res


def med(ts) -> float:
    return float(np.median([t if t is not None else WAIT for t in ts]))


def analyse(sel, res) -> dict:
    by = {r["seed"]: r for r in res}
    per = []
    for k, (lab, r) in enumerate(sel):
        Ts = [by[7400 + 10 * k + i]["T"] for i in range(SOUPS)]
        per.append({"class": lab, "v": r["v"], "g": r["g"], "h": r["h"], "self_sufficient": r["self_sufficient"],
                    "deep_est": r["deep_est"], "copiers": r["copiers"],
                    **{f"T_{d}": [t[d] for t in Ts] for d in ("d050", "d053", "hoe")},
                    **{f"median_{d}": med([t[d] for t in Ts]) for d in ("d050", "d053", "hoe")}})
    nd = sum(p["class"] == "deep" for p in per)
    ns = sum(p["class"] == "shallow" for p in per)
    out = {"rules": {"deep": nd, "shallow": ns}}
    enough = nd >= 6 and ns >= 6
    for d in ("d050", "d053", "hoe"):
        md = [p[f"median_{d}"] for p in per if p["class"] == "deep"]
        ms = [p[f"median_{d}"] for p in per if p["class"] == "shallow"]
        if not enough:
            out[d] = {"verdict": "undecided"}
            continue
        mw = float(mannwhitneyu(ms, md, alternative="greater").pvalue)
        ratio = float(np.median(ms) / max(np.median(md), EVERY))
        out[d] = {"median_of_medians": {"deep": float(np.median(md)), "shallow": float(np.median(ms))},
                  "ratio": ratio, "mannwhitney_p": mw, "pass": bool(mw < 0.01 and ratio >= 3),
                  "jumped": {c: sum(t is not None for p in per if p["class"] == c for t in p[f"T_{d}"])
                             for c in ("deep", "shallow")},
                  "deep_est_vs_T": [float(x) for x in spearmanr([p["deep_est"] for p in per],
                                                                [p[f"median_{d}"] for p in per])],
                  "ss_vs_T": [float(x) for x in spearmanr([p["self_sufficient"] for p in per],
                                                          [p[f"median_{d}"] for p in per])]}
    if not enough:
        out["primary"] = "undecided (fewer than 6 rules in a class)"
    else:
        a, b = out["d053"]["pass"], out["hoe"]["pass"]
        out["primary"] = "pass" if a and b else "fail" if not a and not b else "unresolved (D-053 and HOE disagree)"
    return {"summary": out, "per_rule": per}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    if a.part == "census":
        with Pool(a.workers) as pool:
            res = pool.map(MG.rule_job, fresh_rules(), chunksize=1)
        sel = pick(res)
        out = {"experiment": "E-74", "part": "census", "G": MG.G, "lineages": MG.LINEAGES, "cap": MG.CAP,
               "F": sum(r["self_sufficient"] > 0 for r in res),
               "F_deep": sum(r["self_sufficient"] > 0 and r["deep_est"] >= 1 for r in res),
               "picked": [[lab, r["v"], r["g"], r["h"]] for lab, r in sel], "rules": res,
               "seconds": round(time.time() - t0)}
        json.dump(out, open(a.out, "w"), indent=1)
        print(json.dumps({k: out[k] for k in ("F", "F_deep", "picked", "seconds")}))
        print("=== SENTINEL e74 census DONE", flush=True)
        return
    sel = pick(json.load(open(CENSUS))["rules"])
    RUN.mkdir(parents=True, exist_ok=True)
    jobs = [(7400 + 10 * k + i, r["code"]) for k, (_, r) in enumerate(sel) for i in range(SOUPS)]
    jobs.sort(key=lambda j: j[0] % 10)  # interleave rules so slow rules spread across workers
    with Pool(a.workers) as pool:
        res = pool.map(soup_job, jobs, chunksize=1)
    out = {"experiment": "E-74", "part": "soups"} | analyse(sel, res)
    out["results"], out["seconds"] = res, round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(json.dumps(out["summary"], indent=1, default=str))
    print("=== SENTINEL e74 soups DONE", flush=True)


if __name__ == "__main__":
    main()
