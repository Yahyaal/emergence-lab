"""Replicator detector for program soups (emergence/programs/bff.py), J-040, D-040.

The program analogue of the birth detector (births.py, D-028), and an intervention on copies,
never on the soup being observed:

* growth test: K copies of the candidate are put among N random programs and the soup runs
  EPOCHS epochs with no mutation. Copies are programs whose bytes match the candidate at
  >= SIM of positions. Generation 1 passes if the late count (max over the last quarter) is
  >= MIN_COPIES and >= MIN_GROWTH x the count at the start (K): copies keep multiplying.
* generation 2: one copy made in generation 1 (the most common one that is not an original),
  tested the same way, with copies still matched to the ORIGINAL candidate (no drift).
* rule-level null: random programs are tested the same way. If they multiply too, the rule
  copies anything (the "copyall" control, like Fredkin's rule for cellular automata) and the
  verdict is "rule-level duplication".

Also reported (not used in the verdict): the pair copy rate, the fraction of random partners
that become a copy after one interaction with the candidate run first.

Verdicts: "replicator", "rule-level duplication", "one generation", "no replication".

Selection: `scan` tests the most common exact programs of a soup. Common programs need not be
replicators (an inert majority is common too); the growth test decides.
"""
from __future__ import annotations

import numpy as np

from ..programs import bff as B

SIM = 0.9
K, N, EPOCHS = 8, 1024, 96
MIN_COPIES, MIN_GROWTH = 64, 4
N_RANDOM = 3


def similar(programs: np.ndarray, x: np.ndarray) -> np.ndarray:
    return (programs == x[None, :]).mean(1) >= SIM


def pair_copy_rate(x: np.ndarray, rng: np.random.Generator, partners: int = 128, max_steps: int = 8192) -> float:
    hits = 0
    for _ in range(partners):
        _, b = B.interact(x, rng.integers(0, 256, len(x), dtype=np.uint8), max_steps)
        hits += bool((b == x).mean() >= SIM)
    return hits / partners


def growth(x: np.ndarray, rng: np.random.Generator, ref: np.ndarray | None = None, mode: str = "bff",
           max_steps: int = 8192) -> dict:
    """K copies of x among N random programs, EPOCHS epochs without mutation."""
    ref = x if ref is None else ref
    progs = rng.integers(0, 256, (N, len(x)), dtype=np.uint8)
    progs[:K] = x
    soup = B.Soup(n=N, length=len(x), mutation=0.0, max_steps=max_steps, mode=mode,
                  seed=int(rng.integers(2 ** 31)), programs=progs)
    series = [int(similar(soup.programs, ref).sum())]
    for _ in range(EPOCHS):
        soup.epoch()
        series.append(int(similar(soup.programs, ref).sum()))
    late = max(series[-(EPOCHS // 4):])
    ok = late >= MIN_COPIES and late >= MIN_GROWTH * K
    return {"ok": bool(ok), "start": series[0], "late": late, "series": series, "soup": soup.programs}


def replication_test(x: np.ndarray, rng: np.random.Generator, mode: str = "bff", max_steps: int = 8192) -> dict:
    x = np.asarray(x, dtype=np.uint8)
    g1 = growth(x, rng, mode=mode, max_steps=max_steps)
    out = {"gen1": {k: v for k, v in g1.items() if k != "soup"},
           "pair_copy_rate": pair_copy_rate(x, rng, max_steps=max_steps) if mode == "bff" else None}
    if not g1["ok"]:
        return out | {"verdict": "no replication"}
    copies = [bytes(p) for p in g1["soup"][similar(g1["soup"], x)]]
    others = [c for c in copies if c != bytes(x)] or copies
    child = np.frombuffer(max(set(others), key=others.count), np.uint8).copy()
    g2 = growth(child, rng, ref=x, mode=mode, max_steps=max_steps)
    out["gen2"] = {k: v for k, v in g2.items() if k != "soup"}
    out["child_differs"] = bool((child != x).any())
    rnd = [growth(rng.integers(0, 256, len(x), dtype=np.uint8), rng, mode=mode, max_steps=max_steps)["ok"]
           for _ in range(N_RANDOM)]
    out["random_replicating"] = int(sum(rnd))
    if out["random_replicating"]:
        return out | {"verdict": "rule-level duplication"}
    return out | {"verdict": "replicator" if g2["ok"] else "one generation"}


def scan(programs: np.ndarray, rng: np.random.Generator, max_candidates: int = 4, mode: str = "bff",
         max_steps: int = 8192) -> dict:
    """Test the most common exact programs of a soup."""
    vals, counts = np.unique(programs, axis=0, return_counts=True)
    order = np.argsort(-counts, kind="stable")[:max_candidates]
    results = [replication_test(vals[i], rng, mode, max_steps) | {"count": int(counts[i]),
                                                                    "program": bytes(vals[i]).hex()}
               for i in order]
    return {"tested": len(results), "replicators": sum(r["verdict"] == "replicator" for r in results),
            "verdicts": [r["verdict"] for r in results], "results": results}
