# After replicators exist: heredity, selection, parasites, space and open-ended evolution, compared with Emergence Lab's Finding C

Scope: published work on post-emergence dynamics in artificial replicator systems, compared with Emergence Lab's claims (a) to (g) in `docs/paper.md` sections 5, 8 and 9. Search date: 16 November 2026.

Reading-depth key, given for every source:
- **[FT]**: full text read, or a substantial part of it, in this session.
- **[ABS]**: abstract, metadata or index page only.
- **[SEC]**: secondary summary (search-engine synthesis, third-party page, or a review quoting the primary).
- **[MEM]**: a well-known reference I did not fetch this session. It is given with a DOI and must be checked before anyone cites it.

Budget note: about 20 search/fetch calls. Several primary papers (Ray 1991 chapter, Lenski 2003, Szabó 2002, Bedau 1998, Channon) were not read in full. That limits the precision of some numbers below. Each case is flagged.

---

## Q1. What do Agüera y Arcas et al. (2024) and follow-ups report after BFF replicators emerge? Do they claim evolution or open-endedness?

### Takeaway
The BFF source paper documents emergence and take-over, not adaptation. For BFF it reports no parasites, no measured fitness gain and no open-ended evolution. The richer post-emergence stories (succession, "symbiotic ecosystems", long-term differentiation) are anecdotal and come from the Z80 and Forth substrates, not from BFF. The 2026 follow-ups from the same group (preprints) shift attention to recombination/gene transfer and to externally rewarded tasks. That implicitly concedes that plain BFF soups have not been shown to evolve. Emergence Lab's (b) to (e) are therefore new *measurements* on BFF, but they do not contradict the source paper. The source paper never claimed what Emergence Lab fails to find.

### Cited Findings
- BFF primordial soup setup: 2^17 tapes of 64 bytes, no fitness function, default background mutation 0.024% (per byte per epoch), runs of 16k epochs. About 40% of runs show a transition within 16k epochs. Complexity (brotli-based "high-order entropy") rises and then falls to a different distribution. In the case study a "zero-poisoning" period precedes take-over by "a new family of replicators". [FT, arXiv HTML] — [Agüera y Arcas et al. 2024, arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Mutation is not needed: zero background mutation still gives transitions at roughly the same frequency. Random flipping "appears to speed up the process". [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Competition among BFF replicators in the well-mixed soup is not analysed beyond take-over and token/complexity tracking. [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- BFF 2D: 32,400 programs on a 240 × 135 grid, interactions within radius 2. A "wave of self-replicators" overtakes the grid, taking epochs proportional to grid side length (versus about log n when well mixed). The authors call 2D "a fertile ground for multiple variations of self-replicators to co-exist and compete", with no quantitative competition results. [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Forth 2D: after one replicator spreads, "long-term differentiation" follows. After 20k steps three slightly different replicators coexist, and "the soup is never dominated by one individual program". [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Forth long tape: "good" replicators with a long non-functional head and a short functional tail. The authors present this as a robustness/efficiency trade-off. In one example "the only instruction that changed over time was the one before last". A seeded replicator "proceeded to occupy the entire long tape, further complexify, and persist indefinitely" (anecdotal). [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Z80 2D (16-byte programs): stack-based replicators are later overtaken by memory-copy (LDIR/LDDR) replicators. "More and more capable self-replicators or replicator collectives overtake the soup multiple times". "Some of these self-replicators form a sort of symbiotic ecosystems, while other compete for domination". No assays are reported. [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- SUBLEQ: seeded replicators take over, random starts never transition. The authors attribute this to minimum replicator length (60 bytes; 25 in RSUBLEQ4). [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Claims: the paper calls its evidence about later dynamics anecdotal. It poses "How much complexity can spontaneously arise in open-ended computational systems?" as open, and says replicators "tend to remain broadly similar" over time. It makes no open-ended evolution claim. [FT, via fetch summary] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)
- Follow-up 1 (preprint, arXiv 2607.01483, 1 July 2026; Knierim, Versari, Obryk, Agüera y Arcas, Saurous):
  - Tuned random mutation walks find BFF replicators at least as efficiently as pairwise interaction. A secondary summary gives about 5 × 10^6 program tests for the dyadic model, about 6× faster than uniform sampling.
  - Caps on merger depth/width do not block emergence but do stop take-over.
  - The authors say the open problem shifts to post-emergence processes (crossover, horizontal transfer) that drive diversity and complexity.
  - No parasites or open-endedness discussed.
  [SEC, Emergent Mind page, not the PDF] — [Emergent Mind summary of 2607.01483](https://www.emergentmind.com/papers/2607.01483)
- Follow-up 2 (preprint, arXiv 2607.09211, v2 2 September 2026; Cicala, Niklasson, …, Agüera-Arcas, Richards): 32-byte Z80 soups in which correctly evaluating a polynomial raises interaction probability. Reported results:
  - self-replication and function coevolve;
  - compute pressure gives compact replication code;
  - runtime penalties favour conditional execution;
  - task niches create a stepping-stone curriculum.
  This needs an external reward, so it is not a fixed-rule, reward-free soup. No parasites or spatial results in the abstract. [ABS] — [arXiv 2607.09211](https://arxiv.org/abs/2607.09211)
- Commentary (non-peer-reviewed): one blog argues the "pre-life to life" framing adds little to what is essentially a search problem. [SEC] — [Anatol Wegner newsletter](https://buttondown.com/anatol/archive/emergence-of-computational-life/)

### Inferences
- **(c) many small families, drift away from the founder:** consistent with the source paper's Forth 2D "never dominated by one individual program" and BFF "broadly similar" replicators. Label: **partly known qualitatively**; the 2% median and the founder-distance measurements are new quantification.
- **(d) no fitness gain:** the source paper never measured fitness gain in BFF, so there is nothing to conflict with. The only published hint of directional improvement ("more capable" replicators repeatedly overtaking) is for Z80 and is anecdotal. Label: **apparently new** as a measured negative for BFF. It should not be framed as refuting Agüera y Arcas et al.
- The 2026 Z80 preprint gets adaptation only by adding a task reward that changes reproduction. That suggests the group itself did not find reward-free BFF adaptation worth reporting. This is my inference, not their statement.
- Scale comparison:
  - Emergence Lab's soups (2^13 to 2^17, mostly 2^16) are at or just below the source paper's 2^17.
  - Its 256 × 256 lattice (65,536 cells) is about twice the source paper's 240 × 135 grid.
  - 20,000 post-jump rounds are similar to the source paper's 16k epochs and to the 20k steps at which Forth 2D showed differentiation.
  - On BFF scale, then, Emergence Lab is not undersized relative to the source paper. Both are tiny relative to Tierra/Avida evolution timescales (Q2).

### Gaps
- Whether the source paper reports the BFF 2D outcome after the wave (coexistence counts, turnover): not quantified in the text I read.
- Full text of 2607.01483 and 2607.09211 not read.
- No published study found that measures fitness of later versus earlier BFF replicators, parasitism in BFF, or BFF evolutionary activity. Queries tried: "BFF self-replicators computational life follow-up 2025 evolution parasites"; "self-replicating programs primordial soup evolution open-endedness 2025 2026 arXiv BFF Forth spatial parasites" (extended mode). Result: **not found in this search**.

---

## Q2. Tierra and Avida: how parasites, hyper-parasites and complexity arose, under what conditions, at what scale; what may be missing in BFF?

### Takeaway
Tierran parasites came from the instruction set's addressing rules: template matching that searches *other* organisms' memory, plus memory protection that guards writes but not reads/execution. They appeared within the first few million instructions of runs seeded with a hand-written 80-instruction ancestor. Avida's complex traits (EQU) required external rewards for simpler logic functions and many independent populations. Avida host-parasite coevolution, too, was engineered: parasites are a designed class with an imposed infection rule. BFF lacks every one of these levers. It has no persistent bodies to read from, no protected genome, no address-by-template, and no reward. So the absence of parasites and of fitness gain is the expected outcome, not a surprise.

### Cited Findings
- Tierran ancestor 0080aaa:
  - 80 instructions, hand-written as a minimal self-replicator for debugging. "No functionality was designed into the ancestor beyond the ability to self-replicate."
  - 48 of its 80 instructions are no-ops, forming complementary templates at 12 sites for addressing.
  - DIVIDE removes the parent's write privileges on the daughter.
  [FT of the page] — [Ray, Tierra docs, node11](https://tomray.me/pubs/tierra/node11.html)
- Parasite origin and mechanism:
  - Parasites "begin to emerge within the first few million instructions of elapsed time in a run".
  - A one-bit mutation in instruction 42 changes the copy-procedure template, so the mutant 0045aaa computes its size as 45 and lacks the copy procedure.
  - The allocation "membrane" "only protects write privileges", so code in other creatures' memory can be found by template matching and executed.
  - If a host's copy procedure lies within the search limit (generally 200 to 400 instructions), the parasite's instruction pointer is sent into the host's copy code.
  [FT of the page] — [Ray, Tierra docs, node15](https://tomray.me/pubs/tierra/node15.html)
- Sequence and dynamics: parasites, then immunity to parasites, then circumvention, then hyper-parasites that seize the parasite's instruction pointer, then social hyper-parasites and "cheaters" (hyper-hyper-parasites). Host-parasite Lotka-Volterra-like cycling. [ABS of results index + SEC search summary] — [Ray, Tierra docs, results index node12](https://tomray.me/pubs/tierra/node12.html); [Ray, Tierra overview PDF](https://faculty.cc.gatech.edu/~turk/bio_sim/articles/tierra_thomas_ray.pdf)
- Original citation: Ray, T. S. 1991, "An approach to the synthesis of life", Artificial Life II, SFI Studies XI, Addison-Wesley, 371–408. [SEC, reference list] — [Tierra overview PDF](https://faculty.cc.gatech.edu/~turk/bio_sim/articles/tierra_thomas_ray.pdf)
- Avida complexity:
  - Lenski, Ofria, Pennock and Adami (2003, Nature 423:139–144) studied the origin of EQU, the logic function needing the most NAND operations (at least 5).
  - When only EQU was rewarded, no population evolved it. In the reward-all condition a bit over a third did.
  - Complex features never evolved when simpler functions were not rewarded.
  [SEC: course reviews and search summary; I did not read the paper this session] — [Nature 2003](https://www.nature.com/articles/nature01568); [Lenski lab page](https://lenski.mmg.msu.edu/papers/nature2003/index.html)
- Avida host-parasite coevolution (Zaman et al. 2014, PLoS Biology):
  - Coevolution with parasites produced substantially more complex host traits than evolution without parasites.
  - Parasites are a designed class: an infecting parasite takes 80% of the host's CPU cycles, and infection requires host and parasite to share at least one rewarded function.
  - Hosts also evolved greater evolvability.
  [SEC, search summary of PMC full text] — [Zaman et al. 2014, PMC4267771](https://pmc.ncbi.nlm.nih.gov/articles/PMC4267771)
- Plateau: Bedau, Snyder and Packard (1998) classified long-term dynamics as absent, bounded or unbounded evolutionary activity. They suspected that no existing artificial system showed unbounded (class 3) activity; Echo was among those examined. The biosphere's fossil record is cited as class 3. [SEC, search summary] — [Bedau, Snyder & Packard 1998 PDF](https://people.reed.edu/~mab/papers/alife6.pdf)

### Inferences
- **Why BFF lacks parasites (my inference from the mechanism above, not a published BFF analysis):**
  - In Tierra a parasite borrows a *persistent* neighbour's copy loop by reading/executing its memory at a distance, while that neighbour's code is write-protected and survives.
  - In BFF, two tapes are concatenated, run once, and split. A replicator's loop typically writes over the partner half.
  - A loop-less "parasite" would need the partner to copy *the parasite's* half. That inverts the usual BFF copy direction and makes the parasite the overwritten party.
  - There is no protected genome, no template addressing, and no long-range read.
  - (e) "no parasites in 2,800 + 420 programs" is therefore what this mechanistic comparison predicts. Label for (e): **apparently new as a BFF measurement**, but **unsurprising given the Tierra mechanism**.
  - The project should not present (e) as evidence against evolvability in general. It is evidence about BFF's interaction geometry.
- Tierra parasites emerged within a few million *instructions*. A BFF round of 2^16 pairs runs up to tens of millions of steps, so 20,000 rounds is many orders of magnitude more raw computation than Tierra needed for parasites. **On compute, the BFF negative is not a scale artefact. The missing lever is mechanistic.** (Inference: I did not verify BFF step limits here; the project should check its own step cap.)
- Avida's complexity required rewards and stepping stones. Emergence Lab's fixed-rule, reward-free soups are in the condition where Lenski et al. (2003) saw EQU never evolve (EQU-only reward ≈ no gradient for intermediates). Drift without adaptation (d, g) is the literature's expected outcome for reward-free systems with no ecological niches. Label for (g): **consistent with published expectations; the negative itself is new for BFF**.
- Avida evolution experiments typically run thousands to tens of thousands of generations in many replicate populations. Emergence Lab uses 7 soups and 20,000 rounds; the number of generations per round is unknown to me. This is very small replication (7) relative to Lenski et al. 2003's many replicate populations (exact numbers not verified; see Gaps).

### Gaps
- Tierra soup size (my memory: 60,000 instructions), the reaper rule and mutation rates: not verified this session (node pages read did not contain them).
- Ray's "Evolutionary Optimization" results (my memory: evolved replicators far shorter than the 80-instruction ancestor, i.e. a measurable efficiency gain): not fetched. If confirmed, they are a direct published counterexample to "later code is not fitter" in a seeded system. Fetch tomray.me/pubs/tierra results pages under "Evolutionary Optimization".
- Lenski 2003 population sizes and generations: not verified (one search summary's "50,000 generations" was flagged by itself as from memory; do not use it).
- Whether Bedau et al. (1998) classified Tierra specifically: not confirmed.

---

## Q3. The role of space: what does theory predict, at what scales, and is "space does not raise well-mixed fitness" expected?

### Takeaway
The spatial literature predicts something different from what E-78 tested. Space mainly changes *which* replicators persist at the level of patterns and groups (spirals, waves, clusters). It protects cooperators/replicases against parasites. It often selects for *prudent* or slower individual traits that would *lose* in well-mixed competition. So the null result "late lattice code is not fitter in a well-mixed common garden" (f) is what the literature predicts. The literature's main mechanism is resistance to parasites, and BFF has none, so the main lever is missing. The observed mosaic of small local families is the generic outcome of limited dispersal. Label for (f): **expected / partly known**. The direction of the E-78 point estimate (−0.42, lattice code slightly *less* fit when mixed) also matches the prudence prediction, although it was not significant.

### Cited Findings
- Boerlijst and Hogeweg (1991), "Spiral wave structure in pre-biotic evolution: Hypercycles stable against parasites", Physica D 48:17–28, doi 10.1016/0167-2789(91)90049-f. Findings:
  - In a CA, hypercycles of at least 5 species self-organise into spiral waves.
  - Spiral centres seed the whole spiral, so parasites are pushed outward and lost.
  - The spatial pattern stabilises the system against parasites.
  [SEC, search summaries] — [Scilit record](https://scilit.net/publications/efc379f1c182de0a59ce2da66b1de31e); [q-bio/0406035 review](https://ar5iv.labs.arxiv.org/html/q-bio/0406035)
- Takeuchi and Hogeweg (2012), "Evolutionary dynamics of RNA-like replicator systems", Physics of Life Reviews 9:219–263:
  - Well-mixed hypercycles are evolutionarily unstable to parasites.
  - In space, spiral-wave cores alone leave descendants. "This resistance against parasites requires an important condition: populations must be discrete."
  - Replicase–parasite systems form travelling waves whose dynamics give "macroscopic stability despite microscopic (i.e., local) instability".
  [FT, first ~100k characters of the PMC manuscript] — [PMC3466355](https://pmc.ncbi.nlm.nih.gov/articles/PMC3466355)
- Same review, on what space selects for:
  - Between spirals, the fastest-rotating wave wins. Selection then favours improved catalysts and even "replicators that decay quickly".
  - Because rotation slows with more members, "selection tends toward decreasing the amount of information contained in hypercycles".
  - In the spatial replicase–parasite system, parasite parameters drift in directions not expected from the ODE model, and an emergent trade-off keeps fitness roughly constant.
  [FT, partial] — [PMC3466355](https://pmc.ncbi.nlm.nih.gov/articles/PMC3466355)
- Scales in that literature: hypercycle CA lattices of 512 × 512; diffusion 1 (hypercycle) and 0.01 to 0.1 (replicase–parasite); replicase-to-parasite mutation about 10^-4 per replication. Outcomes need "sufficiently low" diffusion and "sufficiently strong" parasites. [FT, partial] — [PMC3466355](https://pmc.ncbi.nlm.nih.gov/articles/PMC3466355)
- Takeuchi and Hogeweg (2009), "Multilevel selection in models of prebiotic evolution II", PLoS Comput Biol 5:e1000542. It compares spatial self-organisation (implicit) with compartments (explicit) as multilevel selection, and finds that the two give different long-term evolutionary trends for identical microscopic entities. [ABS] — [PMC2757730](https://pmc.ncbi.nlm.nih.gov/articles/PMC2757730)
- Kerr, Neuhauser, Bohannan and Dean (2006), Nature 442:75–78, an experiment with phage and bacteria in 96-well plates:
  - Restricted (local) migration favours prudent phage; unrestricted migration favours rapacious phage.
  - Rapacious phage had higher competitive ability but lower productivity.
  - Migration pattern alone decides whether a tragedy of the commons resolves toward restraint.
  [ABS/SEC] — [RePEc record](https://ideas.repec.org/a/nat/nature/v442y2006i7098d10.1038_nature04864.html)
- Kerr, Riley, Feldman and Bohannan (2002), Nature 418:171–174: local dispersal maintains diversity in a rock-paper-scissors community. [ABS] — [Nature 2002](https://www.nature.com/articles/nature00823)
- Szabó, Scheuring, Czárán and Szathmáry (2002), Nature 420:340–343, "In silico simulations reveal that replicators with limited dispersal evolve towards higher efficiency and fidelity", doi 10.1038/nature01187. In a lattice model *with* parasites, limited dispersal let replicases evolve higher efficiency and copying fidelity. [MEM, not fetched; verify]
- Digital example: Agüera y Arcas et al. report that 2D BFF/Forth/Z80 soups allow coexistence and competition of variants, with no fitness assays (see Q1). [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)

### Inferences
- **Well-mixed common-garden assays are the wrong instrument for spatial adaptation, according to this literature.**
  - Spatially selected traits are often group- or pattern-level (wave speed, cluster persistence) or prudent. They are expected to lose, or tie, under mixing (Kerr 2006).
  - The project already concedes this in section 8 ("Well-mixed instruments"). The literature turns the concession into a prediction: a null was the most likely outcome of E-78 even if spatial adaptation occurred.
  - An informative test would score lattice-evolved versus mixed-evolved code *in lattice competition* (e.g. invasion of a lattice resident from a small patch). Spread-speed of fronts is the natural fitness in a lattice (Fisher-wave logic).
- **The main spatial lever in the theory needs parasites** (Boerlijst & Hogeweg; Szabó et al.; Takeuchi & Hogeweg). Where there are no parasites (e), theory gives little reason to expect space to raise replicator quality. The project should say that E-78 tested space in the regime where theory predicts the least effect.
- **Mosaic of small local families (S arm):** limited dispersal with mutation generically produces patchy clonal domains. Takeuchi & Hogeweg's travelling-wave and spiral pictures are examples of the same principle. Label: **known in principle**. The 55% near-identical-neighbour figure is project-specific quantification.
- **Scale:** the project's 256 × 256 lattice is in the same range as the published spatial models (512 × 512) and above the BFF 2D grid (240 × 135). Lattice size is not obviously inadequate. *Time* and *replication* are the weaker axes: 7 soups, and a seed null (M versus M′) that differed as much as M versus S. That is a power problem, as the project itself notes.

### Gaps
- Typical number of generations for spiral or wave patterns to establish in Boerlijst & Hogeweg: not found (the review excerpt gave no times).
- Szabó et al. 2002 and Czárán & Szathmáry's metabolic replicator model (2000, J Theor Biol, [MEM]) not fetched.
- No digital-program study found that compares lattice-evolved and well-mixed-evolved replicators in well-mixed assays. Queries tried: the Q1 extended query; "Takeuchi Hogeweg 2009 multilevel selection parasites RNA replicator spatial pattern". **Not found in this search.**

---

## Q4. Neutral drift, quasispecies, error thresholds, "survival of the flattest": do they predict many small families and drift without fitness gain?

### Takeaway
Partly. Quasispecies theory predicts that at high mutation rates selection acts on mutationally connected *clouds*, not on the best single genotype. Robust (flatter) genotypes can beat faster ones, so drift among near-neutral variants and no rise in single-genotype replication rate are expected there. Whether BFF soups are in that regime depends on the effective mutation rate per copy. That includes copying errors and partner overwrites, not only background flips, and the project has not reported it. The many near-indistinguishable one-byte variants found by the project ((b): 2 of 141 pairs different) point to a highly neutral landscape, and neutral theory predicts drift without adaptation for such a landscape.

### Cited Findings
- Wilke, Wang, Ofria, Lenski and Adami (2001), Nature 412:331–333:
  - 40 pairs of Avida populations from 40 ancestors, one of each pair at 4× higher mutation rate.
  - In 12 pairs the low-mutation dominant genotype replicated faster. Yet when the two competed, the outcome switched toward the slower genotype as mutation rate rose.
  - The slower genotypes sat on lower but flatter peaks, being more mutationally robust ("survival of the flattest").
  [ABS] — [ADS abstract](https://ui.adsabs.harvard.edu/abs/2001Natur.412..331W/abstract); [ScienceDaily release](https://www.sciencedaily.com/releases/2001/07/010719080551.htm)
- Comas, Moya and González-Candelas (2005), BMC Evol Biol 5:5: the critical mutation rate for the switch depends on the initial fitness vector. [SEC] — [BMC Evol Biol 2005](https://link.springer.com/article/10.1186/1471-2148-5-5)
- Eigen (1971), Naturwissenschaften 58:465–523, doi 10.1007/BF00623322: quasispecies and error threshold; beyond a critical error rate per genome, genetic information is lost. [MEM, not fetched]
- BFF default background mutation is 0.024% per byte per epoch, and zero mutation still yields transitions. Self-modification and partner writes dominate variation. [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)

### Inferences
- At 0.024% per byte, background mutation is about 0.015 flips per 64-byte program per epoch, far below an Eigen threshold for a 64-byte genome. But BFF copying is itself sloppy: the project caught "sloppy copiers" at 59 to 60 of 64 bytes (paper section 7). Effective per-copy error may then be several bytes per copy, which *is* the high-mutation, flat-landscape regime where survival of the flattest applies. That would predict:
  - selection for robustness rather than speed;
  - large neutral clouds, i.e. "many small families";
  - no rise in head-to-head race wins.
  This matches (b), (c) and (d). Label: **(c)/(d) consistent with quasispecies/neutral expectations**.
- Consequence for instruments: races and growth-rate assays measure individual replication. They are blind to robustness-based (flatter) advantage, which shows up only in competition *at the soup's mutation rate* over many generations. The project's invasion assays inside the soup partly capture this, but its races and growth assays do not.

### Gaps
- The project's own per-copy error rate (copy fidelity distribution of verified replicators) is not given in `docs/paper.md` sections 5, 8 and 9. This is needed to place BFF relative to the error threshold.
- No published quasispecies or neutral-network analysis of BFF found. **Not found in this search** (queries as in Q1).

---

## Q5. How is open-ended evolution measured, and how do the project's assays compare with standard practice?

### Takeaway
Standard OEE practice measures *system-level* hallmarks over long runs, judged against neutral "shadow" baselines. These are evolutionary activity (Bedau & Packard) and the MODES change, novelty, complexity and ecology metrics (Dolson et al. 2019). Standard *adaptation* practice in digital evolution is competition against a marked ancestor or replication rate measured in isolation. The project's assays (pairwise races, growth into random code, invasion from rare into kin-free backgrounds) test adaptation, not open-endedness. They are reasonable adaptation tests, but none computes the OEE statistics the field uses. So "level 5 not shown" is correct, but the project has not *tested* level 5 by the field's own criteria, only a precondition (directional adaptation).

### Cited Findings
- Bedau, Snyder and Packard (1998), Artificial Life VI, pp. 228–237:
  - Long-term dynamics fall into three classes (absent, bounded, unbounded) defined by diversity, new evolutionary activity and mean cumulative activity, with activity compared against neutral shadow runs.
  - They suspected that no artificial system then showed unbounded activity.
  - The classification became a de facto OEE test.
  [SEC] — [Bedau et al. 1998 PDF](https://people.reed.edu/~mab/papers/alife6.pdf); [RePEc SFI WP 98-03-025](https://ideas.repec.org/p/wop/safiwp/98-03-025.html)
- Dolson, Vostinar, Wiser and Ofria (2019), "The MODES toolbox", Artificial Life 25(1):50–73, doi 10.1162/artl_a_00280:
  - Metrics for change potential, novelty potential, complexity potential and (in the paper) ecological potential, computed on persistent lineages after a persistence filter.
  - C++ implementations provided; validated on NK landscapes and Avida.
  [ABS] — [PeerJ preprint](https://peerj.com/preprints/27249v2); [NSF PAR](https://par.nsf.gov/biblio/10104628)
- Taylor et al. (2016), "Open-ended evolution: perspectives from the OEE workshop in York", Artificial Life 22(3):408–423, doi 10.1162/ARTL_a_00210. Key points:
  - Pluralism about kinds of OEE.
  - Distinguish observable hallmarks from hypothesised mechanisms.
  - Taylor's five basic requirements for OEE.
  [ABS] — [Tim Taylor publication page](https://tim-taylor.com/paper-details/taylor2016openended.html); [Aston record](https://research.aston.ac.uk/en/publications/open-ended-evolution-perspectives-from-the-oee-workshop-in-york/)
- Packard, Bedau, Channon, Ikegami, Rasmussen, Stanley and Taylor (2019), two editorials:
  - "Open-ended evolution and open-endedness", Artificial Life 25(1):1–3.
  - "An overview of open-ended evolution", Artificial Life 25(2):93–103, with a simplified categorisation of OEE.
  [ABS] — [Taylor page](https://tim-taylor.com/paper-details/packard2019openended.html); [CSS digest](https://comdig.cssociety.org/2019/04/08/open-ended-evolution-and-open-endedness-editorial-introduction-to-the-open-ended-evolution-special-issue/)
- Stanley, Lehman and Soros (2017), "Open-endedness: the last grand challenge you've never heard of" (O'Reilly Radar essay). Stanley (2019), "Why open-endedness matters", Artificial Life 25(3):232–235. [ABS] — [O'Reilly](https://oreilly.com/radar/open-endedness-the-last-grand-challenge-youve-never-heard-of)
- Zaman et al. (2014) used phenotypic complexity (number and difficulty of logic tasks) and evolvability as outcome measures for hosts with versus without parasites. [SEC] — [PMC4267771](https://pmc.ncbi.nlm.nih.gov/articles/PMC4267771)
- Channon's work applying activity statistics to Geb: [MEM]; not fetched (Channon's papers are hosted on Keele's repository, e.g. [Keele output 463185](https://keele-repository.worktribe.com/OutputFile/463185), title not confirmed).

### Inferences
- **Instruments versus field practice:**
  - The project lacks (i) evolutionary activity with a shadow/neutral model;
  - (ii) MODES-style persistent-lineage novelty and complexity counts;
  - (iii) a long, replicated, ancestor-versus-descendant competition series (LTEE-style fitness trajectory).
  - Its invasion-from-rare in kin-free backgrounds is closer to ecological invasibility analysis. That is a legitimate and stricter test of individual fitness than single races.
  - Recommended additions: an activity statistic against a neutral shadow soup, and MODES change/novelty on lineages that pass a persistence filter.
- **Calibration and power:** the project states its assays were calibrated on hand-made variants with large effects (section 5). Published adaptation detection in Avida relies on many replicate populations and long runs, so 7 soups is small. The project's negative cannot rule out small effects. Plainly: (d) is "no large effect detected at n = 7", not "no adaptation".
- (g) Label: "level 5 not shown" is **consistent with the literature's general verdict** that artificial systems rarely or never show unbounded activity (Bedau et al. 1998). It is not a novel conclusion about artificial life generally, only about BFF.

### Gaps
- Recent (2023–2026) OEE reviews: not found in this search beyond the 2019 editorials. The arXiv 2405.18016 "On creativity and open-endedness" surfaced but was not read [ABS-title only] — [arXiv 2405.18016](https://arxiv.org/html/2405.18016v4). Queries tried: "Stanley Lehman Soros open-endedness last grand challenge; Packard 2019 …". A dedicated 2024–2026 OEE review search is still needed.
- Channon (Geb, unbounded activity claims) not read.

---

## Q6. Kin effects and frequency dependence in replicator competition assays: is the project's kinship confound known?

### Takeaway
As a general principle, yes. Fitness that depends on the interaction partner is frequency- and assortment-dependent. Local or assorted interaction among relatives is the core of kin selection and of the spatial multilevel selection results above, so an "advantage" that appears only where a type has relatives in the background is the textbook signature of assortment, not of intrinsic fitness. I found no digital-evolution paper that names this as a confound in replicator invasion assays specifically. The project's kin-free control is an appropriate fix, and the confound itself is not new in principle.

### Cited Findings
- Interaction-dependent outcomes in spatial and assorted populations:
  - restricted migration changes which strategy wins (Kerr et al. 2006);
  - spatial self-organisation acts as implicit multilevel selection (Takeuchi & Hogeweg 2009).
  [ABS] — [Kerr et al. 2006](https://ideas.repec.org/a/nat/nature/v442y2006i7098d10.1038_nature04864.html); [PMC2757730](https://pmc.ncbi.nlm.nih.gov/articles/PMC2757730)
- In BFF, reproduction happens only through pairwise execution on a shared tape, so a program's success depends on its partner's code by construction. [FT] — [arXiv 2406.19108](https://arxiv.org/html/2406.19108)

### Inferences
- In BFF, a partner that is a relative will often run a compatible copy loop that writes the focal's own sequence. A "later" program invading a soup of its own descendants/relatives therefore gains from partners that copy it: kin assortment. The E-52 to E-53 reversal (p = 0.045 vanishing to p = 0.88 when kin-free) is exactly what this predicts. Label: **known in principle (kin/assortment effects); its detection in BFF assays is apparently new**.
- Standard digital-evolution fitness assays avoid this by competing against a *marked ancestor* at fixed ratios, or by measuring replication in isolation (Avida test CPU). BFF cannot run in isolation, because replication needs a partner. The kin-free background is a reasonable substitute. A further control would be a fixed, inert or standard partner panel.

### Gaps
- No paper found that discusses kinship confounds in invasion assays for interaction-based program soups. Queries tried: the Kerr 2006 query; the Q1 queries. **Not found in this search.**
- Lenski et al. (1991) marked-ancestor competition protocol not fetched [MEM].

---

## Q7. Synthesis: labels for (a) to (g) and adequacy of instruments and scale

### Takeaway
None of (a) to (g) conflicts with published work.
- Most are either new BFF-specific measurements of things the source paper never measured, or negatives the wider literature would predict.
- The most important blunt point: (e) and (f) are close to *expected* given the mechanisms that produced parasites in Tierra and the predictions of spatial theory. E-78 used an instrument (well-mixed assay) that the spatial literature predicts is blind or biased against spatial adaptation.
- Scale versus the BFF source paper is comparable. Scale versus Avida-style adaptation studies (replicates, generations) is far smaller.

### Cited Findings
- See Q1 to Q6 for sources. Key anchors:
  - [arXiv 2406.19108](https://arxiv.org/html/2406.19108) [FT]
  - [Tierra node15](https://tomray.me/pubs/tierra/node15.html) [FT]
  - [Takeuchi & Hogeweg 2012](https://pmc.ncbi.nlm.nih.gov/articles/PMC3466355) [FT partial]
  - [Wilke et al. 2001](https://ui.adsabs.harvard.edu/abs/2001Natur.412..331W/abstract) [ABS]
  - [Kerr et al. 2006](https://ideas.repec.org/a/nat/nature/v442y2006i7098d10.1038_nature04864.html) [ABS]
  - [Bedau et al. 1998](https://people.reed.edu/~mab/papers/alife6.pdf) [SEC]
  - [MODES](https://peerj.com/preprints/27249v2) [ABS]

### Inferences

| Claim | Proposed label | Basis |
|---|---|---|
| (a) heredity of one-byte mutants, 140/141 | **Apparently new as a systematic BFF test**; the concept is standard (heredity of variation is the Avida/Tierra baseline) | Source paper shows take-over by replicator families but no mutant-level heredity test (Q1) |
| (b) variants mostly neutral; one fitter species | **Partly known**: a neutral landscape is consistent with quasispecies/neutral theory and with "broadly similar" replicators in the source paper; the quantitative race result is new | Q1, Q4 |
| (c) no dominant family (~2%), founder drift | **Partly known qualitatively** (Forth 2D "never dominated by one program"); the quantification is new | Q1 |
| (d) later code not fitter; kin artefact | **Apparently new for BFF**; *expected* for reward-free systems without ecological niches (Avida needed rewards, Lenski 2003) and for high-error, flat landscapes (Wilke 2001); kin confound **known in principle** | Q2, Q4, Q6 |
| (e) no parasites | **Apparently new measurement; predicted by mechanism**: Tierran parasites required read/execute access to persistent, write-protected neighbours and template addressing, all absent in BFF | Q2 |
| (f) lattice did not raise well-mixed fitness; mosaic of local families | **Expected from spatial theory** (spatial selection acts on patterns, protects against parasites, favours prudence that loses under mixing); mosaic **known in principle**; the specific test is new but low-power and uses an instrument theory predicts is blind | Q3 |
| (g) level 5 not shown | **Consistent with the published consensus** that artificial systems rarely or never show unbounded activity (Bedau 1998); the project has not applied standard OEE statistics, so this is "not tested by field criteria" as much as "not shown" | Q5 |

**Adequacy, plainly:**
- **Soup and lattice size:** comparable to the BFF source paper (2^16 to 2^17; 256² versus 240 × 135). Adequate *for BFF*.
- **Replication:** 7 soups is far below digital-evolution norms (dozens of replicate populations, e.g. 40 pairs in Wilke et al. 2001). The M versus M′ seed null shows the design cannot separate space from noise.
- **Time:** 20,000 rounds is similar to the source paper but short for adaptation studies measured in thousands to tens of thousands of generations. Generations per round were not computed.
- **Instruments:**
  - Well-mixed assays cannot see spatial adaptation (theory-predicted).
  - Races and growth assays cannot see robustness ("flattest") advantages.
  - No Bedau activity or MODES statistics were computed.
- **Mechanism:** BFF lacks the instruction-set features that made Tierra parasites possible. The negatives are as much about BFF's design as about emergent evolution.

### Gaps
- Verify the [MEM] items before citation: Eigen 1971; Szabó et al. 2002; Lenski 2003 numbers; Ray's evolutionary optimization results; Channon.
- Number of BFF generations per round in the project's soups: not available; it is needed to compare with Avida/Tierra generation counts.
- A search for post-2023 OEE reviews and for any 2025–2026 BFF post-emergence work beyond the two Google preprints is incomplete.
