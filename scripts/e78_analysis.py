"""E-78 analysis (docs/data/e78-preregistration.md), written and committed before the main run.

1. Late candidates: in each arm's final snapshot (fork + 20,000), the 40 most common distinct programs
   (bff_long_analysis.distinct_top, as E-54); each gets the replicator test repeated 10 times
   (program_parasites.alone_test, D-049). Verified = at least one of the 10 repeats is "replicator". Late group =
   the first 6 verified programs in order of abundance. Same procedure in M, S and Mp.
2. Early group: E-54's 6 early programs per soup (T + 2000).
3. Invasion (program_fitness.invasion unchanged: 64 copies, 4,096 programs, 16 rounds, 16 replicates, reverse
   counted), kin rule < 0.1% (either orientation, >= 90%). Backgrounds: the ORIGINAL E-54 run's T + 10000
   (primary) and T + 20000 snapshots (early and the three late groups); reciprocal transplant: late S into the M
   arm's final soup and late M into the S arm's final soup, with the early group in both as reference.
4. Parasites: D-048 parasite_test (partner pool = that arm's final snapshot) on top-40 programs whose generation 1
   never grew in the 10 repeats; a parasite verdict is confirmed by a second run with an independent seed.
5. Statistics and verdicts as pre-registered; descriptive trajectories from the run's state files.

    python scripts/e78_analysis.py --workers 11 --e54 /path/to/runs/e54 --out docs/data/experiments/<date>-e78-spatial.json
    python scripts/e78_analysis.py --dry ...   # code-path check on fork snapshots, tiny settings (not data)
"""
from __future__ import annotations

import argparse
import functools
import itertools
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import t as tdist

sys.path.insert(0, str(Path(__file__).parent))
import bff_long_analysis as LA  # noqa: E402
import bff_spatial as BS  # noqa: E402
import e78_run as R  # noqa: E402

from emergence.observatory import program_fitness as F  # noqa: E402
from emergence.observatory import program_parasites as PP  # noqa: E402

E54X = Path("docs/data/experiments/2026-11-08-e54-long-soups.json")
K, MAX_TRY, REPS_INV, REPEATS, KIN_MAX, MIN_GROUP, DELTA_STAR, NPERM = 6, 40, 16, 10, 0.001, 2, 0.28, 10000
ARMS = ("M", "S", "Mp")
GCODE = {"early": 0, "M": 1, "S": 2, "Mp": 3}
BGCODE = {"orig10": 0, "orig20": 1, "finM": 2, "finS": 3}
CFG = {"run": R.RUN, "e54": BS.E54, "dry": False, "soups": list(BS.JUMPED)}


def final_epoch(seed: int) -> int:
    return BS.JUMPED[seed] + BS.FORK_DT + (0 if CFG["dry"] else R.H)


@functools.lru_cache(maxsize=48)
def load(kind: str, seed: int) -> np.ndarray:
    T = BS.JUMPED[seed]
    if kind == "orig10":
        return np.load(Path(CFG["e54"]) / f"{seed}-{T + 10000}.npy")
    if kind == "orig20":
        return np.load(Path(CFG["e54"]) / f"{seed}-{T + 20000}.npy")
    arm = {"finM": "M", "finS": "S", "finMp": "Mp"}[kind]
    if CFG["dry"]:  # code-path check only: every "final" soup is the fork snapshot
        return np.load(Path(CFG["e54"]) / f"{seed}-{T + BS.FORK_DT}.npy")[BS.placement(seed)]
    return np.load(Path(CFG["run"]) / f"{seed}-{arm}-{final_epoch(seed)}.npy")


def prog(h: str) -> np.ndarray:
    return np.frombuffer(bytes.fromhex(h), np.uint8).copy()


def early_programs() -> dict[int, list[str]]:
    inv = json.load(open(E54X))["invasion"]
    out = {}
    for s, T in BS.JUMPED.items():
        rows = sorted({(r["index"], r["program"]) for r in inv if r["seed"] == s and r["group"] == "early"})
        out[s] = [h for _, h in rows]
    return out


def _alone(arg):
    seed, arm, rank, h = arg
    r = PP.alone_test(prog(h), np.random.default_rng([78, 1, seed, GCODE[arm], rank]), REPEATS)
    return {"seed": seed, "arm": arm, "rank": rank, "program": h, "gen1_ok": r["gen1_ok"], "verdicts": r["verdicts"]}


def _invade(arg):
    seed, group, idx, h, bg = arg
    x = prog(h)
    P = load(bg, seed)
    r = F.invasion(x, P, np.random.default_rng([78, 2, seed, GCODE[group], idx, BGCODE[bg]]), alts=[x[::-1]],
                   reps=REPS_INV)
    return {"seed": seed, "group": group, "index": idx, "program": h, "background": bg, "kin": LA.kin(x, P)} | r


def _parasite(arg):
    seed, arm, rank, h, rep = arg
    P = load("fin" + arm, seed)
    r = PP.parasite_test(prog(h), P, np.random.default_rng([78, 3 + rep, seed, GCODE[arm], rank]),
                         alone="no replication")
    r.pop("hosts")
    return {"seed": seed, "arm": arm, "rank": rank, "program": h, "repeat": rep} | r


def cached_map(pool, fn, jobs, cache: Path, key):
    done = {}
    if cache.exists():
        for line in cache.read_text().splitlines():
            r = json.loads(line)
            done[key(r)] = r
    todo = [j for j in jobs if key_of_job(fn, j) not in done]
    print(f"{cache.name}: {len(done)} cached, {len(todo)} to run", flush=True)
    with cache.open("a") as f:
        for i, r in enumerate(pool.imap_unordered(fn, todo, chunksize=1)):
            done[key(r)] = r
            f.write(json.dumps(r) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"  {cache.name} {i}/{len(todo)}", flush=True)
    return [done[key_of_job(fn, j)] for j in jobs]


def key_of_job(fn, j):
    if fn is _alone:
        return (j[0], j[1], j[2])
    if fn is _invade:
        return (j[0], j[1], j[2], j[4])
    return (j[0], j[1], j[2], j[4])


# ---- statistics ---------------------------------------------------------------------------------

def signflip(d, two_sided: bool = False) -> float:
    d = np.asarray(d, float)
    S = np.array(list(itertools.product([-1, 1], repeat=len(d))))
    tot = (S * np.abs(d)).sum(1)
    if two_sided:
        return float((np.abs(tot) >= abs(d.sum()) - 1e-12).mean())
    return float((tot >= d.sum() - 1e-12).mean())


def t_ci(d) -> list[float]:
    d = np.asarray(d, float)
    h = tdist.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return [float(d.mean() - h), float(d.mean() + h)]


def group_scores(inv, seed, group, bg):
    rr = [r for r in inv if r["seed"] == seed and r["group"] == group and r["background"] == bg]
    kept = [r["s"] for r in rr if r["kin"] < KIN_MAX]
    return np.array(kept), len(rr) - len(kept)


def deltas(inv, bg, late_groups=ARMS, early_bg=None, soups=None):
    """Per soup: Delta_A = mean s(late_A) - mean s(early) in background bg (None if a group has < 2)."""
    out, dropped = {}, 0
    for s in soups or CFG["soups"]:
        e, de = group_scores(inv, s, "early", early_bg or bg)
        dropped += de
        row = {}
        for g in late_groups:
            l, dl = group_scores(inv, s, g, bg if not isinstance(bg, dict) else bg[g])
            dropped += dl
            row[g] = float(l.mean() - e.mean()) if len(l) >= MIN_GROUP and len(e) >= MIN_GROUP else None
            row[f"n_{g}"] = len(l)
        row["n_early"] = len(e)
        out[s] = row
    return out, dropped


def primary_test(D: dict, soups: list[int]) -> dict:
    ok = [s for s in soups if all(D[s][a] is not None for a in ARMS)]
    d = np.array([D[s]["S"] - D[s]["M"] for s in ok])
    nul = np.array([D[s]["Mp"] - D[s]["M"] for s in ok])
    if len(ok) < 3:
        return {"soups": ok, "verdict": "undecided (too few soups)"}
    p, pn = signflip(d), signflip(nul, two_sided=True)
    ci = t_ci(d)
    if p < 0.05 and d.mean() > 0 and pn >= 0.05:
        verdict = "pass"
    elif ci[1] < DELTA_STAR:
        verdict = "fail"
    else:
        verdict = "undecided"
    return {"soups": ok, "d": {str(s): round(float(v), 4) for s, v in zip(ok, d)}, "mean_d": round(float(d.mean()), 4),
            "p_one_sided": p, "ci95_mean_d": [round(v, 4) for v in ci], "null_d": {str(s): round(float(v), 4) for s, v in zip(ok, nul)},
            "mean_null_d": round(float(nul.mean()), 4), "p_null_two_sided": pn,
            "sd_d": round(float(d.std(ddof=1)), 4), "sd_null_d": round(float(nul.std(ddof=1)), 4), "verdict": verdict}


def within_arm(inv, bg, arm, rng) -> dict:
    """E-54's test: D = sum over soups of (mean late - mean early), within-soup label permutation, one-sided."""
    cells = {}
    for s in CFG["soups"]:
        e, _ = group_scores(inv, s, "early", bg)
        l, _ = group_scores(inv, s, arm, bg)
        if len(e) >= MIN_GROUP and len(l) >= MIN_GROUP:
            cells[s] = (e, l)
    if not cells:
        return {"D": None}
    D, p = LA.perm_D(cells, rng) if not CFG["dry"] else (sum(np.mean(l) - np.mean(e) for e, l in cells.values()), None)
    return {"D": round(float(D), 4), "p_one_sided": p, "soups": len(cells)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--e54", default=str(BS.E54))
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    global K, MAX_TRY, REPS_INV, REPEATS, NPERM
    CFG["e54"] = Path(a.e54)
    work = Path("runs/e78/analysis")
    if a.dry:
        CFG["dry"], CFG["soups"] = True, [5410, 5401, 5308]
        K, MAX_TRY, REPS_INV, REPEATS = 2, 4, 2, 2
        work = Path("runs/e78/dry")
    work.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    early = early_programs()
    with Pool(a.workers) as pool:
        jobs = [(s, arm, rank, bytes(x).hex()) for s in CFG["soups"] for arm in ARMS
                for rank, x in enumerate(LA.distinct_top(load("fin" + arm, s))[:MAX_TRY])]
        alone = cached_map(pool, _alone, jobs, work / "alone.jsonl", lambda r: (r["seed"], r["arm"], r["rank"]))
        late = {}
        for r in sorted(alone, key=lambda r: r["rank"]):
            if "replicator" in r["verdicts"] and len(late.setdefault((r["seed"], r["arm"]), [])) < K:
                late[(r["seed"], r["arm"])].append(r["program"])
        inv_jobs = []
        for s in CFG["soups"]:
            for i, h in enumerate(early[s][:K]):
                inv_jobs += [(s, "early", i, h, bg) for bg in ("orig10", "orig20", "finM", "finS")]
            for arm in ARMS:
                for i, h in enumerate(late.get((s, arm), [])):
                    inv_jobs += [(s, arm, i, h, bg) for bg in ("orig10", "orig20")]
            for i, h in enumerate(late.get((s, "S"), [])):
                inv_jobs.append((s, "S", i, h, "finM"))
            for i, h in enumerate(late.get((s, "M"), [])):
                inv_jobs.append((s, "M", i, h, "finS"))
        inv = cached_map(pool, _invade, inv_jobs, work / "invasion.jsonl",
                         lambda r: (r["seed"], r["group"], r["index"], r["background"]))
        pj = [(r["seed"], r["arm"], r["rank"], r["program"], 0) for r in alone if r["gen1_ok"] == 0]
        para = cached_map(pool, _parasite, pj, work / "parasites.jsonl",
                          lambda r: (r["seed"], r["arm"], r["rank"], r["repeat"]))
        cj = [(r["seed"], r["arm"], r["rank"], r["program"], 1) for r in para if r["verdict"] == "parasite"]
        conf = cached_map(pool, _parasite, cj, work / "parasites.jsonl",
                          lambda r: (r["seed"], r["arm"], r["rank"], r["repeat"])) if cj else []
    rng = np.random.default_rng(78)
    res = {"settings": {"K": K, "MAX_TRY": MAX_TRY, "REPS_INV": REPS_INV, "REPEATS": REPEATS, "KIN_MAX": KIN_MAX,
                        "DELTA_STAR": DELTA_STAR, "dry": CFG["dry"], "soups": CFG["soups"]}}
    for bg, name in (("orig10", "primary"), ("orig20", "secondary_T20000")):
        D, dropped = deltas(inv, bg)
        res[name] = {"background": bg, "kin_dropped": dropped,
                     "delta": {str(s): {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}
                               for s, r in D.items()},
                     "test": primary_test(D, CFG["soups"]),
                     "without_5410": primary_test(D, [s for s in CFG["soups"] if s != 5410]),
                     "without_5401": primary_test(D, [s for s in CFG["soups"] if s != 5401]),
                     "within_arm": {arm: within_arm(inv, bg, arm, rng) for arm in ARMS}}
    # reciprocal transplant: late S in the M final soup, late M in the S final soup, early in both as reference
    rec = {}
    for s in CFG["soups"]:
        row = {}
        for late_arm, bg in (("S", "finM"), ("M", "finS")):
            e, de = group_scores(inv, s, "early", bg)
            l, dl = group_scores(inv, s, late_arm, bg)
            row[f"{late_arm}_in_{bg}"] = round(float(l.mean() - e.mean()), 4) if len(l) >= MIN_GROUP and len(e) >= MIN_GROUP else None
            row[f"mean_early_{bg}"] = round(float(e.mean()), 4) if len(e) else None
            row[f"mean_late_{late_arm}_{bg}"] = round(float(l.mean()), 4) if len(l) else None
            row[f"kin_dropped_{bg}"] = de + dl
        rec[str(s)] = row
    ok = [s for s in rec if rec[s]["S_in_finM"] is not None and rec[s]["M_in_finS"] is not None]
    rd = [rec[s]["S_in_finM"] - rec[s]["M_in_finS"] for s in ok]
    res["reciprocal"] = {"per_soup": rec, "soups": ok, "mean_S_in_finM": round(float(np.mean([rec[s]["S_in_finM"] for s in ok])), 4) if ok else None,
                         "mean_M_in_finS": round(float(np.mean([rec[s]["M_in_finS"] for s in ok])), 4) if ok else None,
                         "p_two_sided_difference": signflip(rd, True) if len(ok) >= 2 else None}
    vc = {arm: Counter(r["verdict"] for r in para if r["arm"] == arm) for arm in ARMS}
    confirmed = [r for r in conf if r["verdict"] == "parasite"]
    res["parasites"] = {
        "alone_verdicts": {arm: dict(Counter(v for r in alone if r["arm"] == arm for v in r["verdicts"])) for arm in ARMS},
        "self_copier_frac": {arm: round(float(np.mean([r["gen1_ok"] > 0 for r in alone if r["arm"] == arm])), 4) for arm in ARMS},
        "never_grew": {arm: sum(r["gen1_ok"] == 0 for r in alone if r["arm"] == arm) for arm in ARMS},
        "verdicts": {arm: dict(v) for arm, v in vc.items()},
        "confirmed": [{k: r[k] for k in ("seed", "arm", "rank", "program")} for r in confirmed],
        "soups_with_confirmed": {arm: sorted({r["seed"] for r in confirmed if r["arm"] == arm}) for arm in ARMS}}
    res["candidates"] = {f"{s}/{arm}": len(late.get((s, arm), [])) for s in CFG["soups"] for arm in ARMS}
    if not CFG["dry"]:
        traj = {}
        for s in CFG["soups"]:
            for arm in ARMS:
                st = json.loads((Path(CFG["run"]) / f"{s}-{arm}-{final_epoch(s)}.state.json").read_text())
                traj[f"{s}/{arm}"] = {"summaries": st["summaries"], "series": st["series"], "resumed": st["resumed"]}
        res["trajectories"] = traj
    res["seconds"] = round(time.time() - t0)
    out = {"experiment": "E-78" + (" DRY RUN (not data)" if CFG["dry"] else ""), "summary": res,
           "late_programs": {f"{s}/{a}": v for (s, a), v in late.items()}, "alone": alone, "invasion": inv,
           "parasites": para + conf}
    Path(a.out).write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(json.dumps({k: v for k, v in res.items() if k != "trajectories"}, indent=1, default=str))
    print("=== E78 ANALYSIS DONE", flush=True)


if __name__ == "__main__":
    main()
