"""E-82 groundwork (J-099): instruments for BFF-X (scripts/bffx.py).

* `replication_test`  replicator (host) detector: 8 copies of x in 2^15 bytes of random code, 48 epochs, no mutation;
                      passes if x's family grows to >= 64 and >= 4x, twice (generation 2 from the commonest family
                      member); rule-level null on a random program of the same length (as bffvl_assay.replication_test,
                      D-071). For hosts it runs with libmode "none" (nothing can be borrowed): a host must copy
                      itself with its own code. Under the soup's own rule a long host is overrun within 48 epochs by
                      short parasites made from its own debris (J-099), so growth under that rule is not a host test.
* `parasite_test`     parasite detector, adapted from D-048/D-049 (emergence/observatory/program_parasites.py):
                        alone        x never copies itself: no copy in 32 runs against random partners and random
                                     libraries, and its family never grows in 4 replication tests ("self-copier"
                                     otherwise);
                        template q   x runs first with partner and library drawn from the pool (x-like programs
                                     excluded); q = share of runs that leave >= 1 copy of x ("not copied" if
                                     q < Q_MIN);
                        host dep.    the same with random-code libraries; one-sided Fisher test that pool libraries
                                     copy x more often (p < ALPHA), else "host-independent";
                        context      x copies itself with no library at all (libmode none) in >= Q_MIN of runs:
                                     "context self-copier";
                        by-product   templated share F = c k / (c k + n b): k = copies per run with x first (x is
                                     first in half its pairings, so c k / 2 template copies per epoch), b = x-like
                                     programs made per pair from pool triples without x-like programs (n / 2 pairs);
                                     F = (c k / 2) / (c k / 2 + n b / 2); "by-product" if F < F_MIN;
                        otherwise    "parasite". The libraries that copied x are returned as hosts.
* `q_matrix`          time-shift assay: coverage q(P, H) = share of a random 128-byte partner that parasite P (first)
                      fills with copies of itself with host H as its borrowed code, averaged over the parasite/host
                      pairs of two samples. (A first version used the share of runs with >= 1 copy; it saturated at
                      1 in every pilot soup, J-099.)
* `timeshift`         Red Queen statistic from samples at times t1 < ... < tk: RQ = mean over i < j of
                      [q(P_j, H_i) - q(P_i, H_j)] (later parasites on earlier hosts minus earlier parasites on later
                      hosts). Swapping the time labels flips its sign, so the sign-flip test over soups is the
                      shuffled-time null.
"""
from __future__ import annotations

from collections import Counter

import numpy as np
from scipy.stats import fisher_exact

import bffx as X

Q_MIN, ALPHA, F_MIN = 0.02, 0.01, 0.5
M_T, M_PROD = 256, 2048


def like(progs, x) -> np.ndarray:
    lens = np.array([len(p) for p in progs], np.int32)
    buf = np.concatenate(progs) if len(progs) else np.zeros(0, np.uint8)
    return X.members(buf, lens, x)


def background(rng, w: int) -> list[np.ndarray]:
    buf = rng.integers(0, 256, w, dtype=np.uint8)
    return X.split(buf, X.cut(buf))


def seeded_soup(rng, w: int, groups, libmode: str, bg=None) -> X.Soup:
    progs = list(bg) if bg is not None else background(rng, w)
    for x, count in groups:
        progs += [X.u8(x).copy() for _ in range(count)]
    return X.Soup.from_programs(progs, rng=rng, libmode=libmode, mutation=0.0)


def family(s: X.Soup, x) -> np.ndarray:
    return X.members(s.buf, s.lens, x)


def replication_test(x, rng, libmode: str = "none", k: int = 8, w: int = 2 ** 15, epochs: int = 48,
                     null: bool = True) -> dict:
    x = X.u8(x)

    def gen(prog):
        s = seeded_soup(rng, w, [(prog, k)], libmode)
        start = int(family(s, x).sum())
        for _ in range(epochs):
            s.epoch()
        fam = family(s, x)
        late = int(fam.sum())
        ok = late >= 64 and late >= 4 * start
        member = None
        if ok:
            progs = s.programs()
            member = np.frombuffer(Counter(bytes(progs[i]) for i in np.nonzero(fam)[0]).most_common(1)[0][0],
                                   np.uint8).copy()
        return {"start": start, "late": late, "pass": ok}, member

    g1, m = gen(x)
    out = {"gen1": g1, "gen2": None}
    if g1["pass"]:
        out["gen2"], _ = gen(m)
    rep = g1["pass"] and out["gen2"]["pass"]
    if rep and null:
        r = rng.integers(0, 256, len(x), dtype=np.uint8)
        r[r == X.MARKER] = 0x80
        r[-1] = X.MARKER
        s = seeded_soup(rng, w, [(r, k)], libmode)
        st = int(family(s, r).sum())
        for _ in range(epochs):
            s.epoch()
        lt = int(family(s, r).sum())
        out["null"] = {"start": st, "late": lt}
        if lt >= 64 and lt >= 4 * st:
            out["verdict"] = "rule-level duplication"
            return out
    out["verdict"] = "replicator" if rep else ("one generation" if g1["pass"] else "no replication")
    return out


def _runs(x, partners, libs, libmode: str) -> tuple[int, int, list]:
    """x first with each (partner, library); returns (runs with >= 1 copy, total copies, indices with a copy)."""
    hit, tot, who = 0, 0, []
    for i, (b, c) in enumerate(zip(partners, libs)):
        if libmode == "snapshot":
            h, k = X.screen(x, 0, 1, host_b=b, libmode=libmode)
        else:
            h, k = X.screen(x, 0, 1, host_b=b, host_c=c, libmode=libmode)
        hit += h
        tot += k
        if h:
            who.append(i)
    return hit, tot, who


def parasite_test(x, pool: list[np.ndarray], rng, libmode: str = "neighbour", m: int = M_T, m_prod: int = M_PROD,
                  alone_reps: int = 4) -> dict:
    x = X.u8(x)
    seed = int(rng.integers(2 ** 62))
    # alone: random partners and libraries (in snapshot mode the partner is the library)
    a_hits, _ = X.screen(x, seed, 32, libmode=libmode)
    grew = 0
    if a_hits == 0:
        for _ in range(alone_reps):
            r = replication_test(x, np.random.default_rng(int(rng.integers(2 ** 62))), libmode, null=False)
            grew += bool(r["gen1"]["pass"])
            if grew:
                break
    lk = like(pool, x)
    idx = np.flatnonzero(~lk)
    res = {"alone_hits": int(a_hits), "alone_grew": grew}
    if a_hits or grew:
        return {**res, "verdict": "self-copier"}
    pb, pc = rng.choice(idx, m), rng.choice(idx, m)
    hit, tot, who = _runs(x, [pool[i] for i in pb], [pool[i] for i in pc], libmode)
    q, k = hit / m, tot / m
    # host dependence: the same partners, random-code libraries of the same lengths
    rnd = [rng.integers(0, 256, len(pool[i]), dtype=np.uint8) for i in pc]
    if libmode == "snapshot":
        hr, _, _ = _runs(x, rnd, rnd, libmode)
    else:
        hr, _, _ = _runs(x, [pool[i] for i in pb], rnd, libmode)
    p = float(fisher_exact([[hit, m - hit], [hr, m - hr]], alternative="greater")[1])
    # context self-copier: no borrowed code at all
    ctx, _ = X.screen(x, seed + 1, 64, libmode="none")
    # de novo production from pool triples without x-like programs
    made = 0
    tri = rng.choice(idx, (m_prod, 3))
    for a, b, c in tri:
        pcs, _ = X.run_pair(pool[a], pool[b], pool[c], libmode=libmode)
        made += int(like(pcs, x).sum())
    bprod = made / m_prod
    c_, n = int(lk.sum()), len(pool)
    tmpl, denovo = c_ * k / 2, n * bprod / 2
    F = tmpl / (tmpl + denovo) if tmpl + denovo > 0 else 0.0
    hosts = [int(pc[i]) for i in who] if libmode == "neighbour" else [int(pb[i]) for i in who]
    res.update({"q": round(q, 4), "copies_per_run": round(k, 3), "q_random_lib": round(hr / m, 4), "p": p,
                "context_rate": round(ctx / 64, 4), "b": round(bprod, 5), "count": c_, "templated_share": round(F, 4),
                "hosts": hosts})
    if q < Q_MIN:
        v = "not copied"
    elif p >= ALPHA:
        v = "host-independent"
    elif ctx / 64 >= Q_MIN:
        v = "context self-copier"
    elif F < F_MIN:
        v = "by-product"
    else:
        v = "parasite"
    res["verdict"] = v
    return res


def q_pair(P, H, seed: int, trials: int = 32, libmode: str = "neighbour", lp: int = 128) -> float:
    """Coverage: the share of a random lp-byte partner that P (run first) fills with copies of itself when H is its
    borrowed code (library; in snapshot mode H is the partner and lp = len(H)), averaged over `trials` runs:
    copies x len(P) / lp. A host that copies every caller gives ~1; a host that refuses gives 0. Graded, and
    independent of the parasite's length (a shorter parasite makes more copies, not more coverage)."""
    if libmode == "snapshot":
        _, c = X.screen(P, seed, trials, host_b=H, libmode=libmode)
        return c * len(P) / (trials * len(H))
    _, c = X.screen(P, seed, trials, host_c=H, lp=lp, libmode=libmode)
    return c * len(P) / (trials * lp)


def q_matrix(Ps, Hs, seed: int, trials: int = 32, libmode: str = "neighbour") -> float:
    if not Ps or not Hs:
        return float("nan")
    return float(np.mean([q_pair(p, h, seed + 97 * i + j, trials, libmode)
                          for i, p in enumerate(Ps) for j, h in enumerate(Hs)]))


def timeshift(samples: list[tuple[list, list]], seed: int, trials: int = 32, libmode: str = "neighbour") -> dict:
    """samples[t] = (parasites, hosts) at time t (increasing). RQ = mean over i < j of q(P_j, H_i) - q(P_i, H_j)."""
    k = len(samples)
    Q = [[q_matrix(samples[i][0], samples[j][1], seed + 1000 * i + 10 * j, trials, libmode) for j in range(k)]
         for i in range(k)]
    d = [Q[j][i] - Q[i][j] for i in range(k) for j in range(i + 1, k)
         if not (np.isnan(Q[j][i]) or np.isnan(Q[i][j]))]
    return {"Q": [[None if np.isnan(v) else round(v, 4) for v in row] for row in Q],
            "RQ": round(float(np.mean(d)), 4) if d else None}


# ---- designed programs ------------------------------------------------------------------------------
def host(length: int = 12) -> np.ndarray:
    """Hand host: [.>}] then filler and the marker. As the first program it copies itself into its partner; as
    borrowed code it copies whatever program borrowed it."""
    return X.hand_copier(length)


def resistant_host(key: int = 1, length: int = 16) -> np.ndarray:
    """Host that copies its executor only if the executor's first byte equals `key`: byte 0 is `key` (a no-op),
    then '-' x key, '[]' (a trap: loops on a nonzero byte until the step limit), '+' x key, then the copy loop. Run
    by itself, byte 0 is its own key, so it copies itself."""
    code = bytes([key]) + b"-" * key + b"[]" + b"+" * key + b"[.>}]"
    return X.pad(code, length)


def parasite(length: int = 12, key: int | None = None) -> np.ndarray:
    """Hand parasite: inert filler and the marker, so the instruction pointer runs off its end into the borrowed
    code; with `key` its first byte is that key (adapted to resistant_host(key))."""
    p = X.pad(b"", length)
    if key is not None:
        p[0] = key
    return p


def dead_host(length: int = 12) -> np.ndarray:
    """Deceptive (host product): the host with its '[' replaced by ']': ~92% like the host, so the host's own copies
    look like copies of it, but it halts at once (unmatched ']')."""
    d = host(length).copy()
    d[0] = ord("]")
    return d


def host_fragment(length: int = 8) -> np.ndarray:
    """Deceptive (host fragment): the remainder a 12-byte host leaves when its partner is not a multiple of 12: its
    first `length` bytes, no marker. It runs its own loop, so it never borrows code."""
    return host(12)[:length].copy()


def host_pool(rng, n: int = 1024, hosts: float = 0.5, guest=None, guest_share: float = 0.05, h=None,
              junk=None, junk_share: float = 0.0) -> list[np.ndarray]:
    """Hosts (share `hosts`), optional junk and guest, the rest random programs of 4 to 128 bytes cut by the rule."""
    h = host() if h is None else h
    out = [h.copy() for _ in range(int(n * hosts))]
    if junk is not None:
        out += [X.u8(junk).copy() for _ in range(int(n * junk_share))]
    if guest is not None:
        out += [X.u8(guest).copy() for _ in range(int(n * guest_share))]
    while len(out) < n:
        out += background(rng, 4096)
    out = out[:n]
    return [out[i] for i in rng.permutation(len(out))]


def byproduct_pool(rng, n: int = 1024) -> tuple[list[np.ndarray], np.ndarray]:
    """Deceptive by-product: 40% hosts, 40% 'makers', 2% product Z, rest random. Z is an 8-byte inert program; each
    maker is Z followed by its own 8 random inert bytes (no marker), so it falls through and the host copies it:
    the cut makes a Z from every copy. Z is copied by hosts (specifically), but most Z are made by makers."""
    z = parasite(8)
    z[:7] = X.NONOP_NZ[rng.integers(0, len(X.NONOP_NZ), 7)]
    out = [host() for _ in range(int(0.4 * n))]
    for _ in range(int(0.4 * n)):
        out.append(np.concatenate([z, X.NONOP_NZ[rng.integers(0, len(X.NONOP_NZ), 8)]]).astype(np.uint8))
    out += [z.copy() for _ in range(int(0.02 * n))]
    while len(out) < n:
        out += background(rng, 4096)
    out = out[:n]
    return [out[i] for i in rng.permutation(len(out))], z


def soup_top(s: X.Soup, k: int = 40) -> list[tuple[np.ndarray, int]]:
    return [(np.frombuffer(b, np.uint8).copy(), c) for b, c in X.top_distinct(s, k)]


# ---- controls (pytest `test_bffx_controls`, `emergence benchmark --probes`) -----------------------------
def controls(libmode: str = "neighbour") -> list[tuple[str, bool, str]]:
    import bffvl as V
    out = []
    rng = np.random.default_rng(82)

    # the rule
    a = V.Soup(w=2 ** 16, seed=5)
    b = X.Soup(w=2 ** 16, seed=5, libmode="live")
    for _ in range(40):
        a.epoch()
        b.epoch()
    same = bool((a.buf == b.buf).all() and (a.lens == b.lens).all())
    out.append(("bffx rule: libmode live == BFF-VL (bffvl.Soup) bit for bit over 40 epochs", same, f"identical {same}"))
    s = X.Soup(w=2 ** 16, seed=4, libmode=libmode)
    ok, lo, hi = True, 999, 0
    for _ in range(50):
        s.epoch()
        ok &= int(s.lens.sum()) == 2 ** 16 == len(s.buf)
        lo, hi = min(lo, int(s.lens.min())), max(hi, int(s.lens.max()))
    out.append((f"bffx rule ({libmode}): bytes conserved, pieces within [LMIN, LMAX]", ok and lo >= 4 and hi <= 128,
                f"conserved {ok}, lengths {lo}..{hi}"))
    H, P = host(), parasite()
    lib_before = H.copy()
    pcs, _ = X.run_pair(P, rng.integers(0, 256, 100, dtype=np.uint8), H, libmode="neighbour")
    n_p = sum(len(q) == 12 and bool((q == P).all()) for q in pcs)
    out.append(("bffx rule: the library is read only and an inert program that borrows the host's code leaves copies"
                " of itself (neighbour mode)", bool((H == lib_before).all()) and n_p >= 8, f"exact parasite copies {n_p}"))
    pcs, _ = X.run_pair(P, rng.integers(0, 256, 100, dtype=np.uint8), None, libmode="none")
    n0 = sum(len(q) == 12 and bool((q == P).all()) for q in pcs)
    out.append(("bffx rule: with nothing to borrow (libmode none) the inert program leaves only itself", n0 == 1,
                f"copies {n0}"))

    # host (replicator) detector
    v = {L: replication_test(host(L), rng)["verdict"] for L in (8, 24, 48)}
    out.append(("bffx hosts positive: hand hosts of 8, 24 and 48 bytes -> replicator (nothing borrowed)",
                all(x == "replicator" for x in v.values()), f"{v}"))
    v = {"random": replication_test(rng.integers(0, 256, 24, dtype=np.uint8), rng)["verdict"],
         "parasite": replication_test(parasite(), rng)["verdict"],
         "parasite, soup rule": replication_test(parasite(), rng, libmode)["verdict"],
         "dead host": replication_test(dead_host(), rng)["verdict"]}
    out.append((f"bffx hosts negative/deceptive: random program, hand parasite (also under the {libmode} rule in "
                "random code, where it has no hosts), dead host -> no replication",
                all(x == "no replication" for x in v.values()), f"{v}"))

    # parasite detector
    def pt(x, pool, seed):
        return parasite_test(x, pool, np.random.default_rng(seed), libmode, m=128, m_prod=1024)

    r = pt(P, host_pool(rng, guest=P), 1)
    out.append((f"bffx parasites positive ({libmode}): hand parasite at 5% among 50% hand hosts -> parasite",
                r["verdict"] == "parasite", _pb(r)))
    r1 = pt(rng.integers(0, 256, 24, dtype=np.uint8), host_pool(rng), 2)
    r2 = pt(H, host_pool(rng), 3)
    out.append((f"bffx parasites negative ({libmode}): a random program -> not parasite; the host -> self-copier",
                r1["verdict"] != "parasite" and r2["verdict"] == "self-copier", f"{r1['verdict']}; {r2['verdict']}"))
    r1 = pt(dead_host(), host_pool(rng, junk=dead_host(), junk_share=0.2), 4)
    r2 = pt(host_fragment(), host_pool(rng, junk=host_fragment(), junk_share=0.2), 5)
    out.append((f"bffx parasites deceptive ({libmode}): common dead host (host copies look like it) and common host "
                "fragment -> not parasite", r1["verdict"] != "parasite" and r2["verdict"] != "parasite",
                f"dead host: {_pb(r1)}; fragment: {_pb(r2)}"))
    pool, z = byproduct_pool(rng)
    r = pt(z, pool, 6)
    out.append((f"bffx parasites deceptive ({libmode}): product Z made from many makers -> by-product",
                r["verdict"] == "by-product", _pb(r)))
    R = resistant_host(1)
    r = pt(P, host_pool(rng, guest=P, h=R), 7)
    r1 = pt(parasite(key=1), host_pool(rng, guest=parasite(key=1), h=R), 8)
    out.append((f"bffx parasites specificity ({libmode}): the plain parasite among resistant hosts -> not copied; "
                "the parasite with the host's key -> parasite", r["verdict"] == "not copied" and
                r1["verdict"] == "parasite", f"{r['verdict']}; {r1['verdict']}"))
    # selection-aware nulls: common programs of soups in which no code can be borrowed
    s = X.Soup(w=2 ** 17, seed=31, libmode=libmode)
    for _ in range(50):
        s.epoch()
    early = soup_top(s, 20)
    pool = s.programs()
    v1 = [pt(x, pool, 100 + i)["verdict"] for i, (x, _) in enumerate(early)]
    out.append((f"bffx parasites selection-aware null ({libmode}): top 20 programs of a soup at epoch 50 (no hosts "
                "yet) -> 0 parasites", "parasite" not in v1, f"{Counter(v1)}"))

    # time-shift assay
    hist = [([parasite()], [host()]), ([parasite(key=1)], [resistant_host(1)])]
    r = timeshift(hist, 11, libmode=libmode)
    out.append((f"bffx time-shift positive ({libmode}): designed arms race (resistant host, then key-matched parasite) "
                "-> RQ ~ 1", r["RQ"] is not None and r["RQ"] > 0.8, f"{r}"))
    mix_late = [host(), host(), host(), host(), resistant_host(1)]
    r = timeshift([([parasite()], [host()] * 5), ([parasite()], mix_late)], 12, libmode=libmode)
    out.append((f"bffx time-shift graded ({libmode}): 1 of 5 later hosts resistant -> RQ = 0.2", abs(r["RQ"] - 0.2) < 0.03,
                f"RQ {r['RQ']}"))
    r = timeshift([([parasite(8)], [host(12)]), ([parasite(16)], [host(14)])], 13, libmode=libmode)
    r2 = timeshift([([parasite(12)], [host(12)]), ([parasite(14)], [host(14)])], 13, libmode=libmode)
    out.append((f"bffx time-shift negative ({libmode}): later parasites and hosts that changed length without "
                "resistance -> RQ = 0 (8 -> 16-byte parasites); length artefact of coverage (12 -> 14 bytes: "
                "128 is not a multiple of either) below half of delta* 0.1", abs(r["RQ"]) < 0.01 and abs(r2["RQ"]) < 0.05,
                f"RQ {r['RQ']}; artefact {r2['RQ']}"))
    r = timeshift([([parasite(key=1)], [resistant_host(1)]), ([parasite()], [host()])], 14, libmode=libmode)
    out.append((f"bffx time-shift null ({libmode}): the positive history with its time labels reversed -> RQ ~ -1",
                r["RQ"] is not None and r["RQ"] < -0.8, f"RQ {r['RQ']}"))
    return out


def _pb(r: dict) -> str:
    keys = ("verdict", "q", "q_random_lib", "context_rate", "templated_share", "count")
    return ", ".join(f"{k} {r.get(k)}" for k in keys if k in r)


if __name__ == "__main__":
    import json
    import sys
    import time
    t0 = time.time()
    res = controls(sys.argv[1] if len(sys.argv) > 1 else "neighbour")
    for name, ok, det in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {det}", flush=True)
    print(json.dumps({"passed": int(sum(o for _, o, _ in res)), "total": len(res), "sec": round(time.time() - t0)}))
