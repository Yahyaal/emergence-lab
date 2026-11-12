"""Language-agnostic replicator test by inheritance (E-75 phase 0, D-055 proposed).

The whole-program copy tests (D-050, D-053) ask that a program copy all of itself onto its partner and stay
intact. In the SUBLEQ family the first emergent replicator does neither. It is a 5-byte loop that copies itself
into the partner while overwriting most of its own body with partner bytes. What it passes on is the loop.

`inherits(P, run, rng)`: a program is a replicator if some block of it is **inherited**:
  lineage   P runs with a random partner; the partner half runs with a fresh random partner; and so on for
            `gens` generations. A block of P (m contiguous bytes) must be present, anywhere, in the final
            partner half of at least `need` of `lineages` independent lineages;
  knockout  the same block is replaced by random bytes in P, and the lineages are run again; the original block
            must then be absent in all but at most `lineages - need` of them. A block that the program's code
            writes from scratch (a run of zeros or of one filler value, as in a filler smear) is not inherited.
`run(tape) -> tape` is the language's interpreter for a pair (2L bytes, program first).
"""
from __future__ import annotations

import numpy as np


def _lineage(X: np.ndarray, run, rng, gens: int) -> bytes:
    L = len(X)
    for _ in range(gens):
        t = run(np.concatenate([X, rng.integers(0, 256, L, dtype=np.uint8)]))
        X = t[L:]
    return bytes(X)


def inherits(P: np.ndarray, run, rng, gens: int = 5, lineages: int = 4, need: int = 3, m: int = 4,
             max_candidates: int = 6) -> tuple[bool, int | None]:
    """(replicator?, start of the inherited block or None)."""
    P = np.asarray(P, dtype=np.uint8)
    Pb, L = bytes(P), len(P)
    ends = [_lineage(P, run, rng, gens) for _ in range(lineages)]
    cands = [i for i in range(L - m + 1) if sum(Pb[i:i + m] in e for e in ends) >= need]
    # try candidates spread over the program (overlapping windows are near-duplicates)
    picked, last = [], -m
    for i in cands:
        if i >= last + m:
            picked.append(i)
            last = i
    for i in picked[:max_candidates]:
        blk = Pb[i:i + m]
        K = P.copy()
        K[i:i + m] = rng.integers(0, 256, m, dtype=np.uint8)
        de_novo = sum(blk in _lineage(K, run, rng, gens) for _ in range(lineages))
        if de_novo <= lineages - need:
            return True, i
    return False, None


def count(X: np.ndarray, run, seed: int, **kw) -> int:
    rng = np.random.default_rng(seed)
    return sum(inherits(P, run, rng, **kw)[0] for P in X)
