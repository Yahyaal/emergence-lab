---
title: Overview
---

# Emergence Lab

<p class="lead">Can complex, persistent, and eventually evolving structure arise on its own from simple, fixed rules? Emergence Lab runs many small artificial universes, measures them with an observatory that never interferes with them, and searches rule space for universes that are genuinely interesting, while trying hard not to fool itself.</p>

## Goal

**Find out whether complex structures and behaviours can emerge spontaneously from simple mathematical rules, and which rules make that most likely.** The aim is *not* to simulate our universe or to build artificial life by design. It is to explore many simple rule sets, let each universe run under its own fixed rules, and discover which ones naturally produce interesting, persistent, and possibly evolving complexity, without mistaking randomness or repetition for organisation. Full objectives, requirements and principles: [Research → Goal and objectives]({{ '/research.html#goal-and-objectives' | relative_url }}).

This site is the project's **research journal**: what we did, why, what we found, what turned out to be wrong, and what comes next. It is written so that a person or an AI agent can pick up the work with no other context. Start at **[Handoff]({{ '/handoff.html' | relative_url }})** if you are continuing the work.

<p><b>New (16 November):</b> <a href="{{ '/paper.html' | relative_url }}">a paper-style synthesis</a> of the work to date, written for a reader who has not seen the project. It adds no new results. A <a href="{{ '/literature.html' | relative_url }}">literature review</a> by AI agents (not exhaustive, no expert check) followed: two of our results were already published and most others are partly known.</p>

<p><b>Earlier:</b> <a href="{{ '/report.html' | relative_url }}">the report</a> now covers 6 to 14 November. Its latest section (34) is a prospective test in the SUBLEQ soups: versions chosen by how often random pairs write a replicator made replicators in 33 of 42 soups, against 12 of 72, but the pre-registered test came out undecided (7 high-rate versions, not 8). A <a href="{{ '/reviews.html#r-5' | relative_url }}">goal and approach review (R-5)</a> led to the next steps on the <a href="{{ '/handoff.html' | relative_url }}">Handoff</a> page.</p>

## Where things stand

<div class="cards">
<div class="card"><div class="stat">4 substrates</div><p>Life-like cellular automata, the Lenia family (Lenia, Flow-Lenia, multi-channel Lenia), and two kinds of <b>program soup</b>: BFF and a SUBLEQ family. The soups have no space and run in scripts, outside the engine, discovery engine and dashboard.</p></div>
<div class="card"><div class="stat">4 / 5</div><p>Highest <a href="{{ '/research.html#evidence-ladder' | relative_url }}">evidence level</a> reached: <b>heritable variation</b> in BFF replicators that arose from random code (one-byte mutations inherited in 9 of 9, E-42). <b>Level 3</b> (self-replication) in one multi-channel Lenia rule (dividing spots of a single type, E-32) and in both soup languages (E-40, E-41; E-75). <b>Level 5 not shown:</b> later code is not fitter by four measures (E-48 to E-54), also when programs meet only their neighbours on a grid (E-78), and when fitness itself is measured on a grid (E-80: no advantage above 0.02 in relative area in 16 soups of a head-start variant). When programs can change length (E-81, a variable-length variant), later copiers do beat earlier ones, by getting shorter, in 40 of 40 soups; then every soup stops at the same 6-byte copier and fitness stops rising. That is directional selection favoured by the variant's construction, not open-ended evolution.</p></div>
<div class="card"><div class="stat">1.8×</div><p>How many more distinct rules with self-propelled structures the discovery engine finds than random search at equal compute, after removing near-duplicates; 3.4× for rules "complex" on every seed. Engine ahead on <b>20 of 20</b> paired seeds (E-77, pre-registered). Life-like rules only.</p></div>
<div class="card"><div class="stat">170 / 170</div><p>Benchmark checks passing, as last reported: 39 standard checks plus 131 hard and deceptive controls (probes, knockouts, Lenia, Flow-Lenia, births, heredity, program soups).</p></div>
</div>

## Hypotheses so far

| Hypothesis | Status | Evidence |
|---|---|---|
| H1. Guided search (Pareto + novelty + niches) finds more interesting rules than random search | <span class="tag supported">supported</span> | [E-77]({{ '/experiments.html' | relative_url }}): 20 paired seeds, pre-registered. 1.84× more distinct rules with self-propelled shapes (95% interval 1.70–2.25), 3.4× more rules "complex" on every seed; engine ahead on 20 of 20 seeds. The earlier 1.9× and 4.2× (E-03–E-06, 2 seeds) reproduce exactly. Life-like rules only |
| H2. Spontaneous self-replication occurs in Life-like / Generations rules (96×96, ≤ 2000 steps) | <span class="tag notobserved">not observed</span> | 0 of 17 top candidates; the detector does find HighLife's replicator (positive control). Self-replication does arise elsewhere: one multi-channel Lenia rule (E-32) and program soups (E-40, E-41, E-75) |
| H3. Some rules keep producing new kinds of persistent structure (ongoing innovation) | <span class="tag notobserved">not observed</span> / <span class="tag open">2 inconclusive</span> | Innovation ends when universes settle; 2 chaos-like universes are inconclusive (no matched null yet). In BFF soups code keeps drifting after the jump, but later code is not fitter (E-47 to E-54). In a variable-length variant later code is fitter while it shortens, then stops at the 6-byte floor (E-81, J-098) |
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

- **[Story]({{ '/story.html' | relative_url }})**: the whole project for non-technical readers, with animations and a live simulation: why, the idea, the three results, how they compare with other research, and what could come next.
- **[Paper]({{ '/paper.html' | relative_url }})**: a paper-style synthesis of the three main findings (Lenia movers, program-soup replicators, no open-ended evolution yet), with a claims table that traces every number to its source.
- **[Literature]({{ '/literature.html' | relative_url }})**: how each claim compares with published work (published, partly known, not found in this search, tension), from a review by AI agents with no expert check.
- **[Journal]({{ '/journal.html' | relative_url }})**: chronological entries, newest first.
- **[Decisions]({{ '/decisions.html' | relative_url }})**: why the system is the way it is, with the alternatives we rejected.
- **[Experiments]({{ '/experiments.html' | relative_url }})**: every experiment, with its exact command, code commit, results and raw data.
- **[Research]({{ '/research.html' | relative_url }})**: the question, hypotheses, evidence ladder, related work, and the path to a publishable result.
- **[Reviews]({{ '/reviews.html' | relative_url }})**: external reviews of the work and how each point was handled.
- **[Handoff]({{ '/handoff.html' | relative_url }})**: everything a new contributor needs to continue.
