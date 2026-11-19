---
title: Reviews
description: External reviews of the work, and how each point was handled.
---

# Reviews

The work has had five reviews: three by ChatGPT, shared by the project owner (R-1 to R-3), an independent agent review of the overnight Lenia work (R-4), and a review of the project's goal and approach by Claude at the owner's request (R-5). Each review is summarised with our response: agreed (implemented), qualified, pushed back (with evidence), or open. R-1 to R-3 were reviews of source code; our responses include the experiments run to check their claims.

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


## R-4 · Independent review of the overnight Lenia work (J-012 to J-019) {#r-4}

An independent agent with no part in the work reviewed the journal, data, code and report (2026-11-07, about 04:00). It recomputed statistics from the exports and ran two small nulls.

| Point | Response |
|---|---|
| Smooth starts differ from soups in value distribution (more weakly filled cells), not only in spatial correlation; "arrangement matters" is confounded. The proper null is a shuffled smooth field | **Agreed.** Added init kind `smooth_shuffled`; E-19a (pre-registered) tests smooth vs shuffled. Report claim softened until then |
| Soups die (density 0.10) or freeze (0.35) at every density tried, so "0/160" was close to guaranteed | **Agreed.** E-19b sweeps soup density 0.12–0.30 across the transition |
| Rule-level evidence is weaker than universe-level p: 6 of 8 rules, rule-level sign test p = 0.031 | **Agreed.** Claims restated as "in these 8 rules" (J-015) |
| Mover-verification code not committed; three JSONs not reproducible | **Agreed, most important.** `scripts/verify_movers.py` committed and used for E-18 and E-19. E-13/E-14/E-17 regenerated with it (`docs/data/experiments/2026-11-07-e1{3,4,7}-verify-movers.json`): 18/18, 51/51 and 5/7 survive, identical to the earlier ad-hoc results |
| Detector not validated for slow or turning movers; D-022's 0.002 cut-off was set after viewing data, with no held-out check | **Agreed.** Measured (J-022): the detector finds about 92% of wanderers; 1 of 104 was hidden by the quasi-static cut-off. Added a slow, turning positive to the benchmark. Still open: a detector change for turning movers, and a held-out check of the cut-off |
| E-15 "mass only drops" is contradicted by small rises; "never multiply" too strong | **Agreed.** Corrected to "no births seen, weak evidence" |
| Numbers: 51 structures (not 49); 9/160 soups unsettled (not "all freeze"); 12 seed shapes (not 8); E-13 did find a σ 0.0195 glider; path vs net speed of the wanderer; `compare`'s self-propelled count definition | **All confirmed and corrected** |
| "Small island of rule space" contradicted by the E-17 wanderer; island count not deduplicated | **Agreed.** Now "among single-ring rules"; non-deduplicated count labelled |
| "New kind of creature" may already be in Chan's catalogue | **Agreed.** We claim only "new to this project" |


## R-5 · Goal and approach review (2026-11-14) {#r-5}

Reviewer: Claude, at the owner's request, on branch `v3.7-copiercount` (E-75 phase 7, J-085). It read the research page, handoff, decisions, reviews, the report summary and sections 27 to 34, journal entries J-077 to J-085, the E-75 design and the exported data of phases 6 and 7. It did not re-run experiments, the tests or the benchmark. The owner answered the first question and asked the reviewer for its suggestion on the other two, then asked it to plan and carry out the follow-up work. So, apart from that first answer, the responses below are the reviewer's proposals, acted on unless the owner overrules them; points with no action yet are marked open.

| Point | Response |
|---|---|
| **Verdict:** the science is on goal and careful. The founding principles (passive observation, nothing planted, deceptive controls, claims held at their evidence level) have been kept, and failed predictions are recorded as failures | Noted; no action asked |
| **Verdict:** the drift is one of emphasis. 26 of 75 experiments and phases, and nearly everything since 9 November, ask which rule versions make replicators, and how soon (objective O6, about where level 3 appears); levels 4 and 5, the "evolving" half of the goal, are parked | **Agreed.** The predictor thread ends after at most one more run, and the next main question is level 5 (spatial test, below) |
| **Verdict:** the predictor chase has reached its natural end. One result is robust (in BFF variants, a rule whose shortest copier makes a working copy makes replicators); in SUBLEQ each predictor passed once, then failed to transfer or came out undecided, and the newest costs about a quarter of the experiment it predicts | **Agreed.** The thread ends after at most one more run |
| **Verdict:** a simpler model already explains most of it: a jump is the wait for one rare event (J-083), so one rate per rule, measured from the soups, could replace five censuses | **Agreed; done (E-76, J-086).** A fair first description, not exact: 8 of 26 rules deviate from a constant rate |
| **Verdict:** the written record is redundant and stale at the same time: each result is written in five or six places, the overview still said level 2, and the published site stops at E-65 because pull requests are waiting | **Agreed; in progress:** the four stale pages are refreshed (this change, branch `v3.8-docs-refresh`). The merge queue is open (recommendation 7). The [Paper]({{ '/paper.html' | relative_url }}) (J-090) adds one more summary, but it is the only one that sources every number; redundancy is not reduced by it |
| **1.** Close the predictor thread with one model (one rate per rule, estimated from time to jump across soups, rule as the unit, survival analysis) and stop adding censuses; run phase 8 at most once, as a test of whether the rate rises with soup age | **Agreed; synthesis done (E-76).** It found no rise of the rate with soup age, so the reviewer now recommends not running phase 8 as drafted (D-063). **Owner approved on 16 November 2026 (D-063 accepted, J-092): phase 8 will not be run as drafted.** |
| **2.** Go back to level 5 with the instruments already built (kin-free invasion, growth rate, parasite detector), comparing soups where programs meet only their neighbours on a grid against well-mixed soups, pre-registered. The reviewer's own suggestion, untested here | **Agreed:** the spatial level-5 test is to be pre-registered |
| **3.** Make the rule the unit of analysis: report by-rule tests first, size designs by rules, and count rare rules before a design needs them. By the reviewer's own one-sided Fisher tests (not in the journal), phase 3 stays clear (11/12 vs 1/12), phase 4 is a plain failure (5/12 vs 3/12) and phase 7 is modest (6/7 vs 2/12) | **Done for the past tests (E-76):** phase 3 p = 5.4 × 10⁻⁵, phase 7 p = 0.006. The reviewer's phase-4 figure was mislabelled: 5/12 vs 3/12 is "at least 4 of 6 soups"; with "any soup" it is 6/12 vs 5/12, p = 0.50. Rule as the unit for future tests: D-063, accepted (16 November 2026). **Correction done (E-79, J-092):** with rule-level p values where committed, phase 3 survives a Holm correction across the 42 primaries (0.002) and phase 7 does not (0.029 with its registered ≥ 4-of-6 definition; 0.70 adjusted). **Reporting done (J-090):** the [Paper]({{ '/paper.html' | relative_url }}) gives rule-level counts before soup- or world-level ones for every "which rules" claim (Lenia E-14/E-19, BFF E-60 to E-74, SUBLEQ phases 3 to 7) |
| **4.** Drop the "no random-program replicator" screen: a rule where random programs already replicate is a rule with a high rate, and the screen cost phase 7 15 of 16 high-rate candidates | open |
| **5.** Add a stopping rule for lines of inquiry: after two revised predictors fail to transfer, write the synthesis and return to the main question | open (the current predictor thread is being closed, as in point 1) |
| **6.** One source of truth: the journal stays the append-only record, the handoff becomes a short current-state page, the report is regrouped by finding; fix the stale index, research, handoff and report pages now | **In progress:** the four pages are refreshed and the handoff now opens with a short state summary above its history. **Partly closed (J-090):** a synthesis grouped by finding now exists as the [Paper]({{ '/paper.html' | relative_url }}), with a claims table that traces every number to an export or journal entry. The report itself is not regrouped, and the paper is one more place where results are written: where it and the journal disagree, the journal's latest entry wins |
| **7.** Clear the merge queue and keep pull requests small (four stacked pull requests; the published site stops at E-65) | open |
| **8.** Close cheap open items or retire them: run H1 at 20 runs per arm (under 3 hours), or stop quoting the 1.9–4.2× figure | **Agreed; done (E-77, J-087, pre-registered):** engine ahead on 20 of 20 paired seeds, 1.84× [1.70, 2.25] distinct self-propelled rules. The old figure reproduces, but its near-duplicate code had never been committed (D-064) |
| **Question:** paper or exploration? | **Owner:** exploration, held to paper-quality rigour |
| **Question:** do program soups count as the "universes" meant by the goal? They have no space and no dashboard | **Reviewer's suggestion, at the owner's request (owner not sure):** count them as a third family. The research page now says plainly that they have no space and are not covered by the engine, discovery engine or dashboard |
| **Question:** may the predictor thread end after one more run? | **Reviewer's suggestion, at the owner's request:** yes, after at most one more run; the owner has not confirmed |

*Note (16 November 2026, J-091):* R-5 made no recommendation about a literature review; the need was recorded on the research page (J-013) and in the paper's limitations (J-090). A review by AI agents is now done: the [Literature]({{ '/literature.html' | relative_url }}) page. It is not exhaustive and has had no expert check. It led to D-066 (labels; Flow-Lenia "not comparable"; single-run origin limited to SUBLEQ) and D-067 (proposed: a Holm correction across the 45 primaries, awaiting the owner). *(16 November 2026, J-092: D-067 accepted and applied in E-79. Holm across the 42 registered primary p values keeps 18 of 20 passes; E-50 and E-71's within-variant test do not survive; with rules as the unit, the Lenia and most F-predictor passes do not. D-063 accepted: phase 8 will not be run as drafted.)*

*Note (17 November 2026, J-093):* where the E-80 groundwork departs from the design intent it was given (the owner approved a lattice-native assay; the orchestrating agent proposed the design), with the evidence:
1. **Primary garden.** The primary garden is soup 901's lattice-aged garden, not soup 5006's mosaic. Only the 901 garden showed a known fitness difference: the 5006 species ahead 24 of 24. In the 5006 garden, E-46's direction was not seen (3 of 24).
2. **Score.** The primary score is the linear area change, not a log score. The log score is dominated by near-extinctions; its positive-to-noise ratio is 0.82, against 1.21.
3. **Well-mixed comparison.** "The same blocks in the old well-mixed assay" becomes the same tagged assay with well-mixed pairing in the same garden, so only the pairing differs (`program_fitness.invasion` scores one program, not a block).
4. **Seven soups.** A primary on the 7 soups cannot survive the E-79 Holm family (best possible p 1/128 → 0.17). It can detect only an effect about the size of a whole fitter species. It is pre-registered as Part A, but the informative test needs more soups (D-068).
5. **Blocks per arm.** More blocks or seeds per arm do not help: block and assay noise are about 1% of a soup's variance.


*Note (18 November 2026, J-104):* a point of disagreement with the E-85 design premise, with the evidence. The premise was a substrate where "the shortest copier is long relative to the shortest lock, so parasites still win by being short, but a lock is a small fraction of a host's length." BFF-XM (D-078) builds exactly that, and controls (1) to (3) pass. But in a length economy with borrowed code, the ratio of host length to parasite length that sets the parasite's edge also sets how fast hosts are destroyed. At 32 against 4 bytes no host population survives: designed hosts, plain or resistant, are extinct within 100 to 200 epochs, and emergent ones never hold the soup. The exploratory sweep has hand hosts persisting only at a minimum body of about 12 bytes or less, where a 5-byte check is again a large share of the host. So "long copier, short lock" does not by itself give a testable arms race here; a design must also stop host debris from becoming parasites. Recorded as a disagreement with the premise; the owner decides the next step (D-079).
