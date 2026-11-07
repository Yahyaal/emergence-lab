"""Diagnostic behind the v0.5 continuous-label fix (J-012, D-022): what is the "activity"
of a field of static Lenia blobs, and how do old and new labels treat random Lenia rules?

Part 1  Orbium-parameter soup (seed 1, 128x128) after 1000 steps, continued for 3000 more
        steps twice: quantized (the physics as used) and in float64 without rounding.
        If the change came from rounding to 256 levels, the float64 run would freeze.
Part 2  `--rules` random Lenia rules (Lenia.random, `--seed`), 96x96, 500 steps, seed 1,
        observed with the old observer (exact comparisons, 2-state `complex` rule) and the
        current one. Old labels are reconstructed by running with value tolerance 0 and
        classifying without the continuous branch, which is what v0.5 did before the fix.

Usage:
    python scripts/lenia_static_fields.py --out docs/data/experiments/2026-11-06-c01-lenia-static-fields.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from multiprocessing import Pool

import numpy as np
from scipy import ndimage

import emergence.lab as lab
from emergence.discovery import OBJECTIVES, run_settled
from emergence.engine import Universe, UniverseSpec
from emergence.observatory import continuous as C
from emergence.observatory.observer import classify
from emergence.physics import Lenia, parse_rule

ORBIUM = "LENIA/R13/T10/m0.150/s0.0150/b1"
LAGS = [1, 10, 100, 1000, 3000]


def part1() -> dict:
    orb = parse_rule(ORBIUM)
    u = Universe.from_spec(UniverseSpec(orb.to_dict(), 1, 128, 128, 0.35))
    u.step(1000)
    s0 = u.state.astype(np.int16)
    q = [s0]
    for _ in range(3000):
        u.step()
        q.append(u.state.astype(np.int16))
    K = orb._kernel(s0.shape)
    a = s0 / 255.0
    f = [a]
    for _ in range(3000):
        g = 2 * np.exp(-((np.fft.irfft2(np.fft.rfft2(a) * K, s=a.shape) - orb.mu) ** 2) / (2 * orb.sigma ** 2)) - 1
        a = np.clip(a + g / orb.T, 0, 1)
        f.append(a)
    win = np.stack(q[:101])
    d = np.abs(np.diff(win, axis=0))
    active = (d > 1).any(0)
    net = np.abs(win[-1] - win[0])
    mask = win[-1] >= C.THRESHOLD
    edge = mask ^ ndimage.binary_erosion(mask, np.ones((3, 3)))
    near = ndimage.binary_dilation(edge, np.ones((3, 3)), iterations=2)
    return {
        "rule": ORBIUM, "t0": 1000,
        "frac_cells_changed_gt32_levels_at_lag": {
            "quantized": {lag: round(float((np.abs(q[lag] - q[0]) > 32).mean()), 4) for lag in LAGS},
            "float64": {lag: round(float((np.abs(f[lag] - f[0]) > 32 / 255).mean()), 4) for lag in LAGS}},
        "per_step_frac_changed": {"any": round(float((d > 0).mean()), 4), "gt1_level": round(float((d > 1).mean()), 4),
                                  "gt8_levels": round(float((d > 8).mean()), 4), "max_levels": int(d.max())},
        "active_cells_within_2_of_object_edge": round(float((active & near).sum() / active.sum()), 4),
        "active_cells_net_change_gt32_in_100_steps": round(float(((net > 32) & active).sum() / active.sum()), 4),
        "active_cells_oscillating_in_place": round(float((((win.max(0) - win.min(0)) > 32) & (net < 16) & active).sum()
                                                         / active.sum()), 4),
    }


def _observe(args):
    rule, tol = args
    lab.VALUE_TOL = tol  # 0 = the pre-fix observer (exact comparisons)
    spec = UniverseSpec(Lenia.parse(rule).to_dict(), 1, 96, 96, 0.35)
    o = lab.study(spec, steps=500)
    m = dict(o.metrics)
    if tol == 0:
        for k in ("continuous", "quasi_static", "window_change_frac", "free_activity", "dynamic_structures"):
            m.pop(k, None)
        cls = classify(m, o.final_state, 256)
    else:
        cls = o.cls
    return {"class": cls, "settled": run_settled(m, cls), "quasi_static": m.get("quasi_static"),
            "free_activity": round(m.get("free_activity", 0.0), 5), "activity_late": round(m["activity_late"], 5),
            "persistent": m["vocabulary"], "still": m["still_structures"], "self_propelled": m["self_propelled_shapes"],
            "objectives": {k: round(fn(m), 5) for k, fn in OBJECTIVES.items()}}


def part2(n: int, seed: int, workers: int) -> dict:
    rng = np.random.default_rng(seed)
    rules = [Lenia.random(rng).label() for _ in range(n)]
    with Pool(workers or None) as p:
        old = p.map(_observe, [(r, 0) for r in rules])
        new = p.map(_observe, [(r, C.VALUE_TOL) for r in rules])
    per = [{"rule": r, "old": o, "new": w} for r, o, w in zip(rules, old, new)]
    return {"rules": n, "rule_seed": seed, "size": 96, "steps": 500, "universe_seed": 1,
            "old_classes": dict(Counter(o["class"] for o in old)), "new_classes": dict(Counter(w["class"] for w in new)),
            "old_complex_without_self_propelled": sum(o["class"] == "complex" and not o["self_propelled"] for o in old),
            "new_quasi_static_not_extinct": sum(bool(w["quasi_static"]) and w["class"] != "extinct" for w in new),
            "with_self_propelled": sum(bool(w["self_propelled"]) for w in new),
            "free_activity_sorted_nonzero_unsettled_or_qs": sorted(w["free_activity"] for w in new
                                                                   if w["class"] not in ("extinct", "chaotic")),
            "per_rule": per}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", type=int, default=60)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    res = {"part1_noise_or_dynamics": part1(), "part2_random_rules": part2(a.rules, a.seed, a.workers)}
    p2 = res["part2_random_rules"]
    print(json.dumps(res["part1_noise_or_dynamics"], indent=1))
    print("old classes", p2["old_classes"], "| new classes", p2["new_classes"])
    print("old complex without a self-propelled structure:", p2["old_complex_without_self_propelled"],
          "| new quasi-static (not extinct):", p2["new_quasi_static_not_extinct"], "| with self-propelled:", p2["with_self_propelled"])
    print("free activity (non-extinct, non-chaotic):", p2["free_activity_sorted_nonzero_unsettled_or_qs"])
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
