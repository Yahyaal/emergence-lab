# E-74 pre-registration (written before the fresh census and before any E-74 soup)

**Origin:** E-72 tested whether F rules with no "deep" self-copier (one whose copies still copy after 5
generations) are slower to make replicators. Its pre-registered primary failed under the D-050 copy test (shallow
1,675 vs deep 1,475 rounds, p = 0.58). E-73 (J-075) re-scored the same 96 soups with the validated D-053 test
(58/64 + 75% instruction-fidelity guard): deep 163 vs shallow 1,638 rounds, ratio 10, Mann–Whitney p = 0.06. Under
an HOE timing: deep 188 vs shallow 1,500, p = 0.04. Both point the predicted way but neither reaches p < 0.01, with
8 rules per class. E-74 is a larger, fresh test.

**Seen before writing this (disclosed):** all E-72 and E-73 results, including the per-rule D-053 medians of E-72's
16 rules. Nothing about the rules below: their census, depth and soups have not been computed.

**Rules** (`scripts/bff_deepconfirm.py`, `fresh_rules()`): 600 rules of the E-72 family, variant v ∈ 1–5, head0
starting at g ∈ 1–127, head1 at h = g + d with d ∈ 60–68 (mod 128), drawn with numpy seed 74, **excluding all 240
rules of the E-72 census** (every earlier rule with g > 0). Census and depth exactly as E-72
(`bff_multigen.rule_job`: one-generation census of 5–6-instruction kernels; 8 lineages × 5 generations per
self-sufficient kernel, up to 300 kernels; *deep* if ≥ 4 of 8 lineages reach generation 5). An F rule is **F-deep**
if `deep_est ≥ 1`, else **F-shallow**. Up to **12 F-deep and 12 F-shallow** rules are picked at random (numpy seed
740), 6 soups each (seeds 7400 + 10·k + i), 2^14 programs of 64 bytes, up to 16,000 rounds.

**Timing, three ways, at checkpoints every 50 rounds** (all computed in the same run):
- **D-053** (primary): copiers by `classify_fid` (58/64, guard 75%) among the 40 most common distinct programs;
  T = the first checkpoint with ≥ 1 copier whose checkpoint 1,000 rounds later has ≥ 10.
- **HOE** (primary, D-052): T = the first of 3 consecutive checkpoints with high-order entropy ≥ 2.
- **D-050** (reported beside them): as D-053 with `classify_shift` (60/64, no guard).

Per rule: median T over its 6 soups, non-jumps = 16,000.

**Primary:** F-shallow rules are slower. For a timing to pass: the median over shallow rules of their median T is
**≥ 3×** that of the deep rules (the deep median floored at 50 rounds, one checkpoint), and a one-sided
Mann–Whitney test at rule level gives **p < 0.01**. **The primary passes only if both D-053 and HOE pass; it fails
if both fail; otherwise it is unresolved** (D-052). If either class has fewer than 6 rules: **undecided**.
**Prediction:** pass (~45%). The E-72 effect was large under both timings, and 12 vs 12 rules give more power, but
E-72's p values were 0.04–0.06 with 8 vs 8 and its v4 rules were slow in both classes.

**Secondary (exploratory):** jump rate by class under each timing; Spearman of `deep_est` and of the
one-generation self-sufficient count vs median T (which predicts better?); the number of F, F-deep and F-shallow
rules among the 600; soups where the timings disagree by more than 1,000 rounds.

**Limits:** the D-053 test was validated on fixtures from 7 rules, not on every variant; HOE ≥ 2 is calibrated for
standard BFF; 5 generations × 8 lineages is an arbitrary depth; one language family; 6 soups per rule.
