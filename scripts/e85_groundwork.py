"""E-85 groundwork (J-104, D-078, D-079): decisive controls, in order, for BFF-XM (scripts/bffxm.py), and the
emergence pilot. Pilot seeds only (races 1-4; emergence 9851-9862). Results are cached as JSON lines in runs/e85/.

  (0) a hand host replicates: H (32 bytes) at 2% of the bytes in random code grows (deme64, borrowing on and off);
      copiers arise from random code in feasible time: `--pilot` (below);
  (1) parasite advantage: P (4 bytes) against H with hosts common (H 30%, P 2%), borrowing on: ln(P/H) rises;
      without hosts (P 2% alone) P does not grow; with nothing to borrow ln(P/H) falls;
  (2) lock cost: R against H, 10% each, no parasites (nothing borrowed; and borrowing on with no designed parasites);
  (3) kin benefit: R against its sham S with P 5%, A = ln(R/S) change with borrowing minus without, deme64 and mixed;
  (4) net: an H + P soup aged 100 epochs, then 5% of its H turned into R in place: ln(R/H) and R's growth.

    PYTHONPATH=.:scripts python scripts/e85_groundwork.py --controls --workers 11
    PYTHONPATH=.:scripts python scripts/e85_groundwork.py --pilot 9851-9856 --workers 6 --epochs 6000
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
import bffxm as M  # noqa: E402
import bffxm_assay as MA  # noqa: E402

OUT = Path("runs/e85")
REVISED = True        # D-080 rule (tail merge at 32, non-rewriting R); the J-104 runs used runs/e85/ with D-078
SEEDS = (1, 2, 3, 4)
HZ = (10, 25, 50, 100)


def jobs() -> list[tuple]:
    J = []
    for sd in SEEDS:
        for lm in ("neighbour", "none"):
            J.append(("c0_host_growth", sd, "deme64", lm, {"H": 0.02}, "H", None, HZ))
        for geo in ("deme64", "mixed"):
            J.append(("c1_para_vs_host", sd, geo, "neighbour", {"H": 0.30, "P": 0.02}, "P", "H", HZ))
        J.append(("c1_para_vs_host", sd, "deme64", "none", {"H": 0.30, "P": 0.02}, "P", "H", HZ))
        J.append(("c1_para_alone", sd, "deme64", "neighbour", {"P": 0.02}, "P", None, HZ))
        for lm in ("none", "neighbour"):
            J.append(("c2_lock_cost", sd, "deme64", lm, {"R": 0.10, "H": 0.10}, "R", "H", (25, 50, 100, 200)))
        J.append(("c2_lock_cost", sd, "mixed", "none", {"R": 0.10, "H": 0.10}, "R", "H", (25, 50, 100, 200)))
        for geo in ("deme64", "mixed"):
            for lm in ("neighbour", "none"):
                J.append(("c3_kin", sd, geo, lm, {"R": 0.10, "S": 0.10, "P": 0.05}, "R", "S", HZ))
        for geo in ("deme64", "mixed"):
            J.append(("c4_net", sd, geo))
        if REVISED:
            J.append(("c4_net", sd, "deme64", "none"))              # nothing borrowed: R and H identical (null)
            J.append(("c4_clump", sd, "deme64"))
            J.append(("c4_young", sd, "deme64"))
    return J


def run_job(j) -> dict:
    t0 = time.time()
    if j[0].startswith("c4"):
        pl, age = {"c4_net": ("scatter", 10), "c4_clump": ("clump", 10), "c4_young": ("scatter", 3)}[j[0]]
        lm = j[3] if len(j) > 3 else "neighbour"
        r = MA.invade(j[1], j[2], age=age, placement=pl, libmode=lm, horizons=(10, 25, 50, 100, 200))
    else:
        name, sd, geo, lm, sh, f, rv, hz = j
        r = MA.compete(sd, geo, lm, sh, f, rv, horizons=hz)
    r["control"] = j[0]
    r["sec"] = round(time.time() - t0, 1)
    return r


def summarize(rows: list[dict]) -> dict:
    out = {}

    def sc(ctrl, geo, lm, h, key="scores"):
        return [r[key][str(h)] if str(h) in r[key] else r[key][h] for r in rows
                if r["control"] == ctrl and r["geometry"] == geo and r.get("libmode") == lm]

    for ctrl, combos, hs in (("c0_host_growth", [("deme64", "neighbour"), ("deme64", "none")], HZ),
                             ("c1_para_vs_host", [("deme64", "neighbour"), ("mixed", "neighbour"), ("deme64", "none")],
                              HZ),
                             ("c1_para_alone", [("deme64", "neighbour")], HZ),
                             ("c2_lock_cost", [("deme64", "none"), ("deme64", "neighbour"), ("mixed", "none")],
                              (25, 50, 100, 200))):
        for geo, lm in combos:
            for h in hs:
                v = sc(ctrl, geo, lm, h)
                if v:
                    out[f"{ctrl} {geo} {lm} @{h}"] = {"mean": round(float(np.mean(v)), 3),
                                                       "sd": round(float(np.std(v, ddof=1)), 3) if len(v) > 1 else None,
                                                       "values": v}
    for geo in ("deme64", "mixed"):
        for h in HZ:
            a = {r["seed"]: r["scores"][h] for r in rows if r["control"] == "c3_kin" and r["geometry"] == geo
                 and r["libmode"] == "neighbour"}
            b = {r["seed"]: r["scores"][h] for r in rows if r["control"] == "c3_kin" and r["geometry"] == geo
                 and r["libmode"] == "none"}
            d = [round(a[k] - b[k], 4) for k in sorted(a) if k in b]
            if d:
                out[f"c3_kin A {geo} @{h}"] = {"mean": round(float(np.mean(d)), 3),
                                               "sd": round(float(np.std(d, ddof=1)), 3) if len(d) > 1 else None,
                                               "values": d}
        for c in ("c4_net", "c4_clump", "c4_young"):
            for lm in ("neighbour", "none"):
                for h in (10, 25, 50, 100, 200):
                    sel = [r for r in rows if r["control"] == c and r["geometry"] == geo and r.get("libmode") == lm
                           and h in r["score_R_vs_H"]]
                    v = [r["score_R_vs_H"][h] for r in sel]
                    g = [r["R_growth"][h] for r in sel]
                    if v:
                        out[f"{c} {geo} {lm} @{h}"] = {"lnR/H mean": round(float(np.mean(v)), 3), "values": v,
                                                       "lnR growth mean": round(float(np.mean(g)), 3), "growth": g}
    return out


def controls(workers: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "controls.jsonl"
    done = []
    if path.exists():
        done = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    key = lambda r: (r["control"], r["seed"], r["geometry"], r.get("libmode"))  # noqa: E731
    have = {key(r) for r in done}
    todo = [j for j in jobs() if (j[0], j[1], j[2], j[3] if len(j) > 3 and isinstance(j[3], str) else "neighbour")
            not in have]
    with Pool(workers) as p, open(path, "a") as f:
        for r in p.imap_unordered(run_job, todo):
            f.write(json.dumps(r) + "\n")
            f.flush()
            done.append(r)
            print(r["control"], r["seed"], r["geometry"], r.get("libmode"), r.get("scores") or r.get("score_R_vs_H"),
                  r["sec"], flush=True)
    rows = [json.loads(json.dumps(r)) for r in done]
    for r in rows:
        for k in ("scores", "score_R_vs_H", "R_growth"):
            if k in r:
                r[k] = {int(h): v for h, v in r[k].items()}
    summ = summarize(rows)
    (OUT / "controls-summary.json").write_text(json.dumps(summ, indent=1))
    for k, v in summ.items():
        print(k, {a: b for a, b in v.items() if a not in ("values", "growth")}, v.get("values"))


# ---- emergence pilot -----------------------------------------------------------------------------
def pilot_job(arg) -> dict:
    seed, geometry, libmode, epochs, every, xmin = arg
    tag = "" if xmin == M.XMIN else f"-x{xmin}"
    path = OUT / "pilot" / f"{seed}-{geometry}-{libmode}{tag}.json"
    if path.exists():
        return json.loads(path.read_text())
    X, A = M.X, M.A
    M.set_xmin(xmin)                      # exploratory sweep only; the E-85 rule is XMIN = 32
    s = M.make(geometry, rng=np.random.default_rng([85, seed]), libmode=libmode)
    traj, t0 = [], time.time()
    P = M.parasite(4)
    while s.epochs <= epochs:
        if s.epochs % every == 0:
            top = X.top_distinct(s, 40)
            hs = [(b, c) for i, (b, c) in enumerate(top) if X.is_copier(np.frombuffer(b, np.uint8), seed * 7 + i,
                                                                         libmode="none")]
            fam = np.zeros(s.n, bool)
            for b, _ in hs[:10]:
                fam |= X.members(s.buf, s.lens, np.frombuffer(b, np.uint8))
            share = float(s.lens[fam].sum() / s.lens.sum())
            # resistance: among the hosts, those that refuse the inert parasite (coverage < 0.5)
            ref = [len(b) for b, _ in hs[:10] if A.q_pair(P, np.frombuffer(b, np.uint8), 5, 8) < 0.5]
            short = int((s.lens < xmin).sum())
            row = {"epoch": s.epochs, "n": s.n, "mean_len": round(float(s.lens.mean()), 2), "short_share_n":
                   round(short / s.n, 3), "nhost": len(hs), "host_share": round(share, 4),
                   "host_lens": [len(b) for b, _ in hs[:10]], "refusing_hosts": ref,
                   "top5": [(b.hex() if len(b) <= 40 else b[:40].hex() + "..", c) for b, c in top[:5]],
                   "steps_pair": round(s.last_steps / max(1, s.n // 2), 1), "sec": round(time.time() - t0)}
            traj.append(row)
            if s.epochs % (every * 10) == 0:
                np.savez_compressed(OUT / "pilot" / f"{seed}-{geometry}-{libmode}{tag}-{s.epochs}.npz", buf=s.buf,
                                    lens=s.lens)
                print(seed, geometry, libmode, xmin, {k: row[k] for k in ("epoch", "n", "mean_len", "nhost", "host_share",
                                                                    "refusing_hosts", "steps_pair", "sec")},
                      flush=True)
        s.epoch()
    res = {"seed": seed, "geometry": geometry, "libmode": libmode, "xmin": xmin, "traj": traj, "sec": round(time.time() - t0)}
    path.write_text(json.dumps(res))
    return res


def export(path: str) -> None:
    """Groundwork export: control summaries, every race and net trajectory end point, the x sweep and pilot
    trajectories (thinned to every 250 epochs)."""
    import glob
    import subprocess

    def jl(f):
        p = OUT / f
        return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []

    rows = jl("controls.jsonl")
    for r in rows:
        r.pop("traj", None) if r["control"] not in ("c2_lock_cost", "c4_net") else None
    net = jl("net.jsonl")
    pil = []
    for f in sorted(glob.glob(str(OUT / "pilot" / "*.json"))):
        r = json.loads(Path(f).read_text())
        tr = r["traj"]
        pil.append({"seed": r["seed"], "geometry": r["geometry"], "libmode": r["libmode"],
                    "xmin": r.get("xmin", M.XMIN), "sec": r["sec"],
                    "checkpoints_with_hosts": [(t["epoch"], t["nhost"], t["host_share"]) for t in tr if t["nhost"]],
                    "max_host_share": max(t["host_share"] for t in tr),
                    "traj": [t for t in tr if t["epoch"] % 250 == 0]})
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    out = {"experiment": "E-85 groundwork", "status": "decisive control (4) failed; not pre-registered",
           "rule": "BFF-XM deme64 (D-078): BFF-XR deme64 in which a program shorter than 32 bytes has no code of its own",
           "commit": commit,
           "controls_summary": json.loads((OUT / "controls-summary.json").read_text()),
           "controls": rows, "net": net, "xsweep": jl("xsweep.jsonl"), "pilot": pil}
    if REVISED and OUT.name == "v2":
        out["status"] = "revised rule (D-080): decisive control (4) failed again; not pre-registered"
        out["rule"] = ("BFF-XM deme64, revised (D-080): XMIN 32, the tape's unterminated tail merged into the preceding "
                       "piece below 32 bytes, non-rewriting resistant host")
        out["alone"] = jl("alone.jsonl")
        p1 = OUT.parent / "net-variants.jsonl"
        out["net_variants_D078"] = ([json.loads(l) for l in p1.read_text().splitlines() if l.strip()]
                                    if p1.exists() else [])
    Path(path).write_text(json.dumps(out, indent=0))
    print("wrote", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--pilot", default=None)
    ap.add_argument("--geometries", default="deme64")
    ap.add_argument("--libmodes", default="neighbour")
    ap.add_argument("--epochs", type=int, default=6000)
    ap.add_argument("--every", type=int, default=50)
    ap.add_argument("--xmin", default=str(M.XMIN), help="comma list; values other than 32 are an exploratory sweep")
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--export", default=None)
    ap.add_argument("--outdir", default="runs/e85/v2")
    a = ap.parse_args()
    global OUT
    OUT = Path(a.outdir)
    if a.export:
        export(a.export)
        return
    if a.controls:
        controls(a.workers)
    if a.pilot:
        (OUT / "pilot").mkdir(parents=True, exist_ok=True)
        lo, hi = map(int, a.pilot.split("-"))
        J = [(sd, g, lm, a.epochs, a.every, int(x)) for x in a.xmin.split(",") for sd in range(lo, hi + 1)
             for g in a.geometries.split(",") for lm in a.libmodes.split(",")]
        with Pool(a.workers) as p:
            for r in p.imap_unordered(pilot_job, J):
                last = r["traj"][-1]
                print("DONE", r["seed"], r["geometry"], r["libmode"], r.get("xmin"), last["epoch"], last["host_share"], r["sec"],
                      flush=True)
    print("=== SENTINEL e85_groundwork", flush=True)


if __name__ == "__main__":
    main()
