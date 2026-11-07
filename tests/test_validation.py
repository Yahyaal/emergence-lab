import sqlite3

import numpy as np

from emergence.benchmark import run_benchmark
from emergence.discovery import ExploreConfig, Explorer, niche_of
from emergence.engine import Universe, UniverseSpec
from emergence.lab import study, study_universe
from emergence.observatory.structures import analyse, census, verify_in_isolation
from emergence.physics import NoiseControl, OuterTotalistic
from emergence.storage import Store

LIFE = OuterTotalistic.parse("B3/S23")


def test_glider_verified_in_isolation():
    g = np.zeros((32, 32), np.uint8)
    g[[1, 2, 3, 3, 3], [2, 3, 1, 2, 3]] = 1
    frames, s = [], g
    for _ in range(40):
        frames.append(s)
        s = LIFE.step(s)
    a = analyse(frames, LIFE)
    assert a["mover_shapes"] >= 1 and a["self_propelled_shapes"] == a["mover_shapes"]


def test_coincidental_sightings_are_rejected():
    """A still-life block shown at a, a+d, a+2d looks like a mover to shape
    matching, but does not move when run in isolation."""
    frames = []
    for t in range(30):
        g = np.zeros((40, 40), np.uint8)
        r = 5 + t          # pretend it slides one cell per frame
        g[r:r + 2, 5:7] = 1
        frames.append(g)
    a = analyse(frames, LIFE)
    assert a["mover_shapes"] == 1          # candidate
    assert a["self_propelled_shapes"] == 0  # rejected
    key = next(iter(census(frames[0])))
    assert not verify_in_isolation(LIFE, key, (1, 0), 1)


def test_noise_control_is_deterministic_and_structureless():
    spec = UniverseSpec(NoiseControl(0.3).to_dict(), 5, 64, 64, 0.3)
    a, b = study(spec, steps=200), study(spec, steps=200)
    assert a.final_hash == b.final_hash
    assert a.cls == "chaotic" and a.metrics["self_propelled_shapes"] == 0


def test_activity_trend_flags_fading():
    """Synthetic frames whose number of changing cells declines linearly to zero."""
    from emergence.observatory import Observer
    rng = np.random.default_rng(0)
    obs = Observer(total_steps=200, window=50)
    g = (rng.random((32, 32)) < 0.5).astype(np.uint8)
    obs.observe(0, g)
    for t in range(1, 201):
        g = g.copy()
        k = max(0, 200 - t)  # cells flipped this step
        idx = rng.choice(g.size, size=k, replace=False)
        g.flat[idx] ^= 1
        obs.observe(t, g)
    m = obs.finalize().metrics
    assert m["activity_trend"] < 0.5   # last window much quieter than the one before
    steady = Observer(total_steps=100, window=30)
    g = (rng.random((32, 32)) < 0.5).astype(np.uint8)
    for t in range(101):
        g = g.copy()
        g.flat[rng.choice(g.size, size=100, replace=False)] ^= 1
        steady.observe(t, g)
    assert 0.8 < steady.finalize().metrics["activity_trend"] < 1.25


def test_niche_binning_separates_families():
    m = {"spacetime_ratio": 0.5, "activity_late": 0.1, "local_periodic_frac": 0.0, "damage_norm": 0.3,
         "self_propelled_shapes": 2}
    assert niche_of("B3/S23", m) != niche_of("B2/S/C3", m)
    assert niche_of("B3/S23", m).startswith("2state") and "mov1" in niche_of("B3/S23", m)


def test_screening_followups_and_extension(tmp_path):
    cfg = ExploreConfig(population=8, generations=2, steps=100, window=50, width=32, height=32,
                        screen_seeds=2, followups=2, followup_seeds=1, extend_factor=3, seed=3, workers=1)
    store = Store(tmp_path / "x.db")
    eid = Explorer(store, cfg, log=lambda *_: None).run()
    explore, screens = store.universes(eid, role="explore"), store.universes(eid, role="screen")
    assert len(explore) == 16 and len(screens) == 16
    assert all(s["parent_id"] in {u["id"] for u in explore} for s in screens)
    assert all(u["aggregate"] and len(u["aggregate"]["runs"]) == 2 for u in explore)
    fups = store.universes(eid, role="followup")
    assert any(f["steps"] == 300 for f in fups)  # extended runs
    for d in store.discoveries(eid):
        assert d["kind"].split("/")[-1] in {"persists", "fades", "loops"}
        assert "extended_id" in d["evidence"]


def test_old_database_is_migrated(tmp_path):
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE universes (id INTEGER PRIMARY KEY, experiment_id INTEGER, generation INTEGER, role TEXT,"
                " parent_id INTEGER, rule TEXT, spec TEXT, steps INTEGER, window INTEGER, class TEXT, metrics TEXT,"
                " descriptor TEXT, timeseries TEXT, final_hash TEXT, final_state BLOB, novelty REAL,"
                " pareto_rank INTEGER, priority INTEGER, created_at REAL)")
    con.commit()
    con.close()
    Store(path)
    cols = {r[1] for r in sqlite3.connect(path).execute("PRAGMA table_info(universes)")}
    assert "aggregate" in cols


def test_benchmark_passes():
    r = run_benchmark(seeds=1, steps=300, log=lambda *_: None)
    assert r["passed"] == r["total"], [c for c in r["cases"] if not all(x["ok"] for x in c["runs"])]


def test_cycling_extended_run_is_not_persisting(tmp_path):
    """Regression: an extended run that ends in an exact cycle must be 'fades', not 'persists'."""
    cfg = ExploreConfig(population=6, generations=1, steps=80, window=40, width=24, height=24,
                        screen_seeds=1, followups=3, followup_seeds=1, extend_factor=3, seed=11, workers=1)
    store = Store(tmp_path / "y.db")
    eid = Explorer(store, cfg, log=lambda *_: None).run()
    for d in store.discoveries(eid):
        ext = store.universe(d["evidence"]["extended_id"])
        if ext["metrics"]["cycle_found"]:
            assert d["kind"].split("/")[-1] in {"fades", "loops"} and not d["evidence"]["persists"]


def test_calibration_separates_seed_noise_from_rule_differences():
    from emergence.discovery import calibrate
    rng = np.random.default_rng(0)
    prim = [{"id": i, "descriptor": rng.random(5).tolist()} for i in range(40)]
    screens = {p["id"]: [{"descriptor": (np.array(p["descriptor"]) + rng.normal(0, 0.01, 5)).tolist()}] for p in prim}
    cal = calibrate(prim, screens, seed=1)
    assert cal["n_within"] == 40 and cal["threshold"] < np.median(cal["between"]) / 5


def test_random_baseline_never_breeds(tmp_path):
    cfg = ExploreConfig(population=6, generations=3, steps=60, window=30, width=24, height=24, screen_seeds=1,
                        followups=0, seed=5, workers=1, selection="random")
    store = Store(tmp_path / "r.db")
    eid = Explorer(store, cfg, log=lambda *_: None).run()
    assert all(u["parent_id"] is None for u in store.universes(eid, role="explore"))


def test_replication_probe_controls():
    from emergence.benchmark_probes import HIGHLIFE_REPLICATOR, rle
    from emergence.observatory.replication import replication_test
    rng = np.random.default_rng(0)
    assert replication_test(OuterTotalistic.parse("B36/S23"), rle(HIGHLIFE_REPLICATOR), rng)["verdict"] == "self-replicator"
    assert replication_test(OuterTotalistic.parse("B1357/S1357"), rle("obo$3o$bo!"), rng)["verdict"] == "rule-level duplication"
    assert replication_test(LIFE, rle("bo$2bo$3o!"), rng)["verdict"] == "no replication"


def test_innovation_probe_glider_gun_is_not_innovating():
    from emergence.benchmark_probes import GOSPER_GUN, _placed, rle
    from emergence.observatory.innovation import innovation_profile
    inn = innovation_profile(_placed("B3/S23", rle(GOSPER_GUN), 300), steps=600, every=100)
    assert inn["new_second_half"] == 0 and inn["shapes_total"] >= 1


def test_followup_reports_evidence_level(tmp_path):
    cfg = ExploreConfig(population=6, generations=1, steps=80, window=40, width=24, height=24, screen_seeds=2,
                        followups=2, followup_seeds=1, extend_factor=2, seed=4, workers=1)
    store = Store(tmp_path / "e.db")
    eid = Explorer(store, cfg, log=lambda *_: None).run()
    for d in store.discoveries(eid):
        ev = d["evidence"]
        assert 0 <= ev["evidence_level"] <= 3 and ev["innovation"] is not None and ev["replication"] is not None
        assert "heredity/variation: not measured" in d["summary"]


def test_innovation_verdict_rules():
    from emergence.discovery import innovation_verdict
    probe = {"innovation": {"steps": 2000, "established_late": 6, "new_per_sample": [10] * 32}}
    cyc = {"metrics": {"cycle_found": True, "transient": 900}}
    assert innovation_verdict(probe, cyc, 0, 0.0)[0].startswith("none")          # aliasing in an exact cycle
    assert innovation_verdict(probe, None, 0, 0.45)[0].startswith("inconclusive")  # flat turnover + chaos-like
    dec = {"innovation": {"steps": 2000, "established_late": 6, "new_per_sample": [20] * 8 + [5] * 16 + [2] * 8}}
    assert innovation_verdict(dec, None, 0, 0.45)[0] == "still innovating"
    assert innovation_verdict(probe, None, 6, 0.0)[0].startswith("no evidence")   # at the noise floor


def test_innovation_that_ends_is_not_ongoing():
    from emergence.discovery import innovation_verdict
    dec = {"innovation": {"steps": 2000, "established_late": 10, "new_per_sample": [20] * 8 + [5] * 16 + [2] * 8}}
    settled_late = {"cls": "periodic", "metrics": {"cycle_found": True, "transient": 1737, "local_periodic_frac": 1.0}}
    oscillating = {"cls": "periodic", "metrics": {"cycle_found": False, "transient": None, "local_periodic_frac": 0.97}}
    assert innovation_verdict(dec, settled_late, 0, 0.0)[0].startswith("transient innovation that ended")
    assert innovation_verdict(dec, oscillating, 0, 0.0)[0].startswith("transient innovation that ended")


def test_initial_conditions_are_backward_compatible_and_deterministic():
    from emergence.engine import INIT_KINDS, state_hash
    base = UniverseSpec(LIFE.to_dict(), 7, 48, 48, 0.35)
    explicit = UniverseSpec(LIFE.to_dict(), 7, 48, 48, 0.35, init={"kind": "uniform"})
    assert "init" not in base.to_dict()                       # old specs serialise unchanged
    assert state_hash(Universe.from_spec(base).state) == state_hash(Universe.from_spec(explicit).state)
    for kind in INIT_KINDS:
        spec = UniverseSpec(LIFE.to_dict(), 3, 48, 48, 0.35, init={"kind": kind})
        a, b = Universe.from_spec(spec).state, Universe.from_spec(UniverseSpec.from_dict(spec.to_dict())).state
        assert np.array_equal(a, b) and a.any()
    patch = Universe.from_spec(UniverseSpec(LIFE.to_dict(), 3, 48, 48, 0.35, init={"kind": "patch"})).state
    assert patch[:6].sum() == 0 and patch[18:30, 18:30].sum() > 0  # matter only in the centre


def test_knockout_controls():
    from emergence.benchmark_probes import rle
    from emergence.observatory.knockout import knockout_compare, types_over
    g = np.zeros((90, 90), np.uint8)
    g[5:8, 5:8] = rle("bo$2bo$3o!")
    g[30:32, 26:28] = 1
    g[75:77, 70:72] = 1
    glider = np.zeros(g.shape, bool)
    glider[5:8, 5:8] = g[5:8, 5:8] > 0
    far = np.zeros(g.shape, bool)
    far[75:77, 70:72] = True
    before = set(types_over(Universe(LIFE, g.copy()), 40, 20))
    assert knockout_compare(LIFE, g, glider, [far], before, 500, 25)["verdict"] == "depends"
    assert knockout_compare(LIFE, g, far, [far], before, 500, 25)["verdict"] == "independent"


def test_lenia_physics_and_continuous_detector():
    from emergence.observatory import continuous as C
    from emergence.physics import Lenia, parse_rule, physics_from_dict
    orb = parse_rule("LENIA/R13/T10/m0.150/s0.0150/b1")
    assert isinstance(orb, Lenia) and physics_from_dict(orb.to_dict()).label() == orb.label()
    rng = np.random.default_rng(0)
    for _ in range(20):
        p = Lenia.random(rng).mutate(rng)
        assert parse_rule(p.label()).label() == p.label()
    gl = C.emergent_glider(orb)
    assert C.self_propelled(orb, gl, max(C.objects(gl), key=lambda o: o["mass"]))
    # torus-aware labelling: an object split by the seam is one object
    split = np.roll(gl, (0, 64 - 106), axis=(0, 1))
    split = np.roll(split, (0, 64), axis=(0, 1))  # now straddles the seam
    assert len(C.objects(gl)) == len(C.objects(split)) == 1


def test_lenia_initial_conditions_have_values():
    from emergence.physics import parse_rule
    spec = UniverseSpec(parse_rule("LENIA/R13/T10/m0.150/s0.0150/b1").to_dict(), 2, 64, 64, 0.3, init={"kind": "patch"})
    s = Universe.from_spec(spec).state
    assert s.max() > 100 and s[:8].sum() == 0


ORBIUM = "LENIA/R13/T10/m0.150/s0.0150/b1"


def test_tolerant_measures_ignore_rounding_jitter_and_keep_exact_default():
    from emergence.observatory import measures as M
    rng = np.random.default_rng(0)
    base = np.where(rng.random((32, 32)) < 0.3, 200, 0).astype(np.uint8)
    jit = (base & 0xFE) | (rng.integers(0, 2, base.shape, dtype=np.uint8) * (base > 0))
    assert M.activity(base, jit) > 0 and M.activity(base, jit, tol=2) == 0
    big = base.copy()
    big[0, 0] = 255 - big[0, 0]
    assert M.activity(base, big, tol=2) == 1 / base.size
    stack = np.stack([(base & 0xFE) | (rng.integers(0, 2, base.shape, dtype=np.uint8) * (base > 0))
                      for _ in range(12)])
    assert M.local_periodicity(stack)["local_periodic_frac"] < 0.5
    assert M.local_periodicity(stack, tol=2)["active_cell_frac"] == 0.0


def test_lenia_static_blob_field_is_not_complex_but_gliders_are():
    """The v0.5 bug: a field of static blobs was labelled complex (J-012)."""
    from emergence.discovery import OBJECTIVES, run_settled
    from emergence.observatory import continuous as C
    from emergence.physics import parse_rule
    orb = parse_rule(ORBIUM)
    soup = Universe.from_spec(UniverseSpec(orb.to_dict(), 1, 96, 96, 0.35))
    soup.step(300)
    o = study_universe(Universe(orb, soup.state.copy()), 1, steps=200)
    m = o.metrics
    assert m["vocabulary"] >= 4 and m["self_propelled_shapes"] == 0
    assert o.cls != "complex" and m["quasi_static"] and run_settled(m, o.cls)
    assert OBJECTIVES["vocabulary"](m) == m["dynamic_structures"] == 0
    assert OBJECTIVES["aperiodic_activity"](m) < 0.002
    gl = C.emergent_glider(orb)
    two = np.maximum(np.roll(gl, (-32, -60), axis=(0, 1)), np.roll(gl, (32, -60), axis=(0, 1)))
    g = study_universe(Universe(orb, two), 1, steps=200)
    assert g.cls == "complex" and not g.metrics["quasi_static"] and g.metrics["self_propelled_shapes"] == 2


def test_discrete_labels_and_objectives_ignore_continuous_keys():
    from emergence.discovery import OBJECTIVES
    o = study(UniverseSpec(LIFE.to_dict(), 1, 64, 64, 0.35), steps=200)
    m = o.metrics
    assert "continuous" not in m and "quasi_static" not in m
    assert OBJECTIVES["vocabulary"](m) == m["vocabulary"]
    assert OBJECTIVES["aperiodic_activity"](m) == m["activity_late"] * (1 - m["local_periodic_frac"])


def test_jitter_control_is_a_near_fixed_point():
    from emergence.physics import JitterControl
    j = JitterControl()
    o = study_universe(Universe(j, j.random_state(np.random.default_rng(3), (64, 64), 0.3)), 1, steps=120)
    assert not o.metrics["cycle_found"] and o.cls == "frozen"


def test_lenia_mutation_always_changes_the_rule():
    from emergence.physics import Lenia
    rng = np.random.default_rng(1)
    single = Lenia.parse(ORBIUM)
    for _ in range(300):
        c = single.mutate(rng)
        assert c.label() != single.label() and Lenia.parse(c.label()).label() == c.label()


def test_emergent_glider_speed_matches_docstring():
    from emergence.observatory import continuous as C
    from emergence.physics import parse_rule
    orb = parse_rule(ORBIUM)
    w = C.emergent_glider(orb)
    c = max(C.objects(w), key=lambda o: o["mass"])["c"]
    path = np.zeros(2)
    for _ in range(8):  # 25-step legs, so no leg wraps around the 128-cell torus
        for _ in range(25):
            w = orb.step(w)
        c1 = max(C.objects(w), key=lambda o: o["mass"])["c"]
        path += C._torus_delta(c, c1, w.shape)
        c = c1
    assert 0.45 <= np.hypot(*path) / 200 <= 0.6


def test_smooth_init_matches_soup_mass_and_is_deterministic():
    from scipy import ndimage
    from emergence.physics import parse_rule
    orb = parse_rule(ORBIUM).to_dict()
    for d in (0.15, 0.35):
        soup_mass = 0.5 * d * 96 * 96  # expected mass of the soup: density x mean value 0.5
        for ell in (3, 10):
            spec = UniverseSpec(orb, 5, 96, 96, d, init={"kind": "smooth", "ell": ell})
            s = Universe.from_spec(spec).state
            assert abs(s.sum() / 255 / soup_mass - 1) < 0.005
            assert np.array_equal(s, Universe.from_spec(spec).state)
            assert (s > 0).mean() > d  # matched by mass, not by occupied cells
    # longer ell = smoother field: neighbouring cells more alike
    rough, smooth = (Universe.from_spec(UniverseSpec(orb, 5, 96, 96, 0.35, init={"kind": "smooth", "ell": e})).state
                     .astype(float) for e in (3, 10))
    grad = lambda a: np.abs(np.diff(a, axis=1)).mean() / a.std()  # noqa: E731
    assert grad(smooth) < grad(rough)
    # discrete physics: occupied fraction = density, states 0/1
    x = Universe.from_spec(UniverseSpec(LIFE.to_dict(), 5, 96, 96, 0.35, init={"kind": "smooth", "ell": 3})).state
    assert set(np.unique(x)) == {0, 1} and abs(x.mean() - 0.35) < 0.001
    assert ndimage.label(x)[1] < ndimage.label(np.random.default_rng(0).random((96, 96)) < 0.35)[1]


def test_conditions_skip_exact_shape_probes_for_continuous_physics():
    from emergence.conditions import NOT_APPLICABLE, _job, init_of
    from emergence.physics import parse_rule
    assert init_of("uniform") is None and init_of("patch") == {"kind": "patch"}
    assert init_of("smooth:3") == {"kind": "smooth", "ell": 3.0}
    spec = UniverseSpec(parse_rule(ORBIUM).to_dict(), 1, 48, 48, 0.35, init=init_of("smooth:6")).to_dict()
    res = _job((spec, 60, 30))
    assert res["extra"] == {"innovation": None, "innovation_verdict": NOT_APPLICABLE, "knockout": None}


def test_chan_patches_init():
    from emergence.physics import parse_rule
    spec = UniverseSpec(parse_rule(ORBIUM).to_dict(), 4, 128, 128, 0.35, init={"kind": "patches", "n": 20})
    s = Universe.from_spec(spec).state
    assert np.array_equal(s, Universe.from_spec(spec).state)
    assert 0 < (s > 0).mean() < 20 * 144 / s.size + 1e-9 and s.max() <= round(0.9 * 255)
    d = Universe.from_spec(UniverseSpec(LIFE.to_dict(), 4, 128, 128, 0.35, init={"kind": "patches"})).state
    assert set(np.unique(d)) <= {0, 1} and 0 < d.mean() < 0.5
FLOW_STATIC = "FLENIA/R13/m0.326/s0.0041/h0.2/r0.89/a0.08,0.2,0.63/b0.1,0.15,0.18/w0.075,0.492,0.385"
FLOW_WANDER = "FLENIA/R13/m0.082/s0.1634/h0.65/r0.36/a0.59,0.9,0.45/b0.2,0.36,0.04/w0.41,0.248,0.406"


def test_flow_lenia_rule_labels_round_trip_and_mutation_changes_them():
    from emergence.physics import FlowLenia, parse_rule, physics_from_dict
    rng = np.random.default_rng(5)
    for _ in range(30):
        p = FlowLenia.random(rng)
        assert parse_rule(p.label()).label() == p.label() and physics_from_dict(p.to_dict()) == p
        assert p.continuous and 1 <= p.rule_features()["kernels"] <= 3
        c = p.mutate(rng)
        assert c.label() != p.label() and parse_rule(c.label()).label() == c.label()
    single = parse_rule(FLOW_STATIC)
    for _ in range(200):
        assert single.mutate(rng).label() != single.label()
    assert parse_rule("FLENIA/R13/diffusion").diffusion_only


def test_flow_lenia_conserves_mass_in_float32():
    from emergence.physics import FlowLenia, parse_rule
    p = parse_rule(FLOW_WANDER)
    s = FlowLenia.patch_state(np.random.default_rng(2), (64, 64), side=24)
    m0, A = s.sum(dtype=np.float64), s.astype(np.float64)
    for _ in range(1000):
        s, A = p.step(s), p.step_float(A)
    assert s.dtype == np.float32 and abs(s.sum(dtype=np.float64) - m0) / m0 < 1e-6  # float32 rounding
    assert abs(A.sum() - m0) / m0 < 1e-10                                            # float64 core


def test_float_states_through_engine_storage_and_observer():
    from emergence.engine import state_hash
    from emergence.physics import FlowLenia, parse_rule
    from emergence.storage import pack_state, unpack_state
    p = parse_rule(FLOW_WANDER)
    u = Universe.from_spec(UniverseSpec(p.to_dict(), 3, 48, 48, 0.3))
    assert u.state.dtype == np.float32 and 0 < u.state.max() <= 1 and u.fork().state.dtype == np.float32
    back = unpack_state(pack_state(u.state), 48, 48)
    assert back.dtype == np.float32 and np.array_equal(back, u.state)
    assert state_hash(u.state) == state_hash(back) != state_hash(p.view(u.state))
    assert unpack_state(pack_state(p.view(u.state)), 48, 48).dtype == np.uint8
    o = study(UniverseSpec(p.to_dict(), 3, 48, 48, 0.3), steps=60)
    assert o.final_state.dtype == np.float32 and o.metrics["continuous"]
    assert isinstance(FlowLenia.patch_state(np.random.default_rng(0), (48, 48), 20)[0, 0], np.float32)


def test_flow_lenia_rotated_seed_evolves_rotated():
    from emergence.physics import FlowLenia, parse_rule
    p = parse_rule(FLOW_WANDER)
    s = FlowLenia.patch_state(np.random.default_rng(3), (64, 64), side=24)
    a, b = s.copy(), np.rot90(s).copy()
    for _ in range(100):
        a, b = p.step(a), p.step(b)
    assert (np.abs(np.rot90(a) - b) > 2 / 255).mean() < 0.01


def test_flow_lenia_static_blob_rule_is_not_complex():
    from emergence.physics import FlowLenia, parse_rule
    p = parse_rule(FLOW_STATIC)
    o = study_universe(Universe(p, FlowLenia.patch_state(np.random.default_rng(1), (96, 96))), 1, steps=300)
    assert o.cls != "complex" and o.metrics["self_propelled_shapes"] == 0 and o.metrics["quasi_static"]


def test_smooth_shuffled_has_same_values_but_no_correlation():
    from emergence.physics import parse_rule
    orb = parse_rule(ORBIUM).to_dict()
    sm = Universe.from_spec(UniverseSpec(orb, 9, 96, 96, 0.1, init={"kind": "smooth", "ell": 3})).state
    sh = Universe.from_spec(UniverseSpec(orb, 9, 96, 96, 0.1, init={"kind": "smooth_shuffled", "ell": 3})).state
    assert np.array_equal(np.sort(sm.ravel()), np.sort(sh.ravel())) and not np.array_equal(sm, sh)
    corr = lambda a: np.corrcoef(a[:, :-1].ravel(), a[:, 1:].ravel())[0, 1]  # noqa: E731
    assert corr(sm.astype(float)) > 0.5 and abs(corr(sh.astype(float))) < 0.05
