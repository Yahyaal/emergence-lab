---
title: Overview
---

# Emergence Lab

<p class="lead">Can complex, persistent, and eventually evolving structure arise on its own from simple, fixed rules? Emergence Lab runs many small artificial universes, measures them with an observatory that never interferes with them, and searches rule space for universes that are genuinely interesting, while trying hard not to fool itself.</p>

## Goal

**Find out whether complex structures and behaviours can emerge spontaneously from simple mathematical rules, and which rules make that most likely.** The aim is *not* to simulate our universe or to build artificial life by design. It is to explore many simple rule sets, let each universe run under its own fixed rules, and discover which ones naturally produce interesting, persistent, and possibly evolving complexity, without mistaking randomness or repetition for organisation. Full objectives, requirements and principles: [Research → Goal and objectives]({{ '/research.html#goal-and-objectives' | relative_url }}).

This site is the project's **research journal**: what we did, why, what we found, what turned out to be wrong, and what comes next. It is written so that a person or an AI agent can pick up the work with no other context. Start at **[Handoff]({{ '/handoff.html' | relative_url }})** if you are continuing the work.

<p><b>New:</b> <a href="{{ '/report.html' | relative_url }}">the report</a> now covers 6 to 14 November. Its latest section (34) is a prospective test in the SUBLEQ soups: versions chosen by how often random pairs write a replicator made replicators in 33 of 42 soups, against 12 of 72, but the pre-registered test came out undecided (7 high-rate versions, not 8). A <a href="{{ '/reviews.html#r-5' | relative_url }}">goal and approach review (R-5)</a> led to the next steps on the <a href="{{ '/handoff.html' | relative_url }}">Handoff</a> page.</p>

## Where things stand

<div class="cards">
<div class="card"><div class="stat">4 substrates</div><p>Life-like cellular automata, the Lenia family (Lenia, Flow-Lenia, multi-channel Lenia), and two kinds of <b>program soup</b>: BFF and a SUBLEQ family. The soups have no space and run in scripts, outside the engine, discovery engine and dashboard.</p></div>
<div class="card"><div class="stat">4 / 5</div><p>Highest <a href="{{ '/research.html#evidence-ladder' | relative_url }}">evidence level</a> reached: <b>heritable variation</b> in BFF replicators that arose from random code (one-byte mutations inherited in 9 of 9, E-42). <b>Level 3</b> (self-replication) in one multi-channel Lenia rule (dividing spots of a single type, E-32) and in both soup languages (E-40, E-41; E-75). <b>Level 5 not shown:</b> later code is not fitter by four measures (E-48 to E-54).</p></div>
<div class="card"><div class="stat">1.9–4.2×</div><p>How many more distinct interesting rules the discovery engine finds than random search, at equal compute. <b>Preliminary:</b> 2 seeds per arm; a re-run at 20 runs per arm is in progress.</p></div>
<div class="card"><div class="stat">170 / 170</div><p>Benchmark checks passing, as last reported: 39 standard checks plus 131 hard and deceptive controls (probes, knockouts, Lenia, Flow-Lenia, births, heredity, program soups).</p></div>
</div>

## Hypotheses so far

| Hypothesis | Status | Evidence |
|---|---|---|
| H1. Guided search (Pareto + novelty + niches) finds more interesting rules than random search | <span class="tag supported">supported, preliminary</span> | [E-03–E-06]({{ '/experiments.html' | relative_url }}): 1.9× more distinct rules with self-propelled shapes, 4.2× more rules "complex" on every seed; n = 2 seeds per arm; re-run at 20 per arm in progress |
| H2. Spontaneous self-replication occurs in Life-like / Generations rules (96×96, ≤ 2000 steps) | <span class="tag notobserved">not observed</span> | 0 of 17 top candidates; the detector does find HighLife's replicator (positive control). Self-replication does arise elsewhere: one multi-channel Lenia rule (E-32) and program soups (E-40, E-41, E-75) |
| H3. Some rules keep producing new kinds of persistent structure (ongoing innovation) | <span class="tag notobserved">not observed</span> / <span class="tag open">2 inconclusive</span> | Innovation ends when universes settle; 2 chaos-like universes are inconclusive (no matched null yet). In BFF soups code keeps drifting after the jump, but later code is not fitter (E-47 to E-54) |
| H4. Initial conditions, not just rules, determine how much complexity appears | <span class="tag supported">supported in Lenia</span> / <span class="tag notobserved">not in Life-like rules</span> | Lenia: smooth random starts made gliders in 49 of 320 worlds, soups with the same mass in 0 of 320 (E-14, pre-registered); shuffling the same values removes them (E-19). Life-like: an apparent patch effect vanished at matched density (E-09, E-10) |
| H5. A richer physics family reaches higher evidence levels under the same search budget | <span class="tag open">not tested as stated</span> | Higher levels were reached in other families (Lenia level 3, BFF level 4), but no comparison at equal search budget was run |
| H6. Earlier innovations enable later ones | <span class="tag notobserved">not observed</span> | Knockouts are indistinguishable from placebo deletions (P = 0.49–0.51, 92 tests) |

## A taste

<div class="cards">
<div class="card"><img src="{{ '/assets/media/spiral-waves-poster.png' | relative_url }}" alt="Spiral waves"><p><b>Spiral waves</b> self-organise from noise in an excitable-medium rule.</p></div>
<div class="card"><img src="{{ '/assets/media/self-propelled-1181-poster.png' | relative_url }}" alt="Self-propelled shapes"><p><b>Evidence level 2</b>: 13 of 13 moving shapes travel on their own in isolated clones.</p></div>
<div class="card"><img src="{{ '/assets/media/highlife-replicator-poster.png' | relative_url }}" alt="HighLife replicator"><p><b>Positive control</b>: HighLife's replicator, which the replication probe must find.</p></div>
</div>

More in the **[Gallery]({{ '/gallery.html' | relative_url }})**.

## How to read this journal

- **[Journal]({{ '/journal.html' | relative_url }})**: chronological entries, newest first.
- **[Decisions]({{ '/decisions.html' | relative_url }})**: why the system is the way it is, with the alternatives we rejected.
- **[Experiments]({{ '/experiments.html' | relative_url }})**: every experiment, with its exact command, code commit, results and raw data.
- **[Research]({{ '/research.html' | relative_url }})**: the question, hypotheses, evidence ladder, related work, and the path to a publishable result.
- **[Reviews]({{ '/reviews.html' | relative_url }})**: external reviews of the work and how each point was handled.
- **[Handoff]({{ '/handoff.html' | relative_url }})**: everything a new contributor needs to continue.
