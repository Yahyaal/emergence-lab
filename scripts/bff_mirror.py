"""E-57 (docs/data/e57-preregistration.md): do counterfactual soups (head1 starts at 64) jump faster at 2^14,
and are backward copiers rarely replicators on their own (a mirror replicator needs two kernels)?

    python scripts/bff_mirror.py --part census --out docs/data/experiments/2026-11-08-e57-census.json
    python scripts/bff_mirror.py --part soups --workers 4 --out docs/data/experiments/2026-11-08-e57-soups.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

L = K.L
E40_REF = (0, 12)  # standard 2^14 soups jumped by 16,000 rounds (E-40)


def product(P: np.ndarray, h1: int, rng) -> np.ndarray:
    tape = np.concatenate([P, rng.integers(0, 256, L, dtype=np.uint8)]).astype(np.uint8)
    K.lib().run_tape(tape.ctypes.data, 2 * L, K.STEPS, h1)
    return tape[L:].copy()


def self_sufficient(P: np.ndarray, h1: int, rng, runs: int = 4) -> bool:
    prods = np.array([product(P, h1, rng) for _ in range(runs)])
    ok = K.classify(prods, h1, 4, int(rng.integers(1 << 62)))
    return int((ok > 0).sum()) >= 3


def filled(kernel: bytes, rng, tail: bytes = b"") -> np.ndarray:
    x = K.NONOP_NZ[rng.integers(0, len(K.NONOP_NZ), L)].copy()
    x[:len(kernel)] = np.frombuffer(kernel, np.uint8)
    if tail:
        x[L - len(tail):] = np.frombuffer(tail, np.uint8)
    return x


def census() -> dict:
    rng = np.random.default_rng(570)
    kernels = {"standard": [], "counterfactual": []}
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            _, _, res = K.chunk((k, lo, min(lo + K.CHUNK, 10 ** k), False))
            for rule in res:
                kernels[rule] += [h for h, _ in res[rule]["hits"]]
    out = {"kernels": {r: len(v) for r, v in kernels.items()}}
    for rule, h1 in (("standard", 0), ("counterfactual", L)):
        rows = []
        for kern in kernels[rule]:
            x = filled(kern.encode(), rng)
            lab = K.label(K.classify(x[None], h1, 4, int(rng.integers(1 << 62)))[0])
            rows.append({"kernel": kern, "orientation": lab,
                         "self_sufficient": lab != "none" and self_sufficient(x, h1, rng)})
        conf = [r for r in rows if r["orientation"] != "none"]
        out[rule] = {"copiers": len(conf), "self_sufficient": sum(r["self_sufficient"] for r in conf),
                     "examples_self_sufficient": [r["kernel"] for r in conf if r["self_sufficient"]][:12],
                     "rows": rows}
        out[rule]["fraction"] = round(out[rule]["self_sufficient"] / max(len(conf), 1), 3)
    std = kernels["standard"]
    pairs = []
    for k1 in std:
        for k2 in std:
            x = filled(k1.encode(), rng, k2.encode()[::-1])
            lab = K.label(K.classify(x[None], 0, 4, int(rng.integers(1 << 62)))[0])
            if lab != "none" and self_sufficient(x, 0, rng):
                pairs.append([k1, k2, lab])
    out["mirror_pairs"] = {"tested": len(std) ** 2, "self_sufficient": len(pairs),
                           "examples": pairs[:12],
                           "shortest_instructions": min((len(a) + len(b) for a, b, _ in pairs), default=None)}
    ctl = {}
    ctl["handwritten"] = self_sufficient(B.REPLICATOR.copy(), 0, rng)
    E = [np.frombuffer(bytes.fromhex(r["program"]), np.uint8).copy() for r in json.load(open(K.E42))["results"]]
    ctl["e42_emergent"] = [self_sufficient(x, 0, rng) for x in E]
    R = rng.integers(0, 256, (1000, L), dtype=np.uint8)
    ctl["random_1000_self_sufficient"] = int(sum(self_sufficient(x, 0, rng) for x in R))
    ctl["constant_writer"] = self_sufficient(filled(b"[{.]", rng), 0, rng)
    out["controls"] = ctl
    out["primary_B"] = {"standard_le_5pct": out["standard"]["fraction"] <= 0.05,
                        "counterfactual_ge_90pct": out["counterfactual"]["fraction"] >= 0.90}
    out["primary_B"]["pass"] = all(out["primary_B"].values())
    return out


def fisher_one_sided(a: int, n1: int, b: int, n2: int) -> float:
    """P(X >= a) for X ~ hypergeometric: a jumps of n1 vs b of n2."""
    tot, m = n1 + n2, a + b
    return sum(comb(m, x) * comb(tot - m, n1 - x) for x in range(a, min(m, n1) + 1)) / comb(tot, n1)


def soups(workers: int) -> dict:
    C.N, C.WAIT, C.AFTER, C.RUN, C.SEEDS = 2 ** 14, 16000, 1000, Path("runs/e57"), range(5700, 5708)
    C.RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(C.job, list(C.SEEDS), chunksize=1)
    jumped = [r for r in res if r["jumped"]]
    p = fisher_one_sided(len(jumped), len(res), *E40_REF)
    fwd_ok = [r["orientation"]["forward"] >= 1 and r["orientation"]["forward"] >= 0.9 * (
        r["orientation"]["forward"] + r["orientation"]["reverse"] + r["orientation"]["both"]) for r in jumped]
    return {"summary": {"jumped": len(jumped), "of": len(res), "T": {r["seed"]: r["T"] for r in res},
                        "reference_E40": {"jumped": E40_REF[0], "of": E40_REF[1]}, "fisher_p": p,
                        "primary_A": "pass" if len(jumped) >= 6 and p < 0.01 else "fail",
                        "secondary_forward": "pass" if jumped and all(fwd_ok) else ("undecided" if not jumped else "fail"),
                        "orientation": {r["seed"]: {k: v for k, v in r["orientation"].items() if k != "copiers"}
                                        for r in jumped}},
            "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-57", "part": a.part} | (census() if a.part == "census" else soups(a.workers))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    show = {k: v for k, v in out.items() if k not in ("results",)}
    for r in ("standard", "counterfactual"):
        if r in show:
            show[r] = {k: v for k, v in show[r].items() if k != "rows"}
    print(json.dumps(show, indent=1, default=str))
    print(f"=== E57 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
