"""E-83 groundwork (J-101, D-074, D-075): does resisting parasites pay a resistant host (or its kin) in BFF-XR?

  --compete   the decisive positive control (`bffxr_assay.compete`): races between designed programs in random code,
              the same start for every arm, no mutation, scored as the change of ln(focal / rival family bytes).
                RS   R 10%, S 10%, P 5%: the resistant host against its equal-length sham (what refusing is worth)
                RSH  R 5%, S 5%, H 20%, P 5%: the same beside the 6-byte host that dominates real soups
                RH   R 5%, H 20%, P 5%: R against the 6-byte host (refusal benefit minus 5 bytes of length cost)
              geometries ring / mixed (E-82's own bffx.Soup) / ring-global; libmode neighbour and none.
  --pilot     emergence pilot (exploratory): random-code soups under the ring rule, census every 50 epochs.

    PYTHONPATH=.:scripts python scripts/e83_groundwork.py --compete RS --seeds 1-6
    PYTHONPATH=.:scripts python scripts/e83_groundwork.py --pilot 9801-9810 --epochs 4000
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
import bffxr as R_  # noqa: E402
import bffxr_assay as RA  # noqa: E402

OUT = Path("runs/e83")
SETS = {"RS": ({"R": 0.10, "S": 0.10, "P": 0.05}, "R", "S"),
        "RSH": ({"R": 0.05, "S": 0.05, "H": 0.20, "P": 0.05}, "R", "S"),
        "RH": ({"R": 0.05, "H": 0.20, "P": 0.05}, "R", "H")}


def _dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def _compete(arg):
    seed, geo, lm, setname, horizons, radius = arg
    shares, f, r = SETS[setname]
    out = RA.compete(seed, geo, lm, shares, f, r, horizons=horizons, radius=radius)
    out["set"] = setname
    return out


def compete_all(setname: str, seeds, geometries, horizons=(25, 50, 100, 200), radius: int = R_.RADIUS,
                workers: int = 11) -> dict:
    jobs = [(sd, g, lm, setname, horizons, radius) for sd in seeds for g in geometries for lm in ("neighbour", "none")]
    with Pool(workers) as p:
        res = p.map(_compete, jobs)
    by = {(r["seed"], r["geometry"], r["libmode"]): r for r in res}
    summ = {}
    for g in geometries:
        summ[g] = {}
        for h in horizons:
            nb = [by[(sd, g, "neighbour")]["scores"][h] for sd in seeds]
            no = [by[(sd, g, "none")]["scores"][h] for sd in seeds]
            adv = [a - b for a, b in zip(nb, no)]
            summ[g][h] = {"neighbour": nb, "none": no, "nb_mean": round(float(np.mean(nb)), 3),
                          "nb_sd": round(float(np.std(nb, ddof=1)), 3), "none_mean": round(float(np.mean(no)), 3),
                          "A_mean": round(float(np.mean(adv)), 3), "A_sd": round(float(np.std(adv, ddof=1)), 3)}
    return {"set": setname, "shares": SETS[setname][0], "summary": summ, "runs": res, "radius": radius}


# ---- the shortest resistant host -----------------------------------------------------------------------------
def search_resistant(max_len: int = 11) -> dict:
    """Exhaustive search, length by length, for an exact self-copier (4 of 4 random partners, every byte copied, nothing
    borrowed) that leaves the partner of four inert parasites untouched when it is their borrowed code. Search space:
    a contiguous copy loop `[.>}]` or `[.}>]`, the marker at the end, and up to max_len - 6 further bytes from
    the 10 instructions, the marker, 0x00, 0x01, 0xff and the filler 0x80, inserted before or after the loop."""
    import itertools
    sym = [ord(c) for c in "<>{}-+.,[]!"] + [0, 1, 255, 0x80]
    paras = [A.parasite(4), np.frombuffer(b"!!!!", np.uint8), np.frombuffer(b"\x80\x80!!", np.uint8),
             np.frombuffer(b"\x02\x80\x80!", np.uint8)]
    rng = np.random.default_rng(1)
    Bs = [rng.integers(0, 256, 100, dtype=np.uint8) for _ in range(4)]

    def refuses(x):
        for p in paras:
            for b in Bs:
                pcs, _ = X.run_pair(p, b, x, libmode="neighbour")
                if not (np.concatenate(pcs)[len(p):] == b).all():
                    return False
        return True

    out = {}
    for L in range(6, max_len + 1):
        hits = []
        for loop in (b"[.>}]", b"[.}>]"):
            for ins in itertools.product(sym, repeat=L - 6):
                for pos in range(L - 5):
                    code = bytes(ins[:pos]) + loop + bytes(ins[pos:]) + b"!"
                    x = np.frombuffer(code, np.uint8)
                    if X.screen(x, 8, 4, libmode="none", thr=100, opmin=100)[0] == 4 and refuses(x):
                        hits.append(code.hex())
        out[L] = hits
        print(L, len(hits), [bytes.fromhex(h) for h in hits[:8]], flush=True)
        if hits:
            break
    return out


# ---- emergence pilot ----------------------------------------------------------------------------------------
def _pilot(arg):
    seed, geo, epochs, radius = arg
    lm = "none" if geo.endswith(":none") else "neighbour"
    geo = geo.split(":")[0]
    s = R_.make(geo, rng=np.random.default_rng([83, seed]), libmode=lm,
                **({"radius": radius} if geo.startswith("ring") else {}))
    traj, t0 = [], time.time()
    R, Pk = A.resistant_host(1, 11), A.parasite(4, key=1)
    while s.epochs <= epochs:
        if s.epochs % 50 == 0:
            top = X.top_distinct(s, 40)
            hs = [(b, c) for i, (b, c) in enumerate(top)
                  if X.is_copier(np.frombuffer(b, np.uint8), seed * 7919 + s.epochs + i, libmode="none")]
            share = 0.0
            if hs:
                fam = np.zeros(s.n, bool)
                for b, _ in hs[:10]:
                    fam |= X.members(s.buf, s.lens, np.frombuffer(b, np.uint8))
                share = float(s.lens[fam].sum() / s.lens.sum())
            rec = {"epoch": s.epochs, "n": s.n, "mean_len": round(float(s.lens.mean()), 2), "nhost": len(hs),
                   "host_share": round(share, 4), "hosts": [(b.hex(), c) for b, c in hs[:5]],
                   "top": [(b.hex(), c) for b, c in top[:8]]}
            if hs and s.epochs % 500 == 0:
                # does any common host refuse a plain 4-byte parasite (resistance in the wild)?
                rec["q_plain"] = [round(A.q_pair(A.parasite(4), np.frombuffer(b, np.uint8), 5, 16), 3) for b, _ in hs[:5]]
                rec["q_inert_bang"] = [round(A.q_pair(np.frombuffer(b"!!!!", np.uint8), np.frombuffer(b, np.uint8), 6, 16), 3)
                                       for b, _ in hs[:5]]
            traj.append(rec)
        if s.epochs == epochs:
            break
        s.epoch()
    np.savez_compressed(OUT / "pilot" / f"{geo}-{lm}-{seed}.npz", buf=s.buf, lens=s.lens)
    return {"seed": seed, "geometry": geo, "libmode": lm, "traj": traj, "sec": round(time.time() - t0)}


def export() -> dict:
    """Groundwork export (exploratory numbers only): races, the resistant-host search, pilots, seeded arm, power."""
    import subprocess

    def load(name):
        f = OUT / name
        return json.loads(f.read_text()) if f.exists() else None

    def race(name):
        r = load(name)
        return None if r is None else {"set": r["set"], "shares": r["shares"], "radius": r.get("radius"),
                                       "summary": r["summary"]}

    def pil(name):
        r = load(name) or []
        out = []
        for x in r:
            t = x["traj"]
            out.append({"geometry": x["geometry"], "libmode": x.get("libmode", "neighbour"), "seed": x["seed"],
                        "first_host": next((z["epoch"] for z in t if z["nhost"]), None),
                        "first_share_05": next((z["epoch"] for z in t if z["host_share"] >= 0.05), None),
                        "final": {k: t[-1][k] for k in ("epoch", "host_share", "mean_len", "n")},
                        "final_hosts": t[-1]["hosts"][:3], "seconds": x["sec"]})
        return out

    seeded = load("seeded/seeded.json") or []
    proto = load("protopilot/out.json")
    return {
        "experiment": "E-83 groundwork", "exploratory": True,
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "first_attempt_cells_2d": "per-cell 2D lattice (128-byte cells, each slot cut separately) rejected: with no "
                                  "merging across slots, length can only fall; a marker-free `[.>}][` took 77% of "
                                  "the bytes with nothing borrowed (runs/e83/attempt-cells/, not committed)",
        "races": {k: race(f"compete-{k}.json") for k in ("RS", "RSH", "RH", "RS-demes", "RH-deme64", "RS-mixed-early",
                                                          "RS-r1", "RH-r1", "RH-r2")},
        "shortest_resistant_host": load("search_resistant.json"),
        "emergence_pilot": {"ring_4000": pil("pilot/pilot.json"), "ring_12000": pil("pilot/pilot12k.json"),
                            "demes_6000": pil("pilot/pilotdeme.json")},
        "seeded": [{k: x[k] for k in ("seed", "geometry", "RQ", "RQ_reversed", "Q", "sec")} |
                   {"traj": x["traj"][::4] + [x["traj"][-1]],
                    "samples": {e: {"hosts": v["hosts"], "parasites": v["parasites"], "host_share": v["host_share"]}
                                for e, v in x["samples"].items()}} for x in seeded],
        "protocol_pilot": None if proto is None else {
            k: proto[k] for k in ("P1", "P2", "P3", "secondary", "seconds", "commit")} | {
            "scores": proto["scores"], "T": {r["seed"]: r.get("T") for r in proto["soups"]},
            "soup_seconds": {r["seed"]: r.get("seconds") for r in proto["soups"]}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--compete", default=None, help="RS, RSH or RH")
    ap.add_argument("--pilot", default=None, help="seed range a-b")
    ap.add_argument("--seeds", default="1-6")
    ap.add_argument("--epochs", type=int, default=4000)
    ap.add_argument("--geometries", default="ring,mixed,ring-global")
    ap.add_argument("--horizons", default="25,50,100,200")
    ap.add_argument("--radius", type=int, default=R_.RADIUS)
    ap.add_argument("--workers", type=int, default=11)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--export", default=None, help="write the groundwork JSON here")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    if a.compete:
        lo, hi = map(int, a.seeds.split("-"))
        r = compete_all(a.compete, list(range(lo, hi + 1)), a.geometries.split(","),
                        tuple(map(int, a.horizons.split(","))), a.radius, a.workers)
        r["sec"] = round(time.time() - t0)
        _dump(OUT / f"compete-{a.tag or a.compete}.json", r)
        for g, v in r["summary"].items():
            for h, x in v.items():
                print(a.compete, g, h, "neighbour", x["nb_mean"], "+-", x["nb_sd"], "none", x["none_mean"], "A", x["A_mean"],
                      "+-", x["A_sd"], x["neighbour"])
    if a.search:
        _dump(OUT / "search_resistant.json", search_resistant())
    if a.export:
        _dump(Path(a.export), export())
    if a.pilot:
        (OUT / "pilot").mkdir(parents=True, exist_ok=True)
        lo, hi = map(int, a.pilot.split("-"))
        jobs = [(sd, g, a.epochs, a.radius) for g in a.geometries.split(",") for sd in range(lo, hi + 1)]
        with Pool(a.workers) as p:
            res = p.map(_pilot, jobs)
        _dump(OUT / "pilot" / f"{a.tag or 'pilot'}.json", res)
        for r in res:
            first = next((t["epoch"] for t in r["traj"] if t["nhost"]), None)
            last = r["traj"][-1]
            big = next((t["epoch"] for t in r["traj"] if t["host_share"] >= 0.05), None)
            print(r["geometry"], r["libmode"], r["seed"], "first share>=0.05", big, "first host", first, "final share", last["host_share"], "mean_len",
                  last["mean_len"], "hosts", [bytes.fromhex(h) for h, _ in last["hosts"][:3]], "q_plain",
                  last.get("q_plain"), r["sec"], "s")


if __name__ == "__main__":
    main()
