# E-81: does later code become fitter, and shorter, when program length can change? (pre-registration, written before running)

**Status:** written and committed before any confirmatory soup exists. Groundwork: J-097, D-070 (the rule), D-071 (the
instruments and design); export `docs/data/experiments/2026-11-17-e81-groundwork.json`. The driver is
`scripts/e81_run.py`; the rule is `scripts/bffvl.c` / `scripts/bffvl.py`; the instruments are
`scripts/bffvl_assay.py`, all at commit `be08c21`; this file is committed alone after it. Everything run so far used pilot seeds only (9001–9006, 9101–9102, 9201–9203, 9301–9302,
9401–9410, 10401–10404, dry-run 8991–8997); **the registered seeds 8101–8172 and 8201–8204 have never been run.**

## Question

Finding C: in BFF, replicators arise and mutations are inherited (level 4), but later code is not fitter by any measure
(E-48 to E-54, E-78, E-80). BFF programs are fixed at 64 bytes, which closes the main published route to fitness gain
after emergence, getting shorter (Tierra, Squirm3; J-091). **When program length can change under the same simple,
fixed, reward-free rules (BFF-VL, D-070), does later code become fitter than earlier code, do replicators get shorter,
and does fitness keep rising once they are as short as they can be?**

## The rule (BFF-VL, D-070; fixed)

- A soup is W = 2^20 bytes, split into programs of 4 to 128 bytes. At the start, W random bytes are cut by the rule.
- Each epoch: a random permutation of the programs, consecutive pairs (with an odd count the last sits out). The tape
  A ++ B is run by the BFF instruction set: head0 and the instruction pointer start at 0, head1 at the partner's
  first byte, step limit 8192. A head that would move off either end of the tape halts the run.
- The tape is cut after every byte 0x21 (`!`, a no-op for the interpreter) and wherever a piece reaches 128 bytes; no
  piece is shorter than 4 (a short last piece is merged into the one before, or the last cut moves back). The pieces
  are the new programs. Bytes are conserved.
- Then each byte mutates to a random value with probability 0.00024.

## Design (fixed; code `scripts/e81_run.py`)

**Soups.** 40 primary seeds 8101–8140, each `np.random.default_rng([81, seed])`. Spares 8141–8172, used in seed order
only to replace soups excluded for not jumping, after all primary soups have finished.

**Census.** Every 50 epochs: the 40 most common distinct programs; a program is a **copier** if the copy screen finds
a copy of it in all 4 of 4 random 128-byte partners (`bffvl.is_copier`; a copy = a later piece within ±2 bytes of its
length that matches ≥ 90% of its bytes and ≥ 75% of its instruction bytes). Copier share = bytes held by the families
of the first 10 copiers, over W.

**Jump.** T = the first checkpoint with ≥ 1 copier among the 40 commonest programs whose checkpoint 500 epochs later
has copier share ≥ 0.25. A soup with no such T by epoch 10,000 is excluded.

**Samples.** Early = the copiers at T (up to 5, commonest first); mid = at T + 1,000; late = at T + 10,000;
late2 = at T + 20,000.

**Fitness assay (race; `bffvl_assay.compete`).** Random code of 2^16 bytes (cut by the rule) plus about 1,024 bytes of
each candidate (round(1024 / length) copies); no mutation; 8 epochs; every program is assigned to the candidate it
matches best under the copy rule (ties and non-matches to neither); s = ln((bytes_a + 1)/(bytes_b + 1)) at the end
minus the same at the start. 8 replicates per pair, seeds `[81, soup, primary, i, j]`. Every later copier races every
earlier copier of the same soup (at most 25 pairs). A pair of byte-identical programs scores s = 0 and is counted.

**Primaries.** Unit: the soup. Each is tested one-sided (later fitter) with a sign-flip permutation test (Monte
Carlo, 200,000 sign patterns, since n > 16; p = (hits + 1)/(200,000 + 1)), with a 95% t interval.
- **P1 (adaptation after emergence):** d1 = mean s(mid against early) per soup.
- **P2 (adaptation continues):** d2 = mean s(late against mid) per soup.
- **P3 (adaptation once copiers are minimal):** d3 = mean s(late2 against late) per soup.

**Smallest effect of interest:** δ\* = 0.79 for all three, half the race score of the 6-byte minimal copier `[.>}]!`
against the same copier with one extra no-op byte (s = 1.59, 16 of 16, groundwork control): a later-code advantage
smaller than half of "one byte shorter at the floor" is treated as no adaptation.

**Verdicts (each primary):**
- **fail:** the upper end of the 95% interval is below δ\* (also when p < 0.05; reported as "detectable but below
  δ\*");
- **pass:** not fail, and one-sided p < 0.05;
- **undecided:** otherwise.

**Holm.** P1, P2 and P3 are added to `docs/data/e79-primaries.json` with their source lines, and `holm_primaries.py`
is rerun with `--out docs/data/experiments/<date>-e81-holm<m>.json` (a new file; the E-79 and E-80 exports are not
overwritten). The journal says whether each pass survives the family. With the Monte Carlo test the smallest p is
5 × 10⁻⁶, below the worst Holm threshold (≈ 0.05 / 47 = 0.001).

**Predictions (for the record, from the pilot):** P1 pass; P2 pass (pilot: the last step from 7–9 to 6 bytes often
comes after T + 1,000); P3 fail (pilot: soups settle on the 6-byte copier `[.>}]!` or `[.}>]!`; there is nothing shorter).

## Validation gate (before any race is scored)

1. **Every control in `bffvl_assay.controls()` passes** (18 checks, also in `pytest` and the probe benchmark): the rule
   equals h = 64 BFF with the marker off; conservation and bounds; the halting copier; the copy screen (positives 6–128
   bytes, 200 random programs, broken copier, marker and filler smears, copier under noexec, selection-aware nulls);
   the replicator detector; the race (12- against 24-byte copier, the 6- against 7-byte floor step ≥ 15 of 16, a
   neutral one-byte variant |z| < 3, a short non-copier against a 48-byte copier, the repeat null); the length nulls.
2. **Seeded positive:** 4 soups (seeds 8201–8204) start as random code plus 64 copies of a 48-byte padded hand copier
   (`[.>}]`, 42 random no-op bytes, `!`) and run 1,000 epochs. Pass if in ≥ 3 of 4 the commonest copier is shorter
   than 48 bytes **and** its top copiers beat the ancestor in the race (mean s > 0).

If the gate fails, the verdict is "not testable" and no race is scored; the soups are kept.

## Secondaries (no verdicts)

- **S1 length:** byte-weighted mean length of the copier families at T, T + 1,000, T + 10,000 and T + 20,000; the change
  T → T + 1,000 against a **noexec fork** of the T snapshot run 1,000 epochs (drift of the same families under the cut
  rule and mutation alone).
- **S2 fecundity ("faster"):** complete copies made against random 128-byte partners, and steps per run, per sample.
- **S3:** per-soup T, share and length trajectories; identical pairs per primary.

## Exclusions and stopping

Only soups without a confirmed jump by epoch 10,000 are excluded (and replaced from the spares). No other exclusion. If
fewer than 30 soups are admitted after the spares, every primary is reported as undecided. The run stops when all
admitted soups have reached T + 20,000 and every race is scored. No interim look at any race.

## Pilot numbers this design rests on (exploratory, pilot seeds; J-097)

- **Emergence:** 10 of 10 protocol-pilot soups jumped (T = 600 to 8,250; 9 of 10 by 3,500); 6 of 6 earlier pilot soups.
- **Shortening:** the first copiers were 21 to 128 bytes; within 300 to 700 epochs the shortest copier was 6 to 8 bytes.
- **Noise (SD over soups):** d1 2.18 (mean 8.97, 10 of 10 positive); d2 1.20 (mean 0.90, 8 of 10 positive); d3 0.25
  (mean 0.09; 9 soups within ±0.05, one at +0.79).
- **Seeded positive:** 4 of 4 shortened from 48 to 6 bytes within 200 epochs; descendants against ancestor d = 8.6 to 9.2.
- **Power at n = 40** (normal approximation): P1 at the seeded effect ≈ 1; P2 at δ\* 0.99 nominal, 0.86 at the worst Holm
  threshold; P3 95% interval half-width ≈ 0.08 (about a tenth of δ\*), so a fail would be sharp.

## Projected cost

Protocol pilot (10 soups to T + 10,000, 11 workers, shared machine): 17 to 40 min per soup. P3 extension (10,000 more
epochs): 13 to 25 min per soup. So 30 to 65 min per soup to T + 20,000; 40 soups and 4 seeded soups on 11 workers
(12 cores, `nproc`), plus about 1 min of races: **about 2.5 to 4.5 h**, up to about 5.5 h if spares are needed.

## Launch command

```
mkdir -p runs/e81/run && systemd-inhibit --what=sleep:idle --why="E-81" setsid nohup env PYTHONPATH=.:scripts \
    python scripts/e81_run.py --confirm --workers 11 --out docs/data/experiments/<date>-e81.json \
    > runs/e81/run/run.log 2>&1 &
```
