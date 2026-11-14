# E-75 phase 1 protocol (written before the census; design: `docs/data/e75-design.md`)

**Seen before writing this (disclosed):** phase 0 (J-077); and a timing run of the pre-filter on 5 rules with
10^6 programs each:
- forward rule (n4 always s+1 W128 o0): 102 hits, 2 inheritance replicators among them;
- band rule (n4 always s+1 W16 o64): 439 hits, 0 of 200 checked;
- SUBLEQ and RSUBLEQ4: 0 hits;
- n3 always s+1 W64 o40: 5 hits, 0 replicators.

**Census** (`scripts/sq_census.py`): 600 rules drawn uniformly from the 16,416 (numpy seed 75), plus the anchors.
Per rule:
- 10^7 random 64-byte programs, each run once with a random partner for at most 512 steps;
- a *hit* passes an 8-byte block of itself to the partner;
- up to 2,000 hits are checked with the inheritance test (D-055: 5 generations, 4-byte block, knockout;
  8,192 steps).

Classes:
- **F**: at least one replicator found;
- **C**: hits, but no replicator among those checked (copies something, nothing inherited over 5
  generations);
- **none**: no hits.

The density of replicators per 10^7 programs is recorded. The first 40 rules are censused again with a second seed.

This census asks **how often a random program is already a replicator**, not BFF's "does a short copier exist". In
a language where every byte runs, a random program *is* a random kernel followed by more code. It is the
quantity closest to spontaneous emergence. A rule whose replicators are rarer than about 1 in 10^7 random programs
is classed C or none here even if replicators exist (for example the paper's 25- and 60-byte ones).

**Predictions:**
1. **Anchors:** SUBLEQ and RSUBLEQ4 are not F (~90%; their known replicators are 60 and 25 bytes, far too rare in
   random code). SUBLEQ is "none" (~75%).
2. **F needs a walking index:** every F rule has s ≠ 0 (~75%). Without it, copying needs self-modifying loops
   of several instructions.
3. **A band:** copies that land 32, 64 or 96 bytes on fit a 64-byte program, as in the emergent loop (period 32).
   Of F rules with W ≤ 32, ≥ 80% have o within W − 1 of 32, 64 or 96 (~60%).
4. **Gate:** ≥ 16 F and ≥ 16 C rules among the 600 (~55%). If it fails, the family or census is revised and
   this census is disclosed.
5. **Stability:** ≥ 38 of 40 rules get the same class with the second seed (~80%). If not, the sample size is
   raised before phase 2.

**Limits:**
- 10^7 programs per rule bounds the detectable density.
- The 512-step pre-filter misses replicators that take longer to make their first copy.
- Up to 2,000 hits are checked per rule, so an F rule with very many non-replicating hits can be classed C.

## Outcome (added after the run; J-078)

Census: 32 F, 100 C, 468 none of 600 (83 min, 11 workers).
1. Anchors: both "none" (0 hits in 10^7). **Right.**
2. All 32 F rules have s = ±1 (and n = 4). **Right.**
3. Band: 19 of 25 F rules with W ≤ 32 (76% < 80%). **Wrong.** The band was too wide to be a strong test (at W = 32 it
   excludes only o = 0).
4. Gate: 32 F and 100 C. **Passed.**
5. Stability: 37 of 40 (< 38). **Failed.** All three disagreements are rules with ≤ 3 hits or 1 replicator.
   As stated above, the sample size is raised before phase 2 (D-056).
