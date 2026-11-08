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

Continuous physics (Lenia), tolerant structure detector (observatory/continuous.py):
* positive    two gliders DERIVED from the Orbium parameters (asymmetric seed left to
              settle; not hand-typed): 2 movers, both self-propelled in isolation
* negative    a settled Orbium-parameter soup: many persistent STATIC blobs, no movers
* deceptive   smoothed-noise control physics (fresh blob-like random field every step):
              no persistent objects or movers; a decaying lopsided blob under a dying
              rule (its centre drifts as it fades): not self-propelled

Flow-Lenia (mass-conserving, float32 states, physics/flow_lenia.py, J-016, D-026):
* mass        conserved to float32 rounding over 1000 steps
* negative    a rule that collapses the 40x40 patch into one static blob: not self-propelled, not complex
* deceptive   pure diffusion (U = 0): spreads, but no movers; a rotated seed evolves into the
              rotated world (no fake motion from grid or Sobel anisotropy)
* null        random rules picked the way the old objectives picked them: none complex without a mover
* PL          FlowLeniaPL (localized kernel weights, J-033): equals FlowLenia when all weights are the
              rule's; matter and weighted parameters conserved and mixed weights stay between the
              species' values; a fed vacuum (food only) never changes
* positive    NOT available: no self-propelled structure in a search of 80 float rules with
              3-10 kernels (and 88 earlier uint8 rules), J-016

Continuous class label and settledness (observer.classify, quasi_static, v0.5 fix, J-012).
Labels and objectives tuned for 2-state rules called fields of static Lenia blobs "complex":
* complex     positive: two emergent gliders through the full pipeline -> complex.
              negative: settled Orbium soup (static blobs whose edges creep) -> not complex,
              quasi-static, so excluded from ranking. deceptive: smoothed noise stays at zero
              (no persistent objects or movers, not complex).
              selection-aware null: random Lenia rules picked the way the old objectives
              picked them (most persistent objects; most activity) -> none complex without a
              self-propelled structure.
* quasi-static negative: a dynamic rule with nothing that travels (moving stripe texture)
              keeps its free activity and stays rankable.
* slow positive  the "wanderer" (E-17/E-18), a slow turning mover emerging from a smooth start:
              must stay self-propelled and complex (the detector missed ~8% of them, J-022).
* slow movers, extended isolation (SLOW_STEPS = 300, calibrated in E-25, J-030):
              positive: a wanderer the 100-step isolation missed (E-18a #95) is found, and the
              100-step setting still misses it. deceptive: static blobs of a settled soup fail
              the 300-step isolation; a crooked fragment that passes isolation but splits later
              (E-12 #2059) is still rejected by the in-world straightness rule.
              selection-aware null: mover-free random rules in which the observer selects
              in-world movers (E-17 random arm) gain no self-propelled structure.
* near-fixed point  positive: jitter control (fixed field, +-1 level flicker) -> frozen.
              deceptive: the creeping soup is NOT a fixed point (its edges really move).
              negative: two gliders are not frozen.

Birth detector (observatory/births.py, two generations in isolation, J-032, D-028):
* positive    HighLife replicator (discrete); Gray-Scott spots, F 0.0367 k 0.0649 (continuous,
              physics/gray_scott.py): reproducer
* negative    Life glider; Orbium glider; the HighLife replicator pattern under Life: no reproduction
* deceptive   Fredkin B1357/S1357 copies anything: rule-level duplication. Seeds B2/S explodes into
              debris: not a reproducer. Gray-Scott stripes (F 0.03 k 0.059) grow and break up: not a
              reproducer. Gray-Scott worms (F 0.042 k 0.063) split once but the daughters do not:
              one generation. Smoothed noise: not a reproducer. A Lenia blob (E-14 #239, mass 72) that
              bursts into a world-filling labyrinth of ~80 similar-mass pieces within 1000 steps and
              then stops: not a reproducer (passed the first version's "late > early" rule, J-032).
              A fed Flow-Lenia rule (E-30 #43) whose food layer condenses into droplets after any
              disturbance: background (caught only by the perturbed-vacuum null, J-035).
* selection-aware null  `births.scan` (6 most common object types) on a Life soup and a settled
              Orbium soup: 0 reproducers.

Heredity test (observatory/heredity.py, transplanted offspring vs parent, J-033):
* positive    Gray-Scott spots carrying a tracer trait (GrayScottTracer "carried"), 6 founders with
              traits 0.1-0.9: heredity
* negative    the trait is redrawn as noise every step ("redrawn"): no heredity
* deceptive   the trait is set by position ("position"): in the world, nearest neighbours have
              similar traits (common environment), but transplanted offspring do not resemble their
              parent: no heredity. Identical founders (all 0.5): no variation, not heredity.
* selection-aware null  the parent-permutation null inside the test (parents are only kept if
              they reproduced); checked here as the null's 95% quantile staying below the positive's r.
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
# E-30 world 43 (J-035): a fed FlowLeniaPL rule whose food layer condenses after any disturbance
FED_UNSTABLE = ("FLENIA-PL/f0.05/FLENIA/R13/m0.491/s0.1695/h0.8/r0.22/a0.46,0.67,0.68/b0.41,0.94,0.51/w0.401,0.257,0.461"
                "+m0.052/s0.1080/h0.39/r0.52/a0.85,0.73,0.2/b0.67,0.46,0.92/w0.292,0.196,0.188"
                "+m0.377/s0.1946/h0.12/r0.44/a0,0.11,0.23/b0.59,0.75,0.89/w0.476,0.417,0.193")

# Flow-Lenia controls (J-016): drawn by FlowLenia._random_kernel from default_rng(1001) and
# default_rng(1007). STATIC collapses the paper's 40x40 patch into one static blob; WANDER
# forms a few objects that wobble and reshape (no straight self-propelled track).
FLOW_STATIC = "FLENIA/R13/m0.326/s0.0041/h0.2/r0.89/a0.08,0.2,0.63/b0.1,0.15,0.18/w0.075,0.492,0.385"
FLOW_WANDER = "FLENIA/R13/m0.082/s0.1634/h0.65/r0.36/a0.59,0.9,0.45/b0.2,0.36,0.04/w0.41,0.248,0.406"
VALUE_TOL_LEVELS = 2


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

    # 6. continuous physics: Lenia controls for the tolerant structure detector
    from .observatory import continuous as C
    from .physics import SmoothNoiseControl, parse_rule

    def frames_of(physics, state, n=100):
        w, fr = Universe(physics, state), []
        for _ in range(n):
            fr.append(w.state.copy())
            w.step()
        return fr

    orb = parse_rule("LENIA/R13/T10/m0.150/s0.0150/b1")
    gl = C.emergent_glider(orb)
    two = np.maximum(np.roll(gl, (-32, -60), axis=(0, 1)), np.roll(gl, (32, -60), axis=(0, 1)))
    a = C.analyse(frames_of(orb, two), orb)
    check("Lenia positive: two emergent gliders -> 2 self-propelled", a["mover_shapes"] == 2 and a["self_propelled_shapes"] == 2,
          f"movers {a['mover_shapes']:.0f}, self-propelled {a['self_propelled_shapes']:.0f}")
    soup = Universe.from_spec(UniverseSpec(orb.to_dict(), 1, 128, 128, 0.3))
    soup.step(400)
    a = C.analyse(frames_of(orb, soup.state.copy()), orb)
    check("Lenia negative: settled soup = static blobs, no movers", a["mover_shapes"] == 0 and a["still_structures"] >= 5,
          f"persistent {a['vocabulary']:.0f}, still {a['still_structures']:.0f}, movers {a['mover_shapes']:.0f}")
    nz = SmoothNoiseControl(4.0)
    a = C.analyse(frames_of(nz, Universe.from_spec(UniverseSpec(nz.to_dict(), 1, 128, 128, 0.3)).state.copy()), nz)
    check("Lenia deceptive: smoothed noise -> no persistent objects", a["vocabulary"] == 0 and a["mover_shapes"] == 0,
          f"objects/frame {a['objects_per_frame']:.1f}, persistent {a['vocabulary']:.0f}, movers {a['mover_shapes']:.0f}")
    die = parse_rule("LENIA/R13/T10/m0.200/s0.0150/b1")
    a = C.analyse(frames_of(die, gl.copy()), die)
    check("Lenia deceptive: decaying lopsided blob is not self-propelled", (a["self_propelled_shapes"] or 0) == 0,
          f"self-propelled {a['self_propelled_shapes']:.0f}")

    # 7. continuous class label, quasi-static settledness, tolerant fixed point (J-012)
    from .discovery import OBJECTIVES, run_settled
    from .lab import study_universe
    from .physics import JitterControl, Lenia

    def label(physics, state, steps=300):
        o = study_universe(Universe(physics, state), 1, steps=steps)
        return o.cls, o.metrics

    def brief(c, m):
        return (f"{c}, quasi-static {m.get('quasi_static')}, free {m.get('free_activity', 0):.4f}, "
                f"persistent {m['vocabulary']:.0f}, self-propelled {m['self_propelled_shapes']:.0f}")

    c, m = label(orb, two)
    check("Lenia complex positive: two emergent gliders -> complex", c == "complex" and not run_settled(m, c),
          brief(c, m))
    c, m = label(orb, soup.state.copy())
    check("Lenia complex negative: static blob soup -> not complex, quasi-static",
          c != "complex" and m["quasi_static"] and run_settled(m, c), brief(c, m))
    check("Lenia near-fixed-point deceptive: creeping blob soup is not frozen", c != "frozen",
          f"{c}, window change {m['window_change_frac']:.3f}")
    c, m = label(nz, Universe.from_spec(UniverseSpec(nz.to_dict(), 1, 128, 128, 0.3)).state.copy())
    check("Lenia complex deceptive: smoothed noise stays at zero",
          c != "complex" and m["vocabulary"] == 0 and m["mover_shapes"] == 0 and m["self_propelled_shapes"] == 0,
          brief(c, m))
    jit = JitterControl()
    c, m = label(jit, jit.random_state(np.random.default_rng(1), (128, 128), 0.3))
    check("Lenia near-fixed-point positive: +-1 level jitter -> frozen", c == "frozen",
          f"{c}, activity {m['activity_late']:.4f}, window change {m['window_change_frac']:.4f}")
    c, m = label(orb, two)
    check("Lenia near-fixed-point negative: gliders are not frozen", c != "frozen", c)
    stripes = parse_rule("LENIA/R13/T10/m0.139/s0.0091/b1,0.5")
    c, m = label(stripes, Universe.from_spec(UniverseSpec(stripes.to_dict(), 1, 96, 96, 0.35)).state.copy(), 500)
    check("Lenia quasi-static negative: moving stripes, nothing travels -> rankable",
          not m["quasi_static"] and not run_settled(m, c), brief(c, m))
    # selection-aware null: candidates chosen the way the OLD objectives chose them
    old_vocab = lambda m: m.get("vocabulary", 0.0)  # noqa: E731  (instances, inflated by static blobs)
    old_activity = lambda m: m["activity_late"] * (1.0 - m.get("local_periodic_frac", 0.0))  # noqa: E731
    rng = np.random.default_rng(2024)
    runs = []
    for _ in range(16):
        r = Lenia.random(rng)
        runs.append(label(r, Universe.from_spec(UniverseSpec(r.to_dict(), 1, 96, 96, 0.35)).state.copy()))
    alive = [cm for cm in runs if cm[0] != "extinct"]
    picked = {id(cm): cm for f in (old_vocab, old_activity)
              for cm in sorted(alive, key=lambda cm: -f(cm[1]))[:4]}.values()
    bad = [cm for cm in picked if cm[0] == "complex" and not cm[1]["self_propelled_shapes"]]
    check("Lenia complex null: top picks of the old objectives are not complex without a mover", not bad,
          f"{len(picked)} picked of {len(alive)} alive: classes {sorted(cm[0] for cm in picked)}, "
          f"quasi-static {sum(cm[1]['quasi_static'] for cm in picked)}, "
          f"new vocabulary objective {[round(OBJECTIVES['vocabulary'](cm[1])) for cm in picked]}")

    # 7b. slow, turning positive (review R-4, J-022): the E-17/E-18 "wanderer" (mass ~115,
    # ~0.08 cells/step along a curving path) emerging from a smooth start (E-18a universe #81)
    wspec = UniverseSpec({"kind": "lenia", "rule": "LENIA/R13/T10/m0.243/s0.0224/b1,0.5,0.5"}, 1909909783107617907,
                         128, 128, 0.18, init={"kind": "smooth", "ell": 6.0})
    o = study(wspec, steps=2000)
    check("Lenia slow positive: an emergent turning 'wanderer' is self-propelled and complex",
          o.cls == "complex" and (o.metrics["self_propelled_shapes"] or 0) >= 1,
          brief(o.cls, o.metrics))

    # 7c. extended isolation for slow movers (SLOW_STEPS = 300, E-25, J-030). Worlds from E-18a, E-12, E-17.
    w95 = UniverseSpec({"kind": "lenia", "rule": "LENIA/R13/T10/m0.243/s0.0224/b1,0.5,0.5"}, 47715909630089337,
                       128, 128, 0.18, init={"kind": "smooth", "ell": 6.0})
    o = study(w95, steps=2000)
    saved, C.SLOW_STEPS = C.SLOW_STEPS, 100
    try:
        o100 = study(w95, steps=2000)
    finally:
        C.SLOW_STEPS = saved
    check("Lenia slow positive 2: a wanderer the 100-step isolation misses (E-18a #95) is found with 300 steps",
          o.cls == "complex" and (o.metrics["self_propelled_shapes"] or 0) >= 1
          and not o100.metrics["self_propelled_shapes"], f"300 steps: {brief(o.cls, o.metrics)}; 100 steps: "
          f"self-propelled {o100.metrics['self_propelled_shapes']:.0f}")
    blobs = sorted(C.objects(soup.state), key=lambda b: -b["mass"])[:12]
    passed = sum(C.self_propelled(orb, soup.state, b, slow_steps=C.SLOW_STEPS) for b in blobs)
    check("Lenia slow deceptive: static blobs of a settled soup fail the 300-step isolation", passed == 0,
          f"{passed} of {len(blobs)} blobs pass")
    crooked = UniverseSpec({"kind": "lenia", "rule": "LENIA/R13/T10/m0.109/s0.0101/b0.5,0.25,1"}, 924037609305836849,
                           192, 192, 0.3132)
    o = study(crooked, steps=1000)
    check("Lenia slow deceptive: a crooked drifting fragment (E-12 #2059; passes isolation, splits later) is not counted",
          not o.metrics["self_propelled_shapes"] and o.cls != "complex", brief(o.cls, o.metrics))
    # selection-aware null: mover-free random rules (E-17 random arm) in which the observer DOES select
    # in-world movers (straight, >= 5 cells) that failed the 100-step isolation
    null = [(1063, 1126583757680214181, "LENIA/R13/T10/m0.334/s0.0663/b1,0.75", 0.3674),
            (1106, 4359418016614114976, "LENIA/R13/T10/m0.274/s0.0531/b1,0.5,0.25", 0.2057),
            (1216, 4281028167100086452, "LENIA/R13/T10/m0.300/s0.0733/b1,0.25", 0.1896),
            (1275, 1183500400978356013, "LENIA/R13/T10/m0.215/s0.0324/b1,0.5", 0.3968)]
    found = {}
    for uid, seed, rule, dens in null:
        o = study(UniverseSpec({"kind": "lenia", "rule": rule}, seed, 96, 96, dens, init={"kind": "smooth", "ell": 6.0}),
                  steps=500)
        found[uid] = (o.metrics["mover_shapes"], o.metrics["self_propelled_shapes"])
    check("Lenia slow null: selected movers in mover-free random rules stay unverified with 300 steps",
          all(m >= 1 and not sp for m, sp in found.values()),
          ", ".join(f"#{u}: movers {m:.0f}, self-propelled {sp:.0f}" for u, (m, sp) in found.items()))

    # 8. Flow-Lenia (mass-conserving continuous physics, float32 states, v0.7, J-016, D-026)
    from .physics import FlowLenia
    fl_static = parse_rule(FLOW_STATIC)
    fl_wander = parse_rule(FLOW_WANDER)
    side = (128, 128)
    s = FlowLenia.patch_state(np.random.default_rng(7), side)
    m0 = float(s.sum(dtype=np.float64))
    worst_drift = 0.0
    for _ in range(1000):
        s = fl_wander.step(s)
        worst_drift = max(worst_drift, abs(float(s.sum(dtype=np.float64)) - m0) / m0)
    check("Flow-Lenia mass: conserved to float32 rounding over 1000 steps", worst_drift < 1e-6 and s.dtype == np.float32,
          f"mass {m0:.3f} -> {float(s.sum(dtype=np.float64)):.3f}; worst relative drift {worst_drift:.1e}")
    c, m = label(fl_static, FlowLenia.patch_state(np.random.default_rng(1), side), 400)
    check("Flow-Lenia negative: static blob rule -> no self-propelled, not complex",
          c != "complex" and m["self_propelled_shapes"] == 0 and m["still_structures"] >= 1, brief(c, m))
    diff = FlowLenia.parse("FLENIA/R13/diffusion")
    hot = FlowLenia.patch_state(np.random.default_rng(1), side) * 2  # A ~ U[0, 2]: alpha = 1 above 1
    yy, xx = np.mgrid[0:side[0], 0:side[1]]
    rms = lambda a: float(np.sqrt((a / a.sum() * ((yy - 63.5) ** 2 + (xx - 63.5) ** 2)).sum()))  # noqa: E731
    u_d = Universe(diff, hot)
    u_d.step(400)
    grew = rms(u_d.state) - rms(hot)
    c, m = label(diff, hot, 400)
    check("Flow-Lenia deceptive: pure diffusion (U = 0) spreads, no movers, not complex",
          grew > 1.0 and c != "complex" and m["mover_shapes"] == 0 and m["self_propelled_shapes"] == 0,
          f"rms radius +{grew:.1f} cells in 400 steps; " + brief(c, m))
    # a rotated seed must evolve into the rotated world: grid or Sobel anisotropy must not
    # produce direction-dependent motion
    s0 = FlowLenia.patch_state(np.random.default_rng(3), side)
    a_, b_ = s0.copy(), np.rot90(s0).copy()
    worst, dc = 0.0, 0.0
    for _ in range(4):
        for _ in range(50):
            a_, b_ = fl_wander.step(a_), fl_wander.step(b_)
        ra = np.rot90(a_)
        worst = max(worst, float((np.abs(ra - b_) > VALUE_TOL_LEVELS / 255).mean()))
        ca = max(C.objects(ra), key=lambda o: o["mass"])["c"]
        cb = max(C.objects(b_), key=lambda o: o["mass"])["c"]
        dc = max(dc, float(np.hypot(*C._torus_delta(ca, cb, side))))
    check("Flow-Lenia deceptive: rotated seed moves the same way rotated", worst < 0.01 and dc < 1.0,
          f"largest-object centroid mismatch {dc:.2f} cells, cells differing by > 2/255 {worst:.4f} (200 steps)")
    # positive: none found. 80 random float rules (3, 5 and 10 kernels, paper's ranges and patch
    # start) gave no self-propelled structure (J-016), so there is no Flow-Lenia positive; the detector's
    # positive remains the Lenia gliders above. Selection-aware null: random rules picked by
    # the old objectives (most persistent objects; most activity) are not complex without one.
    rng = np.random.default_rng(77)
    runs = []
    for _ in range(8):
        r = FlowLenia.random(rng)
        runs.append(label(r, FlowLenia.patch_state(np.random.default_rng(1), (96, 96)), 300))
    picked = {id(cm): cm for f in (old_vocab, old_activity)
              for cm in sorted(runs, key=lambda cm: -f(cm[1]))[:3]}.values()
    bad = [cm for cm in picked if cm[0] == "complex" and not cm[1]["self_propelled_shapes"]]
    check("Flow-Lenia complex null: top picks by objects/activity are not complex without a mover", not bad,
          f"{len(picked)} picked of {len(runs)}: classes {sorted(cm[0] for cm in picked)}, "
          f"self-propelled {[int(cm[1]['self_propelled_shapes']) for cm in picked]}")
    # Flow-Lenia with parameter localization (FlowLeniaPL, J-033, D-029)
    from .physics import FlowLeniaPL
    pl = FlowLeniaPL(fl_static.kernels + FlowLenia.random(np.random.default_rng(5)).kernels[:1], 13)
    fl2 = FlowLenia(pl.kernels, 13)
    a0 = FlowLenia.patch_state(np.random.default_rng(1), (96, 96)).astype(np.float64)
    a, st = a0.astype(np.float32), pl.localize(a0)
    for _ in range(300):
        a, st = fl2.step(a), pl.step(st)
    check("Flow-Lenia-PL equals Flow-Lenia when every cell has the rule's weights",
          float(abs(st[0] - a).max()) < 1e-4, f"max |A_PL - A| after 300 steps {float(abs(st[0] - a).max()):.1e}")
    hmix = np.stack([np.where(np.arange(96)[None, :] < 48, 0.5, 1.5) * k.h * np.ones((96, 96)) for k in pl.kernels])
    st = pl.localize(a0, hmix)
    q0 = st.astype(np.float64).sum((1, 2))
    for _ in range(300):
        st = pl.step(st)
    w, m = pl.weights(st), st[0] > 0.05
    inside = all(0.5 * k.h - 1e-4 <= w[i][m].min() and w[i][m].max() <= 1.5 * k.h + 1e-4 for i, k in enumerate(pl.kernels))
    drift = float(abs(st.astype(np.float64).sum((1, 2)) / q0 - 1).max())
    check("Flow-Lenia-PL: matter and weighted parameters conserved, mixed weights stay in range",
          drift < 1e-5 and inside, f"worst relative drift {drift:.1e}; weights within the two species' values: {inside}")
    fed = FlowLeniaPL(pl.kernels, 13, 0.05)
    v = fed.vacuum((64, 64))
    st = v
    for _ in range(100):
        st = fed.step(st)
    check("Flow-Lenia-PL fed vacuum: a food-only world does not change and has no objects",
          float(abs(st - v).max()) == 0 and not __import__('emergence.observatory.births', fromlist=['find']).find(fed, st), f"max change {float(abs(st - v).max())}")

    # 9. birth detector (observatory/births.py)
    from .observatory import births as BI
    from .physics import GrayScott

    def birth(ph, st, rng_seed=0):
        o = max(BI.find(ph, st), key=lambda o: o["mass"])
        return BI.reproduction_test(ph, st, o, np.random.default_rng(rng_seed))

    def bbrief(r):
        g1 = r.get("gen1") or {}
        return (f"{r['verdict']}; gen 1 copies {g1.get('early')} -> {g1.get('late')}, clean {g1.get('clean')}, "
                f"gen 2 {(r.get('gen2') or {}).get('ok')}")

    def placed(rule, pat, side=64):
        g = np.zeros((side, side), np.uint8)
        g[20:20 + pat.shape[0], 20:20 + pat.shape[1]] = pat
        return parse_rule(rule), g

    def gs_spot(F, k, t):
        ph = GrayScott(F, k)
        st = ph.seed_spot((128, 128))
        for _ in range(t):
            st = ph.step(st)
        return ph, st

    for name, args, want in [
            ("births positive: HighLife replicator -> reproducer", placed("B36/S23", rle(HIGHLIFE_REPLICATOR)), "reproducer"),
            ("births positive: Gray-Scott spot -> reproducer", gs_spot(0.0367, 0.0649, 1000), "reproducer"),
            ("births negative: Life glider", placed("B3/S23", rle("bo$2bo$3o!")), "no reproduction"),
            ("births negative: replicator pattern under Life", placed("B3/S23", rle(HIGHLIFE_REPLICATOR)), "no reproduction"),
            ("births negative: Orbium glider", (orb, C.emergent_glider(orb)), "no reproduction"),
            ("births deceptive: Fredkin copies anything -> rule-level", placed("B1357/S1357", rle("obo$3o$bo!")),
             "rule-level duplication"),
            ("births deceptive: Seeds debris", placed("B2/S", rle("obo$3o$bo!")), "not reproducer"),
            ("births deceptive: Gray-Scott stripes grow and break up", gs_spot(0.03, 0.059, 300), "not reproducer"),
            ("births deceptive: Gray-Scott worms split once -> one generation", gs_spot(0.042, 0.063, 300),
             "one generation"),
            ("births deceptive: smoothed noise", (SmoothNoiseControl(), SmoothNoiseControl().random_state(
                np.random.default_rng(1), (96, 96), 0.3)), "not reproducer")]:
        r = birth(*args)
        ok = r["verdict"] != "reproducer" if want == "not reproducer" else r["verdict"] == want
        check(name, ok, bbrief(r))
    lab_spec = UniverseSpec({"kind": "lenia", "rule": "LENIA/R13/T10/m0.150/s0.0195/b1"}, 1497778031414372656,
                            128, 128, 0.1, init={"kind": "smooth", "ell": 3.0})
    lw = Universe.from_spec(lab_spec)
    lw.step(1999)
    lst = np.array(lw.state)
    lo = min(BI.find(lw.physics, lst), key=lambda o: abs(o["mass"] - 71.83))
    r = BI.reproduction_test(lw.physics, lst, lo, np.random.default_rng(0))
    check("births deceptive: Lenia blob bursts into a labyrinth (E-14 #239)",
          r["verdict"] != "reproducer" and (r.get("gen1") or {}).get("early", 0) >= 20, bbrief(r))
    # fed Flow-Lenia whose food layer is an unstable fixed point (E-30 world 43, J-035): a small
    # lump "reproduces" by making the food condense; the perturbed-vacuum null must catch it
    from .physics import FlowLeniaPL
    fed = parse_rule(FED_UNSTABLE)
    yy, xx = np.mgrid[-80:80, -80:80]
    lump = fed.food + 0.6 * np.exp(-(yy ** 2 + xx ** 2) / (2 * 2.0 ** 2))
    fst = fed.localize(lump)
    r = BI.reproduction_test(fed, fst, max(BI.find(fed, fst), key=lambda o: o["mass"]), np.random.default_rng(0))
    check("births deceptive: fed Flow-Lenia, food condenses after any disturbance (E-30 #43) -> background",
          r["verdict"] == "background" and r.get("perturbed_background_copies", 0) > 0 and (r.get("gen1") or {}).get("ok"),
          bbrief(r) + f"; exact vacuum copies {r.get('background_copies')}, perturbed {r.get('perturbed_background_copies')}")
    picked = []
    for spec, steps in ((UniverseSpec(life.to_dict(), 1, 96, 96, 0.35), 600),
                        (UniverseSpec(orb.to_dict(), 1, 128, 128, 0.35), 1000)):
        u = Universe.from_spec(spec)
        u.step(steps)
        picked.append(BI.scan(u.physics, np.array(u.state), np.random.default_rng(0)))
    check("births selection-aware null: scans of a Life soup and a settled Orbium soup",
          all(p["reproducers"] == 0 for p in picked) and all(p["tested"] >= 3 for p in picked),
          f"candidates {[p['tested'] for p in picked]}, reproducers {[p['reproducers'] for p in picked]}")

    # 10. heredity test (observatory/heredity.py)
    from .observatory import heredity as HE
    from .physics import GrayScottTracer

    def tracer_world(mode, traits, steps=1500, seed=1):
        ph = GrayScottTracer(mode=mode)
        g = np.random.default_rng(seed)
        st = ph.vacuum((128, 128))
        for (r0, c0), p in zip(g.integers(0, 116, size=(len(traits), 2)), traits):
            st[0, r0:r0 + 12, c0:c0 + 12] = 0.5
            v = 0.25 + 0.01 * g.random((12, 12))
            st[1, r0:r0 + 12, c0:c0 + 12] = v
            st[2, r0:r0 + 12, c0:c0 + 12] = v * p
        for _ in range(steps):
            st = ph.step(st)
        return ph, st

    def neighbour_r(ph, st):
        objs = BI.find(ph, st)
        tr = np.array([HE.object_trait(ph, st, o["mask"]) for o in objs])
        cen = np.array([np.argwhere(o["mask"]).mean(0) for o in objs])
        d = np.hypot(*(np.minimum(abs(cen[:, None] - cen[None]), 128 - abs(cen[:, None] - cen[None]))).transpose(2, 0, 1))
        np.fill_diagonal(d, np.inf)
        return float(np.corrcoef(tr, tr[d.argmin(1)])[0, 1])

    def hbrief(r):
        return (f"{r['verdict']}; families {r.get('families')}, r {r.get('r')}, p {r.get('p')}, "
                f"null r95 {r.get('null_r95')}, spread {r.get('parent_spread')}")

    spread = [0.1 + 0.16 * j for j in range(6)]
    hres = {}
    for mode in ("carried", "redrawn", "position"):
        ph, st = tracer_world(mode, spread)
        hres[mode] = HE.test(ph, st, np.random.default_rng(0), max_parents=8)
        if mode == "position":
            nr = neighbour_r(ph, st)
    check("heredity positive: carried tracer -> heredity", hres["carried"]["verdict"] == "heredity", hbrief(hres["carried"]))
    check("heredity negative: trait redrawn every step -> no heredity", hres["redrawn"]["verdict"] == "no heredity",
          hbrief(hres["redrawn"]))
    check("heredity deceptive: trait set by position (neighbours alike in the world) -> no heredity",
          hres["position"]["verdict"] == "no heredity" and nr > 0.5, hbrief(hres["position"]) + f"; in-world neighbour r {nr:.2f}")
    same = HE.test(*tracer_world("carried", [0.5] * 6), np.random.default_rng(0), max_parents=8)
    check("heredity deceptive: identical founders -> no variation", same["verdict"] == "no variation", hbrief(same))
    check("heredity selection-aware null: permutation null below the positive",
          hres["carried"].get("null_r95", 1) < hres["carried"].get("r", 0) and hres["redrawn"].get("p", 0) > 0.05,
          f"positive r {hres['carried'].get('r')} vs null r95 {hres['carried'].get('null_r95')}; negative p {hres['redrawn'].get('p')}")

    passed = sum(c["ok"] for c in checks)
    log(f"\n{passed}/{len(checks)} probe checks passed")
    return {"passed": passed, "total": len(checks), "checks": checks, "noise_innovation_floor": noise["established_late"]}
