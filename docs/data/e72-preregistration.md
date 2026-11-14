# E-72 pre-registration (written before the fresh census and before any E-72 soup)

**Origin:** E-71 found one F rule (variant 1, head1 at 68) that made no replicators in 8 soups, and another (v1/67)
that was slow. The F test (E-61) checks one generation: does a short copier's copy copy again? E-72 follows
**lineages over 5 generations** (`scripts/bff_multigen.py`): from each self-sufficient kernel, 8 lineages; at each
generation the current program is copied into a fresh random partner, and the copy must itself be a copier
(shift-aware, 4 partners) for the lineage to continue. A kernel is **deep** if ≥ 4 of its 8 lineages reach
generation 5. Per rule: `deep_est` = share of tested kernels that are deep × number of self-sufficient kernels
(at most 300 kernels tested per rule). An F rule is **F-deep** if `deep_est ≥ 1`, else **F-shallow**.

**Seen before writing this (disclosed):**
- Pilot on v1 at h1 = 60, 64, 67, 68: the enumeration reproduces the census counts exactly; at 67 and 68 no
  kernel is deep (copies of copies stop copying), at 64 89% are; v1/60 (fast soups) is also shallow.
- **Part A, the 44 F rules of the E-70 census** (whose soups E-70/E-71 had already run, so explanatory only):
  over the 37 rules with soups, `deep_est` vs median jump time ρ = −0.66 (p = 9e-6), against ρ = −0.44 for the
  one-generation count; the 13 F-shallow rules had median T 2,250 rounds vs 250 for the 24 F-deep (Mann–Whitney
  p = 0.0004). Several shallow rules were nevertheless fast (v1/60 200, v3/67 225, v3/68 350).

**Part B (confirmatory, fresh rules):** 240 rules never run in any census or soup: variant v ∈ 1–5 with **head0
starting at g ∈ 1–127** (all earlier variant rules had g = 0) and head1 at h = g + d, d ∈ 60–68 (mod 128), drawn
with numpy seed 72 (`fresh_rules()`). One-generation census plus depth for each. Up to 8 F-deep and 8 F-shallow
rules picked at random (seed 720), 6 soups each (seeds 7200 + 10·k + i), 2^14 programs, D-050 jump criterion with
checkpoints every 50 rounds, up to 16,000 rounds (as E-71). Per rule: median T, non-jumps = 16,000.

**Primary:** F-shallow rules are slower: the median over shallow rules of their median T is ≥ 3× that of the
deep rules, and a one-sided Mann–Whitney test (rule level) gives p < 0.01. If either class has fewer than 4
rules the result is **undecided**. **Prediction:** pass (~55%: Part A's effect is large, but several shallow
rules were fast there and the new family, with head0 moved, may behave differently).

**Secondary (exploratory):** jump rate by class; Spearman of `deep_est` vs median T and of the one-generation
self-sufficient count vs median T over the picked rules (which predicts better?); how many of the 240 are F.

**Limits:** 5 generations and 8 lineages per kernel is an arbitrary depth; one language family (BFF variants);
6 soups per rule; a rule's census says nothing about longer kernels (> 6 instructions) that soups may also find.
