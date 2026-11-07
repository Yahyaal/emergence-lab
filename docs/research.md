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
| O1 | Build an observatory that tells randomness, repetition and organisation apart, *validated against deceptive controls* | done for 2D CA (59 benchmark checks); extended with every new detector |
| O2 | Build a discovery engine that finds interesting universes more efficiently than random search, without a single complexity score | supported, preliminary (H1) |
| O3 | Find universes with persistent organisation and self-propelled structures (evidence levels 1–2) | reached |
| O4 | Detect spontaneous self-replication (level 3), and then heredity and variation (level 4) | detector validated; none observed |
| O5 | Detect cumulative, open-ended innovation, where new structures enable further new structures (level 5) | knockout test built and validated; not observed (J-010) |
| O6 | Identify which properties of the rules *or the initial conditions* make complexity more likely (H4, H5) | first study done: matter density matters, its spatial arrangement didn't (J-009); rule properties open; Lenia physics and its label validated (J-012), experiments pending |
| O7 | Make every result reproducible and verifiable | done: seeds, specs, commits, exports, `reproduce` |

### Requirements (set by the project owner at the start)

| Requirement | Where it lives | Status |
|---|---|---|
| **Multiple universes**: 2D cellular automata first, each with its own simple fixed rules and random initial conditions | `emergence/physics/`, `engine.py` | done; initial-condition kinds added in v0.4 |
| **Automated observatory**: independently monitor activity, entropy, recurring patterns, persistent structures and other indicators of emergent complexity, without interfering | `emergence/observatory/` | done |
| **Discovery engine**: automatically explore rule sets, identify unusual or promising universes, prioritise further investigation; no single complexity score or predefined idea of life | `emergence/discovery.py` | done |
| **Visualisation**: interactive dashboard to watch, pause, rewind, zoom, compare, and inspect discoveries and their histories | `emergence/server.py`, `web/` | done |
| **Scientific reproducibility**: record rules, seeds, measurements and discoveries | `storage.py`, `emergence reproduce`, `docs/data/` | done |
| **Efficiency**: runs on a normal laptop with no GPU, cloud services or paid APIs | NumPy/SciPy only | done (~4 min per 600-rule experiment on 4 cores) |

### Principles

1. **Complexity must emerge from each universe's own rules**, not from external intervention. Observation is passive; interventions run only on forked clones (D-003).
2. **Keep the simulation engine separate from the observatory** (`lab.py` is the only place they meet).
3. **Distinguish randomness, repetitive patterns and meaningful emergent organisation**: surrogate compression, local periodicity, damage spreading, deceptive controls.
4. **Design for other kinds of physics** beyond cellular automata (the `Physics` interface; Lenia is planned).
5. **Prefer simple, established scientific methods** over unnecessary complexity.

Added during the work: every claim carries its evidence level, and every detector is validated against a control built to fool it.

## Evidence ladder

Each discovery is tagged with the highest level its evidence supports (D-014). Levels 4 and 5 are never assigned until there is a validated measurement for them.

| Level | Meaning | How it is measured | Reached? |
|---|---|---|---|
| 1 | Persistent organization | ≥ 4 persistent shape types, reproduced across seeds (calibrated robustness) | yes |
| 2 | Self-propelled structures | + shapes that travel on their own in an isolated clone | yes (#1181) |
| 3 | Self-replication | a shape makes a growing number of exact copies of itself alone, and random patterns neither copy themselves nor produce it | not observed (detector validated on HighLife's replicator) |
| 4 | Heredity and variation | variants of a replicator also replicate, and pass the variation on | not measured |
| 5 | Open-ended evolution | innovation that continues, and builds on earlier innovation | not measured; innovation probe is a precursor |

## Hypotheses and status

| | Hypothesis | Status |
|---|---|---|
| H1 | Guided search beats random search at equal compute | supported, preliminary (n = 2 seeds per arm; 1.9–4.2× after removing near-duplicates) |
| H2 | Spontaneous self-replication occurs in Life-like / Generations rules at 96×96, ≤ 2000 steps | not observed (0 / 17 top candidates) |
| H3 | Some rules show ongoing innovation | not observed; 2 inconclusive (chaos-like universes, no matched null) |
| H4 | Initial conditions modulate how much complexity a fixed rule produces | not supported as tested: the patch effect disappears at matched density (E-09, E-10); density itself matters; the gradient signal is weak and untested |
| H6 | Earlier innovations enable later ones (cumulative innovation) | not observed: real knockouts are indistinguishable from placebo deletions, P(real > placebo) = 0.49–0.51 across 92 tests (E-10, E-11) |
| H5 | A richer physics family (continuous CA) reaches higher evidence levels under the same search budget | open, proposed |

## What the negative results do and do not mean

They mean the *top candidates of this search*, in *this rule family*, at *this scale and duration*, show no replication or ongoing innovation that clearly beats chance. They do **not** show that simple CAs can't evolve: 17 candidates, 96×96 worlds and ≤ 2000 steps are a tiny sample. Known self-replicators exist even in this family (HighLife's), and they just don't arise or survive in these soups.

## Next steps

Proposed plan for the next phase (D-018). The ordering takes the third review ([R-3]({{ '/reviews.html#r-3' | relative_url }})) into account.

Status after v0.4: the knockout test (Track A, step 3) and the initial-conditions study (Track B) are done (J-009, J-010). Both are negative and the result is robust. That strengthens the case for Track C: the outer-totalistic family at this scale shows no replication or cumulative innovation under any starting condition tried. Suggested order now:
1. Lenia (Track C) with the same probes.
2. A density sweep for the rules where density mattered.
3. Track A steps 1, 2 and 4.

**Track A: innovation science**
1. **Sampling validation:** run the innovation probe against continuous observation (every step) on ~10 universes, and quantify missed and spurious types.
2. **Same-rule null:** compare a universe's late innovation with independent seeds of the same rule at the same age. This separates rule-level regularity from history-specific events, which is the null we actually need for "cumulative".
3. **Causal knockout test** for "earlier innovations enable later ones": when a new type appears, delete it in a clone and check whether the later new types still appear. Dependency means cumulative structure. This is an intervention on clones, which the architecture already supports (D-003).
4. **Statistics:** 10–30 runs per arm for H1, with confidence intervals; probe rates per 1000 steps.
5. **Replication:** rename positives to "candidate self-replicator"; use more null patterns (≥ 20); trace where each copy came from.

**Track B: initial conditions** (cheap; no new physics)
- Same rule, different starting worlds: uniform soup, density gradients, a localized seed patch in vacuum, walls or compartments, sparse "resource" regions. Measure how evidence levels and innovation change. This adds a starting-condition generator to `UniverseSpec`; the observatory stays as it is.

**Track C: a second physics family**
- Lenia (continuous states, smooth kernels) behind the existing `Physics` interface: FFT convolution on CPU, with its own structure detector (thresholded mass, connected components) and an adapted replication probe.
- Validate it against published reference patterns imported from the Lenia authors' data, not retyped from memory.
- Compare families on the evidence ladder at equal compute, not on raw metric values.

**Track D: reproduction and heredity** (added 2026-11-07, J-032; the owner asked what could give them)

Status: a birth detector for both physics families is built and validated (`observatory/births.py`, D-028: two generations in isolation, positives HighLife replicator and Gray-Scott spots). E-27 tests it on the Lenia worlds we have. Since J-033: a transplant **heredity test** (`observatory/heredity.py`, D-029, controls on Gray-Scott spots with a carried / redrawn / position-set trait) and **`FlowLeniaPL`** (route 3's physics, with food) are built and validated. E-29 tests route 2 directly (every random Lenia rule, a lone lump, the birth detector) and E-30 is the first fed FlowLeniaPL scan. Routes, roughly by cost:
1. **Known reproducers as controls** (done): HighLife's replicator (discrete) and Gray-Scott's dividing spots (Pearson 1993). Both copy identically: reproduction without heredity.
2. **A fission objective for Lenia search:** reward a rising object count at constant mass per object, from smooth starts (D-025), then confirm with the birth detector.
3. **Flow-Lenia with parameter localization** (Plantec et al. 2023), the main route to heredity. Each cell carries a parameter vector (e.g. mu, sigma and the kernel weights h) that moves with its matter in the same reintegration step; where flows meet, parameters mix in proportion to the incoming mass, with optional small mutation. The update rule stays fixed and local; what varies is where each "species" sits. Plan:
   - **Physics:** `FlowLeniaPL`, state of shape (1 + P, h, w) float32 (mass plus P parameter channels, stored as mass-weighted sums so mixing is exact and mass-conserving); `view` = mass. The growth step uses each cell's own parameters.
   - **Fed worlds:** in vacuum a mass-conserving creature cannot double, so the birth test runs in a world with a thin uniform layer of free matter ("food"), with a food-only world as the background null.
   - **Lineage and heredity measure:** track objects with their mean parameter vector; at each split, record parent and child vectors. Heredity = parent-offspring regression slope of the parameters, against a null that pairs each child with a random parent of the same time window. Positive control: two hand-placed populations with different parameters (offspring must resemble their own parent). Negative: one population with mixing at every step (parameters blur to the mean; slope near 0).
   - **First experiment:** random multi-species starts (several patches, each with random parameters) in fed worlds; outcome: worlds with a verified reproducer, and the heredity slope with its null.
4. **Multi-channel Lenia** (Chan 2020 reports self-replicating creatures there): a larger physics change, after 3.
5. **Program soups** (Agüera y Arcas et al. 2024: self-replicators emerge from random BFF programs) as a separate substrate, closest to "spontaneous emergence from fixed rules"; would be its own project.

## Could this be academic research?

Yes. Automated discovery in cellular automata is an active area, so the contribution has to be clear. Related work to position against (to be checked in a proper literature review):
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
- **Chan's random starts were not soups.** Chan (2019, *Complex Systems* 28(3); arXiv 1812.05433) writes that creatures such as Orbium emerge "given enough time" from random starts, but gives no rate. His code (`LeniaND.py`, MIT) seeds **15–40 dense square patches of side 0.9 R, values uniform in [0, 0.9], in vacuum**. Our E-12 soup filled the whole grid. Most of his 400+ species came from interactive evolution, not soups.
- **Nobody has published a rate.** We found no estimate of what fraction of Lenia rule space supports movers, or how often they emerge. Chan's μ–σ maps are qualitative (a narrow "river" of creatures). Our E-13a scan gives a first number: 8 of 99 single-ring rules.
- **Flow-Lenia** (Plantec et al., ALIFE 2023, arXiv 2212.07906; *Artificial Life* 31(2), 2025):
  - **Mechanism:** mass conservation, via a flow along the affinity gradient and reintegration tracking.
  - **Claims:** localized and moving patterns are "quite common" from a random central patch, and per-cell parameters (parameter localization) allow evolution inside the simulation.
  - **Weak spots:** no counts of movers; the 2025 evolution analysis uses parameter-point "species", 5 seeds and no neutral (shadow) model. We treat these as hypotheses to test, not results to inherit.
- **Other routes:**
  - Asymptotic Lenia (Kawaguchi et al. 2021) and its "glider equation" (Kojima et al. 2025);
  - Particle Lenia (Mordvintsev et al. 2022);
  - diversity search (Reinke et al. ICLR 2020; Etcheverry et al. NeurIPS 2020; Faldor & Cully ALIFE 2024; Hamon et al. 2024);
  - foundation-model search (Kumar et al. 2024).

  None of these measures *spontaneous, within-run* emergence with nulls. That is the gap our validation-first approach can fill.

**Our likely contribution:** a *validated* discovery methodology. Every detector is tested against deceptive controls, causal claims are tested by intervention on clones, and the search is compared with a baseline at equal compute. The results include negative findings. Most automated-discovery work reports what it found; much less reports how often it is fooled.

**Needed before submission:**
- a real literature review;
- 20–30 runs per condition, with confidence intervals and analyses specified in advance;
- matched nulls for innovation;
- at least two physics families;
- frozen code and data (already reproducible).

**Plausible venues:** the ALIFE conference (full paper or extended abstract), the *Artificial Life* journal, *Complex Systems*. A collaborator from the ALife community would help with positioning.
