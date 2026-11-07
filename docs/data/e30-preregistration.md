# E-30 pre-registration (written before running)

**Origin (Track D route 3, research.md; J-033):** heredity needs something that carries a
creature's rule parameters with it. FlowLeniaPL (D-029) stores each cell's kernel weights with
its matter; the transplant heredity test (D-029) can tell inherited traits from traits shared
through place. Plain Flow-Lenia has no positive control (no movers in 480 worlds, J-016/J-018),
and mass-conserving creatures cannot multiply in an empty world, so worlds are **fed** with a
thin food layer. This is a first look: does anything in fed FlowLeniaPL worlds reproduce?

**Design (`scripts/pl_scan.py`, commit in the experiment row):**
- 100 rules from `FlowLeniaPL.random` (2-3 kernels, the paper's ranges, R 13), seed 30.
- Each rule at food 0 (unfed control: a parent cannot double its mass alone, so the birth
  detector cannot pass by construction) and food 0.05 (below the object threshold of A = 0.2;
  20% of the mean initial patch density). Paired: same rule and start at both food levels.
- Start: 6 patches (20x20, A ~ U[0, 1]) at random places in a 128x128 world, each with its own
  weights (the rule's times U[0.5, 1.5] per kernel), on the food layer. 1500 steps.
- Then the validated birth detector (D-028; 2 most common object types; two generations alone in a
  fed vacuum; background null = food alone) and, for every world with a reproducer, the
  heredity test (trait = share of kernel 0 in the weights).
- Pipeline positive: 4 GrayScottTracer ("carried") worlds through the same path: expect a
  reproducer and heredity in >= 3 of 4.
- A pilot (seed 99, 2 rules, not part of the sample) was run only to time the scan (~400 s per world on a busy machine): 0 reproducers in 4 worlds; the Gray-Scott tracer gave a reproducer and heredity (r = 1.0).

**Primary outcome:** fed worlds with a reproducer. **Prediction:** 0 (one-sided 95% upper bound
then 3%). Unfed: 0 by construction (a check of the pipeline, not a finding).
**Secondary:** heredity verdicts if any reproducer; counts of "one generation" and "explosive";
mass drift in unfed worlds (expect < 1e-5).

**Any reproducer** is looked at by eye and re-run with 3 new start seeds before any claim; a
heredity verdict would be level 3 evidence at most (reproduction with inheritance), never level
4-5 without a selection measurement.

**Limits stated in advance:** one food level; 1500 steps; single random patch start; parameter
mixing (not the paper's rule, D-029); only kernel weights are localized (not mu, sigma).
