# E-56 pre-registration (written before running)

**Origin:** E-55 found that under the standard BFF rule every short copier copies backwards, and that starting
head1 at byte 64 instead of 0 flips this (139 forward, 0 reverse). That is a statement about short kernels.
Does it hold for what a soup actually evolves?

**Run (`scripts/bff_counterfactual.py`):** 4 soups of 2^16 programs (seeds 5600–5603) under the
counterfactual rule (head1 starts at byte 64; interpreter `scripts/bff_kernels.c` `epoch_h`, otherwise
identical to the soup: 64-byte programs, 8192 steps, mutation 0.00024, random pairing). Up to 24,000 rounds;
jump = D-045's HOE criterion (≥ 1.0 at 3 consecutive checkpoints every 250 rounds, T = the first). A jumped
soup runs to T + 2,000 and is saved there.

**Classification:** the 40 most common distinct programs at T + 2,000 (distinct = < 90% identical forwards
and backwards, as E-54) are classified with E-55's copier rule **under the counterfactual interpreter**
(runs first with 4 random partners, partner ≥ 60/64 equal to the program or its reverse, program intact).
The D-040 replicator detector is not used: it runs the standard interpreter.

**Primary prediction:** in every soup that jumps, the copiers among the 40 are forward copiers (≥ 90% of
classified copiers forward, at least one copier). If no soup jumps, the test is undecided (reported as such).
**Comparison (standard rule):** the same classification of E-54's jumped soups at T + 2,000 with the standard
interpreter (E-55 secondary 3 predicts reverse).

**Secondary (descriptive, n = 4):** number of soups that jump by 24,000 rounds (standard 2^16: about half,
E-50/E-54).

**Limits:** 4 soups; the rule change also changes everything else a program can do, so a different jump rate
would not be attributable to copy orientation alone.
