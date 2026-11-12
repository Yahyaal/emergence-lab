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


def test_parasite_detector_controls():
    from emergence.observatory import program_parasites as PP
    rng = np.random.default_rng(3)
    hp = PP.hand_parasite()
    r = PP.parasite_test(hp, PP.host_pool(rng, guest=hp), rng, alone="no replication", m=64, m_prod=256, scrambles=2)
    assert r["verdict"] == "parasite" and r["q_scrambled"] == 0
    r = PP.parasite_test(PP.inert(), PP.host_pool(rng, guest=PP.inert()), rng, alone="no replication", m=64, m_prod=256)
    assert r["verdict"] == "not copied"
    r = PP.parasite_test(rng.integers(0, 256, 64, dtype=np.uint8), PP.host_pool(rng), rng, mode="copyall",
                         alone="no replication", m=64, m_prod=256)
    assert r["verdict"] == "unspecific copying"
    assert PP.parasite_test(hp, PP.host_pool(rng), rng, alone="replicator", m=16, m_prod=16)["verdict"] == "self-copier"


def test_tape_length_parameter():
    """E-68/D-050: bff_kernels.set_length scales L, THR and MAXSHIFT; L = 64 gives the old constants, and the
    forward copy loop is a forward copier at h1 = L (aligned) for a short length too, but not at h1 = 0."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bff_kernels as K
    try:
        K.set_length(16)
        assert (K.L, K.THR, K.MAXSHIFT) == (16, 15, 4)
        x = np.full((1, 16), 0x80, np.uint8)
        x[0, :5] = np.frombuffer(b"[.>}]", np.uint8)
        c, sh = K.classify_shift(x, 16, 4, 1)
        assert K.label(c[0]) == "forward" and sh[0] == 0
        assert K.label(K.classify_shift(x, 0, 4, 1)[0][0]) != "forward"
    finally:
        K.set_length(64)
    assert (K.L, K.THR, K.MAXSHIFT) == (64, 60, 16)


def test_instruction_set_variants():
    """E-70: code = h1 + 65536 * v selects a variant in bff_kernels.c run(). v = 0 is standard BFF (same tape as
    the soup interpreter); v1 ('.' then both heads +1) makes the 3-instruction loop '[.]' a forward copier at
    h1 = 64, which it is not in standard BFF; v4 ('[' tests head1) changes the result of a loop."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bff_kernels as K
    rng = np.random.default_rng(70)
    tape = rng.integers(0, 256, 128, dtype=np.uint8)
    a, b = tape.copy(), tape.copy()
    K.lib().run_tape(a.ctypes.data, 128, K.STEPS, 64)
    K.lib().run_tape(b.ctypes.data, 128, K.STEPS, 64 + 65536 * 0)
    assert (a == b).all()
    x = K.NONOP_NZ[rng.integers(0, len(K.NONOP_NZ), (1, 64))]
    x[0, :3] = np.frombuffer(b"[.]", np.uint8)
    assert K.label(K.classify_shift(x, 64 + 65536, 4, 1)[0][0]) == "forward"
    assert K.label(K.classify_shift(x, 64, 4, 1)[0][0]) == "none"
    t = np.zeros(128, np.uint8)
    t[:3] = np.frombuffer(b"[+]", np.uint8)  # head0 byte is '[' (nonzero): standard loops; head1 at 64 is 0
    s0, s4 = t.copy(), t.copy()
    K.lib().run_tape(s0.ctypes.data, 128, 100, 64)
    K.lib().run_tape(s4.ctypes.data, 128, 100, 64 + 4 * 65536)
    assert s0[0] != t[0] and s4[0] == t[0]


def test_copy_fidelity_controls():
    """E-73/D-053: looser copy test (58/64 bytes + instruction-fidelity guard): sloppy and exact replicators found,
    nulls and filler smears rejected; thr 60 without the guard equals classify_shift."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bff_fidelity as F
    bad = [(n, d) for n, ok, d in F.controls() if not ok]
    assert not bad, bad


def test_subleq_interpreter_matches_reference():
    """E-75: SUBLEQ-family C interpreter == pure-Python reference, every knob."""
    import numpy as np
    from emergence.programs import subleq as Q
    rng = np.random.default_rng(1)
    for n in (3, 4):
        for j in range(4):
            for s in Q.S_VALUES:
                for W in Q.W_VALUES:
                    R = Q.Rule(n=n, j=j, s=s, W=W, o=int(rng.integers(128)), absolute=bool(rng.random() < 0.2))
                    assert Q.Rule.from_code(R.code) == R
                    t = rng.integers(0, 256, 128, dtype=np.uint8)
                    a, sa = Q.run(t, R, 2000)
                    b, sb = Q.run_py(t, R, 2000)
                    assert sa == sb and (a == b).all(), str(R)


def test_subleq_phase0_controls():
    """E-75 phase 0 / D-055: hand-written and emergent replicators found, nulls, random programs, smears and
    copy-all soups rejected, in SUBLEQ and (cross-check) on E-73's BFF fixtures."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import sq_phase0 as P0
    bad = [(n, d) for n, ok, d in P0.controls() if not ok]
    assert not bad, bad


def test_subleq_census_period_matches_census_hits():
    """D-057: sq_census_p with period = L reproduces sq_census exactly; tiles are periodic."""
    from emergence.programs import subleq as Q
    R = Q.Rule(4, 3, 1, 32, 120)
    n, h = Q.census_hits(R, 20000, 5)
    n2, h2, halt = Q.census_period(R, 20000, 5, 64)
    assert n == n2 and (h == h2).all() and 0 < halt < 20000
    _, t, _ = Q.census_period(R, 20000, 6, 4)
    assert len(t) and all((p == np.tile(p[:4], 16)).all() for p in t)
