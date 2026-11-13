# E-75 phase 3 pre-registration: does tile-replicator density predict soups? (D-057)

Written before any phase-3 rule is censused or any phase-3 soup is run. Script: `scripts/sq_phase3.py`.

**Why the predictor changed (disclosed; J-079, J-080):**
- In the phase-2 pilot, the random-program census (F/C) predicted in one direction only: F soups 8/8 jumped, C soups 4/8.
- Fast take-overs were **tiles**: one 4-byte instruction repeated 16 times.
- **Development, after the pilot** (`scripts/sq_tiles.py`, 600 phase-1 rules): a census of 10^6 random tiles per rule. Every F rule has tile replicators, and so do 28 of 100 C rules.
- Among the pilot's 8 rules, the tile-replicator density D_T (per 10^6 tiles) separates the outcomes:

  | Pilot rules | D_T |
  |---|---|
  | F, all jumped | 37–272 |
  | C, jumped | 29, 74 |
  | C, froze | 1, 4 |

  This split was found after seeing the pilot, on 8 rules. It is the hypothesis tested here, not a result.
- **Proposed mechanism:** most random programs in these rules halt within 2 steps (72%). A soup either fills with tiles that copy, or freezes into halters within about 50 rounds. Which happens first depends on how common copying tiles are.

**Pool:** rules with 4 operands, jump always, s = ±1, W ∈ {64, 32, 16, 8}, o 0–127: 1,024 rules. The 600 phase-1 rules are removed, which includes the pilot's 8; 982 remain.

**Groups** (decided by a 10^6-tile census of the pool, D_T estimated from verified hits):
- **HIGH:** D_T ≥ 20.
- **LOW:** D_T ≤ 5, including 0.
- Rules in between are not used.

**Selection:** in a seed-77 order per group, a candidate is kept if it passes all of these:
- random-program census at 10^7: C with ≥ 100 hits (it copies, but no random program replicates);
- at 10^8: still no replicator (up to 5,000 hits verified; D-056);
- a second tile census at 10^7 tiles: still in its group.

The first 12 per group are used. **Every selected rule is C under the old predictor**, so the old predictor says "no jump" for all of them. The test pits the new predictor against the old one.

**Soups:**
- 6 per rule, 144 in all, run as in the pilot: 2^14 programs of 64 bytes, 8,192 steps, mutation 0.00024, up to 16,000 rounds. The top 40 are tested by inheritance every 50 rounds.
- **Jump T:** the first checkpoint with ≥ 1 inheriting program whose checkpoint 1,000 rounds later has ≥ 10.
- **Frozen:** no jump, and ≤ 4 steps per pair at the end.

**Primary:** HIGH soups jump in ≥ 75%, LOW in ≤ 25%, with one-sided Fisher p < 0.01 over soups, and ≥ 6 rules per group.
- It **passes** only if all of these hold.
- It is **undecided** if fewer than 6 rules per group pass selection.
- Otherwise it **fails**.
- Prediction: pass (~50%).

**Secondary (reported, not part of the verdict):**
1. Per rule (a rule jumps if ≥ 4 of 6 soups do): ≥ 10 of 12 HIGH rules jump, ≤ 2 of 12 LOW rules (~50%).
2. ≥ 75% of non-jumping LOW soups are frozen (~70%).
3. Median T in HIGH soups ≤ 1,000 rounds (~60%).

**Limits:**
- The pool is restricted to the knobs where copying is common, so the result says nothing about other jump conditions.
- D_T thresholds come from 8 pilot rules.
- A HIGH rule that is C at 10^8 may be rare (in development, 2 of 42 such rules), so HIGH may fall short of 12. The rule-count condition guards against that.

## Outcome (added after the run; J-080)

- **Selection:** 585 HIGH and 291 LOW rules in the pool. 12 per group selected (275 HIGH and 22 LOW candidates screened).
- **Primary: pass.** HIGH 64/72 soups jumped, LOW 6/72; Fisher p = 1.3 × 10^-24.
- **Secondary:**
  1. 11/12 vs 1/12 rules: **right**.
  2. 66/66 non-jumping LOW soups frozen: **right**.
  3. HIGH median T = 725: **right**.
- **Exceptions:** W8/o56 (HIGH) froze in 6/6; W64/o75 (LOW) jumped in 6/6.
- **Disclosed skew:** 10 of the 12 HIGH rules have s = −1 and o 3–16.
