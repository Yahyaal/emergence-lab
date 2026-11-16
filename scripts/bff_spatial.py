"""E-78 groundwork: BFF soups where programs meet only lattice neighbours, beside well-mixed soups.

`ArmSoup` is `bff.Soup` with one thing changed: the pair list. Everything else is the same C epoch
(`bff_epoch`: for pair p, programs pairs[2p] and pairs[2p+1] are concatenated, the FIRST one's half is
where the instruction pointer starts, the tape is run, the halves are written back) and the same
mutation code, in the same order of generator calls (pairs first, then binomial / positions / values).

* arm "mixed": pairs = rng.permutation(n), exactly `bff.Soup.epoch` (bit-identical for the same seed,
  checked by `controls`). Order inside a pair is random because the permutation is.
* arm "spatial": the n programs sit on a W x H torus (index i = y * W + x, W and H even). Each round:
  axis = rng.integers(2) (0 horizontal, 1 vertical), offset = rng.integers(2), then one coin per pair
  (rng.integers(0, 2, n // 2)) for which program runs first. Horizontal: (x, y) is paired with (x + 1, y)
  for x = offset mod 2 (x + 1 wraps); vertical likewise. Every round is a perfect matching of lattice
  neighbours; over rounds each program meets each of its 4 neighbours with probability 1/4.

Mutation is applied to the flat program array (positions uniform), so it is identical in law in both arms.

Placement of an E-54 snapshot on the grid: rows permuted by `placement(seed)`; the same permutation
is used for every arm, so all arms start from the same array.

    python scripts/bff_spatial.py --controls            # slow controls (minutes), writes runs/e78/controls.json
    python scripts/bff_spatial.py --pilot 5301 --rounds 200 --e54 /path/to/runs/e54   # timing pilot
    python scripts/bff_spatial.py --load 11 --rounds 30 --e54 ...                      # 11 soups at once
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from emergence.programs import bff as B  # noqa: E402

ARMS = ("mixed", "spatial")
SIDE = 256                      # 256 x 256 = 2^16, the E-54 soup size
E54 = Path(os.environ.get("E54_DIR", "runs/e54"))
OUT = Path("runs/e78")


def _json(o):
    return o.item() if hasattr(o, "item") else str(o)
# E-54 jumped soups: seed -> jump round T (docs/data/experiments/2026-11-08-e54-long-soups.json)
JUMPED = {5301: 21750, 5302: 13750, 5308: 12500, 5401: 10250, 5402: 22250, 5406: 16750, 5410: 750}
FORK_DT = 2000                  # fork at the T + 2000 snapshot (the E-54 "early" time point)


def spatial_pairs(rng: np.random.Generator, w: int, h: int) -> np.ndarray:
    """One round's pair list (int32, length w*h, pairs at [2p, 2p+1], first = runs first)."""
    axis, off = int(rng.integers(2)), int(rng.integers(2))
    if axis == 0:
        ys, xs = np.meshgrid(np.arange(h), np.arange(off, w, 2), indexing="ij")
        a, b = ys * w + xs, ys * w + (xs + 1) % w
    else:
        ys, xs = np.meshgrid(np.arange(off, h, 2), np.arange(w), indexing="ij")
        a, b = ys * w + xs, ((ys + 1) % h) * w + xs
    a, b = a.ravel(), b.ravel()
    flip = rng.integers(0, 2, len(a)).astype(bool)
    first, second = np.where(flip, b, a), np.where(flip, a, b)
    return np.stack([first, second], 1).ravel().astype(np.int32)


class ArmSoup(B.Soup):
    """bff.Soup whose pair list depends on the arm; see module docstring."""

    def __init__(self, arm: str = "mixed", width: int | None = None, record_mutations: bool = False, **kw):
        super().__init__(**kw)
        if arm not in ARMS:
            raise ValueError(arm)
        self.arm = arm
        self.width = width or int(round(np.sqrt(self.n)))
        self.height = self.n // self.width
        if arm == "spatial" and (self.width * self.height != self.n or self.width % 2 or self.height % 2):
            raise ValueError("spatial arm needs n = W * H with W, H even")
        self.record_mutations = record_mutations
        self.last_pairs: np.ndarray | None = None
        self.last_mut_idx: np.ndarray | None = None

    def pairs(self) -> np.ndarray:
        if self.arm == "mixed":
            return self.rng.permutation(self.n).astype(np.int32)
        return spatial_pairs(self.rng, self.width, self.height)

    def epoch(self) -> int:
        pairs = self.pairs()
        self.last_pairs = pairs
        self.last_steps = int(B._lib().bff_epoch(self.programs.ctypes.data, self.length, pairs.ctypes.data,
                                                 self.n // 2, self.max_steps, B.MODES[self.mode]))
        idx = np.empty(0, np.int64)
        if self.mutation > 0:   # identical to bff.Soup.epoch
            k = self.rng.binomial(self.programs.size, self.mutation)
            idx = self.rng.integers(0, self.programs.size, k)
            self.programs.reshape(-1)[idx] = self.rng.integers(0, 256, k, dtype=np.uint8)
        if self.record_mutations:
            self.last_mut_idx = idx
        self.epochs += 1
        return self.last_steps


def placement(soup_seed: int, n: int = SIDE * SIDE) -> np.ndarray:
    """Seeded random placement of snapshot rows onto grid cells (shared by all arms of a soup)."""
    return np.random.default_rng([78, soup_seed]).permutation(n)


def arm_seed(soup_seed: int, arm_code: int) -> list[int]:
    """Generator seed of a continuation: 0 = M (mixed), 1 = S (spatial), 2 = M' (second mixed, seed null)."""
    return [78, soup_seed, arm_code]


def fork(soup_seed: int, arm: str, arm_code: int, e54: Path = E54, **kw) -> ArmSoup:
    T = JUMPED[soup_seed]
    P = np.load(e54 / f"{soup_seed}-{T + FORK_DT}.npy")[placement(soup_seed)]
    s = ArmSoup(arm=arm, n=len(P), seed=arm_seed(soup_seed, arm_code), programs=P, **kw)
    s.epochs = T + FORK_DT
    return s


# ---- measurements -------------------------------------------------------------------------------

def like(P: np.ndarray, x: np.ndarray, sim: float = 0.9) -> np.ndarray:
    return ((P == x).mean(1) >= sim) | ((P == x[::-1]).mean(1) >= sim)


def families(P: np.ndarray, min_share: float = 0.01, max_reps: int = 200) -> list[dict]:
    """90%-identity families (either orientation), greedy from the most common exact programs: each
    representative not like an earlier one founds a family; members = programs like it and not yet
    assigned. Returns families holding >= min_share of the soup."""
    assigned = np.zeros(len(P), bool)
    out = []
    for prog, _ in B.top_programs(P, max_reps):
        x = np.frombuffer(prog, np.uint8)
        if assigned[np.flatnonzero((P == x).all(1))[0]]:
            continue
        m = like(P, x) & ~assigned
        assigned |= m
        if m.sum() >= min_share * len(P):
            out.append({"rep": prog.hex(), "count": int(m.sum()), "mask": m})
    return out


def neighbour_ratio(mask: np.ndarray, w: int) -> float:
    """Clustering of a set of cells on the torus: mean share of a member's 4 neighbours that are members,
    divided by the set's overall share. 1 = no clustering (well mixed), > 1 = patches."""
    g = mask.reshape(-1, w)
    if g.sum() == 0 or g.all():
        return float("nan")
    nb = (np.roll(g, 1, 0).astype(int) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1))[g] / 4
    return float(nb.mean() / g.mean())


def largest_component_share(mask: np.ndarray, w: int) -> float:
    """Share of the set in its largest 4-connected component on the torus (union-find, numpy only)."""
    g = mask.reshape(-1, w)
    h = g.shape[0]
    idx = np.flatnonzero(g.ravel())
    if len(idx) == 0:
        return float("nan")
    parent = {int(i): int(i) for i in idx}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in idx:
        y, x = divmod(int(i), w)
        for j in (y * w + (x + 1) % w, ((y + 1) % h) * w + x):
            if j in parent:
                ri, rj = find(int(i)), find(j)
                if ri != rj:
                    parent[ri] = rj
    roots = np.array([find(int(i)) for i in idx])
    return float(np.bincount(np.unique(roots, return_inverse=True)[1]).max() / len(idx))


def summary(s: ArmSoup, steps: int) -> dict:
    fam = families(s.programs)
    top = fam[0]["count"] / s.n if fam else 0.0
    return {"epoch": s.epochs, "steps_per_pair": round(steps / (s.n / 2), 1),
            "hoe": round(B.high_order_entropy(s.programs), 3),
            # HOE compresses the array in storage order; in the spatial arm neighbouring rows are kin, so raw
            # HOE rises with clustering alone. Compare arms with HOE of a fixed shuffle of the rows.
            "hoe_shuffled": round(B.high_order_entropy(s.programs[np.random.default_rng(0).permutation(s.n)]), 3),
            "families_ge1pct": len(fam),
            "top_family_share": round(top, 4), "distinct_exact": int(len(np.unique(s.programs, axis=0))),
            "top_family_neighbour_ratio": round(neighbour_ratio(fam[0]["mask"], s.width), 3) if fam else None}


# ---- controls -----------------------------------------------------------------------------------

def check_matching(rounds: int = 200, w: int = SIDE, h: int = SIDE, seed: int = 1) -> dict:
    """Every round's spatial pairs: a perfect matching of torus neighbours; all 4 (axis, offset) used;
    the first program is the 'a' cell about half of the time."""
    rng = np.random.default_rng(seed)
    n = w * h
    bad, firsts, combos = 0, [], set()
    for _ in range(rounds):
        st = rng.bit_generator.state
        axis, off = int(rng.integers(2)), int(rng.integers(2))
        rng.bit_generator.state = st
        combos.add((axis, off))
        p = spatial_pairs(rng, w, h)
        ok = len(p) == n and np.array_equal(np.sort(p), np.arange(n))
        a, b = p[0::2], p[1::2]
        ya, xa, yb, xb = a // w, a % w, b // w, b % w
        dx, dy = (xb - xa) % w, (yb - ya) % h
        nbr = ((dy == 0) & ((dx == 1) | (dx == w - 1))) | ((dx == 0) & ((dy == 1) | (dy == h - 1)))
        ok &= bool(nbr.all())
        bad += not ok
        lower = np.where(axis == 0, xa % 2 == off, ya % 2 == off)  # 'a' is the cell at the offset parity
        firsts.append(float(lower.mean()))
    return {"rounds": rounds, "bad_rounds": bad, "combos": sorted(combos), "first_is_offset_cell": round(float(np.mean(firsts)), 4),
            "pass": bool(bad == 0 and len(combos) == 4 and abs(np.mean(firsts) - 0.5) < 0.01)}


def check_mixed_identical(programs: np.ndarray | None = None, rounds: int = 50, seed: int = 7, n: int = 2 ** 12,
                          mutation: float = 0.00024) -> dict:
    """The mixed arm through ArmSoup equals bff.Soup (same seed) bit for bit, every round."""
    a = B.Soup(n=n if programs is None else len(programs), seed=seed, programs=programs, mutation=mutation)
    b = ArmSoup(arm="mixed", n=a.n, seed=seed, programs=programs if programs is not None else a.programs.copy(),
                mutation=mutation)
    if programs is None:  # bff.Soup drew its random start from its generator; replay that draw for b
        b.rng = np.random.default_rng(seed)
        b.rng.integers(0, 256, (a.n, a.length), dtype=np.uint8)
    diff, steps = [], []
    for _ in range(rounds):
        sa, sb = a.epoch(), b.epoch()
        diff.append(int((a.programs != b.programs).sum()) + (sa != sb))
        steps.append(sa)
    return {"rounds": rounds, "n": a.n, "rounds_differing": int(sum(d > 0 for d in diff)),
            "mean_steps_per_pair": round(float(np.mean(steps)) / (a.n / 2), 1), "pass": not any(diff)}


def seeded_block(side: int, block: int, rng: np.random.Generator) -> np.ndarray:
    P = rng.integers(0, 256, (side * side, 64), dtype=np.uint8)
    c0 = side // 2 - block // 2
    for y in range(c0, c0 + block):
        P[y * side + c0: y * side + c0 + block] = B.REPLICATOR
    return P


def spread(arm: str, mode: str = "bff", side: int = 128, block: int = 4, rounds: int = 300, seed: int = 78,
           mutation: float = 0.0, every: int = 5) -> dict:
    """Positive locality control: a block of the hand-written replicator in a random soup."""
    P = seeded_block(side, block, np.random.default_rng([seed, 0]))
    s = ArmSoup(arm=arm, n=side * side, width=side, mode=mode, mutation=mutation, seed=[seed, 1, ARMS.index(arm)],
                programs=P)
    rows = []
    for t in range(rounds + 1):
        if t % every == 0:
            m = (s.programs == B.REPLICATOR).mean(1) >= 0.9
            rows.append({"t": t, "copies": int(m.sum()), "share": round(float(m.mean()), 4),
                         "nbr_ratio": round(neighbour_ratio(m, side), 2),
                         "largest_component": round(largest_component_share(m, side), 3)})
        if t < rounds:
            s.epoch()
    return {"arm": arm, "mode": mode, "side": side, "block": block, "series": rows}


def growth_shape(series: list[dict], lo: float = 0.005, hi: float = 0.3) -> dict:
    """Over the growth phase (share in [lo, hi]): slope of log(excess copies) vs log t, excess = copies minus
    the seeded block (2 = an area growing at constant front speed), and R^2 of log copies vs t (exponential)
    against R^2 of sqrt(copies) vs t (front at constant speed)."""
    c0 = series[0]["copies"]
    pts = [(r["t"], r["copies"]) for r in series if lo <= r["share"] <= hi and r["t"] > 0 and r["copies"] > c0]
    if len(pts) < 4:
        return {"points": len(pts)}
    t, c = np.array(pts, float).T

    def r2(x, y):
        return float(np.corrcoef(x, y)[0, 1] ** 2)
    return {"points": len(pts), "loglog_slope": round(float(np.polyfit(np.log(t), np.log(c - c0), 1)[0]), 2),
            "r2_exponential": round(r2(t, np.log(c)), 4), "r2_sqrt_linear": round(r2(t, np.sqrt(c)), 4),
            "t_range": [int(t[0]), int(t[-1])]}


def check_noexec(rounds: int = 60, side: int = 64, seed: int = 9) -> dict:
    """Deceptive: under noexec both arms change nothing but mutation: (a) with mutation 0 the array is
    unchanged; (b) with mutation, every changed byte is at a recorded mutation position; (c) a replicator
    block does not spread in either arm (copies never exceed the seeded 16), although its S-arm cluster
    statistic stays high (clustering alone is not evidence of local spread)."""
    out = {}
    for arm in ARMS:
        P = seeded_block(side, 4, np.random.default_rng([seed, 0]))
        s0 = ArmSoup(arm=arm, n=side * side, width=side, mode="noexec", mutation=0.0, seed=[seed, 1], programs=P)
        for _ in range(rounds):
            s0.epoch()
        unchanged = bool((s0.programs == P).all())
        s1 = ArmSoup(arm=arm, n=side * side, width=side, mode="noexec", mutation=0.001, seed=[seed, 2], programs=P,
                     record_mutations=True)
        allowed = np.zeros(P.size, bool)
        for _ in range(rounds):
            s1.epoch()
            allowed[s1.last_mut_idx] = True
        changed = (s1.programs != P).ravel()
        only_mut = bool(not (changed & ~allowed).any())
        m = (s1.programs == B.REPLICATOR).mean(1) >= 0.9
        out[arm] = {"unchanged_without_mutation": unchanged, "changes_only_at_mutations": only_mut,
                    "changed_bytes": int(changed.sum()), "copies_end": int(m.sum()),
                    "nbr_ratio_end": round(neighbour_ratio(m, side), 2)}
    out["pass"] = all(out[a]["unchanged_without_mutation"] and out[a]["changes_only_at_mutations"]
                      and out[a]["copies_end"] <= 16 for a in ARMS)
    return out


def _spread_job(arg):
    arm, mode = arg
    return spread(arm, mode)


def controls(e54: Path = E54, workers: int = 4) -> dict:
    t0 = time.time()
    res = {"matching": check_matching(), "mixed_identical_random": check_mixed_identical()}
    snap = e54 / f"5301-{JUMPED[5301] + FORK_DT}.npy"
    if snap.exists():   # a jumped soup (long runs, ~8000 steps per pair): 4096 sampled programs, 50 rounds
        P = np.load(snap)[np.random.default_rng(78).choice(2 ** 16, 2 ** 12, replace=False)]
        res["mixed_identical_snapshot"] = check_mixed_identical(programs=P) | {"snapshot": snap.name}
    res["noexec"] = check_noexec()
    with Pool(min(workers, 4)) as pool:
        sp = pool.map(_spread_job, [("spatial", "bff"), ("mixed", "bff"), ("spatial", "noexec"), ("mixed", "noexec")])
    res["spread"] = {f"{r['arm']}/{r['mode']}": r | {"shape": growth_shape(r["series"])} for r in sp}
    S, M = res["spread"]["spatial/bff"], res["spread"]["mixed/bff"]

    def mid(r):  # the first sample with share >= 2%, before saturation
        return next((x for x in r["series"] if x["share"] >= 0.02), r["series"][-1])
    res["spread_verdict"] = {
        "S_quadratic": 1.4 <= S["shape"].get("loglog_slope", 0) <= 2.6 and S["shape"]["r2_sqrt_linear"] > S["shape"]["r2_exponential"],
        "S_clustered": mid(S)["nbr_ratio"] >= 5 and mid(S)["largest_component"] >= 0.8,
        "M_exponential": M["shape"].get("r2_exponential", 0) > M["shape"].get("r2_sqrt_linear", 1),
        "M_unclustered": abs(mid(M)["nbr_ratio"] - 1) < 0.5,
        "noexec_no_spread": all(max(x["copies"] for x in res["spread"][f"{a}/noexec"]["series"]) <= 16 for a in ARMS)}
    res["spread_verdict"] = {k: bool(v) for k, v in res["spread_verdict"].items()}
    res["spread_verdict"]["pass"] = all(res["spread_verdict"].values())
    res["pass"] = all(v.get("pass", True) for v in (res["matching"], res["mixed_identical_random"],
                                                    res.get("mixed_identical_snapshot", {}), res["noexec"],
                                                    res["spread_verdict"]))
    res["seconds"] = round(time.time() - t0)
    return res


# ---- timing pilot -------------------------------------------------------------------------------

def _pilot_job(arg):
    soup_seed, arm, code, rounds, every, e54 = arg
    s = fork(soup_seed, arm, code, Path(e54))
    rows, sec, tot = [summary(s, 0) | {"sec": 0.0}], 0.0, 0
    for _ in range(rounds):
        t0 = time.time()
        st = s.epoch()
        sec += time.time() - t0     # epoch time only (summaries excluded)
        tot += st
        if (s.epochs - JUMPED[soup_seed] - FORK_DT) % every == 0:
            rows.append(summary(s, st) | {"sec": round(sec, 1)})
    np.save(OUT / f"pilot-{soup_seed}-{arm}{code}-{s.epochs}.npy", s.programs)
    return {"soup": soup_seed, "arm": arm, "code": code, "rounds": rounds, "wall_sec": round(sec, 1),
            "sec_per_round": round(sec / rounds, 4), "mean_steps_per_pair": round(tot / rounds / (s.n / 2), 1),
            "series": rows}


def original_stats(soup_seed: int, e54: Path) -> dict:
    """The original E-54 run: logged steps per pair / HOE around the fork, and summaries of its snapshots."""
    T = JUMPED[soup_seed]
    rec = json.loads((e54 / f"{soup_seed}.json").read_text())
    ser = [r for r in rec["series"] if T + FORK_DT - 1000 <= r["epoch"] <= T + FORK_DT + 3000]
    snaps = {}
    for dt in (FORK_DT, FORK_DT + 2000):
        P = np.load(e54 / f"{soup_seed}-{T + dt}.npy")
        fam = families(P)
        snaps[T + dt] = {"hoe": round(B.high_order_entropy(P), 3), "families_ge1pct": len(fam),
                         "top_family_share": round(fam[0]["count"] / len(P), 4) if fam else 0.0,
                         "distinct_exact": int(len(np.unique(P, axis=0)))}
    return {"log_series": ser, "snapshots": snaps, "generator_state_saved": False}


def _load_job(arg):
    soup_seed, arm, code, rounds, e54 = arg
    s = fork(soup_seed, arm, code, Path(e54))
    t0, tot = time.time(), 0
    for _ in range(rounds):
        tot += s.epoch()
    sec = time.time() - t0
    return {"soup": soup_seed, "arm": arm, "sec_per_round": round(sec / rounds, 4),
            "steps_per_pair": round(tot / rounds / (s.n / 2), 1)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--pilot", type=int)
    ap.add_argument("--load", type=int, help="run this many forks at once (timing under load)")
    ap.add_argument("--rounds", type=int, default=200)
    ap.add_argument("--every", type=int, default=50)
    ap.add_argument("--e54", default=str(E54))
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    e54 = Path(a.e54)
    if a.controls:
        r = controls(e54, a.workers)
        (OUT / "controls.json").write_text(json.dumps(r, indent=1, default=_json))
        print(json.dumps({k: v for k, v in r.items() if k != "spread"}, indent=1, default=_json))
        for k, v in r["spread"].items():
            print(k, v["shape"], [(x["t"], x["copies"], x["nbr_ratio"]) for x in v["series"][::4]])
        print("=== E78 CONTROLS DONE", flush=True)
    if a.pilot:
        with Pool(2) as pool:
            res = pool.map(_pilot_job, [(a.pilot, "mixed", 0, a.rounds, a.every, a.e54),
                                        (a.pilot, "spatial", 1, a.rounds, a.every, a.e54)])
        out = {"soup": a.pilot, "fork_epoch": JUMPED[a.pilot] + FORK_DT, "arms": res,
               "original": original_stats(a.pilot, e54)}
        (OUT / f"pilot-{a.pilot}.json").write_text(json.dumps(out, indent=1, default=str))
        print(json.dumps(out, indent=1, default=str))
        print("=== E78 PILOT DONE", flush=True)
    if a.load:
        jobs = [(sd, arm, code, a.rounds, a.e54) for sd in JUMPED for arm, code in (("mixed", 0), ("spatial", 1))]
        with Pool(a.load) as pool:
            res = pool.map(_load_job, jobs[:a.load], chunksize=1)
        (OUT / f"load-{a.load}.json").write_text(json.dumps(res, indent=1))
        print(json.dumps(res, indent=1))
        print("=== E78 LOAD DONE", flush=True)


if __name__ == "__main__":
    main()
