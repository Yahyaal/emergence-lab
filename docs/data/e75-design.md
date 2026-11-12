# E-75 design: does the F predictor carry over to a language outside the BFF family?

Status: **phase 0 done** (J-077; D-054, D-055). Phases 1–3 not started. Not yet a pre-registration: the confirmatory test (phase 3) is pre-registered only
after phases 0–2, with whatever they show disclosed.

## Why

Across E-55–E-74 one result replicated every time. Rules whose shortest copier makes a copy that itself copies
("F") make replicators within a few thousand rounds, and other rules mostly do not: 60/60 vs 15/60 in E-70,
143/144 in E-74. Every test so far changed one detail of BFF: where the heads start, the tape length, or what one
instruction does. The open question is whether the predictor is about BFF or about program soups in general.

## Choice of language: a SUBLEQ family (D-054)

| Option | For | Against |
|---|---|---|
| **SUBLEQ family (chosen)** | Structurally unlike BFF. There are no heads, only a program counter. Every byte is an operand: there are no no-ops, so random code is dense, where BFF's is ~96% inert. Copying needs arithmetic and self-modification. It has an external anchor: Agüera y Arcas et al. (2024) report **no spontaneous replicators** in SUBLEQ (shortest hand-written replicator ~60 bytes) or in their RSUBLEQ4 (25 bytes), but take-over when seeded. | Plain SUBLEQ alone gives one data point. A family is needed, so some rules are built by us. |
| Forth-like stack language | Replicators reportedly emerge fast | Copy loops read/write much like BFF heads; a weaker test of generality |
| Z80 / 8080 | Real CPUs | Huge instruction sets make an exhaustive or near-exhaustive census impractical |

**The family (as built in phase 0, `emergence/programs/subleq.c`; revised from the first draft, see below).**
The memory is the pair's tape, A followed by B: 128 bytes, with addresses taken mod 128. Values are signed for
the jump condition. A program counter `pc` and a hidden index register `r` start at 0. Six knobs:
- **n** ∈ {3, 4} operands:
  - n = 3: `t[pc+a%W+o+r] -= t[pc+b%W+r]`, jump target `pc + (int8)c`;
  - n = 4: `t[pc+a%W+o+r] = t[pc+b%W+r] - t[pc+c%W]`, jump target `pc + (int8)d`.
- **j**: jump if the written value is ≤ 0, < 0, = 0, or always.
- **s** ∈ {0, +1, +2, −1}: added to `r` after every instruction. With s = 0 the language is plain relative
  SUBLEQ / RSUBLEQ4; with s ≠ 0 a loop of one instruction walks across the tape (the analogue of E-70's "`.` then
  heads +1").
- **W** ∈ {128, 64, 32, 16, 8}: the operand window. With W = 128 any address is reachable and o is redundant.
  With narrow windows the partner is reachable only through o, which gives a band of o near 64, as BFF's head1
  band.
- **o** ∈ 0–127: the write offset.
- **absolute** addressing (anchor only).

Execution stops after 8,192 steps, or when an instruction would read past either end of the tape.
**Anchors:** `SUBLEQ` (n = 3, ≤ 0, absolute; data addresses wrap mod 128) and `RSUBLEQ4` (n = 4, ≤ 0, s = 0,
W = 128), our reading of the paper's two languages.

**Changes from the first draft, made while building and before any census:**
1. "never jump" was replaced by "always jump", because with "never" no loop is possible.
2. The step register touches only the a and b addresses, not c, so that c can name a fixed zero cell. Earlier the
   step modified the operand bytes themselves, and then no exact copy of the program is possible: its operand
   bytes change before they are copied.
3. The window W was added, because with full-width operands o has no effect.

The rule space is now 2 × 4 × 4 × (1 + 4 × 128) = 16,416 rules, so phase 1 will census a random sample of rules
(size fixed in the phase-1 commit).

## Phases and gates

**Phase 0: build and validate (no soups beyond controls).**
- **Interpreter:** C kernel plus a pure-Python reference; pytest checks they agree on random tapes for every knob
  setting.
- **Soup framework:** reuse BFF's pairing, mutation, top-40 selection and HOE.
- **Replicator test (language-agnostic, D-055): inheritance.** Built after the first draft's whole-program copy
  test (≥ 58/64 bytes plus a functional guard) failed on the first emergent replicator (see J-077). A program is
  a replicator if a block of ≥ 4 of its bytes is still present after **5 generations** of copies, each into a
  fresh random partner, in ≥ 3 of 4 lineages, **and** the block vanishes when it is randomised in the program
  (so it is inherited, not written from scratch). Depth and block length were set by a sweep: 3 generations let
  E-71's v1/68 near-replicators through (7/40); blocks of 6+ bytes miss the 5-byte emergent loop.
  - Cross-check on the E-73 BFF fixtures: it agrees with D-053 on the positives (39–40/40) and nulls (0/40), and
    rejects the 64 filler smears.
- **Controls, in pytest and `emergence benchmark --probes`:**
  - positive: hand-written replicators for three rules (forward, backward, band), each seeded into a soup, take over; and the unseeded emergent loop (fixture). A hand-written RSUBLEQ4 replicator was not built (the paper reports 25 bytes; ours would need self-modifying copy loops); deferred, not needed for the gate;
  - negative: `noexec` soups;
  - deceptive: `copyall` soups (everything "replicates" with no code);
  - null: top-40 of the two anchor soups at round 300; 200 random programs under 4 rules. HOE: noexec 0.0, copy-all 7.3, emergent loop 6.9;
- **Gate:** all controls pass.

**Phase 1: census of a random sample of the 16,416 rules (size fixed in the phase-1 commit) plus the two anchors.**
- Exhaustive enumeration as in BFF is impossible: one 4-operand instruction has 128^4 settings.
- Instead, for each rule, sample 10^6 kernels of 1–2 instructions (operands uniform in 0–127), each embedded at a
  random position in a random 64-byte program. Count copiers and **self-sufficient** copiers (3 of 4 single
  copies copy again, as E-61).
- **F** = at least one self-sufficient kernel in the sample. **non-F** = copiers found, none self-sufficient.
- Pilot first on ~20 rules to fix the sample size, so that repeat censuses of a rule agree on F/non-F
  (seed-to-seed stability ≥ 95%).
- **Anchor prediction** (to be stated in the phase-1 commit, before running): SUBLEQ and RSUBLEQ4 are non-F, in
  line with the paper's no-emergence result.
- **Gate:** ≥ 16 F and ≥ 16 non-F rules. Otherwise the family is redesigned and the census disclosed.

**Phase 2: pilot soups (exploratory, disclosed).**
- 4 F and 4 non-F rules, 2 soups each: 2^14 programs of 64 bytes, up to 16,000 rounds, checkpoints every 50.
- Purpose: confirm that something can emerge and calibrate run length.
- **Gate:** at least one F soup makes replicators. If none does, that is reported as a result (F does not carry
  over at this scale, or the census is not measuring the right thing) and phase 3 is redesigned or dropped.
  Pilot rules are excluded from phase 3.

**Phase 3: confirmatory (pre-registered after phases 0–2).**
- Up to 12 fresh F and 12 fresh non-F rules, 6 soups each (144 soups, the E-74 budget: ~2–4 h).
- **Primary, as E-70 P2:** F soups ≥ 75% jump; non-F ≤ 25%; one-sided Fisher p < 0.01.
- Jump = inheritance test (D-055) among the 40 most common programs; the whole-program test and HOE are reported beside it (D-052). HOE is fooled by copy-all soups here (7.3) and stays low in seeded take-overs with filler (about 1), so it is not a primary measure in this language. The prediction is set in the
  pre-registration, with phases 1–2 disclosed.
- Secondary: anchors run as soups (4 each); the self-sufficient count vs speed (exploratory only, given E-71–E-74).

## Cost estimate

- Phase 0: ~half a day of code and tests.
- Phase 1: ~2 × 10^9 short runs, an hour or a few on 11 cores (the pilot fixes it).
- Phase 2: ~16 soups, ≤ 2 h.
- Phase 3: 2–4 h.

## Risks

- **Dense code may make soups chaotic.** Every pair of random programs writes everywhere, so copies may be
  overwritten before they spread. That is a real property of the language, and the pilot exposes it.
- **The sampled census can miss rare F kernels.** Its false-negative rate is measured with the hand-written
  replicators' kernels: a census must find them.
- **The s knob is our design.** The fixed rule must not reward copying, and it doesn't: it moves operands whatever
  they point at, as BFF heads move whatever they read. Rules with s = 0 keep the family honest.
