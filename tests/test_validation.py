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
    assert a["mover_shapes"] >= 1 and a["verified_mover_shapes"] == a["mover_shapes"]


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
    assert a["verified_mover_shapes"] == 0  # rejected
    key = next(iter(census(frames[0])))
    assert not verify_in_isolation(LIFE, key, (1, 0), 1)


def test_noise_control_is_deterministic_and_structureless():
    spec = UniverseSpec(NoiseControl(0.3).to_dict(), 5, 64, 64, 0.3)
    a, b = study(spec, steps=200), study(spec, steps=200)
    assert a.final_hash == b.final_hash
    assert a.cls == "chaotic" and a.metrics["verified_mover_shapes"] == 0


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
         "verified_mover_shapes": 2}
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
