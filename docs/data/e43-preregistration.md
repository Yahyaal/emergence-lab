# E-43 pre-registration (written before running)

**Origin (J-042):** mutations in emergent BFF replicators are inherited (E-42, 9/9). Natural
selection also needs variants to differ in how well they spread. Do they?

**Measure (`observatory/program_selection.py`, D-042, new):** competition assay. Parent x and a
one-byte variant m, 8 copies each, among 1024 random programs, 96 epochs without background
mutation; family = programs >= 90% identical to x; s = ln((n_m + 1)/(n_x + 1)) per replicate;
8 replicates; informative if the family reaches 16. Verdict: "variant favoured" / "parent
favoured" if every informative replicate (>= 4) has the same sign and the mean |s| > ln 2;
"no difference" otherwise; "undecided" with < 4 informative replicates.
Controls (benchmark section 12, passing before this run): neutral tail variant of the hand-written
replicator -> no difference; a variant that cannot copy -> parent favoured; neutral pair under
copyall -> undecided.

**Pairs:** all 141 viable mutants of E-42 against their parent (position and value from
`docs/data/experiments/2026-11-08-e42-bff-heredity.json`). **Neutral null:** 24 neutral pairs of
the hand-written replicator (tail positions 27-63, random non-zero value; a zero byte would stop
its copy loop), the same assay. Random stream seed 43. Script `scripts/bff_selection.py`.

**Primary outcome:** share of emergent pairs with a "favoured" verdict (either direction),
compared with the neutral null (one-sided Fisher, p < 0.05).
**Predictions:** "parent favoured" in 5-30% of emergent pairs, "variant favoured" in at most 10%;
at most 1 of 24 neutral pairs gets a favoured verdict; Fisher p < 0.05.

**Evidence level if confirmed:** the three conditions for natural selection (variation,
heredity, differential reproduction) hold for emergent program replicators in this assay. This
is not level 5 (open-ended evolution): it does not show cumulative change in a running soup.

**Limits:** one-byte variants of 9 parents; pairwise contests in small soups (winner-take-all
dynamics, low power for small differences); fitness measured in a fresh random soup, not in the
soup where the replicators arose.
