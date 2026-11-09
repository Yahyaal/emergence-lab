# E-62 pre-registration (written before running)

**Origin:** E-61 (J-062): with a shift-aware classifier, rules h = 61–68 have a short copier whose one copy can
copy (F′), but soups in the new rules 61, 66, 67, 68 made real replicator soups (≥ 10 copiers among 40 at
T + 1,000) in only 7 of 16, against 11 of 12 in E-60's 62, 63, 65; and every real takeover was by **exact**
copiers. A copier at shift d makes children shifted by d, grandchildren by 2d, so its line loses the kernel.
Hypothesis: what predicts fast replicators is a short copier whose **lineage persists**, not one copy.

**Tool (`scripts/bff_lineage.py`):** for a copier x under rule h, follow one line for 64 generations (each
generation = the partner half after running the parent with a fresh random partner). The line **persists** if the
descendant still copies itself every 16 generations and at the end: its product matches it at some shift
|d| ≤ 16, on all but 4 bytes of the overlap, in ≥ 3 of 4 runs (the parent's own half may be damaged). Controls,
checked before registering: hand-written replicator (h = 0) persists; `[.>}]` at h = 64 persists; `[.>}]` at
h = 66 (shift 2) does not; 0 of 100 random programs (h = 0, 64).

**Part A (census):** all h in 0..127; copiers as E-61 (kernels of 5–6 instructions, `classify_shift`, screen 1 /
confirm 4); rule class **P** if at least one copier's line persists, else **N**.
**Primary 1:** P = {62, 63, 64, 65} exactly (prediction: only rules with an exact short copier).

**Part B (fresh soups, seeds 6200 + 10·rank + i):** 4 soups of 2^14 for each rule of E-61's F′ (61–68) except
64, split into group P (in P) and group N (not in P) by Part A's result. **Strict jump criterion (D-047):**
candidate T as D-046 with the shift-aware copier check; confirmed only if ≥ 10 of the 40 most common programs
are copiers at T + 1,000; otherwise the candidate is dropped and the soup runs on, up to 16,000 rounds.
**Primary 2:** group P ≥ 75% jumps and more than group N, one-sided Fisher p < 0.05. If a group is empty: undecided.

**Secondary (descriptive):** survival generations by shift; dropped candidates per group; copier shift at the end
of real jumps (prediction: 0).

**Limits:** one line per copier (lines are stochastic through partners); 64 generations; 4 soups per rule; one
family of rule variants.
