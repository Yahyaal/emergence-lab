# E-63 pre-registration (written before running)

**Origin:** E-60–E-62: every rule whose short copiers include one whose single copy can copy (F′ = 61–68, at shifts
up to 16) made exact-copier replicator soups fast: 28 of 28 fresh soups under the strict D-047 criterion (E-62).
Lineage persistence did not matter (J-063). Untested under D-047: rules just **outside** F′ that still have short
forward copiers (shifted 5–16 bytes), whose single copy cannot copy (E-61 census: 59, 60, 69–82).

**Design (`scripts/bff_outside.py`):** 4 rules drawn at random (numpy seed 63) from {59, 60, 69, …, 82}; 4 soups of
2^14 each (seeds 6300 + 10·rank + i), plus 4 soups at h = 64 (seeds 6390–6393) as a concurrent positive control.
Jump criterion D-047 exactly as in E-62 (`bff_lineage.job`: shift-aware copier check, ≥ 10 copiers among 40 at
T + 1,000, failed candidates dropped, up to 16,000 rounds).

**Primary:** outside-F′ soups: ≤ 4 of 16 jump, and fewer than E-62's F′ soups (28 of 28), one-sided Fisher
p < 0.01. Control: h = 64 ≥ 3 of 4 (else the run is suspect and reported as such).
**Secondary:** shifts of the copiers at the end of any jump (prediction: exact, shift 0, i.e. the soup had to
evolve a longer exact copier); dropped candidates per rule.

**Limits:** 4 rules, 4 soups each, 2^14, 16,000 rounds; one family of rule variants.
