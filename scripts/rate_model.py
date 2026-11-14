"""E-76 (exploratory, outcomes known): one origin rate per rule.

Model: each rule has one rate lambda = replicator origins per pair run. A soup of N programs runs N/2 pair runs
per round, so the wait to a jump is exponential with hazard lambda * N/2 per round. This script fits that model
to soup data that already exist (no soup or census is run) and compares it with the fresh-pair product rate R_P.

Inputs (all committed; fields used):
  2026-11-13-e75-phase3.json    soups[].{code, T}; summary.rules[].{code, rule, group}
  2026-11-13-e75-phase4.json    soups[].{code, T}; summary.rules[].{code, rule, group, pool}
  2026-11-14-e75-phase7.json    soups[].{code, T}; selected[].{code, rule, group, jump, R_P, D_T};
                                screened[].{code, stage1.pairs, stage2.pairs, products}
  2026-11-13-e75-products.json  rules[].{code, pairs, informative, R_P, D_T}
  2026-11-08-e50-soup-size.json soups[].{n, seed, run_epochs, exposure, transitioned, replicator}
  2026-11-08-e54-long-soups.json summary.jumped, summary.new_soups_jumped (12 new 2^16 soups, seeds 5400-5411)
  E-40/E-41 2^14 arm: exposures as in scripts/bff_sizes.py (E41): 10 x 48,000 censored, events at 43,250 and 32,000.

SUBLEQ jump times. T is the checkpoint (every 50 rounds) at which >= 1 inheritor was first seen among the top
programs, confirmed by >= 10 inheritors 1,000 rounds later (sq_phase3.soup_job); so T <= 15,000 and a soup with no
jump is censored at 15,000 rounds (not 16,000). The model is fitted with interval censoring: the origin lies in
(T - 50 - L, T - L], where L is the lag from origin to detection. Primary L = 0; sensitivity L = 16 (median
origin-to-establishment lag, J-083) and L = -100 (T early by up to ~100 rounds because null all-zero replicators
came first, J-083). Rules whose soups all jump at the first checkpoint have an unbounded MLE (lower bound only).

    PYTHONPATH=. python scripts/rate_model.py
"""
from __future__ import annotations

import argparse
import json
import math

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import chi2, fisher_exact

D = "docs/data/experiments/"
PAIRS_SQ = 2 ** 14 // 2  # pair runs per round in SUBLEQ soups
CENSOR_SQ = 15_000
EVERY = 50
LAGS = {"primary (L=0)": 0, "establishment lag (L=16)": 16, "null-early (L=-100)": -100}
PER = 1e8  # rates per 10^8 pair runs
SEED = 2026
NBOOT = 4000
AGE_BINS = [0, 500, 2000, CENSOR_SQ]
LR_MAX = 5.0  # per-round hazard cap (all soups jump before the first checkpoint)
LOGR = np.round(np.arange(-4, 5.0001, 0.02), 2)  # log10 grid for soup/R_P ratios
Q95 = chi2.ppf(0.95, 1)


def cond_of(rule: str) -> str:
    return "always" if "jalways" in rule else ("<=0" if "j<=0" in rule else "<0")


def garwood(k: int, expo: float) -> tuple[float, float]:
    """Exact 95% Poisson interval (k = 0: one-sided 95% upper bound)."""
    if k == 0:
        return 0.0, -math.log(0.05) / expo
    return chi2.ppf(0.025, 2 * k) / 2 / expo, chi2.ppf(0.975, 2 * k + 2) / 2 / expo


def clean(x):
    if isinstance(x, (float, np.floating)):
        x = float(x)
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return float(f"{x:.4g}")
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, np.integer):
        return int(x)
    return x


# ---------------------------------------------------------------- interval-censored exponential

def prep(T: list, C: int = CENSOR_SQ, L: float = 0) -> tuple[np.ndarray, np.ndarray, float]:
    """Interval ends (a, b] of origins for soups jumping by C, and total censored rounds."""
    ev = [t for t in T if t is not None and t <= C]
    a = np.array([max(t - EVERY - L, 0.0) for t in ev])
    b = np.array([max(t - L, 1e-6) for t in ev])
    cens = (len(T) - len(ev)) * max(C - L, 0.0)
    return a, b, cens


def ll_round(lr: float, a, b, cens) -> float:
    if lr <= 0:
        return 0.0 if len(a) == 0 else -np.inf
    return float((-lr * a + np.log(-np.expm1(-lr * (b - a)))).sum() - lr * cens)


def fit_rate(T: list, C: int = CENSOR_SQ, L: float = 0) -> dict:
    """MLE of the per-round hazard with a 95% profile-likelihood interval; returned per 10^8 pair runs."""
    a, b, cens = prep(T, C, L)
    k = len(a)
    if k == 0:
        hi = -math.log(0.05) / cens
        return {"k": 0, "rate": 0.0, "lo": 0.0, "hi": hi / PAIRS_SQ * PER, "saturated": False}
    f = lambda x: -ll_round(math.exp(x), a, b, cens)  # noqa: E731
    sat = bool((a == 0).all() and cens == 0)  # every soup jumped by its first checkpoint: likelihood rises without bound
    r = minimize_scalar(f, bounds=(math.log(1e-9), math.log(LR_MAX)), method="bounded", options={"xatol": 1e-8})
    if sat:
        r.x, r.fun = math.log(LR_MAX), f(math.log(LR_MAX))
    lmax = -r.fun
    g = lambda x: 2 * (lmax + f(x)) - Q95  # noqa: E731
    lo = math.exp(brentq(g, math.log(1e-12), r.x)) if g(math.log(1e-12)) > 0 else 0.0
    hi = math.inf if sat or g(math.log(LR_MAX)) < 0 else math.exp(brentq(g, r.x, math.log(LR_MAX)))
    s = PER / PAIRS_SQ
    return {"k": k, "rate": math.inf if sat else math.exp(r.x) * s, "lo": lo * s, "hi": hi * s, "saturated": bool(sat),
            "mle_round": math.exp(r.x)}


def profile_ratio(T: list, m: int, P: float, C: int = CENSOR_SQ, L: float = 0) -> np.ndarray:
    """Profile log-likelihood of rho = soup rate / fresh product rate on LOGR (max over the fresh rate mu)."""
    a, b, cens = prep(T, C, L)
    out = np.empty(len(LOGR))
    for i, lg in enumerate(LOGR):
        rho = 10.0 ** lg

        def f(x):
            mu = math.exp(x)
            lr = min(rho * mu * PAIRS_SQ, LR_MAX)
            return -(ll_round(lr, a, b, cens) + (m * math.log(mu * P) if m else 0.0) - mu * P)
        r = minimize_scalar(f, bounds=(math.log(1e-16), math.log(1e-3)), method="bounded", options={"xatol": 1e-6})
        out[i] = -r.fun
    return out


def ci_from_profile(pr: np.ndarray) -> dict:
    j = int(pr.argmax())
    ok = LOGR[2 * (pr.max() - pr) <= Q95]
    lo = -math.inf if ok.min() <= LOGR[0] else ok.min()
    hi = math.inf if ok.max() >= LOGR[-1] else ok.max()
    flat = pr.max() - pr.min() < 1e-6
    est = None if flat else (0.0 if j == 0 else (math.inf if j == len(LOGR) - 1 else 10 ** LOGR[j]))
    return {"ratio": est, "lo": 0.0 if lo == -math.inf else 10 ** lo, "hi": math.inf if hi == math.inf else 10 ** hi}


# ---------------------------------------------------------------- data

def load_subleq() -> list[dict]:
    rules = {}
    p3 = json.load(open(D + "2026-11-13-e75-phase3.json"))
    for r in p3["summary"]["rules"]:
        rules[r["code"]] = {"code": r["code"], "rule": r["rule"], "phase": 3, "pool": "always", "group": r["group"]}
    p4 = json.load(open(D + "2026-11-13-e75-phase4.json"))
    for r in p4["summary"]["rules"]:
        rules[r["code"]] = {"code": r["code"], "rule": r["rule"], "phase": 4, "pool": r["pool"], "group": r["group"]}
    p7 = json.load(open(D + "2026-11-14-e75-phase7.json"))
    scr = {s["code"]: s for s in p7["screened"]}
    for r in p7["selected"]:
        s = scr[r["code"]]
        rules[r["code"]] = {"code": r["code"], "rule": r["rule"], "phase": 7, "pool": r["jump"], "group": r["group"],
                            "products": int(s["products"]), "census_pairs": s["stage1"]["pairs"] + s["stage2"]["pairs"],
                            "R_P": r["R_P"], "D_T": r["D_T"]}
    for r in json.load(open(D + "2026-11-13-e75-products.json"))["rules"]:
        rules[r["code"]].update(products=int(r["informative"]), census_pairs=r["pairs"], R_P=r["R_P"], D_T=r["D_T"])
    for d in (p3, p4, p7):
        for s in d["soups"]:
            rules[s["code"]].setdefault("T", []).append(s["T"])
    out = list(rules.values())
    for r in out:
        r["cond"] = cond_of(r["rule"])
        r["jumped"] = sum(t is not None for t in r["T"])
        r["soups"] = len(r["T"])
        assert abs(r["R_P"] - r["products"] / r["census_pairs"] * PER) < 1e-6, r["rule"]
        lo, hi = garwood(r["products"], r["census_pairs"])
        r["R_P_ci"] = [lo * PER, hi * PER]
    return out


# ---------------------------------------------------------------- step 1

def step1(rules: list[dict]) -> dict:
    for r in rules:
        r["fits"] = {name: fit_rate(r["T"], L=L) for name, L in LAGS.items()}
        r["soup"] = r["fits"]["primary (L=0)"]
        k = r["jumped"]
        rounds = sum((max(t - 25, 1) if t is not None else CENSOR_SQ) for t in r["T"])
        r["simple_T25"] = k / (rounds * PAIRS_SQ) * PER  # events / exposure with T - 25, for comparison
    mv = []
    for r in rules:
        rr = [f["rate"] for f in r["fits"].values()]
        if r["jumped"] and all(math.isfinite(x) for x in rr):
            mv.append(max(rr) / min(rr))
    return {"rules": len(rules), "rules_jumped": sum(r["jumped"] > 0 for r in rules),
            "saturated_rules": [r["rule"] for r in rules if r["soup"]["saturated"]],
            "rate_change_across_lags_median": float(np.median(mv)), "rate_change_across_lags_max": float(max(mv)),
            "rules_changed_gt_20pct": int(sum(m > 1.2 for m in mv))}


# ---------------------------------------------------------------- step 2

def km(x: np.ndarray, d: np.ndarray):
    o = np.argsort(x, kind="stable")
    x, d = x[o], d[o]
    at = len(x) - np.arange(len(x))
    return x, d, np.cumprod(np.where(d == 1, 1 - 1 / at, 1.0))


def ks_stat(x: np.ndarray, d: np.ndarray) -> float:
    xs, ds, s = km(x, d)
    sb = np.r_[1.0, s[:-1]]
    m = ds == 1
    e = np.exp(-xs[m])
    return float(max(np.abs(s[m] - e).max(), np.abs(sb[m] - e).max()))


def sim_T(rng, lr: float, n: int) -> np.ndarray:
    t = rng.exponential(1 / lr, n)
    T = EVERY * np.ceil(t / EVERY)
    return np.where(T <= CENSOR_SQ, T, np.nan)


def standardised(groups: list[np.ndarray]):
    """Times at risk (T - 25 or 15,000) scaled by each rule's events/exposure estimate."""
    xs, ds = [], []
    for T in groups:
        d = ~np.isnan(T)
        t = np.where(d, np.maximum(T - 25, 1), CENSOR_SQ)
        xs.append(d.sum() / t.sum() * t)
        ds.append(d.astype(int))
    return np.concatenate(xs), np.concatenate(ds)


def as_list(T: np.ndarray) -> list:
    return [None if np.isnan(x) else float(x) for x in T]


def step2(rules: list[dict]) -> dict:
    rng = np.random.default_rng(SEED)
    # (a) CV of T within rules that jumped in all 6 soups; null: exponential at the rule's MLE, checkpointed
    full = [r for r in rules if r["jumped"] == r["soups"]]
    per_rule, obs_cv, null_cv = [], [], []
    for r in full:
        T = np.array(r["T"], float)
        lr = min(r["soup"]["mle_round"], LR_MAX)
        sims = []
        while len(sims) < NBOOT:
            s = sim_T(rng, lr, len(T))
            if not np.isnan(s).any():
                sims.append(s.std(ddof=1) / s.mean())
        sims = np.array(sims)
        cv = T.std(ddof=1) / T.mean()
        obs_cv.append(cv)
        null_cv.append(sims)
        per_rule.append({"rule": r["rule"], "T": r["T"], "cv": cv, "cv_null_median": float(np.median(sims)),
                         "p_low": float((sims <= cv + 1e-12).mean()), "p_high": float((sims >= cv - 1e-12).mean())})
    m_obs, m_null = float(np.mean(obs_cv)), np.mean(np.array(null_cv), axis=0)
    n_ext = sum((p["p_low"] < 0.05 and p["cv"] > 0) or p["p_high"] < 0.05 for p in per_rule)
    p_ext = float(sum(math.comb(len(full), i) * 0.1 ** i * 0.9 ** (len(full) - i) for i in range(n_ext, len(full) + 1)))
    cv_part = {"rules": len(full), "mean_cv_observed": m_obs, "mean_cv_null_median": float(np.median(m_null)),
               "mean_cv_null_90pct": [float(np.quantile(m_null, 0.05)), float(np.quantile(m_null, 0.95))],
               "p_lower": float((m_null <= m_obs).mean()), "p_higher": float((m_null >= m_obs).mean()),
               "rules_too_regular_p_lt_0.05": [p["rule"] for p in per_rule if p["p_low"] < 0.05 and p["cv"] > 0],
               "rules_too_variable_p_lt_0.05": [p["rule"] for p in per_rule if p["p_high"] < 0.05],
               "rules_outside_either_tail": n_ext, "expected_by_chance": 0.1 * len(full),
               "p_this_many_binomial": p_ext,
               "per_rule": per_rule}
    # (b) pooled standardised times of rules with >= 2 jumps (censoring included) against Exp(1); parametric bootstrap
    multi = [r for r in rules if r["jumped"] >= 2]
    groups = [np.array([np.nan if t is None else t for t in r["T"]], float) for r in multi]
    x, d = standardised(groups)
    obs = ks_stat(x, d)
    boots = []
    for _ in range(NBOOT):
        g2 = []
        for r, T in zip(multi, groups):
            lr = min(r["soup"]["mle_round"], LR_MAX)
            s = sim_T(rng, lr, len(T))
            while (~np.isnan(s)).sum() < 2:  # same selection as the data: rules with >= 2 jumps
                s = sim_T(rng, lr, len(T))
            g2.append(s)
        boots.append(ks_stat(*standardised(g2)))
    boots = np.array(boots)
    xs, ds, s = km(x, d)
    surv = {str(g): {"km": float(s[xs <= g][-1]) if (xs <= g).any() else 1.0, "exp": math.exp(-g)}
            for g in (0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0)}
    # (c) one common detection lag / delay L in [0, 49] (bounded by T = 50 jumps), per-rule rates profiled out
    def tot(L):
        return sum(ll_round(fit_rate(r["T"], L=L).get("mle_round", 0.0), *prep(r["T"], L=L)) for r in multi)
    Ls = np.arange(0, 50, 1.0)
    llv = np.array([tot(L) for L in Ls])
    delay = {"grid": "0-49 rounds", "best_L": float(Ls[llv.argmax()]), "lr_vs_L0": float(2 * (llv.max() - llv[0])),
             "note": "a delay longer than 50 rounds is excluded wherever soups jump at T = 50"}
    first = sum(t == 50 for r in rules for t in r["T"])
    return {"cv_full_rules": cv_part,
            "pooled": {"rules": len(multi), "soups": int(len(x)), "events": int(d.sum()), "ks_observed": obs,
                       "ks_null_median": float(np.median(boots)), "ks_null_95pct": float(np.quantile(boots, 0.95)),
                       "p": float((boots >= obs).mean()), "survival_at": surv},
            "common_lag": delay, "jumps_at_first_checkpoint": first}


# ---------------------------------------------------------------- step 3

def age_counts(T: list, bins: list, shift: float):
    nb = len(bins) - 1
    ev, ex = np.zeros(nb), np.zeros(nb)
    for x in T:
        t = CENSOR_SQ if x is None else max(x + shift, 1)
        for b in range(nb):
            ex[b] += max(0.0, min(t, bins[b + 1]) - bins[b])
        if x is not None:
            ev[min(np.searchsorted(bins, t, side="right") - 1, nb - 1)] += 1
    return ev, ex


def age_fit(rules: list[dict], shift: float) -> dict:
    """Piecewise-constant hazard lambda_r * theta_b, conditional on each rule's total jumps (rules with >= 1 jump)."""
    jr = [r for r in rules if r["jumped"]]
    EV, EX = map(np.array, zip(*[age_counts(r["T"], AGE_BINS, shift) for r in jr]))

    def ll(th):
        w = EX * th
        p = w / w.sum(1, keepdims=True)
        return float((EV * np.log(np.where(EV > 0, p, 1.0))).sum())
    g = np.round(np.arange(-2.5, 2.5001, 0.02), 2)
    surf = np.array([[ll(np.array([1.0, 10 ** u, 10 ** v])) for v in g] for u in g])
    i, j = np.unravel_index(surf.argmax(), surf.shape)
    l1 = surf.max()
    th = []
    for name, prof in (("500-2000", surf.max(1)), ("2000-15000", surf.max(0))):
        ok = g[2 * (l1 - prof) <= Q95]
        th.append({"bin": name, "theta_vs_0_500": 10 ** g[i if name == "500-2000" else j],
                   "ci95": [10 ** ok.min(), 10 ** ok.max()]})
    lr = 2 * (l1 - ll(np.ones(3)))
    return {"shift": shift, "rules": len(jr), "events_per_bin": EV.sum(0).tolist(), "soup_rounds_per_bin": EX.sum(0).tolist(),
            "thetas": th, "lr_constant": float(lr), "p": float(chi2.sf(lr, 2))}


def step3(rules: list[dict]) -> dict:
    for r in rules:
        r["prof"] = profile_ratio(r["T"], r["products"], r["census_pairs"])
        r["prof_early"] = profile_ratio(r["T"], r["products"], r["census_pairs"], C=500)
        r["prof_150"] = profile_ratio(r["T"], r["products"], r["census_pairs"], C=150)
        r["ratio"] = ci_from_profile(r["prof"])
    per_rule = [{"rule": r["rule"], "phase": r["phase"], "group": r["group"], "cond": r["cond"],
                 "jumped": f"{r['jumped']}/{r['soups']}", "T": r["T"], "soup_rate": r["soup"]["rate"],
                 "soup_ci": [r["soup"]["lo"], r["soup"]["hi"]], "saturated": r["soup"]["saturated"],
                 "soup_rate_by_lag": {k: v["rate"] for k, v in r["fits"].items()}, "simple_T25_rate": r["simple_T25"],
                 "R_P": r["R_P"], "R_P_ci": r["R_P_ci"], "products": r["products"], "D_T": r["D_T"],
                 "ratio_soup_over_RP": r["ratio"]} for r in rules]
    by = {}
    for c in ("always", "<=0", "<0"):
        rs = [r for r in rules if r["cond"] == c]
        inf = [r for r in rs if r["jumped"] or r["products"]]
        res = {"rules": len(rs), "informative_rules": len(inf), "soups_jumped": sum(r["jumped"] for r in rs),
               "products": sum(r["products"] for r in rs)}
        for lab, key, C in (("all_rounds", "prof", CENSOR_SQ), ("first_500_rounds", "prof_early", 500),
                            ("first_150_rounds", "prof_150", 150)):
            tot = sum(r[key] for r in inf)
            common = ci_from_profile(tot)
            het = 2 * (sum(r[key].max() for r in inf) - tot.max())
            res[lab] = {"soup_jumps_in_window": sum(t is not None and t <= C for r in rs for t in r["T"]),
                        "common_ratio": common, "heterogeneity_lr": float(het), "df": len(inf) - 1,
                        "p_common_ratio_adequate": float(chi2.sf(het, len(inf) - 1))}
        both = [r["ratio"]["ratio"] for r in rs if r["jumped"] and r["products"] and r["ratio"]["ratio"] is not None]
        res["median_ratio_rules_with_jumps_and_products"] = float(np.median(both)) if both else None
        res["n_rules_with_both"] = len(both)
        res["rules_ratio_ci_above_1"] = [r["rule"] for r in rs if r["ratio"]["lo"] > 1]
        res["rules_ratio_ci_below_1"] = [r["rule"] for r in rs if r["ratio"]["hi"] < 1]
        res["rules_ratio_ci_above_10"] = [r["rule"] for r in rs if r["ratio"]["lo"] > 10]
        res["zero_product_rules_jumping_ge4"] = [
            {"rule": r["rule"], "phase": r["phase"], "jumped": r["jumped"], "median_T": float(np.median([t for t in r["T"] if t])),
             "soup_rate": r["soup"]["rate"], "soup_ci": [r["soup"]["lo"], r["soup"]["hi"]],
             "ratio_lower_95": r["ratio"]["lo"]} for r in rs if r["products"] == 0 and r["jumped"] >= 4]
        by[c] = res
    ages = {name: age_fit(rules, s) for name, s in (("primary (T-25)", -25), ("earliest (T-66)", -66), ("null-early (T+100)", 100))}
    for c in ("always", "<=0", "<0"):
        ages[f"primary, {c} only"] = age_fit([r for r in rules if r["cond"] == c], -25)
    # J-084's claim about the six phase-3/4 zero-product rules that jump in >= 4 soups
    six = [r for r in rules if r["phase"] in (3, 4) and r["products"] == 0 and r["jumped"] >= 4]
    Ts = sorted(t for r in six for t in r["T"] if t is not None)
    claim = {"rules": [r["rule"] for r in six], "jumped_soups": len(Ts), "median_T": float(np.median(Ts)), "min_T": Ts[0],
             "R_P_upper_95_per_1e8": garwood(0, 3e8)[1] * PER,
             "implied_mean_wait_rounds_at_R_P_upper_95": 1 / (garwood(0, 3e8)[1] * PAIRS_SQ),
             "implied_mean_wait_rounds_at_one_product": 3e8 / PAIRS_SQ,
             "ratio_lower_95_by_rule": {r["rule"]: r["ratio"]["lo"] for r in six}}
    return {"per_rule": per_rule, "by_condition": by, "age": ages, "j084_zero_product_claim": claim}


# ---------------------------------------------------------------- step 4

def step4(rules: list[dict]) -> dict:
    tests = {"phase 3": (3, "always", "HIGH", "LOW"), "phase 4 pool A": (4, "A", "HIGH", "LOW"),
             "phase 4 pool B": (4, "B", "HIGH", "LOW"), "phase 7": (7, None, "HIGH", "ZERO")}
    out = {}
    for name, (ph, pool, g1, g2) in tests.items():
        rs = [r for r in rules if r["phase"] == ph and (pool is None or r["pool"] == pool)]
        a = [r for r in rs if r["group"] == g1]
        b = [r for r in rs if r["group"] == g2]
        res = {"groups": [g1, g2], "rules": [len(a), len(b)]}
        for lab, f in (("any_soup_jumped", lambda r: r["jumped"] >= 1), ("ge4_of_6", lambda r: r["jumped"] >= 4)):
            x, y = sum(map(f, a)), sum(map(f, b))
            res[lab] = {"rules": [x, y], "p_one_sided": fisher_exact([[x, len(a) - x], [y, len(b) - y]], alternative="greater")[1]}
        sx, sy = sum(r["jumped"] for r in a), sum(r["jumped"] for r in b)
        na, nb = sum(r["soups"] for r in a), sum(r["soups"] for r in b)
        res["soup_level"] = {"jumped": [sx, sy], "of": [na, nb],
                             "p_one_sided": fisher_exact([[sx, na - sx], [sy, nb - sy]], alternative="greater")[1]}
        out[name] = res
    return out


# ---------------------------------------------------------------- step 5

def bff_rows() -> dict:
    e50 = json.load(open(D + "2026-11-08-e50-soup-size.json"))
    e54 = json.load(open(D + "2026-11-08-e54-long-soups.json"))
    arm14 = [(2 ** 14, 48000, 0)] * 10 + [(2 ** 14, 43250, 1), (2 ** 14, 32000, 1)]  # = bff_sizes.E41
    pre = arm14 + [(s["n"], s["exposure"], int(s["transitioned"])) for s in e50["soups"]]
    ver = list(arm14)
    for s in e50["soups"]:
        if s["seed"] == 5308:  # HOE spike at 11,750, real jump at 12,500 (J-054; bff_long.CONTINUE)
            ver.append((s["n"], 12500, 1))
        elif s["transitioned"] and not s["replicator"]:  # one-checkpoint spike, no replicator: censored where stopped
            ver.append((s["n"], s["run_epochs"], 0))
        else:
            ver.append((s["n"], s["exposure"], int(s["transitioned"])))
    jumped = {int(k): v for k, v in e54["summary"]["jumped"].items()}
    new = [(2 ** 16, jumped[s], 1) if s in jumped else (2 ** 16, 23500, 0) for s in range(5400, 5412)]
    assert sum(d for *_, d in new) == e54["summary"]["new_soups_jumped"]
    return {"pre-registered HOE (E-50 as exported)": pre, "verified replicator (D-045 reading)": ver,
            "verified + E-54 new 2^16 soups": ver + new}


def _pois_cdf(k: int, mu: float) -> float:
    return sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(k + 1))


def bff_fit(rows: list) -> dict:
    n = np.array([r[0] for r in rows], float)
    t = np.array([r[1] for r in rows], float)
    d = np.array([r[2] for r in rows], float)
    expo = t * n / 2
    k, E = int(d.sum()), expo.sum()
    lo, hi = garwood(k, E)
    arms, ll_arms = {}, 0.0
    for a in sorted(set(n)):
        m = n == a
        ka, ea = int(d[m].sum()), expo[m].sum()
        la, ha = garwood(ka, ea)
        mu = k / E * ea
        arms[str(int(a))] = {"soups": int(m.sum()), "events": ka, "pair_runs": ea, "rate": ka / ea * PER,
                             "ci95": [la * PER, ha * PER], "expected_events_common_rate": mu,
                             "p_this_few_or_fewer": _pois_cdf(ka, mu), "p_this_many_or_more": 1 - _pois_cdf(ka - 1, mu) if ka else 1.0}
        if ka:
            ll_arms += ka * math.log(ka / ea) - ka
    lr = 2 * (ll_arms - (k * math.log(k / E) - k))
    x = np.log2(n / 2 ** 14)

    def nll(b):
        w = t * 2.0 ** (b * x)
        l0 = d.sum() / w.sum()
        return -(d * np.log(l0 * 2.0 ** (b * x))).sum() + l0 * w.sum()
    rb = minimize_scalar(nll, bounds=(-6, 8), method="bounded")
    g = np.linspace(-6, 8, 2801)
    ok = [v for v in g if 2 * (nll(v) - rb.fun) <= Q95]
    lr1 = 2 * (nll(1.0) - rb.fun)
    return {"soups": len(rows), "events": k, "pair_runs": E, "rate_per_1e8": k / E * PER, "ci95": [lo * PER, hi * PER],
            "arms": arms, "lr_common_vs_per_arm": lr, "df": len(arms) - 1, "p_common_rate_adequate": float(chi2.sf(lr, len(arms) - 1)),
            "beta_free": {"beta": float(rb.x), "ci95": [min(ok), max(ok)], "p_beta_eq_1": float(chi2.sf(lr1, 1))}}


# ---------------------------------------------------------------- figure

def figure(rules: list[dict], path: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 130, "savefig.bbox": "tight", "axes.spines.top": False, "axes.spines.right": False})
    style = {"always": ("#2f6db5", "o", "jump always"), "<=0": ("#d9822b", "s", "jump ≤ 0"), "<0": ("#3a9a5b", "^", "jump < 0")}
    lim = PER / 3e8  # one product in 3·10^8 pairs
    lo_y, hi_y, top = 0.02, 3000, 1500
    fig, ax = plt.subplots(figsize=(6.6, 5.6))
    for c, (col, mk, lab) in style.items():
        first = True
        for r in rules:
            if r["cond"] != c:
                continue
            s = r["soup"]
            x = r["R_P"] if r["products"] else lim
            y = top if s["saturated"] else (s["rate"] if s["k"] else s["hi"])
            filled = r["products"] > 0 and s["k"] > 0
            ax.scatter(x, y, s=34, marker=mk, color=col if filled else "white", edgecolor=col, lw=1.2, zorder=3,
                       label=lab if first else None)
            first = False
            if s["saturated"]:
                ax.annotate("", xy=(x, y * 1.8), xytext=(x, s["lo"]), arrowprops=dict(arrowstyle="->", color=col, lw=0.8))
            elif s["k"]:
                ax.plot([x, x], [max(s["lo"], lo_y), s["hi"]], color=col, lw=0.7, alpha=0.6)
            else:
                ax.annotate("", xy=(x, y / 2.2), xytext=(x, y), arrowprops=dict(arrowstyle="->", color=col, lw=0.8))
            if r["products"]:
                ax.plot(r["R_P_ci"], [y, y], color=col, lw=0.7, alpha=0.6)
            else:
                ax.annotate("", xy=(x / 2.2, y), xytext=(x, y), arrowprops=dict(arrowstyle="->", color=col, lw=0.8))
    none = sum(1 for r in rules if not r["products"] and not r["soup"]["k"])
    y0 = garwood(0, 6 * CENSOR_SQ * PAIRS_SQ)[1] * PER  # upper bound for 0 jumps in 6 soups
    ax.annotate(f"{none} rules: no jump and no product\n(all at this point)", xy=(lim, y0), xytext=(1.5, 0.06), fontsize=7,
                color="#555a63", arrowprops=dict(arrowstyle="-", color="#8a8f98", lw=0.6))
    v = np.array([0.05, hi_y])
    ax.plot(v, v, color="#8a8f98", lw=0.9, ls="--")
    ax.text(900, 450, "y = x", color="#8a8f98", fontsize=8)
    ax.axvline(lim, color="#8a8f98", lw=0.6, ls=":")
    ax.text(lim * 1.08, 0.025, "census limit\n(1 in 3·10⁸ pairs)", fontsize=7, color="#8a8f98")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.05, hi_y)
    ax.set_ylim(lo_y, hi_y * 2)
    ax.set_xlabel("fresh-pair product rate R_P (per 10⁸ pairs)")
    ax.set_ylabel("soup origin rate (per 10⁸ pair runs, interval-censored MLE)")
    ax.set_title("Soup rate vs fresh-pair rate, 79 SUBLEQ rules (exploratory)\n"
                 "open: no jump (upper bound) or no product (census limit); top row: every soup jumped by round 50",
                 fontsize=8.5)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.savefig(path)
    print("saved", path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=D + "2026-11-14-rate-model.json")
    ap.add_argument("--fig", default="docs/assets/report/rate-model.png")
    a = ap.parse_args()
    rules = load_subleq()
    s1 = step1(rules)
    s2 = step2(rules)
    s3 = step3(rules)
    s4 = step4(rules)
    s5 = {k: bff_fit(v) for k, v in bff_rows().items()}
    out = {"experiment": "E-76", "status": "exploratory re-analysis; outcomes known; no new runs",
           "model": "time to jump ~ Exp(lambda * N/2 per round); rates per 10^8 pair runs",
           "conventions": {"pairs_per_round_subleq": PAIRS_SQ, "censor_round": CENSOR_SQ, "checkpoint": EVERY,
                           "origin_interval": "(T - 50 - L, T - L]", "lags": LAGS, "rate_ci": "95% profile likelihood; zero jumps: one-sided 95% upper",
                           "R_P_ci": "exact Poisson (Garwood)", "ratio_ci": "95% profile likelihood, fresh rate profiled out, grid 0.02 in log10",
                           "seed": SEED, "nboot": NBOOT},
           "step1": s1, "step2_fit": s2, "step3_aging": s3, "step4_rule_level": s4, "step5_bff": s5}
    with open(a.out, "w") as f:
        json.dump(clean(out), f, indent=1)
    print("saved", a.out)
    figure(rules, a.fig)
    print("step1", clean(s1))
    print("step2 CV", clean({k: v for k, v in s2["cv_full_rules"].items() if k != "per_rule"}))
    print("step2 pooled", clean(s2["pooled"]), "lag", clean(s2["common_lag"]), "T=50 jumps", s2["jumps_at_first_checkpoint"])
    for c, v in s3["by_condition"].items():
        print("step3", c, clean(v))
    for k, v in s3["age"].items():
        print("step3 age", k, clean(v))
    print("step3 J-084 claim", clean(s3["j084_zero_product_claim"]))
    for k, v in s4.items():
        print("step4", k, clean(v))
    for k, v in s5.items():
        print("step5", k, clean({kk: vv for kk, vv in v.items()}))


if __name__ == "__main__":
    main()
