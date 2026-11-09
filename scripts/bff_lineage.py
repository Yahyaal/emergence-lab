"""E-62 (docs/data/e62-preregistration.md): lineage persistence of short copiers across all 128 head-start rules,
and fresh soups under the strict D-047 jump criterion.

    python scripts/bff_lineage.py --part census --workers 9 --out docs/data/experiments/2026-11-09-e62-census.json
    python scripts/bff_lineage.py --part soups --workers 9 --out docs/data/experiments/2026-11-09-e62-soups.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from math import comb
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bff_counterfactual as C  # noqa: E402
import bff_kernels as K  # noqa: E402
import bff_orient_confirm as E  # noqa: E402
import bff_shift_census as S  # noqa: E402
from emergence.programs import bff as B  # noqa: E402

GEN, MAXSHIFT, SLACK = 64, 16, 4
RUN = Path("runs/e62")
N, WAIT, AFTER, EVERY, THRESH, PERSIST, MIN_COP = 2 ** 14, 16000, 1000, 250, 1.0, 3, 10


def copies_itself(x: np.ndarray, h: int, rng, runs: int = 4) -> bool:
    """The product of one run matches x at some shift |d| <= MAXSHIFT (overlap minus SLACK) in >= 3 of 4 runs.
    Unlike classify_shift, the parent's own half may be damaged (a lineage only needs its copies)."""
    good = 0
    for _ in range(runs):
        p = S.product(x, h, rng)
        ok = False
        for d in range(-MAXSHIFT, MAXSHIFT + 1):
            ov = K.L - abs(d)
            a, b = (p[d:], x[:K.L - d]) if d >= 0 else (p[:K.L + d], x[-d:])
            if int((a == b).sum()) >= ov - SLACK:
                ok = True
                break
        good += ok
    return good >= 3


def lineage(x: np.ndarray, h: int, rng, gen: int = GEN) -> int:
    """Generations the line survives (gen + 1 = persists): follow one product per generation; at the end the
    descendant must still copy itself."""
    cur = x.copy()
    for g in range(1, gen + 1):
        cur = S.product(cur, h, rng)
        if g % 16 == 0 and not copies_itself(cur, h, rng):
            return g
    return gen + 1 if copies_itself(cur, h, rng) else gen


def census_rule(h: int) -> dict:
    rng = np.random.default_rng([62, h])
    rows = []
    for k in (5, 6):
        for lo in range(0, 10 ** k, K.CHUNK):
            P = K.programs(k, lo, min(lo + K.CHUNK, 10 ** k), False)
            scr = np.nonzero(K.classify_shift(P, h, 1, 0x6201 + k)[0])[0]
            if len(scr):
                conf, sh = K.classify_shift(P[scr], h, 4, 0x6202 + k)
                for i, c, d in zip(scr, conf, sh):
                    if c:
                        rows.append({"kernel": bytes(P[i, :k]).decode(), "orientation": K.label(c), "shift": int(d),
                                     "survives": lineage(P[i].copy(), h, rng)})
    per = [r for r in rows if r["survives"] > GEN]
    return {"h": h, "copiers": len(rows), "persistent": len(per), "class": "P" if per else "N",
            "persistent_shifts": sorted({r["shift"] for r in per}),
            "persistent_orientation": sorted({r["orientation"] for r in per}),
            "examples_persistent": [(r["kernel"], r["shift"]) for r in per][:6],
            "survival_by_shift": {str(d): [r["survives"] for r in rows if r["shift"] == d][:20]
                                  for d in sorted({r["shift"] for r in rows})}}


def controls() -> dict:
    rng = np.random.default_rng(620)
    import bff_mirror as M
    return {"handwritten_h0": lineage(B.REPLICATOR.copy(), 0, rng) > GEN,
            "fwd_kernel_h64": lineage(M.filled(b"[.>}]", rng), 64, rng) > GEN,
            "fwd_kernel_h66_shift2": lineage(M.filled(b"[.>}]", rng), 66, rng) > GEN,
            "random_h0_h64": sum(lineage(rng.integers(0, 256, 64, dtype=np.uint8), h, rng) > GEN
                                 for h in (0, 64) for _ in range(50))}


def census(workers: int) -> dict:
    ctl = controls()
    with Pool(workers) as pool:
        res = pool.map(census_rule, range(128), chunksize=1)
    P = [r["h"] for r in res if r["class"] == "P"]
    return {"controls": ctl, "controls_ok": ctl["handwritten_h0"] and ctl["fwd_kernel_h64"]
            and not ctl["fwd_kernel_h66_shift2"] and ctl["random_h0_h64"] == 0,
            "rules": res, "P": P, "primary1": "pass" if P == [62, 63, 64, 65] else "fail"}


def job(arg) -> dict:
    """D-047 strict criterion: candidate T as D-046 (HOE >= 1 at 3 checkpoints and >= 1 shift-aware copier);
    confirmed if >= MIN_COP copiers among the 40 most common programs at T + AFTER; otherwise the candidate is
    dropped and the same soup runs on, up to WAIT rounds."""
    seed, h1 = arg
    path = RUN / f"{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    soup = E.Soup(h1, n=N, seed=seed)
    series, run, cand, T, dropped = [], 0, None, None, []
    while True:
        st = soup.epoch()
        e = soup.epochs
        if e % EVERY == 0:
            hoe = B.high_order_entropy(soup.programs)
            series.append({"epoch": e, "hoe": round(hoe, 3), "steps_per_pair": round(st / (N / 2), 1)})
            if cand is None:
                run = run + 1 if hoe >= THRESH else 0
                if run >= PERSIST:
                    o = S.orient_shift(soup.programs, h1, 620 + seed + e)
                    if o["forward"] + o["reverse"] + o["both"] >= 1:
                        cand = e - EVERY * (PERSIST - 1)
            elif e == cand + AFTER:
                o = S.orient_shift(soup.programs, h1, 621 + seed + e)
                n = o["forward"] + o["reverse"] + o["both"]
                if n >= MIN_COP:
                    T = cand
                    break
                dropped.append({"candidate": cand, "copiers_at_plus_1000": n, "steps": series[-1]["steps_per_pair"]})
                cand, run = None, 0
        if cand is None and e >= WAIT:
            break
    o = S.orient_shift(soup.programs, h1, 622 + seed)
    res = {"seed": seed, "h1": h1, "T": T, "jumped": T is not None, "end": soup.epochs, "dropped": dropped,
           "orientation": o, "series": series, "sec": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    print(json.dumps({"done": seed, "h1": h1, "T": T, "end": soup.epochs, "dropped": len(dropped),
                      "orientation": {k: v for k, v in o.items() if k != "copiers"}}), flush=True)
    return res


def soups(workers: int, census_path: str) -> dict:
    c = json.load(open(census_path))
    F = [61, 62, 63, 64, 65, 66, 67, 68]  # E-61 F'
    grpP = [h for h in F if h in c["P"] and h != 64]
    grpN = [h for h in F if h not in c["P"]]
    if not grpP or not grpN:
        return {"summary": {"primary2": "undecided (a group is empty)", "P": grpP, "N": grpN}, "results": []}
    rules = grpP + grpN
    jobs = [(6200 + 10 * r + i, h) for r, h in enumerate(rules) for i in range(4)]
    RUN.mkdir(parents=True, exist_ok=True)
    with Pool(workers) as pool:
        res = pool.map(job, jobs, chunksize=1)
    jp = sum(r["jumped"] for r in res if r["h1"] in grpP); nP = 4 * len(grpP)
    jn = sum(r["jumped"] for r in res if r["h1"] in grpN); nN = 4 * len(grpN)
    m, tot = jp + jn, nP + nN
    p = sum(comb(m, x) * comb(tot - m, nP - x) for x in range(jp, min(m, nP) + 1)) / comb(tot, nP)
    ok = jp >= 0.75 * nP and p < 0.05
    return {"summary": {"P": grpP, "N": grpN, "jumped_P": jp, "of_P": nP, "jumped_N": jn, "of_N": nN, "fisher_p": p,
                        "primary2": "pass" if ok else "fail",
                        "per_rule": {h: {"jumped": sum(r["jumped"] for r in res if r["h1"] == h),
                                         "T": [r["T"] for r in res if r["h1"] == h]} for h in rules}},
            "results": res}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=("census", "soups"), required=True)
    ap.add_argument("--workers", type=int, default=9)
    ap.add_argument("--census", default="docs/data/experiments/2026-11-09-e62-census.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0 = time.time()
    out = {"experiment": "E-62", "part": a.part} | (census(a.workers) if a.part == "census" else soups(a.workers, a.census))
    out["seconds"] = round(time.time() - t0)
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("results", "rules")}, indent=1, default=str))
    print(f"=== E62 {a.part.upper()} DONE", flush=True)


if __name__ == "__main__":
    main()
