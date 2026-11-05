"""Discovery engine: explores rule space without a single "complexity score".

Ranking uses two established ideas side by side:

1. **Pareto ranking** (non-dominated sorting) over several *independent*
   objectives - aperiodic activity, order (compressibility), moving structures,
   structural vocabulary, transient length. A universe is promising if no other
   universe beats it on every axis at once. Nothing is summed or weighted.
2. **Novelty search** (Lehman & Stanley): mean distance to the k nearest
   neighbours in behaviour-descriptor space over everything seen so far.
   Rewards "different from what we've already found", with no target.

Promising universes are then *re-tested* with fresh seeds and a larger world
(robustness check) before they are recorded as discoveries, so we don't mistake
a lucky initial condition for a property of the rule.
"""
from __future__ import annotations

import json
import platform
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
from typing import Any, Callable

import numpy as np

from . import __version__
from .engine import UniverseSpec
from .lab import study
from .physics import OuterTotalistic, physics_from_dict
from .storage import Store

TRIVIAL = {"extinct", "saturated", "frozen"}


def is_settled(u: dict) -> bool:
    """Dead, frozen, or purely repetitive (every changing cell just oscillates).
    Settled universes are kept and shown, but not Pareto-ranked or bred from."""
    return u["class"] in TRIVIAL or u["metrics"].get("local_periodic_frac", 0.0) >= 0.95


OBJECTIVES: dict[str, Callable[[dict], float]] = {
    # activity that is NOT explained by cells oscillating in place
    "aperiodic_activity": lambda m: m["activity_late"] * (1.0 - m.get("local_periodic_frac", 0.0)),
    "order": lambda m: 1.0 - min(m["spacetime_ratio"], 1.0),
    "movers": lambda m: m.get("mover_events", 0.0),
    "vocabulary": lambda m: m.get("vocabulary", 0.0),
    "transient": lambda m: m["transient"] if m["cycle_found"] else m["steps"],
}


@dataclass
class ExploreConfig:
    name: str = "exploration"
    population: int = 100
    generations: int = 5
    steps: int = 500
    window: int = 100
    width: int = 64
    height: int = 64
    density_min: float = 0.15
    density_max: float = 0.5
    immigrant_fraction: float = 0.2
    novelty_k: int = 10
    followups: int = 8
    followup_seeds: int = 3
    seed: int = 42
    workers: int = 0  # 0 = all cores


# ----------------------------------------------------------------- ranking
def novelty_scores(desc: np.ndarray, k: int) -> np.ndarray:
    n = len(desc)
    if n < 2:
        return np.zeros(n)
    d = np.sqrt(((desc[:, None, :] - desc[None, :, :]) ** 2).sum(-1))
    np.fill_diagonal(d, np.inf)
    k = min(k, n - 1)
    return np.sort(d, axis=1)[:, :k].mean(axis=1)


def pareto_ranks(obj: np.ndarray) -> np.ndarray:
    """Non-dominated sorting (maximisation). Rank 0 = Pareto front."""
    n = len(obj)
    ranks = np.full(n, -1)
    if n == 0:
        return ranks
    ge = (obj[:, None, :] >= obj[None, :, :]).all(-1)
    gt = (obj[:, None, :] > obj[None, :, :]).any(-1)
    dominates = ge & gt  # dominates[i, j]: i dominates j
    remaining = np.ones(n, dtype=bool)
    r = 0
    while remaining.any():
        dominated = (dominates[remaining][:, remaining]).any(axis=0)
        idx = np.flatnonzero(remaining)[~dominated]
        ranks[idx] = r
        remaining[idx] = False
        r += 1
    return ranks


def rank_population(universes: list[dict], k: int) -> list[dict]:
    """Return {id, novelty, pareto_rank, priority} for each universe."""
    if not universes:
        return []
    desc = np.array([u["descriptor"] for u in universes])
    nov = novelty_scores(desc, k)
    nontrivial = [i for i, u in enumerate(universes) if not is_settled(u)]
    pr = np.full(len(universes), -1)
    if nontrivial:
        obj = np.array([[f(universes[i]["metrics"]) for f in OBJECTIVES.values()] for i in nontrivial])
        pr[nontrivial] = pareto_ranks(obj)
    order = sorted(range(len(universes)),
                   key=lambda i: (pr[i] < 0, pr[i] if pr[i] >= 0 else 0, -nov[i], universes[i]["id"]))
    priority = np.empty(len(universes), dtype=int)
    priority[order] = np.arange(1, len(universes) + 1)
    return [{"id": u["id"], "novelty": float(nov[i]), "pareto_rank": int(pr[i]) if pr[i] >= 0 else None,
             "priority": int(priority[i])} for i, u in enumerate(universes)]


# ----------------------------------------------------------------- evaluation
def _evaluate(job: tuple[dict, int, int]) -> dict[str, Any]:
    spec_d, steps, window = job
    o = study(UniverseSpec.from_dict(spec_d), steps=steps, window=window)
    return {"metrics": o.metrics, "timeseries": o.timeseries, "descriptor": o.descriptor, "cls": o.cls,
            "final_hash": o.final_hash, "final_state": o.final_state}


def environment_info() -> dict[str, str]:
    import scipy
    return {"emergence": __version__, "python": sys.version.split()[0], "numpy": np.__version__,
            "scipy": scipy.__version__, "platform": platform.platform()}


class Explorer:
    def __init__(self, store: Store, config: ExploreConfig, log: Callable[[str], None] = print):
        self.store = store
        self.cfg = config
        self.log = log

    def _spec(self, rule: dict, rng: np.random.Generator) -> dict:
        return UniverseSpec(
            physics=rule, seed=int(rng.integers(0, 2**62)), width=self.cfg.width, height=self.cfg.height,
            density=round(float(rng.uniform(self.cfg.density_min, self.cfg.density_max)), 4),
        ).to_dict()

    def _map(self, pool, jobs):
        if pool is None:
            return [_evaluate(j) for j in jobs]
        return list(pool.map(_evaluate, jobs, chunksize=max(1, len(jobs) // 32)))

    def run(self) -> int:
        cfg = self.cfg
        exp_id = self.store.create_experiment(cfg.name, cfg.seed, asdict(cfg), environment_info())
        self.log(f"experiment #{exp_id}: {cfg.population} universes x {cfg.generations} generations, seed {cfg.seed}")
        workers = cfg.workers or None
        pool = ProcessPoolExecutor(max_workers=workers) if cfg.workers != 1 else None
        try:
            seen: set[str] = set()
            for gen in range(cfg.generations):
                rng = np.random.default_rng([cfg.seed, gen])
                batch = self._propose(exp_id, gen, rng, seen)
                results = self._map(pool, [(s, cfg.steps, cfg.window) for s, _ in batch])
                for (spec, parent), res in zip(batch, results):
                    self.store.add_universe(exp_id, gen, "explore", parent, spec, cfg.steps, cfg.window, res)
                self.store.commit()
                ranked = self._rerank(exp_id)
                counts: dict[str, int] = {}
                for u in self.store.universes(exp_id, role="explore"):
                    if u["generation"] == gen:
                        counts[u["class"]] = counts.get(u["class"], 0) + 1
                front = sum(1 for r in ranked if r["pareto_rank"] == 0)
                self.log(f"  gen {gen}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
                         + f" | pareto front size {front}")
            self._follow_up(exp_id, pool)
            self.store.finish_experiment(exp_id)
        except BaseException:
            self.store.finish_experiment(exp_id, "aborted")
            raise
        finally:
            if pool is not None:
                pool.shutdown()
        return exp_id

    def _rerank(self, exp_id: int) -> list[dict]:
        univ = self.store.universes(exp_id, role="explore")
        ranked = rank_population(univ, self.cfg.novelty_k)
        self.store.set_rankings([(r["novelty"], r["pareto_rank"], r["priority"], r["id"]) for r in ranked])
        self.store.commit()
        return ranked

    def _propose(self, exp_id: int, gen: int, rng: np.random.Generator, seen: set[str]) -> list[tuple[dict, int | None]]:
        cfg = self.cfg
        out: list[tuple[dict, int | None]] = []
        pool = [u for u in self.store.universes(exp_id, role="explore") if not is_settled(u)]
        pool.sort(key=lambda u: u["priority"])
        n_imm = cfg.population if gen == 0 or not pool else int(round(cfg.population * cfg.immigrant_fraction))
        attempts = 0
        while len(out) < cfg.population and attempts < cfg.population * 50:
            attempts += 1
            if len(out) < n_imm:
                rule, parent = OuterTotalistic.random(rng), None
            else:
                # tournament selection on priority (pareto rank, then novelty)
                picks = rng.integers(0, len(pool), size=3)
                p = pool[int(min(picks))]
                rule, parent = physics_from_dict(p["spec"]["physics"]).mutate(rng), p["id"]
            label = rule.label()
            if label in seen:
                continue
            seen.add(label)
            out.append((self._spec(rule.to_dict(), rng), parent))
        return out

    # ------------------------------------------------------------- follow-up
    def _follow_up(self, exp_id: int, pool) -> None:
        cfg = self.cfg
        if cfg.followups <= 0:
            return
        univ = sorted(self.store.universes(exp_id, role="explore"), key=lambda u: u["priority"])
        candidates = [u for u in univ if not is_settled(u)][: cfg.followups]
        # also flag the single most novel universe even if it is "trivial"-looking
        most_novel = max(univ, key=lambda u: u["novelty"] or 0)
        if most_novel not in candidates:
            candidates.append(most_novel)
        self.log(f"  follow-up: re-testing {len(candidates)} candidates with {cfg.followup_seeds} new seeds + 1 large world")
        rng = np.random.default_rng([cfg.seed, 10_000])
        jobs, meta = [], []
        for u in candidates:
            for i in range(cfg.followup_seeds + 1):
                big = i == cfg.followup_seeds
                spec = UniverseSpec(
                    physics=u["spec"]["physics"], seed=int(rng.integers(0, 2**62)),
                    width=cfg.width * (2 if big else 1), height=cfg.height * (2 if big else 1),
                    density=u["spec"]["density"],
                ).to_dict()
                steps = cfg.steps * (2 if big else 1)
                jobs.append((spec, steps, cfg.window))
                meta.append((u, spec, steps))
        results = self._map(pool, jobs)
        by_parent: dict[int, list[dict]] = {}
        for (u, spec, steps), res in zip(meta, results):
            uid = self.store.add_universe(exp_id, -1, "followup", u["id"], spec, steps, cfg.window, res)
            by_parent.setdefault(u["id"], []).append({"id": uid, "cls": res["cls"], "descriptor": res["descriptor"],
                                                      "metrics": res["metrics"], "size": spec["width"]})
        self.store.commit()
        for u in candidates:
            self._record(exp_id, u, by_parent.get(u["id"], []), most_novel_id=most_novel["id"])

    def _record(self, exp_id: int, u: dict, reps: list[dict], most_novel_id: int) -> None:
        classes = [u["class"]] + [r["cls"] for r in reps]
        agree = sum(c == u["class"] for c in classes)
        d0 = np.array(u["descriptor"])
        spread = float(np.mean([np.linalg.norm(np.array(r["descriptor"]) - d0) for r in reps])) if reps else 0.0
        robust = agree == len(classes) and spread < 0.6
        kind = "robust" if robust else "seed-sensitive"
        if u["id"] == most_novel_id:
            kind = "most-novel/" + kind
        m = u["metrics"]
        bits = [f"{u['rule']} looks {u['class']}"]
        if m.get("mover_shapes"):
            bits.append(f"{int(m['mover_shapes'])} moving shape(s)")
        if m.get("vocabulary"):
            bits.append(f"{int(m['vocabulary'])} persistent shapes")
        if m["cycle_found"]:
            bits.append(f"cycle period {m['period']} after {m['transient']} steps")
        else:
            bits.append(f"no recurrence within {m['steps']} steps")
        bits.append(f"damage spread {m['damage_norm'] or 0:.2f}")
        bits.append(f"class reproduced in {agree}/{len(classes)} runs")
        if agree == len(classes) and not robust:
            bits.append(f"but measurements vary between seeds (descriptor spread {spread:.2f} >= 0.6)")
        evidence = {
            "pareto_rank": u["pareto_rank"], "novelty": u["novelty"], "priority": u["priority"],
            "replicate_classes": classes, "replicate_ids": [r["id"] for r in reps],
            "descriptor_spread": round(spread, 4),
            "objectives": {k: round(float(f(m)), 5) for k, f in OBJECTIVES.items()},
        }
        self.store.add_discovery(exp_id, u["id"], kind, "; ".join(bits), evidence)
        self.log(f"    [{kind}] #{u['id']} " + "; ".join(bits))


def reproduce(store: Store, uid: int) -> dict[str, Any]:
    """Re-run a stored universe from its spec and compare with the stored record."""
    u = store.universe(uid)
    if u is None:
        raise KeyError(uid)
    res = _evaluate((u["spec"], u["steps"], u["window"]))
    stored, fresh = u["metrics"], json.loads(json.dumps(res["metrics"]))
    diffs = {}
    for k, v in stored.items():
        w = fresh.get(k)
        if isinstance(v, float) and isinstance(w, float):
            if abs(v - w) > 1e-9 * max(1.0, abs(v)):
                diffs[k] = (v, w)
        elif v != w:
            diffs[k] = (v, w)
    return {"id": uid, "rule": u["rule"], "hash_match": res["final_hash"] == u["final_hash"],
            "stored_hash": u["final_hash"], "fresh_hash": res["final_hash"], "metric_diffs": diffs}
