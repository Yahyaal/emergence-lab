"""E-81 (docs/data/e81-preregistration.md): does later code become fitter, and shorter, when program length can
change? Variable-length BFF (BFF-VL, scripts/bffvl.py, D-070), soups from random code.

  soups   W = 2^20 bytes of random code, BFF-VL rule (head1 at the partner, heads halt at the tape ends, cut at the
          marker '!' and at 128 bytes, no piece < 4 bytes), mutation 0.00024. Checkpoints every 50 epochs: the copy
          screen (`bffvl.is_copier`, 4 random 128-byte partners) on the 40 most common distinct programs. The jump T is
          the first checkpoint with >= 1 copier among them whose checkpoint 500 epochs later has copier families
          (of the top-10 copiers) holding >= 25% of the bytes. Early sample: the copiers at T (up to 5, commonest
          first); mid: at T + 1000; late: at T + 10000; late2: at T + 20000. A soup with no confirmed jump by epoch 10,000 is excluded
          and replaced by the next spare seed.
  races   head-to-head assay `bffvl_assay.compete` (random-code background of 2^16 bytes, ~1,024 bytes of each
          candidate, no mutation, 8 epochs, 8 replicates per pair); s = log byte ratio change, positive = the later
          candidate ahead. Each later copier against each earlier one (identical pairs score 0 and are counted).
  P1      d1 = mean s(mid vs early) per soup; one-sided exact sign-flip test over soups (Monte Carlo above 16).
  P2      d2 = mean s(late vs mid) per soup; the same test.
  P3      d3 = mean s(late2 vs late) per soup; the same test (does adaptation continue once copiers are minimal?).
  gate    the instrument controls (`bffvl_assay.controls`) and the seeded positive (soups seeded with a 48-byte
          padded copier must shorten and their descendants must beat the ancestor) pass before any race is scored.
  2ndary  copier length (byte-weighted mean length of the top-10 copier families) at T, T+1000, T+10000, T+20000; its change
          against a noexec fork of the same T snapshot (no execution: drift of the cut rule and mutation only).

    systemd-inhibit --what=sleep:idle --why="E-81" setsid nohup env PYTHONPATH=.:scripts \
        python scripts/e81_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e81.json \
        > runs/e81/run/run.log 2>&1 &
    PYTHONPATH=.:scripts python scripts/e81_run.py --pilot 9401-9408 --workers 8 --out runs/e81/pilot2/out.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import traceback
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import t as tdist

sys.path.insert(0, str(Path(__file__).parent))
import bffvl as V  # noqa: E402
import bffvl_assay as A  # noqa: E402

# ---- fixed by the pre-registration --------------------------------------------------------------
EVERY, TOPK, TOPFAM = 50, 40, 10
CONFIRM_DT, CONFIRM_SHARE, MAX_WAIT = 500, 0.25, 10000
D1, D2, D3 = 1000, 10000, 20000
K, R, E_RACE, W_RACE, START_BYTES = 5, 8, 8, 2 ** 16, 1024
SEEDS = list(range(8101, 8141))          # 40 primary soups
SPARES = list(range(8141, 8173))         # used in order if a primary soup does not jump by MAX_WAIT
N_MIN = 30                               # fewer admitted soups than this: the run is reported as undecided
SEEDED_SEEDS, ANC_LEN, SEEDED_EPOCHS = [8201, 8202, 8203, 8204], 48, 1000
DELTA = 0.79                             # half the 6- vs 7-byte floor step at E = 8 (groundwork, J-097)
OUT = Path("runs/e81/run")
CFG = {"dry": False, "max_wait": MAX_WAIT, "d1": D1, "d2": D2, "d3": D3}


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(OUT / "progress.log", "a") as f:
        f.write(line + "\n")


def save_json(path: Path, obj) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    os.replace(tmp, path)


# ---- census -----------------------------------------------------------------------------------------
def census(s: V.Soup, seed: int) -> dict:
    """Copiers among the TOPK most common distinct programs (commonest first) and the byte share of the families of
    the first TOPFAM of them; byte-weighted mean length of those families."""
    top = Counter(map(bytes, s.programs())).most_common(TOPK)
    cop = [(b, c) for i, (b, c) in enumerate(top) if V.is_copier(np.frombuffer(b, np.uint8), seed * 1000 + i)]
    share, flen = 0.0, None
    if cop:
        fam = np.zeros(s.n, bool)
        for b, _ in cop[:TOPFAM]:
            fam |= s.members(np.frombuffer(b, np.uint8))
        tot = int(s.lens[fam].sum())
        share = tot / int(s.lens.sum())
        flen = float((s.lens[fam].astype(float) ** 2).sum() / tot) if tot else None
    return {"copiers": [(b.hex(), c) for b, c in cop], "share": round(share, 4),
            "fam_len": None if flen is None else round(flen, 2), "n": s.n,
            "mean_len": round(float(s.lens.mean()), 2), "steps_pair": round(s.last_steps / max(1, s.n // 2), 1)}


def snapshot(s: V.Soup) -> dict:
    return {"buf": s.buf.copy(), "lens": s.lens.copy(), "rng": s.rng.bit_generator.state, "epochs": s.epochs}


def restore(snap: dict, mode: str = "bff") -> V.Soup:
    rng = np.random.default_rng()
    rng.bit_generator.state = snap["rng"]
    s = V.Soup(buf=snap["buf"], lens=snap["lens"], rng=rng, mode=mode)
    s.epochs = snap["epochs"]
    return s


# ---- one soup ---------------------------------------------------------------------------------------
def soup_job(seed: int) -> dict:
    path = OUT / "soups" / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    s = V.Soup(rng=np.random.default_rng([81, seed]))
    traj, cands, T, res = [], [], None, {"seed": seed}
    max_wait, d1, d2, d3 = CFG["max_wait"], CFG["d1"], CFG["d2"], CFG["d3"]
    while True:
        e = s.epochs
        if e % EVERY == 0:
            c = census(s, seed * 100003 + e)
            traj.append({"epoch": e, **{k: c[k] for k in ("share", "fam_len", "n", "mean_len", "steps_pair")},
                         "ncop": len(c["copiers"]),
                         "shortest": min((len(h) // 2 for h, _ in c["copiers"]), default=None)})
            if T is None:
                if c["copiers"] and e <= max_wait:
                    cands.append((e, snapshot(s), c))
                while cands and e >= cands[0][0] + CONFIRM_DT:
                    ce, snap, cc = cands.pop(0)
                    hit = next((r for r in traj if r["epoch"] == ce + CONFIRM_DT), None)
                    if hit and hit["share"] >= CONFIRM_SHARE:
                        T = ce
                        res["T"] = T
                        res["early"] = cc
                        np.savez_compressed(OUT / "soups" / f"{seed}-T.npz", buf=snap["buf"], lens=snap["lens"])
                        res["noexec"] = noexec_fork(snap, seed, d1, [h for h, _ in cc["copiers"]])
                        cands = []
                        break
                if T is None and not cands and e > max_wait:
                    res["T"] = None
                    break
            if T is not None and e == T + d1:
                res["mid"] = c
                np.savez_compressed(OUT / "soups" / f"{seed}-mid.npz", buf=s.buf, lens=s.lens)
            if T is not None and e == T + d2:
                res["late"] = c
                np.savez_compressed(OUT / "soups" / f"{seed}-late.npz", buf=s.buf, lens=s.lens)
            if T is not None and e == T + d3:
                res["late2"] = c
                np.savez_compressed(OUT / "soups" / f"{seed}-late2.npz", buf=s.buf, lens=s.lens)
                break
        s.epoch()
    res["traj"] = traj
    res["seconds"] = round(time.time() - t0)
    save_json(path, res)
    return res


def fam_len(s: V.Soup, hexes: list) -> float | None:
    """Byte-weighted mean length of the programs in the families of the given copiers."""
    fam = np.zeros(s.n, bool)
    for h in hexes[:TOPFAM]:
        fam |= s.members(np.frombuffer(bytes.fromhex(h), np.uint8))
    tot = int(s.lens[fam].sum())
    return round(float((s.lens[fam].astype(float) ** 2).sum() / tot), 2) if tot else None


def noexec_fork(snap: dict, seed: int, d1: int, hexes: list) -> dict:
    """Length null: the T snapshot continued d1 epochs with nothing running (cut rule and mutation only). fam_len is
    measured on the families of the T copiers (in noexec they cannot spread, so the census would find none)."""
    s = restore(snap, mode="noexec")
    s.rng = np.random.default_rng([81, seed, 7])
    before = fam_len(s, hexes)
    for _ in range(d1):
        s.epoch()
    c = census(s, seed * 100003 + 7)
    c["fam_len_T_families"], c["fam_len_T_families_before"] = fam_len(s, hexes), before
    return c


def fecundity(hexes: list, seed: int, partners: int = 16) -> dict:
    """Descriptive ("faster"): mean complete copies and steps per run of each copier against random 128-byte
    partners (copier first); weighted equally over the sample."""
    cps, sts = [], []
    rng = np.random.default_rng([81, seed, 11])
    for h in hexes:
        x = np.frombuffer(bytes.fromhex(h), np.uint8)
        c = V.screen(x, seed * 7919 + len(cps), partners=partners)[1] / partners
        st = []
        for _ in range(partners):
            t = np.concatenate([x, rng.integers(0, 256, V.LMAX, dtype=np.uint8)])
            st.append(V.lib().vl_run(t.ctypes.data, len(t), V.STEPS, len(x), V.EDGE))
        cps.append(c)
        sts.append(float(np.mean(st)))
    return {"copies": round(float(np.mean(cps)), 3) if cps else None,
            "steps": round(float(np.mean(sts)), 1) if sts else None}


# ---- races -------------------------------------------------------------------------------------------
def race_job(arg) -> tuple:
    key, a_hex, b_hex, seedkey = arg
    a, b = np.frombuffer(bytes.fromhex(a_hex), np.uint8), np.frombuffer(bytes.fromhex(b_hex), np.uint8)
    if a_hex == b_hex:
        return key, {"identical": True, "s": 0.0}
    r = A.compete(a, b, np.random.default_rng(seedkey), reps=R, epochs=E_RACE, w=W_RACE, start_bytes=START_BYTES)
    return key, {"identical": False, "s": r["s"], "ss": r["ss"], "a_wins": r["a_wins"], "b_wins": r["b_wins"]}


def race_plan(res: dict, later: str, earlier: str, code: int) -> list:
    la = [h for h, _ in res[later]["copiers"][:K]]
    ea = [h for h, _ in res[earlier]["copiers"][:K]]
    return [((res["seed"], later, earlier, i, j), a, b, [81, res["seed"], code, i, j])
            for i, a in enumerate(la) for j, b in enumerate(ea)]


# ---- seeded positive (gate) -------------------------------------------------------------------------
def ancestor(seed: int) -> np.ndarray:
    return V.hand_copier(ANC_LEN, np.random.default_rng([81, seed, 1]), fill=None)


def seeded_job(seed: int) -> dict:
    path = OUT / "seeded" / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    rng = np.random.default_rng([81, seed])
    anc = ancestor(seed)
    bg = A.background(rng, V.W - 64 * ANC_LEN)
    s = V.Soup.from_programs(bg + [anc.copy() for _ in range(64)], rng=rng)
    traj = []
    for e in range(SEEDED_EPOCHS + 1):
        if e % 100 == 0:
            c = census(s, seed * 100003 + e)
            traj.append({"epoch": e, "share": c["share"], "fam_len": c["fam_len"], "ncop": len(c["copiers"]),
                         "shortest": min((len(h) // 2 for h, _ in c["copiers"]), default=None),
                         "n": c["n"], "mean_len": c["mean_len"]})
        if e < SEEDED_EPOCHS:
            s.epoch()
    top = c["copiers"][:K]
    races = []
    for i, (h, _) in enumerate(top):
        r = A.compete(np.frombuffer(bytes.fromhex(h), np.uint8), anc, np.random.default_rng([81, seed, 9, i]),
                      reps=R, epochs=E_RACE, w=W_RACE, start_bytes=START_BYTES)
        races.append({"len": len(h) // 2, "s": r["s"], "a_wins": r["a_wins"], "b_wins": r["b_wins"]})
    out = {"seed": seed, "ancestor": anc.tobytes().hex(), "traj": traj, "final": c, "races": races,
           "d": float(np.mean([r["s"] for r in races])) if races else None}
    save_json(path, out)
    return out


# ---- statistics ---------------------------------------------------------------------------------------
def signflip_p(d, two_sided: bool = False, n_mc: int = 200000, seed: int = 0) -> float:
    d = np.asarray(d, float)
    if len(d) <= 16:
        S = ((np.arange(2 ** len(d))[:, None] >> np.arange(len(d))) & 1) * 2 - 1
    else:
        S = np.random.default_rng(seed).choice([-1, 1], (n_mc, len(d)))
    tot = (S * np.abs(d)).sum(1)
    if two_sided:
        return float(((np.abs(tot) >= abs(d.sum()) - 1e-12).sum() + (len(d) > 16)) / (len(S) + (len(d) > 16)))
    return float(((tot >= d.sum() - 1e-12).sum() + (len(d) > 16)) / (len(S) + (len(d) > 16)))


def summarize(d, delta=None) -> dict:
    d = np.asarray(d, float)
    n = len(d)
    m, sd = float(d.mean()), float(d.std(ddof=1)) if n > 1 else float("nan")
    half = float(tdist.ppf(0.975, n - 1) * sd / np.sqrt(n)) if n > 1 else float("nan")
    out = {"n": n, "mean": round(m, 4), "sd": round(sd, 4), "ci95": [round(m - half, 4), round(m + half, 4)],
           "p_one_sided": signflip_p(d), "p_two_sided": signflip_p(d, two_sided=True), "positive": int((d > 0).sum())}
    if delta is not None:
        out["delta"] = delta
        # fail whenever the whole interval lies below delta (even if p < 0.05: detectable but negligible)
        out["verdict"] = ("fail" if m + half < delta else
                          "pass" if out["p_one_sided"] < 0.05 else "undecided")
        out["below_delta_but_significant"] = bool(m + half < delta and out["p_one_sided"] < 0.05)
    return out


def soup_d(res: dict, races: dict, later: str, earlier: str) -> float:
    vals = [v["s"] for k, v in races.items() if k[0] == res["seed"] and k[1] == later and k[2] == earlier]
    return float(np.mean(vals)) if vals else float("nan")


# ---- driver --------------------------------------------------------------------------------------------
def drive(workers: int) -> dict:
    out = {"experiment": "E-81", "config": {"EVERY": EVERY, "TOPK": TOPK, "CONFIRM_DT": CONFIRM_DT,
                                            "CONFIRM_SHARE": CONFIRM_SHARE, "MAX_WAIT": CFG["max_wait"],
                                            "D1": CFG["d1"], "D2": CFG["d2"], "D3": CFG["d3"], "DELTA": DELTA, "K": K, "R": R, "E_RACE": E_RACE,
                                            "W_RACE": W_RACE, "START_BYTES": START_BYTES, "rule": {
                                                "W": V.W, "MARKER": V.MARKER, "LMIN": V.LMIN, "LMAX": V.LMAX,
                                                "MUT": V.MUT, "STEPS": V.STEPS, "EDGE": V.EDGE}}}
    with Pool(workers) as pool:
        # the seeded positive and the soups start together; the instrument controls run here meanwhile. No race is
        # scored before the gate (controls + seeded positive) has passed.
        log("gate (controls, seeded positive) and soups started")
        seeded = pool.map_async(seeded_job, SEEDED_SEEDS)
        soups = pool.imap_unordered(soup_job, list(SEEDS))
        ctrl = A.controls()
        seeded = seeded.get()
        out["controls"] = [{"name": n, "ok": bool(o), "detail": d} for n, o, d in ctrl]
        out["seeded"] = seeded
        g = gate(ctrl, seeded)
        out["gate"] = g
        log(f"gate passed={g['passed']} (controls {g['controls_passed']}, seeded shorter {g['seeded_shorter']}/4, "
            f"ahead {g['seeded_ahead']}/4)")
        admitted, excluded = [], []
        spare = list(SPARES)
        for res in soups:
            (admitted if res.get("T") is not None else excluded).append(res)
            log(f"soup {res['seed']} T={res.get('T')} sec={res.get('seconds')}")
        while len(admitted) < len(SEEDS) and spare and excluded:
            need = len(SEEDS) - len(admitted)
            batch, spare = spare[:need], spare[need:]
            for res in pool.imap_unordered(soup_job, batch):
                (admitted if res.get("T") is not None else excluded).append(res)
                log(f"spare {res['seed']} T={res.get('T')}")
        admitted.sort(key=lambda r: r["seed"])
        out["admitted"] = [r["seed"] for r in admitted]
        out["excluded"] = [r["seed"] for r in excluded]
        if not g["passed"]:
            out["verdict"] = "gate failed: no race scored"
            return out
        plan = []
        for r in admitted:
            plan += race_plan(r, "mid", "early", 1) + race_plan(r, "late", "mid", 2) + race_plan(r, "late2", "late", 3)
        races = {}
        for key, v in pool.imap_unordered(race_job, plan, chunksize=4):
            races[key] = v
        log(f"races done: {len(races)}")
    d1 = [soup_d(r, races, "mid", "early") for r in admitted]
    d2 = [soup_d(r, races, "late", "mid") for r in admitted]
    d3 = [soup_d(r, races, "late2", "late") for r in admitted]
    out["P1"] = summarize(d1, DELTA)
    out["P2"] = summarize(d2, DELTA)
    out["P3"] = summarize(d3, DELTA)
    out["per_soup"] = [{"seed": r["seed"], "T": r["T"], "d1": d1[i], "d2": d2[i], "d3": d3[i],
                        "len_late2": r["late2"]["fam_len"], "late2": r["late2"]["copiers"][:K],
                        "len_early": r["early"]["fam_len"], "len_mid": r["mid"]["fam_len"],
                        "len_late": r["late"]["fam_len"], "len_noexec": r["noexec"].get("fam_len_T_families"),
                        "early": r["early"]["copiers"][:K], "mid": r["mid"]["copiers"][:K],
                        "late": r["late"]["copiers"][:K],
                        "fecundity": {w: fecundity([h for h, _ in r[w]["copiers"][:K]], r["seed"])
                                      for w in ("early", "mid", "late", "late2")},
                        "identical_pairs": {f"P{c}": sum(v["identical"] for k, v in races.items()
                                                         if k[0] == r["seed"] and k[1] == w)
                                            for c, w in ((1, "mid"), (2, "late"), (3, "late2"))}}
                       for i, r in enumerate(admitted)]
    out["races"] = [{"key": list(k), **v} for k, v in races.items()]
    out["secondary"] = secondaries(admitted)
    out["n_admitted"] = len(admitted)
    out["verdict"] = {p: out[p]["verdict"] for p in ("P1", "P2", "P3")}
    if len(admitted) < N_MIN:
        out["verdict"] = {p: "undecided (too few soups)" for p in ("P1", "P2", "P3")}
    return out


def secondaries(adm: list) -> dict:
    def diff(a, b):
        return [r[a]["fam_len"] - r[b]["fam_len"] for r in adm if r[a]["fam_len"] and r[b]["fam_len"]]
    s1 = diff("mid", "early")
    nx = [(r, r["noexec"].get("fam_len_T_families"), r["noexec"].get("fam_len_T_families_before")) for r in adm]
    s1n = [(r["mid"]["fam_len"] - r["early"]["fam_len"]) - (a - b) for r, a, b in nx
           if r["mid"]["fam_len"] and r["early"]["fam_len"] and a and b]
    s2 = diff("late", "mid")
    s3 = diff("late2", "late")
    return {"S1_len_mid_minus_early": summarize([-x for x in s1]) | {"raw_mean": float(np.mean(s1)) if s1 else None},
            "S1n_against_noexec": summarize([-x for x in s1n]) if len(s1n) > 1 else None,
            "S2_len_late_minus_mid": summarize([-x for x in s2]) if len(s2) > 1 else None,
            "S3_len_late2_minus_late": summarize([-x for x in s3]) if len(s3) > 1 else None,
            "noexec_change": [a - b for r, a, b in nx if a and b],
            "note": "summaries are of length decreases (positive = shorter later)"}


def gate(ctrl: list, seeded: list) -> dict:
    """Gate: every instrument control passes (`bffvl_assay.controls`), and >= 3 of the 4 seeded soups end with their
    commonest copier shorter than the ancestor and with their copiers ahead of the ancestor (d > 0). The bound DELTA
    is a fixed number (pre-registration), not taken from this run."""
    ok_ctrl = all(o for _, o, _ in ctrl)
    shorter = sum(1 for s in seeded if s["final"]["copiers"] and len(s["final"]["copiers"][0][0]) // 2 < ANC_LEN)
    ahead = sum(1 for s in seeded if s["d"] is not None and s["d"] > 0)
    step = next((d for n, o, d in ctrl if n.startswith("assay ladder at the floor")), None)
    return {"controls_passed": ok_ctrl, "seeded_shorter": shorter, "seeded_ahead": ahead,
            "passed": bool(ok_ctrl and shorter >= 3 and ahead >= 3), "delta": DELTA,
            "floor_step_detail": step}


def preregistered() -> bool:
    out = subprocess.run(["git", "log", "-1", "--format=%H", "--", "docs/data/e81-preregistration.md"],
                         capture_output=True, text=True)
    return bool(out.stdout.strip())


def main() -> None:
    global SEEDS, SPARES, SEEDED_SEEDS, OUT, N_MIN
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--pilot", default=None, help="a-b: pilot seeds (exploratory, never the registered seeds)")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    if a.pilot:
        lo, hi = map(int, a.pilot.split("-"))
        SEEDS, SPARES, SEEDED_SEEDS, N_MIN = list(range(lo, hi + 1)), [], [lo + 1000 + i for i in range(4)], 1
        if set(SEEDS) & set(range(8101, 8173)):
            sys.exit("pilot seeds overlap the registered seeds")
        OUT = Path(a.out).parent
    elif a.dry:
        CFG.update({"dry": True, "max_wait": 1500, "d1": 600, "d2": 900, "d3": 1100})
        SEEDS, SPARES, SEEDED_SEEDS, N_MIN = [9404, 9407], [8993], [8994, 8995, 8996, 8997], 1  # pilot jumpers
        OUT = Path("runs/e81/dry")
    elif not a.confirm:
        sys.exit("give --confirm (after the pre-registration commit), --pilot or --dry")
    elif not preregistered():
        sys.exit("docs/data/e81-preregistration.md is not committed: refusing to run")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "soups").mkdir(exist_ok=True)
    (OUT / "seeded").mkdir(exist_ok=True)
    for f in ("DONE", "FAILED"):
        (OUT / f).unlink(missing_ok=True)
    t0 = time.time()
    log(f"E-81 start (pilot={bool(a.pilot)}, dry={CFG['dry']}), commit "
        f"{subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
    try:
        res = drive(a.workers)
        res["seconds"] = round(time.time() - t0)
        Path(a.out).write_text(json.dumps(res, indent=1, default=float))
        (OUT / "DONE").write_text(json.dumps({"verdict": res.get("verdict"), "seconds": res["seconds"]}) + "\n")
        log(f"DONE verdict={res.get('verdict')} sec={res['seconds']}")
    except Exception:
        tb = traceback.format_exc()
        (OUT / "FAILED").write_text(tb)
        log("FAILED\n" + tb)
        raise


if __name__ == "__main__":
    main()
