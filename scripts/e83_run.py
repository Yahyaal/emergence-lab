"""E-83 (docs/data/e83-preregistration.md): when resisting parasites pays the resisting host's kin, do hosts and
parasites change in a directed way? Rule: BFF-XR deme64 (scripts/bffxr.py, D-074): BFF-X with the soup's programs on
a ring cut into demes of 64 consecutive programs (at a random offset each epoch); pairs and the borrowed code are drawn
within a deme, and every pair's pieces are written back in place, so offspring stay beside their parents. Instruments: E-82's (scripts/bffx_assay.py, D-073), re-
validated on the ring (scripts/bffxr_assay.py, D-075). The protocol is E-82's (scripts/e82_run.py) with the geometry
changed and new seeds; the secondaries add a protection score.

  soups   W = 2^20 bytes of random code under deme64, mutation 0.00024, rng [83, seed]. Census every 50 epochs: hosts =
          programs among the 40 commonest distinct ones that copy themselves into 4 of 4 random 128-byte partners with
          nothing to borrow; host share = bytes of the families of the first 10 hosts. T = the first checkpoint with
          >= 1 host whose checkpoint 500 epochs later has host share >= 0.05. No T by epoch 10,000: excluded.
  samples S1 = T + 1000, S2 = T + 5000, S3 = T + 10000: 5 commonest hosts; first 5 verified parasites among the 40
          commonest non-hosts (`bffx_assay.parasite_test`, pool 4,096 programs of the snapshot).
  P1      (criterion) share of admitted soups with >= 1 verified parasite at S1, S2 and S3.
  P2      RQ = mean over i < j of q(P_j, H_i) - q(P_i, H_j) (q = coverage, `bffx_assay.q_pair`, 32 runs).
  P3      d3 = q(P_1, H_1) - q(P_1, H_3).
  second. RQ_w with protection w(P, H) = share of a random 128-byte partner left unchanged when P runs first with H as
          its library (refusal protects the partner; a host that copies callers with an altered byte does not);
          resistance census (S3 hosts with q < 0.5 against some S1 parasite); host and parasite lengths.
  gate    `bffx_assay.controls` (16) and `bffxr_assay.controls` (ring and time-shift controls), and the decisive race
          (`gate_race`: the resistant host against its equal-length sham with parasites, deme64, 50 epochs, seeds
          8491-8494: resistance advantage A > 0.1 in >= 3 of 4).

    systemd-inhibit --what=sleep:idle --why="E-83" setsid nohup env PYTHONPATH=.:scripts \
        python scripts/e83_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e83.json \
        > runs/e83/run/run.log 2>&1 < /dev/null &
    PYTHONPATH=.:scripts python scripts/e83_run.py --pilot 9901-9910 --workers 11 --out runs/e83/protopilot/out.json
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
import bffxr as R_  # noqa: E402
import bffxr_assay as RA  # noqa: E402

# ---- fixed by the pre-registration --------------------------------------------------------------
EVERY, TOPK, TOPFAM = 50, 40, 10
CONFIRM_DT, CONFIRM_SHARE, MAX_WAIT = 500, 0.05, 10000
OFFS = (1000, 5000, 10000)
KH, KP, POOL, Q_TRIALS = 5, 5, 4096, 32
SEEDS = list(range(8401, 8441))          # 40 primary soups
SPARES = list(range(8441, 8473))
GATE_SEEDS = (8491, 8492, 8493, 8494)    # decisive race in the gate
N_MIN = 30
DELTA = 0.10                             # half the graded time-shift control (1 of 5 later hosts resistant: 0.2)
P1_PASS = 0.75
GATE_A, GATE_H = 0.10, 50
GEOMETRY = "deme64"
OUT = Path("runs/e83/run")
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
    """Hosts and verified parasites of a snapshot (E-82's sampler, rng keyed by 83)."""
    hs, share = hosts_of(s, seed * 100003 + 77 + tag)
    rng = np.random.default_rng([83, seed, tag])
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
    seed, geometry = arg
    path = OUT / "soups" / f"{seed}-{geometry}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    s = R_.make(geometry, rng=np.random.default_rng([83, seed]), libmode="neighbour")
    traj, T, res, cands = [], None, {"seed": seed, "geometry": geometry}, []
    offs = CFG["offs"]
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
                np.savez_compressed(OUT / "soups" / f"{seed}-{geometry}-S{k + 1}.npz", buf=s.buf, lens=s.lens)
                res[f"S{k + 1}"] = sample(s, seed, k + 1)
                if k == len(offs) - 1:
                    break
        s.epoch()
    res["traj"] = traj
    res["seconds"] = round(time.time() - t0)
    save_json(path, res)
    return res


# ---- scores -------------------------------------------------------------------------------------
def _hist(res: dict):
    smp = []
    for k in (1, 2, 3):
        S = res.get(f"S{k}") or {}
        smp.append(([np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in S.get("parasites", [])],
                    [np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in S.get("hosts", [])]))
    return smp


def scores(res: dict) -> dict:
    seed = res["seed"]
    smp = _hist(res)
    ts = A.timeshift(smp, seed * 31 + 5, Q_TRIALS)
    Q = ts["Q"]
    d3 = None if Q[0][0] is None or Q[0][2] is None else round(Q[0][0] - Q[0][2], 4)
    tw = RA.timeshift_w(smp, seed * 37 + 3)
    resist = None
    if smp[0][0] and smp[2][1]:
        resist = int(sum(any(A.q_pair(p, h, seed + 7 * j, 16) < 0.5 for p in smp[0][0])
                         for j, h in enumerate(smp[2][1])))
    return {"seed": seed, "Q": Q, "RQ": ts["RQ"], "d3": d3, "W": tw["W"], "RQ_w": tw["RQ_w"],
            "resistant_S3_hosts": resist, "parasites_all": all(len(p) > 0 for p, _ in smp),
            "host_len_S3": [len(h) for h in smp[2][1]], "para_len_S1": [len(p) for p in smp[0][0]]}


def signflip(d: list, iters: int = 200000, seed: int = 83) -> float:
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


# ---- gate ---------------------------------------------------------------------------------------
def _race(arg):
    sd, lm = arg
    return RA.compete(sd, GEOMETRY, lm, {"R": 0.10, "S": 0.10, "P": 0.05}, "R", "S", horizons=(GATE_H,))


def gate(seeds=GATE_SEEDS, workers: int = 8) -> dict:
    ctl = A.controls("neighbour") + RA.controls()
    with Pool(workers) as p:
        rr = p.map(_race, [(sd, lm) for sd in seeds for lm in ("neighbour", "none")])
    by = {(r["seed"], r["libmode"]): r["scores"][GATE_H] for r in rr}
    adv = {sd: round(by[(sd, "neighbour")] - by[(sd, "none")], 4) for sd in seeds}
    ok_race = sum(v > GATE_A for v in adv.values())
    cp = all(o for _, o, _ in ctl)
    return {"controls": [(n, bool(o), d) for n, o, d in ctl], "controls_pass": cp, "race_A": adv,
            "race_ok": ok_race, "pass": cp and ok_race >= 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--pilot", default=None, help="seed range a-b (pilot seeds only)")
    ap.add_argument("--geometry", default=GEOMETRY)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    global OUT
    if a.pilot:
        OUT = Path(a.out).parent
    (OUT / "soups").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {"experiment": "E-83", "commit": commit, "pilot": bool(a.pilot), "geometry": a.geometry}
    if a.confirm:
        g = gate(workers=a.workers)
        out["gate"] = g
        save_json(OUT / "gate.json", g)
        log(f"gate pass {g['pass']} (controls {g['controls_pass']}, race {g['race_ok']}/4 {g['race_A']})")
        if not g["pass"]:
            out["verdict"] = "not testable"
            save_json(Path(a.out), out)
            log("=== SENTINEL e83 (gate failed)")
            return
        primary = SEEDS
    else:
        lo, hi = map(int, a.pilot.split("-"))
        primary = list(range(lo, hi + 1))
    with Pool(a.workers) as p:
        res = {}
        for r in p.imap_unordered(soup_job, [(sd, a.geometry) for sd in primary]):
            res[r["seed"]] = r
            log(f"soup {r['seed']} T {r.get('T')} {r['seconds']}s "
                f"parasites {[len((r.get(f'S{k}') or {}).get('parasites', [])) for k in (1, 2, 3)]}")
        admitted = [r for r in res.values() if r.get("T") is not None]
        if a.confirm:
            spares = list(SPARES)
            while len(admitted) < len(SEEDS) and spares:
                need = len(SEEDS) - len(admitted)
                batch = [(spares.pop(0), a.geometry) for _ in range(min(need, len(spares)))]
                for r in p.map(soup_job, batch):
                    res[r["seed"]] = r
                    log(f"spare {r['seed']} T {r.get('T')}")
                    if r.get("T") is not None:
                        admitted.append(r)
        admitted.sort(key=lambda r: r["seed"])
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
    rw = [s["RQ_w"] for s in sc if s["RQ_w"] is not None]
    out["secondary"] = {"RQ_w_mean": round(float(np.mean(rw)), 4) if rw else None,
                        "resistant_S3_hosts": [s["resistant_S3_hosts"] for s in sc]}
    if a.confirm and n < N_MIN:
        for k in ("P1", "P2", "P3"):
            out[k]["verdict"] = "undecided"
    out["seconds"] = round(time.time() - t0)
    save_json(Path(a.out), out)
    log(json.dumps({k: out[k] for k in ("P1", "P2", "P3", "secondary")}))
    log("=== SENTINEL e83")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("=== SENTINEL e83 (error)", flush=True)
        raise
