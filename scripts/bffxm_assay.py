"""E-85 groundwork (D-078, D-079): races and controls for BFF-XM (scripts/bffxm.py).

* `start` / `compete`   a race: designed programs (bffxm.DESIGNED) at given byte shares in random code cut by the
                        rule, in a random order, the same start for every arm; score = change of
                        ln((focal bytes + 1) / (rival bytes + 1)). Families are counted as EXACT copies (no mutation
                        in races), because the 32-byte R and its sham S differ in only 2 bytes and E-82's 90%
                        family test would merge them.
* `invade`              the net control: a soup of plain hosts H and parasites P is aged under the rule, then a
                        share of the H programs is turned into R in place (same length, scattered); score = change
                        of ln(R / H) and R's byte growth after the switch.
* `controls`            rule, designed-program and instrument controls (pytest `test_bffxm_controls`, probes).
"""
from __future__ import annotations

import time
from collections import Counter

import numpy as np

import bffxm as M

X, A, R_, RA = M.X, M.A, M.R, M.RA


def exact_bytes(s, x) -> int:
    x = X.u8(x)
    return int(s.lens[X.members(s.buf, s.lens, x, thr=100, opmin=100) & (s.lens == len(x))].sum())


def start(seed: int, shares: dict, w: int = X.W, tag: int = 1) -> list[np.ndarray]:
    rng = np.random.default_rng([85, tag, seed])
    progs = []
    for name, sh in shares.items():
        x = M.DESIGNED[name]()
        progs += [x.copy() for _ in range(int(sh * w / len(x)))]
    progs += A.background(rng, w - sum(map(len, progs)))
    return [progs[i] for i in rng.permutation(len(progs))]


def soup(progs, seed: int, geometry: str, libmode: str, mutation: float = 0.0, tag: int = 2):
    rng = np.random.default_rng([85, tag, seed])
    return R_.from_programs(progs, geometry, rng=rng, libmode=libmode, mutation=mutation)


def compete(seed: int, geometry: str, libmode: str, shares: dict, focal: str = "R", rival: str = "S",
            horizons=(10, 25, 50, 100), every: int = 5, w: int = X.W, mutation: float = 0.0) -> dict:
    s = soup(start(seed, shares, w), seed, geometry, libmode, mutation)
    names = list(shares)
    progs = {k: M.DESIGNED[k]() for k in names}
    traj, t0 = [], time.time()
    for e in range(max(horizons) + 1):
        if e % every == 0 or e in horizons:
            traj.append({"epoch": e, **{k: exact_bytes(s, progs[k]) for k in names}, "n": s.n,
                         "steps_pair": round(s.last_steps / max(1, s.n // 2), 1)})
        if e < max(horizons):
            s.epoch()
    by = {t["epoch"]: t for t in traj}
    a = by[0]
    if rival is None:                         # growth of the focal family alone
        sc = {h: round(float(np.log((by[h][focal] + 1) / (a[focal] + 1))), 4) for h in horizons}
    else:
        sc = {h: round(float(np.log((by[h][focal] + 1) / (by[h][rival] + 1))
                             - np.log((a[focal] + 1) / (a[rival] + 1))), 4) for h in horizons}
    return {"seed": seed, "geometry": geometry, "libmode": libmode, "focal": focal, "rival": rival, "shares": shares,
            "scores": sc, "traj": traj, "sec": round(time.time() - t0, 1)}


def invade(seed: int, geometry: str = "deme64", age: int = 100, share_r: float = 0.05, horizons=(25, 50, 100, 200),
           h_share: float = 0.20, p_share: float = 0.05, libmode: str = "neighbour", every: int = 5,
           w: int = X.W) -> dict:
    """Age an H + P soup for `age` epochs (no mutation), then turn a random `share_r` of the exact H programs into R
    (rng [85, 5, seed]); follow R, H and P bytes."""
    s = soup(start(seed, {"H": h_share, "P": p_share}, w, tag=3), seed, geometry, libmode, tag=4)
    H, Rh, P = M.host(), M.resistant_host(), M.parasite(4)
    for _ in range(age):
        s.epoch()
    progs = s.programs()
    isH = np.flatnonzero(X.members(s.buf, s.lens, H, thr=100, opmin=100) & (s.lens == len(H)))
    rng = np.random.default_rng([85, 5, seed])
    pick = rng.choice(isH, max(1, int(share_r * len(isH))), replace=False) if len(isH) else []
    for i in pick:
        progs[i] = Rh.copy()
    s.buf = X.u8(np.concatenate(progs))
    traj = []
    t0 = time.time()
    for e in range(max(horizons) + 1):
        if e % every == 0 or e in horizons:
            traj.append({"epoch": e, "R": exact_bytes(s, Rh), "H": exact_bytes(s, H), "P": exact_bytes(s, P)})
        if e < max(horizons):
            s.epoch()
    by = {t["epoch"]: t for t in traj}
    a = by[0]
    sc = {h: round(float(np.log((by[h]["R"] + 1) / (by[h]["H"] + 1)) - np.log((a["R"] + 1) / (a["H"] + 1))), 4)
          for h in horizons}
    gr = {h: round(float(np.log((by[h]["R"] + 1) / (a["R"] + 1))), 4) for h in horizons}
    return {"seed": seed, "geometry": geometry, "libmode": libmode, "age": age, "H_at_switch": int(len(isH)),
            "R_switched": int(len(pick)), "score_R_vs_H": sc, "R_growth": gr, "traj": traj,
            "sec": round(time.time() - t0, 1)}


# ---- controls (pytest `test_bffxm_controls`, `emergence benchmark --probes`) ----------------------------
def controls() -> list[tuple[str, bool, str]]:
    import bffx as B
    out = []
    rng = np.random.default_rng(85)
    # the rule: xmin 0 equals BFF-X bit for bit; with xmin 32 bytes are conserved and pieces stay in range
    M.set_xmin(0)
    try:
        a = B.Soup(w=2 ** 16, seed=7, libmode="neighbour")
        b = X.Soup(w=2 ** 16, seed=7, libmode="neighbour")
        for _ in range(30):
            a.epoch()
            b.epoch()
        same = bool(len(a.buf) == len(b.buf) and (a.buf == b.buf).all() and (a.lens == b.lens).all())
    finally:
        M.set_xmin(M.XMIN)
    out.append(("bffxm rule: with xmin = 0 the interpreter equals BFF-X (bffx.Soup, neighbour) bit for bit over 30 "
                "epochs", same, f"identical {same}"))
    s = M.make("deme64", w=2 ** 16, rng=np.random.default_rng(8))
    ok, lo, hi = True, 999, 0
    for _ in range(40):
        s.epoch()
        ok &= int(s.lens.sum()) == 2 ** 16 == len(s.buf)
        lo, hi = min(lo, int(s.lens.min())), max(hi, int(s.lens.max()))
    out.append(("bffxm rule (deme64): bytes conserved, pieces within [LMIN, LMAX], xmin = 32",
                ok and lo >= 4 and hi <= 128 and M.get_xmin() == 32, f"conserved {ok}, lengths {lo}..{hi}"))
    # minimum body: the 6-byte copier no longer copies itself; padded to 31 bytes neither; at 32 it does
    ex = {L: X.screen(X.hand_copier(L), 3, 8, libmode="none", thr=100, opmin=100)[0] for L in (6, 31, 32, 64)}
    out.append(("bffxm minimum body: the copy loop [.>}] copies itself exactly at 32 and 64 bytes, never at 6 or 31 "
                "(nothing borrowed)", ex[32] == 8 and ex[64] == 8 and ex[6] == 0 and ex[31] == 0, f"{ex}"))
    # a short program borrows: a 4-byte inert program is copied by a host library, not without one; the library is
    # read only; a short copy loop is itself copied by a host (it has no code of its own)
    H, P, Rh, S = M.host(), M.parasite(4), M.resistant_host(), M.sham_host()
    before = H.copy()
    pcs, _ = X.run_pair(P, rng.integers(0, 256, 100, dtype=np.uint8), H)
    n_p = sum(len(q) == 4 and bool((q == P).all()) for q in pcs)
    pcs0, _ = X.run_pair(P, rng.integers(0, 256, 100, dtype=np.uint8), None, libmode="none")
    n0 = sum(len(q) == 4 and bool((q == P).all()) for q in pcs0)
    h6 = X.hand_copier(6)
    q6 = A.q_pair(h6, H, 4)
    out.append(("bffxm borrowing: a 4-byte inert program leaves >= 20 copies with a host as library (library "
                "unchanged), only itself with nothing to borrow; the 6-byte copy loop is itself a borrower (q ~ 1)",
                n_p >= 20 and n0 == 1 and bool((H == before).all()) and q6 > 0.9,
                f"copies {n_p}, alone {n0}, q(H6 on H) {q6:.3f}"))
    # designed programs: H, R, S copy themselves exactly; R refuses the plain parasite, copies the key-matched one
    exact = {k: X.screen(x, 9, 8, libmode="none", thr=100, opmin=100)[0] for k, x in (("H", H), ("R", Rh), ("S", S))}
    q = {k: round(A.q_pair(P, x, 10), 3) for k, x in (("H", H), ("R", Rh), ("S", S))}
    qk = round(A.q_pair(M.parasite(4, 1), Rh, 11), 3)
    out.append(("bffxm designed (32 bytes each): H, R, S copy themselves exactly; P is refused by R (q 0) and copied "
                "by H and S (q ~ 1); the key-matched parasite is copied by R",
                all(v == 8 for v in exact.values()) and q["R"] == 0 and q["H"] > 0.9 and q["S"] > 0.9 and qk > 0.9,
                f"exact {exact}, q {q}, key {qk}"))
    return out


def instrument_controls() -> list[tuple[str, bool, str]]:
    """E-82/E-83 instruments re-validated under BFF-XM (hosts are 32-byte programs here)."""
    out = []
    rng = np.random.default_rng(851)
    H, P, Rh = M.host(), M.parasite(4), M.resistant_host()
    # host detector: copy screen + growth test, nothing borrowed
    v = {L: A.replication_test(M.host(L), rng)["verdict"] for L in (32, 40, 48)}
    out.append(("bffxm hosts positive: hand hosts of 32, 40 and 48 bytes -> replicator (nothing borrowed)",
                all(x == "replicator" for x in v.values()), f"{v}"))
    v = {"random": A.replication_test(rng.integers(0, 256, 40, dtype=np.uint8), rng)["verdict"],
         "parasite": A.replication_test(P, rng)["verdict"],
         "6-byte copy loop": A.replication_test(X.hand_copier(6), rng)["verdict"],
         "31-byte copier": A.replication_test(X.hand_copier(31), rng)["verdict"],
         "dead host": A.replication_test(_dead(H), rng)["verdict"]}
    out.append(("bffxm hosts negative/deceptive: random program, parasite, the 6-byte copy loop and a 31-byte padded "
                "copier (below the minimum body: they copy only when borrowing), dead host -> no replication",
                all(x == "no replication" for x in v.values()), f"{v}"))
    copier = {k: X.is_copier(x, 5, libmode="none") for k, x in (("H", H), ("R", Rh), ("H6", X.hand_copier(6)),
                                                                  ("P", P))}
    out.append(("bffxm copy screen (host census): H and R pass, the 6-byte copy loop and P fail",
                copier["H"] and copier["R"] and not copier["H6"] and not copier["P"], f"{copier}"))

    def pt(x, pool, seed):
        return A.parasite_test(x, pool, np.random.default_rng(seed), "neighbour", m=128, m_prod=1024)

    r = pt(P, A.host_pool(rng, guest=P, h=H), 1)
    out.append(("bffxm parasites positive: 4-byte parasite at 5% among 50% 32-byte hosts -> parasite",
                r["verdict"] == "parasite", A._pb(r)))
    r1 = pt(rng.integers(0, 256, 40, dtype=np.uint8), A.host_pool(rng, h=H), 2)
    r2 = pt(H, A.host_pool(rng, h=H), 3)
    out.append(("bffxm parasites negative: a random program -> not parasite; the host -> self-copier",
                r1["verdict"] != "parasite" and r2["verdict"] == "self-copier", f"{r1['verdict']}; {r2['verdict']}"))
    dh = _dead(H)
    r1 = pt(dh, A.host_pool(rng, h=H, junk=dh, junk_share=0.2), 4)
    pool, z = A.byproduct_pool(rng)
    pool = [H.copy() if len(p) == 12 and p[0] == ord("[") else p for p in pool]
    r2 = pt(z, pool, 6)
    out.append(("bffxm parasites deceptive: a common dead host (host copies look like it; it falls through, so it is "
                "copied too, but only by hosts copying themselves) -> not parasite; product Z made by makers -> "
                "by-product", r1["verdict"] != "parasite" and r2["verdict"] == "by-product",
                f"dead host: {A._pb(r1)}; Z: {A._pb(r2)}"))
    r = pt(P, A.host_pool(rng, guest=P, h=Rh), 7)
    r1 = pt(M.parasite(4, 1), A.host_pool(rng, guest=M.parasite(4, 1), h=Rh), 8)
    out.append(("bffxm parasites specificity: plain parasite among resistant hosts -> not copied; key-matched -> "
                "parasite", r["verdict"] == "not copied" and r1["verdict"] == "parasite",
                f"{r['verdict']}; {r1['verdict']}"))
    s = M.make("deme64", w=2 ** 17, rng=np.random.default_rng(34))
    for _ in range(50):
        s.epoch()
    pool = s.programs()
    v = [pt(x, pool, 200 + i)["verdict"] for i, (x, _) in enumerate(A.soup_top(s, 20))]
    out.append(("bffxm parasites selection-aware null: top 20 programs of a deme64 soup at epoch 50 (no hosts) -> 0 "
                "parasites", "parasite" not in v, f"{Counter(v)}"))
    # time-shift statistics with 32-byte hosts
    r = A.timeshift([([P], [H]), ([M.parasite(4, 1)], [Rh])], 11)
    out.append(("bffxm time-shift positive: designed arms race -> RQ ~ 1", r["RQ"] > 0.8, f"RQ {r['RQ']}"))
    r = A.timeshift([([P], [H] * 5), ([P], [H] * 4 + [Rh])], 12)
    out.append(("bffxm time-shift graded: 1 of 5 later hosts resistant -> RQ = 0.2", abs(r["RQ"] - 0.2) < 0.03,
                f"RQ {r['RQ']}"))
    r = A.timeshift([([M.parasite(4)], [M.host(32)]), ([M.parasite(8)], [M.host(40)])], 13)
    out.append(("bffxm time-shift negative: later parasites and hosts that changed length without resistance -> |RQ| "
                "< 0.05", abs(r["RQ"]) < 0.05, f"RQ {r['RQ']}"))
    r = A.timeshift([([M.parasite(4, 1)], [Rh]), ([P], [H])], 14)
    out.append(("bffxm time-shift null: positive history with time labels reversed -> RQ ~ -1", r["RQ"] < -0.8,
                f"RQ {r['RQ']}"))
    W = _rewriting()
    ex = X.screen(W, 12, 8, libmode="none", thr=100, opmin=100)[0] == 8
    q2 = A.timeshift([([P], [H]), ([P], [W])], 23)["RQ"]
    w2 = RA.timeshift_w([([P], [H]), ([P], [W])], 24)["RQ_w"]
    w1 = RA.timeshift_w([([P], [H]), ([M.parasite(4, 1)], [Rh])], 22)["RQ_w"]
    out.append(("bffxm time-shift deceptive: a later host that rewrites callers' first byte (exact self-copier) fools "
                "coverage (RQ > 0.5) but not protection (|RQ_w| < 0.05); the designed race gives RQ_w > 0.5",
                ex and q2 > 0.5 and abs(w2) < 0.05 and w1 > 0.5, f"exact {ex}, RQ {q2}, RQ_w {w2}, race RQ_w {w1}"))
    return out


def _dead(H) -> np.ndarray:
    d = H.copy()
    d[0] = ord("]")
    return d


def _rewriting(key: int = 1) -> np.ndarray:
    return X.pad(bytes([key]) + b"[-]" + b"+" * key + b"[.>}]", M.XMIN)


if __name__ == "__main__":
    import json
    import sys
    t0 = time.time()
    res = controls() + (instrument_controls() if "--all" in sys.argv else [])
    for name, ok, det in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {det}", flush=True)
    print(json.dumps({"passed": int(sum(o for _, o, _ in res)), "total": len(res), "sec": round(time.time() - t0)}))
