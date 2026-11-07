# E-13 pre-registration (written before running; committed with the panel)

**Question:** in Lenia rules where a glider is known to be *viable* (E-13a scan: an
isolated glider grown from an asymmetric seed persists and travels), does one *emerge*
from a random start, and does the kind of start matter?

**Panel:** the 8 glider-viable single-ring rules of E-13a (`rule-panel-e13.txt`).

**Conditions:** `uniform` (soup), `smooth:3`, `smooth:6`, `smooth:10` (blurred noise,
mass-matched to the soup, D-023), `spots` (8 discs of soup in vacuum). Two runs:
E-13b at density 0.35 (default) and E-13c at density 0.10. 5 seeds per rule, 128x128,
2000 steps, `--seed 13` (paired seeds across conditions).

**Primary outcome:** self-propelled structures per universe (`self_prop`).
Secondary: fraction unsettled. Innovation is not applicable (continuous physics).

**Analysis:** paired vs uniform, sign test across the 8 rules and bootstrap 95% CI
(built into `emergence conditions`). With 5 conditions x 2 densities x 2 outcomes, an
effect counts only if p < 0.05/16 (Bonferroni). Also reported: the share of
(rule, condition, seed) runs with at least one self-propelled structure.

**Prediction (stated in advance):** soups at density 0.35 produce ~0 movers (they did in
E-12); smooth starts with ell near the creature size (6-10, kernel radius 13) and the
sparser density produce more, because a glider needs an isolated, asymmetric lump of
mass ~70 with space around it.

## Amendment 1 (2026-11-07, ~00:45 CST; before any E-13 run)

A literature review (J-013) found that Chan (2019), who reports that gliders such as Orbium
emerge "given enough time" from random starts, used a different start from ours: 15-40
dense square patches of side 0.9 R (12 cells), values uniform in [0, 0.9], in vacuum
(`LeniaND.py`, `random_world`). Added as a sixth condition, `patches` (engine init
kind). It is **not mass-matched** (its mass per cell is ~0.11 on 128x128 vs the soup's
0.175 at density 0.35 and 0.05 at 0.10), so it is a protocol comparison, not a
test of spatial arrangement at fixed matter. Bonferroni threshold becomes
p < 0.05/20 (5 contrasts x 2 densities x 2 outcomes). The `patches` arm ignores
`density`, so it is identical in E-13b and E-13c; it is reported once.
