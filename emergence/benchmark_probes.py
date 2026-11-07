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

Flow-Lenia (mass-conserving, physics/flow_lenia.py, J-014, D-025):
* mass        the stored uint8 mass is exactly constant over 1000 steps (float core: rounding drift)
* negative    a rule that collapses the 40x40 patch into one static blob: not self-propelled, not complex
* deceptive   pure diffusion (U = 0): no movers; a rotated seed evolves into the rotated world
              (no fake motion from grid or Sobel anisotropy or from the rounding tie-break)
* null        random rules picked the way the old objectives picked them: none complex without a mover
* positive    NOT available: no self-propelled structure found in an 88-rule search (J-014)

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
* near-fixed point  positive: jitter control (fixed field, +-1 level flicker) -> frozen.
              deceptive: the creeping soup is NOT a fixed point (its edges really move).
              negative: two gliders are not frozen.
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
# Flow-Lenia controls (J-014): drawn by FlowLenia._random_kernel from default_rng(1001) and
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

    # 8. Flow-Lenia (mass-conserving continuous physics, v0.7, J-014, D-025)
    from .physics import FlowLenia
    fl_static = parse_rule(FLOW_STATIC)
    fl_wander = parse_rule(FLOW_WANDER)
    side = (128, 128)
    s = FlowLenia.patch_state(np.random.default_rng(7), side)
    m0, A = int(s.sum(dtype=np.int64)), s * (2.0 / 255)
    a_mass = float(A.sum())
    for _ in range(1000):
        s, A = fl_wander.step(s), fl_wander.step_float(A)
    check("Flow-Lenia mass: stored (uint8) mass exact over 1000 steps", int(s.sum(dtype=np.int64)) == m0,
          f"levels {m0} -> {int(s.sum(dtype=np.int64))}; float core relative drift {(A.sum() - a_mass) / a_mass:.1e}")
    c, m = label(fl_static, FlowLenia.patch_state(np.random.default_rng(1), side), 400)
    check("Flow-Lenia negative: static blob rule -> no self-propelled, not complex",
          c != "complex" and m["self_propelled_shapes"] == 0 and m["still_structures"] >= 1, brief(c, m))
    diff = FlowLenia.parse("FLENIA/R13/diffusion")
    hot = FlowLenia.patch_state(np.random.default_rng(1), side).astype(np.uint16) * 2  # A ~ U[0, 2]: alpha = 1 above 1
    c, m = label(diff, np.minimum(hot, 255).astype(np.uint8), 400)
    check("Flow-Lenia deceptive: pure diffusion (U = 0) -> no movers, not complex",
          c != "complex" and m["mover_shapes"] == 0 and m["self_propelled_shapes"] == 0, brief(c, m))
    # a rotated seed must evolve into the rotated world: grid and Sobel anisotropy, or the
    # index-order tie-break of the conserving rounding, must not produce direction-dependent motion
    s0 = FlowLenia.patch_state(np.random.default_rng(3), side)
    a_, b_ = s0.copy(), np.rot90(s0).copy()
    worst, dc = 0.0, 0.0
    for _ in range(4):
        for _ in range(50):
            a_, b_ = fl_wander.step(a_), fl_wander.step(b_)
        ra = np.rot90(a_)
        worst = max(worst, float((np.abs(ra.astype(np.int16) - b_.astype(np.int16)) > VALUE_TOL_LEVELS).mean()))
        ca = max(C.objects(ra), key=lambda o: o["mass"])["c"]
        cb = max(C.objects(b_), key=lambda o: o["mass"])["c"]
        dc = max(dc, float(np.hypot(*C._torus_delta(ca, cb, side))))
    check("Flow-Lenia deceptive: rotated seed moves the same way rotated", worst < 0.01 and dc < 1.0,
          f"largest-object centroid mismatch {dc:.2f} cells, cells differing > 2 levels {worst:.4f} (200 steps)")
    # positive: none found. A search of 88 random rules from the paper's patch start gave no
    # self-propelled structure (J-014), so there is no Flow-Lenia positive check; the detector's
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

    passed = sum(c["ok"] for c in checks)
    log(f"\n{passed}/{len(checks)} probe checks passed")
    return {"passed": passed, "total": len(checks), "checks": checks, "noise_innovation_floor": noise["established_late"]}
