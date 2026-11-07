# E-19 pre-registration (written before running; responds to review R-4)

**Why:** R-4 pointed out that the smooth start differs from the soup in its value distribution as
well as its spatial correlation (more weakly filled cells), and that the soup sits on a sharp
die/freeze transition at every density tried, so "0 of 160" was close to guaranteed.

**E-19a (confirmatory): is it the spatial correlation?** Panel: the 8 rules of E-13/E-14.
Conditions: `uniform`, `smooth:L` and `smooth_shuffled:L` (exactly the smooth start's cell
values, randomly permuted: same mass, same value distribution, no correlation). Two runs:
density 0.10 with L = 3 and density 0.35 with L = 6 (the E-14 arms). 20 seeds per rule and
condition, master seed 19, 128x128, 2000 steps.
Primary: universes with >= 1 self-propelled structure, `smooth` vs `smooth_shuffled`, one-sided
Fisher exact per density, alpha = 0.025 each. Secondary: a within-rule (stratified) view: per-rule
counts and an exact sign test across rules; every mover re-isolated with
`scripts/verify_movers.py` (must survive 1000 steps alone).
Prediction: smooth > shuffled at both densities, shuffled near 0.

**E-19b (descriptive): is there a soup density that makes gliders?** The same 8 rules, `uniform`
only, densities 0.12, 0.14, ..., 0.30 (10 values), 5 seeds each, master seed 191, 128x128,
2000 steps. Outcome per density: class mix (extinct / frozen field / other) and universes with a
self-propelled structure.
