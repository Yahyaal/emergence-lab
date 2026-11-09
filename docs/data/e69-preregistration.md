# E-69 pre-registration (written before running)

**Origin:** E-68 (tape-length family) failed its soup prediction: F rules made replicators in 18 of 36 soups
(other rules 6 of 36), with a steep length effect: L = 16 0/12, L = 32 6/12, L = 64 4/4, L = 128 12/12 F soups;
jump time falls with L (ρ = −0.90). But E-68 kept the number of programs fixed (2^14), so an L = 128 soup held
8× the bytes of an L = 16 soup, and E-50 found the jump rate proportional to soup size.

**Tool:** `scripts/bff_tapelength_bytes.py` (E-68's `soup_job`, unchanged; D-050 criterion; 16,000 rounds).
**Design:** the same 12 rules E-68 used at L = 16 and L = 32 (3 F, 3 other each), 4 soups each (seeds
6900 + 10·rank + i), with 2^21 bytes per soup, like E-68's L = 128 soups: 2^17 programs at L = 16, 2^16 at L = 32.
A round still pairs every program once, so a round does proportionally more work.

**Primary:** fraction of F soups that jump. "Soup size explains" if ≥ 50% at L = 16 and ≥ 75% at L = 32;
"length itself matters" if ≤ 25% at L = 16; otherwise undecided.
**Prediction:** "length itself matters" (~55%): the L = 16 soups of E-68 sat at HOE ≈ −0.3 with ~40 steps per
pair, and an 8× larger soup should at most shorten the wait about 8×, which E-68's 0/12 in 16,000 rounds makes
unlikely to bring the jump inside 16,000 rounds unless the base rate was just out of reach.
**Secondary:** other rules' jump fraction per L; jump times vs E-68.
**Limits:** one size per L; rounds are not equal compute across sizes (a round at 2^17 programs is 8× more pairs).
