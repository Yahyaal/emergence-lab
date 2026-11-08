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
- **E-17/E-18:** a search from smooth starts found a slow, turning "wanderer" (3-ring rule). It was confirmed in 36/40 smooth-start worlds vs 0/40 soups, and lives on a narrow ridge of rule space.
- **E-19:** a shuffled control confirmed that *spatial correlation* is the cause. Soups make gliders only rarely, at their die/freeze transition.
- **E-20:** 500 controlled collisions produced no births, but gliders can fuse into a stable double glider.
- **Review and detector:** an independent review (R-4) led to corrections and new controls. The detector finds about 92% of slow turning movers (J-022).

**Saturday morning, 7 Nov (J-028 to J-031, second session):**
- **C-02:** the quasi-static cut-off (0.002) has no clean gap on 120 held-out rules; about 1 in 6 static-looking soup fields stays rankable (mostly blob edges creeping past the 3-cell margin). No false creatures; an open problem.
- **E-24:** Chan's patch start makes gliders in 13/160 worlds of 256×256 (0/40 at 128×128); 110 patches never do. Smooth ℓ = 3 gives 18% at both sizes.
- **E-25 / D-027:** the mover detector's isolation run now extends to 300 steps for slow objects that keep their mass (`SLOW_STEPS`); +3 wanderer worlds, no new false positives in 3,789 replayed worlds; straightness stays 0.5. ≈ 95% of wanderers detected.
- **E-26:** a third mover, the slow straight "ring glider" (`LENIA/R13/T10/m0.277/s0.0316/b1,0.5,1`, mass ~178, 0.085 cells/step), found by a random rule draw; 31/80 smooth vs 0/80 soup worlds.

**Saturday late morning, 7 Nov (J-032):**
- **Birth detector** (`observatory/births.py`, D-028) for both families, validated on the HighLife replicator and Gray-Scott dividing spots (`physics/gray_scott.py`), with 12 new probe checks.
- **E-27/E-28:** no reproducer in 568 Lenia worlds (0/285 movers). The first detector version was fooled by blobs bursting into world-filling labyrinths; fixed (doubling rule, fixed reference parent) and confirmed on 350 held-out worlds.
- **Next (Track D, research.md):** Flow-Lenia with parameter localization in fed worlds plus a heredity measure; a division objective; multi-channel Lenia.

**Saturday afternoon, 7 Nov (J-033, J-034, fourth session):**
- **Heredity test** (`observatory/heredity.py`, D-029): parents are moved alone into an empty world; heredity = correlation of parent trait with offspring trait, with a parent-permutation null. Controls on `GrayScottTracer` (carried / redrawn / position-set trait); probe section 10.
- **`FlowLeniaPL`** (`physics/flow_lenia.py`): Flow-Lenia whose kernel weights travel with matter (stored as A·h_i), optional food layer, fast scatter-add reintegration. Equals FlowLenia with uniform weights.
- **E-29:** 0 reproducers among 3000 random Lenia rules from a lone lump (1453 rules decided; 410 undecided because objects fill the test world). Route 2 (fission objective) looks unpromising in single-channel Lenia.
- **E-30** (fed FlowLeniaPL, J-035): 17/100 apparent reproducers were **food condensing** (uniform food is an unstable fixed point; only 32/100 rules have stable food at 0.05). New perturbed-vacuum null (D-030); rescored 0. Next fed scans: stable-food rules only, held out.

**Saturday night – Sunday early, 7–8 Nov (J-036, J-037, J-040, J-041; sixth session + an interactive session):**
- **E-31:** held-out fed FlowLeniaPL on stable-food rules: 0 reproducers in 97 worlds; the D-030 null holds. Fed Flow-Lenia route closed for now.
- **`MultiLenia`** (`physics/multi_lenia.py`, D-031). **E-32:** one random 2-channel rule (#970) makes **dividing spots** (level 3, single attractor type, like Gray-Scott; no heredity possible). Its empty channel acts as a decay term (`scripts/e32_inspect.py`).
- **Program soups (BFF)** (`emergence/programs/bff.py`, C interpreter compiled on first use into `~/.cache/emergence-lab`; replicator detector `observatory/replicators.py`, D-040; probes in `benchmark_programs.py`). Run with `scripts/bff_soups.py`.
- **E-40/E-41:** with 16384 programs, the transition is rare: 3 of 16 soups, at epochs 8750, 32000, 43250 (0 in the first 16000 epochs of 12 pre-registered soups). **Every transitioned soup contains verified replicators (several variants); no untransitioned soup does.** Level 3 from random code. Soups are deterministic given the seed (pilot replay exact).
- **E-42 (D-041, `observatory/program_heredity.py`):** one-byte mutations of all 9 emergent replicators are inherited (9/9 "heredity"; 140 of 141 viable mutants carried). **Level 4 (heritable variation) for program replicators.**
- **E-43 (D-042, `observatory/program_selection.py`):** head-to-head contests of the 141 viable one-byte variants vs their parents: 2 parent favoured, 139 no difference (neutral null 0/24, p = 0.73). Selection not shown; the assay only sees large effects.
- **E-44 (D-043, `program_selection.compete_families`, `scripts/bff_contests.py`, `scripts/e44_analysis.py`):** races between replicators from different soups: 0 of 36 pairs with a clear winner (nulls 1/21); the hand-written replicator beats every emergent one (222/287 races). Replicators #5 and #6 of soup 5006 are **exact byte-reverses** of each other: a **mirror replicator** (each writes its reverse into its partner). Count both forms as one species (`a_alt`/`b_alt`).
- **E-45/E-46 (`scripts/bff_mirror_contests.py`, `scripts/bff_species_contests.py`):** **every emergent replicator is a mirror replicator** (makes its reverse in equal numbers), so always count a species with `a_alt`/`b_alt` = its reverse. With fair counting (E-46), the 5006@32k species wins 176/252 races vs soup 901 (p = 1e-10), is ahead of all 7 other emergent species, and beats #4, an earlier common family of soup 5006 (46/64; both only ~1.6% of the soup, E-47). Hand-written advantage only 56%. Nulls: 0/24 favoured in E-46, 2/70 over E-44–E-46.
- **E-47 (`scripts/bff_turnover.py`):** exact replays of soups 901/5006/5010 to 40,000 rounds (snapshots in `runs/e47/`, not committed; regenerate with `--replay`, ~1 h). No 90%-identity family holds more than a few % of the soup after the jump (0 replacements); the most common program drifts from the founder (identity 100% → 2–20%). #4 and #5/#6 were only ~1.6% each.
- **E-48 (`scripts/bff_time_races.py`):** late (T+10000) vs early (T+1000) common programs: later ahead in 62/108 pairs (p = 0.07, not significant); soup 5006 28/36 (p = 6e-4); two late soup-901 programs are common non-copiers (lose every race). Sample only verified replicators next time.
- **E-49 (`scripts/bff_time_races2.py`, confirmation of E-48 with verified replicators, new time points):** later ahead 24/44 programs (p = 0.33): **not confirmed**; mean 51.6% of races; control 50.3%. Most post-jump change looks neutral in races.
- **Next (most promising):** a more sensitive fitness measure (growth rate from a few copies in a fixed background; validate on hand-written replicator variants), then redo the time comparison with more soups; why do all emergent replicators copy backwards? Earlier idea (superseded): track species over time in a running soup with frequent snapshots (replay soup 5006 from E-41 seeds; does each newcomer beat its predecessor? is change cumulative? needs a validated measure); why do all emergent replicators copy backwards; many more null pairs for the contest criterion; rates vs soup size.

The proposed next phase is in [Research → Next steps]({{ '/research.html#next-steps' | relative_url }}) (D-018).

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest                                   # 72 tests, ~2 min
emergence benchmark --probes             # 39 + 83 validation checks, ~5 min on 12 cores
python scripts/verify_movers.py runs/X.db 1 2   # re-isolate every self-propelled structure, 1000 steps alone
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
| `emergence/physics/` | `Physics` interface (`base.py`), Life-like/Generations (`totalistic.py`), Lenia (`lenia.py`), Flow-Lenia (`flow_lenia.py`, mass-conserving, float32 states via `Physics.dtype` and a uint8 `view` for display and frame measures, D-026), controls (`controls.py`: `NoiseControl`, `SmoothNoiseControl`, `JitterControl`), Gray-Scott (`gray_scott.py`, two-channel float32 state (2, h, w), a known reproducer used as a control; only the birth detector and plain runs support it). Add new physics here with `@register`; set `continuous = True` for continuous states |
| `emergence/engine.py` | `UniverseSpec` (everything needed to reproduce a universe) and `Universe` (read-only state, `fork`) |
| `emergence/observatory/` | measures, structure census and self-propulsion test, recurrence, damage spreading, local periodicity, `innovation.py`, `replication.py`, `shapes.py`; `births.py` (birth detector for both families: two generations in isolation, D-028); `continuous.py` (tolerant census, free activity, emergent glider); continuous label rules in `observer.classify` |
| `emergence/lab.py` | the only place engine and observer meet (`study`, `study_universe`) |
| `emergence/discovery.py` | objectives, calibration, niches, `Explorer`, follow-ups, verdicts (`innovation_verdict`, evidence levels), `reproduce` |
| `emergence/analysis.py` | `compare` for baselines |
| `emergence/benchmark.py`, `benchmark_probes.py` | validation suite |
| `emergence/server.py`, `web/` | dashboard |
| `docs/` | this journal (GitHub Pages, Jekyll). `_data/media.json` lists the clips; `data/experiments/` holds the exports |
| `scripts/` | `journal_export.py`, `make_media.py`, `make_figures.py`, `make_report_figures.py`, `lenia_static_fields.py` (C-01/C-02 diagnostics behind D-022), `heldout_free_activity.py` (C-02), `verify_movers.py`, `detector_calibration.py` (E-25), `birth_scan.py` (E-27), `lump_scan.py` (E-29), `pl_scan.py` (E-30), experiment scripts |

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
- **An exactly uniform vacuum can be an unstable fixed point** (fed Flow-Lenia, J-035): nulls must use a slightly perturbed vacuum.
- **Labels tuned for 2-state rules inflate continuous physics.** Every blob of a settled Lenia soup is a "persistent object", and its edges creep for thousands of steps; that is real dynamics (float64 does the same), not rounding. A detector or objective must be re-validated with the new family's own controls (J-012).
- **Continuous censuses count instances, not types:** `vocabulary` = 20 can be 20 copies of one static blob.
- **Measuring a glider's speed across more than half the torus wraps:** the Orbium glider runs at ~0.53 cells/step, but its 200-step displacement on a 128 torus reads ~0.11. Sum short legs.
- **Empty space next to an Orbium-parameter soup does not stay empty:** the blob field grows into it, so a glider placed beside a soup is swallowed.
- **Uncommitted cloud work is lost when the container goes away** (E-12 run 1, the `smooth` condition, gallery clips). Commit or export before ending a cloud session.

## Open problems, in priority order

0. **Program soups (J-041–J-045):** heredity is shown (E-42) and one species out-competes others (E-45); next is change over time in a running soup (level 5 needs a validated measure of cumulative change); transition rate vs soup size (2^14 vs 2^15–2^17); what follows the transition.
1. Lenia beyond level 2 (see the report's "What next"). Next steps:
   - a replication probe for continuous physics (the exact-shape probes do not apply);
   - do fused double gliders (E-20) arise spontaneously in big smooth-start worlds?
   - map the ring glider's rule neighbourhood (E-26) and try patch starts in the wanderer and ring-glider rules;
   - the quasi-static margin (C-02): blob edges creep past the 3-cell margin in some rules;
   - glider rates vs world size and run length, measured with the validated detector at checkpoints;
   - separate world size from run length for patch starts (E-24 changed both).

   Known gap: creatures that rotate or pulse in place are not counted as `complex` yet.
2. Flow-Lenia needs a positive control before any experiment (J-016, J-018). Try multi-channel Flow-Lenia, or check our implementation against the paper's figures.
3. A density sweep for rules whose behaviour changed with density (E-09, E-10).
4. Statistical power for H1 (10–30 runs per arm).
5. Sampling validation of the innovation probe, and a same-rule null (Track A).
6. Replication: more nulls, copy-origin tracing, multi-part candidates.

## Owner preferences

The owner wants scientific validity over impressive-looking results, honest negative findings, pushback when a suggestion is wrong, laptop-friendly code, and this journal kept current. They have external AI reviewers (ChatGPT) read the work, so keep summaries shareable: findings, what was done, and points of disagreement with reasons.
