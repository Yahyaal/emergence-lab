---
title: Overview
---

# Emergence Lab

<p class="lead">Can complex, persistent, and eventually evolving structure arise on its own from simple, fixed rules? Emergence Lab runs many small artificial universes, measures them with an observatory that never interferes with them, and searches rule space for universes that are genuinely interesting, while trying hard not to fool itself.</p>

## Goal

**Find out whether complex structures and behaviours can emerge spontaneously from simple mathematical rules, and which rules make that most likely.** The aim is *not* to simulate our universe or to build artificial life by design. It is to explore many simple rule sets, let each universe run under its own fixed rules, and discover which ones naturally produce interesting, persistent, and possibly evolving complexity, without mistaking randomness or repetition for organisation. Full objectives, requirements and principles: [Research → Goal and objectives]({{ '/research.html#goal-and-objectives' | relative_url }}).

This site is the project's **research journal**: what we did, why, what we found, what turned out to be wrong, and what comes next. It is written so that a person or an AI agent can pick up the work with no other context. Start at **[Handoff]({{ '/handoff.html' | relative_url }})** if you are continuing the work.

<p><b>New: <a href="{{ '/report.html' | relative_url }}">overnight report of 7 November 2026</a></b>. Lenia gliders arise on their own, but only from smooth random starts (pre-registered, confirmed).</p>

## Where things stand

<div class="cards">
<div class="card"><div class="stat">v0.6</div><p>Current version: two physics families (Life-like rules and Lenia), validated discovery and probes, initial conditions, causal knockouts, and the Lenia start-condition experiments (E-12 to E-14).</p></div>
<div class="card"><div class="stat">2 / 5</div><p>Highest <a href="{{ '/research.html#evidence-ladder' | relative_url }}">evidence level</a> reached: self-propelled structures, in Lenia arising spontaneously from smooth random starts (E-14). No replication, heredity or ongoing innovation observed yet.</p></div>
<div class="card"><div class="stat">1.9–4.2×</div><p>How many more distinct interesting rules the discovery engine finds than random search, at equal compute (2 seeds per arm, so preliminary).</p></div>
<div class="card"><div class="stat">77 / 77</div><p>Benchmark checks passing: 39 standard checks plus 38 hard and deceptive controls (probes, knockouts, Lenia, Flow-Lenia).</p></div>
</div>

## Hypotheses so far

| Hypothesis | Status | Evidence |
|---|---|---|
| H1. Guided search (Pareto + novelty + niches) finds more interesting rules than random search | <span class="tag supported">supported, preliminary</span> | [E-03–E-06]({{ '/experiments.html' | relative_url }}): 1.9× more distinct rules with self-propelled shapes, 4.2× more rules "complex" on every seed; n = 2 seeds per arm |
| H2. Spontaneous self-replication occurs in Life-like / Generations rules (96×96, ≤ 2000 steps) | <span class="tag notobserved">not observed</span> | 0 of 17 top candidates; the detector does find HighLife's replicator (positive control) |
| H3. Some rules keep producing new kinds of persistent structure (ongoing innovation) | <span class="tag notobserved">not observed</span> / <span class="tag open">2 inconclusive</span> | Innovation ends when universes settle; 2 chaos-like universes are inconclusive (no matched null yet) |
| H4. Initial conditions, not just rules, determine how much complexity appears | <span class="tag notobserved">not supported as tested</span> | [E-09, E-10]({{ '/experiments.html' | relative_url }}): an apparent patch effect vanished at matched density; the amount of matter matters, its arrangement didn't |
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
