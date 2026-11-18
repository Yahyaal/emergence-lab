"""E-82 groundwork export (J-099): emergence pilot, seeded pilot, protocol pilot, instrument controls and power, in one
JSON. Exploratory; pilot seeds only.

    PYTHONPATH=.:scripts python scripts/e82_groundwork.py --out docs/data/experiments/2026-11-18-e82-groundwork.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy.stats import norm, t as tdist

import bffx_assay as A
import e82_run as R


def emergence(path="runs/e82/pilot/out.json") -> list:
    out = []
    for r in sorted(json.load(open(path)), key=lambda r: (r["libmode"], r["seed"])):
        tr = r["traj"]
        out.append({"libmode": r["libmode"], "seed": r["seed"],
                    "first_copier": next((t["epoch"] for t in tr if t["ncop"] > 0), None),
                    "first_share_05": next((t["epoch"] for t in tr if t["cop_share"] >= 0.05), None),
                    "first_parasite_candidate": next((t["epoch"] for t in tr if t["npar"] > 0), None),
                    "final": {k: tr[-1][k] for k in ("cop_share", "par_share", "mean_len", "n")},
                    "final_copiers": tr[-1]["copiers"][:5], "final_parasite_candidates": tr[-1]["parasites"][:5],
                    "seconds": r["seconds"]})
    return out


def seeded(path="runs/e82/seeded/out.json") -> list:
    return [{"arm": r["arm"], "seed": r["seed"],
             "traj": [{k: t[k] for k in ("epoch", "n", "mean_len", "host_share", "para_share", "hosts", "paras",
                                         "q_anc_para_on_hosts", "q_cur_para_on_anc_host")} for t in r["traj"]]}
            for r in sorted(json.load(open(path)), key=lambda r: (r["arm"], r["seed"]))]


def power(d: list, delta: float, alphas=(0.05, 0.05 / 49), ns=(10, 20, 40)) -> dict:
    d = np.asarray([x for x in d if x is not None], float)
    sd = float(d.std(ddof=1)) if len(d) > 1 else float("nan")
    out = {"n_pilot": len(d), "mean": round(float(d.mean()), 4) if len(d) else None, "sd": round(sd, 4)}
    for n in ns:
        se = sd / np.sqrt(n) if sd > 0 else 1e-9
        out[f"n{n}"] = {"ci_halfwidth": round(float(tdist.ppf(0.975, n - 1) * se), 4),
                        **{f"power_at_delta_alpha{a:.4g}": round(float(1 - norm.cdf(norm.ppf(1 - a) - delta / se)), 3)
                           for a in alphas}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--protopilot", default="runs/e82/protopilot/out.json")
    a = ap.parse_args()
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    pp = json.load(open(a.protopilot))
    soups = [{k: s.get(k) for k in ("seed", "T", "seconds")} |
             {f"S{k}": {kk: (s.get(f"S{k}") or {}).get(kk) for kk in
                        ("epoch", "hosts", "host_share", "parasites", "para_share", "verdicts", "mean_len", "n")}
              for k in (1, 2, 3)} for s in pp["soups"]]
    ctl = A.controls("neighbour")
    out = {"experiment": "E-82 groundwork", "commit": commit, "exploratory": True,
           "emergence_pilot": emergence(), "seeded_pilot": seeded(),
           "seeded_gate_pilot": {sd: {arm: __import__("e82_seeded").early(arm, sd) for arm in ("HP", "P")}
                                 for sd in range(9621, 9631)},
           "protocol_pilot": {"soups": soups, "scores": pp["scores"], "P1": pp["P1"], "P2": pp["P2"], "P3": pp["P3"],
                              "seconds": pp["seconds"]},
           "controls": [(n, bool(o), d) for n, o, d in ctl],
           "power": {"delta": R.DELTA, "P2_RQ": power([s["RQ"] for s in pp["scores"]], R.DELTA),
                     "P3_d3": power([s["d3"] for s in pp["scores"]], R.DELTA)}}
    Path(a.out).write_text(json.dumps(out, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    print(json.dumps(out["power"], indent=1))
    print(json.dumps(out["seeded_gate_pilot"], indent=1))
    print("controls", sum(o for _, o, _ in out["controls"]), "/", len(out["controls"]))


if __name__ == "__main__":
    main()
