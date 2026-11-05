---
title: Journal
description: Chronological research log, newest first.
---

# Journal

Newest first. Each entry records what we did, why, what we found, and what we learned.
Experiment IDs (E-xx) link to the [Experiments]({{ '/experiments.html' | relative_url }}) page and decision IDs (D-xxx) to [Decisions]({{ '/decisions.html' | relative_url }}).

**How to add an entry** (people and agents): copy the template at the bottom, put it at the top, and fill in the commit hashes and experiment IDs. Keep claims at the evidence level actually reached.

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
