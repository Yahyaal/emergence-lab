# E-28 pre-registration (written before running)

**Origin (J-032):** E-27 found 2 "reproducers" and 23 "one generation" candidates in Lenia
blob-field worlds. Inspection showed no births: an isolated blob bursts into a world-filling
labyrinth of ~80 similar-mass pieces within 500-1000 steps, then the count stops; copy mass drifted
377 -> 278 -> 169 over generations, and no third generation passed. The detector was changed
AFTER seeing this (D-028 revision): late copies must be >= 2x the early max (MIN_GROWTH), and
generation 2 is matched to the original parent. All earlier controls keep their verdicts; the
labyrinth is now a benchmark deceptive (54/54 probe checks). Re-scanning E-27's 23 hit worlds
gives 0 reproducers (post hoc). Because the fix was tuned on E-27, it needs held-out worlds.

**Design (`scripts/birth_scan.py --pool heldout`):** worlds not used in E-27, same per-world
procedure (6 most common object types + in-world mover tracks of the last 100 steps):
- H1: 150 worlds drawn at random (seed 28) from the E-14/E-18 exp. 1/E-24/E-26 worlds without movers that E-27 did not sample
- H2: 100 worlds from E-17 (random and engine-picked rules from smooth starts, 3-ring rules) and E-18 exp. 2 (wanderer ridge), seed 28
- H3: 100 worlds from E-19 (soups and shuffled-smooth starts), seed 28
- Pipeline positive (as E-27): Gray-Scott, 10 worlds with Pearson square seeds, seeds 11-20

**Primary outcome:** worlds with a reproducer in H1-H3. **Prediction:** 0 (one-sided upper 95%
bound then 0.85% per world). Gray-Scott: >= 8/10. Any Lenia reproducer is inspected by eye and
tested for a third generation before any claim. "One generation" counts are reported, not claimed.
