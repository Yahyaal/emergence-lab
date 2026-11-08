"""Selection among program replicator variants (BFF soups): competition assay, J-043, D-042.

Heritable variation (D-041, E-42) is two of the three conditions for natural selection; the third
is that variants differ in how well they spread. Here a parent replicator x and a variant m
(differing at one byte position `pos`) are seeded together, 8 copies each, among 1024 random
programs, and run 96 epochs without background mutation (the replicators.growth set-up). Among the
family (>= 90% identical to x), n_m programs carry m's byte at pos and n_x carry x's byte. Per
replicate run, s = ln((n_m + 1) / (n_x + 1)); REPS replicate runs with independent random soups.

Verdict per pair: "variant favoured" if s > 0 in every replicate and the mean s > ln 2 (the
variant ends at least twice as common); "parent favoured" symmetrically; otherwise "no
difference". Starting counts are equal, so drift alone gives each sign with probability about
1/2 per replicate; all REPS = 6 the same sign by drift alone has probability 2/64 (and the mean
must also exceed ln 2).

Controls (benchmark section 12): a neutral pair (the hand-written replicator and a mutant in its
inert tail) -> no difference; the hand-written replicator against a mutant that cannot copy
(a broken loop) -> parent favoured; the same neutral pair under the copyall rule (every program
copied blindly, so the family never grows) -> undecided, never a "favoured" verdict.
"""
from __future__ import annotations

import numpy as np

from . import replicators as RP
from ..programs import bff as B

REPS, S_MIN, MIN_FAMILY, MIN_INFORMATIVE = 8, float(np.log(2)), 16, 4


def compete(x: np.ndarray, m: np.ndarray, pos: int, rng: np.random.Generator, mode: str = "bff",
            reps: int = REPS) -> dict:
    x, m = np.asarray(x, np.uint8), np.asarray(m, np.uint8)
    s, counts = [], []
    for _ in range(reps):
        progs = rng.integers(0, 256, (RP.N, len(x)), dtype=np.uint8)
        idx = rng.permutation(RP.N)[:2 * RP.K]
        progs[idx[:RP.K]] = x
        progs[idx[RP.K:]] = m
        soup = B.Soup(n=RP.N, length=len(x), mutation=0.0, mode=mode, seed=int(rng.integers(2 ** 31)), programs=progs)
        for _ in range(RP.EPOCHS):
            soup.epoch()
        fam = soup.programs[RP.similar(soup.programs, x)]
        nm, nx = int((fam[:, pos] == m[pos]).sum()), int((fam[:, pos] == x[pos]).sum())
        counts.append([nx, nm])
        s.append(float(np.log((nm + 1) / (nx + 1))))
    inf = [v for v, (nx, nm) in zip(s, counts) if nx + nm >= MIN_FAMILY]
    mean = float(np.mean(inf)) if inf else 0.0
    if len(inf) < MIN_INFORMATIVE:
        verdict = "undecided"
    elif all(v > 0 for v in inf) and mean > S_MIN:
        verdict = "variant favoured"
    elif all(v < 0 for v in inf) and mean < -S_MIN:
        verdict = "parent favoured"
    else:
        verdict = "no difference"
    return {"verdict": verdict, "mean_s": round(mean, 3), "informative": len(inf), "s": [round(v, 3) for v in s],
            "counts": counts}


def mutant(x: np.ndarray, pos: int, val: int) -> np.ndarray:
    m = np.asarray(x, np.uint8).copy()
    m[pos] = val
    return m
