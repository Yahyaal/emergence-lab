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


def test_subleq_product_census_prefilter():
    """D-061: the product-census pre-filter passes hand-written replicators, rejects random programs and the
    zero smear (constant blocks skipped); products() reports products that differ from their inputs."""
    from emergence.programs import subleq as Q
    for R, p in Q.POSITIVES.values():
        assert Q.prefilter(p, R, 3).all()
    R, z = Q.ZERO_SMEAR
    assert not Q.prefilter(z, R, 3).any()
    rnd = np.random.default_rng(4).integers(0, 256, (500, 64), dtype=np.uint8)
    assert Q.prefilter(rnd, Q.Rule(4, 0, 1, 32, 28), 3).sum() <= 5
    n, X, S, st = Q.products(Q.Rule(4, 0, 1, 32, 28), 20000, 9, maxhits=50)
    assert 0 < st["products"] <= 40000 and st["steps"] > 0 and len(X) == min(n, 50)
    for x, s in zip(X, S):
        assert (x[:64] != x[64 + 64 * s:128 + 64 * s]).any()  # a product differs from the input half it replaced
    soup = np.random.default_rng(5).integers(0, 256, (300, 64), dtype=np.uint8)
    keep = soup.copy()
    n, X, S, st = Q.products_from(Q.Rule(4, 0, 1, 32, 28), soup, 20000, 9, maxhits=50)
    assert (soup == keep).all() and st["products"] > 0 and len(X) == min(n, 50)
    rows = {r.tobytes() for r in soup}
    for x in X:  # both inputs are distinct members of the soup
        assert x[64:128].tobytes() in rows and x[128:].tobytes() in rows and (x[64:128] != x[128:]).any()


def test_spatial_soup_controls():
    """E-78 groundwork (scripts/bff_spatial.py): spatial pairs are a perfect matching of torus neighbours every
    round; the mixed arm equals bff.Soup bit for bit (50 rounds); under noexec both arms change nothing but
    mutation. The replicator-spread positive control is slower (~1 min) and runs in `--controls`."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bff_spatial as S
    assert S.check_matching(rounds=50)["pass"]
    assert S.check_matching(rounds=50, w=8, h=6)["pass"]
    assert S.check_mixed_identical(rounds=50)["pass"]
    nx = S.check_noexec(rounds=30)
    assert nx["pass"], nx
    r = S.spread("spatial", side=32, rounds=20, every=10)
    assert r["series"][-1]["copies"] > r["series"][0]["copies"] and r["series"][-1]["largest_component"] > 0.8


def test_e78_resume_exact():
    """E-78 driver (scripts/e78_run.py): a continuation interrupted after round 25 and resumed from its round-20
    snapshot (programs + saved generator state) equals an uninterrupted run, in both arms."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import e78_run as R
    r = R.check_resume()
    assert r["pass"], r


def test_lattice_assay_controls():
    """E-80 groundwork (scripts/lattice_assay.py, J-093): lineage-tag lattice assay. Positive (replicator front, parent
    trapped(0) outspreads handicapped trapped(1)), negative (same code, two labels), deceptive (filler smear fools byte
    identity but not the tag; persisting non-copier; kin in the resident; no tag drift under noexec + mutation), null
    (random-position garden blocks relabelled)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import lattice_assay as L
    bad = [(n, d) for n, ok, d in L.controls() if not ok]
    assert not bad, bad


def test_lattice_tag_update_rules():
    """Tag rules on hand-made before/after pairs: a forward or byte-reversed copy moves the tag, an unchanged half
    keeps it, a wiped half loses it, a filler smear does not move it."""
    import sys
    from pathlib import Path
    import numpy as np
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import lattice_assay as L
    from emergence.programs import bff as B
    rng = np.random.default_rng(0)
    x, q = B.REPLICATOR.copy(), rng.integers(0, 256, 64, dtype=np.uint8)
    before = np.stack([x, q, x, q, x, q, L.smear(), q])
    after = before.copy()
    after[1] = x               # pair 0: forward copy into the partner
    after[3] = x[::-1]         # pair 1: byte-reversed copy
    after[4] = 0               # pair 2: the tagged half is wiped (no copy)
    after[7] = 0x80            # pair 3: smear output, 94% like the smear, none of its instructions
    tags = np.array([1, 0, 1, 0, 1, 0, 1, 0], np.int32)
    new, anc, ev = L.update_tags(before, after, np.arange(8, dtype=np.int32), tags)
    assert list(new) == [1, 1, 1, 1, 0, 0, 1, 0], new
    assert ev["copies"] == 2 and ev["lost"] == 1
    assert (anc[1] == x).all() and (anc[3] == x).all()      # copies inherit the partner's anchor
    # a copy between two members of the same block (different programs, same tag) passes the anchor on
    y = x.copy()
    y[40:50] ^= 0x33                                          # a relative, < 90% like x
    nt, na, _ = L.update_tags(np.stack([x, y]), np.stack([x, x[::-1]]), np.array([0, 1], np.int32),
                              np.array([1, 1], np.int32), np.stack([x, y]))
    assert list(nt) == [1, 1] and (na[1] == x).all()
    # drift: a tagged half edited 4 bytes per round keeps its tag while >= 90% of its anchor, then loses it
    t, a2, cur = np.array([1, 0], np.int32), np.stack([x, q]), x.copy()
    for r in range(3):
        nxt = cur.copy()
        nxt[30 + 4 * r: 34 + 4 * r] ^= 0x55
        t, a2, _ = L.update_tags(np.stack([cur, q]), np.stack([nxt, q]), np.array([1, 0], np.int32), t, a2)
        cur = nxt
        assert t[0] == (1 if r == 0 else 0), (r, t)


def test_e80b_resume_and_rule():
    """E-80 Part B (scripts/e80b_run.py): an h = 64 arm interrupted and resumed equals an uninterrupted one (both
    pairings); the lattice assay at h1 = 0 equals the standard path; the hand-written h = 64 copier copies and its
    trap variant copies only when the partner's last byte is even."""
    import sys
    from pathlib import Path
    import numpy as np
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bff_kernels as K
    import e80b_run as E
    import lattice_assay as L
    from emergence.programs import bff as B
    assert E.check_resume()["pass"]
    rnd = np.random.default_rng(1).integers(0, 256, (1024, 64), dtype=np.uint8)
    blk = np.repeat(B.REPLICATOR[None], 16, 0)
    a = L.assay([blk], rnd, 5, k=4, rounds=12, identity=True)
    b = L.assay([blk], rnd, 5, k=4, rounds=12, identity=True, h1=0)
    assert a["series"] == b["series"] and a["identity"] == b["identity"]
    for last, want in ((0x82, True), (0x83, False)):
        q = rnd[0].copy()
        q[-1] = last
        for x, w in ((E.H0, True), (E.H1P, want)):
            t = np.concatenate([x, q]).copy()
            K.lib().run_tape(t.ctypes.data, 128, 8192, 64)
            assert bool((t[64:] == x).all()) == w


def test_bffvl_cut_rule():
    """E-81 (D-070): the BFF-VL cut rule on hand-made tapes: cut after each marker, at LMAX, never below LMIN, a short
    last piece merged (or the last cut moved back), bytes conserved."""
    import sys
    from pathlib import Path
    import numpy as np
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bffvl as V
    M = V.MARKER

    def tape(*parts):
        return np.concatenate([np.frombuffer(p, np.uint8) if isinstance(p, bytes) else np.full(p, 0x80, np.uint8)
                               for p in parts])
    assert V.cut(tape(5, bytes([M]), 9, bytes([M]))).tolist() == [6, 10]
    assert V.cut(tape(1, bytes([M]), 10)).tolist() == [12]                  # piece of 2 < LMIN: no cut
    assert V.cut(tape(300)).tolist() == [128, 128, 44]                       # forced cuts at LMAX
    assert V.cut(tape(127, bytes([M]), 2)).tolist() == [126, 4]  # last piece 2 < LMIN; merging would exceed LMAX
    assert V.cut(tape(10, bytes([M]), 2)).tolist() == [13]                   # last piece merged
    rng = np.random.default_rng(0)
    for _ in range(200):
        t = rng.integers(0, 256, int(rng.integers(8, 257)), dtype=np.uint8)
        t[rng.random(len(t)) < 0.1] = M
        c = V.cut(t)
        assert c.sum() == len(t) and c.min() >= V.LMIN and c.max() <= V.LMAX


def test_bffvl_controls():
    """E-81 groundwork (scripts/bffvl.py, scripts/bffvl_assay.py, J-097): the rule equals the h = 64 BFF soup with the
    marker off; copy screen, replicator detector and head-to-head assay each with positive, negative, deceptive and
    selection-aware null controls; the length-trend nulls (noexec stationary, copyall collapse)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bffvl_assay as A
    bad = [(n, d) for n, ok, d in A.controls() if not ok]
    assert not bad, bad


def test_bffx_rule():
    """E-82 (D-072): BFF-X equals BFF-VL with libmode live; the library is read only; an inert program that runs into a
    host's code is copied (neighbour and snapshot modes), and not without a host or with nothing to borrow."""
    import sys
    from pathlib import Path
    import numpy as np
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bffvl as V
    import bffx as X
    a, b = V.Soup(w=2 ** 14, seed=9), X.Soup(w=2 ** 14, seed=9, libmode="live")
    for _ in range(20):
        a.epoch()
        b.epoch()
    assert (a.buf == b.buf).all() and (a.lens == b.lens).all()
    H, P = X.hand_copier(12), X.pad(b"", 8)
    h0 = H.copy()
    assert X.screen(P, 1, 8, host_c=H)[0] == 8 and (H == h0).all()
    assert X.screen(P, 2, 8, host_b=X.hand_copier(64), libmode="snapshot")[0] == 8
    assert X.screen(P, 3, 8)[0] == 0 and X.screen(P, 4, 8, host_c=H, libmode="none")[0] == 0
    assert X.screen(H, 5, 8, libmode="none")[0] == 8


def test_bffx_controls():
    """E-82 groundwork (scripts/bffx_assay.py, J-099): host detector, parasite detector (positive, negative, dead-host
    and fragment deceptive, by-product, key specificity, selection-aware null) and the time-shift assay (designed arms
    race, graded control, change without resistance, reversed time labels)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
    import bffx_assay as A
    bad = [(n, d) for n, ok, d in A.controls() if not ok]
    assert not bad, bad
