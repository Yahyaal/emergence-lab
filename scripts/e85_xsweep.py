"""E-85 groundwork, exploratory (J-104): does a hand host persist under borrowing at other minimum bodies? H(XMIN) at 2%
of the bytes in random code, deme64, borrowing on, no mutation, exact copies counted; XMIN 8, 12, 16, 24; seeds 1-2.
(The E-85 rule is XMIN = 32; these values are a sweep, not the rule.)

    PYTHONPATH=.:scripts python scripts/e85_xsweep.py      -> runs/e85/xsweep.jsonl
"""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bffxm as M  # noqa: E402
import bffxm_assay as MA  # noqa: E402


def setx(x):
    M.set_xmin(x)
    M.DESIGNED.update({"H": lambda: M.host(x), "R": lambda: M.resistant_host(1, x), "S": lambda: M.sham_host(1, x)})


def f(a):
    kind, x, sd = a
    setx(x)
    r = MA.compete(sd, "deme64", "neighbour", {"H": 0.02}, "H", None, horizons=(10, 25, 50, 100, 200))
    return {"kind": kind, "x": x, "seed": sd, "traj_H": [t["H"] for t in r["traj"][::4]], "scores": r["scores"]}


if __name__ == "__main__":
    J = [("c0", x, sd) for x in (8, 12, 16, 24) for sd in (1, 2)]
    with Pool(2) as p, open("runs/e85/xsweep.jsonl", "w") as fo:
        for r in p.imap_unordered(f, J):
            fo.write(json.dumps(r) + "\n")
            print(r, flush=True)
