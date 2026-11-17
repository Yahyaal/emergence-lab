---
title: Research
description: The research question, hypotheses, evidence ladder, related work, and the path to a publishable result.
---

# Research

## Goal and objectives

### Goal

Investigate whether complex structures and behaviours can **emerge spontaneously from simple mathematical rules**: build an experimental artificial-universe simulator, explore many different simple rule sets, and discover which ones naturally produce interesting, persistent, and potentially evolving complexity.

### What this project is not

- Not a simulation of our universe.
- Not an attempt to *build* artificial life by design. Nothing is planted, steered or rewarded inside a running universe.
- Not a search for one predefined idea of what life or complexity should look like.

### Research question

How much genuine, persistent and eventually *evolving* complexity can arise from simple, fixed local rules, without any outside design? Which properties of the rules, or of the initial conditions, make it more likely?

### Research objectives

Each objective is measurable, and progress is recorded on the [evidence ladder](#evidence-ladder).

| # | Objective | Status |
|---|---|---|
| O1 | Build an observatory that tells randomness, repetition and organisation apart, *validated against deceptive controls* | done for 2D CA, Lenia and program soups (170 benchmark checks: 39 standard + 131 probes, as last reported); extended with every new detector |
| O2 | Build a discovery engine that finds interesting universes more efficiently than random search, without a single complexity score | supported (H1, E-77) |
| O3 | Find universes with persistent organisation and self-propelled structures (evidence levels 1–2) | reached: level 2 in Life-like rules (found by search) and in Lenia (arising spontaneously from smooth starts, E-14) |
| O4 | Detect spontaneous self-replication (level 3), and then heredity and variation (level 4) | not observed in Life-like rules (0 of 17 candidates). **Replication observed:** one multi-channel Lenia rule makes dividing spots of a single type (E-32); replicators arise from random code in BFF soups (E-40, E-41) and in SUBLEQ versions we added (E-75; the two published versions make none). **Heredity observed in program soups:** one-byte mutations are inherited in 9 of 9 BFF replicators (E-42); not tested in SUBLEQ |
| O5 | Detect cumulative, open-ended innovation, where new structures enable further new structures (level 5) | not observed in Life-like rules (knockouts ≈ placebo, J-010). **Tested in BFF soups, not shown:** later replicators are not reliably fitter than earlier ones by races, growth rate or kin-free invasion, up to 20,000 rounds after the jump (E-48 to E-54); no parasites (E-66, E-67). **Also not shown with space** (E-78): when soups continue with programs meeting only lattice neighbours, late code is no fitter in a well-mixed common garden and no parasites appear. **Nor in a lattice garden** (E-80, J-095, J-096): late neighbour-only code spreads no farther among unrelated code than well-mixed code (7 standard soups, coarse; 16 soups of the h = 64 variant, upper bound 0.02 in relative area). Untested: advantages that need the soup's own neighbours, and parasites on the lattice |
| O6 | Identify which properties of the rules *or the initial conditions* make complexity more likely (H4, H5) | Life-like: matter density matters, its spatial arrangement didn't (J-009). **Lenia:** smooth random starts make gliders, soups with the same mass almost never do (49 of 320 vs 0 of 320, E-14, pre-registered); a shuffled control shows the arrangement is the cause (E-19). **BFF:** a rule version whose shortest copier makes a working copy makes replicators (E-60; held in a second rule family, E-64, E-65, and in five instruction-set variants, E-70; one such rule made none, E-71); no census measure predicts how soon (E-71, E-72, E-74). **SUBLEQ:** tile density passed once and failed under another jump rule (E-75 phases 3, 4); the product rate passed looking back and was undecided looking forward (phases 6, 7) |
| O7 | Make every result reproducible and verifiable | done: seeds, specs, commits, exports, `reproduce` |

### Requirements (set by the project owner at the start)

| Requirement | Where it lives | Status |
|---|---|---|
| **Multiple universes**: 2D cellular automata first, each with its own simple fixed rules and random initial conditions | `emergence/physics/`, `engine.py` | done; initial-condition kinds added in v0.4; Lenia family added from v0.5. Program soups (BFF, SUBLEQ family; `emergence/programs/`, run by scripts) are a third family but have no space and are not covered by the engine |
| **Automated observatory**: independently monitor activity, entropy, recurring patterns, persistent structures and other indicators of emergent complexity, without interfering | `emergence/observatory/` | done for the spatial families; program soups have their own detectors (`observatory/replicators.py`, `program_heredity.py`, `program_fitness.py`, `program_parasites.py`, `programs/inherit.py`), called from scripts |
| **Discovery engine**: automatically explore rule sets, identify unusual or promising universes, prioritise further investigation; no single complexity score or predefined idea of life | `emergence/discovery.py` | done for the spatial families (last used in E-17); soup rule versions are chosen by hand-built censuses, not by the discovery engine |
| **Visualisation**: interactive dashboard to watch, pause, rewind, zoom, compare, and inspect discoveries and their histories | `emergence/server.py`, `web/` | done for the spatial families; program soups are not in the dashboard |
| **Scientific reproducibility**: record rules, seeds, measurements and discoveries | `storage.py`, `emergence reproduce`, `docs/data/` | done |
| **Efficiency**: runs on a normal laptop with no GPU, cloud services or paid APIs | NumPy/SciPy only | done (~4 min per 600-rule experiment on 4 cores); single soup experiments now take 6 to 12 hours on a laptop (E-75 phases 3, 4, 7) |

### Principles

1. **Complexity must emerge from each universe's own rules**, not from external intervention. Observation is passive; interventions run only on forked clones (D-003).
2. **Keep the simulation engine separate from the observatory** (`lab.py` is the only place they meet).
3. **Distinguish randomness, repetitive patterns and meaningful emergent organisation**: surrogate compression, local periodicity, damage spreading, deceptive controls.
4. **Design for other kinds of physics** beyond cellular automata. Spatial families use the `Physics` interface: Life-like rules, and the Lenia family (Lenia, Flow-Lenia, multi-channel Lenia). Program soups (BFF and a SUBLEQ family) are a third family: they have no space, and the engine, discovery engine and dashboard do not cover them; they run in `emergence/programs/` and scripts.
5. **Prefer simple, established scientific methods** over unnecessary complexity.

Added during the work: every claim carries its evidence level, and every detector is validated against a control built to fool it.

## Evidence ladder

Each discovery is tagged with the highest level its evidence supports (D-014). Levels 4 and 5 are never assigned until there is a validated measurement for them.

| Level | Meaning | How it is measured | Reached? |
|---|---|---|---|
| 1 | Persistent organization | ≥ 4 persistent shape types, reproduced across seeds (calibrated robustness) | yes |
| 2 | Self-propelled structures | + shapes that travel on their own in an isolated clone | yes: Life-like (#1181); Lenia, arising spontaneously from smooth starts (E-14). Not applicable to program soups (no space) |
| 3 | Self-replication | a shape makes a growing number of exact copies of itself alone, and random patterns neither copy themselves nor produce it | yes: one multi-channel Lenia rule, dividing spots of a single type (E-32); BFF soups from random code (E-40, E-41); SUBLEQ versions we added (E-75). Not in Life-like rules (detector validated on HighLife's replicator) |
| 4 | Heredity and variation | variants of a replicator also replicate, and pass the variation on | yes in BFF: one-byte mutations inherited in 9 of 9 replicators (E-42). Not possible in the Lenia reproducer (one type); not tested in SUBLEQ |
| 5 | Open-ended evolution | innovation that continues, and builds on earlier innovation | not shown: in BFF soups later code is not fitter by four measures (E-48 to E-54); knockouts ≈ placebo in Life-like rules (J-010) |

## Hypotheses and status

| | Hypothesis | Status |
|---|---|---|
| H1 | Guided search beats random search at equal compute | supported (E-77: 20 paired seeds, pre-registered; distinct rules with self-propelled structures 1.84× [1.70, 2.25], complex on every seed 3.4× [2.6, 3.9], engine ahead on 20 of 20 seeds, p = 9.5 × 10⁻⁷; Life-like/Generations rules only, one budget; self-propulsion is one of the engine's own objectives) |
| H2 | Spontaneous self-replication occurs in Life-like / Generations rules at 96×96, ≤ 2000 steps | not observed (0 / 17 top candidates) |
| H3 | Some rules show ongoing innovation | not observed; 2 inconclusive (chaos-like universes, no matched null) |
| H4 | Initial conditions modulate how much complexity a fixed rule produces | Life-like rules: not supported as tested; the patch effect disappears at matched density (E-09, E-10); density itself matters; the gradient signal is weak and untested. **Lenia: supported** in the rules tested: smooth starts make gliders, soups with the same mass almost never do (E-14, pre-registered), and the spatial arrangement is the cause (E-19) |
| H6 | Earlier innovations enable later ones (cumulative innovation) | not observed: real knockouts are indistinguishable from placebo deletions, P(real > placebo) = 0.49–0.51 across 92 tests (E-10, E-11) |
| H5 | A richer physics family (continuous CA) reaches higher evidence levels under the same search budget | not tested as stated. Higher levels were reached outside Life-like rules (level 3 in one multi-channel Lenia rule, E-32; level 4 in BFF soups, E-42), but no comparison of families at equal search budget was run, and the soups are a different kind of system (no space), so this is not evidence for H5 |

## What the negative results do and do not mean

They mean the *top candidates of this search*, in *this rule family*, at *this scale and duration*, show no replication or ongoing innovation that clearly beats chance. They do **not** show that simple CAs can't evolve: 17 candidates, 96×96 worlds and ≤ 2000 steps are a tiny sample. Known self-replicators exist even in this family (HighLife's), and they just don't arise or survive in these soups.

## Next steps

Proposed plan for the next phase (D-018). The ordering takes the third review ([R-3]({{ '/reviews.html#r-3' | relative_url }})) into account.

**Current status (15 November 2026; review [R-5]({{ '/reviews.html#r-5' | relative_url }})).** Tracks B, C and D below are done; in Track A, the knockout test is done and H1 was re-run at 20 seeds per arm and passed (E-77, J-087). Since 9 November most work asked which rule versions make replicators, and how soon. That predictor thread is being wound down: a one-rate synthesis (one rate per rule, the chance that a run writes a replicator, estimated with the rule as the unit) will summarise it, with at most one more run. The next main question was level 5 with space. It was tested by a pre-registered fork of 7 jumped BFF soups into neighbour-only and well-mixed continuations (E-78, J-089, 15 November): it fails. In the neighbour-only soups, late code is no fitter in a well-mixed common garden, and no parasites appear. Instruments that see advantages existing only in space are not built yet.

**Track A: innovation science** (step 3 done; step 4 in progress; steps 1, 2 and 5 open)
1. **Sampling validation:** run the innovation probe against continuous observation (every step) on ~10 universes, and quantify missed and spurious types.
2. **Same-rule null:** compare a universe's late innovation with independent seeds of the same rule at the same age. This separates rule-level regularity from history-specific events, which is the null we actually need for "cumulative".
3. *(Done: J-010, E-10, E-11; knockouts ≈ placebo.)* **Causal knockout test** for "earlier innovations enable later ones": when a new type appears, delete it in a clone and check whether the later new types still appear. Dependency means cumulative structure. This is an intervention on clones, which the architecture already supports (D-003).
4. *(Done for H1: E-77, 20 paired seeds.)* **Statistics:** 10–30 runs per arm for H1, with confidence intervals; probe rates per 1000 steps.
5. **Replication:** rename positives to "candidate self-replicator"; use more null patterns (≥ 20); trace where each copy came from.

**Track B: initial conditions** (cheap; no new physics). *Done: Life-like rules (E-09, E-10, J-009); Lenia smooth starts (E-13, E-14, E-19, E-24).*
- Same rule, different starting worlds: uniform soup, density gradients, a localized seed patch in vacuum, walls or compartments, sparse "resource" regions. Measure how evidence levels and innovation change. This adds a starting-condition generator to `UniverseSpec`; the observatory stays as it is.

**Track C: a second physics family**. *Done: Lenia (E-12 onwards), Flow-Lenia (E-16), multi-channel Lenia (E-32). The comparison of families at equal compute was not run (H5).*
- Lenia (continuous states, smooth kernels) behind the existing `Physics` interface: FFT convolution on CPU, with its own structure detector (thresholded mass, connected components) and an adapted replication probe.
- Validate it against published reference patterns imported from the Lenia authors' data, not retyped from memory.
- Compare families on the evidence ladder at equal compute, not on raw metric values.

**Track D: reproduction and heredity** (added 2026-11-07, J-032; the owner asked what could give them). *Done: every route below was tried; reproduction was found in multi-channel Lenia (route 4) and in program soups (route 5), heredity in BFF soups (E-42).*

Status: a birth detector for both physics families is built and validated (`observatory/births.py`, D-028: two generations in isolation, positives HighLife replicator and Gray-Scott spots). E-27 tests it on the Lenia worlds we have. Since J-033: a transplant **heredity test** (`observatory/heredity.py`, D-029, controls on Gray-Scott spots with a carried / redrawn / position-set trait) and **`FlowLeniaPL`** (route 3's physics, with food) are built and validated. E-29 tests route 2 directly (every random Lenia rule, a lone lump, the birth detector) E-30, the first fed FlowLeniaPL scan, found 0 reproducers after a false alarm from unstable food was removed (J-035, D-030: perturbed-vacuum null). Next: a held-out fed scan restricted to rules with stable food. Routes, roughly by cost:
1. **Known reproducers as controls** (done): HighLife's replicator (discrete) and Gray-Scott's dividing spots (Pearson 1993). Both copy identically: reproduction without heredity.
2. *(Tried: E-29, no reproducer in 3000 random rules; looks unpromising in single-channel Lenia.)* **A fission objective for Lenia search:** reward a rising object count at constant mass per object, from smooth starts (D-025), then confirm with the birth detector.
3. *(Tried: E-30, E-31, no reproducer in fed worlds.)* **Flow-Lenia with parameter localization** (Plantec et al. 2023), the main route to heredity. Each cell carries a parameter vector (e.g. mu, sigma and the kernel weights h) that moves with its matter in the same reintegration step; where flows meet, parameters mix in proportion to the incoming mass, with optional small mutation. The update rule stays fixed and local; what varies is where each "species" sits. Plan:
   - **Physics:** `FlowLeniaPL`, state of shape (1 + P, h, w) float32 (mass plus P parameter channels, stored as mass-weighted sums so mixing is exact and mass-conserving); `view` = mass. The growth step uses each cell's own parameters.
   - **Fed worlds:** in vacuum a mass-conserving creature cannot double, so the birth test runs in a world with a thin uniform layer of free matter ("food"), with a food-only world as the background null.
   - **Lineage and heredity measure:** track objects with their mean parameter vector; at each split, record parent and child vectors. Heredity = parent-offspring regression slope of the parameters, against a null that pairs each child with a random parent of the same time window. Positive control: two hand-placed populations with different parameters (offspring must resemble their own parent). Negative: one population with mixing at every step (parameters blur to the mean; slope near 0).
   - **First experiment:** random multi-species starts (several patches, each with random parameters) in fed worlds; outcome: worlds with a verified reproducer, and the heredity slope with its null.
4. *(Done: E-32, one rule with dividing spots of a single type.)* **Multi-channel Lenia** (Chan 2020 reports self-replicating creatures there): a larger physics change, after 3.
5. *(Done: BFF from E-40, SUBLEQ family in E-75; it became the project's main substrate.)* **Program soups** (Agüera y Arcas et al. 2024: self-replicators emerge from random BFF programs) as a separate substrate, closest to "spontaneous emergence from fixed rules"; would be its own project.

## Could this be academic research?

Yes. Automated discovery in cellular automata is an active area, so the contribution has to be clear. **A literature review by AI agents (16 November 2026, J-091) is on the [Literature]({{ '/literature.html' | relative_url }}) page.** It is not exhaustive and has had no expert check. Two of our results were already published, most are partly known, and the strongest remaining contributions are controlled counterfactuals that were "not found in this search" (not the same as new). The list below is the earlier, unchecked starting list:
- **Classic theory:** Wolfram's classes, Langton's λ and the edge of chaos.
- **Surveys of Life-like rules:** e.g. Eppstein's work on growth and decay.
- **Compression-based classification:** Zenil.
- **Evolutionary search for gliders:** Sapin and colleagues.
- **Lenia:** Chan, and its follow-ups.
- **Intrinsically-motivated diversity search in self-organizing systems:** Reinke, Etcheverry and Oudeyer.
- **Foundation-model-guided search for artificial life:** Kumar and colleagues.
- **Open-endedness measures:** Bedau and Packard's evolutionary activity statistics; Channon.

### Literature notes: Lenia and spontaneous movers (2026-11-07, J-013)

A first focused review: papers and code read where available, abstracts only where marked in J-013. What it changed for us:
- **Chan's random starts were not soups.** Chan (2019, *Complex Systems* 28(3); arXiv 1812.05433) writes that creatures such as Orbium emerge "given enough time" from random starts, but gives no rate. His code (`LeniaND.py`, MIT) seeds **15–39 dense square patches of side 0.9 R, values uniform in [0, 0.9), in vacuum** (`np.random.randint(15, 40)`; corrected in J-091; our `patch_mask` draws 15–40). Our E-12 soup filled the whole grid. Most of his 400+ species came from interactive evolution, not soups.
- **Nobody has published a rate.** We found no estimate of what fraction of Lenia rule space supports movers, or how often they emerge. Chan's μ–σ maps are qualitative (a narrow "river" of creatures). Our E-13a scan gives a first number: 8 of 99 single-ring rules.
- **Flow-Lenia** (Plantec et al., ALIFE 2023, arXiv 2212.07906; *Artificial Life* 31(2), 2025):
  - **Mechanism:** mass conservation, via a flow along the affinity gradient and reintegration tracking.
  - **Claims:** localized and moving patterns are "quite common" from a random central patch, and per-cell parameters (parameter localization) allow evolution inside the simulation.
  - **Weak spots:** no counts of movers; the 2025 evolution analysis uses parameter-point "species", 5 seeds and no neutral (shadow) model. We treat these as hypotheses to test, not results to inherit.
  - **Our runs (J-016, E-16) are not comparable with the paper** (J-091, D-066): single channel, few kernels, mostly R = 13, and a detector that counts only isolated translating structures, against a paper that gives no rate and counts gyrating patterns as dynamic. They are not a failed reproduction.
- **Other routes:**
  - Asymptotic Lenia (Kawaguchi et al. 2021) and its "glider equation" (Kojima et al. 2025);
  - Particle Lenia (Mordvintsev et al. 2022);
  - diversity search (Reinke et al. ICLR 2020; Etcheverry et al. NeurIPS 2020; Faldor & Cully ALIFE 2024; Hamon et al. 2024);
  - foundation-model search (Kumar et al. 2024).

  None of these measures *spontaneous, within-run* emergence with nulls. That is the gap our validation-first approach can fill. *(J-091: this held for the eight Lenia-family works the review checked; two non-Lenia preprints, Yin 2026 and Hintze and Bohm 2025, claim spontaneous self-replication in cellular automata, without selection-aware nulls. See [Literature]({{ '/literature.html' | relative_url }}).)*

**Our likely contribution:** a *validated* discovery methodology. Every detector is tested against deceptive controls, causal claims are tested by intervention on clones, and the search is compared with a baseline at equal compute. The results include negative findings. Most automated-discovery work reports what it found; much less reports how often it is fooled.

**Needed before submission:**
- a real literature review *(a first one by AI agents is done, J-091, [Literature]({{ '/literature.html' | relative_url }}); a check by a human expert is still needed)*;
- 20–30 runs per condition, with confidence intervals and analyses specified in advance;
- matched nulls for innovation;
- at least two physics families;
- frozen code and data (already reproducible).

**Plausible venues:** the ALIFE conference (full paper or extended abstract), the *Artificial Life* journal, *Complex Systems*. A collaborator from the ALife community would help with positioning.
