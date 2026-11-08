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
