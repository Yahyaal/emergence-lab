---
title: Journal
description: Chronological research log, newest first.
---

# Journal

Newest first. Each entry records what we did, why, what we found, and what we learned.
Experiment IDs (E-xx) link to the [Experiments]({{ '/experiments.html' | relative_url }}) page and decision IDs (D-xxx) to [Decisions]({{ '/decisions.html' | relative_url }}).

**How to add an entry** (people and agents): copy the template at the bottom, put it at the top, and fill in the commit hashes and experiment IDs. Keep claims at the evidence level actually reached.

---

## J-042 · 2026-11-08 · E-42: mutations in emergent program replicators are inherited (heritable variation, level 4)

**Question (pre-registered, `docs/data/e42-preregistration.md`):** the self-replicating programs that emerged in E-41 come in variants. Is that variation heritable: when a replicator carries a mutation, do its copies carry it too, or do they revert to a fixed form (like Lenia's dividing spots, J-037) or lose it?

**Built (D-041):** `observatory/program_heredity.py`. Each single-byte mutant of a replicator is seeded alone (8 copies) in a fresh soup of 1024 random programs and run 96 epochs without background mutation; among the family (≥ 90% identical to the parent), f_mut = share carrying the mutant byte; f_base = the same share when the unmutated parent is seeded. Controls (benchmark section 12, passing): hand-written replicator → heredity (12/12 viable mutants inherited); the same under `noexec` and `copyall` → no variation; a random program → no variation.

**Ran:** E-42, `scripts/bff_heredity.py`, commit `7aa4749`, a few minutes on 9 workers. The 9 distinct programs judged "replicator" in E-41 (soups 901, 5006, 5010), 24 mutants each.

**Found:**
- **"heredity" for 9 of 9** (prediction: at least 7). Sign tests p ≤ 1.2·10⁻⁴.
- Viable mutants: 13–20 of 24 (54–83%; predicted 30–70%: mutations break copying less often than expected). Of 141 viable mutants, **140 were carried by ≥ 60% of the family**, and 131 by 100%. The one exception: a mutation at byte 0 of a soup-5006 replicator, carried by 26% of copies (the first byte is apparently not always copied).
- **f_base = 0 in every case**: the mutant byte never appears at that position without the mutation.
- Families grew to 64–512 copies depending on the mutant: mutants differ in how fast they spread (not yet analysed as fitness).
- Figure: `docs/assets/report/e42-bff-heredity.png` (which byte positions tolerate mutation, per replicator).

**Evidence level 4 (heritable variation)** for program replicators that arose spontaneously from random code: variants exist, they reproduce, and their differences are passed on to descendants in a fresh soup. Not level 5: we have not shown selection among variants, cumulative change, or open-endedness.

**Caveats:** single-byte mutations only; 96 epochs is a few generations; the replicators were taken from soups selected for having transitioned; mutants were tested alone, not in competition. The hand-written positive is a linear copier; emergent replicators behaved the same under the test, which suggests they also copy whole tapes.

**Lesson:** heritable variation was not the hard part in program soups: once self-copiers exist, they copy mutations along with everything else. The hard part was getting self-copiers at all (3 of 16 soups).

---

## J-041 · 2026-11-08 · E-41: self-replicating programs emerge from random code; every transition is confirmed by the detector

**Question (pre-registered after E-40, `docs/data/e41-preregistration.md`):** E-40 never reached a transition, so its detector question stayed open. (A) Does the pilot soup that transitioned (seed 901) replay exactly, and does the detector find replicators in it? (B) Do E-40's 12 soups transition if run 3× longer, and is every transition confirmed by the detector, with none outside?

**Ran:** E-41, `scripts/bff_soups.py --e41`, commit `1c335d4`, 32 min (A) and 20–40 min per soup (B) on 11 workers. (A) seed 901 from scratch, 16000 epochs. (B) E-40's 12 final snapshots continued for 32000 epochs (48000 in all) with fresh random streams (seeds 5000–5011). Detector (unchanged, D-040) on the 4 most common programs 1000 epochs after a transition and at the end.

**Found:**
- **(A) Exact replay:** the HOE series equals the pilot log at every checkpoint; transition at epoch 8750. Detector at 9750: **2 replicators + 2 "one generation"**; at 16000: **2 replicators**, 1 one generation, 1 no replication. Random programs never multiplied (0 of 3 per candidate). The common programs are variants of one family sharing a core (`[[]},.<;45=%` appears in five of the six most common at epoch 9750). Prediction met.
- **(B) 2 of 12 soups transitioned** (seed 5010 at total epoch 32000, seed 5006 at 43250; 95% interval 2%–48% per soup within 48000 epochs). Prediction (2–6) met, at its low end. Both contain verified replicators at both scans (5006 at the end: 97 copies each of two replicator programs, 8 → 512 copies in the growth test and 512 again in generation 2).
- **Selection-aware null:** 0 replicators in the 22 end scans of soups that did not transition (E-40: 12, E-41: 10). Every soup above the HOE threshold contains a replicator; none below does.
- Pooled with E-40 and the pilots: **3 transitions in 16 soups of 16384 programs**, all of them at epoch ≥ 8750; none in the first 16000 epochs of the 12 pre-registered soups.
- Many top programs get "one generation": their copies multiply once, but the chosen copy does not. Likely partial or damaged copies (BFF replicators are known to copy imperfectly and to be parasitized); not investigated.

**Evidence level 3**, now in a second universe and in a stronger form than Lenia's dividing spots: replicators arise **from random code with no fitness function**, are confirmed by intervention (two generations among random programs), and come as **several distinct variants**. Heredity (level 4) is now testable here: do mutant replicators pass on their mutations? That needs a measurement with its own controls; none has been run.

**Lesson:** the transition is a rare event per soup and per epoch at this size; whether it happened at all in a given run is not a property of the rule. Rates need many soups and long runs; the detector, not the entropy curve, decides what was found.

---

## J-040 · 2026-11-08 · Program soups (BFF): a replicator detector, and no transition in 12 soups (E-40)

**Question (Track D route 5; pre-registered, `docs/data/e40-preregistration.md`):** Agüera y Arcas et al. (2024) report that soups of random 64-byte programs in a minimal language (BFF), paired at random and run on a shared tape, undergo a "state transition" in which self-replicating programs appear and take over, with no fitness function. Lenia has given us movers but, until E-32, no reproducers. Does self-replication emerge from random code in our implementation, and does a detector built to our standards confirm it?

**Built (interactive session, commit `4d79737`; D-040):** `emergence/programs/bff.py` (soup, C interpreter via ctypes, a pure-Python reference that the C code must equal on 300 random tapes; modes `noexec` and `copyall` as controls) and `observatory/replicators.py` (growth test of 8 copies among 1024 random programs, two generations, random-program null). Probes (benchmark section 12), all passing: a hand-written 64-byte self-replicator → replicator (8 → 70 copies, generation 2: 838); random program and an all-zeros program → no replication; the replicator under `copyall` and `noexec` → no replication; scans of the most common programs of a noexec soup and an early BFF soup → 0 replicators (selection-aware null).

**Pilot (interactive session, not in the sample):** 4 soups, 16000 epochs. Seed 901 (16384 programs) jumped at epoch ~8750 from a high-order entropy (HOE) of 0.3 to 2.2–3.5 and stayed there; seeds 900, 902, 903 did not.

**Ran:** E-40, `scripts/bff_soups.py`, commit `4d2761e`, 53 min per soup on 11 workers. 12 BFF soups of 16384 programs (seeds 4000–4011), 16000 epochs; controls 4000 epochs: 2 `noexec`, 2 `copyall`. Detector on each soup's 4 most common programs at the end (and 1000 epochs after any transition).

**Found:**
- **0 of 12 BFF soups transitioned** (max HOE 0.54–0.64, all in the first 2000 epochs; final 0.29–0.38). **My prediction (2 to 6) was wrong**, and the pilot's 1 in 4 was the lucky draw. With the pilot: 1 of 16 soups (95% interval 0.2%–30%).
- Detector at the end: every candidate "no replication" (the most common program occurs once or twice: the soup is still diverse).
- Something does change before any transition: the share of instruction bytes rises from 3.9% (random) to ~15% in every BFF soup and stays there, while `noexec` stays at 3.9%. Programs that contain instructions survive interactions better than others. This is selection on the bytes, but not replication.
- Controls: `noexec` HOE 0 (nothing changes); `copyall` HOE 7.0 within 250 epochs (copying alone makes the soup repetitive) yet its common programs are "no replication" (one "one generation" verdict). **HOE alone would have called `copyall` a transition**; the detector does not.

**Interpretation:** not reached; the question stays open. Our soups are 8× smaller than the paper's (2^14 vs 2^17 programs); if a replicator has to arise by chance in some pair, its chance per epoch scales with the number of pairs, so a smaller soup should transition later. E-41 (pre-registered, running) replays the pilot that transitioned, which is deterministic, to test the detector on a real transition, and continues the 12 soups to 48000 epochs.

**Lesson:** one pilot in four is not a rate. Pre-registered predictions built on a single success should be wide, or the pilot should be bigger.

---

## J-037 · 2026-11-08 · E-32: one random multi-channel Lenia rule makes dividing spots (first Lenia reproducer; prediction wrong)

**Question (pre-registered, `docs/data/e32-preregistration.md`; Track D):** E-29 found no reproducer among 3000 random single-channel Lenia rules. Chan (2020) reports self-replication once Lenia has several channels and kernels. Repeating E-29 unchanged on random `MultiLenia` rules (D-031), does a lone lump ever become a reproducer?

**Ran:** E-32, `scripts/mlenia_lump_scan.py`, commit `7aedcaf`, 4.4 h on 8 workers. 1000 rules (seed 32; 521 with 2 channels, 479 with 3), 2 lumps each (radius 13, 26), 128×128 vacuum, 300 settling steps, birth detector (D-028 + D-030) on the 2 most common object types. Gray-Scott pipeline positive 4/4.

**Found:**
- **1 reproducer rule in 1000** (#970, 2 channels, 4 kernels): both tested object types passed two generations, with 0 copies from the empty and the perturbed vacuum. **My prediction (0) was wrong.**
- Rule outcomes: 450 decided (at least one object fully tested; 449 without a reproducer), 143 explosive only, 27 filled, 380 extinct. 5 further "one generation" verdicts (E-29: none).
- Compared with single-channel Lenia (E-29, 0 of 1453 decided rules): 1 of 450, 95% interval 0.006%–1.2%; Fisher one-sided p = 0.24. **The difference in rate is not significant**; what is new is that a reproducer exists at all in our Lenia family.

**Inspected (as pre-registered):**
- **By eye** (`docs/assets/report/e32-divider-strip.png`, `e32-divider.gif`): a small spot alone in an empty world stretches, splits in two within ~150 steps, and the halves split again; after ~2000 steps about 100 spots tile the 160×160 world and the total mass saturates (52 → 4200). It looks like Gray-Scott's "mitosis" spots, not like E-30's condensation: matter grows only next to existing spots, in a front, never from the empty background.
- **Re-run from 3 new lumps** (fresh random streams): a reproducer in **3 of 3**, 0 background copies each time.
- **The scrambled-patch check reports `attractor = True`**: scrambled lumps of the same values also become dividing spots. As for Gray-Scott, the spot is the rule's attractor, so offspring cannot inherit anything from a particular parent. Heredity is impossible here by construction, and the heredity test was not run.
- **What the second channel does (post hoc, scratch test):** channel 1 dies out (mass 0 after settling), so everything happens in channel 0. But the kernel from the empty channel 1 into channel 0 still counts in channel 0's averaged growth, as a constant negative term (growth of 0 is −1), i.e. a **uniform decay**. Removing channel 1 (the same two self-kernels of channel 0 in a one-channel rule) or keeping only either self-kernel: **no reproduction** (6/6 lumps, many static objects). The division needs two kernels *plus* that decay.

**Evidence level:** level 3 (self-replication verified by intervention, two generations, three fresh starts) for one rule, in the weakest form: a single attractor type with no possible heredity, as Gray-Scott. Not a creature with a lineage.

**Interpretation:** dividing spots, the classic reaction-diffusion reproducer, can arise in Lenia from a random rule, but rarely (~0.2% of decided rules), and they are copies of an attractor, not of a parent. For heredity, the next physics needs room for several distinct reproducing types (Track D).

**Lesson:** an "extra channel" can matter without holding any matter: in averaged-growth Lenia an empty channel's kernel is a decay term. Check what a component actually does before crediting it.

---

## J-036 · 2026-11-08 · E-31: held-out fed Flow-Lenia on stable food: no reproduction, and the new null holds

**Question (pre-registered, `docs/data/e31-preregistration.md`):** E-30's fed-world "reproducers" were the food condensing (J-035). The perturbed-vacuum null (D-030) was added after those results, and fed worlds only mean something if the food itself is stable. On new rules (seed 31), screened for stable food first, does anything reproduce?

**Ran:** E-31, `scripts/pl_heldout.py`, commit `8d30db2`, 4.8 h on 11 cores (sharing the machine with E-32). 200 rules screened at food 0.05 and at 0.08 (perturbed food alone, 160×160, 4000 steps); the first 50 stable rules at each level (47 at 0.08) run in the E-30 world (6 patches with their own kernel weights, 128×128, 1500 steps), birth detector with D-030, heredity test on any reproducer.

**Found:**
- **0 reproducers in 97 stable-food worlds** (50 at food 0.05, 47 at 0.08), 183 objects tested, every verdict "no reproduction". No "background" and no "one generation" verdict. Prediction (0) correct; one-sided 95% upper bound ≈ 6% per food level.
- **Stable food is the minority:** 72/200 rules (36%) at 0.05 (E-30: 32/100), **47/200 (24%) at 0.08**: more food, less stability, as predicted.
- Pipeline positive (GrayScottTracer, carried trait): reproducer and heredity 4/4 (r = 1.0, p = 0.0005).

**Interpretation:** the held-out test of D-030 passed: with the food screened, the detector no longer reports condensation, and its positive still passes. Fed Flow-Lenia with localized parameters, in our random rule distribution and with this start, does not reproduce (level 3 not reached). The localized-parameter route (Track D route 3) has nothing to evolve yet.

**Lesson:** a null added after the fact needs a held-out run where it cannot be tuned. This one passed it.

---

## J-035 · 2026-11-07 · E-30: "reproducers" in fed Flow-Lenia were food condensing; the birth detector gets a perturbed-vacuum null

**Question (pre-registered, `docs/data/e30-preregistration.md`; Track D route 3):** in Flow-Lenia with localized parameters (FlowLeniaPL, J-033), fed with a thin food layer and seeded with six "species", does anything reproduce? If so, is there heredity?

**Ran:** E-30, `scripts/pl_scan.py`, commit `ef87a8a`, 2.7 h on 11 cores. 100 random rules × food {0, 0.05}, paired; 6 patches with their own kernel weights; 128×128, 1500 steps; birth detector on the 2 most common object types; heredity test where a reproducer was found. Pipeline positive (Gray-Scott tracer): reproducer and heredity in 4/4.

**Found, as first scored:**
- Unfed: 0/100 worlds with a reproducer (by construction); mass drift ≤ 4e-7.
- **Fed: 17/100 worlds with a "reproducer"** (24 objects), 1 "one generation", and the heredity test said "heredity" in 1 world (r = 0.998, 14 families). **My prediction (0) was wrong on the numbers.**

**Inspected (as pre-registered) and found to be artefacts:**
- The "parents" were small (mass 2–40) next to creature-sized objects (120–600) that never passed. One of them, alone in a fed vacuum, became **99 objects spread over the whole world within 500 steps**.
- **The food layer is an unstable fixed point.** A perfectly uniform layer never changes (so the background null, an exact fed vacuum, made 0 copies), but food with noise of 1e-4 and **no parent at all** condensed into 20–110 droplets in 15 of the 17 rules; with 2% relative noise, in all 17. The droplets have the parent's mass, so the copy count rises like real division (1, 5, 9, 17, 25 … 106).
- The "heredity" verdict is meaningless here: the "offspring" are condensed food, not offspring.

**Changed (D-030, post hoc):** the birth detector also runs a **perturbed vacuum** (float states: × (1 + N(0, 0.02)) + N(0, 1e-4)); copies there → "background", a no-spontaneous-generation rule. The heredity test returns "unstable vacuum" in the same case. Every earlier control keeps its verdict (Gray-Scott's vacuum stays empty under the noise); E-30 world #43 is a new deceptive probe.

**Rescored (`scripts/e30_rescore.py`):**
- **Food stability: only 32 of the 100 rules have a stable food layer at food 0.05.**
- **All 17 hit worlds are on unstable food**; rescanned with the fixed detector: **0 reproducers** (24 background, 10 no reproduction).
- On the 32 stable-food rules (valid under both detector versions): 0 reproducers, 1 "one generation", 59 no reproduction.

**Interpretation:** no reproduction in fed Flow-Lenia with localized parameters, in 100 random rules. The real lesson is about the environment: "feeding" a mass-conserving world can make the food itself the most active thing in it. Any future fed-world experiment must first check that its food is stable (or explicitly study condensation). The fix is post hoc and needs held-out data: the next fed-world scan should use only rules whose food passes the stability check, with the new null pre-registered. Evidence level stays at 2.

**Lesson:** a null built from a perfectly symmetric state can be blind to instability. "Nothing happens in an empty world" has to hold for a slightly disturbed empty world too.

---

## J-034 · 2026-11-07 · E-29: in 3000 random Lenia rules, no lone lump becomes a reproducer

**Question (pre-registered, `docs/data/e29-preregistration.md`; Track D route 2):** E-27/E-28 tested objects in worlds already selected for movers, a small corner of rule space. Before building a "fission objective" for the search, a direct test: give every rule drawn at random the same chance to reproduce. Does any Lenia rule turn a lone lump of matter into a reproducer?

**Ran:** E-29, `scripts/lump_scan.py`, commit `6a6578a`, 72 min on 11 cores. 3000 rules from `Lenia.random` (μ 0.08–0.40, σ/μ 0.05–0.30, 1–3 rings), each with 2 smooth random lumps (radius 13 and 26) alone in a 128×128 vacuum for 300 steps (or up to the last checkpoint before the world filled). Then the unchanged birth detector (D-028) on the 2 most common object types. Pipeline positive: Gray-Scott lumps.

**Found:**
- **0 reproducers in 3000 rules** (5069 object tests), as predicted. Gray-Scott pipeline positive **10/10**. No "one generation" verdict either.
- **Coverage is lower than planned, and this matters for the bound:**

  | Rule outcome (both lumps) | Rules |
  |---|---|
  | at least one object fully tested: no reproduction | **1453** |
  | only "explosive": the test world filled before the detector could decide | 410 |
  | lumps filled the world with nothing testable | 228 |
  | both lumps died | 909 |

  The pre-registered bound (0.1% of the distribution) assumed every rule could be tested. Honestly stated: **0 of 1453 decided rules** (95% upper bound about 0.2% of decided rules); for about a fifth of rule space (638 rules, mostly μ > 0.25 with wide growth) the detector cannot decide, because any object grows into a world-filling front.
- **The undecided cases do not look like division.** Of 1481 explosive tests, 1463 had fewer than 2 copies before the world filled. In the other 18, copies held at most 26% of the matter (75% is required), except one: a huge object (mass 2087, rule #1100, μ 0.396) which, run alone and inspected by eye, spreads into a front that freezes into a labyrinth.

**Interpretation:** across the single-channel, single-kernel Lenia rule distribution we search, a lone lump either dies, settles into still objects or movers, or spreads as a front. None grows and divides like a Gray-Scott spot. Together with E-27/E-28 this makes route 2 (a fission objective for the search) unpromising in this family: there is no gradient of "almost reproducing" rules to climb (0 "one generation" verdicts). Evidence level stays at 2. Known blind spot: rules whose objects spread too fast for a 160×160 test world.

**Lesson:** pre-register the coverage too, not only the count. A bound over "all rules" is only as good as the fraction the detector can actually decide.

---

## J-033 · 2026-11-07 · A heredity test that is not fooled by place, and Flow-Lenia with parameters that travel with matter

**Question:** Track D (research.md) needs two things before any experiment on heredity: (1) a way to tell whether offspring resemble their own parent, and (2) a physics in which a creature can carry something heritable. Neither existed.

**Built (D-029):**
- **`observatory/heredity.py`, a transplant test.** Up to 16 parents (the most common mass class in a world) are each copied alone into the physics' vacuum and run 1500 steps. Their offspring are the objects within 2× of the parent's mass. Heredity = the correlation between the parent's trait, measured in its own world, and its offspring's mean trait, across at least 6 families: r ≥ 0.5 and a parent-permutation p < 0.01. The permutation keeps the selected parents (only those that reproduced) and shuffles who is whose parent, so it accounts for how candidates were chosen. Parents that all have the same trait give "no variation".
- **Why a transplant:** offspring sit next to their parent, so anything set by place (a "common environment") makes parent and offspring alike without inheritance. Biologists separate the two by cross-fostering; moving each parent to the same empty world does the same.
- **Controls, `GrayScottTracer`:** Gray-Scott dividing spots (the birth detector's positive) with a third channel, a trait that never changes the chemistry. *carried*: the trait moves with the spot's matter (positive). *redrawn*: replaced by deterministic noise every step (negative). *position*: set by the column (deceptive: in the world, each spot's nearest neighbour has a similar trait, r > 0.5).
- **`FlowLeniaPL` (physics/flow_lenia.py):** Flow-Lenia with parameter localization (Plantec et al. 2023): each cell carries its own kernel weights h_i, stored as A·h_i and moved by the same reintegration step, so parameters mix in proportion to incoming mass and are conserved exactly. Optional uniform **food** below the object threshold, so a mass-conserving creature could grow. A scatter-add reintegration (≤ 9 target cells per source) is about 3× faster; plain FlowLenia keeps the old code and stays bit-identical.

**Found (validation):**
- Heredity: carried r = 1.0 (heredity); redrawn r ≈ −0.2 (no heredity); position r ≈ −0.3 (no heredity), although in-world neighbours are alike; identical founders → no variation. Probe section 10, 5 checks.
- FlowLeniaPL equals FlowLenia when every cell has the rule's weights (max difference ~1e-6 after 300 steps, float32 rounding); matter and every weighted parameter are conserved (drift < 1e-5); mixed weights stay between the two species' values; a food-only world never changes. 3 probe checks, unit tests.

**Not shown:** that anything in Flow-Lenia reproduces (E-30 asks), and nothing about selection or evolution: the tracer trait has no effect on survival by construction. Our mixing rule has not been checked against the paper's, so FlowLeniaPL results are not directly comparable with Plantec et al.

**Lesson:** "offspring look like their parents" is the classic trap of shared environment; build the deceptive control (a trait set by place) before the measure, and the measure has to be an intervention.

---

## J-032 · 2026-11-07 · A birth detector; none of our Lenia creatures reproduces (E-27, E-28)

**Question:** the owner asked what could give reproduction and heredity. Nothing in the project could have confirmed a birth in Lenia: the replication probe matches exact discrete shapes and only tests clones we place. So: build a detector that works for both physics families, validate it, and ask whether the Lenia worlds we have contain reproducers.

**Built (D-028):**
- `observatory/births.py`: an object is copied alone into the physics' vacuum and run. Copies are objects of the same shape (discrete) or within 2× of the parent's mass (continuous). A **reproducer** must pass two generations: its copies keep multiplying and hold ≥ 75% of the matter, and one copy, alone, does it again. A vacuum world must make none. Discrete scrambled patches that copy themselves give "rule-level duplication" (Fredkin).
- `physics/gray_scott.py`: Gray-Scott reaction-diffusion (Pearson 1993), whose spots grow and divide: a known continuous reproducer, used only as a control. Its state has two channels.
- Benchmark section 9 (12 checks, 54/54 in all): positives HighLife replicator and Gray-Scott spots; negatives Life glider, Orbium glider, the replicator pattern under Life; deceptive Fredkin (rule-level), Seeds debris, Gray-Scott stripes, Gray-Scott worms that split once ("one generation"), smoothed noise, and the Lenia labyrinth below; selection-aware null on a Life soup and a settled Orbium soup.

**Ran:**
- **E-27** (pre-registered, `docs/data/e27-preregistration.md`, one amendment before results: the planned Gray-Scott soup start died out, Pearson's square seeds used instead). 218 worlds with verified movers (E-14, E-18a, E-24, E-26) and 100 mover-free worlds; for each, the 6 most common object types plus every in-world mover. 4 h of CPU on 10 cores.
- **E-28** (pre-registered, `docs/data/e28-preregistration.md`): the same on 350 held-out worlds: 150 more mover-free worlds from the same experiments, 100 from E-17/E-18b (random 3-ring rules from smooth starts, the wanderer ridge), 100 from E-19 (soups, shuffled starts). 4.4 h of CPU.

**Found:**
- **Movers do not reproduce.** 0 of 285 movers (gliders, wanderers, ring gliders) and 0 of 503 candidates in the mover worlds made even one generation of copies.
- **E-27 broke the first version of the detector.** It reported 2 "reproducers" and 23 "one generation" candidates in blob-field worlds. Looking at them (`scripts/birth_inspect.py`, as pre-registered) showed no births: a single blob placed alone **bursts into a labyrinth that fills the world** within 500–1000 steps (~80 pieces of similar mass), then the count stops. Copy mass also drifted 377 → 278 → 169 over generations because each generation was matched to its own parent, and no third generation passed. The first version only asked for "more copies late than early".
- **Fix (post hoc, then held out):** late copies must be ≥ 2× the early maximum, and generation 2 is matched to the original parent. Every earlier control keeps its verdict; the labyrinth became a deceptive control. Re-scanning E-27's 23 hit worlds: 0 reproducers.
- **E-28 confirmed the fixed detector on held-out worlds: 0 of 350 with a reproducer** (95% upper bound 0.85% per world). Gray-Scott pipeline positive: 10/10 in both E-27 and E-28. In E-28, 61 candidates from wildly growing E-17 rules filled the test world ("explosive"), and 3 blob candidates (rules μ 0.121–0.150 with two rings) passed generation 1 only narrowly (34 → 73 copies) and failed generation 2: the second generation is doing real work, and the doubling rule alone would not be enough.

**Interpretation:** in the Lenia rules we have explored, structure either travels (gliders, wanderers, ring gliders), sits still, or spreads as a front or labyrinth. Nothing grows and divides into copies of itself. Evidence level stays at 2. This fits the literature: replication in Lenia has been reported in richer variants (several channels and kernels, Chan 2020), and heritable variation needs something that carries the rule's parameters with the creature (Flow-Lenia with parameter localization, Plantec et al. 2023). Both are now planned as Track D in [Research → Next steps]({{ '/research.html#next-steps' | relative_url }}).

**Limits:** isolation runs in vacuum, so mass-conserving physics (Flow-Lenia) cannot pass by construction (a fed-world variant is planned); candidates are the most common object types, so a rare reproducer among many blobs could be missed; 9 objects in E-28 were too large to test.

**Lesson:** a detector's first real data set is its hardest control. "More copies later" is not reproduction; keep looking at what the detector counted.

---

## J-031 · 2026-11-07 · E-26: a third kind of mover, a slow straight "ring glider", confirmed from smooth starts only

**Question (pre-registered, `docs/data/e26-preregistration.md`):** the held-out check (J-028) turned up one random rule, μ 0.277, σ 0.0316, rings 1/0.5/1, that made movers from a smooth start. Is it a reliable source of movers, and does the smooth-start effect hold?

**Ran:** E-26, commit `8217924`. The rule × 40 seeds × {soup, smooth ℓ = 6}, at density 0.35 and 0.18, 128×128, 2000 steps (4 min). Every mover was verified with `scripts/verify_movers.py`: **36 of 36 survive 1000 steps alone**.

**Found:**

| Density | Smooth ℓ = 6 | Soup | Fisher p (one-sided) |
|---|---|---|---|
| 0.35 (primary) | **13/40** | 0/40 | 3.8 × 10⁻⁵ |
| 0.18 | **18/40** | 0/40 | 3.2 × 10⁻⁷ |

- **Confirmed at both densities.** Every soup world died (80/80 extinct).
- **The creature is unlike both earlier movers.** It has a ring-shaped body, mass 173–180 (glider about 70, wanderer about 115), and moves at 0.075–0.087 cells/step in a **perfectly straight line** (net/path = 1.0 over 1000 steps alone). It is about as slow as the wanderer but does not turn, and much heavier than a glider. We call it the **ring glider** (a descriptive name; similar Lenia creatures may already be known).
- **Where it lives:** μ 0.277 with σ/μ 0.114 is on the upper band of the E-18b wanderer ridge, but with different ring weights (b = 1, 0.5, 1). Its neighbourhood in rule space is not mapped yet.

**Interpretation:** three kinds of spontaneous mover are now confirmed in Lenia: Orbium-like gliders, wanderers and ring gliders. All three need correlated starts, and none comes from soups in these rules. The ring glider was found by **drawing rules at random** (1 of 120) from smooth starts, not by the search engine. That fits E-17: once starts are smooth, mover rules are not vanishingly rare among 3-ring rules. Still level 2 evidence.

**Lesson:** a held-out check run for one purpose (validating a cut-off) can turn up a finding for another. Keep looking at what the check produced, not only at the number it was run for.

---

## J-030 · 2026-11-07 · E-25: a 300-step isolation finds more slow movers at no false-positive cost; relaxing straightness does not help

**Question (pre-registered, `docs/data/e25-preregistration.md`, one amendment before results; follows J-022):** the mover detector misses about 8% of wanderers. Do a longer isolation run (`SLOW_STEPS`) or a looser in-world straightness rule (`STRAIGHTNESS`) fix that without false positives?

**Ran:** E-25, commit `d39b9b1`, 87 min on 4 cores. 3,789 stored universes were re-simulated:
- wanderer worlds: E-18a (160) and E-18b (504);
- glider worlds: E-14 (640);
- worlds with no known creature: E-19b soups (400), the E-12 random arm (1,040 soups) and the E-17 random arm (1,045 smooth starts).

Every persistent track that moved ≥ 5 cells in the last 100 frames was isolated with the old 100-step test and with the new extended test. The extended test keeps running an object that keeps its mass for up to 300 steps, checking every 25 steps. Every detection was checked against a ground truth: alone for 1000 steps, one object, mass kept, still moving at the end.

**Found:**
- **The replay is faithful.** The current detector (V0) reproduces the stored verdict in all 3,789 worlds.

  | Pool | Worlds | V0 (0.5, 100) | V1 (0.5, 300) | V2 (0.25, 300) | V3 (no straightness, 300) |
  |---|---|---|---|---|---|
  | E-18a wanderer | 160 | 96 | **99** | 99 | 99 |
  | E-18b ridge | 504 | 30 | 30 | 30 | 30 |
  | E-14 gliders | 640 | 49 | 49 | 49 | 49 |
  | E-19b soups | 400 | 1 | 1 | 1 | 1 |
  | E-12 random (soups) | 1,040 | 0 | 0 | **1 false** | **1 false** |
  | E-17 random (smooth) | 1,045 | 1 false | 1 false | 1 false | 1 false |

- **The longer isolation only adds true movers.** 6 objects pass only the 300-step test (3 new wanderer worlds); all 6 pass the 1000-step ground truth. Every isolation pass that later failed the ground truth (4 objects) had already passed the 100-step test.
- **Relaxing straightness adds nothing true and one false positive:** a crooked fragment in E-12 universe #2059 that passes isolation and splits within 50 steps of the long run.
- **The current detector has one known false positive in these pools:** E-17 universe #1236, the drifting field chunk already caught by verification in J-019. The ground truth also flags 2 isolated objects in E-18b that split or die after 575–850 steps alone, in worlds that have other, confirmed movers.

**Changed (D-027):** `SLOW_STEPS = 300` is the default; `STRAIGHTNESS` stays 0.5. Four new benchmark checks: a second slow positive (E-18a #95, found only with 300 steps); two deceptive controls (static soup blobs fail the 300-step isolation; the crooked fragment #2059 is still rejected); and a selection-aware null (4 mover-free random rules in which the observer selects in-world movers gain no self-propelled structure). All earlier results are untouched; future runs can only gain detections.

**Interpretation:** about 99 of the roughly 104 wanderer worlds are now detected (≈ 95%, up from ≈ 92%). The remaining misses are wanderers that turn in tight loops or sit still in the observation window; a looser straightness rule does not find them, and it does find junk. The in-world straightness rule earns its place.

**Lesson:** a ground truth that is more expensive than the detector (1000 steps alone vs 100) is what makes a calibration like this possible. Run it on every pool, including the ones where you expect nothing.

---

## J-029 · 2026-11-07 · E-24: Chan's patch start does make gliders, given room; my prediction was wrong

**Question (pre-registered, `docs/data/e24-preregistration.md`):** Chan (2019) says gliders emerge from random starts "given enough time". His start, 15–40 dense patches in vacuum, gave 0 gliders in 40 worlds of 128×128 over 2000 steps (E-13). Do bigger worlds and longer runs change that?

**Pilot (before pre-registration; scratch script, 48 worlds, 256×256, 400 steps):** patch starts are bistable. Each world either dies or fills with a blob field (9/24 extinct, 15/24 filled with Chan's count; 24/24 filled with 110 patches). The planned 10,000-step study was therefore replaced by a 3000-step one.

**Ran:** E-24, commit `027248d`, 94 min on 8 cores. The 8 E-13 rules × 20 seeds × {`patches` (15–40), `patches:110` (Chan's patch density on 128×128), `smooth:3` at density 0.10}, on a 256×256 torus for 3000 steps. Every mover was verified with `scripts/verify_movers.py`: **51 of 51 survive 1000 steps alone**.

**Found:**

| Start (256×256, 3000 steps) | Worlds with a verified glider | 95% CI | Other outcomes |
|---|---|---|---|
| Chan's patches (15–40) | **13/160 (8.1%)** | 4.4–13.5% | 48 extinct, 99 blob fields |
| 110 patches | 0/160 | 0–2.3% | 160 blob fields |
| smooth ℓ = 3, density 0.10 | **29/160 (18.1%)** | 12.5–25.0% | 10 extinct, 121 blob fields |

- **Chan's start works in a bigger world.** 13 glider worlds in 5 of the 8 rules, all with ordinary single gliders (mass 65–75). The same start at 128×128 gave 0/40. **My prediction (at most 1–2 per arm) was wrong.**
- **It is the room, more than the time.** With 110 patches (the same patch *density* as Chan's count on 128×128) the field always wins. In the clip on the Report (universe #183), the glider has formed by step ~50 while the other patches fade. A sparse start lets one patch become a glider before a field can form around it. World size and run length were changed together, so this is suggested, not shown.
- **Smooth starts do not lose out in bigger worlds:** 18.1% at 256×256 and 3000 steps vs 17.5% at 128×128 and 2000 steps (E-14, same density and ℓ). My second prediction (fewer in bigger worlds, because of E-15's growing fields) was also wrong for this density.
- **Smooth starts still beat Chan's patches about two to one** (descriptive; the arms are not mass-matched).

**Interpretation:** Chan's report that creatures emerge from random patch starts is reproduced, with a rate of about 8% of worlds in these rules at this patch density. One earlier statement needs a qualifier: "Chan's patches did not produce gliders" (J-014) held only for 128×128 (marked there). On the report, the claim becomes: correlated starts (smooth fields, or sparse dense patches) make gliders; fine-grained soups almost never do. Both kinds of start that work put matter in **isolated lumps with space around them**, which supports the "isolated lump" mechanism of J-021 (still not tested directly).

**Lesson:** a protocol that failed in a small world was judged too early. When reproducing a claim, match the conditions it was made under (world size included) before calling it unreproduced.

---

## J-028 · 2026-11-07 · C-02: the quasi-static cut-off has no clean gap on new rules; a random rule makes a new mover

**Question (review R-4):** the quasi-static cut-off (free activity < 0.002, D-022) was set on 60 random rules. Does it hold on rules it has never seen, and from smooth starts?

**Ran:** C-02, `scripts/lenia_static_fields.py --seed 8 --rules 120 --skip-part1` with `--init uniform` and `--init smooth:6` (96×96, seed 1, 500 steps; the script gained `--init`). Then `scripts/heldout_free_activity.py` re-ran every rule that is not quasi-static although ≥ 90% of its persistent objects are still, to see where its free activity lies. Commits `027248d`, `d39b9b1`.

**Found:**
- **No clean gap.** Of 59 non-extinct, mover-free soup rules, 43 are quasi-static and 16 rankable. **5 lie within 0.8–1.25× of the cut-off**, and the free activity runs smoothly from 0.0005 to 0.006 (figure on the [Report]({{ '/report.html' | relative_url }})). Smooth starts: 79 quasi-static, 10 rankable, 4 near the cut-off. The same rule can land on either side depending on the start (μ 0.189 and μ 0.216 do).
- **Static-looking fields leak into the ranking.** 10 of the 16 rankable soup rules have ≥ 90% still objects (smooth starts: 2 of 10). In 5 of these 12, **70–94% of the "free" changes lie within 3 cells beyond the excluded margin**: creeping blob edges that reach past the 3-cell margin, not new dynamics. In the other 7, 24–53% do, and the rest is elsewhere (short-lived small objects).
- **No false creature claims.** `complex` still needs a verified mover, so the leak only lets some static fields be ranked and bred from. It does not inflate any mover count.
- **Unplanned: a random rule makes a mover.** One of the 120 rules, μ 0.277, σ 0.0316, rings 1/0.5/1, was `complex` from the smooth start with 2 movers (mass about 178, about 0.085 cells/step, nearly straight). **Both survive 1000 steps alone** (path 83–85 cells). From soup the same world died. It lies on the upper band of the wanderer ridge (σ/μ = 0.114; E-18b), with different ring weights, and moves straight instead of turning. Followed up in E-26 (pre-registered).

**Interpretation:** the cut-off does its main job: most static fields are excluded, and no mover-free world is called complex. But it is a soft boundary, not a gap, and about one in six static-looking soup fields gets through, mostly because blob edges creep further than the margin allows. The search can still waste effort on them. A fix (for example a margin that scales with the kernel radius) would need its own controls. Left open; the cut-off is unchanged.

**Lesson:** a threshold set on one sample needs a held-out sample before anyone calls its margin safe. The "1.6× margin" of D-022 was a property of those 60 rules.

---

## J-027 · 2026-11-07 · E-23: the combination chain stops at two

**Question (pre-registered, `docs/data/e23-preregistration.md`):** can a double glider and a glider fuse into a stable triple?

**Ran:** E-23, 312 collisions (Orbium rule; 8 glider orientations × 13 lateral offsets × 3 phases) between the E-20 double glider (mass 144, moving diagonally) and a single glider, on a 224×224 torus, 1500 steps (`scripts/chain_scan.py`, commit `913faa6`, 5 min).

**Found:**

| Outcome | Collisions |
|---|---|
| World filled by a blob field | 116 (37%) |
| One single glider left | 106 (34%) |
| Nothing left | 68 (22%) |
| Two single gliders left | 22 (7%) |
| **A triple** | **0** |
| **The double glider surviving intact** | **0** |

- **The double never survives a hit.** A double-glider collision is about 15× more likely than a glider–glider collision (2.4%, E-20) to set off a world-filling field.

**Interpretation:** combination in these rules goes one step and stops. Two gliders can make a double; a double plus a glider never makes anything larger, and the double itself is fragile. That is a natural ceiling on cumulative structure here, at least for this route. It fits the overall picture: Lenia's glider-viable rules support spontaneous movers and one level of combination, but nothing that grows, reproduces or accumulates.

**Lesson:** test the second step of a promising first step before calling it a mechanism.

---

## J-026 · 2026-11-07 · E-22: when wanderers meet, two usually become one; no stable composite, no births

**Question (pre-registered, `docs/data/e22-preregistration.md`):** gliders can fuse into a double glider (E-20). What happens when two wanderers meet?

**Ran:** E-22, 200 encounters on a 160×160 torus, 3000 steps each, classified by the full observatory (`scripts/wanderer_encounters.py`, commit `76e0249`, 8.5 min).
- **Pattern:** the wanderer of E-18a universe #81.
- **Partner:** one of 8 exact symmetries, placed 20–40 cells away in a random direction, with a random phase.

**Found:**

| Outcome | Encounters |
|---|---|
| **One wanderer left** | **142 (71%)** |
| Both survive | 43 (22%) |
| Both destroyed | 10 (5%) |
| A heavier "new object" at t = 3000 (mass 146–205) | 5 (2.5%) |
| More than two movers (a birth) | **0** |

- **The new objects are transient.** Followed for 2000 more steps, the two inspected (trials 16 and 59) **relax back to a normal wanderer** (mass 104–148), moving like one.
- **Two wanderers usually become one ordinary wanderer:** absorption, with the mass regulated back. There is no lasting double wanderer.

**Interpretation:** the two movers found tonight interact differently. Gliders can fuse into a stable, larger composite (E-20). Wanderers absorb each other into a single creature of the usual size. Neither multiplies: still no level-3 evidence. The wanderer's mass regulation is a property worth knowing for any future reproduction test, because a creature that grows and splits would need the opposite tendency.

---

## J-025 · 2026-11-07 · E-21: spontaneous double gliders are rare, and an isolation test alone over-counts

**Question (pre-registered, `docs/data/e21-preregistration.md`, with one amendment before running):** how often do double gliders arise from smooth starts, and by fusion or directly?

**Ran:** E-21, the 8 E-13 rules × 40 fresh seeds, smooth ℓ = 3, density 0.10, 128×128, 2000 steps. Each world was traced every 10 steps (`scripts/double_glider_trace.py`, commit `d641b0b`, 8.5 min).

**Found:**
- **The script's raw counts:** 2 worlds with a "verified" double glider (1 direct, 1 unclear, 0 fusion), and 116 with a "verified" single glider.
- **The script's verification is flawed.** Its outcome definition, written in the pre-registration, checks only that a glider-sized object, cut out of the final state, keeps moving alone. That passes **fragments of blob fields** too.
  - Of 36 worlds it counted as glider worlds, the observatory (which needs real in-world movement) found a mover in 25. **All 11 others are blob-field worlds** with 17–49 persistent objects.
  - Of the 2 "double gliders", **one is a field fragment** (53 objects in the world). **One is genuine:** a lone double glider that formed directly from the start's lumps (t ≈ 90).
- **Corrected result: 1 genuine double glider in 320 worlds, formed directly; 0 fusions.** With E-19 (3 of 160 smooth ℓ = 3 worlds), spontaneous double gliders occur in **about 0.6% of smooth-start worlds** (4 of 640). The fusion route has been seen **once** (J-024).
- **Earlier verified counts are not affected.** E-13/E-14/E-18/E-19 used `scripts/verify_movers.py`, which first requires the observatory's in-world track (persistent ≥ 80% of the window, net travel ≥ 5 cells, straight) and only then isolates.

**Interpretation:** double gliders are real but rare in these rules. Fusion is possible (E-20: 7 of 250 perpendicular collisions), but in small worlds with few gliders it rarely happens spontaneously. Cumulative structure (lumps → gliders → double gliders) exists, but at about one event per several hundred worlds.

**Lesson:** "cut it out and it moves" is necessary, not sufficient. A mover must first be seen moving in its own world. The pre-registered outcome here was badly defined, and the analysis says so instead of reporting 116 and 2.

---

## J-024 · 2026-11-07 · Double gliders also arise spontaneously, in one case by fusion of two spontaneous gliders

**Question:** do E-20's double gliders (two fused gliders) also form without being planted?

**Ran:** no new simulation. The masses of all verified movers in E-13, E-14 and E-19 (121 in total) were re-read from their exports (`scripts/verify_movers.py`), and worlds with double-glider-mass movers were traced.

**Found:**
- **E-13 and E-14:** all 69 verified movers are single gliders (mass 64–78).
- **E-19: 3 of 52 are double gliders** (mass 139–157, speed 0.57–0.63), in three different rules (μ 0.140, 0.150, 0.160), all from smooth starts. Each was the lone survivor of its world, and each has the same two-body shape as the E-20 fusions.
- **Two ways they form:**
  - **Universe #204 (Orbium, smooth ℓ = 3):** two gliders formed by t = 40, travelled for about 500 steps, then **collided and fused at t ≈ 530**. This is a two-step, unplanted sequence: gliders arise, then combine into a larger mover.
  - **Universe #562:** the double glider formed directly from the collapsing lumps by t ≈ 30.

**Interpretation:** spontaneous structure can build on earlier spontaneous structure in these rules, at least once: lumps → gliders → a double glider. It is one event, observed after the fact (exploratory), and still level 2. For O5 (cumulative innovation) it is a concrete, testable case. Does the double glider arise *only* via glider fusion, or also directly? How often, per world and per collision? It is a better starting point for a knockout test (J-010) than chaotic turnover was.

---

## J-023 · 2026-11-07 · E-20: glider collisions never make new gliders, but can fuse two into a stable double glider

**Question (pre-registered, `docs/data/e20-preregistration.md`):** can glider collisions create new gliders ("births")? E-15 could not tell (review R-4).

**Ran:** E-20, 500 controlled collisions on a 192×192 torus, 1000 steps after placement (`scripts/collision_scan.py`, commit `3cdd71d`, 4 min on 12 cores).
- **Rules:** μ 0.15 (Orbium) and μ 0.14.
- **Geometries:** head-on and perpendicular. The partner glider is oriented exactly, by flip or transpose.
- **Variations:** lateral offset −24…24 cells and timing phase 0…20 steps.

**Found:**
- **No births.** No collision ended with ≥ 3 gliders that each survive 1000 steps alone, the pre-registered criterion.
- **What collisions do:**
  - **Head-on, μ 0.15:** 44% destroy both, 43% leave one, 13% leave both.
  - **Head-on, μ 0.14:** gliders mostly pass through or survive (78%).
  - **Perpendicular:** mostly one survivor.
- **New: fusion into a double glider.** In **7 perpendicular collisions**, at near-central offsets (−2…+2 cells), the two gliders **fuse into one stable object**: two Orbium-like bodies bonded side by side, mass 131–140 (twice a glider), moving straight at 0.61–0.63 cells/step. It stays intact for ≥ 1000 more steps. A collision **created a new kind of mover**: combination, not reproduction. Similar composite Lenia creatures may be known; new to this project.
- **Explosions.** **6 perpendicular collisions** seed a patch of blob field that grows to fill the world (mass ≈ 140 → 7,400–8,000) within about 1000 steps.
  - This is a plausible origin of E-15's world-filling fields.
  - Some fragments inside the field, cut out, survive alone (at most 2 per world), short of the birth criterion. In the world they are part of the field.

**Interpretation:** interactions between gliders are mostly destructive, but not only. A collision can build a larger composite mover, or trigger a phase change of the whole world. Neither is reproduction (level 3). Fusion is a first sign of **structures combining into new structures**, which the project's cumulative-innovation question (O5) cares about. Whether fused gliders arise spontaneously in big smooth-start worlds is untested.

**Lesson:** a controlled scan of 500 interactions answered in 4 minutes what 30 long, uncontrolled runs (E-15) could not.

---

## J-022 · 2026-11-07 · How often does the detector miss a slow, turning mover? About 8%

**Question (review R-4, point 4):** the mover detector was validated only on Orbium, a fast straight glider at about 0.6 cells/step. Does it miss slow, turning movers such as the wanderer? Does the quasi-static cut-off (D-022) hide them from the search?

**Ran:** every E-18a smooth-start world (120) *without* a detected wanderer was re-run to the end and searched for wanderer-sized objects (mass 95–145). Each one found was tested alone with a longer, 300-step isolation run.

**Found:**
- **Most of those worlds are empty:** 15 of 24 are extinct.
- **8 contain exactly one wanderer-sized object** that the detector missed. With 300 steps alone, **5 of the 8 move by themselves**; 3 do not move ≥ 5 cells net (they turn in tight loops).
- **Detection rate:** about 96 of 104 wanderer worlds, **≈ 92%**. Wanderer counts in E-17/E-18 are therefore slight **under**counts; no conclusion changes.
- **Why they were missed:**
  - 4 wanderers moved in the observation window but failed the 100-step isolation test, which is too short for a slow turner;
  - 4 failed the in-world straightness rule (net/path ≥ 0.5) while turning;
  - 1 sat still through the whole window and was labelled quasi-static, so it was hidden from the search. That is the only case of the cut-off hiding a mover.

**Changed:** a new benchmark positive, "Lenia slow positive". An emergent wanderer (E-18a universe #81) must be detected as self-propelled and labelled complex (38/38 probe checks; all other checks unchanged).

**Not changed (yet):** the detector itself. Raising the isolation run to 300 steps, or relaxing straightness for turning movers, would catch most of the misses, but each change needs its own deceptive controls (drifting blobs, decaying lumps) and re-validation. Left as an open item.

**Lesson:** a detector's positive control should span the range of what it might meet. A single fast, straight positive left the slow, turning kind untested.

---

## J-021 · 2026-11-07 · E-19: it is the spatial correlation; soups make gliders only rarely, at their die/freeze switch

**Question (pre-registered, `docs/data/e19-preregistration.md`; answers review R-4):**
- Is the smooth-start effect caused by spatial correlation, or by the different mix of cell values?
- Is there a soup density that makes gliders?

**Ran:** E-19, commit `dd1e28b`, 128×128, 2000 steps. All movers were verified with `scripts/verify_movers.py`: **52 of 52 survive 1000 steps alone**.
- **E-19a:** the 8 E-13 rules × 20 seeds × soup / smooth / `smooth_shuffled`, the last being exactly the smooth start's values randomly permuted. Densities 0.10 (ℓ = 3) and 0.35 (ℓ = 6). 960 universes.
- **E-19b:** soup only, densities 0.12–0.30 in steps of 0.02, 5 seeds per rule. 400 universes.

**Found:**
- **E-19a, both pre-registered contrasts confirmed:**

  | Density | Smooth | Shuffled | Soup | Fisher p (one-sided) | Rules higher/lower |
  |---|---|---|---|---|---|
  | 0.10 | **37/160** | **0/160** | 0/160 | 6.9 × 10⁻¹³ | 6/0 (sign p = 0.016) |
  | 0.35 | **11/160** | **0/160** | 0/160 | 4.1 × 10⁻⁴ | 5/0 (sign p = 0.031) |

  Same mass and same value distribution, but scrambled positions, give no gliders. **The effect is the spatial correlation.**
- **E-19b, the soup transition:**
  - **Below 0.18 soups die, above 0.24 they become blob fields,** with a mixed zone between. That fits R-4's point that soup outcomes are bistable.
  - **One soup world made a real glider: 1 of 40** at density 0.20, Orbium's rule, right at the switch. Across the sweep that is 1 in 400.
- **Correction:** "soups never make gliders" (J-014/J-015, report) is wrong. Soups make them **rarely**, only near the die/freeze transition. With E-14 and E-19a, it is 1 glider world in 1,120 soup worlds overall, against 13–23% for smooth starts in these rules. This fits Chan's remark that creatures emerge from random starts "given enough time".

**Interpretation:** in these 8 rules, spatially correlated matter is what makes gliders likely, at fixed mass and value mix. The "isolated lump" mechanism is consistent with this but untested.

**Lesson:** the null a reviewer asks for is worth running. It turned "it's the arrangement, probably" into a tested claim, and it caught an overstatement ("never").

---

## J-020 · 2026-11-07 · E-18: the wanderer is robust and lives on a narrow ridge; review R-4

**Question (pre-registered, `docs/data/e18-preregistration.md`):** is E-17's single wanderer rule a reliable source of movers? Where else in rule space do wanderers arise?

**Ran:**
- **E-18a:** the wanderer rule, 40 fresh seeds × soup / smooth ℓ = 3 / 6 / 10, density 0.18, 128×128, 2000 steps (2 min).
- **E-18b:** a 7 × 6 grid of 3-ring rules around it (μ 0.200–0.285, σ/μ 0.06–0.15), soup vs smooth ℓ = 6, 6 seeds (10 min). Commit `cb5fd24`.
- **Verification:** every mover re-isolated with the newly committed `scripts/verify_movers.py`: **190 of 192 survive 1000 steps alone.**

**Found:**
- **E-18a, primary test:** universes with a verified wanderer:

  | Start | Worlds |
  |---|---|
  | smooth ℓ = 6 | **36/40** |
  | smooth ℓ = 3 | 36/40 |
  | smooth ℓ = 10 | 24/40 |
  | soup | **0/40** |

  Smooth ℓ = 6 vs soup: one-sided Fisher p = 1.3 × 10⁻¹⁸. In this rule a smooth start almost guarantees a mover; Orbium's rules manage 13–18%.
- **The movers are one kind of creature:** mass 104–137, path speed about 0.085 cells/step, turning (net/path median 0.29, direction persistence 0.84 between 25-step legs).
- **E-18b, the "wanderer ridge":** wanderers arise in **7 of 42** rules, all on a narrow diagonal band.
  - σ/μ ≈ 0.092 for μ 0.215–0.255 (50–100% of worlds);
  - σ/μ ≈ 0.11 for μ 0.255–0.285 (17–100%).
  - Soups gave 0 in all 252 soup worlds.

**Review R-4 (independent agent; see [Reviews]({{ '/reviews.html#r-4' | relative_url }})):**
- **Main points:**
  - smooth starts also change the *value distribution*, not only the spatial correlation;
  - soups sit on a die/freeze transition, so their "0" is close to guaranteed;
  - the verification code was not committed;
  - the detector is not validated for slow, turning movers;
  - several claims and numbers were overstated or wrong.
- **We agree with all of them.**
  - Corrections are marked "Corrected after review R-4" in J-013 to J-019 and in the report.
  - `verify_movers.py` is committed.
  - **E-19** (pre-registered) tests the main point with a shuffled control, `smooth_shuffled`: exactly the smooth start's values, randomly permuted. It adds a fine soup density sweep across the transition.

**Caveat:** the wanderer turns, and the mover detector needs net travel ≥ 5 cells with straightness ≥ 0.5 over its window. Slower or more tightly turning variants on or near the ridge may be missed, so the ridge could be wider than shown (R-4).

**Lesson:** a reviewer who did not do the work found six real problems in an hour. Build the review in, don't bolt it on.

---

## J-019 · 2026-11-07 · E-17: searching from smooth starts finds a new mover, a slow "wanderer"

**Question (pre-registered, `docs/data/e17-preregistration.md`):** E-12 searched from soups, which never make gliders (E-14). Searching from smooth starts instead, does the engine find mover rules, does it beat random search, and does it find any outside the Orbium island?

**Ran:** E-17, identical to E-12 except `--init smooth:6`, seed 17. Engine 6 min, random 7 min (the faster census helped; E-12 took 12 + 14.5 min). Commit `9ba8254`.

**Found:**
- **Raw hits (any run with a self-propelled structure):** the engine has 5 universes in 2 rules, random search 1 universe in 1 rule. All lie **outside** the single-ring island of E-13a. (`emergence compare` reports engine 1, random 0, because it counts rules whose *mean* over all their runs is at least one self-propelled structure; the pre-registered outcome counts any run.) *(Corrected after review R-4.)*
- **Pre-registered verification (alone for 1000 steps):**
  - **μ 0.357, σ 0.0456, 2 rings (both arms): fails.** Its "mover" is a field chunk of mass 2275 that falls apart. Not a creature.
  - **μ 0.243, σ 0.0224, rings 1/0.5/0.5 (engine only): passes in all 5 objects, from 4 universes.** One is a screening run; three are follow-ups (new seeds and a 2× larger world), so it reproduces.
- **Primary outcome:** **engine 1 verified mover rule, random 0.** Tiny numbers and one seed per arm, so no significance claim (as pre-registered).
- **The new mover is a "wanderer", not a glider.**
  - **Size and shape:** compact, mass about 115 (Orbium: 70), with an internal pattern that keeps changing.
  - **Speed:** path speed 0.07–0.08 cells/step (about 8× slower than Orbium); net displacement speed only 0.017–0.055, because it turns. *(Corrected after review R-4.)*
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
- **No births seen, but weak evidence.** In the 6 glider-only worlds, total mass after t = 200 falls overall in steps of about one glider (≈ 70), with several small rises of 5–24 during collisions (largest +24 at t = 1610). The images show collisions destroying or merging gliders. Because Lenia does not conserve mass, a birth in a lossy collision need not show as a +70 step. With only 6 such worlds, this is absence of evidence, not evidence of absence. A validated per-object census or seeded collision scans are needed. *(Corrected after review R-4.)*
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

- **Every glider is real:** all **51 structures in the 49 universes** were re-isolated and survived 1000 steps alone (validity check, pre-registered). The verification script is now committed as `scripts/verify_movers.py`. *(Corrected after review R-4.)*
- **6 of the 8 rules make gliders.** The best is μ 0.14, σ 0.014 at 8/20 in both arms (95% interval 22–61%). Two rules gave 0/40: σ/μ = 0.13 at μ 0.14, and Orbium's neighbour at σ 0.0195. Their seeded gliders exist (E-13a), and no E-14 smooth start found one (E-13 found one for σ 0.0195 from smooth ℓ = 10). *(Corrected after review R-4.)*
- **The lone-survivor pattern holds:** 47 of 49 glider runs end with exactly one persistent object, the glider; the other 2 end with two gliders.
- **Soups are equally consistent:** at density 0.10 all 160 die; at 0.35 all 160 turn into blob fields (9 of them still slowly changing at the horizon). *(Corrected after review R-4.)*
- **Scope:** these p-values are for universes within these 8 rules and this start generator. The rule-level sign test is p = 0.031 for both contrasts, above α = 0.025, because only 6 of 8 rules contribute. The finding does not yet generalise to "glider-viable rules" (R-4).

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
  - Chan's patches did not produce gliders in 2000 steps on 128×128. Chan's claim ("given enough time") may need larger worlds or longer runs; we did not test that. *(Tested later in E-24, J-029: on 256×256, 13 of 160 patch worlds made gliders.)*
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
- **8 of 99 single-ring rules** support a glider grown from one of 12 asymmetric seed shapes (held 400 steps) (μ 0.14–0.16, σ/μ 0.10–0.13; speeds 0.54–0.69 cells/step, mass 65–77). This is the region around Chan's Orbium.
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
