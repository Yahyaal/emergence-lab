"""E-77: H1 with power. Discovery engine vs random search at equal compute, 20 master seeds, paired by seed.

Settings are those of E-03 to E-06 (`docs/experiments.md`): Life-like/Generations rules, 100 rules x 2 seeds per
generation, 6 generations, 96x96, 500 steps, 6 follow-ups (`emergence explore` defaults otherwise). Each (seed, arm)
is one `emergence explore` process with its own database under runs/e77/ (not committed); as soon as a run ends its
summary is written to runs/e77/<arm>-s<seed>.json, and a restart skips every (seed, arm) that already has one
(handoff pitfall "long multiprocessing runs must save as they go"). A database without a summary is an interrupted
run: it is deleted and the run starts again (runs are deterministic, so nothing changes).

Near-duplicates (D-013): the E-03 to E-06 analysis counted "only rules at least 2 mutations apart", but its code was
never committed. `distinct_greedy` re-implements it: the mutation distance between two outer-totalistic rules is the
number of single mutation steps (`OuterTotalistic.mutate`: flip one birth count, flip one survival count, or move C
by 1) that separate them, |B xor B'| + |S xor S'| + |C - C'|; rules are visited in exploration order (universe id)
and a rule is kept if it is at distance >= 2 from every rule already kept. Applied within each run, separately for
each outcome. It reproduces the published distinct counts of E-03 to E-06 exactly (J-087). Runs use --workers 2, 3 at a time
(results are identical to --workers 1: checked on a short run, J-087).

Usage:
    python scripts/h1_power.py run [--seeds 101-120] [--jobs 3] [--out runs/e77]
    python scripts/h1_power.py summarise runs/e77-repro/engine-s11.db      # one database, printed
    python scripts/h1_power.py analyse [--out runs/e77] [--json docs/data/experiments/....json]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from emergence.analysis import _rule_stats, experiment_summary  # noqa: E402
from emergence.physics.totalistic import OuterTotalistic  # noqa: E402
from emergence.storage import Store  # noqa: E402

SETTINGS = ["--generations", "6", "--steps", "500", "--followups", "6"]  # E-03 to E-06; other flags at defaults
ARMS = {"engine": [], "random": ["--baseline-random"]}
OUTCOMES = ["self_propelled", "complex_all_seeds", "structured"]


# --------------------------------------------------------------- near-duplicate removal
def mutation_distance(a: OuterTotalistic, b: OuterTotalistic) -> int:
    return len(a.birth ^ b.birth) + len(a.survive ^ b.survive) + abs(a.num_states - b.num_states)


def distinct_greedy(rules: list[str], min_dist: int = 2) -> list[str]:
    """Rules (in the given order) kept when each must be >= min_dist mutations from every rule kept before it."""
    kept: list[OuterTotalistic] = []
    out = []
    for r in rules:
        p = OuterTotalistic.parse(r)
        if all(mutation_distance(p, k) >= min_dist for k in kept):
            kept.append(p)
            out.append(r)
    return out


def n_components(rules: list[str]) -> int:
    """Alternative reading (reported, not used): clusters of rules linked by chains of single mutations."""
    ps = [OuterTotalistic.parse(r) for r in rules]
    parent = list(range(len(ps)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(ps)):
        for j in range(i):
            if mutation_distance(ps[i], ps[j]) <= 1:
                parent[find(i)] = find(j)
    return len({find(i) for i in range(len(ps))})


# --------------------------------------------------------------- one run's summary
def summarise(db: str) -> dict:
    st = Store(db)
    exps = st.experiments()
    assert len(exps) == 1, f"{db}: expected one experiment, found {len(exps)}"
    exp = exps[0]
    assert exp["status"] == "finished", f"{db}: status {exp['status']}"
    eid = exp["id"]
    summ = experiment_summary(st, eid)
    univ = st.universes(eid, role="explore")  # ORDER BY id = exploration order
    stats = [(u["spec"]["physics"]["rule"], _rule_stats(u)) for u in univ]
    gen0 = sorted(u["spec"]["physics"]["rule"] for u in univ if u["generation"] == 0)
    out = {"name": exp["name"], "seed": exp["master_seed"], "selection": summ["selection"], "config": exp["config"],
           "environment": exp["environment"], "rules": len(univ), "niches": summ["final"].get("niches", 0),
           "gen0_rules_sha": __import__("hashlib").sha256("\n".join(gen0).encode()).hexdigest()[:16],
           "raw": {}, "distinct": {}, "components": {}, "distinct_rules": {}}
    for k in OUTCOMES:
        hits = [r for r, s in stats if s[k]]
        d = distinct_greedy(hits)
        out["raw"][k] = len(hits)
        out["distinct"][k] = len(d)
        out["components"][k] = n_components(hits)
        out["distinct_rules"][k] = d
    disc = st.discoveries(eid)
    thr = {round(d["evidence"].get("robust_threshold"), 3) for d in disc if d["evidence"].get("robust_threshold")}
    out["robust_threshold"] = sorted(thr)
    out["discoveries"] = len(disc)
    out["curve"] = summ["curve"]
    return out


# --------------------------------------------------------------- driver
def parse_seeds(s: str) -> list[int]:
    out = []
    for part in s.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b) + 1)) if b else [int(a)]
    return out


def one_run(out: Path, seed: int, arm: str) -> str:
    res = out / f"{arm}-s{seed}.json"
    if res.exists():
        return f"skip {res.name}"
    db = out / f"{arm}-s{seed}.db"
    if db.exists():
        db.unlink()  # interrupted run: start again (deterministic)
    cmd = [sys.executable, "-m", "emergence", "--db", str(db), "explore", "--name", f"e77-{arm}-s{seed}",
           "--seed", str(seed), "--workers", "2", *SETTINGS, *ARMS[arm]]
    t0 = time.time()
    with open(out / f"{arm}-s{seed}.log", "w") as log:
        rc = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "PYTHONPATH": str(ROOT)}).returncode
    if rc != 0:
        return f"FAILED {arm}-s{seed} rc={rc}"
    s = summarise(str(db))
    s["wall_s"] = round(time.time() - t0, 1)
    s["command"] = " ".join(["emergence"] + cmd[3:])
    tmp = res.with_suffix(".tmp")
    tmp.write_text(json.dumps(s, indent=1))
    tmp.replace(res)
    return (f"done {arm}-s{seed} in {s['wall_s']:.0f}s: self-propelled {s['raw']['self_propelled']}/"
            f"{s['distinct']['self_propelled']}, complex {s['raw']['complex_all_seeds']}/"
            f"{s['distinct']['complex_all_seeds']}, niches {s['niches']}")


def run(a) -> None:
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(s, arm) for s in parse_seeds(a.seeds) for arm in ARMS]
    print(f"{len(jobs)} runs, {a.jobs} at a time, into {out}", flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        for msg in ex.map(lambda j: one_run(out, *j), jobs):
            print(time.strftime("%H:%M:%S"), msg, flush=True)
    print("ALL-RUNS-FINISHED", flush=True)


# --------------------------------------------------------------- statistics (by hand)
def signed_rank_exact(diffs: np.ndarray) -> dict:
    """One-sided (engine > random) Wilcoxon signed-rank test, exact. Zeros dropped (Wilcoxon's method), ties get
    mid-ranks; the null distribution of W+ is enumerated over all 2^n sign flips by dynamic programming on the
    doubled (integer) ranks."""
    d = diffs[diffs != 0]
    n = len(d)
    if n == 0:
        return {"n": 0, "W_plus": 0.0, "p": 1.0}
    a = np.abs(d)
    order = np.argsort(a, kind="stable")
    ranks = np.empty(n)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and a[order[j + 1]] == a[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    r2 = np.rint(2 * ranks).astype(int)
    w_obs = int(r2[d > 0].sum())
    dist = np.zeros(r2.sum() + 1)
    dist[0] = 1.0
    for r in r2:
        nxt = dist.copy()
        nxt[r:] += dist[:-r]
        dist = nxt
    dist /= dist.sum()
    return {"n": n, "W_plus": w_obs / 2, "p": float(dist[w_obs:].sum())}


def sign_test(diffs: np.ndarray) -> dict:
    from math import comb
    pos, neg = int((diffs > 0).sum()), int((diffs < 0).sum())
    n = pos + neg
    p = sum(comb(n, k) for k in range(pos, n + 1)) / 2 ** n if n else 1.0
    return {"positive": pos, "negative": neg, "ties": int((diffs == 0).sum()), "p": p}


def median_ratio(e: np.ndarray, r: np.ndarray) -> float:
    return float(np.median(e / np.maximum(r, 1)))  # random arm is never near 0 for these outcomes; guard only


def bootstrap_ci(e: np.ndarray, r: np.ndarray, n: int = 10_000, seed: int = 77) -> list[float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(e), size=(n, len(e)))
    ratios = np.median(e[idx] / np.maximum(r[idx], 1), axis=1)
    return [float(np.percentile(ratios, 2.5)), float(np.percentile(ratios, 97.5))]


def compare_outcome(e: np.ndarray, r: np.ndarray) -> dict:
    diff = e - r
    return {"engine_median": float(np.median(e)), "random_median": float(np.median(r)),
            "ratio_of_medians": float(np.median(e) / max(np.median(r), 1)),
            "median_ratio": median_ratio(e, r), "median_ratio_ci95": bootstrap_ci(e, r),
            "wilcoxon": signed_rank_exact(diff), "sign": sign_test(diff)}


def verdict(c: dict) -> str:
    p, m, hi = c["wilcoxon"]["p"], c["median_ratio"], c["median_ratio_ci95"][1]
    if p < 0.01 and m >= 1.5:
        return "pass"
    if p >= 0.05 or hi < 1.5:
        return "fail"
    return "undecided"


def analyse(a) -> None:
    out = ROOT / a.out
    seeds = parse_seeds(a.seeds)
    res = {arm: {s: json.loads((out / f"{arm}-s{s}.json").read_text()) for s in seeds
                 if (out / f"{arm}-s{s}.json").exists()} for arm in ARMS}
    paired = [s for s in seeds if s in res["engine"] and s in res["random"]]
    print(f"{len(paired)} paired seeds of {len(seeds)}")
    gen0_same = all(res["engine"][s]["gen0_rules_sha"] == res["random"][s]["gen0_rules_sha"] for s in paired)
    print(f"generation 0 identical within every seed: {gen0_same}")
    hdr = f"{'seed':>5} | {'self-prop raw/dist':>19} | {'complex raw/dist':>17} | {'niches':>7} | {'wall s':>11}"
    print(hdr + "\n" + " " * 6 + "| engine     random   | engine    random  | eng rnd | eng   rnd")
    for s in paired:
        E, R = res["engine"][s], res["random"][s]
        print(f"{s:>5} | {E['raw']['self_propelled']:>3}/{E['distinct']['self_propelled']:<3}  "
              f"{R['raw']['self_propelled']:>3}/{R['distinct']['self_propelled']:<3}       | "
              f"{E['raw']['complex_all_seeds']:>3}/{E['distinct']['complex_all_seeds']:<3} "
              f"{R['raw']['complex_all_seeds']:>3}/{R['distinct']['complex_all_seeds']:<3}    | "
              f"{E['niches']:>3} {R['niches']:>3} | {E['wall_s']:>5.0f} {R['wall_s']:>5.0f}")
    arr = lambda arm, f: np.array([float(f(res[arm][s])) for s in paired])  # noqa: E731
    tests = {}
    for name, f in [("distinct_self_propelled", lambda x: x["distinct"]["self_propelled"]),
                    ("distinct_complex_all_seeds", lambda x: x["distinct"]["complex_all_seeds"]),
                    ("niches", lambda x: x["niches"]),
                    ("raw_self_propelled", lambda x: x["raw"]["self_propelled"]),
                    ("raw_complex_all_seeds", lambda x: x["raw"]["complex_all_seeds"]),
                    ("distinct_structured", lambda x: x["distinct"]["structured"]),
                    ("raw_structured", lambda x: x["raw"]["structured"])]:
        tests[name] = compare_outcome(arr("engine", f), arr("random", f))
        c = tests[name]
        print(f"{name:<28} medians {c['engine_median']:>5.1f} vs {c['random_median']:>5.1f}; median ratio "
              f"{c['median_ratio']:.2f} [{c['median_ratio_ci95'][0]:.2f}, {c['median_ratio_ci95'][1]:.2f}]; "
              f"Wilcoxon p = {c['wilcoxon']['p']:.2e} (n={c['wilcoxon']['n']}); sign {c['sign']['positive']}+/"
              f"{c['sign']['negative']}-/{c['sign']['ties']}= p = {c['sign']['p']:.2e}")
    prim = tests["distinct_self_propelled"]
    v = verdict(prim) if len(paired) == len(seeds) else "incomplete"
    print(f"PRIMARY VERDICT: {v}")
    if a.json:
        thr = {arm: {s: res[arm][s]["robust_threshold"] for s in paired} for arm in ARMS}
        doc = {"label": "E-77 H1 power: engine vs random search, 20 seeds", "experiment": "E-77", "journal": "J-087",
               "code_commit": a.commit, "preregistration": "docs/data/e77-preregistration.md",
               "command": "python scripts/h1_power.py run --seeds 101-120 --jobs 3 --out runs/e77; "
                          "python scripts/h1_power.py analyse --out runs/e77 --json <this file> --commit <commit>",
               "per_run_command": "emergence --db runs/e77/<arm>-s<seed>.db explore --name e77-<arm>-s<seed> "
                                  "--seed <seed> --workers 2 --generations 6 --steps 500 --followups 6 "
                                  "[--baseline-random]",
               "config": res["engine"][paired[0]]["config"] | {"name": None, "seed": None, "selection": None},
               "environment": res["engine"][paired[0]]["environment"], "seeds": paired,
               "near_duplicates": "scripts/h1_power.py:distinct_greedy (mutation distance >= 2, exploration order)",
               "generation0_identical_within_seed": gen0_same, "tests": tests, "primary_verdict": v,
               "robust_threshold_per_run": thr,
               "runs": {arm: {s: {k: res[arm][s][k] for k in ("rules", "niches", "raw", "distinct", "components",
                                                                "discoveries", "wall_s")}
                              for s in paired} for arm in ARMS}}
        Path(a.json).write_text(json.dumps(doc, indent=1))
        print(f"wrote {a.json}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--seeds", default="101-120")
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--out", default="runs/e77")
    sm = sub.add_parser("summarise")
    sm.add_argument("db")
    an = sub.add_parser("analyse")
    an.add_argument("--seeds", default="101-120")
    an.add_argument("--out", default="runs/e77")
    an.add_argument("--json")
    an.add_argument("--commit", default="")
    a = ap.parse_args()
    if a.cmd == "run":
        run(a)
    elif a.cmd == "summarise":
        s = summarise(a.db)
        print(json.dumps({k: v for k, v in s.items() if k not in ("config", "environment", "curve",
                                                                   "distinct_rules")}, indent=1))
    else:
        analyse(a)
