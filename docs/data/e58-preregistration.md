# E-58 pre-registration (written before running)

**Origin:** E-56/E-57: with head1 starting at byte 64, soups jump within 250–1,750 rounds (12 of 12), against
0 of 12 by 16,000 rounds under the standard rule (2^14). Two explanations:
- **(M) mirror requirement:** under the standard rule every short copier copies backwards, a backward copier's copy
  cannot copy, and the smallest replicator needs two kernels (10 instructions vs 5). Orientation is what matters.
- **(P) any perturbation:** the standard rule happens to be slow; many other head-start rules would be fast,
  for reasons unrelated to orientation (e.g. more copiers of any kind).

**Matched control rule:** head1 starts at byte **127** (the partner's last byte). Pilot seen before writing this
(k = 5 kernels only, 4 partners): 6 shortest copiers, **all backward** (`[.>{]`, `[<},]`, ...), the same number
as the 6 forward ones at head1 = 64; the standard rule has 2. So head1 = 127 has as many shortest copiers as the
fast rule, but backward. (M) predicts it is slow; (P) gives no reason for it to be slow.

**Part A (soups, `scripts/bff_h127.py --part soups`):** 8 soups of 2^14 programs (seeds 5800–5807) under the
head1 = 127 interpreter (`epoch_h` in `scripts/bff_kernels.c`), otherwise E-57's settings: up to 16,000 rounds,
D-045 jump criterion, jumped soups run to T + 1,000 and the 40 most common distinct programs classified under the
same interpreter.
**Primary A:** at most 2 of 8 soups jump by 16,000 rounds, and the count is lower than E-57's 8 of 8 with
one-sided Fisher p < 0.01 (≤ 2 of 8 gives p ≤ 0.004). Secondary: any jumped soup's copiers are ≥ 90% reverse.

**Part B (census, `--part census`):** all kernels of 5–6 instructions with non-zero non-instruction filler (as E-55)
under head1 = 127; copiers confirmed with 4 partners; self-sufficiency as E-57 (copy is itself a copier in ≥ 3 of 4
runs).
**Primary B:** copiers ≥ 90% reverse and at most 5% self-sufficient. Descriptive: number of copiers vs the other two rules.

**Interpretation plan:** A and B pass → (M) supported over (P): orientation, not perturbation, sets the speed.
A fails (fast jumps) → (P) or another mechanism; (M) weakened.

**Limits:** one control rule; n = 8; head1 = 127 still differs from the standard rule in other ways.
