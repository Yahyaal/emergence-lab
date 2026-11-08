# E-51 pre-registration (written before running)

**Origin:** the race assays (E-43, E-44, E-46, E-48, E-49) read end counts after 96 epochs from 8 copies
each, so drift limits them to large effects. E-49 found later verified replicators ahead in only 24 of 44
programs (p = 0.33). D-044 adds a growth-rate assay (`observatory/program_fitness.py`): the early
exponential growth rate r of 16 copies among 4096 background programs, 24 replicates. It was calibrated
before this experiment on a known-effect ladder (hand-written replicator with a trap that lets it copy
with probability p ≈ 2^-k): in the "halting" background, measured r matched ln(1 + p/2) within 0.02 for
p = 1 … 1/16 and separated k = 3 from k = 4 (difference 0.03) at p = 6e-7 with 8 replicates. A pilot (not
part of this experiment) on the 9 E-42 replicators showed that all of them copy perfectly in the halting
background (r ≈ 0.39, the ceiling), and that in the "random" background (random bytes, which damage a
replicator running second) their r is 0.075–0.10, against 0.14 for the hand-written replicator.

**Material:** the E-49 samples: up to 6 verified replicators per soup (901, 5006, 5010) at each of T+2000,
T+6000, T+12000 (T = the soup's transition), reconstructed from
`docs/data/experiments/2026-11-08-e49-time-races.json`; reverse forms counted (`alts = [x[::-1]]`).

**Measures (`scripts/bff_fitness.py`):** for each program, r in the random background (24 replicates; the
primary measure) and in the halting background (8 replicates; descriptive).

**Primary test (later code fitter?):** statistic S = sum over the 3 soups of Spearman ρ(time point, r).
One-sided permutation test, permuting time labels within each soup (10000 permutations), α = 0.05.
**Prediction:** not significant (E-49 found no clear trend), with soup 5006 the most likely to show a
positive ρ (E-48, E-49 soup-level numbers).

**Validity test (does r measure what races measure?):** for the 347 E-49 races (pairs a, b with ≥ 8
informative replicates), Spearman correlation between Δr = r_b − r_a (random background) and b's share
of races won. **Prediction:** ρ > 0.2, one-sided p < 0.01. If this fails, r measures something that does
not decide contests and the primary test is not a test of competitive fitness. Report that plainly.

**Secondary (descriptive):** r of the hand-written replicator in the same backgrounds (reference); the
share of pairs of programs from the same time point that differ at p < 0.05 (Mann–Whitney), compared with
the share for pairs across time points (selection-aware null for "differences" between candidates drawn
the same way).

**Limits:** r measures one component of fitness, spreading into random code, which is the environment
right after the transition but not that of a soup full of replicators. The halting background removes
damage and so has a ceiling every perfect copier reaches. Neither is invasion fitness in the real soup.
