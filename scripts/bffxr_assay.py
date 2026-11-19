"""E-83 groundwork (J-101, D-075): instruments for BFF-XR (scripts/bffxr.py). The host and parasite detectors and the
time-shift statistic are E-82's (`bffx_assay`, D-073) and are geometry-free (they test programs, not soups); this
module adds what the new geometry needs.

* designed programs   `bffx_assay.host` / `resistant_host` / `parasite` (E-82) plus
                        `sham_host`   R with its trap '[]' replaced by two no-op bytes: the same length and the same
                                      bytes elsewhere, so the same cost, but it copies every caller (R's equal-cost
                                      rival: a race R against S measures what refusing callers is worth, nothing else);
* `compete`           a race in a soup: designed programs at given byte shares in random code, all in a random order
                      (scattered, no clusters at the start); the same start (same bytes and order) for every arm; no
                      mutation. Score = change of ln((focal family bytes + 1) / (rival family bytes + 1)) from epoch 0
                      to each horizon. Arms: geometry ring / mixed (E-82's bffx.Soup) / ring-global; libmode neighbour
                      or none (nothing can be borrowed, so R and S behave identically: a built-in null).
* `controls`          rule and geometry controls (pytest `test_bffxr_controls`, probe benchmark).
"""
from __future__ import annotations

import time

import numpy as np

import bffx as X
import bffx_assay as A
import bffxr as R_


def rewriting_host(key: int = 1, length: int = 12) -> np.ndarray:
    """Deceptive for coverage: copies every caller, but first sets the caller's first byte to `key` ('-' then '[-]'
    clears it, '+' x key sets it), so a plain parasite's copies are no longer copies of it (q = 0) although the
    partner is overwritten just the same (no protection). Run by itself, its first byte is `key`, so it copies itself
    exactly."""
    code = bytes([key]) + b"[-]" + b"+" * key + b"[.>}]"
    return X.pad(code, length)


def sham_host(key: int = 1, length: int = 11) -> np.ndarray:
    """R (`bffx_assay.resistant_host(key, length)`) with the trap '[]' replaced by two no-op filler bytes."""
    r = A.resistant_host(key, length).copy()
    i = 1 + key
    assert bytes(r[i:i + 2]) == b"[]"
    r[i:i + 2] = 0x80
    return r


DESIGNED = {"H": lambda: X.hand_copier(6), "R": lambda: A.resistant_host(1, 11), "S": lambda: sham_host(1, 11),
            "P": lambda: A.parasite(4), "Pk": lambda: A.parasite(4, key=1)}


def start(seed: int, shares: dict, w: int = X.W) -> list[np.ndarray]:
    """Designed programs at the given byte shares, the rest random code cut by the rule, in a random order."""
    rng = np.random.default_rng([83, 1, seed])
    progs = []
    for name, sh in shares.items():
        x = DESIGNED[name]()
        progs += [x.copy() for _ in range(int(sh * w / len(x)))]
    progs += A.background(rng, w - sum(map(len, progs)))
    return [progs[i] for i in rng.permutation(len(progs))]


def soup(progs, seed: int, geometry: str, libmode: str, mutation: float = 0.0, radius: int = R_.RADIUS) -> X.Soup:
    rng = np.random.default_rng([83, 2, seed])
    kw = {"radius": radius} if geometry.startswith("ring") else {}
    return R_.from_programs(progs, geometry, rng=rng, libmode=libmode, mutation=mutation, **kw)


def fam_bytes(s: X.Soup, x) -> int:
    return int(s.lens[X.members(s.buf, s.lens, x)].sum())


def compete(seed: int, geometry: str, libmode: str, shares: dict, focal: str = "R", rival: str = "S",
            horizons=(25, 50, 100, 200), every: int = 5, w: int = X.W, radius: int = R_.RADIUS,
            mutation: float = 0.0) -> dict:
    s = soup(start(seed, shares, w), seed, geometry, libmode, mutation, radius)
    names = list(shares)
    progs = {k: DESIGNED[k]() for k in names}
    traj, t0 = [], time.time()
    for e in range(max(horizons) + 1):
        if e % every == 0 or e in horizons:
            traj.append({"epoch": e, **{k: fam_bytes(s, progs[k]) for k in names}})
        if e < max(horizons):
            s.epoch()
    by = {t["epoch"]: t for t in traj}
    a = by[0]
    sc = {h: round(float(np.log((by[h][focal] + 1) / (by[h][rival] + 1)) - np.log((a[focal] + 1) / (a[rival] + 1))), 4)
          for h in horizons}
    return {"seed": seed, "geometry": geometry, "libmode": libmode, "focal": focal, "rival": rival, "scores": sc,
            "traj": traj, "sec": round(time.time() - t0, 1)}


# ---- protection score (secondary of E-83) -----------------------------------------------------------
def w_pair(P, H, seed: int, trials: int = 32, lp: int = 128) -> float:
    """Protection: mean share of a random lp-byte partner left unchanged when P runs first with H as its library."""
    rng = np.random.default_rng(seed)
    P, H = X.u8(P), X.u8(H)
    tot = 0.0
    for _ in range(trials):
        b = rng.integers(0, 256, lp, dtype=np.uint8)
        t = X.u8(np.concatenate([P, b]))
        X.lib().x_run(t.ctypes.data, len(P), lp, H.ctypes.data, len(H), X.STEPS, X.LIBMODES["neighbour"])
        tot += float((t[len(P):] == b).mean())
    return tot / trials


def w_matrix(Ps, Hs, seed: int) -> float:
    if not Ps or not Hs:
        return float("nan")
    return float(np.mean([w_pair(p, h, seed + 97 * i + j) for i, p in enumerate(Ps) for j, h in enumerate(Hs)]))


def timeshift_w(samples, seed: int) -> dict:
    """RQ_w = mean over i < j of w(P_i, H_j) - w(P_j, H_i): later hosts protect their partners from earlier parasites
    more than earlier hosts do from later parasites."""
    k = len(samples)
    W = [[w_matrix(samples[i][0], samples[j][1], seed + 1000 * i + 10 * j) for j in range(k)] for i in range(k)]
    d = [W[i][j] - W[j][i] for i in range(k) for j in range(i + 1, k) if not (np.isnan(W[i][j]) or np.isnan(W[j][i]))]
    return {"W": [[None if np.isnan(v) else round(v, 4) for v in row] for row in W],
            "RQ_w": round(float(np.mean(d)), 4) if d else None}


# ---- controls (pytest `test_bffxr_controls`, `emergence benchmark --probes`) ----------------------------------
def controls() -> list[tuple[str, bool, str]]:
    out = []
    rng = np.random.default_rng(83)
    # the ring pairs neighbours: every pair is two ring-adjacent programs, every program at most once
    s = R_.RingSoup(w=2 ** 14, seed=3)
    perm = s.pairs()
    N = s.n
    pos = np.empty(N, np.int64)
    pos[np.arange(N)] = np.arange(N)
    m = N // 2
    d = np.abs(perm[0:2 * m:2].astype(np.int64) - perm[1:2 * m:2]) % N
    ok = bool(np.all((d == 1) | (d == N - 1))) and len(set(perm.tolist())) == N
    out.append(("bffxr ring: each epoch is a perfect matching of ring neighbours", ok, f"N {N}, pairs {m}"))
    # bytes conserved, lengths in range, and copies stay local
    s = R_.RingSoup(w=2 ** 16, seed=4)
    good, lo, hi = True, 999, 0
    for _ in range(50):
        s.epoch()
        good &= int(s.lens.sum()) == 2 ** 16 == len(s.buf)
        lo, hi = min(lo, int(s.lens.min())), max(hi, int(s.lens.max()))
    out.append(("bffxr ring: bytes conserved, pieces within [LMIN, LMAX]", good and lo >= 4 and hi <= 128,
                f"conserved {good}, lengths {lo}..{hi}"))
    # locality: a block of hosts in the middle of random code spreads outward as a contiguous front (ring), but
    # appears everywhere at once in the well-mixed soup
    H = X.hand_copier(6)
    bg = A.background(rng, 2 ** 16 - 64 * 6)
    mid = len(bg) // 2
    progs = bg[:mid] + [H.copy() for _ in range(64)] + bg[mid:]
    spread = {}
    for geo in ("ring", "mixed"):
        s = R_.from_programs(progs, geo, rng=np.random.default_rng(5), libmode="none", mutation=0.0)
        for _ in range(10):
            s.epoch()
        mem = X.members(s.buf, s.lens, H)
        offs = np.cumsum(s.lens) - s.lens
        p = offs[mem] / len(s.buf)
        # circular spread of host positions: the shortest arc that holds 90% of the host bytes
        ps = np.sort(p)
        k = max(1, int(0.9 * len(ps)))
        arcs = (np.concatenate([ps, ps + 1])[k - 1:k - 1 + len(ps)] - ps) if len(ps) else np.array([1.0])
        spread[geo] = round(float(arcs.min()), 3)
    out.append(("bffxr ring locality: 64 hosts in the middle of random code after 10 epochs (no borrowing): the 90% "
                "arc is short on the ring (< 0.1) and long in the mixed soup (> 0.5)",
                spread["ring"] < 0.1 and spread["mixed"] > 0.5, f"{spread}"))
    # the library is local: with radius 0... radius r: C within r of A. Check on a soup whose programs are all
    # different hosts-or-not markers: a parasite next to hosts is copied; a parasite far from all hosts is not.
    P = A.parasite(4)
    bgn = [A.parasite(8, key=0) for _ in range(2000)]          # inert programs whose first byte is 0: never copied
    progs = bgn[:1000] + [H.copy() for _ in range(4)] + [P.copy()] + [H.copy() for _ in range(4)] + bgn[1000:]
    progs2 = bgn[:1000] + [P.copy()] + bgn[1000:] + [H.copy() for _ in range(8)]
    res = []
    for pr in (progs, progs2):
        cnt = 0
        for k in range(20):
            s = R_.from_programs(pr, "ring", rng=np.random.default_rng(100 + k), libmode="neighbour", mutation=0.0)
            s.epoch()
            cnt += int(X.members(s.buf, s.lens, P).sum()) > 1
        res.append(cnt)
    out.append(("bffxr ring library is local: a parasite among hosts is copied in some epochs; a parasite 1,000 "
                "programs from any host never", res[0] >= 5 and res[1] == 0, f"near {res[0]}/20, far {res[1]}/20"))
    # demes (the E-83 geometry): pairs and libraries stay within a block of K consecutive programs
    s = R_.make("deme64", w=2 ** 16, rng=np.random.default_rng(41))
    for _ in range(5):
        s.epoch()
    N = s.n
    perm = s.pairs()
    m = N // 2
    a, b = perm[0:2 * m:2].astype(np.int64), perm[1:2 * m:2].astype(np.int64)
    d = np.minimum(np.abs(a - b), N - np.abs(a - b))
    far = float(np.mean(d >= 128))
    out.append(("bffxr deme64: each epoch pairs every program once, within its block of 64 (a pair spans two blocks "
                "only after an odd block: < 2% of pairs at distance >= 64)", len(set(perm.tolist())) == N
                and float(np.mean(d >= 64)) < 0.02 and far == 0.0, f"N {N}, share >= 64 apart "
                f"{float(np.mean(d >= 64)):.4f}, >= 128 apart {far}"))
    spread = {}
    bg2 = A.background(np.random.default_rng(42), 2 ** 18)
    mid2 = len(bg2) // 2
    for geo in ("deme64", "mixed"):
        s = R_.from_programs(bg2[:mid2] + [H.copy() for _ in range(64)] + bg2[mid2:], geo,
                             rng=np.random.default_rng(5), libmode="none", mutation=0.0)
        for _ in range(4):
            s.epoch()
        mem = X.members(s.buf, s.lens, H)
        offs = np.cumsum(s.lens) - s.lens
        ps = np.sort(offs[mem] / len(s.buf))
        k = max(1, int(0.9 * len(ps)))
        spread[geo] = round(float((np.concatenate([ps, ps + 1])[k - 1:k - 1 + len(ps)] - ps).min()), 3)
    out.append(("bffxr deme64 locality: 64 hosts in 2^18 bytes of random code after 4 epochs (no borrowing): 90% arc "
                "< 0.3 under deme64, > 0.5 well mixed", spread["deme64"] < 0.3 and spread["mixed"] > 0.5, f"{spread}"))
    res = []
    for pr in (progs, progs2):
        cnt = 0
        for k in range(20):
            s = R_.from_programs(pr, "deme64", rng=np.random.default_rng(300 + k), libmode="neighbour", mutation=0.0)
            s.epoch()
            cnt += int(X.members(s.buf, s.lens, P).sum()) > 1
        res.append(cnt)
    out.append(("bffxr deme64 library is local: a parasite among hosts is copied in some epochs; a parasite 1,000 "
                "programs from any host never", res[0] >= 3 and res[1] == 0, f"near {res[0]}/20, far {res[1]}/20"))
    # the designed programs
    R, S = A.resistant_host(1, 11), sham_host(1, 11)
    ok = [X.screen(x, 9, 8, libmode="none", thr=100, opmin=100)[0] == 8 for x in (R, S, H)]
    q = {k: round(A.q_pair(P, x, 10, 32), 3) for k, x in (("R", R), ("S", S), ("H", H))}
    qk = round(A.q_pair(A.parasite(4, key=1), R, 11, 32), 3)
    out.append(("bffxr designed: R, S and H copy themselves exactly; the plain parasite is refused by R (q 0) and "
                "copied by S and H (q ~ 1); the key-matched parasite is copied by R",
                all(ok) and q["R"] == 0 and q["S"] > 0.9 and q["H"] > 0.9 and qk > 0.9, f"exact {ok}, q {q}, key {qk}"))
    # time-shift statistics in the ring's own terms: coverage (q, primary) and protection (w, secondary)
    hist = [([P], [H]), ([A.parasite(4, key=1)], [R])]
    q1 = A.timeshift(hist, 21)["RQ"]
    w1 = timeshift_w(hist, 22)["RQ_w"]
    W = rewriting_host()
    exact = X.screen(W, 12, 8, libmode="none", thr=100, opmin=100)[0] == 8
    hist2 = [([P], [H]), ([P], [W])]
    q2 = A.timeshift(hist2, 23)["RQ"]
    w2 = timeshift_w(hist2, 24)["RQ_w"]
    w3 = timeshift_w(hist[::-1], 25)["RQ_w"]
    out.append(("bffxr time-shift: designed arms race -> RQ ~ 1 and RQ_w > 0.5 (refusal protects the partner); "
                "reversed labels -> RQ_w < -0.5",
                q1 > 0.8 and w1 > 0.5 and w3 < -0.5, f"RQ {q1}, RQ_w {w1}, reversed RQ_w {w3}"))
    out.append(("bffxr time-shift deceptive: a later host that copies callers with their first byte rewritten "
                "(exact self-copier) -> coverage RQ is fooled (> 0.5), protection RQ_w is not (|RQ_w| < 0.05)",
                exact and q2 > 0.5 and abs(w2) < 0.05, f"exact {exact}, RQ {q2}, RQ_w {w2}"))
    # parasite detector on ring soups: positive (designed parasite among designed hosts, aged on the ring) and the
    # selection-aware null (the 20 commonest programs of a random-code ring soup at epoch 50, before any host)
    progs = [H.copy() for _ in range(3000)] + [P.copy() for _ in range(600)] + A.background(rng, 2 ** 15)
    progs = [progs[i] for i in rng.permutation(len(progs))]
    s = R_.from_programs(progs, "ring", rng=np.random.default_rng(31), mutation=0.0)
    for _ in range(5):
        s.epoch()
    pool = s.programs()
    pool = [pool[i] for i in np.random.default_rng(32).choice(len(pool), min(4096, len(pool)), replace=False)]
    r = A.parasite_test(P, pool, np.random.default_rng(33), m=128, m_prod=1024)
    out.append(("bffxr parasites positive (ring): designed parasite among designed hosts after 5 ring epochs -> "
                "parasite", r["verdict"] == "parasite", A._pb(r)))
    s = R_.RingSoup(w=2 ** 17, rng=np.random.default_rng(34))
    for _ in range(50):
        s.epoch()
    pool = s.programs()
    v = [A.parasite_test(x, pool, np.random.default_rng(200 + i), m=128, m_prod=1024)["verdict"]
         for i, (x, _) in enumerate(A.soup_top(s, 20))]
    from collections import Counter
    out.append(("bffxr parasites selection-aware null (ring): top 20 programs of a ring soup at epoch 50 -> 0 "
                "parasites", "parasite" not in v, f"{Counter(v)}"))
    return out


if __name__ == "__main__":
    import json
    t0 = time.time()
    res = controls()
    for name, ok, det in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {det}", flush=True)
    print(json.dumps({"passed": int(sum(o for _, o, _ in res)), "total": len(res), "sec": round(time.time() - t0)}))
