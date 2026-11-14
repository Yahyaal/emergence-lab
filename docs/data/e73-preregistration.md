# E-73 pre-registration (written before re-scoring; part A seen, disclosed)

**Origin:** E-72 (J-074) found soups scored "no jump" by D-050 that were full of sloppy replicators (copies of
59–60 of 64 bytes; the D-050 copy test needs 60). D-052 asked for a validated looser test before testing speed
predictors again.

**Part A (done, seen): the test and its controls** (`scripts/bff_fidelity.py`, fixtures from replayed soups in
`scripts/fixtures/`, `bff_kernels.classify_fid`). D-053 test = the shift-aware copier test with a match threshold of
**58 of 64** bytes plus an **instruction-fidelity guard**: the copy must reproduce ≥ **75%** of the program's
instruction bytes in the overlap. All controls pass:
- equivalence: threshold 60 without the guard = the old test on every fixture;
- positives: sloppy replicators 38/40 and 40/40 (old test 0/40, 0/40); exact replicators 40/40, 39/40, 40/40;
- negatives / selection-aware nulls: top-40 programs of soups without replicators 0/40 and 0/40; random programs
  ≤ 1/200 per rule. This check was first written as "0 of 200". It failed because one random program contains
  `[ . ]`, a real copier under v1/h1 = 64 (the old test counts it too). It was changed to ≤ 1% after seeing this;
- deceptive: 64 "filler smears" (60 bytes of one value plus a loop that writes it across the partner) × 9 rules:
  0 copiers. The **old test accepts 37 of them**, so the guard also fixes a false positive of D-050 itself.
The sweep shows the same results for any threshold 52–58 with a guard of 50–75%; 58/75 is the strictest choice
that passes.

**Part B: re-score E-70, E-71, E-72** (`scripts/bff_rescore.py`). All 392 soups are replayed from their seeds;
soup trajectories do not depend on detection. At each experiment's own checkpoints (E-70 every 250 rounds,
E-71/E-72 every 50) both tests are applied to the same 40 most common distinct programs with the same seeds. The
jump rule is unchanged (≥ 1 copier, then ≥ 10 at the checkpoint 1,000 rounds later; up to 16,000 rounds).
**Equivalence (must hold, else stop):** the D-050 copier series and T reproduce the stored ones for every soup.
A smoke test on E-71 seed 7120 reproduced T = 150. A second smoke soup (E-72 seed 7220) was still running when
this was written; its result was not seen.

**Predictions under D-053** (re-applying each experiment's pre-registered test unchanged):
1. **E-70 P2** (F ≥ 75% jump, other ≤ 25%, Fisher p < 0.01, F ≥ other in each variant): the other rules were
   exactly at 25% (15/60); sloppy take-overs among them would push it over. Prediction: **fail** (~55%).
2. **E-71 P1** (pooled ρ ≤ −0.4, permutation p < 0.01): ~50%, no prediction of direction beyond chance;
   **P2** (within variant, p < 0.05): **pass** (~80%). v1/68 stays 0/8 (~90%).
3. **E-72 primary** (shallow ≥ 3× slower, Mann–Whitney p < 0.01): the two v2 "0/6" rules should become fast,
   lowering the deep median. Prediction: **fail** (~60%; p stays above 0.01 with 8 vs 8 rules).

**Secondary:** how many soups change verdict or T, by experiment and variant; whether any D-050 jump disappears
under the guard (a filler-smear take-over).

**Decision rule after this:** if D-053 changes any verdict, the D-053 verdict is the one reported, with the D-050
one beside it (D-052). If the two disagree on a speed result, that result is reported as unresolved.

**Limits:** the fixtures come from 9 soups in 7 rules; 58/75 is validated on them, not on every variant; the guard
uses instruction bytes, which a language with different instructions would need redefined.
