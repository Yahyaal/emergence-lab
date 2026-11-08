"""Probe checks for program soups (BFF, emergence/programs) and the replicator detector
(observatory/replicators.py, J-040, D-040). Called from benchmark_probes.run_probe_benchmark.

* interpreter      the C interpreter equals the pure-Python reference on random tapes
* positive         a hand-written self-replicator -> replicator (two generations)
* negative         random programs -> no replication
* deceptive        an inert program that is common (all zeros) -> no replication;
                   neutral copying (rule "copyall": every pair's first program overwrites the
                   second, so counts drift) -> no replication; the replicator in a soup where
                   nothing runs ("noexec") -> no replication
* growth-rate assay (program_fitness, D-044): trap ladder vs theory, k=3 vs 4 sensitivity,
                   non-copier, copyall/noexec deceptive, repeat-assay null
* selection-aware null  `replicators.scan` (most common programs) on a noexec soup after 300
                   epochs and on a BFF soup at epoch 50 (before any transition): 0 replicators
"""
from __future__ import annotations

import numpy as np


def run(check) -> None:
    from .observatory import replicators as RP
    from .programs import bff as B

    rng = np.random.default_rng(0)
    bad = 0
    for _ in range(300):
        t = rng.integers(0, 256, 128, dtype=np.uint8)
        m = rng.random(128) < 0.4
        t[m] = rng.choice(np.frombuffer(b"<>{}-+.,[]", np.uint8), m.sum())
        a, sa = B.run(t, 2000)
        b, sb = B.run_py(t, 2000)
        bad += bool(sa != sb or (a != b).any())
    check("programs: C interpreter equals the Python reference (300 random tapes)", bad == 0, f"{bad} mismatches")

    def brief(r):
        return (f"{r['verdict']}; gen1 {r['gen1']['start']} -> {r['gen1']['late']}, gen2 {(r.get('gen2') or {}).get('late')}, "
                f"pair copy rate {r.get('pair_copy_rate')}")

    rnd = rng.integers(0, 256, 64, dtype=np.uint8)
    for name, x, mode, want in (
            ("replicators positive: hand-written self-replicator -> replicator", B.REPLICATOR, "bff", "replicator"),
            ("replicators negative: random program", rnd, "bff", "no replication"),
            ("replicators deceptive: common but inert (all zeros)", np.zeros(64, np.uint8), "bff", "no replication"),
            ("replicators deceptive: neutral copying rule (copyall) drifts", B.REPLICATOR, "copyall", "no replication"),
            ("replicators deceptive: replicator where nothing runs (noexec)", B.REPLICATOR, "noexec", "no replication")):
        r = RP.replication_test(x, np.random.default_rng(1), mode=mode)
        check(name, r["verdict"] == want, brief(r))

    found = []
    for mode, epochs in (("noexec", 300), ("bff", 50)):
        s = B.Soup(n=2048, mode=mode, seed=7)
        for _ in range(epochs):
            s.epoch()
        found.append(RP.scan(s.programs, np.random.default_rng(2), max_candidates=3, mode=mode)["replicators"])
    check("replicators selection-aware null: scans of a noexec soup and an early BFF soup", sum(found) == 0,
          f"replicators found {found}")

    # heredity of program replicators (observatory/program_heredity.py, J-042, D-041)
    from .observatory import program_heredity as PH

    def hbrief(r):
        return f"{r['verdict']}; viable {r.get('viable')}, inherited {r.get('inherited')}, sign p {r.get('p')}"

    for name, x, mode, want in (
            ("program heredity positive: hand-written replicator, mutations in its copied tail -> heredity",
             B.REPLICATOR, "bff", "heredity"),
            ("program heredity negative: the replicator where nothing runs (noexec) -> no variation",
             B.REPLICATOR, "noexec", "no variation"),
            ("program heredity deceptive: the rule copies everything (copyall) -> no variation",
             B.REPLICATOR, "copyall", "no variation"),
            ("program heredity selection-aware null: a random program, scored only on viable mutants -> no variation",
             np.random.default_rng(5).integers(0, 256, 64, dtype=np.uint8), "bff", "no variation")):
        r = PH.heredity_test(x, np.random.default_rng(3), mode=mode)
        check(name, r["verdict"] == want, hbrief(r))

    # selection among replicator variants (observatory/program_selection.py, J-043, D-042)
    from .observatory import program_selection as PS
    x = B.REPLICATOR
    for name, m, pos, mode, ok in (
            ("program selection negative: neutral variant (inert tail byte) -> no difference",
             PS.mutant(x, 40, 7), 40, "bff", lambda v: v == "no difference"),
            ("program selection positive: variant that cannot copy (broken loop) -> parent favoured",
             PS.mutant(x, 3, 0x80), 3, "bff", lambda v: v == "parent favoured"),
            ("program selection deceptive: neutral pair under the copyall rule -> not a favoured verdict",
             PS.mutant(x, 40, 7), 40, "copyall", lambda v: v in ("undecided", "no difference"))):
        r = PS.compete(x, m, pos, np.random.default_rng(2), mode=mode)
        check(name, ok(r["verdict"]), f"{r['verdict']}; mean s {r['mean_s']}, informative {r['informative']}")

    # contests between unrelated replicator families (program_selection.compete_families, E-44, D-043)
    y = PS.retail(x, np.random.default_rng(1))
    yb = PS.mutant(y, 3, 0x80)
    for name, b, mode, ok in (
            ("family contest negative: hand-written replicator vs the same copier with a redrawn inert tail -> no difference",
             y, "bff", lambda v: v == "no difference"),
            ("family contest positive: vs a redrawn-tail copy with a broken loop -> a favoured",
             yb, "bff", lambda v: v == "a favoured"),
            ("family contest deceptive: neutral families under the copyall rule -> not a favoured verdict",
             y, "copyall", lambda v: v in ("undecided", "no difference"))):
        r = PS.compete_families(x, b, np.random.default_rng(2), mode=mode)
        check(name, ok(r["verdict"]), f"{r['verdict']}; mean s {r['mean_s']}, informative {r['informative']}, "
              f"b wins {r['b_wins']}/{r['sign_n']}, p {r['p']}")

    # growth-rate fitness assay (observatory/program_fitness.py, J-050, D-044)
    from .observatory import program_fitness as F
    frng = np.random.default_rng(13)
    ladder = [F.growth_rate(F.trapped(k), frng, bg="halting", reps=8) for k in range(5)]
    dev = [abs(g["r"] - F.theory(F.trap_p(k))) for k, g in enumerate(ladder)]
    rs = [g["r"] for g in ladder]
    check("program fitness positive/known effects: trap ladder p = 1 .. 1/16 in the halting background, r within 0.03 of ln(1 + p/2) and decreasing",
          max(dev) <= 0.03 and all(a > b for a, b in zip(rs, rs[1:])),
          "r " + ", ".join(f"{g['r']:.3f}/{F.theory(F.trap_p(k)):.3f}" for k, g in enumerate(ladder)))
    c34 = F.compare(ladder[3], ladder[4])
    check("program fitness sensitivity: trap k=3 vs k=4 (theory difference 0.031) separated at p < 0.01 with 8 replicates",
          c34["p"] < 0.01 and c34["d"] < 0, f"d {c34['d']}, p {c34['p']:.2g}")
    nc = [F.growth_rate(F.non_copier(), frng, bg=bg, reps=4)["r"] for bg in ("halting", "random")]
    check("program fitness negative: a non-copier has r < 0.01 (halting and random backgrounds)", max(nc) < 0.01,
          f"r {nc[0]:.4f}, {nc[1]:.4f}")
    dec = [F.growth_rate(frng.integers(0, 256, 64, dtype=np.uint8), frng, mode="copyall", reps=4)["r"],
           F.growth_rate(B.REPLICATOR, frng, mode="noexec", bg="halting", reps=4)["r"]]
    check("program fitness deceptive: random program under copyall (every program copied, counts only drift) and the replicator under noexec -> r < 0.02",
          max(dec) < 0.02, f"r {dec[0]:.4f}, {dec[1]:.4f}")
    ps = [F.compare(F.growth_rate(B.REPLICATOR, frng, reps=8), F.growth_rate(B.REPLICATOR, frng, reps=8))["p"]
          for _ in range(8)]
    check("program fitness null: 8 repeat assays of the same program (random background) -> at most 2 'different' at p < 0.05",
          sum(p < 0.05 for p in ps) <= 2, f"p {[round(p, 3) for p in ps]}")

    # invasion into a resident soup (program_fitness.invasion, E-52): calibration background of
    # hand-written copiers with inert tails, a share q of which end in an odd byte
    irng = np.random.default_rng(52)
    kw = dict(n=1024, k=32, reps=8)
    bg = F.resident_copiers(irng, 1024, 0.5)  # q = 0.25 gave effect -1.8 but p = 0.039 at this size (J-052)
    i0, i1 = F.invasion(F.trapped(0), bg, irng, **kw), F.invasion(F.trapped(1), bg, irng, **kw)
    ci = F.compare({"r": i0["s"], "rs": i0["ss"]}, {"r": i1["s"], "rs": i1["ss"]})
    check("program invasion known effect: trap variant copying with p = 0.5 among resident copiers scores > 1 below the neutral copier (p < 0.01)",
          i1["s"] - i0["s"] < -1.0 and ci["p"] < 0.01, f"s {i0['s']:.2f} vs {i1['s']:.2f}, p {ci['p']:.2g}")
    bg0 = F.resident_copiers(irng, 1024, 0.0)
    n0 = F.invasion(F.trapped(0), bg0, irng, **kw)
    n1 = F.invasion(F.trapped(1), bg0, irng, **kw)
    cn = F.compare({"r": n0["s"], "rs": n0["ss"]}, {"r": n1["s"], "rs": n1["ss"]})
    check("program invasion null: two neutral invaders (trap never fires, q = 0) -> not different at p < 0.05",
          cn["p"] >= 0.05, f"s {n0['s']:.2f} vs {n1['s']:.2f}, p {cn['p']:.2g}")
    nc = F.invasion(F.non_copier(), bg0, irng, **kw)
    check("program invasion negative: a non-copier among resident copiers is wiped out (s < -2)", nc["s"] < -2,
          f"s {nc['s']:.2f}")
    d0 = F.invasion(F.trapped(0), bg, irng, mode="copyall", **kw)
    d1 = F.invasion(F.trapped(1), bg, irng, mode="copyall", **kw)
    cd = F.compare({"r": d0["s"], "rs": d0["ss"]}, {"r": d1["s"], "rs": d1["ss"]})
    check("program invasion deceptive: the same q = 0.5 pair under copyall (code never runs, the trap cannot act) -> not different",
          cd["p"] >= 0.05, f"s {d0['s']:.2f} vs {d1['s']:.2f}, p {cd['p']:.2g}")
