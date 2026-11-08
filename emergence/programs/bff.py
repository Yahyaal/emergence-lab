"""Program soups: BFF (Agüera y Arcas et al. 2024, "Computational Life"), Track D route 5.

A soup is N programs of L bytes (default 64), all random at the start. Each epoch the
programs are paired at random; each pair's tape (A followed by B, 2L bytes) is run by the BFF
interpreter (bff.c; the program can read and write the whole tape, including its partner),
and the two halves are written back. Then every byte mutates to a random value with
probability `mutation` (background noise). Nothing in the rule rewards copying: if
self-replicators appear, they come from the soup's own dynamics.

The interpreter is C (compiled with the system C compiler on first use and cached in
~/.cache/emergence-lab); `run_py` is a pure-Python reference with identical semantics, used
by the tests to check the C code.

Modes (controls): "bff" (the rule), "noexec" (pairing and mutation only, nothing runs:
negative), "copyall" (each pair's first program is copied over the second, whatever it is:
every program "replicates", the analogue of Fredkin's rule; deceptive).
"""
from __future__ import annotations

import ctypes
import hashlib
import lzma
import os
import subprocess
import zlib
from collections import Counter
from pathlib import Path

import numpy as np

MODES = {"bff": 0, "noexec": 1, "copyall": 2}
OPS = set(b"<>{}-+.,[]")
_SRC = Path(__file__).with_name("bff.c")
_LIB = None


def _lib():
    global _LIB
    if _LIB is None:
        src = _SRC.read_bytes()
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "emergence-lab"
        cache.mkdir(parents=True, exist_ok=True)
        so = cache / f"bff-{hashlib.sha1(src).hexdigest()[:12]}.so"
        if not so.exists():
            tmp = so.with_suffix(f".{os.getpid()}.tmp")
            subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(_SRC)], check=True)
            os.replace(tmp, so)
        lib = ctypes.CDLL(str(so))
        lib.bff_run.restype = ctypes.c_long
        lib.bff_run.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long]
        lib.bff_epoch.restype = ctypes.c_long
        lib.bff_epoch.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_long,
                                  ctypes.c_int]
        _LIB = lib
    return _LIB


def run(tape: np.ndarray, max_steps: int = 8192) -> tuple[np.ndarray, int]:
    """Run one tape (uint8) in C; returns (new tape, steps)."""
    t = np.ascontiguousarray(tape, dtype=np.uint8).copy()
    steps = _lib().bff_run(t.ctypes.data, len(t), max_steps)
    return t, int(steps)


def run_py(tape, max_steps: int = 8192) -> tuple[np.ndarray, int]:
    """Pure-Python reference interpreter (same semantics as bff.c)."""
    t = bytearray(bytes(np.asarray(tape, dtype=np.uint8)))
    n = len(t)
    ip = h0 = h1 = steps = 0
    while 0 <= ip < n and steps < max_steps:
        c = t[ip]
        if c == 60: h0 = (h0 - 1) % n
        elif c == 62: h0 = (h0 + 1) % n
        elif c == 123: h1 = (h1 - 1) % n
        elif c == 125: h1 = (h1 + 1) % n
        elif c == 45: t[h0] = (t[h0] - 1) % 256
        elif c == 43: t[h0] = (t[h0] + 1) % 256
        elif c == 46: t[h1] = t[h0]
        elif c == 44: t[h0] = t[h1]
        elif c == 91 and t[h0] == 0:
            d, j = 1, ip + 1
            while j < n:
                d += (t[j] == 91) - (t[j] == 93)
                if d == 0:
                    break
                j += 1
            if j >= n:
                return np.frombuffer(bytes(t), np.uint8).copy(), steps + 1
            ip = j
        elif c == 93 and t[h0] != 0:
            d, j = 1, ip - 1
            while j >= 0:
                d += (t[j] == 93) - (t[j] == 91)
                if d == 0:
                    break
                j -= 1
            if j < 0:
                return np.frombuffer(bytes(t), np.uint8).copy(), steps + 1
            ip = j
        ip += 1
        steps += 1
    return np.frombuffer(bytes(t), np.uint8).copy(), steps


def interact(a: np.ndarray, b: np.ndarray, max_steps: int = 8192) -> tuple[np.ndarray, np.ndarray]:
    """One BFF interaction: run a + b and split."""
    t, _ = run(np.concatenate([a, b]), max_steps)
    return t[:len(a)], t[len(a):]


def _replicator() -> np.ndarray:
    """A hand-written 64-byte self-replicator (positive control). When it runs first in a pair:
    head0 -> counter cell C (64); loop [}->+<] moves head1 to 64 while moving C into D; the
    restore loop moves D back to C (D rests at 1, so the program has no zero byte); then
    [.>}] copies tape[i] to tape[i + 64] until the step limit (it never meets a zero), so the
    partner becomes an exact copy and the original is unchanged."""
    code = b">@\x01[}->+<]>-[-<+>]+<<[.>}]"
    return np.frombuffer(code + b"\x80" * (64 - len(code)), np.uint8).copy()


REPLICATOR = _replicator()


class Soup:
    """N programs of L bytes; `epoch()` pairs, runs and mutates (see module docstring)."""

    def __init__(self, n: int = 2 ** 14, length: int = 64, mutation: float = 0.00024, max_steps: int = 8192,
                 mode: str = "bff", seed: int = 0, programs: np.ndarray | None = None):
        if n % 2 or mode not in MODES:
            raise ValueError("n must be even and mode one of " + ", ".join(MODES))
        self.n, self.length, self.mutation, self.max_steps, self.mode = n, length, mutation, max_steps, mode
        self.rng = np.random.default_rng(seed)
        self.programs = (np.ascontiguousarray(programs, dtype=np.uint8).copy() if programs is not None
                         else self.rng.integers(0, 256, (n, length), dtype=np.uint8))
        self.epochs = 0
        self.last_steps = 0

    def epoch(self) -> int:
        pairs = self.rng.permutation(self.n).astype(np.int32)
        self.last_steps = int(_lib().bff_epoch(self.programs.ctypes.data, self.length, pairs.ctypes.data,
                                               self.n // 2, self.max_steps, MODES[self.mode]))
        if self.mutation > 0:
            k = self.rng.binomial(self.programs.size, self.mutation)
            idx = self.rng.integers(0, self.programs.size, k)  # repeats are rare and harmless
            self.programs.reshape(-1)[idx] = self.rng.integers(0, 256, k, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps


def high_order_entropy(programs: np.ndarray) -> float:
    """Shannon entropy of the byte histogram minus the compressed size (bits per byte, zlib
    level 9): about 0 for random soups, rising when the soup fills with repeated code (the
    paper's "state transition" signal; it uses brotli, we use zlib)."""
    data = np.ascontiguousarray(programs).tobytes()
    p = np.bincount(np.frombuffer(data, np.uint8), minlength=256) / len(data)
    h0 = float(-(p[p > 0] * np.log2(p[p > 0])).sum())
    return h0 - 8 * len(zlib.compress(data, 9)) / len(data)


def ops_fraction(programs: np.ndarray) -> float:
    """Share of bytes that are instructions (10 of 256 values: 3.9% at random)."""
    return float(np.isin(programs, np.frombuffer(bytes(sorted(OPS)), np.uint8)).mean())


def top_programs(programs: np.ndarray, k: int = 5) -> list[tuple[bytes, int]]:
    """The k most common exact programs and their counts."""
    return Counter(map(bytes, programs)).most_common(k)


def compressed_ratio(programs: np.ndarray) -> float:
    data = np.ascontiguousarray(programs).tobytes()
    return len(lzma.compress(data, preset=1)) / len(data)
