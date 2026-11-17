"""E-81 groundwork (J-097): instruments for BFF-VL (scripts/bffvl.py).

* `replication_test`  replicator detector for variable-length code: 8 copies of x among random code (2^15 bytes,
                      cut by the rule), 48 epochs without mutation; generation 1 passes if x's family (programs
                      within +-2 bytes of x's length, >= 90% of x's bytes and >= 75% of its instruction bytes) grows
                      from 8 to >= 64 copies and >= 4x; generation 2 repeats the test from one late family member,
                      still matched to x. The same test on random programs of x's length is the rule-level null
                      ("rule-level duplication" if they grow too). Analogue of D-040 for a byte-budget soup.
* `compete`           head-to-head fitness assay: a and b seeded with equal bytes (~1,024 each) into random code
                      (2^16 bytes), no mutation, E epochs; each program is assigned to the candidate it matches
                      best (family rule above); s = ln((bytes_a + 1) / (bytes_b + 1)) minus the starting log
                      ratio. Replicates with independent backgrounds.
* `census`            the verified replicators among the k most common distinct programs of a soup (copy screen,
                      then `replication_test`), with their lengths.
"""
from __future__ import annotations

import ctypes
from collections import Counter

import numpy as np

import bffvl as V

V.lib().vl_match.restype = None
V.lib().vl_match.argtypes = [V.P, V.P, ctypes.c_int, V.P, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                             V.P]


def match(buf, lens, x, tol=V.TOL, thr=V.THR, opmin=V.OPMIN) -> np.ndarray:
    x = np.ascontiguousarray(x, dtype=np.uint8)
    out = np.zeros(len(lens), np.int32)
    V.lib().vl_match(np.ascontiguousarray(buf).ctypes.data, np.ascontiguousarray(lens, dtype=np.int32).ctypes.data,
                     len(lens), x.ctypes.data, len(x), tol, thr, opmin, out.ctypes.data)
    return out


def assign(soup: V.Soup, cands: list[np.ndarray]) -> np.ndarray:
    """Index of the candidate each program belongs to (best match), -1 for none or for a tie between candidates."""
    M = np.stack([match(soup.buf, soup.lens, c) for c in cands])
    best = M.argmax(0)
    top = M.max(0)
    best[(top < 0) | ((M == top).sum(0) > 1)] = -1
    return best


def background(rng, w: int) -> list[np.ndarray]:
    buf = rng.integers(0, 256, w, dtype=np.uint8)
    return V.split(buf, V.cut(buf))


def seeded_soup(rng, w: int, groups: list[tuple[np.ndarray, int]], mode: str = "bff", bg=None) -> V.Soup:
    """Random code of w bytes plus `count` copies of each program; no mutation."""
    progs = list(bg) if bg is not None else background(rng, w)
    for x, count in groups:
        progs += [np.asarray(x, np.uint8).copy() for _ in range(count)]
    return V.Soup.from_programs(progs, rng=rng, mode=mode, mutation=0.0)


def replication_test(x, rng, mode: str = "bff", k: int = 8, w: int = 2 ** 15, epochs: int = 48, null: bool = True,
                     generation2: bool = True) -> dict:
    x = np.asarray(x, np.uint8)

    def gen(prog):
        s = seeded_soup(rng, w, [(prog, k)], mode)
        start = int((assign(s, [x]) == 0).sum())
        for _ in range(epochs):
            s.epoch()
        fam = assign(s, [x]) == 0
        late = int(fam.sum())
        ok = late >= 64 and late >= 4 * start
        member = None
        if ok:  # generation 2 starts from the commonest exact program of the family (D-040 analogue)
            progs = s.programs()
            member = np.frombuffer(Counter(bytes(progs[i]) for i in np.nonzero(fam)[0]).most_common(1)[0][0],
                                   np.uint8).copy()
        return {"start": start, "late": late, "pass": ok,
                "byte_share": round(float(s.lens[fam].sum() / s.lens.sum()), 4)}, member

    g1, m = gen(x)
    out = {"gen1": g1, "gen2": None}
    if g1["pass"] and generation2:
        out["gen2"], _ = gen(m)
    rep = g1["pass"] and (out["gen2"] or {}).get("pass", not generation2)
    if rep and null:
        r = rng.integers(0, 256, len(x), dtype=np.uint8)
        r[r == V.MARKER] = 0x80
        r[-1] = V.MARKER
        s = seeded_soup(rng, w, [(r, k)], mode)
        st = int((assign(s, [r]) == 0).sum())
        for _ in range(epochs):
            s.epoch()
        lt = int((assign(s, [r]) == 0).sum())
        out["null"] = {"start": st, "late": lt}
        if lt >= 64 and lt >= 4 * st:
            out["verdict"] = "rule-level duplication"
            return out
    out["verdict"] = "replicator" if rep else ("one generation" if g1["pass"] else "no replication")
    return out


def compete(a, b, rng, reps: int = 8, w: int = 2 ** 16, epochs: int = 8, start_bytes: int = 1024,
            mode: str = "bff") -> dict:
    a, b = np.asarray(a, np.uint8), np.asarray(b, np.uint8)
    na, nb = max(1, round(start_bytes / len(a))), max(1, round(start_bytes / len(b)))
    ss, fin = [], []
    for _ in range(reps):
        s = seeded_soup(rng, w, [(a, na), (b, nb)], mode)
        f0 = assign(s, [a, b])
        A0, B0 = s.lens[f0 == 0].sum(), s.lens[f0 == 1].sum()
        for _ in range(epochs):
            s.epoch()
        f = assign(s, [a, b])
        A, B = int(s.lens[f == 0].sum()), int(s.lens[f == 1].sum())
        ss.append(float(np.log((A + 1) / (B + 1)) - np.log((A0 + 1) / (B0 + 1))))
        fin.append((A, B))
    ss = np.array(ss)
    return {"s": round(float(ss.mean()), 3), "sd": round(float(ss.std(ddof=1)), 3) if reps > 1 else None,
            "ss": [round(v, 3) for v in ss], "a_wins": int((ss > 0).sum()), "b_wins": int((ss < 0).sum()),
            "final_bytes": fin, "na": na, "nb": nb}


def census(soup: V.Soup, rng, k: int = 40, screen_seed: int = 1, test: bool = True, max_tests: int = 10) -> list:
    """Verified replicators among the k most common distinct programs: (length, count, hex, verdict)."""
    top = Counter(map(bytes, soup.programs())).most_common(k)
    out = []
    for i, (bts, c) in enumerate(top):
        x = np.frombuffer(bts, np.uint8).copy()
        if not V.is_copier(x, screen_seed * 1000 + i):
            continue
        v = replication_test(x, rng, null=False)["verdict"] if test and len(out) < max_tests else None
        out.append({"len": len(x), "count": c, "hex": bts.hex(), "verdict": v})
    return out


# ---- controls (pytest `test_bffvl_controls`, `emergence benchmark --probes`) -----------------------
def _padded(x: np.ndarray, length: int, rng) -> np.ndarray:
    """x with random no-op bytes inserted before its marker, `length` bytes in all."""
    return np.concatenate([x[:-1], V.NONOP_NZ[rng.integers(0, len(V.NONOP_NZ), length - len(x))],
                           [V.MARKER]]).astype(np.uint8)


def marker_smear(length: int = 16) -> np.ndarray:
    """Deceptive: '!' then [.}] -- head0 stays on the marker byte, so the loop writes markers over the whole partner,
    which is cut into LMIN-byte pieces of '!' (many identical, common programs that copy nothing)."""
    return V.pad(b"![.}]", length)


def filler_smear(length: int = 16, c: int = 0x41) -> np.ndarray:
    """Deceptive (E-73 style): one filler value everywhere and a loop that writes it over the partner."""
    x = np.full(length, c, np.uint8)
    x[1:5] = np.frombuffer(b"[.}]", np.uint8)
    x[-1] = V.MARKER
    return x


def _soup_top(mode: str, epochs: int, seed: int, w: int = 2 ** 17, k: int = 40) -> list[np.ndarray]:
    s = V.Soup(w=w, seed=seed, mode=mode)
    for _ in range(epochs):
        s.epoch()
    return [np.frombuffer(b, np.uint8).copy() for b, _ in Counter(map(bytes, s.programs())).most_common(k)]


def controls() -> list[tuple[str, bool, str]]:
    import bff_kernels as K
    out = []
    rng = np.random.default_rng(81)

    # the rule
    P = rng.integers(0, 256, (512, 64), dtype=np.uint8)
    s = V.Soup(buf=P.reshape(-1), lens=np.full(512, 64, np.int32), marker=-1, lmax=64, mutation=0, seed=3, edge=0)
    perm = np.random.default_rng(3).permutation(512).astype(np.int32)
    Q = P.copy()
    K.lib().epoch_h(Q.ctypes.data, 64, perm.ctypes.data, 256, 8192, 64)
    s.epoch()
    same = bool((s.buf == np.concatenate([Q[perm[i]] for i in range(512)])).all() and (s.lens == 64).all())
    out.append(("bffvl rule: no marker, LMAX 64, wrapping heads == the h = 64 BFF soup (epoch_h) bit for bit", same,
                f"identical {same}"))
    s = V.Soup(w=2 ** 16, seed=4)
    ok, lo, hi = True, 999, 0
    for _ in range(50):
        s.epoch()
        ok &= int(s.lens.sum()) == 2 ** 16 == len(s.buf)
        lo, hi = min(lo, int(s.lens.min())), max(hi, int(s.lens.max()))
    out.append(("bffvl rule: bytes conserved, every piece within [LMIN, LMAX] (50 epochs, random soup)",
                ok and lo >= V.LMIN and hi <= V.LMAX, f"conserved {ok}, lengths {lo}..{hi}"))
    x = V.hand_copier(16)
    pcs = V.run_pair(x, rng.integers(0, 256, 100, dtype=np.uint8))
    nc = sum(bool((p == x).all()) for p in pcs if len(p) == 16)
    out.append(("bffvl rule: heads halt at the tape ends, so the 16-byte hand copier keeps itself and leaves 6 more "
                "copies in a 100-byte partner", bool((pcs[0] == x).all()) and nc == 7, f"exact copies {nc} of 7"))

    # copy screen (census and race samples)
    pos = [V.is_copier(V.hand_copier(L, rng, fill=None), 11 + L) for L in (6, 16, 48, 128)]
    out.append(("bffvl screen positive: hand copiers of 6, 16, 48, 128 bytes", all(pos), f"{pos}"))
    R_ = [rng.integers(0, 256, int(rng.integers(4, 129)), dtype=np.uint8) for _ in range(200)]
    neg = sum(V.is_copier(r, 100 + i) for i, r in enumerate(R_))
    out.append(("bffvl screen negative: 200 random programs (4-128 bytes) and the broken copier",
                neg == 0 and not V.is_copier(V.broken_copier(16), 5), f"random passing {neg}"))
    dec = {"marker smear": V.is_copier(marker_smear(), 6), "filler smear": V.is_copier(filler_smear(), 7),
           "copier under noexec": V.is_copier(V.hand_copier(16), 8, mode="noexec")}
    out.append(("bffvl screen deceptive: marker smear, filler smear, copier where nothing runs",
                not any(dec.values()), f"{dec}"))
    # common programs that are common for reasons other than copying themselves: a noexec soup (300 epochs; only
    # mutation and the cut rule) and a soup in which marker smears cut partners into many identical '!!!!' pieces.
    # (A BFF-VL soup at epoch 50 is not a null: its commonest programs already include real slow copiers, J-097.)
    s = seeded_soup(np.random.default_rng(25), 2 ** 16, [(marker_smear(), 64)])
    for _ in range(20):
        s.epoch()
    smear_top = [np.frombuffer(b, np.uint8).copy() for b, _ in Counter(map(bytes, s.programs())).most_common(40)]
    nulls = [sum(V.is_copier(p, 300 + i) for i, p in enumerate(_soup_top("noexec", 300, 21))),
             sum(V.is_copier(p, 400 + i) for i, p in enumerate(smear_top))]
    out.append(("bffvl screen selection-aware null: top-40 programs of a noexec soup (300 epochs) and of a soup full "
                "of marker-smear products -> 0 copiers", sum(nulls) == 0,
                f"copiers {nulls}; commonest smear-soup program {s.programs()[0][:4].tobytes()!r}, "
                f"x{Counter(map(bytes, s.programs())).most_common(1)[0][1]}"))

    # replicator detector
    v = {L: replication_test(V.hand_copier(L, rng, fill=None), rng)["verdict"] for L in (8, 32)}
    out.append(("bffvl replicators positive: hand copiers of 8 and 32 bytes -> replicator",
                all(x == "replicator" for x in v.values()), f"{v}"))
    v = {"random": replication_test(rng.integers(0, 256, 24, dtype=np.uint8), rng)["verdict"],
         "broken": replication_test(V.broken_copier(16), rng)["verdict"]}
    out.append(("bffvl replicators negative: random program, broken copier -> no replication",
                all(x == "no replication" for x in v.values()), f"{v}"))
    v = {"noexec": replication_test(V.hand_copier(16), rng, mode="noexec")["verdict"],
         "marker smear": replication_test(marker_smear(), rng)["verdict"],
         "smear product '!!!!'": replication_test(np.full(4, V.MARKER, np.uint8), rng)["verdict"]}
    out.append(("bffvl replicators deceptive: copier where nothing runs, marker smear and its common product",
                all(x == "no replication" for x in v.values()), f"{v}"))
    top = _soup_top("bff", 50, 22)[:3]
    v = [replication_test(p, rng)["verdict"] for p in top]
    out.append(("bffvl replicators selection-aware null: 3 commonest programs of a BFF-VL soup at epoch 50",
                "replicator" not in v, f"{v}"))

    # head-to-head assay
    base = V.hand_copier(12, rng, fill=None)
    r = compete(base, _padded(base, 24, rng), rng, reps=8)
    out.append(("bffvl assay positive: 12-byte copier vs the same copier padded to 24 bytes -> shorter ahead in 8/8",
                r["a_wins"] == 8 and r["s"] > 1, f"s {r['s']}, sd {r['sd']}, wins {r['a_wins']}/8"))
    six = V.hand_copier(6)
    seven = V.pad(V.COPIER + b"\x80", 7)
    r = compete(six, seven, rng, reps=16)
    out.append(("assay ladder at the floor: 6- vs 7-byte copier -> 6 ahead in >= 15/16",
                r["a_wins"] >= 15, f"s {r['s']}, sd {r['sd']}, wins {r['a_wins']}/16"))
    neu = base.copy()
    neu[7] = 0x81 if neu[7] != 0x81 else 0x82
    r = compete(base, neu, rng, reps=16)
    z = r["s"] / (r["sd"] / 4)
    out.append(("bffvl assay negative: copier vs a neutral variant (one filler byte) -> no difference (|z| < 3)",
                abs(z) < 3, f"s {r['s']}, sd {r['sd']}, z {z:.2f}"))
    r = compete(V.broken_copier(12, rng, fill=None), _padded(base, 48, rng), rng, reps=8)
    out.append(("bffvl assay deceptive: a short program that cannot copy vs a 48-byte copier -> the long copier ahead",
                r["b_wins"] == 8 and r["s"] < -1, f"s {r['s']}, wins long {r['b_wins']}/8"))
    zs = []
    for i in range(8):
        r = compete(base, neu, np.random.default_rng([81, 5, i]), reps=8)
        zs.append(r["s"] / (r["sd"] / np.sqrt(8)))
    nsig = sum(abs(z) > 2.36 for z in zs)
    out.append(("bffvl assay null: 8 repeat assays of the neutral pair -> at most 2 'different' at p < 0.05",
                nsig <= 2, f"z {[round(z, 2) for z in zs]}"))

    # length-trend nulls
    s = V.Soup(w=2 ** 17, seed=23, mode="noexec")
    m0 = float(s.lens.mean())
    for _ in range(1000):
        s.epoch()
    m1 = float(s.lens.mean())
    out.append(("bffvl length null: under noexec (cut rule and mutation only) mean length moves < 2 bytes in 1000 "
                "epochs", abs(m1 - m0) < 2, f"{m0:.1f} -> {m1:.1f}"))
    s = V.Soup(w=2 ** 16, seed=24, mode="copyall")
    for _ in range(300):
        s.epoch()
    out.append(("bffvl length reference: under copyall (every program copies itself, whatever its code) the soup "
                "collapses to LMIN-byte pieces", float(s.lens.mean()) < 6, f"mean length {s.lens.mean():.2f}"))
    return out


if __name__ == "__main__":
    import json
    import time
    t0 = time.time()
    res = controls()
    for name, ok, det in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {det}", flush=True)
    print(json.dumps({"passed": int(sum(o for _, o, _ in res)), "total": len(res), "sec": round(time.time() - t0)}))
