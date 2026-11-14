# E-66 pre-registration (written before running)

**Origin:** E-54 (J-066) reported that only 22–78% of the 40 most common distinct programs in each snapshot of the
7 jumped long soups are verified replicators; ~20% got "no replication" and ~30% "one generation". The plan was to
ask whether the non-replicators are **parasites** (copied by the replicators, not by themselves). A new detector
was built for that (`emergence/observatory/program_parasites.py`, D-048; benchmark section 14: positive, two
negatives, two deceptive controls, selection-aware null, all pass). Before using it, a pilot on 4 + 3 "no
replication" programs from snapshots 5301@41750 and 5308@32500 showed that **the replicator test itself is
unreliable for them**: the same program got "replicator" with some seeds and "no replication" with others
(generation 1 from K = 8 copies sometimes dies out by chance and sometimes grows to ~500). So the E-54 fractions
may mostly measure establishment luck, not the absence of copying. These 7 pilot programs are part of the data
below (the pilot is why part A exists; its outcome motivated P1).

**Tool:** `scripts/bff_parasites.py`; `program_parasites.alone_test` (`replicators.replication_test`, unchanged,
repeated 10 times with independent seeds; "self-copier" if generation 1 grows in any repeat) and
`program_parasites.parasite_test` (unchanged after this commit).

**Part A (reliability):** all 2,800 E-54 rows (70 snapshots × 40 programs, `verdicts` in
`docs/data/experiments/2026-11-08-e54-long-soups.json`), 10 repeats each, seeds `[66, soup, epoch, rank]`.
Null (selection-aware): two fresh 2^14 soups (seeds 6601, 6602) run 2,000 epochs (pre-transition; checked by
high-order entropy < 1 and by eye), their 40 most common distinct programs (same `distinct_top` selection as
E-54), same repeated test.

**Part B (parasites):** rows whose generation 1 never grew (0/10 here and "no replication" in E-54): parasite test
with the row's own snapshot as partner pool (M = 256 partners × 2 orders, 4 scrambles, 2,048 production pairs).
Hosts: share of partners that made copies that are like (≥ 90%, either orientation) a self-copier of the same
snapshot (part A).

**Predictions:**
- **P1 (primary):** among the E-54 "no replication" rows, ≥ 60% (pooled) grow in at least 1 of 10 repeats, and
  ≥ 50% in at least 5 of 7 soups. (~80% confident, given the pilot.)
- **P2:** of all 2,800 rows, ≥ 85% are self-copiers by the repeated test (E-54 single test: 61%).
- **P3 (null):** 0 self-copiers among the 80 null programs.
- **P4 (part B, low confidence ~40%):** true non-copiers are ≤ 10% of rows; among them parasite + by-product
  ≥ 50%.

**Consequences fixed in advance:** if P1 holds, J-066's sentence "only 22–78% of top-40 programs are verified
replicators" is corrected in the report and journal to the repeated-test figure, and single-test verdicts on
common soup programs are treated as lower bounds from now on (D-049). E-54's primary result (invasion of
verified replicators) is unaffected: it used programs that passed.

**Limits:** BFF standard rule only; snapshots of 7 soups; the parasite test is mean-field (pair rates with
partners drawn from a snapshot), not a soup-level test.
