"""Per-frame measurements. All are standard, simple estimators:

* density / activity            - fraction of non-vacuum / changed cells
* block entropy                 - Shannon entropy of 2x2 binary blocks (bits per cell)
* compression ratio vs. surrogate - zlib size of the frame divided by the zlib size
  of a random shuffle of the same cells (same state histogram, no structure).
  ~1.0 means "as incompressible as noise", well below 1 means spatial order.
"""
from __future__ import annotations

import zlib

import numpy as np


def density(state: np.ndarray) -> float:
    return float(np.count_nonzero(state)) / state.size


def activity(prev: np.ndarray, cur: np.ndarray) -> float:
    return float(np.count_nonzero(prev != cur)) / cur.size


def block_entropy(state: np.ndarray) -> float:
    """Entropy of 2x2 (wrap-around) blocks of the occupied mask, normalised to [0, 1]."""
    a = (state > 0).astype(np.uint8)
    right = np.roll(a, -1, axis=1)
    down = np.roll(a, -1, axis=0)
    diag = np.roll(down, -1, axis=1)
    codes = a | (right << 1) | (down << 2) | (diag << 3)
    p = np.bincount(codes.ravel(), minlength=16) / codes.size
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum() / 4.0)


def compressed_size(data: np.ndarray) -> int:
    return len(zlib.compress(np.ascontiguousarray(data, dtype=np.uint8).tobytes(), 6))


def compression_ratio(data: np.ndarray, rng: np.random.Generator) -> float:
    """Compressed size relative to a shuffled surrogate with identical cell statistics."""
    flat = np.ascontiguousarray(data, dtype=np.uint8).ravel()
    if flat.min() == flat.max():
        return 0.0  # perfectly uniform: maximally ordered (and trivially so)
    shuffled = rng.permutation(flat)
    return compressed_size(flat) / max(compressed_size(shuffled), 1)


def pairwise_difference_baseline(state: np.ndarray, num_states: int) -> float:
    """Probability that two independently drawn cells differ (used to normalise damage)."""
    p = np.bincount(state.ravel(), minlength=num_states) / state.size
    return float(1.0 - (p * p).sum())


def local_periodicity(stack: np.ndarray, max_period: int = 32) -> dict[str, float]:
    """Per-cell periodicity over a (T, H, W) window.

    A cell is *locally periodic* if its own time series repeats with some
    period p <= max_period throughout the window. Returned fraction is over
    cells that changed at all, so empty space doesn't count as "periodic".
    """
    T = stack.shape[0]
    active = (stack != stack[0]).any(axis=0)
    n_active = int(active.sum())
    if n_active == 0:
        return {"active_cell_frac": 0.0, "local_periodic_frac": 1.0}
    periodic = np.zeros(stack.shape[1:], dtype=bool)
    for p in range(1, min(max_period, T // 3) + 1):
        periodic |= (stack[p:] == stack[:-p]).all(axis=0)
    return {"active_cell_frac": n_active / active.size,
            "local_periodic_frac": float((periodic & active).sum()) / n_active}
