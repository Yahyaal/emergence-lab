"""E-84 (D-076): fixed-length BFF-X on demes ("BFF-XF"): BFF's fixed 64-byte programs with E-82's borrowed read-only
code and E-83's demes. Interpreter: scripts/bffx.c, unchanged.

Why: in E-81 to E-83 (variable length) every byte a program carries costs copies, so the shortest copier (6 bytes)
wins and a lock (the shortest resistant host has 10 bytes) is priced out. Here every program has exactly L = 64 bytes,
so a lock costs no length: a copier copies all 64 bytes whatever its loop length, and one copy fills one partner.

The rule, per pair (A runs first, B is the partner, C the library):
  * data tape A ++ B (128 bytes); head0 and the instruction pointer start at 0, head1 at 64 (BFF's h = 64 rule);
    heads halt the run at the ends of A ++ B (as in BFF-VL/BFF-X; BFF wraps);
  * code = A (live) ++ C: once the instruction pointer runs past A's 64 bytes it fetches C's code, read only (libmode
    "neighbour"); "none" = only A's code runs (nothing can be borrowed); "live" = code A ++ B (fixed-length BFF with
    halting heads, the control);
  * after the run the tape is cut into two 64-byte programs (no marker: `x_cut` with marker -1 and LMIN = LMAX = 64);
  * mutation 0.00024 per byte per epoch (BFF's rate).
  Geometry (who meets whom): "deme64" = E-83's demes (programs on a ring in buffer order, cut each epoch at a random
  offset into blocks of 64 programs; pairs and C within a block; pieces written back in place); "mixed" = random pairs,
  C from the whole soup (E-82).

A program that falls off its own end (no halt, heads unmoved) runs C's code on its own bytes: if C is a copy loop it is
copied into B. That is a parasite. A host that checks its caller before copying (a lock) refuses it.
"""
from __future__ import annotations

import ctypes
from collections import Counter

import numpy as np

import bffx as X
import bffxr as R_

L = 64
N = 2 ** 14                      # programs (W = 2^20 bytes, as BFF-X)
W = N * L
NOMARK = -1                      # never equals a byte: no marker cut
STEPS, MUT = X.STEPS, X.MUT
TOL, THR, OPMIN = 0, X.THR, X.OPMIN


class FSoup(X.Soup):
    MARKER, LMIN, LMAX = NOMARK, L, L


class FRing(R_.RingSoup):
    MARKER, LMIN, LMAX = NOMARK, L, L


def random_lens(w: int) -> np.ndarray:
    assert w % L == 0
    return np.full(w // L, L, np.int32)


def make(geometry: str = "deme64", w: int = W, rng=None, seed: int = 0, buf=None, lens=None, **kw) -> X.Soup:
    rng = rng if rng is not None else np.random.default_rng(seed)
    if buf is None:
        buf = rng.integers(0, 256, w, dtype=np.uint8)
        lens = random_lens(w)
    kw.pop("radius", None)
    if geometry == "mixed":
        return FSoup(buf=buf, lens=lens, rng=rng, **kw)
    if geometry.startswith("deme"):
        glob = geometry.endswith("-global")
        return FRing(block=int(geometry[4:].replace("-global", "")), libscope="global" if glob else "local",
                     buf=buf, lens=lens, rng=rng, **kw)
    raise ValueError(geometry)


def from_programs(progs, geometry: str = "deme64", **kw) -> X.Soup:
    progs = [X.u8(p) for p in progs]
    assert all(len(p) == L for p in progs)
    return make(geometry, buf=np.concatenate(progs), lens=random_lens(L * len(progs)), **kw)


def restore(st: dict, geometry: str, **kw) -> X.Soup:
    rng = np.random.default_rng()
    rng.bit_generator.state = st["rng"]
    s = make(geometry, buf=st["buf"], lens=st["lens"], rng=rng, **kw)
    s.epochs = int(st["epochs"])
    return s


def cut(t) -> np.ndarray:
    t = X.u8(t)
    out = np.zeros(len(t) // L + 2, np.int32)
    k = X.lib().x_cut(t.ctypes.data, len(t), NOMARK, L, L, out.ctypes.data)
    return out[:k].copy()


def run_pair(a, b, c=None, libmode: str = "neighbour", steps: int = STEPS) -> tuple[list[np.ndarray], int]:
    a, b = X.u8(a), X.u8(b)
    t = X.u8(np.concatenate([a, b]))
    cc = X.u8(c if c is not None else np.zeros(1, np.uint8))
    st = X.lib().x_run(t.ctypes.data, len(a), len(b), cc.ctypes.data, len(cc) if c is not None else 0, steps,
                       X.LIBMODES[libmode])
    return X.split(t, cut(t)), int(st)


def screen(x, seed: int, trials: int = 4, host_b=None, host_c=None, lp: int = L, lc: int = L,
           libmode: str = "neighbour", tol: int = TOL, thr: int = THR, opmin: int = OPMIN) -> tuple[int, int]:
    """x first against a partner (host_b, or lp random bytes) with a library (host_c, or lc random bytes). Returns
    (trials in which the partner piece is a copy of x, total copies)."""
    x = X.u8(x)
    hb = X.u8(host_b) if host_b is not None else None
    hc = X.u8(host_c) if host_c is not None else None
    c = ctypes.c_int(0)
    h = X.lib().x_screen(x.ctypes.data, len(x), hb.ctypes.data if hb is not None else None,
                         len(hb) if hb is not None else 0, lp, hc.ctypes.data if hc is not None else None,
                         len(hc) if hc is not None else 0, lc, trials, seed & (2 ** 64 - 1), STEPS,
                         X.LIBMODES[libmode], 0, NOMARK, L, L, tol, thr, opmin, ctypes.byref(c))
    return int(h), int(c.value)


def is_copier(x, seed: int, partners: int = 4, libmode: str = "none", **kw) -> bool:
    return screen(x, seed, partners, libmode=libmode, **kw)[0] == partners


def members(buf, lens, x, tol: int = TOL, thr: int = THR, opmin: int = OPMIN) -> np.ndarray:
    """Family of x: >= thr % of the bytes equal and >= opmin % of the instruction bytes equal, checked in BOTH
    directions (x's instruction bytes in y, and y's in x). The second direction is new for fixed length: an inert
    program (no instruction bytes) is otherwise 'like' every host that carries the same filler."""
    m = X.match(buf, lens, x, tol, thr, opmin) >= 0
    if not m.any():
        return m
    Y = X.u8(buf).reshape(-1, L)
    op = np.isin(Y, X.OPS)
    nop = op.sum(1)
    got = (op & (Y == X.u8(x)[None, :])).sum(1)
    return m & ((nop == 0) | (got * 100 >= opmin * nop))


def top_distinct(s: X.Soup, k: int = 40) -> list[tuple[bytes, int]]:
    return Counter(map(bytes, s.buf.reshape(-1, L))).most_common(k)


def programs(s: X.Soup) -> list[np.ndarray]:
    return list(s.buf.reshape(-1, L))


FILL = 0x80


def pad(code: bytes, fill: int = FILL) -> np.ndarray:
    """code then no-op filler to 64 bytes (no marker in this rule)."""
    return np.concatenate([np.frombuffer(code, np.uint8), np.full(L - len(code), fill, np.uint8)]).astype(np.uint8)
