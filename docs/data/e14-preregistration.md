# E-14 pre-registration: confirm E-13's smooth-start glider effect (written before running)

**Origin of the hypothesis:** E-13 (exploratory for this question). Gliders emerged in
18 of 240 smooth-start universes and 0 of 80 mass-matched soups (universe-level Fisher
p = 0.0048, NOT pre-registered; the pre-registered rule-level sign tests could not reach
their Bonferroni threshold with 8 rules). E-14 re-tests it with fresh seeds.

**Panel:** the same 8 glider-viable rules (`rule-panel-e13.txt`). 20 seeds per rule and
condition, master seed 14 (E-13 used 13), 128x128, 2000 steps.

**Two contrasts, fixed in advance:**
1. density 0.10: `smooth:3` vs `uniform` (soup), same mass.
2. density 0.35: `smooth:6` vs `uniform`, same mass.

**Primary outcome:** universe has >= 1 self-propelled structure (observatory test).
**Test:** one-sided Fisher exact test on universes (160 vs 160 per contrast), alpha =
0.025 per contrast (Bonferroni over 2). Prediction: smooth > soup in both.
**Secondary (descriptive):** glider rate per rule with a 95% Wilson interval; final class
mix; whether glider runs end with a single object (the "lone survivor" pattern).
**Validity check:** every self-propelled structure is re-isolated and must survive 1000
steps alone with mass within the tracker's tolerance; failures are reported.
