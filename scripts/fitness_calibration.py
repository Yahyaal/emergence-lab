"""D-044 calibration export: the trap ladder in the halting background (measured r vs ln(1 + p/2)),
and the hand-written + 9 E-42 replicators in both backgrounds.

    python scripts/fitness_calibration.py --out docs/data/experiments/2026-11-08-d044-calibration.json
"""
import argparse
import json

import numpy as np

from emergence.observatory import program_fitness as F
from emergence.programs import bff as B

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()
rng = np.random.default_rng(44)
ladder = []
for k in range(5):
    g = F.growth_rate(F.trapped(k), rng, bg="halting", reps=24)
    ladder.append({"k": k, "p": F.trap_p(k), "theory": F.theory(F.trap_p(k)), "r": g["r"], "se": g["se"]})
    print(ladder[-1], flush=True)
progs = [("hand-written", bytes(B.REPLICATOR).hex())] + [
    (f"{r['soup']}@{r['epoch']}", r["program"])
    for r in json.load(open("docs/data/experiments/2026-11-08-e42-bff-heredity.json"))["results"]]
reps = []
for name, h in progs:
    x = np.frombuffer(bytes.fromhex(h), np.uint8).copy()
    row = {"name": name, "program": h}
    for bg in ("halting", "random"):
        g = F.growth_rate(x, rng, alts=[x[::-1]], bg=bg, reps=24)
        row[bg] = {"r": g["r"], "se": g["se"]}
        row[bg + "_pairs"] = F.pair_stats(x, rng, bg=bg, partners=256, alts=[x[::-1]])
    reps.append(row)
    print(name, row["halting"], row["random"], flush=True)
json.dump({"experiment": "D-044 calibration", "ladder": ladder, "replicators": reps}, open(a.out, "w"), indent=1)
print("=== CAL DONE")
