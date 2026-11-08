import numpy as np

from emergence.observatory import replicators as RP
from emergence.programs import bff as B


def test_c_interpreter_matches_python_reference():
    rng = np.random.default_rng(3)
    for _ in range(200):
        t = rng.integers(0, 256, 128, dtype=np.uint8)
        m = rng.random(128) < 0.4
        t[m] = rng.choice(np.frombuffer(b"<>{}-+.,[]", np.uint8), m.sum())
        a, sa = B.run(t, 1000)
        b, sb = B.run_py(t, 1000)
        assert sa == sb and (a == b).all()


def test_hand_written_replicator_copies_itself_exactly():
    rng = np.random.default_rng(0)
    for _ in range(5):
        a, b = B.interact(B.REPLICATOR, rng.integers(0, 256, 64, dtype=np.uint8))
        assert (a == B.REPLICATOR).all() and (b == B.REPLICATOR).all()


def test_soup_modes_and_mutation():
    s = B.Soup(n=64, mode="noexec", mutation=0.0, seed=1)
    before = s.programs.copy()
    s.epoch()
    assert (s.programs == before).all()
    s = B.Soup(n=64, mode="noexec", mutation=0.05, seed=1)
    before = s.programs.copy()
    s.epoch()
    assert 0.02 < (s.programs != before).mean() < 0.08


def test_replicator_detector_controls():
    assert RP.replication_test(B.REPLICATOR, np.random.default_rng(1))["verdict"] == "replicator"
    assert RP.replication_test(np.zeros(64, np.uint8), np.random.default_rng(1))["verdict"] == "no replication"
    assert RP.replication_test(B.REPLICATOR, np.random.default_rng(1), mode="noexec")["verdict"] == "no replication"


def test_program_heredity_controls():
    import numpy as np
    from emergence.observatory import program_heredity as PH
    from emergence.programs import bff as B
    assert PH.heredity_test(B.REPLICATOR, np.random.default_rng(3), mutants=8)["inherited"] >= 4
    assert PH.heredity_test(B.REPLICATOR, np.random.default_rng(3), mode="noexec", mutants=4)["verdict"] == "no variation"
    assert PH.sign_p(6, 6) == 1 / 64


def test_program_selection_controls():
    import numpy as np
    from emergence.observatory import program_selection as PS
    from emergence.programs import bff as B
    r = PS.compete(B.REPLICATOR, PS.mutant(B.REPLICATOR, 3, 0x80), 3, np.random.default_rng(2), reps=4)
    assert r["verdict"] == "parent favoured"


def test_family_contest():
    import numpy as np
    import pytest
    from emergence.observatory import program_selection as PS
    from emergence.programs import bff as B
    x = B.REPLICATOR
    y = PS.retail(x, np.random.default_rng(1))
    assert (x == y).mean() < 0.9 and not set(y[27:].tolist()) & set(b"<>{}+-.,[]\x00")
    assert PS.sign_p(8, 8) == 2 / 256 and PS.sign_p(4, 8) == 1.0
    r = PS.compete_families(x, PS.mutant(y, 3, 0x80), np.random.default_rng(2), reps=8)
    assert r["verdict"] == "a favoured"
    with pytest.raises(ValueError):
        PS.compete_families(x, x, np.random.default_rng(0), reps=1)


def test_growth_rate_assay():
    from emergence.observatory import program_fitness as F
    rng = np.random.default_rng(0)
    assert (F.trapped(0) == B.REPLICATOR).all()
    assert abs(F.trap_p(1) - 0.5) < 0.05
    full = F.growth_rate(F.trapped(0), rng, bg="halting", reps=3)
    half = F.growth_rate(F.trapped(1), rng, bg="halting", reps=3)
    assert abs(full["r"] - F.theory(1.0)) < 0.04 and abs(half["r"] - F.theory(F.trap_p(1))) < 0.04
    assert F.growth_rate(F.non_copier(), rng, bg="halting", reps=2)["r"] < 0.01
    ps = F.pair_stats(B.REPLICATOR, rng, bg="halting", partners=16)
    assert ps["p"] == ps["s1"] == ps["s2"] == 1.0
