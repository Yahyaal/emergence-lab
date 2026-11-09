# E-60 pre-registration (written before running)

**Origin:** E-57–E-59: with head1 starting at 64, short copiers are mostly self-sufficient (their copy copies
again) and soups jump within a few thousand rounds (16 of 16); with head1 at 0 or 127, no short copier is
self-sufficient and soups are slow (0 of 12, 3 of 24). Three rules. Does the link hold across the whole family
of head-start rules (head1 starts at byte h, h = 0..127)?

**Part A (census, `scripts/bff_headstart.py --part census`):** for every h in 0..127, every kernel of 5 and 6
instructions with non-zero non-instruction filler (as E-55), screened with 1 partner and confirmed with 4, under
that rule; then E-57's self-sufficiency test (copy is itself a copier in ≥ 3 of 4 runs). A rule is **F** if it has
at least one self-sufficient copier of ≤ 6 instructions, else **S**. (Rules 0, 64 and 127 are already known:
S, F, S. Their census here must agree; if not, that is reported and the run is checked before Part B.)

**Part B (soups, `--part soups`):** 4 F rules and 4 S rules drawn at random (numpy seed 60) from each class,
excluding 0, 64 and 127; 4 soups of 2^14 per rule (seeds 6000 + 10·rank + i), E-59 settings and the D-046 jump
criterion as implemented in `scripts/bff_orient_confirm.py` (HOE ≥ 1.0 at 3 checkpoints and a copier under the
soup's own interpreter), up to 16,000 rounds. If either class has fewer than 4 rules (other than 0, 64, 127), all
of its rules are used; if a class is empty, the test is undecided.

**Primary:** jumps in F-rule soups ≥ 12 of 16 and in S-rule soups ≤ 4 of 16, difference significant (one-sided
Fisher p < 0.01).
**Secondary (descriptive):** which h are F (prediction, not tested: h near 64, where a forward copy lands in the
partner without overwriting the copier); copier orientation in jumped soups; the number of copiers per rule vs
jump count (copier count alone should not separate the classes as well as F/S).

**Limits:** 2^14 only; 4 soups per rule; head-start rules are one narrow family of variations of BFF.
