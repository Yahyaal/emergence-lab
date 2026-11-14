# E-71 pre-registration (written before running any E-71 soup)

**Origin:** E-70 (J-072) found, as an exploratory secondary, that among the 15 F rules it ran soups in, the
number of self-sufficient copiers in the census (5–6-instruction kernels whose single copy copies again)
correlated with how fast soups made replicators: Spearman ρ = −0.80, p = 0.0004 (median jump time T per rule).
E-65 had found ρ = −0.51, p = 0.12 within the two-head family. The E-70 result mixes variants (v1 has thousands
of self-sufficient copiers and jumps in 250 rounds), so it could be a between-variant difference rather than a
graded predictor. E-71 tests it on rules not used before, within variants as well as pooled.

**Rules (fixed by the census, before any soup):** every F rule of the E-70 census in variants v1–v5 that E-70 did
not run soups in: 22 rules (`scripts/bff_copiercount.py fresh_rules()`):
v1 h1 = 60, 63, 65, 66, 67, 68; v2 62, 65; v3 61, 62, 63, 67, 68; v4 61, 65, 66, 67; v5 61, 63, 65, 66, 68.
Self-sufficient counts range 1–3,423. v0 F rules are left out (their soups were run in E-61–E-63).
No E-71 soup was run before this was written; the E-70 data above are the only data seen.

**Soups:** 8 per rule (seeds 7100 + 10·k + i), 2^14 programs of 64 bytes, as E-70 (step limit 8192, mutation
0.00024, up to 16,000 rounds). Jump criterion D-050 unchanged except that copiers are counted **every 50 rounds**
(E-70: 250) to resolve fast jumps: T = the first checkpoint with ≥ 1 shift-aware copier (under the rule's own
interpreter, among the 40 most common distinct programs) whose checkpoint 1,000 rounds later has ≥ 10.
Per rule: median T over its 8 soups, non-jumps counted as 16,000.

**Primary 1 (pooled):** Spearman ρ between a rule's self-sufficient count and its median T over the 22 rules is
≤ −0.4, with one-sided permutation p < 0.01 (100,000 permutations). **Prediction:** pass (~65%).

**Primary 2 (within variant):** the sum of within-variant Spearman ρ (variants with ≥ 3 rules: v1, v3, v4, v5) is
negative, with one-sided p < 0.05 against permutations of median T within each variant. This removes any
difference between variants. **Prediction:** pass (~50%; within a variant counts span less and ties at the
fastest times are likely).

**Secondary (exploratory):**
- jump rate: ≥ 75% of the 176 soups jump (E-70's F soups: 60/60);
- the same tests with all copiers (not only self-sufficient) and with the self-sufficient fraction, to see which
  census number carries the information;
- a built-in contrast in v1: h1 = 60 and 68 have 1 and 18 self-sufficient copiers (68 has 4,317 copiers in all)
  against 1,525–3,423 for h1 = 63–67. Prediction: both low rules are slower than every high rule.

**Limits:** one language family (BFF variants), hand-picked variants; 8 soups per rule; jump time at 50-round
resolution; the census counts 5–6-instruction kernels only; a graded relation between a census number and
speed is a level-3 (predictive) claim at most and says nothing about level 5.
