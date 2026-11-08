"""Heredity test for program replicators (BFF soups), J-042, D-041.

Question: when a replicator carries a mutation, do its copies carry the mutation too? That is
heritable variation (evidence level 4), as opposed to copies that revert to a fixed form (an
attractor, like Gray-Scott spots, J-037) or a rule that copies everything (copyall).

For a candidate replicator x (bytes), MUTANTS single-byte mutants are drawn (random position,
random new value). Each mutant m is seeded as K copies among N random programs and run EPOCHS
epochs without background mutation (the replicators.growth set-up). Its copies are the programs
>= 90% identical to x (the family). Measured per mutant:

* viable: the family grows to >= MIN_COPIES (as replicators.growth, generation 1);
* f_mut: fraction of the family carrying m's byte at the mutated position;
* f_base: the same fraction when the unmutated x is seeded instead (baseline: how often that
  byte appears there without the mutation: copying errors, partner bytes, convergence).

A mutant is "inherited" if f_mut >= 0.5 and f_base <= 0.1. Verdict:
* "rule-level duplication" or "no replication": x itself fails replicators.replication_test;
* "no variation": fewer than MIN_VIABLE viable mutants (every mutation kills replication);
* "heredity": >= half of the viable mutants are inherited and f_mut > f_base in significantly
  more viable mutants than not (one-sided sign test, p < 0.01);
* "no heredity": otherwise (copies revert or the mutation is lost).

Selection: only viable mutants are scored, and the baseline is taken from the same kind of
run, so viability cannot by itself produce a "heredity" verdict.
"""
from __future__ import annotations

from math import comb

import numpy as np

from . import replicators as RP
from ..programs import bff as B

MUTANTS, MIN_VIABLE, INHERIT, BASE_MAX = 16, 6, 0.5, 0.1


def _family_run(seed_prog: np.ndarray, ref: np.ndarray, rng: np.random.Generator, mode: str) -> np.ndarray:
    progs = rng.integers(0, 256, (RP.N, len(ref)), dtype=np.uint8)
    progs[:RP.K] = seed_prog
    soup = B.Soup(n=RP.N, length=len(ref), mutation=0.0, mode=mode, seed=int(rng.integers(2 ** 31)), programs=progs)
    for _ in range(RP.EPOCHS):
        soup.epoch()
    return soup.programs[RP.similar(soup.programs, ref)]


def sign_p(k: int, n: int) -> float:
    """One-sided sign test: P(X >= k), X ~ Binomial(n, 1/2)."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def heredity_test(x: np.ndarray, rng: np.random.Generator, mode: str = "bff", mutants: int = MUTANTS,
                  check_replicator: bool = False) -> dict:
    x = np.asarray(x, dtype=np.uint8)
    out: dict = {}
    if check_replicator:
        rt = RP.replication_test(x, rng, mode=mode)
        out["replication_verdict"] = rt["verdict"]
        if rt["verdict"] != "replicator":
            return out | {"verdict": rt["verdict"] if rt["verdict"] == "rule-level duplication" else "no replication"}
    rows = []
    for _ in range(mutants):
        pos = int(rng.integers(len(x)))
        val = int((int(x[pos]) + rng.integers(1, 256)) % 256)
        m = x.copy()
        m[pos] = val
        fam_m = _family_run(m, x, rng, mode)
        fam_x = _family_run(x, x, rng, mode)
        viable = len(fam_m) >= RP.MIN_COPIES
        f_mut = float((fam_m[:, pos] == val).mean()) if len(fam_m) else 0.0
        f_base = float((fam_x[:, pos] == val).mean()) if len(fam_x) else 0.0
        rows.append({"pos": pos, "val": val, "copies": int(len(fam_m)), "viable": bool(viable),
                     "f_mut": round(f_mut, 3), "f_base": round(f_base, 3),
                     "inherited": bool(viable and f_mut >= INHERIT and f_base <= BASE_MAX)})
    v = [r for r in rows if r["viable"]]
    k = sum(r["f_mut"] > r["f_base"] for r in v)
    n = sum(r["f_mut"] != r["f_base"] for r in v)
    p = sign_p(k, n)
    inh = sum(r["inherited"] for r in v)
    out |= {"mutants": rows, "viable": len(v), "inherited": inh, "sign_k": k, "sign_n": n, "p": round(p, 5)}
    if len(v) < MIN_VIABLE:
        return out | {"verdict": "no variation"}
    return out | {"verdict": "heredity" if inh >= len(v) / 2 and p < 0.01 else "no heredity"}
