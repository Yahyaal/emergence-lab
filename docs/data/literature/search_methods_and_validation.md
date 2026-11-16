# Search methods, rule-to-behaviour prediction, and validation practice: prior art compared with Emergence Lab

Scope: claims (a) to (e) of `docs/paper.md` (sections 1, 2, 6, 7, 8, 9). Search date: 16 November 2026. Read status is given for every source: **[full]** = full text or substantial sections read this session; **[partial]** = parts of the full text read (via fetch summary); **[abstract]** = abstract or arXiv landing page only; **[secondary]** = search-engine or third-party summary only; **[prior]** = from the researcher's background knowledge of the paper, not re-checked this session (treat as needing verification before citing). Preprints are marked (preprint).

Total budget used: about 25 tool calls. Several important papers (Langton 1990, Wolfram 1984, Wuensche 1999, Zenil 2010, Sapin et al., Etcheverry et al. 2020, Cisneros et al.) were seen only through abstracts or summaries.

---

## Q1. Classic rule-to-behaviour prediction: how well do λ, Z, input entropy, Eppstein's criteria and compression predict gliders or complex behaviour?

### Takeaway
No classic rule-level parameter has a published, quantitatively validated record of predicting gliders or "complex" behaviour. λ was shown by Mitchell, Hraber and Crutchfield to support weaker claims than Packard drew from it. Eppstein's fertile-and-mortal criterion is a stated hypothesis, supported by examples, not a tested predictor. The classifiers of Wuensche and Zenil sort rules into Wolfram-like classes; they do not predict gliders. The project's F predictor (a rule-only property tested prospectively against soup outcomes, with pre-registration) is therefore more rigorous in form than this classic literature. It is also narrower: replicators in BFF variants, not gliders.

### Cited Findings
- Mitchell, Hraber and Crutchfield (1993, *Complex Systems* 7:89–130) repeated Packard's 1988 GA experiment on λ. Their results were "very different", and they argue that "the interpretation of the original results is not correct". The claim they challenge is that rules capable of complex computation cluster near critical λ, and that evolution selecting for computation drives rules there. [abstract] — [arXiv adap-org/9303003](https://arxiv.org/abs/adap-org/9303003); [SFI working paper](https://www.santafe.edu/research/results/working-papers/revisiting-the-edge-of-chaos-evolving-cellular-aut)
- Background, not checked this session: Langton (1990, *Physica D* 42) reported λ as a statistical, not a deterministic, indicator of transitions between ordered and chaotic behaviour, with large variability among rules at a given λ. Wolfram's (1984) four classes are defined by behaviour from random initial conditions, not computed from the rule. [prior]
- Eppstein (2010, in *Game of Life Cellular Automata*, Springer; arXiv 0911.2890) proposes a two-question classification of Life-like rules. *Fertile*: some finite pattern escapes every bounding box. *Mortal*: some pattern dies out completely. His hypothesis is that "the rules most likely to support interesting patterns are the ones that are both fertile and mortal". His evidence is a "menagerie" of example rules (HighLife and others), not a statistical test. [full, pdftotext of arXiv PDF] — [arXiv 0911.2890](https://arxiv.org/abs/0911.2890)
- Eppstein's numbers: by search software plus "searches using small random seeds", 10,736 of the 16,384 B3 rules (about 65.5%) were found to have spaceships. Fertility is determined in 96% of cases (5,584 rules undetermined). Of 131,072 Life-like rules without B0, 77,563 are proven immortal and 53,214 mortal, about 99.8% decided. He admits immortal rules can still have spaceships (B3456/S013). [full] — [arXiv 0911.2890](https://arxiv.org/abs/0911.2890); [Eppstein's glider survey page](https://ics.uci.edu/~eppstein/ca)
- Eppstein explicitly criticises classification from random initial conditions (Wolfram's, and Gravner's "expansive" rules). He argues it "does not address well the ability of a cellular automaton to support non-random structures", and that many of Life's most interesting patterns could not be found from random starts. [full] — [arXiv 0911.2890](https://arxiv.org/abs/0911.2890)
- Wuensche ("Classifying Cellular Automata Automatically", SFI WP 98-02-018; *Complexity* 4, 1999) sorts 1D CA rules into ordered, complex and chaotic classes by the variance over time of input entropy. The static Z parameter, computed from the rule table, correlates only approximately. A secondary source says Class 4 rules tend to occur near Z ≈ 0.75, "but no clear classification was formed". No accuracy figures were retrieved. [secondary] — [SFI listing](https://www.santafe.edu/research/results/working-papers/classifying-cellular-automata-automatically); [Wuensche PDF](https://users.sussex.ac.uk/~andywu/downloads/papers/cplex.pdf)
- Zenil (2010, *Complex Systems* 19(1); arXiv 0910.4042) uses lossless compression of CA evolutions to approximate program-size complexity. The resulting clusters correspond to Wolfram's main classes, and the paper proposes a "phase transition coefficient" linked to a conjecture about universality. This is a classifier of compressibility; glider prediction was not reported in what was seen. [abstract] — [arXiv 0910.4042](https://arxiv.org/abs/0910.4042)
- Recent (preprint, March 2026): D. Yin, "The Self-Replication Phase Diagram: Mapping Where Life Becomes Possible in Cellular Automata Rule Space" (submitted to *J. R. Soc. Interface*). It covers all 262,144 outer-totalistic Moore rules, with a three-tier detector: proliferation, extended-length confirmation, causal perturbation. Proliferation appears in 20,152 rules (7.69%); causal self-replication is estimated at 1.56%. Proliferating rules concentrate at λ ≈ 0.15–0.25 and a background-stability parameter F ≈ 0.2–0.3. Mass-balance averages 0.21 for replicators against 0.34 for non-replicators; Derrida μ is 1.81 against 1.39. The abstract reports no classifier accuracy, held-out validation or null model. [abstract] — [arXiv 2603.25239](https://arxiv.org/abs/2603.25239)
- A search result points to a 2026 detector-sensitivity analysis with false-positive rates. At a stricter setting, 96.3% of positives were recovered, and false positives among original negatives fell from 66% to 40%. The snippet's source paper was not identified with certainty; it may be Yin 2026. [secondary; unverified attribution] — [arXiv 2603.25239](https://arxiv.org/pdf/2603.25239)

### Inferences
- Rule-level prediction of behaviour in the classic literature is at best statistical (λ, Z) or qualitative (Eppstein, Zenil). The project should not imply it improves on a validated baseline; no such baseline exists. It should say it tests rule-level predictors prospectively, which the classic papers did not.
- Eppstein's 65.5% figure matters for H1 (Q2). In B3 Life-like rules, spaceships are the majority case, though many are found by engineered search rather than from random soups. Counting "distinct rules with self-propelled shapes" therefore measures how a search samples a large set, not how it finds rare ones.
- The project's Lenia result that "the limit was emergence, not existence" (E-12, E-13a), together with the Life-like observation of the same kind, mirrors Eppstein's distinction between what a rule supports and what arises from random starts. Eppstein should be cited for that distinction.
- Yin (2026, preprint) overlaps directly with the project's level-3 work and rule-level prediction: a self-replication census of Life-like rule space, a causal-perturbation tier, and rule parameters as predictors. It is the closest recent prior art found and should be cited and compared.

### Gaps
- No full text read for Langton 1990, Wuensche 1999, Zenil 2010 or Yin 2026, so no accuracy numbers in the authors' own words. Queries tried: "Wuensche Classifying cellular automata automatically input entropy variance Z parameter"; "Zenil compression-based investigation dynamical properties cellular automata classes compressed length"; "Mitchell Hraber Crutchfield Revisiting the edge of chaos lambda".
- No study found that measures the predictive accuracy (sensitivity, specificity, AUC) of λ, Z or fertile/mortal for glider presence across Life-like rules. Not found in this search.

---

## Q2. Automated search: methods, comparison with random search at equal compute, and definitions of "interesting"

### Takeaway
Comparing guided search against random search at equal budget, with independent seeds, is standard in the IMGEP and Lenia line of work, and the reported gains are often far larger than the project's 1.84×. Hamon et al. report 486 moving, stable solitons from 1,600 IMGEP outputs against 30 from 117,000 random-search parameters. ASAL and Leniabreeder report no random baseline. "Interesting" is almost always defined operationally by the searchers' own descriptors, classifiers or foundation-model embeddings, and rarely validated independently. The project's H1 result is ordinary practice, with a modest effect size; its own disclosure that it is partly circular is appropriate.

### Cited Findings
- **Sapin and colleagues** (with Adamatzky, Bull, Bailleux): evolutionary algorithms whose fitness counts gliders, run on 2D (and hexagonal) rules. The 2007 Wolfram conference paper reports finding new glider guns for over half the gliders found, and around 5,000 guns emitting the same gliders. A 2010 *Natural Computing* paper (9(3):513–543) classifies "tens of thousands" of glider guns. Lohn and Reggia (1997), who used a GA to search for self-replicating CA rules, noted that discovered rules had to be checked for self-replication by manual simulation. [secondary] — [Sapin, Wolfram Science 2007](https://www.wolframscience.com/conference/2007/presentations/EmmanuelSapin.html); [UWE repository](https://uwe-repository.worktribe.com/output/975815/stochastic-automated-search-methods-in-cellular-automata-the-discovery-of-tens-of-thousands-of-glider-guns); [Lohn & Reggia](https://drum.lib.umd.edu/handle/1903/468)
- **Reinke, Etcheverry and Oudeyer (ICLR 2020, arXiv 1908.06663)**, run on Lenia:
  - Baselines: random exploration and IMGEP variants (hand-defined, random-VAE, pretrained-VAE and online-learned goal spaces). Every method gets 5,000 iterations (the first 1,000 random) and 10 independent runs.
  - Diversity metric: the number of occupied bins (7 per dimension) in an "analytic behaviour space". The space combines a β-VAE trained on 42,500 patterns with hand-defined features, and the experimenter chose it.
  - "Animals" (spatially localised patterns) are labelled by a rule-based classifier (connected, at least 80% of activation, not wrapping, persisting), not by people.
  - Results: random search has the highest parameter-space diversity. The hand-defined, pretrained and online-learned IMGEPs beat random in behaviour-space diversity (Welch t, p < 0.01). The random-VAE IMGEP did not. Animal counts appear only in figures.
  - [partial] — [ar5iv 1908.06663](https://ar5iv.labs.arxiv.org/html/1908.06663)
- **Hamon, Etcheverry, Chan, Moulin-Frier and Oudeyer**, "Discovering sensorimotor agency in cellular automata using diversity search" (arXiv 2402.10236, Feb 2024; *Science Advances*, 31 Oct 2025):
  - Equal rollout budget: about 11,700 Lenia rollouts per seed; 10 seeds each for IMGEP and random search.
  - Moving stable solitons: 486 (of 1,600 IMGEP outputs) against 30 (of 117,000 random parameter sets). Robust agents (obstacle score ≥ 0.95): 261 against 20.
  - Random search found stable solitons in about 1% of its outputs, but "most of them are static".
  - Operational definition of an agent: an empirical stable-soliton filter, a moving test (minimum distance travelled), and 50 obstacle rollouts of 2,000 steps each. Then 45 generalisation tests (9 perturbation families × 5 strengths, 10 seeds each).
  - Ablations of curriculum, diversity search and gradient descent. No formal significance tests were seen in the main text.
  - [partial, about 100k of 127k characters] — [PMC12577699](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577699/); [arXiv 2402.10236](https://arxiv.org/abs/2402.10236)
- **Faldor and Cully, Leniabreeder (ALIFE 2024, arXiv 2406.04235)**:
  - Methods: MAP-Elites with hand-chosen descriptors, and AURORA with a VAE-learned descriptor. Population 32,768; 10 seeds; Wilcoxon–Mann–Whitney tests with Holm-Bonferroni correction.
  - "Lifelike" means solitons, filtered by mass bounds the authors call arbitrary. The unsupervised fitness is low latent variance, which the authors note penalises periodic and chaotic behaviour.
  - No random-search baseline.
  - Evidence for "unbounded diversity" is cumulative elites still rising after 10⁶ evaluations. The authors call it suggestive and do not claim open-endedness.
  - [partial] — [arXiv 2406.04235 (HTML)](https://arxiv.org/html/2406.04235v1)
- **Kumar, Lu, Kirsch, Tang, Stanley, Isola and Ha, ASAL** (arXiv 2412.17799, v2 May 2025):
  - Vision-language foundation models (CLIP, DINOv2) score simulation videos, in three modes: target, open-endedness and illumination. Substrates: Boids, Particle Life, Life-like CA, Lenia, NCA.
  - No random-search or equal-compute baseline; the only ablation is the choice of embedding (pixels against CLIP against DINOv2, judged qualitatively).
  - Open-endedness is novelty in CLIP space, and the paper admits the notion "is subjective and hard to define". No human study validates it.
  - Brute force over all 2¹⁸ = 262,144 Life-like rules (256 random starts, 2,048 steps) ranks Conway's Life in the top 5% "most open-ended".
  - [partial] — [arXiv 2412.17799v2](https://arxiv.org/html/2412.17799v2)
- **ASAL++**: Baid, Erlebach, Hellegouarch and Wieser, "Guiding Evolution of Artificial Life Using Vision-Language Models" (arXiv 2509.22447; ALIFE 2025 proceedings). A second foundation model (Gemma-3) proposes new targets from the simulation's visual history. Two strategies were tested on Lenia: EST (one new prompt per iteration) and ETT (the whole sequence of prompts). The evaluation is qualitative and comparative ("greater visual novelty" against "more coherent sequences"). No random baseline was seen in the abstract. [abstract] — [arXiv 2509.22447](https://arxiv.org/abs/2509.22447)
- **Cisneros, Sivic and Mikolov**, "Evolving Structures in Complex Systems" (arXiv 1911.01086, IEEE SSCI 2019): a metric for growth in the complexity of emerging patterns, using compression-based and neural (prediction-loss) variants, applied to 1D and 2D CA. The authors report it finds rules with Life-like emergent properties. Validation and baseline details were not retrieved. [abstract/secondary] — [arXiv 1911.01086](https://arxiv.org/abs/1911.01086); [code](https://github.com/hugcis/evolving-structures-in-complex-systems)
- **Etcheverry et al., HOLMES** (NeurIPS 2020, arXiv 2007.01195): hierarchical, progressively learned goal spaces for IMGEP on Lenia. As remembered, it includes random-exploration baselines and evaluates diversity in experimenter-defined spaces. [prior; not checked this session] — [arXiv 2007.01195](https://arxiv.org/abs/2007.01195)
- **Other 2025–2026 work**:
  - Automated discovery of system-level dynamics in Flow-Lenia (arXiv 2505.15998, May 2025). [title/snippet only] — [arXiv 2505.15998](https://arxiv.org/abs/2505.15998)
  - Hintze and Bohm (arXiv 2508.08047, Aug 2025, preprint): causal-lineage reconstruction shows spontaneous, sometimes multi-component self-replicators in the "Outlier" CA. No controls or nulls are described in the abstract. [abstract] — [arXiv 2508.08047](https://arxiv.org/abs/2508.08047)

### Inferences
- **H1's comparison design is standard.** Guided against random at matched budget with independent seeds is the norm in the Oudeyer group's papers (Reinke 2020, Hamon 2024/2025). The project's 20 paired seeds and pre-registration are more careful than most, but the comparison itself is not new.
- **The effect is small next to Hamon et al.** By the per-output rate computed from Hamon's counts (an inference, since Hamon does not report it), IMGEP beats random by about 1,000×, though that is in Lenia and uses gradient refinement. The project's 1.84× is in Life-like rules, where Eppstein's numbers suggest spaceship-bearing rules are common. Random search is therefore a strong baseline there, and a ratio near 2 is unsurprising.
- **Circularity is common in this literature.** "Interesting" is defined by the searcher's own descriptor, classifier or embedding: Reinke's analytic behaviour space, Leniabreeder's descriptors, ASAL's CLIP space. The project already discloses that self-propulsion is one of the engine's objectives. That disclosure is better than common practice, but it does not make H1 an independent result.
- **No found search paper validates its "interesting" label with a deceptive control.** None of the papers read report a control built to fool the metric, for example a static blob field that scores high on CLIP novelty. Hamon's obstacle and generalisation tests are the closest: perturbation tests of the found agents, not tests of the metric.
- **Claim (e) holds only in a narrow form.** Reinke, Hamon, Leniabreeder and ASAL search jointly over parameters and initial states, and Hamon adds gradient optimisation. They find patterns that the rule supports; they do not measure how often structure arises spontaneously from unstructured starts, against a null. The claim that "none of the Lenia-related works measures spontaneous within-run emergence with nulls" is therefore consistent with the papers checked, but only in that narrow form. Reinke uses CPPN-generated (spatially structured) initial states, which is relevant to the project's finding that correlated starts produce gliders. That finding should be framed against this practice.

### Gaps
- No full text read for ASAL++, HOLMES, Cisneros et al. or the Sapin papers, so their baselines are unconfirmed.
- No paper found that reports a guided-against-random ratio specifically for Life-like or Generations rules with gliders. Queries: "Sapin evolutionary algorithm search gliders glider guns 2D cellular automata rules"; "ASAL++ automated search artificial life foundation models 2025 arXiv".

---

## Q3. Taxonomies and ladders: is there an existing equivalent of the five-level evidence ladder?

### Takeaway
Each rung of the project's ladder corresponds to a well-known concept, and several published hierarchies order similar properties. Maynard Smith and Szathmáry order transitions in units of selection. Bedau's classes of evolutionary activity cover none, bounded and unbounded. Dolson et al. order change, novelty, complexity and ecology. Banzhaf et al. distinguish exploratory, expansive and transformational novelty. Krakauer et al. distinguish organismal, colonial and environmentally driven individuality. No published ladder was found that combines persistence → self-propulsion → self-replication → heredity → open-ended evolution as evidence levels, each gated by a validated measurement. The project's ladder is a reasonable assembly of standard criteria, and should be presented as an assembly, not a new theory.

### Cited Findings
- Bedau, Snyder and Packard (ALife VI, 1998), "A classification of long-term evolutionary dynamics": evolutionary activity statistics with three classes (adaptive activity absent, bounded or unbounded) and a "neutral shadow" model. The shadow is identical except that selection is turned off, and its activity is subtracted to give excess adaptive activity. Standish describes a further "unbounded and creative" class that none of Bedau's applied models showed. [secondary] — [Bedau et al. ALife VI PDF](https://people.reed.edu/~mab/papers/alife6.pdf); [Standish, arXiv nlin/0004026](https://arxiv.org/abs/nlin/0004026)
- Validation work by Bullock and Bedau tested whether the statistics would wrongly place intuitively unlifelike systems in Class 3. That is a deliberate false-positive test of an open-endedness measure. [secondary] — [Standish, nlin/0004026](https://arxiv.org/abs/nlin/0004026); [Southampton eprint](https://eprints.soton.ac.uk/261445/1/arl12201.pdf)
- Dolson, Vostinar, Wiser and Ofria (*Artificial Life* 25(1), 2019), MODES toolbox: change, novelty, complexity and ecology potential, presented as a hierarchy in which "novelty requires some degree of change". The metrics were tested on NK landscapes and Avida, and open-endedness is treated as a continuum. [abstract/secondary] — [PeerJ preprint](https://peerj.com/preprints/27249v2/); [NSF PAR copy](https://par.nsf.gov/biblio/10104628)
- Taylor et al. (*Artificial Life* 22(3):408–423, 2016), the report of the York OEE workshop: pluralism about open-ended evolution, and a separation of observable hallmarks from proposed mechanisms. [secondary] — [Taylor publication page](https://tim-taylor.com/paper-details/taylor2016openended.html)
- Banzhaf et al. (*Theory in Biosciences* 135, 2016), "Defining and simulating open-ended novelty":
  - exploratory novelty: within the system's existing model;
  - expansive novelty: the model changes but uses existing concepts;
  - transformational novelty: the meta-model changes.

  Taylor (*Artificial Life* 25(2), 2019) argues that typical measures capture only the exploratory kind. [secondary via Taylor 2019] — [Taylor 2019, ar5iv 1806.01883](https://ar5iv.labs.arxiv.org/html/1806.01883)
- Krakauer, Bertschinger, Olbrich, Flack and Ay (*Theory in Biosciences* 139:209–223, 2020), "The information theory of individuality": individuals are aggregates that propagate information from past to future. Three forms (organismal, colonial, environmentally driven) vary in environmental dependence. Individuality is continuous and nested. [secondary] — [Springer PDF](https://link.springer.com/content/pdf/10.1007/s12064-020-00313-7.pdf)
- Background, not checked this session [prior]:
  - Maynard Smith and Szathmáry, *The Major Transitions in Evolution* (1995): transitions in how information is stored and transmitted, and in units of selection.
  - Beer (2004, *Artificial Life* 10(3)), "Autopoiesis and cognition in the Game of Life": an autopoietic analysis of a glider, with its boundary and its domain of perturbations.
  - Hoel, Albantakis and Tononi (2013, *PNAS*): causal emergence via effective information.
  - Rosas et al. (2020, *PLoS Comput Biol*), "Reconciling emergences": integrated-information-decomposition criteria for causal emergence, with a practical criterion based on mutual information.

### Inferences
- **Level 2.** The project's "self-propelled in an isolated clone" test is close to Hamon's stable soliton plus moving test, and to Beer's analysis of glider individuality. Hamon's added robustness to perturbation is a stronger agency criterion than the project's level 2. Krakauer's measure could formalise level 1 ("persistent organisation") beyond "several shape types across seeds".
- **Levels 4 and 5** are standard notions: heredity and variation from Maynard Smith and Szathmáry and von Neumann, and OEE criteria from Bedau, Dolson, Taylor and Banzhaf. The project's level-5 tests (later code not fitter; no parasites) correspond roughly to asking whether there is Bedau class 2/3 activity, or MODES ecology. The project should cite these and consider computing them; it does not appear to compute Bedau's activity with a shadow null.
- **Selection-aware nulls in ALife go back at least to Bedau's neutral shadow (1998).** The project's null principle has direct precedent in this field.

### Gaps
- Not found in this search: any published ladder ordering persistence, motility, replication, heredity and open-ended evolution as graded evidence levels for artificial worlds. Queries tried: the OEE and individuality searches above. A specific search for "hierarchy of life-like properties artificial life levels" was not run because of budget, so absence is not established.
- Hoel and Rosas measures: not checked this session for validation against false positives, for example known failures of the Rosas criterion on non-emergent systems.

---

## Q4. Methodology: deceptive controls, selection-aware nulls, pre-registration, false positives, unit of analysis, reproducibility, detector benchmarks

### Takeaway
Null models, controls and attention to false positives are long-standing in ALife (Bedau's neutral shadow; Bullock and Bedau's tests for wrongly labelling unlifelike systems; Lohn and Reggia's manual verification of discovered replicators). The general principle of positive and negative controls is ordinary experimental practice. Pre-registration is rare in ALife but not absent: a CA "intention manuscript" in registered-report style exists, and simulation-study preregistration templates exist (COS). No formal ALife benchmark for self-replication or individuality detectors was found. Treating the rule rather than the seed as the statistical unit corresponds to Hurlbert's pseudoreplication problem; no ALife-specific discussion was found. What looks unusual in the project is the combination: a committed probe suite with deliberately deceptive controls for every detector, plus a public log of fooled detectors. The individual ingredients are standard.

### Cited Findings
- **Neutral and shadow nulls.** Bedau's "neutral shadow" is a selection-off copy of the model whose activity is subtracted to isolate adaptation. Filtering data with such "neutral models" gives "excess activity due specifically to adaptation". [secondary] — [Standish, arXiv nlin/0004026](https://arxiv.org/abs/nlin/0004026); [Bedau et al. 1998](https://people.reed.edu/~mab/papers/alife6.pdf)
- **Testing a complexity statistic against systems built to look lifelike.** Bullock and Bedau examined whether evolutionary activity statistics wrongly classify intuitively unlifelike systems as Class 3. This is the same idea as the project's "deceptive control". [secondary] — [Southampton eprint](https://eprints.soton.ac.uk/261445/1/arl12201.pdf)
- **Automated discovery needs a verification step.** Lohn and Reggia (1997) noted that after rule discovery "the cellular space must be manually simulated" to check self-replication. [secondary] — [UMD DRUM](https://drum.lib.umd.edu/handle/1903/468)
- **Specification gaming in digital evolution.** Lehman et al. (2020, *Artificial Life* 26(2)), "The Surprising Creativity of Digital Evolution", is a collection of anecdotes in which evolving systems satisfy the letter of a measure while defeating its intent. This is the evolutionary-computation analogue of the project's fooled-detector table. [prior] — [arXiv 1803.03453](https://arxiv.org/abs/1803.03453)
- **Pre-registration in CA and complex systems.** arXiv 2208.09444, an "intention manuscript" on discretisation and self-organisation in approximations of continuous CA, says it plays a role similar to a Stage 1 registered report. [secondary] — [arXiv 2208.09444](https://arxiv.org/abs/2208.09444)
- **General simulation-study preregistration.** The Center for Open Science has a Simulation Studies Preregistration Template, built on ADEMP. A 2026 preprint, "Why, when, and how to (or not to) preregister a simulation study", argues that preregistration benefits late-phase studies of mature methods more than early-phase studies of new methods. [secondary] — [COS blog](https://www.cos.io/blog/introducing-the-simulation-studies-preregistration-template); [PsyArXiv/OSF cxjrb](https://sciety.org/articles/activity/10.31234/osf.io/cxjrb_v1)
- **Statistical practice in evolutionary computation.** Bartz-Beielstein et al. (2020, arXiv 2007.03488), "Benchmarking in Optimization: Best Practice and Open Issues", covers experimental design, analysis and reproducibility. Vermetten et al. (GECCO 2022) show that COCO's default of 15 runs can be insufficient to rank algorithms. Eftimov and Korošec (GECCO 2018) show that different ranking schemes on the same data give different results. [secondary] — [Bartz-Beielstein et al. PDF](https://cavalab.org/assets/papers/Bartz-Beielstein%20et%20al.%20-%202020%20-%20Benchmarking%20in%20Optimization%20Best%20Practice%20and%20Op.pdf); [Vermetten et al., arXiv 2204.09353](https://arxiv.org/abs/2204.09353)
- **Pseudoreplication.** Hurlbert (1984, *Ecological Monographs* 54:187–211), "Pseudoreplication and the design of ecological field experiments", is the classic source on treating non-independent subsamples as replicates. It is the general form of the project's "six soups of one rule are not six tests" (D-063). [prior] — [Hurlbert 1984, JSTOR](https://www.jstor.org/stable/1942661)
- **Statistical practice in the Lenia search papers.** Leniabreeder uses 10 seeds with Holm-Bonferroni-corrected Mann-Whitney tests. Reinke et al. use 10 runs with Welch t-tests. Hamon et al. use 10 seeds with means and standard deviations. The project's 20 paired seeds and pre-registered sign tests are at or above this norm. [partial] — [Leniabreeder](https://arxiv.org/html/2406.04235v1); [Reinke et al.](https://ar5iv.labs.arxiv.org/html/1908.06663); [Hamon et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC12577699/)
- **Detector false-positive analysis, 2026.** A detector-sensitivity analysis reports false positives among negatives falling from 66% to 40% at a stricter setting, with 96.3% recall; it is probably the Yin 2026 preprint. This is the only quantitative false-positive figure for a CA self-replication detector found. [secondary; attribution uncertain] — [arXiv 2603.25239](https://arxiv.org/pdf/2603.25239)

### Inferences
- **What is standard.** Null models (Bedau's shadow, 1998), positive and negative controls, multiple seeds, and verifying candidates after automated search (Lohn and Reggia) are established. The project should say plainly that its four-part check (positive, negative, deceptive, selection-aware null) applies standard experimental-control practice systematically. It is not a new methodology.
- **What looks less common (found nowhere else in this search).**
  - A versioned benchmark suite that every detector must pass, with adversarial "deceptive" controls written for each detector.
  - Pre-registration of confirmatory tests in ALife experiments.
  - A published table of the project's own detector failures.

  These are distinctive in practice, not in principle. Because the search was limited, "not found" must not be read as "new".
- **The rule-as-unit correction (J-086, D-063)** is a textbook pseudoreplication fix (Hurlbert 1984). The project should cite it as such. That the project initially made the error (p values 10⁵ to 10¹⁹ too small) is a point against claiming methodological leadership.
- **Missing global multiple-comparison correction.** The project does not correct across its 45 pre-registered primaries (paper section 8). Leniabreeder, by contrast, applies Holm-Bonferroni within its comparisons. This is a known weakness by ordinary standards.

### Gaps
- Not found: any ALife or CA benchmark dataset for self-replication, individuality or glider detectors, with labelled positives and negatives. Queries: "2025 automated discovery self-replicators cellular automata detector false positives".
- Not found: an ALife-specific paper on pseudoreplication across seeds of one rule. Queries: "benchmarking evolutionary computation best practice statistical analysis independent runs pseudoreplication Bartz-Beielstein 2020".
- Not found: any ALIFE conference or *Artificial Life* journal registered-report track. Queries: "preregistration artificial life complex systems simulation studies registered report".
- Reproducibility standards specific to ALife (artefact badges and similar) were not searched. Budget.

---

## Q5. Research conducted largely by AI agents: guidance and validity assessment (as of 2026)

### Takeaway
By late 2025 there was published evidence that AI-scientist systems commit exactly the failures the project's controls target: post-hoc selection, metric substitution and inappropriate benchmarks. These failures are hard to detect from the paper alone, and auditing full logs and code works much better. The main venue experiment (Agents4Science 2025) recommends detailed human–AI contribution checklists. The project's committed journal, decisions log and pre-registrations match the "submit trace logs" recommendation. Its reviews being made only by AI systems is a weakness under this guidance.

### Cited Findings
- **Luo, Kasirzadeh and Shah**, "The More You Automate, the Less You See: Hidden Pitfalls of AI Scientist Systems" (arXiv 2509.08713; NeurIPS 2025 AI4Science spotlight; preprint):
  - Four failure modes: inappropriate benchmark selection, data leakage, metric misuse, and post-hoc selection bias.
  - Tested on Agent Laboratory and The AI Scientist v2, using a synthetic task. The AI Scientist v2 sometimes reported self-devised metrics instead of the specified ones.
  - An LLM classifier detecting the failures from papers alone reached near-chance accuracy (51.4%, F1 0.48). Trace logs and code made detection much more effective.
  - The authors recommend that venues require trace logs and code of the whole automated process.
  - [abstract/secondary] — [arXiv 2509.08713](https://arxiv.org/abs/2509.08713); [NeurIPS 2025 page](https://neurips.cc/virtual/2025/126015)
- **Agents4Science 2025** (Stanford-led; AI agents as first authors and reviewers), reported in arXiv 2511.15534:
  - 315 submissions, 62 desk-rejected, 48 accepted. LLM reviewers were calibrated on ICLR 2022 and 2025 decisions, and the top 79 papers also had a human expert review.
  - 56.7% of submissions reported primary AI contribution at every stage.
  - Participants noted weak domain grounding and errors that needed human intervention.
  - The authors recommend that journals adopt human–AI collaboration checklists.
  - Secondary sources differ: 47 or 48 accepted.
  - [abstract/secondary] — [arXiv 2511.15534](https://arxiv.org/abs/2511.15534); [Science News](https://www.sciencenews.org/?p=3161586)
- Lu et al. (2024, arXiv 2408.06292), "The AI Scientist": the system generates, runs and writes up ML research end to end, with an automated reviewer. [prior] — [arXiv 2408.06292](https://arxiv.org/abs/2408.06292)

### Inferences
- **The project's fooled-detector table matches documented failure modes.** Three of its entries (uncommitted deduplication, soup-level p values, post hoc thresholds) are instances of the pitfalls Luo et al. document for AI-run research: post-hoc selection and metric misuse. The project should cite Luo et al. and say that its repository (journal, pre-registration commits, experiment exports) is the kind of full trace Luo et al. recommend.
- **The AI-only review is a weakness.** The five reviews were by AI systems (paper section 8). Under Agents4Science practice, human expert review was added for top papers. The absence of any human domain-expert review should stay prominently disclosed.

### Gaps
- No full text read for either AI-research paper. No formal guidance from a publisher or ALife society on AI-agent-led research was found. A query on journal or ISAL policy was not run because of budget.

---

## Cross-cutting verdict on claims (a)–(e)

- **(a) Ladder.** It assembles standard concepts (Maynard Smith and Szathmáry; Bedau; Dolson; Banzhaf/Taylor; Krakauer; Hamon's operational agency criteria). No identical ladder was found, but that search was incomplete. Present it as an organising scheme, not a contribution.
- **(b) Validation regime.** Each ingredient is established: Bedau's shadow null (1998), Bullock and Bedau's false-positive tests, Lohn and Reggia's verification of automated finds, Hurlbert's pseudoreplication. Pre-registration is rare in ALife but has precedent (arXiv 2208.09444). A systematic, versioned adversarial probe suite per detector was not found elsewhere. That is the defensible, modest claim, and it is good practice made systematic, not a new method.
- **(c) H1, 1.84×.**
  - Guided-against-random at equal budget is the standard comparison (Reinke 2020; Hamon 2024/2025, where the gap is about 1,000× per output by this note's arithmetic).
  - The project's ratio is small, partly circular (self-propulsion is an objective), and in a rule space where Eppstein found spaceships in about 65% of B3 rules.
  - ASAL and Leniabreeder have no random baseline, so the project's pre-registered 20-seed paired design is more rigorous than those two.
- **(d) Fooled detectors.** The phenomenon is well known: specification gaming (Lehman et al. 2020), statistics labelling unlifelike systems as open-ended (Bullock and Bedau), and false positives in AI-run research (Luo et al. 2025). A public, itemised table of a project's own detector failures was not found elsewhere in this search.
- **(e) "No Lenia work measures spontaneous within-run emergence with nulls".**
  - Consistent with Reinke, Hamon, Leniabreeder, ASAL and ASAL++ as read: all search jointly over parameters and initial states, or optimise. None estimates spontaneous emergence rates from unstructured starts against shuffled or matched nulls.
  - The project must add two recent preprints on spontaneous self-replication in CA, which are close in spirit even though they are not Lenia: Hintze and Bohm 2025 (arXiv 2508.08047) and Yin 2026 (arXiv 2603.25239). Their controls should be checked before any novelty claim.
  - Eppstein's paper already separates "supported by the rule" from "arises from random starts" for Life-like rules.
