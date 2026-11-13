# E-75 phase 5 pre-registration: where do the first replicators come from? (D-060)

Written before the main run. Script: `scripts/sq_nucleation.py`.

**Why:** phase 4b (J-082) showed that soups in this language never "freeze". Every soup starts as inert random
code, and replicators either nucleate out of it or never do. Two predictors in a row worked in one setting and
failed in the next. Neither looked at the event that actually starts a jump. This phase watches that event.

**Method:**
- **Exact replay.** A Python replay of each soup makes the same RNG calls as `subleq.Soup`. It was checked byte
  for byte against the C soup over 30 and 100 rounds.
- **Testing runs.** Every executing program whose run takes ≥ 16 steps gets the inheritance test (D-055). A
  positive is confirmed with a second RNG, and results are cached by content.
- **Lineages.** A partner written to by a replicator inherits its lineage tag. A tagged program that executes as a
  non-replicator becomes a lapsed member, and rejoins its lineage if it turns back into a replicator.
- **Origins.** A replicator executing in an untagged slot is an **origin**: a new lineage. Its **cause** is how the
  slot last changed before that:
  - its own run ("self");
  - another program's run ("partner");
  - "mutation";
  - a combination of these;
  - or "initial", if it never changed.
- **Classes.** A lineage is **null** if the founder's inherited block is all zeros, and **informative** otherwise.
- **Establishment** is the first lineage with ≥ 200 replicator executions in one round. Tracing stops there.
  Soups that never jumped originally are traced for 4,000 rounds; soups that jumped, for up to 16,000.
- **Part B.** If the first lineage to establish is null, a C soup with the same seed is run on. Every 50 rounds,
  its top 40 distinct programs are checked, until ≥ 10 of them are informative inheritors (up to 3,000 rounds).

**Seen before writing this (disclosed):**
- **One soup traced end to end in development** (W32/o28 ≤ 0, seed 78002, original T = 100).
  - A program rewrote itself into the **all-zero program** at round 85–86 ("self").
  - Under jump ≤ 0 or always, the instruction 00 00 00 00 writes 0 and jumps to itself while the index walks, so it
    zeroes its partner, which then does the same. It copies itself but carries no information.
  - It spread, and informative mostly-zero variants (for example 00 d4 00 00 …) arose inside it.
  - A version of the tracer that let lineages switch class established an informative lineage at round 353.
  - That version was too slow (25 min) and split lineages endlessly, so lineages now keep their founder's class.
- **A null check on 7 jumped soups of phases 3 and 4**, at T and T + 1,000:
  - At T + 1,000, every soup had 14–40 informative inheritors among its top 40, so these jump calls stand when null
    replicators are excluded.
  - At T, 3 soups were mostly or entirely null (12 of 13, 5 of 5, 26 of 37), so T can be early.
- **Smoke runs** (`MAX_ROUNDS` = 300) of the two positive controls, one negative control and main soup W32/o28
  seed 78000:
  - **Positive controls.** Both injected replicators were detected at round 1 with cause "initial". In W32/o28
    the injected lineage established at round 17. In W16/o18 the injected copy executed once and was lost, and
    a new lineage ("self") established at round 1,251.
  - **Negative control:** nothing established in 300 rounds.
  - **Main soup:** a null lineage established at round 384, and part B found ≥ 10 informative inheritors at
    round 400, which is the soup's original T.

**Sample:**
- **Main:** soups 0 and 1 of every phase-3 rule (24, jump always) and every phase-4 pool-A rule (24, jump ≤ 0):
  96 soups, with the same seeds as originally.
- **Negative control:** soups 0 and 1 of 2 pool-B LOW rules (jump < 0, D_T = 0, 0/36 soups jumped).
- **Positive control:** soup 2 of W32/o28 and of W16/o18, each with one verified replicator injected into slot 0
  at round 0. The replicator is the top program after the jump in soup 5 of the same rule.

**Predictions** (no single primary verdict; this phase is mainly descriptive):
1. **Controls.**
   - Both positive controls detect the injected replicator at its first execution with cause "initial" (seen in
     the smoke run, so not a prediction; a check). A single injected copy can be lost, as in W16/o18, so
     establishing it is not required.
   - No negative-control soup establishes a lineage in 4,000 rounds (~85%).
2. **The tracer agrees with the original runs.** Of main soups that jumped originally, ≥ 90% establish a lineage.
   Of those that did not, ≤ 10% establish an *informative* one first (~75%).
3. **Null first.** Under jump ≤ 0, the first lineage to establish is null in ≥ 50% of the soups that establish
   (~50%). Under jump always, the same instruction also loops, but phase 3's final top programs were almost never
   zero, so null first there in ≤ 25% (~50%).
4. **Origin rate vs establishment.** Compare rules that jumped in ≥ 4 of 6 original soups with rules that jumped in
   ≤ 1 of 6, per soup:
   - The origin rate (confirmed origins per 1,000 rounds before establishment, or over the 4,000 traced rounds) is
     higher in the frequently jumping rules: one-sided Mann–Whitney p < 0.05 (~55%).
   - The fraction of origins whose lineage reaches ≥ 10 executions in a round is **not** significantly different
     (two-sided p ≥ 0.05) (~45%).
   - Together these say the difference between rules lies mainly in how often replicators arise, not in whether
     they survive.
5. **Cause.** Among founders of the first established lineage, "self" (a program rewritten by its own run) is the
   most common cause (~40%).

**Limits:**
- A partner written to by a replicator is tagged even if the write was partial, so some origins may be counted as
  reproductions.
- The inheritance test is stochastic. Confirmation with two RNGs reduces false origins but does not remove them.
- Runs shorter than 16 steps are not tested. A replicator that copies in fewer steps would be missed (none is
  known; tile replicators loop for ≥ 64 steps).
- Two soups per rule.

## Outcome (added after the run; J-083)

Run time 4.8 h, 11 workers. Analysis: `scripts/sq_nucleation_report.py`.

1. **Controls pass.**
   - Positive: both injected replicators were detected at round 1 with cause "initial", as in the smoke run.
   - Negative: 0 origins in 4,000 rounds in all 4 soups.
2. **The tracer agrees with the original runs. Right.**
   - 40/40 soups that jumped originally establish a lineage. 38 of them do so within 50 rounds of the original T
     (range −152 to +373).
   - 0/56 soups that did not jump establish anything.
3. **Null first:**
   - under ≤ 0, 5 of 16 (31%). **Wrong.**
   - under always, 0 of 24. **Right.**
   - In all 5 null-first soups, informative inheritors reached ≥ 10 within 16–97 rounds (part B).
4. **Origin rate vs establishment:**
   - Origin rate: often-jumping rules have a median of 30 origins per 1,000 rounds, rarely-jumping rules 0;
     p = 3 × 10^-19. **Right.** 53 of the 54 rarely-jumping soups had **no origin at all** in 4,000 rounds, and
     the other had 3 that died out.
   - Establishment fraction: p = 0.10, technically right, but **uninformative**. Only one rarely-jumping soup
     had any origin to compare.
5. **Founder cause:** "partner" 24, "self" 16, and none by mutation alone. **Wrong:** "self" is not the most
   common.

**Also seen:**
- In 25 of 40 soups the first origin of any kind came at ≥ 90% of the establishment round.
- The established lineage was the very first origin in 17 of 40 soups, and it established a median of 16.5 rounds
  after the first origin (≤ 20 rounds in 23 of 40).
- Some rules (W32/o42, W32/o111, W64/o60 under ≤ 0; W16/o4–o7 and W64/o3 under always) make hundreds to thousands of
  short-lived origins before one lineage establishes.
