"""E-66 post hoc re-scoring (J-068): part B's 5 candidates with the revised parasite test (self-copy check
added after inspection showed the two "parasites" copy themselves into partners whose code never runs).

    python scripts/e66_rescore.py
"""
import json

import numpy as np

from emergence.observatory import program_parasites as PP

D = json.load(open("docs/data/experiments/2026-11-09-e66-parasites.json"))
out = []
for r in D["partB"]:
    P = np.load(f"runs/e54/{r['soup']}-{r['epoch']}.npy")
    x = np.frombuffer(bytes.fromhex(r["program"]), np.uint8).copy()
    n = PP.parasite_test(x, P, np.random.default_rng([661, r["soup"], r["epoch"], r["rank"]]), alone="no replication")
    n.pop("hosts")
    out.append({"soup": r["soup"], "epoch": r["epoch"], "rank": r["rank"], "first_version": r["verdict"], **n})
    print(out[-1]["soup"], out[-1]["epoch"], r["verdict"], "->", n["verdict"], "self", n["self_rate"], "q", n["q"])
json.dump({"experiment": "E-66 rescore (post hoc)", "rows": out}, open("docs/data/experiments/2026-11-09-e66-rescore.json", "w"), indent=1)
