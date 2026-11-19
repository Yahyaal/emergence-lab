"""E-84 groundwork (J-103, D-077): instruments for fixed-length BFF-X (scripts/bffxf.py). They follow E-82/E-83's
(`bffx_assay`, `bffxr_assay`; D-073, D-075) with the programs fixed at 64 bytes, so each is re-validated here.

* `replication_test`  host detector: 8 copies in 512 random programs (2^15 bytes), 48 epochs, well mixed, nothing
                      borrowed (libmode none), no mutation; family >= 64 and >= 4x, twice; rule-level null.
* `parasite_test`     E-82's parasite detector (alone / template q / host dependence / context / by-product).
* `q_pair`            coverage: share of runs in which parasite P (first) turns a random 64-byte partner into a copy of
                      itself with H as its library (one partner = one possible copy in this rule).
* `w_pair`            protection: mean share of the partner left unchanged.
* `timeshift`, `timeshift_w`   RQ and RQ_w over samples (E-82, E-83).
* `compete`           races of designed programs in random code; each program is assigned to the designed program it
                      matches best (R and its sham differ in 2 of 64 bytes, so plain family membership cannot tell
                      them apart); score = change of ln((focal + 1) / (rival + 1)).
* `sample`            the E-84 sampler (hosts and verified parasites of a snapshot), shared by the driver and the
                      seeded arm.
"""
from __future__ import annotations

import time
from collections import Counter

import numpy as np
from scipy.stats import fisher_exact

import bffx as X
import bffxf as F

Q_MIN, ALPHA, F_MIN = 0.02, 0.01, 0.5
M_T, M_PROD = 256, 2048
LOOP = b"[.>}]"


# ---- designed programs ------------------------------------------------------------------------------
def host(offset: int = 0) -> np.ndarray:
    """Plain host: the copy loop (at `offset`, no-ops before it) and no-op filler."""
    return F.pad(bytes([F.FILL]) * offset + LOOP)


def resistant_host(key: int = 1) -> np.ndarray:
    """Copies its executor only if the executor's first byte is `key`: byte 0 = key (a no-op), '-' x key, '[]' (a
    trap: loops on a nonzero byte until the step limit), '+' x key, then the copy loop. Run by itself, byte 0 is its
    own key, so it copies itself. Same length as every program (64 bytes): the lock costs no length."""
    return F.pad(bytes([key]) + b"-" * key + b"[]" + b"+" * key + LOOP)


def sham_host(key: int = 1) -> np.ndarray:
    """R with its trap '[]' replaced by two no-op bytes: the same bytes elsewhere, but copies every caller."""
    r = resistant_host(key).copy()
    i = 1 + key
    assert bytes(r[i:i + 2]) == b"[]"
    r[i:i + 2] = F.FILL
    return r


def parasite(key: int | None = None, fill: int = F.FILL) -> np.ndarray:
    """Inert program (no instruction bytes), so the instruction pointer runs off its end into the borrowed code; with
    `key` its first byte is that key."""
    p = np.full(F.L, fill, np.uint8)
    if key is not None:
        p[0] = key
    return p


def dead_host() -> np.ndarray:
    """Deceptive (host product): the host with its '[' replaced by ']' (63 of 64 bytes like the host, so the host's
    copies look like it), which halts at once (unmatched ']')."""
    d = host().copy()
    d[0] = ord("]")
    return d


def shifting_host(key: int = 1, shift: int = 7) -> np.ndarray:
    """Deceptive for coverage: copies itself exactly, but a caller whose first byte is not `key` is copied `shift`
    bytes late (q = 0: the partner is no copy of it) while the partner is overwritten just the same (w ~ shift/64:
    no protection). Code: key, '-', '[' '}' x shift '[-]' ']' (if the caller's byte was nonzero: move head1, clear
    it), '+', copy loop."""
    return F.pad(bytes([key]) + b"-[" + b"}" * shift + b"[-]]+" + LOOP)


def maker(pattern_seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """Deceptive by-product: a maker writes a fixed inert program Z into its partner (it scans head0 to its zero byte
    at 40 and copies its own inert tail, then the copied tail again, so Z is the tail repeated). Z is copied by hosts,
    but most Z are made by makers. Returns (maker, Z)."""
    rng = np.random.default_rng([84, 7, pattern_seed])
    tail = X.NONOP_NZ[rng.integers(0, len(X.NONOP_NZ), 23)]
    m = F.pad(b"[>]>" + LOOP)
    m[40] = 0
    m[41:] = tail
    pcs, _ = F.run_pair(m, rng.integers(0, 256, 64, dtype=np.uint8), None, libmode="none")
    return m, pcs[1].copy()


def host_pool(rng, n: int = 1024, hosts: float = 0.5, guest=None, guest_share: float = 0.05, h=None,
              junk=None, junk_share: float = 0.0) -> list[np.ndarray]:
    h = host() if h is None else h
    out = [h.copy() for _ in range(int(n * hosts))]
    if junk is not None:
        out += [X.u8(junk).copy() for _ in range(int(n * junk_share))]
    if guest is not None:
        out += [X.u8(guest).copy() for _ in range(int(n * guest_share))]
    out += list(rng.integers(0, 256, (n - len(out), F.L), dtype=np.uint8))
    return [out[i] for i in rng.permutation(len(out))]


# ---- host detector ----------------------------------------------------------------------------------
def like(progs, x) -> np.ndarray:
    if not len(progs):
        return np.zeros(0, bool)
    buf = np.concatenate(progs)
    return F.members(buf, F.random_lens(len(buf)), x)


def seeded_soup(rng, n: int, groups, libmode: str, geometry: str = "mixed", mutation: float = 0.0):
    progs = []
    for x, count in groups:
        progs += [X.u8(x).copy() for _ in range(count)]
    progs += list(rng.integers(0, 256, (n - len(progs), F.L), dtype=np.uint8))
    progs = [progs[i] for i in rng.permutation(len(progs))]
    return F.from_programs(progs, geometry, rng=rng, libmode=libmode, mutation=mutation)


def replication_test(x, rng, libmode: str = "none", k: int = 8, n: int = 512, epochs: int = 48,
                     null: bool = True) -> dict:
    x = X.u8(x)

    def gen(prog):
        s = seeded_soup(rng, n, [(prog, k)], libmode)
        st = int(F.members(s.buf, s.lens, x).sum())
        for _ in range(epochs):
            s.epoch()
        fam = F.members(s.buf, s.lens, x)
        late = int(fam.sum())
        ok = late >= 64 and late >= 4 * st
        member = None
        if ok:
            pr = F.programs(s)
            member = np.frombuffer(Counter(bytes(pr[i]) for i in np.nonzero(fam)[0]).most_common(1)[0][0],
                                   np.uint8).copy()
        return {"start": st, "late": late, "pass": ok}, member

    g1, m = gen(x)
    out = {"gen1": g1, "gen2": None}
    if g1["pass"]:
        out["gen2"], _ = gen(m)
    rep = g1["pass"] and out["gen2"]["pass"]
    if rep and null:
        r = rng.integers(0, 256, F.L, dtype=np.uint8)
        s = seeded_soup(rng, n, [(r, k)], libmode)
        st = int(F.members(s.buf, s.lens, r).sum())
        for _ in range(epochs):
            s.epoch()
        lt = int(F.members(s.buf, s.lens, r).sum())
        out["null"] = {"start": st, "late": lt}
        if lt >= 64 and lt >= 4 * st:
            out["verdict"] = "rule-level duplication"
            return out
    out["verdict"] = "replicator" if rep else ("one generation" if g1["pass"] else "no replication")
    return out


# ---- parasite detector (E-82's, D-073) --------------------------------------------------------------
def _runs(x, partners, libs, libmode: str):
    hit, tot, who = 0, 0, []
    for i, (b, c) in enumerate(zip(partners, libs)):
        h, k = F.screen(x, 0, 1, host_b=b, host_c=c, libmode=libmode)
        hit += h
        tot += k
        if h:
            who.append(i)
    return hit, tot, who


def parasite_test(x, pool, rng, libmode: str = "neighbour", m: int = M_T, m_prod: int = M_PROD,
                  alone_reps: int = 4) -> dict:
    x = X.u8(x)
    seed = int(rng.integers(2 ** 62))
    a_hits, _ = F.screen(x, seed, 32, libmode=libmode)
    grew = 0
    if a_hits == 0:
        for _ in range(alone_reps):
            r = replication_test(x, np.random.default_rng(int(rng.integers(2 ** 62))), libmode, null=False)
            grew += bool(r["gen1"]["pass"])
            if grew:
                break
    res = {"alone_hits": int(a_hits), "alone_grew": grew}
    if a_hits or grew:
        return {**res, "verdict": "self-copier"}
    lk = like(pool, x)
    idx = np.flatnonzero(~lk)
    pb, pc = rng.choice(idx, m), rng.choice(idx, m)
    hit, tot, who = _runs(x, [pool[i] for i in pb], [pool[i] for i in pc], libmode)
    q, k = hit / m, tot / m
    rnd = [rng.integers(0, 256, F.L, dtype=np.uint8) for _ in pc]
    hr, _, _ = _runs(x, [pool[i] for i in pb], rnd, libmode)
    p = float(fisher_exact([[hit, m - hit], [hr, m - hr]], alternative="greater")[1])
    ctx, _ = F.screen(x, seed + 1, 64, libmode="none")
    made = 0
    for a, b, c in rng.choice(idx, (m_prod, 3)):
        pcs, _ = F.run_pair(pool[a], pool[b], pool[c], libmode=libmode)
        made += int(like(pcs, x).sum())
    bprod = made / m_prod
    c_, n = int(lk.sum()), len(pool)
    tmpl, denovo = c_ * k / 2, n * bprod / 2
    Fs = tmpl / (tmpl + denovo) if tmpl + denovo > 0 else 0.0
    res.update({"q": round(q, 4), "copies_per_run": round(k, 3), "q_random_lib": round(hr / m, 4), "p": p,
                "context_rate": round(ctx / 64, 4), "b": round(bprod, 5), "count": c_, "templated_share": round(Fs, 4),
                "hosts": [int(pc[i]) for i in who]})
    if q < Q_MIN:
        v = "not copied"
    elif p >= ALPHA:
        v = "host-independent"
    elif ctx / 64 >= Q_MIN:
        v = "context self-copier"
    elif Fs < F_MIN:
        v = "by-product"
    else:
        v = "parasite"
    res["verdict"] = v
    return res


def _pb(r: dict) -> str:
    keys = ("verdict", "q", "q_random_lib", "context_rate", "templated_share", "count")
    return ", ".join(f"{k} {r.get(k)}" for k in keys if k in r)


# ---- interaction scores and time-shift --------------------------------------------------------------
def q_pair(P, H, seed: int, trials: int = 32) -> float:
    _, c = F.screen(P, seed, trials, host_c=H)
    return c / trials


def w_pair(P, H, seed: int, trials: int = 32) -> float:
    rng = np.random.default_rng(seed)
    P, H = X.u8(P), X.u8(H)
    tot = 0.0
    for _ in range(trials):
        b = rng.integers(0, 256, F.L, dtype=np.uint8)
        t = X.u8(np.concatenate([P, b]))
        X.lib().x_run(t.ctypes.data, F.L, F.L, H.ctypes.data, len(H), F.STEPS, X.LIBMODES["neighbour"])
        tot += float((t[F.L:] == b).mean())
    return tot / trials


def _matrix(fn, Ps, Hs, seed: int, trials: int) -> float:
    if not Ps or not Hs:
        return float("nan")
    return float(np.mean([fn(p, h, seed + 97 * i + j, trials) for i, p in enumerate(Ps) for j, h in enumerate(Hs)]))


def timeshift(samples, seed: int, trials: int = 32) -> dict:
    """RQ = mean over i < j of q(P_j, H_i) - q(P_i, H_j)."""
    k = len(samples)
    Q = [[_matrix(q_pair, samples[i][0], samples[j][1], seed + 1000 * i + 10 * j, trials) for j in range(k)]
         for i in range(k)]
    d = [Q[j][i] - Q[i][j] for i in range(k) for j in range(i + 1, k) if not (np.isnan(Q[j][i]) or np.isnan(Q[i][j]))]
    return {"Q": [[None if np.isnan(v) else round(v, 4) for v in row] for row in Q],
            "RQ": round(float(np.mean(d)), 4) if d else None}


def timeshift_w(samples, seed: int, trials: int = 32) -> dict:
    """RQ_w = mean over i < j of w(P_i, H_j) - w(P_j, H_i)."""
    k = len(samples)
    Wm = [[_matrix(w_pair, samples[i][0], samples[j][1], seed + 1000 * i + 10 * j, trials) for j in range(k)]
          for i in range(k)]
    d = [Wm[i][j] - Wm[j][i] for i in range(k) for j in range(i + 1, k)
         if not (np.isnan(Wm[i][j]) or np.isnan(Wm[j][i]))]
    return {"W": [[None if np.isnan(v) else round(v, 4) for v in row] for row in Wm],
            "RQ_w": round(float(np.mean(d)), 4) if d else None}


# ---- races ----------------------------------------------------------------------------------------
DESIGNED = {"H": host, "R": resistant_host, "S": sham_host, "P": parasite, "Pk": lambda: parasite(key=1)}


def assign(s, progs: dict) -> dict:
    """Count programs per designed program, each assigned to the one it matches best (>= 90% of bytes and >= 75% of
    instruction bytes; ties to neither)."""
    names = list(progs)
    sc = np.stack([X.match(s.buf, s.lens, progs[k], F.TOL, F.THR, F.OPMIN) for k in names])
    best = sc.max(0)
    win = sc.argmax(0)
    uniq = (sc == best).sum(0) == 1
    ok = (best >= 0) & uniq
    return {k: int(((win == i) & ok).sum()) for i, k in enumerate(names)}


def start(seed: int, shares: dict, n: int = F.N) -> list[np.ndarray]:
    rng = np.random.default_rng([84, 1, seed])
    progs = []
    for name, sh in shares.items():
        progs += [DESIGNED[name]() for _ in range(int(sh * n))]
    progs += list(rng.integers(0, 256, (n - len(progs), F.L), dtype=np.uint8))
    return [progs[i] for i in rng.permutation(len(progs))]


def compete(seed: int, geometry: str, libmode: str, shares: dict, focal: str = "R", rival: str = "S",
            horizons=(25, 50, 100, 200), every: int = 5, n: int = F.N, mutation: float = 0.0) -> dict:
    s = F.from_programs(start(seed, shares, n), geometry, rng=np.random.default_rng([84, 2, seed]), libmode=libmode,
                        mutation=mutation)
    progs = {k: DESIGNED[k]() for k in shares}
    traj, t0 = [], time.time()
    for e in range(max(horizons) + 1):
        if e % every == 0 or e in horizons:
            traj.append({"epoch": e, **assign(s, progs)})
        if e < max(horizons):
            s.epoch()
    by = {t["epoch"]: t for t in traj}
    a = by[0]
    sc = {h: round(float(np.log((by[h][focal] + 1) / (by[h][rival] + 1)) - np.log((a[focal] + 1) / (a[rival] + 1))), 4)
          for h in horizons}
    return {"seed": seed, "geometry": geometry, "libmode": libmode, "focal": focal, "rival": rival,
            "mutation": mutation, "scores": sc, "traj": traj, "sec": round(time.time() - t0, 1)}


# ---- sampler (E-84; E-82/E-83's with 64-byte programs) ------------------------------------------------
TOPK, TOPFAM, KH, KP, POOL = 40, 10, 5, 5, 4096


def hosts_of(s, key: int):
    top = F.top_distinct(s, TOPK)
    hs = [(b, c) for i, (b, c) in enumerate(top) if F.is_copier(np.frombuffer(b, np.uint8), key * 1000 + i)]
    share = 0.0
    if hs:
        fam = np.zeros(s.n, bool)
        for b, _ in hs[:TOPFAM]:
            fam |= F.members(s.buf, s.lens, np.frombuffer(b, np.uint8))
        share = float(fam.mean())
    return hs, round(share, 4)


def sample(s, seed: int, tag: int, exp: int = 84) -> dict:
    hs, share = hosts_of(s, seed * 100003 + 77 + tag)
    rng = np.random.default_rng([exp, seed, tag])
    progs = F.programs(s)
    pool = [progs[i] for i in rng.choice(len(progs), min(POOL, len(progs)), replace=False)]
    hostset = {b for b, _ in hs}
    top = [(b, c) for b, c in F.top_distinct(s, TOPK + len(hs)) if b not in hostset][:TOPK]
    paras, verdicts, tests = [], [], []
    for b, c in top:
        if len(paras) >= KP:
            break
        r = parasite_test(np.frombuffer(b, np.uint8), pool, rng, libmode=s.libmode)
        r.pop("hosts", None)
        verdicts.append(r["verdict"])
        tests.append({"hex": b.hex(), "soup_count": c, **r})
        if r["verdict"] == "parasite":
            paras.append((b.hex(), c))
    fam = np.zeros(s.n, bool)
    for h, _ in paras:
        fam |= F.members(s.buf, s.lens, np.frombuffer(bytes.fromhex(h), np.uint8))
    return {"epoch": s.epochs, "hosts": [(b.hex(), c) for b, c in hs[:KH]], "host_share": share,
            "parasites": paras, "para_share": round(float(fam.mean()), 4), "verdicts": dict(Counter(verdicts)),
            "tests": tests}


def hist_of(smps) -> list:
    return [([np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in S.get("parasites", [])],
             [np.frombuffer(bytes.fromhex(h), np.uint8) for h, _ in S.get("hosts", [])]) for S in smps]


def seeded_job(arg, epochs=(100, 500, 2000), shares=None) -> dict:
    """Seeded arm: designed H (10%), R (1%) and P (5%) in random code, mutation on; the sampler at `epochs`."""
    seed, geo = arg
    shares = shares or {"H": 0.10, "R": 0.01, "P": 0.05}
    s = F.from_programs(start(seed, shares), geo, rng=np.random.default_rng([84, 3, seed]), libmode="neighbour",
                        mutation=F.MUT)
    progs = {**{k: DESIGNED[k]() for k in shares}, "Pk": parasite(key=1)}
    traj, smp = [], []
    for e in range(max(epochs) + 1):
        if e % 50 == 0:
            traj.append({"epoch": e, **assign(s, progs)})
        if e in epochs:
            smp.append(sample(s, seed, len(smp) + 1, exp=841))
        if e < max(epochs):
            s.epoch()
    h = hist_of(smp)
    ts, tw = timeshift(h, seed * 31 + 5), timeshift_w(h, seed * 37 + 3)
    return {"seed": seed, "geometry": geo, "RQ": ts["RQ"], "Q": ts["Q"], "RQ_w": tw["RQ_w"], "W": tw["W"],
            "bytes": {t["epoch"]: {k: v for k, v in t.items() if k != "epoch"} for t in traj if t["epoch"] in epochs},
            "traj": traj, "samples": [{k: v for k, v in S.items() if k != "tests"} for S in smp]}


# ---- controls (pytest `test_bffxf_controls`, `emergence benchmark --probes`) -----------------------------
def controls() -> list[tuple[str, bool, str]]:
    out = []
    rng = np.random.default_rng(84)
    H, R, S, P, Pk = host(), resistant_host(), sham_host(), parasite(), parasite(key=1)
    # the rule
    ok = True
    for geo in ("deme64", "mixed"):
        s = F.make(geo, w=2 ** 16, rng=np.random.default_rng(4))
        b0 = np.sort(s.buf)
        for _ in range(30):
            s.epoch()
        ok &= bool((s.lens == F.L).all()) and len(s.buf) == 2 ** 16 and s.n == 1024
    s = F.make("deme64", w=2 ** 16, rng=np.random.default_rng(5), mutation=0.0, mode="noexec")
    b0 = np.sort(s.buf)
    for _ in range(5):
        s.epoch()
    ok &= bool((np.sort(s.buf) == b0).all())
    out.append(("bffxf rule: every program stays 64 bytes, program count fixed, bytes conserved (noexec)", ok, f"{ok}"))
    lib0 = H.copy()
    b = rng.integers(0, 256, 64, dtype=np.uint8)
    pcs, _ = F.run_pair(P, b, H, "neighbour")
    pcs0, _ = F.run_pair(P, b, None, "none")
    out.append(("bffxf rule: an inert program that borrows the host's code is copied into its partner (library read "
                "only); with nothing to borrow it is not", bool((pcs[1] == P).all() and (H == lib0).all()
                                                                 and (pcs0[1] == b).all()), "ok"))
    s = F.make("deme64", w=2 ** 16, rng=np.random.default_rng(41))
    perm = s.pairs()
    m = s.n // 2
    a_, b_ = perm[0:2 * m:2].astype(np.int64), perm[1:2 * m:2].astype(np.int64)
    d = np.minimum(np.abs(a_ - b_), s.n - np.abs(a_ - b_))
    out.append(("bffxf deme64: a perfect matching within blocks of 64 programs", len(set(perm.tolist())) == s.n
                and int(d.max()) < 64, f"N {s.n}, max distance {int(d.max())}"))
    bgn = [parasite(key=0) for _ in range(2000)]   # first byte 0: the host's loop skips, never copied
    near = bgn[:1000] + [H.copy() for _ in range(4)] + [P.copy()] + [H.copy() for _ in range(4)] + bgn[1000:]
    far = bgn[:1000] + [P.copy()] + bgn[1000:] + [H.copy() for _ in range(8)]
    res = []
    for pr in (near, far):
        cnt = 0
        for k in range(20):
            s = F.from_programs(pr, "deme64", rng=np.random.default_rng(300 + k), mutation=0.0)
            s.epoch()
            cnt += int((s.buf.reshape(-1, 64) == P).all(1).sum()) > 1
        res.append(cnt)
    out.append(("bffxf deme64 library is local: a parasite among hosts is copied in some epochs; one 1,000 programs "
                "from any host never", res[0] >= 3 and res[1] == 0, f"near {res[0]}/20, far {res[1]}/20"))
    # host detector
    v = {k: replication_test(x, rng)["verdict"] for k, x in (("H", H), ("H@20", host(20)), ("R", R), ("S", S))}
    out.append(("bffxf hosts positive: plain host (loop at 0 and at 20), resistant host, sham -> replicator",
                all(x == "replicator" for x in v.values()), f"{v}"))
    v = {"random": replication_test(rng.integers(0, 256, 64, dtype=np.uint8), rng)["verdict"],
         "parasite": replication_test(P, rng)["verdict"],
         "parasite, soup rule": replication_test(P, rng, "neighbour")["verdict"],
         "dead host": replication_test(dead_host(), rng)["verdict"]}
    out.append(("bffxf hosts negative/deceptive: random program, inert parasite (also under the borrowing rule in "
                "random code), dead host -> no replication", all(x == "no replication" for x in v.values()), f"{v}"))

    # parasite detector
    def pt(x, pool, seed):
        return parasite_test(x, pool, np.random.default_rng(seed), m=128, m_prod=1024)

    r = pt(P, host_pool(rng, guest=P), 1)
    out.append(("bffxf parasites positive: inert parasite at 5% among 50% hosts -> parasite", r["verdict"] == "parasite",
                _pb(r)))
    halter = F.pad(b"]")
    r1, r2 = pt(halter, host_pool(rng), 2), pt(H, host_pool(rng), 3)
    out.append(("bffxf parasites negative: a program that halts at once -> not copied; the host -> self-copier",
                r1["verdict"] == "not copied" and r2["verdict"] == "self-copier", f"{r1['verdict']}; {r2['verdict']}"))
    r1 = pt(dead_host(), host_pool(rng, junk=dead_host(), junk_share=0.2), 4)
    mk, z = maker()
    pool = host_pool(rng, hosts=0.4, junk=mk, junk_share=0.4, guest=z, guest_share=0.02)
    r2 = pt(z, pool, 6)
    out.append(("bffxf parasites deceptive: common dead host -> not parasite; product Z written by many makers -> "
                "by-product", r1["verdict"] != "parasite" and r2["verdict"] == "by-product",
                f"dead: {_pb(r1)}; Z: {_pb(r2)}"))
    r1 = pt(P, host_pool(rng, guest=P, h=R), 7)
    r2 = pt(Pk, host_pool(rng, guest=Pk, h=R), 8)
    out.append(("bffxf parasites specificity: plain parasite among resistant hosts -> not copied; key-matched -> "
                "parasite", r1["verdict"] == "not copied" and r2["verdict"] == "parasite",
                f"{r1['verdict']}; {r2['verdict']}"))
    s = F.make("deme64", w=2 ** 17, rng=np.random.default_rng(31))
    for _ in range(50):
        s.epoch()
    pool = F.programs(s)
    v = [pt(np.frombuffer(x, np.uint8), pool, 100 + i)["verdict"] for i, (x, _) in enumerate(F.top_distinct(s, 20))]
    out.append(("bffxf parasites selection-aware null: top 20 programs of a deme64 soup at epoch 50 (no hosts yet) -> "
                "0 parasites", "parasite" not in v, f"{Counter(v)}"))
    # designed programs and interaction scores
    ex = [F.screen(x, 9, 8, libmode="none", thr=100, opmin=100)[0] == 8 for x in (R, S, H)]
    q = {k: round(q_pair(P, x, 10), 3) for k, x in (("R", R), ("S", S), ("H", H))}
    qk = round(q_pair(Pk, R, 11), 3)
    w = {k: round(w_pair(P, x, 12), 3) for k, x in (("R", R), ("H", H))}
    out.append(("bffxf designed: R, S, H copy themselves exactly; R refuses the plain parasite (q 0, w 1), S and H copy "
                "it (q 1, w ~0); R copies the key-matched parasite", all(ex) and q["R"] == 0 and q["S"] == 1
                and q["H"] == 1 and qk == 1 and w["R"] == 1 and w["H"] < 0.05, f"exact {ex}, q {q}, key {qk}, w {w}"))
    # time-shift
    r1 = timeshift([([P], [H]), ([Pk], [R])], 21)
    w1 = timeshift_w([([P], [H]), ([Pk], [R])], 22)
    out.append(("bffxf time-shift positive: designed arms race -> RQ ~ 1, RQ_w > 0.5", r1["RQ"] > 0.9 and w1["RQ_w"] > 0.5,
                f"RQ {r1['RQ']}, RQ_w {w1['RQ_w']}"))
    r = timeshift([([P], [H] * 5), ([P], [H] * 4 + [R])], 22)
    out.append(("bffxf time-shift graded: 1 of 5 later hosts resistant -> RQ 0.2", abs(r["RQ"] - 0.2) < 0.03,
                f"RQ {r['RQ']}"))
    r = timeshift([([P], [H]), ([parasite(fill=0x81)], [host(20)])], 23)
    out.append(("bffxf time-shift negative: later hosts and parasites changed without resistance -> RQ 0",
                abs(r["RQ"]) < 0.01, f"RQ {r['RQ']}"))
    r = timeshift([([Pk], [R]), ([P], [H])], 24)
    out.append(("bffxf time-shift null: reversed labels -> RQ ~ -1", r["RQ"] < -0.9, f"RQ {r['RQ']}"))
    Sh = shifting_host()
    ex = F.screen(Sh, 25, 8, libmode="none", thr=100, opmin=100)[0] == 8
    r = timeshift([([P], [H]), ([P], [Sh])], 26)
    w2 = timeshift_w([([P], [H]), ([P], [Sh])], 27)
    out.append(("bffxf time-shift deceptive: a later host that copies callers 7 bytes late (exact self-copier) -> "
                "coverage RQ fooled (> 0.8), protection RQ_w not (< 0.2)", ex and r["RQ"] > 0.8 and w2["RQ_w"] < 0.2,
                f"exact {ex}, RQ {r['RQ']}, RQ_w {w2['RQ_w']}"))
    return out


if __name__ == "__main__":
    import json
    t0 = time.time()
    res = controls()
    for name, ok, det in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {det}", flush=True)
    print(json.dumps({"passed": int(sum(o for _, o, _ in res)), "total": len(res), "sec": round(time.time() - t0)}))
