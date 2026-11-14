"""E-78 run phase (docs/data/e78-preregistration.md): the 7 jumped E-54 soups forked at T + 2000 into three
continuations of 20,000 rounds each: M (well mixed), S (256 x 256 torus, neighbour matching), Mp (M', a second
well-mixed continuation with another seed). Runner: scripts/bff_spatial.py (ArmSoup).

Resumable: every SNAP rounds each (soup, arm) writes its programs (.npy) and a state file (.json: round, the
generator state, the light series and the snapshot summaries so far). The state file is written last (atomic
rename), so a snapshot counts only when both exist. A restarted job continues from its last state file and gives
the same result as an uninterrupted run (`check_resume`, also in pytest).

    nohup python scripts/e78_run.py --workers 11 --e54 /path/to/runs/e54 > runs/e78/run.log 2>&1 &
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_spatial as BS  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

RUN = Path("runs/e78/run")
H, SNAP, EVERY = 20000, 2000, 250
ARMS3 = {"M": ("mixed", 0), "S": ("spatial", 1), "Mp": ("mixed", 2)}


def snapshot_stats(P: np.ndarray, width: int) -> dict:
    fam = BS.families(P)
    ratios = [BS.neighbour_ratio(f["mask"], width) for f in fam]
    return {"hoe": round(B.high_order_entropy(P), 3),
            "hoe_shuffled": round(B.high_order_entropy(P[np.random.default_rng(0).permutation(len(P))]), 3),
            "distinct_exact": int(len(np.unique(P, axis=0))), "families_ge1pct": len(fam),
            "family_shares": [round(f["count"] / len(P), 4) for f in fam],
            "family_nbr_ratio": [round(r, 2) for r in ratios],
            "median_nbr_ratio": round(float(np.median(ratios)), 2) if ratios else None,
            "top_family_largest_patch": round(BS.largest_component_share(fam[0]["mask"], width), 3) if fam else None}


def _atomic_save_npy(path: Path, arr: np.ndarray) -> None:
    tmp = path.with_suffix(".tmp.npy")
    np.save(tmp, arr)
    os.replace(tmp, path)


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def run_arm(tag: str, programs0: np.ndarray, arm: str, seed, start: int, end: int, outdir: Path, snap: int = SNAP,
            every: int = EVERY, stats: bool = True, stop_at: int | None = None, **kw) -> dict:
    """Run one continuation from `start` to `end`, saving every `snap` rounds; resume from the last saved state.
    `stop_at` simulates an interruption (tests)."""
    outdir.mkdir(parents=True, exist_ok=True)
    states = sorted(outdir.glob(f"{tag}-*.state.json"), key=lambda p: int(p.name.split("-")[-1].split(".")[0]))
    s = BS.ArmSoup(arm=arm, n=len(programs0), seed=seed, programs=programs0, **kw)
    if states:
        st = json.loads(states[-1].read_text())
        s.programs = np.ascontiguousarray(np.load(outdir / f"{tag}-{st['epoch']}.npy"))
        s.rng.bit_generator.state = st["rng"]
        s.epochs = st["epoch"]
        series, summaries, resumed = st["series"], st["summaries"], st.get("resumed", []) + [st["epoch"]]
        if s.epochs >= end:
            return st
    else:
        s.epochs = start
        series, summaries, resumed = [], [], []

    def save():
        if stats:
            summaries.append({"epoch": s.epochs} | snapshot_stats(s.programs, s.width))
        _atomic_save_npy(outdir / f"{tag}-{s.epochs}.npy", s.programs)
        st = {"tag": tag, "epoch": s.epochs, "rng": s.rng.bit_generator.state, "series": series,
              "summaries": summaries, "resumed": resumed}
        _atomic_write(outdir / f"{tag}-{s.epochs}.state.json", json.dumps(st))
        return st
    if not states:
        st = save()
    t0 = time.time()
    while s.epochs < end:
        if stop_at is not None and s.epochs >= stop_at:
            return {"interrupted": s.epochs}
        steps = s.epoch()
        e = s.epochs
        if (e - start) % every == 0:
            row = {"epoch": e, "steps_per_pair": round(steps / (s.n / 2), 1), "sec": round(time.time() - t0, 1)}
            if stats:
                row |= {"hoe": round(B.high_order_entropy(s.programs), 3),
                        "hoe_shuffled": round(B.high_order_entropy(
                            s.programs[np.random.default_rng(0).permutation(s.n)]), 3)}
            series.append(row)
        if (e - start) % snap == 0:
            st = save()
            print(json.dumps({"tag": tag, "epoch": e, "sec": round(time.time() - t0)} | series[-1]), flush=True)
    return st


def check_resume(n: int = 1024, rounds: int = 40, snap: int = 10) -> dict:
    """A run interrupted after round 25 and restarted equals an uninterrupted run (programs, generator, series),
    in both arms."""
    out = {}
    P = np.random.default_rng(5).integers(0, 256, (n, 64), dtype=np.uint8)
    P[: n // 8] = B.REPLICATOR  # some long runs
    for arm in BS.ARMS:
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            a = run_arm("x", P.copy(), arm, [1, 2], 0, rounds, Path(d1), snap=snap, every=5, mutation=0.001)
            r = run_arm("x", P.copy(), arm, [1, 2], 0, rounds, Path(d2), snap=snap, every=5, mutation=0.001, stop_at=25)
            b = run_arm("x", P.copy(), arm, [1, 2], 0, rounds, Path(d2), snap=snap, every=5, mutation=0.001)
            pa, pb = np.load(Path(d1) / f"x-{rounds}.npy"), np.load(Path(d2) / f"x-{rounds}.npy")
            strip = lambda ser: [{k: v for k, v in row.items() if k != "sec"} for row in ser]
            out[arm] = {"interrupted_at": r.get("interrupted"), "resumed_from": b["resumed"],
                        "programs_equal": bool((pa == pb).all()), "rng_equal": a["rng"] == b["rng"],
                        "series_equal": strip(a["series"]) == strip(b["series"]),
                        "summaries_equal": a["summaries"] == b["summaries"]}
    out["pass"] = all(v["programs_equal"] and v["rng_equal"] and v["series_equal"] and v["summaries_equal"]
                      and v["resumed_from"] == [20] for v in out.values())
    return out


def job(spec) -> dict:
    seed, arm_name, e54 = spec
    arm, code = ARMS3[arm_name]
    T = BS.JUMPED[seed]
    start = T + BS.FORK_DT
    P = np.load(Path(e54) / f"{seed}-{start}.npy")[BS.placement(seed)]
    st = run_arm(f"{seed}-{arm_name}", P, arm, BS.arm_seed(seed, code), start, start + H, RUN)
    print(json.dumps({"done": f"{seed}-{arm_name}", "epoch": st["epoch"], "resumed": st["resumed"]}), flush=True)
    return {"tag": f"{seed}-{arm_name}", "epoch": st["epoch"], "resumed": st["resumed"]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--e54", default=str(BS.E54))
    ap.add_argument("--check-resume", action="store_true")
    a = ap.parse_args()
    if a.check_resume:
        print(json.dumps(check_resume(), indent=1))
        return
    RUN.mkdir(parents=True, exist_ok=True)
    # longest first (E-54 logged cost: 5302, 5301, 5402, 5308, 5401, 5406, 5410)
    order = [5302, 5301, 5402, 5308, 5401, 5406, 5410]
    specs = [(s, arm, a.e54) for s in order for arm in ("M", "S", "Mp")]
    t0 = time.time()
    with Pool(min(a.workers, 11)) as pool:
        res = pool.map(job, specs, chunksize=1)
    print(json.dumps({"finished": res, "sec": round(time.time() - t0)}), flush=True)
    print("=== E78 RUN DONE", flush=True)


if __name__ == "__main__":
    main()
