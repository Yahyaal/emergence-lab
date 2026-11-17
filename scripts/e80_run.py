"""E-80 confirmatory run and analysis (docs/data/e80-preregistration.md): late S vs late M code of the 7 E-78 soups
in a lattice-native common garden (scripts/lattice_assay.py), soup as the unit.

Refuses to load late-S snapshots unless docs/data/e80-preregistration.md is committed (checked with git) and
--confirm is given. `--dry` checks the code path with the fork snapshots standing in for every arm (not data).

    python scripts/e80_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e80-lattice.json
    python scripts/e80_run.py --dry --workers 11 --out runs/e80/dry.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import t as tdist

sys.path.insert(0, str(Path(__file__).parent))
import bff_spatial as BS  # noqa: E402
import e80_groundwork as G  # noqa: E402
import lattice_assay as LA  # noqa: E402

# ---- fixed by the pre-registration ---------------------------------------------------------------
GARDEN = "g901"            # primary garden: 4 lattice-aged replicates of soup 901 at round 40,000 (runs/e80/garden-*)
GARDEN2 = "g5006"          # second garden (sensitivity): soup 5006 at round 32,000, same ageing
T_H = 64                   # assay horizon (rounds)
R_BLOCKS, S_SEEDS = 16, 4  # blocks per source and assay seeds per block (primary)
R_SEC, S_SEC = 8, 2        # well-mixed pairing (1 seed) and second garden (2 seeds): 8 blocks each
KIN_MAX = 0.001            # an assay whose block has > 0.1% kin in its garden replicate is excluded
DELTA_STAR = 1.24          # smallest effect of interest: half the emergent positive (score units), pre-registration
MIN_KEEP = 0.5             # a soup is excluded if < half of either arm's primary assays survive the kin rule
GROUPS = ("early", "M", "Mp", "S", "Sshuf")
GCODE = {"early": 0, "M": 1, "Mp": 2, "S": 3, "Sshuf": 3}   # Sshuf = the S blocks, positions permuted
WORK = Path("runs/e80/run")
CFG = {"dry": False}


def snapshot(seed: int, group: str) -> np.ndarray:
    kind = {"Sshuf": "S"}.get(group, group)
    if CFG["dry"]:
        return G.source(seed, "early")
    return G.source(seed, kind)


def block(seed: int, group: str, b: int) -> np.ndarray:
    """S: a contiguous 8 x 8 block of the 256 x 256 S lattice at a seeded random position (preserved), or the same
    block with positions permuted (Sshuf). early / M / Mp: well mixed, a random sample laid out at random."""
    P = snapshot(seed, group)
    rng = np.random.default_rng([80, 10, seed, GCODE[group], b])
    if group in ("S", "Sshuf"):
        blk, _ = LA.make_block(P, rng, geometry=True, width=BS.SIDE, mode="preserved")
        if group == "Sshuf":
            blk = blk[np.random.default_rng([80, 11, seed, b]).permutation(len(blk))]
        return blk
    blk, _ = LA.make_block(P, rng, geometry=False)
    return blk


def jobs() -> list[tuple]:
    J = []
    for seed in BS.JUMPED:
        for g in GROUPS:
            for b in range(R_BLOCKS):
                for j in range(S_SEEDS):
                    J.append((seed, g, b, j, "spatial", GARDEN))
        for g in ("early", "M", "S"):
            for b in range(R_SEC):
                J.append((seed, g, b, 0, "mixed", GARDEN))
        for g in ("early", "M", "Mp", "S"):
            for b in range(R_SEC):
                for j in range(S_SEC):
                    J.append((seed, g, b, j, "spatial", GARDEN2))
    return J


def key(j) -> str:
    return "|".join(map(str, j))


def run_job(j) -> dict:
    seed, group, b, jj, arm, gname = j
    t0 = time.time()
    gi = (b + jj) % G.N_GARDEN
    Gd = G.garden(gname, gi)
    blk = block(seed, group, b)
    kin = LA.kin_share(Gd, blk)
    # common random numbers: same garden replicate, block position and pairing seed for every group of a soup
    aseed = [80, 100, seed, b, jj, gi, G.ARMCODE[arm], G.GCODE[gname]]
    r = LA.assay([blk], Gd, aseed, arm=arm, rounds=T_H, checkpoints=(16, 32, T_H))
    return {"key": key(j), "seed": seed, "group": group, "b": b, "j": jj, "arm": arm, "garden": gname, "gi": gi,
            "kin": kin, "series": {t: v[0] for t, v in r["series"].items()}, "events": r["events"],
            "purity_anchor": r["purity_anchor"][0], "steps_per_pair": r["steps_per_pair"],
            "sec": round(time.time() - t0, 1)}


def score(r: dict, T: int = T_H, log: bool = False) -> float:
    """Primary: relative area change N_T / N_0 - 1 (a martingale under neutrality; bounded below by -1). log=True:
    ln((N_T + 1) / (N_0 + 1)), the invasion-style score (sensitivity)."""
    n = r["series"][str(T)]
    return float(np.log((n + 1) / (LA.K * LA.K + 1))) if log else float(n / (LA.K * LA.K) - 1)


# ---- statistics ---------------------------------------------------------------------------------

def t_ci(d) -> list[float]:
    d = np.asarray(d, float)
    h = tdist.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return [float(d.mean() - h), float(d.mean() + h)]


def soup_means(rows, arm="spatial", garden=GARDEN, T=T_H, log=False) -> tuple[dict, dict]:
    """Per soup and group: mean score over kept assays (kin rule), and the count kept / total."""
    m, kept = {}, {}
    for seed in BS.JUMPED:
        for g in GROUPS:
            rr = [r for r in rows if r["seed"] == seed and r["group"] == g and r["arm"] == arm and r["garden"] == garden]
            ok = [score(r, T, log) for r in rr if r["kin"] <= KIN_MAX]
            kept[(seed, g)] = (len(ok), len(rr))
            m[(seed, g)] = float(np.mean(ok)) if ok else None
    return m, kept


def contrast(m, kept, a: str, b: str, soups=None) -> dict:
    soups = soups or [s for s in BS.JUMPED if m[(s, a)] is not None and m[(s, b)] is not None
                      and kept[(s, a)][0] >= MIN_KEEP * max(kept[(s, a)][1], 1)
                      and kept[(s, b)][0] >= MIN_KEEP * max(kept[(s, b)][1], 1)]
    d = np.array([m[(s, a)] - m[(s, b)] for s in soups])
    if len(d) < 3:
        return {"soups": soups, "verdict": "undecided (too few soups)"}
    return {"soups": soups, "d": {str(s): round(float(v), 4) for s, v in zip(soups, d)},
            "mean_d": round(float(d.mean()), 4), "sd_d": round(float(d.std(ddof=1)), 4),
            "p_one_sided": LA.signflip_p(d), "p_two_sided": LA.signflip_p(d, two_sided=True),
            "ci95": [round(v, 4) for v in t_ci(d)]}


def verdict(primary: dict, null: dict) -> str:
    if "mean_d" not in primary:
        return primary["verdict"]
    if primary["p_one_sided"] < 0.05 and primary["mean_d"] > 0 and null["p_two_sided"] >= 0.05:
        return "pass"
    if primary["ci95"][1] < DELTA_STAR:
        return "fail"
    return "undecided"


def analyse(rows: list[dict]) -> dict:
    m, kept = soup_means(rows)
    prim = contrast(m, kept, "S", "M")
    null = contrast(m, kept, "Mp", "M")
    res = {"settings": {"garden": GARDEN, "garden2": GARDEN2, "T": T_H, "R": R_BLOCKS, "S": S_SEEDS, "KIN_MAX": KIN_MAX,
                        "DELTA_STAR": DELTA_STAR, "dry": CFG["dry"]},
           "kin_excluded": {f"{s}/{g}": kept[(s, g)][1] - kept[(s, g)][0] for (s, g) in kept},
           "means": {f"{s}/{g}": (round(v, 4) if v is not None else None) for (s, g), v in m.items()},
           "primary": prim, "seed_null": null, "verdict": verdict(prim, null),
           "secondary": {"S_vs_early": contrast(m, kept, "S", "early"), "M_vs_early": contrast(m, kept, "M", "early"),
                         "Mp_vs_early": contrast(m, kept, "Mp", "early"),
                         "S_preserved_vs_shuffled": contrast(m, kept, "S", "Sshuf"),
                         "Sshuf_vs_M": contrast(m, kept, "Sshuf", "M")}}
    mm, km = soup_means(rows, arm="mixed")
    res["secondary"]["wellmixed_pairing_S_vs_M"] = contrast(mm, km, "S", "M")
    res["secondary"]["wellmixed_pairing_S_vs_early"] = contrast(mm, km, "S", "early")
    res["secondary"]["wellmixed_pairing_M_vs_early"] = contrast(mm, km, "M", "early")
    # lattice-specific part: (S - M) on the lattice minus (S - M) with well-mixed pairing, per soup, two-sided
    ok = [s for s in prim.get("soups", []) if mm[(s, "S")] is not None and mm[(s, "M")] is not None]
    dd = [(m[(s, "S")] - m[(s, "M")]) - (mm[(s, "S")] - mm[(s, "M")]) for s in ok]
    res["secondary"]["lattice_minus_wellmixed"] = {"soups": ok, "d": [round(v, 4) for v in dd],
                                                   "mean_d": round(float(np.mean(dd)), 4) if dd else None,
                                                   "p_two_sided": LA.signflip_p(dd, two_sided=True) if len(dd) >= 3 else None}
    m2, k2 = soup_means(rows, garden=GARDEN2)
    ml, kl = soup_means(rows, log=True)
    res["sensitivity"] = {"without_5410": contrast(m, kept, "S", "M", [s for s in prim.get("soups", []) if s != 5410]),
                          "without_5401": contrast(m, kept, "S", "M", [s for s in prim.get("soups", []) if s != 5401]),
                          "T32": contrast(*soup_means(rows, T=32), "S", "M"),
                          "log_score": contrast(ml, kl, "S", "M"), "log_score_seed_null": contrast(ml, kl, "Mp", "M"),
                          "garden_g5006": contrast(m2, k2, "S", "M"), "garden_g5006_seed_null": contrast(m2, k2, "Mp", "M")}
    return res


def preregistered() -> bool:
    out = subprocess.run(["git", "log", "-1", "--format=%H", "--", "docs/data/e80-preregistration.md"],
                         capture_output=True, text=True)
    return bool(out.stdout.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    global R_BLOCKS, S_SEEDS, R_SEC, S_SEC, WORK
    if a.dry:
        CFG["dry"] = True
        R_BLOCKS, S_SEEDS, R_SEC, S_SEC, WORK = 2, 1, 1, 1, Path("runs/e80/dry")
    elif a.confirm:
        if not preregistered():
            sys.exit("docs/data/e80-preregistration.md is not committed: refusing to load late-S data")
        os.environ["E80_CONFIRMATORY"] = "1"
    else:
        sys.exit("give --confirm (after the pre-registration commit) or --dry")
    WORK.mkdir(parents=True, exist_ok=True)
    cache = WORK / "assays.jsonl"
    done = {}
    if cache.exists():
        for line in cache.read_text().splitlines():
            r = json.loads(line)
            done[r["key"]] = r
    J = jobs()
    todo = [j for j in J if key(j) not in done]
    print(f"E-80: {len(done)} cached, {len(todo)} to run", flush=True)
    t0 = time.time()
    with Pool(a.workers) as pool, cache.open("a") as f:
        for i, r in enumerate(pool.imap_unordered(run_job, todo, chunksize=1)):
            done[r["key"]] = r
            f.write(json.dumps(r) + "\n")
            f.flush()
            if i % 100 == 0:
                print(f"  {i}/{len(todo)} {round(time.time() - t0)} s", flush=True)
    rows = [done[key(j)] for j in J]
    res = analyse(rows)
    res["seconds"] = round(time.time() - t0)
    out = {"experiment": "E-80" + (" DRY RUN (not data)" if CFG["dry"] else ""), "summary": res, "assays": rows}
    Path(a.out).write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))
    print("=== E80 RUN DONE", flush=True)


if __name__ == "__main__":
    main()
