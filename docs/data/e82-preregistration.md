# E-82: do parasites arise when programs can borrow a persistent neighbour's code, and does an arms race follow? (pre-registration, written before running)

**Status:** written and committed before any confirmatory soup exists. Groundwork: J-099, D-072 (the rule), D-073 (the
instruments and design); export `docs/data/experiments/2026-11-18-e82-groundwork.json`. The rule is `scripts/bffx.c` /
`scripts/bffx.py`; the instruments are `scripts/bffx_assay.py`; the driver is `scripts/e82_run.py` (seeded gate in
`scripts/e82_seeded.py`), all at commit `e980084`; this
file is committed alone after it. Everything run so far used pilot seeds only (9501–9505, 9601–9604, 9621–9630, 9690,
9701–9710, and the control seeds inside `bffx_assay.controls`); **the registered seeds 8301–8372, 8381–8384 and
8391–8394 have never been run.**

## Question

Finding C: BFF replicators arise from random code and mutations are inherited (level 4), but later code is not fitter
(E-48 to E-54, E-78, E-80), and no parasites were found (E-66, E-67). E-81 showed that the one lever BFF-VL opens,
shortness, ends at a 6-byte floor. The literature's other route, parasites and the arms races they drive (Tierra:
parasites, immunity, hyper-parasites; Stringmol), needs persistent bodies and the ability to run another program's
code; in BFF a pair is joined, run once and split, so a parasite has nothing to borrow (J-091). **Under simple, fixed,
reward-free rules that let a program's run borrow a persistent neighbour's code (BFF-X, D-072), do parasites (programs
copied by others' machinery that cannot copy themselves alone) arise from random code; and if so, does the soup then
keep changing in a directed way (hosts that resist, parasites that adapt)?**

## The rule (BFF-X, libmode neighbour, D-072; fixed)

- Everything of BFF-VL (D-070): a soup of W = 2^20 bytes split into programs of 4 to 128 bytes (random start cut by
  the rule); each epoch a random permutation and consecutive pairs (an odd last program sits out); the tape A ++ B
  run by the BFF instruction set with head0 and the instruction pointer at 0 and head1 at B's first byte, step limit
  8192, a head that would leave A ++ B halts the run; the tape cut after every `!` (0x21) and at 128 bytes, no piece
  under 4; mutation 0.00024 per byte per epoch.
- **The one change:** for each pair a third program C is drawn uniformly (with replacement) from the soup as it was
  before the epoch. The instruction pointer runs through A (its live bytes) and then through C's code instead of B's.
  C is read only: no head can reach it, so its body is unchanged by the run. B's code never runs. An instruction
  pointer that leaves A ++ C ends the run; brackets are matched across A ++ C.
- So a program whose run falls off its own end without halting executes its neighbour's code on its own bytes. If C is
  a copy loop such as `[.>}]`, the caller is copied into its partner. That is a parasite in Tierra's sense. Nothing
  rewards copying.

## Design (fixed; code `scripts/e82_run.py`)

**Soups.** 40 primary seeds 8301–8340, each `np.random.default_rng([82, seed])`, libmode neighbour. Spares 8341–8372,
used in seed order only to replace soups excluded for not jumping, after the primary soups have finished. Four null
soups 8381–8384 under libmode none (nothing can be borrowed), run to S1 only.

**Hosts and jump.** Every 50 epochs: the 40 most common distinct programs; a **host** is one that copies itself into
4 of 4 random 128-byte partners with nothing to borrow (`bffx.is_copier`, libmode none; copy = a later piece within
±2 bytes of its length, ≥ 90% of its bytes and ≥ 75% of its instruction bytes). Host share = bytes held by the
families of the first 10 hosts, over W. **T** = the first checkpoint with ≥ 1 host whose checkpoint 500 epochs later
has host share ≥ 0.05. A soup with no T by epoch 10,000 is excluded.

**Samples** at S1 = T + 1,000, S2 = T + 5,000 and S3 = T + 10,000: hosts = the 5 commonest hosts; parasites = the first
5 programs, in order of commonness among the 40 commonest non-hosts, that the parasite detector calls "parasite".

**Parasite detector** (`bffx_assay.parasite_test`, D-073; pool = 4,096 programs drawn from the snapshot, seed
`[82, soup, k]`): in this order, "self-copier" if it copies itself in any of 32 runs against random partners and random
libraries or its family grows in any of 4 replicator tests in random code; "not copied" if, run first with partner and
library drawn from the pool (x-like programs excluded; 256 runs), it leaves a copy in under 2% of runs;
"host-independent" if pool libraries do not copy it more often than random-code libraries (one-sided Fisher,
p ≥ 0.01); "context self-copier" if it copies itself with no library at all in ≥ 2% of 64 runs; "by-product" if its
templated share F < 0.5 (x-like programs made per epoch from x's own runs, against those made de novo by 2,048 pool
triples without it); otherwise **"parasite"**.

**Interaction score.** Coverage q(P, H) = the share of a random 128-byte partner that parasite P, run first, fills with
copies of itself when host H is its library (copies × len(P) / 128), mean of 32 runs (`bffx_assay.q_pair`); for two
samples, the mean over their 5 × 5 parasite/host pairs.

**Primaries.** Unit: the soup.
- **P1 (parasites arise; a criterion, not a test):** the share of admitted soups with ≥ 1 verified parasite at each of
  S1, S2 and S3. **Pass** if ≥ 0.75, otherwise **fail**. Not in the Holm family (no p value; see below).
- **P2 (directed host–parasite change, time-shift):** RQ = mean over i < j of [q(P_j, H_i) − q(P_i, H_j)]: later
  parasites on earlier hosts minus earlier parasites on later hosts. It is positive when later hosts resist earlier
  parasites, when later parasites do better on earlier hosts, or both; swapping the time labels flips its sign, so the
  sign-flip test is the shuffled-time null.
- **P3 (host resistance):** d3 = q(P_1, H_1) − q(P_1, H_3): do the hosts at T + 10,000 resist the parasites of
  T + 1,000 more than the hosts of T + 1,000 did?

P2 and P3 are each tested one-sided (positive) with a sign-flip permutation test (Monte Carlo, 200,000 sign patterns;
p = (hits + 1)/(200,000 + 1)) and a 95% t interval. A soup with no parasite or no host at a sample has its undefined
terms left out of RQ, and is left out of P3 if S1 has no parasite or S1 or S3 no host.

**Smallest effect of interest:** δ\* = 0.10 for P2 and P3, half the time-shift score of the graded built-in control
(1 of 5 later hosts is the designed resistant host, the others plain: RQ = 0.19; `bffx_assay.controls`). A
smaller arms-race signal than "a tenth of the host sample resists" is treated as none. Coverage has a small length
artefact (a parasite whose length does not divide 128 leaves the remainder of the partner uncovered: 12- against
14-byte parasites give RQ 0.047 with no resistance); it stays below half of δ\*, and the soups' parasites are 4 bytes.

**Verdicts (P2, P3):** **fail** if the upper end of the 95% interval is below δ\* (also when p < 0.05; reported as
"detectable but below δ\*"); **pass** if not fail and one-sided p < 0.05; **undecided** otherwise.

**Holm.** P2 and P3 are added to `docs/data/e79-primaries.json` with their source lines after scoring, and
`holm_primaries.py` is rerun with `--out docs/data/experiments/<date>-e82-holm49.json` (a new file; the E-79, E-80 and
E-81 exports are not overwritten). P1 is entered with family "excluded" (a criterion without a p value). The journal
says whether a pass survives.

**Predictions (for the record, from the pilot):** P1 pass; P2 fail; P3 fail.

## Validation gate (before any sample is scored)

1. **Every control in `bffx_assay.controls()` passes** (16 checks, also in `pytest` and the probe benchmark): the rule
   equals BFF-VL with libmode live, bit for bit; conservation and bounds; the read-only library and the copied inert
   program; nothing copied with nothing to borrow; host detector (hand hosts of 8, 24 and 48 bytes; random program,
   hand parasite, dead host); parasite detector (hand parasite among hand hosts; random program and host; common dead
   host and common host fragment; by-product made by makers; the plain parasite among resistant hosts and the
   key-matched parasite; the top 20 programs of an epoch-50 soup); the time-shift assay (designed arms race, the graded
   1-of-5 control, change of length without resistance and the coverage length artefact, reversed time labels).
2. **Seeded positive** (`e82_seeded.early`, seeds 8391–8394): random code (2^20 bytes) plus 64 hand hosts (`[.>}]`, 6
   filler bytes, `!`; 12 bytes) and 64 hand parasites (7 filler bytes and `!`), mutation on, 10 epochs; arm P has the
   parasites only. The parasite family first shrinks in both arms; rebound = max(copies, epochs 4–10) / min(copies,
   epochs 1–3). Pass if rebound ≥ 2 with hosts and < 1 without, in ≥ 3 of 4 seeds.

If the gate fails, the verdict is "not testable" and nothing is scored; the soups are kept. The none-arm soups are
reported beside the gate (their parasites at S1 under their own rule), not as part of it.

## Secondaries (no verdicts)

- **S1 composition:** host share and verified-parasite family share at S1–S3; verdict mix of the tested non-hosts; host
  and parasite lengths; whether the commonest host changed between S1 and S3 (host turnover).
- **S2 the full Q matrix** per soup (3 × 3), parasite and host main effects.
- **S3 per-soup T** and trajectories; the none-arm null.

## Exclusions and stopping

Only soups without a confirmed jump by epoch 10,000 are excluded (and replaced from the spares). No other exclusion.
If fewer than 30 soups are admitted after the spares, every primary is reported as undecided. The run stops when all
admitted soups have reached S3 and every score is computed. No interim look at any score.

## Pilot numbers this design rests on (exploratory, pilot seeds; J-099)

- **Emergence** (5 soups per libmode, 4,000 epochs): neighbour 5 of 5 made hosts (first at epoch 200 to 1,400; host
  share ≥ 0.05 by 900 to 1,900), and parasite candidates appeared at the same checkpoint as the first host in every
  soup; the soups settle with host families at 10–12% of the bytes beside a crowd of 4-byte programs (`!!!!`, `![.!`,
  `...!`). Under libmode none (nothing to borrow) hosts took 45–84% of the bytes and no parasite is possible.
- **Protocol pilot** (`e82_run.py --pilot 9701-9710`): 10 of 10 jumped (T 400 to 2,950); verified parasites in 10 of
  10 at all three samples (P1 share 1.0). Hosts `[.>}]!` (8 soups) or `[.}>]!` (2 soups, replaced by `[.>}]!` by S3);
  parasites are 4-byte programs. **RQ mean 0.004, SD 0.013** (9 of 10 exactly 0); **d3 0 in 10 of 10**. Coverage is
  1.0 for almost every pair: every host copies every parasite.
- **Seeded positive** (seeds 9621–9630): rebound with hosts 3.7 to 18 (10 of 10 ≥ 2), without hosts < 1 in 10 of 10.
  Over 2,000 epochs (seeds 9601–9604) the 12-byte hosts shortened to `[.>}]!` and the designed 8-byte parasite was
  replaced by 4-byte ones; the hosts never stopped copying the ancestral parasite (q 1.0 in 4 of 4).
- **Power** (n = 40, pilot SD 0.013): 95% interval half-width ≈ 0.004, a fortieth of δ\*; power at δ\* ≈ 1 even at
  the worst Holm threshold (0.05/49). A pass would need a signal the pilot did not show; a fail would be sharp.

## What each outcome will and will not mean (added before any registered seed ran)

- **Parasites are close to built in.** Any program whose run falls off its end without halting is copied by a
  neighbour copy loop; random code and host debris supply such programs at once (inert 4-byte pieces). **A P1 pass
  therefore shows that the borrowing rule turns host debris into parasites as soon as hosts exist**, from random code
  and without a designed ancestor. It answers the first half of the question for this rule. It is not a surprising new
  capacity and does not by itself move the evidence level.
- **An arms race is not favoured by construction, and probably not possible here.** The library is read only and the
  soup is well mixed, so a host gains nothing for itself by refusing callers: a resistant host as the library spares
  some third program from being overwritten, a public good; and resistance costs bytes, which the byte budget punishes
  (E-81). Kin are not nearby, so no kin benefit either. **A P2 or P3 fail is then the expected result for this
  geometry**: it would show that persistent, borrowable code plus parasites is not enough for directed change in a
  well-mixed soup, and point to what Tierra had and BFF-X lacks (local memory, so a host's refusals protect its own
  offspring; or a cost to the host of being used). It would not show that parasites never drive arms races in program
  soups.
- **A P2 or P3 pass** would be the informative surprise: hosts at T + 10,000 refusing T + 1,000 parasites, or
  parasites adapting to hosts, in a rule where resistance pays no individual. It would need a follow-up that names the
  mechanism (which bytes changed; whether the resistant hosts are the descendants of resistant variants; a lineage
  check) before any claim. Even then it would be **directed coevolution under one rule, not level 5**, which needs
  continuing innovation shown by a validated open-endedness measure.
- **Floors.** Hosts still end at the 6-byte `[.>}]!` (E-81), and parasites at the 4-byte minimum length. Shortness is
  still a lever; parasitism is the second one this rule opens. A precise null on P2/P3 says that, with these two
  levers, the soup reaches a host–parasite equilibrium and stops.
- **Scope.** One rule (BFF-X, libmode neighbour; BFF-VL's halting heads and `!` marker plus a read-only library drawn
  from a well-mixed soup), one soup size, laptop scale. Results do not transfer to 64-byte BFF, to the snapshot
  variant piloted alongside (D-072), or to spatial soups.

## Projected cost

Protocol pilot (10 soups to S3 on 10 workers): 22 to 24 min per soup, including the samples. 40 primary soups and 4
short null soups on 11 workers (12 cores, `nproc`): about 1.5 to 2 h; up to about 2.5 h if spares are needed. Gate:
about 1 min. Scores: about 5 min.

## Launch command

```
mkdir -p runs/e82/run && systemd-inhibit --what=sleep:idle --why="E-82" setsid nohup env PYTHONPATH=.:scripts \
    python scripts/e82_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e82.json \
    > runs/e82/run/run.log 2>&1 < /dev/null &
```
