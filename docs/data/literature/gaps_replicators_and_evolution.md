# Gaps in the replicator and post-replicator literature: closing searches and source verification

Search date: 16 November 2026. These notes close gaps left by `program_soups_and_replicators.md` and `after_replicators_open_ended_evolution.md`, and they do not repeat those notes. Reading level for every source:
- **FULL**: full text read in this session, either arXiv HTML through the fetch tool or a PDF downloaded and converted with `pdftotext` and searched directly.
- **ABS**: abstract or bibliographic record only, through Europe PMC, the arXiv API or Semantic Scholar.
- **SEC**: a secondary summary, such as a search-engine synthesis, a third-party page or another paper describing the work.

Preprints are marked **(preprint)**.

---

## Q1. Spontaneous replicators before 2024: Coreworld and Pargellis's Amoeba

### Takeaway
Spontaneous emergence of self-replicators from random code is about 35 years old: Coreworld in 1990, Pargellis in 1996, Hutton's Squirm3 in 2002, and Greenbaum and Pargellis in 2017. I could not get the full text of any Coreworld or Pargellis paper in this search: Elsevier and MIT Press pages were closed, and core.ac.uk, MIT Direct and Nokia all returned 403. Everything below about their rates is ABS or SEC.
- The one rate figure found is a 1996 trade-press account of Pargellis: about "one-in-10,000" random cells can self-replicate.
- No source seen reports a waiting-time distribution, an exponential fit, or a dependence of emergence rate on population size.
- No source seen offers a rule-level predictor of which variants give replicators. Pargellis's stated aim was "to determine the factors that optimize the probability of generating self-replicators", but I did not see his answer.

### Cited Findings
- **Coreworld citation (verified as a citation only).** S. Rasmussen, C. Knudsen, R. Feldberg, M. Hindsholm, "The coreworld: emergence and evolution of cooperative structures in a computational chemistry", Physica D 42(1–3):111–134 (1990). Sources: [search summary](https://en.wikipedia.org/wiki/Digital_organism), SEC; the same reference appears in AyA2024's bibliography, [arXiv 2406.19108](https://arxiv.org/html/2406.19108), FULL.
- **What AyA2024 itself says about Coreworld** (this upgrades the earlier notes from SEC to FULL for AyA's description, not for Coreworld itself):
  - "Some simple self-replicators of two instructions (MOV-SPL) often take over."
  - When a functioning self-replicator is seeded, "self-replicators do not take over".
  
  [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- **What AyA2024 says about Pargellis:** "the author observes and quantifies the likelihood of self-replicators to arise with a given environment". The rise is attributed to "either random initialization or to random mutations of imperfect self-replicators". AyA2024 does not name Amoeba — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- **Secondary accounts of Coreworld disagree on how much evolution it showed.** One says Coreworld "succeeded in facilitating the evolution of populations"; another says complex, stable programs were not observed; a third says runs were too short and populations too small. I could not check any of these against the original — [search summary incl. arXiv 1105.1534 and Frontiers 2021](https://arxiv.org/pdf/1105.1534), SEC. The core.ac.uk technical report (https://core.ac.uk/download/216514147.pdf) returned HTTP 403.
- **Pargellis 1996a, "The spontaneous generation of digital 'Life'"**, Physica D 91:86–96, doi 10.1016/0167-2789(95)00268-5. Semantic Scholar lists the abstract as elided and the PDF as closed — [Semantic Scholar API record](https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/0167-2789(95)00268-5?fields=title,authors,year,venue,abstract,citationCount,openAccessPdf), ABS (metadata). A search-engine abstract excerpt says:
  - digital cells "spontaneously emerge from a primordial 'soup', initially composed only of random sequences";
  - mutations then drive them "to evolve into more efficient and complex organisms" competing for CPU time and memory.
  
  [search summary of the abstract](https://portal.mardi4nfdi.de/wiki/Item:Q1909511), SEC.
- **Pargellis 1996b, "The evolution of self-replicating computer organisms"**: Physica D, dated 30 October 1996, doi 10.1016/0167-2789(96)00089-9. Metadata only; no abstract found — [MaRDI record](https://portal.mardi4nfdi.de/wiki/Publication:1814690), ABS (metadata).
- **Numbers from a 1996 SIGNAL Magazine article on Pargellis, reposted on a mailing list by B. D. Harper, 29 April 1996.** These are SEC, at two removes from the paper:
  - Each experiment starts with 40 random cells of 1 to 25 operations, from 16 possible operations. Memory holds up to 1,000 cells of at most 30 operations.
  - A reaper kills about a third of cells each generation.
  - A random cell has about a "one-in-10,000" chance of being able to self-replicate. If no cell reproduces, 40 more random cells are added after a set period.
  - More than 100 experiments were run.
  - About 10% of offspring carry a mutation, and about 97% of mutations are non-viable.
  - After emergence, average cell size falls quickly as useless code is shed.
  - Small "viruses" of 2 to 3 instructions appear, and colonies are "often swarmed by parasites".
  
  [asa3.org archive post](https://asa3.org/archive/evolution/199604/0408.html), SEC. A second post quotes New Scientist: "3 per cent" of cases gave replicating code. The context of that 3% is unclear — [search summary of asa3.org 199604/0399](https://www.asa3.org/archive/evolution/199604/0399.html), SEC.
- **Pargellis 2001 and 2003 (metadata only):**
  - Pargellis, "Digital life behavior in the Amoeba world", Artificial Life 7(1), doi 10.1162/106454601300328025. Semantic Scholar gives the year as 2000.
  - Pargellis, "Self-organizing genetic codes and the emergence of digital life", Complexity (2003), doi 10.1002/cplx.10095.
  
  Abstracts elided — [Semantic Scholar search](https://api.semanticscholar.org/graph/v1/paper/search?query=Pargellis%20digital%20life&fields=title,authors,year,venue,abstract,externalIds&limit=20), ABS (metadata). A Bell Labs listing (June 2000) describes Amoeba as "Tierra-like", with a 32-opcode, computationally universal basis set and codon-to-opcode assignment — [search summary of Nokia Bell Labs pages](https://www.nokia.com/bell-labs/publications-and-media/publications/spontaneous-generation-and-colony-formation-in-the-amoeba-world), SEC (the direct fetch returned 403).
- **Greenbaum and Pargellis 2017**, "Self-replicators emerge from a self-organizing prebiotic computer world", Artificial Life 23(3):318–342, doi 10.1162/ARTL_a_00234. The ALIFE 2016 conference version is doi 10.7551/978-0-262-33936-0-ch016, pp. 60–67. The abstract describes three stages: the opcode basis set becomes biased, short building blocks spread, then the blocks combine into self-replicators. Self-organisation is measured by opcode frequencies, sequence-size distribution and mutual information. No rates appear in the abstract — [search summary of abstract and Crossref](https://api.crossref.org/works/10.1162%2FARTL_A_00234), ABS.
- **No 2017–2025 Amoeba work beyond Greenbaum and Pargellis 2017 / ALIFE 2016 turned up.** Queries:
  - "Pargellis spontaneous generation of digital life Physica D 1996 Amoeba self-replicating rate"
  - "Greenbaum Pargellis ... Artificial Life 2017"
  - "Greenbaum Pargellis 'Digital replicators emerge...' ALIFE 2016 pdf"
  - Semantic Scholar "Pargellis digital life"
  
  Not found in this search.
- **LaBar, Hintze and Adami 2016**, "Evolvability tradeoffs in emergent digital replicators", Artificial Life 22:483–498 ([arXiv 1511.07959](https://arxiv.org/abs/1511.07959)), ABS. It evolves Avida replicators that were found as "rare randomly-assembled self-replicators", not designed ones. It reports two classes: one more evolvable in replication efficiency, the other in acquiring innovations. This is a direct published precedent for studying **post-emergence evolution of spontaneously arising replicators**. The earlier notes did not list it.

### Inferences
- Pargellis's reported setup re-injects random cells until a replicator appears. That is close to the "wait for one rare event" picture. But nothing I could read states an exponential waiting time, a per-cell rate, or a population-size scaling. Treat the project's "one rate per pair run, exponential waits, scaling with population" as **not found in this search** in the pre-2024 digital-life literature. It is not established as novel, because the Pargellis Physica D full texts were not read.
- Pargellis (SEC) and AyA2024 (Coreworld, FULL) both describe tiny replicators: 2-instruction MOV-SPL in Coreworld, and 5-operation self-contained cells and 2–3-instruction "viruses" in Amoeba. Parasites appearing after emergence is reported for Amoeba (SEC). That contrasts with the project's BFF "no parasites" finding and supports the earlier notes' view that parasitism depends on the substrate's mechanics.

### Gaps
- Full texts of Rasmussen et al. 1990 and Pargellis 1996a, 1996b, 2001 and 2003 were not read. Elsevier, MIT Press and Wiley are closed; core.ac.uk, direct.mit.edu and nokia.com returned 403. Their rates, waiting-time data and size dependence are unverified. **Do not cite numbers from them except as "reported in secondary accounts".**
- The "one-in-10,000" figure is from trade press, not the paper. Its meaning ("able to self-replicate" for a random cell) is ambiguous.

---

## Q2. Artificial chemistries: AlChemy, Stringmol, Hutton, and language-level predictors

### Takeaway
- **AlChemy:** self-copying functions (chiefly identity) dominate unless they are suppressed by syntactic filters. That was the route to Level 1 organisations.
- **Squirm3 (Hutton 2002):** the reactions are **designed** so that any chain `e8{x1}*f1` replicates. Spontaneous emergence then needs only "cosmic ray" state flips, and the first replicator appears at about 400,000 iterations in one illustrated run. After that, selection only shortens replicators.
- **Stringmol (Hickinbotham, Stepney and Hogeweg 2021):** runs are **seeded with a hand-designed replicator**. Parasites arise "almost immediately", 12 of 20 spatial runs go extinct, and the surviving runs evolve complex anti-parasite strategies.
- **Language-level predictors:** none of these works predicts replicator emergence from properties of the language. The nearest are Kruszewski and Mikolov's hypothesis (an auto-catalysed, Turing-complete reaction subset) and Mathis et al.'s finding that initial-condition generators decide AlChemy outcomes.

### Cited Findings
- **Fontana and Buss 1994**, PNAS 91(2):757–761, doi 10.1073/pnas.91.2.757. The abstract states three features expected to recur if "the tape were run twice":
  1. Hypercycles of self-reproducing objects arise.
  2. If self-replication is inhibited, self-maintaining organisations arise.
  3. These can combine into higher-order organisations.
  
  [PMC43028](https://pmc.ncbi.nlm.nih.gov/articles/PMC43028), ABS (the body is scanned images).
- **Mathis, Patel, Weimer and Forrest**, "Self Organization in Computation & Chemistry: Return to AlChemy", arXiv 2408.12137 (v2; **preprint**), [arXiv HTML](https://arxiv.org/html/2408.12137), FULL for about 96% of the text. On the original AlChemy:
  - The Level 0 fixed point is "dominated by copy functions", especially identity, which "quickly takes over". The number of unique expressions drops toward one.
  - Level 1 appeared only after syntactic filters blocked copy actions; its members do not copy themselves directly.
  
  New results:
  - Some Level 0 runs end with "10s–100s" of unique expressions (one about 380).
  - Replacing 50% of expressions with identity still collapsed; 99.9% replacement gave "relatively long transients".
  - Setup: 1,000 expressions, 10^6 collisions per stage.
  - The initial-condition generator decides outcomes: a permutation-based generator collapsed to an identity fixed point.
  - No predictor from properties of the language.
- **Vimal, Mathis, Weimer and Forrest 2025**, "Prebiotic functional programs: endogenous selection in an artificial chemistry", arXiv 2509.03534 (**preprint**), ABS. It steers AlChemy without an external fitness function and synthesises Church addition and successor. It cites AyA2024 but does not address replicator emergence rates.
- **Hutton 2002**, "Evolvable self-replicating molecules in an artificial chemistry", Artificial Life 8(4):341–356, doi 10.1162/106454602321202417 ([PDF](https://faculty.cc.gatech.edu/~turk/bio_sim/articles/hutton_rep_molecules.pdf)), FULL:
  - Replication is designed in: "any string of a1's, b1's, c1's and d1's with an e8 at one end and an f1 at the other will replicate ... This is by design".
  - Of the 7,200 possible reaction inputs, 188 are non-null.
  - Spontaneous emergence (experiment 3): a 100 × 100 world of random atoms in state 0, with p_cosmic = 0.00001 per atom per timestep. The reaction rate jumps when the first replicators appear "at around 400000 iterations". This is one run; no rate or distribution is given.
  - After emergence: "the only selection pressures encountered have been towards shorter molecules". "After optimal replicators become prevalent we see no further evolution."
- **Hickinbotham, Stepney and Hogeweg 2021**, "Nothing in evolution makes sense except in the light of parasitism: evolution of complex replication strategies", R. Soc. Open Sci. 8:210441, doi 10.1098/rsos.210441 ([White Rose PDF](https://eprints.whiterose.ac.uk/176868/1/rsos.210441.pdf)), FULL:
  - Seeded: "The system is initially 'seeded' with hand-programmed replicators". There are 100 seed strings of length 65.
  - Arena of 12,500 cells (100 × 125 or 250 × 50 torus); 20 runs to 2 × 10^6 timesteps; **12 of 20 went extinct**.
  - The paper says earlier well-mixed Stringmol "rapidly evolve[s] to extinction, due to the evolution of faster replicating parasites".
  - Survivors evolve slower replication, higher effective mutation rates and self/non-self checks. Complexity cycles as parasites wax and wane.
  - Fitness is "intrinsic and implicit": there is no task.
  - The assembly language has 33 opcodes, 7 of them functional.
- **Kruszewski and Mikolov**, "Emergence of self-reproducing metabolisms as recursive algorithms in an artificial chemistry", arXiv 2103.08245 (**preprint**, v Dec 2021), [arXiv abstract](https://arxiv.org/abs/2103.08245), ABS. Combinatory-logic chemistry with conservation laws. From a "tabula rasa state", one run produces structures that self-reproduce each cycle. The hypothesis is that emergence requires an auto-catalysed subset of Turing-complete reactions. No frequency is reported.

### Inferences
- AlChemy, Squirm3 and Coreworld all show that **trivial or minimal copiers are the default attractor** wherever they exist in the language: identity in AlChemy, MOV-SPL in Coreworld, the shortest chain in Squirm3. This parallels AyA2024's Forth one-byte replicator and 8080 two-byte repeats, and the project's SUBLEQ periodic tiles.
- None of these papers has a quantitative rule-level predictor tested prospectively across language variants, like the project's F, tile density or R_P. Status: **not found in this search**. Queries:
  - "Fontana Buss ... self-copying lambda expressions"
  - "Stringmol Hickinbotham emergence of replicators parasites spontaneous"
  - "Hutton 2002 ... squirm3"
  - arXiv 2408.12137 and 2103.08245 read
  
  Typogenetics and Fontana and Buss's "Arrival of the fittest" (Bull. Math. Biol. 1994) were not read.
- Stringmol and Hutton both run spatially. Their parasites (Stringmol) and their only-shorter evolution (Squirm3) bracket the BFF outcome: no parasites, drift without fitness gain.

### Gaps
- Fontana and Buss 1994 (PNAS and Bull. Math. Biol.) full texts were not read. The "copiers suppressed by filters" detail rests on Mathis et al.'s description (FULL of Mathis, SEC for Fontana).
- Stringmol's emergence of replicators from random strings: not found. The published work is seeded.

---

## Q3. Papers citing Agüera y Arcas et al. 2024, and the two 2026 preprints

### Takeaway
Semantic Scholar lists **29 citing papers** as of 16 November 2026. Only four come from the BFF/Z80 "computational life" line, all preprints by the Google/Paradigms of Intelligence group: Knierim 2026, Cicala 2026, Jha 2026, and indirectly the 2024 paper itself. In this search, **none** measures emergence rate against soup size, analyses reverse or palindromic copying with head positions in soups, measures post-emergence fitness trends in BFF, or tests parasites in BFF.
- **arXiv 2607.01483 (Knierim et al.)** is confirmed (FULL). Its main variant is `bff_selfmove`. It reports **means only** (no waiting-time distribution) and analyses no soup size. Heads 64 apart are favoured through a sampling trick.
- **arXiv 2607.09211 (Cicala et al.)** is confirmed (FULL). It uses **spatial** 32-byte Z80 soups (32 niches of 128 × 128) with a task reward. It gives **no** count of epochs or interactions to the first replicator and no soup-size dependence. Load–Push replicators are later displaced by LDIR. Parasites are not discussed.

### Cited Findings
**Citation scan.** Source: [Semantic Scholar citations API for arXiv:2406.19108](https://api.semanticscholar.org/graph/v1/paper/arXiv:2406.19108/citations?fields=title,authors,year,venue,externalIds&limit=1000), ABS (list).
- Citing items relevant to replicators, with arXiv API abstracts read ([arXiv API](http://export.arxiv.org/api/query?id_list=2607.02954,2509.03534,2610.12251,2609.10817,2607.28250,2412.17799&max_results=10)):
  - **Jha, Cicala, Agüera y Arcas, Richards, Jaques, Kleiman-Weiner, Niklasson**, "Tapes Together Strong", arXiv 2609.10817 (9 Sep 2026, **preprint**), ABS:
    - random Z80 programs with a social dilemma embedded in the physics;
    - "parasitic stealing" destroys shared energy and can block replication;
    - evolved programs suppress stealing;
    - "spatial assortment supports structural complexity".
    
    This is the only citing work found that mentions **parasites** and **space**, but it is Z80 with designed energy mechanics, not BFF.
  - **Norton**, arXiv 2610.12251 (**preprint**): designed universal constructors in threshold networks; not emergence. ABS.
  - **Pigozzi and Levin**, arXiv 2607.28250 (**preprint**): GARD compositional replicators; causal emergence predicts later replication. ABS.
  - **Tensen et al.**, Microcosmos, arXiv 2607.02954 (**preprint**): a GPU filament simulator. ABS.
  - **Kumar et al.**, ASAL, arXiv 2412.17799: foundation-model search of CA/Lenia/Boids. ABS.
  - **Ashford et al.**, arXiv 2603.08463 (**preprint**): Barricelli symbiogenesis replication in 1D/2D CAs; no BFF. ABS.
- The remaining citing items are reviews, perspectives or unrelated work (Kauffman 2025 Phil Trans B; López-Díaz 2025 J R Soc Interface on semantic closure; Thomas 2026 PCJ; Abramsky 2025; etc.) — titles only from the [Semantic Scholar list](https://api.semanticscholar.org/graph/v1/paper/arXiv:2406.19108/citations?fields=title,authors,year,venue,externalIds&limit=1000), ABS.
- Google Scholar was not queried, because there is no API and it blocks automated fetches. Semantic Scholar coverage may miss workshop papers.

**arXiv 2607.01483, "BFF: Simple explanations for complex phenomena"** (**preprint**), by Charlotte Knierim, Luca Versari, Robert Obryk, Blaise Agüera y Arcas and Rif A. Saurous. v1 only, submitted 1 July 2026, cs.NE. Sources: [abs](https://arxiv.org/abs/2607.01483), [HTML](https://arxiv.org/html/2607.01483), FULL.
- **Head offsets:**
  - Heads 64 apart "start in the same location in the first and second program", which eases exact copying.
  - Experiment 3.8 (CUST64) adds byte value 64 to the operator class to make heads exactly 64 apart easier to reach.
  - A footnote mentions a program whose heads are "two apart", so each execution shifts it by two.
  - Head start rules of `bff`, `bff_noheads` and `bff_selfmove` are **not** discussed, and `bff_noheads` is never mentioned.
- **Variant:** `bff_selfmove`, which "automatically moves the read head on a copy". Other variants gave "very similar results", but they are unnamed.
- **Interactions to the first replicator:** about 2.5 × 10^6 interactions, or 5 × 10^6 programs tested, averaged over 100 seeds (Experiment 3.1).
  - **Only means are reported.** There are no histograms and no exponential fit.
  - A variance "on the order of at most 10^3" is mentioned for a beta-prior comparison.
- **Soup size:** not analysed. "Different soup sizes" appears only in a list of variants that gave similar results.
- **Mutation-only random walks:** the random-walk process mutates every byte with probability p each step. Expected programs tested per replicator (Table 1; 10^10 programs per entry):

  | p | Uniform | BFF-fitted | CUST | CUST64 |
  |---|---|---|---|---|
  | 1/200 | 9.5×10^8 | 3.5×10^7 | 7.9×10^6 | 1.9×10^6 |
  | 1/100 | 4.4×10^8 | 1.9×10^7 | 4.1×10^6 | 9.9×10^5 |
  | 1/50 | 2.0×10^8 | 1.0×10^7 | 2.1×10^6 | 5.2×10^5 |
  | 1 (independent sampling) | 2.9×10^7 | 1.7×10^6 | 4.5×10^5 | 9.4×10^4 |

  - CUST64 "beats running the BFF system even for p=1/200".
  - With uniform bytes, **mutation-only walks are slower than the soup**: 9.5 × 10^8 at p = 1/200 against 5 × 10^6. The "at least as easily" claim depends on the tuned sampling distributions.
  - The text's factors ("about 6 times slower", "factor of 3", "factor of 10", "roughly a factor of 25") partly disagree with the table ratios to 5 × 10^6. CUST64 gives about 53, not 25.
- **Detector:**
  - A chain of 5 executions per Algorithm 1, but the text says it "collect[s] the nine final tapes" (an internal inconsistency).
  - The score runs from 0 to 64, and a replicator needs at least 48. Results are "not significantly" changed for thresholds of about 20 or more.
  - A byte matches if it agrees in at least 3 final tapes. The minimum over the two halves is taken.
  - The odd chain length catches self-inverting replicators.
  - It checks exact positions only, so shifted "semi-replicators" are not counted.
- **Post-emergence:**
  - It distinguishes appearance from gelation or take-over: a replicator can "appear but die out".
  - Blocking mergers stops take-over.
  - Crossover and horizontal gene transfer analogues are called "an open problem".
  - **No** parasites, fitness or diversity analysis.

**arXiv 2607.09211, "Coevolution of self-replication and function in a digital primordial soup"** (**preprint**), by Francesco Cicala, Eyvind Niklasson, Ettore Randazzo, Sami Boukortt, Alessio Basti, Mayalen Etcheverry, Rif A. Saurous, Ben Laurie, James Manyika, Blaise Agüera-Arcas and Blake Richards. v1 10 July 2026; v2 2 September 2026. Sources: [abs](https://arxiv.org/abs/2607.09211), [HTML](https://arxiv.org/html/2607.09211), FULL (both halves read).
- **Setup:**
  - 32-byte Z80 programs, 2^19 programs in 32 niches. Each niche is a 128 × 128 grid with von Neumann pairing.
  - 5% of partners are drawn from any niche ("cross-niche pollination").
  - Mutation: 1/64 chance per program per epoch of one random byte.
  - A pair is concatenated into a 64-byte tape and executed from byte 0 for up to 512 instructions.
  - Passing a polynomial-evaluation task raises interaction probability from 0.3 to 1.0, minus a runtime penalty C·k/B with C = 0.3 and B = 512.
  - Runs last 10^6 epochs. Most conditions use 100 seeds; the ancestor analysis uses 2,000.
- **Timing to the first replicator:** not quantified. There is no interaction count and no soup-size analysis.
- **Head or pointer offsets:** not discussed in the BFF sense. Registers start at fixed values (HL, BC, E, PC = 0; SP = 0xFF), and the LDIR replicator sets HL and DE to the two program starts.
- **Mutation-only control:** none. The closest is a "hard-wired copy" control in which the partner is overwritten with an exact copy and no Z80 code runs, so mutation is the only source of heritable change. On cubic tasks, hard-wired copy solves 21.0–30.8% against 3.8–7.0% for emergent replication (N = 2,000).
- **Post-emergence:**
  - Load–Push replicators appear first.
  - LDIR replicators later take over. This happens without tasks too, but more slowly.
  - Robustness to 1, 4 or 8 mutations ranks LDIR ≫ LDD ≫ Load–Push.
  - With LDIR blocked, the LDD transition fails within 10^7 epochs without tasks.
  - LDDR (reverse block copy) is searched for but not reported as dominant.
  - Parasites are **not discussed**. Most dominant replicators inspected were asexual.
- **No-task baseline:** confounded, because every program interacts with probability 1 rather than 0.3.

**Corrections to the earlier notes.**
- `after_replicators...md` Q1 cited 2607.01483 only through Emergent Mind (SEC) and 2607.09211 at ABS. Both are now FULL.
- The SEC claim "about 6× faster than uniform sampling" matches the paper's text: 2.9 × 10^7 / 5 × 10^6 ≈ 5.8.
- `program_soups...md` stated that 2607.09211 was read only for the first ~100k characters. The rest has now been read; it adds no timing or soup-size data.

### Inferences
- Measuring emergence rate against soup size, with an explicit per-interaction rate, remains **not found in this search**. Knierim's per-interaction framing assumes it, but the paper shows no data.
- The **only published BFF-family timing is a mean, for `bff_selfmove`**. No published waiting-time distribution exists for any BFF variant (consistent with the earlier notes).
- Post-emergence evolution in the Google line moved to Z80 with rewards or energy mechanics. There, replicator **mechanism** turnover is reported (Load–Push to LDIR), plus parasitic "stealing" in Jha 2026 (ABS). That is evidence of mechanism-level succession that BFF has not shown.

### Gaps
- Google Scholar citations were not checked. Semantic Scholar's 29 may be incomplete, especially for ALIFE 2025/2026 proceedings.
- Jha 2026 was read at abstract level only.

---

## Q4. Verification of evolution sources tagged MEM, ABS or SEC in the earlier notes

### Takeaway
Most key claims hold. Corrections:
- **Ray's evolutionary optimisation is now verified:** the 80-instruction ancestor at 839 CPU cycles per replication evolved to a 22-instruction creature at 146 cycles, a **5.75-fold** gain.
- **Lenski 2003 numbers are verified:** 3,600 individuals, 50 populations, 23 of 50 evolved EQU in reward-all, 0 of 50 in EQU-only, 100,000 updates ≈ 15,873 ancestral generations.
- **Wilke 2001 is verified at abstract level** (40 pairs, 4-fold mutation difference, 12 disparate pairs). The genomic rates 0.5 and 2.0 come from the 2018 replication, **not** from the original abstract.
- **Szabó 2002 and Kerr 2006 are verified at abstract level.**
- **Bedau, Snyder and Packard 1998 is verified in full.** It examined **only Echo**, its neutral shadow, and the fossil record; it did **not** classify Tierra. The "no artificial system" statement is a suspicion, not a finding.
- **MODES is verified in full.**
- **Channon (Geb) is at ABS/SEC level:** Geb was classified as class 3 (unbounded), "the first autonomous artificial system to pass this test".
- **Boerlijst and Hogeweg 1991 remains SEC.**

### Cited Findings
**Ray, Tierra.**
- Source: [Tierra docs node26 "Evolutionary Optimization"](https://tomray.me/pubs/tierra/node26.html), FULL of the page:
  - The ancestor (80 instructions) "requires 839 CPU cycles to replicate".
  - The smallest evolved creature has 22 instructions and needs 146 cycles: "a 5.75-fold difference in efficiency".
  - Other runs plateaued at 27 and 30 instructions. Figure 4 spans 500 × 10^6 instructions executed.
  - Mutation-rate settings 1, 2, 4, 8, … 128, expressed as 1 in N individuals per generation. Rates 1 and 2 were unstable and 4 was the highest stable rate. "optimization of the algorithm is maximized at the highest mutation rate that does not cause instability". Ecology was richer at slightly lower rates.
- Source: [Tierra docs node13](https://tomray.me/pubs/tierra/node13.html), FULL of the page:
  - The soup is about 60,000 instructions, "inoculated with a single individual of the 80 instruction ancestral genotype".
  - The reaper starts at 80% memory fill.
  - About 400,000 instructions fill the soup with about 375 creatures. The ancestor executes 839 instructions in its first replication and 813 thereafter.
  
  This **confirms** the earlier notes' MEM item "60,000 instructions".

**Lenski, Ofria, Pennock and Adami 2003.** Nature 423:139–144, doi 10.1038/nature01568 ([PDF, course archive](https://www.cs.princeton.edu/courses/archive/fall24/cos597C/bib/598-2017/adami03Nature.pdf)), FULL; abstract via [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1038/nature01568%22&resultType=core&format=json).
- Setup:
  - 3,600 identical copies of a hand-written 50-instruction ancestor (15 instructions needed for replication, 35 nop-C) on a lattice of 3,600.
  - Point mutation 0.0025 per instruction copied; insertions and deletions 0.05 each per genome copied, so about 0.225 mutations per replication.
  - 100,000 updates = 15,873 ancestral generations.
- Results:
  - Reward-all: **23 of 50** populations evolved EQU.
  - Across 36 other regimes × 10 populations: 124 of 360 (34%).
  - EQU-only: **0 of 50** (P < 4.3 × 10^-29), even though those populations tested more genotypes (2.15 × 10^7 against 1.22 × 10^7).
  - Some deleterious mutations served as stepping stones.
- Correction: the earlier notes' SEC "a bit over a third" is the 124/360 figure for the 36 single-change regimes. Reward-all itself was **23/50 = 46%**.

**Wilke, Wang, Ofria, Lenski and Adami 2001.** Nature 412:331–333, doi 10.1038/35085569 ([Europe PMC abstract](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1038/35085569%22&resultType=core&format=json)), ABS.
- Abstract: "Forty pairs of populations were derived from 40 different ancestors", one of each pair at a 4-fold higher mutation rate.
- "In 12 cases" the low-rate dominant replicated more than 1.5-fold faster.
- In every one of those 12, competition switched to favour the slower genotype as mutation rate rose.
- The specific genomic rates (0.5 and 2.0 per genome per generation) are stated in the 2018 replication, **Franklin, LaBar and Adami**, "Mapping the peaks", bioRxiv 10.1101/298125 (**preprint**; [PDF](https://www.biorxiv.org/content/10.1101/298125.full.pdf)), FULL:
  - 201 populations of 3,600; 10^4 generations of mutation-rate adaptation; competitions from 1,800 + 1,800 for 200 generations.
  - 166 of 201 pairs met the 1.5-fold criterion.
  - The original used mass-action reproduction; the replication used local placement.

**Szabó, Scheuring, Czárán and Szathmáry 2002.** Nature 420:340–343, doi 10.1038/nature01187 ([Europe PMC abstract](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1038/nature01187%22&resultType=core&format=json)), ABS.
- Replicases "adsorbed to a prebiotic mineral surface".
- A cellular automaton shows that "copying fidelity, replicase speed and template efficiency all increase with evolution, despite the presence of molecular parasites", attributed to "reciprocal altruism ('within-species mutualism') on the surface".
- This **confirms** the earlier MEM summary. Lattice size and rates were not seen.

**Kerr, Neuhauser, Bohannan and Dean 2006.** Nature 442:75–78, doi 10.1038/nature04864, PMID 16823452 ([Europe PMC abstract](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1038/nature04864%22&resultType=core&format=json)), ABS. E. coli and T4 across "a large network of subpopulations". "Rapacious phage displace prudent variants ... but prudent phage are more productive when alone". Prudent phage dominate under spatially restricted migration. Confirms the earlier notes.

**Boerlijst and Hogeweg 1991.** Physica D 48:17–28, doi 10.1016/0167-2789(91)90049-f. Secondary summaries agree:
- hypercycles of 5 or more species form spiral waves;
- spiral centres seed the whole spiral, so parasites are pushed outward;
- parasites were introduced after the spatial structure had formed.

[Scilit record and search summaries](https://scilit.net/publications/efc379f1c182de0a59ce2da66b1de31e), SEC. Still not read in full.

**Takeuchi and Hogeweg 2009.** PLoS Comput Biol 5:e1000542 ([PMC2757730](https://pmc.ncbi.nlm.nih.gov/articles/PMC2757730)), FULL for the first ~100k characters:
- A replicase–parasite CA (surface model) is compared with a cellular-Potts compartment model. Both give macroscopic replicase–parasite coexistence that the well-mixed ODE cannot.
- Wave-level selection acts on "fecundity of waves"; vesicle-level selection acts on longevity.
- In the compartment model, "survival of the flattest" appears at high mutation rates, with a "sharp transition" in Fig. 6.
- Numerical lattice size and diffusion were in equation images and not read.

**Takeuchi and Hogeweg 2012** was already FULL (partial) in the earlier notes; not re-read.

**Bedau, Snyder and Packard 1998**, "A classification of long-term evolutionary dynamics" ([PDF](https://people.reed.edu/~mab/papers/alife6.pdf)), FULL.
- Page numbers conflict: the PDF header says Artificial Life VI pp. 228–237, but the first page says pp. 189–198.
- Classes are defined by diversity D, new activity A_new and mean cumulative activity A_cum.
- The systems are **Holland's Echo, a neutral shadow of Echo, and the Phanerozoic fossil record**. The paper does not discuss Tierra.
- The neutral shadow copies birth and death timing and the mutation rate from the real run, but chooses parents at random.
- Conclusion: "We also suspect that no existing artificial evolving system has class 3 dynamics". Echo "and perhaps all other existing artificial evolutionary systems, apparently lack" unbounded growth of adaptive activity.
- This resolves the earlier gap: Bedau et al. 1998 did not classify Tierra.

**Dolson, Vostinar, Wiser and Ofria 2019**, "The MODES toolbox", Artificial Life 25(1):50–73, doi 10.1162/artl_a_00280 ([NSF PAR PDF](https://par.nsf.gov/servlets/purl/10104628)), FULL.
- Four hallmarks: change potential, novelty potential, complexity potential and ecological potential.
- A **persistence filter** counts a lineage only if it survives t generations. In the experiments, t was set equal to the population size, with sensitivity checks at several t (including 1,000 and 2,000).
- Shadow runs are "a viable filter option". The persistence filter, unlike shadows, does not fully remove neutral effects.
- Tested on NK landscapes and Avida.

**Channon**, "Passing the ALife test: activity statistics classify evolution in Geb as unbounded", ECAL 2001 (LNCS 2159), doi 10.1007/3-540-44811-x_45. Geb "exhibits unbounded evolutionary activity, making it the first autonomous artificial system to pass this test", with the caution to "look for weaknesses in the test". A follow-up, "Improving and still passing the ALife test" (Genetic Programming and Evolvable Machines, doi 10.1007/s10710-006-9009-3), introduced component-normalised activity to answer criticisms of normalisation. A 2019 journal paper asked whether Geb's maximum individual complexity grows indefinitely. Sources: [gpbib record, via search summary](https://gpbib.cs.ucl.ac.uk/gp-html/Channon_2001_PAT.html) (the direct fetch was refused); [Keele repository](https://keele-repository.worktribe.com/OutputFile/463185). SEC/ABS.

**Hickinbotham et al. 2021 (Stringmol)**, FULL (see Q2): this is a modern digital example in which spatial pattern formation prevents parasite-driven extinction and parasites drive complexity. It supports the earlier notes' Q3 claim that the main spatial lever in theory needs parasites.

### Inferences
- **Ray's 5.75-fold gain is a direct published counterexample** to "later code is not fitter", in a seeded system with a protected genome, a reaper and CPU-time competition. Pargellis (SEC) also reports rapid size reduction after emergence, and Hutton (FULL) reports only shortening. So **efficiency gains through shortening are the common published post-emergence outcome in Tierra-like and chemistry systems**. Emergence Lab's BFF programs have fixed length (64 bytes), which removes this lever. That is a mechanistic reason to expect no such trend in BFF. This is my inference; no paper says it about BFF.
- Scale comparisons now possible:
  - Lenski 2003 used 50 replicate populations per condition and about 15,873 generations.
  - Wilke 2001 used 40 pairs.
  - Franklin et al. used 201 pairs.
  - Emergence Lab's level-5 tests use 7 soups (E-78) and 20,000 rounds; see Q6 for what a round is in generations.

### Gaps
- Boerlijst and Hogeweg 1991 full text was not read.
- Channon 2001 full text was not read; the fetch to gpbib failed and Keele PDFs were not fetched.
- Eigen 1971 (the error threshold), Zaman et al. 2014 and Czárán and Szathmáry 2000 remain unverified (MEM/SEC in the earlier notes). **Do not cite their details without a check.**
- Wilke 2001's exact genomic mutation rates were not seen in the original. Cite "4-fold higher" from the abstract.

---

## Q5. Reviews of open-ended evolution, 2020–2026

### Takeaway
No comprehensive 2020–2026 review of OEE was found. The most recent field-level item located is the **Editorial Introduction to the 2024 Special Issue on Open-Ended Evolution** (Artificial Life 30(3):300, doi 10.1162/artl_e_00445). It follows the fourth OEE workshop (ALIFE 2021) and could not be fetched (403); only a search summary was seen. The standard reference points remain:
- Taylor et al. 2016 (OEE1 workshop);
- Packard et al. 2019 (two editorials);
- Bedau-style activity statistics with shadows, Channon's refinement, and MODES.

Reported state of the art (SEC): "only a few systems" such as Geb were classified as open-ended by Bedau-Packard measures.

### Cited Findings
- 2024 Special Issue editorial, Artificial Life 30(3):300. It follows the fourth OEE workshop at ALIFE 2021, builds on the earlier special issues, and argues that cultural evolution is a distinctive instance of OEE — [search summary](https://dx.doi.org/10.1162/artl_e_00445), SEC (the direct fetch of direct.mit.edu returned 403).
- The OEE1 workshop report (Taylor et al. 2016, Artificial Life 22(3):408–423) remains the standard overview. It reviews Tierra, Avida and Geb, and notes that few systems were classified as open-ended by activity statistics — [search summary](https://direct.mit.edu/artl/article/22/3/408); [Aston PDF](https://publications.aston.ac.uk/id/eprint/44173/1/artl_a_00210.pdf), SEC (PDF not read).
- A 2026 arXiv paper (2603.01701, not read) cites Geb as one of few programs with signs of open-endedness — [search summary](https://arxiv.org/pdf/2603.01701), SEC.
- Recent OEE-adjacent work found but not read: TerraLingua (arXiv 2603.16910, LLM ecologies; notes that OEE definitions require pre-specified dimensions), SEC; Hash Chemistry (arXiv 1806.06628); Swarm Chemistry II (arXiv 1804.03304).

### Inferences
- The field's standard evidence for OEE is still:
  - evolutionary activity against a neutral shadow (Bedau and Packard; Channon's component normalisation);
  - MODES hallmarks on persistence-filtered lineages.
  
  Both are system-level statistics over long runs. The earlier notes' recommendation stands: apply them to BFF soups before saying more than "level 5 not shown".

### Gaps
- No 2020–2026 survey article on OEE was found and read. Queries:
  - "open-ended evolution review 2023 2024 2025 state of the art artificial life survey" (extended)
  - the earlier notes' Stanley/Packard queries
  
  The 2024 editorial's text and the special issue's table of contents were not read. **Not found in this search**; do not conclude that none exists.

---

## Q6. From the repository: per-copy error rate of emergent BFF replicators, and generations per round

### Takeaway
**The per-copy byte error rate of emergent standard-BFF replicators is not recorded.** The repository records:
- **Thresholds**: ≥ 90% byte identity for copies in the growth test (D-040); 60/64, later 58/64 plus an instruction guard, for jump detection (D-050, D-053).
- A **probability of copying per meeting**, which is ≈ 1 for all tested emergent replicators in a halting background.
- **Background mutation**: 0.00024 per byte per round, the same as AyA2024's 0.024%.

The "59–60 of 64 bytes" sloppy copiers (J-074) are in **variant rules** (v2 with g = 57/58, h = 122), **not standard BFF**. The earlier notes (`after_replicators...md` Q4) applied this figure to BFF in general, and that should be corrected.

**Generations per round are also not recorded.** By construction a program meets exactly one partner per round, so a replicator can make at most one copy per round. The measured growth rates bound a doubling at about 1.7 rounds (ceiling) and 6.5–9 rounds (into random code).

### Cited Findings
All items below were read in full in the repository.
- Soup mechanics, `emergence/programs/bff.py`:
  - `Soup(... mutation=0.00024, max_steps=8192)`.
  - Each `epoch()` draws a random permutation and runs N/2 pairs, so each program is in exactly one pair per round.
  - Mutation then replaces Binomial(N·L, 0.00024) random bytes. That is about 0.0154 mutations per 64-byte program per round.
  - 0.00024 = 0.024% equals AyA2024's default. This closes the earlier notes' gap "the project's mutation rate was not checked".
- **Copy-identity thresholds (not error rates):**
  - D-040: in the replicator growth test, a copy is a program "≥ 90% identical" to the candidate (`docs/decisions.md` D-040).
  - D-050: jump detection used a 60/64 copy test. D-053 (J-075) lowered it to 58/64 with an instruction-fidelity guard (≥ 75% of instruction bytes reproduced), validated with:
    - sloppy positives (38/40 and 40/40 copiers);
    - exact replicators (40, 39 and 40 of 40);
    - filler-smear deceptives (0 accepted, against 37 of 64 under the old test).
    
    Source: `docs/journal.md` J-075.
- **Sloppy copiers are in variant rules:**
  - J-074: rules "v2 g = 57/58, h = 122" scored 0/6 under D-050 although HOE reached 6.4.
  - On replay, the most common programs (`>[ . ]` loops) copy "59–60 of 64 bytes" in place. The same probably applies to v4 g = 64, h = 124.
  - These are BFF-family variants with changed rule parameters, not the standard rule. Source: `docs/journal.md` J-074, and paper.md's detector table ("a 60-of-64-byte copy test missed copiers at 59 to 60 bytes").
- **Exact copying in head-offset variants:** in every real jump in E-61 (rules h = 61–68), "the takeover is by exact copiers (shift 0, 39–40 of 40 programs)". Shifted copiers' lineages lose the kernel within 1–22 generations, while exact copiers last all 32 generations of product chains — `docs/journal.md` J-062.
- **Probability of copying per meeting (standard BFF):**
  - J-050: all 9 E-42 emergent replicators "copy perfectly in the halting background" (r 0.386–0.392, against a theoretical ceiling ln 1.5 = 0.405 for p = 1).
  - J-051: all 47 E-49 replicators do the same (r 0.379–0.397).
  - Into random code, r = 0.076–0.108 for emergent replicators and about 0.14 for the hand-written one. A random partner that runs first damages a replicator most of the time; the hand-written one survives about 35% of such meetings.
  
  "Perfectly" here means p ≈ 1 under the ≥ 90% identity criterion, **not** zero byte errors — `docs/journal.md` J-050, J-051; `docs/decisions.md` D-044.
- **Heredity:** single-byte mutants of emergent replicators pass on their mutations (140/141 in the paper's Finding C, per the earlier notes). This shows copies preserve the mutated byte, but no per-byte copy error was measured.

### Inferences
- **Per-copy error, an upper bound only:** emergent standard-BFF replicators copy with ≥ 90% identity (≤ 6 bytes wrong of 64) in essentially every meeting in a halting background. Heredity tests imply that a mutated byte is usually transmitted. The actual distribution of byte errors per copy is unmeasured. So the earlier inference that "effective per-copy error may be several bytes per copy, placing BFF in the survival-of-the-flattest regime" is **not supported by recorded data for standard BFF**. It rested on the variant-rule sloppy copiers. A direct measurement would be: the byte-error distribution of child against parent over many copy events in a halting background, plus the partner-overwrite damage rate in the soup.
- **Generations per round (my arithmetic from the recorded growth rates):**
  - At the ceiling, r = 0.405 per round means doubling time = ln 2 / 0.405 ≈ 1.7 rounds. That corresponds to the replicator running first, and so copying, in about half of its meetings.
  - Into random code, r ≈ 0.08–0.11 gives a doubling time of about 6.5–9 rounds.
  - In a soup saturated with replicators, most meetings are replicator against replicator. A "generation" there means overwriting a near-identical relative, and the number of lineage-distinct generations per round is undefined without lineage tracking.
  - **Rough bound:** at most about 0.5 copy events per program per round. So 20,000 rounds (E-78) correspond to at most about 10^4 copy events along a lineage, the same order as Lenski 2003's 15,873 ancestral generations. This is an upper bound, not a measurement.
- **Background mutation per genome per generation:** 0.0154 per program per round. Over a generation time of about 2 rounds or more, that is about 0.03 or more per 64-byte genome per generation from background alone. This is far below Avida's 0.225 (Lenski 2003) and Wilke's 0.5–2.0 (Franklin et al.), so background mutation alone does not place BFF in the "flattest" regime. Copy errors and partner overwrites would have to dominate, and those are unmeasured.

### Gaps
- Not recorded in the repository:
  - the byte-level copy error distribution of emergent standard-BFF replicators;
  - the fraction of meetings in a saturated soup that damage a replicator;
  - lineage-based generations per round.
  
  Searches run: `grep` of `docs/journal.md`, `docs/paper.md`, `docs/decisions.md` and `docs/handoff.md` for fidelity, "of 64", sloppy, error rate, per copy, generation(s), mutation rate, doubling and growth; and a read of `emergence/programs/bff.py`.
