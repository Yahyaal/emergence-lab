# E-68 pre-registration (written before running)

**Origin:** E-60–E-65 showed, in two start-position families of BFF with 64-byte programs, that rules where a
short copier's single copy copies again (F rules) make replicators fast, and that F rules are those whose two
pointers start about half a tape apart. Every test so far kept the program length at 64 bytes. E-68 changes
the program length L (tape 2L), the first change to the language itself rather than to where pointers start.

**Tool:** `scripts/bff_tapelength.py`. `bff_kernels.set_length(L)` sets L, the copy threshold THR = L − L/16
and the shift window MAXSHIFT = L/4 (60 and 16 at L = 64, the old constants). The C interpreter already took L
as an argument. The step limit stays 8192 and the per-byte mutation rate 0.00024 (as in all earlier soups);
soups have 2^14 programs at every L (so short-L soups hold fewer bytes).

**Equivalence check (must hold, else stop):** the census at L = 64 reproduces E-61 rule by rule (copiers,
self-sufficient copiers, class). Pilot: h = 64 gives 188 / 137 / F, as in E-61.

**Part A (census):** for L in 16, 32, 64, 128 and every head1 start h1 in 0..2L−1 (480 rules), E-61's census
(`bff_shift_census.census_rule`, unchanged: every 5- and 6-instruction kernel, shift-aware classifier,
self-sufficiency = 3 of 4 single copies copy again).
**Primary 1:** at every L, h1 = L is an F rule and every F rule has |h1 − L| ≤ L/8 (F rules sit half a tape
apart at every length). **Prediction:** pass (~70%; at L = 16 the shift window and threshold are coarse).

**Part B (soups):** at L = 16, 32, 128: up to 3 F rules (h1 = L if it is F, plus random others; numpy seed 680)
and 3 non-F rules (random rules with copiers but no self-sufficient one; if fewer than 3, filled with rules
without copiers). At L = 64 only h1 = 64 (for the length comparison; L = 64 was tested in E-61–E-65). 4 soups
of 2^14 per rule, seeds 6800 + 10·rank + i, up to 16,000 rounds.
**Jump criterion (D-050):** every 250 rounds, shift-aware copiers under the rule's own interpreter and L among
the 40 most common distinct programs; T = the first checkpoint with ≥ 1 copier whose checkpoint 1,000 rounds
later has ≥ 10. No HOE gate: the HOE ≥ 1 threshold is calibrated only for 64-byte standard soups (D-046
pitfall), and an L = 16 pilot soup sat at HOE −0.3. HOE is recorded.
**Primary 2 (L ≠ 64, all must hold):** F-rule soups ≥ 75% jump; non-F soups ≤ 25%; one-sided Fisher p < 0.01;
and at each L, F soups jump at least as often as non-F soups. **Prediction:** pass (~65%; we have never run
soups at L ≠ 64, and one L = 16 pilot F soup did not jump in 3,000 rounds while an L = 128 one jumped at 500).

**Secondary (exploratory):** jump time T vs L at h1 = L (16 soups; non-jumps = 16,000), Spearman, two-sided.
**Descriptive:** F-rule positions per L; orientation of self-sufficient copiers; copier shifts at the end.

**Limits:** one language family (BFF), 2^14 soups, 4 soups per rule; THR and MAXSHIFT are scaled choices, not
calibrated per L beyond the L = 64 equivalence.
