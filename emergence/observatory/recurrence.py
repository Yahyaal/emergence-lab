"""Exact recurrence detection: has the whole universe returned to an earlier state,
possibly shifted (a translating cycle, e.g. a lone glider on the torus)?

Exact recurrence uses a cryptographic hash of the state. Translation-invariant
recurrence uses the magnitude of the 2D Fourier transform (invariant to
cyclic shifts) as a candidate filter, then verifies the shift exactly.
"""
from __future__ import annotations

import hashlib

import numpy as np


def _h(b: bytes) -> bytes:
    return hashlib.blake2b(b, digest_size=12).digest()


class RecurrenceDetector:
    def __init__(self) -> None:
        self.exact: dict[bytes, int] = {}
        self.shifted: dict[bytes, tuple[int, np.ndarray]] = {}
        self.result: dict | None = None

    def update(self, t: int, state: np.ndarray) -> None:
        if self.result is not None:
            return
        key = _h(state.tobytes())
        if key in self.exact:
            t0 = self.exact[key]
            self.result = {"period": t - t0, "transient": t0, "shift": (0, 0)}
            return
        self.exact[key] = t
        mag = np.abs(np.fft.rfft2(state.astype(np.float64)))
        tkey = _h(np.round(mag, 3).tobytes())
        if tkey in self.shifted:
            t0, prev = self.shifted[tkey]
            shift = _find_shift(prev, state)
            if shift is not None:
                self.result = {"period": t - t0, "transient": t0, "shift": shift}
                return
        self.shifted[tkey] = (t, state.copy())


def _find_shift(prev: np.ndarray, cur: np.ndarray) -> tuple[int, int] | None:
    a = prev.astype(np.float64)
    b = cur.astype(np.float64)
    corr = np.fft.irfft2(np.conj(np.fft.rfft2(a)) * np.fft.rfft2(b), s=a.shape)
    dr, dc = np.unravel_index(int(np.argmax(corr)), corr.shape)
    if np.array_equal(np.roll(prev, (dr, dc), axis=(0, 1)), cur):
        h, w = cur.shape
        dr = dr - h if dr > h // 2 else dr
        dc = dc - w if dc > w // 2 else dc
        return int(dr), int(dc)
    return None
