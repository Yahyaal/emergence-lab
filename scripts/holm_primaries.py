"""E-79 (analysis of existing results, no simulation): multiple-comparison correction across the pre-registered
primaries of the 45 experiments in docs/paper.md Appendix B (D-067; pre-registration docs/data/e79-preregistration.md).

Input:  docs/data/e79-primaries.json   one record per registered primary (family = in | excluded | predicted_null),
                                       each p value traced to a committed file and line.
Output: docs/data/experiments/2026-11-16-e79-holm.json (the E-79 result, 42 p values), and the tables on stdout.
        When later primaries are added to e79-primaries.json (E-80: 44 p values), write to a new file with --out
        (e.g. docs/data/experiments/2026-11-17-e80-holm44.json) so the E-79 export is not overwritten.

Methods (fixed in the pre-registration):
  primary     Holm step-down, family-wise alpha 0.05, over the 42 p values in the family;
  secondary   Benjamini-Hochberg, q = 0.05;
  sens. (a)   rule-level p values (D-063) where the registered unit was the world or soup and a committed rule-level
              test of the same contrast exists (E-14, E-19, E-75 phases 3, 4, 7; `ge4_of_6` for the E-75 phases);
  sens. (b)   Holm within each thread;
  sens. (c)   exploratory: (a) plus rule-level one-sided Fisher tests recomputed from committed per-rule soup outcomes
              for the soup-level Fisher primaries that compare groups of rules (E-60 to E-65, E-68, E-70).

    PYTHONPATH=. python scripts/holm_primaries.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALPHA = 0.05
SRC = "docs/data/e79-primaries.json"
OUT = "docs/data/experiments/2026-11-16-e79-holm.json"


def holm(p: list[float]) -> list[float]:
    """Holm-adjusted p values, in input order: sort ascending, adj_(i) = max_{j<=i} min(1, (m - j + 1) p_(j))."""
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (m - rank) * p[i]))
        adj[i] = run
    return adj


def bh(p: list[float]) -> list[float]:
    """Benjamini-Hochberg adjusted p values, in input order: adj_(i) = min_{j>=i} min(1, m p_(j) / j)."""
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    adj = [0.0] * m
    run = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        run = min(run, min(1.0, m * p[i] / (rank + 1)))
        adj[i] = run
    return adj


def holm_reject(p: list[float], alpha: float = ALPHA) -> list[bool]:
    """Independent check: Holm's sequential procedure as a rejection rule (reject p_(k) <= alpha / (m - k + 1)
    while every smaller p was rejected)."""
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    rej = [False] * m
    for k, i in enumerate(order):
        if p[i] <= alpha / (m - k):
            rej[i] = True
        else:
            break
    return rej


def check_against_libraries(p: list[float]) -> dict:
    out = {}
    # Holm: the adjusted values must reproduce the sequential rejection rule at every alpha that matters.
    adj = holm(p)
    alphas = sorted(set([0.001, 0.005, 0.01, 0.025, 0.05, 0.1] + [a * 1.000001 for a in adj if a < 0.99]))
    out["holm_vs_sequential_rule"] = all(
        [a_i <= a for a_i in adj] == holm_reject(p, a) for a in alphas)
    try:
        from scipy.stats import false_discovery_control
        ref = list(false_discovery_control(p, method="bh"))
        out["bh_vs_scipy_max_abs_diff"] = max(abs(x - y) for x, y in zip(bh(p), ref))
    except ImportError:  # pragma: no cover
        out["bh_vs_scipy_max_abs_diff"] = None
    try:
        import statsmodels.stats.multitest as mt  # noqa: F401  (not installed in the project venv)
        out["statsmodels"] = "available"
    except ImportError:
        out["statsmodels"] = "not installed"
    return out


def fisher_greater(a_j: int, a_n: int, b_j: int, b_n: int) -> float:
    from scipy.stats import fisher_exact
    return float(fisher_exact([[a_j, a_n - a_j], [b_j, b_n - b_j]], alternative="greater").pvalue)


def fmt(x: float | None) -> str:
    if x is None:
        return "–"
    if x == 0:
        return "0"
    if x >= 0.001:
        return f"{x:.3f}"
    return f"{x:.1e}"


def correct(rows: list[dict], key: str) -> list[dict]:
    p = [r[key] for r in rows]
    h, b = holm(p), bh(p)
    out = []
    for r, hi, bi in zip(rows, h, b):
        out.append({"id": r["id"], "p": r[key], "holm": hi, "bh": bi,
                    "holm_sig": hi <= ALPHA, "bh_sig": bi <= ALPHA,
                    "test_met_alpha": r["test_met_alpha"], "alpha": r["alpha"],
                    "original_pass": original_pass(r)})
    return out


def original_pass(r: dict) -> bool:
    """The primary's original verdict was a pass ('met'); conjunctions count as passes only if all parts held."""
    return r["original_verdict"].startswith("met")


def main(src: str, out_path: str | None) -> dict:
    data = json.loads(Path(src).read_text())
    recs = data["records"]
    fam = [r for r in recs if r["family"] == "in"]
    m = len(fam)
    p = [r["p_raw"] for r in fam]

    checks = check_against_libraries(p)
    # Recheck of the one p value that was only reported in the journal (E-43), from committed counts.
    rechecks = {}
    for r in fam:
        if "recheck_counts" in r:
            t = r["recheck_counts"]["table"]
            rechecks[r["id"]] = fisher_greater(t[0][0], sum(t[0]), t[1][0], sum(t[1]))

    main_rows = correct(fam, "p_raw")
    by_id = {r["id"]: r for r in fam}
    table = []
    for c in main_rows:
        r = by_id[c["id"]]
        table.append({
            "id": r["id"], "experiment": r["experiment"], "thread": r["thread"], "label": r["line_label"],
            "test": r["test"], "unit": r["unit"], "sidedness": r["sidedness"], "alpha": r["alpha"],
            "p_raw": r["p_raw"], "p_kind": r["p_kind"], "original_verdict": r["original_verdict"],
            "test_met_alpha": r["test_met_alpha"], "original_pass": c["original_pass"],
            "holm": c["holm"], "bh": c["bh"],
            "keeps_significance_holm": c["holm_sig"], "keeps_significance_bh": c["bh_sig"],
            "pass_survives_holm": bool(c["original_pass"] and c["holm_sig"]),
            "pass_survives_bh": bool(c["original_pass"] and c["bh_sig"]),
            "holm_below_registered_alpha": c["holm"] < r["alpha"],
            "precise_value": r.get("precise_value"),
        })
    table.sort(key=lambda t: t["p_raw"])

    def counts(rows):
        return {"family_size": len(rows),
                "tests_meeting_registered_alpha": sum(r["test_met_alpha"] for r in rows),
                "original_passes": sum(r["original_pass"] for r in rows),
                "holm_significant": sum(r["holm_sig"] for r in rows),
                "bh_significant": sum(r["bh_sig"] for r in rows),
                "passes_surviving_holm": sum(r["original_pass"] and r["holm_sig"] for r in rows),
                "passes_surviving_bh": sum(r["original_pass"] and r["bh_sig"] for r in rows),
                "passes_losing_holm": [r["id"] for r in rows if r["original_pass"] and not r["holm_sig"]],
                "passes_losing_bh": [r["id"] for r in rows if r["original_pass"] and not r["bh_sig"]],
                "significant_tests_losing_holm": [r["id"] for r in rows if r["test_met_alpha"] and not r["holm_sig"]],
                "significant_tests_losing_bh": [r["id"] for r in rows if r["test_met_alpha"] and not r["bh_sig"]]}

    summary = {"primary_holm_and_bh": counts(main_rows),
               "holm_below_registered_alpha": sum(t["holm_below_registered_alpha"] for t in table),
               "significant_tests_with_holm_not_below_registered_alpha": [
                   t["id"] for t in table if t["test_met_alpha"] and not t["holm_below_registered_alpha"]]}

    # ---- sensitivity (a): rule-level p values (D-063) where a committed rule-level test exists
    sa_rows = []
    sa_subs = []
    for r in fam:
        rr = dict(r)
        rl = r.get("rule_level")
        if rl:
            rr["p_sens"] = rl["p"]
            rr["test_met_alpha"] = rl["p"] < r["alpha"]
            sa_subs.append({"id": r["id"], "registered_p": r["p_raw"], "rule_level_p": rl["p"], "test": rl["test"],
                            "source": rl["source"], "any_soup_jumped_p": rl.get("any_soup_jumped_p")})
        else:
            rr["p_sens"] = r["p_raw"]
        sa_rows.append(rr)
    sa = correct(sa_rows, "p_sens")
    sens_a = {"substitutions": sa_subs, "rows": sa, "counts": counts(sa)}

    # ---- sensitivity (b): Holm within each thread
    sens_b = {}
    for th in data["threads"]:
        rows = [r for r in fam if r["thread"] == th]
        if not rows:
            sens_b[th] = {"family_size": 0, "note": "no pre-registered primary in this thread among the 45"}
            continue
        c = correct(rows, "p_raw")
        sens_b[th] = {"rows": c, "counts": counts(c)}

    # ---- sensitivity (c), exploratory: (a) plus recomputed rule-level Fisher tests
    sc_rows = []
    sc_subs = []
    for r in sa_rows:
        rr = dict(r)
        rc = r.get("rule_counts")
        if rc:
            pj = fisher_greater(rc["jumped"][0], rc["of"][0], rc["jumped"][1], rc["of"][1])
            rr["p_sens"] = pj
            rr["test_met_alpha"] = pj < r["alpha"]
            sc_subs.append({"id": r["id"], "registered_p": r["p_raw"], "rule_level_p_recomputed": pj,
                            "groups": rc["groups"], "rules_with_a_jump": rc["jumped"], "rules": rc["of"],
                            "source": rc["source"]})
        sc_rows.append(rr)
    sc = correct(sc_rows, "p_sens")
    sens_c = {"label": "exploratory (added in the pre-registration)", "substitutions": sc_subs, "rows": sc,
              "counts": counts(sc)}

    excluded = [{"id": r["id"], "experiment": r["experiment"], "test": r["test"], "reason": r["reason"],
                 "original_verdict": r["original_verdict"]} for r in recs if r["family"] == "excluded"]
    nulls = [{"id": r["id"], "experiment": r["experiment"], "test": r["test"], "p_raw": r["p_raw"],
              "alpha": r["alpha"], "original_verdict": r["original_verdict"], "reason": r["reason"]}
             for r in recs if r["family"] == "predicted_null"]
    flags = {"rounded_as_reported": [r["id"] for r in fam if r["p_kind"].startswith("rounded")],
             "bounds": [r["id"] for r in fam if "bound" in r["p_kind"]],
             "intersection_union": [r["id"] for r in fam if r["p_kind"].startswith("intersection")],
             "recomputed": [r["id"] for r in fam if r.get("recomputed")]}

    out = {"experiment": "E-79", "journal": "J-092", "decision": "D-067 (and D-063 for sensitivity a)",
           "preregistration": data["preregistration"], "input": src,
           "command": "PYTHONPATH=. python scripts/holm_primaries.py",
           "alpha_family_wise": ALPHA, "q_fdr": ALPHA, "m": m,
           "checks": checks, "rechecks_from_counts": rechecks, "p_value_flags": flags,
           "summary": summary, "table": table, "sensitivity_a_rule_level": sens_a,
           "sensitivity_b_within_thread": sens_b, "sensitivity_c_rule_level_recomputed": sens_c,
           "excluded": excluded, "predicted_null": nulls, "rescores_reference": data.get("rescores_reference", [])}

    # ---- print
    print(f"E-79: {m} primaries in the family; {len(excluded)} excluded; {len(nulls)} predicted-null listed apart")
    print(f"checks: {checks}; rechecks: {rechecks}")
    print()
    print(f"{'primary':40s} {'unit':28s} {'raw p':>9s} {'α':>7s} {'Holm':>9s} {'BH':>9s}  orig. verdict / survives")
    for t in table:
        if t["original_pass"]:
            surv = "pass survives" if t["keeps_significance_holm"] else "PASS LOST under Holm"
        elif t["test_met_alpha"]:
            surv = ("test keeps significance (verdict not a pass)" if t["keeps_significance_holm"]
                    else "test loses significance (verdict was not a pass)")
        else:
            surv = "not significant"
        if t["test_met_alpha"] and not t["keeps_significance_bh"]:
            surv += "; lost under BH"
        print(f"{t['label'][:40]:40s} {t['unit'][:28]:28s} {fmt(t['p_raw']):>9s} {t['alpha']:>7g} "
              f"{fmt(t['holm']):>9s} {fmt(t['bh']):>9s}  {t['original_verdict'][:28]} / {surv}")
    print()
    print("primary:", json.dumps(summary["primary_holm_and_bh"]))
    print("Holm below registered alpha:", summary["holm_below_registered_alpha"],
          "; significant tests whose Holm-adjusted p is not below their own alpha:",
          summary["significant_tests_with_holm_not_below_registered_alpha"])
    print()
    print("sensitivity (a), rule level where committed:")
    for s in sa_subs:
        print(f"  {s['id']:14s} registered {fmt(s['registered_p'])} -> rule level {fmt(s['rule_level_p'])}")
    for r in sa:
        if r["id"] in {s["id"] for s in sa_subs}:
            print(f"  {r['id']:14s} Holm {fmt(r['holm'])}  BH {fmt(r['bh'])}")
    print("  counts:", json.dumps(sens_a["counts"]))
    print()
    print("sensitivity (b), Holm within thread:")
    for th, v in sens_b.items():
        if v.get("family_size", 1) == 0:
            print(f"  {th}: empty")
            continue
        print(f"  {th}: {json.dumps(v['counts'])}")
    print()
    print("sensitivity (c), exploratory, rule-level Fisher recomputed:")
    for s in sc_subs:
        print(f"  {s['id']:10s} {s['groups'][0]} {s['rules_with_a_jump'][0]}/{s['rules'][0]} vs {s['groups'][1]} "
              f"{s['rules_with_a_jump'][1]}/{s['rules'][1]}: p {fmt(s['rule_level_p_recomputed'])} "
              f"(soup level {fmt(s['registered_p'])})")
    print("  counts:", json.dumps(sens_c["counts"]))
    print()
    print("predicted null (not in the family):")
    for n in nulls:
        print(f"  {n['id']:16s} p {fmt(n['p_raw'])} (α {n['alpha']}): {n['original_verdict']}")
    print("excluded:")
    for e in excluded:
        print(f"  {e['id']:12s} {e['reason']}")

    if out_path:
        Path(out_path).write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
        print(f"\nwrote {out_path}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    main(a.src, a.out)
