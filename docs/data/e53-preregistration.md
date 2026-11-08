# E-53 pre-registration (written before running)

**Origin (E-52, J-052):** later (T+12000) replicators invaded their soups better than early (T+2000) ones
(D = 0.42, p = 0.045), but only in the late backgrounds (Δ = +0.19, +0.22, +0.11), not in the early ones
(Δ ≈ 0). A confound was found after the run: each candidate has close relatives (≥ 90% identical) only in
the background of its own time (1–2% of that soup), and an injected copy overwritten by a relative is
still counted as a family member. In the late backgrounds, kinship and time are the same variable, so the
post hoc analysis cannot separate them. Kinship decays fast: no candidate has any relative 2,000 rounds
away from its own time (checked for T+4000, T+9000, T+10000, T+20000 before writing this).

**Question:** in backgrounds where **neither** group has relatives, do later replicators invade better than
earlier ones?

**Design (`scripts/bff_invasion.py --e53`, assay unchanged from E-52):** candidates = the E-49 verified
replicators at T+2000 (early) and T+12000 (late) of soups 901, 5006, 5010 (33 programs). Backgrounds =
E-47 snapshots of the same soup at T+4000, T+9000 and a later "future" time (T+20000 for 901 and 5010;
T+12500 for 5006, its last snapshot). Every candidate is assayed in all 3 backgrounds of its soup
(16 replicates). 3 resident-null programs per background. The candidates' kin share in each background is
recorded; the analysis requires it to be < 0.1% for every candidate (else the cell is reported separately).

**Primary test:** as E-52: D = sum over the 9 cells of (mean s late − mean s early); one-sided
permutation test within cells (10000), α = 0.05.

**Hypotheses:** (A) directional adaptation: D > 0, strongest in the T+9000 and future backgrounds.
(B) E-52 was a kinship artefact: D ≈ 0. **Prediction:** we lean to (B) (about 60%), because E-49 and
E-51 found no general trend, and kinship correlated with score within the late backgrounds of 901 and
5010 (ρ = 0.54, 0.64) but not of 5006.

**Secondary:** per-soup Δ (soup 5006 has led in E-46, E-48, E-49, E-51); Δ by background time.
