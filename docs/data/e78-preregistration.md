# E-78 pre-registration (DRAFT: not final, nothing run yet)

> **Status: draft for the planner and the owner.** The groundwork (runner, controls, timing pilot, power
> estimate) is done; the choices listed under "Open choices" must be settled and every number marked
> **OPEN** must be fixed before this is committed as the pre-registration. Nothing below has been run on the
> 7 soups beyond the 200-round pilot of soup 5301.

**Origin:** in well-mixed BFF soups, replicators arise (level 3) and mutations are inherited (level 4, E-42),
but later code is not fitter than earlier code by four measures (races E-48/E-49, growth rate E-51, kin-free
invasion E-53/E-54) and no parasites were found (E-66, E-67). Level 5 has been tested only in soups where any
program can meet any other. Spatial structure is the classic condition under which cooperation, parasites and
coexisting lineages appear in artificial-life systems, so the question is whether the negative answer
depends on well-mixing.

**Question:** when the same jumped soups continue with programs that meet only their lattice neighbours,
does later code become fitter than in a well-mixed continuation of the same snapshot?

## Design (fork, not new soups)

**Soups:** the 7 jumped E-54 soups of 2^16 programs (5301, 5302, 5308, 5401, 5402, 5406, 5410; jump rounds T
= 21750, 13750, 12500, 10250, 22250, 16750, 750), each at its **T + 2000 snapshot** (`runs/e54/<seed>-<T+2000>.npy`,
the E-54 "early" time point; uncommitted cache in the main checkout). The snapshots hold programs only; the
generator state was not saved, so no continuation can equal the original run.

**Arms (`scripts/bff_spatial.py`, `ArmSoup`):** each snapshot is placed on a 256 × 256 torus by a seeded
permutation of its rows (`placement`, `default_rng([78, seed])`, the same for every arm) and forked into:
- **M** (well mixed): pairs = `rng.permutation(n)`, exactly `bff.Soup.epoch` (bit-identical, see controls);
- **S** (spatial): each round a perfect matching of lattice neighbours: axis (horizontal / vertical) and
  parity offset (0 / 1) drawn each round, cell (x, y) paired with (x + 1, y) for x ≡ offset (mod 2) (or the
  vertical analogue, with wrap), and one coin per pair for which program runs first. Over rounds each program
  meets each of its 4 neighbours with probability 1/4;
- **M′** (seed null, recommended): a second well-mixed continuation with another seed.

Everything else is E-54's: the same C epoch (`bff_epoch`), mutation 0.00024 per byte per round applied to
the flat array (positions uniform: identical in law in every arm), step limit 8192, mode `bff`, 64-byte
programs. Generator seeds: M `[78, seed, 0]`, S `[78, seed, 1]`, M′ `[78, seed, 2]`. Snapshots every 2,000
rounds after the fork to `runs/e78/<seed>-<arm>-<round>.npy`, plus a 250-round series of steps per pair, HOE
(raw and on a fixed shuffle of the rows, see below), families ≥ 1% and the top family's neighbour ratio.
Forking a snapshot is an intervention on a clone; the original E-54 data are only read.

**Horizon:** **OPEN** (owner's choice); recommendation **20,000 rounds after the fork** (final round T +
22,000), the same span E-54 used between its early and late samples (16,000) plus margin, so that a negative
in S is as strong as E-54's in M. A replicator front in S moves only ~0.1 cells per round into random code
(positive control below), so a new variant needs of the order of 1,000+ rounds to cross the torus; 5,000
rounds would allow only a few sweeps.

## Outcomes

All fitness assays are **common garden and well mixed**: `program_fitness.invasion` unchanged (64 copies
into 4,096 programs sampled from a background, 16 rounds, 16 replicates, paired no-injection control, family
counted with the reverse form). Candidates and kin rule as E-54 (`bff_long_analysis.py`): up to 6 distinct
verified replicators (single `replication_test` pass; D-049: valid as a selection), in order of abundance
among the 40 most common distinct programs; a candidate with ≥ 0.1% of ≥ 90%-identical programs (either
orientation) in the background is dropped and counted.

- **Early group** (shared by the arms): the 6 E-54 early candidates of each soup (T + 2000), re-assayed with
  fresh seeds. **OPEN:** reuse E-54's programs (recommended: same selection, no new randomness) or re-select.
- **Late groups:** the candidates of each arm's final snapshot (and of each intermediate snapshot).
- **Backgrounds (OPEN):** recommended primary = the original E-54 run's T + 10000 snapshot of the same soup
  (E-54's primary background), secondary = its T + 20000 snapshot. Both are well-mixed soups unrelated by
  kin to the late code (to be checked by the kin rule).

**(a) Primary: between-arm fitness change.** For soup k and arm A: Δ_A,k = mean s(late_A,k) − mean
s(early_k) in the primary background. Statistic d_k = Δ_S,k − Δ_M,k (= mean s(late_S) − mean s(late_M),
since the early group is shared), soup as the unit, n = 7. Test: exact one-sided sign-flip permutation test
of Σ d_k > 0 (all 2^7 = 128 sign patterns; the smallest attainable p is 1/128 = 0.008).
- **Pass:** p ≤ 0.05, **and** the seed-null check (d) does not fail.
- **Fail:** p > 0.05 **and** the one-sided 95% upper bound of mean d_k (t, 6 df) is below the effect the
  design can detect, δ* = **0.28 (OPEN)**: no between-arm advantage as large as we could see.
- **Undecided:** anything else, including a failed null check.

**Secondary (reported, not used for the primary verdict):**
1. Within-arm late vs early (E-54's test): D_A = Σ_k Δ_A,k with the within-soup permutation of early/late
   labels (10,000), for S, M and M′.
2. The same statistics in the T + 20000 background.
3. Intermediate snapshots (every 2,000 rounds): d_k(j) and Δ_A,k(j); Spearman ρ of Σ_k Δ_S,k(j) with j.
   **OPEN:** whether this trajectory is pre-registered as a test (cost below) or descriptive only.
4. Reciprocal transplant (**OPEN**, optional): late_S in a sample of the M soup and late_M in a sample of
   the S soup, both at the final round (kin-checked).

**(b) Parasites (D-048 with D-049).** At the final snapshot of every arm (OPEN: also intermediate ones), the
40 most common distinct programs: `program_parasites.alone_test` (10 repeats); those whose generation 1
never grows get `parasite_test` with the arm's own snapshot as the partner pool. A parasite verdict is
confirmed by a second run with an independent seed. Reported: soups with ≥ 1 confirmed parasite per arm,
and the verdict mix. **Evidence for space-dependent parasites** (descriptive, n = 7 cannot make it a strong
test): confirmed parasites in ≥ 2 S soups and in no M or M′ soup (OPEN). Known gap: the partner pool is the
whole (well-mixed) snapshot; a parasite that depends on its local hosts can be missed. A local-pool variant
(partners drawn near the candidate's copies) would be a new detector and needs its own controls first (OPEN).

**(c) Coexistence and spatial structure.** At every snapshot, per arm: the number of 90%-identity families
(either orientation) holding ≥ 1% of the soup (`bff_spatial.families`, greedy from the 200 most common exact
programs), the top family's share, distinct exact programs. For S: the neighbour ratio of each family ≥ 1%
(mean share of a member's 4 neighbours that are members, divided by the family's share; 1 = no clustering)
and the share of the family in its largest 4-connected patch; the same statistic on M's storage order is the
null (≈ 1). **HOE pitfall found in the pilot:** `high_order_entropy` compresses the array in storage order;
in S neighbouring rows are kin, so raw HOE rises with clustering alone (5301: 4.29 → 5.15 in 200 rounds while
HOE on shuffled rows fell to 3.90). Compare arms only with HOE of a fixed shuffle (`hoe_shuffled`).
More families or clustering in S is expected and is **not** level 5.

**(d) Seed null (M′).** d′_k = Δ_M′,k − Δ_M,k gives the arm-vs-arm difference expected from the seed alone.
Null check: the two-sided sign-flip test on d′_k must give p > 0.05 and |mean d′| < |mean d| (OPEN wording);
if it fails, the primary is undecided. The SD of d′_k is the empirical noise of d_k and replaces the planning
estimate below. **Budget:** M′ adds 7 jobs; with 11 workers it costs ~1.6 h more wall time at 20,000 rounds
(9.9 vs 8.3 h), so we recommend including it.

## What would and would not count as level 5

Level 5 in this project means cumulative innovation: later code that is better, and improvements that build
on earlier ones (`docs/research.md`, O5). This design can at most show its first ingredient.
- **Evidence toward level 5 (stated as "directional adaptation under space", not level 5 itself):** primary
  pass **and** within-S D_S > 0 with p ≤ 0.05 (S code improves in absolute terms, not only relative to an M
  arm that declines) **and** the same sign in the secondary background. A rising trajectory over the
  intermediate snapshots (secondary 3) would strengthen it toward "cumulative"; a single step would not.
- **Does not count:** a between-arm difference in drift, diversity, number of families, clustering, HOE or
  steps per pair; a primary pass driven by M getting worse (Δ_M < 0, Δ_S ≈ 0); an effect in one background
  only; parasites alone (that is an ecology result, level-3 ecology, not cumulative evolution).

## Planning numbers

**Controls** (`scripts/bff_spatial.py`; fast ones in `pytest`: `test_spatial_soup_controls`; all in
`--controls`, ~1 min, `runs/e78/controls.json`; export `docs/data/experiments/2026-11-14-e78-groundwork.json`):
- spatial pairs: 200 rounds on 256 × 256 (and an 8 × 6 grid in pytest): every round a perfect matching,
  every pair torus neighbours, all 4 (axis, offset) used, first program on the offset cell 50.0%;
- M through `ArmSoup` = `bff.Soup` bit for bit for 50 rounds, on a random soup of 4,096 (556 steps per pair)
  and on 4,096 programs sampled from snapshot 5301-23750 (2,835 steps per pair);
- positive locality control: a 4 × 4 block of the hand-written replicator in a random 128 × 128 soup, no
  mutation, 300 rounds. S: excess copies ∝ t^1.86, √copies linear in t (R² 0.985 vs 0.890 for exponential),
  at 2.2% share (round 70) neighbour ratio 40 and 99% of copies in one 4-connected patch; 3,833 copies (23%)
  at round 300, still 98% in one patch (front ~0.1 cell/round). M: 16 → 2,636 copies in 40 rounds
  (exponential, R² 0.98 vs 0.89), at 3.2% share neighbour ratio 0.93 and 0.6% in the largest patch;
  saturates (~87%) by round 60;
- deceptive control: under `noexec` both arms leave the array unchanged without mutation, change bytes only
  at recorded mutation positions with it, and the replicator block never grows (16 copies, 300 rounds), while
  its S neighbour ratio stays at 768: clustering alone is not evidence of local spread.

**Timing pilot** (soup 5301 forked at 23,750, 200 rounds per arm, two processes at once): M 0.175 s per
round, 2,712 steps per pair; S 0.149 s, 2,365 steps per pair. M continues like the original: the E-54 log
gives 2,459–2,681 steps per pair and HOE 4.29–4.38 at rounds 23,750–24,250; M gave 2,638–2,858 and
4.32–4.37; families ≥ 1%: 1–3 (snapshots 23,750 / 25,750: 1 / 2); top family 1.0–1.6% (original 1.3%). Exact
equality is impossible (generator state not saved). Under an 11-process load (11 forks, 40 rounds) the cost
is 1.38 × 10⁻⁴ s per round per unit of steps per pair (0.32–1.30 s per round at 2,400–8,100 steps per pair),
about 2.2× the unloaded cost (6 cores, 12 threads, laptop).

**Wall time** (`scripts/e78_power.py`: E-54's logged steps per pair after T + 2000, its last value beyond the
log, loaded cost, longest job first on 11 workers; assumes S costs like M, which the pilot supports):

| Horizon after fork | 2 arms (M, S): wall / CPU | 3 arms (M, S, M′): wall / CPU |
|---|---|---|
| 5,000 rounds | 2.1 h / 15 h | 2.3 h / 22 h |
| 10,000 rounds | 4.2 h / 31 h | 4.7 h / 47 h |
| 20,000 rounds | 8.3 h / 67 h | 9.9 h / 101 h |

Snapshots: 4 MB each; 20,000 rounds × 3 arms × 7 soups = 210 files, ~0.9 GB (cache, not committed).
Analysis (OPEN, estimated): one invasion assay 16 s alone, ~30 s under load; one time point (6 early + 3 × 6
late candidates, 2 backgrounds, 7 soups = 336 assays) ≈ 15 min on 11 workers; parasites (D-049 repeats on
3 × 7 × 40 programs) ≈ 10 min per time point. All 10 intermediate time points: ~4 h.

**Detectable effect at n = 7** (`scripts/e78_power.py`, exact one-sided sign-flip test, α = 0.05, 2,000
simulations; size at δ = 0: 4.6–4.9%). The noise of d_k is not known before M′ is run; three models from the
E-54 export:

| Noise model for d_k | σ | δ for 50% power | δ for 80% power |
|---|---|---|---|
| assay and candidate sampling only (√2 × median SE of a 6-candidate group mean, 0.051) | 0.07 | 0.06 | 0.08 |
| E-54-like heterogeneity, heavy-tailed (resampled differences of E-54's 14 centred late − early deltas) | 0.24 | 0.18 | **0.28** |
| E-54-like, normal (√2 × SD of E-54's 7 deltas, 0.22; 0.09 without soup 5401) | 0.32 | 0.24 | 0.36 |

The realistic model is the middle one: between continuations of one snapshot the late code differs by more
than assay noise (soup 5401's late sample held one family scoring −0.8). So **n = 7 detects a mean
between-arm difference of about 0.3 log units of invasion score with 80% power**; differences under ~0.15
will usually be missed. For scale: E-54's per-soup deltas were −0.49 to +0.19, and the calibration ladder
(J-052) gives s ≈ −1.3 for an invader whose copies fail 10% of the time, so 0.3 is a modest but not tiny
fitness difference. More soups would come only from new jumped soups (~1.5 h per 2^16 soup per core to wait
for a jump, half jump) or from counterfactual-rule soups (E-56, a different rule).

## Prediction (OPEN until the design is fixed)

- Primary pass: **~15%**. E-48 to E-54 found no adaptation in M, and in S the fitness that space favours
  may not show in a well-mixed assay (see weaknesses).
- Within-S D_S > 0 significant: ~15%; both (the "directional adaptation under space" reading): ~10%.
- Confirmed parasites in ≥ 2 S soups: ~10%; in M or M′: ≤ 5% (0 in 3,220 programs in E-66/E-67).
- More families ≥ 1% and neighbour ratio ≫ 1 in S at the end: ~90% (already 45–52 within 200 rounds in the
  pilot); this is expected and is not level 5.
- Level 5 shown by this experiment: < 5% (it cannot show cumulative innovation by itself).

## Known weaknesses

- **Common garden misses advantages that exist only in space** (e.g. resistance to being overwritten by
  neighbours, kin cooperation, local parasite defence). A null result in (a) means "no advantage visible in
  a well-mixed soup", not "no adaptation in S". A spatial invasion assay (a patch of the candidate on a
  grid background) would be a new instrument needing a calibration ladder and controls (OPEN).
- **Home advantage for M:** the backgrounds are well-mixed soups like the one M's code evolved in, so the
  common garden is biased against S, if anything.
- **Placement destroys nothing:** a well-mixed soup has no geometry, so a random permutation onto the grid
  loses no structure; the S arm starts unclustered and has to build its patches (it does within ~50 rounds).
- **n = 7 and one snapshot per soup:** soups are the unit; the fork point is fixed (T + 2000), so the arms
  share their history and early group; results are for standard BFF at 2^16 and mutation 0.00024.
- **Neighbourhood choice:** 4-neighbour matching with one partner per round; an 8-neighbour or random-walk
  mixing would give other results. The matching is chosen because it keeps one interaction per program per
  round, as in M, so time scales match.
- **Background kin:** the late arms descend from the same T + 2000 state as the original's backgrounds;
  kin at 90% identity decayed within 2,000 rounds in E-53/E-54, but in S old lineages may persist locally
  for longer; the kin rule catches it (counted).
- **HOE is geometry-sensitive** (see (c)); steps per pair already differ between arms (pilot: S 13% lower).
- The parasite detector's partner pool is well mixed (see (b)).

## Open choices for the planner / owner

1. Horizon (recommend 20,000 rounds after the fork: ~10 h with M′, plus ~1–4 h of analysis).
2. Include M′ (recommend yes: +1.6 h wall).
3. Backgrounds for the common garden (recommend E-54's original T + 10000 and T + 20000 snapshots); whether
   to add the reciprocal transplant.
4. Early group: reuse E-54's 6 early programs (recommended) or re-select.
5. The fail threshold δ* (0.28 from the power model, or a value the owner considers worth detecting).
6. Intermediate snapshots: pre-registered trajectory test or descriptive; how many are assayed.
7. Whether to build a spatial invasion assay and a local-pool parasite test first (new instruments, with
   their own controls, before pre-registration), or accept the common-garden limitation.
8. Keep the 4-neighbour perfect matching; mutation and step limit as E-54.
