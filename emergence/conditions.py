"""Initial-conditions study: does WHERE matter starts change what a fixed rule produces?

Design (fixed before running, so the analysis can't be tuned to the results):
* a panel of rules x a set of initial conditions (engine.INIT_KINDS) x seeds
* each universe gets the standard observation (lab.study), a passive innovation
  profile over the same horizon, and, if it shows innovation that has not ended, a
  knockout test of whether later novelty depends on its first mid-run novelty
* primary outcomes per rule and condition (seed means):
    unsettled   fraction of seeds still not settled at the horizon
    self_prop   self-propelled shape types
    innovating  fraction of seeds with verdict "still innovating"
* each condition is compared with "uniform" for the SAME rule (paired), using a
  two-sided sign test across rules and a bootstrap 95% CI of the mean difference.

Results are stored as an experiment (role "condition") so the dashboard can replay them.
"""
from __future__ import annotations

import json
import math
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Callable

import numpy as np

from .discovery import _evaluate, environment_info, innovation_verdict, movers, run_settled
from .engine import Universe, UniverseSpec
from .observatory.innovation import innovation_profile
from .observatory.knockout import knockout_experiment
from .physics import OuterTotalistic
from .storage import Store

DEFAULT_INITS = ["uniform", "gradient", "patch", "spots"]
OUTCOMES = ["unsettled", "self_prop", "innovating"]


def _job(job: tuple[dict, int, int]) -> dict[str, Any]:
    spec_d, steps, window = job
    res = _evaluate((spec_d, steps, window))
    every = max(25, steps // 32)
    inn = innovation_profile(Universe.from_spec(UniverseSpec.from_dict(spec_d)), steps=steps, every=every)
    as_ext = {"cls": res["cls"], "metrics": res["metrics"]}
    verdict, _ = innovation_verdict({"innovation": inn}, as_ext, 0, res["metrics"].get("damage_norm"))
    ko = None
    if inn["established_late"] > 0 and not (res["metrics"]["cycle_found"] or run_settled(res["metrics"], res["cls"])):
        curve, q = inn["new_per_sample"], len(inn["new_per_sample"]) // 4
        mids = [i for i in range(q, 3 * q) if curve[i] > 0]
        if mids:
            t1 = mids[0] * every
            rng = np.random.default_rng([spec_d["seed"], 31])
            ko = knockout_experiment(Universe.from_spec(UniverseSpec.from_dict(spec_d)), t1,
                                     horizon=min(1000, steps - t1), every=every, rng=rng)
    res["extra"] = {"innovation": inn, "innovation_verdict": verdict, "knockout": ko}
    return res


def run_conditions(store: Store, rules: list[str], inits: list[str], seeds: int, size: int, steps: int,
                   density: float = 0.35, name: str = "conditions", master_seed: int = 0, workers: int = 0,
                   log: Callable[[str], None] = print) -> int:
    cfg = {"kind": "conditions", "rules": rules, "inits": inits, "seeds": seeds, "size": size, "steps": steps,
           "density": density, "master_seed": master_seed}
    exp_id = store.create_experiment(name, master_seed, cfg, environment_info())
    rng = np.random.default_rng([master_seed, 777])
    jobs, meta = [], []
    for rule in rules:
        phys = OuterTotalistic.parse(rule).to_dict()
        rule_seeds = [int(x) for x in rng.integers(0, 2**62, size=seeds)]  # same seeds across conditions (paired)
        for ii, kind in enumerate(inits):
            for s in rule_seeds:
                spec = UniverseSpec(phys, s, size, size, density,
                                    init=None if kind == "uniform" else {"kind": kind}).to_dict()
                jobs.append((spec, steps, 100))
                meta.append((rule, kind, ii))
    log(f"conditions experiment #{exp_id}: {len(rules)} rules x {len(inits)} conditions x {seeds} seeds "
        f"= {len(jobs)} universes, {steps} steps on {size}x{size}")
    pool = ProcessPoolExecutor(max_workers=workers or None) if workers != 1 else None
    try:
        results = list(pool.map(_job, jobs, chunksize=1)) if pool else [_job(j) for j in jobs]
    finally:
        if pool:
            pool.shutdown()
    for (rule, kind, ii), (spec, steps_, window), res in zip(meta, jobs, results):
        extra = res.pop("extra")
        uid = store.add_universe(exp_id, ii, "condition", None, spec, steps_, window, res)
        store.db.execute("UPDATE universes SET aggregate=? WHERE id=?",
                         (json.dumps({"init": kind, **extra}, default=str), uid))
    store.commit()
    store.finish_experiment(exp_id)
    return exp_id


# ------------------------------------------------------------------ analysis
def _sign_test(diffs: list[float]) -> tuple[int, int, float]:
    pos, neg = sum(d > 0 for d in diffs), sum(d < 0 for d in diffs)
    n = pos + neg
    if n == 0:
        return pos, neg, 1.0
    k = min(pos, neg)
    p = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)
    return pos, neg, p


def _boot_ci(diffs: list[float], seed: int = 0, n: int = 2000) -> tuple[float, float]:
    if not diffs:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    a = np.array(diffs)
    means = a[rng.integers(0, len(a), size=(n, len(a)))].mean(axis=1)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def summarize(store: Store, exp_id: int) -> dict[str, Any]:
    univ = store.universes(exp_id, role="condition")
    cells: dict[tuple[str, str], list[dict]] = {}
    for u in univ:
        cells.setdefault((u["rule"], u["aggregate"]["init"]), []).append(u)
    cfg = store.experiment(exp_id)["config"]
    per: dict[tuple[str, str], dict[str, float]] = {}
    for (rule, kind), us in cells.items():
        settled = [u["metrics"]["cycle_found"] or run_settled(u["metrics"], u["class"]) for u in us]
        verdicts = [u["aggregate"]["innovation_verdict"] for u in us]
        kos = [(u["aggregate"].get("knockout") or {}).get("verdict") for u in us]
        per[(rule, kind)] = {
            "unsettled": 1 - float(np.mean(settled)),
            "self_prop": float(np.mean([movers(u["metrics"]) for u in us])),
            "innovating": float(np.mean([v == "still innovating" for v in verdicts])),
            "inconclusive": float(np.mean([v.startswith("inconclusive") for v in verdicts])),
            "knockout_depends": sum(k == "depends" for k in kos),
            "knockout_tested": sum(k not in (None, "untestable") for k in kos),
            "initial_density": float(np.mean([Universe.from_spec(UniverseSpec.from_dict(u["spec"])).state.mean()
                                              for u in us])),
        }
    rules, inits = cfg["rules"], cfg["inits"]
    table = {kind: {o: float(np.mean([per[(r, kind)][o] for r in rules])) for o in
                    OUTCOMES + ["inconclusive", "knockout_depends", "knockout_tested", "initial_density"]}
             for kind in inits}
    comparisons = {}
    for kind in inits:
        if kind == "uniform":
            continue
        comparisons[kind] = {}
        for o in OUTCOMES:
            diffs = [per[(r, kind)][o] - per[(r, "uniform")][o] for r in rules]
            pos, neg, p = _sign_test(diffs)
            lo, hi = _boot_ci(diffs, seed=len(comparisons))
            comparisons[kind][o] = {"mean_diff": float(np.mean(diffs)), "ci95": [lo, hi], "rules_higher": pos,
                                    "rules_lower": neg, "sign_test_p": p}
    return {"experiment": exp_id, "config": cfg, "by_condition": table, "vs_uniform": comparisons,
            "per_rule": {f"{r} | {k}": v for (r, k), v in per.items()}}


def report(summary: dict, log=print) -> None:
    inits = summary["config"]["inits"]
    log(f"{'condition':<10} {'init dens':>9} " + " ".join(f"{o:>12}" for o in OUTCOMES)
        + f" {'inconclusive':>12} {'KO depends/tested (per rule)':>28}")
    for kind in inits:
        t = summary["by_condition"][kind]
        log(f"{kind:<10} {t['initial_density']:>9.3f} " + " ".join(f"{t[o]:>12.3f}" for o in OUTCOMES)
            + f" {t['inconclusive']:>12.3f} {t['knockout_depends']:>5.2f}/{t['knockout_tested']:.2f}")
    log("\npaired vs uniform (same rule, same seeds); mean difference [95% CI], rules higher/lower, sign-test p:")
    for kind, outs in summary["vs_uniform"].items():
        for o, c in outs.items():
            log(f"  {kind:<9} {o:<11} {c['mean_diff']:+.3f} [{c['ci95'][0]:+.3f}, {c['ci95'][1]:+.3f}]  "
                f"{c['rules_higher']}/{c['rules_lower']}  p={c['sign_test_p']:.3g}")
