"""Program soups in a SUBLEQ family (E-75, D-054): the F-predictor test outside the BFF family.

Same soup as `bff.Soup` (N programs of L bytes, random pairing, the pair's tape A + B run by the interpreter,
background mutation), with a different language: one subtract-and-branch instruction, a program counter, no
heads and no no-ops (every byte is an operand). Semantics are in subleq.c; `run_py` is the pure-Python
reference with identical semantics, used by the tests.

A `Rule` packs six knobs: operands n (3 or 4), jump condition j, index-register step s, operand window W, write
offset o, and absolute addressing (the published SUBLEQ, Agüera y Arcas et al. 2024). `SUBLEQ` and `RSUBLEQ4`
are the two anchors: the paper's languages in this framework. Its text is partly garbled, so these are our
reading of them, and absolute SUBLEQ wraps data addresses mod N.

Hand-written replicators (positive controls) are at the bottom; `ZERO_SMEAR` is a deceptive control: a program
that zeroes its partner while being mostly zeros itself, so the partner matches it in 59 of 64 bytes without
anything being copied.
"""
from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from emergence.programs.bff import MODES, high_order_entropy  # noqa: F401  (re-exported for soups)

_SRC = Path(__file__).with_name("subleq.c")
_LIB = None
S_VALUES = (0, 1, 2, -1)
W_VALUES = (128, 64, 32, 16, 8)
J_NAMES = ("<=0", "<0", "==0", "always")


@dataclass(frozen=True)
class Rule:
    n: int = 4
    j: int = 0
    s: int = 0
    W: int = 128
    o: int = 0
    absolute: bool = False

    @property
    def code(self) -> int:
        if self.n not in (3, 4) or self.j not in range(4) or self.s not in S_VALUES or self.W not in W_VALUES \
                or not 0 <= self.o < 128:
            raise ValueError(f"bad rule {self}")
        return ((self.n == 4) | self.j << 1 | S_VALUES.index(self.s) << 3 | W_VALUES.index(self.W) << 5
                | self.o << 8 | int(self.absolute) << 15)

    @classmethod
    def from_code(cls, code: int) -> "Rule":
        return cls(n=4 if code & 1 else 3, j=(code >> 1) & 3, s=S_VALUES[(code >> 3) & 3],
                   W=W_VALUES[(code >> 5) & 7], o=(code >> 8) & 127, absolute=bool((code >> 15) & 1))

    def __str__(self) -> str:
        return (f"n{self.n} j{J_NAMES[self.j]} s{self.s:+d} W{self.W} o{self.o}" + (" abs" if self.absolute else ""))


SUBLEQ = Rule(n=3, j=0, s=0, W=128, o=0, absolute=True)
RSUBLEQ4 = Rule(n=4, j=0, s=0, W=128, o=0)


def _lib():
    global _LIB
    if _LIB is None:
        src = _SRC.read_bytes()
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "emergence-lab"
        cache.mkdir(parents=True, exist_ok=True)
        so = cache / f"subleq-{hashlib.sha1(src).hexdigest()[:12]}.so"
        if not so.exists():
            tmp = so.with_suffix(f".{os.getpid()}.tmp")
            subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(_SRC)], check=True)
            os.replace(tmp, so)
        lib = ctypes.CDLL(str(so))
        lib.sq_run.restype = ctypes.c_long
        lib.sq_run.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long, ctypes.c_int]
        lib.sq_epoch.restype = ctypes.c_long
        lib.sq_epoch.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_long,
                                 ctypes.c_int, ctypes.c_int]
        lib.sq_classify.restype = None
        lib.sq_classify.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_uint64, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                    ctypes.c_void_p, ctypes.c_void_p]
        _LIB = lib
    return _LIB


def _code(rule) -> int:
    return rule.code if isinstance(rule, Rule) else int(rule)


def run(tape: np.ndarray, rule, max_steps: int = 8192) -> tuple[np.ndarray, int]:
    t = np.ascontiguousarray(tape, dtype=np.uint8).copy()
    steps = _lib().sq_run(t.ctypes.data, len(t), max_steps, _code(rule))
    return t, int(steps)


def run_py(tape, rule, max_steps: int = 8192) -> tuple[np.ndarray, int]:
    """Pure-Python reference (same semantics as subleq.c)."""
    R = rule if isinstance(rule, Rule) else Rule.from_code(rule)
    t = bytearray(bytes(np.asarray(tape, dtype=np.uint8)))
    N = len(t)
    pc = reg = steps = 0
    while steps < max_steps:
        if pc < 0 or pc + R.n > N:
            break
        a, b, c = t[pc], t[pc + 1], t[pc + 2]
        d = t[pc + 3] if R.n == 4 else c
        if R.absolute:
            A, B = (a + R.o + reg) % N, (b + reg) % N
        else:
            A, B = (pc + a % R.W + R.o + reg) % N, (pc + b % R.W + reg) % N
        if R.n == 3:
            v = (t[A] - t[B]) % 256
        else:
            C = c % N if R.absolute else (pc + c % R.W) % N
            v = (t[B] - t[C]) % 256
        t[A] = v
        target = d if R.absolute else pc + (d - 256 if d > 127 else d)
        sv = v - 256 if v > 127 else v
        jump = (sv <= 0, sv < 0, sv == 0, True)[R.j]
        pc = target if jump else pc + R.n
        reg = (reg + R.s) % N
        steps += 1
    return np.frombuffer(bytes(t), np.uint8).copy(), steps


def classify(P: np.ndarray, rule, partners: int = 4, seed: int = 0, thr: int = 58, maxshift: int = 16,
             guard: bool = True, max_steps: int = 8192) -> tuple[np.ndarray, np.ndarray]:
    """Copy test (D-055, proposed): shift-aware match >= thr of L bytes with every partner, program half intact,
    and (guard) the first copy is itself a copier. Returns (orientation bits, shift) per program."""
    P = np.ascontiguousarray(np.atleast_2d(P), dtype=np.uint8)
    out = np.zeros(len(P), np.uint8)
    sh = np.zeros(len(P), np.int8)
    _lib().sq_classify(P.ctypes.data, len(P), P.shape[1], _code(rule), partners, seed & (2 ** 64 - 1), max_steps,
                       thr, maxshift, int(guard), out.ctypes.data, sh.ctypes.data)
    return out, sh


class Soup:
    """N programs of L bytes under a SUBLEQ-family rule; `epoch()` pairs, runs and mutates (as bff.Soup)."""

    def __init__(self, rule, n: int = 2 ** 14, length: int = 64, mutation: float = 0.00024, max_steps: int = 8192,
                 mode: str = "bff", seed: int = 0, programs: np.ndarray | None = None):
        if n % 2 or mode not in MODES:
            raise ValueError("n must be even and mode one of " + ", ".join(MODES))
        self.rule, self.code = rule, _code(rule)
        self.n, self.length, self.mutation, self.max_steps, self.mode = n, length, mutation, max_steps, mode
        self.rng = np.random.default_rng(seed)
        self.programs = (np.ascontiguousarray(programs, dtype=np.uint8).copy() if programs is not None
                         else self.rng.integers(0, 256, (n, length), dtype=np.uint8))
        self.epochs = 0
        self.last_steps = 0

    def epoch(self) -> int:
        pairs = self.rng.permutation(self.n).astype(np.int32)
        self.last_steps = int(_lib().sq_epoch(self.programs.ctypes.data, self.length, pairs.ctypes.data,
                                              self.n // 2, self.max_steps, MODES[self.mode], self.code))
        if self.mutation > 0:
            k = self.rng.binomial(self.programs.size, self.mutation)
            idx = self.rng.integers(0, self.programs.size, k)
            self.programs.reshape(-1)[idx] = self.rng.integers(0, 256, k, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps


def distinct_top(programs: np.ndarray, k: int = 40) -> np.ndarray:
    vals, counts = np.unique(programs, axis=0, return_counts=True)
    return vals[np.argsort(-counts, kind="stable")[:k]]


# --- hand-written replicators (positive controls) and a deceptive control --------------------------------
def _prog(kernel: bytes, fill: int = 0x80, at: int = 0, length: int = 64) -> np.ndarray:
    p = np.full(length, fill, np.uint8)
    p[at:at + len(kernel)] = np.frombuffer(kernel, np.uint8)
    return p


# n4 j=always s=+1 W128 o0: t[64 + r] = t[0 + r] - t[4]; jump to self. Byte 4 is 0, so the loop copies the
# program onto its partner (r = 0..63), then copies the copy back onto itself (no change), until the step limit.
F_FORWARD = (Rule(n=4, j=3, s=1, W=128, o=0), _prog(bytes([64, 0, 4, 0, 0])))
# n4 j=always s=-1: the same copying backwards, from byte 63 down (t[127 - r] = t[63 - r] - t[4]).
F_BACKWARD = (Rule(n=4, j=3, s=-1, W=128, o=0), _prog(bytes([127, 63, 4, 0, 0])))
# n4 j=always s=+1 W16 o64: narrow operands reach the partner only through the write offset (a band near 64).
F_BAND = (Rule(n=4, j=3, s=1, W=16, o=64), _prog(bytes([0, 0, 4, 0, 0])))
POSITIVES = {"forward": F_FORWARD, "backward": F_BACKWARD, "band": F_BAND}
# deceptive: b == c, so v = 0 is written over the partner; the program is 59 zeros, so the partner then
# matches it in 59 of 64 bytes, but the "copy" (all zeros) copies nothing.
ZERO_SMEAR = (Rule(n=4, j=3, s=1, W=128, o=0), _prog(bytes([64, 9, 9, 0, 0]), fill=0, at=0))
