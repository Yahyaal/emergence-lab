# E-57 pre-registration (written before running)

**Origin:** in E-56 all 4 counterfactual soups (head1 starts at byte 64; 2^16 programs) jumped within 250–1,000
rounds. Standard 2^16 soups: about half jump within 24,000 rounds (E-50, E-54), first jumps at ~750–22,000.
E-56 had n = 4 and its jump count was descriptive. Two questions:

1. Is the faster jump real (confirmation at another soup size)?
2. A candidate mechanism, written down now: a **forward** copier makes an exact copy of itself, so any forward
   copier is a replicator. A **backward** copier makes its mirror image, and the mirror carries the copy loop
   reversed (`[{.>]` becomes `]>.{[`, not a loop), so a backward copier only replicates if the program also
   contains a working copier in the other direction: a mirror replicator needs two kernels, about twice the
   instructions. That would make replicators much rarer under the standard rule even though copiers are only
   ~2.5× rarer (E-55: 55 vs 139).

**Part A (soups, `scripts/bff_mirror.py --part soups`):** 8 counterfactual soups of 2^14 programs (seeds
5700–5707), the E-56 interpreter and settings otherwise (64-byte programs, 8192 steps, mutation 0.00024),
up to 16,000 rounds; jump = D-045 HOE criterion (≥ 1.0 at 3 consecutive checkpoints every 250 rounds);
a jumped soup runs to T + 1,000 and its 40 most common distinct programs are classified as in E-56.
Reference (standard rule, same size, same horizon): E-40, **0 of 12** soups jumped by 16,000 rounds
(1 of 16 with the pilots). Check made before E-57: the counterfactual interpreter with head1 at 0 reproduces
the standard soup bit for bit (4096 programs, 300 rounds).
**Primary A:** at least 6 of 8 counterfactual soups jump by 16,000 rounds (and one-sided Fisher vs 0/12,
p < 0.01). Secondary: in every jumped soup ≥ 90% of classified copiers are forward (E-56's result).

**Part B (mechanism, `--part census`):** every copier kernel of 5–6 instructions from E-55's census (rebuilt
with fresh non-zero non-instruction filler, re-confirmed with 4 partners), under its own rule. A copier is
**self-sufficient** if, in at least 3 of 4 runs with random partners, the copy it leaves in the partner half is
itself a copier (any orientation, 4 partners) under the same rule.
**Primary B:** standard rule ≤ 5% of copier kernels self-sufficient; counterfactual ≥ 90%.
**Descriptive:** programs made of two standard kernels, K1 at the start and K2 reversed at the end
(all ordered pairs of the standard copier kernels): how many are self-sufficient (mirror replicators of ~10–12
instructions)?
**Controls:** hand-written replicator (forward, self-sufficient expected), the 9 E-42 emergent replicators
(standard, self-sufficient expected: they are mirror replicators), 1000 random programs (none), the constant
writer `[{.]` (deceptive: writes into its partner; not a copier, not self-sufficient).

**Limits:** Part A compares with a reference run in another session (different seeds; same code path, shown
equal). Part B shows what short programs can do; it does not trace the soups' actual path. If both pass, the
mechanism is supported, not proven: the counterfactual also changes everything else a program can do.
