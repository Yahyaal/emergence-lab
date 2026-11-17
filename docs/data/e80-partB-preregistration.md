# E-80 Part B: amendment to the E-80 pre-registration (written before running)

**Status:** an amendment to `docs/data/e80-preregistration.md` (Part A, commit `75c39a7`). Part A ran as registered
and **failed** (J-095, commit `bebab04`). The owner approved D-068's Option 1 on 17 November 2026. This file fixes Part
B's design before any Part B computation. The driver `scripts/e80b_run.py` is at commit `c529a54`, and this
file is committed alone after it. Its only runs so far are a code-path dry run (`--dry`: tiny seeded soups, not data)
and the resume check.

**Question:** in new, independent soups, does late S code spread farther than late M code of the same soup in a
lattice-native common garden? The soups use the h = 64 head-start rule, so many of them can be made overnight.

## Points resolved before writing

### 1. Rule consistency

Code that evolved under h = 64 is assayed under h = 64. Every assay of Part B, including the garden's own ageing and
every gate control, runs the interpreter `bff_kernels.epoch_h` with head1 starting at 64 (`lattice_assay.assay(..., h1=64)`).
That code path equals Part A's at h1 = 0, checked bit for bit.

Part A's 901 garden and its 5006-species positive are standard-rule objects. They are **not** used. Part B uses:
- **Garden:** made under h = 64 from a soup outside the 16 (seed 8100; spares 8101, 8102, 8103 in that order, the first
  admitted by the same jump rule as the soups).
  - Its fork snapshot (T + 2000) is sampled four times (4,096 programs each, `[80, 210, i]`).
  - Each sample is aged 2,000 rounds on a 64 × 64 torus under h = 64, with S pairing and mutation 0.00024
    (`[80, 211, i]`).
- **Hand-written h = 64 programs:**
  - **H0** = `[.>}]` plus 59 bytes of 0x80, a copier that copies tape[i] to tape[i + 64] until the step limit;
  - **H1** = `<[--]>[.>}]` plus filler, a handicap: H0 behind a trap on the partner's last byte, so it copies only when
    that byte is even (checked on 200 random partners: 100% when even, 0% when odd);
  - **SMEAR** = 0x80 `[.}]` plus filler, which overwrites its partner with 0x80: 94% like itself, none of its
    instructions.

**There is no emergent species-level positive under h = 64.** No pair of h = 64 types with a known fitness difference
exists in the allowed data. Part B's positives are therefore the hand-written handicap (H0 against H1) and an emergent
knockout (the garden's most common copier against the same program with its `.` and `,` bytes replaced by 0x80). Both
compare copiers with crippled copiers. **This validation is weaker than Part A's,** where a whole fitter species was
seen 24 of 24. It shows that the assay registers a loss of copying ability in this garden. It does not show that it
registers the smaller differences selection would produce.

### 2. Validation gate (fixed now; numbers)

All gate controls use the 64 × 64 h = 64 garden, 8 × 8 blocks, T = 64, score A = N_64 / 64 − 1 (assay seeds
`[80, 220, control, replicate]`, garden replicate = replicate mod 4). Part B scores S blocks **only if every criterion
passes**:

| Control | Kind | Replicates | Criterion |
|---|---|---|---|
| G1 | positive, tracking: H0 in random code | 4 | every replicate has N_64 ≥ 192 and ≥ 95% of tagged sites ≥ 90% like H0 |
| G2 | positive, the registered one: H0 vs H1 in the garden, paired (same garden replicate, position and pairing seed) | 24 | mean A(H0) − A(H1) > 0, paired z ≥ 3, H0 ahead in ≥ 18 of 24 |
| G3 | positive: emergent copier vs its knockout, paired | 24 | same criteria as G2; fails if the garden source has no copier among its 40 most common programs |
| G4 | negative: H0 under two labels in one garden | 24 | two-sided sign-flip p ≥ 0.01 (Monte Carlo, 100,000 draws) |
| G5 | selection-aware null: two random-position garden blocks, relabelled | 24 | two-sided sign-flip p ≥ 0.01 |
| G6 | deceptive: SMEAR in a garden of programs that halt at once | 8 | the tag count stays ≤ 64 in every replicate, and summed over the 8 replicates byte identity exceeds the tag count by ≥ 16 sites |
| G7 | deceptive: knockout H0 (persists, cannot copy) in random code | 4 | N_64 ≤ 64 in every replicate |
| G8 | deceptive, label drift: noexec with mutation 0.01, 48 rounds | 4 | N stays exactly 64, 0 tag transfers |
| G9 | kin | all early blocks of the admitted soups (16 per soup) | ≥ 90% of them have kin share ≤ 0.1% in their garden replicate |

G1 to G8 are evaluated as soon as the garden exists (about 1 h into the run). G9 is evaluated after the early, M and M′
blocks are scored, which is still before any S block. **If any criterion fails, Part B is "not testable" and no S block
is scored.** The soups still finish, and their snapshots are kept for a later, newly registered test. A crash in a gate
job stops the run (FAILED) rather than counting as a pass.

### 3. Smallest effect of interest and power

**δ\* is fixed by rule:** δ\* = G2's mean difference A(H0) − A(H1) divided by 2. It is measured in the h = 64 garden
before any S block is scored and recorded in `runs/e80/partB/gate.json` and the export. Continuation noise is measured
by M′ − M across the admitted soups.

**Power, stated as an assumption:** the 16 new soups are assumed to show E-78/Part A noise (SD of a soup's d ≈ 1.96;
Part A measured 1.56 for S − M and 1.96 for M′ − M), and a positive-control-sized effect is taken as Part A's 2.48.
Then, with 16 soups (one-sided t approximation to the exact sign-flip test):
- the nominal power at 2.48 is 0.999, and at 1.24 (half the positive) it is 0.78;
- **after the Holm family: 0.93 at 2.48, and 0.25 at 1.24.**
  - The family now holds 44 p values: 42, plus Part A's, plus Part B's.
  - To survive, Part B's p must be ≤ 0.0020, computed on the current family by bisection.
  - The smallest attainable p with 16 soups is 1/65,536.

So 16 soups can detect an effect the size of Part A's positive control, including after the family correction, if the
new soups are no noisier than E-78's. They cannot reliably detect half of it after correction. These numbers are
assumptions: h = 64 soups of 2^14 programs may have different continuation noise, and the h = 64 positive (G2) may be
larger or smaller than 2.48.

### 4. Soup admission, seeds, times

**Seeds:**
- primary 8001 to 8016;
- spares, in this order: 8017, 8018, …, 8028;
- garden 8100, then 8101 to 8103.

**Prefork:** each soup starts from random code (`HSoup`, generator `[80, 200, seed]`), well mixed under h = 64, with 2^14
programs, mutation 0.00024 and step limit 8,192.

**Jump criterion** (D-047, with the D-053 copy test under the rule's own interpreter). D-045's detector runs the
standard interpreter, so it cannot verify h = 64 copiers (D-046).
- A **candidate** is the first round of a run of 3 checkpoints (every 250 rounds) with HOE ≥ 1.0, provided ≥ 1 of the
  40 most common distinct programs is a copier by `bff_kernels.classify_fid` (h1 = 64, 4 partners, shift-aware, 58/64 +
  75% instruction guard).
- The candidate is **confirmed** if, at the first checkpoint ≥ candidate + 1,000 rounds, at least 10 of those 40
  programs are copiers. Otherwise it is dropped and the soup runs on.
- **T** = the confirmed candidate round.

**Admission:**
- A soup is admitted if it has a confirmed jump; a candidate pending at round 6,000 may still be confirmed.
- A soup with no confirmed jump by round 6,000 is rejected and replaced by the next spare, in order.
- The analysed set is the 16 admitted soups.
- With fewer than 10 admitted soups after the spares, Part B is "not testable". With 10 to 15, it runs with what was
  admitted, and the power statement above no longer holds.

**Fork:** at round T + 2,000. The fork snapshot is placed on the 128 × 128 grid by the permutation `[80, 201, seed]`
(shared by all arms) and is also the "early" group.

**Arms:** M (well mixed, `[80, 202, seed, 0]`), S (128 × 128 torus, E-78 neighbour matching, `[80, 202, seed, 1]`) and
M′ (well mixed, `[80, 202, seed, 2]`). Each runs 10,000 rounds, to T + 12,000.
- Snapshots every 2,000 rounds.
- A checkpoint of programs and generator every 500 rounds; resume is exact (`e80b_run.check_resume`: interrupted =
  uninterrupted, both pairings).

### 5. Analysis (unit: the soup; as Part A unless stated)

**Blocks and assays:**
- 8 × 8 blocks: S cut at seeded random positions of the 128 × 128 lattice (`[80, 231, seed, 3, b]`); Sshuf permutes
  the same block (`[80, 232, seed, b]`); early, M and M′ are random samples laid out at random.
- 16 blocks × 4 seeds per group. Garden replicate `(b + j) mod 4`; assay seed `[80, 230, seed, b, j, gi, arm]`.
- Common random numbers across groups. Score A at T = 64.
- Kin rule: an assay is excluded if its block has > 0.1% kin in its garden replicate.

**Primary:** d_k = mean A(S, preserved) − mean A(M), with an exact one-sided sign-flip test over 2^16 patterns.

**Required reference:** the seed null d′_k = mean A(M′) − mean A(M), two-sided.

**Verdicts, as Part A:**
- **pass:** p < 0.05, mean d > 0, and seed null two-sided p ≥ 0.05;
- **fail:** the upper end of the 95% t interval is below δ\* (rule 3);
- **undecided:** anything else;
- **not testable:** the gate fails, or fewer than 10 soups are admitted.

**Secondaries** (the same named few as Part A):
1. S − early, M − early and M′ − early.
2. S − Sshuf, two-sided.
3. Well-mixed pairing, 8 blocks × 1 seed (early, M, S): S − M, S − early, M − early, and lattice-minus-mixed
   (S − M), two-sided.

There is no second garden: none exists under h = 64.

**Sensitivity:** T = 32; the log score, with its seed null.

**Exclusions:**
- a soup is dropped from a contrast if fewer than half of either group's assays survive the kin rule;
- with fewer than 3 soups the contrast is "undecided (too few soups)";
- a crashed job stops the run (FAILED). The run is restarted with the same command and resumes from its caches; nothing
  is redrawn.

**Stopping rule:**
- **One pass:** everything listed runs once. No interim look at S. Nothing is added after the start.
- **Code frozen:** if code must change after the start, the change and its effect are reported. The verdict stays with
  the registered code unless the bug invalidates it, in which case Part B is "undecided" with the reason stated.

**Multiple comparisons:**
- The primary p joins the E-79 family (`e79-primaries.json`; `holm_primaries.py` rerun), making 44 p values; it must be
  ≤ about 0.0020 to survive.
- The seed null joins the predicted-null list.
- Both raw and adjusted results are reported.

**Peeking:**
- **Before this file's commit:** nothing comparing S with M or S with early was computed. No Part B soup, garden or
  gate control has run; only the code-path dry run and the resume check.
- **What the dry run revealed (disclosed):** it uses tiny seeded soups and an H0-dominated garden, so its G2 to G5 and
  G9 values are meaningless. Its G1, G6, G7 and G8 do not depend on the garden and use the same seeds as the real run,
  so replicates 0 to 3 of those controls are already known: G1 N_64 = 370 to 520 (all tagged sites H0), G7 N ≤ 64,
  G8 N = 64, all passing.
  - **G6 was changed after the dry run.** It showed that under h = 64 the smear overwrites its own code after one
    firing, so byte identity gains only 0 to 11 sites per replicate (74, 64, 64, 75 against a tag count of 64). The
    first criterion (identity ≥ 80 in every replicate) was replaced by the summed criterion above, with 8 replicates
    instead of 4.
  - Replicates 0 to 3 already sum to 21, so G6's deception part is known to pass. The tag part (≤ 64 in every
    replicate) still has to hold in replicates 4 to 7.
- **After the commit:** S and Sshuf blocks are scored only after G1 to G9 pass. The code enforces this: `snapshot()`
  refuses S unless the gate has passed.

### 6. What each outcome would and would not show

- **Pass:** late S code spreads farther than late M code in a lattice garden of the same rule, across 16 independent
  soups. If it survives Holm, it is the first significant evidence in this project of **directional adaptation under
  space**, and evidence toward level 5. Level 5 itself is not assigned: that needs cumulative innovation (O5), which this
  design cannot show.
- **Fail:** no S advantage of δ\* or more (half the handicap difference in this garden). Together with E-78 and Part A,
  this would mean that neither the standard rule nor h = 64 shows a lattice advantage of that size.
- **Undecided:** the new soups cannot separate S from M at δ\*. Their M′ − M spread is reported as the noise estimate
  for any later design.
- **Not testable:** the instrument could not be validated under h = 64 (gate), or too few soups jumped. No statement
  about S.

**Limits, stated now:**
- a different rule from standard BFF (head1 starts at 64; forward copiers);
- soups a quarter of E-78's size (2^14, 128 × 128);
- 10,000 rounds of continuation, half of E-78's;
- one garden, from one h = 64 soup;
- the validation positive is synthetic or a knockout, not a fitter species;
- the 16 soups share the rule and the code version, so they are independent replicates of one condition, not of the
  question in general.
- **The kin rule is weak under h = 64.** It works on whole-program identity at 90%, while a working h = 64 copier can be
  5 bytes (`[.>}]`). Soups that arose independently, and the garden, may carry the same short copy kernel in different
  filler, and the rule will not call that kin. In the dry run, descendants of one seeded copier were already below 90%
  after 700 rounds of mutation. That is shared mechanism, not shared descent, so it is not the E-52/E-53 artefact; but
  the garden is less "foreign" to the focal code than in Part A.

## Commands, code, wall time

- **Code:** `scripts/e80b_run.py`, `scripts/lattice_assay.py` (h1 support) at commit `c529a54`. This file is
  committed alone after it.
- **Launch** (after this file is pushed): from the worktree root,

  ```bash
  mkdir -p runs/e80/partB && systemd-inhibit --what=sleep:idle --why="E-80 Part B" \
    setsid nohup env PYTHONPATH=. /home/yahya/Documents/projects/emergence-lab/.venv/bin/python \
    scripts/e80b_run.py --confirm --workers 11 --out docs/data/experiments/2026-11-17-e80-partB.json \
    > runs/e80/partB/run.log 2>&1 < /dev/null &
  ```

  - Progress goes to `runs/e80/partB/progress.log`.
  - At the end the driver writes `runs/e80/partB/DONE` (verdict, gate) or `runs/e80/partB/FAILED` (traceback).
  - It refuses to start unless this file is committed. A restart with the same command resumes from
    `runs/e80/partB/jobs.jsonl` and the per-soup checkpoints.
- **Expected wall time:** about 9 to 10.5 h on 11 workers (≈ 94 CPU-h).
  - Preforks: 17 jobs, about 20 to 40 min each.
  - Arms: 48 jobs of about 1.7 h each at 0.6 s per round under load.
  - Garden and gate: about 1 h, overlapping the soups.
  - Assays: about 5,500 at ~5 CPU-s, ~45 min.
  - Rejected soups add ~15 min each.
- **Memory:** about 70 MB per worker (measured in the dry run); about 1 GB in all.

## Prediction

| Outcome | Probability |
|---|---|
| Gate passes | ~75% (the risk is G2: hand-written copiers may be swept out of an emergent h = 64 garden before the trap matters) |
| ≥ 16 soups admitted | ~95% (E-57: 8 of 8 jumped within 1,750 rounds) |
| Given a passed gate: pass | ~10% |
| Given a passed gate: fail | ~35% |
| Given a passed gate: undecided | ~55% |
| Survives Holm | ~5% |
| Level 5 shown | 0% |
