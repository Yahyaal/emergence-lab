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

Condition names may carry one parameter after a colon: "smooth:3" is {"kind": "smooth",
"ell": 3}. For continuous physics (Lenia) the innovation and knockout probes are skipped,
as in discovery._probe: they match shapes exactly, and continuous creatures never repeat
exactly, so they would report meaningless zeros. "innovating" is then not applicable (NaN).

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
from .physics import parse_rule, physics_from_dict
from .storage import Store

DEFAULT_INITS = ["uniform", "gradient", "patch", "spots"]
OUTCOMES = ["unsettled", "self_prop", "innovating"]
NOT_APPLICABLE = "not applicable (continuous physics)"
INIT_PARAM = {"smooth": "ell"}  # condition "kind:value" sets this init parameter


def init_of(name: str) -> dict | None:
    """Condition name -> UniverseSpec.init: "uniform" -> None, "smooth:3" -> {"kind": "smooth", "ell": 3.0}."""
    kind, _, arg = name.partition(":")
    if kind == "uniform":
        return None
    if not arg:
        return {"kind": kind}
    if kind not in INIT_PARAM:
        raise ValueError(f"condition {name!r}: {kind!r} takes no parameter")
    return {"kind": kind, INIT_PARAM[kind]: float(arg)}


def _job(job: tuple[dict, int, int]) -> dict[str, Any]:
    spec_d, steps, window = job
    res = _evaluate((spec_d, steps, window))
    if getattr(physics_from_dict(spec_d["physics"]), "continuous", False):
        res["extra"] = {"innovation": None, "innovation_verdict": NOT_APPLICABLE, "knockout": None}
        return res
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
        phys = parse_rule(rule).to_dict()
        rule_seeds = [int(x) for x in rng.integers(0, 2**62, size=seeds)]  # same seeds across conditions (paired)
        for ii, kind in enumerate(inits):
            for s in rule_seeds:
                spec = UniverseSpec(phys, s, size, size, density, init=init_of(kind)).to_dict()
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
        kr = [(u["aggregate"].get("knockout") or {}).get("rate_verdict") for u in us]
        applicable = NOT_APPLICABLE not in verdicts
        continuous = bool(us[0]["metrics"].get("continuous"))
        per[(rule, kind)] = {
            "unsettled": 1 - float(np.mean(settled)),
            "self_prop": float(np.mean([movers(u["metrics"]) for u in us])),
            "innovating": float(np.mean([v == "still innovating" for v in verdicts])) if applicable else math.nan,
            "inconclusive": float(np.mean([v.startswith("inconclusive") for v in verdicts])) if applicable else math.nan,
            "knockout_depends": sum(k == "depends" for k in kos),
            "knockout_tested": sum(k not in (None, "untestable") for k in kos),
            "knockout_rate_depends": sum(k == "depends" for k in kr),
            # discrete: occupied fraction; continuous: mass per cell (mean value, 0..1)
            "initial_density": float(np.mean([Universe.from_spec(UniverseSpec.from_dict(u["spec"])).state.mean()
                                              for u in us])) / (255.0 if continuous else 1.0),
        }
    rules, inits = cfg["rules"], cfg["inits"]
    table = {kind: {o: float(np.mean([per[(r, kind)][o] for r in rules])) for o in
                    OUTCOMES + ["inconclusive", "knockout_depends", "knockout_tested", "knockout_rate_depends",
                                "initial_density"]}
             for kind in inits}
    comparisons = {}
    for kind in inits:
        if kind == "uniform":
            continue
        comparisons[kind] = {}
        for o in OUTCOMES:
            diffs = [per[(r, kind)][o] - per[(r, "uniform")][o] for r in rules]
            if any(math.isnan(d) for d in diffs):
                comparisons[kind][o] = {"not_applicable": True}
                continue
            pos, neg, p = _sign_test(diffs)
            lo, hi = _boot_ci(diffs, seed=len(comparisons))
            comparisons[kind][o] = {"mean_diff": float(np.mean(diffs)), "ci95": [lo, hi], "rules_higher": pos,
                                    "rules_lower": neg, "sign_test_p": p}
    # population-level knockout test: real knockouts vs placebo knockouts (each control
    # deletion treated as the target and compared with the other controls)
    real, plac = [], []
    for u in univ:
        k = u["aggregate"].get("knockout") or {}
        if k.get("verdict") in (None, "untestable") or "drop_controls" not in k:
            continue
        c = np.array(k["drop_controls"])
        real.append(k["rate_dependency"])
        plac += [float(c[i] - np.delete(c, i).mean()) for i in range(len(c)) if len(c) > 1]
    placebo = None
    if real and plac:
        r, p_ = np.array(real), np.array(plac)
        placebo = {"n_real": len(r), "n_placebo": len(p_), "p_real_gt_placebo": float((r[:, None] > p_[None, :]).mean()),
                   "placebo_p95": float(np.percentile(p_, 95)), "real_above_placebo_p95": int((r > np.percentile(p_, 95)).sum())}
    return {"experiment": exp_id, "config": cfg, "by_condition": table, "vs_uniform": comparisons,
            "knockout_placebo": placebo,
            "per_rule": {f"{r} | {k}": v for (r, k), v in per.items()}}


def report(summary: dict, log=print) -> None:
    inits = summary["config"]["inits"]
    log(f"{'condition':<10} {'init dens':>9} " + " ".join(f"{o:>12}" for o in OUTCOMES)
        + f" {'inconclusive':>12} {'KO depends/tested (per rule)':>28}")
    for kind in inits:
        t = summary["by_condition"][kind]
        log(f"{kind:<10} {t['initial_density']:>9.3f} " + " ".join(f"{t[o]:>12.3f}" for o in OUTCOMES)
            + f" {t['inconclusive']:>12.3f} {t['knockout_depends']:>5.2f}/{t['knockout_tested']:.2f}"
            + f"  rate-depends {t['knockout_rate_depends']:.2f}")
    kp = summary.get("knockout_placebo")
    if kp:
        log(f"\nknockouts vs placebo: P(real > placebo) = {kp['p_real_gt_placebo']:.3f} (0.5 = no effect); "
            f"{kp['real_above_placebo_p95']} of {kp['n_real']} real knockouts above the placebo 95th pct "
            f"({0.05 * kp['n_real']:.1f} expected by chance)")
    log("\npaired vs uniform (same rule, same seeds); mean difference [95% CI], rules higher/lower, sign-test p:")
    for kind, outs in summary["vs_uniform"].items():
        for o, c in outs.items():
            if c.get("not_applicable"):
                log(f"  {kind:<9} {o:<11} not applicable (continuous physics)")
                continue
            log(f"  {kind:<9} {o:<11} {c['mean_diff']:+.3f} [{c['ci95'][0]:+.3f}, {c['ci95'][1]:+.3f}]  "
                f"{c['rules_higher']}/{c['rules_lower']}  p={c['sign_test_p']:.3g}")
