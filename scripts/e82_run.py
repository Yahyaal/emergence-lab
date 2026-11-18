"""E-82 (docs/data/e82-preregistration.md): do parasites arise from random code when programs can borrow a persistent
neighbour's code, and does the soup then keep changing in a directed way (a host-parasite arms race)?
Rule: BFF-X, libmode neighbour (scripts/bffx.py, D-072). Instruments: scripts/bffx_assay.py (D-073).

  soups   W = 2^20 bytes of random code, mutation 0.00024. Census every 50 epochs: hosts = programs among the 40
          most common distinct ones that copy themselves with nothing to borrow (bffx.is_copier, libmode none, 4 of
          4 random 128-byte partners); host share = bytes of the families of the first 10 hosts. Jump T = the first
          checkpoint with >= 1 host whose checkpoint 500 epochs later has host share >= 0.05. No T by epoch 10,000:
          excluded, replaced by the next spare.
  samples at S1 = T + 1000, S2 = T + 5000, S3 = T + 10000: hosts = the 5 commonest hosts; parasites = the first 5
          programs, in order of commonness among the 40 commonest non-hosts, that the parasite detector
          (`bffx_assay.parasite_test`, pool = 4,096 programs drawn from the snapshot) calls "parasite".
  P1      (criterion, built in by construction) share of admitted soups with >= 1 verified parasite at S1, S2 and S3.
  P2      RQ = mean over i < j of q(P_j, H_i) - q(P_i, H_j) (later parasites on earlier hosts minus earlier
          parasites on later hosts; q = coverage, the share of a random 128-byte partner that the parasite, run
          first, fills with copies of itself with the host as its library, mean of 32 runs and of the 5 x 5 pairs).
          One-sided sign-flip test over soups (Monte Carlo, 200,000 patterns).
  P3      host resistance: d3 = q(P_1, H_1) - q(P_1, H_3) (do later hosts resist the earliest parasites?).
  gate    instrument controls (`bffx_assay.controls`) and the seeded positive (`e82_seeded.early`: 64 designed hosts
          and 64 designed parasites in random code; the parasite's family rebounds >= 2x in epochs 4-10 with the
          hosts and < 1x without them, in >= 3 of 4 seeds). Reported beside it: the none-arm null (4 soups under
          libmode none, parasites at S1).

    systemd-inhibit --what=sleep:idle --why="E-82" setsid nohup env PYTHONPATH=.:scripts \
        python scripts/e82_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e82.json \
        > runs/e82/run/run.log 2>&1 < /dev/null &
    PYTHONPATH=.:scripts python scripts/e82_run.py --pilot 9701-9710 --workers 11 --out runs/e82/protopilot/out.json
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
import bffx as X  # noqa: E402
import bffx_assay as A  # noqa: E402

# ---- fixed by the pre-registration --------------------------------------------------------------
EVERY, TOPK, TOPFAM = 50, 40, 10
CONFIRM_DT, CONFIRM_SHARE, MAX_WAIT = 500, 0.05, 10000
OFFS = (1000, 5000, 10000)
KH, KP, POOL, Q_TRIALS = 5, 5, 4096, 32
SEEDS = list(range(8301, 8341))          # 40 primary soups
SPARES = list(range(8341, 8373))
NULL_SEEDS = [8381, 8382, 8383, 8384]    # libmode none (nothing to borrow): parasite null at S1
GATE_SEEDS = (8391, 8392, 8393, 8394)    # seeded positive
N_MIN = 30
DELTA = 0.10                             # half the graded time-shift control (1 of 5 later hosts resistant: 0.2)
P1_PASS = 0.75
OUT = Path("runs/e82/run")
CFG = {"max_wait": MAX_WAIT, "offs": OFFS}


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(OUT / "progress.log", "a") as f:
        f.write(line + "\n")


def save_json(path: Path, obj) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    os.replace(tmp, path)


def hosts_of(s: X.Soup, key: int) -> tuple[list, float]:
    top = X.top_distinct(s, TOPK)
    hs = [(b, c) for i, (b, c) in enumerate(top)
          if X.is_copier(np.frombuffer(b, np.uint8), key * 1000 + i, libmode="none")]
    share = 0.0
    if hs:
        fam = np.zeros(s.n, bool)
        for b, _ in hs[:TOPFAM]:
            fam |= X.members(s.buf, s.lens, np.frombuffer(b, np.uint8))
        share = float(s.lens[fam].sum() / s.lens.sum())
    return hs, round(share, 4)


def sample(s: X.Soup, seed: int, tag: int) -> dict:
    """Hosts and verified parasites of a snapshot."""
    hs, share = hosts_of(s, seed * 100003 + 77 + tag)
    rng = np.random.default_rng([82, seed, tag])
    progs = s.programs()
    pool = [progs[i] for i in rng.choice(len(progs), min(POOL, len(progs)), replace=False)]
    hostset = {b for b, _ in hs}
    top = [(b, c) for b, c in X.top_distinct(s, TOPK + len(hs)) if b not in hostset][:TOPK]
    paras, verdicts, tests = [], [], []
    for b, c in top:
        if len(paras) >= KP:
            break
        r = A.parasite_test(np.frombuffer(b, np.uint8), pool, rng, libmode=s.libmode)
        r.pop("hosts", None)
        verdicts.append(r["verdict"])
        tests.append({"hex": b.hex(), "soup_count": c, **r})
        if r["verdict"] == "parasite":
            paras.append((b.hex(), c))
    fam = np.zeros(s.n, bool)
    for h, _ in paras:
        fam |= X.members(s.buf, s.lens, np.frombuffer(bytes.fromhex(h), np.uint8))
    return {"epoch": s.epochs, "hosts": [(b.hex(), c) for b, c in hs[:KH]], "host_share": share,
            "parasites": paras, "para_share": round(float(s.lens[fam].sum() / s.lens.sum()), 4),
            "verdicts": dict(Counter(verdicts)), "tests": tests, "n": s.n, "mean_len": round(float(s.lens.mean()), 2)}


def soup_job(arg) -> dict:
    seed, libmode = arg
    path = OUT / "soups" / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    s = X.Soup(rng=np.random.default_rng([82, seed]), libmode=libmode)
    traj, T, res, cands = [], None, {"seed": seed, "libmode": libmode}, []
    offs = CFG["offs"] if libmode == "neighbour" else CFG["offs"][:1]
    while True:
        e = s.epochs
        if e % EVERY == 0:
            hs, share = hosts_of(s, seed * 100003 + e)
            traj.append({"epoch": e, "share": share, "nhost": len(hs), "n": s.n, "mean_len": round(float(s.lens.mean()), 2),
                         "steps_pair": round(s.last_steps / max(1, s.n // 2), 1),
                         "shortest": min((len(b) for b, _ in hs), default=None)})
            if T is None:
                if hs and e <= CFG["max_wait"]:
                    cands.append(e)
                while cands and e >= cands[0] + CONFIRM_DT:
                    ce = cands.pop(0)
                    hit = next((r for r in traj if r["epoch"] == ce + CONFIRM_DT), None)
                    if hit and hit["share"] >= CONFIRM_SHARE:
                        T = res["T"] = ce
                        cands = []
                        break
                if T is None and not cands and e > CFG["max_wait"]:
                    res["T"] = None
                    break
            if T is not None and e - T in offs:
                k = offs.index(e - T)
                np.savez_compressed(OUT / "soups" / f"{seed}-S{k + 1}.npz", buf=s.buf, lens=s.lens)
                res[f"S{k + 1}"] = sample(s, seed, k + 1)
                if k == len(offs) - 1:
                    break
        s.epoch()
    res["traj"] = traj
    res["seconds"] = round(time.time() - t0)
    save_json(path, res)
    return res


def scores(res: dict) -> dict:
    """P2 and P3 for one admitted soup (parasites and hosts as bytes)."""
    seed = res["seed"]
    smp = []
    for k in (1, 2, 3):
        S = res.get(f"S{k}") or {}
        smp.append(([np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in S.get("parasites", [])],
                    [np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in S.get("hosts", [])]))
    ts = A.timeshift(smp, seed * 31 + 5, Q_TRIALS)
    Q = ts["Q"]
    d3 = None if Q[0][0] is None or Q[0][2] is None else round(Q[0][0] - Q[0][2], 4)
    return {"seed": seed, "Q": Q, "RQ": ts["RQ"], "d3": d3,
            "parasites_all": all(len(p) > 0 for p, _ in smp)}


def signflip(d: list, iters: int = 200000, seed: int = 82) -> float:
    d = np.asarray(d, float)
    obs = d.mean()
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(iters // 10000):
        sg = rng.choice([-1.0, 1.0], (10000, len(d)))
        hits += int(((sg * d).mean(1) >= obs - 1e-12).sum())
    return (hits + 1) / (iters + 1)


def verdict(d: list) -> dict:
    d = [x for x in d if x is not None]
    if len(d) < 2:
        return {"n": len(d), "verdict": "undecided"}
    m, sd = float(np.mean(d)), float(np.std(d, ddof=1))
    half = tdist.ppf(0.975, len(d) - 1) * sd / np.sqrt(len(d)) if sd > 0 else 0.0
    p = signflip(d)
    lo, hi = m - half, m + half
    v = "fail" if hi < DELTA else ("pass" if p < 0.05 else "undecided")
    return {"n": len(d), "mean": round(m, 4), "sd": round(sd, 4), "ci": [round(lo, 4), round(hi, 4)], "p": p,
            "positive": int(sum(x > 0 for x in d)), "zero": int(sum(x == 0 for x in d)), "verdict": v}


def gate(seeds=GATE_SEEDS) -> dict:
    """Instrument controls and the seeded positive (designed parasite spreads with designed hosts, not without)."""
    import e82_seeded as SD
    ctl = A.controls("neighbour")
    seeded = {}
    for sd in seeds:
        r = {arm: SD.early(arm, sd) for arm in ("HP", "P")}
        seeded[sd] = r
    ok_seeded = sum(v["HP"]["rebound"] >= 2 and v["P"]["rebound"] < 1 for v in seeded.values())
    return {"controls": [(n, bool(o), d) for n, o, d in ctl], "controls_pass": all(o for _, o, _ in ctl),
            "seeded": seeded, "seeded_ok": ok_seeded, "pass": all(o for _, o, _ in ctl) and ok_seeded >= 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--pilot", default=None, help="seed range a-b (pilot seeds only)")
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    global OUT
    if a.pilot:
        OUT = Path(a.out).parent
    (OUT / "soups").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {"experiment": "E-82", "commit": commit, "pilot": bool(a.pilot)}
    if a.confirm:
        g = gate()
        out["gate"] = g
        save_json(OUT / "gate.json", g)
        log(f"gate pass {g['pass']} (controls {g['controls_pass']}, seeded {g['seeded_ok']}/4)")
        if not g["pass"]:
            out["verdict"] = "not testable"
            save_json(Path(a.out), out)
            log("=== SENTINEL e82 (gate failed)")
            return
        primary = SEEDS
    else:
        lo, hi = map(int, a.pilot.split("-"))
        primary = list(range(lo, hi + 1))
    with Pool(a.workers) as p:
        jobs = [(sd, "neighbour") for sd in primary] + ([(sd, "none") for sd in NULL_SEEDS] if a.confirm else [])
        res = {}
        for r in p.imap_unordered(soup_job, jobs):
            res[(r["seed"], r["libmode"])] = r
            log(f"soup {r['seed']} {r['libmode']} T {r.get('T')} {r['seconds']}s "
                f"parasites {[len((r.get(f'S{k}') or {}).get('parasites', [])) for k in (1, 2, 3)]}")
        admitted = [r for (sd, lm), r in res.items() if lm == "neighbour" and r.get("T") is not None]
        if a.confirm:
            spares = list(SPARES)
            while len(admitted) < len(SEEDS) and spares:
                need = len(SEEDS) - len(admitted)
                batch = [(spares.pop(0), "neighbour") for _ in range(min(need, len(spares)))]
                for r in p.map(soup_job, batch):
                    res[(r["seed"], r["libmode"])] = r
                    log(f"spare {r['seed']} T {r.get('T')}")
                    if r.get("T") is not None:
                        admitted.append(r)
        sc = p.map(scores, admitted)
    out["soups"] = [res[k] for k in sorted(res)]
    out["scores"] = sc
    n = len(admitted)
    p1 = sum(s["parasites_all"] for s in sc)
    out["P1"] = {"soups": n, "with_parasites_S1_S2_S3": p1, "share": round(p1 / max(n, 1), 3),
                 "verdict": ("pass" if p1 / max(n, 1) >= P1_PASS else "fail") if n >= (N_MIN if a.confirm else 2)
                 else "undecided"}
    out["P2"] = verdict([s["RQ"] for s in sc])
    out["P3"] = verdict([s["d3"] for s in sc])
    if a.confirm:
        nulls = [res[(sd, "none")] for sd in NULL_SEEDS if (sd, "none") in res]
        out["none_null"] = [{"seed": r["seed"], "T": r.get("T"),
                             "parasites_S1": len((r.get("S1") or {}).get("parasites", []))} for r in nulls]
        if n < N_MIN:
            for k in ("P1", "P2", "P3"):
                out[k]["verdict"] = "undecided"
    out["seconds"] = round(time.time() - t0)
    save_json(Path(a.out), out)
    log(json.dumps({k: out[k] for k in ("P1", "P2", "P3")}))
    log("=== SENTINEL e82")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("=== SENTINEL e82 (error)", flush=True)
        raise
