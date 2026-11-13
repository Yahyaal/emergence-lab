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
- **Sunday late morning – afternoon, 8 Nov (J-050 to J-054, eighth session):**
  - **Fitness instruments (D-044, `observatory/program_fitness.py`):** `growth_rate` (early growth from 16 copies among 4096 programs; backgrounds "random" and "halting", where a background program stops at once so theory is exact: r = ln(1 + p/2)); `invasion` (64 copies into a sample of a real soup, paired no-injection control, score = log change of the excess family). Both calibrated on `trapped(k)`, the hand-written replicator that copies with known probability ≈ 2^-k, and `resident_copiers` (a background where the trap fires with a chosen probability). 9 probes (benchmark section 13).
  - **E-51:** growth rate of the 47 E-49 replicators: no trend over time (p = 0.38); soup 5006 rises again (post hoc). Growth rate predicts races only weakly (ρ = 0.196).
  - **E-52/E-53:** invasion into the soups themselves: later code ahead (p = 0.045) **only where it alone had close relatives** in the background; in kin-free backgrounds no advantage (p = 0.88). **Pitfall:** a family-based count favours candidates whose relatives are in the background; use backgrounds from other times (kin at 90% identity is gone within 2,000 rounds).
  - **E-50 (`scripts/bff_sizes.py`):** transition rate ∝ soup size (β = 1.02, p = 0.014; 2^16: 5/10 within 24,000 rounds). 3 one-checkpoint HOE spikes (zero-writing waves, no replicator) were counted by the pre-registered criterion; D-045: require HOE ≥ 1 at 3 consecutive checkpoints plus a detector-confirmed replicator.
- **Next (most promising):** many jumped soups at 2^16 (half jump within 24,000 rounds; ~1.5 h per soup per core), run long after the jump (50,000+ rounds) with snapshots; then test fitness change over long gaps with the kin-free invasion assay (E-53 design), and look for parasites (programs that are copied but do not copy). **E-54 done (J-066):** 4/12 new 2^16 soups jumped; across 7 jumped soups, late (T+18000) vs early (T+2000) verified replicators in kin-free invasion: D = −0.15, p = 0.64 (future background p = 0.95). (E-54 also reported only 22–78% of the 40 most common programs as verified replicators; **corrected by E-66**, see below.) Snapshots in `runs/e54/` (not committed).
  - **E-66 (J-068, `scripts/bff_parasites.py`, `observatory/program_parasites.py`, D-048, D-049):** the replicator test repeated 10× on the 2,800 E-54 programs: **99.8% copy themselves** (single test 50.8%; verdict mix over 28,000 repeats = E-54's single-test mix, so differences between programs were mostly chance; null 0/80). Parasite detector (benchmark section 14): **0 parasites**; the first version called 2 programs parasites that copy themselves but die when running second (now verdict "context self-copier", one is a control). Result cache `runs/e66-partA.jsonl`. **E-67 (J-069, `scripts/bff_parasites_rare.py`):** 420 rarer programs (6–40, 2–5, 1 copies) from final snapshots: 0 parasites; self-copiers 99/96/69%. Parasites do not appear in standard BFF at this scale; next lead is a richer language (instruction set / tape length).
  - **E-55–E-57 (`scripts/bff_kernels.py`, `bff_counterfactual.py`, `bff_mirror.py`; separate interpreter `scripts/bff_kernels.c` with head1's start as a parameter, soup code untouched; with head1 = 0 it equals the soup bit for bit):** backward copying is a property of the rule (both heads start at 0 and wrap). Counterfactual rule (head1 starts at 64): soups evolve forward copiers and jump within 250–1,750 rounds (12 of 12; standard 2^14: 0 of 12 by 16,000). No backward copier replicates alone: the smallest standard replicator is a mirror pair of two kernels (10 instructions vs 5). Counterfactual soups are a cheap way to get many jumped soups (minutes each). E-58 control (head1 = 127: as many short copiers, all backward, none self-sufficient): slow again, 1 of 8 by 16,000 rounds; confirmed by E-59 (2 of 16 vs 8 of 8, p = 6e-5; pooled 3/24 vs 16/16). E-60 (`scripts/bff_headstart.py`): of all 128 head-start rules only h = 62–65 have a self-sufficient copier of ≤ 6 instructions (116 have no short copier at all); those rules 12/12 jumped vs 2/16 in random others. **Fixed pitfall (J-061, D-047):** the E-55 copier classifier only sees copies aligned at byte 64; use `bff_kernels.classify_shift` (copies up to 16 bytes off) for any rule other than 0/64/127. E-61–E-63 (`bff_shift_census.py`, `bff_lineage.py`, `bff_outside.py`): with shifts, F′ = h 61–68; every F′ soup makes exact replicators fast under D-047 (32/32), rules just outside (72, 74, 80, 82) 1/16. Lineage persistence (E-62) did not predict anything. **Jump criterion for rule variants: D-047** (`bff_lineage.job`: ≥ 10 copiers among 40 at T + 1,000; a failed candidate is dropped and the soup runs on). **Pitfall:** the HOE ≥ 1.0 jump threshold is calibrated for the standard rule only; in head1 = 127 soups background HOE sits near 0.9 and crossed it with no copier (D-046: require copiers under the rule's own interpreter; real jumps also raise steps per pair from ~500 to ~7,000).
  - **E-64 (`scripts/bff_twoheads.py`; `bff_kernels.c` `run()` takes code = h + 256·g, g = head0's start):** the F predictor carries over to the two-head-start family: census of 256 random (g, h) rules gives 3 F, 33 C, 220 none (~11 min); soups (D-047) F 10/12 vs C 1/16 (p = 5e-5). The one C jump used shifted **reverse** copiers, which the 5–6-instruction census does not count. E-65 (`scripts/bff_twoheads2.py`, 768 more rules): 7 F rules, **26/28 vs C 1/16** (p = 9e-9), every F rule ≥ 3/4; the count of self-sufficient copiers does not significantly predict speed (ρ = −0.51, p = 0.12). Post hoc: F rules of this family = pointers half a tape apart (h − g = 60–68) with g near 0, 64 or 126. Next: a family that changes the instruction set or tape length.
  - **E-68 (J-070, `scripts/bff_tapelength.py`, D-050; `bff_kernels.set_length(L)` scales L, THR = L − L/16, shift window L/4; L = 64 = old constants, census reproduces E-61 exactly):** programs of L = 16/32/64/128 bytes, pointer 2 at any h1 in 0..2L−1. Census: F rules always sit at h1 ≈ L (14–17, 30–34, 61–68, 125–136). Soups (2^14 programs, copier-only jump criterion D-050, no HOE gate): F 18/36 vs other 6/36 (pre-registered ≥ 75% **failed**): L = 16 0/12 vs 0/12, L = 32 6/12 vs 1/12, L = 128 12/12 vs 5/12; jump time falls with L (ρ = −0.90). Confound: fixed program count, so bytes ∝ L. **E-69 (J-071, `scripts/bff_tapelength_bytes.py`):** same rules at L = 16/32 with matched bytes (2^21): F 4/12 and 10/12, other 0/24 (pre-registered verdict undecided); soup size explains much of the length effect but not all. Next: instruction-set variants (switch in `bff_kernels.c run()`, equivalence at default first).
  - **E-70 (J-072, `scripts/bff_instrset.py`, D-051; `bff_kernels.c run()` code = h1 + 256·g + 65536·v):** five instruction-set variants (v1 `.` then heads +1, v2 `.` then heads −1, v3 `,` then heads +1, v4 loops test head1, v5 `+`/`−` on head1) × 128 h1. v0 reproduces E-61 on all 128 rules. Census: F rules at h1 60–68 in every variant (P1 pass); v1 has 3,893 self-sufficient kernels at h1 = 64 (`[.]` copies whole). Soups: **F 60/60 vs other 15/60** (P2 pass, p = 2e-20; 8 of the 15 are rules one step outside the band); exploratory: more self-sufficient copiers → faster (ρ = −0.80). Soup cache `runs/e70/`. Next: confirm the count/speed link pre-registered; a non-BFF language.
  - **E-71 (J-073, `scripts/bff_copiercount.py`):** 22 fresh F rules from the E-70 census, 8 soups each (checkpoints every 50 rounds). The self-sufficient copier count predicts speed **within** a variant (Σρ = −2.45, p = 0.006, pre-registered pass) but not pooled across variants (ρ = −0.34, p = 0.06, fail): E-70's ρ = −0.80 was mostly a between-variant effect. Total copiers: no information. Self-sufficient *fraction*: ρ = −0.48 pooled (exploratory). 165/176 jumped; **F rule v1/68 made nothing in 8 soups** (18 of 4,317 copiers self-sufficient), so F is not a guarantee at the band's edge. Soup cache `runs/e71/`. Next: a multi-generation F test (does the copy of the copy copy?) to explain v1/68; pre-register the fraction on fresh rules; a non-BFF language. *Correction (J-074): the pooled verdict depends on the jump definition (HOE timing: ρ = −0.57, p = 0.003); within-variant holds under both.*
  - **E-72 (J-074, `scripts/bff_multigen.py`, D-052):** 5-generation lineage test of self-sufficient kernels. It explains v1/67–68 after the fact (no deep kernels) but **failed on 16 fresh rules** (variants with head0 moved: shallow 1,675 vs deep 1,475 rounds, p = 0.58). **Pitfall:** D-050's copy threshold (60/64) misses sloppy copiers. Two v2 rules (g 57/58, h 122) scored 0/6 while HOE reached 6.4: their `>[ . ]` loops copy 59–60/64 bytes. HOE timing in turn misses v3 take-overs. Per D-052, report speed under both definitions. Next: validate a looser copy threshold with controls (sloppy positive, partial-copier negative, null), re-score E-70–E-72, then a non-BFF language.
  - **E-73 (J-075, D-053, `scripts/bff_fidelity.py`, `bff_rescore.py`, `e73_analysis.py`):** validated looser copy test `bff_kernels.classify_fid` (58/64 + 75% instruction-fidelity guard). Its controls run in `pytest` (`test_copy_fidelity_controls`) and in `emergence benchmark --probes`; fixtures are in `scripts/fixtures/e73-*.npy` (regenerate with `bff_fidelity_fixtures.py`). Re-score of all 392 E-70–E-72 soups: no verdict flips; E-72's deep/shallow speed gap reappears (163 vs 1,638 rounds, p 0.06), so it is unresolved. **Pitfall:** the old test (60/64, no guard) accepts 37 of 64 filler smears; use `classify_fid` for new BFF-variant soups and report D-050 beside it (D-052). Re-scored data `runs/e73/` (cache, not committed).
  - **E-74 (J-076, `scripts/bff_deepconfirm.py`):** fresh test of the five-generation predictor (12 deep vs 12 shallow rules, 144 soups, timed by D-053, HOE and D-050). **It fails under every timing** (ratios 0.66–0.95). 143/144 soups jumped. Neither depth nor the one-generation count predicts speed among F rules here. Conclusion: within BFF variants, the F/non-F yes/no result replicates, and no census measure of speed does. The recommended next step is a non-BFF language. `soup_job` there times all three ways in one run; reuse it for new soups.
  - **E-75 phase 0 (J-077, D-054, D-055; design `docs/data/e75-design.md`):** SUBLEQ family in `emergence/programs/subleq.c/.py` (`Rule` packs n, j, s, W, o, absolute; anchors `SUBLEQ`, `RSUBLEQ4`; hand-written replicators `POSITIVES`; deceptive `ZERO_SMEAR`). Replicator test by inheritance in `emergence/programs/inherit.py` (works for any interpreter `run(tape) -> tape`; ~1 ms per program). Controls in `scripts/sq_phase0.py` (pytest + benchmark). **Pitfall:** whole-program copy tests (D-050/D-053/`subleq.classify`) are blind to replicators that rewrite their own body; use inheritance for SUBLEQ, and report whole-program counts beside it. HOE is unreliable in SUBLEQ (copy-all 7.3, seeded take-over ~1).
  - **E-75 phase 1 (J-078, D-056, `scripts/sq_census.py`, protocol `docs/data/e75-phase1-protocol.md`):** census of 600 rules by random programs (`subleq.census_hits`, C pre-filter `sq_census`; hits verified by inheritance). 32 F / 100 C / 468 none; anchors none; F needs n = 4 and s = ±1 (mostly a one-instruction self-jumping loop). Stability 37/40 failed (edge-of-detection rules), so phase 2 must re-census its candidate rules at 10^8 programs before using them (D-056). ~8 s per rule per 10^6 programs per worker incl. verification.
  - **E-75 phase 2 (J-079, `scripts/sq_pilot.py`, protocol `docs/data/e75-phase2-protocol.md`):** pilot soups, cache `runs/e75-pilot/`. F 8/8 jump (median 100 rounds), C 4/8; the non-jumping C soups freeze into halters (first instruction jumps off the tape). Fast take-overs are periodic 4-byte tiles, invisible to the random-program census. n4/always soups cost ~0.5 s per round (8,192 steps per pair); halting soups ~5 ms. **Pitfall:** HOE goes slightly negative in frozen soups.
  - **E-75 phase 3 (J-080, D-057; `scripts/sq_tiles.py`, `scripts/sq_phase3.py`, pre-registration `docs/data/e75-phase3-preregistration.md`):** tile census (`subleq.census_period`, period = n; period = 64 reproduces `census_hits`). Pre-registered test passes: HIGH-D_T copying rules 64/72 soups jump, LOW 6/72, p = 10^-24; non-jumping soups freeze into halters. Cache `runs/e75-phase3/`. Cost: 7.5 h (always-jump soups ~0.5 s per round). Open: the exceptions are partly explained post hoc by phase 4; the exceptions W8/o56 (HIGH, froze) and W64/o75 (LOW, jumped); post-jump evolution of tile replicators.
  - **E-75 phase 4 (J-081, D-058; `scripts/sq_phase4.py`, pre-registration `docs/data/e75-phase4-preregistration.md`):** D_T with phase-3 thresholds under jump ≤ 0 (pool A) and < 0 (pool B). **Primary fails** (A: 29/72 vs 20/72, p = 0.08); B separates 25/36 vs 0/36 but is confounded with s. Post hoc: non-inheriting random-program hits (`hits8` in the JSON `screened` list) anti-correlate with jumping in A and in phase 3 (ρ ≈ −0.8), with condition-specific cuts. Cache `runs/e75-phase4/`. Cost: 6.3 h; frozen soups ~80 s, jumping ones up to ~1 h. **Pitfall:** `soup_job` is reused from `sq_phase3` by resetting `P3.RUN` inside the worker. Open: why the copy-hit count goes with fewer jumps (maybe a proxy for W).
  - **E-75 phase 4b (J-082, D-059; `scripts/sq_inert.py`):** **there is no frozen state.** Random soups in these rules run at 2–7 steps per pair from round 0, keep all programs distinct and copy almost nothing (≤ 0.2%); soups that later jump look the same. The "freeze into halters" and "race" claims of J-079–J-081 are withdrawn, and the clone knockout is dropped. **Pitfall:** the `frozen` flag (≤ 4 steps per pair) in phase 2–4 JSONs means "never left the random start". Next question: what sets the nucleation rate; trace the first replicator in each jumped soup back to its origin.
  - **E-75 phase 5 (J-083, D-060; `scripts/sq_nucleation.py`, `scripts/sq_nucleation_report.py`, pre-registration `docs/data/e75-phase5-preregistration.md`):** exact Python replay of soups (identical to `subleq.Soup`) with lineage tracking. Jump rate is set by **origins**: rarely-jumping rules make none in 4,000 rounds; once one appears, it establishes in ~16 rounds. Founders are written in one run (partner or self), never by mutation alone. **Null replicators:** the all-zero program passes D-055 under jump ≤ 0 or always without carrying information. The tracer classes them by an all-zero inherited block; jump calls checked on 7 soups stand, but T can be early. Cost: ~0.07 s per round under ≤ 0 and ~0.45 s under always before a jump; slow after a zero take-over. Next: a **product census** (how often does a random pair's run *write* a replicator?) as a predictor, pre-registered; it needs a C pre-filter.

The proposed next phase is in [Research → Next steps]({{ '/research.html#next-steps' | relative_url }}) (D-018).

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest                                   # 73 tests, ~4 min
emergence benchmark --probes             # 39 + 92 validation checks, ~8 min on 12 cores
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

- **A stochastic test run once per item measures luck (E-66, D-049):** `replicators.replication_test` from 8 copies loses a typical soup replicator ~1 time in 5. Repeat it (`program_parasites.alone_test`, 10×) before calling a program a non-replicator or comparing programs by verdict.
- **Long multiprocessing runs must save as they go:** E-66's first launch crashed in the last second of part A (negative seed key) and lost 80 min. Cache each result to a JSONL file and resume.
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

0. **Program soups (J-041–J-054):** heredity is shown (E-42); one species out-competes others (E-45/E-46); later code is not reliably fitter over 10,000 rounds by four measures (E-48–E-53); transition rate ∝ soup size (E-50). Next: many 2^16 soups run long after the jump, kin-free invasion over long gaps (level 5 needs this), parasites; ~~backward copying~~ (E-55–E-57). Counterfactual soups jump in minutes and could carry the level-5 questions (state that results are for that rule).
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
