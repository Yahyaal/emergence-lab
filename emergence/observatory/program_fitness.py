"""Growth-rate fitness assay for program replicators (BFF soups), J-050, D-044.

The race assays (D-042, D-043) put two replicators together and read the end counts after 96
epochs; drift from 8 starting copies each makes them insensitive (E-43, E-49). This assay measures
one component of fitness directly and with less noise: the early exponential growth rate of a
program alone among random programs.

K copies of x are put among N random programs; the soup runs without mutation. Copies are
programs >= 90% identical to x or to any of `alts` (for mirror replicators, the byte-reverse,
E-45). r = least-squares slope of ln(copies) against epoch over epochs 0..t*, where t* is the first
epoch with copies >= CAP (N/4: before saturation); a replicate that never reaches CAP within
MAX_EPOCHS gives the slope over all epochs (and is flagged); one whose copies die out gives r = 0
and is flagged. REPS replicates with independent random backgrounds; the result is the mean r and
its standard error.

Two backgrounds: "random" (random bytes, as in a soup before the transition) and "halting" (an
unmatched ']' followed by random non-instruction bytes: a partner that runs first stops at once and
never touches the candidate; a plain inert partner would not do, since the instruction pointer would
run on into the candidate's own code with the heads in the wrong place). Theory for calibration: in the early phase
almost every copy is paired with a background program and runs first with probability 1/2. If it
then copies itself with probability p and survives with probability s1 (running first) or s2
(running second), copies grow by (s1 + s2 + p) / 2 per epoch (`pair_stats`, mean-field). In the
halting background s1 = s2 = 1, so r(p) = ln(1 + p/2), r(1) = 0.405. Random partners damage a
replicator that runs second most of the time (s2 ~ 0.3 for the hand-written one), so its r there
is only ~0.14.

Known-effect ladder (benchmark section 13): `trapped(k)` is the hand-written replicator with a trap
before its copy loop, a loop that subtracts 2^k from the partner's last byte until it is zero. It
ends only if that byte is a multiple of 2^k; otherwise the program runs out of steps without
copying. Against halting partners p is known exactly (`trap_p`, about 2^-k), so r should follow
ln(1 + p/2). Controls: a
non-copier (r ~ 0, negative), the copyall rule (every program grows, including random ones: the
assay reports the random-program baseline r0 so a rule-level effect is visible, deceptive), and a
selection-aware null: two independent assays of the same program give "different" at the nominal
rate, and so do pairs of candidates drawn the same way at the same time point.

Two programs are compared with a two-sided Mann-Whitney test on their per-replicate r values.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import mannwhitneyu

from . import replicators as RP
from ..programs import bff as B

K, N, CAP, MAX_EPOCHS, REPS = 16, 4096, 1024, 40, 24


def _members(programs: np.ndarray, refs: list[np.ndarray]) -> int:
    m = np.zeros(len(programs), bool)
    for r in refs:
        m |= RP.similar(programs, r)
    return int(m.sum())


INERT = np.array([v for v in range(1, 256) if v not in B.OPS], np.uint8)


def background(rng: np.random.Generator, n: int, length: int, kind: str) -> np.ndarray:
    if kind == "random":
        return rng.integers(0, 256, (n, length), dtype=np.uint8)
    if kind == "halting":
        progs = rng.choice(INERT, (n, length))
        progs[:, 0] = ord("]")  # unmatched: a background program that runs first stops at once
        return progs
    raise ValueError(kind)


def one_rate(x: np.ndarray, rng: np.random.Generator, alts: list | None = None, mode: str = "bff",
             bg: str = "random", k: int = K, n: int = N, cap: int = CAP, max_epochs: int = MAX_EPOCHS) -> dict:
    x = np.asarray(x, np.uint8)
    refs = [x] + [np.asarray(a, np.uint8) for a in (alts or [])]
    progs = background(rng, n, len(x), bg)
    progs[rng.permutation(n)[:k]] = x
    soup = B.Soup(n=n, length=len(x), mutation=0.0, mode=mode, seed=int(rng.integers(2 ** 31)), programs=progs)
    series = [_members(soup.programs, refs)]
    while soup.epochs < max_epochs and series[-1] < cap and series[-1] > 0:
        soup.epoch()
        series.append(_members(soup.programs, refs))
    if series[-1] == 0:
        return {"r": 0.0, "series": series, "flag": "extinct"}
    t = np.arange(len(series))
    y = np.log(np.maximum(series, 1))
    r = float(np.polyfit(t, y, 1)[0]) if len(series) >= 3 else float(y[-1] - y[0])
    return {"r": r, "series": series, "flag": None if series[-1] >= cap else "no cap"}


def growth_rate(x: np.ndarray, rng: np.random.Generator, alts: list | None = None, mode: str = "bff",
                bg: str = "random", reps: int = REPS, **kw) -> dict:
    rs = [one_rate(x, rng, alts, mode, bg, **kw) for _ in range(reps)]
    r = np.array([v["r"] for v in rs])
    return {"r": round(float(r.mean()), 4), "se": round(float(r.std(ddof=1) / np.sqrt(len(r))), 4),
            "rs": [round(float(v), 4) for v in r], "flags": sum(v["flag"] is not None for v in rs),
            "extinct": sum(v["flag"] == "extinct" for v in rs)}


def compare(ga: dict, gb: dict) -> dict:
    """Two-sided Mann-Whitney test on per-replicate rates (robust to the occasional replicate whose
    copies are lost early); d = r_b - r_a (means), d_med = difference of medians."""
    p = float(mannwhitneyu(gb["rs"], ga["rs"], alternative="two-sided").pvalue)
    return {"d": round(gb["r"] - ga["r"], 4), "d_med": round(float(np.median(gb["rs"]) - np.median(ga["rs"])), 4),
            "p": p}


def theory(p: float) -> float:
    """Expected r in the halting background for copy probability p (copies are never harmed there)."""
    return float(np.log(1 + p / 2))


def trap_p(k: int) -> float:
    """Exact copy probability of trapped(k) against halting partners (last byte uniform over INERT)."""
    return float(np.mean(INERT % 2 ** k == 0))


def pair_stats(x: np.ndarray, rng: np.random.Generator, bg: str = "random", partners: int = 256,
               alts: list | None = None) -> dict:
    """Per-interaction probabilities against background partners: p = partner becomes a copy when x
    runs first; s1, s2 = x itself stays a copy when it runs first / second. Mean-field prediction of
    the early growth rate: r = ln((s1 + s2 + p) / 2)."""
    x = np.asarray(x, np.uint8)
    refs = [x] + [np.asarray(a, np.uint8) for a in (alts or [])]
    is_copy = lambda y: any((y == r).mean() >= RP.SIM for r in refs)
    p = s1 = s2 = 0
    for q in background(rng, partners, len(x), bg):
        a, b = B.interact(x, q)
        p += is_copy(b)
        s1 += is_copy(a)
        _, b2 = B.interact(q, x)
        s2 += is_copy(b2)
    p, s1, s2 = p / partners, s1 / partners, s2 / partners
    return {"p": p, "s1": s1, "s2": s2, "r_pred": float(np.log(max((s1 + s2 + p) / 2, 1e-9)))}


def trapped(k: int) -> np.ndarray:
    """The hand-written replicator with a trap on the partner's last byte (p = 2^-k, see above).
    The setup leaves head0 at byte 0; '<' moves it to the partner's last byte (tape index 2L - 1),
    the loop subtracts 2^k until zero, '>' returns head0 to 0, then the unchanged copy loop runs."""
    code = b">@\x01[}->+<]>-[-<+>]+<<" + (b"<[" + b"-" * 2 ** k + b"]>" if k > 0 else b"") + b"[.>}]"
    return np.frombuffer(code + b"\x80" * (64 - len(code)), np.uint8).copy()


def non_copier() -> np.ndarray:
    """The hand-written replicator with its copy loop's '.' replaced by an inert byte."""
    x = B.REPLICATOR.copy()
    x[bytes(x).index(b"[.>}]") + 1] = 0x80
    return x


# ---- invasion into a resident soup (E-52, J-052) ----------------------------------------------
# K_INV copies of x replace random members of a resident background (4096 programs sampled from a
# soup); the soup runs ROUNDS rounds without mutation. A control run starts from the same background
# without the injection and uses the same random pairings (same Soup seed), so programs of x's family
# that the residents make anyway are subtracted: excess e(t) = n_injected(t) - n_control(t).
# Score s = ln((e(T) + 1) / (e(0) + 1)); 0 = x spreads like the residents it replaced.
# In a soup of replicators every meeting is winner-take-all (whoever runs first overwrites the
# other), so drift is strong: reps and K_INV are larger than for growth_rate.

K_INV, N_INV, ROUNDS, REPS_INV = 64, 4096, 16, 16


def invasion(x: np.ndarray, background_programs: np.ndarray, rng: np.random.Generator, alts: list | None = None,
             k: int = K_INV, n: int = N_INV, rounds: int = ROUNDS, reps: int = REPS_INV, mode: str = "bff") -> dict:
    x = np.asarray(x, np.uint8)
    refs = [x] + [np.asarray(a, np.uint8) for a in (alts or [])]
    bgp = np.asarray(background_programs, np.uint8)
    s, ex = [], []
    for _ in range(reps):
        base = bgp[rng.choice(len(bgp), n, replace=len(bgp) < n)].copy()
        inj = base.copy()
        inj[rng.permutation(n)[:k]] = x
        seed = int(rng.integers(2 ** 31))
        A = B.Soup(n=n, length=len(x), mutation=0.0, mode=mode, seed=seed, programs=inj)
        C = B.Soup(n=n, length=len(x), mutation=0.0, mode=mode, seed=seed, programs=base)
        e0 = _members(A.programs, refs) - _members(C.programs, refs)
        for _ in range(rounds):
            A.epoch()
            C.epoch()
        eT = _members(A.programs, refs) - _members(C.programs, refs)
        ex.append([e0, eT])
        s.append(float(np.log((max(eT, 0) + 1) / (max(e0, 0) + 1))))
    s_ = np.array(s)
    return {"s": round(float(s_.mean()), 4), "se": round(float(s_.std(ddof=1) / np.sqrt(len(s_))), 4),
            "ss": [round(v, 4) for v in s], "excess": ex}


def resident_copiers(rng: np.random.Generator, n: int, q_odd: float) -> np.ndarray:
    """Calibration background: n hand-written copiers with redrawn inert tails (each its own family);
    a share q_odd end in an odd byte, the rest in an even one. Against them trapped(1) copies with
    probability exactly 1 - q_odd and is otherwise identical to trapped(0)."""
    out = np.empty((n, 64), np.uint8)
    odd, even = INERT[INERT % 2 == 1], INERT[INERT % 2 == 0]
    code = bytes(B.REPLICATOR).index(b"\x80")
    for i in range(n):
        y = B.REPLICATOR.copy()
        y[code:] = rng.choice(INERT, 64 - code)
        y[63] = rng.choice(odd if rng.random() < q_odd else even)
        out[i] = y
    return out
