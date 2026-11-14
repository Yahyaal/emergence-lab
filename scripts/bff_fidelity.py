"""E-73 (D-053): validation of a looser copy test for BFF variant rules. `bff_kernels.classify_fid` = the shift-aware
copier test with a lower match threshold (thr of 64 bytes) plus an instruction-fidelity guard (the copy must
reproduce >= opmin % of the program's instruction bytes).

Controls (fixtures from scripts/bff_fidelity_fixtures.py, top-40 distinct programs of replayed soups):
  positive     sloppy replicators D-050 missed (E-72 v2 g57/g58, copies of 58-60/64 bytes); exact replicators
               (E-70 v1/v2/v3 at h1 = 64)
  negative     random programs; top-40 of soups with no replicators (standard BFF at round 2,000; E-71 v1/68 at
               2,000, where many programs copy part of themselves)
  deceptive    'filler smears': 60 bytes of one value plus a 4-instruction loop that writes that value across the
               partner, so the partner matches the program in 60/64 bytes without containing its instructions
  null         the negatives are top-40 selections, the same selection the jump criterion applies

    PYTHONPATH=scripts python scripts/bff_fidelity.py --out docs/data/experiments/2026-11-11-e73-fidelity.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_kernels as K  # noqa: E402
import bff_fidelity_fixtures as FX  # noqa: E402

THR, OPMIN = 58, 75
POS = ("sloppy_v2_g57", "sloppy_v2_g58", "exact_v1_h64", "exact_v2_h64", "exact_v3_h64")
NEG = ("null_v0_h0", "null_v1_h68")
SMEAR_KERNELS = (b"[.}]", b"[.{]", b"[,}]", b"[,{]", b"[.>]", b"[.<]", b"[,>]", b"[,<]")
SMEAR_FILL = (0x00, 0x41, 0xE9, 0x01)


def fixture(name: str) -> tuple[np.ndarray, int]:
    return np.load(Path(__file__).parent / "fixtures" / f"e73-{name}.npy"), FX.SOUPS[name][0]


def smears() -> np.ndarray:
    out = []
    for c in SMEAR_FILL:
        for k in SMEAR_KERNELS:
            for pos in (0, 60):
                P = np.full(64, c, np.uint8)
                P[pos:pos + 4] = np.frombuffer(k, np.uint8)
                out.append(P)
    return np.array(out)


def count(X, code, thr, opmin, seed=7301) -> int:
    c, _ = K.classify_fid(X, code, 4, seed, thr=thr, opmin=opmin)
    return int((c > 0).sum())


def controls(thr: int = THR, opmin: int = OPMIN) -> list[tuple[str, bool, str]]:
    checks = []
    codes = sorted({FX.SOUPS[n][0] for n in FX.SOUPS})
    # equivalence: thr 60, opmin 0 == classify_shift
    eq = True
    for n in FX.SOUPS:
        X, code = fixture(n)
        a = K.classify_shift(X, code, 4, 7301)
        b = K.classify_fid(X, code, 4, 7301, thr=60, opmin=0)
        eq &= bool((a[0] == b[0]).all() and (a[1] == b[1]).all())
    checks.append(("fidelity equivalence: thr 60, no guard == classify_shift on all fixtures", eq, ""))
    for n in POS:
        X, code = fixture(n)
        k, k60 = count(X, code, thr, opmin), count(X, code, 60, 0)
        checks.append((f"fidelity positive: {n} ({FX.SOUPS[n][3]}) -> >= 30/40 copiers", k >= 30,
                       f"{k}/40 (D-050 test: {k60}/40)"))
    rng = np.random.default_rng(73)
    R = rng.integers(0, 256, (200, 64), dtype=np.uint8)
    kr = max(count(R, c, thr, opmin) for c in codes)
    # not 0: in these languages a random program can hold a real 3-instruction copier (program 187 contains
    # `[ . ]`, a self-sufficient copier under v1/h64 that the old test counts too; J-075)
    checks.append(("fidelity negative: 200 random programs, every fixture rule -> <= 1% copiers", kr <= 2, f"max {kr}/200"))
    for n in NEG:
        X, code = fixture(n)
        k = count(X, code, thr, opmin)
        checks.append((f"fidelity null (top-40 selection): {n} ({FX.SOUPS[n][3]}) -> <= 1/40 copiers", k <= 1, f"{k}/40"))
    S = smears()
    ks = {c: count(S, c, thr, opmin) for c in codes}
    k60 = {c: count(S, c, 60, 0) for c in codes}
    checks.append((f"fidelity deceptive: {len(S)} filler smears x {len(codes)} rules -> 0 copiers", sum(ks.values()) == 0,
                   f"guarded {sum(ks.values())}; unguarded at thr 60 (D-050 test): {sum(k60.values())}"))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sweep = {}
    S = smears()
    for thr in (52, 54, 56, 57, 58, 59, 60):
        for opmin in (0, 50, 75, 100):
            row = {n: count(*fixture(n), thr, opmin) for n in FX.SOUPS}
            row["smears"] = sum(count(S, c, thr, opmin) for c in sorted({FX.SOUPS[n][0] for n in FX.SOUPS}))
            sweep[f"{thr}/{opmin}"] = row
            print(thr, opmin, row, flush=True)
    checks = controls()
    for name, ok, det in checks:
        print("PASS" if ok else "FAIL", name, "->", det)
    json.dump({"experiment": "E-73", "thr": THR, "opmin": OPMIN, "sweep": sweep,
               "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
               "fixtures": {n: v[3] for n, v in FX.SOUPS.items()}}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
