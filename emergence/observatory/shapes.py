"""Shape helpers shared by the innovation and replication probes."""
from __future__ import annotations

import numpy as np

from .structures import MAX_TAU, census


def patch_of(key: bytes) -> np.ndarray:
    return np.frombuffer(key[2:], dtype=np.uint8).reshape(key[0], key[1])


def canonical_patch(p: np.ndarray) -> bytes:
    """Orientation-free key: the same shape rotated or mirrored gets the same key."""
    variants = []
    for k in range(4):
        r = np.rot90(p, k)
        for q in (r, r[:, ::-1]):
            q = np.ascontiguousarray(q)
            variants.append(bytes(q.shape) + q.tobytes())
    return min(variants)


def canonical(key: bytes) -> bytes:
    return canonical_patch(patch_of(key))


def persistent_shapes(frames: list[np.ndarray]) -> set[bytes]:
    """Canonical keys of shapes that, within this short run of frames, either stay
    put at t, t+p, t+2p (still lifes, oscillators) or translate a, a+d, a+2d (movers)."""
    cens = [census(f) for f in frames]
    possets = [{k: set(v) for k, v in c.items()} for c in cens]
    out: set[bytes] = set()
    W = len(frames)
    for t in range(W):
        for k, poss in cens[t].items():
            for tau in range(1, MAX_TAU + 1):
                if t + 2 * tau >= W:
                    break
                mid, far = possets[t + tau].get(k), possets[t + 2 * tau].get(k)
                if not mid or not far:
                    continue
                if any(x in mid and x in far for x in poss) or any(
                        (y[0] != x[0] or y[1] != x[1]) and (2 * y[0] - x[0], 2 * y[1] - x[1]) in far
                        for x in poss for y in mid):
                    out.add(canonical(k))
                    break
    return out
