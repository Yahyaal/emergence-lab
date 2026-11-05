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
