"""E-75 phase 0 (docs/data/e75-design.md): controls for the SUBLEQ family and for the language-agnostic
inheritance test (D-055 proposed, `emergence/programs/inherit.py`). `controls()` is also run by pytest
(tests/test_programs.py) and by `emergence benchmark --probes`.

Fixtures (scripts/fixtures/e75-*.npy, top-40 distinct programs): `emergent-forward` = an unseeded soup under
n4/always/s+1 at round 100 (4,096 programs, seed 7), taken over by a 5-byte loop that the whole-program copy test
cannot see; `null-rsubleq4`, `null-subleq` = the two anchor rules at round 300 (seeds 8, 9). E-73's BFF fixtures
are reused for the cross-language check.

    PYTHONPATH=scripts python scripts/sq_phase0.py --out docs/data/experiments/2026-11-12-e75-phase0.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from emergence.programs import inherit as I  # noqa: E402
from emergence.programs import subleq as Q  # noqa: E402

FIX = Path(__file__).parent / "fixtures"


def sqrun(rule):
    return lambda t: Q.run(t, rule)[0]


def bffrun(code):
    import bff_kernels as K

    def f(t):
        t = np.ascontiguousarray(t, dtype=np.uint8).copy()
        K.lib().run_tape(t.ctypes.data, len(t), K.STEPS, code)
        return t
    return f


def fx(name: str) -> np.ndarray:
    return np.load(FIX / f"e75-{name}.npy")


def controls(full: bool = True) -> list[tuple[str, bool, str]]:
    out = []
    rng = np.random.default_rng(75)
    # 1 interpreter: C == Python reference over random rules (all knobs) and tapes
    bad = tot = 0
    for _ in range(300):
        R = Q.Rule(n=int(rng.choice([3, 4])), j=int(rng.integers(4)), s=int(rng.choice(Q.S_VALUES)),
                   W=int(rng.choice(Q.W_VALUES)), o=int(rng.integers(128)), absolute=bool(rng.random() < 0.1))
        t = rng.integers(0, 256, 128, dtype=np.uint8)
        a, sa = Q.run(t, R, 3000)
        b, sb = Q.run_py(t, R, 3000)
        tot += 1
        bad += int(sa != sb or (a != b).any())
    out.append(("subleq interpreter: C == Python reference on 300 random rules and tapes", bad == 0, f"{bad}/{tot} differ"))
    # 2 positives: hand-written replicators, both tests
    for name, (R, P) in Q.POSITIVES.items():
        inh = I.inherits(P, sqrun(R), np.random.default_rng(1))[0]
        wp = bool(Q.classify(P, R, seed=1)[0][0])
        out.append((f"subleq positive: hand-written {name} replicator ({R}) -> inherited and whole-program copier",
                    inh and wp, f"inheritance {inh}, whole-program {wp}"))
    # 3 deceptive: zero smear
    R, P = Q.ZERO_SMEAR
    inh = I.inherits(P, sqrun(R), np.random.default_rng(1))[0]
    ung = bool(Q.classify(P, R, seed=1, guard=False)[0][0])
    out.append(("subleq deceptive: zero smear (partner matches 59/64 bytes, nothing copied) -> rejected",
                not inh and not bool(Q.classify(P, R, seed=1)[0][0]),
                f"inheritance {inh}; unguarded whole-program test accepts: {ung}"))
    # 4 emergent replicator (positive, real): whole-program test blind, inheritance sees it
    X = fx("emergent-forward")
    R = Q.POSITIVES["forward"][0]
    k = I.count(X, sqrun(R), 3)
    kw = int((Q.classify(X, R, seed=3)[0] > 0).sum())
    out.append(("subleq positive: unseeded n4/always/s+1 soup at round 100 (5-byte loop) -> >= 30/40 inherited",
                k >= 30, f"{k}/40 (whole-program test: {kw}/40)"))
    # 5 selection-aware nulls: anchors' soups at round 300; random programs
    for name, R in (("null-rsubleq4", Q.RSUBLEQ4), ("null-subleq", Q.SUBLEQ)):
        k = I.count(fx(name), sqrun(R), 4)
        out.append((f"subleq null (top-40 selection): {name} soup at round 300 -> <= 1/40", k <= 1, f"{k}/40"))
    Rnd = np.random.default_rng(73).integers(0, 256, (200, 64), dtype=np.uint8)
    rules = [Q.POSITIVES["forward"][0], Q.POSITIVES["band"][0], Q.RSUBLEQ4, Q.SUBLEQ]
    kr = max(I.count(Rnd, sqrun(R), 7) for R in rules)
    out.append(("subleq negative: 200 random programs under 4 rules -> <= 1% inherited", kr <= 2, f"max {kr}/200"))
    if full:
        # 6 soups: seeded take-over (positive), no execution (negative), copy-all (deceptive for HOE)
        for name, (R, P) in Q.POSITIVES.items():
            progs = np.random.default_rng(5).integers(0, 256, (4096, 64), dtype=np.uint8)
            progs[:16] = P
            s = Q.Soup(R, n=4096, seed=5, programs=progs)
            for _ in range(60):
                s.epoch()
            k = I.count(Q.distinct_top(s.programs), sqrun(R), 8)
            out.append((f"subleq soup positive: 16 seeded {name} replicators in 4,096, round 60 -> >= 30/40 inherited",
                        k >= 30, f"{k}/40"))
        R = Q.POSITIVES["forward"][0]
        for mode, want in (("noexec", "none"), ("copyall", "none")):
            s = Q.Soup(R, n=4096, seed=6, mode=mode)
            for _ in range(100):
                s.epoch()
            k = I.count(Q.distinct_top(s.programs), sqrun(R), 9)
            h = Q.high_order_entropy(s.programs)
            out.append((f"subleq soup {'negative' if mode == 'noexec' else 'deceptive'}: {mode} soup, round 100 -> "
                        f"0/40 inherited" + (" (HOE is fooled)" if mode == "copyall" else ""), k == 0,
                        f"{k}/40, HOE {h:.2f}"))
    # 7 cross-language: the inheritance test on E-73's BFF fixtures agrees with D-053
    import bff_fidelity as FID
    import bff_fidelity_fixtures as FX
    for n in FID.POS:
        X, code = FID.fixture(n)
        k = I.count(X, bffrun(code), 5)
        out.append((f"inheritance on BFF: {n} -> >= 30/40", k >= 30, f"{k}/40 (D-053 {FID.count(X, code, 58, 75)}/40)"))
    for n in FID.NEG:
        X, code = FID.fixture(n)
        k = I.count(X, bffrun(code), 5)
        out.append((f"inheritance on BFF null (top-40): {n} -> <= 1/40", k <= 1, f"{k}/40"))
    codes = sorted({FX.SOUPS[n][0] for n in FX.SOUPS})
    S = FID.smears()
    ks = sum(I.count(S, bffrun(c), 6) for c in codes)
    out.append((f"inheritance on BFF deceptive: {len(S)} filler smears x {len(codes)} rules -> 0", ks == 0, f"{ks}"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    checks = controls()
    for n, ok, d in checks:
        print("PASS" if ok else "FAIL", n, "->", d, flush=True)
    json.dump({"experiment": "E-75", "phase": 0, "inheritance": {"gens": 5, "lineages": 4, "need": 3, "m": 4},
               "checks": [{"name": n, "ok": o, "detail": d} for n, o, d in checks],
               "all_pass": all(o for _, o, _ in checks)}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
