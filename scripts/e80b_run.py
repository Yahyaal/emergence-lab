"""E-80 Part B (docs/data/e80-partB-preregistration.md): 16 new jumped soups under the h = 64 head-start rule
(2^14 programs, 128 x 128 torus), each forked into S, M and M' for 10,000 rounds, then the lattice-native assay in a
kin-free garden made under the same rule. One detached, resumable driver:

  phase 1  garden soup (seed 8100, spares 8101-8103) and the 16 soups (seeds 8001-8016, spares 8017-8028 in order):
           well mixed under h = 64 until a D-047-style jump is confirmed (copier test `bff_kernels.classify_fid`,
           D-053), then on to T + 2000 (the fork); arms M, S, M' run 10,000 rounds each, checkpointed every 500.
  phase 2  4 garden replicates (4,096 programs of the garden fork, aged 2,000 rounds on 64 x 64 under h = 64);
           the validation gate G1-G8 in that garden.
  phase 3  assays of early, M, M' blocks (allowed); gate G9 (kin); if the gate passed, S and Sshuf blocks; analysis.

Every step writes its result to runs/e80/partB/ and is skipped on restart; an interrupted soup resumes from its
last checkpoint (programs + generator state) and gives the same result as an uninterrupted run (`check_resume`).

    systemd-inhibit --what=sleep:idle --why="E-80 Part B" setsid nohup env PYTHONPATH=. \
        python scripts/e80b_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e80-partB.json \
        > runs/e80/partB/run.log 2>&1 &
    python scripts/e80b_run.py --dry --workers 11 --out runs/e80/partB-dry/out.json   # code path, tiny settings
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import t as tdist

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402
import bff_spatial as BS  # noqa: E402
import lattice_assay as LA  # noqa: E402

from emergence.programs import bff as B  # noqa: E402

# ---- fixed by the amendment ---------------------------------------------------------------------
H1 = 64
N, SIDE, MUT, MAX_STEPS = 2 ** 14, 128, 0.00024, 8192
SEEDS = list(range(8001, 8017))
SPARES = list(range(8017, 8029))
GARDEN_SEEDS = [8100, 8101, 8102, 8103]
N_TARGET, N_MIN = 16, 10
EVERY, THRESH, PERSIST, AFTER, MIN_COP, WAIT = 250, 1.0, 3, 1000, 10, 6000
FORK_DT, HROUNDS, SNAP, CKPT = 2000, 10000, 2000, 500
ARMS = {"M": ("mixed", 0), "S": ("spatial", 1), "Mp": ("mixed", 2)}
G_N, G_AGE, G_SIDE = 4, 2000, LA.SIDE
T_H, R_BLOCKS, S_SEEDS, R_SEC = 64, 16, 4, 8
GATE_REPS = 24
KIN_MAX = 0.001
GROUPS = ("early", "M", "Mp", "S", "Sshuf")
GCODE = {"early": 0, "M": 1, "Mp": 2, "S": 3, "Sshuf": 3}
OUT = Path("runs/e80/partB")
CFG = {"dry": False}


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(OUT / "progress.log", "a") as f:
        f.write(line + "\n")


def save_json(path: Path, obj) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    os.replace(tmp, path)


def save_npy(path: Path, arr: np.ndarray) -> None:
    tmp = path.with_name(path.stem + ".tmp.npy")
    np.save(tmp, arr)
    os.replace(tmp, path)


# ---- soups under h = 64 ----------------------------------------------------------------------------

class HSoup(BS.ArmSoup):
    """bff_spatial.ArmSoup under the head-start rule: the pair run is bff_kernels.epoch_h (head1 starts at H1);
    pairs and mutation exactly as ArmSoup (same generator calls in the same order)."""

    def epoch(self) -> int:
        pairs = self.pairs()
        self.last_steps = int(K.lib().epoch_h(self.programs.ctypes.data, self.length, pairs.ctypes.data,
                                              self.n // 2, self.max_steps, H1))
        if self.mutation > 0:
            k = self.rng.binomial(self.programs.size, self.mutation)
            idx = self.rng.integers(0, self.programs.size, k)
            self.programs.reshape(-1)[idx] = self.rng.integers(0, 256, k, dtype=np.uint8)
        self.epochs += 1
        return self.last_steps


def copiers(P: np.ndarray, seed: int) -> int:
    """Copiers (classify_fid under h = 64, 4 partners, shift-aware, D-053) among the 40 most common distinct
    programs (either orientation, 90% identity, as bff_counterfactual.distinct_top)."""
    X = np.array(C.distinct_top(P))
    c, _ = K.classify_fid(X, H1, 4, seed)
    return int((c != 0).sum())


def _ckpt(tag: str) -> Path:
    return OUT / "soups" / f"{tag}.state.json"


def run_soup(tag: str, P0: np.ndarray | None, arm: str, seed, start: int, end: int | None, mode: str,
             stop_at: int | None = None, outdir: Path | None = None) -> dict:
    """mode 'prefork': well mixed from P0 (or random) until a confirmed jump, then to T + FORK_DT (end ignored);
    mode 'arm': from P0 for end - start rounds. Checkpoint (programs + generator + detector state) every CKPT rounds;
    resumes from the last one. Returns the final state dict."""
    d = outdir or (OUT / "soups")
    d.mkdir(parents=True, exist_ok=True)
    st_path = d / f"{tag}.state.json"
    s = HSoup(arm=arm, n=N, width=SIDE, seed=seed, mutation=MUT, max_steps=MAX_STEPS,
              programs=P0 if P0 is not None else None)
    det = {"series": [], "run": 0, "cand": None, "T": None, "dropped": [], "snaps": []}
    if st_path.exists():
        st = json.loads(st_path.read_text())
        if st.get("done"):
            return st
        s.programs = np.ascontiguousarray(np.load(d / f"{tag}-ckpt.npy"))
        s.rng.bit_generator.state = st["rng"]
        s.epochs = st["epoch"]
        det = st["det"]
    else:
        s.epochs = start

    def checkpoint(done=False):
        save_npy(d / f"{tag}-ckpt.npy", s.programs)
        st = {"tag": tag, "epoch": s.epochs, "rng": s.rng.bit_generator.state, "det": det, "done": done}
        save_json(st_path, st)
        return st
    while True:
        if stop_at is not None and s.epochs >= stop_at:
            return {"interrupted": s.epochs}
        if mode == "arm" and s.epochs >= end:
            break
        if mode == "prefork" and det["T"] is not None and s.epochs >= det["T"] + FORK_DT:
            break
        if mode == "prefork" and det["T"] is None and det["cand"] is None and s.epochs >= WAIT:
            break
        steps = s.epoch()
        e = s.epochs
        if mode == "prefork" and e % EVERY == 0:
            hoe = B.high_order_entropy(s.programs)
            det["series"].append({"epoch": e, "hoe": round(hoe, 3), "steps_per_pair": round(steps / (N / 2), 1)})
            if det["T"] is None:
                if det["cand"] is None:
                    det["run"] = det["run"] + 1 if hoe >= THRESH else 0
                    if det["run"] >= PERSIST and copiers(s.programs, 800 + e) >= 1:
                        det["cand"] = e - EVERY * (PERSIST - 1)
                elif e >= det["cand"] + AFTER:
                    n = copiers(s.programs, 801 + e)
                    if n >= MIN_COP:
                        det["T"] = det["cand"]
                    else:
                        det["dropped"].append({"candidate": det["cand"], "copiers": n})
                        det["cand"], det["run"] = None, 0
        if mode == "arm" and (e - start) % SNAP == 0:
            save_npy(d / f"{tag}-{e}.npy", s.programs)
            det["snaps"].append({"epoch": e, "steps_per_pair": round(steps / (N / 2), 1)})
        if (e - start) % CKPT == 0:
            checkpoint()
    if mode == "prefork" and det["T"] is not None:
        save_npy(d / f"{tag}-fork.npy", s.programs)
    if mode == "arm" and not (d / f"{tag}-{s.epochs}.npy").exists():
        save_npy(d / f"{tag}-{s.epochs}.npy", s.programs)
    st = checkpoint(done=True)
    return st


def soup_seed(seed: int, what: str):
    return {"prefork": [80, 200, seed], "placement": [80, 201, seed], "garden_sample": [80, 210, seed]}[what]


def job(spec) -> dict:
    """Worker entry: ('prefork', seed) | ('arm', seed, name) | ('garden', i) | ('assay', ...). Exceptions are
    returned, not raised, so one failure does not kill the pool."""
    t0 = time.time()
    try:
        kind = spec[0]
        if kind == "prefork":
            seed = spec[1]
            P0 = None
            if CFG["dry"]:   # code-path check only: a seeded copier block so the tiny soup jumps at once
                P0 = np.random.default_rng(seed).integers(0, 256, (N, 64), dtype=np.uint8)
                P0[: N // 16] = H0
            st = run_soup(f"{seed}-pre", P0, "mixed", soup_seed(seed, "prefork"), 0, None, "prefork")
            return {"spec": spec, "T": st["det"]["T"], "end": st["epoch"], "dropped": st["det"]["dropped"],
                    "series": st["det"]["series"], "sec": round(time.time() - t0)}
        if kind == "arm":
            seed, name = spec[1], spec[2]
            arm, code = ARMS[name]
            pre = json.loads(_ckpt(f"{seed}-pre").read_text())
            start = pre["det"]["T"] + FORK_DT
            P = np.load(OUT / "soups" / f"{seed}-pre-fork.npy")[np.random.default_rng(soup_seed(seed, "placement")).permutation(N)]
            st = run_soup(f"{seed}-{name}", P, arm, [80, 202, seed, code], start, start + HROUNDS, "arm")
            return {"spec": spec, "end": st["epoch"], "snaps": st["det"]["snaps"], "sec": round(time.time() - t0)}
        if kind == "garden":
            i, gseed = spec[1], spec[2]
            P = np.load(OUT / "soups" / f"{gseed}-pre-fork.npy")
            G0 = P[np.random.default_rng([80, 210, i]).choice(len(P), G_SIDE * G_SIDE, replace=False)]
            G, ser = age_garden_h(G0, G_AGE, [80, 211, i])
            save_npy(OUT / f"garden-{i}.npy", G)
            return {"spec": spec, "series": ser, "sec": round(time.time() - t0)}
        if kind == "assay":
            return {"spec": spec} | run_assay(spec) | {"sec": round(time.time() - t0, 1)}
        raise ValueError(kind)
    except Exception:
        return {"spec": spec, "error": traceback.format_exc()}


def age_garden_h(programs: np.ndarray, rounds: int, seed, side: int = G_SIDE) -> tuple[np.ndarray, list]:
    s = HSoup(arm="spatial", n=side * side, width=side, programs=programs, seed=seed, mutation=MUT)
    ser = []
    for t in range(rounds + 1):
        if t % 250 == 0:
            Gr = s.programs.reshape(side, side, -1)
            Gn = np.roll(Gr, 1, 1)
            nb = float((((Gr == Gn).mean(2) >= 0.9) | ((Gr == Gn[..., ::-1]).mean(2) >= 0.9)).mean())
            ser.append({"t": t, "nbr_identity": round(nb, 3), "steps_per_pair": round(s.last_steps / (s.n / 2), 1)})
        if t < rounds:
            s.epoch()
    return s.programs.copy(), ser


# ---- programs for the gate ------------------------------------------------------------------------

def hprog(code: bytes) -> np.ndarray:
    return np.frombuffer(code + b"\x80" * (64 - len(code)), np.uint8).copy()


H0 = hprog(b"[.>}]")                # hand-written h = 64 copier: copies tape[i] -> tape[i + 64] until the step limit
H1P = hprog(b"<[--]>[.>}]")         # handicap: copies only if the partner's last byte is even (about half the time)
SMEAR = hprog(b"\x80[.}]")          # writes 0x80 over its partner: 94% like itself, none of its instructions


def knockout(x: np.ndarray) -> np.ndarray:
    y = x.copy()
    y[(y == ord(".")) | (y == ord(","))] = 0x80
    return y


def native_copier(gseed: int) -> np.ndarray:
    """The most common distinct program of the garden source (fork snapshot) that classify_fid calls a copier."""
    P = np.load(OUT / "soups" / f"{gseed}-pre-fork.npy")
    X = np.array(C.distinct_top(P))
    c, _ = K.classify_fid(X, H1, 8, 830)
    return X[int(np.flatnonzero(c)[0])]


def garden(i: int) -> np.ndarray:
    return np.load(OUT / f"garden-{i}.npy")


# ---- assays --------------------------------------------------------------------------------------

def run_assay(spec) -> dict:
    _, what, seed, group, b, j, arm = spec
    if what == "gate":
        return gate_assay(group, b, seed)
    gi = (b + j) % G_N
    G = garden(gi)
    blk = block(seed, group, b)
    aseed = [80, 230, seed, b, j, gi, 0 if arm == "spatial" else 1]
    r = LA.assay([blk], G, aseed, arm=arm, rounds=T_H, checkpoints=(16, 32, T_H), h1=H1)
    return {"key": "|".join(map(str, spec)), "seed": seed, "group": group, "b": b, "j": j, "arm": arm, "gi": gi,
            "kin": LA.kin_share(G, blk), "series": {t: v[0] for t, v in r["series"].items()},
            "purity_anchor": r["purity_anchor"][0], "events": r["events"], "steps_per_pair": r["steps_per_pair"]}


def snapshot(seed: int, group: str) -> np.ndarray:
    if group == "early":
        return np.load(OUT / "soups" / f"{seed}-pre-fork.npy")[np.random.default_rng(soup_seed(seed, "placement")).permutation(N)]
    name = {"Sshuf": "S"}.get(group, group)
    if name == "S" and not CFG.get("s_allowed"):
        raise PermissionError("S blocks are scored only after the gate passed")
    pre = json.loads(_ckpt(f"{seed}-pre").read_text())
    return np.load(OUT / "soups" / f"{seed}-{name}-{pre['det']['T'] + FORK_DT + HROUNDS}.npy")


def block(seed: int, group: str, b: int) -> np.ndarray:
    P = snapshot(seed, group)
    rng = np.random.default_rng([80, 231, seed, GCODE[group], b])
    if group in ("S", "Sshuf"):
        blk, _ = LA.make_block(P, rng, geometry=True, width=SIDE, mode="preserved")
        if group == "Sshuf":
            blk = blk[np.random.default_rng([80, 232, seed, b]).permutation(len(blk))]
        return blk
    blk, _ = LA.make_block(P, rng, geometry=False)
    return blk


def gate_assay(ctrl: str, rep: int, gseed: int) -> dict:
    """One replicate of a gate control (64 x 64, 8 x 8 blocks, T = 64, under h = 64)."""
    k2 = LA.K * LA.K
    gi = rep % G_N
    seed = [80, 220, ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"].index(ctrl), rep]
    rnd = np.random.default_rng([80, 221, rep]).integers(0, 256, (G_SIDE * G_SIDE, 64), dtype=np.uint8)
    out = {"ctrl": ctrl, "rep": rep}
    if ctrl == "G1":
        r = LA.assay([np.repeat(H0[None], k2, 0)], rnd, seed, rounds=T_H, h1=H1)
        out |= {"N": r["NT"][0], "purity": r["purity"][0]}
    elif ctrl in ("G2", "G3"):
        G = garden(gi)
        if ctrl == "G2":
            a, b = H0, H1P
        else:
            try:
                a = native_copier(gseed)
            except IndexError:   # no copier among the 40 most common programs: G3 fails (recorded, not a crash)
                return out | {"A_parent": 0.0, "A_handicap": 0.0, "no_native_copier": True}
            b = knockout(a)
        ra = LA.assay([np.repeat(a[None], k2, 0)], G, seed, rounds=T_H, h1=H1)
        rb = LA.assay([np.repeat(b[None], k2, 0)], G, seed, rounds=T_H, h1=H1)
        out |= {"A_parent": ra["NT"][0] / k2 - 1, "A_handicap": rb["NT"][0] / k2 - 1}
    elif ctrl == "G4":
        blk = np.repeat(H0[None], k2, 0)
        r = LA.assay([blk, blk.copy()], garden(gi), seed, rounds=T_H, h1=H1)
        out |= {"d": r["NT"][0] / k2 - r["NT"][1] / k2}
    elif ctrl == "G5":
        G = garden(gi)
        g = np.random.default_rng(seed + [1])
        b1, _ = LA.make_block(G, g)
        b2, _ = LA.make_block(G, g)
        r = LA.assay([b1, b2], G, seed, rounds=T_H, h1=H1)
        out |= {"d": r["NT"][0] / k2 - r["NT"][1] / k2}
    elif ctrl == "G6":
        from emergence.observatory import program_fitness as F
        halt = F.background(np.random.default_rng([80, 222, rep]), G_SIDE * G_SIDE, 64, "halting")
        r = LA.assay([np.repeat(SMEAR[None], k2, 0)], halt, seed, rounds=T_H, h1=H1, identity=True)
        out |= {"N": r["NT"][0], "identity": r["identity"][str(T_H)][0]}
    elif ctrl == "G7":
        r = LA.assay([np.repeat(knockout(H0)[None], k2, 0)], rnd, seed, rounds=T_H, h1=H1)
        out |= {"N": r["NT"][0]}
    elif ctrl == "G8":
        r = LA.assay([np.repeat(H0[None], k2, 0)], rnd, seed, rounds=48, mode="noexec", mutation=0.01)
        out |= {"N": r["NT"][0], "copies": r["events"]["copies"]}
    return out


GATE_PLAN = {"G1": 4, "G2": GATE_REPS, "G3": GATE_REPS, "G4": GATE_REPS, "G5": GATE_REPS, "G6": 8, "G7": 4, "G8": 4}


def paired_z(d) -> float:
    d = np.asarray(d, float)
    sd = d.std(ddof=1)
    return float(d.mean() / (sd / np.sqrt(len(d)))) if sd > 0 else (float("inf") if d.mean() > 0 else 0.0)


def evaluate_gate(rows: list[dict]) -> dict:
    """Criteria fixed in the amendment (numbers, not adjectives)."""
    by = {}
    for r in rows:
        by.setdefault(r["ctrl"], []).append(r)
    k2 = LA.K * LA.K
    res = {}
    g = by["G1"]
    res["G1"] = {"pass": all(r["N"] >= 3 * k2 and r["purity"] >= 0.95 for r in g),
                 "N": [r["N"] for r in g], "purity": [round(r["purity"], 3) for r in g]}
    for c in ("G2", "G3"):
        d = np.array([r["A_parent"] - r["A_handicap"] for r in by[c]])
        res[c] = {"pass": bool(d.mean() > 0 and paired_z(d) >= 3 and (d > 0).sum() >= 18), "mean_d": float(d.mean()),
                  "sd": float(d.std(ddof=1)), "z": paired_z(d), "ahead": int((d > 0).sum()), "n": len(d),
                  "mean_parent": float(np.mean([r["A_parent"] for r in by[c]])),
                  "mean_handicap": float(np.mean([r["A_handicap"] for r in by[c]]))}
    for c in ("G4", "G5"):
        d = np.array([r["d"] for r in by[c]])
        p = LA.signflip_p(d, two_sided=True, n_mc=100000, seed=80)
        res[c] = {"pass": p >= 0.01, "mean_d": float(d.mean()), "p_two_sided": p, "n": len(d)}
    g = by["G6"]
    # under h = 64 the smear destroys itself after one firing (it overwrites its own code), so byte identity gains only
    # a few sites per replicate: the deception criterion is a total excess of identity over tags of >= 16 sites
    res["G6"] = {"pass": all(r["N"] <= k2 for r in g) and sum(r["identity"] - r["N"] for r in g) >= 16,
                 "N": [r["N"] for r in g], "identity": [r["identity"] for r in g]}
    res["G7"] = {"pass": all(r["N"] <= k2 for r in by["G7"]), "N": [r["N"] for r in by["G7"]]}
    res["G8"] = {"pass": all(r["N"] == k2 and r["copies"] == 0 for r in by["G8"]), "N": [r["N"] for r in by["G8"]]}
    res["pass_G1_G8"] = all(res[c]["pass"] for c in GATE_PLAN)
    res["delta_star"] = round(res["G2"]["mean_d"] / 2, 3)
    return res


# ---- statistics (as Part A) ----------------------------------------------------------------------

def score(r: dict, T: int = T_H, log: bool = False) -> float:
    n = r["series"][str(T)]
    return float(np.log((n + 1) / (LA.K * LA.K + 1))) if log else float(n / (LA.K * LA.K) - 1)


def soup_means(rows, soups, arm="spatial", T=T_H, log=False):
    m, kept = {}, {}
    for s in soups:
        for g in GROUPS:
            rr = [r for r in rows if r["seed"] == s and r["group"] == g and r["arm"] == arm]
            ok = [score(r, T, log) for r in rr if r["kin"] <= KIN_MAX]
            kept[(s, g)] = (len(ok), len(rr))
            m[(s, g)] = float(np.mean(ok)) if ok else None
    return m, kept


def contrast(m, kept, a, b, soups) -> dict:
    ok = [s for s in soups if m.get((s, a)) is not None and m.get((s, b)) is not None
          and kept[(s, a)][0] >= 0.5 * max(kept[(s, a)][1], 1) and kept[(s, b)][0] >= 0.5 * max(kept[(s, b)][1], 1)]
    d = np.array([m[(s, a)] - m[(s, b)] for s in ok])
    if len(d) < 3:
        return {"soups": ok, "verdict": "undecided (too few soups)"}
    h = tdist.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return {"soups": ok, "n": len(ok), "d": {str(s): round(float(v), 4) for s, v in zip(ok, d)},
            "mean_d": round(float(d.mean()), 4), "sd_d": round(float(d.std(ddof=1)), 4),
            "p_one_sided": LA.signflip_p(d), "p_two_sided": LA.signflip_p(d, two_sided=True),
            "ci95": [round(float(d.mean() - h), 4), round(float(d.mean() + h), 4)]}


def verdict(prim: dict, null: dict, delta_star: float) -> str:
    if "mean_d" not in prim:
        return prim["verdict"]
    if prim["p_one_sided"] < 0.05 and prim["mean_d"] > 0 and null.get("p_two_sided", 0) >= 0.05:
        return "pass"
    if prim["ci95"][1] < delta_star:
        return "fail"
    return "undecided"


# ---- driver ---------------------------------------------------------------------------------------

def check_resume() -> dict:
    """An arm interrupted and resumed from its checkpoint equals an uninterrupted one (small settings)."""
    global N, SIDE, CKPT
    saved = (N, SIDE, CKPT)
    N, SIDE, CKPT = 1024, 32, 10
    try:
        P = np.random.default_rng(5).integers(0, 256, (N, 64), dtype=np.uint8)
        P[: N // 8] = H0
        out = {}
        for arm in ("mixed", "spatial"):
            with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
                a = run_soup("x", P.copy(), arm, [1, 2], 0, 40, "arm", outdir=Path(d1))
                run_soup("x", P.copy(), arm, [1, 2], 0, 40, "arm", stop_at=25, outdir=Path(d2))
                b = run_soup("x", P.copy(), arm, [1, 2], 0, 40, "arm", outdir=Path(d2))
                out[arm] = bool((np.load(Path(d1) / "x-ckpt.npy") == np.load(Path(d2) / "x-ckpt.npy")).all()
                                and a["rng"] == b["rng"])
        return out | {"pass": all(out.values())}
    finally:
        N, SIDE, CKPT = saved


def preregistered() -> bool:
    out = subprocess.run(["git", "log", "-1", "--format=%H", "--", "docs/data/e80-partB-preregistration.md"],
                         capture_output=True, text=True)
    return bool(out.stdout.strip())


def main() -> None:
    global SEEDS, SPARES, GARDEN_SEEDS, N_TARGET, N_MIN, HROUNDS, R_BLOCKS, S_SEEDS, R_SEC, GATE_REPS, OUT, G_AGE
    global N, SIDE, MIN_COP, WAIT, FORK_DT, AFTER
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--check-resume", action="store_true")
    a = ap.parse_args()
    if a.check_resume:
        print(json.dumps(check_resume()))
        return
    if a.dry:   # code path only: 3 soups, 300 rounds per arm, tiny assay counts (not data)
        CFG["dry"] = True
        SEEDS, SPARES, GARDEN_SEEDS, N_TARGET, N_MIN = [8901, 8902, 8903], [8904], [8990, 8991], 3, 3
        HROUNDS, R_BLOCKS, S_SEEDS, R_SEC, G_AGE = 300, 2, 1, 1, 100
        N, SIDE, MIN_COP, WAIT, FORK_DT, AFTER = 4096, 64, 1, 3000, 200, 250
        GATE_REPS = 4
        GATE_PLAN.update({c: 4 for c in GATE_PLAN})
        OUT = Path("runs/e80/partB-dry")
    elif not a.confirm:
        sys.exit("give --confirm (after the amendment commit) or --dry")
    elif not preregistered():
        sys.exit("docs/data/e80-partB-preregistration.md is not committed: refusing to run")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "soups").mkdir(exist_ok=True)
    for f in ("DONE", "FAILED"):
        (OUT / f).unlink(missing_ok=True)
    t0 = time.time()
    try:
        res = drive(a.workers)
        res["seconds"] = round(time.time() - t0)
        Path(a.out).write_text(json.dumps(res, indent=1, default=float))
        (OUT / "DONE").write_text(json.dumps({"verdict": res.get("verdict"), "gate": res.get("gate_passed"),
                                              "seconds": res["seconds"]}) + "\n")
        log(f"DONE verdict={res.get('verdict')} gate={res.get('gate_passed')} sec={res['seconds']}")
    except Exception:
        tb = traceback.format_exc()
        (OUT / "FAILED").write_text(tb)
        log("FAILED\n" + tb)
        raise


def drive(workers: int) -> dict:
    log(f"E-80 Part B start (dry={CFG['dry']}), commit {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()}")
    cache = OUT / "jobs.jsonl"
    done = {}
    if cache.exists():
        for line in cache.read_text().splitlines():
            r = json.loads(line)
            done[json.dumps(r["spec"])] = r
    fout = cache.open("a")

    def record(r):
        if "error" in r:
            raise RuntimeError(f"job {r['spec']} failed:\n{r['error']}")
        done[json.dumps(r["spec"])] = r
        fout.write(json.dumps(r, default=float) + "\n")
        fout.flush()

    pool = Pool(workers)
    pending = {}

    def submit(spec):
        key = json.dumps(list(spec))
        if key in done or key in pending:
            return
        pending[key] = pool.apply_async(job, (list(spec),))

    def harvest(block=False):
        got = []
        while True:
            for k in list(pending):
                if pending[k].ready():
                    r = pending.pop(k).get()
                    record(r)
                    got.append(r)
            if got or not block or not pending:
                return got
            time.sleep(2)

    def result(spec):
        return done.get(json.dumps(list(spec)))

    # phase 1: garden soup (first jumped of GARDEN_SEEDS) and the soups (first N_TARGET admitted, in seed order)
    gq, sq = list(GARDEN_SEEDS), list(SEEDS) + list(SPARES)
    g_active, active = None, []
    admitted, rejected = [], []
    gseed = None

    def next_garden():
        nonlocal g_active
        if gq:
            g_active = gq.pop(0)
            submit(("prefork", g_active))

    next_garden()
    for s in sq[:N_TARGET]:
        submit(("prefork", s))
        active.append(s)
    sq = sq[N_TARGET:]
    gate_rows, gate_submitted, gardens_submitted = [], False, False
    gate = None
    last_status = time.time()
    while True:
        # garden
        if gseed is None and g_active is not None:
            r = result(("prefork", g_active))
            if r is not None:
                if r["T"] is not None:
                    gseed = g_active
                    CFG["garden_seed"] = gseed
                    log(f"garden soup {gseed}: jump T={r['T']}")
                else:
                    log(f"garden soup {g_active}: no confirmed jump by {WAIT}")
                    g_active = None
                    if not gq:
                        raise RuntimeError("no garden soup jumped: Part B not testable")
                    next_garden()
        if gseed is not None and not gardens_submitted:
            for i in range(G_N):
                submit(("garden", i, gseed))
            gardens_submitted = True
        if gardens_submitted and not gate_submitted and all(result(("garden", i, gseed)) for i in range(G_N)):
            for i in range(G_N):
                log(f"garden {i}: {result(('garden', i, gseed))['series'][-1]}")
            for c, n in GATE_PLAN.items():
                for rep in range(n):
                    submit(("assay", "gate", gseed, c, rep, 0, "spatial"))
            gate_submitted = True
        if gate_submitted and gate is None:
            rows = [result(("assay", "gate", gseed, c, rep, 0, "spatial")) for c, n in GATE_PLAN.items() for rep in range(n)]
            if all(rows):
                gate = evaluate_gate(rows)
                save_json(OUT / "gate.json", gate)
                log(f"gate G1-G8: {'PASS' if gate['pass_G1_G8'] else 'FAIL'} " +
                    json.dumps({c: gate[c]["pass"] for c in GATE_PLAN}) + f" delta*={gate['delta_star']}")
        # soups: admission, replacement, arms
        for s in list(active):
            r = result(("prefork", s))
            if r is None or s in admitted or s in rejected:
                continue
            if r["T"] is not None:
                admitted.append(s)
                log(f"soup {s}: admitted, jump T={r['T']}, fork {r['T'] + FORK_DT}")
                for name in ARMS:
                    submit(("arm", s, name))
            else:
                rejected.append(s)
                active.remove(s)
                log(f"soup {s}: rejected (no confirmed jump by {WAIT})")
                if sq:
                    nxt = sq.pop(0)
                    active.append(nxt)
                    submit(("prefork", nxt))
                    log(f"spare {nxt} started")
        soups_done = (len([s for s in active if s in admitted or s in rejected]) == len(active)
                      and all(result(("arm", s, n)) for s in admitted for n in ARMS))
        if soups_done and gate is not None:
            break
        if not pending:
            if soups_done and gate is None and gseed is None:
                raise RuntimeError("garden never built")
            if not soups_done and not pending:
                raise RuntimeError("stalled: no pending jobs but soups not done")
        harvest(block=True)
        if time.time() - last_status > 900:
            last_status = time.time()
            log(f"status: admitted {len(admitted)}, rejected {len(rejected)}, pending {len(pending)}, "
                f"arms done {sum(1 for s in admitted for n in ARMS if result(('arm', s, n)))}")
    soups = sorted(admitted)[:N_TARGET] if len(admitted) > N_TARGET else sorted(admitted)
    log(f"phase 1 done: {len(soups)} soups admitted {soups}; rejected {rejected}")
    out = {"experiment": "E-80 Part B" + (" DRY RUN (not data)" if CFG["dry"] else ""),
           "garden_seed": gseed, "soups": soups, "rejected": rejected, "gate": gate,
           "prefork": {s: {k: v for k, v in result(("prefork", s)).items() if k != "series"} for s in soups + rejected},
           "gardens": [result(("garden", i, gseed)) for i in range(G_N)]}
    if len(soups) < N_MIN:
        out["verdict"] = f"not testable (only {len(soups)} soups admitted, < {N_MIN})"
        pool.close()
        return out
    # phase 3a: allowed groups (early, M, Mp) and the well-mixed-pairing early / M blocks
    specs = [("assay", "soup", s, g, b, j, "spatial") for s in soups for g in ("early", "M", "Mp")
             for b in range(R_BLOCKS) for j in range(S_SEEDS)]
    specs += [("assay", "soup", s, g, b, 0, "mixed") for s in soups for g in ("early", "M") for b in range(R_SEC)]
    for sp in specs:
        submit(sp)
    while pending:
        harvest(block=True)
    rows = [result(sp) for sp in specs]
    kin_ok = np.mean([r["kin"] <= KIN_MAX for r in rows if r["group"] == "early" and r["arm"] == "spatial"])
    gate["G9"] = {"pass": bool(kin_ok >= 0.9), "early_blocks_kin_free": float(kin_ok)}
    gate["passed"] = bool(gate["pass_G1_G8"] and gate["G9"]["pass"])
    save_json(OUT / "gate.json", gate)
    out["gate"], out["gate_passed"] = gate, gate["passed"]
    log(f"gate G9 kin-free share {kin_ok:.3f}: {'PASS' if gate['G9']['pass'] else 'FAIL'}; gate {'PASSED' if gate['passed'] else 'FAILED'}")
    m, kept = soup_means(rows, soups)
    out["seed_null"] = contrast(m, kept, "Mp", "M", soups)
    out["M_vs_early"] = contrast(m, kept, "M", "early", soups)
    if not gate["passed"] and not CFG["dry"]:   # (the dry run exercises the S path regardless; not data)
        out["verdict"] = "not testable (validation gate failed; no S block scored)"
        pool.close()
        return out
    # phase 3b: S blocks, only now
    CFG["s_allowed"] = True
    specs_s = [("assay", "soup", s, g, b, j, "spatial") for s in soups for g in ("S", "Sshuf")
               for b in range(R_BLOCKS) for j in range(S_SEEDS)]
    specs_s += [("assay", "soup", s, "S", b, 0, "mixed") for s in soups for b in range(R_SEC)]
    log(f"scoring S blocks: {len(specs_s)} assays")
    pool.close()
    pool = Pool(workers, initializer=_allow_s)
    pending.clear()
    for sp in specs_s:
        submit(sp)
    while pending:
        harvest(block=True)
    pool.close()
    rows += [result(sp) for sp in specs_s]
    out.update(analyse(rows, soups, gate["delta_star"]))
    save_json(OUT / "analysis.json", {k: v for k, v in out.items() if k != "assays"})
    out["assays"] = rows
    return out


def _allow_s():
    CFG["s_allowed"] = True


def analyse(rows, soups, delta_star) -> dict:
    m, kept = soup_means(rows, soups)
    prim = contrast(m, kept, "S", "M", soups)
    null = contrast(m, kept, "Mp", "M", soups)
    mm, km = soup_means(rows, soups, arm="mixed")
    ok = [s for s in prim.get("soups", []) if mm.get((s, "S")) is not None and mm.get((s, "M")) is not None]
    dd = [(m[(s, "S")] - m[(s, "M")]) - (mm[(s, "S")] - mm[(s, "M")]) for s in ok]
    ml, kl = soup_means(rows, soups, log=True)
    return {"primary": prim, "seed_null": null, "verdict": verdict(prim, null, delta_star), "delta_star": delta_star,
            "kin_excluded": {f"{s}/{g}": kept[(s, g)][1] - kept[(s, g)][0] for (s, g) in kept},
            "means": {f"{s}/{g}": (round(v, 4) if v is not None else None) for (s, g), v in m.items()},
            "secondary": {"S_vs_early": contrast(m, kept, "S", "early", soups),
                          "M_vs_early": contrast(m, kept, "M", "early", soups),
                          "Mp_vs_early": contrast(m, kept, "Mp", "early", soups),
                          "S_preserved_vs_shuffled": contrast(m, kept, "S", "Sshuf", soups),
                          "wellmixed_pairing_S_vs_M": contrast(mm, km, "S", "M", soups),
                          "wellmixed_pairing_S_vs_early": contrast(mm, km, "S", "early", soups),
                          "wellmixed_pairing_M_vs_early": contrast(mm, km, "M", "early", soups),
                          "lattice_minus_wellmixed": {"soups": ok, "d": [round(v, 4) for v in dd],
                                                      "mean_d": round(float(np.mean(dd)), 4) if dd else None,
                                                      "p_two_sided": LA.signflip_p(dd, two_sided=True) if len(dd) >= 3 else None}},
            "sensitivity": {"T32": contrast(*soup_means(rows, soups, T=32), "S", "M", soups),
                            "log_score": contrast(ml, kl, "S", "M", soups),
                            "log_score_seed_null": contrast(ml, kl, "Mp", "M", soups)}}


if __name__ == "__main__":
    main()
