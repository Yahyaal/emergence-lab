"""E-85 groundwork (J-105): the untested variants of control (4) under BFF-XM (D-078): rare R as a clump (one deme of 64
programs; or the scattered count as one run) and rare R in a young soup (introduced at epoch 0 or 3). Seeds 1-4.

    PYTHONPATH=.:scripts python scripts/e85_net_variants.py   -> runs/e85/net-variants.jsonl
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bffxm_assay as MA  # noqa: E402


def f(a):
    sd, placement, age = a
    r = MA.invade(sd, "deme64", age=age, placement=placement, horizons=(10, 25, 50, 100, 200))
    r.pop("traj")
    return r


if __name__ == "__main__":
    J = [(sd, pl, age) for sd in (1, 2, 3, 4) for pl, age in (("deme", 0), ("deme", 10), ("clump", 0), ("clump", 10),
                                                                ("scatter", 3))]
    with Pool(11) as p, open("runs/e85/net-variants.jsonl", "w") as fo:
        for r in p.imap_unordered(f, J):
            fo.write(json.dumps(r) + "\n")
            print(r["seed"], r["placement"], r["age"], r["R_switched"], "lnR/H", r["score_R_vs_H"], "R", r["R_growth"],
                  flush=True)
