# E-75 phase 6 pre-registration: the product census (D-061)

Written before the main run. Script: `scripts/sq_products.py`.

**Why:** phase 5 (J-083) found two things:
- Rules differ in how often replicators *originate*: 53 of 54 soups of rarely-jumping rules had no origin at all in
  4,000 rounds.
- Each founder was written in a single pair run, mostly from near-random parents.

The earlier predictors (random-program hits, tile density D_T) counted programs that *are* replicators. This one
counts runs that *write* one. If origins set the jump rate, this should predict which rules jump, including in
pool A (jump ≤ 0), where tile density failed (phase 4, J-081).

**Method:**
- Per rule, 3 × 10^8 random pairs (A, B) of 64-byte programs are each run once (8,192 steps, as in the soups).
- Each half of the result that differs from its input is a **product**.
- **Pre-filter (C, `subleq.sq_prefilter`).** A product passes if some 4-byte block of it that is not one repeated
  byte is found in the partner half after each of 2 generations with random partners, in ≥ 1 of 2 lineages.
- Products that pass get the inheritance test (D-055), confirmed with a second RNG (`sq_nucleation.Tester`). Both
  inputs are tested too.
- **R_P** = informative replicator products whose inputs are both non-replicators, per 10^8 pairs. **Null**
  products (the inherited block is all zeros) and products of a replicator input are counted apart.
- Pre-filter hits beyond 5,000 per 10^7-pair chunk are not tested; R_P is scaled up by the tested fraction.
- Seeds: `SeedSequence([80, code, chunk])`.

**Sample:** all 60 rules with 6 soups each from phases 3 and 4. The outcome is soups jumped out of 6 (already
known; the predictor is computed blind to it):
- 24 rules with jump always (phase 3);
- 24 rules with jump ≤ 0 (phase 4, pool A);
- 12 rules with jump < 0 (phase 4, pool B).

So this is a pre-registered test of a new predictor on known outcomes. It is not a prospective test. If it passes,
the next step is a prospective one: choosing new rules by R_P and then running their soups.

**Seen before writing this (disclosed):**
- **Pre-filter recall:** 3,109 of 3,118 informative founders and origins in phase 5 pass the pre-filter (99.7%).
- **Fresh random pairs are much rarer producers than soups' origin bursts suggest.** In 10^7 pairs each, W32/o28 ≤ 0
  and W32/o11 always gave no confirmed product. Phase 5's first origins came after hundreds to thousands of rounds,
  which puts the per-run rate near 10^-8 to 10^-7.
- **Development pilot** (seed 81, 2.2 × 10^8 pairs each; `runs/e75-products-pilot.json`):

  | Rule | Soups jumped | D_T | Confirmed informative products |
  |---|---|---|---|
  | always W32 o11 | 6/6 | 57 | 13 |
  | always W16 o4 | 6/6 | 47 | 132 |
  | always s+1 W8 o125 | 6/6 | 25 | 1,911 (plus 5,773 from replicator inputs) |
  | always s+1 W16 o72 | 0/6 | 0 | 0 (of 10,127 pre-filter hits) |
  | ≤ 0 W32 o28 | 6/6 | 27 | 5 (plus 6 null) |

  An example product is an arithmetic byte sequence (24 18 0c 00 f4 …), written by a near-random program.
- **Baselines on the same 60 rules** (Spearman ρ of D_T with soups jumped): all 0.63, always 0.76, pool A 0.14,
  pool B 0.97. D_T chose the groups (HIGH vs LOW), so these baselines are favourable to D_T.

**Predictions** (Spearman ρ of R_P with soups jumped out of 6, ties averaged):
1. **Primary: pool A.** ρ ≥ 0.5 with one-sided p < 0.01 (~55%).
2. **All 60 rules:** ρ(R_P) > ρ(D_T) = 0.63 (~60%).
3. **Per pool:** always ρ ≥ 0.6 (~65%); pool B ρ ≥ 0.7 (~55%).
4. **No product, no jump:** rules with R_P = 0 (no informative product in 3 × 10^8 pairs) jump in ≤ 10% of their
   soups, all pools together (~60%).
5. **Rate sets speed:** among rules that jumped in ≥ 4 of 6 soups, R_P correlates negatively with the median jump
   time T. Spearman ρ < 0, one-sided p < 0.05 (~55%).

**Also reported:** self-written (side 0) vs partner-written (side 1) products, null products under ≤ 0, products
from replicator inputs, and the number of distinct products.

**Limits:**
- Fresh random pairs are not soup material: soup programs have been rewritten by many earlier runs (phase 4b
  measured them as near-random, but not identical).
- Products are counted, not pairs; one pair can give two.
- The pre-filter can miss a replicator whose block survives only in some lineages (0.3% of phase-5 founders).
- 6 soups per rule, so jump counts are coarse.
