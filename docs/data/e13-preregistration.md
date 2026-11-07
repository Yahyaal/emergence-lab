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
