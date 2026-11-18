"""E-83 (D-074): BFF-X on a ring ("BFF-XR"): Tierra's one-dimensional memory with BFF-X's borrowing.

The rule is BFF-X (scripts/bffx.py, D-072) unchanged, except WHO meets WHOM. The C epoch (`bffx.c x_epoch`) is reused
as it is: it runs the pairs of `perm` in order and writes each pair's tape back in that order, cut as a whole (so
pieces can still merge across the A/B boundary, exactly as in E-82). The soup buffer itself is the space:

  geometry "ring"   the programs sit on a ring in buffer order. Each epoch an offset o in {0, 1} is drawn and program
                    o + 2k is paired with program o + 2k + 1 (the last one wraps to program 0; with an odd count the
                    left-over program sits out); a coin per pair decides which runs first (A). The tapes are written
                    back in ring order, so a pair's pieces (a copier's copies, a parasite's copies) stay where the pair
                    was: offspring sit next to their parent. Library C (libmode neighbour) is drawn uniformly from the
                    programs within RADIUS positions of A on the ring (A and B included), read only, as in E-82.
  geometry "mixed"  bffx.Soup itself (E-82: random pairs, library from the whole soup); the well-mixed control.
  libscope          "local" (default for ring) or "global" (ring pairs, library from the whole soup; exploratory
                    decomposition).

With offset 1 the ring is rotated by one program per epoch (the wrapped pair is written last); a rotation changes
nothing on a ring. Mutation as bffx.Soup (after the epoch, positions uniform over the buffer).

A resistant host's refusals therefore protect the programs around it, most of which are its own kin: the step E-82's
interpretation predicted (J-100).
"""
from __future__ import annotations

import ctypes

import numpy as np

import bffx as X

RADIUS = 4


class RingSoup(X.Soup):
    def __init__(self, radius: int = RADIUS, libscope: str = "local", block: int | None = None, **kw):
        super().__init__(**kw)
        self.radius, self.libscope, self.block = radius, libscope, block
        self._blk = None

    def pairs(self) -> np.ndarray:
        N = self.n
        if self.block:
            return self._block_pairs()
        o = int(self.rng.integers(2))
        idx = (np.arange(N, dtype=np.int64) + o) % N
        m = N // 2
        a, b = idx[0:2 * m:2], idx[1:2 * m:2]
        flip = self.rng.integers(0, 2, m).astype(bool)
        first, second = np.where(flip, b, a), np.where(flip, a, b)
        perm = np.empty(N, np.int32)
        perm[0:2 * m:2], perm[1:2 * m:2] = first, second
        if N % 2:
            perm[-1] = idx[-1]
        return perm

    def _block_pairs(self) -> np.ndarray:
        """Demes: the ring is cut into blocks of `block` consecutive programs at a random offset; each block's
        programs are shuffled and the blocks concatenated in ring order; consecutive programs are paired (a pair
        crosses into the next block only after an odd-sized block). Block of each position kept for the library."""
        N, K = self.n, self.block
        o = int(self.rng.integers(K))
        idx = (np.arange(N, dtype=np.int64) + o) % N
        blk = np.arange(N) // K
        key = blk * 2.0 + self.rng.random(N)          # shuffle within blocks, keep block order
        order = np.argsort(key, kind="stable")
        self._blk = (idx[order], blk[order], blk)
        return idx[order].astype(np.int32)

    def epoch(self) -> int:
        N = self.n
        perm = self.pairs()
        m = max(1, N // 2)
        if self.libmode == "neighbour" and self.block and self.libscope == "local":
            # library: a program drawn uniformly from A's block
            _, bl, _ = self._blk
            nb = int(bl.max()) + 1
            start = np.searchsorted(bl, np.arange(nb))
            size = np.diff(np.append(start, N))
            ba = bl[0:2 * (N // 2):2]
            pos = start[ba] + (self.rng.random(len(ba)) * size[ba]).astype(np.int64)
            libidx = perm[pos].astype(np.int32)
            if len(libidx) == 0:
                libidx = np.zeros(1, np.int32)
        elif self.libmode == "neighbour":
            if self.libscope == "local":
                libidx = ((perm[0:2 * (N // 2):2].astype(np.int64)
                           + self.rng.integers(-self.radius, self.radius + 1, N // 2)) % N).astype(np.int32)
                if len(libidx) == 0:
                    libidx = np.zeros(1, np.int32)
            else:
                libidx = self.rng.integers(0, N, m).astype(np.int32)
        else:
            libidx = np.zeros(1, np.int32)
        dst = np.empty_like(self.buf)
        cap = len(self.buf) // X.LMIN + 2
        nl, org = np.empty(cap, np.int32), np.empty(cap, np.int32)
        nout = ctypes.c_int(0)
        self.last_steps = int(X.lib().x_epoch(self.buf.ctypes.data, self.lens.ctypes.data, N, perm.ctypes.data,
                                              libidx.ctypes.data, dst.ctypes.data, nl.ctypes.data, org.ctypes.data,
                                              ctypes.byref(nout), self.steps, X.MODES[self.mode],
                                              X.LIBMODES[self.libmode], X.MARKER, X.LMIN, X.LMAX))
        k = nout.value
        self.buf, self.lens, self.origin = dst, nl[:k].copy(), org[:k].copy()
        if self.mutation > 0:
            mm = self.rng.binomial(self.buf.size, self.mutation)
            pos = self.rng.integers(0, self.buf.size, mm)
            self.buf[pos] = self.rng.integers(0, 256, mm, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps

    def state(self) -> dict:
        return {**super().state(), "geometry": "ring", "radius": self.radius, "libscope": self.libscope,
                "block": self.block}


def make(geometry: str = "ring", **kw) -> X.Soup:
    if geometry == "ring":
        return RingSoup(**kw)
    if geometry == "ring-global":
        return RingSoup(libscope="global", **kw)
    if geometry.startswith("deme"):                  # "deme64" = blocks of 64 programs, library from A's block
        kw.pop("radius", None)
        glob = geometry.endswith("-global")
        return RingSoup(block=int(geometry[4:].replace("-global", "")), libscope="global" if glob else "local", **kw)
    if geometry == "mixed":
        kw.pop("radius", None)
        return X.Soup(**kw)
    raise ValueError(geometry)


def from_programs(progs, geometry: str = "ring", **kw) -> X.Soup:
    progs = [X.u8(p) for p in progs]
    return make(geometry, buf=np.concatenate(progs), lens=np.array([len(p) for p in progs], np.int32), **kw)


def restore(st: dict, **kw) -> X.Soup:
    rng = np.random.default_rng()
    rng.bit_generator.state = st["rng"]
    geo = kw.pop("geometry", st.get("geometry", "mixed"))
    extra = {"radius": int(st.get("radius", RADIUS))} if geo.startswith("ring") else {}
    if geo == "ring" and st.get("block"):
        geo = f"deme{int(st['block'])}" + ("-global" if st.get("libscope") == "global" else "")
        extra = {}
    if geo == "ring":
        extra["libscope"] = st.get("libscope", "local")
    s = make(geo, buf=st["buf"], lens=st["lens"], rng=rng, libmode=kw.pop("libmode", st.get("libmode", "neighbour")),
             **extra, **kw)
    s.epochs = int(st["epochs"])
    return s
