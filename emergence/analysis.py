"""Cross-experiment analysis: does the discovery engine beat a random-search baseline?

All counts are per *rule* (primary universe + its seed screens). Some measures
are things the engine optimises (self-propelled shapes, niches); others are not
optimised directly (class "complex" on every seed, structured activity), so a
win on those is less circular.
"""
from __future__ import annotations

import numpy as np

from .discovery import OBJECTIVES, movers
from .storage import Store


def _rule_stats(u: dict) -> dict:
    a = u.get("aggregate") or {}
    obj = a.get("objectives", {})
    return {
        "settled": a.get("settled", True),
        "niche": a.get("niche"),
        "self_propelled": obj.get("self_propelled", movers(u["metrics"])) >= 1,
        "complex_all_seeds": bool(a.get("classes")) and all(c == "complex" for c in a["classes"]),
        # structured activity: aperiodic change that is clearly compressible (not noise)
        "structured": (not a.get("settled", True)) and obj.get("aperiodic_activity", 0) > 0.005
                      and obj.get("order", 0) >= 0.15,
    }


def experiment_summary(store: Store, exp_id: int) -> dict:
    exp = store.experiment(exp_id)
    univ = store.universes(exp_id, role="explore")
    st = [(u["generation"], _rule_stats(u)) for u in univ]
    gens = sorted({g for g, _ in st})
    curve = []
    niches: set = set()
    for g in gens:
        rows = [s for gg, s in st if gg <= g]
        niches |= {s["niche"] for gg, s in st if gg == g and s["niche"]}
        curve.append({"generation": g, "rules": len(rows), "niches": len(niches),
                      "self_propelled": sum(s["self_propelled"] for s in rows),
                      "complex_all_seeds": sum(s["complex_all_seeds"] for s in rows),
                      "structured": sum(s["structured"] for s in rows)})
    disc = store.discoveries(exp_id)
    return {"id": exp_id, "name": exp["name"], "selection": exp["config"].get("selection", "engine"),
            "seed": exp["master_seed"], "final": curve[-1] if curve else {}, "curve": curve,
            "discoveries": len(disc), "persists": sum(d["kind"].endswith("persists") for d in disc),
            "robust": sum("robust" in d["kind"] for d in disc)}


def compare(store: Store, ids: list[int], log=print) -> list[dict]:
    rows = [experiment_summary(store, i) for i in ids]
    keys = ["rules", "niches", "self_propelled", "complex_all_seeds", "structured"]
    log(f"{'exp':>4} {'selection':<9} {'seed':>6} " + " ".join(f"{k:>17}" for k in keys) + f" {'robust':>7} {'persists':>8}")
    for r in rows:
        f = r["final"]
        log(f"{r['id']:>4} {r['selection']:<9} {r['seed']:>6} " + " ".join(f"{f.get(k, 0):>17}" for k in keys)
            + f" {r['robust']:>4}/{r['discoveries']:<2} {r['persists']:>5}/{r['discoveries']:<2}")
    by = {}
    for r in rows:
        by.setdefault(r["selection"], []).append(r["final"])
    if len(by) > 1:
        log("\nmean per selection method:")
        for sel, fs in by.items():
            log(f"  {sel:<9} " + "  ".join(f"{k}={np.mean([f[k] for f in fs]):.1f}" for k in keys))
    return rows


__all__ = ["compare", "experiment_summary", "OBJECTIVES"]
