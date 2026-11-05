---
title: Overview
---

# Emergence Lab

<p class="lead">Can complex, persistent, and eventually evolving structure arise on its own from simple, fixed rules? Emergence Lab runs many small artificial universes, measures them with an observatory that never interferes with them, and searches rule space for universes that are genuinely interesting, while trying hard not to fool itself.</p>

This site is the project's **research journal**: what we did, why, what we found, what turned out to be wrong, and what comes next. It is written so that a person or an AI agent can pick up the work with no other context. Start at **[Handoff]({{ '/handoff.html' | relative_url }})** if you are continuing the work.

## Where things stand

<div class="cards">
<div class="card"><div class="stat">v0.3</div><p>Current version: validated discovery plus evidence probes for replication and innovation. <a href="https://github.com/Yahyaal/emergence-lab/pull/1">PR #1</a>.</p></div>
<div class="card"><div class="stat">2 / 5</div><p>Highest <a href="{{ '/research.html#evidence-ladder' | relative_url }}">evidence level</a> reached: self-propelled structures. No replication, heredity or ongoing innovation observed yet.</p></div>
<div class="card"><div class="stat">1.9–4.2×</div><p>How many more distinct interesting rules the discovery engine finds than random search, at equal compute (2 seeds per arm, so preliminary).</p></div>
<div class="card"><div class="stat">53 / 53</div><p>Benchmark checks passing: 39 standard checks plus 14 hard and deceptive controls.</p></div>
</div>

## Hypotheses so far

| Hypothesis | Status | Evidence |
|---|---|---|
| H1. Guided search (Pareto + novelty + niches) finds more interesting rules than random search | <span class="tag supported">supported, preliminary</span> | [E-03–E-06]({{ '/experiments.html' | relative_url }}): 1.9× more distinct rules with self-propelled shapes, 4.2× more rules "complex" on every seed; n = 2 seeds per arm |
| H2. Spontaneous self-replication occurs in Life-like / Generations rules (96×96, ≤ 2000 steps) | <span class="tag notobserved">not observed</span> | 0 of 17 top candidates; the detector does find HighLife's replicator (positive control) |
| H3. Some rules keep producing new kinds of persistent structure (ongoing innovation) | <span class="tag notobserved">not observed</span> / <span class="tag open">2 inconclusive</span> | Innovation ends when universes settle; 2 chaos-like universes are inconclusive (no matched null yet) |
| H4. Initial conditions, not just rules, determine how much complexity appears | <span class="tag open">open, proposed</span> | Not yet tested; see [Research]({{ '/research.html' | relative_url }}) |

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
