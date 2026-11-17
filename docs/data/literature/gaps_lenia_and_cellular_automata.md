# Gaps left by the first literature pass: Lenia-family and Life-like CA (initial conditions, spontaneous rates, controls)

Compiled 16 Nov 2026. This builds on `lenia_and_starting_conditions.md` and `search_methods_and_validation.md` and does not repeat what they cover. Each finding is tagged with how much of the source was read:

- **[full text]**: the full PDF or HTML text, either extracted by me (pdftotext) or read and summarised by the fetch tool. Most HTML reads went through a summarising fetch model, so exact quotes from those are as returned by that tool.
- **[code]**: repository source.
- **[abstract]**: the abstract only.
- **[secondary]**: a search-engine summary or a second-hand citation.

Preprints are marked. Claim letters (a) to (g) refer to the labels used in the earlier notes.

## Q1. Lenia-family papers: initialisation, spontaneous soliton rates, random-search baselines and controls

### Takeaway
None of the eight Lenia-family works checked measures how often solitons arise spontaneously from random initial states.

- **Starts.** Three kinds are used:
  - learned or optimised seeds: sensorimotor Lenia, Leniabreeder, the glider equation;
  - a single compact random patch or Gaussian: Flow-Lenia, Particle Lenia, the glider equation;
  - whole-grid Perlin noise: the phase-boundaries paper (2402.17848).
- **Search, not initial state.** Where rates exist, they are rates *per sampled parameter set* under search, never per random initial state.
- **Random-search baselines.** Only two works have one:
  - Hamon et al.: 30 moving stable solitons in 117,000 random-search trials, against 486 of 1,600 for IMGEP.
  - Papadopoulos et al. 2024: 5.5% "interesting" by eye under random sampling, against 13.0% with the Phase Transition Finder (PTF).
- **No nulls.** None uses a null or shuffled control for the initial state.

### Cited Findings

**Hamon, Etcheverry, Chan, Moulin-Frier, Oudeyer, "Discovering sensorimotor agency in cellular automata using diversity search"**
- *Where published.* It is confirmed as a journal paper: *Science Advances*, DOI 10.1126/sciadv.adp0834, 31 Oct 2025 (PMC copy). The arXiv preprint is 2402.10236, Feb 2024. [full text of the PMC and arXiv HTML, partially read by the fetch tool] — [PMC12577699](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577699/); [arXiv 2402.10236](https://arxiv.org/html/2402.10236)
- *Initial state.* It is learned, not random: a 40×40 pattern with values in [0,1], optimised together with the rule by gradient descent. Training uses one creature alone, with obstacles on one side of a 256×256 grid. The world has two channels: a fixed obstacle channel and a learnable channel with 10 self-kernels, controlled by 132 parameters. — [arXiv HTML](https://arxiv.org/html/2402.10236); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577699/)
- *Random-search baseline, same budget.* About 11,700 rollouts per seed over 10 seeds.
  - IMGEP: "486 of the 1600 parameters (10 seeds × 160 parameters) led to moving stable solitons", of which 261 had robustness ≥ 0.95.
  - Random search: "only 30 moving stable solitons were found through the 10 seeds of random search", of which 20 had robustness ≥ 0.95, out of 117,000 trials.
  - The paper also says random search finds stable solitons in "~1% of all its discoveries", mostly static. That 1% counts all stable solitons, moving or not, so it is not the same quantity as the 30 movers.
  - The paper also states: "random rules rarely result in the emergence of localized patterns."
  - No rate from random *initial states* is given.
  — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577699/)
- *Framing.* The authors call this "engineering second-order emergence", not spontaneous emergence. — [arXiv HTML](https://arxiv.org/html/2402.10236)

**Faldor and Cully, Leniabreeder ("Toward Artificial Open-Ended Evolution within Lenia using Quality-Diversity", ALIFE 2024; arXiv 2406.04235)** [full text via HTML]
- *Set-up.* 128×128 world with 3 channels. Each genotype is a 32×32×3 seed placed at the centre of an otherwise empty world. The search covers the seed (3,072 values) plus μ, σ and h for 15 kernels, so 3,117 dimensions. The initial population is "a batch of Aquarium solitons with isotropic variations", so the search starts from known creatures.
- *Baselines and controls.* There is no random-search baseline, no rate of moving solitons and no null. Statistics are 10 replicates per experiment, with Wilcoxon–Mann–Whitney tests and Holm–Bonferroni correction across QD variants only.
— [arXiv 2406.04235](https://arxiv.org/html/2406.04235)

**Kumar et al., ASAL (arXiv 2412.17799, preprint)** [full text via HTML]
- *Life-like CA.* "The initial state is a random 64×64 grid, where the sparsity level is uniformly sampled from U(0.05, 0.4)." The paper brute-forces all 2^18 = 262,144 rules, with 256 random initial states and 2,048 steps per rule. Game of Life "ranks among the top 5% most open-ended CAs" under a CLIP-based metric.
- *Lenia.* The substrate has a 32×32×3 initial state that is part of the searched parameters.
- *Baselines and validation.* There is no random-search baseline, no rate of moving or persistent structures, and no ground-truth or human validation of the CLIP metric. The foundation-model ablation is qualitative.
— [arXiv 2412.17799](https://arxiv.org/html/2412.17799)

**Kawaguchi, Suzuki, Arita and Chan, "Introducing asymptotics to the state-updating rule in Lenia" (ALIFE 2021)**
- *Not read.* The MIT Press page returned HTTP 403.
- *What secondary sources say.* The paper replaced Lenia's clipped update with a target-minus-state (asymptotic) update. Its search varied the shape of the growth function. Nothing about its initial states was found. [secondary] — [researchr listing](https://researchr.org/publication/KawaguchiSAC21)
- *Status.* Initialisation and any rates are **not verified**.

**Kojima, Yevenko and Ikegami, "The Glider Equation for Asymptotic Lenia" (arXiv 2508.04167, Aug 2025, preprint)** [full text via HTML v2]
- *Method.* Gliders are found by gradient descent with Adam on a travelling-wave residual loss. Initial patterns are mostly "Gaussian distributions with various width to promote the emergence of localized patterns" (σ = 15 in Fig. 1). The world is a single channel on a 144×144 torus.
- *Random starts.* They appear only as 20 random-kernel patterns per condition. The paper shows the five lowest-loss non-dissipating patterns and does not say how many of the 20 became gliders.
- *Baselines.* There is no spontaneous rate and no random-search baseline. The claim that the method finds patterns "difficult to discover through traditional methods" is not quantified.
— [arXiv 2508.04167v2](https://arxiv.org/html/2508.04167v2)

**Mordvintsev et al., Particle Lenia (2022 web article)** [full text]
- *Initialisation.* 200 particles uniform in a 12×12 square in 2D, or 256 particles uniform in a ball of radius 8.4 in 3D.
- *Outcomes.* The 2D run ends in a "spinning attractor". In 3D, particles "assemble into a mushroom-shaped glider". Different seeds give "different scenarios". 100 seed-only runs are mentioned, but no count of moving outcomes is given.
- *Parameters.* They were chosen interactively with the browser demo. There is no parameter search and no control.
— [Particle Lenia](https://google-research.github.io/self-organising-systems/particle-lenia/)

**Plantec et al., Flow-Lenia journal version (*Artificial Life* 31(2), 2025; arXiv 2506.08569)** [full text via HTML]
- *Random search.* Starts from "a 40×40 patch with uniformly sampled concentrations", runs 150 steps, over 10^5 parameter sets shared with a Lenia comparison. Table 1 is unchanged: R ∈ [2,25], μ ∈ [0.05,0.5], σ ∈ [0.001,0.2], h ∈ [0,1], r ∈ [0.2,1], a and b ∈ [0,1]^3, w ∈ [0.01,0.5]^3, s = 0.65, n = 2, dt = 0.2.
- *Multi-species runs.* 3 channels, with 5 kernels per channel pair (45 kernels), and 64 creatures each started as a 20×20 uniform patch. Grid size is not stated in the text read.
- *Rates and controls.* There are still **no counts** of moving patterns: "dynamic patterns are quite common", and "often static or slowly moving". The only control on the parameter sets is qualitative: they "mostly lead to empty or exploding patterns in the Lenia system". I found no neutral or shadow model for the evolutionary-activity measures.
— [arXiv 2506.08569](https://arxiv.org/html/2506.08569)

**Papadopoulos, Doat, Renard and Hongler, "Looking for Complexity at Phase Boundaries in Continuous Cellular Automata" (arXiv 2402.17848, Feb/Mar 2024, preprint)** [full text via HTML v2; this replaces the earlier notes' "secondary" tag]
- *Start.* Confirmed: "we will be initializing all runs with Perlin noise in all channels". Perlin scale and octaves are not given. The text continues: "we are implicitly selecting for interesting dynamics that develop for this class of random initial conditions."
- *Set-up.* Three channels with 106 free parameters, searched on a 5×5 world for 800 steps and evaluated on about a 16×16 torus.
- *Rates (Table 1).* "Interesting" was judged "by visual inspection", with about 200 samples per condition.

  | Prior | Random sampling | PTF |
  |---|---|---|
  | Neutral | 5.5% | 13.0% |
  | Smart | 14.0% | 30.5% |

- *What is missing.* There are no replicates, error bars or significance tests. The initial condition was not varied; including it in the search is listed as future work.
— [arXiv 2402.17848v2](https://arxiv.org/html/2402.17848v2)

### Inferences
- The project's framing, that the Lenia literature finds creatures by search and measures no spontaneous within-run rate with nulls, holds for every paper read here. That is not a novelty conclusion; it covers only these papers.
- The only published random baselines are rates per random *rule* (with learned or fixed starts) or "interesting" judged by eye. They are not comparable with the project's per-world counts of verified movers.
- The Hamon et al. baseline is the closest published number to "spontaneous movers from random rules": 30 in 117,000 random-search trials, about 0.026%. Its random search also covered initial patterns and used a filter for moving stable solitons, so the comparison is loose.

### Gaps
- Kawaguchi et al. 2021: full text not read (HTTP 403).
- The Hamon et al. ablations (no obstacles, uniform target sampling) were not read: the fetch covered only the first 100k characters of each version.
- "Capturing Emerging Complexity in Lenia" (arXiv 2305.09378) and Semantic Lenia (arXiv 2608.11657) were again not read.

## Q2. Yin (arXiv 2603.25239) and Hintze and Bohm (arXiv 2508.08047): do they exist, what they do, and how they bear on the project

### Takeaway
Both preprints exist, but the brief describes one of them inaccurately.

- **Yin** does map self-replication across all 262,144 outer-totalistic Moore rules. Its 1.56% "causal self-replication" rate is a *chained estimate* from a permissive proliferation screen with acknowledged high false-positive rates. There is no heredity test, and gliders are not addressed.
- **Hintze and Bohm** is **not** about Life-like rules or random soups. It studies one novelty-searched, non-totalistic 3×3 rule ("Outlier"), run from one specific seed cluster with no null.

Both bear on the project's claim to measure spontaneous emergence with nulls. Neither uses a selection-aware null or a shuffled control, but Yin has validation benchmarks and a single-cell knockout test.

### Cited Findings

**Yin, "The Self-Replication Phase Diagram: Mapping Where Life Becomes Possible in Cellular Automata Rule Space" (arXiv 2603.25239v1, 26 Mar 2026, preprint)**
- *Existence.* The author is listed as Don Yin, with "Dong Yin" in the submission history. The page says "outer-totalistic binary ... Moore neighbourhood" and never "Life-like", but the 262,144-rule space is the same. [abstract] — [arXiv abs](https://arxiv.org/abs/2603.25239)
- *Initial conditions.* [full text via HTML]
  - Screening runs on a 64×64 torus from "two initial densities (D0=0.15 and 0.35)".
  - The original protocol used 4 initial conditions per density and 512 steps. The equalised protocol, used for neighbourhood comparisons, used 1 per density and 256 steps.
  - A large-scale check reran 100 positives at 256×256 for 8,192 steps.
  — [arXiv HTML](https://arxiv.org/html/2603.25239v1)
- *Detection pipeline.*
  - Tier 1: either a monotonically increasing component count over at least 3 checkpoints, or a canonical (rotation- and reflection-invariant) component hash seen at least 3 times.
  - Tier 2: the same criterion at 512 steps with 8 checkpoints, so not independent.
  - Tier 3: a causal test. The candidate is isolated on an empty grid and must replicate alone. It counts as causal if "≥50% of single-cell deletions prevent replication". N = 10 trials per rule.
  — [arXiv HTML](https://arxiv.org/html/2603.25239v1)
- *Controls.*
  - Validation: "the GoL (B3/S23) and HighLife (B36/S23) are correctly identified as positive for self-replication". A dead rule and a high-λ chaotic rule are classed as negative.
  - λ–F nearest-neighbour matched controls, and 10,000-shuffle permutation tests for the mass-balance and O-information comparisons.
  - Detector robustness: across 12 parameter settings, "the false-positive rate among original negatives drops from 66% to 40%" at the stricter threshold.
  - There is no shuffled-initial-condition or selection-aware null for the replicator calls themselves.
  — [arXiv HTML](https://arxiv.org/html/2603.25239v1)
- *Headline numbers.*
  - 20,152 of 262,144 rules (7.69%) pass tier 1.
  - The 1.56% causal rate is the product 7.69% × 97.8% × 20.8%, with interval [1.2%, 2.0%]. It is an estimate, not a direct count.
  - Neighbourhood rates: von Neumann 4.79% (49 of 1,024, equalised protocol; 33.2% under the original protocol), Moore 7.69%, extended Moore 16.69% (sample of 10,000).
  - 12.2% of positives are "distributed replication" with no single seed.
  - Heredity and lineage are not tested. Gliders and spaceships are not mentioned.
  - Stated limits include: "Our pattern-proliferation definition is permissive".
  — [arXiv HTML](https://arxiv.org/html/2603.25239v1)

**Hintze and Bohm, "Rethinking Self-Replication: Detecting Distributed Selfhood in the Outlier Cellular Automaton" (arXiv 2508.08047v1, 11 Aug 2025, preprint)** [full text via HTML]
- *The rule.* "Outlier" is a binary rule on a 3×3 neighbourhood: a 271-step AND/XOR logic function found by novelty search (Yang 2024). It is not totalistic, so it is outside the Life-like space.
- *The run.* A 1,024×1,024 torus, started from "the same seed cluster (c0)" as in Yang (2024). This is not a random soup. Runs last 20,000 ticks, plus one 75,000-tick run on an "effectively infinite grid".
- *Method.* Per-cell causal tracing with minimal contributing neighbours, which builds an ancestry graph of clusters. A replicator must make at least two exact copies that trace back to it.
- *Numbers.* The graph has 31,959,320 nodes and 966,208 unique clusters. Replicator c2 has 2,439 appearances over 15 generations, with a growth factor of about 1.50.
- *What is missing.* There is no null, no shuffled control and no cross-rule comparison. Code is available "upon request".
- *Claims versus evidence.* The paper claims replicators are "spontaneous and robust" from what appears to be one seeded run. The authors also hypothesise that the boundary affects second-generation events.
— [arXiv 2508.08047](https://arxiv.org/html/2508.08047v1)

### Inferences
- **Bearing on Life-like results.** Yin is the nearest published exhaustive survey of the project's Life-like rule space. Its replication rates (1.6 to 7.7% of rules) concern *proliferation*, not self-propelled structures. It does not conflict with the project's Life-like mover results (E-09, E-10), and it does not cover them.
- **Possible Yin artefact.** Yin's validation calls Life (B3/S23) "positive for self-replication". Life is not known for spontaneous replicators from soup, so this suggests the proliferation criterion counts repeated common objects. The paper's own 40 to 66% false-positive figures support that reading. The project's HighLife-validated birth detector with a perturbed-vacuum null is stricter.
- **Bearing on "spontaneous emergence with nulls".** Both preprints claim spontaneous replication, but neither has a selection-aware null or a shuffled-start control. Hintze and Bohm does not test random starts at all. The project's methodological claim therefore stands **partly**: Yin's tier-3 single-cell deletion is a causal test, close in spirit to the project's isolation and knockout tests, and should be cited as such.
- **Possible conflict to check.** Yin counts HighLife-type replicators as present in up to 7.7% of rules. The project reports no reproducers in its Lenia work and a single multi-channel exception. These are different substrates, so they do not conflict, but the related-work section should say so.

### Gaps
- I did not verify Yin's "causal" pass rate (20.8%) on a sample myself. I also did not check whether Yin's tier-1 hash criterion would count gliders (a recurring hash) as proliferation; the paper is silent on this.

## Q3. Outside Lenia: has anyone tested spatial correlation, smoothness or patch size of random initial conditions for the emergence of localized movers, with matched mass or a shuffled or phase-randomised control?

### Takeaway
**Not found in this search.** Only one study varies an initial-condition property systematically: Hudcová et al. 2026 varies uniform-noise *patch area* (already in the earlier notes). Gray-Scott work notes that spot formation depends on perturbation size and shape, but not as a controlled emergence-rate study. SmoothLife's paper does not describe its initial states. Larger-than-Life (Evans) asks whether "bugs" arise from random starts at suitable densities, but I could not read it. No study found uses a correlation-length sweep at fixed mass or a shuffled or phase-randomised surrogate start.

### Cited Findings
- **SmoothLife (Rafler, arXiv 1111.1567).** The paper text describes neither the initial-state generation nor glider frequency from random starts. It notes that an earlier continuous Life without the inner radius found "no gliders". [full text via ar5iv, short paper] — [ar5iv 1111.1567](https://ar5iv.labs.arxiv.org/html/1111.1567)
  - A NetLogo model page says gliding objects "quickly appear" from a random start. This is anecdotal, with no count. [secondary] — [NetLogo SmoothLife](https://ccl.netlogo.org/netlogo/models/SmoothLife)
- **Larger-than-Life (Evans 2001).** A search snippet says Evans asked whether glider-like "digital creatures" appear from random states at a suitable density. The text was not obtained. [secondary] — search result pointing to [Pivato, RealLife, arXiv math/0503504](https://arxiv.org/pdf/math/0503504)
- **Gray-Scott and reaction-diffusion.**
  - Spot outcomes depend on "the size and geometry of an initial perturbation". In an excitable-media model, large perturbations can decay while smaller ones form spots.
  - A rectangular initial condition split into four spikes in a Gray-Scott-type model ([arXiv patt-sol/9804001](https://arxiv.org/pdf/patt-sol/9804001)).
  - Spot self-replication is set mainly by parameters: with the same initial condition, S = 4.5 replicates and S = 4.1 does not ([arXiv 1009.2805](https://arxiv.org/pdf/1009.2805)).
  - None of these measures emergence rates against a shuffled control. [secondary: search summaries; not read in full]
- **Shuffling as a correlation-destroying control in CA.** One 2025 totalistic-CA paper notes that shuffling a configuration at fixed density destroys correlations and pushes the dynamics toward mean field. It applies this to dynamics, not to the emergence of localized structures. [secondary] — [arXiv 2512.04140](https://arxiv.org/html/2512.04140v3)
- **Already covered in the earlier notes, not re-read:** MaCE (Perlin circle, about 83% by eye, no start comparison), Hudcová et al. (patch area 10² to 90², uniform values, no smoothness or density sweep), Reinke et al. (white noise "tend[s] to evolve into dead or global patterns").
- **Phase-boundaries paper.** It confirms it fixed Perlin starts and lists varying the initial condition as future work ([2402.17848v2](https://arxiv.org/html/2402.17848v2)). This is direct evidence that this group had not done the correlation experiment by March 2024.

### Inferences
- Claim (b), that correlated starts produce movers and shuffled starts of the same values do not, remains **not found in this search**. Its qualitative motivation, that compact or structured seeds beat white noise, is **partly known** (Reinke et al.; Gray-Scott perturbation-size dependence; standard practice of compact seeds).

### Gaps
- Queries used:
  - "SmoothLife Rafler 2011 generalization Game of Life continuous gliders random initial"
  - "Larger than Life Evans bugs emerge from random initial conditions density"
  - "Gray-Scott spot replication dependence on initial perturbation size width"
  - "initial condition correlation length effect on emergence of localized structures cellular automata surrogate shuffled" (extended)
- Evans 2001 and Pearson 1993 full texts were not read. Phase-randomised surrogates (as in time-series analysis) were not found in any CA context.
- Absence of evidence here is not evidence of novelty.

## Q4. Life-like soups: glider yield per soup and dependence on initial density; Eppstein on initial conditions

### Takeaway
- **Glider yield.** From Catagolue's B3/S23 C1 census, Life yields about **1.92 gliders per 16×16 asymmetric soup** (my computation from census totals). LWSS are far rarer, at about 0.0028 per soup.
- **Density.** Catagolue's standard census uses a fixed soup size and density, so density dependence of glider yield was not found as a published number. Related results:
  - lifespan and final population plateau at about 25 to 50% initial density, with a maximum near 37.5%;
  - ash density tends to about 0.029 largely independent of initial density.
- **Eppstein.** He explicitly *rejects* random initial conditions as the basis for classifying Life-like rules and gives no glider rates.

### Cited Findings
- **Catagolue b3s23/C1 census.** "339 739 217 865 028 soups" and "7 421 561 391 760 522 objects". [full text of the census page, as read today] — [Catagolue b3s23/C1](https://catagolue.hatsya.com/census/b3s23/C1)
- **Spaceship counts** from the xq4 text census [full text]: glider (xq4_153) 652,508,356,959,329; LWSS 953,349,907,380; MWSS 251,165,481,594; HWSS 43,648,630,692. — [Catagolue textcensus xq4](https://catagolue.hatsya.com/textcensus/b3s23/C1/xq4)
  - Per soup (my arithmetic): glider ≈ 1.92; LWSS ≈ 2.8 × 10⁻³; MWSS ≈ 7.4 × 10⁻⁴; HWSS ≈ 1.3 × 10⁻⁴.
  - Caveat: apgsearch soups are 16×16 at density 0.5 on an infinite plane, and gliders are counted as census objects. The density is from my background knowledge of apgsearch, not verified in this search.
- **Density dependence of lifespan (N. Johnston blog).**
  - Set-up: 20×20 torus, densities 1 to 99%, 13,592 random patterns per density.
  - Results: average and median lifespans plateau at about 25 to 50% density, consistent with a maximum near 37.5%. The median final population peaks at 13, at 38%.
  - Gliders are not discussed. [full text, blog]
  — [njohnston.ca "Longevity in Conway's Game of Life Revisited"](https://njohnston.ca/?p=493)
- **Ash density.** Flammenkamp's experiments (D = 0.371 to 0.375, tori 2^12 and 2^14) give an asymptotic ash density of 0.0287115. A forum post reports about 0.028 "almost regardless" of initial density. [secondary: search summary] — [York ECAL05 paper citing Flammenkamp](https://www-users.cs.york.ac.uk/ss44/bib/ss/nonstd/ecal05.pdf)
  - Another summary says soups at 15 to 70% density drift toward the same attractor, and denser soups die quickly. [secondary] — [arXiv 1809.03266](https://arxiv.org/pdf/1809.03266)
- **Eppstein, "Growth and Decay in Life-Like Cellular Automata" (arXiv 0911.2890; Springer 2010)** [full text, extracted by me]
  - Patterns from random fields in Life "consist overwhelmingly of small still lifes and small period-two oscillators". Citing Flammenkamp, the pulsar, pentadecathlon and figure-8 arise "once per 20,000, 1.6 million, or 33 million distinct patterns".
  - On random starts as a basis: he argues against using random initial conditions to classify rules, because rigorous results exist only for very low density, and because "Because our primary interest is in engineered patterns rather than random fields, we restrict our attention to patterns that have a finite number of live cells."
  - He describes Gravner's "expansive" classification, which uses random n×n bounding boxes in vacuum: a patch start.
  - Qualitative random-start notes: HighLife, B368/S12578 and others "slowly settle down to scattered oscillators and still lifes". Day & Night behaves symmetrically about p = 1/2.
  - There are no glider rates and no density sweeps for gliders.
  — [arXiv 0911.2890](https://arxiv.org/abs/0911.2890)

### Inferences
- **Life gliders are not rare.** Life's soups are a strong positive for spontaneous movers, at about 2 gliders per 16×16 soup. A project finding of "no movers from soup" in a Life-like rule would be anomalous for Life itself. The project's Life-like results report *self-propelled shape types*, so this does not conflict.
- **The density confound is real.** Census practice holds soup size and density fixed by design, and Gravner's random n×n patch in vacuum is the classical patch start. The project's E-10 finding, that the central-patch effect vanishes at matched density, is consistent with this. A claim that a central patch helps would have conflicted with nothing, and its disappearance is unsurprising.

### Gaps
- The LifeWiki "Soup" page again returned HTTP 403.
- No published glider-per-soup versus density curve was found. Catagolue's non-standard density censuses were not tabulated for gliders in this search.
- Evans' Larger-than-Life density results were not read.

## Q5. Internal check: what E-16 actually ran, against Flow-Lenia's published set-up

### Takeaway
**Calling E-16 "we could not reproduce movers" is overstated and partly inaccurate.**

- **E-16 never used the paper's start.** It used no single centred 40×40 patch. Its "patches" condition is Chan's 15 to 40 small patches. Journal J-018's phrase "from their own patch start" is therefore wrong for E-16.
- **The rules differ from the paper's.** E-16 used one channel, 1 to 3 kernels, and R fixed at 13.
- **Its detector counts only isolated translating survivors.** The paper's "dynamic" patterns include gyrating and snake-like motion.
- **The paper publishes no rate.** There is no count to reproduce.

The closer replication is the J-016 validation run: 80 rules from the paper's 40×40 patch, with 3, 5 and 10 kernels, 128², 500 steps, 0 movers. That is still single-channel, without the paper's R range for most rules, and with implementation choices the paper leaves unspecified.

### Cited Findings (repository: code and journal read directly)
- **E-16 command and set-up.**
  - Command: `emergence conditions --rules-file docs/data/rule-panel-e16.txt --inits uniform,smooth:3,smooth:6,patches --seeds 1 --size 128 --steps 1000 --density 0.35 --seed 16`.
  - Scale: 100 random rules × 4 starts = 400 worlds, 1 seed each, 128×128, 1,000 steps. "0 self-propelled in 400 universes (5 candidates, all rejected by isolation)".
  — `docs/experiments.md` line 48; `docs/journal.md` J-018
- **E-16 starts, as implemented** (`emergence/engine.py`, `Universe.from_spec`, `INIT_KINDS`):
  - `uniform`: a whole-grid soup with 35% of cells occupied and values U[0,1]. Expected mass is 0.175 per cell, about 2,870 over 128².
  - `smooth:3` and `smooth:6`: Gaussian-blurred noise over the whole grid, matched to the soup's total mass.
  - `patches`: "Chan's (2019) random start", with 15 to 40 squares of side 12 at random places and values U[0, 0.9].
  - None is the paper's start. `FlowLenia.patch_state` (a centred 40×40 patch, U[0,1], mass about 800) exists in `emergence/physics/flow_lenia.py` but is called only from `emergence/benchmark_probes.py`, not by `emergence conditions`.
- **E-16 rules** (`FlowLenia.random`, `emergence/physics/flow_lenia.py`):
  - One channel, R fixed at 13, `rng.integers(1, 4)`, so **1 to 3 kernels** of 3 rings each.
  - μ ∈ [0.05,0.5], σ ∈ [0.001,0.2], h ∈ [0.01,1], r ∈ [0.2,1], a ∈ [0,1]^3, b ∈ [0.001,1]^3, w ∈ [0.01,0.5]^3.
  - Fixed constants: θ_A = 1, n = 2, dt = 0.2, s = 0.65, dd = 5, with unnormalised Sobel gradients.
  - The plan file (`docs/data/e16-plan.md`) itself notes "Flow-Lenia's own paper uses one central patch".
- **Flow-Lenia 2023 published set-up** [full text, extracted by me from the PDF]:
  - Start: "Initial patterns A0 are set with a 40 × 40 patch with matter drawn from uniform distribution in the center of the grid and no matter everywhere else."
  - Table 1: R ∈ [2, 25]; r ∈ [0.2,1]; h, a, b ∈ [0,1] (a and b per ring); w ∈ [0.01,0.5]^3; μ ∈ [0.05,0.5]; σ ∈ [0.001,0.2]; s = 0.65; n = 2; dt = 0.2. θ_A, Sobel normalisation and displacement clipping are not given.
  - Channel and kernel counts for random search are **not stated**. The timing benchmark is "1 channel, 10 kernels and 128 × 128". The paper says "Using multiple kernels led to the emergence of SLPs with more complex shapes and behaviors", and Fig. 1 includes 2-channel creatures.
  — [Plantec et al. 2023, arXiv 2212.07906](https://arxiv.org/abs/2212.07906)
- **Flow-Lenia 2023 on movement** [full text]:
  - "dynamic patterns are quite common ... gyrating SLPs (a) or snake like patterns (b) with complex motion". "Dynamic" here includes rotation in place.
  - Optimisation for directed motion: "good solutions can be found in the 2 channels condition but not in the single channel case. However, when running the algorithm for longer (e.g 5000 generations), we have been able to found single channel creatures with similar fitness". The earlier notes' statement that single-channel optimisation failed is therefore **incomplete**: it succeeded with longer runs.
  - Directed-motion creatures used 10 to 25 kernels.
  — [arXiv 2212.07906](https://arxiv.org/abs/2212.07906)
- **2025 journal version.** Random search runs 150 steps from the 40×40 patch, over 10^5 parameter sets, still with no mover counts. — [arXiv 2506.08569](https://arxiv.org/html/2506.08569)
- **J-016 (the project's validation run).** "80 random float rules from the paper's 40×40 uniform patch (128×128 torus, 500 steps): 20 with 3 kernels, 20 with 5, 20 with 10, and 20 with 10 kernels and R random in [8, 25]. 0 self-propelled structures." The entry also lists unspecified-detail choices (Sobel normalisation, dd = 5, θ_A = 1) as caveats. — `docs/journal.md` J-016

### Differences, E-16 against the paper

| Item | E-16 | Plantec et al. 2023 |
|---|---|---|
| Start | soup at 0.35 occupancy; mass-matched smooth fields; Chan multi-patch | one centred 40×40 U[0,1] patch, vacuum elsewhere |
| Total initial mass | about 2,870 (soup and smooth) | about 800 |
| Channels | 1 | not stated for random search; 1- and 2-channel creatures shown |
| Kernels | 1 to 3 | not stated; 10 in the timing benchmark; "multiple kernels" give richer behaviour |
| R | fixed at 13 | [2, 25] |
| h, b lower bounds | 0.01, 0.001 | 0, 0 (immaterial) |
| θ_A, Sobel, dd | 1, unnormalised, 5 (own choices) | unspecified |
| Steps | 1,000 | not stated (2023); 150 (2025) |
| What counts | an isolated translating structure that survives 1,000 steps alone | "dynamic", including gyrating and snake-like patterns, judged visually |
| Published rate | 0 of 400 | none |

### Inferences
- **What J-018 and the paper get wrong.** J-018's phrase "We cannot reproduce that, from their own patch start or from any other" is inaccurate for E-16. E-16 had no 40×40 centred-patch condition. Only J-016 tested that start, with 80 rules, not 400. The paper's sentence (§3, line 221) "We could not reproduce movers (E-16)" inherits this error.
- **Suggested accurate wording.** "In single-channel Flow-Lenia with 1 to 10 kernels and R = 13 (mostly), we found no translating structure that survives in isolation: 0 in 400 worlds from soup, smooth and multi-patch starts (E-16), and 0 in 80 rules from the paper's centred 40×40 patch (J-016). Plantec et al. report dynamic patterns, including rotating ones, as common but give no count, so there is no published rate to compare against."
- **Why the gap is not a contradiction.** The paper's "dynamic" includes rotation in place, and its directed motion needed 2 channels or long optimisation. A null for *isolated translating* movers among random single-channel, few-kernel rules is **consistent with** the paper, not in conflict with it. Label this result **"partly known / not comparable"**, not "failed reproduction".

### Gaps
- I did not inspect the authors' reference code (it has no licence, per J-016) to find the default channel and kernel counts or θ_A used in their random search.
- The project has not run a matched test: 40×40 centred patch, R ∈ [2,25], about 10 kernels, 2 channels.
