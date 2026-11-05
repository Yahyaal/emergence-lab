"""Discovery engine: explores rule space without a single "complexity score".

Each *rule* is screened on several seeds. The engine then combines three
established ideas:

1. **Pareto ranking** (non-dominated sorting) over several *independent*
   objectives, averaged over a rule's seeds: aperiodic activity, order
   (compressibility), self-propelled movers (verified in isolation), persistent
   shapes, and sustained dynamics. Nothing is summed or weighted.
2. **Novelty search** (Lehman & Stanley): mean distance to the k nearest
   neighbours in behaviour-descriptor space. Rewards "different from what we've
   already found", with no target.
3. **MAP-Elites-style parent selection** (Mouret & Clune): rules are binned into
   coarse behaviour niches (rule family x order x local periodicity x damage
   spreading x verified movers); a niche is drawn uniformly over occupied niches,
   then a parent by tournament within it. This keeps one productive family or
   behaviour from taking over the search.

Promising rules then get follow-up experiments: fresh seeds, a 2x larger world,
and an *extended* run of the original universe for several times as long, to
see whether the behaviour persists or eventually becomes trivial. Robustness is
judged on the continuous behaviour descriptor, not on the coarse class labels.
"""
from __future__ import annotations

import json
import platform
import re
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
ROBUST_SPREAD = 0.5  # max mean descriptor distance of re-runs to call a finding robust


def run_settled(m: dict, cls: str) -> bool:
    """Dead, frozen, or purely repetitive (every changing cell just oscillates in place)."""
    return cls in TRIVIAL or m.get("local_periodic_frac", 0.0) >= 0.95


def movers(m: dict) -> float:
    v = m.get("verified_mover_shapes")
    return float(m.get("mover_shapes", 0.0) if v is None else v)


OBJECTIVES: dict[str, Callable[[dict], float]] = {
    # activity that is NOT explained by cells oscillating in place
    "aperiodic_activity": lambda m: m["activity_late"] * (1.0 - m.get("local_periodic_frac", 0.0)),
    "order": lambda m: 1.0 - min(m["spacetime_ratio"], 1.0),
    # distinct shapes that travel on their own in an isolated clone
    "verified_movers": movers,
    "vocabulary": lambda m: m.get("vocabulary", 0.0),
    # a long transient before a cycle, or dynamics that are not fading at the horizon;
    # a universe that is merely dying slowly earns proportionally less
    "sustained": lambda m: (m["transient"] if m["cycle_found"]
                            else m["steps"] * min(1.0, m.get("activity_trend", 1.0))),
}


@dataclass
class ExploreConfig:
    name: str = "exploration"
    population: int = 100       # rules per generation
    generations: int = 5
    steps: int = 500
    window: int = 100
    width: int = 96
    height: int = 96
    density_min: float = 0.15
    density_max: float = 0.5
    screen_seeds: int = 2       # seeds per rule during exploration
    immigrant_fraction: float = 0.2
    novelty_k: int = 10
    followups: int = 8
    followup_seeds: int = 3
    extend_factor: int = 4      # extended run = extend_factor x steps on the original seed
    seed: int = 42
    workers: int = 0            # 0 = all cores


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


def _bin(x: float, edges: tuple[float, ...]) -> int:
    return int(np.searchsorted(edges, x, side="right"))


def niche_of(rule: str, mean_metrics: dict) -> str:
    """Coarse behaviour cell. Axes chosen to separate *unsettled* universes, most of
    which are noise-like: finer order bins near 1, local periodicity, and damage
    spreading (ordered / intermediate / chaotic, cf. Langton's edge of chaos)."""
    family = "multi" if re.search(r"/C\d+", rule) else "2state"
    order = _bin(mean_metrics["spacetime_ratio"], (0.5, 0.8, 0.95))
    lp = _bin(mean_metrics["local_periodic_frac"], (0.3, 0.7))
    dmg = _bin(mean_metrics["damage_norm"], (0.2, 0.6))
    mov = int(movers(mean_metrics) >= 1)
    return f"{family}|st{order}|lp{lp}|dmg{dmg}|mov{mov}"


def aggregate(u: dict, screens: list[dict]) -> dict[str, Any]:
    """Combine a rule's primary run with its seed screens."""
    runs = [u] + screens
    keys = ["activity_late", "local_periodic_frac", "spacetime_ratio", "mover_shapes", "vocabulary",
            "activity_trend", "damage_norm", "steps"]
    mean_m = {k: float(np.mean([r["metrics"].get(k) or 0.0 for r in runs])) for k in keys}
    mean_m["verified_mover_shapes"] = float(np.mean([movers(r["metrics"]) for r in runs]))
    objectives = {k: float(np.mean([f(r["metrics"]) for r in runs])) for k, f in OBJECTIVES.items()}
    classes = [r["class"] for r in runs]
    settled = all(run_settled(r["metrics"], r["class"]) for r in runs)
    return {
        "runs": [r["id"] for r in runs],
        "classes": classes,
        "seed_agreement": classes.count(u["class"]) / len(classes),
        "settled": settled,
        "objectives": objectives,
        "descriptor": np.mean([r["descriptor"] for r in runs], axis=0).round(5).tolist(),
        "niche": None if settled else niche_of(u["rule"], mean_m),
    }


def rank_population(universes: list[dict], k: int, screens: dict[int, list[dict]] | None = None) -> list[dict]:
    """Rank primary universes (one per rule). Returns id, novelty, pareto_rank, priority, aggregate."""
    if not universes:
        return []
    screens = screens or {}
    aggs = [aggregate(u, screens.get(u["id"], [])) for u in universes]
    desc = np.array([a["descriptor"] for a in aggs])
    nov = novelty_scores(desc, k)
    eligible = [i for i, a in enumerate(aggs) if not a["settled"]]
    pr = np.full(len(universes), -1)
    if eligible:
        obj = np.array([list(aggs[i]["objectives"].values()) for i in eligible])
        pr[eligible] = pareto_ranks(obj)
    order = sorted(range(len(universes)),
                   key=lambda i: (pr[i] < 0, pr[i] if pr[i] >= 0 else 0, -nov[i], universes[i]["id"]))
    priority = np.empty(len(universes), dtype=int)
    priority[order] = np.arange(1, len(universes) + 1)
    return [{"id": u["id"], "novelty": float(nov[i]), "pareto_rank": int(pr[i]) if pr[i] >= 0 else None,
             "priority": int(priority[i]), "aggregate": aggs[i]} for i, u in enumerate(universes)]


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

    def _spec(self, rule: dict, rng: np.random.Generator, density: float | None = None) -> dict:
        if density is None:
            density = round(float(rng.uniform(self.cfg.density_min, self.cfg.density_max)), 4)
        return UniverseSpec(physics=rule, seed=int(rng.integers(0, 2**62)), width=self.cfg.width,
                            height=self.cfg.height, density=density).to_dict()

    def _map(self, pool, jobs):
        if pool is None:
            return [_evaluate(j) for j in jobs]
        return list(pool.map(_evaluate, jobs, chunksize=max(1, len(jobs) // 32)))

    def run(self) -> int:
        cfg = self.cfg
        exp_id = self.store.create_experiment(cfg.name, cfg.seed, asdict(cfg), environment_info())
        self.log(f"experiment #{exp_id}: {cfg.population} rules x {cfg.screen_seeds} seeds x {cfg.generations} "
                 f"generations on {cfg.width}x{cfg.height}, seed {cfg.seed}")
        pool = ProcessPoolExecutor(max_workers=cfg.workers or None) if cfg.workers != 1 else None
        try:
            seen: set[str] = set()
            for gen in range(cfg.generations):
                rng = np.random.default_rng([cfg.seed, gen])
                batch = self._propose(exp_id, gen, rng, seen)
                jobs = []
                for spec, _parent, screens in batch:
                    jobs += [(s, cfg.steps, cfg.window) for s in [spec] + screens]
                results = iter(self._map(pool, jobs))
                for spec, parent, screens in batch:
                    pid = self.store.add_universe(exp_id, gen, "explore", parent, spec, cfg.steps, cfg.window,
                                                  next(results))
                    for s in screens:
                        self.store.add_universe(exp_id, gen, "screen", pid, s, cfg.steps, cfg.window, next(results))
                self.store.commit()
                ranked = self._rerank(exp_id)
                gen_ids = {u["id"] for u in self.store.universes(exp_id, role="explore") if u["generation"] == gen}
                counts: dict[str, int] = {}
                for u in self.store.universes(exp_id, role="explore"):
                    if u["id"] in gen_ids:
                        counts[u["class"]] = counts.get(u["class"], 0) + 1
                front = sum(1 for r in ranked if r["pareto_rank"] == 0)
                niches = len({r["aggregate"]["niche"] for r in ranked if r["aggregate"]["niche"]})
                self.log(f"  gen {gen}: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
                         + f" | front {front} | niches {niches}")
            self._follow_up(exp_id, pool)
            self.store.finish_experiment(exp_id)
        except BaseException:
            self.store.finish_experiment(exp_id, "aborted")
            raise
        finally:
            if pool is not None:
                pool.shutdown()
        return exp_id

    def _screens(self, exp_id: int) -> dict[int, list[dict]]:
        out: dict[int, list[dict]] = {}
        for s in self.store.universes(exp_id, role="screen"):
            out.setdefault(s["parent_id"], []).append(s)
        return out

    def _rerank(self, exp_id: int) -> list[dict]:
        univ = self.store.universes(exp_id, role="explore")
        ranked = rank_population(univ, self.cfg.novelty_k, self._screens(exp_id))
        self.store.set_rankings([(r["novelty"], r["pareto_rank"], r["priority"], json.dumps(r["aggregate"]), r["id"])
                                 for r in ranked])
        self.store.commit()
        return ranked

    def _propose(self, exp_id: int, gen: int, rng: np.random.Generator, seen: set[str]):
        cfg = self.cfg
        out = []
        univ = self.store.universes(exp_id, role="explore")
        # MAP-Elites-style: pick an occupied behaviour niche uniformly, then a binary
        # tournament on priority among that niche's members (not only its single elite,
        # which would leave just a handful of parents while few niches are occupied)
        members: dict[str, list[dict]] = {}
        for u in sorted(univ, key=lambda u: u["priority"]):
            niche = (u.get("aggregate") or {}).get("niche")
            if niche:
                members.setdefault(niche, []).append(u)
        niche_list = sorted(members)
        n_imm = cfg.population if gen == 0 or not niche_list else int(round(cfg.population * cfg.immigrant_fraction))
        attempts = 0
        while len(out) < cfg.population and attempts < cfg.population * 50:
            attempts += 1
            if len(out) < n_imm:
                rule, parent = OuterTotalistic.random(rng), None
            else:
                group = members[niche_list[int(rng.integers(len(niche_list)))]]
                p = group[int(rng.integers(len(group), size=2).min())]  # sorted by priority
                rule, parent = physics_from_dict(p["spec"]["physics"]).mutate(rng), p["id"]
            label = rule.label()
            if label in seen:
                continue
            seen.add(label)
            primary = self._spec(rule.to_dict(), rng)
            screens = [self._spec(rule.to_dict(), rng, primary["density"]) for _ in range(cfg.screen_seeds - 1)]
            out.append((primary, parent, screens))
        return out

    # ------------------------------------------------------------- follow-up
    def _follow_up(self, exp_id: int, pool) -> None:
        cfg = self.cfg
        if cfg.followups <= 0:
            return
        univ = sorted(self.store.universes(exp_id, role="explore"), key=lambda u: u["priority"])
        eligible = [u for u in univ if not u["aggregate"]["settled"]]
        # diversity first: the best candidate of each niche, then fill by priority
        candidates, used = [], set()
        for u in eligible:
            if u["aggregate"]["niche"] not in used and len(candidates) < cfg.followups:
                candidates.append(u)
                used.add(u["aggregate"]["niche"])
        for u in eligible:
            if len(candidates) >= cfg.followups:
                break
            if u not in candidates:
                candidates.append(u)
        most_novel = max(univ, key=lambda u: u["novelty"] or 0)
        if most_novel not in candidates:
            candidates.append(most_novel)
        self.log(f"  follow-up: {len(candidates)} candidates x ({cfg.followup_seeds} new seeds + 1 large world"
                 f" + 1 run {cfg.extend_factor}x longer)")
        rng = np.random.default_rng([cfg.seed, 10_000])
        jobs, meta = [], []
        for u in candidates:
            for i in range(cfg.followup_seeds):
                jobs.append((self._spec(u["spec"]["physics"], rng, u["spec"]["density"]), cfg.steps, cfg.window))
                meta.append((u, "seed"))
            big = UniverseSpec(physics=u["spec"]["physics"], seed=int(rng.integers(0, 2**62)),
                               width=cfg.width * 2, height=cfg.height * 2, density=u["spec"]["density"]).to_dict()
            jobs.append((big, cfg.steps * 2, cfg.window))
            meta.append((u, "large"))
            jobs.append((u["spec"], cfg.steps * cfg.extend_factor, cfg.window))  # same universe, observed longer
            meta.append((u, "extended"))
        results = self._map(pool, jobs)
        by_parent: dict[int, list[dict]] = {}
        for (u, kind), (spec, steps, _), res in zip(meta, jobs, results):
            uid = self.store.add_universe(exp_id, -1, "followup", u["id"], spec, steps, cfg.window, res)
            by_parent.setdefault(u["id"], []).append({"id": uid, "kind": kind, "cls": res["cls"],
                                                      "descriptor": res["descriptor"], "metrics": res["metrics"]})
        self.store.commit()
        for u in candidates:
            self._record(exp_id, u, by_parent.get(u["id"], []), most_novel_id=most_novel["id"])

    def _record(self, exp_id: int, u: dict, reps: list[dict], most_novel_id: int) -> None:
        agg = u["aggregate"]
        d0 = np.array(u["descriptor"])
        replicas = [r for r in reps if r["kind"] in ("seed", "large")]
        ext = next((r for r in reps if r["kind"] == "extended"), None)
        spread = float(np.mean([np.linalg.norm(np.array(r["descriptor"]) - d0) for r in replicas])) if replicas else 0.0
        classes = agg["classes"] + [r["cls"] for r in replicas]
        agree = classes.count(u["class"])
        robust = spread < ROBUST_SPREAD
        persists = ext is not None and not run_settled(ext["metrics"], ext["cls"]) and \
            ext["metrics"].get("activity_trend", 1.0) >= 0.5
        kind = ("robust" if robust else "seed-sensitive") + ("" if ext is None else ("/persists" if persists else "/fades"))
        if u["id"] == most_novel_id:
            kind = "most-novel/" + kind
        m = u["metrics"]
        bits = [f"{u['rule']} looks {u['class']}"]
        if m.get("mover_shapes"):
            bits.append(f"{int(movers(m))} of {int(m['mover_shapes'])} candidate mover shape(s) verified in isolation")
        if m.get("vocabulary"):
            bits.append(f"{int(m['vocabulary'])} persistent shapes")
        if m["cycle_found"]:
            bits.append(f"cycle period {m['period']} after {m['transient']} steps")
        else:
            bits.append(f"no recurrence within {m['steps']} steps")
        bits.append(f"damage spread {m['damage_norm'] or 0:.2f}")
        bits.append(f"descriptor spread across re-runs {spread:.2f} ({'<' if robust else '>='} {ROBUST_SPREAD})")
        bits.append(f"same class in {agree}/{len(classes)} runs")
        if ext is not None:
            em = ext["metrics"]
            bits.append(f"run {em['steps']} steps: still {ext['cls']}, activity trend {em.get('activity_trend', 0):.2f}"
                        if persists else
                        f"run {em['steps']} steps: becomes {ext['cls']}"
                        + (f" (cycle from t={em['transient']})" if em["cycle_found"] else ""))
        evidence = {
            "pareto_rank": u["pareto_rank"], "novelty": u["novelty"], "priority": u["priority"],
            "niche": agg["niche"], "screen_runs": agg["runs"], "screen_classes": agg["classes"],
            "replicate_classes": [r["cls"] for r in replicas], "replicate_ids": [r["id"] for r in replicas],
            "extended_id": ext["id"] if ext else None, "extended_class": ext["cls"] if ext else None,
            "persists": persists, "descriptor_spread": round(spread, 4),
            "objectives": {k: round(v, 5) for k, v in agg["objectives"].items()},
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
