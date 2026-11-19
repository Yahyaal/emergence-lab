"""E-82 (D-072): BFF-VL with a borrowed code segment ("BFF-X"). Interpreter, cut rule and screens in scripts/bffx.c.

The rule is BFF-VL (scripts/bffvl.py, D-070) with one change: once the instruction pointer has run past the first
program A, it fetches its instructions from a second code segment L instead of from the live partner bytes. The
heads still read and write only the tape A ++ B, and only A ++ B is cut into the new programs.

  libmode "live"      L = B as it is now: BFF-VL exactly (control)
  libmode "snapshot"  L = B as it was when the run started: the partner's code runs to its end even while the heads
                      overwrite it (the partner is the host and is consumed as data)
  libmode "neighbour" L = C, a third program drawn at random from the soup before the epoch (with replacement),
                      read only: C's code runs on A ++ B, no head can reach C, so C's body is unchanged ("persistent
                      library"); B's code never runs
  libmode "none"      L empty: only A's code runs (asymmetric control; nothing can be borrowed)

A program that runs past its own end without copying anything (an inert program, say) is copied when the code it
falls into is a copy loop: that is a parasite in Tierra's sense (it executes a host's copy procedure on its own
bytes). Nothing rewards copying or punishes it.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np

MARKER, LMIN, LMAX = 0x21, 4, 128
W, MUT, STEPS = 2 ** 20, 0.00024, 8192
LIBMODES = {"live": 0, "snapshot": 1, "neighbour": 2, "none": 3}
MODES = {"bff": 0, "noexec": 1}
OPS = np.frombuffer(b"<>{}-+.,[]", np.uint8)
NONOP = np.array([v for v in range(256) if v not in set(OPS.tolist()) and v != MARKER], np.uint8)
NONOP_NZ = NONOP[NONOP != 0]
TOL, THR, OPMIN = 2, 90, 75
_LIB = None
P = ctypes.c_void_p


def lib():
    global _LIB
    if _LIB is None:
        src = Path(__file__).with_name("bffx.c")
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "emergence-lab"
        cache.mkdir(parents=True, exist_ok=True)
        so = cache / f"bffx-{hashlib.sha1(src.read_bytes()).hexdigest()[:12]}.so"
        if not so.exists():
            tmp = so.with_suffix(f".{os.getpid()}.tmp")
            subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
            os.replace(tmp, so)
        L = ctypes.CDLL(str(so))
        I, LG, U64 = ctypes.c_int, ctypes.c_long, ctypes.c_uint64
        L.x_run.restype, L.x_run.argtypes = LG, [P, I, I, P, I, LG, I]
        L.x_cut.restype, L.x_cut.argtypes = I, [P, I, I, I, I, P]
        L.x_epoch.restype = LG
        L.x_epoch.argtypes = [P, P, I, P, P, P, P, P, P, LG, I, I, I, I, I]
        L.x_screen.restype = I
        L.x_screen.argtypes = [P, I, P, I, I, P, I, I, I, U64, LG, I, I, I, I, I, I, I, I, P]
        L.x_match.restype = None
        L.x_match.argtypes = [P, P, I, P, I, I, I, I, P]
        _LIB = L
    return _LIB


def u8(x) -> np.ndarray:
    return np.ascontiguousarray(x, dtype=np.uint8)


def cut(t, marker: int = MARKER, lmin: int = LMIN, lmax: int = LMAX) -> np.ndarray:
    t = u8(t)
    out = np.zeros(len(t) // lmin + 2, np.int32)
    k = lib().x_cut(t.ctypes.data, len(t), marker, lmin, lmax, out.ctypes.data)
    return out[:k].copy()


def split(buf, lens) -> list[np.ndarray]:
    return np.split(buf, np.cumsum(lens)[:-1]) if len(lens) else []


def run_pair(a, b, c=None, libmode: str = "neighbour", steps: int = STEPS) -> tuple[list[np.ndarray], int]:
    """One interaction: a ++ b run with library c (libmode neighbour). Returns (pieces, steps)."""
    a, b = u8(a), u8(b)
    t = u8(np.concatenate([a, b]))
    cc = u8(c if c is not None else np.zeros(1, np.uint8))
    st = lib().x_run(t.ctypes.data, len(a), len(b), cc.ctypes.data, len(cc) if c is not None else 0, steps,
                     LIBMODES[libmode])
    return split(t, cut(t)), int(st)


def pad(code: bytes, length: int, rng=None, fill: int | None = 0x80) -> np.ndarray:
    """code + filler (no-op bytes, never the marker) + marker, `length` bytes in all."""
    k = length - len(code) - 1
    if k < 0:
        raise ValueError("code too long")
    f = (np.full(k, fill, np.uint8) if fill is not None
         else NONOP_NZ[(rng or np.random.default_rng(0)).integers(0, len(NONOP_NZ), k)])
    return np.concatenate([np.frombuffer(code, np.uint8), f, [MARKER]]).astype(np.uint8)


COPIER = b"[.>}]"


def hand_copier(length: int = 6, rng=None, fill: int | None = 0x80) -> np.ndarray:
    return pad(COPIER, length, rng, fill)


class Soup:
    """BFF-X soup. `buf` holds the programs back to back, `lens` their lengths. The cut constants are class attributes
    so that a fixed-length variant (scripts/bffxf.py, E-84) can reuse the epoch; their defaults are BFF-X's."""

    MARKER, LMIN, LMAX = MARKER, LMIN, LMAX

    def __init__(self, w: int = W, seed: int = 0, libmode: str = "neighbour", mode: str = "bff",
                 mutation: float = MUT, steps: int = STEPS, buf=None, lens=None, rng=None):
        self.libmode, self.mode, self.mutation, self.steps = libmode, mode, mutation, steps
        self.rng = rng if rng is not None else np.random.default_rng(seed)
        if buf is None:
            buf = self.rng.integers(0, 256, w, dtype=np.uint8)
            lens = cut(buf)
        self.buf = u8(buf).copy()
        self.lens = np.ascontiguousarray(lens, dtype=np.int32).copy()
        assert int(self.lens.sum()) == len(self.buf)
        self.epochs = 0
        self.last_steps = 0
        self.origin = None

    @classmethod
    def from_programs(cls, progs, **kw):
        progs = [u8(p) for p in progs]
        return cls(buf=np.concatenate(progs), lens=np.array([len(p) for p in progs], np.int32), **kw)

    @property
    def n(self) -> int:
        return len(self.lens)

    def programs(self) -> list[np.ndarray]:
        return split(self.buf, self.lens)

    def epoch(self) -> int:
        N = self.n
        perm = self.rng.permutation(N).astype(np.int32)
        libidx = (self.rng.integers(0, N, max(1, N // 2)).astype(np.int32) if self.libmode == "neighbour"
                  else np.zeros(1, np.int32))
        dst = np.empty_like(self.buf)
        cap = len(self.buf) // self.LMIN + 2
        nl, org = np.empty(cap, np.int32), np.empty(cap, np.int32)
        nout = ctypes.c_int(0)
        self.last_steps = int(lib().x_epoch(self.buf.ctypes.data, self.lens.ctypes.data, N, perm.ctypes.data,
                                            libidx.ctypes.data, dst.ctypes.data, nl.ctypes.data, org.ctypes.data,
                                            ctypes.byref(nout), self.steps, MODES[self.mode],
                                            LIBMODES[self.libmode], self.MARKER, self.LMIN, self.LMAX))
        k = nout.value
        self.buf, self.lens, self.origin = dst, nl[:k].copy(), org[:k].copy()
        if self.mutation > 0:
            m = self.rng.binomial(self.buf.size, self.mutation)
            idx = self.rng.integers(0, self.buf.size, m)
            self.buf[idx] = self.rng.integers(0, 256, m, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps

    def state(self) -> dict:
        return {"buf": self.buf.copy(), "lens": self.lens.copy(), "rng": self.rng.bit_generator.state,
                "epochs": self.epochs, "libmode": self.libmode}


def restore(st: dict, **kw) -> Soup:
    rng = np.random.default_rng()
    rng.bit_generator.state = st["rng"]
    s = Soup(buf=st["buf"], lens=st["lens"], rng=rng, libmode=kw.pop("libmode", st.get("libmode", "neighbour")),
             **kw)
    s.epochs = int(st["epochs"])
    return s


def screen(x, seed: int, trials: int = 4, host_b=None, host_c=None, lp: int = LMAX, lc: int = LMAX,
           libmode: str = "neighbour", mode: str = "bff", tol: int = TOL, thr: int = THR,
           opmin: int = OPMIN) -> tuple[int, int]:
    """x runs first against a partner (host_b, or lp random bytes) with a library (host_c, or lc random bytes; used
    by libmode neighbour). Returns (trials with >= 1 copy of x after the first piece, total copies)."""
    x = u8(x)
    hb = u8(host_b) if host_b is not None else None
    hc = u8(host_c) if host_c is not None else None
    c = ctypes.c_int(0)
    h = lib().x_screen(x.ctypes.data, len(x), hb.ctypes.data if hb is not None else None,
                       len(hb) if hb is not None else 0, lp, hc.ctypes.data if hc is not None else None,
                       len(hc) if hc is not None else 0, lc, trials, seed & (2 ** 64 - 1), STEPS,
                       LIBMODES[libmode], MODES[mode], MARKER, LMIN, LMAX, tol, thr, opmin, ctypes.byref(c))
    return int(h), int(c.value)


def is_copier(x, seed: int, partners: int = 4, libmode: str = "neighbour", **kw) -> bool:
    """Self-copier: copies itself into every one of `partners` random LMAX-byte partners with random libraries
    (snapshot mode: the random partner is also the library)."""
    return screen(x, seed, partners, libmode=libmode, **kw)[0] == partners


def match(buf, lens, x, tol: int = TOL, thr: int = THR, opmin: int = OPMIN) -> np.ndarray:
    x = u8(x)
    out = np.zeros(len(lens), np.int32)
    lib().x_match(u8(buf).ctypes.data, np.ascontiguousarray(lens, dtype=np.int32).ctypes.data, len(lens),
                  x.ctypes.data, len(x), tol, thr, opmin, out.ctypes.data)
    return out


def members(buf, lens, x, **kw) -> np.ndarray:
    return match(buf, lens, x, **kw) >= 0


def top_distinct(s: Soup, k: int = 40) -> list[tuple[bytes, int]]:
    return Counter(map(bytes, s.programs())).most_common(k)
