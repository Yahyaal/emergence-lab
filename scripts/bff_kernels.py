"""E-55 copy-kernel census (docs/data/e55-preregistration.md): why do emergent BFF replicators copy backwards?

Every kernel of 1..6 instructions, at the start of a 64-byte program padded with random non-instruction filler,
is run first in a pair with random partners, under the standard rule (head1 starts at 0) and a counterfactual
(head1 starts at byte 64). Counts forward and reverse copiers. Plus controls, a filler sensitivity run, a
mechanism trace of the 9 E-42 replicators and (with --e54) the orientation of E-54's verified replicators.

    python scripts/bff_kernels.py --workers 2 --out docs/data/experiments/2026-11-08-e55-kernels.json
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import subprocess
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from emergence.programs import bff as B

L, STEPS, THR, KMAX, CHUNK = 64, 8192, 60, 6, 100_000
MAXSHIFT = 16  # classify_shift default; E-68 scales L, THR and MAXSHIFT together with set_length()
OPS = np.frombuffer(b"<>{}-+.,[]", np.uint8)
NONOP = np.array([v for v in range(256) if v not in set(OPS.tolist())], np.uint8)  # includes 0
NONOP_NZ = NONOP[NONOP != 0]
E42 = "docs/data/experiments/2026-11-08-e42-bff-heredity.json"
_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        src = Path(__file__).with_name("bff_kernels.c")
        cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "emergence-lab"
        cache.mkdir(parents=True, exist_ok=True)
        so = cache / f"bffk-{hashlib.sha1(src.read_bytes()).hexdigest()[:12]}.so"
        if not so.exists():
            tmp = so.with_suffix(f".{os.getpid()}.tmp")
            subprocess.run(["cc", "-O3", "-shared", "-fPIC", "-o", str(tmp), str(src)], check=True)
            os.replace(tmp, so)
        _LIB = ctypes.CDLL(str(so))
        _LIB.classify.restype = None
        _LIB.classify.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_uint64, ctypes.c_long, ctypes.c_int, ctypes.c_void_p]
        _LIB.epoch_h.restype = ctypes.c_long
        _LIB.epoch_h.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_long, ctypes.c_int]
        _LIB.run_tape.restype = ctypes.c_long
        _LIB.run_tape.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long, ctypes.c_int]
        _LIB.classify_shift.restype = None
        _LIB.classify_shift.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_uint64, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_void_p,
                                        ctypes.c_void_p]
        _LIB.classify_fid.restype = None
        _LIB.classify_fid.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_uint64, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_void_p, ctypes.c_void_p]
    return _LIB


def set_length(length: int) -> None:
    """E-68: program length L (tape 2L). THR = L - L // 16 and MAXSHIFT = L // 4, so L = 64 gives the defaults
    (60, 16) used by every earlier experiment. Module-global: call it in each worker before classifying."""
    global L, THR, MAXSHIFT
    if not 16 <= length <= 240 or length % 16:
        raise ValueError("length must be a multiple of 16 in 16..240 (h1start packs h1 into 8 bits)")
    L, THR, MAXSHIFT = length, length - length // 16, length // 4


def classify(P: np.ndarray, h1start: int, partners: int, seed: int) -> np.ndarray:
    P = np.ascontiguousarray(P, dtype=np.uint8)
    out = np.zeros(len(P), np.uint8)
    lib().classify(P.ctypes.data, len(P), L, h1start, partners, seed, STEPS, THR, out.ctypes.data)
    return out


def classify_shift(P: np.ndarray, h1start: int, partners: int, seed: int, maxshift: int | None = None):
    """E-61: shift-aware classify (copies may sit up to `maxshift` bytes off byte L). Returns (codes, shifts)."""
    maxshift = MAXSHIFT if maxshift is None else maxshift
    P = np.ascontiguousarray(P, dtype=np.uint8)
    out, sh = np.zeros(len(P), np.uint8), np.zeros(len(P), np.int8)
    lib().classify_shift(P.ctypes.data, len(P), L, h1start, partners, seed, STEPS, THR, maxshift,
                         out.ctypes.data, sh.ctypes.data)
    return out, sh


def classify_fid(P: np.ndarray, h1start: int, partners: int, seed: int, thr: int | None = None, opmin: int = 75,
                 maxshift: int | None = None):
    """E-73 (D-053): classify_shift plus an instruction-fidelity guard (copy must reproduce >= opmin % of the
    program's instruction bytes). thr = THR and opmin = 0 reproduce classify_shift exactly."""
    thr = THR if thr is None else thr
    maxshift = MAXSHIFT if maxshift is None else maxshift
    P = np.ascontiguousarray(P, dtype=np.uint8)
    out, sh = np.zeros(len(P), np.uint8), np.zeros(len(P), np.int8)
    lib().classify_fid(P.ctypes.data, len(P), L, h1start, partners, seed, STEPS, thr, maxshift, opmin,
                       out.ctypes.data, sh.ctypes.data)
    return out, sh


def label(c: int) -> str:
    return ["none", "forward", "reverse", "both"][int(c)]


def programs(k: int, lo: int, hi: int, zero_filler: bool) -> np.ndarray:
    idx = np.arange(lo, hi)
    digits = (idx[:, None] // (10 ** np.arange(k - 1, -1, -1))[None, :]) % 10
    rng = np.random.default_rng([55, k, lo, int(zero_filler)])
    pool = NONOP if zero_filler else NONOP_NZ
    P = pool[rng.integers(0, len(pool), (hi - lo, L))]
    P[:, :k] = OPS[digits]
    return P


def chunk(arg):
    k, lo, hi, zf = arg
    P = programs(k, lo, hi, zf)
    res = {}
    for name, h1 in (("standard", 0), ("counterfactual", L)):
        scr = classify(P, h1, 1, 0x5501 + k)
        hit = np.nonzero(scr)[0]
        conf = classify(P[hit], h1, 4, 0x5502 + k) if len(hit) else np.zeros(0, np.uint8)
        res[name] = {"screen": int(len(hit)),
                     "hits": [(bytes(P[i, :k]).decode(), label(c)) for i, c in zip(hit, conf) if c]}
    return k, zf, res


def trace(x: np.ndarray, partner: np.ndarray) -> dict:
    """Instrumented reference interpreter (same semantics as bff.c): writes into the partner half."""
    t = bytearray(bytes(np.concatenate([x, partner])))
    n = len(t)
    ip = h0 = h1 = steps = 0
    writes, wrapped_before_first = [], None  # wrapped: the writing head went below byte 0 before its first partner write
    h1_wrapped = h0_wrapped = False
    while 0 <= ip < n and steps < STEPS:
        c = t[ip]
        if c == 60:
            if h0 == 0: h0_wrapped = True
            h0 = (h0 - 1) % n
        elif c == 62: h0 = (h0 + 1) % n
        elif c == 123:
            if h1 == 0: h1_wrapped = True
            h1 = (h1 - 1) % n
        elif c == 125: h1 = (h1 + 1) % n
        elif c == 45: t[h0] = (t[h0] - 1) % 256
        elif c == 43: t[h0] = (t[h0] + 1) % 256
        elif c == 46:
            t[h1] = t[h0]
            if h1 >= L: writes.append(("h1", h1)); wrapped_before_first = h1_wrapped if wrapped_before_first is None else wrapped_before_first
        elif c == 44:
            t[h0] = t[h1]
            if h0 >= L: writes.append(("h0", h0)); wrapped_before_first = h0_wrapped if wrapped_before_first is None else wrapped_before_first
        elif c == 91 and t[h0] == 0:
            d, j = 1, ip + 1
            while j < n:
                if t[j] == 91: d += 1
                elif t[j] == 93:
                    d -= 1
                    if d == 0: break
                j += 1
            if j >= n: break
            ip = j
        elif c == 93 and t[h0] != 0:
            d, j = 1, ip - 1
            while j >= 0:
                if t[j] == 93: d += 1
                elif t[j] == 91:
                    d -= 1
                    if d == 0: break
                j -= 1
            if j < 0: break
            ip = j
        ip += 1
        steps += 1
    down = sum(1 for a, b in zip(writes, writes[1:]) if a[0] == b[0] and (b[1] - a[1]) % n == n - 1)
    up = sum(1 for a, b in zip(writes, writes[1:]) if a[0] == b[0] and (b[1] - a[1]) % n == 1)
    heads = sorted({w[0] for w in writes})
    return {"partner_writes": len(writes), "down": down, "up": up, "heads": heads,
            "head_wrapped_before_first_write": wrapped_before_first}


def controls(rng) -> dict:
    out = {}
    out["handwritten_replicator"] = label(classify(B.REPLICATOR[None], 0, 4, 1)[0])
    E = [np.frombuffer(bytes.fromhex(r["program"]), np.uint8).copy() for r in json.load(open(E42))["results"]]
    out["e42_emergent"] = [label(c) for c in classify(np.array(E), 0, 4, 2)]
    R = rng.integers(0, 256, (1000, L), dtype=np.uint8)
    out["random_1000"] = {label(c): int(n) for c, n in zip(*np.unique(classify(R, 0, 4, 3), return_counts=True))}
    f = NONOP_NZ[rng.integers(0, len(NONOP_NZ), L)]
    const = f.copy(); const[:4] = np.frombuffer(b"[{.]", np.uint8)  # writes byte 0 ('[') downward over everything
    out["deceptive_constant_writer"] = label(classify(const[None], 0, 4, 4)[0])
    half = np.frombuffer(b"[{.>]", np.uint8)
    pal = f.copy(); pal[:32] = f[:32]; pal[32:] = f[:32][::-1]; pal[:5] = half; pal[-5:] = half[::-1]
    out["deceptive_palindrome_copier"] = label(classify(pal[None], 0, 4, 5)[0])
    out["e42_trace"] = []
    for i, x in enumerate(E):
        T = [trace(x, rng.integers(0, 256, L, dtype=np.uint8)) for _ in range(8)]
        out["e42_trace"].append({"index": i, "partner_writes": sum(t["partner_writes"] for t in T),
                                 "down": sum(t["down"] for t in T), "up": sum(t["up"] for t in T),
                                 "heads": sorted({h for t in T for h in t["heads"]}),
                                 "head_wrapped_before_first_write": [t["head_wrapped_before_first_write"] for t in T]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--kmax", type=int, default=KMAX)
    ap.add_argument("--out", required=True)
    ap.add_argument("--e54", default=None, help="E-54 analysis JSON: classify its verified replicators")
    a = ap.parse_args()
    t0 = time.time()
    rng = np.random.default_rng(550)
    summary = {"experiment": "E-55", "controls": controls(rng)}
    print(json.dumps(summary["controls"], indent=1), flush=True)
    jobs = [(k, lo, min(lo + CHUNK, 10 ** k), False) for k in range(1, a.kmax + 1) for lo in range(0, 10 ** k, CHUNK)]
    jobs += [(k, lo, min(lo + CHUNK, 10 ** k), True) for k in range(1, min(a.kmax, 5) + 1) for lo in range(0, 10 ** k, CHUNK)]
    census = {}
    with Pool(a.workers) as pool:
        for k, zf, res in pool.imap_unordered(chunk, jobs):
            key = f"{'zero' if zf else 'main'}-k{k}"
            c = census.setdefault(key, {p: {"screen": 0, "hits": []} for p in ("standard", "counterfactual")})
            for p in res:
                c[p]["screen"] += res[p]["screen"]; c[p]["hits"] += res[p]["hits"]
            print(key, {p: (res[p]["screen"], len(res[p]["hits"])) for p in res}, f"{time.time() - t0:.0f}s", flush=True)
    table = {}
    for key, c in sorted(census.items()):
        table[key] = {p: {lab: sum(1 for _, l in c[p]["hits"] if l == lab) for lab in ("forward", "reverse", "both")}
                      | {"screen": c[p]["screen"]} for p in c}
        for p in c:
            for lab in ("forward", "reverse", "both"):
                ex = sorted(h for h, l in c[p]["hits"] if l == lab)
                table[key][p][f"examples_{lab}"] = ex[:12]
    summary["census"] = table
    tot = {p: {lab: sum(table[f"main-k{k}"][p][lab] for k in range(1, a.kmax + 1)) for lab in ("forward", "reverse", "both")}
           for p in ("standard", "counterfactual")}
    short = {p: {lab: next((k for k in range(1, a.kmax + 1) if table[f"main-k{k}"][p][lab]), None)
                 for lab in ("forward", "reverse")} for p in ("standard", "counterfactual")}
    summary["totals_main"], summary["shortest_main"] = tot, short
    def ok(p, a_, b_):
        return tot[p][a_] >= 10 * max(tot[p][b_], 1) and short[p][a_] is not None and (short[p][b_] is None or short[p][a_] < short[p][b_])
    summary["primary"] = {"standard_reverse_dominates": ok("standard", "reverse", "forward"),
                          "counterfactual_forward_dominates": ok("counterfactual", "forward", "reverse")}
    summary["primary"]["pass"] = all(summary["primary"].values())
    if a.e54:
        d = json.load(open(a.e54))
        progs = sorted({r["program"] for r in d.get("results", d.get("invasions", [])) if "program" in r})
        X = np.array([np.frombuffer(bytes.fromhex(h), np.uint8) for h in progs]) if progs else np.zeros((0, L), np.uint8)
        labs = [label(c) for c in classify(X, 0, 4, 6)] if len(X) else []
        summary["e54_orientation"] = {"n": len(labs), **{lab: labs.count(lab) for lab in ("forward", "reverse", "both", "none")}}
    summary["seconds"] = round(time.time() - t0)
    json.dump(summary, open(a.out, "w"), indent=1)
    print(json.dumps({k: summary[k] for k in ("totals_main", "shortest_main", "primary")}, indent=1))
    print("E-55 DONE", flush=True)


if __name__ == "__main__":
    main()
