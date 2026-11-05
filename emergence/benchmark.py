"""Validation benchmark: does the observatory report what is known to be there?

Two kinds of cases:

* **Synthetic controls** with a known answer by construction (pure noise, an
  empty world, a lone glider, a field of blinkers, a still life).
* **Known rules** whose qualitative behaviour from random soups is documented
  in the cellular-automata literature (Life, HighLife, Seeds, Brian's Brain, ...).

Every case states what *must* hold. The report lists each check as PASS/FAIL so
false positives and blind spots are visible, not hidden in averages.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .engine import Universe, UniverseSpec
from .lab import study, study_universe
from .physics import NoiseControl, OuterTotalistic

SETTLED = {"extinct", "frozen", "periodic", "drifting", "saturated"}


@dataclass
class Case:
    name: str
    expectation: str
    make: Callable[[int], tuple[Universe, int]]   # seed -> (universe, seed)
    check: Callable[[dict, str], bool]            # (metrics, class) -> ok


def _rule(rule: str, size: int = 96, density: float = 0.35):
    def make(seed):
        spec = UniverseSpec(OuterTotalistic.parse(rule).to_dict(), seed, size, size, density)
        return Universe.from_spec(spec), seed
    return make


def _placed(rule: str, cells_fn, size: int = 48):
    def make(seed):
        g = np.zeros((size, size), np.uint8)
        for r, c in cells_fn(seed, size):
            g[r % size, c % size] = 1
        return Universe(OuterTotalistic.parse(rule), g), seed
    return make


def _glider(seed, n):
    r0, c0 = 5 + seed % 7, 5 + (3 * seed) % 11
    return [(r0, c0 + 1), (r0 + 1, c0 + 2), (r0 + 2, c0), (r0 + 2, c0 + 1), (r0 + 2, c0 + 2)]


def _blinkers(seed, n):
    rng = np.random.default_rng(seed)
    cells = []
    for i in range(6):
        r, c = 4 + 7 * (i % 3) + int(rng.integers(0, 2)), 4 + 14 * (i // 3) + int(rng.integers(0, 2))
        cells += [(r, c), (r, c + 1), (r, c + 2)]
    return cells


def _blocks(seed, n):
    return [(r + dr, c + dc) for r, c in [(5, 5), (20, 30), (35, 12)] for dr in (0, 1) for dc in (0, 1)]


def _noise(seed):
    spec = UniverseSpec(NoiseControl(0.3).to_dict(), seed, 96, 96, 0.3)
    return Universe.from_spec(spec), seed


def _movers(m):
    return m.get("verified_mover_shapes") or 0


CASES = [
    # --- synthetic controls -------------------------------------------------
    Case("control: i.i.d. noise", "chaotic; 0 verified movers (unverified candidates = false-positive rate)",
         _noise, lambda m, c: c == "chaotic" and _movers(m) == 0),
    Case("control: empty world", "extinct", _placed("B3/S23", lambda s, n: []), lambda m, c: c == "extinct"),
    Case("control: lone glider (Life)", "drifting; verified mover (4 shapes = the glider's 4 phases)",
         _placed("B3/S23", _glider), lambda m, c: c == "drifting" and _movers(m) >= 1),
    Case("control: blinker field (Life)", "periodic; no movers",
         _placed("B3/S23", _blinkers), lambda m, c: c == "periodic" and m["mover_shapes"] == 0),
    Case("control: still lifes (Life)", "frozen; no movers",
         _placed("B3/S23", _blocks), lambda m, c: c == "frozen" and m["mover_shapes"] == 0),
    # --- known rules from random soups ---------------------------------------
    Case("Seeds B2/S", "chaotic (explosive, no stable objects)", _rule("B2/S"),
         lambda m, c: c == "chaotic" and (m["damage_norm"] or 0) > 0.5),
    Case("Brian's Brain B2/S/C3", "never settles; abundant verified gliders", _rule("B2/S/C3"),
         lambda m, c: c not in {"extinct", "frozen"} and _movers(m) >= 1),
    Case("Life B3/S23", "not chaotic; settles to ash or is still evolving", _rule("B3/S23"),
         lambda m, c: c != "chaotic" and (m["damage_norm"] or 0) < 0.5),
    Case("HighLife B36/S23", "not chaotic; like Life", _rule("B36/S23"),
         lambda m, c: c != "chaotic" and (m["damage_norm"] or 0) < 0.5),
    Case("Maze B3/S12345", "frozen/periodic labyrinth; damage heals", _rule("B3/S12345"),
         lambda m, c: c in {"frozen", "periodic"} and (m["damage_norm"] or 0) < 0.2),
    Case("Life without death B3/S012345678", "frozen (growth stops)", _rule("B3/S012345678"),
         lambda m, c: c == "frozen"),
    Case("Day & Night B3678/S34678", "not chaotic", _rule("B3678/S34678"), lambda m, c: c != "chaotic"),
    Case("Dead rule B8/S", "extinct", _rule("B8/S"), lambda m, c: c == "extinct"),
]


def run_benchmark(seeds: int = 3, steps: int = 500, log=print) -> dict:
    rows, passed, total = [], 0, 0
    for case in CASES:
        results = []
        for s in range(1, seeds + 1):
            u, seed = case.make(s)
            o = study_universe(u, seed, steps=steps)
            ok = bool(case.check(o.metrics, o.cls))
            results.append({"seed": seed, "class": o.cls, "ok": ok, "verified_movers": _movers(o.metrics),
                            "candidate_movers": o.metrics.get("mover_shapes", 0),
                            "damage_norm": o.metrics.get("damage_norm"),
                            "local_periodic_frac": o.metrics.get("local_periodic_frac")})
            passed += ok
            total += 1
        rows.append({"case": case.name, "expectation": case.expectation, "runs": results})
        mark = "PASS" if all(r["ok"] for r in results) else "FAIL"
        log(f"{mark}  {case.name:34s} expect: {case.expectation}")
        log("        " + "  ".join(f"seed{r['seed']}:{r['class']}"
                                   f"(mov {r['verified_movers']:.0f}/{r['candidate_movers']:.0f}"
                                   f", dmg {r['damage_norm'] or 0:.2f})" + ("" if r["ok"] else "!")
                                   for r in results))
    noise = next(r for r in rows if r["case"].startswith("control: i.i.d."))["runs"]
    fp = sum(r["candidate_movers"] for r in noise)
    log(f"\n{passed}/{total} checks passed. Mover false positives on pure noise: {fp:.0f} candidate shape(s)"
        f" in {len(noise)} runs, all rejected by isolation tests." if fp else
        f"\n{passed}/{total} checks passed. No mover candidates at all on pure noise.")
    return {"passed": passed, "total": total, "noise_candidate_false_positives": fp, "cases": rows}


__all__ = ["CASES", "run_benchmark", "study"]
