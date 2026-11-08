# E-47 pre-registration (written before the replays are inspected)

**Origin (J-046):** in soup 5006 one replicator species (#4) was replaced by another (#5/#6), and
in a controlled race the newcomer beats its predecessor (46/64). Is that typical? If species
turnover after a transition is driven by selection, each new dominant species should beat the
one it displaced; if it is drift, newcomers should win about half the races.

**Data:** exact replays (checked against the E-41 snapshots) of the three soups that transitioned:
901 (from random), 5006 and 5010 (continued from E-40 at 16000 epochs, as in E-41), each to
40000 epochs, snapshots every 250 epochs from 1000 epochs before the E-41 transition.
`scripts/bff_turnover.py --replay`.

**Dominant-species sequence (fixed here):** at each snapshot, the most common exact program d.
Species membership = >= 90% byte identity to the species reference **or its reverse** (all
emergent replicators are mirror replicators). A species' reference is its first dominant
program. A new species starts when d is outside the current species for 2 consecutive snapshots
(same new species both times) and d's species holds >= 5% of the soup. Its reference is d at the
first of those snapshots.

**Races:** each replacement (old reference -> new reference) is raced with
`compete_families` (D-043), both reverses counted, 64 replicates, seed 47.

**Primary outcome:** the number of replacements in which the newcomer wins more than half of the
informative races; one-sided sign test over replacements, p < 0.05 (needs >= 5 replacements to be
able to pass; with fewer, the primary test is reported as underpowered).
**Secondary:** pooled newcomer share of races (binomial vs 1/2); per-replacement verdicts; the
identity of the dominant program to the first dominant program over time (descriptive: does the
soup drift away from its founder?).

**Predictions:** at least 4 replacements in total across the three soups; newcomer ahead in at
least 2/3 of them; pooled newcomer share > 0.55 with p < 0.01.

**Evidence level if confirmed:** repeated selection-driven replacement in running soups, which is
a necessary part of cumulative evolution; level 5 would still need evidence that the changes
accumulate (e.g. later species beat much earlier ones by more, or new functions appear).

**Limits:** three soups; the newcomer/predecessor race is run in a fresh random soup, not the
soup's current background; dominance by exact program count can miss a species split into many
variants.
