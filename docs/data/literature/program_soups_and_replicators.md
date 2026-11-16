# Program soups and spontaneous self-replicators: prior work against Emergence Lab claims (a) to (g)

Search date: 16 November 2026. Reading level is stated for each source:
- **FULL**: full text read through arXiv HTML. The fetch tool returns summaries and short verbatim quotes, so a few long passages may have been missed.
- **CODE**: GitHub repository source code, PRs or issues read directly.
- **ABSTRACT**: abstract or landing page only.
- **SECONDARY**: search-engine summary or third-party page only.

Main sources:
- [AyA2024] Agüera y Arcas, Alakuijala, Evans, Laurie, Mordvintsev, Niklasson, Randazzo, Versari, "Computational Life: How Well-formed, Self-replicating Programs Emerge from Simple Interaction", arXiv 2406.19108v2 (2 Aug 2024; preprint), https://arxiv.org/html/2406.19108. **FULL** (v2; v1 not compared line by line).
- [Knierim2026] Knierim, Versari, Obryk, Agüera y Arcas, Saurous, "BFF: Simple explanations for complex phenomena", arXiv 2607.01483v1 (1 Jul 2026; **preprint**), https://arxiv.org/html/2607.01483. **FULL**.
- [Cicala2026] Cicala, Niklasson, Randazzo, ... Agüera y Arcas, Richards, "Coevolution of self-replication and function in a digital primordial soup", arXiv 2607.09211v2 (2 Sep 2026; **preprint**), https://arxiv.org/html/2607.09211. **FULL for the first ~100k characters, rest not read.**
- [Jha2026] Jha, Cicala, Agüera y Arcas, Richards, Jaques, Kleiman-Weiner, Niklasson, "Tapes Together Strong", arXiv 2609.10817 (9 Sep 2026; **preprint**), https://arxiv.org/abs/2609.10817. **ABSTRACT**.
- [cubff] The code repository of AyA2024, https://github.com/paradigms-of-intelligence/cubff. **CODE**: read `bff.inc.h`, `bff.cu`, `bff_noheads.cu`, `bff_selfmove.cu`, `python/selfrep_spawning.py`, `python/cond_exp.py`, PRs #14, #29, #34, #43, #47, #51 and issue #46.
- [Adami2015] Adami, "Information-theoretic considerations concerning the origin of life", arXiv 1409.0590 (Orig. Life Evol. Biosph. 2015, per the Springer link https://link.springer.com/article/10.1007/s11084-015-9439-0), https://ar5iv.arxiv.org/html/1409.0590. **FULL**.
- [CG2017] C G, LaBar, Hintze, Adami, "Origin of life in a digital microcosm", arXiv 1701.03993 (Phil. Trans. R. Soc. A 375, 2017, per search metadata), https://ar5iv.arxiv.org/html/1701.03993. **FULL**.

## (a) Replicators from random BFF soups: the setup and results of Agüera y Arcas et al. 2024

### Takeaway
Claim (a) is **already published**. The project itself presents it as a reproduction, which is correct. The project's numbers (3 of 16 soups of 2^14 programs within 48,000 rounds) are also quantitatively consistent with AyA2024's 40% within 16k epochs at 2^17 programs, once both are put on a per-pair-run basis (see Inferences).

### Cited Findings
- AyA2024 setup:
  - The soup usually holds 2^17 programs. Each program is 64 bytes, initialised uniformly at random.
  - Each epoch forms random ordered pairs. A pair is concatenated into a 128-byte tape, executed, and split back into two programs.
  - Execution stops after 2^13 steps. The HTML rendering is garbled, but it reads as 2^13. 
  - Default runs last 16k epochs; experiments typically use 1,000 runs.
  - The default background mutation is 0.024%. Ablations used 0%, 0.012%, 0.048%, 0.1%, 0.5% and 1%.
  
  Source: [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- Frequency: replicators appear "in 40% of the runs within 16k epochs" at the default mutation rate. About 60% of long runs make no replicator — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- With 0% mutation, the transition occurs "with roughly the same frequency" as at the default rate. "increasing the mutation rate speeds up the rise of self-replicators" — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- Short runs (128 epochs, random start) transitioned in only 3 of 1,000. Runs seeded with one hand-written replicator took over in 22% of 128-epoch runs, which the authors read as "roughly 1/5 of all self-replicators manage to take over". The "long-no-noise" variant transitioned about 50% of the time — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- Detection uses "high-order entropy": Shannon entropy minus normalised Kolmogorov complexity, approximated with brotli compression. Emergence Lab's HOE is the same measure — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- In the case study, a first replicator emerged near epoch 2354/2355 (the text is inconsistent between figures). A "zero-poisoning" period followed, then a second replicator family took over — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- An independent replicator could not reproduce emergence with `bff_noheads --num 1024`, even after more than 1 million epochs. Emergence came after about 4 million epochs using `--lang bff --num 1024 --mutation_prob 0.0005`, and a third user still failed. This is anecdotal evidence that small soups are slow or unreliable — [cubff issue #46](https://github.com/paradigms-of-intelligence/cubff/issues/46) (Nov 2025 to 2026), CODE.

### Inferences
- **Rate consistency check** (my arithmetic, assuming one "epoch" = one "round" = N/2 pair runs):
  - At the project's rate of 0.036 per 10^8 pair runs, AyA2024's 16k epochs × 2^16 pairs ≈ 1.05 × 10^9 pair runs give an expected 0.38 events. That is P(transition) ≈ 1 − e^−0.38 ≈ 0.32, against AyA's reported 40%.
  - For the project's own soups: 48,000 × 2^13 ≈ 3.9 × 10^8 pair runs gives P ≈ 0.13, or about 2.1 expected of 16, against 3 observed.
  - So the project's single rate roughly predicts AyA's 40% across an 8-fold size difference. That is supporting evidence for (b), not a conflict.
  - This depends on the two projects using the same rule (`bff_noheads`, both heads at 0) and similar mutation rates. The project's mutation rate was not checked here.
- The project's "copy-all" deceptive control for HOE adds a validation step. It is not a new phenomenon.

### Gaps
- I did not check whether AyA2024's soup experiments used `bff` (heads read from bytes 0 and 1) or `bff_noheads` (both heads at 0); see (c) and (d). The README's example command uses `bff_noheads`.
- I did not see any distribution of transition times in AyA2024.

## (b) Take-over rate scales linearly with soup size, as one origin rate per pair interaction

### Takeaway
This is **partly known**:
- AyA2024 does not report soup-size effects.
- The original authors' group measures emergence time in interactions or "programs tested", not in epochs. They state that results at different soup sizes were "very similar", which is the same model the project fits.
- The cubff code contains tools to estimate a per-pair spawn rate and to check whether waiting times are memoryless. These date from February to December 2025, and I found no published results from them.
- I found no published fit of take-over rate against soup size (an exponent β ≈ 1) in this search.

### Cited Findings
- Knierim2026 times emergence by interactions: "The average time to first self-replicator in BFF is ≈2.5⋅10^6 interactions, which corresponds to 5⋅10^6 programs tested". This is averaged over 100 seeds, in the `bff_selfmove` variant — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- Knierim2026 reports that other variants, including "different soup sizes, interactions with all programs paired up simultaneously or one interaction at a time", gave "very similar results". The comparison is in programs tested — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- Knierim2026 distinguishes "time to first self-replicator" from take-over (gelation): "previous work ... has always looked at the point the soup gelates" — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- `python/selfrep_spawning.py` (PR #34, "estimator of likelihood of producing a self-replicator", Feb–Mar 2025) estimates spawn rate as follows:
  - It pairs 65,536 copies of a given program each with a fresh random 64-byte partner (`allowed_interactions = i ^ 1`).
  - It then counts how many resulting programs self-replicate.
  
  This is a fresh-random-pair product rate, the same idea as the project's R_P (claim f, Phase 6) — [cubff PR #34](https://github.com/paradigms-of-intelligence/cubff/pull/34), CODE.
- `python/cond_exp.py` (PR #29, Feb 2025) does two things:
  - It estimates E[X − x | X > x] (mean residual waiting time), plus the CDF, of the epoch at which high-order entropy first exceeds 3.0, across runs.
  - Constant mean residual life is the signature of an exponential (memoryless) waiting time.
  
  [cubff PR #29](https://github.com/paradigms-of-intelligence/cubff/pull/29), CODE.
- PR #51 (Dec 2025) is titled "actually count expected time until a random walk hits a self-replicator". It changes the sampler to count every replicator found and reinitialise only that program — [cubff PR #51](https://github.com/paradigms-of-intelligence/cubff/pull/51), CODE.
- AyA2024 gives no soup-size analysis — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- AyA2024 states takeover propagation time in 2D grows with grid side (about √n) versus about log n when well mixed. That concerns spread after origin, not origin rate — [AyA2024](https://arxiv.org/html/2406.19108), FULL.

### Inferences
- Knierim2026's figure (bff_selfmove, first replicator) is about 1 per 2.5 × 10^6 interactions, or about 40 per 10^8. The project's figure (standard rule, verified take-over) is 0.036 per 10^8. The difference is about 1,000-fold, and the two measurements are not comparable:
  - They use different variants. bff_selfmove auto-advances the read head and was designed to make copying easier.
  - They measure different events: first replicator versus take-over. AyA2024's seeded runs suggest only about 1/5 of replicators take over.
  
  The project should not cite Knierim's number as a check on its own without that caveat.
- The project's novel part is narrow: an explicit size sweep (2^13 to 2^16) with a pre-registered exponent test and a pooled per-pair-run rate. The underlying model of a "rate per interaction, independent of soup size" is implicit in how the Google group now measures time.

### Gaps
- I found no result from cond_exp.py (e.g., whether BFF transition times are exponential) in any paper or README.
- Queries tried that found nothing on rate against population size for program soups:
  - "BFF self-replicators emergence primordial soup follow-up 2025"
  - "spontaneous self-replicators random programs instruction set predicts emergence SUBLEQ BFF variants 2025 2026 arXiv"
  
  No dedicated search on origin-of-life population-size scaling in chemistry or theory was done, so a general rare-event or Poisson treatment in origin-of-life theory may exist and was not checked.

## (c) Emergent BFF replicators copy backwards and produce their byte-reverse; kernel census explanation

### Takeaway
The **observation is partly known**: reverse copying, palindromic replicators, and self-inverting replicators needing an even number of copies are all in the Google group's paper, code and preprint. The project's **explanation** is a census showing that with both heads at byte 0 every short copier is a reverse copier. I did not find that explanation in this search.

### Cited Findings
- AyA2024's case-study replicator is described as a palindrome, so it yields a correct copy "despite being copied in reverse". The pre-replicator "copies every second byte from tape A into B in reverse order". The transition passes through "a reversed replicator" that a pre-replicator then copies "into a direct replicator" — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- cubff PR #14 (robryk, 13 Feb 2025, not merged) says: "we're getting palindromic self-replicators in bff then, with varying inter-head distances" — [cubff PR #14](https://github.com/paradigms-of-intelligence/cubff/pull/14), CODE.
- Knierim2026: "some self-replicators invert themselves and will produce an exact copy only after an even number of executions". Their detector uses an odd-length chain of five executions so that such replicators are caught. They "do not compare the second halves to the first halves, as there are self-replicators that invert themselves" — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- In cubff, `bff_noheads` initialises head0 = head1 = 2 × 64 = 128, which wraps to byte 0 on the 128-byte tape. In `bff` (BFF_HEADS), head0 = tape[0] mod 128 and head1 = tape[1] mod 128, so heads start where the first two bytes say — [cubff bff.inc.h](https://github.com/paradigms-of-intelligence/cubff/blob/main/bff.inc.h), CODE.

### Inferences
- The project's statement that every emergent replicator has two mirror forms (J-046) matches Knierim2026's "invert themselves ... even number of executions". It should be labelled as known.
- "All 9 copied backwards" is consistent with AyA2024's single case study.
- The census-based explanation (both heads at byte 0, so all 55 short copiers are reverse copiers, and the minimal replicator needs two kernels of 10 instructions) was not found and may be new. The Google group clearly knew the phenomenon, so a check of the AyA2024 v1 text and Agüera y Arcas's book is needed before claiming it.

### Gaps
- I did not read Agüera y Arcas's books *What Is Life?* / *What Is Intelligence?* (2025) directly. A search found no mention of reverse copying in summaries — [Penguin listing](https://penguinrandomhouse.com/books/800181/what-is-life-by-blaise-aguera-y-arcas), SECONDARY; [gonzoml review](https://gonzoml.substack.com/p/what-is-life), SECONDARY. Not found in this search ≠ absent.

## (d) Moving one head's start to byte 64 makes forward copiers and fast soups

### Takeaway
This is **partly known**:
- AyA2024 already found that head start positions matter, and that an offset to head1 is needed for looping replicators in the long-tape setting.
- cubff's default `bff` language reads head starts from the program's own first bytes.
- Knierim2026 deliberately biases programs toward heads exactly 64 apart because that "makes it easier", and quantifies a speed-up in random-walk search.

The project's specific soup result was not found: one fixed head at 64, take-over in 250–1,750 rounds, 8 of 8 against 0 of 12, and a backward-copier control at 127.

### Cited Findings
- AyA2024 (long-tape variant): "we need to decide what to do about head0 and head1's initial positions".
  - If heads are set equal to the PC, "trivial (non-looping) self-replicators" arise.
  - "Adding an offset to head1 is sufficient to allow looping self-replicators to arise".
  - "Anecdotally, we appear to require an offset somewhat larger than 8 to work (e.g., 12 or 16)".
  
  [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- Knierim2026 adds byte value 64 to the operator bucket of their sampling distribution. "The rationale behind this is to make it easier to start with head positions that are exactly 64 positions apart". Heads 64 apart "start in the same location" relative to the two halves — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- Programs tested per replicator found (Knierim2026, Table 1):

  | Sampling distribution | Programs tested per replicator |
  |---|---|
  | Uniform random 64-byte strings | 2.9×10^7 |
  | ℬℱℱ-fitted | 1.7×10^6 |
  | CUST | 4.5×10^5 |
  | CUST64 (byte 64 favoured, so heads 64 apart) | 9.4×10^4 |
  | BFF soup (for comparison) | 5×10^6 |

  CUST64 is about 4.8× better than CUST. The text calls CUST64 "roughly a factor of 25" better than BFF, but the table ratio is about 53 — an internal inconsistency — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- `bff_selfmove` (added Mar 2025) has a single copy op that auto-advances the read head, which "makes producing an exact copy of the first program much easier as there is no need to align the heads first" — [Knierim2026](https://arxiv.org/html/2607.01483), FULL; [cubff PR #43](https://github.com/paradigms-of-intelligence/cubff/pull/43), CODE.
- PR #14 mentions palindromic replicators "with varying inter-head distances" in `bff` (variable head starts) — [cubff PR #14](https://github.com/paradigms-of-intelligence/cubff/pull/14), CODE.

### Inferences
- The project should say plainly that head start positions were already known to be an important design choice, and that heads 64 apart were already known to help produce exact copies (Knierim2026, preprint, Jul 2026).
- What remains distinctive is narrower:
  - the controlled single-change counterfactual in full soups;
  - the forward/backward framing;
  - the backward-copier control at h = 127 (E-59), which separates "more short copiers" from "forward copiers".

### Gaps
- I did not find a systematic sweep of head starts in published work. The `bff` variant randomises head starts per program, but I found no published comparison of `bff` against `bff_noheads` emergence rates.

## (e) Rule-level predictor F (a short copier whose copy is a copier) across BFF variants and instruction sets; nothing predicted speed

### Takeaway
F itself is **not found in this search**. The general idea that a property of a language computed in advance predicts emergence is **partly known**:
- AyA2024 proposed shortest replicator length as "a key factor" but "not the sole factor".
- Adami's information theory gives P ≈ D^−I, where I is the information content of the smallest replicators.
- Avida's minimal replicator length and density were obtained by exhaustive enumeration, which is close in method to the project's kernel census.

### Cited Findings
- AyA2024 on SUBLEQ: "SUBLEQ-like languages seem to have a much higher expected length for a functioning initial self-replicator". They "note that the shortest length of hand-crafted self-replicators in SUBLEQ" is larger. RSUBLEQ4 has a 25-byte replicator yet still did not emerge from random starts, so length is likely key but "not the sole factor" — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- AyA2024: "self-replicators are too rare to be generated by random background mutation" in SUBLEQ, and "There are no dynamics to change the distribution of strings" — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- Adami2015 gives P₀ = D^(−I_S), with I_S = L(H_a − H_b).
  - In Avida (D = 26), a 15-instruction replicator gives P₀ = 26^−15 ≈ 6×10^−20.
  - Biased monomer frequencies can raise P by many orders of magnitude (P⋆ ≈ 26^−5 in the example).
  - Cites Rupp et al.: 10 replicators in 2×10^8 biased samples.
  
  [Adami2015](https://ar5iv.arxiv.org/html/1409.0590), FULL.
- CG2017 (Avida):
  - Exhaustive search of all 26^8 ≈ 2.09×10^11 length-8 genomes found 914 replicators (density ≈ 4.4×10^−9, "about one replicator per 200 million sequences"). That is an information content of about 5.9 mers.
  - No replicators were found at length 7, nor at lengths 5 and 6 (exhaustive).
  - An earlier random sample of about 10^9 length-8 sequences found 6.
  
  [CG2017](https://ar5iv.arxiv.org/html/1701.03993), FULL.
- CG2017 competition: all 914 replicators (10 each) competed in populations capped at 10^4 for 5×10^4 updates, 200 replicates. Three genotypes won 37, 49 and 45 of 200 — [CG2017](https://ar5iv.arxiv.org/html/1701.03993), FULL.
- Knierim2026 offers no predictor across languages. Changing the sampling distribution changes programs-to-replicator by 300× (2.9×10^7 to 9.4×10^4), with mutation probability p = 1/200 to 1 also mattering — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- Pargellis's Amoeba (2000) produced self-replicating colonies whose members had only 7 essential instructions from a 32-opcode set — [Nokia Bell Labs listing](https://www.nokia.com/bell-labs/publications-and-media/publications/spontaneous-generation-and-colony-formation-in-the-amoeba-world), ABSTRACT/SECONDARY.

### Inferences
- F differs from "shortest replicator length" and from "replicator density" in a specific way: it asks whether a short copier's copy is itself a copier, which captures orientation and heredity. It is a reasonable refinement of known ideas.
- The project should cite AyA2024's length hypothesis and Adami's D^−I as the predecessor predictors. A natural baseline the project apparently did not test is the density of replicators among random programs, à la CG2017 and Knierim2026's programs-to-replicator. The SUBLEQ R_P is close to this.
- "Nothing predicted speed" has a close relative in AyA2024: RSUBLEQ4's short replicator did not suffice. Length is "not the sole factor".

### Gaps
- Not found in this search: any published predictor tested prospectively across many rule variants. Queries tried:
  - "spontaneous self-replicators random programs instruction set predicts emergence SUBLEQ BFF variants 2025 2026 arXiv"
  - "BFF self-replicators emergence primordial soup follow-up 2025"
- Not checked for language-level predictors (prior knowledge suggests these as places to look, unverified here):
  - Fontana's AlChemy;
  - Hutton's Squirm3;
  - Stringmol (Hickinbotham et al.);
  - typogenetics (Hofstadter; Varetto; Kvasnička et al.).

## (f) SUBLEQ family: plain SUBLEQ and RSUBLEQ4 give no replicators; designed variants give tile and self-rewriting replicators

### Takeaway
The negative part (no replicators in plain SUBLEQ or RSUBLEQ4 from random starts) is **already published** in AyA2024; the project confirms it. The designed SUBLEQ family is **not found in this search**: stepping index, operand window, periodic-tile replicators, self-rewriting 5-byte loops, and the tile-density and R_P predictors. The R_P measurement idea (rate at which fresh random pairs write a replicator) has a close unpublished precedent in cubff's `selfrep_spawning.py`.

### Cited Findings
- AyA2024 SUBLEQ results:
  - "when randomly initialized, the soup remained in almost complete random uniformity even following billions of executions".
  - The smallest hand-crafted SUBLEQ replicator the authors could write is 60 bytes. The HTML reads "6060", a rendering artifact.
  - RSUBLEQ4 has a 25-byte replicator: seeded soups are taken over, but random starts give no transition.
  
  [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- AyA2024 also tested:
  - **Forth:** there is a one-byte trivial replicator, and "almost all runs" transition within 1k epochs.
  - **Forth on a long tape:** good replicators appear in about a minute, about 180 billion instructions.
  - **Z80 (2D grid, 16-byte programs):** stack-based copiers come first, then LDIR/LDDR replicators, with successive takeovers.
  - **8080 (long tape):** the only replicators were non-looping two-byte repeats such as "01 c5", and a looping variant was never observed.
  
  [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- cubff contains `subleq.cu` and `rsubleq4.cu` — [cubff repo](https://github.com/paradigms-of-intelligence/cubff), CODE.
- cubff `selfrep_spawning.py` pairs a program with fresh random partners and counts replicators produced, i.e., a fresh-pair product rate — [cubff PR #34](https://github.com/paradigms-of-intelligence/cubff/pull/34), CODE.

### Inferences
- AyA2024's 8080 result (non-looping two-byte repeated replicators) is close in kind to the project's "periodic tiles, one instruction repeated" in SUBLEQ variants. The project should cite it as a prior example of tile-like replicators emerging in an assembly-like language.
- AyA2024's trivial-replicator discussion (Forth one-byte replicator; non-looping replicators when heads equal the PC) is also relevant.

### Gaps
- Not found in this search: any other published SUBLEQ variant family with emergent replicators, or any test of tile density or fresh-pair product rate as a predictor.

## (g) Founders written in a single pair run, never by mutation alone; take-over as wait for one rare event with roughly exponential waiting times

### Takeaway
This is **partly known, with some tension**:
- AyA2024 already showed that BFF replicators arise without mutation, through self-modification and interaction.
- In their traced case, emergence was a multi-step process over several interactions: pre-replicator, then reversed replicator, then direct replicator. That is in tension with a "one rare pair run writes the founder" picture, at least in BFF. The project's single-run claim is about SUBLEQ.
- Knierim2026 shows that pure mutation random walks with no pairing find BFF replicators at least as easily as the soup does. This conflicts with any reading that pair interaction is needed.
- The exponential waiting-time model was apparently being checked in cubff (2025), but I found no published result.

### Cited Findings
- AyA2024 concludes that replicators "arise mostly due to self-modification and interaction among different programs", not from random initialisation or mutation. Zero-mutation runs transition at roughly the default frequency — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- AyA2024's tracer tokens follow the case-study origin through five steps:
  1. A pre-replicator copies every second byte in reverse.
  2. A reversed replicator is created.
  3. The pre-replicator copies it into a direct replicator and breaks its own loop.
  4. The direct replicator modifies tape A but is stopped by a 0.
  5. The full replicator is complete.
  
  [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- Knierim2026: "we can easily find BFF self-replicators by executing a simple 'random walk mutation' process", faster than soup evolution per program tested. Their view is that paired interaction is not "an unusually powerful search operator" in BFF — [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- Knierim2026 also capped ancestry-tree depth and width:
  - Capping at 2 only slows emergence.
  - With caps of 0, so that no copying between programs is allowed, replicators still arise from + and − edits alone, more slowly.
  - Blocking merges "merely stops self-replicators from taking over the soup".
  
  [Knierim2026](https://arxiv.org/html/2607.01483), FULL.
- AyA2024, seeded runs: about 22% of single seeded replicators take over within 128 epochs. Establishment is not guaranteed once a replicator appears — [AyA2024](https://arxiv.org/html/2406.19108), FULL.
- cubff `cond_exp.py` computes mean residual waiting time E[X − x | X > x] of the transition epoch across runs. This is a direct test of memorylessness (exponential waiting) — [cubff PR #29](https://github.com/paradigms-of-intelligence/cubff/pull/29), CODE.
- Coreworld: according to AyA2024's related-work summary, replicators there (e.g., two-instruction MOV-SPL) arise "due to either random initialization or to random mutations of imperfect self-replicators" — [AyA2024 via search summary](https://arxiv.org/pdf/2406.19108), SECONDARY for the Coreworld detail. The original is Rasmussen et al., Physica D 42:111–134 (1990), not read; the technical report is at [core.ac.uk](https://core.ac.uk/download/216514147.pdf), not read.

### Inferences
- The project's (g) is stated for SUBLEQ founders (24 written by the partner, 16 by the program itself, 0 by mutation alone). It does not directly conflict with BFF literature, but it should not be generalised to BFF:
  - AyA2024's BFF trace shows staged assembly across interactions.
  - Knierim2026 shows that mutation-only walks suffice in BFF.
- The "one rate, exponential waits" model is a natural formalisation of what the Google group measures. It is not claimed in their papers.
- The project's finding that soups under one SUBLEQ jump condition produce replicators about 7× faster than fresh pairs fits AyA2024's staged pre-replicator story. Soup history can raise the rate.

### Gaps
- Not found in this search: published waiting-time distributions for BFF transitions, or explicit Poisson or exponential models of replicator origin in program soups. Older digital-life work was not checked for waiting-time models (Pargellis 1996 Physica D "The spontaneous generation of digital 'life'", Greenbaum & Pargellis 2017 Artificial Life). [Greenbaum & Pargellis 2017 listing](https://scholars.mssm.edu/en/publications/self-replicators-emerge-from-a-self-organizing-prebiotic-computer-2/) was seen at ABSTRACT/SECONDARY level: Amoeba shows a self-organisation phase (opcode frequencies, mutual information) followed by emergence of replicators. No rate was seen.

## Summary labels for (a) to (g) (my judgement from the sources above)
- **(a)** Already published (AyA2024): 2^17 programs, 64 bytes, 0.024% mutation, 40% within 16k epochs. The project's numbers are consistent with it.
- **(b)** Partly known:
  - The per-interaction framing and the statement that soup size makes little difference are in Knierim2026 (preprint) and cubff tooling.
  - A size-sweep exponent and a pooled rate were not found.
- **(c)** Observation partly known: reverse copying, palindromes and self-inverting replicators are in AyA2024, cubff PR #14 and Knierim2026. The census explanation was not found.
- **(d)** Partly known:
  - Head-start importance and an offset requirement are in AyA2024.
  - Heads 64 apart helping, with a ~4.8× random-walk speed-up, are in Knierim2026.
  - The soup counterfactual and the backward-copier control were not found.
- **(e)** F itself not found. Predecessors: shortest-replicator length (AyA2024), information content D^−I and replicator density (Adami2015, CG2017).
- **(f)** The negative SUBLEQ/RSUBLEQ4 result is already published. The designed family and its predictors were not found. The fresh-pair product rate has an unpublished precedent in cubff code. Tile-like non-looping replicators have a precedent in 8080.
- **(g)** Partly known and in partial tension:
  - Zero-mutation emergence is in AyA2024.
  - BFF emergence is multi-step in AyA2024's trace.
  - Mutation-only random walks suffice in BFF (Knierim2026).
  - Exponential waits are untested in print, though being checked in cubff code.

### Additional gaps (not searched due to budget)
- Agüera y Arcas's *What Is Intelligence?* (MIT Press/Antikythera, 2025; open access) and *What Is Life?* were not read.
- Citation lists of AyA2024 (Semantic Scholar or Google Scholar) were not systematically scanned. Only the three 2026 Google-group preprints were found. Jha2026 was read only at the abstract.
- AlChemy, Stringmol, Hutton, typogenetics, Tierra and Avida emergence-rate papers beyond Adami2015 and CG2017 were not read.
- AyA2024 v1 was not compared with v2.
