# E-75 phase 4 pre-registration: does tile density predict soups under other jump conditions? (D-058)

Written before any phase-4 rule is censused or any phase-4 soup is run. Script: `scripts/sq_phase4.py`.

**Why:** phase 3 (J-080) passed in one corner only: 4 operands, *jump always*. Rules that jump only when the result is
≤ 0 or < 0 run code differently: a program does not always leave its first instruction, and fewer runs halt within
2 steps.

**Seen before writing this (disclosed):**
- The phase-3a development tile census (600 rules, J-080), split by jump condition, for 4-operand rules:

  | Jump | HIGH (D_T ≥ 20) | LOW (D_T ≤ 5) | halt within 2 steps | most tile-copying LOW rules |
  |---|---|---|---|---|
  | ≤ 0 | 8 of 93 | 78 | 52–53% | many copy tiles (21–472 hits per 10^6), none inherit |
  | < 0 | 0 of 80 | 80 | 36–37% | the same (21–623 hits per 10^6); highest D_T is 4 |
  | == 0 | 0 of 64 | 64 | — | no hits at all |

- Timing on two rules: a 10^6-program census takes 3 s, and a soup of each kind had fallen to 3–4 steps per pair
  by round 50. No soup was run longer.

**Pools:** 4 operands, s = ±1, W ∈ {64, 32, 16, 8}, o 0–127, minus the 600 phase-1 rules.
- **Pool A:** jump ≤ 0.
- **Pool B:** jump < 0.

Each pool rule gets a 10^6-tile census (seed 1). D_T is computed as in D-057.

**Groups:**
- **HIGH:** D_T ≥ 20.
- **LOW:** D_T ≤ 5 *and* ≥ 50 tile hits per 10^6. A LOW rule copies tiles, but those tiles do not inherit. This
  makes LOW a deceptive control rather than rules that never copy.
- The thresholds are unchanged from D-057.

**Selection:** in a seed-78 order per group, a candidate is kept if it passes all of these:
- the random-program census at 10^7 finds no replicator (hits may be any number, including 0);
- the census at 10^8 still finds no replicator (D-056);
- a 10^7-tile re-census keeps it in its group (LOW must again have ≥ 50 tile hits per 10^6).

Every selected rule is C or "none" under the old random-program predictor, which says "no jump" for all of them.

**Soups** (as in phase 3): 2^14 programs of 64 bytes, 8,192 steps, mutation 0.00024, up to 16,000 rounds,
inheritance on the top 40 every 50 rounds. Jump T and *frozen* are defined as in phase 3.
- Pool A: 12 HIGH and 12 LOW rules, 6 soups each (144).
- Pool B: 6 LOW rules, plus up to 6 HIGH rules if any pass, 6 soups each.

**Primary (pool A):** it **passes** if all of these hold, and **fails** otherwise:
- HIGH soups jump in ≥ 75% and LOW soups in ≤ 25%;
- one-sided Fisher p < 0.01 over soups;
- at least 6 rules per group.

It is **undecided** if fewer than 6 rules per group pass selection. Prediction: pass (~45%; lower than in phase 3
because the halting race is weaker here, so LOW soups may linger without freezing and give tiles more time).

**Secondary (reported, not part of the verdict):**
1. Pool A per rule (a rule jumps if ≥ 4 of 6 soups do): ≥ 10 of 12 HIGH, ≤ 2 of 12 LOW (~40%).
2. Pool A: ≥ 75% of non-jumping LOW soups are frozen (≤ 4 steps per pair) (~55%).
3. Pool A: median T of HIGH soups ≤ 1,000 rounds (~45%).
4. Pool B: ≤ 1% of rules are HIGH (~70%).
5. Pool B: LOW soups jump in ≤ 25% (~75%).
6. Pool B HIGH rules, if any pass selection, jump in ≥ 75% of soups (no probability given; it depends on whether
   any exist).

**Limits:**
- The rules still have 4 operands and a walking index (s = ±1). Jump "== 0", 3-operand rules and s ∈ {0, 2} are
  not tested. The dev census found no hits for "== 0", and phase 1 found no F rules outside n = 4, s = ±1.
- The D_T thresholds come from the phase-2 pilot. Phase 3 was their first fair test, and this is their first
  test under a different jump condition.
- The LOW tile-hit floor (≥ 50 per 10^6) is new. It was chosen from the dev census, where it keeps most copying
  rules in both pools.

## Outcome (added after the run; J-081)

- **Selection:**
  - Pool A: 150 HIGH and 499 LOW of 980 rules. 12 + 12 selected; 22 + 22 screened. Of the screened HIGH rules, 6
    were F, 4 of them only at 10^8.
  - Pool B: 34 HIGH and 359 LOW of 982 rules. 6 + 6 selected; 11 + 11 screened.
  - Run time: 6.3 h.
- **Primary: fail.** HIGH 29/72 soups jumped (40%), LOW 20/72 (28%); Fisher p = 0.08.
- **Secondary:**
  1. Per rule: 5/12 vs 3/12. **Wrong.**
  2. 52/52 non-jumping LOW soups frozen. **Right.**
  3. HIGH median T = 900. **Right.**
  4. Pool B HIGH fraction: 3.5% (> 1%). **Wrong.**
  5. Pool B LOW: 0/36 jumped. **Right.**
  6. Pool B HIGH: 25/36 (69%, < 75%). **Wrong.** Also, every B HIGH rule has s = +1 and every B LOW rule
     s = −1, so pool B cannot separate D_T from the index direction.
- **Post hoc (not pre-registered; a hypothesis only):**
  - **Freezing is not final.** 73 of the 74 jumped soups had been frozen (≤ 4 steps per pair) at a checkpoint
    before T, and so had 44 of 70 in phase 3. Jumps are escapes from a frozen soup, not the winner of an early
    race.
  - **Copying without inheritance predicts freezing.** The number of random-program hits at 10^8 (copies that
    do not inherit) correlates negatively with jumping:
    - in pool A, Spearman ρ = −0.79 over 24 rules; jumping rules have 43–170 hits, the others 87–1,255;
    - in phase 3, ρ = −0.85; jumping rules have 896–3,341 hits (and 14,280 for W64/o75), the others
      10,078–91,041.
    - This covers phase 3's HIGH exception W8/o56 (88,973 hits, froze), but the thresholds differ about
      twentyfold between the two jump conditions.
