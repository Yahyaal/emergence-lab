"""E-84 groundwork (J-103): extra races behind the decisive-control verdict. (1) parasite against plain host, no
resistance anywhere: can a parasite outgrow the host whose code it borrows when every program has 64 bytes? (2) the
R-vs-sham advantage in smaller demes (16, 8 programs)."""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import bffxf_assay as FA  # noqa: E402


def job(a):
    return FA.compete(**a)


if __name__ == "__main__":
    jobs = []
    for sd in (1, 2, 3, 4):
        for geo in ("deme64", "mixed"):
            jobs.append(dict(seed=sd, geometry=geo, libmode="neighbour", shares={"P": 0.1, "H": 0.1}, focal="P",
                             rival="H", horizons=(5, 10, 25, 50)))
        for geo in ("deme16", "deme8"):
            for lm in ("neighbour", "none"):
                jobs.append(dict(seed=sd, geometry=geo, libmode=lm, shares={"R": 0.1, "S": 0.1, "P": 0.05},
                                 focal="R", rival="S", horizons=(10, 25, 50)))
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 2) as p:
        rr = p.map(job, jobs)
    Path("runs/e84/extra.json").write_text(json.dumps(rr))
    for r in rr:
        print(r["seed"], r["geometry"], r["libmode"], r["focal"], "vs", r["rival"], r["scores"],
              [tuple(t.values()) for t in r["traj"] if t["epoch"] in (0, 5, 10, 25, 50)], flush=True)
