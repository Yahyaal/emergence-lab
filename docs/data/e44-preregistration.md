# E-44 pre-registration (written before running)

**Origin (J-043):** one-byte variants of emergent BFF replicators looked neutral in head-to-head
contests (2/141 favoured, p = 0.73). The assay only sees large effects. Replicators from
different soups differ in 65-100% of their bytes (pairwise identity 0-33%), so if fitness
differences exist among replicators, contests between unrelated families are where they should
show. A second question: within a soup, does the replicator that dominates later beat the one
that dominated earlier (is the change over time in E-41 adaptive)?

**Measure (`program_selection.compete_families`, D-043, new):** replicators a and b (< 90%
identical), 8 copies each, among 1024 random programs, 96 epochs, no background mutation;
n_a, n_b = programs >= 90% identical to a, b; s = ln((n_b + 1)/(n_a + 1)); 16 replicate soups;
informative if n_a + n_b >= 16. Verdict "a/b favoured" if >= 8 informative replicates, two-sided
sign test p < 0.01 and mean |s| > ln 2; otherwise "no difference" ("undecided" with < 8
informative). Controls (benchmark section 12, passing before this run): hand-written replicator
vs the same copier with a redrawn inert tail -> no difference; vs a redrawn-tail copy with a
broken loop -> a favoured; copyall -> not favoured.

**Competitors:** the 9 emergent replicators of E-42 (soups 901, 5006, 5010; order as in
`docs/data/experiments/2026-11-08-e42-bff-heredity.json`) and the hand-written replicator (H).
- Emergent pairs: all 36 pairs of the 9 (a = earlier in the file).
- H pairs: H vs each of the 9 (secondary).
- Designed null: 12 pairs H vs `retail(H)` with independent tails (neutral by construction).
- Emergent null: for each of the 9 replicators, its E-43 one-byte variant with the smallest
  |mean s| among "no difference" variants, scored with the same 16-replicate criterion
  (`compete_marked`); 9 pairs.
- **Replication:** every pair is run twice with independent random streams (batch A, seed 44;
  batch B, seed 4400).

**Primary outcome:** share of the 36 emergent pairs with a favoured verdict in batch A, compared
with the pooled nulls (21 pairs, batch A), one-sided Fisher p < 0.05.
**Secondary:** (1) of the pairs favoured in batch A, the share whose batch-B mean s has the same
sign (selection-aware: verdicts are confirmed on fresh soups); (2) within-soup, cross-epoch pairs
(901: epoch 9750 vs 16000, 4 pairs; 5006: 28250 vs 32000, 2 pairs; 5010: 17000 vs 32000, 1 pair):
how many favour the later replicator; (3) a ranking (wins over favoured verdicts, batches A+B)
and whether it is transitive.

**Predictions:** favoured in >= 30% of emergent pairs (batch A); at most 1 of 21 null pairs
favoured; Fisher p < 0.05; >= 80% of batch-A favoured verdicts keep their sign in batch B; the
later replicator favoured in a majority of decided cross-epoch pairs.

**Evidence level if confirmed:** differential reproduction among heritable variants (the third
condition for natural selection) for emergent program replicators, in this assay. Still not
level 5: this does not show cumulative change in a running soup.

**Limits:** 9 replicators from 3 soups; contests in a fresh random soup, not the soup of origin;
winner-take-all dynamics; family membership by 90% byte identity (hybrids count for neither).
