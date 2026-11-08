# E-50 pre-registration (written before running)

**Question:** does the BFF state transition (the appearance of self-replicators, J-040/J-041) become
more likely per epoch in larger soups, and how strongly? Agüera y Arcas et al. (2024) used 2^17
programs and saw transitions within a few thousand epochs in a large share of runs; with 2^14
programs we saw 2 of 12 pre-registered soups transition by epoch 48000 (E-40/E-41; plus pilot 901
at 8750, chosen because it transitioned and therefore excluded here).

**Hypothesis:** the origin of a replicator is a rare event per program interaction, so the transition
hazard per epoch grows with the number of programs N, λ(N) ∝ N^β with β ≈ 1.

**Design (`scripts/bff_sizes.py`, code otherwise unchanged from E-41):** BFF soups from random programs,
64 bytes, mutation 0.00024 per byte per epoch, 8192 steps, as in E-40:
- N = 2^13: 12 soups (seeds 5100-5111), up to 48000 epochs;
- N = 2^15: 12 soups (seeds 5200-5211), up to 32000 epochs;
- N = 2^16: 10 soups (seeds 5300-5309), up to 24000 epochs.
HOE is recorded every 250 epochs; the transition epoch is the first checkpoint with HOE ≥ 1.0 (as
E-40). A soup that transitions is scanned with the unchanged replicator detector
(`replicators.scan`) 1000 epochs later and then stopped (to save CPU); others are scanned at the end.
The 2^14 arm is E-40/E-41 as run (12 soups; exposures 10 × 48000, 43250, 32000; 2 events).

**Primary analysis:** a Poisson (exponential waiting-time) model, events ~ Poisson(exposure · λ0 · (N/2^14)^β),
exposure = epochs observed until transition or end, fitted by maximum likelihood over all four sizes.
Primary test: β > 0, one-sided likelihood-ratio test against β = 0, α = 0.05. Report β with a 95%
profile-likelihood interval.

**Predictions:** β ≈ 1 gives about 1.0, 2.8 and 3.5 expected transitions in the 2^13, 2^15 and 2^16 arms
(λ(2^14) = 2 / 555250 per epoch). We predict at least 3 transitions in total in the 2^15 and 2^16 arms and
β > 0 at α = 0.05. Power is low (few events); a non-significant result with a wide interval is the honest
outcome to expect if hazards are near our 2^14 estimate.

**Secondary (replication of E-41's claim):** every transitioned soup contains a verified replicator at its
scan 1000 epochs later; no untransitioned soup does at its end scan.

**Limits:** the HOE threshold 1.0 is the E-40 criterion; random-soup HOE baselines (~0.3) barely depend on N
at these sizes, but this is checked in the analysis (median HOE of the first 4 checkpoints per arm).
Mutations per epoch scale with N (same per-byte rate), as in the paper. Horizons differ by arm (CPU budget);
the waiting-time model handles that, but assumes a constant hazard over time, which E-41 cannot test.
