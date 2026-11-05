"""Structure census: connected components tracked over a window of frames.

A *structure* is an 8-connected component of non-vacuum cells. Its *shape key*
is its exact cell pattern (states included) inside its bounding box, so the same
object seen at different places gets the same key.

From the census we derive:
* still structures - identical shape at the identical place for ~the whole window
* vocabulary       - distinct *persistent* shapes: seen at the same place at
                     t, t+p, t+2p (p <= 8: still lifes and oscillator phases),
                     or as a mover. Random blobs in a noisy soup rarely qualify.
* movers           - a shape seen at a, a+d, a+2d at times t, t+tau, t+2tau
                     (d != 0): a coherent object translating at constant velocity.
                     The three-point requirement keeps chance coincidences rare.

Limitation (documented, acceptable for an MVP): components crossing the torus
seam are split in two, so objects are lost briefly while they wrap.
"""
from __future__ import annotations

from collections import Counter, defaultdict

import numpy as np
from scipy import ndimage

_STRUCT = np.ones((3, 3), dtype=bool)
MAX_CELLS = 120   # bigger blobs are "background", not objects
MIN_CELLS = 3     # smaller than this is too generic to call an object
MAX_TAU = 8


def census(state: np.ndarray) -> dict[bytes, list[tuple[int, int]]]:
    """Map shape key -> list of bounding-box origins in this frame."""
    labels, n = ndimage.label(state > 0, structure=_STRUCT)
    out: dict[bytes, list[tuple[int, int]]] = defaultdict(list)
    if n == 0:
        return out
    sizes = np.bincount(labels.ravel())
    for i, sl in enumerate(ndimage.find_objects(labels), start=1):
        if sl is None or not (MIN_CELLS <= sizes[i] <= MAX_CELLS):
            continue
        sub = labels[sl] == i
        patch = np.where(sub, state[sl], 0).astype(np.uint8)
        key = bytes(patch.shape) + patch.tobytes()
        out[key].append((sl[0].start, sl[1].start))
    return out


def analyse(frames: list[np.ndarray]) -> dict[str, float]:
    W = len(frames)
    if W == 0:
        return {}
    cens = [census(f) for f in frames]
    possets = [{k: set(v) for k, v in c.items()} for c in cens]

    placed: Counter[tuple[bytes, tuple[int, int]]] = Counter()
    n_objects = 0
    for c in cens:
        for k, poss in c.items():
            n_objects += len(poss)
            for p in poss:
                placed[(k, p)] += 1

    still = [kp for kp, cnt in placed.items() if cnt >= 0.9 * W]
    persistent: set[bytes] = set()
    for t in range(W):
        for k, poss in cens[t].items():
            if k in persistent:
                continue
            for p in range(1, MAX_TAU + 1):
                if t + 2 * p >= W:
                    break
                a, b = possets[t + p].get(k), possets[t + 2 * p].get(k)
                if a and b and any(x in a and x in b for x in poss):
                    persistent.add(k)
                    break

    mover_shapes: set[bytes] = set()
    velocities: set[tuple[int, int]] = set()
    events = 0
    for t in range(W):
        for k, poss in cens[t].items():
            for tau in range(1, MAX_TAU + 1):
                if t + 2 * tau >= W:
                    break
                mid = possets[t + tau].get(k)
                if not mid:
                    continue
                far = possets[t + 2 * tau].get(k, ())
                hit = False
                for a in poss:
                    for b in mid:
                        dr, dc = b[0] - a[0], b[1] - a[1]
                        if (dr or dc) and max(abs(dr), abs(dc)) <= tau and (b[0] + dr, b[1] + dc) in far:
                            events += 1
                            mover_shapes.add(k)
                            g = np.gcd(np.gcd(abs(dr), abs(dc)), tau)
                            velocities.add((int(dr // g), int(dc // g), int(tau // g)))
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    break

    return {
        "objects_per_frame": n_objects / W,
        "still_structures": float(len(still)),
        "vocabulary": float(len(persistent | mover_shapes)),
        "mover_shapes": float(len(mover_shapes)),
        "mover_events": float(events),
        "mover_velocities": float(len(velocities)),
    }
