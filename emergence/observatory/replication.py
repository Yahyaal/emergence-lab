"""Replication probe (intervention on isolated clones, never on the original universe).

Question: does a pattern give rise to copies of itself under this physics?

Method: place the pattern alone in an empty world (side not a power of two;
linear rules annihilate on power-of-two tori) and count exact copies of it
(orientation-free) over time.

* replicates      the copy count grows: >= 3 copies in the second half, more than
                  the maximum seen in the first quarter
Two null tests, both on random patterns of the same size and density:

* rule-level duplication  do random patterns copy THEMSELVES? Then the rule
                  duplicates everything (e.g. Fredkin's linear rule B1357/S1357).
* background production   do random patterns produce copies of the CANDIDATE
                  shape? Then the shape is just a common product of the rule's
                  dynamics (e.g. explosive rules such as Seeds B2/S make common
                  small shapes from anything), not something that copies itself.
                  This matters because scans pick the most common shapes in a
                  soup, which are exactly the ones background production favours.

Verdicts: "self-replicator", "rule-level duplication", "common product",
"explosive" (the pattern fills the test world, so copies can't be told apart from
debris; reported as untestable, never as replication), "no replication".

What this does NOT show: heredity or variation. Copies are exact by
construction of the test; whether variants also replicate is a separate question.
Limitation: only single connected shapes are tested (e.g. a glider gun, made of
separate pieces, is not a candidate).
"""
from __future__ import annotations

import numpy as np

from .shapes import canonical, canonical_patch
from .structures import census


EXPLOSION_FRACTION = 0.25  # stop when this fraction of the test world is occupied


def copy_series(physics, patch: np.ndarray, steps: int = 192, side: int = 160, every: int = 8,
                target: bytes | None = None) -> list[int] | None:
    """Copy counts over time, or None if the pattern explodes to fill the world."""
    w = np.zeros((side, side), np.uint8)
    r0, c0 = side // 2 - patch.shape[0] // 2, side // 2 - patch.shape[1] // 2
    w[r0:r0 + patch.shape[0], c0:c0 + patch.shape[1]] = patch
    target = canonical_patch(patch) if target is None else target
    out = []
    limit = EXPLOSION_FRACTION * w.size
    for t in range(steps + 1):
        if t % every == 0:
            if np.count_nonzero(w) > limit:
                return None
            out.append(sum(len(v) for k, v in census(w).items() if canonical(k) == target))
        if t < steps:
            w = physics.step(w)
    return out


def grows(series: list[int] | None) -> tuple[bool, int, int]:
    if series is None:
        return False, 0, 0
    q = max(1, len(series) // 4)
    early, late = max(series[:q + 1]), max(series[len(series) // 2:])
    return late >= 3 and late > early, early, late


def replication_test(physics, patch: np.ndarray, rng: np.random.Generator, n_random: int = 5,
                     steps: int = 192) -> dict:
    series = copy_series(physics, patch, steps)
    if series is None:
        return {"verdict": "explosive", "copies_early": 0, "copies_late": 0, "random_replicating": 0,
                "random_producing_candidate": 0, "n_random": 0}
    ok, early, late = grows(series)
    self_copy = background = 0
    if ok:
        dens = max(float((patch > 0).mean()), 0.3)
        target = canonical_patch(patch)
        for _ in range(n_random):
            rp = (rng.random(patch.shape) < dens).astype(np.uint8)
            if not rp.any():
                continue
            self_copy += grows(copy_series(physics, rp, steps))[0]
            background += grows(copy_series(physics, rp, steps, target=target))[0]
    verdict = ("no replication" if not ok else
               "rule-level duplication" if self_copy else
               "common product" if background else "self-replicator")
    return {"verdict": verdict, "copies_early": early, "copies_late": late,
            "random_replicating": self_copy, "random_producing_candidate": background, "n_random": n_random}


def scan_for_replicators(physics, frames: list[np.ndarray], rng: np.random.Generator,
                         max_candidates: int = 25, min_cells: int = 4) -> dict:
    """Test the most common distinct shapes of a universe for replication."""
    from collections import Counter
    counts: Counter[bytes] = Counter()
    rep_key: dict[bytes, bytes] = {}
    for f in frames:
        for k, poss in census(f).items():
            c = canonical(k)
            if np.count_nonzero(np.frombuffer(k[2:], np.uint8)) >= min_cells:
                counts[c] += len(poss)
                rep_key.setdefault(c, k)
    results = []
    for c, _ in counts.most_common(max_candidates):
        k = rep_key[c]
        patch = np.frombuffer(k[2:], np.uint8).reshape(k[0], k[1])
        r = replication_test(physics, patch, rng)
        if r["verdict"] not in ("no replication",):
            results.append({**r, "shape": f"{k[0]}x{k[1]}", "cells": int(np.count_nonzero(patch))})
    return {"tested": min(len(counts), max_candidates),
            "self_replicators": sum(r["verdict"] == "self-replicator" for r in results),
            "rule_level_duplication": sum(r["verdict"] == "rule-level duplication" for r in results),
            "common_products": sum(r["verdict"] == "common product" for r in results),
            "explosive": sum(r["verdict"] == "explosive" for r in results),
            "hits": results}
