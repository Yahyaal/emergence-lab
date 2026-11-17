"""E-80 groundwork (J-093): gardens, calibration on allowed data, noise components and power for the lattice assay.

Allowed data before the pre-registration (no late-S data is loaded anywhere in this file; `source()` refuses "S"):
  * synthetic programs and gardens; E-46's 5006 species (E-42 #5) and E-47 snapshots of soups 901 / 5010 / 5006,
    which are unrelated to the 7 E-54 soups (independent random starts);
  * the 7 E-78 fork-point snapshots ("early", T + 2000, identical in every arm) and the final M and M' snapshots.

    python scripts/e80_groundwork.py --gardens --workers 11      # lattice-aged gardens -> runs/e80/garden-*.npy
    python scripts/e80_groundwork.py --calibrate --workers 11    # assays -> runs/e80/calib.jsonl (cached, resumable)
    python scripts/e80_groundwork.py --power --out docs/data/experiments/<date>-e80-groundwork.json
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_spatial as BS  # noqa: E402
import lattice_assay as LA  # noqa: E402

from emergence.observatory import program_fitness as F  # noqa: E402

OUT = LA.OUT
GARDENS = {"g5006": ("5006-32000.npy", 3), "g901": ("901-40000.npy", 1)}   # primary, secondary (+ "random")
N_GARDEN, AGE, GSIDE = 4, 2000, LA.SIDE
SOURCES = {"early": 0, "M": 1, "Mp": 2, "S": 3}
ARMCODE = {"spatial": 0, "mixed": 1}
GCODE = {"g5006": 0, "g901": 1, "random": 2}
H = 20000
ROUNDS_MAX = 192             # calibration horizon (checkpoints 16 ... 192)
E42 = Path("docs/data/experiments/2026-11-08-e42-bff-heredity.json")


def source(seed: int, kind: str) -> np.ndarray:
    """Snapshot of one of the 7 E-78 soups: early (fork point), M or Mp final. Late S is refused unless the
    confirmatory run sets E80_CONFIRMATORY=1 (pre-registration committed first)."""
    T = BS.JUMPED[seed] + BS.FORK_DT
    if kind == "S" and os.environ.get("E80_CONFIRMATORY") != "1":
        raise PermissionError("late S snapshots are the confirmatory contrast: not loaded before the pre-registration")
    if kind == "early":
        return np.load(LA.E78RUN / f"{seed}-M-{T}.npy")
    return np.load(LA.E78RUN / f"{seed}-{kind}-{T + H}.npy")


def garden(name: str, i: int) -> np.ndarray:
    if name == "random":
        return np.random.default_rng([80, 0, i]).integers(0, 256, (GSIDE * GSIDE, 64), dtype=np.uint8)
    return np.load(OUT / f"garden-{name}-{i}.npy")


def _garden_job(arg):
    name, i = arg
    fn, code = GARDENS[name]
    P = np.load(LA.E47 / fn)
    G0 = P[np.random.default_rng([80, code, i]).choice(len(P), GSIDE * GSIDE, replace=False)]
    G, ser = LA.age_garden(G0, AGE, [80, code, i, 1])
    np.save(OUT / f"garden-{name}-{i}.npy", G)
    return {"garden": name, "i": i, "source": fn, "series": ser}


def e42(i: int) -> np.ndarray:
    """E-42 replicator i: #5 = soup 5006's species at 32000 (#6 its byte-reverse); #0 = soup 901 at 9750.
    E-46: the 5006 species beats soup 901's replicators in 176 of 252 races (p = 1e-10)."""
    r = json.load(open(E42))["results"]
    return np.frombuffer(bytes.fromhex(r[i]["program"]), np.uint8).copy()


# ---- calibration jobs ---------------------------------------------------------------------------

def jobs(r: int = 8, s_seeds: int = 3, mixed_seeds: int = 1, r_other: int = 4) -> list[tuple]:
    J = []
    # noise and power: 7 soups x {early, M, Mp} x r blocks x seeds; same (soup, b, j) -> same garden replicate,
    # block position and pairing seed in every source (common random numbers, as planned for S vs M)
    for seed in BS.JUMPED:
        for src in ("early", "M", "Mp"):
            for b in range(r):
                for j in range(s_seeds):
                    J.append(("noise", seed, src, b, j, "g5006", "spatial"))
                for j in range(mixed_seeds):
                    J.append(("noise", seed, src, b, j, "g5006", "mixed"))
                if b < r_other:
                    J.append(("noise", seed, src, b, 0, "g901", "spatial"))
                    J.append(("noise", seed, src, b, 0, "random", "spatial"))
    # emergent positives (E-46: the 5006 species beats soup 901's replicators), each against a native block cut from
    # the garden at a random position, same seed: in g5006 the native (5006) block should beat 64 copies of 901's #0;
    # in g901 64 copies of the 5006 species should beat the native (901) block
    for rep in range(24):
        J.append(("pos_focal", 0, "p901", rep, 0, "g5006", "spatial"))
        J.append(("pos_native", 0, "native", rep, 0, "g5006", "spatial"))
        J.append(("pos_focal", 0, "species", rep, 0, "g901", "spatial"))
        J.append(("pos_native", 0, "native", rep, 0, "g901", "spatial"))
    # ladder in a garden of hand-written copiers (q_odd = 0.5): trapped(0) > trapped(1) > trapped(2) > non-copier
    for rep in range(12):
        for f in ("trapped0", "trapped1"):
            J.append(("ladder", 0, f, rep, 0, "copiers", "spatial"))
    return J


def key(j) -> str:
    return "|".join(map(str, j))


def run_job(j) -> dict:
    kind, seed, src, b, jj, gname, arm = j
    t0 = time.time()
    if kind == "noise":
        gi = (b + jj) % N_GARDEN
        G = garden(gname, gi)
        P = source(seed, src)
        blk, info = LA.make_block(P, np.random.default_rng([80, 9, seed, SOURCES[src], b]), geometry=False)
        aseed = [80, 1, seed, b, jj, gi, ARMCODE[arm], GCODE[gname]]
    elif kind in ("pos_focal", "pos_native"):
        gi = b % N_GARDEN
        G = garden(gname, gi)
        if kind == "pos_focal":
            blk = np.repeat(e42(5 if src == "species" else 0)[None], LA.K * LA.K, 0)
        else:
            blk, info = LA.make_block(G, np.random.default_rng([80, 8, b]), geometry=True)
        aseed = [80, 2, b, gi, GCODE[gname]]
    else:
        gi = b
        G = F.resident_copiers(np.random.default_rng([80, 7, b]), GSIDE * GSIDE, 0.5)
        x = {"trapped0": F.trapped(0), "trapped1": F.trapped(1), "trapped2": F.trapped(2),
             "noncopier": F.non_copier()}[src]
        blk = np.repeat(x[None], LA.K * LA.K, 0)
        aseed = [80, 3, b]
    r = LA.assay([blk], G, aseed, arm=arm, rounds=ROUNDS_MAX)
    return {"key": key(j), "kind": kind, "seed": seed, "src": src, "b": b, "j": jj, "garden": gname, "gi": gi,
            "arm": arm, "series": {t: v[0] for t, v in r["series"].items()}, "purity": r["purity"][0], "purity_anchor": r["purity_anchor"][0],
            "events": r["events"], "steps_per_pair": r["steps_per_pair"], "kin": LA.kin_share(G, blk),
            "sec": round(time.time() - t0, 1)}


def calibrate(workers: int) -> None:
    cache = OUT / "calib.jsonl"
    done = set()
    if cache.exists():
        done = {json.loads(line)["key"] for line in cache.read_text().splitlines()}
    todo = [j for j in jobs() if key(j) not in done]
    # slow kinds first
    todo.sort(key=lambda j: (j[0] != "pos_focal" and j[0] != "pos_native", j[0] != "ladder", j[5] != "g5006"))
    print(f"calibration: {len(done)} cached, {len(todo)} to run", flush=True)
    t0 = time.time()
    with Pool(workers) as pool, cache.open("a") as f:
        for i, r in enumerate(pool.imap_unordered(run_job, todo, chunksize=1)):
            f.write(json.dumps(r) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"  {i}/{len(todo)} {round(time.time() - t0)} s", flush=True)
    print("=== E80 CALIBRATION DONE", round(time.time() - t0), "s", flush=True)


# ---- analysis: controls, noise components, power ---------------------------------------------------

def score(series: dict, T: int, k2: int = LA.K * LA.K, linear: bool = False) -> float:
    n = series[str(T)]
    return float(n / k2 - 1) if linear else float(np.log((n + 1) / (k2 + 1)))


def load_calib() -> list[dict]:
    return [json.loads(line) for line in (OUT / "calib.jsonl").read_text().splitlines()]


def components(rows: list[dict], T: int, garden: str = "g5006", arm: str = "spatial", linear: bool = False) -> dict:
    """Variance components of the per-replicate score: assay (same block, different seeds), block (between blocks
    of one snapshot, beyond assay noise), continuation (M vs M' per soup, beyond sampling)."""
    sel = [r for r in rows if r["kind"] == "noise" and r["garden"] == garden and r["arm"] == arm]
    tab = {}
    for r in sel:
        tab.setdefault((r["seed"], r["src"], r["b"]), {})[r["j"]] = score(r["series"], T, linear=linear)
    seeds = sorted({k[0] for k in tab})
    nb = max(k[2] for k in tab) + 1
    ns = max(len(v) for v in tab.values())
    within = [np.var(list(v.values()), ddof=1) for v in tab.values() if len(v) > 1]
    s2_assay = float(np.mean(within)) if within else float("nan")
    bmeans = {k: np.mean(list(v.values())) for k, v in tab.items()}
    between = []
    for seed in seeds:
        for src in ("early", "M", "Mp"):
            m = [bmeans[(seed, src, b)] for b in range(nb) if (seed, src, b) in bmeans]
            if len(m) > 1:
                between.append(np.var(m, ddof=1))
    s2_block = max(float(np.mean(between)) - s2_assay / ns, 0.0) if between else float("nan")
    # paired M' - M per soup (common random numbers: same b, j)
    dprime, dpair_var = {}, []
    for seed in seeds:
        dd = [tab[(seed, "Mp", b)][j] - tab[(seed, "M", b)][j] for b in range(nb) for j in range(ns)
              if (seed, "Mp", b) in tab and j in tab[(seed, "Mp", b)] and (seed, "M", b) in tab and j in tab[(seed, "M", b)]]
        dprime[seed] = float(np.mean(dd))
        dpair_var.append(np.var(dd, ddof=1))
    n_rep = nb * ns
    # paired differences decomposed by block: within-block (assay, across seeds) and between-block components
    s2_adiff, s2_bdiff = [], []
    for seed in seeds:
        per_b = [[tab[(seed, "Mp", b)][j] - tab[(seed, "M", b)][j] for j in range(ns)] for b in range(nb)]
        s2_adiff.append(np.mean([np.var(x, ddof=1) for x in per_b]) if ns > 1 else np.nan)
        s2_bdiff.append(np.var([np.mean(x) for x in per_b], ddof=1))
    s2_adiff = float(np.mean(s2_adiff)) if ns > 1 else 0.0
    s2_bdiff = max(float(np.mean(s2_bdiff)) - s2_adiff / ns, 0.0)
    samp = s2_bdiff / nb + s2_adiff / (nb * ns)       # sampling variance of one soup's mean paired difference
    var_dp = float(np.var(list(dprime.values()), ddof=1))
    s2_cont_diff = max(var_dp - samp, 0.0)            # variance of the true per-soup M' - M difference
    early_minus_M = {seed: float(np.mean([bmeans[(seed, "M", b)] - bmeans[(seed, "early", b)] for b in range(nb)]))
                     for seed in seeds}
    means = {f"{seed}/{src}": round(float(np.mean([bmeans[(seed, src, b)] for b in range(nb)])), 3)
             for seed in seeds for src in ("early", "M", "Mp")}
    return {"T": T, "garden": garden, "arm": arm, "linear": linear, "blocks": nb, "seeds_per_block": ns,
            "s2_assay": s2_assay, "s2_block": s2_block, "var_paired_rep": float(np.mean(dpair_var)),
            "dprime": dprime, "mean_dprime": float(np.mean(list(dprime.values()))), "sd_dprime": var_dp ** 0.5,
            "sampling_var_dprime": samp, "s2_cont_diff": s2_cont_diff, "s2_block_diff": s2_bdiff,
            "s2_assay_diff": s2_adiff, "zero": 0.0,
            "p_dprime_two_sided": LA.signflip_p(list(dprime.values()), two_sided=True),
            "M_minus_early": early_minus_M, "means": means}


def power(sd_d: float, n: int, alpha: float = 0.05, sims: int = 2000, seed: int = 0) -> dict:
    """Mean d with 50% / 80% power for the one-sided test at n soups, d_k ~ N(mu, sd_d): the exact sign-flip test
    (simulated, common random draws) for n <= 12, the one-sided t-test (noncentral t, exact) above, which the
    sign-flip test approaches."""
    from scipy.stats import nct, t as tdist
    out = {"test": "sign-flip" if n <= 12 else "t"}
    if n <= 12:
        S = (((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1).astype(float)
        Z = np.random.default_rng(seed).normal(0, 1, (sims, n))

        def pw(mu):
            D = mu + sd_d * Z
            tot = np.abs(D) @ S.T
            p = (tot >= D.sum(1, keepdims=True) - 1e-12).mean(1)
            return float((p < alpha).mean())
    else:
        tc = tdist.ppf(1 - alpha, n - 1)

        def pw(mu):
            return float(nct.sf(tc, n - 1, mu / (sd_d / np.sqrt(n))))
    for target in (0.5, 0.8):
        lo, hi = 0.0, 6 * sd_d
        for _ in range(16):
            mid = (lo + hi) / 2
            if pw(mid) >= target:
                hi = mid
            else:
                lo = mid
        out[f"mde_{int(target * 100)}"] = round(hi, 3)
    return out


def sd_design(c: dict, r: int, s: int, cont: str = "s2_cont_diff") -> float:
    """SD of one soup's d (S - M, r blocks x s seeds per arm, common random numbers), assuming the true per-soup
    S - M difference varies between continuations as much as M' - M does (continuation noise)."""
    return float(np.sqrt(c[cont] + c["s2_block_diff"] / r + c["s2_assay_diff"] / (r * s)))


def null_fpr(rows: list[dict], T: int, garden: str = "g5006", splits: int = 2000, seed: int = 80) -> dict:
    """Selection-aware null: within each soup, the M and M' blocks (same process, blocks drawn at random) are pooled
    and split at random into two labelled halves of equal size; one-sided sign-flip p of the half difference across
    the 7 soups. The rate of p < 0.05 should be <= 0.05 (exact test: 0.047 at most). Also the arm-label permutation
    of the real M' - M contrast."""
    sel = [r for r in rows if r["kind"] == "noise" and r["garden"] == garden and r["arm"] == "spatial"
           and r["src"] in ("M", "Mp")]
    by = {}
    for r in sel:
        by.setdefault(r["seed"], {}).setdefault((r["src"], r["b"]), []).append(score(r["series"], T))
    rng = np.random.default_rng(seed)
    ps = []
    for _ in range(splits):
        d = []
        for sd, blocks in by.items():
            m = np.array([np.mean(v) for v in blocks.values()])
            idx = rng.permutation(len(m))
            d.append(m[idx[: len(m) // 2]].mean() - m[idx[len(m) // 2:]].mean())
        ps.append(LA.signflip_p(d))
    ps = np.array(ps)
    return {"T": T, "splits": splits, "fpr_0.05": round(float((ps < 0.05).mean()), 4),
            "fpr_0.10": round(float((ps < 0.10).mean()), 4)}


def verdict_probs(sd: float, n: int, mu: float, delta_star: float, sims: int = 20000, seed: int = 1) -> dict:
    """Probabilities of the pre-registered verdicts (pass / fail / undecided) under d_k ~ N(mu, sd) and an
    independent seed null M' - M ~ N(0, sd), exact sign-flip tests, n <= 12."""
    from scipy.stats import t as tdist
    rng = np.random.default_rng(seed)
    S = (((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1).astype(float)
    D, N = rng.normal(mu, sd, (sims, n)), rng.normal(0, sd, (sims, n))
    p = ((np.abs(D) @ S.T) >= D.sum(1, keepdims=True) - 1e-12).mean(1)
    pn = ((np.abs(N) @ S.T) >= np.abs(N.sum(1, keepdims=True)) - 1e-12).mean(1)
    up = D.mean(1) + tdist.ppf(0.975, n - 1) * D.std(1, ddof=1) / np.sqrt(n)
    ps = (p < 0.05) & (D.mean(1) > 0) & (pn >= 0.05)
    fl = ~ps & (up < delta_star)
    return {"pass": round(float(ps.mean()), 3), "fail": round(float(fl.mean()), 3),
            "undecided": round(float(1 - ps.mean() - fl.mean()), 3)}


# cost model for new soups (h = 64 head-start rule, 2^14 programs on a 128 x 128 torus), measured in this groundwork:
# post-jump ~0.6 s per round per continuation under 11-12 process load (spatial fork 0.62 s at 5,470 steps per pair);
# pre-fork (jump + 2,000 rounds) ~0.4 CPU-h; lattice assays ~0.5 CPU-h per soup (5 groups x 64 assays + secondaries)
SEC_ROUND, PREFORK_H, ASSAY_H, CPU = 0.6, 0.4, 0.5, 11


def cost(n: int, H: int, arms: int = 3) -> dict:
    cpu_h = n * (PREFORK_H + arms * H * SEC_ROUND / 3600 + ASSAY_H)
    return {"soups": n, "rounds_per_arm": H, "arms": arms, "cpu_h": round(cpu_h, 1),
            "wall_h_11_workers": round(cpu_h / CPU, 1)}


def headline(rows: list[dict]) -> dict:
    """The numbers the pre-registration fixes: primary garden g901, linear score (relative area change) at T = 64,
    r = 16 blocks x s = 4 seeds; positive effect, noise components, MDE, verdict probabilities, costed options."""
    h = {}
    sp = {r["b"]: r for r in rows if r["kind"] == "pos_focal" and r["garden"] == "g901"}
    na = {r["b"]: r for r in rows if r["kind"] == "pos_native" and r["garden"] == "g901"}
    for T in (32, 64, 128):
        for lin in (False, True):
            d = np.array([score(sp[b]["series"], T, linear=lin) - score(na[b]["series"], T, linear=lin) for b in sp])
            c = components(rows, T, "g901", "spatial", linear=lin)
            c2 = components(rows, T, "g5006", "spatial", linear=lin)
            h[f"T{T}/{'linear' if lin else 'log'}"] = {
                "positive_mean_d": round(float(d.mean()), 3), "positive_sd": round(float(d.std(ddof=1)), 3),
                "positive_ahead": int((d > 0).sum()), "positive_n": len(d),
                "g901_sd_dprime": round(c["sd_dprime"], 3), "g901_var_paired_rep": round(c["var_paired_rep"], 3),
                "g901_s2_cont": round(c["s2_cont_diff"], 3), "g901_dprime": {str(k): round(v, 3) for k, v in c["dprime"].items()},
                "g901_mean_dprime": round(c["mean_dprime"], 3), "g901_p_dprime": c["p_dprime_two_sided"],
                "g5006_sd_dprime": round(c2["sd_dprime"], 3), "g5006_s2_cont": round(c2["s2_cont_diff"], 3),
                "g5006_s2_assay_diff": round(c2["s2_assay_diff"], 3), "g5006_s2_block_diff": round(c2["s2_block_diff"], 3),
                "ratio_positive_to_sd_dprime": round(float(d.mean() / c["sd_dprime"]), 2)}
    c = components(rows, 64, "g901", "spatial", linear=True)
    sd = float(np.sqrt(c["s2_cont_diff"] + c["var_paired_rep"] / 64))
    delta = round(float(h["T64/linear"]["positive_mean_d"]) / 2, 2)
    h["primary_design"] = {"garden": "g901", "score": "linear", "T": 64, "r": 16, "s": 4, "sd_d": round(sd, 3),
                           "delta_star": delta,
                           "mde": {n: power(sd, n) for n in (7, 10, 16, 24, 32, 40, 48)},
                           "verdicts_n7": {str(mu): verdict_probs(sd, 7, mu, delta) for mu in (0.0, delta, 2 * delta)}}
    from scipy.stats import nct, t as tdist
    h["holm_level_power"] = {n: {str(mu): round(float(nct.sf(tdist.ppf(1 - 0.002, n - 1), n - 1, mu / (sd / np.sqrt(n)))), 3)
                                 for mu in (delta, 2 * delta)} for n in (16, 24, 32, 40, 48)}
    # selection-aware null on the primary score: random halves of the M and M' blocks per soup
    sel = [r for r in rows if r["kind"] == "noise" and r["garden"] == "g901" and r["arm"] == "spatial" and r["src"] in ("M", "Mp")]
    by = {}
    for r in sel:
        by.setdefault(r["seed"], []).append(score(r["series"], 64, linear=True))
    rng = np.random.default_rng(80)
    ps = []
    for _ in range(2000):
        d = []
        for v in by.values():
            v = np.array(v)
            i = rng.permutation(len(v))
            d.append(v[i[: len(v) // 2]].mean() - v[i[len(v) // 2:]].mean())
        ps.append(LA.signflip_p(d))
    h["null_fpr_primary_score"] = round(float((np.array(ps) < 0.05).mean()), 4)
    h["costs"] = {"option1_under_12h": cost(16, 10000), "option2_powered": cost(40, 10000),
                  "option2_powered_H20000": cost(40, 20000), "option1_alt_24_soups_H5000": cost(24, 5000)}
    return h


def analyse(out: str | None) -> dict:
    rows = load_calib()
    res = {"n_assays": len(rows), "cpu_seconds": round(sum(r["sec"] for r in rows)),
           "max_kin": max(r["kin"] for r in rows if r["kind"] == "noise"),
           "kin_by_garden": {g: max([r["kin"] for r in rows if r["kind"] == "noise" and r["garden"] == g] or [0])
                             for g in ("g5006", "g901", "random")}}
    Ts = [16, 32, 64, 96, 128, 192]
    # positives: species vs native per garden and horizon (paired by replicate)
    pos = {}
    for g in ("g5006", "g901"):
        sp = {r["b"]: r for r in rows if r["kind"] == "pos_focal" and r["garden"] == g}
        na = {r["b"]: r for r in rows if r["kind"] == "pos_native" and r["garden"] == g}
        both = sorted(set(sp) & set(na))
        pos[g] = {}
        for T in Ts:
            sign = -1 if g == "g5006" else 1      # expected fitter: native in g5006, the species in g901
            d = sign * np.array([score(sp[b]["series"], T) - score(na[b]["series"], T) for b in both])
            pos[g][T] = {"n": len(d), "mean_d": round(float(d.mean()), 3), "sd": round(float(d.std(ddof=1)), 3),
                         "z": round(float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))), 2),
                         "fitter_ahead": int((d > 0).sum()),
                         "mean_focal": round(float(np.mean([score(sp[b]["series"], T) for b in both])), 3),
                         "mean_native": round(float(np.mean([score(na[b]["series"], T) for b in both])), 3)}
        pos[g]["purity_focal"] = round(float(np.mean([sp[b]["purity"] or 0 for b in both])), 3)
    res["positive_species"] = pos
    lad = {}
    for f in ("trapped0", "trapped1"):
        rr = [r for r in rows if r["kind"] == "ladder" and r["src"] == f]
        lad[f] = {T: round(float(np.mean([score(r["series"], T) for r in rr])), 3) for T in Ts}
    res["ladder"] = lad
    comp = {}
    for g, arm in (("g5006", "spatial"), ("g5006", "mixed"), ("g901", "spatial"), ("random", "spatial")):
        for T in Ts:
            try:
                comp[f"{g}/{arm}/{T}"] = components(rows, T, g, arm)
            except (ValueError, KeyError, ZeroDivisionError):
                pass
        comp[f"{g}/{arm}/128/linear"] = components(rows, 128, g, arm, linear=True)
    res["components"] = comp
    res["null_fpr"] = {T: null_fpr(rows, T) for T in (32, 64, 128)}
    # minimum detectable mean d (one-sided exact sign-flip, alpha 0.05) for the primary design, by horizon
    des = {}
    for T in (32, 64, 128):
        c = comp[f"g5006/spatial/{T}"]
        for r, s_ in ((8, 3), (16, 4), (32, 4)):
            for n in (7, 10, 16, 24, 32):
                sd = sd_design(c, r, s_)
                des[f"T{T}/r{r}/s{s_}/n{n}"] = {"sd_d": round(sd, 3), **power(sd, n)}
            des[f"T{T}/r{r}/s{s_}/n7/assay_only"] = {"sd_d": round(sd_design(c, r, s_, "zero"), 3),
                                                      **power(sd_design(c, r, s_, "zero"), 7)} if "zero" in c else None
    res["design"] = des
    res["headline"] = headline(rows)
    if out:
        Path(out).write_text(json.dumps(res, indent=1, default=float))
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gardens", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--power", action="store_true")
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.gardens:
        specs = [(g, i) for g in GARDENS for i in range(N_GARDEN)]
        with Pool(min(a.workers, len(specs))) as pool:
            res = pool.map(_garden_job, specs, chunksize=1)
        (OUT / "gardens.json").write_text(json.dumps(res, indent=1))
        for r in res:
            print(r["garden"], r["i"], [(x["t"], x["nbr_identity"], x["distinct"], x["steps_per_pair"])
                                        for x in r["series"]], flush=True)
        print("=== E80 GARDENS DONE", flush=True)
    if a.calibrate:
        calibrate(a.workers)
    if a.power:
        r = analyse(a.out)
        print(json.dumps({k: v for k, v in r.items() if k != "components"}, indent=1, default=float))


if __name__ == "__main__":
    main()
