---
title: Journal
description: Chronological research log, newest first.
---

# Journal

Newest first. Each entry records what we did, why, what we found, and what we learned.
Experiment IDs (E-xx) link to the [Experiments]({{ '/experiments.html' | relative_url }}) page and decision IDs (D-xxx) to [Decisions]({{ '/decisions.html' | relative_url }}).

**How to add an entry** (people and agents): copy the template at the bottom, put it at the top, and fill in the commit hashes and experiment IDs. Keep claims at the evidence level actually reached.

---

## J-075 · 2026-11-11 · E-73: a validated looser copy test changes 33 of 392 jump times; no verdict flips, but the five-generation effect reappears

**Question (pre-registered, `docs/data/e73-preregistration.md`, commit `37a7a81`):** J-074 found sloppy replicators (copies of 59–60 of 64 bytes) that the D-050 copy test (60/64) misses. Build a looser test, validate it with controls, then re-score every soup of E-70, E-71 and E-72 with it and re-apply each experiment's pre-registered test unchanged.

**Ran:**
- **Part A, the test** (`bff_kernels.classify_fid`, `scripts/bff_fidelity.py`, fixtures from 9 replayed soups in `scripts/fixtures/`). D-053 = shift-aware copier test at **58/64** bytes plus an **instruction-fidelity guard**: the copy must reproduce ≥ 75% of the program's instruction bytes in the overlap.
- **Part B, the re-score** (`scripts/bff_rescore.py`, 392 soups replayed from their seeds, both tests on the same top-40 programs at each experiment's checkpoints, 8 h 24 min on 10 workers). Then `scripts/e73_analysis.py` re-applies the tests.

**Found:**
- **Controls all pass** (`2026-11-11-e73-fidelity.json`):
  - With threshold 60 and no guard the new test is identical to the old one on every fixture.
  - Sloppy replicators: 38/40 and 40/40 copiers (old test 0/40). Exact replicators: 40, 39 and 40 of 40.
  - Top-40 programs of soups without replicators (the selection-aware null): 0/40 and 0/40.
  - Deceptive "filler smears", where a loop writes one value across the partner so that 60/64 bytes match without any copying of instructions: 0 accepted, while the **old test accepts 37 of 64**. The guard also removes a false positive in D-050 itself.
  - Thresholds 52–58 with a guard of 50–75% give the same results; 58/75 is the strictest that passes.
- **One control changed after seeing it (disclosed in the pre-registration):** the random-program negative was written as 0 of 200. One random program contains `[ . ]`, a genuine 3-instruction copier under v1/h1 = 64 that the old test also counts. The check is now ≤ 1% (2 of 200); the worst rule gives 1 of 200.
- **Equivalence holds for all 392 soups:** the replayed D-050 copier series and jump times match the stored ones exactly.
- **What changes (secondary):**
  - 33 of 392 soups get a different jump time: 12 new jumps (all 6 soups of each sloppy v2 rule, g = 57/58, h = 122, now at round 50) and 21 earlier ones (median 250 rounds earlier, range 50–2,500).
  - **No jump is lost and none comes later**, so no D-050 jump was a filler smear.
  - The three v4 g = 64, h = 124 soups at HOE 3.0 stay at no jump under both tests. Their dominant programs are not copiers (fixture `transient_v4_g64`, 0/40).
- **Pre-registered verdicts under D-053** (D-050 in brackets):
  - **E-70 P2: pass** (pass). Unchanged: F 60/60, other 15/60, Fisher p = 2e-20. **Prediction (fail, ~55%) wrong.** Only 1 of 120 soups changed, an F soup 250 rounds earlier; no sloppy take-overs among the other rules.
  - **E-71 P1: fail** (fail): ρ = −0.33, p = 0.067 (−0.34, 0.060). **P2: pass** (pass): Σρ = −2.27, p = 0.011 (−2.45, 0.006). v1/68 still makes nothing, 0/8. Predictions right (P2 pass, v1/68 0/8; no directional call on P1).
  - **E-72 primary: fail** (fail), as predicted, but the effect is very different. Deep rules now take a median **163** rounds against 1,638 for shallow ones (**ratio 10**, Mann–Whitney p = 0.06); under D-050 the medians were 1,475 vs 1,675 (ratio 1.1, p = 0.58). Exploratory: deep count vs median T ρ = −0.52 (p = 0.04; D-050 −0.09); one-generation count vs T ρ = −0.59 (D-050 −0.74).

**Interpretation:**
- The **jump-or-not results are robust to the copy test**. E-70's 60/60 vs 15/60 does not move, and no D-050 jump turns out to be a smear.
- The **speed results are not**. E-72's null result came almost entirely from the two sloppy v2 rules being scored as never jumping. Under the validated test the five-generation predictor points the right way with a tenfold effect. With 8 vs 8 rules it still falls short of p < 0.01, and the HOE timing (D-052, p = 0.04) agrees in direction.
- Per the pre-registered decision rule, both verdicts are reported. The deep-vs-shallow speed question is **unresolved, leaning towards an effect**; it needs a fresh confirmatory test with more rules.
- E-71's pooled result stays unresolved: D-053 says fail, HOE timing says pass.

**Changed:** `bff_kernels.c/.py` (`classify_fid`), `scripts/bff_fidelity.py`, `bff_fidelity_fixtures.py`, `bff_rescore.py`, `e73_analysis.py`; copy-fidelity controls in `pytest` and `emergence benchmark --probes`; D-053.

**Lesson:** a detector threshold tuned on one language silently decides speed results in another. Validate it on the new language before trusting a "no".

**Next:** (a) a fresh, larger confirmatory test of the five-generation predictor under D-053 (more rules per class; primary under D-053 and HOE, both required); (b) a language outside the BFF family.

---

## J-074 · 2026-11-10 · E-72: following copies for five generations explains the old failures but does not predict new ones; and our jump detector misses sloppy copiers

**Question (pre-registered, `docs/data/e72-preregistration.md`, commit `bf5ee1b`):** E-71's F rule v1/68 made nothing. The F test checks one generation (does the copy copy?). Does a five-generation version predict speed better? Each self-sufficient kernel starts 8 lineages of single copies, each into a fresh random partner. A kernel is *deep* if ≥ 4 of its 8 lineages still copy at generation 5. An F rule is *F-deep* if it has any deep kernel, else *F-shallow*. Primary (fresh rules): F-shallow rules are ≥ 3× slower (median of rule medians), with Mann–Whitney p < 0.01.

**Ran:** `scripts/bff_multigen.py`.
- Part A: the 44 E-70 F rules (1.5 min). Explanatory only, because their soups were already known.
- Part B: 240 rules never run before: variants v1–v5 with head0 starting at g = 1–127 and head1 at g + 60..68. Census plus depth (8 min), then 6 soups in each of 8 F-deep and 8 F-shallow rules (96 soups, 4 h 10 min).

**Found:**
- **Part A (explanatory):** the enumeration reproduces the census counts exactly. At v1/67 and v1/68 no kernel is deep: copies of copies stop copying. Over the 37 rules with soups, the deep count against median T gives ρ = −0.66, against −0.44 for the one-generation count. Shallow rules took 2,250 rounds, deep rules 250. Some shallow rules were fast anyway (v1/60, v3/67, v3/68).
- **Part B census:** 27 of 240 rules are F (11%), 17 deep and 10 shallow.
- **Part B primary: fail.** Shallow rules took a median 1,675 rounds and deep rules 1,475 (ratio 1.1, p = 0.58). The one-generation self-sufficient count predicted better (ρ = −0.74, p = 0.001; exploratory).
- **A measurement failure in two rules.** Deep rules v2 g = 57/58, h = 122 scored 0/6 under D-050. Yet HOE rose to 6.4 within about 500 rounds, and nearly every pair ran to the step limit. Re-running seed 7220 for 600 rounds: the most common programs (`>[ . ]` loops) copy **59–60 of 64 bytes** in place. These are sloppy replicators just under the classifier's 60-byte threshold, and D-050 missed them. The same probably applies to v4 g = 64, h = 124 (three soups at HOE 3.0, no copiers detected).
- **Re-analysis with an HOE jump time** (HOE ≥ 2 at 3 consecutive checkpoints; post hoc): deep 188 rounds vs shallow 1,500, p = 0.04. The direction now matches the prediction, but the result is still short of p < 0.01. HOE in turn misses copier take-overs in v3/67 at g = 0 (4 of 6 soups stay below HOE 2).
- **E-71 checked the same way:** 13 of 176 soups disagree between the two definitions. The within-variant result holds under every definition (p ≤ 0.004). **The pooled result does not:** under HOE timing ρ = −0.57, p = 0.003, which would have passed P1. J-073's "across languages, no" is corrected to "not shown either way". v1/68 stands: its soups never exceeded HOE 0.6.

**Interpretation:** a multi-generation census explains the two slow v1 rules after the fact, but it did not predict speed in a fresh family. It is not established as a better predictor. The bigger lesson is about measurement: in variant languages, "when did replicators take over?" depends on the detector. Copy fidelity varies by language, and a fixed 60/64 threshold misses sloppy copiers. Results about *whether* soups jump (E-70: F 60/60 vs 15/60) are less exposed than results about *how fast*, but the 15 "non-jumps" there could hide some sloppy take-overs too.

**Changed:** `scripts/bff_multigen.py`; D-052 (report jump times under both definitions; require agreement).

**Lesson:** when a soup scores "no jump" while HOE sits at 6, look at the soup before accepting the verdict.

**Next:** (a) validate a copy-fidelity threshold (for example 56/64) with positive controls (sloppy copiers), negative controls (partial copiers that never take over) and a null, then re-score E-70–E-72 under it; (b) pre-register the speed predictors again only after that; (c) a language outside BFF.

---

## J-073 · 2026-11-10 · E-71: the copier count predicts speed within a language, not across languages; the share of copiers that work does better

**Question (pre-registered, `docs/data/e71-preregistration.md`, commit `ea680f8`):** E-70 found, as an exploratory result, that F rules with more self-sufficient copiers in the census make replicators sooner (ρ = −0.80 over 15 rules). Is this a graded predictor, or a difference between variants? Test on the 22 F rules of the E-70 census (v1–v5) that E-70 did not run soups in, 8 soups each, jump time at 50-round resolution. (1) Pooled Spearman ρ ≤ −0.4, one-sided permutation p < 0.01. (2) Within variants (v1, v3, v4, v5): the sum of the within-variant ρ is negative, with p < 0.05 against permutations within each variant.

**Ran:** `scripts/bff_copiercount.py --workers 11` (176 soups of 2^14 programs, about 1 h; D-050 criterion with checkpoints every 50 rounds). The first two runs crashed while writing the summary (numpy bool in JSON). The soups were cached and the analysis reran unchanged. Figure: `scripts/e71_figure.py` → `docs/assets/report/e71-copiercount.png`.

**Found:**
- **P1 (pooled) fail:** ρ = −0.34, permutation p = 0.06.
- **P2 (within variant) pass:** the sum of within-variant ρ is −2.45, p = 0.006. Every variant is negative: v1 −0.55, v3 −0.60, v4 −0.80, v5 −0.50.
- **Jump rate:** 165/176 soups jumped (94%). 21 of 22 F rules jumped in at least 5 of 8 soups. **One F rule failed completely: v1/h1 = 68**, 0/8 in 16,000 rounds. It has 4,317 copiers but only 18 self-sufficient ones, and its soups never had more than 1 copier among the 40 most common programs (HOE stayed below 0.6, so the detector did not miss a jump). The F class is not a guarantee at the edge of the band.
- **Secondary:**
  - The total copier count carries no information (pooled ρ = +0.01).
  - The **self-sufficient fraction** (self-sufficient copiers ÷ all copiers) does better: pooled ρ = −0.48 (p = 0.012), within-variant p = 0.004.
  - The v1 contrast failed: v1/60, with 1 self-sufficient copier, was fast (median 200 rounds), while v1/67, with 1,525, was slow (6,850; 3 of 8 soups did not jump).
  - Pooling E-70's 15 rules with E-71's 22 gives ρ = −0.44 (p = 0.006). This mixes 4-soup and 8-soup estimates and 250- and 50-round checkpoints.

**Correction (J-074):** the pooled failure below depends on the jump definition: with an HOE-based jump time the pooled test gives ρ = −0.57, p = 0.003. Read "across languages" as *not shown either way*. The within-variant result holds under both definitions.

**Interpretation:** within a language, versions with more short self-copiers tend to make replicators sooner. Across languages the raw count does not compare: v1 counts thousands, because `[.]` is a complete copier there, yet some v1 versions are slow. E-70's ρ = −0.80 was largely a between-variant effect. A number that compares across languages may be the *share* of copiers whose copy copies (exploratory here). The v1/68 failure suggests that one generation of copying (the F test) is not always enough: in v1 at h1 = 68 copies may drift off position over generations. That is untested.

**Changed:** `scripts/bff_copiercount.py`, `scripts/e71_figure.py`. No detector or `emergence/` change.

**Lesson:** an exploratory correlation that pools groups can be a difference between the groups; pre-registering a within-group test is what separated the two here.

**Next:** (a) a multi-generation version of the F test (does the copy of the copy still copy, 2–3 generations?) to explain v1/68 and v1/67, computed before any new soups; (b) pre-register the self-sufficient fraction as the graded predictor, on fresh rules (e.g. the two-head or tape-length families); (c) a language outside the BFF family.

---

## J-072 · 2026-11-09 · E-70: change what an instruction does, and the F predictor holds in all five variants (60/60 vs 15/60)

**Question (pre-registered, `docs/data/e70-preregistration.md`, commit `7f3e1f0`):** every test of the F predictor (E-61–E-69) kept BFF's instruction semantics fixed. Does it carry over when one instruction does something else? Five variants (D-051): `.` then both heads +1 (v1) or −1 (v2); `,` then both heads +1 (v3); `[` `]` test head1's byte (v4); `+` `−` act on head1's byte (v5), each × 128 head1 starts. (1) Census: is h1 = 64 F in every variant, with every F rule in 48–80? (2) Soups: F ≥ 75% jump, others ≤ 25%, Fisher p < 0.01, F ≥ others in every variant.

**Ran:** `scripts/bff_instrset.py --workers 11` (census 28 min, 768 rules incl. v0; soups 2 h 26 min, 120 soups of 2^14 programs, D-050 criterion). Figures: `scripts/e70_figure.py`, `scripts/e70_soup_picture.py`. Pilot results (h1 = 64 F in every variant; a few soups) were seen before the pre-registration and disclosed in it.

**Found:**
- **Equivalence:** v0 reproduces E-61 on all 128 rules.
- **P1 pass:** F rules v1 60–68, v2 62–66, v3 61–68, v4 61–67, v5 61–68 (v0 61–68); all self-sufficient copiers forward. Self-sufficient kernels at h1 = 64: v1 3,893 (e.g. `<>[.]`: the auto-advancing copy makes `[.]` a complete copier), v3 535, v2 314, v5 142, v0 137, v4 99.
- **P2 pass:** F soups **60/60** jumped (median T 250–750 per rule, slowest v5/h1 = 67 at 1,500–3,500); other rules **15/60** (exactly at the 25% limit); one-sided Fisher p = 2e-20; F ≥ others in each variant (12/12 vs 1, 3, 3, 4, 4 of 12). 8 of the 15 non-F jumps are rules one step outside the band (v4/h1 = 59, v5/h1 = 60: 4/4 each, T 750–6,250); the other 7 from v2/7 (3/4), v3/83 (2/4), v3/125 (1/4), v1/123 (1/4, at 14,500). Non-F median T 3,000.
- **Secondary (exploratory):** over the 15 F rules, number of self-sufficient copiers vs median T: ρ = −0.80, p = 0.0004 (E-65 within one family: ρ = −0.51, p = 0.12).

**Interpretation:** the F property, computed from the rule alone, has now predicted fast replicator emergence across four kinds of rule change (head1 start, both head starts, program length, instruction semantics), in pre-registered tests; within F rules, the abundance of short self-copiers looks like a graded predictor of speed. Caveats: the five variants are hand-picked, not a sample of languages; non-F rules next to the band often jump too (the census's 5–6-instruction window misses slightly longer or shifted self-copiers, as in E-63/E-64); the graded result was exploratory and mixes variants; nothing here bears on level 5.

**Lesson:** packing the variant into the rule code that every tool already passes along (D-051) made the whole census/soup pipeline reusable without touching it, and the v0 equivalence check came for free.

**Next:** confirm the copier-count/speed link with fresh rules (pre-registered, e.g. F rules from all four families binned by count); try a language outside the BFF family; level-5 questions in fast variants (v1 jumps in 250 rounds) need fitness assays under the variant's own interpreter.

---

## J-071 · 2026-11-09 · E-69: with the same amount of code, short programs catch up partly; the F predictor is clean again

**Question (pre-registered, `docs/data/e69-preregistration.md`, commit `6f5c663`):** is E-68's length effect a soup-size effect? E-68 kept 2^14 programs at every L, so short-program soups held fewer bytes, and E-50 found the jump rate ∝ soup size. E-69 reran E-68's 12 rules at L = 16 and 32 (3 F + 3 other each, 4 soups each) with 2^21 bytes per soup, like E-68's L = 128 soups (2^17 programs at L = 16, 2^16 at L = 32).

**Ran:** `scripts/bff_tapelength_bytes.py --workers 11` (3 h 24 min; 48 soups; E-68's `soup_job` and D-050 unchanged).

**Found:**
- **Primary: undecided** (thresholds: "soup size explains" if F ≥ 50% at L = 16 and ≥ 75% at L = 32; "length itself matters" if ≤ 25% at L = 16). F soups: **L = 16 4/12** (E-68: 0/12), **L = 32 10/12** (E-68: 6/12). Our prediction ("length itself matters") was not borne out either.
- **Other rules: 0/24** (E-68 at 2^14: 1/24). Post hoc, at matched bytes: F 14/24 vs other 0/24 (Fisher one-sided p = 4e-6); including L = 128 from E-68 (same bytes): F 26/36 vs other 5/36.
- Every jump was a real take-over: forward, aligned copiers, 10–40 of the 40 most common programs and HOE 1.9–5.1 at T + 1,000. L = 16 jumps came from 2 of the 3 F rules (h1 = 15: 3/4 at round 1,500; h1 = 16: 1/4 at 500; h1 = 14: 0/4).
- At equal bytes, success still rises with length: 4/12 (L = 16), 10/12 (L = 32), 12/12 (L = 128).

**Interpretation:** soup size accounts for much of E-68's length effect (it doubled or more the F success at L = 16 and 32, and the predictor separates F from other rules cleanly once bytes are matched), but not all of it: with the same bytes, 16-byte programs still make replicators less often than 32- or 128-byte ones. Two caveats: a round at 2^17 programs runs 8× more pairings than at 2^14, so "same bytes" is not "same compute per round"; and 4 soups per rule leaves wide intervals. The census predictor is now supported at four lengths for *which* rules can be fast; the *pace* depends on the amount of code and, to a lesser degree, on length.

**Lesson:** when changing one property of a language, ask what else changes with it (here, total bytes); a matched control converted a failed prediction into a mostly explained one.

**Next:** instruction-set variants (e.g. an auto-advancing copy instruction) need a variant switch in `scripts/bff_kernels.c run()`; check equivalence at the default first, then census before soups.

---

## J-070 · 2026-11-09 · E-68: change the program length, and F rules still sit half a tape apart; but short programs make no replicators at all

**Question (pre-registered, `docs/data/e68-preregistration.md`, commit `d2c0138`):** E-60–E-65 tested the F predictor only with 64-byte programs. Does it carry over when the language itself changes, here the program length L (tape 2L)? (1) Census: is h1 = L an F rule at every L, with every F rule within L/8 of L? (2) Soups: do F rules make replicators fast at every length?

**Ran:** `scripts/bff_tapelength.py` (census 30 min, 480 rules; soups 85 min, 76 soups of 2^14 programs). `bff_kernels.set_length(L)` scales the copy threshold (L − L/16) and shift window (L/4); the C interpreter already took L. Jump criterion D-050 (copiers only; HOE is not calibrated at other L). Figure: `scripts/e68_figure.py` → `docs/assets/report/e68-tapelength.png`.

**Found:**
- **Equivalence:** the census at L = 64 reproduces E-61 rule by rule.
- **P1 pass:** F rules are h1 = 14–17 (L = 16), 30–34 (32), 61–68 (64), 125–136 (128): always around h1 = L, the band widening with L; every self-sufficient copier is forward and the same short kernels head the list at every L (`[<{,]`, `[{<,]`). 99–138 self-sufficient kernels per h1 = L rule.
- **P2 fail:** F soups 18/36 jumped, other rules 6/36 (one-sided Fisher p = 0.003; each L has F ≥ other). By length: **L = 16: 0/12 F, 0/12 other** (HOE drifts down to −0.35, ~40 steps per pair, not one copier among the top 40 in 16,000 rounds); L = 32: 6/12 vs 1/12; L = 64 (h1 = 64 only): 4/4; **L = 128: 12/12 vs 5/12**.
- **Secondary:** at h1 = L, jump time falls with L (ρ = −0.90, p = 2e-6): L = 128 4/4 at 250 rounds, L = 64 250–500, L = 32 1/4 at 10,750, L = 16 none.
- Non-F jumps: at L = 128, h1 = 8 and 15 jumped with shifted reverse copiers (as the one C jump of E-64), and h1 = 15 and 143 (and L = 32 h1 = 7) with aligned forward copiers longer than the 6-instruction census window. One L = 32 F jump (h1 = 33, T = 250) was confirmed at HOE 0.25 with 11 copiers, i.e. before take-over (D-050 weakness).

**Interpretation:** the census part of the predictor is a property of the language geometry and carries over cleanly: a short copier's copy works only when the pointers start half a tape apart. But whether a soup actually gets there depends strongly on length: short programs (16 bytes) made nothing, long programs (128 bytes) made replicators even in many non-F rules. **Confound:** soups had the same number of programs, so an L = 128 soup held 8× the bytes of an L = 16 soup, and E-50 found the jump rate ∝ soup size. E-69 tests this at matched bytes.

**Lesson:** a predictor of *which* rules can make replicators is not a predictor of *whether* a given soup will; the soup's raw material (here, length or bytes) sets the pace.

**Next:** E-69 (matched bytes, L = 16 and 32): soup size explains much but not all (J-071).

---

## J-069 · 2026-11-09 · E-67: no parasites further down the ranking either

**Question (pre-registered, `docs/data/e67-preregistration.md`, commit `543b2b8`):** E-66 found no parasites among the 40 most common programs. Are there any among rarer ones? Final snapshot of each of the 7 jumped E-54 soups; 20 random exact programs per soup in each of three strata (6–40 copies, 2–5 copies, single), 420 in all; replicator test repeated 10×, parasite test (with the self-copy check) on those that never grew.

**Ran:** `scripts/bff_parasites_rare.py --workers 11` (10 min).

**Found:**
- **P1 pass: 0 parasites in 420 programs.**
- **P2 pass:** self-copiers 99.3% (6–40 copies), 96.4% (2–5), 69.3% (singletons).
- **P3:** the 49 non-self-copiers are 29 "not copied" and 20 "context self-copiers" (copy themselves into any partner whose code never runs, die when running second; 17 of them singletons). Non-self-copiers are unrelated to the soup's common programs (median 55–62 of 64 bytes differ from the nearest top-40 program, either orientation); self-copiers are closer (median 22–34).

**Interpretation:** across all abundance levels we sampled, these soups contain self-copiers, newly arisen unrelated programs that nothing copies, and a few unrelated programs that copy themselves but cannot hold their ground; no program is maintained by others' copying. Parasitism, the classic first step of ecological complexity in Tierra-like systems, does not appear in standard BFF at 2^16 programs over 20,000 rounds after the jump. One plausible reason (not tested): BFF replicators copy a fixed half-tape window regardless of content, so a parasite would have to be copied by a host that runs *second*, which in BFF happens only when the first program's code falls through into the host (as in our hand-made parasite). Evidence: pre-registered negative, 7 soups, final snapshots only.

**Lesson:** after fixing the test (J-068), the negative held up in a second, independent sample.

**Next:** the instruction-set / tape-length family (does a richer language allow parasites or other ecology?).

---

## J-068 · 2026-11-09 · E-66: almost every common program in a jumped soup copies itself; the "non-replicators" were bad luck in our test, and no parasites were found

**Question (pre-registered, `docs/data/e66-preregistration.md`, commit `4807796`):** E-54 found that only 22–78% of the 40 most common programs in jumped soups pass the replicator test. Are the others **parasites**, copied by the replicators without copying themselves? A pilot for the new parasite detector (D-048) showed that the replicator test gives different verdicts for the same program with different seeds, so part A first repeats it 10 times on all 2,800 E-54 programs; part B runs the parasite test on programs whose copies never grew.

**Ran:** `scripts/bff_parasites.py --workers 11` (77 min; first launch crashed at the end of part A on a negative seed key for the null programs and saved nothing; fixed in `32081a9` with a result cache, tests and seeds unchanged). Post hoc re-scoring of part B: `scripts/e66_rescore.py`. Figure: `scripts/e66_figure.py` → `docs/assets/report/e66-parasites.png`.

**Found:**
- **P1 pass:** of the 602 programs E-54 called "no replication", **597 (99.2%)** grew in at least one of 10 repeats; every soup ≥ 95%.
- **P2 pass:** **2,795 of 2,800 (99.8%)** common programs are self-copiers by the repeated test (single-test "replicator" in E-54: 50.8%). The verdict mix over all 28,000 repeats (52% replicator, 27% one generation, 22% no replication) is almost exactly E-54's (51/28/22): **the single-test differences between programs were mostly chance.** Copies of a typical program grew in ~78% of tests (8 starting copies are often all lost before they spread); programs E-54 called replicators grew in 81%, those it called non-replicators in 73%.
- **P3 pass:** 0 of 80 common programs of two pre-transition soups (HOE 0.49, 0.56) grew in any repeat.
- **P4 fail:** true non-copiers are rare (5 of 2,800, 0.18%, all in soup 5401), but the parasite + by-product share was 2/5, below the 50% predicted.
- **The two "parasites" were not parasites.** Inspection: each copies itself into **every** partner whose code never runs (200/200 "halting" partners) and into 80% of random partners, but is destroyed whenever it runs second; alone among random programs its copies therefore shrink. It is a copier that only persists among partners that spare it. The detector now checks this (self-copy rate into halting partners; verdict "context self-copier"); with it, part B is **0 parasites, 2 context self-copiers, 3 not copied** (post hoc, same data).

**Changed:** `observatory/program_parasites.py` (D-048: parasite test, repeated `alone_test`, self-copy check, `CONTEXT_COPIER` control); benchmark section 14 (8 checks: positive, two negatives, three deceptive incl. the E-66 program, selection-aware null); D-049 (single replicator-test verdicts on common soup programs are lower bounds).

**Interpretation:** after a jump, the soup's common programs are essentially all self-copiers; E-54's "soups stay mixed" was a property of our test, not of the soups. We found **no parasites** among common programs of 7 soups (level-3 ecology question answered negatively at this scale; a rare parasite below the top 40 would be missed). E-54's primary result is unaffected (it compared programs that passed).

**Lesson:** a stochastic test run once per item measures luck as much as the item; repeat it before reading differences between items. And a detector that counts copies must ask who made them.

**Next:** parasites, if they exist, are rare; looking further down the abundance ranking needs the same test on less common programs. The instruction-set / tape-length family remains the main open lead.

---

## J-067 · 2026-11-09 · E-65: with 7 new rules, the predictor holds rule by rule; the graded version is not established

**Question (pre-registered, `docs/data/e65-preregistration.md`, commit `febabe2`):** E-64's F arm rested on 3 rules. In 768 new random rules of the two-head-start family, do **all** F rules make replicators quickly (≥ 75% of soups, and ≥ 2 of 4 soups in ≥ 75% of F rules), and C rules not? Secondary: does the number of self-sufficient short copiers predict how soon (Spearman with median jump round)?

**Ran:** `scripts/bff_twoheads2.py --workers 10` (census 1,809 s; 44 soups of 2^14, ~55 min; D-047 exactly as E-62–E-64). Figure: `scripts/e65_figure.py` → `docs/assets/report/e65-twoheads.png`.

**Found:**
- **Census:** 7 F rules, 118 C, 643 none. Every self-sufficient copier copies forwards.
- **Primary: pass.** F rules **26 of 28** soups (every rule ≥ 3 of 4: 4/4 in five rules, 3/4 in two); C rules (4 drawn at random) **1 of 16**; Fisher p = 9 × 10⁻⁹. All 26 F jumps end in exact forward copiers (shift 0; 20–40 of 40 programs). The one C jump (g = 11, h = 60, round 9,000) also ends in exact forward copiers: a longer copier evolved.
- **Secondary: not significant.** ρ = −0.51 between self-sufficient copiers and median jump round, one-sided p = 0.12 (7 rules). The two slowest F rules have 1 and 80 such copiers, so the count is at best a weak guide. We gave it a 40% chance.
- **Pooled E-64 + E-65 (1,024 random rules):** F rules 36 of 40 soups (10 rules), C rules 2 of 32 (8 rules).
- **Descriptive, post hoc:** all 10 F rules of the 1,024 have pointers about half a tape apart (h − g = 60–68 mod 128) **and** pointer 1 within a few bytes of a half boundary (g ∈ 2, 60–67, 124–126). Of 76 rules with that offset, the other 66 are C (8) or have no short copier (58). So in this family "F" amounts to: the two pointers start at matching positions in the two halves, give or take a few bytes, which lets a short loop copy one half onto the other.

**Interpretation:** the predictor now has two pre-registered out-of-sample confirmations in the two-head family (E-64, E-65) on top of the one-pointer family (E-60–E-63): 10 of 10 F rules make replicators in most soups, 2 of 32 C-rule soups do. It is binary: whether a rule allows a short self-copying copier matters; how many it allows was not shown to matter. The geometric reading (aligned pointers in the two halves) is post hoc and specific to this family. Evidence: pre-registered replication; still one language, 2^14 soups.

**Lesson:** a replication designed to include every F rule found, not a sample of 3, closed the main weakness of E-64; the graded hypothesis was rightly kept secondary.

**Next:** a family that changes the instruction set or tape length, where the geometry is different; parasites in long soups (J-066).

---

## J-066 · 2026-11-09 · E-54: seven long-running soups, 20,000 rounds after the jump: later replicators are still not fitter

**Question (pre-registered, `docs/data/e54-preregistration.md`, commit `2601c48`; analysis script `10d2e86` written before the run finished):** with 3 soups and 10,000 rounds, later replicators were not reliably fitter than earlier ones (E-48, E-49, E-51, E-53). With more jumped soups (2^16 programs) and a 16,000-round gap, is there an advantage, measured with the kin-free invasion assay (D-044)?

**Ran:** `scripts/bff_long.py` (12 new soups, seeds 5400–5411, up to 24,000 rounds; 3 E-50 soups continued), each jumped soup run to T + 20,000 (~14 h on 11 cores). **Deviation:** a power loss at 22:19 stopped soups 5302 and 5402; they continued from their last snapshots (31,750 and 32,250) with new random streams (`scripts/bff_long_resume.py`). For 5302 this affects only the T+20000 background; for 5402 the late candidates and the T+20000 background come from the resumed run. Analysis: `scripts/bff_long_analysis.py --workers 11` (22 min). Figure: `scripts/e54_figure.py` → `docs/assets/report/e54-long-soups.png`.

**Found:**
- **Jumps:** 4 of 12 new soups jumped by 24,000 rounds (5401 at 10,250, 5402 at 22,250, 5406 at 16,750, 5410 at 750); E-50 predicted about half (5/10 there). With the 3 continued soups, 7 jumped soups; each gave 6 early and 6 late distinct verified replicators; none had kin in the backgrounds (0 dropped).
- **Primary: not significant, as predicted.** D = −0.15 (sum over soups of mean s late − mean s early), permutation p = 0.64. Per soup: −0.49 (5401), −0.03, −0.01, −0.01, +0.07, +0.13, +0.19.
- **Secondary (future background, T+20000):** D = −0.50, p = 0.95; later code is not better at invading the future either.
- **Descriptive:** verified replicators are only **22–78%** of the 40 most common distinct programs at every snapshot (2,800 tests: 1,423 replicators, 775 copy for one generation only, 602 do not replicate). No trend over 20,000 rounds; soups stay a mix of copiers, partial copiers and non-copiers. **Corrected by E-66 (J-068):** with the test repeated 10 times, 99.8% of these programs copy themselves; the single-test split was mostly chance.
- Invasion scores are mostly below 0 for both groups: a few copies of a single soup program usually lose ground in a sample of the soup.

**Interpretation:** across 7 soups and 16,000 rounds, the most sensitive calibrated assay we have shows no sign that later replicators are fitter. Together with E-48–E-53 this makes "no detectable cumulative adaptation after the jump in standard BFF at these scales" the best-supported reading: the post-jump change looks mostly neutral (drift). Level 5 is not shown. Caveats: the assay was calibrated on hand-written variants with large built-in differences (J-050, J-052); small advantages, or adaptation that only shows in the soup's own context, would be missed. The jump rate (4/12) is lower than E-50's estimate but within chance (E-50 5/10).

**Lesson:** the long run was worth it as a firm negative: more soups and a longer gap did not reveal a trend hidden by noise. The power-loss deviation was small and is recorded.

**Next:** the large share of programs that copy once or not at all is the obvious lead for parasitism: are the non-copiers copied *by* the replicators (true parasites), or debris? That needs a "copied but does not copy" measure with a null. Head-start rules where soups jump in minutes (E-56) make the level-5 question much cheaper to ask, but the fitness assays then need to run under the rule's own interpreter.

---

## J-065 · 2026-11-09 · E-64: the "copy that copies" predictor carries over to a second family of rules

**Question (pre-registered, `docs/data/e64-preregistration.md`, commit `1c756d5`):** E-60–E-63 found, in the family "pointer 2 starts at byte h", that soups make replicators fast exactly in the rules whose short copiers include one whose single copy copies again (F). Does the same rule-level property, computed before any soup is run, predict fast replicators in a **new family**: pointer 1 starts at byte g and pointer 2 at byte h (g = 1..127, h = 0..127)?

**Ran:** `scripts/bff_twoheads.py` (census of 256 random (g, h) rules, 669 s; 28 soups of 2^14, 2,588 s; strict D-047 criterion, up to 16,000 rounds). Figure: `scripts/e64_figure.py` → `docs/assets/report/e64-twoheads.png`.

**Found:**
- **Census:** 3 F rules ((2, 64), (60, 126), (67, 127)), 33 C rules (short copiers, none self-sufficient), 220 with no short copier of 5–6 instructions.
- **Primary: pass.** F rules: **10 of 12** soups made real replicators (4/4, 4/4, 2/4; T = 250–14,750); C rules (4 drawn at random): **1 of 16** (0/4, 0/4, 0/4, 1/4). One-sided Fisher p = 5 × 10⁻⁵. F ≥ 75% and C ≤ 25% as registered. Only 3 F rules exist in the sample, so the F arm rests on 3 rules.
- **Secondary:** all 11 self-sufficient short copiers copy forwards (as predicted). Copiers at the end of the 10 F-rule jumps: forward, nearly all exact (shift 0; one soup has 5 of 25 at shift 1), as predicted. The one C-rule jump (g = 124, h = 3, at round 13,250) is different: **reverse** copiers with shifts −1 to −4, a kind the 5–6-instruction census does not count as self-sufficient.
- Descriptive, post hoc: the three F rules have h − g = 62, 66, 60 (mod 128), close to the F′ band 61–68 of the one-pointer family (g = 0). But two C rules have offsets 64 and 68, so the offset alone is not the predictor: the absolute position matters too.
- The slowest F rule (67, 127; 2 of 4) has the fewest self-sufficient copiers (2), against 3 and 6 in the two 4-of-4 rules.

**Interpretation:** the predictor found in one family (does the rule's simplest copier make a copy that copies?) predicted, before running soups, which rules of a second, much larger family make replicators quickly: 10 of 12 vs 1 of 16 against rules that also have short copiers. This is now a "which rules make it likely" result supported in two families, though both are start-position variants of one language (BFF), the F arm has only 3 rules, and soups are 2^14. Evidence: pre-registered, out-of-family prediction.

**Lesson:** the census is cheap (11 minutes for 256 rules) and its prediction is strong; the rare exceptions (a slow F rule, a C rule that jumped with shifted reverse copiers) point to what the 5–6-instruction census misses: longer or shifted copiers that soups can still find given enough time.

**Next:** a family that changes the instruction set or the tape length, not only start positions; and a graded predictor (number of self-sufficient copiers, or the length of the shortest one) to explain speed within F.

---

## J-064 · 2026-11-08 · E-63: rules just outside the F′ band are slow: a sharp boundary at the edge of "a copy that copies"

**Question (pre-registered, `docs/data/e63-preregistration.md`, commit `2c9c5fa`):** E-62 found every F′ rule (61–68) makes exact replicators fast under D-047 (28/28). Are rules just outside F′, which still have plenty of short forward copiers (shifted 5–16 bytes) but none whose single copy copies, slow under the same strict criterion?

**Ran:** `scripts/bff_outside.py --workers 10` (837 s). Rules drawn at random from {59, 60, 69–82}: **72, 74, 80, 82**; 4 soups of 2^14 each, plus 4 at h = 64 as a concurrent positive control; D-047 exactly as E-62.

**Found:**
- **Primary: pass. Outside F′: 1 of 16 soups made real replicators** (rule 72, soup 6300, T = 3,000; 40 of 40 programs exact copiers at the end), against 28 of 28 in F′ rules (E-62); one-sided Fisher p = 7 × 10⁻¹¹. **Control h = 64: 4 of 4** (T = 250, 250, 250, 2,250).
- The 15 others never had a candidate: 0–1 copiers among 40 after 16,000 rounds, 290–420 steps per pair, although their rules have 110–138 short forward copiers each (E-61 census).
- Secondary: the one jump outside F′ is exact (shift 0), as predicted: the soup evolved a longer copier that lands its copy at byte 64.

**Interpretation:** across E-60–E-63 the band where soups make replicators fast is exactly the band where a short copier's single copy can copy again (h = 61–68): 32 of 32 soups inside, 1 of 16 just outside (plus 0–1 of 16 in the backward-copier rules tested in E-60 with a weaker criterion). The number of short copiers does not predict it: rules 69–80 have as many as 66–68. What matters is whether the simplest copier's **copy** works, which is a property of the rule computable in seconds. Evidence: a pre-registered prediction about 4 untested rules, with a concurrent control; still one family of rule variants and soups of 2^14.

**Lesson:** after two failed hypotheses (E-61's one-generation test with a weak criterion, E-62's lineages), the simplest rule-level property survived a clean test. The criterion (D-047) mattered as much as the hypothesis.

**Next:** test the same predictor outside the head-start family (e.g. different instruction sets or tape lengths), where the "copy that copies" property is computed before the soups are run.

---

## J-063 · 2026-11-08 · E-62: lineage persistence does not separate the rules; every rule from 61 to 68 makes exact replicators

**Question (pre-registered, `docs/data/e62-preregistration.md`, commit `a39789e`):** J-062 suggested that what predicts fast replicators is a short copier whose **lineage persists** (exact copies), not one good copy. Census of lineage persistence (64 generations, shift-aware) in all 128 rules; fresh soups in E-61's F′ rules under the strict D-047 criterion (≥ 10 copiers among 40 at T + 1,000; a failed candidate is dropped and the soup runs on to 16,000).

**Ran:** `scripts/bff_lineage.py` (census 361 s; 28 soups of 2^14, 994 s; 9 workers). Controls passed (hand-written replicator and `[.>}]` at h = 64 persist; `[.>}]` at h = 66 does not; 0 of 100 random).

**Found:**
- **Primary 1: fail.** P = **62–66**, not 62–65: rule 66 has 2 persistent copiers (shift 1 and 2, e.g. `.[>.}]`). No persistent copier outside 62–66.
- **Primary 2: fail.** Group P (62, 63, 65, 66): **16 of 16** jumped; group N (61, 67, 68): **12 of 12** (p = 1). Every one of the 28 soups ended with 13–40 copiers among 40, **all at shift 0 (exact)** except 4 programs in two soups.
- Median T: 63: 750; 61: 1,125; 62: 1,375; 65: 2,500; 67: 2,500; 66: 4,125; 68: 5,375 (2 of 4 soups after 8,000). Rule 68 is the slowest, but the groups overlap completely.
- 6 candidates were dropped (0–7 copiers at T + 1,000) and those soups went on to real jumps later.

**Interpretation:** the lineage idea is wrong as a predictor here: soups in rules with only drifting short copiers (61, 67, 68) evolve exact copiers within a few thousand rounds anyway. **Correction to J-062:** its "7 of 16 by the strict reading" came from the E-61 soups stopping at T + 1,000 after an early false candidate. Run on under D-047, the same rules give 12 of 12. So E-61's registered result (16/16) was right for the wrong reason, and the F′ class (a short copier whose single copy copies, at any small shift) remains the best predictor we have: all 8 F′ rules are fast (44 of 44 soups across E-60–E-62 by the strict criterion where measured). Still untested: whether rules just outside F′ (e.g. 59–60, 69–80, forward copiers that fail the one-copy test) are slow under the strict criterion.

**Lesson:** a jump criterion that stops a soup on a false candidate under-counts; "drop and continue" is the right design (now D-047). And a mechanism that sounded right (lineages must persist) failed its test because evolution repairs drift quickly.

**Next:** soups in rules just outside F′ under D-047, pre-registered (E-63).

---

## J-062 · 2026-11-08 · E-61: a shift-aware census widens the fast rules to h = 61–68, but what takes over is exact copiers

**Question (pre-registered, `docs/data/e61-preregistration.md`, commit `5b65cc2`):** J-061 showed our copier classifier misses copies placed a few bytes off byte 64. Redo E-60's census of all 128 head-start rules with a shift-aware classifier (`classify_shift`, |d| ≤ 16), and run soups in any rule that becomes F.

**Ran:** `scripts/bff_shift_census.py --part census` (9 workers, 355 s), then `--part soups` (16 soups of 2^14 in rules 61, 66, 67, 68, shift-aware D-046 criterion; 9 workers, 264 s).

**Found:**
- **Census:** **55 of 128 rules have short copiers** once shifts count (E-60: 12). Shifts follow the geometry: backward copiers in rules 0–10 and 115–127 sit about h (or h − 128) bytes off; forward copiers in 59–82 about h − 64. Checks passed: total copiers ≥ E-60's in every rule; F′ contains 62–65.
- **Primary 1: pass.** F′ = **61–68** (new: 61, 66, 67, 68), all self-sufficient copiers forward. No backward copier is self-sufficient at any shift (rules 0–10 and 115–127 have 75–233 shifted copiers each, 0 self-sufficient).
- **Primary 2: pass as registered: 16 of 16 soups jumped**, T = 250–2,750 (one-sided Fisher vs E-60's S soups 2/16: p = 2.5 × 10⁻⁷).
- **But the bar is weak (as J-060 warned).** 8 of the 16 "jumps" are HOE crossings at rounds 250–500 with 0–4 copiers among 40 at T + 1,000 and 190–680 steps per pair: early waves of short programs, not replicator soups. With J-060's stricter reading (≥ 10 copiers among 40 at T + 1,000): **rule 61: 3/4, 66: 1/4, 67: 3/4, 68: 0/4; 7 of 16** (E-60's F rules 62, 63, 65: 11 of 12; S rules: 0–1 of 16).
- **In every real jump the takeover is by exact copiers (shift 0, 39–40 of 40 programs), even in rules 61, 66 and 67, where the census found no exact copier of ≤ 6 instructions.** The soups evolved longer exact copiers (heads adjusted to land the copy at byte 64).
- Exploratory, from Part A (addendum to the pre-registration, written while Part B ran; six soups had finished seconds earlier, unseen): a copier at shift d makes a child shifted by d, a grandchild by 2d, and so on, so its lineage loses the kernel. In 32-generation product chains, exact copiers lasted all 32 generations, shifted ones mostly failed within 1–22.

**Interpretation:** "has a one-generation self-sufficient short copier" over-predicts: by the strict reading the four new rules are in between (7/16), and rule 68, whose only self-sufficient copier is shifted by 2–4 bytes, made none. What took over everywhere was an **exact** copier. A better rule-level predictor is probably "an exact copy is reachable", i.e. a lineage that persists. Not yet tested as a prediction. The primary passes, but read strictly the result is weaker than E-60's. Evidence: 16 soups in 4 rules plus a census; strict reading not pre-registered for this experiment.

**Lesson:** a one-generation copy test cannot tell a lasting replicator from a lineage that drifts away; replication is a property of lineages, not of single copy events. And a jump criterion with "≥ 1 copier" accepts early waves (D-047).

**Correction (J-063):** the strict reading below was confounded: these soups stopped at T + 1,000 after early false candidates; run on under D-047, rules 61, 67, 68 give 12 of 12 real jumps.

**Next (superseded by J-063):** a lineage-persistence census (does a copier's line still copy after 64 generations, shift-aware?) across all 128 rules, pre-registered, predicting fast soups in 62–65 and slower in 61, 66–68; the D-047 jump criterion.

---

## J-061 · 2026-11-08 · E-60 follow-up (exploratory): the rule-7 "puzzle" soup is full of shifted mirror copiers

**Question (not pre-registered; follow-up to J-060's open puzzle):** soup 6031 (head1 starts at byte 7) sat in a high-order, high-execution state from round ~7,000 with no copier by our classifier, which only recognises copies placed exactly at byte 64 (or mirrored there). Do its common programs copy themselves to a *shifted* position?

**Ran:** `scripts/e60_shifted.py` (replay of soup 6031 to round 14,750 = T + 1,000, deterministic). For each of the 40 most common distinct programs, 4 runs against random partners; the best agreement of the partner half with the program rotated by any offset d (0–63), forwards or mirrored. A copy counts at ≥ 56 of 64 bytes in ≥ 3 of 4 runs. Started by the 10th scheduled session; cut off by a power loss at 22:19 and re-run from scratch.

**Found:**
- **25 of 40 programs are copiers**: 24 write a **mirrored copy shifted by 6–8 bytes** (56–58 of 64 bytes agree, the rest is the part shifted past the partner's end); 1 is an ordinary aligned mirror copier (the one the classifier saw).
- The copies are not trivial: the programs have 40–52 distinct byte values, the most common byte at most 12% (a constant writer would match a constant program, not these).
- A shift of ~7 is what a backward copier gets when its writing head starts at byte 7 instead of 0.

**Interpretation:** soup 6031 is a real replicator soup, probably from round ~7,000 (when its HOE rose), not 13,750. So J-060's stricter reading ("S rules 0 of 16") is wrong: at least **1 of 16** S soups made replicators, still much later than any F soup (7,000 vs 250–2,500, one at 10,250). The pre-registered primary (F 12/12 vs S 2/16) stands. But the census behind the F/S split has the same blind spot: rule 7 may have short *shifted* copiers that we never counted, so "116 of 128 rules have no short copier" is an under-count. Evidence: exploratory, one soup.

**Lesson:** a detector tuned on one rule silently misses the same structure under a neighbouring rule. Any census across rules must be invariant to the rule's own geometry (here, where the heads start).

**Next:** a shift-aware copier census of all 128 rules, pre-registered, re-testing the F/S prediction.

---

## J-060 · 2026-11-08 · E-60: across all 128 head-start rules, only four have self-sufficient short copiers, and only those make replicators fast

**Question (pre-registered, `docs/data/e60-preregistration.md`, commit `5c6183f`):** does "has a self-sufficient copier of ≤ 6 instructions" (F) vs not (S) predict fast replicator emergence across the whole family of rules "head1 starts at byte h", h = 0..127?

**Ran:** E-60, `scripts/bff_headstart.py`. Census of all 128 rules (5 workers, 279 s); then 4 soups of 2^14 for each of 3 F rules and 4 S rules (picked at random with seed 60, excluding 0, 64, 127), D-046 criterion as in E-59, up to 16,000 rounds (5 workers, ~45 min).

**Found:**
- **Census:** only **h = 62, 63, 64, 65 are F** (self-sufficient copiers 4, 47, 96, 10; all forward). Short copiers of any kind exist only near h = 0 (backward: 53, 4), h = 64 (forward) and h = 127 (backward: 2, 32, 130 at 125–127); **116 of 128 rules have no copier of ≤ 6 instructions at all**. Rules 0, 64, 127 agree with E-55/E-57/E-58.
- The F class had only 3 rules besides 64, so all were used (as pre-registered): 62, 63, 65. S picks: 7, 120, 125, 126.
- **Primary: pass. F rules: 12 of 12 soups jumped (rounds 250–2,500, one at 10,250); S rules: 2 of 16 (p = 3 × 10⁻⁶).** Rule 126, with 32 backward copiers: 0 of 4; rule 120 (no copiers): 0 of 4.
- **Caveats found on inspection (not pre-registered):** D-046's "at least one copier among 40" is a weak bar. Both S "jumps" have hardly any copier at T + 1,000 (rule 7: 1 of 40; rule 125: 0 of 40), and so does one F jump (6022, rule 65: 0 of 40, steps per pair ~100–500: a takeover by short non-copying programs). Several F jumps start with steps per pair *falling* to ~90 before replicators spread. With a stricter reading (≥ 10 copiers among 40 at T + 1,000): F 11 of 12, S 0 of 16. Same conclusion.
- **An open puzzle:** S-rule soup 6031 (h = 7) sat in a high-order, high-execution state (HOE ~4.5, ~5,000–6,600 steps per pair) for ~7,000 rounds with **no** copier by our classifier. The classifier only recognises copies aligned at byte 64 (or mirrored); in rule 7 a replicator might copy to a shifted position. So "no copier" in non-standard rules may miss real replicators. Not followed up yet.
- Figure: `docs/assets/report/e60-headstart.png`.

**Interpretation:** the link holds across the family. The only rules whose short copiers are self-sufficient are the four where pointer 2 starts at, or within two bytes of, the partner's start, and those are the only rules where soups made replicators fast (16 of 16 at h = 64; 12 of 12 at 62, 63, 65). Rules with only backward copiers (0, 125–127) or none are slow. How common short copiers are does not predict it (rule 126 has 32; 0 of 4 jumped). Evidence: a predictive correlate across 7 newly tested rules plus 3 earlier ones; the classifier's blind spot for shifted copies limits claims about S rules.

**Lesson:** a property computable from the rule alone in seconds (does a short self-sufficient copier exist?) predicted which of 128 universes produce replicators quickly. That is the kind of "which rules make it likely" answer the project is after, at small scale.

---

## J-059 · 2026-11-08 · E-59: confirmed with fresh soups: backward-copier rule 2 of 16, forward-copier rule 8 of 8

**Question (pre-registered, `docs/data/e59-preregistration.md`, commit `628ec53`):** E-58's conclusion rested on a corrected reading of a criterion that misfired. Confirmation with fresh seeds and the D-046 criterion fixed in advance (HOE ≥ 1.0 at 3 checkpoints **and** a copier under the soup's own interpreter; HOE-only crossings keep running).

**Ran:** E-59, `scripts/bff_orient_confirm.py --workers 4`, 39 min. 16 soups of 2^14 with head1 = 127 (seeds 5900–5915), 8 with head1 = 64 (5920–5927), up to 16,000 rounds; jumped soups to T + 1,000.

**Found:**
- **Primary: pass. head1 = 127: 2 of 16 jumped (T = 3,750, 5,000); head1 = 64: 8 of 8 (T = 250–3,750, median 1,000). One-sided Fisher p = 6 × 10⁻⁵.**
- Secondary orientation: pass (both head1 = 127 jumps 40/40 backward copiers; all 8 head1 = 64 jumps forward: 309 of 320 programs, 0 backward, 11 not copiers).
- Secondary steps per pair > 3,000 at T + 1,000: **fail in one soup**: 5904 (head1 = 127) peaked at 4,096 and was at 2,786 at T + 1,000; all 40 common programs are copiers, so it is a real jump; the 3,000 line was a guess.
- The new criterion did its job: 7 head1 = 127 soups had HOE-only crossings (14 checks in all) with no copier and kept running; 5 of them never jumped. In soup 5915 HOE hovered near 1.0 from round 4,500 and the burst (steps 363 → 5,606) came at 5,750, so its T (5,000) is early by ~750 rounds.
- **Pooled with E-57/E-58 (2^14, by 16,000 rounds): head1 = 64: 16 of 16; head1 = 127: 3 of 24; standard (E-40): 0 of 12.** Figure updated.

**Interpretation:** confirmed. Two rules with about as many short copiers (133 vs 127) differ by more than 10× in how often replicators arise, and the difference follows the direction of copying: forward copiers are replicators by themselves, backward ones need a mirror partner. Strongest claim we can make: in BFF-like rules, whether the simplest copiers are self-sufficient sets the waiting time for replicators. Still one soup size and three rules.

**Lesson:** pre-registering the fixed criterion and repeating with fresh seeds turned a "rescued" result into a clean one.

---

## J-058 · 2026-11-08 · E-58: a matched control rule with backward copiers is slow again, so orientation, not perturbation, sets the speed (as registered: fail)

**Question (pre-registered, `docs/data/e58-preregistration.md`, commit `cf061d4`):** E-56/E-57's speed-up could come from the mirror requirement (M: backward copiers need a mirror partner) or from changing the rule at all (P). Control rule: head1 starts at byte **127**. Pilot before registering (k = 5 only): 6 shortest copiers, all backward, as many as the fast head1 = 64 rule. (M) predicts slow, (P) gives no reason for slow.

**Ran:** E-58, `scripts/bff_h127.py`: census (12 s) and 8 soups of 2^14 (seeds 5800–5807, 3 workers, ~25 min), settings as E-57. Follow-up, **not pre-registered**: the 4 soups stopped early on an HOE-only crossing were replayed deterministically from scratch to 16,000 rounds with the HOE stop disabled (`--part rerun`, ~15 min).

**Found:**
- **Census (primary B): pass.** 127 copiers of 5–6 instructions, **all backward**, shortest 5 instructions; **0 of 127 self-sufficient** (standard 0 of 52; head1 = 64: 97 of 133). So this rule has about as many short copiers as the fast rule, but none replicates alone.
- **Soups (primary A), as registered: fail.** 5 of 8 met the HOE criterion (≥ 1.0 at 3 checkpoints), p = 0.10 vs E-57's 8 of 8; secondary "fail" (4 of the 5 had no copier).
- **But 4 of those 5 were not jumps.** Under this rule the background HOE sits near 0.9 (standard: 0.3–0.5), and it drifted over 1.0. Those soups had **no copier** among their 40 most common programs and steps per pair stayed ≤ 543 (every real jump so far: 6,000–8,000). Replayed to 16,000 rounds: still **no copier**, steps ≤ 543.
- **One real jump:** soup 5806 at round **11,500** (HOE 0.58 → 4.41 in one checkpoint, steps 518 → 6,577), **40 of 40 common programs backward copiers**.
- **Reading with D-045 in full** (a jump needs a replicator; written before E-58, but the pre-registration only named the HOE part): **1 of 8 jumped by 16,000 rounds, vs 8 of 8 at head1 = 64: p = 0.0007**; with E-40's standard 0 of 12. New D-046 makes this the rule for non-standard rules.
- Figure updated: `docs/assets/report/e57-counterfactual-jumps.png` (five arms; three census bars).

**Interpretation:** a rule with as many short copiers as the fast rule, but backward ones, is slow like the standard rule, and the one replicator it made copies backwards. This supports (M), orientation and the mirror requirement, over (P), any change to the rule. The pre-registered test failed on a criterion that turned out not to measure jumps in this rule; the conclusion rests on the corrected reading and should be confirmed with more soups.

**Lesson:** a threshold calibrated in one rule (HOE ≥ 1.0) does not transfer to another; confirm a "jump" with the thing it is supposed to mean (copiers, a burst of execution).

---

## J-057 · 2026-11-08 · E-57: the counterfactual speed-up holds at 2^14 (8 of 8 vs 0 of 12); backward copiers are never replicators on their own

**Question (pre-registered, `docs/data/e57-preregistration.md`, commit `0946633`):** (A) is E-56's fast jump under the counterfactual rule real, at another soup size? (B) a mechanism: a forward copier's copy is itself, so any forward copier replicates; a backward copier's copy is its mirror, in which the copy loop is reversed and no longer a loop, so a backward copier only replicates if it also carries a copier facing the other way (two kernels).

**Ran:** E-57, `scripts/bff_mirror.py`. (A) `--part soups --workers 3`, 8 counterfactual soups of 2^14 (seeds 5700–5707), up to 16,000 rounds, D-045 criterion, to T + 1,000, ~16 min in all. Before the run: the counterfactual interpreter with head1 at 0 reproduces the standard soup bit for bit (4096 programs, 300 rounds). (B) `--part census`, 29 s: the 5–6-instruction copier kernels of E-55 rebuilt with fresh filler; a copier is *self-sufficient* if in ≥ 3 of 4 runs the copy it leaves is itself a copier under the same rule. Added `run_tape` to `scripts/bff_kernels.c` (exposes the existing `run`; nothing else changed).

**Found:**
- **Primary A: pass. 8 of 8 counterfactual soups jumped, at rounds 250–1,750 (median 500); standard rule at this size (E-40): 0 of 12 by 16,000. One-sided Fisher p = 8 × 10⁻⁶.** Secondary: forward copiers in every jumped soup (311 of the 320 most common programs forward, 0 reverse, 9 not copiers).
- **Primary B: fail as pre-registered.** Standard: **0 of 52** short copiers self-sufficient (prediction ≤ 5%: met). Counterfactual: **97 of 133 (73%)**, below the pre-registered 90%. Looked at after the result: the 36 failures are all kernels that move a head before their first write (`[>}.]`, `[}>.]` and their 6-instruction variants), so they copy everything except their own first byte `[`; the copy lacks the loop's start. They are copiers but not replicators.
- **Mirror programs (descriptive):** a program with one standard kernel at the start and one reversed at the end is self-sufficient in **2763 of 3025** combinations. The shortest standard-rule replicator found here has **10** instructions; under the counterfactual, **5**.
- Controls: hand-written replicator and all 9 E-42 emergent replicators self-sufficient; 0 of 1000 random programs; the constant writer `[{.]` not.
- Copier counts with fresh filler: 52 standard (E-55: 55), 133 counterfactual (E-55: 139): a few kernels depend on their filler.
- Figure: `docs/assets/report/e57-counterfactual-jumps.png`.

**Interpretation:** under the counterfactual rule, replicators appear one to two orders of magnitude sooner, at two soup sizes. The mechanism is supported, though the pre-registered threshold failed: no backward copier replicates by itself, so under the standard rule the smallest replicator needs two kernels (10 instructions), against 5 under the counterfactual. Five extra specific instructions are far less likely to be assembled by chance, which fits the size of the speed-up; we have not measured that link directly. Caveat from E-56's pre-registration still applies: the counterfactual changes everything a program can do, so other differences may contribute. The standard comparison is from earlier sessions (different seeds, same code path).

**Lesson:** "how easily does life arise" can hinge on one arbitrary detail of the rule: here, where one pointer starts decides whether the simplest replicator needs 5 instructions or 10, and changes the waiting time by over 10×.

---

## J-056 · 2026-11-08 · E-56: under the counterfactual rule, soups evolve forward copiers, and jump within 1,000 rounds

**Question (pre-registered, `docs/data/e56-preregistration.md`, commit `ee34b8c`):** E-55 showed that moving head1's start from byte 0 to byte 64 turns every short copier from backward to forward. Does that hold for what a soup actually evolves?

**Ran:** E-56, `scripts/bff_counterfactual.py --workers 4`, ~50 min per soup. 4 soups of 2^16 programs (seeds 5600–5603) under the counterfactual interpreter (`epoch_h` in `scripts/bff_kernels.c`), up to 24,000 rounds, D-045 jump criterion, then to T + 2,000; the 40 most common distinct programs classified with E-55's copier rule under the counterfactual interpreter. Check made afterwards (J-057 run): the same interpreter with head1 at 0 reproduces the standard soup bit for bit (4096 programs, 300 rounds), so the code path is the soup's.

**Found:**
- **Primary: pass. In all 4 soups, all 40 of the 40 most common distinct programs are forward copiers (160/160, 0 reverse).**
- **Secondary (descriptive): all 4 soups jumped, at rounds 250, 250, 250 and 1,000.** Standard 2^16 soups: 5 of 10 in E-50 by 24,000 rounds (first at 11,750); E-54's 12 new soups: 4 jumped (750 to 22,250). After the jump the counterfactual soups run ~7,000 steps per pair (standard post-jump soups: ~4,500–8,000).
- **Comparison arm (standard rule; E-54's 7 jumped soups at T + 2,000, `scripts/e56_comparison.py`, run later the same evening): 247 reverse copiers, 0 forward**, 33 not copiers (32 of them in soup 5401). As E-55 predicted.

**Interpretation:** what the soups evolve follows the rule's simplest copiers: change where one head starts and the replicators that take over copy forwards. The jump is also far faster, more than an order of magnitude at this size, a much larger change than the 2.5× more copiers among short kernels would suggest. As pre-registered, a different jump rate cannot be attributed to orientation alone (the change affects everything a program can do). E-57 tests whether the speed-up holds at 2^14 and one mechanism: a forward copier's copy is itself, a backward copier's copy is its mirror, which usually cannot copy.

**Lesson:** a one-detail counterfactual of the rule changed not only the form of the replicators but how quickly they appear; rates measured in one rule say little about "how easy is life" in general.

---

## J-055 · 2026-11-08 · E-55: replicators copy backwards because the heads wrap around the tape

**Question (pre-registered, `docs/data/e55-preregistration.md`):** all 9 replicators that emerged in our soups copy themselves backwards (J-046). Why? Hypothesis written before the census: both heads start at byte 0, so one `{` (or `<`) puts a head at byte 127, the partner's last byte, and a 5-instruction loop such as `[{.>]` then copies the program into its partner in reverse. A forward copy needs a head 64 cells ahead, which takes 64 moves or a counting loop (the hand-written replicator spends 27 bytes on it). So backward copiers are far easier to stumble on.

**Ran:** E-55, `scripts/bff_kernels.py` (its own copy of the interpreter in `scripts/bff_kernels.c`, with head1's start as a parameter; the soup code is untouched), 2 workers, 21 s. Every kernel of 1–6 instructions (1,111,110) at the start of a 64-byte program padded with random non-instruction filler, run first in a pair with random partners; a copier must leave its partner equal to itself (forward) or to its reverse (≥ 60 of 64 bytes) and stay intact, with 4 of 4 partners. Two physics: the standard rule and a counterfactual in which head1 starts at byte 64. The pre-registration was written before the census but committed together with the results (same session, ~20 minutes).

**Found:**
- **Primary: standard rule: 55 reverse copiers, 0 forward; counterfactual: 139 forward, 0 reverse. Prediction met in both directions.** The shortest copiers have 5 instructions in both physics. Standard: `[{.>]` (head1 wraps to 127 and writes downwards) and `[<,}]` (head0 wraps to 127 and pulls bytes into the partner); the 6-instruction ones are these with one extra instruction. Counterfactual: `[.>}]`, `[.}>]`, `[>}.]`, `[}>.]`, `[<{,]`, `[{<,]`.
- Filler that may contain zero bytes (k ≤ 5): the same kernels, same counts.
- Controls: the hand-written replicator is classified forward; all 9 E-42 emergent replicators reverse; 1000 random programs none; a constant writer `[{.]` (fills its partner with one byte value, then overwrites itself) none; a palindromic copier "both" (not counted as either).
- **Mechanism trace of the 9 emergent replicators (8 random partners each):** all their writes into the partner are made by a head moving **downwards** (17,752 consecutive downward steps, 0 upward), and in every run the writing head had wrapped below byte 0 before its first write. 7 of 9 write with head0 (`,`, the `[<,}]` kind); the 2 from soup 5006 at 32,000 write with head1 (`.`, the `[{.>]` kind). (Deviation: the pre-registration asked only whether **head1** wraps; after seeing that 7 replicators write with head0, the trace was extended to whichever head writes.)
- Figure: `docs/assets/report/e55-copy-kernels.png`.

**Interpretation:** the backward copying is explained by the rule, not by anything the soups learned: under the standard rule, every copier of up to 6 instructions is a backward copier, and moving one head's starting point is enough to flip that. The emergent replicators use exactly the two minimal backward mechanisms. This also explains why they are mirror replicators: a backward copy of a backward copier is its reverse, which must itself copy (both forms passed the heredity test, E-42). The census measures how easy the simplest copiers are to reach; it does not trace the soups' actual path to them. Held-out check pending: the orientation of E-54's verified replicators (pre-registered: all reverse).

**Lesson:** a striking regularity in what emerges can be a plain property of the rule; a counterfactual rule that changes one detail is the cheapest way to tell.

---

## J-054 · 2026-11-08 · E-50: bigger program soups jump sooner, roughly in proportion to their size; two "jumps" were brief spikes

**Question (pre-registered, `docs/data/e50-preregistration.md`, commit `9b31f52`):** does the BFF state transition (the appearance of replicators) become more likely per round in bigger soups? Hypothesis: the origin is a rare event per program interaction, so the rate ∝ N^β with β ≈ 1.

**Ran:** E-50, `scripts/bff_sizes.py`, ~3 h on 10 workers. Soups of 2^13 (12 soups, up to 48,000 rounds), 2^15 (12, up to 32,000) and 2^16 programs (10, up to 24,000); a soup that crossed HOE ≥ 1.0 was scanned with the replicator detector 1,000 rounds later (or at its horizon) and stopped. The 2^14 arm is E-40/E-41 as run (2 of 12 by 48,000).

**Found:**
- **Primary: β = 1.02 (95% CI 0.11 to 2.02), one-sided p = 0.014. Prediction met:** the rate grows with soup size, about in proportion.
- By arm (pre-registered criterion): 2^13: 2 of 12 (rounds 45,250 and 47,750); 2^14: 2 of 12; **2^15: 0 of 12** (≈ 2.8 expected under the fit; P(0) ≈ 6%); 2^16: **5 of 10** (11,750 to 21,750). Prediction "≥ 3 in the 2^15 and 2^16 arms" met (5), all in 2^16.
- **The transition criterion was fooled 3 times.** In 2^13 soup 5110 and 2^16 soups 5305 and 5309, HOE jumped to 1.2–1.6 for one checkpoint and fell back below 0.2 within 1,000 rounds. The most common programs then were almost all zero bytes: a wave of programs that write zeros, which dies out. The detector found **no replicator** in any of them. So the secondary prediction "every transitioned soup contains a replicator" **failed** as stated. It holds for the 6 real jumps (HOE stays at 2.5–4; steps per pair rise to the 8,192 limit), and no untransitioned soup had a replicator. Soup 5308 had such a spike at 11,750 and then a real jump at 12,500.
- **Post hoc, counting only jumps with a verified replicator** (spike soups censored where they were stopped): β = 0.93 (CI −0.17 to 2.15), p = 0.049. Same direction, weaker evidence.
- Baseline HOE (median of the first 4 checkpoints) is 0.49–0.51 in all three new arms, so the 1.0 threshold means the same at every size.
- Figure: `docs/assets/report/e50-soup-size.png`.

**Interpretation:** bigger soups make replicators sooner, consistent with a constant chance per program interaction (β ≈ 1). This is why the paper's soups (2^17 programs) jump in a few thousand rounds and ours (2^14) took tens of thousands. The interval is wide (9 events) and the 2^15 arm's 0 of 12 is unexplained, beyond chance. HOE ≥ 1 at a single checkpoint is **not** a reliable sign of the transition: it must hold for several checkpoints, or be confirmed by the detector (D-045).

**Lesson:** a one-checkpoint threshold on a noisy statistic invites false events. Pre-register a persistence requirement, and keep the detector scan as the ground truth.

---

## J-053 · 2026-11-08 · E-53: without relatives in the background, later code does not invade better; E-52 was most likely kinship

**Question (pre-registered, `docs/data/e53-preregistration.md`, commit `ed8418b`):** E-52's advantage of later replicators appeared only in backgrounds where they alone had close relatives. In backgrounds where **neither** group has relatives, do later replicators still invade better?

**Ran:** E-53, `scripts/bff_invasion.py --e53`, assay unchanged. The 33 early (T+2000) and late (T+12000) E-49 replicators of soups 901, 5006, 5010, each in its soup's snapshots at T+4000, T+9000 and a later time (T+20000; 5006: T+12500), 16 replicates, plus 3 resident nulls per background. Two crashes, both fixed without touching the assay: a negative time code in an RNG seed for the null jobs (the first run was lost after 104 of 126 assays; the rerun is deterministic and now cached per assay), then a lookup of T+6000 programs in the race-validity step. Fix commits `d1aa604`, `1ba29ab`.

**Found:**
- Every candidate's kin share in every background: **0** (as checked before the prereg).
- **Primary: D = −0.34, permutation p = 0.88. Later code does not invade better.** Per cell (late − early): 901: −0.09, −0.16, −0.05; 5006: −0.06, −0.06, +0.10; 5010: +0.04, −0.09, +0.01 (backgrounds T+4000, T+9000, later).
- Validity: in these kin-free backgrounds, invasion scores do not predict E-49 race outcomes at all (ρ = −0.02, 166 pairs). In E-52 (own-time backgrounds) they did slightly (0.209).
- **Prediction met:** we leaned (60%) to "E-52 was a kinship artefact".

**Interpretation:** E-52's "later code fits later soups" was most likely produced by relatives in the count, not by adaptation. Across the four measures now applied to the question (races E-48/E-49, growth rate E-51, invasion E-52/E-53), **later replicators are not reliably fitter than earlier ones.** Soup 5006 leans that way in races and growth rate, but not in kin-free invasion (+0.10 in the latest background only). The post-jump change in these soups looks mostly neutral. **Level 5 is not shown, and the evidence now weighs against a strong directional trend over 10,000 rounds.**

**Lesson:** a pre-registered follow-up that removes a suspected confound is cheap and decisive. Report the first result as suggestive until it is done.

---

## J-052 · 2026-11-08 · E-52: later replicators invade the later soup better, but kinship is confounded with time

**Question (pre-registered, `docs/data/e52-preregistration.md`, commit `ea948b1`):** growth into random code misses what decides races (J-051). Do later replicators spread better **inside the soups themselves**?

**Did:** an invasion assay (`program_fitness.invasion`): 64 copies of a candidate replace random members of 4096 programs drawn from a soup snapshot. The soup runs 16 rounds with no mutation, beside a paired control (same background, same pairings, no injection). The score is s = ln((excess family members at the end + 1)/(at the start + 1)); 0 means the candidate spreads like the residents it replaced. Calibration on hand-written copiers whose last byte is odd with a chosen share q, invaded by the trap variant (copies with probability 1 − q): q = 0.1, 0.25, 0.5 gave s = −1.3, −2.9, −4.0, neutral invaders −0.27 to +0.34 (8 replicates). Four probes: known effect, neutral null, non-copier, copyall deceptive. The known-effect probe first used q = 0.25 at the probe's small size (1024 programs, 8 replicates): effect −1.8 but p = 0.039, failing its p < 0.01 bar. It now uses q = 0.5 (effect −2.8, p = 8e-4). The 4096-program assay used in the experiment is larger.

**Ran:** E-52, `scripts/bff_invasion.py`, ~40 min on 2 workers. The 47 E-49 replicators, each in its own soup's snapshots at T+2000 and T+12000, plus 6 random residents per background (null), 16 replicates each.

**Found:**
- **Primary: D = 0.42, p = 0.045. Later code invades better (prediction "not significant" wrong).** But the whole effect is in the **late backgrounds** (Δ = +0.19, +0.22, +0.11 for 901, 5006, 5010); in the early ones Δ = −0.08, −0.01, 0.00.
- **Validity: invasion predicts race outcomes slightly better than growth rate** (ρ = 0.209 vs 0.196, 347 pairs; prediction ρ > 0.196 met, narrowly).
- Residents drawn at random score −1.2 to −3.6: most programs in a soup are poor copiers or none, and replicators of any time score near 0 or above. In soup 5006's late background every candidate does well (+0.6 to +1.0).
- **Confound found after the run:** each candidate has close relatives (≥ 90% identical) **only in the background of its own time** (1–2% of the soup; none 2,000 rounds away). An injected copy overwritten by a relative still counts as a family member, so relatives can protect a candidate's score. In the late backgrounds only late candidates have relatives, so kinship and time are the same variable there. Within those cells, score correlates with kinship in 901 (ρ = 0.54) and 5010 (0.64) but not in 5006 (0.00). Against a pure kinship artefact: early candidates do **not** score better in the early backgrounds, where only they have relatives.

**Interpretation:** suggestive, not established. The time-shift pattern (later code better in later soups, not in earlier ones) is what adaptation to a changing soup would look like, but the same pattern can come from kinship in the count. E-53 repeated the assay in backgrounds where neither group has relatives: **no advantage (J-053)**, so the E-52 effect was most likely kinship. **Level 5 not shown.**

**Lesson:** when the background is drawn from the same population as one group of candidates, a family-based count favours that group. Check kinship before choosing backgrounds; a kin-free background (a different time) is the clean design.

---

## J-051 · 2026-11-08 · E-51: a sensitive growth-rate measure still finds no general fitness trend; soup 5006 again rises

**Question (pre-registered, `docs/data/e51-preregistration.md`, commit `3ee9274`):** with a calibrated growth-rate measure (D-044, J-050) instead of races, are later verified replicators fitter than earlier ones of the same soup? And does the new measure agree with the races?

**Ran:** E-51, `scripts/bff_fitness.py`, ~15 min on 2 workers (E-50 used the other cores). The 47 E-49 replicators (soups 901, 5006, 5010; 2,000, 6,000 and 12,000 rounds after each jump) and the hand-written one, 24 growth runs each in the random-code background and 8 in the halting background.

**Found:**
- **Primary: no trend. S = Σ Spearman ρ(time, r) = 0.14, permutation p = 0.38. Prediction (not significant) met.** Per soup: 901 ρ = −0.09, **5006 ρ = +0.64**, 5010 ρ = −0.41.
- **Soup 5006 again goes up** (mean r 0.088 → 0.097 → 0.097, about +10%); permutation p = 0.005 for this soup alone. The prereg named 5006 as the soup most likely to rise but set no per-soup test, so this is a **post hoc** number. It is the fourth measure pointing the same way for this soup (E-46, E-48, E-49).
- **Validity: growth rate predicts race outcomes only weakly.** Spearman ρ between Δr and the share of races won = 0.196 (347 pairs, one-sided p = 1e-4; pairs share programs, so p is optimistic). **Prediction (ρ > 0.2 and p < 0.01) narrowly not met** on ρ. r explains ~4% of the variation in race outcomes.
- Programs differ: 49 of 240 cross-time pairs differ at p < 0.05 (20%), and 9 of 107 same-time pairs (8%, against 5% expected). So r varies between programs, and between time points more than within them, but in no consistent direction overall.
- All 47 copy perfectly in the halting background (r 0.379–0.397, the ceiling). In random code their r is 0.076–0.108; the hand-written replicator's is 0.140.
- Figures: `docs/assets/report/e51-growth-rates.png`, `docs/assets/report/d044-calibration.png`.

**Interpretation:** emergent replicators differ in how well they spread into random code, and these differences shift over time, but in two of three soups not upward. Soup 5006 is the exception, and it is consistent across four different measures. Growth into random code is only a small part of what decides a race between two replicators: races are mostly decided by what happens when replicators meet each other (who overwrites whom), which this assay does not measure. **Level 5 is still not shown.** One soup's consistent upward trend is the best candidate for adaptive change so far.

**Lesson:** a calibrated, precise measure of the *wrong component* of fitness does not settle the question. The next measure should put the candidates in the environment they actually live in: invasion from rare into a soup of replicators (resident background), with a neutral marker as control.

---

## J-050 · 2026-11-08 · A growth-rate fitness assay, calibrated on variants with known copying odds (D-044)

**Why:** the race assays (D-042, D-043) start from 8 copies each and read end counts; drift limits them to large effects (E-43, E-49). We needed a measure whose precision and accuracy are known before it is used on emergent code.

**Did:** `emergence/observatory/program_fitness.py` (D-044). r = slope of ln(copies) over the early rounds, from 16 copies among 4096 background programs, no mutation, until copies reach a quarter of the soup (at most 40 rounds); 24 replicate runs; comparisons by Mann–Whitney (one replicate whose copies are lost early skewed Welch's t in a first try). Two backgrounds:
- **random code:** as in a soup before its jump. Random partners that run first damage a replicator most of the time (the hand-written one survives only ~35% of such meetings), so r there is ~0.14, not the 0.405 a naive calculation gives.
- **halting:** each background program starts with an unmatched `]`, so it stops at once when it runs first. A plain inert background does not work: the instruction pointer runs on into the replicator's own code with the heads in the wrong place, and the replicator destroys itself (survival 6%). In the halting background a copy is never harmed, so r = ln(1 + p/2), where p is the chance of copying per meeting.
- **Known-effect ladder:** `trapped(k)` is the hand-written replicator with a loop that subtracts 2^k from its partner's last byte until it reaches zero. If the byte is not a multiple of 2^k the loop never ends and the program runs out of steps before copying. So p is known exactly (≈ 2^-k).

**Found (`docs/data/experiments/2026-11-08-d044-calibration.json`):**
- Measured vs theory, 24 runs each: p = 1: 0.390 / 0.405; ½: 0.201 / 0.224; ¼: 0.116 / 0.117; ⅛: 0.060 / 0.061; 1⁄16: 0.031 / 0.030. A slight shortfall at high r (copies start meeting each other before the cap). SE ≈ 0.001–0.003.
- **Sensitivity:** k = 3 vs k = 4 (difference 0.03) separated at p = 6e-7 with 8 runs each.
- All 9 E-42 emergent replicators copy perfectly in the halting background (r 0.386–0.392, like the hand-written one). In random code they spread at 0.079–0.095, the hand-written one at 0.147.
- Probes (benchmark section 13, 5 checks): ladder vs theory, k = 3 vs 4, non-copier r ≈ 0 (negative), copyall and noexec rules r ≈ 0 (deceptive: under copyall every program "copies" but counts only drift), 8 repeat assays of one program with ≤ 2 "different" (null). All pass. Test `test_growth_rate_assay`.

**Lesson:** a measure for evolving code can be calibrated like a lab instrument, with built-in variants of known effect. The halting background is the calibration standard; the random background is closer to the soups' real environment but still not the same.

---

## J-049 · 2026-11-08 · E-49: with verified replicators and fresh time points, later code is not reliably fitter

**Question (pre-registered, `docs/data/e49-preregistration.md`, commit `da4000f`):** E-48 with its flaws fixed: are later replicators fitter than earlier ones of the same soup? Samples were filtered by the replicator test (D-040), taken at new time points (2,000, 6,000 and 12,000 rounds after the jump), and the same-round control used random orientation.

**Ran:** E-49, `scripts/bff_time_races2.py`, ~35 min on 11 workers. 47 verified replicators (6 per time point, fewer in 3 cases: 5010 at +6000 had only 2 in 40 candidates), 240 cross-time and 107 same-round pairs, 32 races each.

**Found:**
- **Primary (program level): later replicator ahead in 24 of 44 cases (55%, p = 0.33). Prediction (≥ 60%, p < 0.01) not met.** Pair level: 129 of 240 (p = 0.14); mean share of races won by the later replicator 0.516.
- Same-round control: 49 of 107 ahead, mean share 0.503: the control is clean.
- Soup 5006 again leans later (53 of 84 pairs, p = 0.011, mean 0.548), as predicted; 5010 0.527; 901 0.482.
- By gap: 2,000 → 12,000 is the clearest (60 of 90 pairs, p = 0.001, mean 0.545), larger than 2,000 → 6,000 (0.523), as predicted; but 6,000 → 12,000 goes the other way (0.469). Pairs share programs, so pair-level p-values overstate the evidence.
- Figure: `docs/assets/report/e49-time-races.png`.

**Interpretation:** later code is at most **slightly** fitter than earlier code, and not reliably so: the confirmatory test fails. The soups change a lot (J-047) but, measured in races among random programs, most of the change looks neutral. The one consistent signal is soup 5006 (E-46, E-48, E-49 all in the same direction), plus a small advantage over the longest gap. **Adaptive, cumulative change is not shown.**

**Lesson:** fitness differences among emergent replicators are small relative to race noise. Power, not cleverness, is the bottleneck: the next test needs a more sensitive fitness measure (e.g. growth rate from a small seed in a fixed background), validated on the hand-written replicator's known variants first.

---

## J-048 · 2026-11-08 · E-48: is later code fitter than earlier code? In one soup yes, overall not shown

**Question (pre-registered, `docs/data/e48-preregistration.md`, commit `5695abf`):** the soups drift far from their founders (J-047). If the drift is adaptive, programs from later rounds should out-race programs from earlier rounds of the same soup.

**Ran:** E-48, `scripts/bff_time_races.py`, ~25 min on 11 workers. From the E-47 replays, the 6 most common distinct families at 1,000 and at 10,000 rounds after each soup's jump; every late program raced every early one (108 pairs), plus same-round pairs as the drift control (90 pairs), 32 races per pair, both orientations counted.

**Found:**
- **Primary: later program ahead in 62 of 108 pairs (57%, sign test p = 0.07). Prediction (≥ 60%, p < 0.01) not met.**
- The soups differ. **Soup 5006: later ahead in 28 of 36 pairs (p = 0.0006; 58% of races).** Soup 5010: 22 of 36 (p = 0.12). Soup 901: 12 of 36, later code *behind* (35% of races).
- Soup 901's result is driven by two of its six late programs that **lost every race against every opponent**: common programs that apparently do not copy themselves in a fresh soup. Excluding them (post hoc): 901 is 12 of 24 (neutral) and the total is 62 of 96 (p = 0.003). Our sample rule ("most common programs") did not require copying; it should have.
- Same-round pairs: the program that was more common in the soup won 52 of 81 decided pairs (p = 0.014, post hoc), and more so the bigger the gap in abundance; without the two non-copiers 44 of 73 (p = 0.10). Not robust.
- Figure: `docs/assets/report/e48-time-races.png`.

**Interpretation:** in soup 5006, code from 10,000 rounds after the jump out-races code from 1,000 rounds after: there, the drift includes **adaptive change**, consistent with E-46 (a later 5006 family beat an earlier one). Across the three soups the pre-registered test does not reach significance, partly because the sample mixed in programs that are common but cannot copy. Level 5 (open-ended evolution) is not reached.

**Lesson:** "most common" is not "replicator": a sample for fitness races should be filtered by the replicator test first (pre-registered), and the drift control should use random orientation, not abundance order.

---

## J-047 · 2026-11-08 · E-47: after the jump, no species dominates; the soup is a drifting cloud of variants

**Question (pre-registered, `docs/data/e47-preregistration.md`, commit `f47ba3b`):** is species turnover in running soups driven by selection, i.e. does each new dominant species beat the one it displaced in a race?

**Ran:** E-47, `scripts/bff_turnover.py`. Exact replays of soups 901, 5006 and 5010 to 40,000 rounds (every E-41 checkpoint reproduced bit for bit: 9750/16000, 28250/32000, 17000/32000), snapshots every 250 rounds from 1000 rounds before each transition (271 snapshots), ~55 min on 3 cores. Then the pre-registered dominant-species sequence and races.

**Found:**
- **Primary outcome not testable: 0 replacements in 3 soups** under the pre-registered rule (prediction ≥ 4: wrong). Also 0 with 2% and 1% thresholds (exploratory).
- Why: **no 90%-identity family dominates after the transition.** The most common program's family holds a median of 2.2–2.4% of the soup (max 6% in 5006, 12% in 5010, one 30% spike in 901), and consecutive snapshots 250 rounds apart have their most common program in the same family only 5–23% of the time. The soup is a large, shifting cloud of related variants, not a succession of species.
- **The most common program drifts away from the founder:** byte identity to the first dominant program (best orientation) falls from 100% to about 15–20% in soup 901 over ~20,000 rounds and to ~10% in 5006 over 12,000 rounds; in 5010 it falls to a few % within 5,000 rounds. Random programs share ~0.4%. Figure: `docs/assets/report/e47-turnover.png`.
- This corrects J-046's wording: #4 and #5/#6 were never dominant; each was one of the most common exact programs, holding ~1.6% of the soup (257 and 269 programs of 16,384).

**Interpretation:** the soups keep changing after the jump, steadily and far: within tens of thousands of rounds the code that is most common shares little with the code that started the takeover. Whether that change is adaptive or neutral drift cannot be told from this measurement: copying with errors drifts on its own. The E-46 result (a newcomer family out-races an older family of the same soup) is one data point in favour of selection; a test needs a null for drift (e.g. race programs sampled at times t and t + Δ against each other, compared with races between programs sampled at the same time).

**Lesson:** "dominant species" was the wrong picture for these soups: the pre-registration assumed a structure the data does not have. Measure the population structure (family sizes, turnover) before defining events on it.

---

· 2026-11-08 · E-46: every emergent replicator is a mirror replicator; with fair counting, one species still wins

**What we noticed after E-45:** soup 5006's earlier replicator #4 also sat beside its own reverse in the E-41 snapshot (129 copies and 128 reverse copies). We then seeded each of the 9 emergent replicators alone (4 soups each): **every one produces its exact byte-reverse in about equal numbers.** All the replicators that emerged in our soups copy themselves backwards; only the hand-written one copies forwards. So E-44 counted every emergent species by half (one form), and E-45 counted the 5006@32k species (#5/#6) by both forms but its opponents by one. Both biases could have created the reported advantages.

**Question (pre-registered, `docs/data/e46-preregistration.md`, commit `c4b0925`):** with both forms counted for every species, do the E-45 advantage and E-44's hand-written advantage survive? We predicted they would not.

**Ran:** E-46, `scripts/bff_species_contests.py`, ~15 min on 11 workers. 8 emergent species (all 28 pairs), the hand-written replicator vs each, and 24 neutral pairs (hand-written vs redrawn tail), 64 races each, seed 46.

**Found:**
- **Prediction 1 wrong: the 5006@32k species still wins 176 of 252 races against soup 901's species (69.8%, p = 10⁻¹⁰),** the same share as E-45. In winner-take-all races the factor-2 undercount rarely flips a race. It is ahead of all 7 other emergent species (56–79% of races), "favoured" against 3. **It beats #4, a family that was common earlier in its own soup and had disappeared by round 32000, in 46 of 64 races (72%, favoured).** (J-047: neither family ever held more than ~2% of the soup; "replaced" overstates it.)
- Prediction 2 wrong in part: the hand-written replicator's advantage shrinks from 77% of races (E-44, biased) to **56% (286/510, p = 0.003)**: most of E-44's advantage was the counting bias; a small one remains.
- **Neutral controls behave this time: 0 of 24 favoured, pooled 50.9%.** Over E-44 to E-46, 2 of 70 null pair runs got a favoured verdict (~3%).
- Emergent pairs favoured: 3 of 28 vs 0 of 24 nulls (Fisher p = 0.15, prediction 3 met); all 3 involve the 5006@32k species. Other species are indistinguishable from one another. Cross-epoch pairs in soups 901 and 5010: no difference.
- Figure: `docs/assets/report/e46-species-contests.png`. Snapshots of soup 5006 (E-41): at epoch 28250, 257 programs belong to #4's species and none to #5's; at 32000, 0 and 269.

**Interpretation:** E-45's conclusion survives a fair measurement: one emergent species is reproducibly fitter than the others in a common environment, and it also beats a family that was common earlier in its own soup. That is what selection driving a change would look like, in **one** soup and one pair (and J-047 shows neither family was ever dominant); we have not shown that the change *was* caused by the advantage, nor that changes accumulate. The striking structural fact is that all 9 emergent replicators are mirror replicators: in our soups, self-copying arose in the reversed form every time (3 soups).

**Lesson:** check what a "family" is in *every* competitor before comparing families. Our first correction (E-45 counted one species fairly) was itself unfair to the opponents.

---

· 2026-11-08 · E-45: the mirror replicator species beats other emergent replicators (confirmed, with a caveat about the null)

**Question (pre-registered, `docs/data/e45-preregistration.md`, after a post-hoc pattern in E-44):** does the mirror replicator species of soup 5006 (J-044) out-compete the replicators of soup 901 when both of its forms are counted?

**Ran:** E-45, `scripts/bff_mirror_contests.py`, commit `d2d04a5`, ~3 min on 11 workers. `compete_families` with species counting (`a_alt`, D-043): 8 copies of #5 seeded, family = programs ≥ 90% identical to #5 or #6; 64 replicate races per pair, fresh seed 45.

**Found:**
- **Primary: the mirror species won 173 of 249 informative races against the four soup-901 replicators (69.5%, binomial p = 4·10⁻¹⁰); "a favoured" in 3 of 4 pairs, the fourth in the same direction (66%, p = 0.015).** Prediction (≥ 0.6, ≥ 2 of 4 favoured, none reversed) met.
- Secondary: against #4 (its predecessor in soup 5006), #7 and #8 (soup 5010) it won 126 of 187 (67%, p = 10⁻⁶; one pair favoured). Against the hand-written replicator: a tie (50%).
- **Null prediction failed:** one of the 4 designed-null pairs (hand-written replicator vs a copy with a redrawn inert tail) was also "a favoured" (68%, p = 0.005). The null pairs pooled: 56.9%. Mirror vs null pooled: Fisher p = 0.002. We checked one explanation (tail bytes near 0 that random code can zero, cutting the copy short) and it does not fit: every redrawn tail has such bytes. Across E-44 and E-45, 2 of 46 null pair runs got a favoured verdict, more than the nominal ~1%.
- Figure: `docs/assets/report/e45-mirror-contests.png`.

**Interpretation:** a reproducible fitness difference between emergent replicator species from different soups: the mirror species spreads faster than the others in a common environment, by a margin found in a fresh, pre-registered test. With heredity (E-42), this gives the three ingredients of natural selection among emergent replicators **in this assay** (variation, heredity, differential reproduction). The effect is moderate (about 2 wins for every loss) and of the same size as one supposedly neutral control, so the verdict for any single pair is weak; the pooled comparison is what carries the claim. Still not level 5: nothing here shows selection *producing* cumulative change in a running soup.

**Correction (J-046):** every emergent replicator turned out to be a mirror replicator, so E-45 undercounted the *opponents* by half. E-46 repeated the test with fair counting: the advantage holds (176/252). The null failure did not recur (0 of 24).

**Lesson:** "designed neutral" controls are not automatically neutral in a soup where random code edits every tape; the false-positive rate of the contest criterion should be measured with many more null pairs before single-pair verdicts are trusted.

---

## J-044 · 2026-11-08 · E-44: unrelated emergent replicators look equally fit; a designed copier beats them all; a mirror replicator

**Question (pre-registered, `docs/data/e44-preregistration.md`):** one-byte variants looked neutral (E-43). Do replicators from *different* soups (65–100% of bytes different) differ in competition? Does the later replicator of a soup beat the earlier one?

**Built (D-043):** `program_selection.compete_families`: two replicators from different families, 8 copies each among 1024 random programs, 96 epochs; families by ≥ 90% byte identity; 16 replicate races; favoured if ≥ 8 informative races, two-sided sign test p < 0.01 and mean |log-ratio| > ln 2. Controls (benchmark section 12): hand-written replicator vs the same copier with a redrawn inert tail → no difference; vs a redrawn-tail copy with a broken loop → a favoured; copyall → undecided.

**Ran:** E-44, `scripts/bff_contests.py`, commit `9b6209a`, ~4 min on 11 workers. All 36 pairs of the 9 emergent replicators, the hand-written one vs each, 12 designed-null and 9 emergent-null pairs; everything twice (batches A and B, independent soups).

**Found:**
- **Primary: 0 of 36 emergent pairs favoured** (batch A; batch B: 1 of 36); nulls 1 of 21; Fisher p = 1. **Prediction (≥ 30%) wrong.** Batch A and B effect sizes barely agree across pairs (Spearman 0.22, p = 0.19). Cross-epoch pairs: 0 of 7 decided either way.
- **The hand-written replicator beats the emergent ones:** it won 222 of 287 informative races (p = 3·10⁻²¹; "a favoured" in 1 + 4 of 9 pairs). **Corrected in J-046:** most of this was a counting bias (each emergent species was counted by one of its two forms); with fair counting, 56% (E-46).
- **A mirror replicator.** Replicators #5 and #6 (soup 5006, epoch 32000) are **exact byte-reversals of each other**. Run first in a pair, #5 stays intact and writes its own reverse into its partner (32 of 32 random partners); the reverse does the same. Seeded alone, #5 gives equal numbers of #5 and #6 (8 of 8 soups). The species alternates between two forms each generation, like a strand and its complement. (In E-42, each form passed the heredity test; by the mechanism, a mutation at byte p of #5 should reappear at byte 63 − p of #6 and back at p a generation later; not measured separately.) Figure: `docs/assets/report/e44-mirror-replicator.png`. Two soup-901 replicators (#0, #1) are 66% reverse-identical, so reverse copying may be common. **(J-046: in fact all 9 emergent replicators are mirror replicators.)**
- Post hoc, from the contest matrix (`docs/assets/report/e44-bff-contests.png`): the mirror pair, although each form counted only half of its species, ended more common than the four soup-901 replicators in 162 of 250 races (p = 3·10⁻⁶). Tested in E-45.

**Interpretation:** at the resolution of 16-race contests, unrelated emergent replicators are about equally fit, while a hand-written copier is clearly fitter: fitness differences exist in this physics but the soups' replicators sit at similar levels. Selection among them is not shown by E-44's pre-registered test.

**Lesson:** measure what a family *is* before counting it: a species with two forms is undercounted by half when only one form is the reference. `compete_families` now accepts alternative forms.

---

## J-043 · 2026-11-08 · E-43: one-byte variants of emergent replicators look neutral in competition (selection not shown)

**Question (pre-registered, `docs/data/e43-preregistration.md`):** natural selection needs variation (yes), heredity (yes, E-42) and differences in how well variants spread. Do the one-byte variants of E-42 differ from their parents in head-to-head competition?

**Built (D-042):** `observatory/program_selection.py`: parent and variant, 8 copies each among 1024 random programs, 96 epochs, 8 replicate soups; "favoured" only if every informative replicate has the same sign and the mean log-ratio exceeds ln 2. Controls (benchmark section 12, passing): neutral tail variant of the hand-written replicator → no difference; variant that cannot copy → parent favoured; copyall → undecided.

**Ran:** E-43, `scripts/bff_selection.py`, commit `841accf`, a few minutes on 11 workers. All 141 viable E-42 variants against their parents; 24 neutral pairs of the hand-written replicator as a null.

**Found:**
- **2 of 141 emergent pairs "parent favoured"** (1.4%), 0 "variant favoured", 139 "no difference". Neutral null: 0 of 24. Fisher one-sided p = 0.73. **Prediction (5–30% parent favoured) wrong; the primary test is not significant.**
- The two deleterious variants: byte 23 of a soup-901 replicator, and byte 0 of a soup-5006 replicator (the one position whose mutation was only partly inherited in E-42).
- Contests are winner-take-all: in most replicates one line ends near 0 and the other in the hundreds, in either direction. The assay can see a variant that loses consistently and by a lot; it cannot see small differences.

**Interpretation:** one-byte changes that leave a replicator able to copy itself are, as far as this assay can tell, mostly neutral. Differential reproduction among variants, the third condition for natural selection, is **not shown**. This does not mean there is no selection: in E-41's soups, families do change over time and a few programs dominate. But a measurement that sees it needs more power (more replicates, longer or larger contests, or variants that differ by more than one byte, such as variants taken from different soups).

**Lesson:** heredity was easy to show, fitness differences are not: neutrality is the default for small changes in a copier whose speed is set by its copy loop.

---

## J-042 · 2026-11-08 · E-42: mutations in emergent program replicators are inherited (heritable variation, level 4)

**Question (pre-registered, `docs/data/e42-preregistration.md`):** the self-replicating programs that emerged in E-41 come in variants. Is that variation heritable: when a replicator carries a mutation, do its copies carry it too, or do they revert to a fixed form (like Lenia's dividing spots, J-037) or lose it?

**Built (D-041):** `observatory/program_heredity.py`. Each single-byte mutant of a replicator is seeded alone (8 copies) in a fresh soup of 1024 random programs and run 96 epochs without background mutation; among the family (≥ 90% identical to the parent), f_mut = share carrying the mutant byte; f_base = the same share when the unmutated parent is seeded. Controls (benchmark section 12, passing): hand-written replicator → heredity (12/12 viable mutants inherited); the same under `noexec` and `copyall` → no variation; a random program → no variation.

**Ran:** E-42, `scripts/bff_heredity.py`, commit `7aa4749`, a few minutes on 9 workers. The 9 distinct programs judged "replicator" in E-41 (soups 901, 5006, 5010), 24 mutants each.

**Found:**
- **"heredity" for 9 of 9** (prediction: at least 7). Sign tests p ≤ 1.2·10⁻⁴.
- Viable mutants: 13–20 of 24 (54–83%; predicted 30–70%: mutations break copying less often than expected). Of 141 viable mutants, **140 were carried by ≥ 60% of the family**, and 131 by 100%. The one exception: a mutation at byte 0 of a soup-5006 replicator, carried by 26% of copies (the first byte is apparently not always copied).
- **f_base = 0 in every case**: the mutant byte never appears at that position without the mutation.
- Families grew to 64–512 copies depending on the mutant: mutants differ in how fast they spread (not yet analysed as fitness).
- Figure: `docs/assets/report/e42-bff-heredity.png` (which byte positions tolerate mutation, per replicator).

**Evidence level 4 (heritable variation)** for program replicators that arose spontaneously from random code: variants exist, they reproduce, and their differences are passed on to descendants in a fresh soup. Not level 5: we have not shown selection among variants, cumulative change, or open-endedness.

**Caveats:** single-byte mutations only; 96 epochs is a few generations; the replicators were taken from soups selected for having transitioned; mutants were tested alone, not in competition. The hand-written positive is a linear copier; emergent replicators behaved the same under the test, which suggests they also copy whole tapes.

**Lesson:** heritable variation was not the hard part in program soups: once self-copiers exist, they copy mutations along with everything else. The hard part was getting self-copiers at all (3 of 16 soups).

---

## J-041 · 2026-11-08 · E-41: self-replicating programs emerge from random code; every transition is confirmed by the detector

**Question (pre-registered after E-40, `docs/data/e41-preregistration.md`):** E-40 never reached a transition, so its detector question stayed open. (A) Does the pilot soup that transitioned (seed 901) replay exactly, and does the detector find replicators in it? (B) Do E-40's 12 soups transition if run 3× longer, and is every transition confirmed by the detector, with none outside?

**Ran:** E-41, `scripts/bff_soups.py --e41`, commit `1c335d4`, 32 min (A) and 20–40 min per soup (B) on 11 workers. (A) seed 901 from scratch, 16000 epochs. (B) E-40's 12 final snapshots continued for 32000 epochs (48000 in all) with fresh random streams (seeds 5000–5011). Detector (unchanged, D-040) on the 4 most common programs 1000 epochs after a transition and at the end.

**Found:**
- **(A) Exact replay:** the HOE series equals the pilot log at every checkpoint; transition at epoch 8750. Detector at 9750: **2 replicators + 2 "one generation"**; at 16000: **2 replicators**, 1 one generation, 1 no replication. Random programs never multiplied (0 of 3 per candidate). The common programs are variants of one family sharing a core (`[[]},.<;45=%` appears in five of the six most common at epoch 9750). Prediction met.
- **(B) 2 of 12 soups transitioned** (seed 5010 at total epoch 32000, seed 5006 at 43250; 95% interval 2%–48% per soup within 48000 epochs). Prediction (2–6) met, at its low end. Both contain verified replicators at both scans (5006 at the end: 97 copies each of two replicator programs, 8 → 512 copies in the growth test and 512 again in generation 2).
- **Selection-aware null:** 0 replicators in the 22 end scans of soups that did not transition (E-40: 12, E-41: 10). Every soup above the HOE threshold contains a replicator; none below does.
- Pooled with E-40 and the pilots: **3 transitions in 16 soups of 16384 programs**, all of them at epoch ≥ 8750; none in the first 16000 epochs of the 12 pre-registered soups.
- Many top programs get "one generation": their copies multiply once, but the chosen copy does not. Likely partial or damaged copies (BFF replicators are known to copy imperfectly and to be parasitized); not investigated.

**Evidence level 3**, now in a second universe and in a stronger form than Lenia's dividing spots: replicators arise **from random code with no fitness function**, are confirmed by intervention (two generations among random programs), and come as **several distinct variants**. Heredity (level 4) is now testable here: do mutant replicators pass on their mutations? That needs a measurement with its own controls; none has been run.

**Lesson:** the transition is a rare event per soup and per epoch at this size; whether it happened at all in a given run is not a property of the rule. Rates need many soups and long runs; the detector, not the entropy curve, decides what was found.

---

## J-040 · 2026-11-08 · Program soups (BFF): a replicator detector, and no transition in 12 soups (E-40)

**Question (Track D route 5; pre-registered, `docs/data/e40-preregistration.md`):** Agüera y Arcas et al. (2024) report that soups of random 64-byte programs in a minimal language (BFF), paired at random and run on a shared tape, undergo a "state transition" in which self-replicating programs appear and take over, with no fitness function. Lenia has given us movers but, until E-32, no reproducers. Does self-replication emerge from random code in our implementation, and does a detector built to our standards confirm it?

**Built (interactive session, commit `4d79737`; D-040):** `emergence/programs/bff.py` (soup, C interpreter via ctypes, a pure-Python reference that the C code must equal on 300 random tapes; modes `noexec` and `copyall` as controls) and `observatory/replicators.py` (growth test of 8 copies among 1024 random programs, two generations, random-program null). Probes (benchmark section 12), all passing: a hand-written 64-byte self-replicator → replicator (8 → 70 copies, generation 2: 838); random program and an all-zeros program → no replication; the replicator under `copyall` and `noexec` → no replication; scans of the most common programs of a noexec soup and an early BFF soup → 0 replicators (selection-aware null).

**Pilot (interactive session, not in the sample):** 4 soups, 16000 epochs. Seed 901 (16384 programs) jumped at epoch ~8750 from a high-order entropy (HOE) of 0.3 to 2.2–3.5 and stayed there; seeds 900, 902, 903 did not.

**Ran:** E-40, `scripts/bff_soups.py`, commit `4d2761e`, 53 min per soup on 11 workers. 12 BFF soups of 16384 programs (seeds 4000–4011), 16000 epochs; controls 4000 epochs: 2 `noexec`, 2 `copyall`. Detector on each soup's 4 most common programs at the end (and 1000 epochs after any transition).

**Found:**
- **0 of 12 BFF soups transitioned** (max HOE 0.54–0.64, all in the first 2000 epochs; final 0.29–0.38). **My prediction (2 to 6) was wrong**, and the pilot's 1 in 4 was the lucky draw. With the pilot: 1 of 16 soups (95% interval 0.2%–30%).
- Detector at the end: every candidate "no replication" (the most common program occurs once or twice: the soup is still diverse).
- Something does change before any transition: the share of instruction bytes rises from 3.9% (random) to ~15% in every BFF soup and stays there, while `noexec` stays at 3.9%. Programs that contain instructions survive interactions better than others. This is selection on the bytes, but not replication.
- Controls: `noexec` HOE 0 (nothing changes); `copyall` HOE 7.0 within 250 epochs (copying alone makes the soup repetitive) yet its common programs are "no replication" (one "one generation" verdict). **HOE alone would have called `copyall` a transition**; the detector does not.

**Interpretation:** not reached; the question stays open. Our soups are 8× smaller than the paper's (2^14 vs 2^17 programs); if a replicator has to arise by chance in some pair, its chance per epoch scales with the number of pairs, so a smaller soup should transition later. E-41 (pre-registered, running) replays the pilot that transitioned, which is deterministic, to test the detector on a real transition, and continues the 12 soups to 48000 epochs.

**Lesson:** one pilot in four is not a rate. Pre-registered predictions built on a single success should be wide, or the pilot should be bigger.

---

## J-037 · 2026-11-08 · E-32: one random multi-channel Lenia rule makes dividing spots (first Lenia reproducer; prediction wrong)

**Question (pre-registered, `docs/data/e32-preregistration.md`; Track D):** E-29 found no reproducer among 3000 random single-channel Lenia rules. Chan (2020) reports self-replication once Lenia has several channels and kernels. Repeating E-29 unchanged on random `MultiLenia` rules (D-031), does a lone lump ever become a reproducer?

**Ran:** E-32, `scripts/mlenia_lump_scan.py`, commit `7aedcaf`, 4.4 h on 8 workers. 1000 rules (seed 32; 521 with 2 channels, 479 with 3), 2 lumps each (radius 13, 26), 128×128 vacuum, 300 settling steps, birth detector (D-028 + D-030) on the 2 most common object types. Gray-Scott pipeline positive 4/4.

**Found:**
- **1 reproducer rule in 1000** (#970, 2 channels, 4 kernels): both tested object types passed two generations, with 0 copies from the empty and the perturbed vacuum. **My prediction (0) was wrong.**
- Rule outcomes: 450 decided (at least one object fully tested; 449 without a reproducer), 143 explosive only, 27 filled, 380 extinct. 5 further "one generation" verdicts (E-29: none).
- Compared with single-channel Lenia (E-29, 0 of 1453 decided rules): 1 of 450, 95% interval 0.006%–1.2%; Fisher one-sided p = 0.24. **The difference in rate is not significant**; what is new is that a reproducer exists at all in our Lenia family.

**Inspected (as pre-registered):**
- **By eye** (`docs/assets/report/e32-divider-strip.png`, `e32-divider.gif`): a small spot alone in an empty world stretches, splits in two within ~150 steps, and the halves split again; after ~2000 steps about 100 spots tile the 160×160 world and the total mass saturates (52 → 4200). It looks like Gray-Scott's "mitosis" spots, not like E-30's condensation: matter grows only next to existing spots, in a front, never from the empty background.
- **Re-run from 3 new lumps** (fresh random streams): a reproducer in **3 of 3**, 0 background copies each time.
- **The scrambled-patch check reports `attractor = True`**: scrambled lumps of the same values also become dividing spots. As for Gray-Scott, the spot is the rule's attractor, so offspring cannot inherit anything from a particular parent. Heredity is impossible here by construction, and the heredity test was not run.
- **What the second channel does (post hoc, scratch test):** channel 1 dies out (mass 0 after settling), so everything happens in channel 0. But the kernel from the empty channel 1 into channel 0 still counts in channel 0's averaged growth, as a constant negative term (growth of 0 is −1), i.e. a **uniform decay**. Removing channel 1 (the same two self-kernels of channel 0 in a one-channel rule) or keeping only either self-kernel: **no reproduction** (6/6 lumps, many static objects). The division needs two kernels *plus* that decay.

**Evidence level:** level 3 (self-replication verified by intervention, two generations, three fresh starts) for one rule, in the weakest form: a single attractor type with no possible heredity, as Gray-Scott. Not a creature with a lineage.

**Interpretation:** dividing spots, the classic reaction-diffusion reproducer, can arise in Lenia from a random rule, but rarely (~0.2% of decided rules), and they are copies of an attractor, not of a parent. For heredity, the next physics needs room for several distinct reproducing types (Track D).

**Lesson:** an "extra channel" can matter without holding any matter: in averaged-growth Lenia an empty channel's kernel is a decay term. Check what a component actually does before crediting it.

---

## J-036 · 2026-11-08 · E-31: held-out fed Flow-Lenia on stable food: no reproduction, and the new null holds

**Question (pre-registered, `docs/data/e31-preregistration.md`):** E-30's fed-world "reproducers" were the food condensing (J-035). The perturbed-vacuum null (D-030) was added after those results, and fed worlds only mean something if the food itself is stable. On new rules (seed 31), screened for stable food first, does anything reproduce?

**Ran:** E-31, `scripts/pl_heldout.py`, commit `8d30db2`, 4.8 h on 11 cores (sharing the machine with E-32). 200 rules screened at food 0.05 and at 0.08 (perturbed food alone, 160×160, 4000 steps); the first 50 stable rules at each level (47 at 0.08) run in the E-30 world (6 patches with their own kernel weights, 128×128, 1500 steps), birth detector with D-030, heredity test on any reproducer.

**Found:**
- **0 reproducers in 97 stable-food worlds** (50 at food 0.05, 47 at 0.08), 183 objects tested, every verdict "no reproduction". No "background" and no "one generation" verdict. Prediction (0) correct; one-sided 95% upper bound ≈ 6% per food level.
- **Stable food is the minority:** 72/200 rules (36%) at 0.05 (E-30: 32/100), **47/200 (24%) at 0.08**: more food, less stability, as predicted.
- Pipeline positive (GrayScottTracer, carried trait): reproducer and heredity 4/4 (r = 1.0, p = 0.0005).

**Interpretation:** the held-out test of D-030 passed: with the food screened, the detector no longer reports condensation, and its positive still passes. Fed Flow-Lenia with localized parameters, in our random rule distribution and with this start, does not reproduce (level 3 not reached). The localized-parameter route (Track D route 3) has nothing to evolve yet.

**Lesson:** a null added after the fact needs a held-out run where it cannot be tuned. This one passed it.

---

## J-035 · 2026-11-07 · E-30: "reproducers" in fed Flow-Lenia were food condensing; the birth detector gets a perturbed-vacuum null

**Question (pre-registered, `docs/data/e30-preregistration.md`; Track D route 3):** in Flow-Lenia with localized parameters (FlowLeniaPL, J-033), fed with a thin food layer and seeded with six "species", does anything reproduce? If so, is there heredity?

**Ran:** E-30, `scripts/pl_scan.py`, commit `ef87a8a`, 2.7 h on 11 cores. 100 random rules × food {0, 0.05}, paired; 6 patches with their own kernel weights; 128×128, 1500 steps; birth detector on the 2 most common object types; heredity test where a reproducer was found. Pipeline positive (Gray-Scott tracer): reproducer and heredity in 4/4.

**Found, as first scored:**
- Unfed: 0/100 worlds with a reproducer (by construction); mass drift ≤ 4e-7.
- **Fed: 17/100 worlds with a "reproducer"** (24 objects), 1 "one generation", and the heredity test said "heredity" in 1 world (r = 0.998, 14 families). **My prediction (0) was wrong on the numbers.**

**Inspected (as pre-registered) and found to be artefacts:**
- The "parents" were small (mass 2–40) next to creature-sized objects (120–600) that never passed. One of them, alone in a fed vacuum, became **99 objects spread over the whole world within 500 steps**.
- **The food layer is an unstable fixed point.** A perfectly uniform layer never changes (so the background null, an exact fed vacuum, made 0 copies), but food with noise of 1e-4 and **no parent at all** condensed into 20–110 droplets in 15 of the 17 rules; with 2% relative noise, in all 17. The droplets have the parent's mass, so the copy count rises like real division (1, 5, 9, 17, 25 … 106).
- The "heredity" verdict is meaningless here: the "offspring" are condensed food, not offspring.

**Changed (D-030, post hoc):** the birth detector also runs a **perturbed vacuum** (float states: × (1 + N(0, 0.02)) + N(0, 1e-4)); copies there → "background", a no-spontaneous-generation rule. The heredity test returns "unstable vacuum" in the same case. Every earlier control keeps its verdict (Gray-Scott's vacuum stays empty under the noise); E-30 world #43 is a new deceptive probe.

**Rescored (`scripts/e30_rescore.py`):**
- **Food stability: only 32 of the 100 rules have a stable food layer at food 0.05.**
- **All 17 hit worlds are on unstable food**; rescanned with the fixed detector: **0 reproducers** (24 background, 10 no reproduction).
- On the 32 stable-food rules (valid under both detector versions): 0 reproducers, 1 "one generation", 59 no reproduction.

**Interpretation:** no reproduction in fed Flow-Lenia with localized parameters, in 100 random rules. The real lesson is about the environment: "feeding" a mass-conserving world can make the food itself the most active thing in it. Any future fed-world experiment must first check that its food is stable (or explicitly study condensation). The fix is post hoc and needs held-out data: the next fed-world scan should use only rules whose food passes the stability check, with the new null pre-registered. Evidence level stays at 2.

**Lesson:** a null built from a perfectly symmetric state can be blind to instability. "Nothing happens in an empty world" has to hold for a slightly disturbed empty world too.

---

## J-034 · 2026-11-07 · E-29: in 3000 random Lenia rules, no lone lump becomes a reproducer

**Question (pre-registered, `docs/data/e29-preregistration.md`; Track D route 2):** E-27/E-28 tested objects in worlds already selected for movers, a small corner of rule space. Before building a "fission objective" for the search, a direct test: give every rule drawn at random the same chance to reproduce. Does any Lenia rule turn a lone lump of matter into a reproducer?

**Ran:** E-29, `scripts/lump_scan.py`, commit `6a6578a`, 72 min on 11 cores. 3000 rules from `Lenia.random` (μ 0.08–0.40, σ/μ 0.05–0.30, 1–3 rings), each with 2 smooth random lumps (radius 13 and 26) alone in a 128×128 vacuum for 300 steps (or up to the last checkpoint before the world filled). Then the unchanged birth detector (D-028) on the 2 most common object types. Pipeline positive: Gray-Scott lumps.

**Found:**
- **0 reproducers in 3000 rules** (5069 object tests), as predicted. Gray-Scott pipeline positive **10/10**. No "one generation" verdict either.
- **Coverage is lower than planned, and this matters for the bound:**

  | Rule outcome (both lumps) | Rules |
  |---|---|
  | at least one object fully tested: no reproduction | **1453** |
  | only "explosive": the test world filled before the detector could decide | 410 |
  | lumps filled the world with nothing testable | 228 |
  | both lumps died | 909 |

  The pre-registered bound (0.1% of the distribution) assumed every rule could be tested. Honestly stated: **0 of 1453 decided rules** (95% upper bound about 0.2% of decided rules); for about a fifth of rule space (638 rules, mostly μ > 0.25 with wide growth) the detector cannot decide, because any object grows into a world-filling front.
- **The undecided cases do not look like division.** Of 1481 explosive tests, 1463 had fewer than 2 copies before the world filled. In the other 18, copies held at most 26% of the matter (75% is required), except one: a huge object (mass 2087, rule #1100, μ 0.396) which, run alone and inspected by eye, spreads into a front that freezes into a labyrinth.

**Interpretation:** across the single-channel, single-kernel Lenia rule distribution we search, a lone lump either dies, settles into still objects or movers, or spreads as a front. None grows and divides like a Gray-Scott spot. Together with E-27/E-28 this makes route 2 (a fission objective for the search) unpromising in this family: there is no gradient of "almost reproducing" rules to climb (0 "one generation" verdicts). Evidence level stays at 2. Known blind spot: rules whose objects spread too fast for a 160×160 test world.

**Lesson:** pre-register the coverage too, not only the count. A bound over "all rules" is only as good as the fraction the detector can actually decide.

---

## J-033 · 2026-11-07 · A heredity test that is not fooled by place, and Flow-Lenia with parameters that travel with matter

**Question:** Track D (research.md) needs two things before any experiment on heredity: (1) a way to tell whether offspring resemble their own parent, and (2) a physics in which a creature can carry something heritable. Neither existed.

**Built (D-029):**
- **`observatory/heredity.py`, a transplant test.** Up to 16 parents (the most common mass class in a world) are each copied alone into the physics' vacuum and run 1500 steps. Their offspring are the objects within 2× of the parent's mass. Heredity = the correlation between the parent's trait, measured in its own world, and its offspring's mean trait, across at least 6 families: r ≥ 0.5 and a parent-permutation p < 0.01. The permutation keeps the selected parents (only those that reproduced) and shuffles who is whose parent, so it accounts for how candidates were chosen. Parents that all have the same trait give "no variation".
- **Why a transplant:** offspring sit next to their parent, so anything set by place (a "common environment") makes parent and offspring alike without inheritance. Biologists separate the two by cross-fostering; moving each parent to the same empty world does the same.
- **Controls, `GrayScottTracer`:** Gray-Scott dividing spots (the birth detector's positive) with a third channel, a trait that never changes the chemistry. *carried*: the trait moves with the spot's matter (positive). *redrawn*: replaced by deterministic noise every step (negative). *position*: set by the column (deceptive: in the world, each spot's nearest neighbour has a similar trait, r > 0.5).
- **`FlowLeniaPL` (physics/flow_lenia.py):** Flow-Lenia with parameter localization (Plantec et al. 2023): each cell carries its own kernel weights h_i, stored as A·h_i and moved by the same reintegration step, so parameters mix in proportion to incoming mass and are conserved exactly. Optional uniform **food** below the object threshold, so a mass-conserving creature could grow. A scatter-add reintegration (≤ 9 target cells per source) is about 3× faster; plain FlowLenia keeps the old code and stays bit-identical.

**Found (validation):**
- Heredity: carried r = 1.0 (heredity); redrawn r ≈ −0.2 (no heredity); position r ≈ −0.3 (no heredity), although in-world neighbours are alike; identical founders → no variation. Probe section 10, 5 checks.
- FlowLeniaPL equals FlowLenia when every cell has the rule's weights (max difference ~1e-6 after 300 steps, float32 rounding); matter and every weighted parameter are conserved (drift < 1e-5); mixed weights stay between the two species' values; a food-only world never changes. 3 probe checks, unit tests.

**Not shown:** that anything in Flow-Lenia reproduces (E-30 asks), and nothing about selection or evolution: the tracer trait has no effect on survival by construction. Our mixing rule has not been checked against the paper's, so FlowLeniaPL results are not directly comparable with Plantec et al.

**Lesson:** "offspring look like their parents" is the classic trap of shared environment; build the deceptive control (a trait set by place) before the measure, and the measure has to be an intervention.

---

## J-032 · 2026-11-07 · A birth detector; none of our Lenia creatures reproduces (E-27, E-28)

**Question:** the owner asked what could give reproduction and heredity. Nothing in the project could have confirmed a birth in Lenia: the replication probe matches exact discrete shapes and only tests clones we place. So: build a detector that works for both physics families, validate it, and ask whether the Lenia worlds we have contain reproducers.

**Built (D-028):**
- `observatory/births.py`: an object is copied alone into the physics' vacuum and run. Copies are objects of the same shape (discrete) or within 2× of the parent's mass (continuous). A **reproducer** must pass two generations: its copies keep multiplying and hold ≥ 75% of the matter, and one copy, alone, does it again. A vacuum world must make none. Discrete scrambled patches that copy themselves give "rule-level duplication" (Fredkin).
- `physics/gray_scott.py`: Gray-Scott reaction-diffusion (Pearson 1993), whose spots grow and divide: a known continuous reproducer, used only as a control. Its state has two channels.
- Benchmark section 9 (12 checks, 54/54 in all): positives HighLife replicator and Gray-Scott spots; negatives Life glider, Orbium glider, the replicator pattern under Life; deceptive Fredkin (rule-level), Seeds debris, Gray-Scott stripes, Gray-Scott worms that split once ("one generation"), smoothed noise, and the Lenia labyrinth below; selection-aware null on a Life soup and a settled Orbium soup.

**Ran:**
- **E-27** (pre-registered, `docs/data/e27-preregistration.md`, one amendment before results: the planned Gray-Scott soup start died out, Pearson's square seeds used instead). 218 worlds with verified movers (E-14, E-18a, E-24, E-26) and 100 mover-free worlds; for each, the 6 most common object types plus every in-world mover. 4 h of CPU on 10 cores.
- **E-28** (pre-registered, `docs/data/e28-preregistration.md`): the same on 350 held-out worlds: 150 more mover-free worlds from the same experiments, 100 from E-17/E-18b (random 3-ring rules from smooth starts, the wanderer ridge), 100 from E-19 (soups, shuffled starts). 4.4 h of CPU.

**Found:**
- **Movers do not reproduce.** 0 of 285 movers (gliders, wanderers, ring gliders) and 0 of 503 candidates in the mover worlds made even one generation of copies.
- **E-27 broke the first version of the detector.** It reported 2 "reproducers" and 23 "one generation" candidates in blob-field worlds. Looking at them (`scripts/birth_inspect.py`, as pre-registered) showed no births: a single blob placed alone **bursts into a labyrinth that fills the world** within 500–1000 steps (~80 pieces of similar mass), then the count stops. Copy mass also drifted 377 → 278 → 169 over generations because each generation was matched to its own parent, and no third generation passed. The first version only asked for "more copies late than early".
- **Fix (post hoc, then held out):** late copies must be ≥ 2× the early maximum, and generation 2 is matched to the original parent. Every earlier control keeps its verdict; the labyrinth became a deceptive control. Re-scanning E-27's 23 hit worlds: 0 reproducers.
- **E-28 confirmed the fixed detector on held-out worlds: 0 of 350 with a reproducer** (95% upper bound 0.85% per world). Gray-Scott pipeline positive: 10/10 in both E-27 and E-28. In E-28, 61 candidates from wildly growing E-17 rules filled the test world ("explosive"), and 3 blob candidates (rules μ 0.121–0.150 with two rings) passed generation 1 only narrowly (34 → 73 copies) and failed generation 2: the second generation is doing real work, and the doubling rule alone would not be enough.

**Interpretation:** in the Lenia rules we have explored, structure either travels (gliders, wanderers, ring gliders), sits still, or spreads as a front or labyrinth. Nothing grows and divides into copies of itself. Evidence level stays at 2. This fits the literature: replication in Lenia has been reported in richer variants (several channels and kernels, Chan 2020), and heritable variation needs something that carries the rule's parameters with the creature (Flow-Lenia with parameter localization, Plantec et al. 2023). Both are now planned as Track D in [Research → Next steps]({{ '/research.html#next-steps' | relative_url }}).

**Limits:** isolation runs in vacuum, so mass-conserving physics (Flow-Lenia) cannot pass by construction (a fed-world variant is planned); candidates are the most common object types, so a rare reproducer among many blobs could be missed; 9 objects in E-28 were too large to test.

**Lesson:** a detector's first real data set is its hardest control. "More copies later" is not reproduction; keep looking at what the detector counted.

---

## J-031 · 2026-11-07 · E-26: a third kind of mover, a slow straight "ring glider", confirmed from smooth starts only

**Question (pre-registered, `docs/data/e26-preregistration.md`):** the held-out check (J-028) turned up one random rule, μ 0.277, σ 0.0316, rings 1/0.5/1, that made movers from a smooth start. Is it a reliable source of movers, and does the smooth-start effect hold?

**Ran:** E-26, commit `8217924`. The rule × 40 seeds × {soup, smooth ℓ = 6}, at density 0.35 and 0.18, 128×128, 2000 steps (4 min). Every mover was verified with `scripts/verify_movers.py`: **36 of 36 survive 1000 steps alone**.

**Found:**

| Density | Smooth ℓ = 6 | Soup | Fisher p (one-sided) |
|---|---|---|---|
| 0.35 (primary) | **13/40** | 0/40 | 3.8 × 10⁻⁵ |
| 0.18 | **18/40** | 0/40 | 3.2 × 10⁻⁷ |

- **Confirmed at both densities.** Every soup world died (80/80 extinct).
- **The creature is unlike both earlier movers.** It has a ring-shaped body, mass 173–180 (glider about 70, wanderer about 115), and moves at 0.075–0.087 cells/step in a **perfectly straight line** (net/path = 1.0 over 1000 steps alone). It is about as slow as the wanderer but does not turn, and much heavier than a glider. We call it the **ring glider** (a descriptive name; similar Lenia creatures may already be known).
- **Where it lives:** μ 0.277 with σ/μ 0.114 is on the upper band of the E-18b wanderer ridge, but with different ring weights (b = 1, 0.5, 1). Its neighbourhood in rule space is not mapped yet.

**Interpretation:** three kinds of spontaneous mover are now confirmed in Lenia: Orbium-like gliders, wanderers and ring gliders. All three need correlated starts, and none comes from soups in these rules. The ring glider was found by **drawing rules at random** (1 of 120) from smooth starts, not by the search engine. That fits E-17: once starts are smooth, mover rules are not vanishingly rare among 3-ring rules. Still level 2 evidence.

**Lesson:** a held-out check run for one purpose (validating a cut-off) can turn up a finding for another. Keep looking at what the check produced, not only at the number it was run for.

---

## J-030 · 2026-11-07 · E-25: a 300-step isolation finds more slow movers at no false-positive cost; relaxing straightness does not help

**Question (pre-registered, `docs/data/e25-preregistration.md`, one amendment before results; follows J-022):** the mover detector misses about 8% of wanderers. Do a longer isolation run (`SLOW_STEPS`) or a looser in-world straightness rule (`STRAIGHTNESS`) fix that without false positives?

**Ran:** E-25, commit `d39b9b1`, 87 min on 4 cores. 3,789 stored universes were re-simulated:
- wanderer worlds: E-18a (160) and E-18b (504);
- glider worlds: E-14 (640);
- worlds with no known creature: E-19b soups (400), the E-12 random arm (1,040 soups) and the E-17 random arm (1,045 smooth starts).

Every persistent track that moved ≥ 5 cells in the last 100 frames was isolated with the old 100-step test and with the new extended test. The extended test keeps running an object that keeps its mass for up to 300 steps, checking every 25 steps. Every detection was checked against a ground truth: alone for 1000 steps, one object, mass kept, still moving at the end.

**Found:**
- **The replay is faithful.** The current detector (V0) reproduces the stored verdict in all 3,789 worlds.

  | Pool | Worlds | V0 (0.5, 100) | V1 (0.5, 300) | V2 (0.25, 300) | V3 (no straightness, 300) |
  |---|---|---|---|---|---|
  | E-18a wanderer | 160 | 96 | **99** | 99 | 99 |
  | E-18b ridge | 504 | 30 | 30 | 30 | 30 |
  | E-14 gliders | 640 | 49 | 49 | 49 | 49 |
  | E-19b soups | 400 | 1 | 1 | 1 | 1 |
  | E-12 random (soups) | 1,040 | 0 | 0 | **1 false** | **1 false** |
  | E-17 random (smooth) | 1,045 | 1 false | 1 false | 1 false | 1 false |

- **The longer isolation only adds true movers.** 6 objects pass only the 300-step test (3 new wanderer worlds); all 6 pass the 1000-step ground truth. Every isolation pass that later failed the ground truth (4 objects) had already passed the 100-step test.
- **Relaxing straightness adds nothing true and one false positive:** a crooked fragment in E-12 universe #2059 that passes isolation and splits within 50 steps of the long run.
- **The current detector has one known false positive in these pools:** E-17 universe #1236, the drifting field chunk already caught by verification in J-019. The ground truth also flags 2 isolated objects in E-18b that split or die after 575–850 steps alone, in worlds that have other, confirmed movers.

**Changed (D-027):** `SLOW_STEPS = 300` is the default; `STRAIGHTNESS` stays 0.5. Four new benchmark checks: a second slow positive (E-18a #95, found only with 300 steps); two deceptive controls (static soup blobs fail the 300-step isolation; the crooked fragment #2059 is still rejected); and a selection-aware null (4 mover-free random rules in which the observer selects in-world movers gain no self-propelled structure). All earlier results are untouched; future runs can only gain detections.

**Interpretation:** about 99 of the roughly 104 wanderer worlds are now detected (≈ 95%, up from ≈ 92%). The remaining misses are wanderers that turn in tight loops or sit still in the observation window; a looser straightness rule does not find them, and it does find junk. The in-world straightness rule earns its place.

**Lesson:** a ground truth that is more expensive than the detector (1000 steps alone vs 100) is what makes a calibration like this possible. Run it on every pool, including the ones where you expect nothing.

---

## J-029 · 2026-11-07 · E-24: Chan's patch start does make gliders, given room; my prediction was wrong

**Question (pre-registered, `docs/data/e24-preregistration.md`):** Chan (2019) says gliders emerge from random starts "given enough time". His start, 15–40 dense patches in vacuum, gave 0 gliders in 40 worlds of 128×128 over 2000 steps (E-13). Do bigger worlds and longer runs change that?

**Pilot (before pre-registration; scratch script, 48 worlds, 256×256, 400 steps):** patch starts are bistable. Each world either dies or fills with a blob field (9/24 extinct, 15/24 filled with Chan's count; 24/24 filled with 110 patches). The planned 10,000-step study was therefore replaced by a 3000-step one.

**Ran:** E-24, commit `027248d`, 94 min on 8 cores. The 8 E-13 rules × 20 seeds × {`patches` (15–40), `patches:110` (Chan's patch density on 128×128), `smooth:3` at density 0.10}, on a 256×256 torus for 3000 steps. Every mover was verified with `scripts/verify_movers.py`: **51 of 51 survive 1000 steps alone**.

**Found:**

| Start (256×256, 3000 steps) | Worlds with a verified glider | 95% CI | Other outcomes |
|---|---|---|---|
| Chan's patches (15–40) | **13/160 (8.1%)** | 4.4–13.5% | 48 extinct, 99 blob fields |
| 110 patches | 0/160 | 0–2.3% | 160 blob fields |
| smooth ℓ = 3, density 0.10 | **29/160 (18.1%)** | 12.5–25.0% | 10 extinct, 121 blob fields |

- **Chan's start works in a bigger world.** 13 glider worlds in 5 of the 8 rules, all with ordinary single gliders (mass 65–75). The same start at 128×128 gave 0/40. **My prediction (at most 1–2 per arm) was wrong.**
- **It is the room, more than the time.** With 110 patches (the same patch *density* as Chan's count on 128×128) the field always wins. In the clip on the Report (universe #183), the glider has formed by step ~50 while the other patches fade. A sparse start lets one patch become a glider before a field can form around it. World size and run length were changed together, so this is suggested, not shown.
- **Smooth starts do not lose out in bigger worlds:** 18.1% at 256×256 and 3000 steps vs 17.5% at 128×128 and 2000 steps (E-14, same density and ℓ). My second prediction (fewer in bigger worlds, because of E-15's growing fields) was also wrong for this density.
- **Smooth starts still beat Chan's patches about two to one** (descriptive; the arms are not mass-matched).

**Interpretation:** Chan's report that creatures emerge from random patch starts is reproduced, with a rate of about 8% of worlds in these rules at this patch density. One earlier statement needs a qualifier: "Chan's patches did not produce gliders" (J-014) held only for 128×128 (marked there). On the report, the claim becomes: correlated starts (smooth fields, or sparse dense patches) make gliders; fine-grained soups almost never do. Both kinds of start that work put matter in **isolated lumps with space around them**, which supports the "isolated lump" mechanism of J-021 (still not tested directly).

**Lesson:** a protocol that failed in a small world was judged too early. When reproducing a claim, match the conditions it was made under (world size included) before calling it unreproduced.

---

## J-028 · 2026-11-07 · C-02: the quasi-static cut-off has no clean gap on new rules; a random rule makes a new mover

**Question (review R-4):** the quasi-static cut-off (free activity < 0.002, D-022) was set on 60 random rules. Does it hold on rules it has never seen, and from smooth starts?

**Ran:** C-02, `scripts/lenia_static_fields.py --seed 8 --rules 120 --skip-part1` with `--init uniform` and `--init smooth:6` (96×96, seed 1, 500 steps; the script gained `--init`). Then `scripts/heldout_free_activity.py` re-ran every rule that is not quasi-static although ≥ 90% of its persistent objects are still, to see where its free activity lies. Commits `027248d`, `d39b9b1`.

**Found:**
- **No clean gap.** Of 59 non-extinct, mover-free soup rules, 43 are quasi-static and 16 rankable. **5 lie within 0.8–1.25× of the cut-off**, and the free activity runs smoothly from 0.0005 to 0.006 (figure on the [Report]({{ '/report.html' | relative_url }})). Smooth starts: 79 quasi-static, 10 rankable, 4 near the cut-off. The same rule can land on either side depending on the start (μ 0.189 and μ 0.216 do).
- **Static-looking fields leak into the ranking.** 10 of the 16 rankable soup rules have ≥ 90% still objects (smooth starts: 2 of 10). In 5 of these 12, **70–94% of the "free" changes lie within 3 cells beyond the excluded margin**: creeping blob edges that reach past the 3-cell margin, not new dynamics. In the other 7, 24–53% do, and the rest is elsewhere (short-lived small objects).
- **No false creature claims.** `complex` still needs a verified mover, so the leak only lets some static fields be ranked and bred from. It does not inflate any mover count.
- **Unplanned: a random rule makes a mover.** One of the 120 rules, μ 0.277, σ 0.0316, rings 1/0.5/1, was `complex` from the smooth start with 2 movers (mass about 178, about 0.085 cells/step, nearly straight). **Both survive 1000 steps alone** (path 83–85 cells). From soup the same world died. It lies on the upper band of the wanderer ridge (σ/μ = 0.114; E-18b), with different ring weights, and moves straight instead of turning. Followed up in E-26 (pre-registered).

**Interpretation:** the cut-off does its main job: most static fields are excluded, and no mover-free world is called complex. But it is a soft boundary, not a gap, and about one in six static-looking soup fields gets through, mostly because blob edges creep further than the margin allows. The search can still waste effort on them. A fix (for example a margin that scales with the kernel radius) would need its own controls. Left open; the cut-off is unchanged.

**Lesson:** a threshold set on one sample needs a held-out sample before anyone calls its margin safe. The "1.6× margin" of D-022 was a property of those 60 rules.

---

## J-027 · 2026-11-07 · E-23: the combination chain stops at two

**Question (pre-registered, `docs/data/e23-preregistration.md`):** can a double glider and a glider fuse into a stable triple?

**Ran:** E-23, 312 collisions (Orbium rule; 8 glider orientations × 13 lateral offsets × 3 phases) between the E-20 double glider (mass 144, moving diagonally) and a single glider, on a 224×224 torus, 1500 steps (`scripts/chain_scan.py`, commit `913faa6`, 5 min).

**Found:**

| Outcome | Collisions |
|---|---|
| World filled by a blob field | 116 (37%) |
| One single glider left | 106 (34%) |
| Nothing left | 68 (22%) |
| Two single gliders left | 22 (7%) |
| **A triple** | **0** |
| **The double glider surviving intact** | **0** |

- **The double never survives a hit.** A double-glider collision is about 15× more likely than a glider–glider collision (2.4%, E-20) to set off a world-filling field.

**Interpretation:** combination in these rules goes one step and stops. Two gliders can make a double; a double plus a glider never makes anything larger, and the double itself is fragile. That is a natural ceiling on cumulative structure here, at least for this route. It fits the overall picture: Lenia's glider-viable rules support spontaneous movers and one level of combination, but nothing that grows, reproduces or accumulates.

**Lesson:** test the second step of a promising first step before calling it a mechanism.

---

## J-026 · 2026-11-07 · E-22: when wanderers meet, two usually become one; no stable composite, no births

**Question (pre-registered, `docs/data/e22-preregistration.md`):** gliders can fuse into a double glider (E-20). What happens when two wanderers meet?

**Ran:** E-22, 200 encounters on a 160×160 torus, 3000 steps each, classified by the full observatory (`scripts/wanderer_encounters.py`, commit `76e0249`, 8.5 min).
- **Pattern:** the wanderer of E-18a universe #81.
- **Partner:** one of 8 exact symmetries, placed 20–40 cells away in a random direction, with a random phase.

**Found:**

| Outcome | Encounters |
|---|---|
| **One wanderer left** | **142 (71%)** |
| Both survive | 43 (22%) |
| Both destroyed | 10 (5%) |
| A heavier "new object" at t = 3000 (mass 146–205) | 5 (2.5%) |
| More than two movers (a birth) | **0** |

- **The new objects are transient.** Followed for 2000 more steps, the two inspected (trials 16 and 59) **relax back to a normal wanderer** (mass 104–148), moving like one.
- **Two wanderers usually become one ordinary wanderer:** absorption, with the mass regulated back. There is no lasting double wanderer.

**Interpretation:** the two movers found tonight interact differently. Gliders can fuse into a stable, larger composite (E-20). Wanderers absorb each other into a single creature of the usual size. Neither multiplies: still no level-3 evidence. The wanderer's mass regulation is a property worth knowing for any future reproduction test, because a creature that grows and splits would need the opposite tendency.

---

## J-025 · 2026-11-07 · E-21: spontaneous double gliders are rare, and an isolation test alone over-counts

**Question (pre-registered, `docs/data/e21-preregistration.md`, with one amendment before running):** how often do double gliders arise from smooth starts, and by fusion or directly?

**Ran:** E-21, the 8 E-13 rules × 40 fresh seeds, smooth ℓ = 3, density 0.10, 128×128, 2000 steps. Each world was traced every 10 steps (`scripts/double_glider_trace.py`, commit `d641b0b`, 8.5 min).

**Found:**
- **The script's raw counts:** 2 worlds with a "verified" double glider (1 direct, 1 unclear, 0 fusion), and 116 with a "verified" single glider.
- **The script's verification is flawed.** Its outcome definition, written in the pre-registration, checks only that a glider-sized object, cut out of the final state, keeps moving alone. That passes **fragments of blob fields** too.
  - Of 36 worlds it counted as glider worlds, the observatory (which needs real in-world movement) found a mover in 25. **All 11 others are blob-field worlds** with 17–49 persistent objects.
  - Of the 2 "double gliders", **one is a field fragment** (53 objects in the world). **One is genuine:** a lone double glider that formed directly from the start's lumps (t ≈ 90).
- **Corrected result: 1 genuine double glider in 320 worlds, formed directly; 0 fusions.** With E-19 (3 of 160 smooth ℓ = 3 worlds), spontaneous double gliders occur in **about 0.6% of smooth-start worlds** (4 of 640). The fusion route has been seen **once** (J-024).
- **Earlier verified counts are not affected.** E-13/E-14/E-18/E-19 used `scripts/verify_movers.py`, which first requires the observatory's in-world track (persistent ≥ 80% of the window, net travel ≥ 5 cells, straight) and only then isolates.

**Interpretation:** double gliders are real but rare in these rules. Fusion is possible (E-20: 7 of 250 perpendicular collisions), but in small worlds with few gliders it rarely happens spontaneously. Cumulative structure (lumps → gliders → double gliders) exists, but at about one event per several hundred worlds.

**Lesson:** "cut it out and it moves" is necessary, not sufficient. A mover must first be seen moving in its own world. The pre-registered outcome here was badly defined, and the analysis says so instead of reporting 116 and 2.

---

## J-024 · 2026-11-07 · Double gliders also arise spontaneously, in one case by fusion of two spontaneous gliders

**Question:** do E-20's double gliders (two fused gliders) also form without being planted?

**Ran:** no new simulation. The masses of all verified movers in E-13, E-14 and E-19 (121 in total) were re-read from their exports (`scripts/verify_movers.py`), and worlds with double-glider-mass movers were traced.

**Found:**
- **E-13 and E-14:** all 69 verified movers are single gliders (mass 64–78).
- **E-19: 3 of 52 are double gliders** (mass 139–157, speed 0.57–0.63), in three different rules (μ 0.140, 0.150, 0.160), all from smooth starts. Each was the lone survivor of its world, and each has the same two-body shape as the E-20 fusions.
- **Two ways they form:**
  - **Universe #204 (Orbium, smooth ℓ = 3):** two gliders formed by t = 40, travelled for about 500 steps, then **collided and fused at t ≈ 530**. This is a two-step, unplanted sequence: gliders arise, then combine into a larger mover.
  - **Universe #562:** the double glider formed directly from the collapsing lumps by t ≈ 30.

**Interpretation:** spontaneous structure can build on earlier spontaneous structure in these rules, at least once: lumps → gliders → a double glider. It is one event, observed after the fact (exploratory), and still level 2. For O5 (cumulative innovation) it is a concrete, testable case. Does the double glider arise *only* via glider fusion, or also directly? How often, per world and per collision? It is a better starting point for a knockout test (J-010) than chaotic turnover was.

---

## J-023 · 2026-11-07 · E-20: glider collisions never make new gliders, but can fuse two into a stable double glider

**Question (pre-registered, `docs/data/e20-preregistration.md`):** can glider collisions create new gliders ("births")? E-15 could not tell (review R-4).

**Ran:** E-20, 500 controlled collisions on a 192×192 torus, 1000 steps after placement (`scripts/collision_scan.py`, commit `3cdd71d`, 4 min on 12 cores).
- **Rules:** μ 0.15 (Orbium) and μ 0.14.
- **Geometries:** head-on and perpendicular. The partner glider is oriented exactly, by flip or transpose.
- **Variations:** lateral offset −24…24 cells and timing phase 0…20 steps.

**Found:**
- **No births.** No collision ended with ≥ 3 gliders that each survive 1000 steps alone, the pre-registered criterion.
- **What collisions do:**
  - **Head-on, μ 0.15:** 44% destroy both, 43% leave one, 13% leave both.
  - **Head-on, μ 0.14:** gliders mostly pass through or survive (78%).
  - **Perpendicular:** mostly one survivor.
- **New: fusion into a double glider.** In **7 perpendicular collisions**, at near-central offsets (−2…+2 cells), the two gliders **fuse into one stable object**: two Orbium-like bodies bonded side by side, mass 131–140 (twice a glider), moving straight at 0.61–0.63 cells/step. It stays intact for ≥ 1000 more steps. A collision **created a new kind of mover**: combination, not reproduction. Similar composite Lenia creatures may be known; new to this project.
- **Explosions.** **6 perpendicular collisions** seed a patch of blob field that grows to fill the world (mass ≈ 140 → 7,400–8,000) within about 1000 steps.
  - This is a plausible origin of E-15's world-filling fields.
  - Some fragments inside the field, cut out, survive alone (at most 2 per world), short of the birth criterion. In the world they are part of the field.

**Interpretation:** interactions between gliders are mostly destructive, but not only. A collision can build a larger composite mover, or trigger a phase change of the whole world. Neither is reproduction (level 3). Fusion is a first sign of **structures combining into new structures**, which the project's cumulative-innovation question (O5) cares about. Whether fused gliders arise spontaneously in big smooth-start worlds is untested.

**Lesson:** a controlled scan of 500 interactions answered in 4 minutes what 30 long, uncontrolled runs (E-15) could not.

---

## J-022 · 2026-11-07 · How often does the detector miss a slow, turning mover? About 8%

**Question (review R-4, point 4):** the mover detector was validated only on Orbium, a fast straight glider at about 0.6 cells/step. Does it miss slow, turning movers such as the wanderer? Does the quasi-static cut-off (D-022) hide them from the search?

**Ran:** every E-18a smooth-start world (120) *without* a detected wanderer was re-run to the end and searched for wanderer-sized objects (mass 95–145). Each one found was tested alone with a longer, 300-step isolation run.

**Found:**
- **Most of those worlds are empty:** 15 of 24 are extinct.
- **8 contain exactly one wanderer-sized object** that the detector missed. With 300 steps alone, **5 of the 8 move by themselves**; 3 do not move ≥ 5 cells net (they turn in tight loops).
- **Detection rate:** about 96 of 104 wanderer worlds, **≈ 92%**. Wanderer counts in E-17/E-18 are therefore slight **under**counts; no conclusion changes.
- **Why they were missed:**
  - 4 wanderers moved in the observation window but failed the 100-step isolation test, which is too short for a slow turner;
  - 4 failed the in-world straightness rule (net/path ≥ 0.5) while turning;
  - 1 sat still through the whole window and was labelled quasi-static, so it was hidden from the search. That is the only case of the cut-off hiding a mover.

**Changed:** a new benchmark positive, "Lenia slow positive". An emergent wanderer (E-18a universe #81) must be detected as self-propelled and labelled complex (38/38 probe checks; all other checks unchanged).

**Not changed (yet):** the detector itself. Raising the isolation run to 300 steps, or relaxing straightness for turning movers, would catch most of the misses, but each change needs its own deceptive controls (drifting blobs, decaying lumps) and re-validation. Left as an open item.

**Lesson:** a detector's positive control should span the range of what it might meet. A single fast, straight positive left the slow, turning kind untested.

---

## J-021 · 2026-11-07 · E-19: it is the spatial correlation; soups make gliders only rarely, at their die/freeze switch

**Question (pre-registered, `docs/data/e19-preregistration.md`; answers review R-4):**
- Is the smooth-start effect caused by spatial correlation, or by the different mix of cell values?
- Is there a soup density that makes gliders?

**Ran:** E-19, commit `dd1e28b`, 128×128, 2000 steps. All movers were verified with `scripts/verify_movers.py`: **52 of 52 survive 1000 steps alone**.
- **E-19a:** the 8 E-13 rules × 20 seeds × soup / smooth / `smooth_shuffled`, the last being exactly the smooth start's values randomly permuted. Densities 0.10 (ℓ = 3) and 0.35 (ℓ = 6). 960 universes.
- **E-19b:** soup only, densities 0.12–0.30 in steps of 0.02, 5 seeds per rule. 400 universes.

**Found:**
- **E-19a, both pre-registered contrasts confirmed:**

  | Density | Smooth | Shuffled | Soup | Fisher p (one-sided) | Rules higher/lower |
  |---|---|---|---|---|---|
  | 0.10 | **37/160** | **0/160** | 0/160 | 6.9 × 10⁻¹³ | 6/0 (sign p = 0.016) |
  | 0.35 | **11/160** | **0/160** | 0/160 | 4.1 × 10⁻⁴ | 5/0 (sign p = 0.031) |

  Same mass and same value distribution, but scrambled positions, give no gliders. **The effect is the spatial correlation.**
- **E-19b, the soup transition:**
  - **Below 0.18 soups die, above 0.24 they become blob fields,** with a mixed zone between. That fits R-4's point that soup outcomes are bistable.
  - **One soup world made a real glider: 1 of 40** at density 0.20, Orbium's rule, right at the switch. Across the sweep that is 1 in 400.
- **Correction:** "soups never make gliders" (J-014/J-015, report) is wrong. Soups make them **rarely**, only near the die/freeze transition. With E-14 and E-19a, it is 1 glider world in 1,120 soup worlds overall, against 13–23% for smooth starts in these rules. This fits Chan's remark that creatures emerge from random starts "given enough time".

**Interpretation:** in these 8 rules, spatially correlated matter is what makes gliders likely, at fixed mass and value mix. The "isolated lump" mechanism is consistent with this but untested.

**Lesson:** the null a reviewer asks for is worth running. It turned "it's the arrangement, probably" into a tested claim, and it caught an overstatement ("never").

---

## J-020 · 2026-11-07 · E-18: the wanderer is robust and lives on a narrow ridge; review R-4

**Question (pre-registered, `docs/data/e18-preregistration.md`):** is E-17's single wanderer rule a reliable source of movers? Where else in rule space do wanderers arise?

**Ran:**
- **E-18a:** the wanderer rule, 40 fresh seeds × soup / smooth ℓ = 3 / 6 / 10, density 0.18, 128×128, 2000 steps (2 min).
- **E-18b:** a 7 × 6 grid of 3-ring rules around it (μ 0.200–0.285, σ/μ 0.06–0.15), soup vs smooth ℓ = 6, 6 seeds (10 min). Commit `cb5fd24`.
- **Verification:** every mover re-isolated with the newly committed `scripts/verify_movers.py`: **190 of 192 survive 1000 steps alone.**

**Found:**
- **E-18a, primary test:** universes with a verified wanderer:

  | Start | Worlds |
  |---|---|
  | smooth ℓ = 6 | **36/40** |
  | smooth ℓ = 3 | 36/40 |
  | smooth ℓ = 10 | 24/40 |
  | soup | **0/40** |

  Smooth ℓ = 6 vs soup: one-sided Fisher p = 1.3 × 10⁻¹⁸. In this rule a smooth start almost guarantees a mover; Orbium's rules manage 13–18%.
- **The movers are one kind of creature:** mass 104–137, path speed about 0.085 cells/step, turning (net/path median 0.29, direction persistence 0.84 between 25-step legs).
- **E-18b, the "wanderer ridge":** wanderers arise in **7 of 42** rules, all on a narrow diagonal band.
  - σ/μ ≈ 0.092 for μ 0.215–0.255 (50–100% of worlds);
  - σ/μ ≈ 0.11 for μ 0.255–0.285 (17–100%).
  - Soups gave 0 in all 252 soup worlds.

**Review R-4 (independent agent; see [Reviews]({{ '/reviews.html#r-4' | relative_url }})):**
- **Main points:**
  - smooth starts also change the *value distribution*, not only the spatial correlation;
  - soups sit on a die/freeze transition, so their "0" is close to guaranteed;
  - the verification code was not committed;
  - the detector is not validated for slow, turning movers;
  - several claims and numbers were overstated or wrong.
- **We agree with all of them.**
  - Corrections are marked "Corrected after review R-4" in J-013 to J-019 and in the report.
  - `verify_movers.py` is committed.
  - **E-19** (pre-registered) tests the main point with a shuffled control, `smooth_shuffled`: exactly the smooth start's values, randomly permuted. It adds a fine soup density sweep across the transition.

**Caveat:** the wanderer turns, and the mover detector needs net travel ≥ 5 cells with straightness ≥ 0.5 over its window. Slower or more tightly turning variants on or near the ridge may be missed, so the ridge could be wider than shown (R-4).

**Lesson:** a reviewer who did not do the work found six real problems in an hour. Build the review in, don't bolt it on.

---

## J-019 · 2026-11-07 · E-17: searching from smooth starts finds a new mover, a slow "wanderer"

**Question (pre-registered, `docs/data/e17-preregistration.md`):** E-12 searched from soups, which never make gliders (E-14). Searching from smooth starts instead, does the engine find mover rules, does it beat random search, and does it find any outside the Orbium island?

**Ran:** E-17, identical to E-12 except `--init smooth:6`, seed 17. Engine 6 min, random 7 min (the faster census helped; E-12 took 12 + 14.5 min). Commit `9ba8254`.

**Found:**
- **Raw hits (any run with a self-propelled structure):** the engine has 5 universes in 2 rules, random search 1 universe in 1 rule. All lie **outside** the single-ring island of E-13a. (`emergence compare` reports engine 1, random 0, because it counts rules whose *mean* over all their runs is at least one self-propelled structure; the pre-registered outcome counts any run.) *(Corrected after review R-4.)*
- **Pre-registered verification (alone for 1000 steps):**
  - **μ 0.357, σ 0.0456, 2 rings (both arms): fails.** Its "mover" is a field chunk of mass 2275 that falls apart. Not a creature.
  - **μ 0.243, σ 0.0224, rings 1/0.5/0.5 (engine only): passes in all 5 objects, from 4 universes.** One is a screening run; three are follow-ups (new seeds and a 2× larger world), so it reproduces.
- **Primary outcome:** **engine 1 verified mover rule, random 0.** Tiny numbers and one seed per arm, so no significance claim (as pre-registered).
- **The new mover is a "wanderer", not a glider.**
  - **Size and shape:** compact, mass about 115 (Orbium: 70), with an internal pattern that keeps changing.
  - **Speed:** path speed 0.07–0.08 cells/step (about 8× slower than Orbium); net displacement speed only 0.017–0.055, because it turns. *(Corrected after review R-4.)*
  - **Path:** it **turns as it goes**. Direction correlation between successive 50-step stretches is 0.65–0.79. Over 2000 steps alone, its net displacement is 0.08–0.55 of its path; one copy nearly circles.
  - It moves by itself, so it passes the self-propulsion test, and it is clearly different from Orbium.
- **Other outcomes:** 0 rules `complex` on every seed in either arm. "Structured" rules: 103 (engine) vs 29 (random).

**Interpretation:** smooth starts make the search see movers it was blind to under soups, and the engine finds one random search did not. The evidence is thin, one rule and one seed per arm, but it is a reproducible, verified creature of a different kind, in a different part of rule space (3 rings, larger μ). It is still level 2 evidence. We do not know whether this creature is already documented in the Lenia literature; we claim only that it is new to this project.

**Lesson:** the start condition decides what a search can see. E-12's "zero" was a property of the soup, not of rule space.

---

## J-018 · 2026-11-07 · E-16: no movers in Flow-Lenia from any start condition

**Question (exploratory, plan in `docs/data/e16-plan.md`):** smooth starts unlocked gliders in Lenia (E-14). Do they also give Flow-Lenia its first self-propelled structure, which it needs as a positive control (J-016)?

**Ran:** E-16, 100 random Flow-Lenia rules (the paper's ranges, R = 13; `rule-panel-e16.txt`) × 4 starts (soup, smooth ℓ = 3, smooth ℓ = 6, Chan-style patches), 1 seed, density 0.35, 128×128, 1000 steps. Commit `323bea1`; 15 min on 12 cores.

**Found:**
- **No movers: 0 self-propelled structures in 400 universes.** 5 candidate movers all failed the isolation test.
- **Class mix** (summed over the 4 starts): about 40% `active`, 50% `periodic`, 9% `frozen`, a few `saturated`.
- **The `periodic` share is probably inflated.** Flow-Lenia's frame measures use an 8-bit view, so changes below about 0.016 in A count as none (J-016). The structure census, which decides "self-propelled", uses the true float state and is not affected.
- **The start condition made no visible difference:** unsettled fractions 0.19–0.23 for soup and smooth starts, 0.10 for patches.

**Interpretation:** Plantec et al. report that moving patterns are "quite common" in random Flow-Lenia, but give no counts. We cannot reproduce that, from their own patch start or from any other. Three explanations remain open:
1. Our implementation differs in details the paper does not specify (Sobel normalisation, displacement clipping, θ_A).
2. Their "dynamic" patterns are mostly wobbling or rotating in place, which our detector correctly does not count as self-propelled.
3. Single-channel movers are genuinely rare. The paper itself needed long optimisation for directed motion with one channel.

Flow-Lenia still has no positive control, so no Flow-Lenia experiment is run beyond this search.

**Also fixed:** the conditions summary divided float (physical) states by 255 when reporting the initial mass per cell (it showed 0.001 instead of 0.175).

**Lesson:** a claim that something is "common", with no count, is a hypothesis to test, not a baseline to build on.

---

## J-017 · 2026-11-07 · E-15: in big worlds the blob field usually wins, and gliders are never born

**Question (descriptive):** E-13/E-14 gliders mostly destroy each other in 128×128 worlds. In 9× larger worlds, how do glider populations develop? Do collisions ever create new gliders?

**Ran:** E-15, 3 glider-viable rules (μ 0.14, 0.15, 0.16) × 10 seeds, smooth ℓ = 3 at density 0.10, 384×384, 5000 steps, with a census every 10 steps (`scripts/glider_population.py`, commit `ca4c7b1`). It took 1 h 40 min; the object census was the bottleneck and is now 10× faster (`323bea1`).

**Found:**
- **A race between gliders and a growing blob field.** In **23 of 30** worlds a patch of static-blob field survived the early collapse and **spread over the whole world**: Lenia does not conserve mass, and total mass grew from about 7,400 to about 30,000–35,000. It swallowed any gliders.
  - **6 of 30** ended with only gliders: 1–2 gliders of mass 71–75 in an empty world.
  - **1** died out.
  - The field always won for μ 0.14 (10/10), for μ 0.15 in 8/10, and for μ 0.16 in 5/10.
- **Larger worlds favour the field.** In 128×128 worlds, glider runs end as lone survivors (J-015). In 384×384 worlds, a field nucleus usually survives somewhere, so glider-only worlds become rarer. The rate of glider worlds is not a fixed property of a rule; it depends on world size.
- **No births seen, but weak evidence.** In the 6 glider-only worlds, total mass after t = 200 falls overall in steps of about one glider (≈ 70), with several small rises of 5–24 during collisions (largest +24 at t = 1610). The images show collisions destroying or merging gliders. Because Lenia does not conserve mass, a birth in a lossy collision need not show as a +70 step. With only 6 such worlds, this is absence of evidence, not evidence of absence. A validated per-object census or seeded collision scans are needed. *(Corrected after review R-4.)*
- **A detector warning (self-inflicted):** the quick glider count in the script (glider-sized mass, moving 3–12 cells per 10 steps, no isolation test) reported hundreds of "gains". Most were moving edges inside blob fields; the rest were count flicker during collisions. The script's glider counts are therefore **not** used for any claim. The mass traces and the images are.

**Interpretation:** in Lenia's glider-viable rules, a glider is a fragile intermediate state. It needs the world to collapse enough to leave isolated lumps, but not so much that nothing survives, and no blob field anywhere. Glider–glider interactions are destructive. This is evidence level 2 without any sign of level 3 (reproduction) or of a growing population.

**Changed:** D-025 (start conditions must be reported and justified for continuous physics). The E-15 figures are in the report.

**Lesson:** a quick, unvalidated counter is a hypothesis generator, not a measurement. Its "births" were artefacts that a look at the frames exposed in a minute.

---

## J-016 · 2026-11-07 · v0.7: Flow-Lenia physics with float32 states (implementation and validation only, no experiments)

**Question / why:** add a mass-conserving continuous family, Flow-Lenia (Plantec et al. 2022/2023, arXiv 2212.07906): matter is moved along a flow instead of being created and destroyed. This is a second Lenia-like family next to the E-12/E-13 Lenia work (J-013, J-014).

**Built:**
- **Physics** (`physics/flow_lenia.py`), reimplemented from the paper's equations. The reference code has no licence and was not used.
  - Single channel on a torus, FFT ring kernels, Gaussian growth.
  - Flow F = (1 − α)∇U − α∇A, with α = clip(A², 0, 1) (θ_A = 1, n = 2). Gradients are unnormalised 3×3 Sobel filters with wrap.
  - Reintegration tracking: dt = 0.2, s = 0.65, displacement clipped to dd − s = 4.35.
- **Rules:** written `FLENIA/R13/m…/s…/h…/r…/a…/b…/w…`, kernels joined by `+`.
  - `random()` uses the paper's ranges, with R fixed at 13 and 1–3 kernels of 3 rings each.
  - `mutate()` always changes the label.
  - `FLENIA/R13/diffusion` is the U = 0 control.
- **Float states in the engine (D-026).** A physics may declare `dtype = np.float32`.
  - **True float state:** the universe, forks, `state_hash` (tagged with the dtype) and storage (float32 blobs) all keep it.
  - **uint8 view:** each physics has a `view` (A on [0, 2]), which the observer's frame measures, the damage probe, the dashboard and `make_media` use.
  - **Structure census and exact recurrence** use the float state. Their thresholds are converted so they mean the same physical value as for uint8 Lenia.
  - **uint8 physics are untouched:** their view is the state itself.
- **Wiring:** discovery niche family `flow_lenia`, dashboard colour ramp, CLI help.

**Why float, not uint8:** a first uint8 version used exact largest-remainder rounding, and its integer mass was exactly conserved. But it had **quantization friction**: flows under about half a level per step were rounded away. Pure diffusion of the paper's patch froze after < 50 steps (rms radius 16.6), while float kept spreading (22.2 at step 400). Some rules that wobbled in float were pinned in uint8. It was dropped.

**Found:**
- **Bit identity:** the text output of `emergence benchmark --probes` (39 standard checks plus all 32 earlier probe checks) is identical before and after the change, and all earlier tests pass.
- **Mass:** conserved to float32 rounding. The worst relative drift within 1000 steps is 1.5e-8, with no trend (the float64 core drifts ~1e-13).
- **Rotation:** a rot90 seed evolves into the rot90 world exactly (200 steps; centroid mismatch 0.00). The grid and the Sobel filters do not make fake motion.
- **No positive control found.** 80 random float rules from the paper's 40×40 uniform patch (128×128 torus, 500 steps): 20 with 3 kernels, 20 with 5, 20 with 10, and 20 with 10 kernels and R random in [8, 25].
  - **0 self-propelled structures.** Two tracks passed the mover test, but both are small fragments (mass ~10) that fail the isolation test.
  - Most rules collapse into one blob or a few static blobs. The rest shed fragments or wobble.
  - Four candidates with the largest drift were inspected over 800 steps: fragments settle or creep, and none travels alone.
  - The 88 rules of the first, uint8 version (now dropped) gave none either.
  - This agrees with the paper: random search gives mostly static patterns, and directed motion with one channel needed long optimisation; two channels made it much easier.
  - **Two channels were not tried:** a 3D state would touch every observer path.

**Validation:** 5 probe checks (37/37; standard 39/39):
- mass conserved to float32 rounding;
- negative: a static-blob rule → not complex, quasi-static;
- deceptive: diffusion spreads (+9 cells rms in 400 steps) but has no movers;
- deceptive: a rotated seed moves the same way, rotated;
- selection-aware null: random rules picked by the old objectives → none complex without a mover.

There is **no Flow-Lenia positive**; the detector's positive is still the Lenia gliders. 5 new tests (56 in total).

**Caveats:**
- The paper states neither the Sobel normalisation nor the displacement clipping; the choices here are unnormalised Sobel and dd = 5.
- θ_A = 1 for one channel is our choice; the paper gives no value.
- Frame measures (activity, entropy, compression, local periodicity) see the uint8 view, so changes under 2/255 × 2 ≈ 0.016 in A count as no change. That is why the diffusion control is labelled `periodic`.

**Lesson:** a state that conserves mass exactly can still be the wrong physics. Rounding friction stopped slow flows, so the state had to be floating point.

---

## J-015 · 2026-11-07 · E-14 confirms: smooth starts make gliders, soups never do

**Question (pre-registered before running, `docs/data/e14-preregistration.md`):** does E-13's exploratory finding hold with fresh seeds and a test that can reach significance?

**Ran:** E-14, the same 8 glider-viable rules × 20 new seeds (master seed 14), 128×128, 2000 steps (commit `3453e99`). Two pre-registered contrasts, each a one-sided Fisher exact test on universes at α = 0.025:
- smooth ℓ = 3 vs soup at density 0.10 (same mass);
- smooth ℓ = 6 vs soup at density 0.35 (same mass).

**Found:**
- **Both contrasts confirmed:**

  | Density | Smooth start | Soup | Fisher p (one-sided) |
  |---|---|---|---|
  | 0.10 | smooth ℓ = 3: **28/160** universes | **0/160** | 1.0 × 10⁻⁹ |
  | 0.35 | smooth ℓ = 6: **21/160** | **0/160** | 2.4 × 10⁻⁷ |

- **Every glider is real:** all **51 structures in the 49 universes** were re-isolated and survived 1000 steps alone (validity check, pre-registered). The verification script is now committed as `scripts/verify_movers.py`. *(Corrected after review R-4.)*
- **6 of the 8 rules make gliders.** The best is μ 0.14, σ 0.014 at 8/20 in both arms (95% interval 22–61%). Two rules gave 0/40: σ/μ = 0.13 at μ 0.14, and Orbium's neighbour at σ 0.0195. Their seeded gliders exist (E-13a), and no E-14 smooth start found one (E-13 found one for σ 0.0195 from smooth ℓ = 10). *(Corrected after review R-4.)*
- **The lone-survivor pattern holds:** 47 of 49 glider runs end with exactly one persistent object, the glider; the other 2 end with two gliders.
- **Soups are equally consistent:** at density 0.10 all 160 die; at 0.35 all 160 turn into blob fields (9 of them still slowly changing at the horizon). *(Corrected after review R-4.)*
- **Scope:** these p-values are for universes within these 8 rules and this start generator. The rule-level sign test is p = 0.031 for both contrasts, above α = 0.025, because only 6 of 8 rules contribute. The finding does not yet generalise to "glider-viable rules" (R-4).

**Interpretation:**
- **What this shows:** in the glider-viable Lenia rules, self-propelled structures do arise on their own from unplanted random starts (**evidence level 2, spontaneous**), but **only when the start is spatially correlated**. The amount of matter is held fixed, so it is the arrangement that matters.
- **This differs from the Life-like result.** In J-009/E-10, arrangement did not matter once density was matched.
- **Why, in mechanism terms:** a glider needs an isolated lump of about its own mass and size with empty space around it. Correlated noise produces such lumps; uncorrelated soup averages out to a uniform potential that either freezes or dies.
- **What it does not show:** an ecology. The gliders mostly destroy each other until one is left (E-15 looks at this).

**Changed:** nothing in the code; data in `docs/data/experiments/2026-11-07-e14*.json`.

**Lesson:** an exploratory result, re-tested with fresh seeds and a test fixed in advance that can actually reach its threshold, is worth more than any number of post-hoc p-values.

---

## J-014 · 2026-11-07 · E-13: gliders emerge spontaneously, but only from smooth starts

**Question (pre-registered, `docs/data/e13-preregistration.md`):** in the 8 glider-viable rules of E-13a, does a glider arise by itself from a random start? Does the kind of start matter?

**Ran:**
- **Rules and seeds:** the 8 rules × 5 seeds, 128×128, 2000 steps (commit `df3a341`).
- **Starts:** soup, smooth ℓ = 3 / 6 / 10 (mass-matched, D-023), spots, and Chan's patches.
- **Densities:** 0.35 (E-13b, 240 universes, 9 min) and 0.10 (E-13c, 200 universes, 3 min).

**Found:**
- **Gliders emerged, from smooth starts only:** **18 of 240 smooth-start universes** grew a self-propelled structure, against **0 of 80** mass-matched soups. Spots gave 0 of 80 and Chan's patches 0 of 40.
  - smooth ℓ = 3 at density 0.10: 8/40
  - smooth ℓ = 6 at density 0.35: 6/40
  - other smooth arms: 0–2/40
- **All 18 are real gliders.** Each was re-isolated and survived **1000 steps alone** with mass 64–78, moving at 0.58–0.70 cells/step. They are the same creatures the E-13a scan grew from hand-made seeds; for μ 0.14, σ 0.014 the speed is 0.637 seeded and 0.638 spontaneous. This is the first spontaneous self-propelled structure in Lenia in this project (**evidence level 2**).
- **How they arise: survival after collapse.**
  - The soup becomes a static blob field at density 0.35 (all 40 runs) or dies at 0.10 (all 40).
  - Smooth starts mostly die, but first form a few isolated lumps. Some of these become gliders, which then disappear (collisions, decay) until at most one is left. Every glider run ends with **exactly one object**, a lone glider in an empty world.
  - Chan's patches did not produce gliders in 2000 steps on 128×128. Chan's claim ("given enough time") may need larger worlds or longer runs; we did not test that. *(Tested later in E-24, J-029: on 256×256, 13 of 160 patch worlds made gliders.)*
- **Pre-registered statistics: not confirmed.**
  - The planned test was a sign test across the 8 rules, at p < 0.05/20. The best contrast reached p = 0.0625 (smooth ℓ = 3 at 0.10: 5 rules higher, 0 lower). **With only 8 rules a sign test cannot go below p = 0.0078, so the design could never pass its own threshold.** That was a planning error.
  - A universe-level Fisher test (18/240 vs 0/80, p = 0.0048) was **not** pre-registered and is exploratory.

**Changed:**
- **E-14 pre-registered** (`docs/data/e14-preregistration.md`) to confirm the effect with fresh seeds: 20 seeds × 8 rules, two universe-level Fisher tests at α = 0.025.
- **E-15 (descriptive) queued:** glider populations in 9× larger worlds (`scripts/glider_population.py`).

**Lessons:**
- **Check that a pre-registered test can reach its threshold with the planned sample before running it.**
- **Matter has to be arranged, not just present.** A glider needs an isolated lump of the right size with empty space around it. Smooth fields make such lumps; soups make either a frozen field or nothing.

---

## J-013 · 2026-11-07 · E-12: no Lenia rule makes gliders from a soup, though gliders can exist

**Question:** with the corrected label (J-012), does the discovery engine find Lenia rules where self-propelled structures arise on their own, and does it beat random search?

**Ran:**
- **E-12:** engine vs random search, seed 11. 100 rules × 2 seeds × 5 generations per arm, 96×96, 500 steps, plus follow-ups; 12 + 14.5 min on 12 cores. Commit `feef3f1`.
- **E-13a:** a glider-viability scan, 99 single-ring rules on a μ × σ/μ grid (`scripts/lenia_glider_scan.py`).

**Found (E-12):**
- **No movers at all.** **0 self-propelled structures in 2085 universes** (1045 engine, 1040 random), and 0 rules `complex`. 5 candidate movers all failed the isolation test. Two were inspected: a slowly drifting blob, and a piece of debris that needs its neighbours. Alone, both dissolve within 25–50 steps.
- **The engine still finds more structure,** as it did for Life-like rules (J-004):
  - "Structured" rules: 103 vs 27, or **58 vs 27 (2.1×) after removing near-duplicates** (μ and σ/μ to 0.01, same ring count).
  - Behaviour niches: 11 vs 9.
  - Quasi-static universes: 49% (engine) vs 81% (random).
- **The structure the engine finds is not motion.** Its follow-up candidates reach evidence level 0–1. They are persistent textures, chaotic fields and slowly changing blob fields.

**Found (E-13a): gliders can exist, but only in a small island.**
- **8 of 99 single-ring rules** support a glider grown from one of 12 asymmetric seed shapes (held 400 steps) (μ 0.14–0.16, σ/μ 0.10–0.13; speeds 0.54–0.69 cells/step, mass 65–77). This is the region around Chan's Orbium.
- **The engine found this island without being told:** 59 of its 500 rules fall inside it (7 single-ring), against 9 for random search (6.6×). Still, not one soup there produced a glider.
- **So for these rules, emergence is the bottleneck, not search.** The physics allows gliders; random soups don't make them.

**Literature (agent review; papers and code read where available, abstracts only where marked in [Research]({{ '/research.html' | relative_url }})):**
- **Chan's starts were different from ours.** Chan (2019) says creatures such as Orbium emerge "given enough time" from random starts, but gives no rate. His starts were **15–40 dense patches of side 0.9 R in vacuum**, not full-grid soups.
- **Nobody reports a rate.** No paper estimates how much of Lenia rule space supports movers, or how often they emerge. E-13a is a first number for single-ring rules.
- **Flow-Lenia** (Plantec et al. 2023, 2025) claims movers are common and evolution happens inside the simulation, but reports no counts and no neutral model.

**Changed:**
- **E-13 pre-registered and committed** before running (`docs/data/e13-preregistration.md`).
  - Panel: the 8 viable rules.
  - Starts: soup, smooth starts with ℓ = 3, 6, 10 (mass-matched), spots, and Chan's patches (added by a dated amendment after the review, before any run).
  - Densities: 0.35 and 0.10.
- **New init kind `patches`** (Chan's protocol).
- **Flow-Lenia implementation started** on its own branch (`v0.7-flow-lenia`).

**Caveats:**
- The E-13a viability test uses 8 hand-chosen seed shapes, so it can miss gliders that need other shapes. 8/99 is a lower bound for single-ring rules.
- E-12 is one seed per arm. The engine-vs-random comparison is preliminary, as in J-004.

**Lesson:** separate *can it exist* from *does it arise*. A search that finds the right region can still report zero if emergence, not viability, is the limit.

---

## J-012 · 2026-11-06 · Static Lenia blob fields were labelled "complex"; fixed for continuous physics

**Question / why:** a review found that the class label and the discovery objectives, tuned for 2-state rules, inflate Lenia results. `emergence observe "LENIA/R13/T10/m0.150/s0.0150/b1" --steps 1000 --size 128 --seed 1` returned **complex** for a field of 20 static blobs (0 movers, activity 0.041, local periodicity 0, no cycle). Three 2-state tests fire on continuous fields:
- **4+ persistent objects count as complex:** every blob of a settled Lenia soup is a persistent object, and the census counts *instances*, not shape types.
- **Any value change counts as activity,** and exact-cycle and exact local-periodicity tests never fire on continuous values.
- **Objectives reward static fields:** `vocabulary` (instances) and `aperiodic_activity` favour exactly these fields, so the search is pushed toward static blob fields. That fits 0 of 500 rules in E-12 run 1 producing a mover.

**First question: rounding noise or real dynamics?** Real. In the Orbium soup ([C-01]({{ '/experiments.html' | relative_url }}), `scripts/lenia_static_fields.py`):
- **Float64 does the same.** Continued for 3000 steps, both the quantized run and a float64 run without any rounding change 13% of cells by > 32 levels. 5% have changed after 100 steps.
- **Not ±1-level flicker.** Per-step changes reach 25 levels; only 4% of changing cells stay within 8 levels.
- **It is all at object edges.** 100% of changing cells are within 2 cells of an edge. 56% creep (net change > 32 levels in 100 steps) and 19% oscillate in place.

The blobs never travel; their edges relax slowly for thousands of steps. Calling this "frozen" would be as wrong as calling it "complex".

**Found:** 60 random Lenia rules (96×96, 500 steps). The old label called **27 complex**; all 27 have **no self-propelled structure**, and nearly all their persistent objects are still. The new label calls none complex. 26 are quasi-static, and 5 remain rankable `active` rules with real dynamics but nothing that travels (moving stripe textures, breathing ring-shaped blobs). None of the 60 has a self-propelled structure.

**Changed (continuous physics only; discrete labels, objectives and all 39 + 24 earlier benchmark results are unchanged and were checked byte for byte; D-022):**
- **Value tolerance:** activity and local periodicity ignore changes of ≤ 2 levels (of 255). The emergent glider changes its cells by a median of 19 levels per step; only 5% of its changes are ≤ 2.
- **Near-fixed point:** no change above the tolerance in the window → `frozen`. Tested with a jitter control: a fixed field with ±1-level flicker, which exact tests call active.
- **`complex`** needs at least one self-propelled structure; static persistent objects no longer count.
- **Quasi-static:** no self-propelled structure, and *free activity* (activity more than 3 cells away from objects that stay in place) below 0.002. Such runs are labelled `active` but count as settled, so they are never ranked or bred from, like frozen discrete runs (D-005).
- **Objectives:** `aperiodic_activity` uses free activity, and `vocabulary` counts persistent objects that are *not* still.
- **`analysis.complex_all_seeds`** (`emergence compare`) inherits the corrected label. Lenia results stored before this fix must be re-run.

**Caveats:**
- **The 0.002 cut-off is a judgment call.** It sits between the highest free activity of a field that looked static (0.0018) and the lowest of one that looked dynamic (0.0029), a 1.6× margin, set from 60 rules after viewing them. The `complex` label does not depend on it; ranking near it may flip.
- **Movers are the only route to `complex` in Lenia.** Creatures that rotate or pulse in place are not counted.

**Validation:** 8 new probe checks (32/32 Lenia and probe checks; 39/39 standard): positive (two emergent gliders → complex), negative (blob soup → not complex, quasi-static), deceptive (smoothed noise stays at zero; creeping soup is not frozen; jitter is frozen), a dynamic non-travelling rule stays rankable, and a selection-aware null. That null takes the random rules the *old* objectives would pick (most persistent objects; most activity): none may be complex without a mover. 51 tests.

**Also fixed:**
- **`Lenia.mutate`** could return the parent unchanged (one ring, add branch, coin flip fails). Small μ/σ steps could also round to the same label. Every mutation now changes the label, and the constructor rounds to label precision.
- **Emergent glider speed:** it is **~0.53 cells/step**, not ~0.1 as documented. Measuring over 200 steps on a 128-cell torus wraps around (106 cells > 64) and reads ≈ 0.11, which is probably where 0.1 came from.
- **`continuous.track`** is now annotated as returning a tuple.

**Rebuilt (lost with the cloud container, never committed):** the `smooth` start condition (D-023), and the conditions study now skips the exact-shape probes for continuous physics (`innovating` is reported as not applicable).

**Lesson:** a label or objective validated on one physics family must be re-validated with that family's own controls before its numbers are read.

---

## J-011 · 2026-11-05 · v0.5: Lenia physics and a tolerant structure detector

**Built (commit `85b289f`, rebased onto `main` after PR #3):**
- **Lenia physics** (`physics/lenia.py`): continuous states quantized to 256 levels, FFT convolution, ring kernels, Gaussian growth. Rules are written `LENIA/R13/T10/m0.150/s0.0150/b1`, and exploration varies μ, σ and the rings.
- **Tolerant structure census** (`observatory/continuous.py`): thresholded objects labelled on the torus, frame-to-frame tracking with a mass tolerance, persistent/still/mover counts, and a self-propulsion test on isolated clones.
- **Controls:** a smoothed-noise control physics and Lenia benchmark controls: two emergent gliders derived from the Orbium parameters (not hand-typed), a settled soup, smoothed noise, and a decaying lopsided blob (24/24).
- **Integration:** discovery, CLI and dashboard accept any physics. The exact-shape probes (innovation, replication, knockout) are marked not applicable for continuous physics.

**Ran (cloud, now lost):** E-12 run 1, a Lenia exploration. It reported about **44% of rules "complex"** and **0 of 500 rules with a mover**. Those numbers came from the inflated label (J-012) and **cannot be trusted**. The data, the `smooth` start condition, the conditions-study probe skip and the gallery clips were never committed and were lost with the cloud container. No E-12 data exists in this repository.

**Lesson:** commit or export before the container goes away; uncommitted cloud work is not a result.

---

## J-010 · 2026-11-05 · Knockout test: no evidence of cumulative innovation

**Question:** do earlier innovations *enable* later ones (cumulative innovation, objective O5)?

**Built:** `observatory/knockout.py` (D-020). When a new persistent type appears, three kinds of forked clone are run:
- **unchanged;**
- **knockout:** the new type deleted;
- **controls:** the same number of cells deleted from *old* structures.

The question is whether later novelty is lost more after the knockout than after the controls. Validated on:
- **positive:** a glider hits a block and leaves debris. Deleting the glider, or the first debris, removes 75–100% of the later novelties, against 0% for the controls;
- **negative:** deleting an uninvolved block;
- **deceptive:** Brian's Brain (20/20 probe checks pass).

**Ran:** E-09 to E-11 (92 knockouts across 22 rules × 4 initial conditions).

**Found:**
- **Set-based test, which asks whether the same new shapes appear:** 88 of 92 were *inconclusive*. Deleting old structure rewrote 50–90% of the future just as much as deleting the new type: any change spreads over 1000 steps. This happens even in rules whose 64-step damage measure is low, so the short damage measure underestimates sensitivity over long horizons.
- **Count-based test, which asks whether fewer new shapes appear:** added because of the above. Its first version flagged 5 "dependencies", but a **placebo test** (each control deletion treated as the target) shows real knockouts are **indistinguishable from placebos**: P(real > placebo) = 0.491 (E-11) and 0.510 (E-10). Only 1 real knockout exceeded the placebo's 95th percentile per run, against 1.5–3.1 expected by chance.

**Changed:** the count-based verdict now requires an actual drop, larger than every control's, of at least the placebo's 95th percentile (0.5). The study summary reports the population-level placebo test. Commits `b47ff1f`, `85c3c2e`, `1a48270`.

**Conclusion:** among universes that look like they keep innovating, **no new structure is necessary for later novelty**. The apparent innovation behaves like chance turnover in a sensitive (chaos-like) system. This is O5 tested and not observed, at this scale.

**Lessons:**
- In sensitive systems, compare interventions with **placebo interventions**, not with zero.
- A threshold chosen before seeing the null distribution will produce false positives.

---

## J-009 · 2026-11-05 · Initial conditions: the "environment" effect was a density effect

**Question (H4, from review R-3):** does *where* matter starts change what a fixed rule produces?

**Built:** initial-condition generators in `UniverseSpec.init`: uniform, gradient, central patch, spots (D-019). Old specs stay bit-identical (tested). `emergence conditions` runs a paired study: the same rules and seeds under each condition, with a sign test and a bootstrap CI, and outcomes fixed in advance.

**Ran:**
- **E-09:** 22 rules × 4 conditions × 3 seeds, 96×96, 2000 steps.
- **E-10:** a density-matched control.
- **E-11:** an exact rerun of E-09.

**Found:**
- **E-09:** starting from a central patch gave **+1.35 self-propelled shape types** (9 rules higher, 0 lower; p = 0.004, CI excludes 0). This was the only result that survived a Bonferroni correction across 9 tests. Conway's Life showed it most clearly (0 → 15 in one seed; see [Gallery]({{ '/gallery.html#life-central-patch' | relative_url }})).
- **But the patch also starts with less matter** (density 0.125 vs 0.35). **E-10** compared the patch with a uniform soup at the *same* 0.125 density: **no difference** (−0.08, 5 higher / 4 lower, p = 1). The effect came from **less matter, not localized matter**: sparser worlds let gliders survive.
- **Gradient:** slightly more universes still unsettled (+0.14, CI excludes 0, but sign test p = 0.125); weak, and not followed up yet.
- **E-11 reproduced E-09 exactly** on every primary outcome.

**Conclusion:** H4 as tested is not supported. Localizing matter (patch, spots) doesn't matter once density is matched. Density itself does.

**Lesson:** any "environment" comparison must hold the amount of matter fixed (D-021). Without E-10 we would have reported a false environment effect.

---

## J-008 · 2026-11-05 · Journal, docs and next-phase plan

**What:** Created this site (`docs/`, served by GitHub Pages), the agent handoff (`AGENTS.md`, [Handoff]({{ '/handoff.html' | relative_url }})), the experiment data exports (`docs/data/experiments/`) and a reproducible media pipeline (`scripts/make_media.py`, `scripts/make_figures.py`).

**Why:** The work had spread across chat sessions and two AI reviewers. Decisions and negative results were at risk of being lost, and a new agent couldn't have continued without the conversation history.

**Review:** ChatGPT's third review ([R-3]({{ '/reviews.html#r-3' | relative_url }})) recommended two research tracks: stronger innovation controls, and a second physics family (Lenia). It also suggested studying initial conditions. We agree with most of it, with three amendments (see [Research → Next steps]({{ '/research.html#next-steps' | relative_url }})):
- **Causal knockouts:** test whether earlier novelties *enable* later ones by removing them in a clone.
- **Initial conditions first:** start with the initial-conditions track, because it is cheap and needs no new physics.
- **Same-rule null:** prefer a same-rule, independent-seed null over generic space-time surrogates.

**Status:** plan proposed (D-018), not yet started.

---

## J-007 · 2026-11-05 · Round 5: innovation must be ongoing to count

**Ran:** E-08 (full pipeline, seed 12).

**Found:** Two universes were labelled "still innovating", yet their long runs had settled:
- **B3/S0123678** entered an exact cycle at t = 1737.
- **B17/S1348/C7** ended with 97% of its changing cells oscillating in place.

**Changed:** "Still innovating" now requires the extended run to remain unsettled; otherwise the verdict is *transient innovation that ended* (D-016). Commit `32df04e`.

**Lesson:** a claim in the present tense ("still innovating") must be checked at the end of the observation, not averaged over it.

---

## J-006 · 2026-11-05 · Round 4: sampling aliasing; chaos is inconclusive

**Found (E-07):**
- **#1169 B3/S1236/C7 (sampling aliasing):** it was flagged as innovating, but its long run sits in an exact cycle of period 840 from t = 933. Sparse sampling kept catching cycle phases it had not seen yet, and those looked like new shapes.
- **#173 B1678/S13478 (steady turnover):** it produces new shape types at a flat rate (75, 62, 52, 71 per quarter), and only ~5% of them recur. That is what a stationary noisy process gives by chance.

**Changed:**
- No innovation can be counted after an exact cycle begins.
- A flat new-type rate with damage spreading ≥ 0.3 is reported as *inconclusive* (a heuristic; a matched null is still open).

Commit `328c078`.

**Lesson:** i.i.d. noise is not a fair null for a spatially correlated chaotic rule.

---

## J-005 · 2026-11-05 · Rounds 2–3: innovation and replication probes

**Built:**
- **Innovation probe:** orientation-free persistent shape types tracked over a long run. "Established late" means first seen in the third quarter and seen again in the fourth. Each experiment runs a noise control that gives the false-positive floor.
- **Replication probe:** the shape alone in an empty clone, whose copy count must grow. Two null tests on random patterns: rule-level duplication and common product.
- **Evidence ladder** (D-014).
- **14 hard and deceptive controls** (D-012).

**Found while validating:**
- **Seeds false positives:** a scan of Seeds (B2/S) soups first reported **6 "self-replicators"**. They were simply common shapes that any explosion produces, so the *common product* null was added and rejects them.
- **Power-of-two artifact:** Fredkin's rule seemed not to replicate, because the 256-cell test world is a power of two and linear rules annihilate there. The test world is now 160 cells.
- **Explosive patterns:** they made the probe ~100× slower, so a cutoff marks them *explosive (untestable)*.

**Result (E-07):** 0 self-replicators among 9 candidates; the highest evidence level was 2 (#1181). Commit `7009020`.

**Lesson:** scanning the most common shapes selects exactly the shapes that background production favours. Every detector needs a null built around how its candidates were *selected*.

---

## J-004 · 2026-11-05 · Round 1: calibrated robustness and a random baseline

**Question:** does the discovery engine beat random search at all? It had never been tested.

**Ran:** E-03 to E-06: engine and random search, seeds 11 and 12, identical compute (100 rules × 2 seeds × 6 generations on 96×96).

**Found:**
- **The engine wins.** It finds 90 vs 29 rules with self-propelled shapes, 56.5 vs 8 rules "complex" on every seed, and 33 vs 25 niches.
- **The advantage shrinks after deduplication.** Counting only rules at least 2 mutations apart, it is **1.9×** and **4.2×**. About 40% of the raw advantage was near-duplicate mutants.

**Also:**
- **Robustness threshold:** recalibrated from each experiment's own seed variation (90th percentile ≈ 0.3). The old fixed 0.5 accepted 29% of pairs of *different* rules.
- **Tournament:** made explicit.
- **Naming:** "verified movers" renamed "self-propelled shapes".

Commit `b77f873`.

**Lesson:** report counts after removing near-duplicates whenever a search breeds from its own winners.

---

## J-003 · 2026-11-05 · Review R-2 and the v0.3 plan

ChatGPT reviewed v0.2 ([R-2]({{ '/reviews.html#r-2' | relative_url }})). We agreed on calibration, terminology and the evidence ladder. We pushed back on going straight to a replication detector, and on Fredkin's rule as the positive control: it copies *everything*, so it belongs with the deceptive controls, and HighLife's replicator is the real positive. We prioritised a random-search baseline and an innovation-over-time measure first.

---

## J-002 · 2026-11-05 · v0.2: validated discovery

**Built:**
- **Mover verification:** candidate movers are tested in isolated clones.
- **Seed screening:** every rule runs on 2 seeds on 96×96.
- **Niches:** MAP-Elites-style behaviour niches.
- **Longer runs:** a 4× extended run for each candidate, with verdicts *persists / fades / loops*.
- **Sustained objective:** a slowly dying universe now scores less.
- **Benchmark:** `emergence benchmark` (39/39) and a deterministic noise-control physics.

**Mistakes found and fixed during the run:**
- **Niche collapse:** the first niche axes put 90% of the eligible rules into one niche (just 4 niches occupied in generation 0), so the axes were redefined.
- **Missed cycles:** universes that fell into long exact cycles were reported as "persists".

**Result (E-02):**
- **Niches grew from 7 to 33**, and the multi-state share in the top 30 fell from 87% to 77%: a modest gain.
- **7 of 11 candidates settled** in their longer run, some only after ~3000 steps.
- **#1029**, a striped medium with moving defects, persisted. Its defects only move *within* the stripes, so they never count as self-propelled.

Commits `d9b2197`, `f394662`.

---

## J-001 · 2026-11-05 · v0.1: MVP and first evaluation

**Built:**
- **Engine:** Life-like and Generations automata on a torus, behind a physics interface.
- **Observatory:** activity, block entropy, compression against a shuffled copy, recurrence, structure census, damage spreading.
- **Discovery:** Pareto ranking plus novelty search.
- **Lab notebook:** SQLite, with deterministic seeding and `reproduce`.
- **Dashboard:** gallery, playback, rewind, zoom, comparison and lineage.

Commit `4a07778`.

**Found (E-01):**
- **Real phenomena:** novelty search found spiral waves and glider-rich rules without being told what to look for ([Gallery]({{ '/gallery.html' | relative_url }})).
- **Strobing rules:** initially ranked top, with ~99% of cells flipping every step. A *local periodicity* measure fixed this, and settled universes are now excluded from ranking (D-005).
- **Fields of independent oscillators:** they never repeat globally but are just repetition, and the same local periodicity measure catches them.
- **Family collapse:** multi-state rules grew from 28% to 73% of the population in 10 generations (fixed in v0.2).
- **Isolated mover candidates:** #463's mover later proved to be a false positive.

**Lesson:** the first versions of "interesting" are always fooled by something trivial. Look at the universes, not just the scores.

---

## Entry template

```markdown
## J-0NN · YYYY-MM-DD · Short title

**Question / why:** what we wanted to know or fix.
**Ran:** experiment IDs (add them to experiments.md and export data with scripts/journal_export.py).
**Found:** numbers, with the caveats that matter (sample size, near-duplicates, nulls).
**Changed:** code changes, decision IDs, commit hashes.
**Lesson:** one sentence worth remembering.
```
