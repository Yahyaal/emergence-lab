# Lenia-family and Life-like CA: spontaneous emergence of movers and reproducers vs. initial conditions (compared with Emergence Lab claims (a) to (g))

Scope note: compiled 16 Nov 2026, using about 18 tool calls. Each finding says how much of the source was read: **[full text]** means I read the extracted PDF or HTML text, or the relevant sections of it; **[abstract]** means the abstract or abstract page only; **[code]** means I read source code; **[secondary]** means a search-engine summary or project page I did not verify against the paper. Several of the papers named in the brief (Asymptotic Lenia, Kojima et al., Particle Lenia, sensorimotor Lenia, Leniabreeder, ASAL) were **not read in this search**. They are listed under Gaps, not described from memory.

## Q1. How do the main Lenia papers initialise worlds, and does any of them measure how often solitons arise from random starts?

### Takeaway
The published Lenia line starts from a **compact random patch inside an empty world**, not from a full-grid soup. Creatures are found by interactive or semi-automatic search, with humans selecting the results. Chan 2019, Chan 2020 and Flow-Lenia 2023 give **no rates** of solitons from random starts and **no controls**. Two newer works do give numbers: MaCE 2025 (preprint) reports soliton emergence in about 83% of 100 random runs, judged by eye, and Hudcová et al. 2026 (late-breaking abstract) varies the initial patch size over more than 10^5 systems. Neither has a null or shuffled control.

### Cited Findings
- **Chan 2019, how creatures were found [full text].** Section 2.3 lists four strategies of "Interactive Evolutionary Computation": random generation, parameter tweaking, automatic exploration and manual mutation. On random generation it says that "Given enough time, naturally occurring lifeforms would emerge from the primordial soup, for example Orbium, Scutium, Paraptera, and radial symmetric patterns". The starts are described as "Initial configurations with random patches of non-zero sites". The paper gives no counts, rates, patch sizes or densities. It says automated exploration "is ineffective without the aid of artificial intelligence", and "Transient patterns captured during random generation could also be stabilized into new species" by parameter tweaking. — [Chan 2019, arXiv:1812.05433](https://arxiv.org/abs/1812.05433)
- **Chan 2019, open questions [full text].** Open question 8 reads "Do self-replicating and pattern-emitting lifeforms exist in Lenia?", so self-replication was not known in single-channel Lenia in 2019. Question 7 asks whether Lenia is capable of open-ended evolution. — [Chan 2019](https://arxiv.org/abs/1812.05433)
- **Chan's reference code, the exact random-start recipe [code].** The recipe is in `Lenia.random_world()` in `LeniaND.py`. It places `np.random.randint(15, 40)` patches, so 15 to 39. Each patch is a square or cube of side `int(R * 0.9)`, filled with `np.random.random_sample(...) * 0.9`, so values are uniform on [0, 0.9). Placement keeps a margin `border = R//2 + dim//2`. An alternative `is_fill` mode fills the whole world except a 2R margin with uniform noise. The default world is 2^(W−P) = 128 cells per side. `DEF_R` = 20 in 2D, and the randomised R ranges over 10 to 40. This confirms the project's description of "15 to 40 dense patches"; the exact upper bound is 39. — [Chakazul/Lenia LeniaND.py](https://raw.githubusercontent.com/Chakazul/Lenia/master/Python/LeniaND.py)
- **Chan 2020 ("Lenia and Expanded Universe", ALIFE 2020) [full text].** The paper describes semi-automatic search with Global, Depth-first and Breadth-first strategies and a Genetic algorithm. Results are filtered automatically by survival, then "selected by the human-in-loop for novelty, visual appeal, or prospects for further study". Global search "generates random genotypes and phenotypes from the global search space". No initial-condition recipe and no rates are given. — [Chan 2020, arXiv:2005.03742](https://arxiv.org/abs/2005.03742)
- **Flow-Lenia 2023 (Plantec et al., ALIFE 2023, best paper) [full text].** "Initial patterns A0 are set with a 40 × 40 patch with matter drawn from uniform distribution in the center of the grid and no matter everywhere else." Patterns were found "By performing random and manual search". The Figure 2 caption shows patterns from "randomly sampled parameters sets (no cherry picking)". No counts are given. — [Plantec et al. 2023, arXiv:2212.07906](https://arxiv.org/abs/2212.07906)
- **Flow-Lenia journal version [abstract/secondary].** Published as "Flow-Lenia: Emergent Evolutionary Dynamics in Mass Conservative Continuous Cellular Automata", *Artificial Life* 31(2): 228–248 (2025). It uses the evolutionary-activity framework on multispecies simulations. I did not get the full text, so its initial conditions and any rates are unverified. — [DeepMind publication page](https://deepmind.google/research/publications/106327/); [comdig summary](https://comdig.unam.mx/2025/08/09/flow-lenia-emergent-evolutionary-dynamics-in-mass-conservative-continuous-cellular-automata)
- **Reinke, Etcheverry and Oudeyer (IMGEP, ICLR 2020) [project page].** "Using a simple random initialization of each individual cell will generate white noise patterns which tend to evolve into dead or global patterns spanning the whole grid." They therefore generate structured initial states with CPPNs on a "256x256 grid". The page gives no fraction of discovered "animals". — [developmentalsystems.org IMGEP page](http://developmentalsystems.org/intrinsically_motivated_discovery_of_diverse_patterns)
- **MaCE (Papadopoulos and Guichard, arXiv 2507.12306, July 2025; preprint, possibly ALIFE 2025 proceedings via DOI 10.1162/ISAL.a.846) [full text, relevant sections].**
  - Initial condition: "Each generation starts with a random circle of Perlin noise in the center, and we let it evolve for 1000 iterations".
  - Rate: "After 100 random generations, we found that ~83% of the time the system has soliton emergence". With independent parameter sampling the figure was "~61%".
  - Judgement: "we visually determine whether the system produces solitons", where solitons are defined "qualitatively as moving" structures.
  - Limits: this is a mass-conserving variant, with no null and no comparison of start types.
  — [MaCE arXiv:2507.12306](https://arxiv.org/html/2507.12306)
- **Hudcová, Dušek, Tuccio and Hongler, "Visualizing the Structure of Lenia Parameter Space" (arXiv 2601.01932, 5 Jan 2026, preprint, "Late Breaking Abstract") [full text via HTML].**
  - Set-up: 100×100 grid. The noise patch has "uniform random values in [0,1]" and is surrounded by zeros, following Chan. Patch shapes are random Voronoi polygons. Patch areas run over 10², 20², …, 90², with 64 configurations per area.
  - Scale: "over 10^5 Lenia systems", and about 10,000 systems per μ–σ plane for 8 kernels.
  - Claims: they "observed a strong correspondence between unclassified initial configurations and the emergence of moving solitons", and solitons lie in a region that "typically lies in a transition region between the stable and metastable phase".
  - Limits: no numerical soliton rate. Patch density and smoothness are not varied.
  — [arXiv:2601.01932](https://arxiv.org/html/2601.01932)
- **"Looking for Complexity at Phase Boundaries in Continuous Cellular Automata" (arXiv 2402.17848) [secondary: search summary only; the PDF was too large to fetch].** Reportedly initialises all runs with Perlin noise and says this "implicitly select[s] for interesting dynamics" for that class of starts. Soliton phases are reported as sharp transitions in parameter space. — [arXiv:2402.17848](https://arxiv.org/pdf/2402.17848)

### Inferences
- Claim (c), "Chan's published start", is accurately described: 15 to 39 patches of side 0.9R with values in [0, 0.9), in a 128² default world. But Chan never published a rate for it. The project's 13 of 160 (256², 3,000 steps) and 0 of 40 (128²) appear to be the first counts for that recipe that I found.
- The practice of starting from *structured or compact* initial states is established in the literature: patches (Chan), a centred 40×40 patch (Flow-Lenia), CPPNs (Reinke et al.), a Perlin-noise circle (MaCE), Perlin noise (2402.17848). Reinke et al. state explicitly that per-cell white noise tends to give dead or global patterns. So the *qualitative* contrast behind claims (a), (b) and (d) is **partly known**: soup is bad and structured starts are good. It is folklore and design practice, not a measured contrast.
- Claim (a), no gliders from soup in 2,085 worlds, agrees with the Reinke et al. statement and is **partly known** qualitatively. The specific count and the viability scan (8 of 99 rules) are not in the sources read.

### Gaps
- Not read in this search: Kawaguchi et al. 2021 (Asymptotic Lenia), Kojima et al. 2025 (glider equation), Mordvintsev et al. 2022 (Particle Lenia), Hamon et al. 2024 (sensorimotor Lenia, *Science Advances*), Faldor and Cully 2024 (Leniabreeder), Kumar et al. 2024 (ASAL), "Capturing Emerging Complexity in Lenia" (arXiv 2305.09378), and Semantic Lenia (arXiv 2608.11657). Their initialisation recipes and any rates remain unverified here and should be checked before the project writes its related-work section.
- I could not read the full text of the 2025 Flow-Lenia *Artificial Life* paper.

## Q2. Has anyone studied how spatial correlation or smoothness of initial conditions affects soliton or glider emergence, with a shuffled or phase-randomised control?

### Takeaway
**Not found in this search.** The closest prior work varies the *size* of a uniform-noise patch (Hudcová et al. 2026), uses Perlin noise or CPPNs as a design choice (MaCE 2025; 2402.17848; Reinke et al. 2020), or states qualitatively that white noise fails (Reinke et al.). None of the works found manipulates the correlation length at fixed mass, and none uses a value-preserving shuffle control. Claim (b), including its shuffled control, is "apparently new" only in the weak sense: it was not found by these queries.

### Cited Findings
- Per-cell white-noise starts "tend to evolve into dead or global patterns spanning the whole grid", which motivated CPPN-structured starts. — [Reinke et al. project page](http://developmentalsystems.org/intrinsically_motivated_discovery_of_diverse_patterns)
- Patch *size* is varied (10² to 90² cells, 64 samples per size) with uniform [0,1] values. Correlation, smoothness and density are not varied. — [Hudcová et al. 2026](https://arxiv.org/html/2601.01932)
- Perlin-circle starts give about 83% soliton emergence across 100 random parameter draws, judged visually. There is no comparison with white noise. — [MaCE](https://arxiv.org/html/2507.12306)
- Perlin-noise starts are said to "implicitly select" dynamics. — [arXiv:2402.17848 (secondary)](https://arxiv.org/pdf/2402.17848)

### Inferences
- The *mechanism* the project proposes, isolated lumps with space around them, matches the community's habit of seeding compact patches. The project's contribution would be a quantified contrast at fixed mass with a shuffled control, not the qualitative idea.
- The MaCE figure of about 83% (mass-conserving, Perlin circle, by eye) is far above the project's 7 to 23%. The difference in substrate, in the definition of a soliton (moving, judged by eye, versus a verified glider surviving 1,000 steps alone) and in rule sampling makes the two numbers non-comparable. They are not in conflict.

### Gaps
- Queries tried: "Lenia initial conditions spatial correlation emergence solitons random initialization statistics" (extended), plus the fetches above. Not searched: SmoothLife and Larger-than-Life initial-condition studies; reaction-diffusion (Gray-Scott, Pearson 1993) dependence on initial perturbation size; phase-randomised or surrogate controls in CA. These need dedicated queries before the project calls (b) new.

## Q3. What is reported about self-replication in Lenia, and is heredity claimed or measured anywhere?

### Takeaway
Self-replication in *extended* (multi-kernel or multi-channel) Lenia is **already published** and described as "not rare" (Chan 2020), but with no rates. Flow-Lenia (2023) reports "Dividing and merging dots" as "a common pattern" and food-driven division into "two identical creatures". MaCE (2025) explicitly notes the *absence* of heredity. Claim (e), dividing spots without heredity in 1 of 1,000 random multi-channel rules, is therefore **partly known, and in tension with published wording**. Chan's "not rare" and Flow-Lenia's "common" suggest much higher prevalence than the project's 1 in 1,000. The discrepancy is probably explained by Chan's human-guided search and different rule sampling, not by random rules.

### Cited Findings
- Chan 2020 [full text]: "Self-replication An important milestone in the study of Lenia is the discovery of self-replication. It is conspicuously missing in the original Lenia, but turns out to be not rare in extended rules."
  - Mechanism: "one soliton develops into two partitions of similar structures, each develops into a full soliton, drifts away, and is capable of further division."
  - On debris and density: "In highly reproductive cases, new individuals can develop out of debris." There is also "autocatalytic replication": when soliton density rises, "congregation of solitons will force self-replication to happen".
  - Figure 3 caption: "the first replicator discovered" (multi-kernel); "replicator under three rounds of binary fission".
  - The paper gives no heredity, variation or selection measurement. The replicators were found through the semi-automatic, human-in-the-loop search.
  — [Chan 2020](https://arxiv.org/abs/2005.03742)
- Chan 2020 [full text]: "Unlike the original Lenia, where most solitons are well defined and moderately symmetric, solitons found in the extended rules ... become highly chaotic yet highly self-organized". — [Chan 2020](https://arxiv.org/abs/2005.03742)
- Flow-Lenia 2023 [full text]: "Dividing and merging dots (c) resembling reaction-diffusion patterns are also a common pattern." With food, "when growing after eating, some creatures will divide in two identical creatures as shown in figure 6 (f), crucial pattern for evolution to occur." Also: "Demonstrating the emergence of intrinsic evolutionary processes has been left out of the scope of this paper". Multi-species runs use 1024 × 1024 worlds with 144 creatures, simulated for 200k steps, with mutations every 500 steps. — [Plantec et al. 2023](https://arxiv.org/abs/2212.07906)
- MaCE 2025 [full text]: solitons "start to colonize the space and reproduce as they gather extra mass", and one mitosis episode is shown. But: "The main missing piece towards evolution is the capacity to transmit their genes", since "each new creature goes through the selection process each time!" — [MaCE](https://arxiv.org/html/2507.12306)

### Inferences
- The project's diagnosis, that its dividing spot is an attractor of the rule so offspring cannot inherit, matches MaCE's explicit statement. Heredity-free division in Lenia variants is **already published** (MaCE; arguably Flow-Lenia's "dividing dots resembling reaction-diffusion"). The project's scrambled-lump test is a cleaner operationalisation of the same point.
- The project's single-channel null, "no reproducer among movers", agrees with Chan 2019 (open question 8) and Chan 2020 ("conspicuously missing in the original Lenia"). It is **already published** as a qualitative statement.
- To my knowledge from these sources, no Lenia paper reports a measured heredity test. The parameter-localisation mutations in Flow-Lenia multi-species runs are a designed heredity channel, not an emergent one.

### Gaps
- I did not read the 2025 *Artificial Life* Flow-Lenia paper, which may contain evolutionary-activity measurements relevant to heredity.
- I did not search for later "self-replication Lenia" papers (2024–2026).

## Q4. What do the Flow-Lenia papers say about how common moving patterns are, with what starts and parameters? (claim f)

### Takeaway
Flow-Lenia 2023 says "dynamic patterns are quite common", and also that its patterns "are often static or slowly moving". It gives **no counts**. Its start is a centred 40×40 uniform patch with randomly sampled parameters (its Table 1). The project's 0 of 400 is in **soft tension** with "quite common", but it cannot be called a contradiction without matching the start (a 40×40 centred patch) and the parameter ranges.

### Cited Findings
- On how common movers are: "Most of the patterns generated in Flow Lenia are SLPs ... While part of emerging patterns tend to be static ones, dynamic patterns are quite common in Flow Lenia. For instance gyrating SLPs (a) or snake like patterns (b) with complex motion ... can be frequently observed." — [Plantec et al. 2023](https://arxiv.org/abs/2212.07906)
- Discussion: "Even though patterns generated by Flow Lenia are often static or slowly moving, we have been able to find creatures with complex dynamics from random search only". — [Plantec et al. 2023](https://arxiv.org/abs/2212.07906)
- In the 2023 paper, directed movement was obtained by *optimisation* in one experiment (fitness f(θ) = dist(φ(A0), φ(A400))). "Results ... show that good solutions can be found in the 2 channels condition but not in the single channel" one. So single-channel Flow-Lenia movers were hard to obtain even by optimisation. — [Plantec et al. 2023](https://arxiv.org/abs/2212.07906)

### Inferences
- The optimisation result (movers found in 2 channels but not in 1) is directly relevant. If the project's E-16 used single-channel or few-kernel Flow-Lenia, a null is **consistent with** the published difficulty rather than a failure to reproduce. The project should check its channel count and kernel number against Table 1 of Plantec et al. and use the 40×40 centred patch before calling the result a failed reproduction.

### Gaps
- Table 1's parameter ranges were not extracted verbatim. Mass-conserving variants (MaCE: about 83% movers, by eye) suggest that movers can be common in mass-conserving Lenia under Perlin-circle starts.

## Q5. Life-like rules: what do soup censuses and density studies say about initial density, patch shape and spaceship emergence? (claims d, g)

### Takeaway
The standard Life soup census (apgsearch and Catagolue) uses **16×16 asymmetric soups**. The census is huge: about 3.19 × 10^14 soups and about 6.98 × 10^15 objects as of a March 2025 snapshot [secondary]. Catagolue also keeps per-density and per-symmetry censuses. I did **not** find a sourced study of how central patch versus full-grid starts, at matched density, affects spaceship counts. So claim (g) is "not found in this search". It is methodologically unsurprising, because census practice fixes soup size and density.

### Cited Findings
- Catagolue statistics (cached March 2025): about 6.98 × 10^15 objects of 542,283 types from about 3.19 × 10^14 asymmetric 16×16 soups. **[secondary]**: search summary of the statistics page, not read directly. — [Catagolue statistics](https://gol.hatsya.co.uk/statistics)
- A 2017 forum thread reports objects-per-soup at 25% density for rule variants (for example about 628 vs about 17.8 per soup), showing that density-specific censuses exist. **[secondary]** — [conwaylife forum "Catagolue Oddities"](https://conwaylife.com/forums/viewtopic.php?p=47391)
- The LifeWiki "Soup" page returned HTTP 403 and was not read.

### Inferences
- The finding that a central-patch "effect" vanished at matched density is a sound control. In Life the standard census confound is density per area, and census tools hold it fixed by design.

### Gaps
- Not obtained: the glider occurrence rate per soup in the B3/S23 census (the Catagolue glider object page did not show a total in the portion read); Eppstein's "Growth and decay in Life-like cellular automata" (arXiv 0911.2890); density sweeps for Life (for example the classic result that random Life soups settle to an ash density of about 0.03). These need direct reading.

## Q6. Critiques noting that Lenia creatures are mostly found by search or hand-tuning

### Takeaway
The primary sources themselves say so. Chan 2019 describes creature discovery as "Interactive Evolutionary Computation" with human selection and manual mutation. Chan 2020's search keeps results "selected by the human-in-loop". Flow-Lenia's discussion says that in earlier Lenia "one needs to search or evolve for patterns that are both non-vanishing and non-exploding". The project's framing (search vs. spontaneous emergence) is therefore **already acknowledged** in the primary literature. Rates of spontaneous emergence with nulls were not found.

### Cited Findings
- "...the previous versions of Lenia, where one needs to search or evolve for patterns that are both non-vanishing and non-exploding, and to constantly monitor their existential status." — [Plantec et al. 2023](https://arxiv.org/abs/2212.07906)
- Chan 2019 section 2.3, and Chan 2020 human-in-the-loop selection, as quoted above. — [Chan 2019](https://arxiv.org/abs/1812.05433); [Chan 2020](https://arxiv.org/abs/2005.03742)

### Inferences
Provisional labels for the claims (evidence from this search only):
- **(a)** Partly known. The qualitative point that soup fails is stated by Reinke et al. The project's counts and viability scan were not found in the literature.
- **(b)** Not found in this search. No work found varies correlation at fixed mass or uses a shuffle control. Several works use correlated starts (Perlin, CPPN, patch) by design.
- **(c)** The recipe is published by Chan (in code, not in the paper). No published rate was found.
- **(d)** Partly known in qualitative form ("dead or global patterns"). No density threshold (0.18 / 0.24) was found published for Lenia.
- **(e)** Partly known, with tension. Chan 2020 calls self-replication "not rare" in extended Lenia, and Flow-Lenia calls dividing dots "common". MaCE explicitly notes no heredity. The 1 in 1,000 random-rule rate is new as a number, but it should be framed against those statements.
- **(f)** Soft tension with Flow-Lenia's "quite common" moving patterns. It is consistent with the 2023 finding that single-channel optimisation for movement failed.
- **(g)** Not found in this search.

### Gaps
- No dedicated search was run for published critiques or reviews of Lenia (for example open-endedness reviews that discuss hand-curation).
