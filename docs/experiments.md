---
title: Experiments
description: Registry of every experiment, with exact commands, code commits, results and raw data.
---

# Experiments

Every result in this journal can be reproduced: check out the listed commit, run the command, and the same seeds give the same universes.
The SQLite databases aren't committed; the compact JSON exports below hold the config, environment, per-generation curves and every discovery with its evidence.

## Engine vs random search (E-03 to E-06)

<div class="legend"><span><i style="border-color:var(--s1)"></i>discovery engine</span><span><i style="border-color:var(--s2)"></i>random search</span><span><i style="border-color:var(--muted);border-top-style:dashed"></i>dashed = seed 12, solid = seed 11</span></div>
<figure>
{% include fig-baseline.svg %}
<figcaption>Cumulative number of rules found, by generation, at equal compute (100 rules × 2 seeds per generation, 96×96, 500 steps). Generation 0 is identical in both arms (same random start), so the gap opens only once selection starts. Raw counts include near-duplicate mutants: after counting only rules at least 2 mutations apart, the engine's advantage is 1.9× (self-propelled) and 4.2× (complex on every seed). Hover a point for its value.</figcaption>
</figure>

<details><summary>Table view</summary>

| Run | Selection | Seed | Rules | Niches | Self-propelled (raw / distinct) | Complex on all seeds (raw / distinct) |
|---|---|---|---|---|---|---|
| E-03 | engine | 11 | 600 | 34 | 81 / 50 | 53 / 34 |
| E-04 | random | 11 | 600 | 27 | 29 / 27 | 8 / 8 |
| E-05 | engine | 12 | 600 | 32 | 99 / 55 | 60 / 33 |
| E-06 | random | 12 | 600 | 23 | 29 / 29 | 8 / 8 |

</details>

## Registry

| ID | What | Commit | Command | Key results | Data |
|---|---|---|---|---|---|
| E-01 | v0.1 evaluation | `4a07778` | `emergence explore --name eval --generations 10 --steps 800 --seed 2026 --followups 10 --size 64` (1 seed per rule) | 1000 universes in 2 min 10 s. Spiral waves (#824) and glider-trail (#767) rules found. Multi-state share grew 28% → 73%; 87% of the top 30. Strobing rules ranked top until local periodicity was added | [json]({{ '/data/experiments/2026-11-05-v01-eval-s2026.json' | relative_url }}) |
| E-02 | v0.2 evaluation | `f394662` | `emergence explore --name eval-v2 --generations 10 --steps 800 --seed 2026 --followups 10` | 2 seeds × 96×96; 8 min 11 s. 33 niches; top-30 multi-state share 77%. 7 of 11 candidates settle in the 4× run (after the "persists" fix). #1029 persists but its defects are not self-propelled | [json]({{ '/data/experiments/2026-11-05-v02-eval-s2026.json' | relative_url }}) |
| E-03–E-06 | Engine vs random baseline | `b77f873` | `emergence explore --name {engine,random}-s{11,12} --generations 6 --steps 500 --seed {11,12} --followups 6 [--baseline-random]` | See the figure above. Calibrated robustness threshold 0.25–0.33 per run | [json]({{ '/data/experiments/2026-11-05-r1-baseline.json' | relative_url }}) |
| E-07 | Probes, seed 11 | `7009020` | `emergence explore --name probes-s11 --generations 6 --steps 500 --seed 11 --followups 8` | 9 candidates: 0 self-replicators. Highest evidence level 2 (#1181, "loops" on the torus). #1169's innovation was sampling aliasing (fixed in R4); #173 is inconclusive | [json]({{ '/data/experiments/2026-11-05-r3-probes-s11.json' | relative_url }}) |
| E-08 | Probes, seed 12 | `328c078` | `emergence explore --name final-s12 --generations 6 --steps 500 --seed 12 --followups 8` | 8 candidates: 0 self-replicators. 2 transient innovations that ended (fixed verdict in R5), 1 inconclusive (#595), the rest none | [json]({{ '/data/experiments/2026-11-05-r4-probes-s12.json' | relative_url }}) |
| E-09 | Initial conditions, density 0.35 | `b47ff1f` | `emergence conditions --rules-file docs/data/rule-panel-e09.txt --seeds 3 --size 96 --steps 2000 --seed 9` | 22 rules × 4 conditions × 3 seeds. Patch: +1.35 self-propelled types (9/0 rules, p = 0.004). Gradient: +0.14 unsettled (p = 0.125). 0 set-based knockout dependencies; 88% of knockouts inconclusive | [json]({{ '/data/experiments/2026-11-05-e09-initial-conditions.json' | relative_url }}) |
| E-10 | Density-matched control | `85c3c2e` | `emergence conditions --rules-file docs/data/rule-panel-e09.txt --inits uniform,patch --density 0.125 --seeds 3 --size 96 --steps 2000 --seed 9` | Patch vs uniform at the same overall density: −0.08 self-propelled types (5/4, p = 1), so E-09's effect was density. Knockouts vs placebo: P(real > placebo) = 0.510. 117 s | [json]({{ '/data/experiments/2026-11-05-e10-density-matched.json' | relative_url }}) |
| E-11 | Rerun of E-09 with count-based knockouts | `85c3c2e` | same command as E-09 | Identical primary outcomes to E-09 (reproducible). 62 knockouts: P(real > placebo) = 0.491; 1 above the placebo 95th percentile (3.1 expected by chance). 228 s | [json]({{ '/data/experiments/2026-11-05-e11-rerun-rate-knockouts.json' | relative_url }}) |
| E-12 run 1 | Lenia discovery (cloud) | `85b289f` (before the fix) | not recorded | **Invalid and lost.** Reported ~44% of rules "complex" and 0 of 500 with a mover; the label was inflated by static blob fields (J-012). Data was never committed and was lost with the cloud container | – |
| C-01 | Lenia static-field diagnostic | this PR (v0.5 fix) | `python scripts/lenia_static_fields.py --out docs/data/experiments/2026-11-06-c01-lenia-static-fields.json` | Static-blob activity is real edge relaxation (float64 and quantized both change 13% of cells by > 32 levels over 3000 steps). 60 random rules: old label 27 complex, all without a self-propelled structure; new label 0 complex, 26 quasi-static, 5 rankable active, 0 with a mover. ~1 min on 12 cores | [json]({{ '/data/experiments/2026-11-06-c01-lenia-static-fields.json' | relative_url }}) |
| B-01 | Benchmark | `32df04e` (v0.3); `1a48270` (v0.4) | `emergence benchmark --seeds 3 --probes` | 39/39 standard + 14/14 hard controls (v0.3); 39/39 + 20/20 with the knockout controls (v0.4); 39/39 + 32/32 with the Lenia controls and the continuous-label fix (v0.5). Noise: 1 candidate mover in 3 runs (rejected by isolation); innovation noise floor 1 | – |

E-01 to E-08 commits are on the `v0.3-evidence` branch; E-09 to E-11 on `v0.4-conditions-knockouts`. The E-09 to E-11 exports hold the study summaries (per-rule outcomes, paired tests, placebo test). The `--seed 9` master seed picks the same per-rule seeds for every condition (paired design). PRs: [#1](https://github.com/Yahyaal/emergence-lab/pull/1) (v0.3), [#2](https://github.com/Yahyaal/emergence-lab/pull/2) (v0.4). The verdicts stored in the E-07 and E-08 exports predate the R4/R5 fixes; the journal reports the corrected verdicts, re-derived from the stored probe data with the current `innovation_verdict()`.

## Adding an experiment

1. Run it and note the exact command and `git rev-parse --short HEAD`.
2. Export it: `python scripts/journal_export.py lab.db <ids> --label "..." --commit <hash> --command "..." --out docs/data/experiments/<date>-<slug>.json`
3. Add a row above, and a journal entry.
4. For a new figure, extend `scripts/make_figures.py`. For a new clip, add it to `docs/_data/media.json` and run `python scripts/make_media.py <id>`.
