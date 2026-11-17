# E-80 pre-registration (written before running)

**Origin:** E-78 (J-089) forked the 7 jumped E-54 soups into a well-mixed continuation (M), a neighbour-only
continuation on a 256 × 256 torus (S) and a second well-mixed continuation (M′), 20,000 rounds each. Late S code was
no fitter than late M code, but fitness was measured in a **well-mixed** common garden. Spatial theory predicts
exactly that null: advantages that arise under local interaction (holding ground, spreading as a front, restraint)
are invisible when everything is mixed (J-091). The owner approved building a neighbour-aware assay and
pre-registering an experiment with it. Groundwork (instrument, controls, gardens, noise, power, costs): J-093, commit
`6b81b79`; instrument choices D-069; run options for more soups D-068 (proposed, awaiting the owner).

**Question:** in a lattice-native common garden, does late S code spread farther than late M code of the same soup?

## What was looked at before this file was written

**Allowed and used:**
- Synthetic programs and gardens: the hand-written replicator, `trapped(k)`, the non-copier, a filler smear, random,
  halting and copier gardens.
- E-42 replicators #0 (soup 901) and #5 (soup 5006).
- E-47 snapshots of soups 901, 5006 and 5010 (2^14 programs, unrelated to the 7 soups), for gardens and garden
  diagnostics.
- From the E-78 run directory (read only): for each of the 7 soups, the fork-point snapshot (T + 2000, identical in
  every arm; read from the M file) and the final M and final M′ snapshots.
  - Lattice-assay scores of early, M and M′ blocks were computed and examined in three versions of the tag rules:
    v1 (unanchored, 230 assays), v2 (anchors not passed on within a lineage, 142 assays) and v3 (final, 960 assays).
  - The 5301, 5402 and 5410 fork snapshots were also used for timing and garden diagnostics.
- One new random soup under the h = 64 head-start rule, for timing only.
- The `--dry` check of `scripts/e80_run.py` ran assays on fork snapshots standing in for every arm. It checks the code
  path only; its scores were not examined.

**Not looked at:**
- No late-S snapshot and no S state file was loaded. `e80_groundwork.source()` refuses "S"; `e80_run.py` refuses it
  unless this file is committed and `--confirm` is given.
- No lattice-assay outcome comparing S code with M or early code was computed.
- Known beforehand from E-78 (J-089, published): S is a mosaic of small local families; S code is not fitter in the
  well-mixed garden.

**Choices made after seeing allowed data, disclosed:**
- **Primary garden g901.** It is the only garden where the emergent positive was seen: 24 of 24. In g5006 it was not
  seen.
- **Primary score and horizon (linear area change at T = 64).** This pair has the best ratio of positive effect to the
  M′ − M continuation noise.
- **δ\*.** Set at half the positive.
- **Replication (16 blocks × 4 seeds).** Chosen from the noise components.

All of these use only the positive controls and the M, M′ and early blocks.

## Design

**Soups and sources (unit of analysis: the soup, n = 7, the D-063 analogue):** 5301, 5302, 5308, 5401, 5402, 5406 and
5410, from the E-78 cache `<E78_RUN>/<seed>-<arm>-<epoch>.npy`, read only. Groups per soup:
- **early:** the fork snapshot, T + 2000;
- **M, M′:** final, T + 22000;
- **S:** final, T + 22000, structure **preserved**;
- **Sshuf:** the same S blocks with positions permuted.

**Blocks (`e80_run.block`):** 8 × 8 = 64 programs.
- **S:** a contiguous block of the 256 × 256 S lattice at a seeded random position (generator
  `[80, 10, seed, 3, b]`; the stored row order is the grid). Sshuf permutes it with `[80, 11, seed, b]`.
- **early, M, M′:** well mixed, so a random sample without replacement laid out at random (`[80, 10, seed, code, b]`,
  code 0, 1, 2).
- **16 blocks** per group per soup (b = 0 … 15).

**Assay (`scripts/lattice_assay.py`, unchanged from the groundwork commit):**
- **Garden:** the block is planted at a seeded random position in a copy of a garden replicate.
- **Pairing and length:** the lattice runs **64 rounds** of the E-78 S pairing (`bff_spatial.spatial_pairs`), mode
  `bff`, step limit 8,192, **no mutation**.
- **Descent (D-069):** a lineage tag with an anchor. A site takes its partner's tag only on a detected copy: changed
  bytes, ≥ 90% match in either orientation, ≥ 75% of the instruction bytes, closer than its own old bytes, and ≥ 90% like
  the partner's anchor. A tag is lost when the code drifts below 90% of its anchor.
- **Score:** **A = N_64 / 64 − 1**, where N_64 is the number of tagged sites after 64 rounds.
- **Seeds:** **4 assay seeds** per block (j = 0 … 3). Garden replicate `gi = (b + j) mod 4`; assay seed
  `[80, 100, seed, b, j, gi, 0, 0]`.
- **Common random numbers:** every group of a soup sees the same garden replicate, block position and pairing seed for
  the same (b, j).

**Primary garden g901:** 4 replicates (`runs/e80/garden-g901-{0..3}.npy`, regenerated exactly by
`PYTHONPATH=. python scripts/e80_groundwork.py --gardens`).
- Each replicate is 4,096 programs sampled from E-47 soup 901 at round 40,000 (`[80, 1, i]`), aged 2,000 rounds on the
  64 × 64 lattice (S pairing, mutation 0.00024, `[80, 1, i, 1]`).
- sha256 of the four replicate files concatenated in order 0 to 3 (first 16 hex digits): g901 `3f208cb2897ca4ed`; g5006 `26e365b4b66d663a`.

**Kin rule:** an assay is excluded if more than 0.1% of its garden replicate is ≥ 90% identical (either orientation) to
any program of its block. In calibration the kin share was 0 for all 1,176 early, M and M′ blocks.

## Outcomes (`scripts/e80_run.py`, committed with the groundwork)

**Primary.** For soup k:
- **Statistic:** d_k = mean A(S, preserved) − mean A(M), over its 64 kept assays per group.
- **Test:** exact one-sided sign-flip test of Σ d_k > 0 over all 2^7 = 128 sign patterns (smallest p 1/128).
- **Interval:** two-sided 95% t interval for the mean d (6 df).

**Required reference (seed null):** d′_k = mean A(M′) − mean A(M), exact two-sided sign-flip test. It is predicted
null and is listed apart from the multiple-comparison family, as in E-79.

**Verdicts, in this order:**
- **Pass:** p < 0.05, mean d > 0, and the seed null is not significant (two-sided p ≥ 0.05).
- **Fail:** the upper end of the 95% t interval for mean d is below **δ\* = 1.24**.
- **Undecided:** anything else.

**Smallest effect of interest, δ\* = 1.24.** It is half the emergent positive in this garden at this horizon: 64 copies
of the 5006 species against a native 901 block, mean difference 2.48 in A, 24 of 24 replicates (J-093). An S advantage
half the size of a whole fitter species is the smallest effect this design treats as worth detecting.

**What 7 soups can detect** (J-093; continuation SD ≈ 1.95, so SD of d ≈ 1.96 at 16 × 4):
- **Detectable effect:** 80% power at a mean d of 2.15, and 50% at 1.39.
- **Verdict probabilities** under these rules:

  | True d | Pass | Fail | Undecided |
  |---|---|---|---|
  | 0 | 4% | 30% | 67% |
  | 1.24 | 38% | 2% | 60% |
  | 2.48 | 81% | 0% | 20% |

**Secondary (reported; none changes the primary verdict):**
1. **Late against early within each arm:** S − early (one-sided), M − early and M′ − early (reported), each per soup
   with the exact sign-flip test, primary garden and score.
2. **Structure preserved against shuffled:** S − Sshuf, two-sided sign-flip.
3. **The same blocks with well-mixed pairing.** The same tagged assay in the same garden with well-mixed pairing (8
   blocks × 1 seed, groups early, M and S, seed `[80, 100, seed, b, 0, gi, 1, 0]`) gives S − M, S − early and M − early.
   The lattice-specific part is (S − M) on the lattice minus (S − M) with mixing, per soup, two-sided. This replaces "the
   old well-mixed invasion assay", which scores single programs, so that only the pairing differs (D-069).

**Sensitivity (reported):**
- without soup 5410 (jumped at round 750);
- without 5401;
- T = 32;
- the log score ln((N_64 + 1) / 65);
- the second garden g5006 (8 blocks × 2 seeds; groups early, M, M′, S), with its own seed null.

g5006 forms a mosaic like S but has no validated emergent positive (J-093).

**Exclusions:**
- **Kin:** the kin rule above.
- **Soups:** a soup is dropped from a contrast if fewer than half of either group's assays survive the kin rule.
- **Minimum:** with fewer than 3 soups left the contrast is "undecided (too few soups)".
- **Crashes:** a crashed assay is rerun with the same seed (assays are deterministic).

**Stopping rule:**
- **One run:** every assay listed by `e80_run.jobs()` runs once.
- **No interim looks:** the analysis runs only after all assays are cached.
- **Fixed sample:** no soups, blocks or seeds are added after the start.
- **Code frozen:** if the code must change after the run starts (a bug), the change and its effect are reported, and
  the verdict stays with the registered code unless the bug makes it invalid. In that case the verdict is "undecided"
  and the reason is stated.

## Multiple comparisons (joins the E-79 family)

**Holm family:** by the J-092 convention, the primary p value is added to `docs/data/e79-primaries.json` (family
"in", source line in this file) and `scripts/holm_primaries.py` is rerun. That makes 43 p values. The journal states
both raw and Holm-adjusted results. The seed null joins the predicted-null list.

**Stated in advance:**
- With 7 soups the smallest attainable p (1/128 = 0.0078) adjusts to about 0.17 in this family (computed on the
  current 42 values), so **a pass cannot survive the family-wise correction.**
- A pass would be reported as "nominal pass, not significant after Holm".
- Under BH (q = 0.05, the E-79 secondary) it could survive.

## What each outcome would and would not show (level 5 is never assigned by this experiment)

- **Pass:** late S code spreads farther than late M code of the same soup in a lattice common garden, by an effect
  near the size of a fitter species. Read with secondary 1 (S − early > 0) and secondary 3 (the advantage is larger on
  the lattice than with mixing), this would be **evidence of directional adaptation to the lattice in S, at the
  nominal level only**.
  - It would not show cumulative innovation (O5): improvements that build on one another.
  - It would not show that the advantage arose by selection rather than by drift in one continuation. The seed null
    and n = 7 limit that.
- **Fail:** in this garden, no S advantage as large as half a species-level effect. Smaller lattice advantages remain
  possible. Together with E-78, this would mean "no large advantage under space, seen either in a well-mixed or in a
  lattice garden".
- **Undecided (the likeliest outcome, about 60 to 67%):** nothing beyond what J-093 already says. Seven soups are too
  few. The test then rests on D-068.
- **Any between-group difference in S − Sshuf, in steps per pair or in clustering is not level 5.** A
  structure-preserved advantage would point to an effect of local arrangement: kin groups that hold ground. That is an
  ecological effect, not cumulative evolution.

## Part B (more soups): planned, not pre-registered here

D-068 offers two options for new independent soups, both under the h = 64 head-start rule (E-57), with 2^14 programs on
a 128 × 128 torus, forked at jump + 2,000 rounds into S, M and M′:
- **Option 1:** 16 soups × 10,000 rounds per arm, about 94 CPU-h (8.6 h on 11 workers).
- **Option 2:** 40 soups, about 236 CPU-h (21.5 h).

Their driver does not exist yet. If the owner chooses one, its design (jump criterion, seeds, horizon, primary test and
δ\*, using the Part A instrument unchanged) will be pre-registered as an amendment to this file and committed alone
before any Part B soup is created. **No Part B data exist.**

## Commands, seeds, code

- **Code:** the groundwork commit `6b81b79` (instrument, gardens, driver, analysis). This file is committed
  alone after it. The run starts after this commit.
- **Gardens** (already built; rebuild to check): `PYTHONPATH=. python scripts/e80_groundwork.py --gardens --workers 8`.
- **Run and analysis:**
  `E78_RUN=<E-78 run dir> PYTHONPATH=. python scripts/e80_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e80-lattice.json`.
  - Cache `runs/e80/run/assays.jsonl` (resumable).
  - 7 × (5 × 64 + 3 × 8 + 4 × 16) = 2,856 assays.
- **Expected wall time:** about 20 to 40 minutes on 11 workers.
  - Dry-run and calibration timing: about 4 CPU-s per assay, so about 3.2 CPU-h.
  - S code may run more steps per pair than M (E-78), hence the upper end.

## Prediction

| Outcome | Probability | Basis |
|---|---|---|
| Primary pass | ~10% | E-78 and E-48 to E-54 found no adaptation; the theory says lattice advantages may exist; power is low |
| Fail | ~25% | |
| Undecided | ~65% | |
| S − early > 0 significant | ~10% | |
| S − Sshuf two-sided significant | ~15% | patches of kin may hold ground |
| Lattice-minus-mixed S − M > 0 | ~50% | sign only |
| Level 5 shown | 0% | not assignable by design |
