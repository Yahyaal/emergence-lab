import numpy as np
import pytest

from emergence.engine import Universe, UniverseSpec, run, state_hash
from emergence.physics import OuterTotalistic, physics_from_dict

LIFE = OuterTotalistic.parse("B3/S23")


def grid(cells, n=16):
    g = np.zeros((n, n), np.uint8)
    for r, c in cells:
        g[r, c] = 1
    return g


def test_rule_roundtrip():
    for rule in ["B3/S23", "B36/S23", "B2/S/C3", "B/S", "B1357/S02468/C5"]:
        p = OuterTotalistic.parse(rule)
        assert p.label() == rule
        assert physics_from_dict(p.to_dict()) == p


def test_bad_rule():
    with pytest.raises(ValueError):
        OuterTotalistic.parse("B9/S23")


def test_blinker_period_two():
    g = grid([(5, 4), (5, 5), (5, 6)])
    g2 = LIFE.step(LIFE.step(g))
    assert np.array_equal(g, g2) and not np.array_equal(g, LIFE.step(g))


def test_glider_translates_on_torus():
    g = grid([(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)])
    s = g
    for _ in range(4):
        s = LIFE.step(s)
    assert np.array_equal(s, np.roll(g, (1, 1), axis=(0, 1)))
    for _ in range(4 * 15):
        s = LIFE.step(s)
    assert np.array_equal(s, g)  # wrapped all the way round a 16x16 torus


def test_generations_decay():
    p = OuterTotalistic.parse("B2/S/C3")  # Brian's Brain
    g = grid([(5, 5)])
    s1 = p.step(g)
    assert s1[5, 5] == 2  # alive -> dying
    assert p.step(s1)[5, 5] == 0


def test_step_does_not_mutate_input():
    g = grid([(5, 4), (5, 5), (5, 6)])
    before = g.copy()
    LIFE.step(g)
    assert np.array_equal(g, before)


def test_universe_state_is_read_only():
    u = Universe.from_spec(UniverseSpec(LIFE.to_dict(), seed=1, width=16, height=16))
    with pytest.raises(ValueError):
        u.state[0, 0] = 1


def test_determinism():
    spec = UniverseSpec(LIFE.to_dict(), seed=123, width=32, height=32, density=0.3)
    a = [state_hash(s) for _, s in run(spec, 50)]
    b = [state_hash(s) for _, s in run(spec, 50)]
    assert a == b


def test_random_and_mutate_stay_valid():
    rng = np.random.default_rng(0)
    for _ in range(200):
        p = OuterTotalistic.random(rng)
        q = p.mutate(rng)
        assert 0 not in p.birth and 0 not in q.birth and p.birth and q.birth
        assert OuterTotalistic.parse(q.label()) == q


def test_flow_lenia_pl_matches_flow_lenia_and_conserves_weights():
    from emergence.physics import FlowLenia, FlowLeniaPL, parse_rule, physics_from_dict
    from emergence.physics.flow_lenia import reintegrate, reintegrate_many
    rng = np.random.default_rng(0)
    A = rng.random((2, 32, 32))
    dy, dx = rng.uniform(-4.3, 4.3, (2, 32, 32))
    assert np.allclose(reintegrate_many(A, dy, dx), np.stack([reintegrate(c, dy, dx) for c in A]), atol=1e-12)
    fl = FlowLenia.random(np.random.default_rng(5))
    pl = FlowLeniaPL(fl.kernels, fl.R)
    a0 = FlowLenia.patch_state(np.random.default_rng(1), (48, 48), side=20).astype(np.float64)
    a, s = a0.astype(np.float32), pl.localize(a0)
    for _ in range(50):
        a, s = fl.step(a), pl.step(s)
    assert abs(s[0] - a).max() < 1e-4
    q0 = pl.localize(a0, pl._h * 1.3).astype(np.float64).sum((1, 2))
    s = pl.localize(a0, pl._h * 1.3)
    for _ in range(50):
        s = pl.step(s)
    assert np.allclose(s.astype(np.float64).sum((1, 2)), q0, rtol=1e-5)
    fed = FlowLeniaPL(fl.kernels, fl.R, 0.05)
    assert parse_rule(fed.label()) == fed and physics_from_dict(fed.to_dict()) == fed
    assert np.array_equal(fed.step(fed.vacuum((32, 32))), fed.vacuum((32, 32)))


def test_multi_lenia_one_channel_is_lenia_and_rules_roundtrip():
    from emergence.physics import Lenia, MKernel, MultiLenia, parse_rule, physics_from_dict
    orb = Lenia.parse("LENIA/R13/T10/m0.150/s0.0150/b1")
    ml = MultiLenia(1, [MKernel(0, 0, 1, orb.mu, orb.sigma, 1, orb.peaks)])
    a = np.random.default_rng(0).random((48, 48))
    lenia_float = np.clip(a + (2 * np.exp(-((np.fft.irfft2(np.fft.rfft2(a) * orb._kernel(a.shape), s=a.shape)
                                              - orb.mu) ** 2) / (2 * orb.sigma ** 2)) - 1) / orb.T, 0, 1)
    assert abs(ml.step(a[None].astype(np.float32))[0] - lenia_float).max() < 1e-6
    rng = np.random.default_rng(3)
    for _ in range(50):
        p = MultiLenia.random(rng)
        q = p.mutate(rng)
        assert q.label() != p.label()
        assert parse_rule(p.label()) == p and physics_from_dict(q.to_dict()) == q
        assert {k.tgt for k in p.kernels} == set(range(p.C))
    s = p.random_state(rng, (32, 32), 0.3)
    s2 = p.step(s)
    assert s2.shape == s.shape and s2.dtype == np.float32 and 0 <= s2.min() and s2.max() <= 1
    assert np.array_equal(p.step(s), s2)
    assert not np.array_equal(s, s2)
    with pytest.raises(ValueError):
        MultiLenia(2, [MKernel(0, 0, 1, 0.15, 0.015, 1, (1,))])  # channel 1 has no kernel
