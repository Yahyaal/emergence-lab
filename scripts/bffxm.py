"""E-85 (D-078): BFF-X with a minimum body for running one's own code ("BFF-XM"), on E-83's demes.

The rule is BFF-XR deme64 (scripts/bffxr.py, D-074: BFF-X with pairs and borrowed code drawn within demes of 64
programs on a ring, pieces written back in place) with ONE change, in the interpreter (scripts/bffxm.c): **a program
shorter than XMIN = 32 bytes has no code of its own.** When it runs first, the instruction pointer starts in the
borrowed code C instead of at its own first byte; the heads start where they always do. Programs of 32 bytes or
more run exactly as in BFF-X. Nothing else changes (byte budget 2^20, programs of 4 to 128 bytes cut after the
marker `!`, heads halt at the tape ends, step limit 8192, mutation 0.00024).

Consequences, by construction: the shortest self-copier (host) has 32 bytes (the 6-byte `[.>}]!` padded with
filler); a parasite (a program that falls into a host's copy loop) can be as short as 4 bytes and leaves about eight
times as many copies in a partner as a 32-byte host; a partner check (`\\x01-[]+`, 5 bytes) fits inside the
host's 32 bytes, so a resistant host need not be longer than a plain one.

This module re-loads the E-82/E-83 Python modules (`bffx`, `bffx_assay`, `bffxr`, `bffxr_assay`) as separate module
objects bound to the BFF-XM interpreter, so every E-82/E-83 instrument runs unchanged under the new rule while the
original modules (and their compiled library) stay untouched in the same process:

    import bffxm as M
    M.X.Soup, M.X.screen, M.X.is_copier ...   (bffx API under BFF-XM)
    M.R.make("deme64", ...)                   (bffxr geometry under BFF-XM)
    M.A.parasite_test, M.A.q_pair, M.A.timeshift    (bffx_assay under BFF-XM)
    M.RA.compete, M.RA.timeshift_w            (bffxr_assay under BFF-XM; its DESIGNED table is replaced below)
"""
from __future__ import annotations

import ctypes
import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import bffx as _bffx  # noqa: E402  (the original, for the xmin = 0 equivalence control)

XMIN = 32
TAILMIN = 32          # D-080 (revised rule, J-105); 0 gives the first BFF-XM rule of J-104 (D-078)
_LIBM = None


def _load_lib():
    src = HERE / "bffxm.c"
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "emergence-lab"
    cache.mkdir(parents=True, exist_ok=True)
    so = cache / f"bffxm-{hashlib.sha1(src.read_bytes()).hexdigest()[:12]}.so"
    if not so.exists():
        tmp = so.with_suffix(f".{os.getpid()}.tmp")
        subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
        os.replace(tmp, so)
    L = ctypes.CDLL(str(so))
    P, I, LG, U64 = ctypes.c_void_p, ctypes.c_int, ctypes.c_long, ctypes.c_uint64
    L.x_run.restype, L.x_run.argtypes = LG, [P, I, I, P, I, LG, I]
    L.x_cut.restype, L.x_cut.argtypes = I, [P, I, I, I, I, P]
    L.x_epoch.restype = LG
    L.x_epoch.argtypes = [P, P, I, P, P, P, P, P, P, LG, I, I, I, I, I]
    L.x_screen.restype = I
    L.x_screen.argtypes = [P, I, P, I, I, P, I, I, I, U64, LG, I, I, I, I, I, I, I, I, P]
    L.x_match.restype = None
    L.x_match.argtypes = [P, P, I, P, I, I, I, I, P]
    L.x_set_xmin.restype, L.x_set_xmin.argtypes = None, [I]
    L.x_get_xmin.restype, L.x_get_xmin.argtypes = I, []
    L.x_set_tailmin.restype, L.x_set_tailmin.argtypes = None, [I]
    L.x_get_tailmin.restype, L.x_get_tailmin.argtypes = I, []
    L.x_set_xmin(XMIN)
    L.x_set_tailmin(TAILMIN)
    return L


def lib():
    global _LIBM
    if _LIBM is None:
        _LIBM = _load_lib()
    return _LIBM


def set_xmin(v: int) -> None:
    """Change the interpreter's minimum body (controls only; the E-85 rule is XMIN = 32)."""
    lib().x_set_xmin(int(v))


def set_tailmin(v: int) -> None:
    """D-080 tail-merge threshold (0: the J-104 rule, D-078)."""
    lib().x_set_tailmin(int(v))


def get_tailmin() -> int:
    return int(lib().x_get_tailmin())


def get_xmin() -> int:
    return int(lib().x_get_xmin())


def _clone(name: str, path: Path, deps: dict):
    """Load `path` as a new module `name`, with the modules in `deps` standing in for their names during import."""
    saved = {k: sys.modules.get(k) for k in deps}
    try:
        sys.modules.update(deps)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return mod


X = _clone("bffxm_x", HERE / "bffx.py", {})
X.lib = lib                                     # every X function and X.Soup.epoch look `lib` up at call time
A = _clone("bffxm_a", HERE / "bffx_assay.py", {"bffx": X})
R = _clone("bffxm_r", HERE / "bffxr.py", {"bffx": X})
RA = _clone("bffxm_ra", HERE / "bffxr_assay.py", {"bffx": X, "bffx_assay": A, "bffxr": R})


# ---- designed programs (all hosts XMIN bytes long, so a lock costs no length) -------------------------
def host(length: int = XMIN) -> np.ndarray:
    """Plain host H: [.>}] + filler + marker, `length` bytes."""
    return X.hand_copier(length)


def resistant_host(key: int = 1, length: int = XMIN) -> np.ndarray:
    """R (D-080): copies its executor only if the executor's first byte is `key`, WITHOUT changing a refused caller:
    byte 0 = key, '-' x key, then '[+<]' (on a mismatch: restore the byte, then '<' at head0 = 0 halts the run),
    '+' x key (restore on a match), then the copy loop. Run by itself, byte 0 is its own key, so it copies itself."""
    return X.pad(bytes([key]) + b"-" * key + b"[+<]" + b"+" * key + b"[.>}]", length)


def resistant_host_rewriting(key: int = 1, length: int = XMIN) -> np.ndarray:
    """E-82's R ('-[]+' trap), used in J-104: a refused caller is left with its first byte decremented."""
    return A.resistant_host(key, length)


def sham_host(key: int = 1, length: int = XMIN) -> np.ndarray:
    """S: R with '[+<]' replaced by four filler bytes (same length, same bytes elsewhere; copies everyone)."""
    r = resistant_host(key, length).copy()
    i = 1 + key
    assert bytes(r[i:i + 4]) == b"[+<]"
    r[i:i + 4] = 0x80
    return r


def parasite(length: int = 4, key: int | None = None) -> np.ndarray:
    return A.parasite(length, key)


DESIGNED = {"H": host, "R": resistant_host, "S": sham_host, "P": lambda: parasite(4), "Pk": lambda: parasite(4, 1),
            "H6": lambda: X.hand_copier(6)}
RA.DESIGNED = DESIGNED                          # RA.start / RA.compete use these


def make(geometry: str = "deme64", **kw):
    return R.make(geometry, **kw)
