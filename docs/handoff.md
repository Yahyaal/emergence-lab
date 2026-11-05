---
title: Handoff
description: Everything a new contributor or AI agent needs to continue the work without prior context.
---

# Handoff

Read this page first if you are picking up the project, then the latest [Journal]({{ '/journal.html' | relative_url }}) entries.

## Goal

Find out whether complex, persistent and possibly evolving structure emerges spontaneously from simple fixed rules, and which rules or initial conditions make it likely. We don't simulate our universe and we don't build life by design. Full goal, objectives (O1–O7), the owner's original requirements and principles: [Research → Goal and objectives]({{ '/research.html#goal-and-objectives' | relative_url }}).

## State in one paragraph

Emergence Lab (v0.4, Python) runs many 2D cellular-automaton universes (Life-like B/S and Generations B/S/C rules on a torus). A passive observatory measures them, and a discovery engine searches rule space: Pareto ranking, novelty search, MAP-Elites niches and seed screening. Promising rules get follow-ups: new seeds, a larger world, a 4× longer run, an innovation-over-time probe, and a replication probe on isolated clones. Each discovery gets an evidence level (1–5). v0.4 added initial-condition generators (`UniverseSpec.init`), a paired conditions study (`emergence conditions`) and a causal knockout probe calibrated with placebo deletions. So far:
- the engine beats random search (preliminary);
- the best evidence reached is level 2 (self-propelled structures);
- no replication or cumulative innovation has been observed: knockouts ≈ placebo;
- starting from a patch only mattered through the amount of matter.

The proposed next phase is in [Research → Next steps]({{ '/research.html#next-steps' | relative_url }}) (D-018).

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest                                   # ~40 tests, ~30 s
emergence benchmark --probes             # 39 + 14 validation checks, ~3 min
emergence explore --generations 6        # ~4 min on 4 cores -> lab.db
emergence serve                          # dashboard at http://127.0.0.1:8000
emergence discoveries 1                  # findings with evidence
emergence compare 1 2                    # e.g. engine vs --baseline-random
```

## Where things are

| Path | What |
|---|---|
| `emergence/physics/` | `Physics` interface (`base.py`), Life-like/Generations (`totalistic.py`), `NoiseControl` (`controls.py`). Add new physics here with `@register` |
| `emergence/engine.py` | `UniverseSpec` (everything needed to reproduce a universe) and `Universe` (read-only state, `fork`) |
| `emergence/observatory/` | measures, structure census and self-propulsion test, recurrence, damage spreading, local periodicity, `innovation.py`, `replication.py`, `shapes.py` |
| `emergence/lab.py` | the only place engine and observer meet (`study`, `study_universe`) |
| `emergence/discovery.py` | objectives, calibration, niches, `Explorer`, follow-ups, verdicts (`innovation_verdict`, evidence levels), `reproduce` |
| `emergence/analysis.py` | `compare` for baselines |
| `emergence/benchmark.py`, `benchmark_probes.py` | validation suite |
| `emergence/server.py`, `web/` | dashboard |
| `docs/` | this journal (GitHub Pages, Jekyll). `_data/media.json` lists the clips; `data/experiments/` holds the exports |
| `scripts/` | `journal_export.py`, `make_media.py`, `make_figures.py` |

## Conventions

- **Branches and PRs:** never commit to `main`; use a branch and a PR. Commit author is `yahyaal`. Commit messages end with the attribution lines your environment requires.
- **GitHub from cloud agent sessions:** `gh` GraphQL (`gh pr create`) is blocked. Use REST: `gh api -X POST repos/Yahyaal/emergence-lab/pulls --input body.json`. The Pages settings API is also blocked, so the owner enables Pages manually.
- **Long experiments:** run them in the background (`nohup ... &`) and append a sentinel line to the log. Cloud containers can restart and kill background jobs, so check `uptime` and the log. Don't edit `emergence/*.py` while an experiment is *starting* (each `emergence` process imports the code at launch); editing after its workers have forked is safe.
- **Determinism:** the same command + commit + seed gives the same universes. Never introduce unseeded randomness. Observer and probe randomness use separate streams derived from the seed.
- **Every new detector needs:** a known positive, a negative, a *deceptive* control built to fool it, and a null that accounts for how its candidates are selected. Add them to `benchmark_probes.py`.
- **Claims:** keep them at the evidence level actually reached. Report counts after removing near-duplicates when the search breeds from its winners. Never assign evidence levels 4–5 without a validated measurement.
- **Journal:** after each meaningful change or experiment, add a journal entry (template at the bottom of the Journal page), a decision row if you chose between alternatives, and an experiment row with an exported JSON.

## Pitfalls already hit (don't repeat them)

- Power-of-two torus sizes annihilate linear rules (Fredkin B1357/S1357), so test worlds use side 160.
- Life soups at 64×64 look "complex" at 500 steps and cycle later: always confirm with the extended run.
- Scanning the *most common* shapes for replication selects shapes any explosion produces. Hence the "common product" null.
- Sparse sampling of a long exact cycle looks like innovation. Innovation can't be counted after a cycle begins.
- i.i.d. noise is not a matched null for correlated chaos.
- Niche axes must be checked against the data: the first set put 90% of rules into one niche.
- Environment comparisons need matched density: a "patch" effect was really just less matter (E-10).
- In sensitive universes compare interventions with *placebo* interventions: a fixed threshold produced 5 false "dependencies" (J-010).
- The 64-step damage measure underestimates sensitivity over 1000-step horizons.

## Open problems, in priority order

1. Lenia physics with its own structure detector, run through the same probes (Track C); now the most promising lever.
2. A density sweep for rules whose behaviour changed with density (E-09, E-10).
3. Statistical power for H1 (10–30 runs per arm).
4. Sampling validation of the innovation probe, and a same-rule null (Track A).
5. Replication: more nulls, copy-origin tracing, multi-part candidates.

## Owner preferences

The owner wants scientific validity over impressive-looking results, honest negative findings, pushback when a suggestion is wrong, laptop-friendly code, and this journal kept current. They have external AI reviewers (ChatGPT) read the work, so keep summaries shareable: findings, what was done, and points of disagreement with reasons.
