# E-27 pre-registration (written before running)

**Origin:** the owner asked what could give reproduction and heredity. No birth was ever seen
(E-15, E-20, E-22, E-23), but nothing could have confirmed one: the replication probe only
handles exact discrete shapes and only tests clones we place. v2.2 adds a birth detector for
both physics families (`emergence/observatory/births.py`, D-028) and Gray-Scott
reaction-diffusion (`physics/gray_scott.py`) as a known continuous reproducer.

**Detector (fixed before this run):** an object is copied alone into vacuum and run (continuous
4000 steps, checkpoint every 50; discrete 192 steps, every step). Copies are objects within a
mass factor 2 of the parent (continuous) or of the same shape (discrete). Generation 1 passes if
late copies >= 4 (discrete 3) and more than early, holding >= 75% of the world's matter, and
vacuum alone makes no copies. A "reproducer" also passes generation 2 (one copy, isolated
again). Discrete: scrambled patches that reproduce themselves give "rule-level duplication".

**Validation already measured (calibration, before this run):**
- positives: HighLife replicator; Gray-Scott spots (F 0.0367, k 0.0649 and F 0.022, k 0.059) -> reproducer
- deceptive: Fredkin B1357/S1357 -> rule-level duplication; Seeds -> no; Gray-Scott stripes and
  labyrinths -> no / explosive; Gray-Scott worms (F 0.042, k 0.063) -> one generation; smoothed
  and white noise controls -> no / explosive
- selection-aware null (`scan`, most common object types): Life soups (2), settled Orbium soups (2),
  smoothed noise: 0 reproducers in 24 candidates

**Question:** do the Lenia worlds where we found movers contain reproducers?

**Design:** final states of stored worlds, replayed from their specs (`scripts/birth_scan.py`).
For each world, candidates are the 6 most common object types (`births.scan`) plus every
in-world mover track of the last 100 steps (same criteria as `verify_movers.py`).

- Pool A (movers): every world with a self-propelled structure in E-14 (gliders), E-18 exp. 1
  (wanderer), E-26 (ring glider) and E-24 (Chan patches, 256x256).
- Pool B (blob fields): 100 worlds without movers drawn at random (seed 27) from the same databases.
- Pipeline positive: Gray-Scott F 0.0367 k 0.0649, 10 random soups (`random_state`, 128x128,
  density 0.05), 2000 steps, scanned the same way.

**Primary outcome:** number of worlds with a reproducer in pools A and B.

**Prediction:** 0 in A and B (no reproduction in these Lenia rules); >= 8 of 10 in the pipeline
positive. Any Lenia "reproducer" is inspected by eye and re-tested for a third generation before
any claim; a claim would be evidence level 3 (reproduction), not heredity.

**Not tested here:** heredity; mass-conserving physics (Flow-Lenia cannot pass a test in vacuum).

**Amendment (before any pool A/B result):** a smoke test of the pipeline positive (seed 1) showed
that the pre-registered Gray-Scott soup (`random_state`, 5% of cells) dies out: isolated cells
diffuse away before a spot forms (0 objects at step 2000). The pipeline positive now uses
Pearson's own kind of start: 4 perturbed 12x12 squares (U 0.5, V 0.25 + 1% noise) at random
places, 2000 steps. Prediction unchanged (>= 8 of 10). One pool A world was also smoke-tested
(E-14, 2 candidates, both "no reproduction"); it is included in the run as planned.
