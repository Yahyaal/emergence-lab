"""Parasite detector for program soups (BFF), J-068, D-048.

Question: in soups after the transition, ~20% of the most common programs fail the replicator test
(replicators.replication_test: alone among random programs they make no copies). Are they kept
common because other programs (the replicators) copy them? Such a program is a parasite in the
sense of Tierra and of Aguera y Arcas et al. (2024): it is copied, but it does not copy itself.

The test is an intervention on copies, never on the soup being observed. For a candidate x and a
partner pool P (the soup snapshot it came from):

* alone: x does not copy itself: `alone_test`, the replicator test repeated 10 times, never sees
  generation 1 grow (any growth gives "self-copier"). Callers may pass a verdict computed earlier.
* template rate q: x is paired with M partners drawn from P (programs like x excluded), once in each
  order. A copy is made when the partner's slot ends up like x (>= 90% of bytes equal to x, or to its
  reverse: emergent replicators write mirror copies, E-45). q = copies / 2M.
* specificity: the same for S byte-scrambled versions of x (same bytes, other order). Scrambles keep
  the composition, so a pool that copies whatever runs first (a "permissive" host, or the copyall
  rule) copies them too. One-sided Fisher test of x's copies against the pooled scramble copies.
* self-copy check (added after E-66, J-068): x runs first against M "halting" partners (an unmatched
  ']' then inert bytes, so the partner's code never runs; `program_fitness.background`). If x still
  copies itself into them at rate >= Q_MIN, x is a copier, not a parasite: it fails the alone test only
  because random partners destroy it when it runs second ("context self-copier"). E-66 found two such
  programs that the first version called parasites.
* de novo production b: random pairs drawn from P without x-like programs; b = x-like outputs per
  pair. A by-product is made from other templates; a parasite mostly from its own.
* templated share F = c q / (c q + (n / 2) b), with c the number of x-like programs in P and n = |P|:
  of the x-like programs made per epoch (mean field), the share copied from an existing x.

Verdicts, in this order: "self-copier" (alone test not "no replication"), "not copied" (q < Q_MIN),
"unspecific copying" (not specific), "context self-copier" (self-copy rate >= Q_MIN), "by-product"
(F < F_MIN), "parasite".

Also reported: the hosts, i.e. which partners made the copies (indices into P), so callers can ask
whether they are verified replicators.

Controls (benchmark section 14): positive `hand_parasite()` at 5% of a pool of hand-written
replicators (50%) and random programs: an inert program whose bytes 1-2 are the replicator's counter
cells; when it runs first, the instruction pointer runs on into the replicator, which then copies its
partner over itself. Negatives: an inert program and a random program in the same kind of pool; deceptive (a) the copyall rule (every first program is copied:
unspecific), (b) `byproduct_pool()` (inert "makers" that share the parasite's first 25 bytes and have
random tails: the host turns each into the same product Z, so Z is copied but mostly made de novo);
(c) `CONTEXT_COPIER` among random programs
(copies itself, fails the growth test: context self-copier); selection-aware null: the most common programs of an early BFF soup (no replicators) tested the same
way give no parasite.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import fisher_exact

from . import replicators as RP
from ..programs import bff as B

SIM = 0.9
M, M_PROD, SCRAMBLES = 256, 2048, 4
Q_MIN, ALPHA, F_MIN = 0.02, 0.01, 0.5
INERT_BYTE = 0x80


def like(programs: np.ndarray, x: np.ndarray) -> np.ndarray:
    programs = np.atleast_2d(programs)
    return ((programs == x[None, :]).mean(1) >= SIM) | ((programs == x[::-1][None, :]).mean(1) >= SIM)


def pair(a: np.ndarray, b: np.ndarray, mode: str = "bff", max_steps: int = 8192) -> tuple[np.ndarray, np.ndarray]:
    if mode == "bff":
        return B.interact(a, b, max_steps)
    if mode == "copyall":
        return a.copy(), a.copy()
    if mode == "noexec":
        return a.copy(), b.copy()
    raise ValueError(mode)


def template_rate(x: np.ndarray, pool: np.ndarray, rng: np.random.Generator, m: int = M, mode: str = "bff") -> dict:
    """x paired with m partners from pool (x-like excluded), each in both orders."""
    idx = np.flatnonzero(~like(pool, x))
    if len(idx) == 0:
        return {"copies": 0, "trials": 0, "q": 0.0, "survival": None, "hosts": []}
    pick = rng.choice(idx, m, replace=len(idx) < m)
    copies, alive, hosts = 0, 0, []
    for j in pick:
        p = pool[j]
        a, b = pair(x, p, mode)           # x first
        c1 = bool(like(b, x)[0])
        a2, b2 = pair(p, x, mode)         # x second
        c2 = bool(like(a2, x)[0])
        copies += c1 + c2
        alive += bool(like(a, x)[0]) + bool(like(b2, x)[0])
        if c1 or c2:
            hosts.append(int(j))
    return {"copies": copies, "trials": 2 * m, "q": copies / (2 * m), "survival": alive / (2 * m), "hosts": hosts}


def production_rate(x: np.ndarray, pool: np.ndarray, rng: np.random.Generator, m: int = M_PROD,
                    mode: str = "bff") -> dict:
    """Random pairs from pool without x-like programs; x-like outputs per pair."""
    idx = np.flatnonzero(~like(pool, x))
    if len(idx) < 2:
        return {"made": 0, "pairs": 0, "b": 0.0}
    made = 0
    for _ in range(m):
        i, j = rng.choice(idx, 2, replace=False)
        a, b = pair(pool[i], pool[j], mode)
        made += int(like(np.stack([a, b]), x).sum())
    return {"made": made, "pairs": m, "b": made / m}


def parasite_test(x: np.ndarray, pool: np.ndarray, rng: np.random.Generator, mode: str = "bff",
                  alone: str | None = None, m: int = M, m_prod: int = M_PROD, scrambles: int = SCRAMBLES) -> dict:
    x = np.asarray(x, np.uint8)
    pool = np.asarray(pool, np.uint8)
    if alone is None:
        alone = alone_test(x, rng, mode=mode)["verdict"]
    t = template_rate(x, pool, rng, m, mode)
    sc, st = 0, 0
    for _ in range(scrambles):
        r = template_rate(rng.permutation(x), pool, rng, m, mode)
        sc, st = sc + r["copies"], st + r["trials"]
    p = float(fisher_exact([[t["copies"], t["trials"] - t["copies"]], [sc, st - sc]], alternative="greater")[1]) \
        if t["trials"] else 1.0
    from .program_fitness import background
    halt = background(rng, m, len(x), "halting")
    self_copies = sum(bool(like(pair(x, h, mode)[1], x)[0]) for h in halt)
    pr = production_rate(x, pool, rng, m_prod, mode)
    c, n = int(like(pool, x).sum()), len(pool)
    made_t, made_d = c * t["q"], n / 2 * pr["b"]
    F = made_t / (made_t + made_d) if made_t + made_d > 0 else 0.0
    if alone != "no replication":
        verdict = "self-copier"
    elif t["q"] < Q_MIN:
        verdict = "not copied"
    elif p >= ALPHA:
        verdict = "unspecific copying"
    elif self_copies / m >= Q_MIN:
        verdict = "context self-copier"
    elif F < F_MIN:
        verdict = "by-product"
    else:
        verdict = "parasite"
    return {"verdict": verdict, "alone": alone, "q": round(t["q"], 4), "copies": t["copies"], "trials": t["trials"],
            "survival": None if t["survival"] is None else round(t["survival"], 4),
            "q_scrambled": round(sc / st, 4) if st else 0.0, "p": p, "self_rate": round(self_copies / m, 4), "b": round(pr["b"], 5), "count": c,
            "templated_share": round(F, 4), "hosts": t["hosts"]}


def alone_test(x: np.ndarray, rng: np.random.Generator, repeats: int = 10, mode: str = "bff") -> dict:
    """The replicator test repeated with independent seeds (E-66: one test from K = 8 copies often loses
    every copy by chance, so a single "no replication" does not mean the program cannot copy itself).
    Verdict "no replication" only if generation 1 never grew in `repeats` tests. Valid only where random
    programs cannot drift to 8x their start: under the copyall rule some repeats pass by drift alone."""
    vs, g1 = [], 0
    for _ in range(repeats):
        r = RP.replication_test(np.asarray(x, np.uint8), np.random.default_rng(int(rng.integers(2 ** 63))), mode=mode)
        vs.append(r["verdict"])
        g1 += bool(r["gen1"]["ok"])
    return {"verdict": "no replication" if g1 == 0 else max(set(vs) - {"no replication"}, key=vs.count),
            "gen1_ok": g1, "repeats": repeats, "verdicts": vs}


# --- controls ---------------------------------------------------------------------------------

# A program from soup 5401 at round 16,250 (E-66): it copies itself into any partner when it runs first,
# but is destroyed whenever it runs second, so alone among random programs its copies never grow (0 of
# 10 replicator tests). The first version of this detector called it a parasite (deceptive control).
CONTEXT_COPIER = bytes.fromhex(
    "000038383800383 8b92c2222b7d4000c0c5394314 6c100003c5b2c3c7d1eb3646d0f50e95d7d3c2c5b0fa25a3c2c04e349ee55bc14b900872ce7000000000000"
    .replace(" ", ""))

def hand_parasite() -> np.ndarray:
    """Inert program with the hand-written replicator's counter cells (64, 1) at bytes 1-2. Run first
    against the replicator, nothing executes in its half; the instruction pointer enters the
    replicator with both heads at 0, so the replicator reads 64 from the parasite's byte 1, moves its
    write head to 64 and copies the parasite over itself (until its own loop is overwritten)."""
    from .program_fitness import INERT
    x = np.full(64, INERT_BYTE, np.uint8)
    x[1], x[2] = 64, 1
    x[3:25] = np.random.default_rng(0).choice(INERT, 22)  # not all one byte: the host's debris is
    return x                                               # mostly 0x80 (~60/64 like an all-0x80 program)


def inert() -> np.ndarray:
    return np.full(64, INERT_BYTE, np.uint8)


def host_pool(rng: np.random.Generator, n: int = 1024, hosts: float = 0.5, guest: np.ndarray | None = None,
              guest_share: float = 0.05) -> np.ndarray:
    """Hand-written replicators (share `hosts`) among random programs, plus `guest` at `guest_share`."""
    P = rng.integers(0, 256, (n, 64), dtype=np.uint8)
    P[: int(n * hosts)] = B.REPLICATOR
    if guest is not None:
        P[int(n * hosts): int(n * hosts) + int(n * guest_share)] = guest
    return P[rng.permutation(n)]


def byproduct_pool(rng: np.random.Generator, n: int = 1024) -> tuple[np.ndarray, np.ndarray]:
    """Deceptive by-product: 40% hand-written replicators, 40% 'makers', 2% product Z, rest random.
    A maker is inert, shares Z's first 25 bytes and has a random inert tail (each maker unique, < 90%
    like Z). When a maker runs first, the replicator copies about its first 25 bytes over itself and
    keeps its own inert tail: the product is Z. Z is copied the same way (so it is copied, and
    specifically), but most Z are made from makers. Returns (pool, Z)."""
    from .program_fitness import INERT
    z = hand_parasite()
    z[3:25] = rng.choice(INERT, 22)  # a different filler from the hand parasite
    P = rng.integers(0, 256, (n, 64), dtype=np.uint8)
    nh, nm, nz = int(0.4 * n), int(0.4 * n), int(0.02 * n)
    P[:nh] = B.REPLICATOR
    for i in range(nh, nh + nm):
        P[i, :25] = z[:25]
        P[i, 25:] = rng.choice(INERT, 39)
    P[nh + nm: nh + nm + nz] = z
    return P[rng.permutation(n)], z
