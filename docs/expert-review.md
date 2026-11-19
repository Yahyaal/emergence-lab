---
title: Expert review pack
description: What we claim, at what evidence level, how strong the evidence is, and which claims and choices we most want an artificial-life researcher to check.
---

# Expert review pack

<p class="lead">Written on 19 November 2026 (J-106) for an outside artificial-life researcher who knows BFF and "Computational Life" (Agüera y Arcas et al. 2024), Tierra, Avida, Squirm3 and open-endedness work, but not our code or our IDs. It adds no new results. Every number is copied from the journal, a pre-registration or a JSON export, and its source is given. A few headline numbers were recomputed from the exports (section 9).</p>

**How to use this page.** Section 1 is a half-page summary. Sections 3 and 4 hold the results. Section 5 lists the claims we most want checked, ranked, each with a concrete way to check it. Section 7 holds our questions to you. If you have one hour, read 1, 4, 5 and 7.

**IDs used below.** E-xx is an experiment (rows in [Experiments]({{ '/experiments.html' | relative_url }})). J-xxx is a journal entry ([Journal]({{ '/journal.html' | relative_url }})). D-xxx is a design decision ([Decisions]({{ '/decisions.html' | relative_url }})). R-x is an earlier review ([Reviews]({{ '/reviews.html' | relative_url }})). Exports are under `docs/data/experiments/`; pre-registrations are `docs/data/e*-preregistration.md`.

## 1. Summary

**Question.** Does complex, persistent and possibly evolving structure arise on its own from simple fixed rules, and which rules or initial conditions make it likely? Nothing is planted, steered or rewarded inside a running world. Observation is passive; interventions run only on cloned copies.

**What we built.** A laptop-scale lab (Python, NumPy, small C interpreters). It has four substrates: Life-like cellular automata, the Lenia family, BFF program soups, and a SUBLEQ-like family we defined. Each claim is placed on a five-step **evidence ladder**: 1 persistent organisation; 2 self-propelled structures; 3 self-replication; 4 heredity and variation; 5 open-ended evolution (`docs/research.md`, D-014). Every detector has a positive, a negative, a deceptive control built to fool it, and a null that accounts for how candidates were selected. Confirmatory tests are pre-registered.

**Headline findings, at the level reached.**
- **Level 3 from random code** in BFF (E-40, E-41), as Agüera y Arcas et al. reported first, and in SUBLEQ versions we designed (E-75).
- **Level 4 in BFF only:** one-byte mutations of all 9 emergent replicators are inherited (E-42).
- **Level 5 is not shown.** In standard BFF, later code is not fitter than earlier code by four measures (E-48 to E-54). That stays true with neighbour-only meetings (E-78) and with a lattice-native fitness assay (E-80; precise only in a variant rule). No parasites appear in standard BFF (E-66, E-67).
- **When program length can vary** (BFF-VL, E-81), later copiers do beat earlier ones, because they get shorter. Then every soup stops at the same 6-byte copier. This is directional selection favoured by the rule's construction, not level 5.
- **E-82 to E-85 asked whether a host–parasite arms race can start.** Each variant removed one obstacle and hit another. Our synthesis: the conditions an arms race needs (parasites that win, cheap resistance, resident host populations, room for a lock) pull against each other in these soups. E-82 and E-83 were pre-registered; **E-84 and E-85 are groundwork only, not pre-registered**, on 4 pilot seeds.

**What we do not claim.** Level 5. Novelty of the BFF replicator result (published). Any result at scales beyond a laptop (soups of 2^13 to 2^17 programs, tens of thousands of rounds). We computed none of the field's standard open-endedness statistics (Bedau–Packard activity against a neutral shadow; MODES).

## 2. Methods in brief

### 2.1 Substrates and rules

| Name | What it is | Where |
|---|---|---|
| **BFF** (standard) | 2^14 random programs of 64 bytes (also 2^13 to 2^16). Each **round** (in later variants called an **epoch**: the same unit) every program is paired at random; the pair's joined 128-byte tape runs a Brainfuck-like instruction set, step limit 8,192, then is split back. Both heads start at byte 0 and wrap. Background mutation 0.024% per byte per round. | `emergence/programs/bff.py` |
| **Head-start variants** (h, g) | BFF with one head starting at byte h (and the other at g). The **h = 64** rule is used in E-80 Part B and is the base of BFF-VL. | `scripts/bff_kernels.c` |
| **SUBLEQ family** | A family of SUBLEQ-like languages we defined (16,416 rules; a stepping index and an operand window are our additions, D-054). Plain SUBLEQ and RSUBLEQ4 are anchors; they made no replicators. | `emergence/programs/subleq.c/.py` |
| **Lattice soups** (E-78, E-80) | BFF where programs meet only lattice neighbours on a torus (S), against well-mixed continuations (M) and a second well-mixed seed (M′, the seed null). | `scripts/bff_spatial.py`, `scripts/lattice_assay.py` |
| **BFF-VL** (E-81, D-070) | A 2^20-byte budget split into programs of 4 to 128 bytes. Second head starts at the partner. **Two departures from BFF:** heads halt at the tape ends instead of wrapping, and the tape is cut after every marker byte `!` (a no-op) and at 128. Bytes are conserved; the number of programs is not. A copier of length L leaves about L_partner/L copies, so shorter copiers win by construction. | `scripts/bffvl.c/.py` |
| **BFF-X** (E-82, D-072) | BFF-VL, but for each pair a third program C is drawn from the soup. The instruction pointer runs A, then **C's code instead of B's**. C is read only, so it persists. A program that falls off its end runs its neighbour's copy loop on its own bytes and is copied: Tierra's parasite mechanism, in minimal form. | `scripts/bffx.c/.py` |
| **BFF-XR deme64** (E-83, D-074) | BFF-X with programs on a ring. Each epoch the ring is cut at a random offset into **demes** of 64 programs; pairs and borrowed code are drawn within a deme, and pieces are written back in place. Offspring stay near their parent, so refusing callers protects kin. | `scripts/bffxr.py` |
| **BFF-XF** (E-84, D-076) | Fixed 64-byte programs with BFF-X's borrowed library and E-83's demes. A lock costs no length. | `scripts/bffxf.py` |
| **BFF-XM deme64** (E-85, D-078, D-080) | BFF-XR deme64 in which a program shorter than 32 bytes has no code of its own (its instruction pointer starts in the borrowed code). The shortest host is 32 bytes, a parasite can be 4. Revision D-080 merges a short unterminated tail into the previous piece and uses a lock that does not rewrite the caller. | `scripts/bffxm.c/.py` |

All BFF variants above are hand-designed by us. D-070 to D-080 are recorded as "proposed": reviewed by the coordinating agent session, not yet accepted by the owner (`docs/decisions.md`).

### 2.2 Detectors and controls

Project terms used below:
- **Jump:** the moment a soup is taken over by self-copying programs, confirmed by a replicator detector, not by entropy alone (D-045, D-047, D-050).
- **Replicator detector** (D-040): 8 copies of a candidate among random programs must grow to at least 64 and at least 4× over two generations, with random programs tested the same way as a null.
- **Heredity test** (D-041): each one-byte mutant of a replicator is seeded alone; a mutation is "inherited" if at least half of the resulting family carries it while the unmutated parent's family does not.
- **Race score** (E-81, D-071): about 1,024 bytes of each of two programs in 2^16 bytes of random code, 8 epochs, no mutation; score = change in ln(bytes of A / bytes of B). Calibrated on a ladder of padded copiers (one extra byte on a 12-byte copier: 1.27; 7-byte against 6-byte: 1.59).
- **Host and parasite** (E-82, D-073): a host copies itself with nothing to borrow. A parasite never copies itself, is copied with soup libraries but not with random ones, and its copies mostly come from its own runs.
- **Coverage q(P, H):** the share of a 128-byte partner that parasite P fills with copies of itself when H is the library.
- **Time-shift score RQ:** mean over sample times i < j of q(P_j, H_i) − q(P_i, H_j). It is 1 for a designed arms race, −1 reversed, 0.19–0.20 when 1 host in 5 resists (the graded control). **d3** = q(P_1, H_1) − q(P_1, H_3): do hosts at T + 10,000 resist parasites of T + 1,000? **Protection w** (E-83 onward) is the share of the partner left untouched; it catches hosts that "refuse" by rewriting the caller.

Each detector has a positive, a negative, a deceptive control and a selection-aware null in `emergence/benchmark_probes.py` and `emergence/benchmark_programs.py`. The latest benchmark run passes 39 standard checks and 222 probes (J-105). Section 7 of `docs/paper.md` lists 13 cases where a detector fooled us and the control that now exists.

### 2.3 Pre-registration discipline

For E-81 to E-83 (and the earlier pre-registered tests) the hypothesis, analysis, sample size and verdict rules were committed and pushed before any registered seed ran (E-81 `72ffb96`, E-82 `e8010f6`, E-83 `67331d3`). Each run has a **validation gate**: the instrument controls and a built-in positive must pass before any score is computed. The **smallest effect of interest δ\*** is half the effect of a built-in control (E-81: half the 6-vs-7-byte race score, 0.79; E-82, E-83: half the graded 1-in-5 resistance score, 0.10; E-80 Part B: half the copier-against-dying-copier difference, 0.435). With 40 soups a tiny drift becomes significant, so **a primary fails when its whole 95% interval lies below δ\***, even if p < 0.05. Tests are one-sided sign-flip permutation tests with the soup as the unit.

### 2.4 Multiple comparisons

A pre-registered Holm correction (D-067, E-79) covers every registered primary that is a significance test of a predicted effect. Primaries that are counts or criteria (including E-42's heredity count and the P1 parasite criteria) are excluded with a reason; predicted-null tests are listed apart. The latest export, `2026-11-18-e83-holm51.json`, has **51 p values: 22 passes, 20 survive Holm**. Lost: the soup-size exponent E-50 (adjusted 0.40) and E-71's within-variant copier count (0.17). With rules rather than soups as the unit, far fewer survive (J-092: the Lenia contrasts and all F-predictor tests except E-70 do not).

## 3. Main findings

"Pre-reg." = pre-registered; "Holm" = adjusted p in the 51-value family where the test is in it.

| Finding | Level | Key numbers (95% intervals) | Exp. | Source |
|---|---|---|---|---|
| Self-propelled structures in Lenia arise from spatially correlated (smooth) starts, not from uncorrelated ones of the same mass; shuffling the same values removes them | 2 | Smooth / shuffled / soup: 37 / 0 / 0 of 160 worlds at density 0.10 (p = 6.9 × 10⁻¹³). Rule level: 6 of 8 rules higher, sign test p = 0.016; does not survive Holm at rule level | E-14, E-19a (pre-reg.) | J-015, J-021; `2026-11-07-e19-shuffled-null-and-soup-sweep.json` |
| Replicators arise from random BFF code (published result, reproduced) | 3 | 3 of 16 soups of 2^14 by 48,000 rounds; verified replicators in every jumped soup, none in 22 end scans of the others | E-40, E-41 (pre-reg.) | J-040, J-041; `2026-11-08-e41-bff-longer.json` |
| One origin rate per pair run fits BFF soups of all sizes | 3 (rate) | 0.036 per 10^8 pair runs (0.017 to 0.066); exploratory | E-76 | J-086; `2026-11-14-rate-model.json` → `step5_bff` |
| Moving one head's start to byte 64 gives forward copiers and fast jumps | 3 | 8/8 soups by 250–1,750 rounds vs 0/12 by 16,000; h = 127 control 2/16 vs 8/8 | E-57, E-59 (pre-reg.) | J-057, J-059 |
| "Shortest copier makes a working copy" (F) predicts which BFF-variant rules make replicators; nothing predicts speed | 3 (O6) | Soups F 60/60 vs other 15/60 (E-70, p = 2 × 10⁻²⁰). Rule-level Fisher after Holm: only E-70 survives (0.012) | E-60 to E-74 | `docs/paper.md` §4.3; J-072, J-092 |
| Heredity: one-byte mutations of emergent BFF replicators are inherited | **4** | 9 of 9 replicators; 140 of 141 viable mutants carried | E-42 (pre-reg.; a count, outside the Holm family) | J-042; `2026-11-08-e42-bff-heredity.json` → `summary` |
| Later standard-BFF code is not fitter (four measures) | 5 not shown | Races p = 0.07, then 0.33 with verified replicators; growth-rate trend p = 0.38; kin-free invasion p = 0.88; 7 long soups D = −0.15, p = 0.64 | E-48 to E-54 | J-048 to J-053, J-066; `2026-11-08-e54-long-soups.json` |
| No parasites in standard BFF | 5 not shown | 99.8% of 2,800 common programs copy themselves; 0 parasites; 0 among 420 rarer programs | E-66, E-67 | J-068, J-069; `2026-11-09-e66-parasites.json` |
| Neighbour-only meetings do not make fitter code (well-mixed garden) | 5 not shown | d = −0.42 (−1.10 to 0.25), δ\* 0.28; seed null significant (M′ below M in 7 of 7, p = 0.016) | E-78 (pre-reg.) | J-089; `2026-11-15-e78-spatial.json` |
| …nor in a lattice garden | 5 not shown | Part A (7 soups): −0.61 (−2.05 to 0.83), δ\* 1.24. Part B (16 h = 64 soups): **−0.047 (−0.114 to 0.020)**, δ\* 0.435 | E-80 (pre-reg.) | J-095, J-096; `2026-11-17-e80-partB.json` |
| **With variable length, later copiers are fitter because shorter, then stop** | directional selection; 5 not shown | P1 (T+1,000 vs T) 9.12 (8.65–9.60), 40/40; P2 (T+10,000 vs T+1,000) 0.55 (0.19–0.90), passes only because the interval reaches above δ\* 0.79; P3 (T+20,000 vs T+10,000) −0.025 (−0.078 to 0.028), fail. Holm: P1, P2 1.9 × 10⁻⁴ | E-81 (pre-reg.) | J-098; `2026-11-17-e81.json` |
| With borrowable code, parasites appear at once; no arms race | 5 not shown | P1 parasites in 40/40; P2 RQ 0.0011 (−0.0004 to 0.0027), δ\* 0.10; P3 d3 = 0 in 40/40 | E-82 (pre-reg.) | J-100; `2026-11-18-e82.json` |
| With demes, refusing pays kin, but no host resists | 5 not shown | Gate race +0.17 to +0.32 (4/4); P2 RQ 0.0004 (−0.0002 to 0.001); P3 0 in 40/40 | E-83 (pre-reg.) | J-102; `2026-11-18-e83.json` |

**On the null in fixed-length BFF.** The literature review (J-091) noted that the usual published route to fitness gain after emergence is shortening (Tierra's 80 → 22 instructions; Squirm3), and BFF programs are fixed at 64 bytes. E-81 tested this inference: once length can change, later code is fitter, from a median 106 bytes at the jump to 6.2 bytes 1,000 epochs later, and then it stops (J-098). We read this as "BFF's null is what its fixed length predicts", for this one variant rule.

## 4. The E-81 to E-85 chain

Each step removed one wall and hit another.

| Step | Variant | Wall it removed | New wall it hit | Key numbers | Status |
|---|---|---|---|---|---|
| E-81 | BFF-VL | Fixed length: nothing could improve | Length floor: every soup ends on the 6-byte `[.>}]!` (24 soups) or `[.}>]!` (16); nothing beats it | P1 9.12, P2 0.55, P3 −0.025 (−0.078 to 0.028) | pre-reg. (J-098) |
| E-82 | BFF-X | No persistent bodies or borrowable code, so no parasites | Resistance is a public good: a refusing library spares a random third program, and costs bytes | Parasites (4–5 bytes) in 40/40; mean coverage 0.998 (every host copies every parasite); RQ 0.0011, d3 0 in 40/40 | pre-reg. (J-100) |
| E-83 | BFF-XR deme64 | Public good: refusing now pays kin | Room for a lock: the shortest refusing host is 10 bytes, the winning copier 6; the length cost is about ten times the kin benefit | Kin benefit +0.17 to +0.32 under deme64, 0.00 with a global library, −0.10 in E-82's rule; shortest host at T `[.>}]!` in 40/40; RQ 0.0004; d3 0 in 40/40 | pre-reg. (J-102) |
| E-84 | BFF-XF (fixed 64 bytes) | Lock cost: a lock costs ≈ 0 against a plain copier | Parasite advantage: with one partner slot per pair a parasite copies at most as often as its host | Parasite vs host −5.0 in log ratio at 50 epochs (8/8); refusing earns kin +0.01 ± 0.12; no refusing host among 39 snapshots | **groundwork, not pre-reg.** (J-103) |
| E-85 | BFF-XM deme64 | Gives parasite advantage, free lock and kin benefit at once | Resident hosts: copy remainders under 32 bytes are parasites with an eight-fold edge; no host population survives | Controls: (1) parasite vs host +4.8 at 25 epochs (8/8); (2) lock cost +0.007 ± 0.12; (3) kin benefit +0.50 ± 0.13 (deme64), +0.03 mixed; **(4) net fails**: a rare resistant host is extinct by epoch 50 (4/4), every host by 100–200 | **groundwork, not pre-reg.** (J-104) |
| E-85 rev. | BFF-XM + tail merge + non-rewriting lock (D-080) | Host debris as parasites; the leaking lock | Same: random code alone supplies short marker-ended parasites; plain hosts collapse within 50–100 epochs | (1) +6.6; (2) +0.10 ± 0.10; (3) +0.27 ± 0.14 (deme64), −0.10 mixed; (4) rare R extinct by 25–50 (4/4), also clumped or in a young soup. A resistant host alone persists to 200 epochs in 2 of 4 (declining) | **groundwork, not pre-reg.; line stopped** (J-105) |

Sources: J-098, J-100, J-102, J-103, J-104, J-105; exports `2026-11-17-e81.json`, `2026-11-18-e82.json`, `2026-11-18-e83.json`, `2026-11-18-e84-groundwork.json`, `2026-11-18-e85-groundwork.json`, `2026-11-19-e85-revision.json`. E-84 and E-85 numbers are means over 4 pilot seeds (1–4), mostly from designed programs, not from soups that arose from random code.

**Synthesis (an interpretation, not a tested result).** In these soups an arms race needs four things at once: (a) parasites that out-replicate their hosts, (b) resistance that is cheap, (c) a resident host population that persists, and (d) room in the host for a lock. They pull against each other:
- In a length economy, being short is the parasite's edge (a). It also makes the 6-byte copier the floor, leaving no room for a 4-byte check (d) (E-83).
- Removing the length economy makes the lock free (b) but takes away the parasite's edge (a) (E-84).
- Making hosts long relative to parasites restores (a), (b) and the kin benefit, but the same length ratio that gives parasites their edge destroys the hosts (c) (E-85). An exploratory sweep found hand hosts persist only when the minimum body is about 12 bytes or less (J-104), where a 5-byte check is again a large share of the host.

A disagreement with the E-85 design premise ("long copier, short lock") is recorded in `docs/reviews.md` (notes of 18 and 19 November). The project's recommendation, not a result: pause the BFF-variant thread; the next informative step is a substrate where checking a partner is cheap relative to copying, or this review.

## 5. Claims most worth checking

Ranked by importance × our uncertainty. Commands run from the repository root with the venv active; see section 8 for the `PYTHONPATH` pitfall. Runtimes are the recorded ones on 11 worker processes of one laptop.

**1. The synthesis that the four arms-race conditions conflict in these soups (section 4).**
- *Why it matters:* it is the main conclusion of the last week and our reason to pause the line.
- *What would overturn it:* a simple BFF-like rule, or a parameter we did not try (deme size, XMIN between 12 and 32, mutation, soup size), where hosts persist alongside winning parasites and a cheap lock exists. Or a known published system that does this from random code.
- *How to check:* read J-103 to J-105 and the controls in `scripts/bffxm_assay.py`. Re-run `PYTHONPATH=.:scripts python scripts/e85_groundwork.py --controls --workers 11` (revised rule; outputs to `runs/e85/v2`) and `python scripts/e85_net_variants.py`. Each race takes seconds (`sec` ≈ 3 per row in the export); total wall time was not recorded, we expect minutes. The XMIN sweep: `scripts/e85_xsweep.py`.
- *Our uncertainty:* high. Not pre-registered, 4 seeds, designed programs, one deme size, designed after seeing failures.

**2. Level 5 is not shown in standard BFF (E-48 to E-54, E-78, E-80).**
- *Why it matters:* it is the project's main negative.
- *What would overturn it:* a fitness assay we did not run (for example a lineage-based or in-soup measure, or Bedau–Packard activity against a neutral shadow) that shows directional change; or evidence that our assays cannot see the kind of change BFF makes.
- *How to check:* `scripts/bff_long_analysis.py --workers 11` reruns E-54 from snapshots (22 min; but snapshots in `runs/e54/` are not committed and take ~14 h to regenerate with `scripts/bff_long.py`). E-80 Part B: `scripts/e80b_run.py --confirm --workers 11` (8 h 26 min).
- *Our uncertainty:* moderate. Only 7 standard soups; well-mixed assays; the precise lattice test is in the h = 64 variant, not standard BFF; no open-endedness statistics computed.

**3. The race score as a fitness measure (E-81) and δ\* = 0.79.**
- *Why it matters:* P1–P3 rest on it, and E-82/E-83's gate races use the same idea.
- *What would overturn it:* evidence that 8-epoch races in random code rank programs differently from long-run outcomes in the soup itself, or that saturation (scores reach ±11 beyond about 16 epochs) or the random-code background biases the comparison.
- *How to check:* the ladder and controls in `scripts/bffvl_assay.py` (in `pytest` as `test_bffvl_controls`); `docs/data/e81-preregistration.md`; J-097 ("Instruments"). Recompute P1–P3 from `per_soup[].d1..d3` in `2026-11-17-e81.json` (seconds).
- *Our uncertainty:* moderate.

**4. The 10-byte "shortest refusing host" (E-83).**
- *Why it matters:* the E-83 explanation (length floor, not missing kin benefit) depends on it.
- *What would overturn it:* a refusing self-copier under 10 bytes. Our search was exhaustive only over a copy loop plus up to 5 bytes from 15 values (paper Appendix A, A219), not over all programs.
- *How to check:* `PYTHONPATH=.:scripts python scripts/e83_groundwork.py --search`; export `2026-11-18-e83-groundwork.json` → `shortest_resistant_host`. Runtime not recorded.
- *Our uncertainty:* moderate. A wider search, or a different notion of "refuse", could find a shorter lock.

**5. Heredity at level 4 (E-42).**
- *Why it matters:* it is our highest evidence level.
- *What would overturn it:* if "carried by at least half of the family after 96 epochs alone" mostly measures that a copier copies its own bytes, not heredity in a sense an evolutionary biologist would accept; or if the 9 replicators are 4–5 mirror species, so the effective n is smaller.
- *How to check:* `python scripts/bff_heredity.py --workers 9 --out <file>` (a few minutes; J-042); criteria in D-041. Note that E-42 is a verdict count, not a significance test, so it is outside the Holm family.
- *Our uncertainty:* low to moderate on the measurement; moderate on whether it deserves the label "level 4".

**6. The time-shift statistic and parasite detector (E-82, E-83).**
- *Why it matters:* the sharp P2/P3 fails rest on them.
- *What would overturn it:* a form of resistance coverage cannot see (for example partial or delayed refusal), or parasites the detector misses (host-specific ones; none was seen).
- *How to check:* `scripts/bffx_assay.py` and `scripts/bffxr_assay.py` controls (16 + 12, in `pytest`); recompute RQ from `scores[].RQ` in the E-82 and E-83 exports. Full reruns: `scripts/e82_run.py --confirm --workers 11` (1 h 19 min), `scripts/e83_run.py --confirm --workers 11` (1 h 38 min).
- *Our uncertainty:* low for "no resistance in these soups" (mean coverage 0.998 and 0.9998); moderate for whether these instruments would see subtler host–parasite change.

**7. E-84's argument that a fixed-length parasite can never beat its host.**
- *Why it matters:* it is one leg of the synthesis.
- *What would overturn it:* a fixed-length rule with several partner slots per run, or a binding step budget, where parasites win (J-103 names both as untested).
- *How to check:* J-103 ("Why (a) fails"); `scripts/e84_groundwork.py --compete --seeds 1-4 --workers 2`. Runtime not recorded.
- *Our uncertainty:* low for this rule (an analytic argument plus 8/8 races); the generalisation is untested.

**8. E-81's "directional selection, not level 5".**
- *Why it matters:* it is our only positive post-emergence result.
- *What would overturn it:* evidence that P2 reflects something besides shortening, or that the soups keep changing after T + 20,000 on a measure other than races.
- *How to check:* `scripts/e81_run.py --confirm --workers 11` (3 h 36 min). Length secondaries in `2026-11-17-e81.json` → `secondary`.
- *Our uncertainty:* low on the reading; P2's mean (0.55) is below δ\*, and 7 soups carry 74% of its sum (J-098).

**9. The Holm family (E-79).**
- *Why it matters:* it decides which passes we still quote.
- *What would overturn it:* a different but defensible family (for example including predicted-null tests or the criteria) that changes survivors.
- *How to check:* `PYTHONPATH=. python scripts/holm_primaries.py --out /tmp/check.json` (seconds; do not overwrite the committed E-79 export); family in `docs/data/e79-primaries.json`.
- *Our uncertainty:* low on arithmetic (recomputed here, section 9); moderate on the choice of family.

**10. Parasites in BFF-X are "close to built in" (E-82 P1).**
- *Why it matters:* it decides how much P1's 40/40 is worth.
- *What would overturn it:* nothing in our data; the question is whether you agree that P1 is mechanistic, not a capacity of emergent code.
- *How to check:* the D-072 rule and J-099's pilot; the `none` arm (nothing to borrow) shows 0 parasites in 4 of 4 soups (J-100).
- *Our uncertainty:* low.

## 6. Known weaknesses and threats to validity

- **Laptop scale, one soup size per line.** BFF soups of 2^13 to 2^16 programs (2^17 only at 16 bytes); BFF-VL and its descendants at 2^20 bytes only; up to 20,000 rounds after a jump. The whole project ran over about two weeks (5 to 19 November 2026).
- **Departures from published BFF.** BFF-VL and all later variants use halting heads (wrapping heads made copiers overwrite themselves, J-097), an end-marker byte `!`, and the second head starting at the partner. E-81 to E-85 therefore say nothing directly about 64-byte BFF (J-098 "Scope").
- **Rules chosen after pilots.** Deme64 was chosen because more local geometries did not let hosts take over and less local ones gave no kin benefit (J-101). XMIN = 32 and the D-080 revision were designed after seeing failures (J-104, J-105).
- **Groundwork vs confirmation.** E-84 and E-85 are on 4 pilot seeds, mostly with designed programs. Their "fails" are failures of decisive controls, not of pre-registered tests.
- **Detector thresholds.** Several were set after seeing data (quasi-static cut-off, birth doubling rule, inheritance depth, tile thresholds; paper §8). The BFF-VL replicator detector is validated for 6–48-byte copiers only; the BFF-XM host detector for 32–48 bytes.
- **Instruments calibrated with large positives.** The E-80 positive is a copier against a copier that dies; the E-82/E-83 graded control is 1 in 5 hosts fully resistant. Small advantages would be missed.
- **Well-mixed fitness assays.** Advantages that exist only in space, or need the soup's own neighbours, are invisible to most of our instruments (E-78; partly addressed by E-80).
- **Rule as the unit.** With rules as the unit, the Lenia contrasts and most F-predictor tests do not survive Holm (J-092).
- **Agent-written code, one coordinator.** AI agents (Claude) designed, ran and wrote up most of the work; one coordinating session reviewed it. Five earlier reviews were all by AI systems (R-1 to R-5). No human domain expert has reviewed the work, and the literature review (J-091) was done by AI agents, is not exhaustive, and was not checked by an expert.
- **Logged disagreements.** `docs/reviews.md` records: our push-back on Fredkin's rule as a positive control (R-2); our preference for a same-rule null over block surrogates (R-3); five departures of the E-80 design from the intent it was given (17 November); and the disagreement with the E-85 premise (18 and 19 November).
- **Unresolved items the journal flags.** Open-endedness statistics not computed; no matched Flow-Lenia test; the Lenia quasi-static cut-off has no clean gap (C-02); the reason SUBLEQ soups beat fresh pairs under one jump condition is open (E-76); R-5 points 4, 5 and 7 open; E-81's noexec length null defined in only 14 of 40 soups.

## 7. Questions for you

1. **Is there a known substrate or result that gets past the wall in section 4?** That is, persistent hosts, parasites that win, and resistance cheap enough to spread, all arising from random code under fixed rules. Is Tierra's protected memory plus slicer the minimal ingredient we are missing, or is it the ancestor?
2. **Is the race score a reasonable fitness measure?** Short head-to-head races in random code, log byte ratio after 8 epochs. Would you trust it to rank soup code over time, or would you use something else (invasion from rare in the soup itself, lineage survival, or Bedau–Packard activity against a neutral shadow)?
3. **Are our δ\* choices sensible?** We set δ\* to half a built-in control effect and fail a primary when its whole interval lies below δ\*. Is "half a large designed effect" too lenient for level-5 questions?
4. **Does E-42 deserve "level 4"?** Inherited one-byte mutations in 9 emergent replicators, with no test that variants differ in fitness.
5. **Is the E-81 result interesting to the field,** or is "shortening then stasis" in a variable-length BFF fully expected from Squirm3 and Tierra?
6. **Which open-endedness statistic would you compute first** on our saved soups, and against what null?
7. **Is the synthesis (four conditions that conflict) a known result** in host–parasite models with length-dependent replication, and if so, where?
8. **Would you change the evidence ladder?** In particular, is "directional selection after emergence" worth a named step between 4 and 5?

## 8. Reproducing

**Environment.**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
```
The C interpreters compile on first use into `~/.cache/emergence-lab`. NumPy and SciPy only; no GPU.

**The editable-install pitfall.** The `emergence` console script and imports through the editable install load the package of the checkout where `pip install -e` ran. In a second checkout or git worktree, run from that checkout with `PYTHONPATH=.`:
```bash
PYTHONPATH=. .venv/bin/python -m pytest -q                       # 96 tests (J-105)
PYTHONPATH=. .venv/bin/python -m emergence benchmark --probes    # 39/39 and 222/222 (J-105)
```
(`.venv/bin/python` is the venv's interpreter, wherever it lives.) The scripts for E-81 onward also need `scripts` on the path: `PYTHONPATH=.:scripts`.

**Main entry points.**
- BFF soups: `scripts/bff_soups.py` (E-40, E-41), `scripts/bff_heredity.py` (E-42), `scripts/bff_long.py` and `bff_long_analysis.py` (E-54), `scripts/bff_parasites.py` (E-66).
- Lattice: `scripts/e78_run.py`, `scripts/e80_run.py`, `scripts/e80b_run.py`.
- Variants: `scripts/e81_run.py`, `e82_run.py`, `e83_run.py` (each with `--pilot` and `--confirm`); groundwork drivers `e84_groundwork.py`, `e85_groundwork.py`, `e85_net_variants.py`.
- Holm: `scripts/holm_primaries.py` with `--out <new file>`; the default output is the E-79 export and must not be overwritten.
- Exact commands and code commits for every experiment: [Experiments]({{ '/experiments.html' | relative_url }}).

**Where data lives.** Compact exports: `docs/data/experiments/` (one JSON per experiment; Holm exports `*-holm<m>.json`). Pre-registrations: `docs/data/e*-preregistration.md`. Soup caches and snapshots under `runs/` are not committed (for example `runs/e81/run/`, `runs/e82/run/`, `runs/e83/run/`, `runs/e85/v2/`); they regenerate from the commands. Same command, commit and seed give the same soups.

## 9. Where sources disagree, and what we recomputed

**Recomputed from the exports for this pack (all matched unless noted):**
- Holm across 51 p values, from `p_raw` in `2026-11-18-e83-holm51.json`: every adjusted value matches; 22 passes, 20 survive; E-50 0.396, E-71/P2 0.175.
- E-81 P1, P2, P3 (mean, SD, t interval, count positive) from `per_soup[].d1..d3` in `2026-11-17-e81.json`: 9.12 (8.65–9.60) 40/40; 0.547 (0.19–0.90) 30/40; −0.025 (−0.078 to 0.028) 17/40. Jump epochs 50 to 9,050, median 1,425; final copiers `[.>}]!` 24, `[.}>]!` 16.
- E-82 RQ from `scores[].RQ`: 0.0011 (−0.0004 to 0.0027), 6 positive, 2 negative, 32 zero; T 250 to 3,050, median 950.
- E-83 RQ: 0.0004 (−0.0002 to 0.001), 2 positive, 38 zero; T 1,850 to 9,200, median 5,100; soup 8417 without a jump.
- E-80 Part B and E-78 primaries from per-soup d: −0.047 (−0.114 to 0.020); −0.42 (−1.10 to 0.25).
- E-85 controls: groundwork (1) +4.78, (2) +0.007, (3) +0.496, (4) ln(R/H) at 25 −0.29 from the raw `net` rows; revision (1) +6.56, (2) +0.105, (3) +0.27 (mixed −0.10), (4) −3.26.
- E-54 D −0.153, p 0.64; E-66 self-copier share 0.998; E-42 9 of 9 "heredity".

**Disagreements and untraceable numbers:**
1. **Benchmark size.** `index.md` says 170/170, `research.md` (O1) and `paper.md` §1 say 170, `paper.md` Appendix A row A1 says 225 (39 + 186), and the handoff and J-105 say 39 + 222. J-105 is the latest run; the other pages are stale.
2. **E-81 copier length at T + 20,000.** J-098, the experiments row and paper A204 give "median 6.17 bytes". From `per_soup[].len_late2` the median is 6.19 and the mean is 6.165; 6.17 matches the mean. (At T + 10,000 the median and mean are both 6.19.)
3. **E-85 revision, sham extinction.** J-105 says the sham "is extinct by 140–160"; D-080's status says "by 100–140". The export (`alone` trajectories, sampled every 20 epochs) has zero bytes from epoch 140 in 1 seed and 160 in 3, which matches J-105.
4. **E-85 groundwork export summary.** In `2026-11-18-e85-groundwork.json`, the `controls_summary` entries for control (4) (`c4_net …`) are all zeros, while the raw `net` rows give ln(R/H) at 25 epochs of −0.29 (−0.86 to +0.26), as J-104 reports. The summary appears to aggregate under a key that does not match the rows' labels (`c4_net_age10`). J-104's "R's bytes fall by −1.3 in log by 10 epochs" matches the smallest drop among the 4 seeds (−1.29); their mean is −1.54.
5. **"R alone holds the soup to 200 epochs in 2 of 4"** (handoff, D-080). The export shows R's bytes falling steadily in all 4 seeds, from 0.58–0.65 MB at epoch 20 to 0.18–0.19 MB at 200 in the 2 best seeds (about 18% of the 2^20-byte budget). "Persists, declining" is more accurate than "holds".
6. **Holm-adjusted values depend on family size.** E-81 P1/P2 are 1.7 × 10⁻⁴ among 47 (J-098, paper) and 1.9 × 10⁻⁴ among 51 (latest export); E-50 is 0.30 among 42 and 0.40 among 51. Not a conflict, but pages quote different family sizes.
7. **The report** (`docs/report.md`) ends at E-78 (section 36) and does not cover E-79 to E-85.

## Read more

- [Paper]({{ '/paper.html' | relative_url }}): the full synthesis with a claims table (Appendix A) and pre-registration tally (Appendix B).
- [Literature]({{ '/literature.html' | relative_url }}): claim-by-claim comparison with published work (by AI agents; no expert check).
- [Handoff]({{ '/handoff.html' | relative_url }}): current state, pitfalls and open problems.
