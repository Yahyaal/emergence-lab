# E-75 design: does the F predictor carry over to a language outside the BFF family?

Status: **design** (D-054). Not yet a pre-registration: the confirmatory test (phase 3) is pre-registered only
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

**The family.** The memory is the pair's tape, A followed by B: 128 bytes, with addresses taken mod 128 and
signed bytes. One instruction type is executed from the program counter, with operands read relative to it. Four
knobs:
- **n** ∈ {3, 4} operands:
  - n = 3: `*(pc+a) -= *(pc+b)` (as SUBLEQ, relative);
  - n = 4: `*(pc+a+o) = *(pc+b) - *(pc+c)` (as RSUBLEQ4).
- **o** ∈ 0–127: an offset added to the write address (for n = 3, to `a` of the write). This is the analogue of
  BFF's head1 start, and it moves where writes land.
- **s** ∈ {0, 1}: after executing, the machine adds s to the instruction's own `a` and `b` bytes. This is the
  analogue of E-70's "`.` then heads +1": a loop of one instruction can walk across the tape.
- **j** ∈ {≤ 0, < 0, = 0, never}: the jump condition on the written value. "never" means always fall through to
  pc + n.

That gives 2 × 128 × 2 × 4 = 2,048 rules. Execution stops at a step limit (2^13, as BFF) or when pc leaves the
tape. The paper's SUBLEQ is n = 3, o = 0, s = 0, j = ≤ 0 with absolute addressing; we include it and RSUBLEQ4 as
two extra **anchor rules**. Their semantics need checking against the paper's PDF before phase 1: the HTML text
is garbled in places.

## Phases and gates

**Phase 0: build and validate (no soups beyond controls).**
- **Interpreter:** C kernel plus a pure-Python reference; pytest checks they agree on random tapes for every knob
  setting.
- **Soup framework:** reuse BFF's pairing, mutation, top-40 selection and HOE.
- **Copy test (language-agnostic, D-055 proposed):** a program is a copier if, run with random partners, the
  partner matches it in ≥ 58/64 bytes (shift-aware), **and** that copy, run with a fresh random partner, copies
  again (a *functional* guard, replacing D-053's instruction-byte guard, which does not transfer to a language
  without no-ops).
  - Cross-check on the E-73 BFF fixtures: it must agree with D-053 on the positives and nulls, and reject the 64
    filler smears.
- **Controls, in pytest and `emergence benchmark --probes`:**
  - positive: a hand-written replicator for one F rule, seeded into a soup, takes over; and one for RSUBLEQ4;
  - negative: `noexec` soups;
  - deceptive: `copyall` soups (everything "replicates" with no code);
  - null: top-40 of random soups. HOE's threshold is recalibrated on these: dense code may change its baseline.
- **Gate:** all controls pass.

**Phase 1: census of all 2,048 rules plus the two anchors.**
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
- Jump = functional copy test; HOE timing reported beside it (D-052). The prediction is set in the
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
