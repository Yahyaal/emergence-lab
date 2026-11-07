# E-25 pre-registration: calibrating the mover detector for slow, turning movers (J-022 follow-up)

**Question:** J-022 found the continuous mover detector misses about 8% of wanderers, because
(a) the 100-step isolation run is too short for a slow turner and (b) the in-world
straightness rule (net / path >= 0.5) rejects turning tracks. Can it be fixed without
false positives?

**Change under test** (`observatory/continuous.py`; only ever *adds* detections):
- `SLOW_STEPS`: an object that keeps its mass alone but has not travelled 5 cells after 100
  steps keeps running up to `SLOW_STEPS` steps, checked every 25 steps (mass within 1.4x, at most
  2 objects at every checkpoint; net displacement summed between checkpoints must reach 5 cells).
- `STRAIGHTNESS`: the in-world minimum net / path.

**Variants:** V0 = current (0.5, 100); V1 = (0.5, 300); V2 = (0.25, 300); V3 = (0, 300).

**Worlds (re-simulated from stored specs, last 100 frames as the observer sees them):**
- slow-mover pool: E-18a (160 worlds, wanderer rule) and E-18b (504 worlds, ridge map);
- fast-glider pool: E-14 (640 worlds);
- negative pools with no known creature: E-19b soups (400 worlds), E-12 random-search arm (1040 soups,
  random rules) and E-17 random-search arm (1045 smooth starts, random rules).

**Ground truth for every detection:** the object alone in a 256x256 world for 1000 steps, checked
every 25 steps: exactly one object, mass within 1.4x of the start, path length (sum of 25-step
centroid moves) >= 20 cells overall and >= 10 cells in the last 500 steps. A detection that fails
it is a **false positive**.

**Decision rule (fixed in advance):** adopt the variant with the most ground-truth-confirmed
world detections among those with **zero false positives in the negative pools and no more than one
in all pools together**; if none beats V0 under that rule, keep V0. A variant's per-pool detections
must be a superset of V0's (built in).

**Also reported:** detection counts per pool and variant, extra cost (isolation steps), and
how many detected worlds in each pool are new compared with V0.
