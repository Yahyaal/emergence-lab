# E-75 phase 7 pre-registration: a prospective test of the product census (D-062)

Written before the main run. Script: `scripts/sq_phase7.py`.

**Why:** in phase 6 (J-084), the product rate R_P was measured on 60 rules whose soups had already been run. It
predicted which rules jump (ρ = 0.71) and how fast. But the outcomes were known, and the thresholds below are read
from that data. This phase chooses **new** rules by R_P alone, then runs their soups.

**Rules from phase 6 (training data):**

| Jump rule | HIGH | Training result | ZERO | Training result |
|---|---|---|---|---|
| always | R_P ≥ 5 per 10^8 | 11 rules, 66/66 soups jumped | no informative product in 3 × 10^8 pairs | 0/48 |
| ≤ 0 and < 0 | ≥ 2 products in 3 × 10^8 pairs (R_P ≥ 0.67) | 5 rules, 30/30 | no informative product in 3 × 10^8 pairs | 35/174 (20%) |

The thresholds differ by jump rule because under always, low rates (0.3–2) gave four false positives. Under ≤ 0 and
< 0, any rate above the floor went with jumps.

**Selection** (`scripts/sq_phase7.py`):
- **Pools:** n4 / s = ±1 / W ∈ {64, 32, 16, 8} / o 0–127, for each jump rule (always, ≤ 0, < 0). The 600 phase-1
  census rules and the 60 rules of phases 3–4 are excluded.
- **Order:** candidates are taken in a seed-82 random order per jump rule, in batches of 11, at most 44 per jump rule.
- **Stage 1:** 10^8 random pairs (seed base 82).
  - HIGH candidate: ≥ 5 informative products under always, or ≥ 1 under ≤ 0 / < 0.
  - ZERO candidate: none.
- **Stage 2:** 2 × 10^8 more pairs (seed base 83). Over the 3 × 10^8 pairs:
  - HIGH needs ≥ 15 products under always, or ≥ 2 under ≤ 0 / < 0;
  - ZERO needs 0;
  - and, as in phases 3–4 (D-056), the random-program census at 10^7 and 10^8 must find no replicator.
- **Wanted:** 4 HIGH and 4 ZERO per jump rule (24 rules), in candidate order.
- **Soups:** 6 per rule, exactly as phases 3–4 (2^14 programs, ≤ 16,000 rounds, jump T as D-050 with D-055); seeds
  82000 + 10k + i.
- If a jump rule yields fewer than 4 of a group within its 44 candidates, the experiment goes ahead with what was
  found. The primary needs ≥ 8 HIGH and ≥ 8 ZERO rules in total; otherwise it is **undecided**.
- **Tile density D_T** for each selected rule comes from the stage-1 tile censuses of phases 3–4. It is recorded,
  not used for selection.

**Seen before writing this:**
- All of phase 6.
- A smoke run of the selection code with tiny chunks (2 × 10^5 pairs) and the screen disabled, so the products it
  counted are not the main run's. One always candidate (W16/o39) produced 25 products in 6 × 10^6 pairs. It may hold
  random-program replicators; the screen will decide.

**Predictions** (soups jumped, of 6 per rule):
1. **Primary:** HIGH soups jump in ≥ 75% of soups, ZERO soups in ≤ 25%, and one-sided Fisher p < 0.001 (~60%).
2. **HIGH rules:** ≥ 80% of HIGH rules jump in ≥ 4 of 6 soups (~60%).
3. **ZERO:**
   - under always, ≤ 10% of soups jump (~65%);
   - under ≤ 0 and < 0 together, ≤ 35% (~60%).
4. **Speed:** within HIGH rules, R_P correlates negatively with median T: Spearman ρ < 0, one-sided p < 0.05
   (~40%; only ~12 rules).
5. **Versus tile density:** over the selected rules, ρ(R_P, soups jumped) > ρ(D_T, soups jumped) (~65%).

**Limits:**
- 6 soups per rule.
- HIGH and ZERO rules may differ in other ways (W, s, o) that also matter. R_P could be a proxy for them.
- The selection is stratified by jump rule, and ZERO rules under ≤ 0 / < 0 are expected to jump sometimes (phase 6).
