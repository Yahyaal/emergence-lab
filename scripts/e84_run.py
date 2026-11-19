"""DRAFT, NOT PRE-REGISTERED AND NOT RUN (J-103, D-077): the decisive control (a) failed in the groundwork, so no
docs/data/e84-preregistration.md exists. Kept as the driver a fixed-length follow-up would start from.

E-84 draft: when a lock costs no length, does resistance to parasites arise from random
code where it pays kin, and do hosts and parasites change in a directed way? Rule: fixed-length BFF-X on demes
(scripts/bffxf.py, D-076): 2^14 programs of 64 bytes; the instruction pointer runs through A and then through a
read-only library C; heads read and write A ++ B only, halt at its ends; pairs and C within demes of 64 programs on a
ring; mutation 0.00024. Instruments: scripts/bffxf_assay.py (D-077). Protocol: E-83's (scripts/e83_run.py) with the
programs fixed at 64 bytes and new seeds.

  soups   rng [84, seed]. Census every 50 epochs: hosts = programs among the 40 commonest distinct ones that copy
          themselves into 4 of 4 random 64-byte partners with nothing to borrow; host share = share of programs in the
          families of the first 10 hosts. T = first checkpoint with >= 1 host whose checkpoint 500 epochs later has host
          share >= 0.05. No T by epoch 10,000: excluded.
  samples S1 = T + 1000, S2 = T + 5000, S3 = T + 10000: 5 commonest hosts; first 5 verified parasites among the 40
          commonest non-hosts (`bffxf_assay.parasite_test`, pool 4,096 programs of the snapshot).
  P1      (criterion) share of admitted soups with >= 1 verified parasite at S1, S2 and S3.
  P2      RQ = mean over i < j of q(P_j, H_i) - q(P_i, H_j) (q = coverage, 32 runs).
  P3      d3 = q(P_1, H_1) - q(P_1, H_3).
  second. RQ_w (protection), resistance census (hosts refusing the inert parasite or some earlier parasite),
          composition.
  gate    `bffxf_assay.controls`, decisive race (a) (R vs sham S with parasites, deme64, 50 epochs: A > 0.10 in >= 3
          of 4 seeds 8491-8494) and cost race (b) (R vs plain H, nothing borrowed, mutation on, 200 epochs: score
          > -0.25 in >= 3 of 4).

    systemd-inhibit --what=sleep:idle --why="E-84" setsid nohup env PYTHONPATH=.:scripts \
        python scripts/e84_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e84.json \
        > runs/e84/run/run.log 2>&1 < /dev/null &
    PYTHONPATH=.:scripts python scripts/e84_run.py --pilot 9901-9910 --workers 11 --out runs/e84/protopilot/out.json
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
import bffxf as F  # noqa: E402
import bffxf_assay as FA  # noqa: E402

# ---- fixed by the pre-registration --------------------------------------------------------------
EVERY = 50
CONFIRM_DT, CONFIRM_SHARE, MAX_WAIT = 500, 0.05, 10000
OFFS = (1000, 5000, 10000)
Q_TRIALS = 32
SEEDS = list(range(8401, 8441))          # 40 primary soups
SPARES = list(range(8441, 8473))
GATE_SEEDS = (8491, 8492, 8493, 8494)
N_MIN = 30
DELTA = 0.10                             # half the graded time-shift control (1 of 5 later hosts resistant: 0.2)
P1_PASS = 0.75
GATE_A, GATE_H = 0.10, 50
COST_MIN, COST_H = -0.25, 200
GEOMETRY = "deme64"
OUT = Path("runs/e84/run")


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(OUT / "progress.log", "a") as f:
        f.write(line + "\n")


def save_json(path: Path, obj) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    os.replace(tmp, path)


def soup_job(arg) -> dict:
    seed, geometry = arg
    path = OUT / "soups" / f"{seed}-{geometry}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    s = F.make(geometry, rng=np.random.default_rng([84, seed]), libmode="neighbour")
    traj, T, res, cands = [], None, {"seed": seed, "geometry": geometry}, []
    P = FA.parasite()
    while True:
        e = s.epochs
        if e % EVERY == 0:
            hs, share = FA.hosts_of(s, seed * 100003 + e)
            refuse = sum(FA.q_pair(P, np.frombuffer(b, np.uint8), e + i, 8) < 0.5 for i, (b, _) in enumerate(hs[:10]))
            traj.append({"epoch": e, "share": share, "nhost": len(hs), "refuse_inert": int(refuse),
                         "steps_pair": round(s.last_steps / max(1, s.n // 2), 1)})
            if T is None:
                if hs and e <= MAX_WAIT:
                    cands.append(e)
                while cands and e >= cands[0] + CONFIRM_DT:
                    ce = cands.pop(0)
                    hit = next((r for r in traj if r["epoch"] == ce + CONFIRM_DT), None)
                    if hit and hit["share"] >= CONFIRM_SHARE:
                        T = res["T"] = ce
                        cands = []
                        break
                if T is None and not cands and e > MAX_WAIT:
                    res["T"] = None
                    break
            if T is not None and e - T in OFFS:
                k = OFFS.index(e - T)
                np.savez_compressed(OUT / "soups" / f"{seed}-{geometry}-S{k + 1}.npz", buf=s.buf, lens=s.lens)
                res[f"S{k + 1}"] = FA.sample(s, seed, k + 1)
                if k == len(OFFS) - 1:
                    break
        s.epoch()
    res["traj"] = traj
    res["seconds"] = round(time.time() - t0)
    save_json(path, res)
    return res


# ---- scores -------------------------------------------------------------------------------------
def scores(res: dict) -> dict:
    seed = res["seed"]
    smp = FA.hist_of([res.get(f"S{k}") or {} for k in (1, 2, 3)])
    ts = FA.timeshift(smp, seed * 31 + 5, Q_TRIALS)
    Q = ts["Q"]
    d3 = None if Q[0][0] is None or Q[0][2] is None else round(Q[0][0] - Q[0][2], 4)
    tw = FA.timeshift_w(smp, seed * 37 + 3)
    resist = None
    if smp[0][0] and smp[2][1]:
        resist = int(sum(any(FA.q_pair(p, h, seed + 7 * j, 16) < 0.5 for p in smp[0][0])
                         for j, h in enumerate(smp[2][1])))
    P = FA.parasite()
    inert = [sum(FA.q_pair(P, h, seed + 11 * j, 16) < 0.5 for j, h in enumerate(smp[k][1])) for k in range(3)]
    return {"seed": seed, "Q": Q, "RQ": ts["RQ"], "d3": d3, "W": tw["W"], "RQ_w": tw["RQ_w"],
            "resistant_S3_hosts": resist, "hosts_refusing_inert": inert,
            "parasites_all": all(len(p) > 0 for p, _ in smp)}


def signflip(d: list, iters: int = 200000, seed: int = 84) -> float:
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
    sd, kind, lm = arg
    if kind == "a":
        return FA.compete(sd, GEOMETRY, lm, {"R": 0.10, "S": 0.10, "P": 0.05}, "R", "S", horizons=(GATE_H,))
    return FA.compete(sd, GEOMETRY, "none", {"R": 0.10, "H": 0.10}, "R", "H", horizons=(COST_H,), mutation=F.MUT)


def gate(seeds=GATE_SEEDS, workers: int = 8) -> dict:
    ctl = FA.controls()
    jobs = [(sd, "a", lm) for sd in seeds for lm in ("neighbour", "none")] + [(sd, "b", "none") for sd in seeds]
    with Pool(workers) as p:
        rr = p.map(_race, jobs)
    by = {(j[0], j[1], j[2]): r["scores"] for j, r in zip(jobs, rr)}
    adv = {sd: round(by[(sd, "a", "neighbour")][GATE_H] - by[(sd, "a", "none")][GATE_H], 4) for sd in seeds}
    cost = {sd: by[(sd, "b", "none")][COST_H] for sd in seeds}
    ok_a = sum(v > GATE_A for v in adv.values())
    ok_b = sum(v > COST_MIN for v in cost.values())
    cp = all(o for _, o, _ in ctl)
    return {"controls": [(n, bool(o), d) for n, o, d in ctl], "controls_pass": cp, "race_A": adv, "race_ok": ok_a,
            "cost": cost, "cost_ok": ok_b, "pass": cp and ok_a >= 3 and ok_b >= 3}


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
    out = {"experiment": "E-84", "commit": commit, "pilot": bool(a.pilot), "geometry": GEOMETRY}
    if a.confirm:
        g = gate(workers=a.workers)
        out["gate"] = g
        save_json(OUT / "gate.json", g)
        log(f"gate pass {g['pass']} (controls {g['controls_pass']}, race {g['race_ok']}/4 {g['race_A']}, "
            f"cost {g['cost_ok']}/4 {g['cost']})")
        if not g["pass"]:
            out["verdict"] = "not testable"
            save_json(Path(a.out), out)
            log("=== SENTINEL e84 (gate failed)")
            return
        primary = SEEDS
    else:
        lo, hi = map(int, a.pilot.split("-"))
        primary = list(range(lo, hi + 1))
    with Pool(a.workers) as p:
        res = {}
        for r in p.imap_unordered(soup_job, [(sd, GEOMETRY) for sd in primary]):
            res[r["seed"]] = r
            log(f"soup {r['seed']} T {r.get('T')} {r['seconds']}s "
                f"parasites {[len((r.get(f'S{k}') or {}).get('parasites', [])) for k in (1, 2, 3)]}")
        admitted = [r for r in res.values() if r.get("T") is not None]
        if a.confirm:
            spares = list(SPARES)
            while len(admitted) < len(SEEDS) and spares:
                need = len(SEEDS) - len(admitted)
                batch = [(spares.pop(0), GEOMETRY) for _ in range(min(need, len(spares)))]
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
                        "resistant_S3_hosts": [s["resistant_S3_hosts"] for s in sc],
                        "hosts_refusing_inert": [s["hosts_refusing_inert"] for s in sc]}
    if a.confirm and n < N_MIN:
        for k in ("P1", "P2", "P3"):
            out[k]["verdict"] = "undecided"
    out["seconds"] = round(time.time() - t0)
    save_json(Path(a.out), out)
    log(json.dumps({k: out[k] for k in ("P1", "P2", "P3", "secondary")}))
    log("=== SENTINEL e84")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("=== SENTINEL e84 (error)", flush=True)
        raise
