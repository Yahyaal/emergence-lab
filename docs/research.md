---
title: Research
description: The research question, hypotheses, evidence ladder, related work, and the path to a publishable result.
---

# Research

## Question

How much genuine, persistent and eventually *evolving* complexity can arise from simple, fixed local rules, without any outside design? Which properties of the rules, or of the initial conditions, make it more likely?

Principles: complexity must come from each universe's own rules; the observatory never interferes; randomness, repetition and organisation must be told apart; established, simple methods are preferred; and every claim carries its evidence level.

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
| H4 | Initial conditions modulate how much complexity a fixed rule produces | open, proposed |
| H5 | A richer physics family (continuous CA) reaches higher evidence levels under the same search budget | open, proposed |

## What the negative results do and do not mean

They mean the *top candidates of this search*, in *this rule family*, at *this scale and duration*, show no replication or ongoing innovation that clearly beats chance. They do **not** show that simple CAs can't evolve: 17 candidates, 96×96 worlds and ≤ 2000 steps are a tiny sample. Known self-replicators exist even in this family (HighLife's), and they just don't arise or survive in these soups.

## Next steps

Proposed plan for the next phase (D-018). The ordering takes the third review ([R-3]({{ '/reviews.html#r-3' | relative_url }})) into account.

**Track A: innovation science** (highest priority)
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

**Our likely contribution:** a *validated* discovery methodology. Every detector is tested against deceptive controls, causal claims are tested by intervention on clones, and the search is compared with a baseline at equal compute. The results include negative findings. Most automated-discovery work reports what it found; much less reports how often it is fooled.

**Needed before submission:**
- a real literature review;
- 20–30 runs per condition, with confidence intervals and analyses specified in advance;
- matched nulls for innovation;
- at least two physics families;
- frozen code and data (already reproducible).

**Plausible venues:** the ALIFE conference (full paper or extended abstract), the *Artificial Life* journal, *Complex Systems*. A collaborator from the ALife community would help with positioning.
