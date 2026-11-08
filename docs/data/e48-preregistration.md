# E-48 pre-registration (written before running)

**Origin (J-047):** after the jump, the most common code drifts far from its founder. Copying
with errors drifts on its own, so drift alone is not adaptation. If the change is adaptive,
programs from later rounds should out-compete programs from earlier rounds of the same soup.

**Samples (E-47 snapshots, exact replays):** for each soup (901, 5006, 5010), with T = the
epoch of the first dominant program in E-47 (`sequences[].species[0].first`: 8750, 27500,
16750), the early sample at T + 1000 and the late sample at T + 10000. From each sample,
the 6 most common exact programs that belong to distinct families (no two >= 90% identical in
either orientation; greedy from the top). Pairs across samples must also be distinct families
(otherwise skipped and reported).

**Races:** `compete_families` (D-043), both orientations counted, 32 races per pair, seed 48.
- Cross-time pairs: late vs early, all 6 x 6 per soup (108 in all, minus skipped).
- Same-time pairs (drift control): early vs early and late vs late, 15 + 15 per soup, with the
  orientation (which program is "a") fixed by sample order.

**Unit of analysis:** a pair with >= 8 informative races; its score = share of races won by the
late program (cross-time) or by the first-listed program (same-time).

**Primary outcome:** among cross-time pairs, the number in which the late program wins more than
half the races; one-sided sign test vs 1/2, p < 0.01.
**Secondary:** pooled late-win share of races; per-soup results; same-time pairs: share of pairs
"ahead" (expected ~1/2) and the spread of shares (how different contemporaries are).

**Predictions:** late ahead in >= 60% of cross-time pairs with p < 0.01 (pooled over soups); at
least 2 of 3 soups in the same direction; same-time pairs ~50% ahead.

**Evidence if confirmed:** adaptive change over time in emergent replicator soups (later code is
fitter than earlier code of the same soup, in a common environment), which is a component of
cumulative evolution. Not level 5 by itself (no open-endedness, one time step, fresh random
soup as the environment).

**Limits:** fitness measured among random programs, not in the evolving soup; non-replicating
common programs give undecided races (excluded); three soups.
