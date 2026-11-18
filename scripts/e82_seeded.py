"""E-82 seeded positive (groundwork, J-099): random code plus a designed host and a designed parasite under BFF-X.

Arms (same seeds):
  HP    random code (W bytes) + 64 hand hosts (12 bytes) + 64 hand parasites (8 bytes), libmode neighbour
  P     the parasites without hosts (the parasite cannot copy alone)
  HPn   hosts and parasites with libmode none (nothing can be borrowed)
Checkpoints at epochs 0, 5, 10, 20, 50, 100, 200, 500, 1000, 1500, 2000: byte share of the host family and of the parasite family (bffx.members of the designed
programs), the 5 commonest self-copiers ("hosts" by the copy screen with nothing to borrow) and their q against the
ancestral parasite (does the host population come to resist it?), and the commonest non-copiers that are copied with
the commonest host as library (parasite candidates).

    PYTHONPATH=.:scripts python scripts/e82_seeded.py --seeds 9601-9604 --epochs 2000 --workers 11 \
        --out runs/e82/seeded/out.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import bffx as X  # noqa: E402
import bffx_assay as A  # noqa: E402

TIMES, NH, NP = (0, 5, 10, 20, 50, 100, 200, 500, 1000, 1500, 2000), 64, 64
HOST, PARA = A.host(12), A.parasite(8)


def census(s: X.Soup, key: int) -> dict:
    top = A.soup_top(s, 40)
    hosts = [x for i, (x, _) in enumerate(top) if X.is_copier(x, key + i, libmode="none")][:5]
    paras = []
    if hosts:
        for i, (x, _) in enumerate(top):
            if any(len(x) == len(h) and (x == h).all() for h in hosts) or X.is_copier(x, key + i, libmode="none"):
                continue
            if X.screen(x, key + 300 + i, 4, libmode=s.libmode)[0] == 0 and \
                    X.screen(x, key + 600 + i, 4, host_c=hosts[0], libmode=s.libmode)[0] >= 3:
                paras.append(x)
    tot = s.lens.sum()
    fh, fp = X.members(s.buf, s.lens, HOST), X.members(s.buf, s.lens, PARA)
    return {"epoch": s.epochs, "n": s.n, "mean_len": round(float(s.lens.mean()), 2),
            "host_share": round(float(s.lens[fh].sum() / tot), 4), "para_share": round(float(s.lens[fp].sum() / tot), 4),
            "hosts": [h.tobytes().hex() for h in hosts], "paras": [p.tobytes().hex() for p in paras[:5]],
            "q_anc_para_on_hosts": round(A.q_matrix([PARA], hosts, key + 900, 16), 4) if hosts else None,
            "q_cur_para_on_anc_host": round(A.q_matrix(paras[:5], [HOST], key + 950, 16), 4) if paras else None}


EARLY = 10


def early(arm: str, seed: int, w: int = 2 ** 20) -> dict:
    """Gate of E-82. The designed parasite's family (copies) at epochs 0..EARLY, with the designed hosts (arm HP) and
    without them (arm P), mutation on, libmode neighbour. In both arms the parasite first loses copies (it is
    overwritten as a partner before hosts are common); it spreads if it then grows again: rebound = max(count,
    epochs 4..EARLY) / min(count, epochs 1..3). Pass: rebound >= 2 with hosts and < 1 without."""
    rng = np.random.default_rng([82, 6, seed])
    groups = [(HOST, NH), (PARA, NP)] if arm == "HP" else [(PARA, NP)]
    s = A.seeded_soup(rng, w, groups, "neighbour")
    s.mutation = X.MUT
    c = []
    for _ in range(EARLY + 1):
        c.append(int(X.members(s.buf, s.lens, PARA).sum()))
        s.epoch()
    reb = max(c[4:]) / max(1, min(c[1:4]))
    return {"counts": c, "rebound": round(reb, 3), "hosts": int(X.members(s.buf, s.lens, HOST).sum())}


def job(arg):
    arm, seed, epochs, w, outdir = arg
    path = Path(outdir) / f"{arm}-{seed}.json"
    if path.exists():
        return json.loads(path.read_text())
    t0 = time.time()
    rng = np.random.default_rng([82, 6, seed])
    groups = {"HP": [(HOST, NH), (PARA, NP)], "P": [(PARA, NP)], "HPn": [(HOST, NH), (PARA, NP)]}[arm]
    s = A.seeded_soup(rng, w, groups, "none" if arm == "HPn" else "neighbour")
    s.mutation = X.MUT
    traj = []
    while s.epochs <= epochs:
        if s.epochs in TIMES:
            traj.append(census(s, seed * 100003 + s.epochs * 7))
        s.epoch()
    res = {"arm": arm, "seed": seed, "traj": traj, "seconds": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="9601-9604")
    ap.add_argument("--arms", default="HP,P,HPn")
    ap.add_argument("--epochs", type=int, default=2000)
    ap.add_argument("--w", type=int, default=2 ** 20)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split("-"))
    outdir = Path(a.out).parent
    outdir.mkdir(parents=True, exist_ok=True)
    jobs = [(arm, sd, a.epochs, a.w, str(outdir)) for sd in range(lo, hi + 1) for arm in a.arms.split(",")]
    res = []
    with Pool(a.workers) as p:
        for r in p.imap_unordered(job, jobs):
            tr = r["traj"]
            pk = max(tr, key=lambda t: t["para_share"])
            print(f"{r['arm']:4s} {r['seed']} peak parasite {pk['para_share']} at {pk['epoch']}; final host "
                  f"{tr[-1]['host_share']} para {tr[-1]['para_share']} len {tr[-1]['mean_len']} "
                  f"q(anc para, hosts) {tr[-1]['q_anc_para_on_hosts']} {r['seconds']}s", flush=True)
            res.append(r)
    Path(a.out).write_text(json.dumps(res))
    print("=== SENTINEL e82 seeded")


if __name__ == "__main__":
    main()
