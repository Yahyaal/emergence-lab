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


# ---- contests between unrelated replicators (E-44, D-043) -------------------------------------
# Two replicators a and b from different families (< 90% identical to each other) are seeded together,
# 8 copies each, among 1024 random programs, 96 epochs; n_a, n_b = programs >= 90% identical to a, b.
# s = ln((n_b + 1)/(n_a + 1)) per replicate; informative if n_a + n_b >= 16. With REPS_F = 16
# replicates, "b favoured" / "a favoured" if >= 8 replicates are informative, a two-sided sign test on
# them gives p < 0.01 and the mean |s| > ln 2. Drift from equal starts gives each sign ~1/2.

REPS_F, MIN_INF_F, P_SIGN = 16, 8, 0.01
INERT = np.array([v for v in range(1, 256) if chr(v) not in "<>{}+-.,[]"], np.uint8)


def sign_p(k: int, n: int) -> float:
    """Two-sided binomial sign test, P(|X - n/2| >= |k - n/2|) for X ~ Bin(n, 1/2)."""
    from math import comb
    if n == 0:
        return 1.0
    d = abs(k - n / 2)
    return float(min(1.0, sum(comb(n, i) for i in range(n + 1) if abs(i - n / 2) >= d - 1e-9) / 2 ** n))


def compete_families(a: np.ndarray, b: np.ndarray, rng: np.random.Generator, mode: str = "bff",
                     reps: int = REPS_F) -> dict:
    a, b = np.asarray(a, np.uint8), np.asarray(b, np.uint8)
    if RP.similar(a[None], b)[0]:
        raise ValueError("a and b are >= 90% identical: use compete() with a marker byte")
    s, counts = [], []
    for _ in range(reps):
        progs = rng.integers(0, 256, (RP.N, len(a)), dtype=np.uint8)
        idx = rng.permutation(RP.N)[:2 * RP.K]
        progs[idx[:RP.K]] = a
        progs[idx[RP.K:]] = b
        soup = B.Soup(n=RP.N, length=len(a), mutation=0.0, mode=mode, seed=int(rng.integers(2 ** 31)), programs=progs)
        for _ in range(RP.EPOCHS):
            soup.epoch()
        na, nb = int(RP.similar(soup.programs, a).sum()), int(RP.similar(soup.programs, b).sum())
        counts.append([na, nb])
        s.append(float(np.log((nb + 1) / (na + 1))))
    inf = [v for v, (na, nb) in zip(s, counts) if na + nb >= MIN_FAMILY]
    mean = float(np.mean(inf)) if inf else 0.0
    k = sum(v > 0 for v in inf)
    n = sum(v != 0 for v in inf)
    p = sign_p(k, n)
    if len(inf) < MIN_INF_F:
        verdict = "undecided"
    elif p < P_SIGN and mean > S_MIN:
        verdict = "b favoured"
    elif p < P_SIGN and mean < -S_MIN:
        verdict = "a favoured"
    else:
        verdict = "no difference"
    return {"verdict": verdict, "mean_s": round(mean, 3), "informative": len(inf), "b_wins": int(k), "sign_n": int(n),
            "p": round(p, 5), "s": [round(v, 3) for v in s], "counts": counts}


def compete_marked(x: np.ndarray, m: np.ndarray, pos: int, rng: np.random.Generator, mode: str = "bff",
                   reps: int = REPS_F) -> dict:
    """compete() scored with the compete_families criterion (null for E-44 on emergent material)."""
    r = compete(x, m, pos, rng, mode=mode, reps=reps)
    inf = [v for v, (nx, nm) in zip(r["s"], r["counts"]) if nx + nm >= MIN_FAMILY]
    k, n = sum(v > 0 for v in inf), sum(v != 0 for v in inf)
    p = sign_p(k, n)
    mean = r["mean_s"]
    if len(inf) < MIN_INF_F:
        v = "undecided"
    elif p < P_SIGN and abs(mean) > S_MIN:
        v = "b favoured" if mean > 0 else "a favoured"
    else:
        v = "no difference"
    return r | {"verdict": v, "b_wins": int(k), "sign_n": int(n), "p": round(p, 5)}


def retail(x: np.ndarray, rng: np.random.Generator, start: int = 27) -> np.ndarray:
    """The hand-written replicator with its inert tail redrawn from non-instruction, non-zero bytes:
    the same copier, but < 90% identical to the original (a separate family)."""
    y = np.asarray(x, np.uint8).copy()
    y[start:] = rng.choice(INERT, len(y) - start)
    return y
