# E-75 phase 2 protocol: pilot soups (exploratory; written before running)

Design: `docs/data/e75-design.md` (phase 2). Phase 1: J-078. Selection rule: D-056.

**Seen before writing this (disclosed):**
- phase 1 (J-078);
- the candidate draw below;
- a timing run of 50 rounds in two soups that are not used here:
  - n4/always/s+1/W8/o12 (F): 0.5 s per round, with all 40 most common programs inheriting at round 50;
  - n4/j<0/s−1/W16/o40: 0.001 s per round, 0 of 40.

**Stage 1: re-census (D-056).** Script: `scripts/sq_pilot.py`.
- **Candidates:** 6 F and 6 C rules from the phase-1 census, drawn in a seed-76 order.
  - F: F at 10^7 with ≥ 3 replicators.
  - C: C at 10^7 with ≥ 100 hits, restricted to 4 operands and jump "always". This matches the F rules on the knobs that phase 1 found necessary, so C is a strict control.
  - F draw: n4/always with s+1/W32/o120, s+1/W32/o44, s−1/W64/o68, s+1/W16/o44, s+1/W64/o94, s+1/W16/o35.
  - C draw: n4/always with s+1/W32/o64, s−1/W16/o32, s−1/W8/o72, s−1/W32/o15, s+1/W8/o126, s−1/W8/o84.
- **Re-census:** each candidate is censused again at 10^8 random programs (new seed), with up to 5,000 hits verified.
- **Selection:** the first 4 of each list that keep their class are used.
- **Limit:** C rules with many hits have only 5,000 of their hits verified, so "stays C" is a 5,000-hit check, not a full one.

**Stage 2: soups.**
- **Setup:** 2 soups per selected rule (16 soups): 2^14 programs of 64 bytes, 8,192 steps, background mutation 0.00024, up to 16,000 rounds.
- **Every 50 rounds:** the 40 most common programs are tested by inheritance (D-055, primary), by the whole-program copy test with guard, and by HOE (both reported beside it).
- **Jump T:** the first checkpoint with ≥ 1 inheriting program whose checkpoint 1,000 rounds later has ≥ 10.
- A soup stops once T is known.

**Predictions (exploratory pilot; not a confirmatory test):**
1. **Gate:** at least one F soup jumps (~95%). If none does, phase 3 is redesigned or dropped (design).
2. At least 7 of 8 F soups jump (~80%), with a median T ≤ 500 rounds (~65%).
3. At most 2 of 8 C soups jump within 16,000 rounds (~50%). C rules copy a lot, and a soup can evolve replicators that are rarer than 1 in 10^8 random programs.
4. In jumped F soups, the whole-program test finds < 10 of 40 at T + 1,000 in at least half of them (~60%; replicators that rewrite their own body, as in J-077).

**Use:** pilot rules are excluded from phase 3. Phase 3's pre-registration sets run length and the expected jump rates from this pilot.

## Outcome (added after the run; J-079)

- **Re-census:** all 6 F candidates stayed F. One C candidate (n4/always/s+1/W32/o64) turned F (2 replicators at 10^8) and was dropped.
  - Used, F: s+1/W32/o120, s+1/W32/o44, s−1/W64/o68, s+1/W16/o44.
  - Used, C: s−1/W16/o32, s−1/W8/o72, s−1/W32/o15, s+1/W8/o126.
1. Gate: **passed** (8 of 8 F soups jumped).
2. **Right:** 8/8, median T = 100 rounds.
3. **Wrong:** 4 of 8 C soups jumped (W8/o126 at 50 and 50; W32/o15 at 2,400 and 6,150). The other 4 froze into programs that halt at once.
4. **Wrong:** the whole-program test agrees with inheritance in 7 of 8 jumped F soups.
