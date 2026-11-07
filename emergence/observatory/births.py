"""Birth detector: does an object, alone, make copies that make copies? (J-032, D-028)

Works for discrete and continuous physics. Like the self-propulsion test it is an
intervention on an isolated clone, never on the original universe.

Method: the candidate object (with a halo) is copied alone into an empty world (the
physics' vacuum) and run. At every checkpoint, objects are matched to the parent:

* discrete physics    same shape as the parent (orientation-free, structures.canonical)
* continuous physics  mass within a factor COPY_TOL (2) of the parent's mass; spots that
                      grow and then divide swing about 2x in mass over a cycle

A copy count series is recorded. The object REPRODUCES (generation 1) if

* the late copy count (max over the second half) is >= MIN_COPIES (discrete 3, continuous 4)
  and at least MIN_GROWTH (2) times the max over the first quarter: copies keep multiplying.
  (Added after E-27, J-032: a Lenia blob that bursts into a world-filling labyrinth makes
  ~80 similar-mass pieces within 500 steps and then stops; "late > early" let it through); for continuous physics 4 copies within a
  factor 2 need at least twice the parent's mass, so a parent that only breaks up into
  pieces (fragmentation without growth) cannot pass;
* at that checkpoint the copies hold >= CLEAN_FRAC of all the matter in the world, so
  copies are not just a common shape among debris (explosive rules, noise);
* an empty world run the same way makes no copies (background null: the physics does not
  create parent-like objects from vacuum, e.g. noise control physics).

Generation 2: one copy at that checkpoint is isolated alone into a fresh world and tested
the same way, with copies still matched to the ORIGINAL parent (so the type cannot drift
by a factor 2 per generation; E-27 showed 377 -> 278 -> 169). A "reproducer" passes both generations: its copies make copies.

Rule-level null (discrete only): random patterns of the parent's size and density, tested
the same way. If they reproduce THEMSELVES (Fredkin's linear rule copies everything), the
verdict is "rule-level duplication". For continuous physics a scrambled patch of the
parent's values is tested too, but only reported (`attractor`): a rule in which any lump of
matter becomes a dividing spot (Gray-Scott) is still reproducing; it says the type is an
attractor, not a copy of a particular parent.

Verdicts: "reproducer", "rule-level duplication", "one generation" (gen 1 passes, the copy
does not reproduce), "explosive" (the world fills before the test can decide), "background"
(vacuum makes copies), "no reproduction".

What this does NOT show: heredity. Copies are matched to the parent by construction; a
measure of whether offspring differ like their parents is a separate step (needs a
physics with heritable variation, e.g. Flow-Lenia with localized parameters).
Limitation: isolation runs in vacuum, so mass-conserving physics (Flow-Lenia) can never
pass: copies need matter from somewhere. A fed-world variant is future work.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from . import continuous as C
from .shapes import canonical, canonical_patch
from .structures import census

COPY_TOL = 2.0
MIN_COPIES = {False: 3, True: 4}  # by `continuous`
CLEAN_FRAC = 0.75
MIN_GROWTH = 2
FILL_FRACTION = 0.3  # the test world counts as full beyond this occupied fraction
DISCRETE = {"steps": 192, "every": 1, "side": 160}
CONTINUOUS = {"steps": 4000, "every": 50, "side": 160}


def _continuous(physics) -> bool:
    return bool(getattr(physics, "continuous", False))


def field(physics, state: np.ndarray) -> np.ndarray:
    """The 2D field objects are found in: the state, or the physics' view for multi-channel states."""
    return physics.view(state) if state.ndim == 3 else state


def vacuum(physics, shape: tuple[int, int], like: np.ndarray) -> np.ndarray:
    if hasattr(physics, "vacuum"):
        return physics.vacuum(shape)
    return np.zeros(shape, like.dtype)


def find(physics, state: np.ndarray) -> list[dict]:
    """Objects with a mass and a `mask` (cells), on the torus."""
    f = field(physics, state)
    if _continuous(physics):
        objs = C.objects(f)
        labels = C.label_torus(f >= C._thr(f))[0] if objs else None
        for o in objs:
            o["mask"] = labels == o["label"]
        return objs
    labels, n = C.label_torus(f > 0)
    out = []
    for i in range(1, n + 1):
        m = labels == i
        out.append({"mask": m, "mass": float(m.sum())})
    return out


def _shape_key(f: np.ndarray, mask: np.ndarray) -> bytes:
    rows, cols = np.nonzero(mask)
    patch = np.where(mask, f, 0)[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    return canonical_patch(patch.astype(np.uint8))


def alone(physics, state: np.ndarray, mask: np.ndarray, side: int, margin: int = 4) -> np.ndarray:
    """The object (mask dilated by `margin` cells) copied into the centre of an empty world."""
    halo = ndimage.binary_dilation(mask, structure=np.ones((3, 3), bool), iterations=margin) if margin else mask
    h, w = mask.shape
    rows, cols = np.nonzero(halo)
    # centre on the circular mean so objects across the seam stay whole
    cy = (np.angle(np.exp(2j * np.pi * rows / h).mean()) % (2 * np.pi)) * h / (2 * np.pi)
    cx = (np.angle(np.exp(2j * np.pi * cols / w).mean()) % (2 * np.pi)) * w / (2 * np.pi)
    shift = (int(round(h / 2 - cy)), int(round(w / 2 - cx)))
    ax = (-2, -1)
    rs, rm = np.roll(state, shift, axis=ax), np.roll(halo, shift, axis=(0, 1))
    rows, cols = np.nonzero(rm)
    r0, r1, c0, c1 = rows.min(), rows.max() + 1, cols.min(), cols.max() + 1
    if max(r1 - r0, c1 - c0) > side - 8:
        raise ValueError("object too large for the test world")
    world = vacuum(physics, (side, side), state)
    oy, ox = (side - (r1 - r0)) // 2, (side - (c1 - c0)) // 2
    sub = rs[..., r0:r1, c0:c1]
    keep = rm[r0:r1, c0:c1]
    tgt = world[..., oy:oy + r1 - r0, ox:ox + c1 - c0]
    world[..., oy:oy + r1 - r0, ox:ox + c1 - c0] = np.where(keep, sub, tgt)
    return world


def _matcher(physics, world: np.ndarray, parent: dict):
    # discrete: the parent's shape comes from parent["key"] if given, else from `world`
    """Function objs, field -> (copies, matter fraction in copies)."""
    cont = _continuous(physics)
    if cont:
        pm = parent["mass"]

        def is_copy(o, f):
            return pm / COPY_TOL <= o["mass"] <= pm * COPY_TOL
    else:
        key = parent.get("key") or _shape_key(field(physics, world), parent["mask"])

        def is_copy(o, f):
            return o["mass"] == parent["mass"] and _shape_key(f, o["mask"]) == key
    return is_copy


def copy_series(physics, world: np.ndarray, parent: dict, steps: int, every: int):
    """Copies per checkpoint and, for each, (copies, clean fraction, copy objects, state).
    Stops early (full=True) when the world fills up."""
    is_copy = _matcher(physics, world, parent)
    cont = _continuous(physics)
    series, snaps = [], []
    full = False
    for t in range(steps + 1):
        if t % every == 0:
            f = field(physics, world)
            occ = (f >= C._thr(f)) if cont else (f > 0)
            if occ.mean() > FILL_FRACTION:
                full = True
                break
            objs = find(physics, world)
            copies = [o for o in objs if is_copy(o, f)]
            total = (f.astype(np.float64) / C._unit(f))[occ].sum() if cont else float(occ.sum())
            cm = sum(o["mass"] for o in copies)
            series.append(len(copies))
            snaps.append((len(copies), cm / total if total > 0 else 0.0, copies, world))
        if t < steps:
            world = physics.step(world)
    return series, snaps, full


def generation(physics, world: np.ndarray, parent: dict, steps: int, every: int, ref: dict | None = None) -> dict:
    """One generation; copies are matched to `ref` (default: `parent`, the object in `world`)."""
    series, snaps, full = copy_series(physics, world, ref or parent, steps, every)
    need = MIN_COPIES[_continuous(physics)]
    if len(series) < 4:
        return {"ok": False, "full": full, "early": 0, "late": 0, "clean": 0.0, "snap": None, "series": series}
    q = max(1, len(series) // 4)
    early = max(series[:q + 1])
    half = len(series) // 2
    i = half + int(np.argmax(series[half:]))
    late, clean = snaps[i][0], snaps[i][1]
    ok = late >= need and late >= MIN_GROWTH * max(early, 1) and clean >= CLEAN_FRAC
    return {"ok": bool(ok), "full": full, "early": int(early), "late": int(late), "clean": round(float(clean), 3),
            "snap": snaps[i] if ok else None, "series": series}


def reproduction_test(physics, state: np.ndarray, obj: dict, rng: np.random.Generator,
                      steps: int | None = None, every: int | None = None, side: int | None = None,
                      n_random: int = 3) -> dict:
    """Two-generation reproduction test of one object (see module docstring)."""
    cont = _continuous(physics)
    cfg = CONTINUOUS if cont else DISCRETE
    steps, every, side = steps or cfg["steps"], every or cfg["every"], side or cfg["side"]
    margin = 4 if cont else 0
    try:
        w0 = alone(physics, state, obj["mask"], side, margin)
    except ValueError:
        return {"verdict": "too large"}
    start = find(physics, w0)
    if not start:
        return {"verdict": "no reproduction", "gen1": None}
    parent = max(start, key=lambda o: o["mass"])
    if not cont:
        parent["key"] = _shape_key(field(physics, w0), parent["mask"])
    g1 = generation(physics, w0, parent, steps, every)
    out = {"parent_mass": round(parent["mass"], 2), "gen1": {k: v for k, v in g1.items() if k != "snap"}}
    if not g1["ok"]:
        out["verdict"] = "explosive" if g1["full"] and g1["late"] < MIN_COPIES[cont] else "no reproduction"
        return out
    # background null: vacuum alone must not make copies
    vac = vacuum(physics, (side, side), state)
    bg, _, _ = copy_series(physics, vac, parent, steps, every)
    out["background_copies"] = int(max(bg) if bg else 0)
    if out["background_copies"]:
        out["verdict"] = "background"
        return out
    # generation 2: a copy, alone
    _, _, copies, snap_world = g1["snap"]
    child = sorted(copies, key=lambda o: o["mass"])[len(copies) // 2]
    w2 = alone(physics, snap_world, child["mask"], side, margin)
    c2 = find(physics, w2)
    g2 = generation(physics, w2, max(c2, key=lambda o: o["mass"]), steps, every, ref=parent) if c2 else {"ok": False}
    out["gen2"] = {k: v for k, v in g2.items() if k != "snap"}
    # rule-level null (discrete) / attractor check (continuous): scrambled patches
    f0 = field(physics, w0)
    rows, cols = np.nonzero(parent["mask"])
    box = (slice(rows.min(), rows.max() + 1), slice(cols.min(), cols.max() + 1))
    hits = 0
    for _ in range(n_random):
        rw = w0.copy()
        sub = rw[(...,) + box]
        perm = rng.permutation(sub.shape[-2] * sub.shape[-1])
        rw[(...,) + box] = sub.reshape(sub.shape[:-2] + (-1,))[..., perm].reshape(sub.shape)
        ro = find(physics, rw)
        if ro:
            hits += generation(physics, rw, max(ro, key=lambda o: o["mass"]), steps, every)["ok"]
    out["scrambled_reproducing"] = int(hits)
    out["n_random"] = n_random
    if cont:
        out["attractor"] = bool(hits)
    if not cont and hits:
        out["verdict"] = "rule-level duplication"
    elif g2.get("ok"):
        out["verdict"] = "reproducer"
    else:
        out["verdict"] = "one generation"
    del f0
    return out


def scan(physics, state: np.ndarray, rng: np.random.Generator, max_candidates: int = 6, **kw) -> dict:
    """Test the most common object types of one state (selection like scan_for_replicators):
    discrete by shape, continuous by mass (log2 bins of width 1/2)."""
    objs = [o for o in find(physics, state) if o["mass"] >= (3 if not _continuous(physics) else 1)]
    f = field(physics, state)
    groups: dict = {}
    for o in objs:
        k = (_shape_key(f, o["mask"]) if not _continuous(physics) else int(np.floor(2 * np.log2(o["mass"]))))
        groups.setdefault(k, []).append(o)
    order = sorted(groups.values(), key=len, reverse=True)[:max_candidates]
    results = [reproduction_test(physics, state, g[0], rng, **kw) for g in order]
    return {"tested": len(results),
            "reproducers": sum(r["verdict"] == "reproducer" for r in results),
            "verdicts": [r["verdict"] for r in results], "results": results}
