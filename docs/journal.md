---
title: Journal
description: Chronological research log, newest first.
---

# Journal

Newest first. Each entry records what we did, why, what we found, and what we learned.
Experiment IDs (E-xx) link to the [Experiments]({{ '/experiments.html' | relative_url }}) page and decision IDs (D-xxx) to [Decisions]({{ '/decisions.html' | relative_url }}).

**How to add an entry** (people and agents): copy the template at the bottom, put it at the top, and fill in the commit hashes and experiment IDs. Keep claims at the evidence level actually reached.

---

## J-019 · 2026-11-07 · E-17: searching from smooth starts finds a new mover, a slow "wanderer"

**Question (pre-registered, `docs/data/e17-preregistration.md`):** E-12 searched from soups, which never make gliders (E-14). Searching from smooth starts instead, does the engine find mover rules, does it beat random search, and does it find any outside the Orbium island?

**Ran:** E-17, identical to E-12 except `--init smooth:6`, seed 17. Engine 6 min, random 7 min (the faster census helped; E-12 took 12 + 14.5 min). Commit `9ba8254`.

**Found:**
- **Raw hits (any run with a self-propelled structure):** the engine has 5 universes in 2 rules, random search 1 universe in 1 rule. All lie **outside** the single-ring island of E-13a.
- **Pre-registered verification (alone for 1000 steps):**
  - **μ 0.357, σ 0.0456, 2 rings (both arms): fails.** Its "mover" is a field chunk of mass 2275 that falls apart. Not a creature.
  - **μ 0.243, σ 0.0224, rings 1/0.5/0.5 (engine only): passes in all 5 objects, from 4 universes.** One is a screening run; three are follow-ups (new seeds and a 2× larger world), so it reproduces.
- **Primary outcome:** **engine 1 verified mover rule, random 0.** Tiny numbers and one seed per arm, so no significance claim (as pre-registered).
- **The new mover is a "wanderer", not a glider.**
  - **Size and shape:** compact, mass about 115 (Orbium: 70), with an internal pattern that keeps changing.
  - **Speed:** 0.07–0.08 cells/step, about 8× slower than Orbium.
  - **Path:** it **turns as it goes**. Direction correlation between successive 50-step stretches is 0.65–0.79. Over 2000 steps alone, its net displacement is 0.08–0.55 of its path; one copy nearly circles.
  - It moves by itself, so it passes the self-propulsion test, and it is clearly different from Orbium.
- **Other outcomes:** 0 rules `complex` on every seed in either arm. "Structured" rules: 103 (engine) vs 29 (random).

**Interpretation:** smooth starts make the search see movers it was blind to under soups, and the engine finds one random search did not. The evidence is thin, one rule and one seed per arm, but it is a reproducible, verified creature of a different kind, in a different part of rule space (3 rings, larger μ). It is still level 2 evidence. We do not know whether this creature is already documented in the Lenia literature; we claim only that it is new to this project.

**Lesson:** the start condition decides what a search can see. E-12's "zero" was a property of the soup, not of rule space.

---

## J-018 · 2026-11-07 · E-16: no movers in Flow-Lenia from any start condition

**Question (exploratory, plan in `docs/data/e16-plan.md`):** smooth starts unlocked gliders in Lenia (E-14). Do they also give Flow-Lenia its first self-propelled structure, which it needs as a positive control (J-016)?

**Ran:** E-16, 100 random Flow-Lenia rules (the paper's ranges, R = 13; `rule-panel-e16.txt`) × 4 starts (soup, smooth ℓ = 3, smooth ℓ = 6, Chan-style patches), 1 seed, density 0.35, 128×128, 1000 steps. Commit `323bea1`; 15 min on 12 cores.

**Found:**
- **No movers: 0 self-propelled structures in 400 universes.** 5 candidate movers all failed the isolation test.
- **Class mix** (summed over the 4 starts): about 40% `active`, 50% `periodic`, 9% `frozen`, a few `saturated`.
- **The `periodic` share is probably inflated.** Flow-Lenia's frame measures use an 8-bit view, so changes below about 0.016 in A count as none (J-016). The structure census, which decides "self-propelled", uses the true float state and is not affected.
- **The start condition made no visible difference:** unsettled fractions 0.19–0.23 for soup and smooth starts, 0.10 for patches.

**Interpretation:** Plantec et al. report that moving patterns are "quite common" in random Flow-Lenia, but give no counts. We cannot reproduce that, from their own patch start or from any other. Three explanations remain open:
1. Our implementation differs in details the paper does not specify (Sobel normalisation, displacement clipping, θ_A).
2. Their "dynamic" patterns are mostly wobbling or rotating in place, which our detector correctly does not count as self-propelled.
3. Single-channel movers are genuinely rare. The paper itself needed long optimisation for directed motion with one channel.

Flow-Lenia still has no positive control, so no Flow-Lenia experiment is run beyond this search.

**Also fixed:** the conditions summary divided float (physical) states by 255 when reporting the initial mass per cell (it showed 0.001 instead of 0.175).

**Lesson:** a claim that something is "common", with no count, is a hypothesis to test, not a baseline to build on.

---

## J-017 · 2026-11-07 · E-15: in big worlds the blob field usually wins, and gliders are never born

**Question (descriptive):** E-13/E-14 gliders mostly destroy each other in 128×128 worlds. In 9× larger worlds, how do glider populations develop? Do collisions ever create new gliders?

**Ran:** E-15, 3 glider-viable rules (μ 0.14, 0.15, 0.16) × 10 seeds, smooth ℓ = 3 at density 0.10, 384×384, 5000 steps, with a census every 10 steps (`scripts/glider_population.py`, commit `ca4c7b1`). It took 1 h 40 min; the object census was the bottleneck and is now 10× faster (`323bea1`).

**Found:**
- **A race between gliders and a growing blob field.** In **23 of 30** worlds a patch of static-blob field survived the early collapse and **spread over the whole world**: Lenia does not conserve mass, and total mass grew from about 7,400 to about 30,000–35,000. It swallowed any gliders.
  - **6 of 30** ended with only gliders: 1–2 gliders of mass 71–75 in an empty world.
  - **1** died out.
  - The field always won for μ 0.14 (10/10), for μ 0.15 in 8/10, and for μ 0.16 in 5/10.
- **Larger worlds favour the field.** In 128×128 worlds, glider runs end as lone survivors (J-015). In 384×384 worlds, a field nucleus usually survives somewhere, so glider-only worlds become rarer. The rate of glider worlds is not a fixed property of a rule; it depends on world size.
- **No births.** In the 6 glider-only worlds, total mass after t = 200 only ever **drops**, in steps of about one glider (≈ 70). The one rise (+24 at t = 1610) is a collision transient followed at once by a drop. Gliders collide, and the collisions destroy or merge them; **no collision created a new glider.**
- **A detector warning (self-inflicted):** the quick glider count in the script (glider-sized mass, moving 3–12 cells per 10 steps, no isolation test) reported hundreds of "gains". Most were moving edges inside blob fields; the rest were count flicker during collisions. The script's glider counts are therefore **not** used for any claim. The mass traces and the images are.

**Interpretation:** in Lenia's glider-viable rules, a glider is a fragile intermediate state. It needs the world to collapse enough to leave isolated lumps, but not so much that nothing survives, and no blob field anywhere. Glider–glider interactions are destructive. This is evidence level 2 without any sign of level 3 (reproduction) or of a growing population.

**Changed:** D-025 (start conditions must be reported and justified for continuous physics). The E-15 figures are in the report.

**Lesson:** a quick, unvalidated counter is a hypothesis generator, not a measurement. Its "births" were artefacts that a look at the frames exposed in a minute.

---

## J-016 · 2026-11-07 · v0.7: Flow-Lenia physics with float32 states (implementation and validation only, no experiments)

**Question / why:** add a mass-conserving continuous family, Flow-Lenia (Plantec et al. 2022/2023, arXiv 2212.07906): matter is moved along a flow instead of being created and destroyed. This is a second Lenia-like family next to the E-12/E-13 Lenia work (J-013, J-014).

**Built:**
- **Physics** (`physics/flow_lenia.py`), reimplemented from the paper's equations. The reference code has no licence and was not used.
  - Single channel on a torus, FFT ring kernels, Gaussian growth.
  - Flow F = (1 − α)∇U − α∇A, with α = clip(A², 0, 1) (θ_A = 1, n = 2). Gradients are unnormalised 3×3 Sobel filters with wrap.
  - Reintegration tracking: dt = 0.2, s = 0.65, displacement clipped to dd − s = 4.35.
- **Rules:** written `FLENIA/R13/m…/s…/h…/r…/a…/b…/w…`, kernels joined by `+`.
  - `random()` uses the paper's ranges, with R fixed at 13 and 1–3 kernels of 3 rings each.
  - `mutate()` always changes the label.
  - `FLENIA/R13/diffusion` is the U = 0 control.
- **Float states in the engine (D-026).** A physics may declare `dtype = np.float32`.
  - **True float state:** the universe, forks, `state_hash` (tagged with the dtype) and storage (float32 blobs) all keep it.
  - **uint8 view:** each physics has a `view` (A on [0, 2]), which the observer's frame measures, the damage probe, the dashboard and `make_media` use.
  - **Structure census and exact recurrence** use the float state. Their thresholds are converted so they mean the same physical value as for uint8 Lenia.
  - **uint8 physics are untouched:** their view is the state itself.
- **Wiring:** discovery niche family `flow_lenia`, dashboard colour ramp, CLI help.

**Why float, not uint8:** a first uint8 version used exact largest-remainder rounding, and its integer mass was exactly conserved. But it had **quantization friction**: flows under about half a level per step were rounded away. Pure diffusion of the paper's patch froze after < 50 steps (rms radius 16.6), while float kept spreading (22.2 at step 400). Some rules that wobbled in float were pinned in uint8. It was dropped.

**Found:**
- **Bit identity:** the text output of `emergence benchmark --probes` (39 standard checks plus all 32 earlier probe checks) is identical before and after the change, and all earlier tests pass.
- **Mass:** conserved to float32 rounding. The worst relative drift within 1000 steps is 1.5e-8, with no trend (the float64 core drifts ~1e-13).
- **Rotation:** a rot90 seed evolves into the rot90 world exactly (200 steps; centroid mismatch 0.00). The grid and the Sobel filters do not make fake motion.
- **No positive control found.** 80 random float rules from the paper's 40×40 uniform patch (128×128 torus, 500 steps): 20 with 3 kernels, 20 with 5, 20 with 10, and 20 with 10 kernels and R random in [8, 25].
  - **0 self-propelled structures.** Two tracks passed the mover test, but both are small fragments (mass ~10) that fail the isolation test.
  - Most rules collapse into one blob or a few static blobs. The rest shed fragments or wobble.
  - Four candidates with the largest drift were inspected over 800 steps: fragments settle or creep, and none travels alone.
  - The 88 rules of the first, uint8 version (now dropped) gave none either.
  - This agrees with the paper: random search gives mostly static patterns, and directed motion with one channel needed long optimisation; two channels made it much easier.
  - **Two channels were not tried:** a 3D state would touch every observer path.

**Validation:** 5 probe checks (37/37; standard 39/39):
- mass conserved to float32 rounding;
- negative: a static-blob rule → not complex, quasi-static;
- deceptive: diffusion spreads (+9 cells rms in 400 steps) but has no movers;
- deceptive: a rotated seed moves the same way, rotated;
- selection-aware null: random rules picked by the old objectives → none complex without a mover.

There is **no Flow-Lenia positive**; the detector's positive is still the Lenia gliders. 5 new tests (56 in total).

**Caveats:**
- The paper states neither the Sobel normalisation nor the displacement clipping; the choices here are unnormalised Sobel and dd = 5.
- θ_A = 1 for one channel is our choice; the paper gives no value.
- Frame measures (activity, entropy, compression, local periodicity) see the uint8 view, so changes under 2/255 × 2 ≈ 0.016 in A count as no change. That is why the diffusion control is labelled `periodic`.

**Lesson:** a state that conserves mass exactly can still be the wrong physics. Rounding friction stopped slow flows, so the state had to be floating point.

---

## J-015 · 2026-11-07 · E-14 confirms: smooth starts make gliders, soups never do

**Question (pre-registered before running, `docs/data/e14-preregistration.md`):** does E-13's exploratory finding hold with fresh seeds and a test that can reach significance?

**Ran:** E-14, the same 8 glider-viable rules × 20 new seeds (master seed 14), 128×128, 2000 steps (commit `3453e99`). Two pre-registered contrasts, each a one-sided Fisher exact test on universes at α = 0.025:
- smooth ℓ = 3 vs soup at density 0.10 (same mass);
- smooth ℓ = 6 vs soup at density 0.35 (same mass).

**Found:**
- **Both contrasts confirmed:**

  | Density | Smooth start | Soup | Fisher p (one-sided) |
  |---|---|---|---|
  | 0.10 | smooth ℓ = 3: **28/160** universes | **0/160** | 1.0 × 10⁻⁹ |
  | 0.35 | smooth ℓ = 6: **21/160** | **0/160** | 2.4 × 10⁻⁷ |

- **Every glider is real:** all 49 were re-isolated and survived 1000 steps alone (validity check, pre-registered).
- **6 of the 8 rules make gliders.** The best is μ 0.14, σ 0.014 at 8/20 in both arms (95% interval 22–61%). Two rules gave 0/40: σ/μ = 0.13 at μ 0.14, and Orbium's neighbour at σ 0.0195. Their seeded gliders exist (E-13a), but no smooth start found one.
- **The lone-survivor pattern holds:** 47 of 49 glider runs end with exactly one persistent object, the glider; the other 2 end with two gliders.
- **Soups are equally consistent:** at density 0.10 all 160 die; at 0.35 all 160 freeze into a static blob field.

**Interpretation:**
- **What this shows:** in the glider-viable Lenia rules, self-propelled structures do arise on their own from unplanted random starts (**evidence level 2, spontaneous**), but **only when the start is spatially correlated**. The amount of matter is held fixed, so it is the arrangement that matters.
- **This differs from the Life-like result.** In J-009/E-10, arrangement did not matter once density was matched.
- **Why, in mechanism terms:** a glider needs an isolated lump of about its own mass and size with empty space around it. Correlated noise produces such lumps; uncorrelated soup averages out to a uniform potential that either freezes or dies.
- **What it does not show:** an ecology. The gliders mostly destroy each other until one is left (E-15 looks at this).

**Changed:** nothing in the code; data in `docs/data/experiments/2026-11-07-e14*.json`.

**Lesson:** an exploratory result, re-tested with fresh seeds and a test fixed in advance that can actually reach its threshold, is worth more than any number of post-hoc p-values.

---

## J-014 · 2026-11-07 · E-13: gliders emerge spontaneously, but only from smooth starts

**Question (pre-registered, `docs/data/e13-preregistration.md`):** in the 8 glider-viable rules of E-13a, does a glider arise by itself from a random start? Does the kind of start matter?

**Ran:**
- **Rules and seeds:** the 8 rules × 5 seeds, 128×128, 2000 steps (commit `df3a341`).
- **Starts:** soup, smooth ℓ = 3 / 6 / 10 (mass-matched, D-023), spots, and Chan's patches.
- **Densities:** 0.35 (E-13b, 240 universes, 9 min) and 0.10 (E-13c, 200 universes, 3 min).

**Found:**
- **Gliders emerged, from smooth starts only:** **18 of 240 smooth-start universes** grew a self-propelled structure, against **0 of 80** mass-matched soups. Spots gave 0 of 80 and Chan's patches 0 of 40.
  - smooth ℓ = 3 at density 0.10: 8/40
  - smooth ℓ = 6 at density 0.35: 6/40
  - other smooth arms: 0–2/40
- **All 18 are real gliders.** Each was re-isolated and survived **1000 steps alone** with mass 64–78, moving at 0.58–0.70 cells/step. They are the same creatures the E-13a scan grew from hand-made seeds; for μ 0.14, σ 0.014 the speed is 0.637 seeded and 0.638 spontaneous. This is the first spontaneous self-propelled structure in Lenia in this project (**evidence level 2**).
- **How they arise: survival after collapse.**
  - The soup becomes a static blob field at density 0.35 (all 40 runs) or dies at 0.10 (all 40).
  - Smooth starts mostly die, but first form a few isolated lumps. Some of these become gliders, which then disappear (collisions, decay) until at most one is left. Every glider run ends with **exactly one object**, a lone glider in an empty world.
  - Chan's patches did not produce gliders in 2000 steps on 128×128. Chan's claim ("given enough time") may need larger worlds or longer runs; we did not test that.
- **Pre-registered statistics: not confirmed.**
  - The planned test was a sign test across the 8 rules, at p < 0.05/20. The best contrast reached p = 0.0625 (smooth ℓ = 3 at 0.10: 5 rules higher, 0 lower). **With only 8 rules a sign test cannot go below p = 0.0078, so the design could never pass its own threshold.** That was a planning error.
  - A universe-level Fisher test (18/240 vs 0/80, p = 0.0048) was **not** pre-registered and is exploratory.

**Changed:**
- **E-14 pre-registered** (`docs/data/e14-preregistration.md`) to confirm the effect with fresh seeds: 20 seeds × 8 rules, two universe-level Fisher tests at α = 0.025.
- **E-15 (descriptive) queued:** glider populations in 9× larger worlds (`scripts/glider_population.py`).

**Lessons:**
- **Check that a pre-registered test can reach its threshold with the planned sample before running it.**
- **Matter has to be arranged, not just present.** A glider needs an isolated lump of the right size with empty space around it. Smooth fields make such lumps; soups make either a frozen field or nothing.

---

## J-013 · 2026-11-07 · E-12: no Lenia rule makes gliders from a soup, though gliders can exist

**Question:** with the corrected label (J-012), does the discovery engine find Lenia rules where self-propelled structures arise on their own, and does it beat random search?

**Ran:**
- **E-12:** engine vs random search, seed 11. 100 rules × 2 seeds × 5 generations per arm, 96×96, 500 steps, plus follow-ups; 12 + 14.5 min on 12 cores. Commit `feef3f1`.
- **E-13a:** a glider-viability scan, 99 single-ring rules on a μ × σ/μ grid (`scripts/lenia_glider_scan.py`).

**Found (E-12):**
- **No movers at all.** **0 self-propelled structures in 2085 universes** (1045 engine, 1040 random), and 0 rules `complex`. 5 candidate movers all failed the isolation test. Two were inspected: a slowly drifting blob, and a piece of debris that needs its neighbours. Alone, both dissolve within 25–50 steps.
- **The engine still finds more structure,** as it did for Life-like rules (J-004):
  - "Structured" rules: 103 vs 27, or **58 vs 27 (2.1×) after removing near-duplicates** (μ and σ/μ to 0.01, same ring count).
  - Behaviour niches: 11 vs 9.
  - Quasi-static universes: 49% (engine) vs 81% (random).
- **The structure the engine finds is not motion.** Its follow-up candidates reach evidence level 0–1. They are persistent textures, chaotic fields and slowly changing blob fields.

**Found (E-13a): gliders can exist, but only in a small island.**
- **8 of 99 single-ring rules** support a glider grown from one of 8 asymmetric seed shapes (μ 0.14–0.16, σ/μ 0.10–0.13; speeds 0.54–0.69 cells/step, mass 65–77). This is the region around Chan's Orbium.
- **The engine found this island without being told:** 59 of its 500 rules fall inside it (7 single-ring), against 9 for random search (6.6×). Still, not one soup there produced a glider.
- **So for these rules, emergence is the bottleneck, not search.** The physics allows gliders; random soups don't make them.

**Literature (agent review; papers and code read where available, abstracts only where marked in [Research]({{ '/research.html' | relative_url }})):**
- **Chan's starts were different from ours.** Chan (2019) says creatures such as Orbium emerge "given enough time" from random starts, but gives no rate. His starts were **15–40 dense patches of side 0.9 R in vacuum**, not full-grid soups.
- **Nobody reports a rate.** No paper estimates how much of Lenia rule space supports movers, or how often they emerge. E-13a is a first number for single-ring rules.
- **Flow-Lenia** (Plantec et al. 2023, 2025) claims movers are common and evolution happens inside the simulation, but reports no counts and no neutral model.

**Changed:**
- **E-13 pre-registered and committed** before running (`docs/data/e13-preregistration.md`).
  - Panel: the 8 viable rules.
  - Starts: soup, smooth starts with ℓ = 3, 6, 10 (mass-matched), spots, and Chan's patches (added by a dated amendment after the review, before any run).
  - Densities: 0.35 and 0.10.
- **New init kind `patches`** (Chan's protocol).
- **Flow-Lenia implementation started** on its own branch (`v0.7-flow-lenia`).

**Caveats:**
- The E-13a viability test uses 8 hand-chosen seed shapes, so it can miss gliders that need other shapes. 8/99 is a lower bound for single-ring rules.
- E-12 is one seed per arm. The engine-vs-random comparison is preliminary, as in J-004.

**Lesson:** separate *can it exist* from *does it arise*. A search that finds the right region can still report zero if emergence, not viability, is the limit.

---

## J-012 · 2026-11-06 · Static Lenia blob fields were labelled "complex"; fixed for continuous physics

**Question / why:** a review found that the class label and the discovery objectives, tuned for 2-state rules, inflate Lenia results. `emergence observe "LENIA/R13/T10/m0.150/s0.0150/b1" --steps 1000 --size 128 --seed 1` returned **complex** for a field of 20 static blobs (0 movers, activity 0.041, local periodicity 0, no cycle). Three 2-state tests fire on continuous fields:
- **4+ persistent objects count as complex:** every blob of a settled Lenia soup is a persistent object, and the census counts *instances*, not shape types.
- **Any value change counts as activity,** and exact-cycle and exact local-periodicity tests never fire on continuous values.
- **Objectives reward static fields:** `vocabulary` (instances) and `aperiodic_activity` favour exactly these fields, so the search is pushed toward static blob fields. That fits 0 of 500 rules in E-12 run 1 producing a mover.

**First question: rounding noise or real dynamics?** Real. In the Orbium soup ([C-01]({{ '/experiments.html' | relative_url }}), `scripts/lenia_static_fields.py`):
- **Float64 does the same.** Continued for 3000 steps, both the quantized run and a float64 run without any rounding change 13% of cells by > 32 levels. 5% have changed after 100 steps.
- **Not ±1-level flicker.** Per-step changes reach 25 levels; only 4% of changing cells stay within 8 levels.
- **It is all at object edges.** 100% of changing cells are within 2 cells of an edge. 56% creep (net change > 32 levels in 100 steps) and 19% oscillate in place.

The blobs never travel; their edges relax slowly for thousands of steps. Calling this "frozen" would be as wrong as calling it "complex".

**Found:** 60 random Lenia rules (96×96, 500 steps). The old label called **27 complex**; all 27 have **no self-propelled structure**, and nearly all their persistent objects are still. The new label calls none complex. 26 are quasi-static, and 5 remain rankable `active` rules with real dynamics but nothing that travels (moving stripe textures, breathing ring-shaped blobs). None of the 60 has a self-propelled structure.

**Changed (continuous physics only; discrete labels, objectives and all 39 + 24 earlier benchmark results are unchanged and were checked byte for byte; D-022):**
- **Value tolerance:** activity and local periodicity ignore changes of ≤ 2 levels (of 255). The emergent glider changes its cells by a median of 19 levels per step; only 5% of its changes are ≤ 2.
- **Near-fixed point:** no change above the tolerance in the window → `frozen`. Tested with a jitter control: a fixed field with ±1-level flicker, which exact tests call active.
- **`complex`** needs at least one self-propelled structure; static persistent objects no longer count.
- **Quasi-static:** no self-propelled structure, and *free activity* (activity more than 3 cells away from objects that stay in place) below 0.002. Such runs are labelled `active` but count as settled, so they are never ranked or bred from, like frozen discrete runs (D-005).
- **Objectives:** `aperiodic_activity` uses free activity, and `vocabulary` counts persistent objects that are *not* still.
- **`analysis.complex_all_seeds`** (`emergence compare`) inherits the corrected label. Lenia results stored before this fix must be re-run.

**Caveats:**
- **The 0.002 cut-off is a judgment call.** It sits between the highest free activity of a field that looked static (0.0018) and the lowest of one that looked dynamic (0.0029), a 1.6× margin, set from 60 rules after viewing them. The `complex` label does not depend on it; ranking near it may flip.
- **Movers are the only route to `complex` in Lenia.** Creatures that rotate or pulse in place are not counted.

**Validation:** 8 new probe checks (32/32 Lenia and probe checks; 39/39 standard): positive (two emergent gliders → complex), negative (blob soup → not complex, quasi-static), deceptive (smoothed noise stays at zero; creeping soup is not frozen; jitter is frozen), a dynamic non-travelling rule stays rankable, and a selection-aware null. That null takes the random rules the *old* objectives would pick (most persistent objects; most activity): none may be complex without a mover. 51 tests.

**Also fixed:**
- **`Lenia.mutate`** could return the parent unchanged (one ring, add branch, coin flip fails). Small μ/σ steps could also round to the same label. Every mutation now changes the label, and the constructor rounds to label precision.
- **Emergent glider speed:** it is **~0.53 cells/step**, not ~0.1 as documented. Measuring over 200 steps on a 128-cell torus wraps around (106 cells > 64) and reads ≈ 0.11, which is probably where 0.1 came from.
- **`continuous.track`** is now annotated as returning a tuple.

**Rebuilt (lost with the cloud container, never committed):** the `smooth` start condition (D-023), and the conditions study now skips the exact-shape probes for continuous physics (`innovating` is reported as not applicable).

**Lesson:** a label or objective validated on one physics family must be re-validated with that family's own controls before its numbers are read.

---

## J-011 · 2026-11-05 · v0.5: Lenia physics and a tolerant structure detector

**Built (commit `85b289f`, rebased onto `main` after PR #3):**
- **Lenia physics** (`physics/lenia.py`): continuous states quantized to 256 levels, FFT convolution, ring kernels, Gaussian growth. Rules are written `LENIA/R13/T10/m0.150/s0.0150/b1`, and exploration varies μ, σ and the rings.
- **Tolerant structure census** (`observatory/continuous.py`): thresholded objects labelled on the torus, frame-to-frame tracking with a mass tolerance, persistent/still/mover counts, and a self-propulsion test on isolated clones.
- **Controls:** a smoothed-noise control physics and Lenia benchmark controls: two emergent gliders derived from the Orbium parameters (not hand-typed), a settled soup, smoothed noise, and a decaying lopsided blob (24/24).
- **Integration:** discovery, CLI and dashboard accept any physics. The exact-shape probes (innovation, replication, knockout) are marked not applicable for continuous physics.

**Ran (cloud, now lost):** E-12 run 1, a Lenia exploration. It reported about **44% of rules "complex"** and **0 of 500 rules with a mover**. Those numbers came from the inflated label (J-012) and **cannot be trusted**. The data, the `smooth` start condition, the conditions-study probe skip and the gallery clips were never committed and were lost with the cloud container. No E-12 data exists in this repository.

**Lesson:** commit or export before the container goes away; uncommitted cloud work is not a result.

---

## J-010 · 2026-11-05 · Knockout test: no evidence of cumulative innovation

**Question:** do earlier innovations *enable* later ones (cumulative innovation, objective O5)?

**Built:** `observatory/knockout.py` (D-020). When a new persistent type appears, three kinds of forked clone are run:
- **unchanged;**
- **knockout:** the new type deleted;
- **controls:** the same number of cells deleted from *old* structures.

The question is whether later novelty is lost more after the knockout than after the controls. Validated on:
- **positive:** a glider hits a block and leaves debris. Deleting the glider, or the first debris, removes 75–100% of the later novelties, against 0% for the controls;
- **negative:** deleting an uninvolved block;
- **deceptive:** Brian's Brain (20/20 probe checks pass).

**Ran:** E-09 to E-11 (92 knockouts across 22 rules × 4 initial conditions).

**Found:**
- **Set-based test, which asks whether the same new shapes appear:** 88 of 92 were *inconclusive*. Deleting old structure rewrote 50–90% of the future just as much as deleting the new type: any change spreads over 1000 steps. This happens even in rules whose 64-step damage measure is low, so the short damage measure underestimates sensitivity over long horizons.
- **Count-based test, which asks whether fewer new shapes appear:** added because of the above. Its first version flagged 5 "dependencies", but a **placebo test** (each control deletion treated as the target) shows real knockouts are **indistinguishable from placebos**: P(real > placebo) = 0.491 (E-11) and 0.510 (E-10). Only 1 real knockout exceeded the placebo's 95th percentile per run, against 1.5–3.1 expected by chance.

**Changed:** the count-based verdict now requires an actual drop, larger than every control's, of at least the placebo's 95th percentile (0.5). The study summary reports the population-level placebo test. Commits `b47ff1f`, `85c3c2e`, `1a48270`.

**Conclusion:** among universes that look like they keep innovating, **no new structure is necessary for later novelty**. The apparent innovation behaves like chance turnover in a sensitive (chaos-like) system. This is O5 tested and not observed, at this scale.

**Lessons:**
- In sensitive systems, compare interventions with **placebo interventions**, not with zero.
- A threshold chosen before seeing the null distribution will produce false positives.

---

## J-009 · 2026-11-05 · Initial conditions: the "environment" effect was a density effect

**Question (H4, from review R-3):** does *where* matter starts change what a fixed rule produces?

**Built:** initial-condition generators in `UniverseSpec.init`: uniform, gradient, central patch, spots (D-019). Old specs stay bit-identical (tested). `emergence conditions` runs a paired study: the same rules and seeds under each condition, with a sign test and a bootstrap CI, and outcomes fixed in advance.

**Ran:**
- **E-09:** 22 rules × 4 conditions × 3 seeds, 96×96, 2000 steps.
- **E-10:** a density-matched control.
- **E-11:** an exact rerun of E-09.

**Found:**
- **E-09:** starting from a central patch gave **+1.35 self-propelled shape types** (9 rules higher, 0 lower; p = 0.004, CI excludes 0). This was the only result that survived a Bonferroni correction across 9 tests. Conway's Life showed it most clearly (0 → 15 in one seed; see [Gallery]({{ '/gallery.html#life-central-patch' | relative_url }})).
- **But the patch also starts with less matter** (density 0.125 vs 0.35). **E-10** compared the patch with a uniform soup at the *same* 0.125 density: **no difference** (−0.08, 5 higher / 4 lower, p = 1). The effect came from **less matter, not localized matter**: sparser worlds let gliders survive.
- **Gradient:** slightly more universes still unsettled (+0.14, CI excludes 0, but sign test p = 0.125); weak, and not followed up yet.
- **E-11 reproduced E-09 exactly** on every primary outcome.

**Conclusion:** H4 as tested is not supported. Localizing matter (patch, spots) doesn't matter once density is matched. Density itself does.

**Lesson:** any "environment" comparison must hold the amount of matter fixed (D-021). Without E-10 we would have reported a false environment effect.

---

## J-008 · 2026-11-05 · Journal, docs and next-phase plan

**What:** Created this site (`docs/`, served by GitHub Pages), the agent handoff (`AGENTS.md`, [Handoff]({{ '/handoff.html' | relative_url }})), the experiment data exports (`docs/data/experiments/`) and a reproducible media pipeline (`scripts/make_media.py`, `scripts/make_figures.py`).

**Why:** The work had spread across chat sessions and two AI reviewers. Decisions and negative results were at risk of being lost, and a new agent couldn't have continued without the conversation history.

**Review:** ChatGPT's third review ([R-3]({{ '/reviews.html#r-3' | relative_url }})) recommended two research tracks: stronger innovation controls, and a second physics family (Lenia). It also suggested studying initial conditions. We agree with most of it, with three amendments (see [Research → Next steps]({{ '/research.html#next-steps' | relative_url }})):
- **Causal knockouts:** test whether earlier novelties *enable* later ones by removing them in a clone.
- **Initial conditions first:** start with the initial-conditions track, because it is cheap and needs no new physics.
- **Same-rule null:** prefer a same-rule, independent-seed null over generic space-time surrogates.

**Status:** plan proposed (D-018), not yet started.

---

## J-007 · 2026-11-05 · Round 5: innovation must be ongoing to count

**Ran:** E-08 (full pipeline, seed 12).

**Found:** Two universes were labelled "still innovating", yet their long runs had settled:
- **B3/S0123678** entered an exact cycle at t = 1737.
- **B17/S1348/C7** ended with 97% of its changing cells oscillating in place.

**Changed:** "Still innovating" now requires the extended run to remain unsettled; otherwise the verdict is *transient innovation that ended* (D-016). Commit `32df04e`.

**Lesson:** a claim in the present tense ("still innovating") must be checked at the end of the observation, not averaged over it.

---

## J-006 · 2026-11-05 · Round 4: sampling aliasing; chaos is inconclusive

**Found (E-07):**
- **#1169 B3/S1236/C7 (sampling aliasing):** it was flagged as innovating, but its long run sits in an exact cycle of period 840 from t = 933. Sparse sampling kept catching cycle phases it had not seen yet, and those looked like new shapes.
- **#173 B1678/S13478 (steady turnover):** it produces new shape types at a flat rate (75, 62, 52, 71 per quarter), and only ~5% of them recur. That is what a stationary noisy process gives by chance.

**Changed:**
- No innovation can be counted after an exact cycle begins.
- A flat new-type rate with damage spreading ≥ 0.3 is reported as *inconclusive* (a heuristic; a matched null is still open).

Commit `328c078`.

**Lesson:** i.i.d. noise is not a fair null for a spatially correlated chaotic rule.

---

## J-005 · 2026-11-05 · Rounds 2–3: innovation and replication probes

**Built:**
- **Innovation probe:** orientation-free persistent shape types tracked over a long run. "Established late" means first seen in the third quarter and seen again in the fourth. Each experiment runs a noise control that gives the false-positive floor.
- **Replication probe:** the shape alone in an empty clone, whose copy count must grow. Two null tests on random patterns: rule-level duplication and common product.
- **Evidence ladder** (D-014).
- **14 hard and deceptive controls** (D-012).

**Found while validating:**
- **Seeds false positives:** a scan of Seeds (B2/S) soups first reported **6 "self-replicators"**. They were simply common shapes that any explosion produces, so the *common product* null was added and rejects them.
- **Power-of-two artifact:** Fredkin's rule seemed not to replicate, because the 256-cell test world is a power of two and linear rules annihilate there. The test world is now 160 cells.
- **Explosive patterns:** they made the probe ~100× slower, so a cutoff marks them *explosive (untestable)*.

**Result (E-07):** 0 self-replicators among 9 candidates; the highest evidence level was 2 (#1181). Commit `7009020`.

**Lesson:** scanning the most common shapes selects exactly the shapes that background production favours. Every detector needs a null built around how its candidates were *selected*.

---

## J-004 · 2026-11-05 · Round 1: calibrated robustness and a random baseline

**Question:** does the discovery engine beat random search at all? It had never been tested.

**Ran:** E-03 to E-06: engine and random search, seeds 11 and 12, identical compute (100 rules × 2 seeds × 6 generations on 96×96).

**Found:**
- **The engine wins.** It finds 90 vs 29 rules with self-propelled shapes, 56.5 vs 8 rules "complex" on every seed, and 33 vs 25 niches.
- **The advantage shrinks after deduplication.** Counting only rules at least 2 mutations apart, it is **1.9×** and **4.2×**. About 40% of the raw advantage was near-duplicate mutants.

**Also:**
- **Robustness threshold:** recalibrated from each experiment's own seed variation (90th percentile ≈ 0.3). The old fixed 0.5 accepted 29% of pairs of *different* rules.
- **Tournament:** made explicit.
- **Naming:** "verified movers" renamed "self-propelled shapes".

Commit `b77f873`.

**Lesson:** report counts after removing near-duplicates whenever a search breeds from its own winners.

---

## J-003 · 2026-11-05 · Review R-2 and the v0.3 plan

ChatGPT reviewed v0.2 ([R-2]({{ '/reviews.html#r-2' | relative_url }})). We agreed on calibration, terminology and the evidence ladder. We pushed back on going straight to a replication detector, and on Fredkin's rule as the positive control: it copies *everything*, so it belongs with the deceptive controls, and HighLife's replicator is the real positive. We prioritised a random-search baseline and an innovation-over-time measure first.

---

## J-002 · 2026-11-05 · v0.2: validated discovery

**Built:**
- **Mover verification:** candidate movers are tested in isolated clones.
- **Seed screening:** every rule runs on 2 seeds on 96×96.
- **Niches:** MAP-Elites-style behaviour niches.
- **Longer runs:** a 4× extended run for each candidate, with verdicts *persists / fades / loops*.
- **Sustained objective:** a slowly dying universe now scores less.
- **Benchmark:** `emergence benchmark` (39/39) and a deterministic noise-control physics.

**Mistakes found and fixed during the run:**
- **Niche collapse:** the first niche axes put 90% of the eligible rules into one niche (just 4 niches occupied in generation 0), so the axes were redefined.
- **Missed cycles:** universes that fell into long exact cycles were reported as "persists".

**Result (E-02):**
- **Niches grew from 7 to 33**, and the multi-state share in the top 30 fell from 87% to 77%: a modest gain.
- **7 of 11 candidates settled** in their longer run, some only after ~3000 steps.
- **#1029**, a striped medium with moving defects, persisted. Its defects only move *within* the stripes, so they never count as self-propelled.

Commits `d9b2197`, `f394662`.

---

## J-001 · 2026-11-05 · v0.1: MVP and first evaluation

**Built:**
- **Engine:** Life-like and Generations automata on a torus, behind a physics interface.
- **Observatory:** activity, block entropy, compression against a shuffled copy, recurrence, structure census, damage spreading.
- **Discovery:** Pareto ranking plus novelty search.
- **Lab notebook:** SQLite, with deterministic seeding and `reproduce`.
- **Dashboard:** gallery, playback, rewind, zoom, comparison and lineage.

Commit `4a07778`.

**Found (E-01):**
- **Real phenomena:** novelty search found spiral waves and glider-rich rules without being told what to look for ([Gallery]({{ '/gallery.html' | relative_url }})).
- **Strobing rules:** initially ranked top, with ~99% of cells flipping every step. A *local periodicity* measure fixed this, and settled universes are now excluded from ranking (D-005).
- **Fields of independent oscillators:** they never repeat globally but are just repetition, and the same local periodicity measure catches them.
- **Family collapse:** multi-state rules grew from 28% to 73% of the population in 10 generations (fixed in v0.2).
- **Isolated mover candidates:** #463's mover later proved to be a false positive.

**Lesson:** the first versions of "interesting" are always fooled by something trivial. Look at the universes, not just the scores.

---

## Entry template

```markdown
## J-0NN · YYYY-MM-DD · Short title

**Question / why:** what we wanted to know or fix.
**Ran:** experiment IDs (add them to experiments.md and export data with scripts/journal_export.py).
**Found:** numbers, with the caveats that matter (sample size, near-duplicates, nulls).
**Changed:** code changes, decision IDs, commit hashes.
**Lesson:** one sentence worth remembering.
```
