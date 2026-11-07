"""Structure census for continuous-state physics (e.g. Lenia).

Exact shape matching (structures.py) fails for continuous fields: a gliding Lenia
creature never repeats its cell values exactly. Here objects are tracked tolerantly:

* object        an 8-connected region where the value >= THRESHOLD (0.1), with its mass
                (sum of values), area and centroid
* track         objects linked frame to frame by nearest centroid (<= MAX_JUMP cells)
                with mass within a factor MASS_TOL
* persistent    a track that lasts >= 80% of the observation window
* mover         a persistent track whose net displacement is >= MIN_TRAVEL cells and
                whose path is reasonably straight (net / path length >= 0.5)
* self-propelled  the mover, copied alone (with its low-value halo) into an empty,
                separate world, keeps its mass (within MASS_TOL) and travels >= MIN_TRAVEL
                cells by itself. Same principle as the discrete test: shows it CAN move
                alone, not trajectory identity.

Returned keys mirror structures.analyse so the rest of the system works unchanged:
still_structures, vocabulary (= persistent objects), mover_shapes, mover_events,
mover_velocities, self_propelled_shapes, objects_per_frame. Note that `vocabulary` counts
persistent object INSTANCES, not shape types as in the discrete census: twenty identical
static blobs give 20. Two continuous-only keys:

* dynamic_structures  persistent objects that are not still (movers and reshaping objects)
* free_activity       fraction of cells per step whose value changes by more than
                      VALUE_TOL levels OUTSIDE still objects (each dilated by STILL_MARGIN
                      cells). The edges of static blobs keep creeping and oscillating for
                      thousands of steps (real slow relaxation, also present without
                      quantization); this measure excludes that and keeps everything else.

Value scale: uint8 states are in levels (value = level / 255, e.g. Lenia); float states
(e.g. Flow-Lenia) are in physical units. THRESHOLD and VALUE_TOL are written in 1/255
levels and converted for float states (THRESHOLD = 0.102, VALUE_TOL = 0.0078), so both
families use the same physical thresholds; uint8 results are unchanged.

Objects are labelled on the torus (components touching across the seam are merged) and
centroids use circular means, so wrapping objects are tracked correctly.
Limitations: merging and splitting objects end tracks; a slow mover may not reach
MIN_TRAVEL inside the window; objects larger than half the world are not handled.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

THRESHOLD = 26          # 0.1 on the 0..255 scale
MIN_AREA, MAX_AREA = 12, 4000
MAX_JUMP = 4.0          # cells per frame
MASS_TOL = 1.4          # mass may change by up to this factor between linked frames
MIN_TRAVEL = 5.0
VALUE_TOL = 2           # levels (of 255): smaller per-step changes are rounding-scale
STILL_MARGIN = 3        # cells around a still object whose activity is attributed to it
MIN_STILL_FRAMES = 10   # a track this long that never leaves its place anchors free_activity
_STRUCT = np.ones((3, 3), dtype=bool)


def _unit(state: np.ndarray) -> float:
    """Stored units per value 1: 255 for uint8 levels, 1 for float (physical) states."""
    return 1.0 if np.issubdtype(state.dtype, np.floating) else 255.0


def _thr(state: np.ndarray):
    return THRESHOLD if _unit(state) == 255.0 else THRESHOLD / 255.0


def _tol(state: np.ndarray):
    return VALUE_TOL if _unit(state) == 255.0 else VALUE_TOL / 255.0


def label_torus(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """8-connected labelling on a torus: components touching across the seam are merged."""
    labels, n = ndimage.label(mask, structure=_STRUCT)
    if n == 0:
        return labels, 0
    parent = np.arange(n + 1)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        if a and b:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)

    h, w = mask.shape
    for d in (-1, 0, 1):  # top row vs bottom row, and left column vs right column (with diagonals)
        for a, b in zip(labels[0], np.roll(labels[-1], d)):
            union(int(a), int(b))
        for a, b in zip(labels[:, 0], np.roll(labels[:, -1], d)):
            union(int(a), int(b))
    roots = np.array([find(i) for i in range(n + 1)])
    uniq, new = np.unique(roots, return_inverse=True)
    lab = new[labels]
    return lab, len(uniq) - 1


def objects(state: np.ndarray) -> list[dict]:
    mask = state >= _thr(state)
    labels, n = label_torus(mask)
    if n == 0:
        return []
    idx = np.arange(1, n + 1)
    v = state.astype(np.float64) / _unit(state)
    area = ndimage.sum(mask, labels, idx)
    mass = ndimage.sum(v, labels, idx)
    h, w = state.shape
    yy, xx = np.mgrid[0:h, 0:w]
    sums = []  # circular (torus) means, weighted by value: all labels in one pass per axis
    for grid, size in ((yy, h), (xx, w)):
        ang = 2 * np.pi * grid / size
        sums.append((ndimage.sum(v * np.cos(ang), labels, idx), ndimage.sum(v * np.sin(ang), labels, idx), size))
    out = []
    for i in range(n):
        if not (MIN_AREA <= area[i] <= MAX_AREA):
            continue
        c = [(np.arctan2(sn[i], cs[i]) % (2 * np.pi)) * size / (2 * np.pi) for cs, sn, size in sums]
        out.append({"label": i + 1, "area": float(area[i]), "mass": float(mass[i]), "c": np.array(c)})
    return out


def _torus_delta(a, b, shape):
    d = b - a
    for k in (0, 1):
        if d[k] > shape[k] / 2:
            d[k] -= shape[k]
        elif d[k] < -shape[k] / 2:
            d[k] += shape[k]
    return d


def track(frames: list[np.ndarray]) -> tuple[list[dict], list[list[dict]]]:
    """Link objects frame to frame. Returns (tracks, objects per frame)."""
    shape = frames[0].shape
    per = [objects(f) for f in frames]
    tracks: list[dict] = []
    active: dict[int, int] = {}  # object index in previous frame -> track id
    for t, objs in enumerate(per):
        new_active = {}
        used = set()
        if t > 0:
            prev = per[t - 1]
            cand = []
            for j, o in enumerate(objs):
                for i, p in enumerate(prev):
                    d = _torus_delta(p["c"], o["c"], shape)
                    dist = float(np.hypot(*d))
                    ratio = o["mass"] / max(p["mass"], 1e-9)
                    if dist <= MAX_JUMP and 1 / MASS_TOL <= ratio <= MASS_TOL and i in active:
                        cand.append((dist, i, j, d))
            for dist, i, j, d in sorted(cand, key=lambda x: x[0]):
                if j in used or i not in active or active[i] in new_active.values():
                    continue
                tid = active[i]
                tr = tracks[tid]
                tr["disp"] += d
                tr["path"] += dist
                tr["end"] = t
                tr["last"] = (t, j)
                new_active[j] = tid
                used.add(j)
        for j, o in enumerate(objs):
            if j not in used:
                tracks.append({"start": t, "end": t, "disp": np.zeros(2), "path": 0.0, "first": (t, j),
                               "last": (t, j)})
                new_active[j] = len(tracks) - 1
        active = new_active
    for tr in tracks:
        tr["length"] = tr["end"] - tr["start"] + 1
    return tracks, per


def isolate(state: np.ndarray, obj: dict, margin: int = 4) -> np.ndarray:
    """The object with its low-value halo, alone, shifted to the centre of the world
    (so it is never split by the torus seam). Everything else is zeroed."""
    h, w = state.shape
    shift = (int(round(h / 2 - obj["c"][0])), int(round(w / 2 - obj["c"][1])))
    rolled = np.roll(state, shift, axis=(0, 1))
    labels, n = ndimage.label(rolled >= _thr(state), structure=_STRUCT)
    if n == 0:
        return np.zeros_like(state)
    cents = ndimage.center_of_mass(rolled >= _thr(state), labels, np.arange(1, n + 1))
    best = 1 + int(np.argmin([np.hypot(cy - h / 2, cx - w / 2) for cy, cx in cents]))
    halo = ndimage.binary_dilation(labels == best, structure=_STRUCT, iterations=margin)
    return np.where(halo, rolled, 0).astype(state.dtype)


def self_propelled(physics, state: np.ndarray, obj: dict, steps: int = 100) -> bool:
    """Does the object, alone in an empty world, keep its mass and travel by itself?"""
    alone = isolate(state, obj)
    rows, cols = np.nonzero(alone)
    if len(rows) == 0:
        return False
    r0, r1, c0, c1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
    pad = 2 * int(MIN_TRAVEL) + 3 * getattr(physics, "R", 13) + steps // 2
    side = int(max(64, max(r1 - r0, c1 - c0) + 2 * pad))
    world = np.zeros((side, side), state.dtype)
    oy, ox = (side - (r1 - r0)) // 2, (side - (c1 - c0)) // 2
    world[oy:oy + r1 - r0, ox:ox + c1 - c0] = alone[r0:r1, c0:c1]
    start = objects(world)
    if not start:
        return False
    o0 = max(start, key=lambda o: o["mass"])
    for _ in range(steps):
        world = physics.step(world)
    end = objects(world)
    if not end:
        return False
    o1 = max(end, key=lambda o: o["mass"])
    ratio = o1["mass"] / o0["mass"]
    travel = float(np.hypot(*_torus_delta(o0["c"], o1["c"], world.shape)))
    return 1 / MASS_TOL <= ratio <= MASS_TOL and travel >= MIN_TRAVEL and len(end) <= 2


def free_activity(frames: list[np.ndarray], per: list[list[dict]], tracks: list[dict],
                  margin: int = STILL_MARGIN) -> float:
    """Mean fraction of cells per step that change by more than VALUE_TOL levels outside
    objects that stay in place. An object stays in place if its track lasts at least
    MIN_STILL_FRAMES frames with a net displacement under 1 cell; persistence is not
    required, because pinching blobs change mass abruptly and break their tracks without
    moving. Its cells at the start and end of the track, dilated by `margin` cells on the
    torus, are excluded."""
    still = [tr for tr in tracks if tr["length"] >= MIN_STILL_FRAMES and np.hypot(*tr["disp"]) < 1.0]
    if len(frames) < 2:
        return 0.0
    mask = np.zeros(frames[0].shape, dtype=bool)
    labels: dict[int, np.ndarray] = {}
    for tr in still:
        for t, j in (tr["first"], tr["last"]):
            if t not in labels:
                labels[t] = label_torus(frames[t] >= _thr(frames[t]))[0]
            mask |= labels[t] == per[t][j]["label"]
    if mask.any():
        mask = ndimage.maximum_filter(mask, size=2 * margin + 1, mode="wrap")
    free = ~mask
    st = np.stack(frames)
    st = st.astype(np.float64) if np.issubdtype(st.dtype, np.floating) else st.astype(np.int16)
    changed = np.abs(np.diff(st, axis=0)) > _tol(frames[0])
    return float((changed & free).sum()) / (changed.shape[0] * free.size)


def analyse(frames: list[np.ndarray], physics=None, max_tests: int = 6) -> dict[str, float]:
    W = len(frames)
    if W == 0:
        return {}
    tracks, per = track(frames)
    persistent = [tr for tr in tracks if tr["length"] >= 0.8 * W]
    movers = [tr for tr in persistent if np.hypot(*tr["disp"]) >= MIN_TRAVEL
              and np.hypot(*tr["disp"]) >= 0.5 * max(tr["path"], 1e-9)]
    still = [tr for tr in persistent if np.hypot(*tr["disp"]) < 1.0]
    verified = None
    if physics is not None:
        verified = 0
        for tr in sorted(movers, key=lambda tr: -np.hypot(*tr["disp"]))[:max_tests]:
            t, j = tr["last"]
            verified += self_propelled(physics, frames[t], per[t][j])
    dirs = {(int(np.sign(round(tr["disp"][0] / max(np.hypot(*tr["disp"]), 1e-9)))),
             int(np.sign(round(tr["disp"][1] / max(np.hypot(*tr["disp"]), 1e-9))))) for tr in movers}
    return {
        "self_propelled_shapes": None if verified is None else float(verified),
        "objects_per_frame": float(np.mean([len(p) for p in per])),
        "still_structures": float(len(still)),
        "vocabulary": float(len(persistent)),
        "mover_shapes": float(len(movers)),
        "mover_events": float(len(movers)),
        "mover_velocities": float(len(dirs)),
        "dynamic_structures": float(len(persistent) - len(still)),
        "free_activity": free_activity(frames, per, tracks),
    }


def emergent_glider(physics, side: int = 128, settle: int = 300) -> np.ndarray:
    """A glider DERIVED from the physics (not hand-typed): an asymmetric seed (elliptical
    disc with a value gradient) left to settle in an empty world. For the Orbium
    parameters it becomes a single object that keeps its mass (~70) and travels
    ~0.53 cells/step (measured over steps 300-700).
    Used as the positive control; returns the settled world."""
    yy, xx = np.mgrid[0:side, 0:side]
    cy = cx = side // 2
    rad, slope, ecc = 10, 1.0, 0.7
    r = np.hypot((yy - cy) / ecc, xx - cx)
    g = np.clip(0.5 + slope * (xx - cx) / (2 * rad), 0, 1)
    a = np.where(r <= rad, g * np.clip(1 - (r / rad) ** 2, 0, 1) * 1.6, 0)
    w = np.rint(np.clip(a, 0, 1) * 255).astype(np.uint8)
    for _ in range(settle):
        w = physics.step(w)
    return w
