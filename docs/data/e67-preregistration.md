# E-67 pre-registration (written before running)

**Origin:** E-66 (J-068) found no parasites among the 40 most common programs of 7 jumped soups: 99.8% of them copy
themselves. Parasites, if they exist, might be rarer. E-67 applies the same tests further down the abundance ranking.

**Tool:** `scripts/bff_parasites_rare.py`; `program_parasites.alone_test` (10 repeats) and `parasite_test` (with
the self-copy check added after E-66; code at this commit, unchanged during the run).

**Sample:** the final E-54 snapshot of each of the 7 jumped soups (5301@41750, 5302@33750, 5308@32500,
5401@30250, 5402@42250, 5406@36750, 5410@20750). Exact distinct programs are split by copy count into three strata:
**mid** (6–40 copies), **rare** (2–5), **single** (1). 20 programs per stratum per soup drawn at random (numpy
seed `[67, soup]`), 420 programs in all. Seeds for the tests `[67, soup, stratum, i]`.

**Measures:** self-copier = copies grew in ≥ 1 of 10 replicator tests; for the others, the parasite test with the
snapshot as partner pool (verdicts: parasite, by-product, unspecific copying, context self-copier, not copied).

**Predictions:**
- **P1 (primary):** parasites are rare: at most 2 of 420 programs get the verdict "parasite" (~70% confident).
- **P2:** the self-copier share falls with rarity: mid ≥ 90%, rare ≥ 70%, single ≥ 50% (~50% confident for all three).
- **P3 (descriptive):** among non-self-copiers, verdict counts per stratum; how far each is (in bytes) from the
  nearest top-40 program of its soup.

**Limits:** 7 soups, final snapshots only; strata by exact identity (a rare program may be a one-byte variant of a
common one); the parasite test is mean-field.
