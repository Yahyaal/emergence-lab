# E-59 pre-registration (written before running)

**Origin:** E-58's conclusion (a rule with backward copiers, head1 = 127, is slow; head1 = 64, forward copiers, is
fast) rests on a corrected reading after the pre-registered jump criterion misfired (J-058, D-046). This is the
confirmation, with the corrected criterion fixed in advance.

**Run (`scripts/bff_orient_confirm.py`):** new seeds. 16 soups of 2^14 under head1 = 127 (seeds 5900–5915) and
8 under head1 = 64 (seeds 5920–5927); interpreter `epoch_h` (`scripts/bff_kernels.c`), E-57 settings otherwise,
up to 16,000 rounds. **Jump (D-046):** HOE ≥ 1.0 at 3 consecutive checkpoints (every 250 rounds) **and** at least
one copier, under the soup's own interpreter, among the 40 most common distinct programs at that checkpoint
(E-55 classifier, 4 partners). T = the first checkpoint of the run. If HOE holds but there is no copier, the soup
keeps running (checked again at each later checkpoint while HOE stays ≥ 1.0). A jumped soup runs to T + 1,000;
its 40 most common programs are classified again there.

**Primary:** head1 = 127 jumps in at most 4 of 16 soups, head1 = 64 in at least 7 of 8, and the difference is
significant (one-sided Fisher p < 0.01).
**Secondary:** copiers at T + 1,000 are ≥ 90% backward in every head1 = 127 jump and ≥ 90% forward in every
head1 = 64 jump. Steps per pair at T + 1,000 above 3,000 in every jumped soup (descriptive check of D-046).

**Limits:** one size (2^14); the two rules still differ in more than orientation.
