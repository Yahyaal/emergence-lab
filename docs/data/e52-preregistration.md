# E-52 pre-registration (written before running)

**Origin (J-051):** growth into random code (D-044) predicts race outcomes only weakly (ρ = 0.196) and
shows no fitness trend over time except in soup 5006. After the jump, replicators live among other
replicators, so the relevant fitness is how well a program spreads **in the soup it actually lives in**.

**Assay (`program_fitness.invasion`, added for this experiment):** 64 copies of candidate x replace random
members of 4096 programs sampled from a soup snapshot; 16 rounds without mutation; a paired control run
from the same background with the same pairings and no injection; excess e = n(injected) − n(control) of
x's family (≥ 90% identical to x or its reverse); score s = ln((e(16) + 1)/(e(0) + 1)); 16 replicates.
Calibrated before this experiment on hand-written copiers (`resident_copiers`): a trap variant that copies
with probability 0.9, 0.75 and 0.5 scored −1.3, −2.9 and −4.0, neutral invaders −0.27 to +0.34 (SE ≈ 0.2,
8 replicates); benchmark probes (known effect, neutral null, non-copier, copyall deceptive) added.

**Material:** candidates = the 47 E-49 verified replicators (soups 901, 5006, 5010; T+2000, T+6000,
T+12000). Backgrounds = the E-47 snapshots of the same soup at T+2000 and T+12000 (6 backgrounds).
Every candidate is assayed in both backgrounds of its soup. Resident null: in each background, 6 programs
drawn at random from that background are assayed the same way (36 null assays).

**Primary test (is later code fitter in the soups themselves?):** per cell (soup × background),
Δ = mean s of T+12000 candidates − mean s of T+2000 candidates; statistic D = sum of the 6 Δ.
One-sided permutation test (early/late labels permuted within each cell, 10000 permutations), α = 0.05.
**Prediction:** not significant overall (E-49, E-51); soup 5006 has Δ > 0 in both backgrounds.

**Secondary:** (1) validity: Spearman correlation between the difference in invasion score (mean of the two
backgrounds) and the E-49 race share for the 347 E-49 pairs; prediction ρ > 0.196 (better than growth rate).
(2) Time-shift pattern (descriptive): do candidates score better in the background of their own time?
(3) Candidates vs resident null in each background (descriptive).

**Limits:** backgrounds are frozen snapshots run without mutation for 16 rounds; 4096 of 16384 programs are
sampled per replicate; the family criterion (90% identity) includes resident relatives, which the paired
control subtracts on average but not exactly. Strong drift (winner-take-all meetings) limits single-program
precision; the test pools programs.
