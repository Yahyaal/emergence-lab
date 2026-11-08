"""Probe checks for program soups (BFF, emergence/programs) and the replicator detector
(observatory/replicators.py, J-040, D-040). Called from benchmark_probes.run_probe_benchmark.

* interpreter      the C interpreter equals the pure-Python reference on random tapes
* positive         a hand-written self-replicator -> replicator (two generations)
* negative         random programs -> no replication
* deceptive        an inert program that is common (all zeros) -> no replication;
                   neutral copying (rule "copyall": every pair's first program overwrites the
                   second, so counts drift) -> no replication; the replicator in a soup where
                   nothing runs ("noexec") -> no replication
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
