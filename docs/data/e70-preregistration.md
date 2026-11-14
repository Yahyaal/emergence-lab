# E-70 pre-registration (written before running the census and soups)

**Origin:** E-60–E-69 showed, in three rule families of BFF (head1 start, both head starts, program length),
that rules where a short copier's single copy copies again (F rules) make replicators fast, and that F rules
are those whose pointers start about half a tape apart. Every family so far kept the instruction set fixed.
E-70 changes what one instruction does: the first change to the language's semantics.

**Tool:** `scripts/bff_instrset.py`; `scripts/bff_kernels.c` `run()` reads a variant v from the rule code
(code = h1 + 256·g + 65536·v, g = 0 here). Variants (each changes one thing; all keep the 10 instructions):

| v | change |
|---|---|
| 0 | standard BFF |
| 1 | `.` copies, then both heads move +1 |
| 2 | `.` copies, then both heads move −1 |
| 3 | `,` copies, then both heads move +1 |
| 4 | `[` and `]` test head1's byte instead of head0's |
| 5 | `+` and `−` act on head1's byte instead of head0's |

64-byte programs, step limit 8192, mutation 0.00024, 2^14 programs per soup (as E-61–E-68).

**Equivalence check (must hold, else stop):** v = 0 reproduces the E-61 census rule by rule (copiers,
self-sufficient copiers, class) for all 128 h1. Pilot (seen before writing this): h = 64, 7, 120 match E-61.

**Pilot (seen before writing this, disclosed):** census at h1 = 64 is F in every variant (v1 3,893
self-sufficient copiers, e.g. `<>[.]`; v2 314; v3 535; v4 99; v5 142); v1/h1 = 0, v2/h1 = 0 and v4/h1 = 0 are
S. Soup pilots (1,000 rounds, seeds 7000+): v1/h1 = 64 had 40/40 copiers by round 250, v2/h1 = 64 28 by 250;
v0/h1 = 0, v4/h1 = 0, v5/h1 = 30 had none.

**Part A (census):** all 6 × 128 rules, E-61's census unchanged (every 5- and 6-instruction kernel,
shift-aware classifier, self-sufficiency = 3 of 4 single copies copy again).
**Primary 1:** in every variant v1–v5, h1 = 64 is F and every F rule has 48 ≤ h1 ≤ 80 (F rules sit half a
tape apart whatever the instruction set). **Prediction:** pass (~55%; h1 = 64 is already known to pass, the
band is the open part: auto-moving copies could allow copiers at other offsets).

**Part B (soups):** for each variant v1–v5, up to 3 F rules (h1 = 64 plus random other F rules; numpy seed
700) and 3 non-F rules (random rules with copiers but none self-sufficient; filled with rules without copiers
if fewer). 4 soups per rule, seeds 7000 + 10·rank + i, up to 16,000 rounds.
**Jump criterion (D-050, as E-68):** every 250 rounds, shift-aware copiers under the rule's own interpreter
among the 40 most common distinct programs; T = the first checkpoint with ≥ 1 copier whose checkpoint 1,000
rounds later has ≥ 10. No HOE gate.
**Primary 2 (all must hold):** F-rule soups ≥ 75% jump; non-F soups ≤ 25%; one-sided Fisher p < 0.01; in
each variant F soups jump at least as often as non-F soups. **Prediction:** pass (~70%).

**Secondary (exploratory):** Spearman between a rule's number of self-sufficient copiers and its median T
(non-jumps = 16,000) over the F rules picked, two-sided. E-65 found ρ = −0.51, p = 0.12 within one family;
here the counts range over two orders of magnitude. Prediction: negative (more copiers, faster).

**Limits:** one language (BFF) with five hand-picked one-instruction variants; 4 soups per rule; the census
counts copiers of 5–6 instructions only; no level-5 claim is possible from jump times.
