"""E-75 phase 5 (pre-registered, docs/data/e75-phase5-preregistration.md; D-060): where do the first replicators
come from? An exact Python replay of a soup (same RNG calls as subleq.Soup, checked byte for byte) that follows
every replicator lineage from its first appearance.

Per round, every pair is run as subleq.Soup does. The executing program (the first of the pair) is tested with the
inheritance test (D-055) when its run takes >= S_MIN steps; a positive is retested with a second RNG and counts
only if both agree (results cached by content). Then:
  - a partner written to by a replicator inherits the executor's lineage tag (a putative copy);
  - a tagged slot that executes a non-replicator becomes a *lapsed* member; if it later executes a replicator it
    rejoins its lineage (a revival), and a lapsed slot written to by another replicator takes that one's tag;
  - a replicator execution in an untagged slot is an ORIGIN: a new lineage. Its cause is how the slot last changed
    before it: 'partner' (written by another program's run), 'self' (its own run rewrote it), 'mutation', or a
    combination; 'initial' if it never changed since round 0.
A lineage keeps the class of its founder: *null* if the inherited block is all zeros (the all-zero program writes
zeros over its partner and so "copies" itself without carrying information), else *informative*. A lineage
*establishes* when it makes >= EST replicator executions in one round; tracing stops at the first establishment
(or at MAX_ROUNDS for soups that never jumped in the original run, MAX_JUMPED for those that did).
Part B: if the first lineage to establish is null, a C soup (same seed) is run on and checked every EVERY rounds
until its top-40 distinct programs hold >= MIN_INF informative inheritors (or B_ROUNDS after establishment).

    PYTHONPATH=. python scripts/sq_nucleation.py --workers 11 --out docs/data/experiments/2026-11-13-e75-nucleation.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parents[1]))
from emergence.programs import inherit as I  # noqa: E402
from emergence.programs import subleq as Q  # noqa: E402

P3 = Path("docs/data/experiments/2026-11-13-e75-phase3.json")
P4 = Path("docs/data/experiments/2026-11-13-e75-phase4.json")
N, L, MU = 2 ** 14, 64, 0.00024
S_MIN, EST, MAX_ROUNDS, MAX_JUMPED = 16, 200, 4000, 16_000
EVERY, MIN_INF, B_ROUNDS = 50, 10, 3000
SELF, PARTNER, MUT = 1, 2, 4
CAUSE = {0: "initial", SELF: "self", PARTNER: "partner", MUT: "mutation", SELF | MUT: "self+mutation",
         PARTNER | MUT: "partner+mutation", SELF | PARTNER: "self+partner", SELF | PARTNER | MUT: "all"}


class Tester:
    """Inheritance test (D-055), confirmed with a second RNG; cached by content. Returns 0 (not a replicator),
    1 (a *null* replicator: the inherited block is all zeros, e.g. the all-zero program, which writes zeros
    over its partner and so "copies" itself without carrying information) or 2 (an informative replicator)."""

    def __init__(self, R):
        self.R, self.cache = R, {}
        self.run = lambda t: Q.run(t, R)[0]  # noqa: E731
        self.tests = 0

    def __call__(self, prog: np.ndarray) -> int:
        k = prog.tobytes()
        v = self.cache.get(k)
        if v is None:
            self.tests += 1
            h = int.from_bytes(hashlib.sha1(k).digest()[:8], "little")
            ok, i = I.inherits(prog, self.run, np.random.default_rng([h, 1]))
            if ok:
                ok, j = I.inherits(prog, self.run, np.random.default_rng([h, 2]))
            v = 0 if not ok else (1 if k[i:i + 4] == bytes(4) and k[j:j + 4] == bytes(4) else 2)
            self.cache[k] = v
        return v


def trace(seed: int, code: int, max_rounds: int, inject: str | None = None) -> dict:
    R = Q.Rule.from_code(code)
    rng = np.random.default_rng(seed)
    P = rng.integers(0, 256, (N, L), dtype=np.uint8)
    if inject:
        P[0] = np.frombuffer(bytes.fromhex(inject), np.uint8)
    test = Tester(R)
    tag = np.full(N, -1, np.int64)          # lineage of the slot's content; -1 none; <= -2 lapsed member of -tag-2
    last_round = np.zeros(N, np.int64)      # round in which the slot last changed (0: never)
    last_cause = np.zeros(N, np.int64)      # SELF / PARTNER / MUT bits of that change
    prev = P.copy()                         # content before that change
    writer = np.zeros((N, L), np.uint8)     # executor content that wrote into the slot (PARTNER changes)
    lineages, series, est = [], [], None
    e = 0
    while e < max_rounds and est is None:
        e += 1
        start = P.copy()
        cause = np.zeros(N, np.int64)
        pairs = rng.permutation(N).astype(np.int32)
        reps: dict[int, int] = {}
        kinds = [0, 0, 0]
        for p in range(N // 2):
            a, b = int(pairs[2 * p]), int(pairs[2 * p + 1])
            before = np.concatenate([P[a], P[b]])
            t, n = Q.run(before, R)
            is_rep = False
            if n >= S_MIN:
                kind = test(before[:L])
                is_rep = kind > 0
                if is_rep:
                    if tag[a] <= -2:  # a lapsed member of a lineage turned back into a replicator: a revival
                        tag[a] = -tag[a] - 2
                        lineages[int(tag[a])]["revivals"] += 1
                    if tag[a] < 0:
                        c = int(last_cause[a])
                        lineages.append({"id": len(lineages), "round": e, "slot": a, "steps": int(n),
                                         "cause": CAUSE[c], "changed_round": int(last_round[a]),
                                         "null": kind == 1,
                                         "program": before[:L].tobytes().hex(),
                                         "before_change": prev[a].tobytes().hex() if c else None,
                                         "writer": writer[a].tobytes().hex() if c & PARTNER else None,
                                         "executions": 0, "peak": 0, "peak_round": e, "last_round": e, "revivals": 0})
                        tag[a] = len(lineages) - 1
                    reps[int(tag[a])] = reps.get(int(tag[a]), 0) + 1
                    kinds[kind] += 1
                elif tag[a] >= 0:
                    tag[a] = -tag[a] - 2  # lapsed: descended from lineage tag[a] but not a replicator now
            if (t[:L] != before[:L]).any():
                cause[a] |= SELF
                P[a] = t[:L]
            if (t[L:] != before[L:]).any():
                cause[b] |= PARTNER
                writer[b] = before[:L]
                if is_rep:
                    tag[b] = tag[a]
                P[b] = t[L:]
        k = rng.binomial(P.size, MU)
        idx = rng.integers(0, P.size, k)
        P.reshape(-1)[idx] = rng.integers(0, 256, k, dtype=np.uint8)
        cause[np.unique(idx // L)] |= MUT
        ch = np.flatnonzero((P != start).any(1))
        prev[ch] = start[ch]
        last_round[ch], last_cause[ch] = e, cause[ch]
        if reps:
            series.append([e, kinds[1], kinds[2], len(reps)])
            for lid, c in reps.items():
                lg = lineages[lid]
                lg["executions"] += c
                lg["last_round"] = e
                if c > lg["peak"]:
                    lg["peak"], lg["peak_round"] = c, e
                if c >= EST and est is None:
                    est = {"round": e, "lineage": lid, "null": lg["null"]}
    return {"seed": seed, "code": code, "rule": str(R), "rounds": e, "established": est, "lineages": lineages,
            "series": series, "tests": test.tests, "replicator_contents": sum(test.cache.values()), "final": P}


def informative_after(seed: int, code: int, start: int, stop: int) -> dict:
    """Part B (fast C soup): after a null lineage establishes, the first checkpoint (every EVERY rounds, from the
    first multiple of EVERY after `start`) whose top-40 distinct programs hold >= MIN_INF informative inheritors."""
    R = Q.Rule.from_code(code)
    run = lambda t: Q.run(t, R)[0]  # noqa: E731
    s = Q.Soup(R, n=N, seed=seed)
    cps = []
    while s.epochs < stop:
        s.epoch()
        if s.epochs < start or s.epochs % EVERY:
            continue
        X = Q.distinct_top(s.programs)
        rng = np.random.default_rng(7700 + seed + s.epochs)
        res = [I.inherits(x, run, rng) for x in X]
        inh = [(x, i) for x, (ok, i) in zip(X, res) if ok]
        null = sum(bytes(x[i:i + 4]) == bytes(4) for x, i in inh)
        cps.append([s.epochs, len(inh) - null, null])
        if len(inh) - null >= MIN_INF:
            return {"round": s.epochs, "checkpoints": cps}
    return {"round": None, "checkpoints": cps}


def job(arg) -> dict:
    kind, phase, group, k, i, code, T, inject = arg
    t0 = time.time()
    seed = (77000 if phase == 3 else 78000) + 10 * k + i
    res = trace(seed, code, MAX_JUMPED if T is not None else MAX_ROUNDS, inject)
    res.pop("final")
    est = res["established"]
    if est and est["null"]:
        res["informative_after"] = informative_after(seed, code, est["round"], est["round"] + B_ROUNDS)
    res.update(kind=kind, phase=phase, group=group, soup=i, T_original=T, sec=round(time.time() - t0))
    print(json.dumps({x: res[x] for x in ("kind", "rule", "seed", "T_original", "rounds", "established", "sec")}
                     | {"origins": len(res["lineages"])}), flush=True)
    return res


def jobs() -> list:
    out = []
    d3, d4 = json.load(open(P3)), json.load(open(P4))
    soups = {s["seed"]: s for s in d3["soups"] + d4["soups"]}
    for phase, d in ((3, d3), (4, d4)):
        for k, q in enumerate(d["summary"]["rules"]):
            if phase == 4 and q["pool"] != "A":
                continue
            for i in (0, 1):
                seed = (77000 if phase == 3 else 78000) + 10 * k + i
                out.append(("main", phase, q["group"], k, i, q["code"], soups[seed]["T"], None))
    # negative controls: pool B LOW rules (no tile replicators, 0/36 soups jumped)
    B = [(k, q) for k, q in enumerate(d4["summary"]["rules"]) if q["pool"] == "B" and q["group"] == "LOW"]
    for k, q in B[:2]:
        for i in (0, 1):
            out.append(("negative", 4, "B-LOW", k, i, q["code"], None, None))
    # positive controls: a verified replicator (top program after the jump in another soup of the same rule)
    for k, q in enumerate(d4["summary"]["rules"]):
        if q["rule"] in ("n4 j<=0 s+1 W32 o28", "n4 j<=0 s+1 W16 o18"):
            top = soups[78000 + 10 * k + 5]["top3"][0]
            out.append(("positive", 4, q["group"], k, 2, q["code"], 0, top))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    J = jobs()
    J.sort(key=lambda j: -(j[6] or MAX_ROUNDS))  # longest first
    with Pool(a.workers) as pool:
        res = pool.map(job, J, chunksize=1)
    json.dump({"experiment": "E-75", "phase": 5, "S_MIN": S_MIN, "EST": EST, "MAX_ROUNDS": MAX_ROUNDS,
               "soups": res, "seconds": round(time.time() - t0)}, open(a.out, "w"), indent=1)
    print("=== SENTINEL e75 nucleation DONE", flush=True)


if __name__ == "__main__":
    main()
