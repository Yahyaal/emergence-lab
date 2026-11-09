"""E-68 (docs/data/e68-preregistration.md): the tape-length family. Programs of L bytes (tape 2L), L in 16, 32,
64, 128; head1 starts at h1 in 0..2L-1, head0 at 0. Does the 'copy that copies' predictor (F rules, E-61-E-65)
carry over to other program lengths, and do F rules sit half a tape apart (h1 near L) at every length?

Part A: the E-61 shift-aware census (bff_shift_census.census_rule, unchanged) for every (L, h1) after
bff_kernels.set_length(L); L = 64 replays E-61 exactly (equivalence check).
Part B: soups of 2^14 programs of L bytes in F and non-F rules, copier-based jump criterion (D-050).

    python scripts/bff_tapelength.py --part census --workers 11 --out docs/data/experiments/2026-11-09-e68-census.json
    python scripts/bff_tapelength.py --part soups --workers 11 --out docs/data/experiments/2026-11-09-e68-soups.json
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
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402
import bff_shift_census as S  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

LENGTHS = (16, 32, 64, 128)
E61 = "docs/data/experiments/2026-11-08-e61-census.json"
RUN = Path("runs/e68")
N, WAIT, AFTER, EVERY, MIN_COP, NF, NS, SOUPS = 2 ** 14, 16000, 1000, 250, 10, 3, 3, 4


def census_job(arg) -> dict:
    L, h = arg
    K.set_length(L)
    r = S.census_rule(h)
    return {"L": L} | r


def census(workers: int) -> dict:
    jobs = [(L, h) for L in sorted(LENGTHS, reverse=True) for h in range(2 * L)]
    with Pool(workers) as pool:
        res = sorted(pool.map(census_job, jobs, chunksize=1), key=lambda r: (r["L"], r["h"]))
    old = {r["h"]: r for r in json.load(open(E61))["rules"]}
    eq = all((r["copiers"], r["self_sufficient"], r["class"]) == (old[r["h"]]["copiers"], old[r["h"]]["self_sufficient"],
                                                                  old[r["h"]]["class"]) for r in res if r["L"] == 64)
    per = {}
    for L in LENGTHS:
        rs = [r for r in res if r["L"] == L]
        F = [r["h"] for r in rs if r["class"] == "F"]
        per[L] = {"F": F, "S": [r["h"] for r in rs if r["class"] == "S" and r["copiers"] > 0],
                  "none": [r["h"] for r in rs if r["copiers"] == 0],
                  "L_is_F": L in F, "F_near_L": all(abs(h - L) <= L // 8 for h in F),
                  "self_sufficient_orientation": sorted({o for r in rs if r["class"] == "F"
                                                         for o in r["self_sufficient_orientation"]})}
    p1 = all(per[L]["L_is_F"] and per[L]["F_near_L"] for L in LENGTHS)
    return {"rules": res, "per_L": per, "equivalence_L64_vs_E61": eq, "primary1": "pass" if p1 else "fail"}


def soup_job(arg) -> dict:
    """D-050: every EVERY rounds count shift-aware copiers (own rule, own L) among the 40 most common distinct
    programs; T = the first checkpoint with >= 1 copier whose checkpoint AFTER rounds later has >= MIN_COP.
    No HOE gate (its threshold is calibrated for L = 64 only); HOE is recorded."""
    seed, L, h1 = arg
    path = RUN / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    K.set_length(L)
    C.H1 = h1
    t0 = time.time()
    soup = C.CounterfactualSoup(n=N, length=L, seed=seed)
    series, cop, T = [], {}, None
    while soup.epochs < WAIT:
        st = soup.epoch()
        e = soup.epochs
        if e % EVERY == 0:
            o = S.orient_shift(soup.programs, h1, 680 + seed + e)
            cop[e] = o["forward"] + o["reverse"] + o["both"]
            series.append({"epoch": e, "copiers": cop[e], "hoe": round(B.high_order_entropy(soup.programs), 3),
                           "steps_per_pair": round(st / (N / 2), 1)})
            if cop[e] >= MIN_COP and cop.get(e - AFTER, 0) >= 1:
                T = e - AFTER
                break
    o = S.orient_shift(soup.programs, h1, 681 + seed)
    res = {"seed": seed, "L": L, "h1": h1, "T": T, "jumped": T is not None, "end": soup.epochs, "orientation": o,
           "series": series, "sec": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    print(json.dumps({"done": seed, "L": L, "h1": h1, "T": T, "end": soup.epochs, "sec": res["sec"],
                      "orientation": {k: v for k, v in o.items() if k != "copiers"}}), flush=True)
    return res


def fisher(jf: int, nf: int, js: int, ns: int) -> float:
    m, tot = jf + js, nf + ns
    return sum(comb(m, x) * comb(tot - m, nf - x) for x in range(jf, min(m, nf) + 1)) / comb(tot, nf)


def pick(census_path: str) -> list[tuple[str, int, int]]:
    c = json.load(open(census_path))
    rng = np.random.default_rng(680)
    rules = []
    for L in LENGTHS:
        p = c["per_L"][str(L)]
        if L == 64:  # E-61-E-65 already tested h = 64's neighbours; only h1 = L here, for the length comparison
            rules.append(("F", L, L))
            continue
        F = list(p["F"])
        f = [L] if L in F else []
        rest = [h for h in F if h != L]
        f += sorted(int(x) for x in rng.choice(rest, min(NF - len(f), len(rest)), replace=False)) if rest else []
        s = list(p["S"])
        sel = sorted(int(x) for x in rng.choice(s, min(NS, len(s)), replace=False)) if s else []
        if len(sel) < NS:  # fill with rules that have no short copier at all
            sel += sorted(int(x) for x in rng.choice(p["none"], NS - len(sel), replace=False))
        rules += [("F", L, h) for h in f] + [("N", L, h) for h in sel]
    return rules


def soups(workers: int, census_path: str) -> dict:
    rules = pick(census_path)
    jobs = [(6800 + 10 * r + i, L, h) for r, (_, L, h) in enumerate(rules) for i in range(SOUPS)]
    RUN.mkdir(parents=True, exist_ok=True)
    jobs.sort(key=lambda j: -j[1])  # long tapes first
    with Pool(workers) as pool:
        res = pool.map(soup_job, jobs, chunksize=1)
    cls = {(L, h): k for k, L, h in rules}
    out = {"rules": [list(r) for r in rules]}
    test = [r for r in res if r["L"] != 64]
    j = {k: sum(r["jumped"] for r in test if cls[(r["L"], r["h1"])] == k) for k in ("F", "N")}
    n = {k: sum(cls[(r["L"], r["h1"])] == k for r in test) for k in ("F", "N")}
    p = fisher(j["F"], n["F"], j["N"], n["N"])
    by_L = {}
    for L in LENGTHS:
        rl = [r for r in res if r["L"] == L]
        by_L[L] = {k: [sum(r["jumped"] for r in rl if cls[(L, r["h1"])] == k), sum(cls[(L, r["h1"])] == k for r in rl)]
                   for k in ("F", "N")}
        by_L[L]["per_rule"] = {h: {"class": cls[(L, h)], "T": [r["T"] for r in rl if r["h1"] == h]}
                               for h in sorted({r["h1"] for r in rl})}
    each = all(by_L[L]["F"][0] >= by_L[L]["N"][0] for L in LENGTHS if L != 64)
    ok = j["F"] >= 0.75 * n["F"] and j["N"] <= 0.25 * n["N"] and p < 0.01 and each
    diag = [r for r in res if r["h1"] == r["L"]]
    Ts = [r["T"] if r["jumped"] else WAIT for r in diag]
    rho, prho = spearmanr([r["L"] for r in diag], Ts)
    out["summary"] = {"jumped": j, "of": n, "fisher_p": p, "F_ge_N_each_L": each, "primary2": "pass" if ok else "fail",
                      "by_L": by_L, "secondary_T_vs_L_at_h1_eq_L": {"rho": float(rho), "p_two_sided": float(prho),
                                                                   "T": {L: [r["T"] for r in diag if r["L"] == L]
                                                                         for L in LENGTHS}}}
    out["results"] = res
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-09-e68-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-68", "part": a.part} | (census(a.workers) if a.part == "census" else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rules")}, indent=1, default=str))
    print(f"=== SENTINEL e68 {a.part} DONE", flush=True)


if __name__ == "__main__":
    main()
