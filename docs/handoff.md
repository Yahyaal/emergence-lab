---
title: Handoff
description: Everything a new contributor or AI agent needs to continue the work without prior context.
---

# Handoff

Read this page first if you are picking up the project, then the latest [Journal]({{ '/journal.html' | relative_url }}) entries.

## Goal

Find out whether complex, persistent and possibly evolving structure emerges spontaneously from simple fixed rules, and which rules or initial conditions make it likely. We don't simulate our universe and we don't build life by design. Full goal, objectives (O1–O7), the owner's original requirements and principles: [Research → Goal and objectives]({{ '/research.html#goal-and-objectives' | relative_url }}).

## State in one paragraph

Emergence Lab (v0.5, Python) runs many 2D cellular-automaton universes (Life-like B/S and Generations B/S/C rules on a torus). A passive observatory measures them, and a discovery engine searches rule space: Pareto ranking, novelty search, MAP-Elites niches and seed screening. Promising rules get follow-ups: new seeds, a larger world, a 4× longer run, an innovation-over-time probe, and a replication probe on isolated clones. Each discovery gets an evidence level (1–5). v0.4 added initial-condition generators (`UniverseSpec.init`), a paired conditions study (`emergence conditions`) and a causal knockout probe calibrated with placebo deletions. So far:
- the engine beats random search (preliminary);
- the best evidence reached is level 2 (self-propelled structures);
- no replication or cumulative innovation has been observed: knockouts ≈ placebo;
- starting from a patch only mattered through the amount of matter.

v0.5 adds a second physics family, **Lenia** (continuous states quantized to 256 levels, FFT), with a tolerant structure detector (`observatory/continuous.py`) and its own controls (J-011). The first Lenia exploration (E-12 run 1, cloud) was invalid and its data is lost: the class label and objectives, tuned for 2-state rules, called fields of static blobs "complex". v0.5 fixes this for continuous physics only (J-012, D-022):
- `complex` now requires a self-propelled structure;
- static blob fields are *quasi-static* and are not ranked.

**Overnight 6–7 Nov (J-013 to J-018; summary on the [Report]({{ '/report.html' | relative_url }}) page):**
- **E-12:** Lenia discovery from soups found 0 self-propelled structures in 2085 universes.
- **E-13a:** gliders can exist in only 8 of 99 single-ring rules, around Orbium.
- **E-13/E-14:** in those rules, **smooth (correlated) random starts make gliders and soups with the same mass never do** (pre-registered and confirmed: 49/320 vs 0/320, p < 1e-6).
- **E-15:** in big worlds a growing blob field usually wins, and gliders interact only destructively (no births).
- **v0.7 adds Flow-Lenia** with float32 states (J-016). It still has no positive control: 0 movers in 400 universes (E-16).
- **E-17**, a discovery search from smooth starts, ran last.

The proposed next phase is in [Research → Next steps]({{ '/research.html#next-steps' | relative_url }}) (D-018).

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest                                   # 57 tests, ~1-3 min
emergence benchmark --probes             # 39 + 37 validation checks, ~2 min on 12 cores
emergence explore --generations 6        # ~4 min on 4 cores -> lab.db
emergence serve                          # dashboard at http://127.0.0.1:8000
emergence discoveries 1                  # findings with evidence
emergence compare 1 2                    # e.g. engine vs --baseline-random
emergence observe "LENIA/R13/T10/m0.150/s0.0150/b1" --size 128 --steps 1000   # one Lenia universe
emergence explore --physics lenia ...    # search Lenia rule space
emergence conditions --rules "LENIA/..." --inits uniform,smooth:3,smooth:6,smooth:10
```

## Where things are

| Path | What |
|---|---|
| `emergence/physics/` | `Physics` interface (`base.py`), Life-like/Generations (`totalistic.py`), Lenia (`lenia.py`), Flow-Lenia (`flow_lenia.py`, mass-conserving, float32 states via `Physics.dtype` and a uint8 `view` for display and frame measures, D-026), controls (`controls.py`: `NoiseControl`, `SmoothNoiseControl`, `JitterControl`). Add new physics here with `@register`; set `continuous = True` for continuous states |
| `emergence/engine.py` | `UniverseSpec` (everything needed to reproduce a universe) and `Universe` (read-only state, `fork`) |
| `emergence/observatory/` | measures, structure census and self-propulsion test, recurrence, damage spreading, local periodicity, `innovation.py`, `replication.py`, `shapes.py`; `continuous.py` (tolerant census, free activity, emergent glider); continuous label rules in `observer.classify` |
| `emergence/lab.py` | the only place engine and observer meet (`study`, `study_universe`) |
| `emergence/discovery.py` | objectives, calibration, niches, `Explorer`, follow-ups, verdicts (`innovation_verdict`, evidence levels), `reproduce` |
| `emergence/analysis.py` | `compare` for baselines |
| `emergence/benchmark.py`, `benchmark_probes.py` | validation suite |
| `emergence/server.py`, `web/` | dashboard |
| `docs/` | this journal (GitHub Pages, Jekyll). `_data/media.json` lists the clips; `data/experiments/` holds the exports |
| `scripts/` | `journal_export.py`, `make_media.py`, `make_figures.py`, `lenia_static_fields.py` (C-01 diagnostic behind D-022) |

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
- **Labels tuned for 2-state rules inflate continuous physics.** Every blob of a settled Lenia soup is a "persistent object", and its edges creep for thousands of steps; that is real dynamics (float64 does the same), not rounding. A detector or objective must be re-validated with the new family's own controls (J-012).
- **Continuous censuses count instances, not types:** `vocabulary` = 20 can be 20 copies of one static blob.
- **Measuring a glider's speed across more than half the torus wraps:** the Orbium glider runs at ~0.53 cells/step, but its 200-step displacement on a 128 torus reads ~0.11. Sum short legs.
- **Empty space next to an Orbium-parameter soup does not stay empty:** the blob field grows into it, so a glider placed beside a soup is swallowed.
- **Uncommitted cloud work is lost when the container goes away** (E-12 run 1, the `smooth` condition, gallery clips). Commit or export before ending a cloud session.

## Open problems, in priority order

1. Lenia beyond level 2. Next steps:
   - a replication probe for continuous physics (the exact-shape probes do not apply);
   - glider rates vs world size and run length, measured with the validated detector at checkpoints;
   - Chan's patch protocol in larger worlds and longer runs.

   Known gap: creatures that rotate or pulse in place are not counted as `complex` yet.
2. Flow-Lenia needs a positive control before any experiment (J-016, J-018). Try multi-channel Flow-Lenia, or check our implementation against the paper's figures.
3. A density sweep for rules whose behaviour changed with density (E-09, E-10).
4. Statistical power for H1 (10–30 runs per arm).
5. Sampling validation of the innovation probe, and a same-rule null (Track A).
6. Replication: more nulls, copy-origin tracing, multi-part candidates.

## Owner preferences

The owner wants scientific validity over impressive-looking results, honest negative findings, pushback when a suggestion is wrong, laptop-friendly code, and this journal kept current. They have external AI reviewers (ChatGPT) read the work, so keep summaries shareable: findings, what was done, and points of disagreement with reasons.
