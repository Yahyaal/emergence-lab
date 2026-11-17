"""E-80 groundwork: a lattice-native (neighbour-aware) common-garden fitness assay for BFF code (J-093).

E-78 measured fitness only in a well-mixed garden; spatial theory predicts that advantages which arise under local
interaction are invisible there (J-091). This assay plants a k x k block of focal programs in a resident lattice and
runs the SAME neighbour-only pairing as the E-78 S arm (`bff_spatial.spatial_pairs`, `bff_spatial.ArmSoup`), with no
mutation. The outcome is how far the focal lineage spreads.

Tracking descent: an explicit LINEAGE TAG per site, carried outside the 64 bytes (D-068 groundwork, J-093). After
each pair run the tag of the half `dst` is updated from the bytes before and after the run:
  * copy:  dst's bytes changed, and they now match a source (partner before or after the run, forward or byte-reversed:
           emergent replicators are mirror replicators, E-45) in >= SIM of the 64 bytes AND reproduce >= OPMIN of that
           source's instruction bytes (the E-73 fidelity guard, against filler smears), AND they are closer to that
           source than to dst's own previous bytes  ->  dst takes the partner's tag;
           A copy from a tagged partner also requires dst's new bytes to be >= SIM identical to the partner's ANCHOR, the
           focal program its lineage started from; dst inherits that anchor with the tag;
  * lost:  dst's bytes changed, no copy, and they are < SIM identical to dst's own anchor  ->  tag 0 (unlabelled);
  * else:  the tag stays (unchanged or lightly damaged code keeps its lineage).
So a tag means: descended from a focal program through detected copies AND still >= 90% that program. The anchor
was added after the first calibration (J-093): without it, tags drifted onto chimeras of focal and resident code
through repeated partial overwrites (in the 5006 garden only 21% of sites tagged as soup-901 code were still
901-like after 256 rounds), and a second calibration showed that copies between two members of the SAME block must
pass the anchor on too (otherwise heterogeneous blocks lose tags whenever a member writes a relative's code).
Tags are updated simultaneously from the tags before the round. Tag 0 = resident / unlabelled; focal blocks get 1
(and 2, ... for several labelled blocks in one garden).

The alternative, byte identity to the focal family (>= 90% to any block program or its reverse, as in
`program_fitness.invasion`), is computed beside the tag count for the controls only: it counts filler smears and
resident relatives as focal (controls `smear` and `kin` below), which the tag does not.

Score of one assay replicate: s = ln((N_T + 1) / (N_0 + 1)), N = number of sites carrying the focal tag, N_0 = k^2.
Under neutrality N is a martingale (voter-like), so s is slightly negative on average (Jensen); only DIFFERENCES of s
between focal sources in the same garden (same resident, block position and pairing seed: common random numbers) are
interpreted. Front: the radius-equivalent growth sqrt(N/pi) per round (descriptive).

Transplant modes (`make_block`):
  * "preserved": a contiguous k x k block cut from a source lattice at a seeded random position, positions kept;
  * "shuffled":  the same programs, positions permuted inside the block.
  For a well-mixed source (early, M, M') there is no geometry: the block is a random sample laid out at random.

    python scripts/lattice_assay.py --controls          # fast synthetic controls (also in pytest and the benchmark)
    python scripts/lattice_assay.py --garden            # build the lattice-aged resident gardens (runs/e80/)
    python scripts/lattice_assay.py --calibrate --workers 11   # full controls + noise/power on allowed data
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_spatial as BS  # noqa: E402

from emergence.observatory import program_fitness as F  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

SIM, OPMIN = 0.9, 0.75
SIDE, K, ROUNDS = 64, 8, 128                    # assay lattice 64 x 64 (4,096 programs, as invasion), block 8 x 8
CHECKPOINTS = (16, 32, 64, 96, 128, 192, 256)
OUT = Path("runs/e80")
E47 = Path(os.environ.get("E47_DIR", "/home/yahya/Documents/projects/emergence-lab/runs/e47"))
E78RUN = Path(os.environ.get("E78_RUN", "/home/yahya/Documents/projects/emergence-lab/.claude/worktrees/"
                                         "agent-ae3a0ebc051c3fb7b/runs/e78/run"))
OPS = np.zeros(256, bool)
OPS[list(B.OPS)] = True


# ---- tag tracking -------------------------------------------------------------------------------

def _match(after: np.ndarray, src: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Row-wise byte identity of `after` with `src`, and the share of src's instruction bytes reproduced."""
    eq = after == src
    ops = OPS[src]
    nops = ops.sum(1)
    fid = np.where(nops > 0, (eq & ops).sum(1) / np.maximum(nops, 1), 0.0)
    return eq.mean(1), fid


def _sim_either(A: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.maximum((A == X).mean(1), (A == X[:, ::-1]).mean(1))


def update_tags(before: np.ndarray, after: np.ndarray, pairs: np.ndarray, tags: np.ndarray,
                anchors: np.ndarray | None = None, guard: bool = True) -> tuple[np.ndarray, np.ndarray, dict]:
    """New tags and anchors after one round (see module docstring). Only pairs that touch a tagged site are examined.
    anchors[i] = the focal program site i's lineage started from (kept with the tag, passed on with copies)."""
    if anchors is None:
        anchors = before.copy()
    a, b = pairs[0::2].astype(np.int64), pairs[1::2].astype(np.int64)
    live = (tags[a] != 0) | (tags[b] != 0)
    a, b = a[live], b[live]
    new, new_anc = tags.copy(), anchors.copy()
    n_copy = n_lost = n_drift = 0
    for dst, src in ((b, a), (a, b)):
        if len(dst) == 0:
            continue
        A = after[dst]
        changed = (A != before[dst]).any(1)
        best_sim = np.zeros(len(dst))
        best_fid = np.zeros(len(dst))
        for S in (before[src], after[src], before[src][:, ::-1], after[src][:, ::-1]):
            sm, fd = _match(A, S)
            better = sm > best_sim
            best_sim = np.where(better, sm, best_sim)
            best_fid = np.where(better, fd, best_fid)
        self_sim = (A == before[dst]).mean(1)
        ok_fid = best_fid >= OPMIN if guard else np.ones(len(dst), bool)
        # a copy from a tagged partner must also still be its lineage's focal program (>= SIM to the partner's anchor)
        anc_ok = (tags[src] == 0) | (_sim_either(A, anchors[src]) >= SIM)
        # copies between two sites of the SAME tag also count: the tag stays and the anchor is passed on (members of
        # a real block differ, and mirror replicators write their byte-reverse into their kin)
        copy = changed & (best_sim >= SIM) & ok_fid & (best_sim > self_sim) & anc_ok
        # a tagged half that changed without a copy keeps its tag only while >= SIM to its own anchor
        keep = _sim_either(A, anchors[dst]) >= SIM
        lost = changed & ~copy & (tags[dst] != 0) & ~keep
        n_drift += int((lost & (self_sim >= SIM)).sum())
        new[dst[copy]] = tags[src[copy]]
        new_anc[dst[copy]] = anchors[src[copy]]
        new[dst[lost]] = 0
        n_copy += int((copy & (tags[src] != tags[dst])).sum())
        n_lost += int(lost.sum())
    return new, new_anc, {"copies": n_copy, "lost": n_lost, "drift_lost": n_drift}


class TagSoup(BS.ArmSoup):
    """bff_spatial.ArmSoup plus a lineage tag and anchor per site, updated between the pair run and mutation."""

    def __init__(self, tags: np.ndarray, guard: bool = True, **kw):
        super().__init__(**kw)
        self.tags = np.asarray(tags, np.int32).copy()
        self.anchors = self.programs.copy()
        self.guard = guard
        self.events = {"copies": 0, "lost": 0, "drift_lost": 0}

    def epoch(self) -> int:
        pairs = self.pairs()
        before = self.programs.copy()
        self.last_steps = int(B._lib().bff_epoch(self.programs.ctypes.data, self.length, pairs.ctypes.data,
                                                 self.n // 2, self.max_steps, B.MODES[self.mode]))
        self.tags, self.anchors, ev = update_tags(before, self.programs, pairs, self.tags, self.anchors, self.guard)
        for k_, v in ev.items():
            self.events[k_] += v
        if self.mutation > 0:   # identical in law to bff.Soup.epoch
            k = self.rng.binomial(self.programs.size, self.mutation)
            idx = self.rng.integers(0, self.programs.size, k)
            self.programs.reshape(-1)[idx] = self.rng.integers(0, 256, k, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps


# ---- blocks, gardens, kin ---------------------------------------------------------------------------

def like_any(P: np.ndarray, refs: np.ndarray, sim: float = SIM) -> np.ndarray:
    """Rows of P >= sim identical (either orientation) to any row of refs (refs deduplicated)."""
    refs = np.unique(np.asarray(refs, np.uint8), axis=0)
    m = np.zeros(len(P), bool)
    for x in refs:
        m |= ((P == x).mean(1) >= sim) | ((P == x[::-1]).mean(1) >= sim)
    return m


def kin_share(resident: np.ndarray, block: np.ndarray) -> float:
    """Share of resident programs >= 90% identical (either orientation) to any block program (E-54 kin rule)."""
    return float(like_any(resident, block).mean())


def block_sites(y0: int, x0: int, k: int, w: int, h: int) -> np.ndarray:
    ys, xs = np.meshgrid((y0 + np.arange(k)) % h, (x0 + np.arange(k)) % w, indexing="ij")
    return (ys * w + xs).ravel()


def make_block(source: np.ndarray, rng: np.random.Generator, k: int = K, mode: str = "preserved",
               geometry: bool = True, width: int | None = None) -> tuple[np.ndarray, dict]:
    """k*k programs in block layout (row-major). geometry=True: source is a lattice (row i = cell (i // W, i % W));
    a contiguous block is cut at a random position, kept ('preserved') or permuted ('shuffled').
    geometry=False (well-mixed source): a random sample without replacement, laid out at random (both modes)."""
    n = len(source)
    if geometry:
        w = width or int(round(np.sqrt(n)))
        h = n // w
        y0, x0 = int(rng.integers(h)), int(rng.integers(w))
        idx = block_sites(y0, x0, k, w, h)
        info = {"y0": y0, "x0": x0}
    else:
        idx = rng.choice(n, k * k, replace=False)
        info = {"sample": True}
    blk = source[idx].copy()
    if mode == "shuffled" or not geometry:
        blk = blk[rng.permutation(k * k)]
    elif mode != "preserved":
        raise ValueError(mode)
    return blk, info


def age_garden(programs: np.ndarray, rounds: int, seed, side: int = SIDE, mutation: float = 0.00024,
               every: int = 250) -> tuple[np.ndarray, list[dict]]:
    """Run a sample on the lattice (S-arm rules, with mutation) until stationary; returns the grid and a series of
    neighbour identity (share of horizontal neighbour pairs >= 90% identical), distinct programs, steps per pair."""
    s = BS.ArmSoup(arm="spatial", n=side * side, width=side, programs=programs, seed=seed, mutation=mutation)
    ser = []
    for t in range(rounds + 1):
        if t % every == 0:
            G = s.programs.reshape(side, side, -1)
            Gn = np.roll(G, 1, 1)     # either orientation: mirror replicators write their byte-reverse (E-45)
            nb = float((((G == Gn).mean(2) >= SIM) | ((G == Gn[..., ::-1]).mean(2) >= SIM)).mean())
            ser.append({"t": t, "nbr_identity": round(nb, 3), "distinct": int(len(np.unique(s.programs, axis=0))),
                        "steps_per_pair": round(s.last_steps / (s.n / 2), 1)})
        if t < rounds:
            s.epoch()
    return s.programs.copy(), ser


# ---- the assay ----------------------------------------------------------------------------------

def assay(blocks: list[np.ndarray], resident: np.ndarray, seed, arm: str = "spatial", k: int = K,
          rounds: int = ROUNDS, checkpoints=CHECKPOINTS, positions=None, mode: str = "bff", guard: bool = True,
          identity: bool = False, mutation: float = 0.0, max_steps: int = 8192) -> dict:
    """Plant each block (k*k programs, row-major) in a copy of `resident` (a side x side grid) with tag 1, 2, ...;
    run `rounds` rounds of `arm` pairing (spatial = E-78 S rules; mixed = well-mixed permutation, the old assay's
    geometry); record tag counts at checkpoints. positions: list of (y0, x0) or None (seeded random, blocks
    non-overlapping). In the mixed arm block sites are random cells (no geometry). identity=True also runs a paired
    no-injection control with the same seed and reports the byte-identity excess count (as program_fitness.invasion)."""
    rng = np.random.default_rng(seed)
    n = len(resident)
    side = int(round(np.sqrt(n)))
    P = np.ascontiguousarray(resident, np.uint8).copy()
    tags = np.zeros(n, np.int32)
    sites = []
    if arm == "spatial":
        pos = list(positions) if positions is not None else []
        while len(pos) < len(blocks):
            y0, x0 = int(rng.integers(side)), int(rng.integers(side))
            cand = set(block_sites(y0, x0, k, side, side))
            if all(not (cand & set(s)) for s in sites):
                pos.append((y0, x0))
                sites.append(block_sites(y0, x0, k, side, side))
        sites = [block_sites(y0, x0, k, side, side) for y0, x0 in pos]
    else:
        perm = rng.permutation(n)
        sites = [perm[i * k * k:(i + 1) * k * k] for i in range(len(blocks))]
        pos = None
    for j, (blk, st) in enumerate(zip(blocks, sites), 1):
        P[st] = blk
        tags[st] = j
    soup_seed = int(rng.integers(2 ** 31))
    s = TagSoup(tags, guard=guard, arm=arm, n=n, width=side, programs=P, seed=soup_seed, mutation=mutation,
                mode=mode, max_steps=max_steps)
    refs = [np.unique(b, axis=0) for b in blocks]
    ctrl = None
    if identity:
        ctrl = BS.ArmSoup(arm=arm, n=n, width=side, programs=resident, seed=soup_seed, mutation=mutation, mode=mode,
                          max_steps=max_steps)

    def ident():
        return [int(like_any(s.programs, r).sum()) - (int(like_any(ctrl.programs, r).sum()) if ctrl is not None else 0)
                for r in refs]
    series = {0: [int((s.tags == j).sum()) for j in range(1, len(blocks) + 1)]}
    idser = {0: ident()} if identity else None
    steps = 0
    for t in range(1, rounds + 1):
        steps += s.epoch()
        if ctrl is not None:
            ctrl.epoch()
        if t in checkpoints or t == rounds:
            series[t] = [int((s.tags == j).sum()) for j in range(1, len(blocks) + 1)]
            if identity:
                idser[t] = ident()
    N0 = series[0]
    NT = series[rounds]
    out = {"N0": N0, "NT": NT, "s": [float(np.log((b + 1) / (a + 1))) for a, b in zip(N0, NT)],
           "series": {str(t): v for t, v in series.items()},
           "front": [float((np.sqrt(b / np.pi) - np.sqrt(a / np.pi)) / rounds) for a, b in zip(N0, NT)],
           "purity": [float(like_any(s.programs[s.tags == j], refs[j - 1]).mean()) if (s.tags == j).any() else None
                      for j in range(1, len(blocks) + 1)],
           "purity_anchor": [float(_sim_either(s.programs[s.tags == j], s.anchors[s.tags == j]).min())
                             if (s.tags == j).any() else None for j in range(1, len(blocks) + 1)],
           "events": s.events, "steps_per_pair": round(steps / rounds / (n / 2), 1), "positions": pos}
    if identity:
        out["identity"] = {str(t): v for t, v in idser.items()}
        out["s_identity"] = [float(np.log((max(b, 0) + 1) / (max(a, 0) + 1))) for a, b in zip(idser[0], idser[rounds])]
    return out


# ---- synthetic programs for the controls ---------------------------------------------------------------

def tailed(x: np.ndarray, rng: np.random.Generator, n: int) -> np.ndarray:
    """n copies of a hand-written program with its inert filler redrawn (each its own family)."""
    code = bytes(x).index(b"\x80")
    out = np.repeat(x[None], n, 0)
    out[:, code:] = rng.choice(F.INERT, (n, 64 - code))
    return out


def smear() -> np.ndarray:
    """Deceptive: writes its first byte (inert 0x80) backwards over the whole tape from head1 = 127, so its partner
    becomes 64 x 0x80, which is 60/64 = 94% identical to the smear itself, but inert and carrying none of its
    instruction bytes (it never copies)."""
    return np.frombuffer(b"\x80[.{]" + b"\x80" * 59, np.uint8).copy()


def odd_tailed_copiers(rng: np.random.Generator, n: int) -> np.ndarray:
    """Hand-written copiers with redrawn inert tails ending in an ODD byte: trapped(1) never copies into them."""
    return F.resident_copiers(rng, n, 1.0)


# ---- controls -------------------------------------------------------------------------------------

def _rep_diff(fa, fb, resident_fn, reps, seed, side, k, rounds, **kw):
    """Paired replicates: focal A and focal B in the same garden (common random numbers: same resident, same block
    position, same pairing seed); returns per-replicate s_A, s_B."""
    sa, sb = [], []
    for r in range(reps):
        res = resident_fn(np.random.default_rng([seed, r, 0]))
        a = assay([fa(np.random.default_rng([seed, r, 1]))], res, [seed, r, 2], k=k, rounds=rounds, **kw)
        b = assay([fb(np.random.default_rng([seed, r, 1]))], res, [seed, r, 2], k=k, rounds=rounds, **kw)
        sa.append(a["s"][0])
        sb.append(b["s"][0])
    return np.array(sa), np.array(sb)


def _z(d: np.ndarray) -> float:
    return float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))) if d.std(ddof=1) > 0 else (np.inf if d.mean() > 0 else 0.0)


def controls(side: int = 32, k: int = 4, rounds: int = 48, reps: int = 8) -> list[tuple[str, bool, str]]:
    """Fast synthetic controls (pytest and `emergence benchmark --probes`): positive, negative, deceptive, null."""
    out = []
    n, kk = side * side, k * k
    rand_res = lambda g: g.integers(0, 256, (n, 64), dtype=np.uint8)
    cop_res = lambda g: tailed(B.REPLICATOR, g, n)

    # mechanics: tags move only on detected copies (label drift): noexec with heavy mutation keeps exactly k^2 tags
    r = assay([np.repeat(B.REPLICATOR[None], kk, 0)], rand_res(np.random.default_rng(1)), 1, k=k, rounds=rounds,
              mode="noexec", mutation=0.01)
    out.append(("lattice assay label drift: noexec + mutation 0.01 -> tag count stays k^2, no copies",
                r["NT"][0] == kk and r["events"]["copies"] == 0,
                f"N {r['N0'][0]} -> {r['NT'][0]}, copies {r['events']['copies']}, purity {r['purity'][0]:.2f}"))

    # positive (tracking): the hand-written replicator in random code spreads as a front; tagged sites are its code
    r = assay([np.repeat(B.REPLICATOR[None], kk, 0)], rand_res(np.random.default_rng(2)), 2, k=k, rounds=rounds,
              identity=True)
    out.append(("lattice assay positive: replicator block in random code spreads; tags = its code (purity >= 0.95)",
                r["NT"][0] >= 3 * kk and r["purity"][0] >= 0.95 and abs(r["s"][0] - r["s_identity"][0]) < 0.3,
                f"N {r['N0'][0]} -> {r['NT'][0]}, s {r['s'][0]:.2f} (identity {r['s_identity'][0]:.2f}), "
                f"purity {r['purity'][0]:.2f}, front {r['front'][0]:.3f}/round"))

    # positive (known fitness difference): parent trapped(0) vs handicapped trapped(1), each against hand-written
    # copiers whose tails end in an odd byte (trapped(1) never copies into them; they always copy into it)
    sa, sb = _rep_diff(lambda g: np.repeat(F.trapped(0)[None], kk, 0), lambda g: np.repeat(F.trapped(1)[None], kk, 0),
                       lambda g: odd_tailed_copiers(g, n), reps, 11, side, k, rounds)
    d = sa - sb
    out.append(("lattice assay positive: parent trapped(0) outspreads handicapped trapped(1) (paired, z > 3)",
                _z(d) > 3 and (d > 0).mean() >= 0.75,
                f"mean s parent {sa.mean():.2f}, handicapped {sb.mean():.2f}, d {d.mean():.2f} (z {_z(d):.1f}), "
                f"parent ahead {int((d > 0).sum())}/{reps}"))

    # negative: the same code in two blocks with different labels, one garden -> no difference
    da = []
    for rep in range(reps):
        res = cop_res(np.random.default_rng([12, rep]))
        blk = np.repeat(B.REPLICATOR[None], kk, 0)
        r = assay([blk, blk.copy()], res, [12, rep, 1], k=k, rounds=rounds)
        da.append(r["s"][0] - r["s"][1])
    da = np.array(da)
    out.append(("lattice assay negative: same code, two labels in one garden -> no difference (|z| < 2.5)",
                abs(_z(da)) < 2.5, f"mean d {da.mean():.2f} (z {_z(da):.1f}), sd {da.std(ddof=1):.2f}"))

    # deceptive: a filler smear. In a garden of programs that halt at once when they run first (program_fitness
    # "halting"), the smear turns its neighbours into 64 x 0x80, 94% identical to itself but inert and without its
    # instructions: byte identity counts them as spread, the tag (fidelity guard) does not
    halt_res = F.background(np.random.default_rng(3), n, 64, "halting")
    r = assay([np.repeat(smear()[None], kk, 0)], halt_res, 3, k=k, rounds=rounds, identity=True)
    out.append(("lattice assay deceptive: filler smear -> identity count grows, tag count does not",
                r["NT"][0] <= kk and r["identity"][str(rounds)][0] >= 1.25 * kk,
                f"tags {r['N0'][0]} -> {r['NT'][0]}; identity excess {r['identity']['0'][0]} -> "
                f"{r['identity'][str(rounds)][0]}"))
    r2 = assay([np.repeat(smear()[None], kk, 0)], halt_res, 3, k=k, rounds=rounds, guard=False)
    out.append(("lattice assay deceptive: without the fidelity guard the tag is fooled too (guard is needed)",
                r2["NT"][0] > kk, f"unguarded tags {r2['N0'][0]} -> {r2['NT'][0]}"))

    # deceptive: a block that persists without spreading (non-copier in random code) -> no spread
    r = assay([np.repeat(F.non_copier()[None], kk, 0)], rand_res(np.random.default_rng(4)), 4, k=k, rounds=rounds)
    out.append(("lattice assay deceptive: persisting non-copier block -> s <= 0 (persists, does not spread)",
                r["s"][0] <= 0.0 and r["NT"][0] <= kk, f"N {r['N0'][0]} -> {r['NT'][0]}, s {r['s'][0]:.2f}"))

    # deceptive: kin in the resident. Half the residents are the focal program itself (same code, unlabelled); the
    # focal is no fitter than its kin. Byte identity (with the paired no-injection control of the old assay) and the
    # tag are compared with a kin-free garden of equally fit copiers; the kin rule (> 0.1% kin) must fire
    kin_res = lambda g: np.where(g.random(n)[:, None] < 0.5, B.REPLICATOR[None], tailed(B.REPLICATOR, g, n))
    blk = np.repeat(B.REPLICATOR[None], kk, 0)
    tk, tf, ik, if_ = [], [], [], []
    for rep in range(reps):
        a = assay([blk], kin_res(np.random.default_rng([13, rep])), [13, rep], k=k, rounds=rounds, identity=True)
        b = assay([blk], cop_res(np.random.default_rng([13, rep])), [13, rep], k=k, rounds=rounds, identity=True)
        tk.append(a["s"][0]); tf.append(b["s"][0]); ik.append(a["s_identity"][0]); if_.append(b["s_identity"][0])
    tk, tf, ik, if_ = map(np.array, (tk, tf, ik, if_))
    kin_flag = kin_share(kin_res(np.random.default_rng(5)), blk)
    out.append(("lattice assay deceptive: kin in the resident -> kin rule fires; tag bias smaller than identity's",
                kin_flag > 0.001 and abs(tk.mean() - tf.mean()) < max(abs(ik.mean() - if_.mean()), 0.75),
                f"resident kin share {kin_flag:.2f}; tag s kin {tk.mean():.2f} vs kin-free {tf.mean():.2f}; "
                f"identity s kin {ik.mean():.2f} vs kin-free {if_.mean():.2f}"))

    # null that accounts for block selection: blocks cut at random positions of the garden itself and relabelled,
    # two per garden -> the A-B difference is centred on 0. Scores are heavy-tailed (small blocks often die out), so
    # this control uses 2 x reps replicates and a 1% two-sided level (with 8 replicates it once gave p = 0.03 by
    # chance; 24 replicates: mean -0.36 +- 0.49, J-093)
    dn = []
    for rep in range(2 * reps):
        res = cop_res(np.random.default_rng([14, rep]))
        g = np.random.default_rng([14, rep, 1])
        b1, _ = make_block(res, g, k)
        b2, _ = make_block(res, g, k)
        r = assay([b1, b2], res, [14, rep, 2], k=k, rounds=rounds)
        dn.append(r["s"][0] - r["s"][1])
    dn = np.array(dn)
    p = signflip_p(dn, two_sided=True)
    out.append(("lattice assay null: random-position blocks of the garden itself, relabelled -> no difference",
                p >= 0.01, f"mean d {dn.mean():.2f} (se {dn.std(ddof=1) / np.sqrt(len(dn)):.2f}, n {len(dn)}), "
                           f"two-sided sign-flip p {p:.3f}"))
    return out


def signflip_p(d, two_sided: bool = False, n_mc: int = 0, seed: int = 0) -> float:
    """Exact sign-flip permutation p (Monte Carlo with n_mc draws when len(d) > 16)."""
    d = np.asarray(d, float)
    if len(d) <= 16:
        S = ((np.arange(2 ** len(d))[:, None] >> np.arange(len(d))) & 1) * 2 - 1
    else:
        S = np.random.default_rng(seed).choice([-1, 1], (n_mc or 20000, len(d)))
    tot = (S * np.abs(d)).sum(1)
    if two_sided:
        return float((np.abs(tot) >= abs(d.sum()) - 1e-12).mean())
    return float((tot >= d.sum() - 1e-12).mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args()
    if a.controls:
        t0 = time.time()
        res = controls()
        for name, ok, det in res:
            print(f"{'PASS' if ok else 'FAIL'}  {name}  {det}", flush=True)
        print(json.dumps({"passed": int(sum(o for _, o, _ in res)), "total": len(res), "sec": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
