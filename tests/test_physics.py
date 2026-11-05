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
