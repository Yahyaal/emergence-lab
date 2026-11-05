import numpy as np

from emergence.engine import Universe, UniverseSpec, run, state_hash
from emergence.lab import study
from emergence.observatory import Observer
from emergence.observatory import measures as M
from emergence.observatory.recurrence import RecurrenceDetector
from emergence.observatory.structures import analyse
from emergence.physics import OuterTotalistic

LIFE = OuterTotalistic.parse("B3/S23")


def spec(rule, seed=1, n=64, density=0.35):
    return UniverseSpec(OuterTotalistic.parse(rule).to_dict(), seed=seed, width=n, height=n, density=density)


def test_compression_ratio_separates_noise_and_order():
    rng = np.random.default_rng(0)
    noise = (rng.random((64, 64)) < 0.5).astype(np.uint8)
    stripes = np.zeros((64, 64), np.uint8)
    stripes[::2] = 1
    assert M.compression_ratio(noise, rng) > 0.9
    assert M.compression_ratio(stripes, rng) < 0.3


def test_block_entropy_bounds():
    rng = np.random.default_rng(0)
    assert M.block_entropy(np.zeros((32, 32), np.uint8)) == 0.0
    assert M.block_entropy((rng.random((64, 64)) < 0.5).astype(np.uint8)) > 0.95


def test_recurrence_exact_and_shifted():
    g = np.zeros((16, 16), np.uint8)
    g[[0, 1, 2, 2, 2], [1, 2, 0, 1, 2]] = 1  # glider
    det = RecurrenceDetector()
    s = g
    for t in range(10):
        det.update(t, s)
        s = LIFE.step(s)
    assert det.result == {"period": 4, "transient": 0, "shift": (1, 1)}


def test_glider_detected_as_mover():
    g = np.zeros((32, 32), np.uint8)
    g[[1, 2, 3, 3, 3], [2, 3, 1, 2, 3]] = 1
    frames, s = [], g
    for _ in range(40):
        frames.append(s)
        s = LIFE.step(s)
    a = analyse(frames)
    assert a["mover_shapes"] >= 1 and a["mover_events"] > 0


def test_still_life_detected():
    g = np.zeros((16, 16), np.uint8)
    g[4:6, 4:6] = 1  # block
    a = analyse([g] * 20)
    assert a["still_structures"] == 1 and a["mover_events"] == 0


def test_local_periodicity_of_independent_oscillators():
    # two blinkers -> every changing cell is periodic
    g = np.zeros((32, 32), np.uint8)
    g[5, 4:7] = 1
    g[20, 10:13] = 1
    frames, s = [], g
    for _ in range(30):
        frames.append(s)
        s = LIFE.step(s)
    lp = M.local_periodicity(np.stack(frames))
    assert lp["local_periodic_frac"] == 1.0 and lp["active_cell_frac"] > 0


def test_known_rules_get_sensible_classes():
    assert study(spec("B8/S"), steps=100).cls == "extinct"
    assert study(spec("B2/S"), steps=200).cls == "chaotic"          # Seeds
    assert study(spec("B3/S12345"), steps=300).cls in {"frozen", "periodic"}  # Maze
    o = study(spec("B36/S23"), steps=500)                           # HighLife
    assert o.cls in {"complex", "periodic", "active"}


def test_damage_spreading_distinguishes_chaos_from_order():
    chaos = study(spec("B2/S"), steps=200).metrics["damage_norm"]
    order = study(spec("B3/S12345"), steps=200).metrics["damage_norm"]
    assert chaos > 0.5 > order


def test_observer_does_not_affect_universe():
    s = spec("B36/S23", seed=9, n=32)
    plain = [state_hash(x) for _, x in run(s, 80)]
    u = Universe.from_spec(s)
    obs = Observer(total_steps=80, window=40)
    observed = [state_hash(u.state)]
    obs.observe(0, u.state)
    for _ in range(80):
        u.step()
        obs.observe(u.t, u.state)
        observed.append(state_hash(u.state))
    obs.finalize()
    assert plain == observed


def test_study_is_reproducible():
    a, b = study(spec("B36/S23", seed=5), steps=200), study(spec("B36/S23", seed=5), steps=200)
    assert a.final_hash == b.final_hash and a.metrics == b.metrics and a.descriptor == b.descriptor
