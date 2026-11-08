# E-31 pre-registration (written before running)

**Origin (J-035, D-030):** in E-30, every apparent reproducer in fed FlowLeniaPL worlds was the
food layer condensing; uniform food was unstable in 68 of 100 rules. The perturbed-vacuum null
(D-030) was added after those results, so it needs held-out data, and fed worlds are only
meaningful when the food itself is stable. This scan does both, on new rules.

**Design (`scripts/pl_heldout.py`, commit in the experiment row):**
- Rules: `FlowLeniaPL.random`, seed 31 (E-30 used 30), rule indices 0-199, at food 0.05 and 0.08
  (both below the object threshold 0.2; 0.08 gives 60% more matter to grow on).
- **Stability screen** (per rule and food level): the perturbed food layer
  (`births.perturbed_vacuum`), alone, 160x160, 4000 steps; stable = no object at any 500-step
  checkpoint. Only stable rules go on.
- **Scan:** the first 50 stable rules at each food level (fewer if fewer are stable), the E-30
  world unchanged (6 patches with their own kernel weights, 128x128, 1500 steps), the current
  birth detector (D-028 + D-030; 2 most common object types) and, for any reproducer, the
  heredity test (D-029).
- Pipeline positive: 4 GrayScottTracer ("carried") worlds through the same path; expect a
  reproducer and heredity in >= 3 of 4.
- Pilot (seed 99, 3 rules, 1 world, not part of the sample): only to check that the script runs.

**Primary outcome:** worlds with a reproducer, among stable-food worlds. **Prediction:** 0 at both
food levels (one-sided 95% upper bound then about 6% per food level with 50 worlds).
**Secondary:** fraction of rules with stable food at each level (E-30: 32% at 0.05; prediction:
lower at 0.08); "background" verdicts (should be rare after the screen: the detector's own
perturbed-vacuum run is in a 160x160 world like the screen, so a "background" verdict here means
the parent's surroundings, not the food alone, set off condensation); "one generation" counts.

**Any reproducer** is looked at by eye (frames of the isolation run) and re-run with 3 new start
seeds before any claim; a heredity verdict would be level 3 evidence at most.

**Limits stated in advance:** same world, start and run length as E-30; 1500 steps may be too
short for slow growth; only kernel weights are localized; our mixing rule is not the paper's.
