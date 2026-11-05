"""Hard / deceptive controls for the v0.3 probes (innovation, replication, long runs).

Each case is built to fool a weaker test:

* transient trap   Life soups on 64x64 look "complex" at 500 steps and settle into
                   a cycle later. A 500-step verdict is wrong; the long run must catch it.
* glider gun       active forever and full of movers, but it makes the same glider
                   forever: "persists" would pass it, the innovation probe must not.
* noise            measures the innovation probe's false-positive floor.
* HighLife replicator   known positive for the replication probe.
* Fredkin B1357/S1357   copies EVERY pattern (linear rule): must be reported as
                   rule-level duplication, not self-replication.
* glider / block / blinker  must not replicate.
* soups of Life, HighLife, Seeds  scanned for spontaneous replicators: expected none
                   (false-positive check on realistic shapes).
* knockout, positive    a glider hits a block and leaves debris: deleting the glider,
                   or the first debris, must remove the later novelties (depends).
* knockout, negative    deleting a block the collision never touches: independent.
* knockout, deceptive   Brian's Brain: ANY deletion rewrites the future (damage
                   spreading); must not be reported as a dependency.
"""
from __future__ import annotations

import re

import numpy as np

from .engine import Universe, UniverseSpec
from .lab import study
from .observatory.innovation import innovation_profile
from .observatory.knockout import knockout_compare, knockout_experiment, types_over
from .observatory.replication import replication_test, scan_for_replicators
from .physics import NoiseControl, OuterTotalistic

GOSPER_GUN = "24bo$22bobo$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o$2o8bo3bob2o4bobo$10bo5bo7bo$11bo3bo$12b2o!"
HIGHLIFE_REPLICATOR = "2b3o$bo2bo$o3bo$o2bo$3o!"


def rle(s: str) -> np.ndarray:
    rows, row = [], []
    for n, ch in re.findall(r"(\d*)([bo$!])", s):
        n = int(n or 1)
        if ch in "bo":
            row += [1 if ch == "o" else 0] * n
        else:
            rows.append(row)
            if ch == "$":
                rows += [[] for _ in range(n - 1)]
            row = []
    w = max(len(r) for r in rows)
    return np.array([r + [0] * (w - len(r)) for r in rows], np.uint8)


def _placed(rule: str, pattern: np.ndarray, side: int) -> Universe:
    g = np.zeros((side, side), np.uint8)
    g[10:10 + pattern.shape[0], 10:10 + pattern.shape[1]] = pattern
    return Universe(OuterTotalistic.parse(rule), g)


def run_probe_benchmark(log=print) -> dict:
    checks = []

    def check(name, ok, detail):
        checks.append({"case": name, "ok": bool(ok), "detail": detail})
        log(f"{'PASS' if ok else 'FAIL'}  {name:58s} {detail}")

    life = OuterTotalistic.parse("B3/S23")
    # 1. transient trap
    for seed in (2, 3, 4):
        spec = UniverseSpec(life.to_dict(), seed, 64, 64, 0.35)
        short, long_ = study(spec, steps=500), study(spec, steps=3000)
        ok = (not short.metrics["cycle_found"]) and long_.metrics["cycle_found"]
        check(f"transient trap: Life 64x64 seed {seed}", ok,
              f"500 steps: {short.cls}; 3000 steps: {long_.cls} (cycle from t={long_.metrics['transient']})")

    # 2. innovation: glider gun (no innovation) and noise floor
    gun = innovation_profile(_placed("B3/S23", rle(GOSPER_GUN), 400), steps=1200, every=100)
    check("glider gun: sustained movers but no new shape types", gun["new_second_half"] == 0,
          f"{gun['shapes_total']} shape types, {gun['new_second_half']} new in 2nd half")
    noise_u = Universe.from_spec(UniverseSpec(NoiseControl(0.3).to_dict(), 1, 96, 96, 0.3))
    noise = innovation_profile(noise_u, steps=3200, every=100)
    check("noise: innovation false-positive floor <= 2", noise["established_late"] <= 2,
          f"established late innovations = {noise['established_late']} (floor)")

    # 3. replication controls
    rng = np.random.default_rng(0)
    rep = replication_test(OuterTotalistic.parse("B36/S23"), rle(HIGHLIFE_REPLICATOR), rng)
    check("HighLife replicator is a self-replicator", rep["verdict"] == "self-replicator",
          f"copies {rep['copies_early']} -> {rep['copies_late']}, random patterns: copy themselves "
          f"{rep['random_replicating']}/5, produce this shape {rep['random_producing_candidate']}/5")
    rep_life = replication_test(life, rle(HIGHLIFE_REPLICATOR), rng)
    check("same pattern under Life does not replicate", rep_life["verdict"] == "no replication", rep_life["verdict"])
    fred = replication_test(OuterTotalistic.parse("B1357/S1357"), rle("obo$3o$bo!"), rng)
    check("Fredkin rule: rule-level duplication, not self-replication", fred["verdict"] == "rule-level duplication",
          f"{fred['verdict']} (random patterns copying {fred['random_replicating']}/5)")
    for name, pat in [("glider", "bo$2bo$3o!"), ("block", "2o$2o!"), ("blinker", "3o!")]:
        r = replication_test(life, rle(pat), rng)
        check(f"{name} (Life) does not replicate", r["verdict"] == "no replication", r["verdict"])

    # 4. realistic false-positive scan on soups
    for rule in ("B3/S23", "B36/S23", "B2/S"):
        u = Universe.from_spec(UniverseSpec(OuterTotalistic.parse(rule).to_dict(), 1, 96, 96, 0.35))
        u.step(400)
        frames = []
        for _ in range(30):
            frames.append(u.state.copy())
            u.step()
        s = scan_for_replicators(u.physics, frames, rng, max_candidates=15)
        check(f"soup scan {rule}: no spontaneous self-replicators", s["self_replicators"] == 0,
              f"tested {s['tested']} shapes: self-replicators {s['self_replicators']}, "
              f"rule-level {s['rule_level_duplication']}, common products {s['common_products']}, explosive {s['explosive']}")

    # 5. knockout (causal dependency of later novelty on an earlier one)
    g = np.zeros((90, 90), np.uint8)
    g[5:8, 5:8] = rle("bo$2bo$3o!")   # glider heading for the block below
    g[30:32, 26:28] = 1               # block in its path: the collision leaves new debris
    g[75:77, 70:72] = 1               # two blocks the collision never reaches
    g[70:72, 12:14] = 1
    glider = np.zeros(g.shape, bool)
    glider[5:8, 5:8] = g[5:8, 5:8] > 0
    far1, far2 = np.zeros(g.shape, bool), np.zeros(g.shape, bool)
    far1[75:77, 70:72] = True
    far2[70:72, 12:14] = True
    before = set(types_over(Universe(life, g.copy()), 40, 20))
    pos = knockout_compare(life, g, glider, [far1, far2], before, 500, 25)
    check("knockout positive: delete the glider -> later debris lost", pos["verdict"] == "depends",
          f"lost {pos.get('lost_knockout')} vs controls {pos.get('lost_controls')}")
    flow = knockout_experiment(Universe(life, g.copy()), 125, 400, 25, rng)
    check("knockout positive, automatic flow: first debris enables later debris", flow["verdict"] == "depends",
          f"t1={flow.get('t1')}: lost {flow.get('lost_knockout')} vs controls {flow.get('lost_controls')}")
    neg = knockout_compare(life, g, far1, [far2], before, 500, 25)
    check("knockout negative: delete an uninvolved block -> independent", neg["verdict"] == "independent",
          f"lost {neg.get('lost_knockout')} vs controls {neg.get('lost_controls')}")
    bb = knockout_experiment(Universe.from_spec(UniverseSpec(OuterTotalistic.parse("B2/S/C3").to_dict(), 1, 96, 96, 0.35)),
                             300, 600, 50, rng)
    check("knockout deceptive: Brian's Brain is not a dependency", bb["verdict"] != "depends",
          f"{bb['verdict']}: lost {bb.get('lost_knockout')} vs controls {bb.get('lost_controls')}")
    check("knockout positive, rate-based reading: novelty rate drops", pos["rate_verdict"] == "depends",
          f"drop {pos.get('drop_knockout')} vs controls {pos.get('drop_controls')}")
    check("knockout deceptive, rate-based reading: no rate effect in Brian's Brain",
          bb.get("rate_verdict") != "depends",
          f"{bb.get('rate_verdict')}: drop {bb.get('drop_knockout')} vs controls {bb.get('drop_controls')}")

    passed = sum(c["ok"] for c in checks)
    log(f"\n{passed}/{len(checks)} probe checks passed")
    return {"passed": passed, "total": len(checks), "checks": checks, "noise_innovation_floor": noise["established_late"]}
