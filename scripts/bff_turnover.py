"""E-47: species turnover in running BFF soups (docs/data/e47-preregistration.md).

Phase 1 (--replay): replays soups 901 (from random, seed 901) and 5006, 5010 (continued from the E-40
snapshots, as in E-41) to 40000 epochs, saving the soup every 250 epochs from 1000 epochs before the
E-41 transition. Replay is exact (checked against the E-41 snapshots).
Phase 2 (--analyse): dominant-species sequence per soup and races newcomer vs predecessor.

    python scripts/bff_turnover.py --replay --workers 3
    python scripts/bff_turnover.py --analyse --workers 11 --out docs/data/experiments/2026-11-08-e47-turnover.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import binomtest

from emergence.observatory import program_selection as PS
from emergence.observatory import replicators as RP
from emergence.programs import bff as B

RUN, E41, E40 = Path("runs/e47"), Path(".claude/worktrees/bff/runs/e41"), Path(".claude/worktrees/bff/runs/e40")
N, EPOCHS, EVERY = 16384, 40000, 250
# (seed, initial snapshot or None, transition epoch in E-41, E-41 snapshots to check)
SOUPS = [(901, None, 8750, (9750, 16000)), (5006, "bff-4006-16000.npy", 27250, (28250, 32000)),
         (5010, "bff-4010-16000.npy", 16000, (17000, 32000))]
MIN_SHARE, PERSIST, REPS = 0.05, 2, 64


def replay(spec) -> dict:
    seed, init, trans, check = spec
    progs = np.load(E40 / init) if init else None
    soup = B.Soup(n=N, mode="bff", seed=seed, programs=progs)
    exact = {}
    for e in range(1, EPOCHS + 1):
        soup.epoch()
        if e in check:
            ref = E41 / f"bff-{seed}-{e}.npy"
            exact[e] = bool(ref.exists() and np.array_equal(np.load(ref), soup.programs))
        if e % EVERY == 0 and e >= trans - 1000:
            np.save(RUN / f"{seed}-{e}.npy", soup.programs)
        if e % 2000 == 0:
            print(json.dumps({"seed": seed, "epoch": e, "exact": exact}), flush=True)
    return {"seed": seed, "exact_replay": exact}


def same_species(p: np.ndarray, ref: np.ndarray) -> bool:
    return bool(RP.similar(p[None], ref)[0] or RP.similar(p[None], ref[::-1])[0])


def species_share(programs: np.ndarray, ref: np.ndarray) -> float:
    return float((RP.similar(programs, ref) | RP.similar(programs, ref[::-1])).mean())


def sequence(seed: int, trans: int) -> dict:
    """Dominant species over time. A species is fixed by its reference (its first dominant program);
    a new species starts when the dominant program is < 90% identical to the current reference in
    both orientations for PERSIST consecutive snapshots and holds >= MIN_SHARE of the soup."""
    snaps = sorted(int(f.stem.split("-")[1]) for f in RUN.glob(f"{seed}-*.npy"))
    track, species, pending = [], [], []
    for e in snaps:
        P = np.load(RUN / f"{seed}-{e}.npy")
        top = np.frombuffer(B.top_programs(P, 1)[0][0], np.uint8).copy()
        share = species_share(P, top)
        row = {"epoch": e, "top": bytes(top).hex(), "top_species_share": round(share, 4)}
        if share >= MIN_SHARE:
            if not species:
                species.append({"ref": top, "first": e})
            elif not same_species(top, species[-1]["ref"]):
                pending.append((e, top))
                if len(pending) >= PERSIST and all(same_species(t, pending[0][1]) for _, t in pending):
                    species.append({"ref": pending[0][1], "first": pending[0][0]})
                    pending = []
            else:
                pending = []
        row["species"] = len(species) - 1
        row["shares"] = [round(species_share(P, s["ref"]), 4) for s in species]
        row["identity_to_first"] = round(float((top == species[0]["ref"]).mean()), 3) if species else None
        track.append(row)
    return {"seed": seed, "species": [{"ref": bytes(s["ref"]).hex(), "first": s["first"]} for s in species],
            "track": track}


def race(arg):
    k, old, new = arg
    h = lambda x: np.frombuffer(bytes.fromhex(x), np.uint8).copy()
    a, b = h(old), h(new)
    r = PS.compete_families(a, b, np.random.default_rng([47, k]), reps=REPS, a_alt=[a[::-1]], b_alt=[b[::-1]])
    s = [v for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    return r | {"new_wins": int(sum(v > 0 for v in s)), "n": len(s)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--analyse", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out")
    a = ap.parse_args()
    RUN.mkdir(parents=True, exist_ok=True)
    if a.replay:
        with Pool(a.workers) as pool:
            res = pool.map(replay, SOUPS, chunksize=1)
        (RUN / "replay.json").write_text(json.dumps(res))
        print(json.dumps(res))
        print("=== E47 REPLAY DONE", flush=True)
    if a.analyse:
        seqs = [sequence(s, t) for s, _, t, _ in SOUPS]
        jobs = []
        for q in seqs:
            for old, new in zip(q["species"], q["species"][1:]):
                jobs.append((len(jobs), old["ref"], new["ref"], q["seed"], old["first"], new["first"]))
        with Pool(a.workers) as pool:
            rr = pool.map(race, [j[:3] for j in jobs], chunksize=1)
        races = [{"seed": j[3], "old_first": j[4], "new_first": j[5], "old": j[1], "new": j[2]} | r for j, r in zip(jobs, rr)]
        k = sum(r["new_wins"] > r["n"] / 2 for r in races)
        w, n = sum(r["new_wins"] for r in races), sum(r["n"] for r in races)
        summary = {"replacements": len(races), "newcomer_ahead": k,
                   "sign_p": float(binomtest(k, len(races), alternative="greater").pvalue) if races else None,
                   "pooled_newcomer_share": round(w / max(n, 1), 3),
                   "pooled_p": float(binomtest(w, n, alternative="greater").pvalue) if n else None,
                   "verdicts": [r["verdict"] for r in races]}
        replay_info = json.loads((RUN / "replay.json").read_text()) if (RUN / "replay.json").exists() else None
        json.dump({"experiment": "E-47", "summary": summary, "replay": replay_info, "sequences": seqs, "races": races},
                  open(a.out, "w"), indent=1)
        print(json.dumps(summary, indent=1))
        print("=== E47 DONE", flush=True)


if __name__ == "__main__":
    main()
