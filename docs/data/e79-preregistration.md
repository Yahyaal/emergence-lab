# E-79 pre-registration: a Holm correction across the pre-registered primaries (D-067)

Written and committed before any adjusted p value is computed. Script to come: `scripts/holm_primaries.py`
(reads `docs/data/e79-primaries.json`, writes `docs/data/experiments/2026-11-16-e79-holm.json`).
No simulation is run. The owner approved D-067 ("follow your recommendations") and D-063 on 16 November 2026.

**Why:** the paper (`docs/paper.md`, section 8) scores 45 experiments with a pre-registered primary and applies no
correction across them. This analysis finds out which passes survive a family-wise correction. Losing
significance is an acceptable, even expected, outcome.

**Seen before writing this (disclosed):** every raw p value below has been public in the journal and the exports
since its experiment ran, and I read the pre-registration files and the exports to build the family. So the raw
p values were known while the family was being defined. What is fixed here is the family, the rules for picking
each p value, and the methods; nothing in them may change after the adjusted values are computed.

## Family

**Scope:** every pre-registered primary test of the 45 experiments scored in `docs/paper.md` Appendix B. For each,
the primary is taken from its pre-registration file in `docs/data/` (all 45 have one), not from Appendix B, which
was compiled from journal wording. Places where Appendix B disagrees with the file are listed in J-092. The
pre-registrations of the experiments Appendix B leaves out as descriptive (E-17, E-20 to E-25, E-27 to E-32,
E-40, E-73, E-75 phases 1 and 2) were also re-read: none registers a primary significance test (their primaries
are counts with a predicted 0, descriptive tables, or protocol checks; E-73 is a re-score of E-70 to E-72, see
below), so no experiment is added. A registered primary found missing from Appendix B would be added and reported
as an addition.

**One p value per registered primary.** Rules:
1. If a pre-registration names several primaries, each one that is a significance test enters the family.
2. If a primary's verdict is a conjunction of a significance test with descriptive thresholds (a minimum share, a
   ratio, a rule count), the test's p value enters, and the original verdict, which also depends on the other
   conditions, is reported unchanged beside it.
3. If a primary passes only when several significance tests all pass (an intersection-union test: E-74's two
   timings), its p value is the largest of the component p values; the components are recorded.
4. A primary that is not a significance test (a descriptive criterion, a count threshold, a census band, an
   equivalence bound, a replay check) is excluded from the family and listed with the reason.
5. A primary whose pre-registered prediction is a null (the pre-registration says the test will be "not
   significant", "not above 1/2", or that the effect will disappear) is listed separately: its p value does not
   enter the family as evidence for an effect. The E-78 seed-null contrast, which had to be non-significant for a
   pass, is listed there too.
6. Re-scores of earlier primaries on the same data (E-73's D-053 re-scoring of E-70, E-71 and E-72) are not new
   primaries. The originally registered p values enter; the re-scored values are recorded for reference.

**Classification fixed now** (pre-registration file → primary):

| Thread | Experiment | In the family | Excluded or listed separately |
|---|---|---|---|
| Lenia | E-13 | sign test across the 8 rules, `self_prop`, each start vs `uniform`: smooth:3, smooth:6, smooth:10, spots at density 0.35 and at 0.10, and patches once (its arm ignores density, Amendment 1): 9 tests, registered α = 0.05/20 | — |
| Lenia | E-14 | two one-sided Fisher tests (density 0.10 and 0.35), α = 0.025 each | — |
| Lenia | E-18 | E-18a one-sided Fisher, smooth:6 vs uniform, α = 0.05 | E-18b (exploratory map) |
| Lenia | E-19 | E-19a two one-sided Fisher tests, smooth vs shuffled, α = 0.025 each | E-19b (descriptive) |
| Lenia | E-26 | one-sided Fisher at density 0.35, α = 0.05 | — |
| BFF emergence | E-41 | — | A: replay and detector check; B: count of transitions (2 to 6 of 12) |
| BFF after | E-42 | — | count of "heredity" verdicts (≥ 7 of 9) |
| BFF after | E-43 | one-sided Fisher, favoured share vs neutral null, α = 0.05 | — |
| BFF after | E-44 | one-sided Fisher, batch-A favoured share vs pooled nulls, α = 0.05 | — |
| BFF after | E-45 | one-sided binomial vs 1/2, pooled primary pairs, α = 0.01 | — |
| BFF after | E-46 | — | outcomes 1, 2, 3 predicted null (listed separately); outcome 4 descriptive |
| BFF after | E-47 | — | sign test over replacements never computed (0 replacements; needed ≥ 5): not recoverable |
| BFF after | E-48 | one-sided sign test over cross-time pairs, α = 0.01 | — |
| BFF after | E-49 | one-sided program-level sign test, α = 0.01 | — |
| BFF emergence | E-50 | one-sided likelihood-ratio test of β > 0, α = 0.05 | — |
| BFF after | E-51 | — | predicted null (listed separately) |
| BFF after | E-52 | — | predicted null (listed separately) |
| BFF after | E-53 | — | predicted null (listed separately) |
| BFF after | E-54 | — | predicted null (listed separately) |
| BFF emergence | E-55 | — | count ratio in a census |
| BFF emergence | E-56 | — | descriptive share of forward copiers |
| BFF emergence | E-57 | Primary A: one-sided Fisher vs E-40's 0/12, α = 0.01 | Primary B: census thresholds |
| BFF emergence | E-58 | Primary A: one-sided Fisher (lower than E-57's 8/8), α = 0.01 | Primary B: census thresholds |
| BFF emergence | E-59 | one-sided Fisher, α = 0.01 | — |
| BFF emergence | E-60 | one-sided Fisher, F vs S soups, α = 0.01 | — |
| BFF emergence | E-61 | Primary 2: one-sided Fisher vs E-60's S soups, α = 0.01 | Primary 1: census band |
| BFF emergence | E-62 | Primary 2: one-sided Fisher, P vs N soups, α = 0.05 | Primary 1: census set equality |
| BFF emergence | E-63 | one-sided Fisher vs E-62's F′ soups, α = 0.01 | — |
| BFF emergence | E-64 | one-sided Fisher, F vs C soups, α = 0.01 | — |
| BFF emergence | E-65 | one-sided Fisher, F vs C soups, α = 0.01 | — |
| BFF after | E-66 | — | P1: descriptive share (P2 to P4 are not primaries) |
| BFF after | E-67 | — | P1: count threshold (≤ 2 of 420 parasites) |
| BFF emergence | E-68 | Primary 2: one-sided Fisher, F vs non-F soups at L ≠ 64, α = 0.01 | Primary 1: census band |
| BFF emergence | E-69 | — | descriptive thresholds on jump fractions |
| BFF emergence | E-70 | Primary 2: one-sided Fisher, F vs non-F soups, α = 0.01 | Primary 1: census band |
| BFF emergence | E-71 | Primary 1: pooled Spearman, one-sided permutation, α = 0.01; Primary 2: within-variant, one-sided permutation, α = 0.05 | — |
| BFF emergence | E-72 | one-sided Mann–Whitney at rule level, α = 0.01 | — |
| BFF emergence | E-74 | one-sided Mann–Whitney at rule level under D-053 and under HOE, both needed (rule 3), α = 0.01 | D-050 timing (reported beside, not primary) |
| SUBLEQ | E-75 ph. 3 | one-sided Fisher over soups, α = 0.01 | — |
| SUBLEQ | E-75 ph. 4 | pool A one-sided Fisher over soups, α = 0.01 | pool B (secondary) |
| SUBLEQ | E-75 ph. 5 | — | the pre-registration states "no single primary verdict; this phase is mainly descriptive" |
| SUBLEQ | E-75 ph. 6 | pool A Spearman ρ, one-sided, α = 0.01 | — |
| SUBLEQ | E-75 ph. 7 | one-sided Fisher over soups, α = 0.001 | — |
| Search engine | E-77 | one-sided exact Wilcoxon signed-rank over seeds, α = 0.01 | — |
| BFF after | E-78 | one-sided exact sign-flip test, α = 0.05 | seed-null contrast (must be non-significant; listed separately) |

That is 42 p values in the family (Lenia 15, BFF emergence 16, BFF after emergence 6, SUBLEQ 4, search engine 1;
the Life-like thread has no pre-registered primary among the 45, so it is empty). If tabulation finds a primary
misclassified here against its file, the correction is made, reported as a deviation, and both results are given.

## Which p value

- The p value reported at the time, for the registered test, as registered: from the experiment's export key, or
  the journal entry or the pre-registration's outcome section when the export lacks it. No test is recomputed
  with a different method.
- A p value reported only as a bound (for example p < 1e-6) is used as that bound, and flagged.
- A p value reported rounded (for example 4 × 10⁻⁴) is used as reported; a more precise committed value of the
  same test, if one exists, is recorded beside it but not used.
- A registered test whose p value was never reported and cannot be read from a committed export is marked "not
  recoverable", unless it can be recomputed exactly from committed counts with the registered test; then it is
  recomputed and flagged "recomputed".
- Every p value is traced to a committed file, with the line or key quoted, in `docs/data/e79-primaries.json`.

## Methods

- **Primary correction:** Holm step-down at family-wise α = 0.05 over all p values in the family. Adjusted
  p_(i) = max over j ≤ i of min(1, (m − j + 1) p_(j)), p values sorted ascending; ties keep input order.
  A primary **keeps significance** if its Holm-adjusted p ≤ 0.05. A **pass survives** if the primary's test met
  its registered α originally and its Holm-adjusted p ≤ 0.05. Also reported, as a stricter reading: whether the
  adjusted p is below the primary's own registered α.
- **Secondary:** Benjamini–Hochberg at q = 0.05 (adjusted p_(i) = min over j ≥ i of min(1, m p_(j) / j)).
- Both are implemented directly and checked against `scipy.stats.false_discovery_control` (BH) and, for Holm,
  against an independent step-down implementation and a published example in a unit test (`statsmodels` is not
  installed in the venv).
- **Sensitivity (a), D-063:** the same family, with the rule-level p value in place of the registered one wherever
  the registered unit was the world or soup and a rule-level test of the same contrast exists in the committed
  record: E-14 (sign test, J-015), E-19 (sign tests, E-19 export), E-75 phases 3, 4 and 7 (`2026-11-14-rate-model.json`
  → `step4_rule_level`). For the E-75 phases the rule-level outcome used is the one their pre-registrations define
  (a rule jumps if ≥ 4 of 6 soups do: `ge4_of_6`); `any_soup_jumped`, which the paper quotes, is reported beside it.
  Elsewhere the registered p value is kept.
- **Sensitivity (b):** Holm within each thread separately: Life-like (empty), Lenia, BFF emergence, BFF after
  emergence, SUBLEQ, search engine.
- **Sensitivity (c), exploratory, added here:** for soup-level Fisher primaries comparing two groups of rules with
  at least 2 rules per group and no committed rule-level test (E-60, E-61, E-62, E-63, E-64, E-65, E-68, E-70), a
  rule-level one-sided Fisher test recomputed from the per-rule soup outcomes in the committed exports (a rule
  "jumps" if any of its soups jumped, as in the paper's tallies A62 to A72), substituted into the family on top of
  sensitivity (a). Single-rule contrasts (E-18, E-26, E-50, E-57, E-58, E-59) have no rule-level test and keep
  their p values. This sensitivity is labelled exploratory everywhere.

## What will be reported

- A table of every primary: experiment, registered test, unit, raw p, registered α and original verdict,
  Holm-adjusted p, BH-adjusted p, and whether it survives; plus the excluded and predicted-null lists with reasons.
- The number surviving Holm, BH and each sensitivity analysis.
- Which statements in `docs/paper.md` lean on results that do not survive, with a short clause added at each.
- Limits: dependence between tests (several reuse the same data or comparators: E-61 and E-63 use E-60's and
  E-62's soups as their comparison arms; E-71 to E-74 and E-75 phase 6 reuse earlier rules; E-14/E-19 share rules),
  p values reported as bounds or rounded, and the primaries excluded.

## Decisions fixed in advance

- Nothing in the family definition changes after the adjusted p values are tabulated.
- A registered primary that Appendix B missed is added and reported as an addition.
- Original verdicts, raw numbers and results are not changed or deleted in the paper; a clause is added where a
  pre-registered pass does not survive Holm.
- Evidence levels are not changed by this analysis unless a level rests on a single primary that loses
  significance; any such change is stated in J-092.
