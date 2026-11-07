# E-29 pre-registration (written before running)

**Origin (J-032, Track D route 2 in research.md):** E-27/E-28 tested objects found in worlds we
had already run (mostly glider-island and wanderer-ridge rules, from smooth starts and soups):
0 reproducers in 568 worlds. Those worlds were selected for movers, so they cover a small part
of Lenia rule space. Route 2 planned a "fission objective" for the search engine. Before building
one, a cheaper and more direct test: give **every** rule from the random-rule distribution the
same chance to reproduce, with no in-world selection that could hide a fast divider among blob fields.

**Design (`scripts/lump_scan.py`, commit noted in the experiment row):**
- 3000 rules from `Lenia.random` (mu 0.08-0.40, sigma/mu 0.05-0.30, 1-3 rings, R 13, T 10), seed 29.
- Per rule, 2 lumps: smooth noise (Gaussian blur width 3, scaled to [0, 1]) inside a disk of
  radius 13 or 26, alone at the centre of a 128x128 vacuum. Run 300 steps. If the world fills
  (occupied > 30%) first, the last 25-step checkpoint (from step 50) before it filled is used.
- The settled state goes to the validated birth detector (`births.scan`, D-028, unchanged): the 2
  most common object types, each tested for two generations alone in a 160x160 vacuum over 4000
  steps, with the vacuum background null and the scrambled-patch (attractor) check.
- Pipeline positive: Gray-Scott (F 0.0367, k 0.0649) lumps of radius 6 and 13, 10 seeds.
- A pilot (seed 99, 22 rules, not part of the sample) was run only to time the scan and check the
  pipeline: 0 reproducers, Gray-Scott 2/2.

**Primary outcome:** rules with at least one "reproducer" verdict. **Prediction:** 0. If 0, the
one-sided 95% upper bound on the fraction of the random-rule distribution with a lump-born
reproducer of this kind is 3/3000 = 0.1%. Gray-Scott: >= 9/10 seeds with a reproducer.
**Secondary (descriptive):** counts of extinct / filled / object outcomes and of "one generation"
and "explosive" verdicts; where in (mu, sigma/mu) they fall.

**Any Lenia reproducer** is inspected by eye (frames of generation 1 and 2), tested for a third
generation and re-run with 3 new lump seeds before any claim. "One generation" verdicts are
reported, not claimed.

**Limits stated in advance:** one start shape per radius (lumps, not soups or patches); 300
settling steps; only the 2 most common object types per lump; T fixed at 10 and R at 13; single
channel and single kernel. A null result says reproducers of this kind are rare in this
distribution, not that single-channel Lenia cannot reproduce.
