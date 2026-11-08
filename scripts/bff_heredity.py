"""E-42: is variation heritable in emergent BFF replicators? (docs/data/e42-preregistration.md)

Runs the program heredity test (observatory/program_heredity.py, D-041) on every distinct
program judged "replicator" in E-41's scans.

    python scripts/bff_heredity.py --workers 9 --out docs/data/experiments/2026-11-08-e42-bff-heredity.json
"""
from __future__ import annotations

import argparse
import json
from multiprocessing import Pool

import numpy as np

from emergence.observatory import program_heredity as PH

E41 = "docs/data/experiments/2026-11-08-e41-bff-longer.json"


def candidates() -> list[dict]:
    seen: dict[str, dict] = {}
    for r in json.load(open(E41))["soups"]:
        for ep, sc in r["scans"].items():
            for x in sc["results"]:
                if x["verdict"] == "replicator" and x["program"] not in seen:
                    seen[x["program"]] = {"program": x["program"], "soup": r["seed"], "epoch": int(ep), "count": x["count"]}
    return list(seen.values())


def job(arg):
    i, c = arg
    x = np.frombuffer(bytes.fromhex(c["program"]), np.uint8).copy()
    r = PH.heredity_test(x, np.random.default_rng(42 + i), mutants=24)
    print(json.dumps({"i": i, "soup": c["soup"], "verdict": r["verdict"], "viable": r["viable"],
                      "inherited": r["inherited"], "p": r["p"]}), flush=True)
    return c | r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=9)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cs = candidates()
    with Pool(a.workers) as p:
        res = p.map(job, list(enumerate(cs)), chunksize=1)
    from collections import Counter
    summary = {"candidates": len(res), "verdicts": dict(Counter(r["verdict"] for r in res))}
    json.dump({"experiment": "E-42", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary))
    print("=== E42 DONE", flush=True)


if __name__ == "__main__":
    main()
