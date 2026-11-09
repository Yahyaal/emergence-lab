# E-61 pre-registration (written before running)

**Origin:** J-061 (E-60b, exploratory): soup 6031 under rule h = 7 (head1 starts at byte 7) is full of copiers
that write a mirrored copy **shifted by 6–8 bytes**, which our classifier (copies only exactly at byte 64)
missed. E-60's census used the same classifier, so its F/S split ("only h = 62–65 have a self-sufficient short
copier"; "116 of 128 rules have no short copier") may be an under-count.

**Tool:** `classify_shift` (`scripts/bff_kernels.c`): as `classify`, but the partner half may hold the program or
its mirror shifted by d bytes, |d| ≤ 16, agreeing on all but ≤ 4 bytes of the overlap, with the same d for all
partners; program half intact (≥ 60 of 64). Checked before registering: random programs 0 of 500 under h = 0, 7,
64; known aligned copiers and the hand-written replicator labelled as before with d = 0; the 40 common programs of
soup 6031: 25 copiers (shifts 0, 6, 7, 8), as J-061.

**Part A (census, `scripts/bff_shift_census.py --part census`):** as E-60 Part A (all h in 0..127, kernels of 5
and 6 instructions, non-zero non-instruction filler, screen 1 partner, confirm 4), with `classify_shift`.
Self-sufficient: the copy (partner half after one run) is itself a shift-aware copier in ≥ 3 of 4 runs.
Class **F′** if a rule has a self-sufficient copier, else **S′**.
Checks: in every rule, total copiers ≥ E-60's count; F′ ⊇ {62, 63, 64, 65}. The aligned (d = 0) count is reported
next to E-60's; it can differ by a few because the screening partners are random (a timing run of rule 64 before
registering: 130 aligned vs E-60's 132, 188 in all).

**Primary 1 (census):** every F′ rule lies in 48 ≤ h ≤ 80, and every self-sufficient copier copies forwards
(prediction: a mirrored copy of a copier does not copy, shifted or not; only forward copies near byte 64 work).
**Primary 2 (soups, Part B, only if F′ has rules outside 62–65):** up to 4 of these new F′ rules drawn at random
(numpy seed 61), 4 soups of 2^14 each (seeds 6100 + 10·rank + i), E-60 settings, D-046 jump criterion with the
**shift-aware** copier check, up to 16,000 rounds. Pass if ≥ 75% of these soups jump and one-sided Fisher p < 0.01
against E-60's S-rule soups (2 of 16). If F′ has no new rules, Primary 2 is undecided and E-60's split stands
under the shift-aware classifier.

**Secondary (descriptive):** number of rules with any short copier (E-60: 12 of 128); for E-60's S rules 7, 120,
125, 126: class and copier counts under shift awareness; the distribution of shifts per rule (prediction: backward
copiers in rule h are shifted by about h or h − 128).

**Limits:** shifts up to 16 bytes only; kernels of 5–6 instructions only; one family of rule variations.

## Addendum (written after Part A while Part B was running; not part of the registered test)

**Correction:** six Part B soups (6111–6113, 6101, 6122, 6123) had finished 10–45 s before this addendum was
committed (22:59:18). I had not looked at them, but the prediction below cannot count as made in advance.

Part A found F′ = 61–68. Inspection (exploratory): a copier at shift d makes a child shifted by d, whose own
child is shifted by 2d, and so on, so its lineage loses the kernel; in a 32-generation product chain, aligned
(d = 0) copiers lasted all 32 generations, shifted ones mostly failed within 1–22. In rules 61, 66, 67, 68 every
self-sufficient copier found is shifted (d ≠ 0). **Additional prediction (not registered as primary):** if a
lasting lineage matters, soups in 61, 66, 67, 68 jump later than E-60's soups in 62, 63, 65 (median T 250–2,500);
if one-generation self-sufficiency is what matters, they jump as fast. The registered Primary 2 is unchanged.
