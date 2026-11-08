# E-32 pre-registration (written before running)

**Origin (J-034, Track D):** E-29 found no reproducer among 3000 random single-channel Lenia
rules (0 of 1453 decided). Chan (2020, "Lenia and Expanded Universe") reported self-replicating
creatures once Lenia had several channels and several kernels. Is the single channel the limit?

**Physics:** `MultiLenia` (`emergence/physics/multi_lenia.py`, new): C channels, each kernel reads
one channel and writes to one, growth averaged over a channel's kernels weighted by h, float32
states. Validated before this scan: with one channel and one kernel it equals float Lenia
(unit test, < 1e-6 per step) and the Orbium glider glides (probe section 11); the Orbium glider is
not a reproducer; a rule whose empty world grows matter by itself is "explosive"/"background".

**Design (`scripts/mlenia_lump_scan.py`, commit in the experiment row):** E-29 unchanged except for
the physics and the lump:
- 1000 rules from `MultiLenia.random`, seed 32: C in {2, 3} (equal odds), one self-kernel per
  channel plus 1 to 2C kernels between random channels; per kernel mu ~ U[0.08, 0.40],
  sigma = mu x U[0.05, 0.30], 1-3 rings (as `Lenia.random`), relative radius r ~ U[0.5, 1]
  (R = 13), weight h ~ U[0.2, 1]; T = 10.
- Per rule, 2 lumps (radius 13 and 26); each channel is independent smooth noise in the same disk
  (the E-29 lump per channel). 128x128 vacuum, 300 steps (or the last 25-step checkpoint before
  more than 30% of the world is occupied).
- Birth detector (D-028 with the D-030 perturbed-vacuum null; objects found on the largest
  channel value), 2 most common object types.
- Pipeline positive: 4 Gray-Scott seeds as in E-29.
- Pilot (seed 99, 3 rules, not in the sample): only to check that the script runs and time it.

**Primary outcome:** rules with a reproducer. **Prediction:** 0. If 0, the bound is stated over
*decided* rules (at least one object fully tested), as E-29 learned.
**Secondary:** the settled-outcome split (extinct / objects / filled / explosive) compared with
E-29's (909 extinct, 228 filled, 410 explosive-only, 1453 decided of 3000); counts of "one
generation" verdicts (a gradient towards reproduction, if any).

**Any reproducer** is inspected by eye (isolation frames), re-run alone from 3 new lumps, and
checked against the perturbed vacuum before any claim; it would be level 3 evidence at most
(reproduction without heredity).

**Limits stated in advance:** our random rule distribution is not Chan's (his replicators were
found by search and hand-tuning, with up to 15 kernels); 300 settling steps; one lump shape;
objects are defined on the largest channel, so a creature whose parts sit in different channels
may be split or merged differently than a human would. A null result says "rare under this
distribution", not "absent from multi-channel Lenia".
