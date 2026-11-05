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
                     (d != 0): a *candidate* translating object. Shape matching
                     alone does not prove the sightings are one causal object, so:
* verified movers  - each candidate shape is copied alone into an empty, separate
                     world (an isolated clone, never the original universe) and
                     run for 2*tau steps. It is verified only if it reappears
                     displaced by 2d by itself, i.e. it is a self-propelled object
                     under this physics, not a coincidence or context effect.

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


def _patch_from_key(key: bytes) -> np.ndarray:
    h, w = key[0], key[1]
    return np.frombuffer(key[2:], dtype=np.uint8).reshape(h, w)


def verify_in_isolation(physics, key: bytes, d: tuple[int, int], tau: int) -> bool:
    """Run the shape alone in an empty world; does it travel by 2d in 2*tau steps?"""
    patch = _patch_from_key(key)
    ph, pw = patch.shape
    side = max(ph, pw) + 4 * tau + 12
    world = np.zeros((side, side), np.uint8)
    r0, c0 = side // 2 - ph // 2, side // 2 - pw // 2
    world[r0:r0 + ph, c0:c0 + pw] = patch
    for _ in range(2 * tau):
        world = physics.step(world)
    return (r0 + 2 * d[0], c0 + 2 * d[1]) in census(world).get(key, ())


def analyse(frames: list[np.ndarray], physics=None) -> dict[str, float]:
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
    examples: dict[bytes, tuple[tuple[int, int], int]] = {}
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
                            if k not in mover_shapes:
                                examples[k] = ((dr, dc), tau)
                            mover_shapes.add(k)
                            g = np.gcd(np.gcd(abs(dr), abs(dc)), tau)
                            velocities.add((int(dr // g), int(dc // g), int(tau // g)))
                            hit = True
                            break
                    if hit:
                        break
                if hit:
                    break

    verified = None
    if physics is not None:
        verified = sum(verify_in_isolation(physics, k, d, tau) for k, (d, tau) in examples.items())

    return {
        "verified_mover_shapes": None if verified is None else float(verified),
        "objects_per_frame": n_objects / W,
        "still_structures": float(len(still)),
        "vocabulary": float(len(persistent | mover_shapes)),
        "mover_shapes": float(len(mover_shapes)),
        "mover_events": float(events),
        "mover_velocities": float(len(velocities)),
    }
