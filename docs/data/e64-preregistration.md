# E-64 pre-registration (written before running)

**Origin:** E-60–E-63: in the family "head1 starts at byte h", soups make replicators quickly exactly in the rules
whose short copiers include one whose single copy copies again (F′, h = 61–68: 32 of 32 soups), and not just outside
(1 of 16), although those rules have as many short copiers. The predictor was found and tested in one family.
Does it carry over to a **new family**: head0 starts at byte g and head1 at byte h (g = 1..127, h = 0..127)?
The copy geometry changes in non-obvious ways (e.g. at g = 5, h = 69 the kernel `[.>}]` copies everything except
its own first 5 bytes, so it is not a copier).

**Tool:** `scripts/bff_kernels.c` `run()` takes code = h + 256 g; g = 0 is every earlier experiment (checked: with
code 0 the kernel interpreter equals the soup interpreter on a random tape; `[.>}]` at code 64 is a copier with
shift 0; 0 of 300 random programs are copiers at g = 10, h = 64).

**Part A (census, `scripts/bff_twoheads.py --part census`):** 256 distinct (g, h) pairs drawn at random (numpy
seed 64; g in 1..127, h in 0..127). Per rule, as E-61: kernels of 5–6 instructions, `classify_shift`, screen 1 /
confirm 4, E-61's self-sufficiency test. Class **F** (a self-sufficient copier exists), **C** (copiers, none
self-sufficient), **0** (no short copier).

**Part B (soups, `--part soups`):** up to 4 F rules and up to 4 C rules drawn at random (numpy seed 640); 4 soups of
2^14 per rule (seeds 6400 + 10·rank + i); strict D-047 criterion exactly as E-62/E-63 (`bff_lineage.job`), up to
16,000 rounds. Comparing F with C (rules that have copiers) is the hard comparison, as in E-63.

**Primary:** F-rule soups ≥ 75% real jumps, C-rule soups ≤ 25%, one-sided Fisher p < 0.01. If either class has
fewer than 2 rules in the sample, the test is undecided (reported with the census).
**Secondary (descriptive):** where F rules lie in (g, h) (no prediction registered); orientation of self-sufficient
copiers (prediction: forward); shift of copiers at the end of real jumps (prediction: mostly exact).

**Limits:** a sample of 256 of 16,256 rules; 4 soups per rule; 2^14; one language (BFF).
