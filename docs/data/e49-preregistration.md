# E-49 pre-registration (written before running)

**Origin (J-048):** E-48 found later code fitter than earlier code in soup 5006 (28/36 pairs) but
not overall (62/108, p = 0.07); its sample included common programs that do not copy themselves,
and its same-round control was ordered by abundance. E-49 repeats the question with those flaws
fixed, on new data.

**Samples:** the E-47 replays (exact), soups 901, 5006, 5010, with T = the E-47 first-dominant
epoch (8750, 27500, 16750). Time points T + 2000, T + 6000, T + 12000 (not used in E-48). At each,
candidates are the most common exact programs in order, skipping any >= 90% identical (either
orientation) to one already taken; each candidate must pass the replicator test
(`replicators.replication_test`, D-040, verdict "replicator", rng seed [49, soup, epoch, rank]);
the first 6 that pass are the sample (at most 40 candidates tried; fewer than 6 -> use those).

**Races:** `compete_families` (D-043), both orientations counted, 32 races, seed 49.
- Cross-time: for each soup and each gap (2000->6000, 6000->12000, 2000->12000), every later
  program vs every earlier one.
- Same-time control: all pairs within each time point, orientation (which is "a") chosen at
  random (seed 4900).

**Primary outcome (program level, conservative):** for each soup, gap and later program, its mean
share of races won against the earlier programs (pairs with >= 8 informative races). Count of
later programs with mean > 0.5; one-sided sign test, p < 0.01.
**Secondary:** pair-level sign test (later ahead in > half the races); per soup; per gap (is the
advantage larger for the longer gap 2000->12000?); same-time pairs (expected ~1/2 ahead).

**Predictions:** later programs ahead at the program level in >= 60% of cases, p < 0.01; soup
5006 in the same direction as E-48; the 2000->12000 gap shows a larger mean share than either
shorter gap; same-time pairs within 40-60% ahead.

**Evidence if confirmed:** adaptive change after the jump, in replicator-verified samples, on
data not used to form the hypothesis. A larger advantage over longer gaps would suggest the
change accumulates (a component of cumulative evolution, still not open-endedness, level 5).

**Limits:** three soups; fitness measured among random programs, not in the evolving soup; the
replicator test counts one orientation (conservative).
