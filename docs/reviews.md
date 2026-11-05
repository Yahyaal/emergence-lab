---
title: Reviews
description: External reviews of the work, and how each point was handled.
---

# Reviews

The project owner shared the work with ChatGPT for independent review three times. Each review is summarised with our response: agreed (implemented), qualified, or pushed back (with evidence). Reviews were of source code; our responses include the experiments run to check their claims.

## R-1 · Review of v0.1 {#r-1}

| Point | Response |
|---|---|
| Mover detection may mistake coincidences for moving objects | **Agreed, checked empirically.** No candidate movers on pure i.i.d. noise across densities 0.05–0.5. Chaotic rules only produced candidates where real spaceships are documented (Seeds, Brian's Brain). We still added an intervention test: the shape must travel alone in an isolated clone (D-007). It later rejected v0.1's #463 and 1 noise candidate |
| Rewarding "no cycle within N steps" credits slowly dying universes | **Agreed.** Replaced with a *sustained* objective (scaled by activity trend) and an extended 4× run (D-011) |
| Excluding periodic worlds from breeding may lose interesting rules | **Qualified.** Only *locally* periodic universes (≥ 95% of changing cells oscillate in place) were excluded; universes that repeat as a whole because gliders loop were never excluded. The real flaw was the hard threshold, which was replaced with continuous measures |
| No evolutionary tracking | **Agreed on the goal, but premature.** We built the validation infrastructure first (benchmark, controls), then probes in v0.3 |
| Don't add physics until the observatory is validated | **Agreed** at the time; revisited in R-3 |

## R-2 · Review of v0.2 {#r-2}

| Point | Response |
|---|---|
| Robustness threshold 0.5 is arbitrary | **Agreed, confirmed with data:** 29% of *different-rule* pairs were closer than 0.5. Now calibrated per experiment (D-010) |
| Tournament relies on implicit sort order | **Agreed:** made explicit |
| "Verified mover" overstates what isolation shows | **Agreed:** renamed *self-propelled*; trajectory identity is documented as unverified |
| "Persists" ≠ new organization | **Agreed, and the most important point.** Built the innovation probe (D-016); a glider gun is the control |
| Use a known self-replicator as a positive control, e.g. Fredkin's rule | **Pushed back:** Fredkin's rule copies *every* pattern, so it is a deceptive control (rule-level duplication). The positive control is HighLife's replicator (D-015) |
| Go straight to a replication detector | **Pushed back on the order:** first a random-search baseline (does the engine work at all?) and an innovation measure; then replication |

## R-3 · Review of v0.3 (PR #1) {#r-3}

| Point | Response |
|---|---|
| Two seeds per arm is too few for H1 | **Agreed:** 10–30 runs per arm planned (Track A); the claim is labelled preliminary |
| Innovation probe samples short bursts and can miss or misdate types | **Agreed:** we already found one case (period-840 aliasing). Validation against continuous observation is planned |
| Replication probe may be too restrictive (single offspring, resource-dependent, distributed or varied offspring) | **Agreed as a known trade-off:** it is a high-specificity screen, not a definition of reproduction. Positives will be called *candidate self-replicators*; more nulls and copy-origin tracing are planned |
| Use correlation-preserving surrogates (block resampling etc.) as the innovation null | **Qualified:** for persistence-based measures, space-time block surrogates either break persistence (too easy a null) or copy it inside blocks (meaningless). We prefer a **same-rule, independent-seed null** plus **causal knockouts** on clones to test "earlier innovations enable later ones", which is the property R-3 itself identifies as what matters |
| Introduce richer physics now (Lenia), as a second track | **Agreed** (D-018 Track C), with its own structure detector and published reference patterns as controls |
| Study initial conditions and environments under fixed rules | **Agreed, and prioritised:** it is cheap and needs no new physics (Track B) |
| Merge PR #1 as the baseline | **Agreed** |
