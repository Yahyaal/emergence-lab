---
title: Paper
description: A paper-style synthesis of the project's findings, 5 to 15 November 2026, with every number traced to its source.
---

# Structure from fixed rules: spontaneous movers in Lenia, replicators in program soups, and no open-ended evolution yet

<p class="lead">A synthesis of Emergence Lab, 5 to 15 November 2026 (journal entries J-001 to J-089). Written from the committed data, journal, decisions, pre-registrations and reviews; no new experiments or analyses. Every number in the text has a row in <a href="#appendix-a-claims-table">Appendix A</a>. Revised on 16 November 2026 (J-091) after a <a href="{{ '/literature.html' | relative_url }}">literature review</a> done by AI agents; it is not exhaustive and no human expert has checked it. Revised again the same day (J-092) with a pre-registered Holm correction across the primaries (E-79, <a href="#appendix-b2-holm-correction-across-the-primaries-e-79">Appendix B2</a>).</p>

## Abstract

We ran small artificial universes under fixed rules and asked whether persistent, self-propelled, self-copying or evolving structure appears without design, and what makes it likely. Every detector was checked against a positive, a negative, a control built to fool it, and a null matched to how its candidates are selected; confirmatory tests were pre-registered. (A) In Lenia, a continuous cellular automaton, self-propelled structures arise on their own from spatially correlated random starts and almost never from uncorrelated starts of the same mass. A shuffled control shows that spatial arrangement is the cause, in the 8 rules tested. (B) In soups of random programs, self-replicators arise with no fitness function: in BFF, as reported by others, and in a SUBLEQ-like family we defined. In BFF variants, whether a rule's shortest copier makes a copy that also copies predicted which rules make replicators in several pre-registered tests; nothing predicted how fast. In the SUBLEQ family each predictor passed once, then failed to transfer or came out undecided. (C) Mutations in replicators are inherited (evidence level 4), but later code was not fitter by four measures, no parasites appeared, and lattice-only interaction changed neither. Open-ended evolution (level 5) was not shown: no large adaptive effect was detected in 7 soups, and the field's standard open-endedness statistics were not computed. Limits: few rules per test, rule families partly shaped by us, laptop scale, well-mixed fitness instruments, and a literature review done by AI agents that is not exhaustive and has had no expert check; by that review, two of our results were already published and most others are partly known. A Holm correction across the 42 pre-registered primary p values, applied after the fact (E-79), keeps 18 of 20 passes (the soup-size exponent and the within-variant copier count lose significance); with rules as the unit, the Lenia passes and, in an exploratory recomputation, all but one F-predictor pass would not survive it.

## 1. Question and approach

**Goal.** The project asks whether complex structures and behaviours can emerge spontaneously from simple mathematical rules, and which properties of the rules, or of the initial conditions, make that more likely ([Research]({{ '/research.html#goal-and-objectives' | relative_url }})). It is not a simulation of our universe and not an attempt to build life by design. Nothing is planted, steered or rewarded inside a running universe.

**Terms.** A *rule* is one fixed version of a physics or a programming language. A *world* is one run of a rule from one random start. In the program work, a *soup* is a population of random programs that meet in pairs and run on a shared tape; one soup is one run of one rule. (In the Lenia work, "soup" is also the name of one start condition: uniform, uncorrelated random cells. We say "soup start" there.) A *jump* is the moment a program soup is taken over by self-copying programs, confirmed by a replicator detector, not by an entropy curve alone. A test is *pre-registered* when its hypothesis, analysis and pass/fail criteria were committed to the repository before the run; *post hoc* marks anything decided after seeing the data. *HOE* is the high-order entropy of a soup, a compression-based measure of how repetitive it is.

**Evidence ladder.** Each claim carries the highest level its evidence reaches (D-014). Levels 4 and 5 are never assigned without a validated measurement.

| Level | Meaning | How it is measured |
|---|---|---|
| 1 | Persistent organisation | several persistent shape types, reproduced across seeds |
| 2 | Self-propelled structures | a shape travels on its own in an isolated clone |
| 3 | Self-replication | a shape or program makes a growing number of copies of itself alone, and random patterns do not |
| 4 | Heredity and variation | variants also replicate and pass their variation on |
| 5 | Open-ended evolution | innovation that continues and builds on earlier innovation |

**Method.** Four commitments shaped the work.

1. *Validation first.* Every detector has a known positive, a negative, a deceptive control built to fool it, and a null that accounts for how its candidates were selected (D-012; `emergence benchmark --probes`). As last reported, the benchmark held 170 checks. Each part has precedent: Bedau's neutral shadow (a selection-off copy used as a null), Bullock and Bedau's tests of whether activity statistics misclassify unlifelike systems, and Lohn and Reggia's warning that automatically found self-replicating rules must be checked by simulation ([Literature]({{ '/literature.html' | relative_url }})).
2. *Passive observation.* The simulation never sees the observer. Interventions (isolation tests, knockouts, transplants, forks) run only on cloned universes (D-003).
3. *Pre-registration.* Confirmatory tests were pre-registered; the files are in `docs/data/`. Exploratory results are labelled as such.
4. *The rule as the unit.* Questions about which rules make structure are answered with rules as the unit of analysis. This was adopted late (D-063, after E-76). Earlier tests were run with worlds or soups as the unit, and we report both. Six soups of one rule are not six independent tests of a property of that rule. This is the textbook fix for pseudoreplication, an error we made first (section 7).

## 2. Substrates and methods

| Substrate | What it is | Where |
|---|---|---|
| Life-like and Generations cellular automata | 2D outer-totalistic rules (B/S, B/S/C) on a torus | `emergence/physics/totalistic.py` |
| Lenia family | continuous cellular automata with smooth ring kernels: Lenia (states quantised to 256 levels), Flow-Lenia (mass-conserving, float states), multi-channel Lenia | `emergence/physics/` |
| BFF program soups | random 64-byte programs in a minimal Brainfuck-like language; each round, programs are paired at random and run on their joined 128-byte tape; background mutation | `emergence/programs/bff.py` |
| SUBLEQ family | a family of SUBLEQ-like languages defined by us | `emergence/programs/subleq.c`, `subleq.py` |

The spatial substrates run through one engine, a passive observatory and a discovery engine (Pareto ranking, novelty search and behaviour niches; D-004, D-009). The program soups have no space; scripts run them outside the engine.

**The SUBLEQ family is ours.** We built it to test a BFF result in a structurally different language (D-054). Its knobs are the number of operands, the jump condition, a write offset, and two features we added: an index that steps on each instruction, and an operand window W (J-077). The family has 16,416 rules. The two published variants we included as anchors, plain SUBLEQ and RSUBLEQ4, made no replicators: not one hit in 10<sup>7</sup> random programs each (E-75 phase 1). Agüera y Arcas et al. (2024) reported this first; we confirm it. Every SUBLEQ result below is therefore about rule versions we designed.

**Compute.** Everything ran on one laptop with no GPU: NumPy and SciPy, plus small C interpreters called through ctypes. Experiments took from minutes to 15.8 hours on 11 worker processes (E-78).

## 3. Finding A: in Lenia, self-propelled structures depend on the spatial correlation of the random start

<figure>
<img src="{{ '/assets/report/emergence-soup-vs-smooth.png' | relative_url }}" alt="Two rows of four Lenia snapshots at steps 0, 100, 400 and 2000. Top: a fine-grained random start freezes into a maze of static blobs. Bottom: a smooth random start breaks into lumps, a few become gliders, and one glider remains.">
<figcaption><b>Figure 1.</b> One illustrative world pair: the Orbium rule, same seed, same total mass. Top: a soup start freezes into static blobs. Bottom: a smooth start breaks into lumps; a few become gliders and one survives. The rates are in Figure 2 and Appendix A, not in this picture.</figcaption>
</figure>

**A search from soup starts finds no movers, although movers can exist.** The discovery engine and a random search together ran 2,085 Lenia worlds from soup starts and found no self-propelled structure (E-12). Yet a viability scan, which grew gliders from 12 hand-made seed shapes, found 8 of 99 single-ring rules that support a glider (E-13a), all around Chan's Orbium. This is a lower bound, since other seed shapes might work. So in these rules the limit was emergence, not existence, a distinction Eppstein (2010) draws for Life-like rules.

**Smooth starts make gliders; soup starts with the same mass almost never do.** A smooth start is Gaussian-blurred white noise, matched to the soup start by total mass (D-023). In an exploratory run, 18 of 240 smooth-start worlds grew a verified glider, against 0 of 80 soup starts (E-13). Its pre-registered rule-level sign test could not pass: with 8 rules the smallest possible p is 0.0078, above the registered threshold. The confirmatory test (E-14, fresh seeds, universe-level Fisher tests at α = 0.025) found 28 of 160 smooth worlds against 0 of 160 soup worlds at density 0.10 (p = 1.0 × 10⁻⁹), and 21 of 160 against 0 of 160 at density 0.35 (p = 2.4 × 10⁻⁷). Every glider survived 1,000 steps alone. **At the rule level the evidence is weaker:** 6 of the 8 rules made gliders, a sign test gives p = 0.031 for both contrasts, and that is above the registered α (review R-4). After a Holm correction across the project's 42 pre-registered primaries (E-79, J-092), the two world-level tests survive (adjusted p = 3.6 × 10⁻⁸ and 7.8 × 10⁻⁶); with the rule-level sign tests in their place they would not (adjusted p = 0.71).

**The cause is spatial arrangement, not the mix of values.** A smooth field also has more weakly filled cells than a soup start. Review R-4 pointed out this confound, and a pre-registered shuffled control removed it (E-19a): the same values as the smooth start, randomly permuted in space. At density 0.10, smooth starts made gliders in 37 of 160 worlds, shuffled starts in 0 of 160 and soup starts in 0 of 160 (p = 6.9 × 10⁻¹³). At density 0.35 the counts were 11, 0 and 0 of 160 (p = 4.1 × 10⁻⁴). By rule, 6 rules were higher and none lower (sign test p = 0.016), and 5 higher, none lower (p = 0.031). Under the Holm correction the world-level tests survive (adjusted p = 2.7 × 10⁻¹¹ and 0.010); the rule-level sign tests would not (adjusted p = 0.39 and 0.71, E-79 sensitivity analysis).

**Prior work on structured starts.** Correlated or compact starts are common practice in Lenia work (Chan's patches, Flow-Lenia's centred patch, Reinke et al.'s CPPN starts, Perlin noise in MaCE and in Papadopoulos et al. 2024, who write that this is "implicitly selecting for interesting dynamics"), Reinke et al. note that white noise tends to give "dead or global patterns", and Hudcová et al. (2026) vary only the area of a noise patch. We did not find a sweep at fixed mass or a value-preserving shuffle control in this search, so the shuffle-controlled contrast is "not found in this search", which is not a claim that it is new ([Literature]({{ '/literature.html' | relative_url }})).

**Soup starts are not hopeless, only close to it.** R-4 also noted that soup starts either die or freeze into blob fields, so their zero was nearly guaranteed. A density sweep (E-19b) found that soup starts die below density 0.18 and become blob fields above 0.24. One soup world in 400 made a glider, at density 0.20, right at the switch. Across all soup-start worlds run in this rule panel, gliders appeared in 1 of 1,120. Smooth starts gave 7 to 23% of worlds, depending on rule panel and density (E-14, E-19a).

<figure>
<img src="{{ '/assets/report/e19-null-and-sweep.png' | relative_url }}" alt="Left: glider worlds by start condition at two densities; gliders only from smooth starts, none from shuffled or soup starts. Right: soup-start outcomes across densities 0.12 to 0.30; extinct below about 0.18, blob fields above about 0.24, one glider world at 0.20.">
<figcaption><b>Figure 2.</b> E-19 (pre-registered). Left: shuffling the positions of the smooth start's values removes every glider. Right: the soup-start density sweep; one glider world sits at the die/freeze switch. World-level counts; the rule-level sign tests are in the text.</figcaption>
</figure>

**Sparse patches also work, given room.** Chan's published start (his code, `LeniaND.py`) places 15 to 39 dense patches of side int(0.9R), values in [0, 0.9), in an empty world; our implementation draws 15 to 40 patches of side 12. It made no gliders in 40 worlds of 128 × 128 (E-13). In worlds of 256 × 256 run for 3,000 steps, it made gliders in 13 of 160 worlds (8.1%), in 5 of the 8 rules, while 110 patches made none in 160 and smooth starts made them in 29 of 160 (E-24). World size and run length changed together, so "room matters" is suggested, not shown. Both successful starts put matter into isolated lumps with space around them; that mechanism is consistent with the data but untested.

**Other movers.** A search from smooth starts found a slow, turning mover, the "wanderer", in one rule (E-17). In that rule, smooth starts made wanderers in 36 of 40 worlds and soup starts in 0 of 40 (E-18a). On a grid of 42 neighbouring rules, wanderers arose in 7, all on a narrow diagonal band, and in none of 252 soup-start worlds (E-18b). A rule drawn at random gave a third kind, a slow straight "ring glider", in 13 and 18 of 40 smooth worlds at two densities and in 0 of 40 soup worlds at each (E-26). Each of these is one rule. We claim only that they are new to this project.

**Populations and collisions.** In worlds of 384 × 384, a growing blob field swallowed the gliders in 23 of 30 worlds (E-15). In 500 controlled collisions no glider was born, but 7 fused two gliders into a stable double glider (E-20). Spontaneous double gliders were rare (1 genuine case in 320 smooth worlds, E-21), and a double glider hit by a glider never formed a triple in 312 collisions (E-23). Meeting wanderers usually merged into one (71% of 200 encounters, E-22).

**No reproduction, except one multi-channel rule.** A birth detector (D-028, validated on HighLife's replicator and Gray-Scott spots) found no reproducing mover among 285, and no reproducer in 350 held-out worlds (E-27, E-28). Lone lumps in 3,000 random single-channel rules gave no reproducer in the 1,453 rules the detector could decide (E-29). In single-channel Flow-Lenia with R = 13 and 1 to 3 kernels, no isolated translating structure appeared in 400 worlds from soup, smooth and Chan-style patch starts (E-16); an earlier run from the Flow-Lenia paper's own centred 40 × 40 patch found none in 80 rules with 3 to 10 kernels (J-016). Plantec et al. report dynamic patterns, including gyrating ones, as common but publish no rate, sample R from [2, 25] and show multi-kernel and two-channel creatures, so our result is not comparable with theirs; it is not a failed reproduction. Fed Flow-Lenia with travelling parameters produced no reproducers once a food artefact was removed (E-30, E-31). One rule in 1,000 random multi-channel rules made dividing spots (E-32; 1 of 450 decided rules). Lumps with scrambled values also became dividing spots, so the spot is an attractor of the rule: offspring cannot inherit anything from a particular parent. This is level 3 in its weakest form, with no possible heredity. Its rate did not differ significantly from single-channel Lenia (p = 0.24). Chan (2020) found self-replication "not rare in extended rules" and Plantec et al. (2023) call dividing dots "a common pattern"; both found them by guided search or other sampling, so our rate among random rules measures something different. MaCE (2025) already names the missing "capacity to transmit their genes" as the gap towards evolution; our scrambled-lump test is a cleaner version of that point.

**What finding A supports.** Level 2, arising spontaneously, in the Lenia family, from spatially correlated starts. The causal role of arrangement is tested by the shuffled control, at the world level with p values below 10⁻³, and at the rule level with sign-test p values of 0.016 to 0.031 over the 8 rules of one panel near Orbium; the world-level tests survive a Holm correction across the project's primaries, the rule-level ones do not (E-79). It does not establish a general law for glider-capable rules. It contrasts with Life-like rules, where an apparent effect of a central patch (+1.35 self-propelled shape types, p = 0.004) disappeared when density was matched (−0.08, p = 1; E-09, E-10).

## 4. Finding B: which rules make replicators in program soups

### 4.1 Replicators from random BFF code

In 12 pre-registered BFF soups of 2<sup>14</sup> programs, none jumped by round 16,000 (E-40), against our prediction of 2 to 6. Continued to round 48,000, two more jumped (E-41). With a pilot that jumped at round 8,750, that makes 3 of 16 soups. The detector found verified replicators in every jumped soup and none in the 22 end scans of soups that did not jump. A deceptive control mattered here: a "copy-all" mode raised HOE to 7.0 bits with no replicator present, so HOE alone would have reported a jump. This reproduces, at small scale, the central observation of Agüera y Arcas et al. (2024): self-replicators emerge from random BFF programs with no fitness function. Our experiments did not compare rates with theirs. The literature review (J-091) did the arithmetic: at our pooled rate (0.036 per 10<sup>8</sup> pair runs, below), their 16,000 epochs at 2<sup>17</sup> programs give about 0.38 expected events, a transition probability of about 0.32, against their reported 40%, with the same background mutation rate (0.024% per byte per round). Two caveats: whether their soups started both heads at byte 0, as ours do, is unverified, and the arithmetic extrapolates our rate beyond our largest 64-byte soups (2<sup>16</sup>), so this is a consistency check, not a result.

<figure>
<img src="{{ '/assets/report/e41-bff-soup.png' | relative_url }}" alt="Three panels of coloured pixel rows. Left: random speckle. Middle: more instruction bytes but still varied rows. Right: most rows share code at the same positions, forming vertical stripes.">
<figcaption><b>Figure 3.</b> One soup (pilot seed 901, replayed exactly), programs as rows of coloured bytes. Left: the random start. Middle: just before the jump. Right: 1,000 rounds after it, one family of self-copying programs and its variants has spread. One soup, shown for illustration.</figcaption>
</figure>

**The jump rate grows with soup size.** Across soups of 2<sup>13</sup> to 2<sup>16</sup> programs, the jump rate per round scaled as size<sup>β</sup> with β = 1.02 (95% interval 0.11 to 2.02, one-sided p = 0.014; E-50, pre-registered). This pass does not survive a Holm correction across the 42 primaries (adjusted p = 0.30; E-79), nor within the BFF-emergence tests alone (0.085). Three of the registered "jumps" were brief waves of zero-writing programs with no replicator; counting only verified jumps (post hoc), β = 0.93 (−0.17 to 2.15), p = 0.049. A later exploratory fit (E-76) found one rate per pair run, 0.036 per 10<sup>8</sup> (0.017 to 0.066), adequate for all four sizes (p = 0.16 against separate rates). Knierim et al. (2026) also time BFF emergence per interaction and report "very similar results" across soup sizes, and the authors' cubff repository holds unpublished tools for a fresh-pair spawn rate and a memorylessness test. Their mean time is for a variant built to ease copying (`bff_selfmove`) and counts first appearance, not take-over, so it is not a check on our rate.

<figure>
<img src="{{ '/assets/report/e50-soup-size.png' | relative_url }}" alt="Left: jump rate per million rounds against soup size on log scales, with a fit line; the 32,768 arm has no jumps. Right: HOE traces of the five largest soups that crossed the threshold; three stay high, two spike and fall back.">
<figcaption><b>Figure 4.</b> E-50. Left: jumps per million rounds by soup size, as pre-registered (blue) and counting verified replicators only (orange); grey is the fit. Right: two of the threshold crossings were brief zero-writing waves, not jumps. Nine events in all, so the interval on β is wide.</figcaption>
</figure>

### 4.2 Why emergent copiers run backwards, and a one-detail counterfactual

Reverse and palindromic copying in BFF is published (Agüera y Arcas et al. 2024; cubff PR #14), Knierim et al. (2026) describe self-inverting replicators that need an even number of executions, and both groups found head offsets important; Knierim et al. start heads 64 apart on purpose. What we add is the census explanation, the one-change soup counterfactual and the h = 127 control below. All 9 replicators that emerged in our standard BFF soups copied themselves backwards and made their own byte-reverse (J-046). A census of every program kernel of 1 to 6 instructions explained why (E-55, pre-registered): under the standard rule both heads start at byte 0 and wrap around the tape, so all 55 short copiers copy in reverse. Moving one head's starting byte to 64 turned that into 139 forward copiers and no reverse ones. A backward copier's copy is its mirror, which no longer contains a working loop, so under the standard rule the smallest replicator needs two kernels (10 instructions), against 5 under the counterfactual (E-57).

Under the counterfactual rule, 8 of 8 soups of 2<sup>14</sup> programs jumped within 250 to 1,750 rounds, against 0 of 12 under the standard rule by round 16,000 (p = 8 × 10⁻⁶; E-57). A control rule with as many short copiers, all backward (head 1 starting at byte 127), was slow again: 2 of 16 soups against 8 of 8 (p = 6 × 10⁻⁵; E-59). That control's first test (E-58) failed as registered, because its HOE threshold misfired in this rule; the conclusion rests on a corrected reading and on the fresh confirmation E-59.

### 4.3 The "shortest copier makes a working copy" predictor (F)

We call a rule **F** if, among its copiers of at most 6 instructions, at least one leaves a copy that is itself a copier. The property is computed from the rule alone, in seconds to minutes, before any soup runs. It has predecessors: Agüera y Arcas et al. (2024) proposed the shortest replicator length as "a key factor" but not the only one, Adami (2015) estimates the chance of a random replicator as D<sup>−I</sup>, and C G et al. (2017) counted replicators exhaustively among all length-8 Avida genomes. We have not tested F against the simplest baseline, the density of replicators among random programs. The table gives every soup test of it, rule-level counts first. Rule counts are tallied from the exports; only the soup-level p values were computed by the experiments.

| Exp. | Rule family | F rules with any jump | Other rules with any jump | Soups (F vs other) | Registered verdict |
|---|---|---|---|---|---|
| E-60 | head 1 start h, all 128 rules | 3 of 3 | 2 of 4 (weak criterion; 1 of 4 on the corrected reading, J-061) | 12/12 vs 2/16, p = 3 × 10⁻⁶ | pass |
| E-62 | F′ rules (shift-aware) | 7 of 7 | (none run) | 28/28 | lineage predictor fails |
| E-63 | rules just outside F′ | (control h = 64: 4/4) | 1 of 4 | 1/16 vs 28/28, p = 7 × 10⁻¹¹ | pass |
| E-64 | two head starts (g, h), 256 rules | 3 of 3 | 1 of 4 | 10/12 vs 1/16, p = 5 × 10⁻⁵ | pass |
| E-65 | same family, 768 new rules | 7 of 7 | 1 of 4 | 26/28 vs 1/16, p = 9 × 10⁻⁹ | pass |
| E-68 | program length 16 to 128 bytes | (not tallied) | (not tallied) | 18/36 vs 6/36; length 16: 0/12 vs 0/12 | soup prediction fails |
| E-69 | lengths 16, 32 at matched bytes | (not tallied) | (not tallied) | length 16: 4/12; length 32: 10/12; other 0/24 | undecided |
| E-70 | five instruction-set variants | 15 of 15 | 6 of 15 | 60/60 vs 15/60, p = 2 × 10⁻²⁰ | pass |
| E-71 | 22 further F rules from E-70 | 21 of 22 | — | 165/176 | (a speed test; one F rule made nothing) |
| E-74 | 24 fresh F rules | 24 of 24 | — | 143/144 | (a speed test) |

Three failures bound the result. In E-68 the property held in the census at every program length, but 16-byte programs made no replicators at all; at matched bytes this was partly a soup-size effect (E-69). One F rule (variant 1, h = 68) made nothing in 8 soups (E-71). And non-F rules next to the band often jumped too (6 of 15 non-F rules in E-70), because the census misses slightly longer or shifted copiers. A first version of this predictor also failed in a different form: "lineages that persist" did not separate rules (E-62).

**After correction.** Every soup-level pass in the table survives a Holm correction across the project's 42 pre-registered primaries (adjusted p ≤ 0.002), as does E-61's (8 × 10⁻⁶; E-79). The rule-level tallies are small, though. Rule-level Fisher tests recomputed from them (exploratory, E-79) give p = 0.29 (E-60), 0.21 (E-61), 0.024 (E-63), 0.11 (E-64), 0.024 (E-65) and 3.5 × 10⁻⁴ (E-70); after Holm only E-70's survives (adjusted p = 0.012). E-68's Fisher test (p = 0.0027, below its α of 0.01, though the verdict failed on the 75% share) does not survive either (0.062).

<figure>
<img src="{{ '/assets/report/e60-headstart.png' | relative_url }}" alt="Top: short copiers per rule over h from 0 to 127; backward copiers near 0 and 127, forward copiers only at 62 to 65, where stars mark rules with a self-sufficient copier. Bottom: share of soups that jumped by 16,000 rounds in the rules run.">
<figcaption><b>Figure 5.</b> E-60 and earlier soups. Top: short copiers in each of the 128 rule versions; stars mark F versions. Bottom: soups that jumped. Caveat found later (J-061): the copier test here saw only copies aligned at byte 64, so it missed shifted copiers; one soup at h = 7 turned out to be full of them.</figcaption>
</figure>

**No census measure predicted speed.** The number of self-sufficient copiers looked like a graded predictor in exploratory data (ρ = −0.80 over 15 rules, E-70), but a pre-registered test found it worked within a variant (p = 0.006) and not pooled across variants (p = 0.06; E-71). The within-variant pass does not survive a Holm correction across the 42 primaries (adjusted p = 0.13), though it does within the BFF-emergence tests alone (0.042; E-79). A five-generation version failed on fresh rules (E-72), looked ten times better after a validated re-scoring (p = 0.06, E-73), then failed under every timing on 24 fresh rules (ratios 0.66 to 0.95; E-74). Speed results also depended on the detector: in E-74 the three jump timings differed by more than 1,000 rounds in 24 of 144 soups.

### 4.4 The SUBLEQ family: a chain in which each predictor passed once

We then asked whether "a short copier that makes working copies" generalises to a different language. The answer is a chain of partial results.

- **Phase 0 (build).** The first unseeded take-over was a 5-byte loop that rewrites most of its own body. Every whole-program copy test missed it (0 of 40), so we built an inheritance test: a block of at least 4 bytes must survive 5 generations of copies into fresh random partners, and vanish when knocked out (D-055; 39 of 40 on the loop).
- **Phase 1 (census).** Of 600 sampled rules, 32 were F, 100 copied without inheritance, 468 neither. Every F rule had 4 operands and an index step of ±1. A pre-registered stability check failed (37 of 40 rules kept their class with a second seed).
- **Phase 2 (pilot).** F rules: 8 of 8 soups jumped. Non-F copying rules: 4 of 8. The take-overs were periodic tiles, one instruction repeated, which a census of random programs never samples.
- **Phase 3 (pre-registered, passes).** A new predictor, tile-replicator density, separated rules: 11 of 12 HIGH rules jumped, 1 of 12 LOW (rule-level p = 5.4 × 10⁻⁵; soups 64/72 vs 6/72).
- **Phase 4 (pre-registered, fails).** With thresholds unchanged, under another jump condition: 6 of 12 HIGH rules vs 5 of 12 LOW (p = 0.50; soups 29/72 vs 20/72, p = 0.08).
- **Phase 4b (exploratory).** Earlier entries said non-jumping soups "freeze into halters" and that jumps were "escapes". Measuring at round 0 showed they never leave the random start. Those claims are withdrawn (J-082).
- **Phase 5 (pre-registered trace of origins).** In 53 of 54 soups of rarely-jumping rules, no replicator ever arose in 4,000 rounds. Where one arose, it established within a median of 16.5 rounds. Founders were written in a single run of a pair (24 by the partner, 16 by the program itself), never by mutation alone. **In this SUBLEQ family, a jump is the wait for one rare event.** This is not claimed for BFF (section 4.5).
- **Phase 6 (pre-registered, retrospective).** So we measured that event: R<sub>P</sub>, the rate at which runs of fresh random pairs write a replicator. It predicted jumps where tile density had failed (ρ = 0.64, p = 4 × 10⁻⁴; after Holm, adjusted p = 0.010, below 0.05 but not below its registered α of 0.01; E-79), but rules with no product still jumped in 35 of 222 soups.
- **Phase 7 (pre-registered, prospective).** New rules chosen by R<sub>P</sub> alone: 6 of 7 HIGH rules jumped against 2 of 12 ZERO rules (rule-level p = 0.006; soups 33/42 vs 12/72). That rule-level p counts a rule as jumping if any of its soups did and was computed after the fact; with the pre-registration's own rule definition (≥ 4 of 6 soups) it is 0.029 and would not survive a Holm correction, while the soup-level test does (adjusted p = 2.3 × 10⁻⁹; E-79). The design needed 8 HIGH rules and the pools gave 7, so the primary is **undecided**. On these 19 rules, tile density correlated with outcome slightly better than R<sub>P</sub> (ρ = 0.75 vs 0.67).

Both ideas have precedents. Tile-like replicators appeared in the source paper's 8080 soups (non-looping two-byte repeats) and, as that paper describes, in Coreworld (two-instruction MOV-SPL copiers). R<sub>P</sub> has an unpublished twin in the cubff repository's `selfrep_spawning.py`, which pairs a program with fresh random partners and counts the replicators produced.

### 4.5 One rate per rule

Review R-5 proposed replacing further censuses with one model: each rule has a single origin rate, and the wait to a jump is exponential (E-76, exploratory, rule as the unit). It is a fair first description, not an exact one. The mean coefficient of variation of jump times, 0.77, matches the exponential's 0.79. But 8 of 26 rules fall in the 5% tails, against 2.6 expected (p = 0.003). Where jumps follow "always", soups produced replicators at the fresh-pair rate in their first 500 rounds (ratio 1.00, 95% interval 0.69 to 1.38). Under "jump if ≤ 0" they produced about 7 times faster (6.9, 4.8 to 10.0), already in the first rounds, with no rise with soup age (p = 0.48). Under "jump if < 0" the ratio was 0.66 (0.46 to 0.91). Why soups beat fresh pairs under one jump condition is open. BFF's rate is 10 to 1,000 times lower than that of the SUBLEQ rules that jumped.

<figure>
<img src="{{ '/assets/report/rate-model.png' | relative_url }}" alt="Scatter of soup origin rate against fresh-pair product rate for 79 SUBLEQ rules on log axes, coloured by jump condition, with a diagonal line; many rules with no product and no jump sit at a single point near the census limit.">
<figcaption><b>Figure 6.</b> E-76 (exploratory; outcomes known before the analysis). Each point is one rule; open markers and arrows are bounds; on the dashed line soups make replicators exactly as often as fresh random pairs. 37 rules with no jump and no product share one point.</figcaption>
</figure>

**What finding B supports.** Level 3: replicators arise from random code in BFF and in SUBLEQ versions we designed. In BFF variants, the F property predicted which rules make replicators in pre-registered tests across four kinds of rule change, with stated exceptions. These soup-level passes survive a Holm correction; recomputed with rules as the unit, only E-70's would (exploratory, E-79). All of these variants keep BFF's head-and-tape design, and the five instruction sets were picked by hand. Outside BFF, no single predictor transferred. The best summary is a rate per rule, in both languages. In the SUBLEQ family we also traced the mechanism: replicators appear when a rare pair run writes one, so anything that raises the number of pair runs (soup size) or the chance per run (the rule) brings the jump sooner. We do not claim that mechanism for BFF: Agüera y Arcas et al. (2024) trace a BFF origin through several stages over several interactions, and Knierim et al. (2026) find BFF replicators by mutation-only random walks and still find them when no copying between programs is allowed (D-066).

## 5. Finding C: after replicators appear

**Heredity: yes, in BFF.** Every single-byte mutant of the 9 emergent replicators was seeded alone in a fresh soup (E-42, pre-registered). All 9 replicators showed heredity: of 141 mutants that could still copy, 140 were carried by at least 60% of their descendants. This is level 4 for programs that arose from random code. It was not tested in SUBLEQ, and it is impossible in the Lenia divider.

**Selection among variants: mostly not seen.** One-byte variants were indistinguishable from their parents in head-to-head races: 2 of 141 pairs showed a difference, 0 of 24 neutral pairs (p = 0.73; E-43). Replicators from different soups did not differ either: 0 of 36 pairs (E-44). One exception held up. A species from soup 5006 won 176 of 252 races against soup 901's replicators (69.8%, p = 1.3 × 10⁻¹⁰; E-46), after we found that every emergent replicator has two mirror forms and corrected the counting (J-046). That test was registered with the prediction of no difference, so E-79 lists it outside the Holm family; its p value would survive any correction of this size. The same correction shrank a hand-written replicator's apparent advantage from 77% to 56% of races. This is one species in one soup; it does not show that selection drove the soup's change.

**Drift without adaptation, by four measures.** After a jump no family dominates: the most common family holds a median of about 2% of the soup, and the most common program drifts far from the founder (E-47). Is the drift adaptive? Races between late and early programs: not significant (E-48, p = 0.07; with verified replicators only, E-49, p = 0.33). Growth rate into random code: no trend (E-51, p = 0.38). Invasion into the soup itself showed an advantage for later code (E-52, p = 0.045), but only in backgrounds where the later code alone had relatives; in kin-free backgrounds it vanished (E-53, p = 0.88). Across 7 soups and a 16,000-round gap, kin-free invasion again showed nothing (E-54, D = −0.15, p = 0.64). Soup 5006 leaned upward in several of these measures; that is post hoc. Seeded systems differ: in Tierra, Ray's 80-instruction ancestor evolved into a 22-instruction creature, a 5.75-fold efficiency gain, and in Hutton's Squirm3 selection only shortened molecules. Shortening is the usual published route to fitness gain after emergence, and BFF programs have a fixed length of 64 bytes; that may explain the absence of a trend, but this is our inference, not a published result.

**No parasites.** E-54 had reported that only 22 to 78% of common programs were replicators. That was luck of a single stochastic test. Repeated 10 times, 99.8% of 2,800 common programs copied themselves, and none was a parasite (E-66). Among 420 rarer programs, there were again none (E-67). Parasites are common elsewhere: Tierran parasites appear within the first few million instructions and exploit template addressing and memory that protects only writes, Stringmol parasites arise "almost immediately", and Jha et al. (2026, abstract only) report "parasitic stealing" in Z80 soups. BFF has no persistent bodies, protected genomes or template addressing, and its pairs are joined, run once and split, so we read this negative as a property of BFF's interaction geometry, not of emergent replicators in general.

**Space did not change the answer.** Review R-5 suggested that well-mixed soups might hide adaptation that needs local interaction. E-78 (pre-registered) forked each of the 7 jumped E-54 soups into three continuations of 20,000 rounds: well mixed (M), neighbour-only on a 256 × 256 torus (S), and well mixed with another seed (M′, a seed null). The primary test asked whether late S code gained more fitness, in a well-mixed common garden, than late M code. It failed: the mean difference was −0.42 (95% interval −1.10 to 0.25, below the registered bound of 0.28; p = 0.91). The seed null was significant: M′ fell below M in 7 of 7 soups (p = 0.016). Two well-mixed continuations of one snapshot therefore differ about as much as space and mixing do, which means continuation noise is large at 7 soups. Late code was not fitter within any arm, and no parasites appeared. Post hoc, S became a mosaic of small local families: about 55% of neighbouring programs were at least 90% identical, while the largest family held only 0.2 to 0.4% of the soup. Spatial replicator theory predicts this null for our assay: space mainly protects against parasites, and it can favour prudent or less informative types that lose under mixing (Takeuchi and Hogeweg 2012; Kerr et al. 2006). With no parasites and a well-mixed common garden, a null was the likely outcome even if spatial adaptation had happened; a lattice-native assay, such as invasion from a patch or front speed, is needed to see it.

<figure>
<img src="{{ '/assets/report/e78-spatial.png' | relative_url }}" alt="Left: per-soup late-minus-early invasion score in three arms; the neighbour-only arm is not higher and is much lower in two soups. Middle: families holding at least 1% of the soup over time; the neighbour-only arm falls to zero. Right: share of near-identical grid neighbours, about 55% in the neighbour-only arm.">
<figcaption><b>Figure 7.</b> E-78. Left: late minus early invasion score per soup (pre-registered measure). Middle: families holding at least 1% of the soup (pre-registered descriptive; undefined in S, which has none). Right: near-identical grid neighbours (post hoc). Orange: neighbour-only; blue and grey: well mixed, two seeds. Seven soups.</figcaption>
</figure>

**What "level 5 not shown" means.** In standard BFF soups of up to 2<sup>16</sup> programs, followed up to 20,000 rounds after the jump, later replicators were not detectably fitter than earlier ones by races, growth rate or kin-free invasion, and no parasites were found, with well-mixed or neighbour-only meetings. It does **not** mean that these soups cannot evolve. What we tested is a precondition, directional adaptation, and the result is no large adaptive effect detected with 7 soups; we did not compute the field's standard open-endedness statistics (evolutionary activity against a neutral shadow, Bedau et al. 1998; the MODES metrics, Dolson et al. 2019). Both fitness instruments are well mixed, so an advantage that exists only in space is invisible to them. The assays were calibrated on hand-made variants with large built-in differences; small advantages would be missed. Seven soups is a small sample, the gap is a few tens of thousands of rounds, and one language at one scale was tested. In Life-like rules, the earlier knockout test of "earlier innovations enable later ones" found real knockouts indistinguishable from placebo deletions (P = 0.49 to 0.51 over 92 tests; E-10, E-11).

## 6. The discovery engine (H1)

H1 says the guided search finds more interesting rules than random search at equal compute. The first test used 2 seeds per arm (E-03 to E-06) and found 1.9× more distinct rules with self-propelled shapes and 4.2× more rules "complex" on every seed, after removing near-duplicates. The code for that removal was never committed; it was rebuilt when the test was repeated (J-087, D-064). The pre-registered repeat with 20 paired seeds (E-77) found 1.84× more distinct self-propelled rules (bootstrap 95% interval 1.70 to 2.25), with the engine ahead on 20 of 20 seeds (p = 9.5 × 10⁻⁷, the smallest possible with 20). For rules complex on every seed the ratio was 3.4 (2.6 to 3.9). Limits: Life-like and Generations rules only, one budget, one world size, and self-propulsion is one of the engine's own objectives, so that win is partly circular. In Lenia the engine found the glider island (59 of its 500 rules against 9 for random search, E-13a), but the Lenia comparisons E-12 and E-17 are single-seed. The design (guided against random search at equal budget, independent seeds) is standard (Reinke et al. 2020; Hamon et al. 2025), and our ratio is small next to Hamon et al.'s 486 moving stable solitons in 1,600 guided outputs against 30 in 117,000 random trials, a loose comparison because their random search also sampled initial patterns. In Life-like rules a ratio near 2 is unsurprising: Eppstein (2010) found spaceships in 10,736 of 16,384 B3 rules (65.5%).

## 7. How the detectors were fooled, and what caught it

| Case | What was wrong | How it was caught | Control that now exists |
|---|---|---|---|
| Static Lenia blobs called complex (J-012) | the "complex" label, tuned on two-state rules, called 27 of 60 random Lenia rules complex; all were static blob fields | a review, then looking at the universes | "complex" needs a verified mover; blob-soup negative, jitter and selection-aware null probes (D-022) |
| Labyrinth bursts (J-032) | the first birth detector reported 2 reproducers: single blobs bursting into world-filling labyrinths | pre-registered inspection of every hit | doubling rule and fixed reference parent; labyrinth as deceptive control; held-out E-28 |
| Food condensation (J-035) | 17 of 100 fed Flow-Lenia worlds had "reproducers"; the food layer itself condensed into droplets | pre-registered inspection; food alone with slight noise | perturbed-vacuum null (D-030), tested on held-out rules (E-31) |
| Kinship in invasion (J-052, J-053) | later code "invaded better" only where it alone had relatives in the background | kin check after the run | kin-free backgrounds (E-53 onward) |
| Single stochastic test (J-068) | "only 22 to 78% are replicators" was the luck of one test per program | a pilot of the parasite detector gave different verdicts for the same program | test repeated 10 times; single verdicts are lower bounds (D-049) |
| Sloppy copiers, filler smears (J-074, J-075) | a 60-of-64-byte copy test missed copiers at 59 to 60 bytes, and accepted loops that smear one value (37 of 64) | HOE at 6.4 in soups scored "no jump" | 58-byte test with an instruction-fidelity guard (D-053), sloppy positive, smear deceptive, null |
| Self-rewriting replicators (J-077) | every whole-program copy test missed a loop that rewrites its own body (0 of 40) | the first unseeded SUBLEQ take-over | inheritance test with knockout (D-055) |
| The null all-zero replicator (J-083) | a program of zero bytes passes the inheritance test while carrying no information | development of the origin trace | tracer classifies all-zero inherited blocks; jump calls rechecked on 7 soups |
| "Frozen" soups (J-082) | a "freeze into halters" mechanism was reported for three phases | measuring soups at round 0 | claims withdrawn; the flag now reads "never left the random start" |
| Soup-level p values (J-086) | six soups of one rule were treated as six tests; p values 10⁵ to 10¹⁹ times too small | the one-rate synthesis (review R-5) | rule as the unit (D-063) |
| Uncommitted deduplication (J-087) | the step behind H1's headline ratios existed only as a session's calculation | reproduction of E-03 to E-06 | committed `distinct_greedy` (D-064) |
| HOE rising with clustering (J-088) | in spatial soups, HOE rises with clustering alone because it reads the soup in storage order | the positive and `noexec` controls of the spatial runner | HOE on shuffled rows |
| Zero-writing waves (J-054) | brief waves of zero-writing programs crossed the HOE threshold for one checkpoint | the replicator scan found nothing | jump needs 3 checkpoints and a verified replicator (D-045) |

The common pattern: a measure validated on one system was trusted on another. The fix each time was a control from the new system itself. Such controls have precedents (Bedau's neutral shadow; Bullock and Bedau's false-positive tests; Lohn and Reggia's checks by simulation); a public, itemised table of a project's own detector failures was not found in the literature search.

## 8. Limitations and threats to validity

- **Sample sizes.** The Lenia result rests on one panel of 8 rules near Orbium, plus single rules for the other movers. The level-5 tests use 3 to 7 soups. The F-predictor arms had 3 to 15 F rules per test, and SUBLEQ phase 7 had 7 HIGH rules where 8 were needed. Rule-level tests are therefore modest even where world-level p values are tiny.
- **Many tests, one correction applied after the fact.** Appendix B scores the experiments with a pre-registered primary. Re-reading their pre-registration files (E-79, J-092) gives 42 registered primary p values that test a predicted effect; 15 registered primaries that are not significance tests (descriptive criteria, counts, census bands; E-47's test was never computed and E-75 phase 5 registered none); and 8 tests whose prediction was a null. A Holm correction at family-wise α = 0.05, pre-registered (D-067) and applied in E-79, keeps 18 of the 20 passes. The soup-size exponent (E-50, adjusted p = 0.30) and the within-variant copier count (E-71, 0.13) lose significance, as does E-68's Fisher test (0.062; its verdict had already failed). Benjamini–Hochberg at q = 0.05 keeps all 22 significant tests. With rule-level p values where the record has them (D-063), 14 passes survive: the Lenia contrasts (E-14, E-19a) fall away, the phase-7 rule count (p = 0.029 with the registered rule definition) does not survive, and E-75 phase 3 stays. Recomputed at the rule level for the F predictor (exploratory), only E-70 survives. Holm within each thread loses only E-50. The tests are not independent (several reuse comparison arms or rules), which Holm tolerates; some p values are rounded as reported (Appendix B2).
- **Post hoc steps.** Several thresholds were set after seeing data: the quasi-static cut-off of D-022 (on 60 rules), the birth detector's doubling rule (after E-27), the perturbed-vacuum null (after E-30), the inheritance test's depth (by a sweep after the controls), and the tile thresholds (on 8 pilot rules). Most were then tested on held-out data; the E-78 mosaic and the soup-5006 trend were not.
- **Families shaped by us.** The SUBLEQ family's stepping index and operand window are our additions (D-054); the published variants made no replicators. The BFF variants are hand-picked. "Which rules make replicators" is answered within these families, not across languages in general.
- **One laptop scale.** Worlds of 96 to 384 cells on a side; soups of 2<sup>13</sup> to 2<sup>17</sup> programs; runs of at most tens of thousands of rounds. Rates and effects may change at larger scales.
- **Well-mixed instruments.** Both fitness assays and the parasite test run in well-mixed soups. Advantages or parasites that exist only in space are invisible to E-78, and spatial theory predicts that such advantages are the main ones (section 5).
- **Timescale.** The whole project ran over 11 days (5 to 15 November 2026). Single experiments ran for minutes to 16 hours. Nothing here speaks to long-term evolution.
- **Authorship.** AI agents (Claude) designed, ran and wrote up most of the work, with the owner setting goals and approving long runs. Five reviews were made by AI systems (three by ChatGPT, R-1 to R-3; an independent agent, R-4; Claude, R-5). No human domain expert has reviewed the work.
- **Literature review by AI agents only.** On 16 November 2026 AI agents compared our claims with published work ([Literature]({{ '/literature.html' | relative_url }}), J-091). It is not exhaustive: several key sources were closed, Google Scholar was not queried, and no human expert has checked it. By that review two of our results were already published and most others are partly known. "Not found in this search" is not a claim of novelty; we claim novelty only with respect to this project.

## 9. Related work

*This section summarises the [Literature]({{ '/literature.html' | relative_url }}) page: a review done by AI agents on 16 November 2026 (J-091), with a claim-by-claim table, reading depths and links. It is not exhaustive and no human expert has checked it. "Not found in this search" means only that; it is not a claim of novelty.*

- **Program soups.** Agüera y Arcas et al. (2024, [arXiv 2406.19108](https://arxiv.org/html/2406.19108)) showed that self-replicators emerge from random BFF programs and that plain SUBLEQ and RSUBLEQ4 make none; both results are theirs, and we reproduce them. They also report reversed and palindromic replicators, the role of head offsets, and a staged origin over several interactions. Knierim et al. (2026, [arXiv 2607.01483](https://arxiv.org/html/2607.01483)) time emergence per interaction, start heads 64 apart, describe self-inverting replicators and find replicators by mutation-only walks. Cicala et al. (2026, [arXiv 2607.09211](https://arxiv.org/html/2607.09211)) and Jha et al. (2026, [arXiv 2609.10817](https://arxiv.org/abs/2609.10817)) study Z80 soups. The authors' [cubff repository](https://github.com/paradigms-of-intelligence/cubff) holds unpublished tools close to our one-rate model and R<sub>P</sub>. Earlier spontaneous replicators: Coreworld (Rasmussen et al. 1990), Pargellis's Amoeba, Hutton's Squirm3 ([2002](https://faculty.cc.gatech.edu/~turk/bio_sim/articles/hutton_rep_molecules.pdf)), Greenbaum and Pargellis (2017), and AlChemy and its revisit ([Mathis et al. 2024](https://arxiv.org/html/2408.12137)); LaBar, Hintze and Adami ([2016](https://arxiv.org/abs/1511.07959)) followed spontaneously arising Avida replicators. Replicator density: Adami ([2015](https://ar5iv.arxiv.org/html/1409.0590)) and C G et al. ([2017](https://ar5iv.arxiv.org/html/1701.03993)).
- **After emergence.** Ray's Tierra (efficiency gains by shortening, parasites; [Tierra docs](https://tomray.me/pubs/tierra/node26.html)), Stringmol ([Hickinbotham et al. 2021](https://eprints.whiterose.ac.uk/176868/1/rsos.210441.pdf)), Lenski et al. ([2003](https://www.cs.princeton.edu/courses/archive/fall24/cos597C/bib/598-2017/adami03Nature.pdf)), and spatial replicator theory (Takeuchi and Hogeweg [2009](https://pmc.ncbi.nlm.nih.gov/articles/PMC2757730), [2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3466355); Kerr et al. 2006; Szabó et al. 2002).
- **Open-endedness measures.** Bedau and Packard's evolutionary activity with a neutral shadow ([Bedau et al. 1998](https://people.reed.edu/~mab/papers/alife6.pdf)); the MODES toolbox ([Dolson et al. 2019](https://par.nsf.gov/servlets/purl/10104628)); Taylor et al. ([2016](https://tim-taylor.com/paper-details/taylor2016openended.html)); Channon's claim that Geb passes Bedau's test. We computed none of these statistics.
- **Lenia.** Chan (2019, *Complex Systems* 28(3); arXiv 1812.05433), whose published random start is 15 to 39 dense patches in an empty world ([`LeniaND.py`](https://raw.githubusercontent.com/Chakazul/Lenia/master/Python/LeniaND.py)), not a full-grid soup (section 3 tests this start). Chan (2020, [arXiv 2005.03742](https://arxiv.org/abs/2005.03742)) reports self-replication as "not rare" in multi-channel Lenia. Structured starts: Reinke et al. (CPPN starts; white noise gives "dead or global patterns"), MaCE ([2025](https://arxiv.org/html/2507.12306)), Papadopoulos et al. ([2024](https://arxiv.org/html/2402.17848v2)) and Hudcová et al. ([2026](https://arxiv.org/html/2601.01932)). Other follow-ups: Asymptotic Lenia (Kawaguchi et al. 2021) and its "glider equation" (Kojima et al. 2025); Particle Lenia (Mordvintsev et al. 2022).
- **Flow-Lenia** (Plantec et al., ALIFE 2023, [arXiv 2212.07906](https://arxiv.org/abs/2212.07906); *Artificial Life* 31(2), 2025, [arXiv 2506.08569](https://arxiv.org/html/2506.08569)): mass conservation and parameter localization; reports dynamic patterns, including gyrating ones, as common, without counts. Our single-channel runs (E-16; J-016 from the paper's own patch) found no isolated translating structure; with no published rate and different settings, this is not comparable with their report, not a failed reproduction.
- **Life-like rules.** Eppstein ([2010](https://arxiv.org/abs/0911.2890)) separates what a rule supports from what random starts produce; the [Catagolue census](https://catagolue.hatsya.com/census/b3s23/C1) controls soup size and density by design. Earlier listed, not checked in the review: Wolfram's classes, Langton's λ, Zenil's compression-based classification, Sapin's evolutionary search for gliders.
- **Search and validation.** Diversity search: Reinke et al. ([2020](https://ar5iv.labs.arxiv.org/html/1908.06663)), Etcheverry et al. (NeurIPS 2020), Faldor and Cully ([2024](https://arxiv.org/html/2406.04235)), Hamon et al. ([2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577699/)); foundation-model search (Kumar and colleagues 2024). Validation lineage: Bedau's neutral shadow, Bullock and Bedau, Lohn and Reggia. AI-scientist pitfalls: Luo et al. ([2025](https://arxiv.org/abs/2509.08713)).
- **Reaction-diffusion reproducers:** Gray-Scott dividing spots (Pearson 1993), used here only as a control.

**Spontaneous emergence with nulls.** None of the eight Lenia-family works checked in the review (among them sensorimotor Lenia by Hamon et al., Leniabreeder, ASAL, the glider equation, Particle Lenia, Flow-Lenia 2025 and the phase-boundaries paper) measures spontaneous, within-run emergence with nulls: they search or optimise, and their random baselines are rates per random rule. Two non-Lenia preprints do claim spontaneous self-replication in cellular automata: Yin (2026, [arXiv 2603.25239](https://arxiv.org/html/2603.25239v1)) maps all 262,144 outer-totalistic Moore rules and adds a causal single-cell deletion tier, close in spirit to our knockouts, and Hintze and Bohm (2025, [arXiv 2508.08047](https://arxiv.org/html/2508.08047v1)) study one novelty-searched rule. Neither has a selection-aware null. So the likely contribution remains methodological, in a narrower form: detectors validated against controls built to fool them, causal claims tested on clones, controlled counterfactuals where the literature had a habit or an anecdote, and negative results reported.

## 10. Reproducibility

- **Code and tests.** `pip install -e '.[dev]'`, then `pytest` and `emergence benchmark --probes`. The same command, commit and seed give the same universes and soups (D-006); several soups were replayed bit for bit (E-41, E-47, E-75 phase 5).
- **Experiments.** The [Experiments]({{ '/experiments.html' | relative_url }}) page lists each experiment's exact command and code commit. Compact JSON exports are in `docs/data/experiments/`; `emergence reproduce` checks state hashes for the spatial families.
- **Pre-registrations.** `docs/data/e*-preregistration.md`, plus the E-75 design and protocols; each is committed before its run, and the journal gives the commit.
- **Not committed.** SQLite run databases (D-017) and soup caches and snapshots under `runs/` (for example `runs/e54/`, `runs/e66-partA.jsonl`, `runs/e70/`, `runs/e73/`, `runs/e75-*`, and `runs/e78/run/`, about 0.9 GB). They regenerate from the commands. The C interpreters compile on first use into `~/.cache/emergence-lab`.
- **Known gaps.** The first Lenia exploration (E-12 run 1) was lost with a cloud container and is not used. A power loss interrupted two E-54 soups, which were resumed from snapshots with new random streams (recorded in J-066).

## Appendix A: claims table

Sources are paths under `docs/`. "J-0xx" means the journal entry of that ID; JSON paths are given as file → key. Pre-registered: *yes* (the number is a registered outcome), *no* (exploratory or descriptive), *post hoc* (decided after seeing data). Unit: what one observation is.

| # | Claim | Value | Exp. / journal | Source | Pre-reg. | Unit |
|---|---|---|---|---|---|---|
| A1 | Benchmark checks, as last reported | 170 (39 + 131) | — | `research.md` O1; `index.md` | no | check |
| A2 | SUBLEQ family size | 16,416 rules | E-75 ph. 0, J-077 | `journal.md` J-077 | no | rule |
| A3 | Published anchors' random-program hits | 0 in 10⁷ each | E-75 ph. 1, J-078 | `data/experiments/2026-11-12-e75-census.json` → `anchors`, `nprog` | yes (protocol) | program |
| A4 | Longest single experiment | 15.8 h (15 h 48 min) on 11 workers | E-78, J-089 | `journal.md` J-089 | no | run |
| A5 | Soup-start Lenia worlds without a mover in search | 0 in 2,085 | E-12, J-013 | `journal.md` J-013 | no | world |
| A6 | Seed shapes in viability scan | 12 | E-13a, J-013, R-4 | `data/experiments/2026-11-07-e13a-glider-viability.json` → `seeds`; `reviews.md` R-4 | no | shape |
| A7 | Single-ring rules supporting a glider | 8 of 99 | E-13a, J-013 | `journal.md` J-013 | no | rule |
| A8 | Exploratory smooth vs soup | 18/240 vs 0/80 | E-13, J-014 | `journal.md` J-014 | yes (counts); test post hoc | world |
| A9 | Smallest attainable sign-test p with 8 rules | 0.0078 | E-13, J-014 | `journal.md` J-014 | yes | rule |
| A10 | E-14 density 0.10 | 28/160 vs 0/160, p = 1.0 × 10⁻⁹ | E-14, J-015 | `2026-11-07-e14-movers.json` → `fisher` | yes | world |
| A11 | E-14 density 0.35 | 21/160 vs 0/160, p = 2.4 × 10⁻⁷ | E-14, J-015 | `2026-11-07-e14-movers.json` → `fisher` | yes | world |
| A12 | E-14 registered α | 0.025 per contrast | E-14, J-015 | `2026-11-07-e14-movers.json` → `fisher.alpha_per_contrast` | yes | — |
| A13 | Gliders surviving 1,000 steps alone | all (51 of 51) | E-14, J-015 | `2026-11-07-e14-verify-movers.json`; `journal.md` J-015 | yes | object |
| A14 | E-14 rules making gliders; rule-level sign test | 6 of 8; p = 0.031 | E-14, J-015, R-4 | `journal.md` J-015; `reviews.md` R-4 | no (rule-level added after review) | rule |
| A15 | E-19a density 0.10 | 37 / 0 / 0 of 160 (smooth / shuffled / soup), p = 6.9 × 10⁻¹³ | E-19a, J-021 | `2026-11-07-e19-shuffled-null-and-soup-sweep.json` → `e19a.d0.1` | yes | world |
| A16 | E-19a density 0.35 | 11 / 0 / 0 of 160, p = 4.1 × 10⁻⁴ | E-19a, J-021 | same → `e19a.d0.35` | yes | world |
| A17 | E-19a rules higher/lower | 6/0 (p = 0.016); 5/0 (p = 0.031) | E-19a, J-021 | same → `rules_higher`, `sign_p` | yes | rule |
| A18 | Soup-start die / freeze densities | die < 0.18; blob fields > 0.24 | E-19b, J-021 | same → `e19b_soup_sweep` | yes | world |
| A19 | Soup-start glider worlds in sweep | 1 of 400, at density 0.20 | E-19b, J-021 | same → `e19b_soup_sweep` | yes | world |
| A20 | All soup-start worlds with a glider | 1 of 1,120 (E-13 80 + E-14 320 + E-19a 320 + E-19b 400) | J-021 | `journal.md` J-021 | no | world |
| A21 | Smooth-start glider share | 7 to 23% of worlds (11/160 to 37/160) | E-14, E-19a | A10, A11, A15, A16 | yes | world |
| A22 | Chan patches, 128 × 128 | 0 of 40 | E-13, J-014 | `journal.md` J-014 | yes | world |
| A23 | Chan patches, 256 × 256, 3,000 steps | 13/160 (8.1%), in 5 of 8 rules | E-24, J-029 | `2026-11-07-e24-chan-patches.json` → `verified_by_arm.patches`, `conditions_summary.per_rule` | yes | world (rule) |
| A24 | 110 patches; smooth ℓ = 3 | 0/160; 29/160 | E-24, J-029 | same → `verified_by_arm` | yes | world |
| A25 | Patch counts in Chan's start; in ours | 15 to 39 (`np.random.randint(15, 40)`), side int(0.9R), values in [0, 0.9); ours 15 to 40, side 12 | E-13, E-24, J-091 | `literature.md` (Chan's `LeniaND.py`, CODE); `emergence/engine.py` `patch_mask` | — | — |
| A26 | Wanderer, smooth vs soup | 36/40 vs 0/40 | E-18a, J-020 | `journal.md` J-020; `2026-11-07-e18-wanderer.json` | yes | world |
| A27 | Wanderer ridge | 7 of 42 rules; 0 of 252 soup-start worlds | E-18b, J-020 | `journal.md` J-020 | yes | rule / world |
| A28 | Ring glider | 13/40 and 18/40 smooth vs 0/40 soup at each density | E-26, J-031 | `journal.md` J-031 | yes | world |
| A29 | Blob field wins in big worlds | 23 of 30 worlds, 384 × 384 | E-15, J-017 | `journal.md` J-017; `2026-11-07-e15-glider-population.json` | no | world |
| A30 | Controlled collisions; births; fusions | 500; 0; 7 | E-20, J-023 | `journal.md` J-023 | yes | collision |
| A31 | Spontaneous double gliders | 1 genuine in 320 worlds | E-21, J-025 | `journal.md` J-025 | yes (outcome redefined, disclosed) | world |
| A32 | Double + glider collisions; triples | 312; 0 | E-23, J-027 | `journal.md` J-027 | yes | collision |
| A33 | Wanderer encounters ending with one | 142 of 200 (71%) | E-22, J-026 | `journal.md` J-026 | yes | encounter |
| A34 | Movers tested for reproduction | 0 of 285 | E-27/E-28, J-032 | `journal.md` J-032 | yes | object |
| A35 | Held-out worlds with a reproducer | 0 of 350 | E-28, J-032 | `journal.md` J-032 | yes | world |
| A36 | Single-channel lump scan | 0 reproducers; 1,453 of 3,000 rules decided | E-29, J-034 | `journal.md` J-034; `2026-11-07-e29-lump-scan.json` → `summary` | yes | rule |
| A37 | Flow-Lenia isolated translating structures (E-16: one channel, R = 13, 1 to 3 kernels; soup, smooth and Chan-patch starts) | 0 in 400 worlds | E-16, J-018 | `journal.md` J-018; `data/rule-panel-e16.txt`; `emergence/physics/flow_lenia.py` `FlowLenia.random` | no (plan) | world |
| A38 | Multi-channel reproducer rules | 1 of 1,000; 1 of 450 decided | E-32, J-037 | `journal.md` J-037; `2026-11-08-e32-mlenia-lumps.json` → `summary` | yes | rule |
| A39 | Rate vs single-channel | p = 0.24 | E-32, J-037 | `journal.md` J-037 | no (this Fisher test is not in the E-32 pre-registration, whose primary is a count; corrected in J-092) | rule |
| A40 | Life-like central patch effect | +1.35 types, p = 0.004 | E-09, J-009 | `journal.md` J-009; `2026-11-05-e09-initial-conditions.json` | outcomes fixed in advance | rule (paired) |
| A41 | At matched density | −0.08, p = 1 | E-10, J-009 | `journal.md` J-009; `2026-11-05-e10-density-matched.json` | outcomes fixed in advance | rule (paired) |
| A42 | E-14/E-19 world-level p values below | 10⁻³ | E-14, E-19a | A10, A11, A15, A16 | yes | world |
| A43 | BFF soups jumped by round 16,000 | 0 of 12 (prediction 2 to 6) | E-40, J-040 | `2026-11-08-e40-bff-soups.json` → `summary.bff` | yes | soup |
| A44 | BFF soup size in E-40/E-41 | 2¹⁴ programs | E-40 | `journal.md` J-040 | yes | — |
| A45 | Jumps by round 48,000 | 2 more of 12 | E-41, J-041 | `2026-11-08-e41-bff-longer.json` → `summary`; `journal.md` J-041 | yes | soup |
| A46 | Pilot jump round; total | 8,750; 3 of 16 soups | E-41, J-041 | `journal.md` J-041 | yes | soup |
| A47 | End scans of non-jumped soups with a replicator | 0 of 22 | E-41, J-041 | `journal.md` J-041 | yes | soup |
| A48 | Copy-all HOE without a replicator | 7.0 bits | E-40, J-040 | `journal.md` J-040 | yes (control) | soup |
| A49 | Size range | 2¹³ to 2¹⁶ programs | E-50, J-054 | `2026-11-08-e50-soup-size.json` → `analysis.arms` | yes | soup |
| A50 | Size exponent; events | β = 1.02 (0.11 to 2.02), p = 0.014; 9 events | E-50, J-054 | same → `analysis.fit` | yes | soup |
| A51 | Registered jumps that were zero waves | 3 | E-50, J-054 | `journal.md` J-054 | yes (found on inspection) | soup |
| A52 | Verified-only exponent | β = 0.93 (−0.17 to 2.15), p = 0.049 | E-50, J-054 | `2026-11-14-rate-model.json` → `step5_bff."verified replicator (D-045 reading)".beta_free`; `journal.md` J-054 | post hoc | soup |
| A53 | BFF one rate | 0.036 per 10⁸ pair runs (0.017 to 0.066); common-rate p = 0.16 | E-76, J-086 | `2026-11-14-rate-model.json` → `step5_bff."verified + E-54 new 2^16 soups"` | no | soup |
| A54 | Emergent replicators, all backward and mirror | 9 of 9 | E-46, J-046 | `journal.md` (E-46 entry, J-046) | post hoc observation, then tested | program |
| A55 | Short copiers, standard rule | 55 reverse, 0 forward | E-55, J-055 | `journal.md` J-055; `2026-11-08-e55-kernels.json` | yes | kernel |
| A56 | Kernel sizes in census | 1 to 6 instructions | E-55 | `journal.md` J-055 | yes | — |
| A57 | Short copiers, counterfactual (head 1 at byte 64) | 139 forward, 0 reverse | E-55, J-055 | same | yes | kernel |
| A58 | Smallest replicator | 10 instructions (standard) vs 5 | E-57, J-057 | `journal.md` J-057 | no (descriptive) | program |
| A59 | Counterfactual vs standard soups | 8/8 (rounds 250 to 1,750) vs 0/12 by 16,000; p = 8 × 10⁻⁶ | E-57, J-057 | `2026-11-08-e57-soups.json` → `summary` | yes | soup |
| A60 | Head-1-at-127 control | 2/16 vs 8/8, p = 6 × 10⁻⁵ | E-59, J-059 | `2026-11-08-e59-orientation-confirm.json` → `summary` | yes | soup |
| A61 | F definition: copier length | ≤ 6 instructions | E-60 | `journal.md` J-060 | yes | — |
| A62 | E-60 census size; rule level | 128 rules; F 3 of 3; others 2 of 4 with any jump (1 of 4 after J-061) | E-60, J-060, J-061 | `2026-11-08-e60-soups.json` → `results` (tallied by `h1`); `journal.md` J-061 | yes (soups); rule tally post hoc | rule |
| A63 | E-60 soups | 12/12 vs 2/16, p = 3 × 10⁻⁶ | E-60, J-060 | same → `summary` | yes | soup |
| A64 | E-62 rule level; soups | 7 of 7; 28/28 | E-62, J-063 | `journal.md` J-063 | yes | rule / soup |
| A65 | E-63 | outside rules 1 of 4; soups 1/16 vs 28/28, p = 7 × 10⁻¹¹; control 4/4 | E-63, J-064 | `2026-11-09-e63-outside.json` → `summary` | yes | rule / soup |
| A66 | E-64 rule level | F 3 of 3; C 1 of 4 | E-64, J-065 | `2026-11-09-e64-soups.json` → `results` (tallied) | rule tally post hoc | rule |
| A67 | E-64 rule family size; soups | 256 rules; 10/12 vs 1/16, p = 5 × 10⁻⁵ | E-64, J-065 | same → `summary` | yes | soup |
| A68 | E-65 rule level | F 7 of 7 (all ≥ 3 of 4); C 1 of 4 | E-65, J-067 | `2026-11-09-e65-soups.json` → `results` (tallied) | rule tally post hoc | rule |
| A69 | E-65 family size; soups | 768 rules; 26/28 vs 1/16, p = 9 × 10⁻⁹ | E-65, J-067 | same → `summary` | yes | soup |
| A70 | E-68 program lengths; soups | 16 to 128 bytes; 18/36 vs 6/36; length 16: 0/12 vs 0/12 | E-68, J-070 | `journal.md` J-070 | yes | soup |
| A71 | E-69 matched bytes | length 16: 4/12; length 32: 10/12; other 0/24 | E-69, J-071 | `journal.md` J-071 | yes | soup |
| A72 | E-70 rule level | F 15 of 15; other 6 of 15 with any jump | E-70, J-072 | `2026-11-09-e70-soups.json` → `results` (tallied by `h1`) | rule tally post hoc | rule |
| A73 | E-70 soups | 60/60 vs 15/60, p = 2 × 10⁻²⁰ | E-70, J-072 | same → `summary` | yes | soup |
| A74 | E-70 variants | five | E-70, D-051 | `journal.md` J-072 | yes | — |
| A75 | E-71 | 21 of 22 F rules jumped; soups 165/176; one F rule 0 of 8 | E-71, J-073 | `journal.md` J-073 | yes | rule / soup |
| A76 | E-74 | 24 of 24 F rules; soups 143/144 | E-74, J-076 | `2026-11-12-e74-soups.json` → `summary`; `journal.md` J-076 | yes | rule / soup |
| A77 | Copier count vs speed (exploratory) | ρ = −0.80 over 15 rules | E-70, J-072 | `2026-11-09-e70-soups.json` → `summary.secondary_selfsufficient_vs_medianT` | no | rule |
| A78 | Within / pooled across variants | p = 0.006 / p = 0.06 | E-71, J-073 | `journal.md` J-073 | yes | rule |
| A79 | Five-generation predictor after re-score | tenfold, p = 0.06 | E-73, J-075 | `journal.md` J-075 | yes (re-score) | rule |
| A80 | E-74 timing ratios | 0.66 to 0.95 | E-74, J-076 | `2026-11-12-e74-soups.json` → `summary.{d050,d053,hoe}.ratio` | yes | rule |
| A81 | Timings differing by > 1,000 rounds | 24 of 144 soups | E-74, J-076 | `journal.md` J-076 | no | soup |
| A82 | Inheritance test parameters | ≥ 4-byte block, 5 generations | E-75 ph. 0, D-055 | `decisions.md` D-055 | no (depth by sweep) | — |
| A83 | Emergent loop: whole-program vs inheritance | 0/40 vs 39/40 | E-75 ph. 0, J-077 | `journal.md` J-077 | no | program |
| A84 | Loop size | 5 bytes | E-75 ph. 0, J-077 | `journal.md` J-077 | no | — |
| A85 | Phase 1 classes | 600 rules: 32 F, 100 C, 468 none | E-75 ph. 1, J-078 | `2026-11-12-e75-census.json` → `summary.classes` | yes (protocol) | rule |
| A86 | F rules' knobs | all 4 operands, step ±1 | E-75 ph. 1, J-078 | same → `summary.by_n`, `by_s` | yes (protocol) | rule |
| A87 | Stability check | 37 of 40 (failed) | E-75 ph. 1, J-078 | same → `summary.stability` | yes | rule |
| A88 | Phase 2 pilot | F 8/8; C 4/8 | E-75 ph. 2, J-079 | `2026-11-12-e75-pilot.json` → `summary` | protocol (pilot) | soup |
| A89 | Phase 3 | rules 11/12 vs 1/12, p = 5.4 × 10⁻⁵; soups 64/72 vs 6/72 | E-75 ph. 3, J-080, J-086 | `2026-11-14-rate-model.json` → `step4_rule_level."phase 3"`; `2026-11-13-e75-phase3.json` → `summary.primary` | yes (soup); rule-level post hoc | rule / soup |
| A90 | Phase 4 pool A | rules 6/12 vs 5/12, p = 0.50; soups 29/72 vs 20/72, p = 0.08 | E-75 ph. 4, J-081, J-086 | `2026-11-14-rate-model.json` → `step4_rule_level."phase 4 pool A"`; `2026-11-13-e75-phase4.json` → `summary.A` | yes (soup); rule-level post hoc | rule / soup |
| A91 | Phase 5 rarely-jumping soups with no origin | 53 of 54 in 4,000 rounds | E-75 ph. 5, J-083 | `journal.md` J-083 | yes | soup |
| A92 | Establishment after first origin | median 16.5 rounds | E-75 ph. 5, J-083 | `journal.md` J-083 | yes | soup |
| A93 | Founders by partner / self | 24 / 16 | E-75 ph. 5, J-083 | `journal.md` J-083 | yes | founder |
| A94 | Phase 6 primary | ρ = 0.64, p = 4 × 10⁻⁴ | E-75 ph. 6, J-084 | `journal.md` J-084 | yes | rule |
| A95 | Zero-product rules still jumping | 35 of 222 soups | E-75 ph. 6, J-084 | `journal.md` J-084 | yes | soup |
| A96 | Phase 7 | rules 6/7 vs 2/12, p = 0.006; soups 33/42 vs 12/72 | E-75 ph. 7, J-085, J-086 | `2026-11-14-rate-model.json` → `step4_rule_level."phase 7"`; `journal.md` J-085 | yes (soup); rule-level post hoc | rule / soup |
| A97 | Phase 7 HIGH rules needed / found | 8 / 7 | E-75 ph. 7, J-085 | `journal.md` J-085 | yes | rule |
| A98 | Phase 7 rules; D_T vs R_P | 19; ρ = 0.75 vs 0.67 | E-75 ph. 7, J-085 | `journal.md` J-085 | no | rule |
| A99 | Mean CV of jump times | 0.77 observed vs 0.79 expected | E-76, J-086 | `2026-11-14-rate-model.json` → `step2_fit.cv_full_rules` | no | rule |
| A100 | Rules in 5% tails | 8 of 26 vs 2.6 expected, p = 0.003 | E-76, J-086 | same | no | rule |
| A101 | Soup / fresh-pair ratio, "always", first 500 rounds | 1.00 (0.69 to 1.38) | E-76, J-086 | `journal.md` J-086; same file → `step3_aging.by_condition` | no | rule |
| A102 | Ratio, "≤ 0", all rounds | 6.9 (4.8 to 10.0) | E-76, J-086 | same → `step3_aging.by_condition."<=0"` | no | rule |
| A103 | No rise with age under "≤ 0" | p = 0.48 | E-76, J-086 | `journal.md` J-086 | no | rule |
| A104 | Ratio, "< 0" | 0.66 (0.46 to 0.91) | E-76, J-086 | same → `step3_aging.by_condition."<0"` | no | rule |
| A105 | BFF vs jumping SUBLEQ rates | 10 to 1,000 times lower | E-76, J-086 | `journal.md` J-086 | no | rule |
| A106 | Rules in E-76 figure; rules at one point | 79; 37 | E-76, J-086 | `2026-11-14-rate-model.json` → `step1`; figure annotation | no | rule |
| A107 | Heredity | 9 of 9 replicators | E-42, J-042 | `2026-11-08-e42-bff-heredity.json` → `summary` | yes | program |
| A108 | Viable mutants carried by ≥ 60% | 140 of 141 | E-42, J-042 | `journal.md` J-042 | yes | mutant |
| A109 | One-byte variants differing | 2 of 141; null 0 of 24; p = 0.73 | E-43, J-043 | `2026-11-08-e43-bff-selection.json` → `summary`; `journal.md` J-043 | yes | pair |
| A110 | Cross-soup pairs differing | 0 of 36 | E-44, J-044 | `journal.md` J-044 | yes | pair |
| A111 | Soup 5006 species vs soup 901 | 176/252 (69.8%), p = 1.3 × 10⁻¹⁰ | E-46, J-046 | `2026-11-08-e46-species-contests.json` → `summary.o1_mirror_vs_901` | yes | race |
| A112 | Hand-written advantage before / after fair counting | 77% (222/287) → 56% (286/510) | E-44, E-46 | `journal.md` J-044; `2026-11-08-e46-species-contests.json` → `summary.o2_handwritten_vs_emergent` | yes | race |
| A113 | Most common family's share after a jump | median about 2% (2.2 to 2.4%) | E-47, J-047 | `journal.md` J-047 | yes (descriptive) | snapshot |
| A114 | Late vs early races | p = 0.07 (E-48); p = 0.33 (E-49) | E-48, E-49 | `journal.md` J-048, J-049 | yes | program pair / program |
| A115 | Growth-rate trend | p = 0.38 | E-51, J-051 | `journal.md` J-051 | yes | program |
| A116 | Invasion, own-time backgrounds | p = 0.045 | E-52, J-052 | `journal.md` J-052 | yes | soup × background |
| A117 | Invasion, kin-free | p = 0.88 | E-53, J-053 | `journal.md` J-053 | yes | soup × background |
| A118 | Long soups | 7 soups; 16,000-round gap; D = −0.15, p = 0.64 | E-54, J-066 | `2026-11-08-e54-long-soups.json` → `summary.primary` | yes | soup |
| A119 | E-54 single-test replicator share | 22 to 78% | E-54, J-066 | same → `summary.replicator_share_top40` | no (descriptive; corrected) | program |
| A120 | Self-copiers with 10 repeats | 99.8% of 2,800 | E-66, J-068 | `2026-11-09-e66-parasites.json` → `summary.P2` | yes | program |
| A121 | Parasites among rarer programs | 0 of 420 | E-67, J-069 | `2026-11-09-e67-rare.json` → `summary.P1` | yes | program |
| A122 | E-78 design | 7 soups; 3 arms; 20,000 rounds; 256 × 256 torus | E-78, J-089, D-065 | `2026-11-15-e78-spatial.json` → `summary.settings`; `decisions.md` D-065 | yes | soup |
| A123 | E-78 primary | mean d = −0.42 (−1.10 to 0.25); p = 0.91; bound 0.28 | E-78, J-089 | same → `summary.primary.test` (`mean_d`, `ci95_mean_d`, `p_one_sided`); `settings.DELTA_STAR` | yes | soup |
| A124 | E-78 seed null | M′ below M in 7 of 7; p = 0.016 | E-78, J-089 | same → `summary.primary.test` (`null_d`, `p_null_two_sided`) | yes | soup |
| A125 | Neighbour pairs ≥ 90% identical in S | about 55% | E-78, J-089 | `journal.md` J-089; `2026-11-15-e78-explore.json` | post hoc | neighbour pair |
| A126 | Largest family in S | 0.2 to 0.4% of the soup | E-78, J-089 | `journal.md` J-089 | post hoc | soup |
| A127 | Max soup size studied | 2¹⁶ programs (E-54, E-78) | E-54, E-78 | `journal.md` J-066 | yes | soup |
| A128 | Gap after jump studied | up to 20,000 rounds | E-54, E-78 | `journal.md` J-066, J-089 | yes | soup |
| A129 | Life-like knockouts vs placebo | P = 0.49 to 0.51 over 92 tests | E-10, E-11, J-010 | `journal.md` J-010 | outcomes fixed in advance | knockout |
| A130 | H1 first test | 2 seeds; 1.9× and 4.2× after deduplication | E-03 to E-06, J-004 | `experiments.md` E-03 to E-06 table; `journal.md` J-004 | no | seed |
| A131 | H1 repeat | 20 paired seeds; 1.84× (1.70 to 2.25); 20 of 20; p = 9.5 × 10⁻⁷ | E-77, J-087 | `2026-11-14-e77-h1-power.json` → `tests.distinct_self_propelled` | yes | seed |
| A132 | H1 complex on every seed | 3.4 (2.6 to 3.9) | E-77, J-087 | same → `tests.distinct_complex_all_seeds` | yes | seed |
| A133 | Lenia engine vs random in glider island | 59 vs 9 of 500 rules | E-13a, J-013 | `journal.md` J-013 | no | rule |
| A134 | Static blobs labelled complex | 27 of 60 rules | J-012 | `journal.md` J-012 | no | rule |
| A135 | Birth detector v1 false reproducers | 2 | E-27, J-032 | `journal.md` J-032 | yes (inspection) | object |
| A136 | Fed worlds with false reproducers | 17 of 100 | E-30, J-035 | `journal.md` J-035 | yes | world |
| A137 | Missed sloppy copies; smears accepted by old test | 59 to 60 of 64 bytes; 37 of 64 | E-72, E-73, J-074, J-075 | `journal.md` J-074, J-075 | yes (controls) | program |
| A138 | HOE in a soup scored "no jump" | 6.4 | E-72, J-074 | `journal.md` J-074 | no | soup |
| A139 | Copy-test thresholds | 60 of 64 (old); 58 of 64 with guard (new) | D-050, D-053 | `decisions.md` D-053 | yes | — |
| A140 | All-zero replicator: jump calls rechecked | 7 soups | E-75 ph. 5, J-083 | `journal.md` J-083 | no | soup |
| A141 | Soup-level p values too small by | 10⁵ to 10¹⁹ | E-76, J-086 | `journal.md` J-086 | no | — |
| A142 | Jump persistence requirement | 3 checkpoints | D-045 | `decisions.md` D-045 | — | — |
| A143 | Experiments with a pre-registered primary, scored | 45 in the first version; 44 after re-reading the pre-registrations (E-75 phase 5 registered no primary) | Appendix B, E-79 | this page, Appendix B; `data/e79-primaries.json` → record `E-75 ph. 5` | — | experiment |
| A144 | Lenia rule panel | 8 rules | E-13 to E-24 | `data/rule-panel-e13.txt` | yes | rule |
| A145 | Level-5 test sizes | 3 to 7 soups | E-48 to E-54, E-78 | `journal.md` J-048 to J-066, J-089 | yes | soup |
| A146 | F rules per test | 3 to 15 | E-60 to E-70 | A62 to A72 | yes | rule |
| A147 | Quasi-static cut-off set on | 60 rules | J-012, D-022 | `journal.md` J-012 | post hoc | rule |
| A148 | Tile thresholds fitted on | 8 pilot rules | E-75 ph. 3, J-080 | `journal.md` J-080 | post hoc | rule |
| A149 | World and soup scales | 96 to 384 cells per side; 2¹³ to 2¹⁷ programs | all | E-03 to E-06 (96), E-15 (384), E-50 (2¹³), E-69 (2¹⁷) | — | — |
| A150 | Project span; experiment durations | 11 days (5 to 15 Nov 2026); minutes to 16 h | J-001 to J-089 | `journal.md` dates; J-089 | — | — |
| A151 | Reviews | five (R-1 to R-5) | — | `reviews.md` | — | — |
| A152 | Uncommitted E-78 snapshots | about 0.9 GB | E-78 | `handoff.md` open problems | — | — |
| A153 | Soups interrupted by power loss in E-54 | 2 | E-54, J-066 | `journal.md` J-066 | deviation recorded | soup |
| A154 | BFF program and tape size | 64-byte programs; 128-byte joined tape | D-040, J-040 | `journal.md` J-040, J-055 | — | — |
| A155 | Lenia state quantisation | 256 levels | J-011 | `journal.md` J-011 | — | — |
| A156 | Figure 3 snapshot | 1,000 rounds after the jump | E-41, J-041 | `report.md` figure caption; `journal.md` J-041 (detector 1,000 epochs after) | yes | soup |
| A157 | Fitness measures with no later advantage | four (races, growth rate, invasion, kin-free invasion) | E-48 to E-54 | `research.md` O5; `journal.md` J-053 | yes | — |
| A158 | Flow-Lenia from the paper's centred 40 × 40 patch (float rules) | 0 self-propelled in 80 rules (20 each with 3, 5, 10 kernels at R = 13; 20 with 10 kernels, R in [8, 25]) | J-016 | `journal.md` J-016 | no (validation) | rule |
| A159 | Plantec et al.: start and R range | centred 40 × 40 uniform patch; R in [2, 25]; no mover counts | J-091 | `literature.md` (Plantec et al. 2023, 2025, FULL) | — | — |
| A160 | BFF rate arithmetic (review, not a result) | 0.38 expected events, P ≈ 0.32, vs their 40% | J-091 | `literature.md` (Agüera y Arcas et al. 2024, FULL; our rate A53) | no (review arithmetic) | — |
| A161 | Background mutation rate, ours and theirs | 0.00024 per byte per round = 0.024% | J-091 | `emergence/programs/bff.py` (`mutation`); `literature.md` | — | — |
| A162 | Tierra efficiency gain | 80 → 22 instructions, 839 → 146 cycles, 5.75-fold | J-091 | `literature.md` (Ray, Tierra docs, FULL) | — | — |
| A163 | Hamon et al. guided vs random | 486 of 1,600 vs 30 of 117,000 moving stable solitons | J-091 | `literature.md` (Hamon et al. 2025, FULL partial) | — | — |
| A164 | B3 rules with spaceships | 10,736 of 16,384 (65.5%) | J-091 | `literature.md` (Eppstein 2010, FULL) | — | — |
| A165 | Largest 64-byte BFF soups measured | 2¹⁶ programs (2¹⁷ only at 16 bytes, E-69) | E-54, E-69, E-76 | `journal.md` J-066, J-071 | — | soup |
| A166 | Registered primary p values in the Holm family; primaries excluded (not significance tests or not computed); predicted-null tests listed apart | 42; 15; 8 | E-79, J-092 | `data/experiments/2026-11-16-e79-holm.json` → `m`, `excluded`, `predicted_null` | yes (E-79) | primary |
| A167 | Tests meeting their registered α; passes (verdict met) | 22; 20 | E-79 | same → `summary.primary_holm_and_bh` (`tests_meeting_registered_alpha`, `original_passes`) | yes (E-79) | primary |
| A168 | Passes surviving Holm (α 0.05); significant tests surviving BH (q 0.05) | 18 of 20; 22 of 22 | E-79 | same → `passes_surviving_holm`, `bh_significant` | yes (E-79) | primary |
| A169 | Passes losing significance under Holm (adjusted p) | E-50 (0.30), E-71 primary 2 (0.13); also E-68's Fisher test (0.062, verdict already fail) | E-79 | same → `table[].holm` | yes (E-79) | primary |
| A170 | E-14 world-level tests after Holm | 3.6 × 10⁻⁸ and 7.8 × 10⁻⁶ | E-79 | same → `table[id = E-14/d0.10, E-14/d0.35].holm` | yes (E-79) | world |
| A171 | E-19a world-level tests after Holm | 2.7 × 10⁻¹¹ and 0.010 | E-79 | same → `table[id = E-19a/…].holm` | yes (E-79) | world |
| A172 | Lenia rule-level sign tests after Holm (sensitivity a) | E-14 0.71, 0.71; E-19a 0.39, 0.71 | E-79 | same → `sensitivity_a_rule_level.rows` | yes (sensitivity) | rule |
| A173 | Passes surviving with rule-level p values (sensitivity a; D-063) | 14 of 20 | E-79 | same → `sensitivity_a_rule_level.counts` | yes (sensitivity) | primary |
| A174 | Holm within each thread: passes lost | E-50 only (adjusted 0.085); E-71 primary 2 survives (0.042) | E-79 | same → `sensitivity_b_within_thread` | yes (sensitivity) | primary |
| A175 | F-predictor rule-level Fisher, recomputed from the tallies | E-60 0.29, E-61 0.21, E-63 0.024, E-64 0.11, E-65 0.024, E-70 3.5 × 10⁻⁴; after Holm only E-70 survives (0.012) | E-79 | same → `sensitivity_c_rule_level_recomputed` | exploratory | rule |
| A176 | Passes surviving sensitivity (c) | 9 of 20 | E-79 | same → `sensitivity_c_rule_level_recomputed.counts` | exploratory | primary |
| A177 | E-75 phase 6 after Holm | 0.010 (registered α 0.01); exact p recomputed 4.14 × 10⁻⁴ | E-79 | same → `table[id = E-75 ph. 6]`; `data/e79-primaries.json` → `precise_value` | yes (E-79) | rule |
| A178 | E-75 phase 7 rule-level p with the registered definition (≥ 4 of 6 soups); after Holm | 0.029; 0.70 | E-76, E-79 | `2026-11-14-rate-model.json` → `step4_rule_level."phase 7".ge4_of_6`; E-79 → `sensitivity_a_rule_level` | post hoc (rule level) | rule |
| A179 | E-75 phase 7 soup-level test after Holm | 2.3 × 10⁻⁹ | E-79 | E-79 → `table[id = E-75 ph. 7].holm` | yes (E-79) | soup |
| A180 | E-50 and E-71 primary 2 after Holm | 0.30; 0.13 | E-79 | same → `table[].holm` | yes (E-79) | soup / rule |

## Appendix B: pre-registered primaries scorecard

First compiled from the journal's own wording for each experiment (J-014 to J-089). For E-79 (J-092) every pre-registration file was re-read; rows marked † were corrected where the journal wording disagreed with the file, and the original wording is kept in J-092. "Met" means the registered test reached its criterion for the effect it tested; for tests whose hypothesis was a null (for example "later code is fitter", predicted not significant), "not met" is the predicted outcome. Experiments with only a descriptive count, a pilot, a protocol or a re-score are listed separately and not tallied.

| Exp. | Registered primary | Result |
|---|---|---|
| E-13 † | sign tests across the 8 rules, each start (smooth ℓ = 3, 6, 10; spots; patches) vs soup at two densities, p < 0.05/20 | not met (design could not reach its threshold) |
| E-14 | smooth vs soup, two universe-level Fisher tests | met |
| E-18 | wanderer rule, smooth ℓ = 6 vs soup | met |
| E-19 | smooth vs shuffled, two densities | met |
| E-26 | ring-glider rule, smooth vs soup | met |
| E-41 | replay and detector confirmation of jumps | met |
| E-42 | heredity in ≥ 7 of 9 replicators | met |
| E-43 † | share of variant pairs with a favoured verdict vs a neutral null, one-sided Fisher p < 0.05 (prediction: parent favoured in 5 to 30%) | not met |
| E-44 † | share of cross-soup pairs favoured vs pooled nulls, one-sided Fisher p < 0.05 (prediction: ≥ 30%) | not met |
| E-45 † | mirror species' share of races vs 1/2, one-sided binomial p < 0.01 (prediction: ≥ 0.6) | met |
| E-46 † | with fair counting: (1) mirror species vs soup 901, (2) hand-written vs emergent, (3) emergent pairs vs nulls; all predicted null | mixed (1 and 2 met, against their predicted null; 3 not met, as predicted) |
| E-47 | dominant-species replacements | not testable (0 replacements) |
| E-48 | later ahead in ≥ 60% of pairs, p < 0.01 | not met |
| E-49 | same, verified replicators | not met |
| E-50 | rate rises with soup size | met |
| E-51 | growth-rate trend with time | not met (predicted) |
| E-52 | later code invades better (predicted not significant) | met (later explained by kinship) |
| E-53 | same in kin-free backgrounds | not met (predicted) |
| E-54 | later replicators fitter, kin-free invasion | not met (predicted) |
| E-55 | backward vs forward short copiers by rule | met |
| E-56 | counterfactual soups evolve forward copiers | met |
| E-57 | A: counterfactual speed-up; B: ≥ 90% of counterfactual copiers self-sufficient | mixed (A met, B not) |
| E-58 † | A: control rule slow (HOE criterion), Fisher p < 0.01; B: census, copiers ≥ 90% reverse and ≤ 5% self-sufficient | mixed (A not met, criterion misfired; B met) |
| E-59 | head-1-at-127 slower than 64 | met |
| E-60 | F vs S rules | met |
| E-61 | shift-aware F′ band; F′ soups jump | met |
| E-62 | lineage persistence separates rules | not met |
| E-63 | rules just outside F′ slow | met |
| E-64 | F vs C in a new family | met |
| E-65 | all F rules fast, C not | met |
| E-66 † | P1 (the only primary): ≥ 60% of single-test non-replicators grow in a repeated test | met (P2, P3 also right; P4 wrong) |
| E-67 | no parasites among rarer programs | met |
| E-68 | P1 census band; P2 soups | mixed (P1 met, P2 not) |
| E-69 | soup size vs length | undecided |
| E-70 | P1 census band; P2 soups | met |
| E-71 | P1 pooled; P2 within variant | mixed (P1 not, P2 met) |
| E-72 | shallow rules ≥ 3× slower | not met |
| E-74 | same, fresh rules, two timings | not met |
| E-75 ph. 3 † | tile density separates soups (HIGH ≥ 75%, LOW ≤ 25%, Fisher over soups p < 0.01) | met |
| E-75 ph. 4 | tile density transfers to jump ≤ 0 | not met |
| E-75 ph. 6 | R<sub>P</sub> predicts jumps in pool A | met |
| E-75 ph. 7 | rules chosen by R<sub>P</sub> jump | undecided (too few HIGH rules) |
| E-77 | engine beats random at 20 seeds | met |
| E-78 | neighbour-only late code fitter | not met |

**Tally (44 experiments, after the J-092 re-reading):** met 23; not met 13 (for 3 of these, E-51, E-53 and E-54, not meeting the criterion was the predicted outcome; E-13 failed by a design error); mixed 5; undecided 2; not testable 1. The first version tallied 45 (met 23, not met 14, mixed 4, undecided 2, not testable 2); the differences are E-46 (met → mixed), E-58 (not met → mixed), E-66 (mixed → met) and E-75 phase 5, whose pre-registration states that it has no single primary verdict, now listed below.

Not tallied (descriptive counts, pilots, protocols or re-scores, though pre-registered or protocol-led): E-17, E-20 to E-25, E-27 to E-32, E-40, E-73, E-75 phases 1, 2 and 5. (E-75 phase 5's origin-rate prediction was tested and right, p = 3 × 10⁻¹⁹; its establishment prediction was uninformative; J-083.) Of these, the journal records a stated prediction as wrong for E-24, E-30 (as first scored), E-32 and E-40, and as right for E-29 and E-31.

## Appendix B2: Holm correction across the primaries (E-79)

Pre-registered before any adjusted value was computed (`docs/data/e79-preregistration.md`, commit `341ff62`; D-067); script `scripts/holm_primaries.py`; data `docs/data/e79-primaries.json` (each p value with its source file and line) and `docs/data/experiments/2026-11-16-e79-holm.json`. The family is every registered primary of the experiments above that is a significance test of a predicted effect: 42 p values. Raw p is the value reported at the time for the registered test. Holm and BH are adjusted over all 42. "Survives" means the original verdict was a pass and the Holm-adjusted p ≤ 0.05. The last column is sensitivity (a): the committed rule-level p value and its Holm-adjusted value, where the registered unit was the world or soup (D-063).

| Primary | Unit | Raw p | Reg. α | Verdict | Holm | BH | Survives Holm | Rule level (a) |
|---|---|---|---|---|---|---|---|---|
| E-75 ph. 3, tile density, jump always | soup | 1.3 × 10⁻²⁴ | 0.01 | met | 5.7 × 10⁻²³ | 5.7 × 10⁻²³ | yes | 5.4 × 10⁻⁵ → 0.002 |
| E-70, instruction variants, F vs non-F | soup | 2.4 × 10⁻²⁰ | 0.01 | met | 9.7 × 10⁻¹⁹ | 5.0 × 10⁻¹⁹ | yes | — |
| E-18a, wanderer rule, smooth vs soup | world | 1.3 × 10⁻¹⁸ | 0.05 | met | 5.1 × 10⁻¹⁷ | 1.8 × 10⁻¹⁷ | yes | (one rule) |
| E-19a, smooth vs shuffled, density 0.10 | world | 6.9 × 10⁻¹³ | 0.025 | met | 2.7 × 10⁻¹¹ | 7.2 × 10⁻¹² | yes | 0.016 → 0.39 |
| E-75 ph. 7, product rate, prospective | soup | 6 × 10⁻¹¹ ‡ | 0.001 | undecided | 2.3 × 10⁻⁹ | 4.9 × 10⁻¹⁰ | test yes (verdict undecided) | 0.029 → 0.70 |
| E-63, just outside F′ | soup | 7.0 × 10⁻¹¹ | 0.01 | met | 2.6 × 10⁻⁹ | 4.9 × 10⁻¹⁰ | yes | — |
| E-45, mirror species vs soup 901 | race | 3.6 × 10⁻¹⁰ | 0.01 | met | 1.3 × 10⁻⁸ | 2.2 × 10⁻⁹ | yes | — |
| E-14, smooth vs soup, density 0.10 | world | 1.0 × 10⁻⁹ | 0.025 | met | 3.6 × 10⁻⁸ | 5.4 × 10⁻⁹ | yes | 0.031 → 0.71 |
| E-65, all F rules, two-head family | soup | 8.9 × 10⁻⁹ | 0.01 | met | 3.0 × 10⁻⁷ | 4.1 × 10⁻⁸ | yes | — |
| E-14, smooth vs soup, density 0.35 | world | 2.4 × 10⁻⁷ | 0.025 | met | 7.8 × 10⁻⁶ | 9.7 × 10⁻⁷ | yes | 0.031 → 0.71 |
| E-61 primary 2, new F′ rules vs E-60's S rules | soup | 2.5 × 10⁻⁷ | 0.01 | met | 8.1 × 10⁻⁶ | 9.7 × 10⁻⁷ | yes | — |
| E-77, engine vs random search (H1) | seed | 9.5 × 10⁻⁷ | 0.01 | met | 3.0 × 10⁻⁵ | 3.3 × 10⁻⁶ | yes | (seed unit) |
| E-60, F vs S rules, head-start family | soup | 3.0 × 10⁻⁶ | 0.01 | met | 9.0 × 10⁻⁵ | 9.7 × 10⁻⁶ | yes | — |
| E-57 primary A, counterfactual vs standard | soup | 7.9 × 10⁻⁶ | 0.01 | met | 2.3 × 10⁻⁴ | 2.4 × 10⁻⁵ | yes | (one rule per arm) |
| E-26, ring-glider rule, smooth vs soup | world | 3.8 × 10⁻⁵ | 0.05 | met | 0.0011 | 1.1 × 10⁻⁴ | yes | (one rule) |
| E-64, F vs C, two-head family | soup | 5.0 × 10⁻⁵ | 0.01 | met | 0.0013 | 1.3 × 10⁻⁴ | yes | — |
| E-59, head 1 at 127 vs 64 | soup | 6.1 × 10⁻⁵ | 0.01 | met | 0.0016 | 1.5 × 10⁻⁴ | yes | (one rule per arm) |
| E-75 ph. 6, product rate, pool A | rule | 4 × 10⁻⁴ ‡ | 0.01 | met | 0.010 | 9.0 × 10⁻⁴ | yes (not below its own α) | (rule unit) |
| E-19a, smooth vs shuffled, density 0.35 | world | 4.1 × 10⁻⁴ | 0.025 | met | 0.010 | 9.0 × 10⁻⁴ | yes | 0.031 → 0.71 |
| E-68 primary 2, program length, F vs non-F | soup | 0.0027 | 0.01 | not met (share < 75%) | 0.062 | 0.0057 | test no (verdict fail) | — |
| E-71 primary 2, copier count within variant | rule | 0.0060 | 0.05 | met | 0.13 | 0.012 | **no** | (rule unit) |
| E-50, jump rate vs soup size | soup | 0.014 | 0.05 | met | 0.30 | 0.027 | **no** | (one rule) |
| E-71 primary 1, copier count pooled | rule | 0.060 | 0.01 | not met | 1 | 0.11 | — | |
| E-48, late vs early races | program pair | 0.074 | 0.01 | not met | 1 | 0.13 | — | |
| E-75 ph. 4, tile density, jump ≤ 0 | soup | 0.080 | 0.01 | not met | 1 | 0.13 | — | 0.33 → 1 |
| E-58 primary A, head 1 at 127 (HOE criterion) | soup | 0.10 | 0.01 | not met | 1 | 0.16 | — | |
| E-49, late vs early, verified replicators | program | 0.33 | 0.01 | not met | 1 | 0.47 | — | |
| E-72, deep vs shallow | rule | 0.58 | 0.01 | not met | 1 | 0.79 | — | |
| E-74, deep vs shallow, fresh rules (max of D-053 0.18 and HOE 0.73) | rule | 0.73 | 0.01 | not met | 1 | 0.93 | — | |
| E-43, one-byte variants vs neutral null | variant pair | 0.73 ‡ | 0.05 | not met | 1 | 0.93 | — | |
| E-78, neighbour-only vs well mixed | soup | 0.91 | 0.05 | not met | 1 | 1 | — | |
| E-44, cross-soup pairs vs nulls | replicator pair | 1 | 0.05 | not met | 1 | 1 | — | |
| E-62 primary 2, lineage persistence | soup | 1 | 0.05 | not met | 1 | 1 | — | |
| E-13, 9 sign tests (smooth ℓ = 3 at 0.10 lowest) | rule | 0.0625 to 1 | 0.0025 | not met | 1 | 0.11 to 1 | — | |

‡ Reported rounded; used as reported. E-43's 0.73 recomputes from the committed counts as 0.729; phase 6's exact value recomputes as 4.14 × 10⁻⁴ (Holm 0.0103); phase 7's committed value is 5.8 × 10⁻¹¹. No p value in the family was reported only as a bound.

**Counts.** Of 42 tests, 22 met their registered α and 20 were passes. Holm keeps 18 passes (and phase 7's test); BH keeps all 22. Sensitivity (a), rule-level p values where committed: 14 passes survive. Sensitivity (b), Holm within each thread: only E-50 is lost (0.085). Sensitivity (c), exploratory, adding rule-level Fisher tests recomputed for the F predictor (E-60 0.29, E-61 0.21, E-62 1, E-63 0.024, E-64 0.11, E-65 0.024, E-68 0.32, E-70 3.5 × 10⁻⁴): 9 passes survive (E-18a, E-26, E-45, E-57, E-59, E-70, E-75 phases 3 and 6, E-77).

**Outside the family.** Not significance tests (15): E-41 (replay check; count of jumps), E-42 (count of heredity verdicts), E-55 and E-56 (census counts, shares), E-57 B, E-58 B, E-61 P1, E-62 P1, E-68 P1, E-70 P1 (census thresholds or bands), E-66 P1 and E-67 P1 (shares, counts), E-69 (thresholds), E-47 (registered sign test never computed: 0 replacements; not recoverable), E-75 phase 5 (no primary registered). Predicted null (8), listed apart: E-46 outcomes 1 (p = 1.3 × 10⁻¹⁰), 2 (0.0034) and 3 (0.15); E-51 (0.38); E-52 (0.045); E-53 (0.88); E-54 (0.64); E-78's seed-null contrast (0.016, which had to be non-significant for a pass).
