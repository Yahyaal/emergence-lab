"""E-81 (D-070): variable-length BFF ("BFF-VL"). Interpreter and cut rule in scripts/bffvl.c.

The rule, in full:
  * the soup is a fixed budget of W bytes (default 2^20, as a 2^14 x 64 BFF soup), split into programs of
    LMIN..LMAX bytes (4..128); at the start the W random bytes are cut by the same rule as any tape;
  * each epoch the programs are paired at random (a random permutation, consecutive pairs; with an odd count the
    last one sits out); each pair's tape A ++ B is run by the BFF interpreter, with head0 at 0 and head1 at the
    partner's first byte (the variable-length form of the h = 64 head-start rule, E-56, E-80 Part B), step limit 8192;
  * the tape is then cut after every marker byte M = 0x21 ('!', a no-op for the interpreter) and wherever a piece
    reaches LMAX bytes; no piece shorter than LMIN (bffvl.c `vl_cut`). The pieces are the new programs. Bytes are
    conserved, the number of programs is not;
  * then every byte mutates to a random value with probability 0.00024 (as BFF).
Nothing rewards copying or shortness. A program that copies itself into its partner's bytes makes as many copies as
fit, so a short copier makes more copies per pair than a long one; whether short copiers arise and win is the
question.

Controls of the rule (pytest, benchmark): marker disabled and LMAX = L with all programs L bytes == the h = L BFF soup
(`bff_kernels.epoch_h`) bit for bit; bytes conserved; every piece within bounds.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import zlib
from pathlib import Path

import numpy as np

MARKER, LMIN, LMAX = 0x21, 4, 128
W, MUT, STEPS = 2 ** 20, 0.00024, 8192
EDGE = 1  # heads halt the run when they would leave the tape (BFF: wrap, EDGE = 0); D-070
MODES = {"bff": 0, "noexec": 1, "copyall": 2}
OPS = np.frombuffer(b"<>{}-+.,[]", np.uint8)
NONOP = np.array([v for v in range(256) if v not in set(OPS.tolist()) and v != MARKER], np.uint8)
NONOP_NZ = NONOP[NONOP != 0]
TOL, THR, OPMIN = 2, 90, 75  # family / copy test: length within +-2 bytes, >= 90% bytes, >= 75% instruction bytes
_LIB = None
P = ctypes.c_void_p


def lib():
    global _LIB
    if _LIB is None:
        src = Path(__file__).with_name("bffvl.c")
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "emergence-lab"
        cache.mkdir(parents=True, exist_ok=True)
        so = cache / f"bffvl-{hashlib.sha1(src.read_bytes()).hexdigest()[:12]}.so"
        if not so.exists():
            tmp = so.with_suffix(f".{os.getpid()}.tmp")
            subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
            os.replace(tmp, so)
        L = ctypes.CDLL(str(so))
        I, LG, U64 = ctypes.c_int, ctypes.c_long, ctypes.c_uint64
        L.vl_run.restype, L.vl_run.argtypes = LG, [P, I, LG, I, I]
        L.vl_cut.restype, L.vl_cut.argtypes = I, [P, I, I, I, I, P]
        L.vl_epoch.restype = LG
        L.vl_epoch.argtypes = [P, P, I, P, P, P, P, P, P, LG, I, I, I, I, I]
        L.vl_screen.restype = I
        L.vl_screen.argtypes = [P, I, I, I, U64, LG, I, I, I, I, I, I, I, I, P]
        L.vl_members.restype = None
        L.vl_members.argtypes = [P, P, I, P, I, I, I, I, P]
        _LIB = L
    return _LIB


def cut(t: np.ndarray, marker: int = MARKER, lmin: int = LMIN, lmax: int = LMAX) -> np.ndarray:
    """Piece lengths of a byte string under the cut rule."""
    t = np.ascontiguousarray(t, dtype=np.uint8)
    out = np.zeros(len(t) // lmin + 2, np.int32)
    k = lib().vl_cut(t.ctypes.data, len(t), marker, lmin, lmax, out.ctypes.data)
    return out[:k].copy()


def run_pair(a: np.ndarray, b: np.ndarray, marker: int = MARKER, lmin: int = LMIN, lmax: int = LMAX,
             steps: int = STEPS, edge: int = EDGE) -> list[np.ndarray]:
    """One interaction: run a ++ b (head1 at len(a)) and cut. Returns the pieces."""
    t = np.ascontiguousarray(np.concatenate([a, b]), dtype=np.uint8)
    lib().vl_run(t.ctypes.data, len(t), steps, len(a), edge)
    return split(t, cut(t, marker, lmin, lmax))


def split(buf: np.ndarray, lens: np.ndarray) -> list[np.ndarray]:
    return np.split(buf, np.cumsum(lens)[:-1]) if len(lens) else []


def pad(code: bytes, length: int, rng=None, fill: int | None = 0x80) -> np.ndarray:
    """code + filler (no-op bytes, never the marker) + marker, `length` bytes in all."""
    k = length - len(code) - 1
    if k < 0:
        raise ValueError("code too long")
    f = (np.full(k, fill, np.uint8) if fill is not None
         else NONOP_NZ[(rng or np.random.default_rng(0)).integers(0, len(NONOP_NZ), k)])
    return np.concatenate([np.frombuffer(code, np.uint8), f, [MARKER]]).astype(np.uint8)


# hand-written copier: head0 at 0, head1 at the partner; [.>}] copies byte by byte until head0 meets a zero byte
# (there is none in the program, so the loop copies the program repeatedly into the partner's bytes until the step
# limit or until it overwrites itself); the marker at its end makes each copy a separate program.
COPIER = b"[.>}]"


def hand_copier(length: int, rng=None, fill: int | None = 0x80) -> np.ndarray:
    return pad(COPIER, length, rng, fill)


def broken_copier(length: int, rng=None, fill: int | None = 0x80) -> np.ndarray:
    """Same bytes, but the loop's back-jump is gone ('.' copies one byte, then the program falls through)."""
    return pad(b"[.>}\x80", length, rng, fill)


class Soup:
    """BFF-VL soup (module docstring). `buf` holds the programs back to back, `lens` their lengths."""

    def __init__(self, w: int = W, seed: int = 0, mode: str = "bff", mutation: float = MUT, steps: int = STEPS,
                 marker: int = MARKER, lmin: int = LMIN, lmax: int = LMAX, buf=None, lens=None, rng=None,
                 edge: int = EDGE):
        self.mode, self.mutation, self.steps, self.edge = mode, mutation, steps, edge
        self.marker, self.lmin, self.lmax = marker, lmin, lmax
        self.rng = rng if rng is not None else np.random.default_rng(seed)
        if buf is None:
            buf = self.rng.integers(0, 256, w, dtype=np.uint8)
            lens = cut(buf, marker, lmin, lmax)
        self.buf = np.ascontiguousarray(buf, dtype=np.uint8).copy()
        self.lens = np.ascontiguousarray(lens, dtype=np.int32).copy()
        assert int(self.lens.sum()) == len(self.buf)
        self.epochs = 0
        self.last_steps = 0
        self.origin = self.rank = None

    @classmethod
    def from_programs(cls, progs, **kw):
        progs = [np.asarray(p, np.uint8) for p in progs]
        return cls(buf=np.concatenate(progs), lens=np.array([len(p) for p in progs], np.int32), **kw)

    @property
    def n(self) -> int:
        return len(self.lens)

    def programs(self) -> list[np.ndarray]:
        return split(self.buf, self.lens)

    def epoch(self) -> int:
        N = self.n
        perm = self.rng.permutation(N).astype(np.int32)
        dst = np.empty_like(self.buf)
        cap = len(self.buf) // self.lmin + 2
        nl, org, rk = np.empty(cap, np.int32), np.empty(cap, np.int32), np.empty(cap, np.int32)
        nout = ctypes.c_int(0)
        self.last_steps = int(lib().vl_epoch(self.buf.ctypes.data, self.lens.ctypes.data, N, perm.ctypes.data,
                                             dst.ctypes.data, nl.ctypes.data, org.ctypes.data, rk.ctypes.data,
                                             ctypes.byref(nout), self.steps, MODES[self.mode], self.marker,
                                             self.lmin, self.lmax, self.edge))
        k = nout.value
        self.buf, self.lens = dst, nl[:k].copy()
        self.origin, self.rank = org[:k].copy(), rk[:k].copy()
        if self.mutation > 0:
            m = self.rng.binomial(self.buf.size, self.mutation)
            idx = self.rng.integers(0, self.buf.size, m)
            self.buf[idx] = self.rng.integers(0, 256, m, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps

    def members(self, x: np.ndarray, tol: int = TOL, thr: int = THR, opmin: int = OPMIN) -> np.ndarray:
        return members(self.buf, self.lens, x, tol, thr, opmin)

    def state(self) -> dict:
        return {"buf": self.buf.copy(), "lens": self.lens.copy(), "rng": self.rng.bit_generator.state,
                "epochs": self.epochs}


def members(buf, lens, x, tol: int = TOL, thr: int = THR, opmin: int = OPMIN) -> np.ndarray:
    x = np.ascontiguousarray(x, dtype=np.uint8)
    buf = np.ascontiguousarray(buf, dtype=np.uint8)
    lens = np.ascontiguousarray(lens, dtype=np.int32)
    out = np.zeros(len(lens), np.uint8)
    lib().vl_members(buf.ctypes.data, lens.ctypes.data, len(lens), x.ctypes.data, len(x), tol, thr, opmin,
                     out.ctypes.data)
    return out.astype(bool)


def screen(x: np.ndarray, seed: int, partners: int = 4, lp: int = LMAX, mode: str = "bff", tol: int = TOL,
           thr: int = THR, opmin: int = OPMIN, marker: int = MARKER, lmin: int = LMIN, lmax: int = LMAX,
           steps: int = STEPS, edge: int = EDGE) -> tuple[int, int]:
    """Copy screen (bffvl.c `vl_screen`): (partners with >= 1 copy of x, total copies), x run first against random
    partners of lp bytes."""
    x = np.ascontiguousarray(x, dtype=np.uint8)
    c = ctypes.c_int(0)
    h = lib().vl_screen(x.ctypes.data, len(x), lp, partners, seed & (2 ** 64 - 1), steps, marker, lmin, lmax, tol,
                        thr, opmin, MODES[mode], edge, ctypes.byref(c))
    return int(h), int(c.value)


def is_copier(x, seed: int, partners: int = 4, **kw) -> bool:
    """Copies itself into every one of `partners` random LMAX-byte partners."""
    return screen(x, seed, partners, **kw)[0] == partners


def hoe(buf: np.ndarray) -> float:
    data = np.ascontiguousarray(buf).tobytes()
    p = np.bincount(np.frombuffer(data, np.uint8), minlength=256) / len(data)
    h0 = float(-(p[p > 0] * np.log2(p[p > 0])).sum())
    return h0 - 8 * len(zlib.compress(data, 9)) / len(data)


def top_distinct(soup: Soup, k: int = 40) -> list[tuple[bytes, int]]:
    from collections import Counter
    return Counter(map(bytes, soup.programs())).most_common(k)
