# E-78 pre-registration (written before running)

**Origin:** in well-mixed BFF soups, replicators arise (level 3) and mutations are inherited (level 4, E-42),
but later code is not fitter than earlier code by four measures (races E-48/E-49, growth rate E-51, kin-free
invasion E-53/E-54) and no parasites were found (E-66, E-67). Level 5 has been tested only in soups where any
program can meet any other. In artificial-life systems, spatial structure is the classic condition for
cooperation, parasites and coexisting lineages. So the question is whether the negative answer depends on
well-mixing. Groundwork (runner, controls, pilot, power): J-088, commit `27fa64e`. Design approved by the owner
as a package (planner's decisions, 14 November); recorded as D-065.

**Question:** when the same jumped soups continue with programs that meet only their lattice neighbours,
does later code become fitter than in a well-mixed continuation of the same snapshot?

## Design (fork, not new soups)

**Soups:** all 7 jumped E-54 soups of 2^16 programs: 5301, 5302, 5308, 5401, 5402, 5406, 5410, with jump rounds
T = 21750, 13750, 12500, 10250, 22250, 16750, 750. Each starts from its **T + 2000 snapshot** (the E-54 "early"
time point; `runs/e54/<seed>-<T+2000>.npy`, an uncommitted cache in the main checkout, read only). The snapshots
hold programs only, so no continuation can equal the original run.

**Arms (`scripts/bff_spatial.py` `ArmSoup`, driver `scripts/e78_run.py`):** each snapshot is placed on a 256 × 256
torus by a seeded permutation of its rows (`default_rng([78, seed])`, the same for every arm) and forked into
three continuations of **20,000 rounds** (to T + 22,000):
- **M** (well mixed): pairs = `rng.permutation(n)`, exactly `bff.Soup.epoch` (bit-identical, checked);
- **S** (spatial): each round is a perfect matching of lattice neighbours. The axis (horizontal / vertical) and
  the parity offset (0 / 1) are drawn each round. Cell (x, y) is paired with (x + 1, y) for x ≡ offset (mod 2),
  or the vertical analogue, with wrap. One coin per pair decides which program runs first;
- **M′** (seed null): a second well-mixed continuation with another seed.

Everything else is as in E-54: the same C epoch, mutation 0.00024 per byte per round on the flat array, step
limit 8192, mode `bff`, 64-byte programs. Generator seeds: M `[78, seed, 0]`, S `[78, seed, 1]`, M′
`[78, seed, 2]`. **Operations:**
- Each (soup, arm) writes its programs and its generator state every 2,000 rounds, to `runs/e78/run/`.
- After an interruption it resumes exactly from its last snapshot (`check_resume`, in `pytest`: an interrupted
  run equals an uninterrupted one).
- 21 jobs on at most 11 worker processes; expected ~10 h.

Forking a snapshot is an intervention on a clone; the original E-54 data are only read.

## Outcomes (`scripts/e78_analysis.py`, committed with this file)

**Assay:** `program_fitness.invasion`, unchanged: 64 copies into 4,096 programs sampled from a background,
16 rounds, 16 replicates, paired control with no injection, family counted with its reverse form. **Kin rule**
as in E-54: a candidate with ≥ 0.1% of ≥ 90%-identical programs (either orientation) in the background is
dropped, and the drops are counted. A soup's Δ for an arm is defined only if that arm's late group and the early
group each keep ≥ 2 candidates.

**Candidates:**
- **Late:** for each arm, the 40 most common distinct programs of its final snapshot (`distinct_top`, as in
  E-54). Each gets the replicator test repeated 10 times (`program_parasites.alone_test`, D-049). A program is
  *verified* if at least one of its 10 repeats is "replicator". The late group is the first 6 verified programs,
  in order of abundance. The procedure is the same in M, S and M′.
- **Early:** E-54's 6 early programs per soup (T + 2000, shared by the arms).

**(a) Primary.** Background: the **original E-54 run's T + 10000 snapshot** of the same soup, a separate
continuation from all three arms (common garden, well mixed).
- For soup k and arm A: Δ_A,k = mean s(late_A,k) − mean s(early_k). Statistic: d_k = Δ_S,k − Δ_M,k. The soup is
  the unit, n = 7.
- Test: exact one-sided sign-flip permutation test of Σ d_k > 0, over all 2^7 = 128 sign patterns; the smallest
  attainable p is 1/128 = 0.008.
- **Seed-null contrast:** d′_k = Δ_M′,k − Δ_M,k, with the same sign-flip test, two-sided.

Verdicts, evaluated in this order:
- **Pass:** p < 0.05, mean d > 0, and the seed-null contrast is not significant (two-sided p ≥ 0.05).
- **Fail:** the upper end of the two-sided 95% t interval for mean d (6 df) is below **δ\* = 0.28**.
- **Undecided:** anything else.

A pass whose interval lies entirely below 0.28 would be reported as a small effect.

**Sensitivity analyses** (same test, n = 6, smallest p 1/64): without soup 5410 (jumped at round 750), and
without soup 5401 (whose E-54 late sample held one family scoring −0.8).

**What n = 7 can detect** (`scripts/e78_power.py`, J-088; one-sided sign-flip, α 0.05):
- Under E-54-like heterogeneity between continuations (resampled E-54 deltas, σ of d ≈ 0.24), 80% power needs
  a mean d of **≈ 0.28** log units of invasion score, and 50% power needs 0.18.
- If only assay noise mattered (σ ≈ 0.07), 80% power needs 0.08. A normal model with E-54's SD (σ ≈ 0.32)
  needs 0.36.
- Differences below ~0.15 will usually be missed. For scale, E-54's per-soup deltas ran from −0.49 to +0.19.
  An invader whose copies fail 10% of the time scores about −1.3 (J-052).
- The SD of d′ (the seed null) gives the actual noise after the run.

**Secondary (all reported; none changes the primary verdict):**
1. The same statistics (d, d′, verdict rule) in the original run's **T + 20000** background.
2. Within-arm late vs early (E-54's test): D_A = Σ_k Δ_A,k with within-soup permutation of the early/late
   labels (10,000, one-sided), for S, M and M′, in both backgrounds.
3. **Reciprocal transplant:** late S code invading the M arm's final soup, and late M code invading the S
   arm's final soup. The soups are sampled well mixed, kin-checked, with the early group assayed in both soups
   as the reference: Δ″_S,k = s(late_S in M_final) − s(early in M_final), and Δ″_M,k likewise in S_final.
   Reported per soup, with the two-sided sign-flip p of Δ″_S − Δ″_M (descriptive).
4. **Parasites (D-048 with D-049):** in each arm's final snapshot, among the 40 most common distinct programs.
   Programs whose generation 1 never grew in the 10 repeats get `parasite_test`, with that arm's final snapshot
   as the partner pool (whole soup, well mixed). A parasite verdict is confirmed by a second run with an
   independent seed. Reported: verdict mix and soups with ≥ 1 confirmed parasite, per arm. Descriptive reading:
   "parasites appear under space" if confirmed parasites are found in ≥ 2 S soups and in no M or M′ soup.
5. **Descriptive trajectories** at every snapshot (every 2,000 rounds), per arm:
   - 90%-identity families holding ≥ 1% of the soup, and their shares;
   - `hoe_shuffled` (HOE of a fixed shuffle of the rows; raw HOE is also logged but is geometry-sensitive,
     J-088);
   - distinct exact programs;
   - the spatial clustering statistic: the neighbour ratio of each family ≥ 1% (median), and the top family's
     share in its largest 4-connected patch. M's storage order is the null, ≈ 1;
   - steps per pair and HOE every 250 rounds.

   Intermediate snapshots are descriptive only. Invasion tests at intermediate snapshots are run only if time
   allows after the primary, and are then labelled exploratory.

## Limits of this design (stated in advance, repeated in the write-up)

- **No spatial versions of the instruments.** The fitness assay and the parasite detector are well mixed.
  **Advantages or parasites that exist only in space are invisible to this design**, for example resistance to
  being overwritten by neighbours, kin cooperation, or a parasite that needs its local hosts. A null result means
  "no advantage visible in a well-mixed common garden", not "no adaptation in S".
- **A between-arm difference in drift, diversity, number of families, clustering, HOE or steps per pair is not
  level 5.** Parasites alone would be an ecology result, not cumulative evolution.
- **What would count as evidence toward level 5**, stated as "directional adaptation under space" and not as
  level 5 itself. All three are needed:
  - a primary pass;
  - within-S D_S > 0 with p < 0.05 in the primary background (S code improves in absolute terms, not only
    relative to an M arm that declines);
  - the same sign in the T + 20000 background.

  Level 5 (cumulative innovation, O5) would need improvements that build on one another, which this design
  cannot show.
- **Home advantage for M:** the backgrounds are well-mixed soups like the one M's code evolved in, so if
  anything the common garden is biased against S.
- **Placement destroys nothing:** a well-mixed soup has no geometry. The S arm starts unclustered and builds
  patches (within ~50 rounds in the pilot).
- **The arms are not independent:** n = 7, one fork point per soup, and a shared history and early group. The
  results hold for standard BFF at 2^16 and mutation 0.00024. The 4-neighbour matching keeps one interaction per
  program per round, as in M; other neighbourhoods could give other results.
- **Kin:** late code descends from the same T + 2000 state as the backgrounds. Kin decayed within 2,000 rounds in
  E-53/E-54, but old lineages may persist locally in S. The kin rule catches this, and drops are counted.

## Prediction

- Primary pass: **~15%**. E-48 to E-54 found no adaptation in M, and what space favours may not show in a
  well-mixed assay. Fail: ~45%. Undecided: ~40%.
- Within-S D_S > 0 significant: ~15%. Both (the "directional adaptation under space" reading): ~10%.
- Confirmed parasites in ≥ 2 S soups: ~10%. In M or M′: ≤ 5% (0 in 3,220 programs in E-66/E-67).
- More families ≥ 1% and neighbour ratio ≫ 1 in S at the end: ~90% (45–52 within 200 rounds in the pilot).
  This is expected and is not level 5.
- Level 5 shown by this experiment: < 5%.

## Planning numbers (J-088)

- **Controls:** pairs form a perfect neighbour matching; M = `bff.Soup` bit for bit; a replicator block
  spreads as one growing patch in S (excess ∝ t^1.86) and exponentially and unclustered in M; `noexec` changes
  nothing but mutation; resume is exact.
- **Timing:** 1.38 × 10⁻⁴ s per round per unit of steps per pair under 11-process load. Projected wall time
  for 3 arms × 20,000 rounds: 9.9 h (101 CPU-h).
- **Analysis:** estimated ~1 h. The analysis code was checked for crashes on fork snapshots with tiny settings
  (`--dry`, not data).
