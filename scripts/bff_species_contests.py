"""E-46: species-corrected contests between emergent BFF replicators (docs/data/e46-preregistration.md).

Every competitor is counted by both of its forms (x and its byte-reverse): all emergent replicators of
E-42 turned out to be mirror replicators.

    python scripts/bff_species_contests.py --workers 11 --out docs/data/experiments/2026-11-08-e46-species-contests.json
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from multiprocessing import Pool

import numpy as np
from scipy.stats import binomtest, fisher_exact

from emergence.observatory import program_selection as PS
from emergence.programs import bff as B

E42 = "docs/data/experiments/2026-11-08-e42-bff-heredity.json"
REPS = 64
SPECIES = [0, 1, 2, 3, 4, 5, 7, 8]          # E-42 indices; #6 is the reverse of #5


def rev(h: str) -> str:
    return bytes(bytes.fromhex(h)[::-1]).hex()


def pairs() -> list[dict]:
    P = [r["program"] for r in json.load(open(E42))["results"]]
    H = bytes(B.REPLICATOR).hex()
    out = [{"kind": "emergent", "i": i, "j": j, "a": P[i], "b": P[j]} for i, j in combinations(SPECIES, 2)]
    out += [{"kind": "handwritten", "i": -1, "j": j, "a": H, "b": P[j]} for j in SPECIES]
    rng = np.random.default_rng(4601)
    out += [{"kind": "null", "i": -1, "j": -2 - t, "a": H, "b": bytes(PS.retail(B.REPLICATOR, rng)).hex()}
            for t in range(24)]
    return out


def job(arg):
    k, p = arg
    h = lambda x: np.frombuffer(bytes.fromhex(x), np.uint8).copy()
    r = PS.compete_families(h(p["a"]), h(p["b"]), np.random.default_rng([46, k]), reps=REPS,
                            a_alt=[h(rev(p["a"]))], b_alt=[h(rev(p["b"]))])
    return {"pair": k} | p | r


def wins(res, sel, side="a"):
    s = [v for r in res if sel(r) for v, c in zip(r["s"], r["counts"]) if sum(c) >= 16 and v != 0]
    w = sum((v < 0) if side == "a" else (v > 0) for v in s)
    return {"wins": w, "n": len(s), "share": round(w / max(len(s), 1), 3),
            "p_greater": float(binomtest(w, len(s), alternative="greater").pvalue) if s else 1.0}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with Pool(a.workers) as pool:
        res = []
        for n, r in enumerate(pool.imap_unordered(job, list(enumerate(pairs()))), 1):
            res.append(r)
            print(f"{n} done", flush=True)
    res.sort(key=lambda r: r["pair"])
    fav = lambda r: r["verdict"] in ("a favoured", "b favoured")
    em, nl = [r for r in res if r["kind"] == "emergent"], [r for r in res if r["kind"] == "null"]
    k1, k2 = sum(map(fav, em)), sum(map(fav, nl))
    # outcome 1: mirror (#5) vs soup-901 species; #5 is b in pairs (i, 5) with i in 0..3
    o1 = wins(res, lambda r: r["kind"] == "emergent" and r["j"] == 5 and r["i"] in (0, 1, 2, 3), side="b")
    summary = {"o1_mirror_vs_901": o1,
               "o2_handwritten_vs_emergent": wins(res, lambda r: r["kind"] == "handwritten", side="a"),
               "o3_emergent_favoured": [k1, len(em)], "o3_null_favoured": [k2, len(nl)],
               "o3_fisher_p": float(fisher_exact([[k1, len(em) - k1], [k2, len(nl) - k2]], alternative="greater")[1]),
               "null_pooled_a": wins(res, lambda r: r["kind"] == "null", side="a"),
               "verdicts": {r["kind"] + f" {r['i']}-{r['j']}": [r["verdict"], r["mean_s"]] for r in res}}
    json.dump({"experiment": "E-46", "summary": summary, "results": res}, open(a.out, "w"), indent=1)
    print(json.dumps(summary, indent=1))
    print("=== E46 DONE", flush=True)


if __name__ == "__main__":
    main()
