# E-54 pre-registration (written before running)

**Origin:** with three soups and 10,000 rounds, later replicators are not reliably fitter than earlier ones
(E-48, E-49, E-51; E-52's advantage was kinship, E-53). E-50 showed that soups of 2^16 programs jump within
24,000 rounds about half the time, so more jumped soups and longer gaps are now affordable.

**Run (`scripts/bff_long.py`):** 12 new soups of 2^16 programs (seeds 5400–5411) wait up to 24,000 rounds for
the jump (D-045: HOE ≥ 1.0 at 3 consecutive checkpoints; T = the first). The three E-50 soups that jumped
(5301, 5302, 5308; T = 21750, 13750, 12500) continue from their saved snapshots with fresh random streams.
Every jumped soup runs to T + 20,000, saved every 2,000 rounds.

**Analysis (`scripts/bff_long_analysis.py`, written before the run finishes, assays unchanged):**
- Candidates per jumped soup: up to 6 distinct verified replicators (replicator test D-040; distinct = < 90%
  identical forwards and backwards), taken in order of abundance among the 40 most common distinct programs
  at T+2000 (early) and at T+18000 (late), as in E-49.
- Background: the soup's snapshot at T+10000. Kin check: every candidate's share of ≥ 90%-identical
  programs (forwards or backwards) there must be < 0.1%. A candidate above that is dropped and counted.
- Invasion assay (D-044, `program_fitness.invasion`, unchanged: 64 copies, 4096 programs, 16 rounds,
  16 replicates).

**Primary test:** D = sum over jumped soups of (mean s late − mean s early); one-sided permutation test of
early/late labels within soups (10000), α = 0.05. Soups with fewer than 2 candidates in either group are
excluded (counted).
**Prediction:** not significant (E-53 found no advantage over 10,000 rounds); we give a real advantage
over 16,000 rounds about a 30% chance.

**Secondary:**
1. The same comparison in the T+20000 background (kin-checked the same way): "future" fitness.
2. Descriptive: per snapshot, the share of the 40 most common distinct programs that pass the replicator
   test (does the soup fill with non-copying programs, i.e. parasites or debris?).
3. Number of soups that jump by 24,000 rounds among 5400–5411 (E-50 predicts about half).

**Limits:** as E-52/E-53; continued soups use new random streams after their snapshot; the three E-50 soups
were selected because they jumped (fine for after-the-jump questions, not for jump rates).
