# E-65 pre-registration (written before running)

**Origin:** E-64 confirmed, out of family, that rules whose short copiers include one whose single copy copies
again (F) make replicators quickly (10/12 soups vs 1/16 in C rules), but the F arm rested on only **3 rules**,
one of them slow (2/4). Post hoc, across the 11 F rules of E-62–E-64, more self-sufficient short copiers went
with earlier jumps (soup level ρ = −0.38, p = 0.01; rule level ρ = −0.44, p = 0.17, n = 11): a graded predictor
is suggested but not established.

**Tool:** `scripts/bff_twoheads2.py`, reusing E-64's census (`bff_twoheads.census_rule`, unchanged) and the
D-047 soup job (`bff_lineage.job`, unchanged).

**Part A (census):** 768 new distinct (g, h) pairs of the two-head-start family (numpy seed 65; g in 1..127,
h in 0..127; none of E-64's 256). Classes F / C / 0 as E-64.

**Part B (soups):** **every** F rule found (if more than 16, 16 drawn at random with numpy seed 650) and 4 C rules
drawn at random (seed 650); 4 soups of 2^14 per rule (seeds 6500 + 10·rank + i); D-047 exactly as E-62–E-64, up
to 16,000 rounds.

**Primary (all must hold):** F-rule soups ≥ 75% real jumps; C-rule soups ≤ 25%; one-sided Fisher p < 0.01; and at
least 75% of F rules have ≥ 2 of 4 soups jumping (the predictor works rule by rule, not just on average). If
fewer than 2 F or 2 C rules are found, undecided.
**Prediction:** pass (we put ~75% on it; the expected number of F rules is ~9).

**Secondary:** across the new F rules, Spearman correlation between the number of self-sufficient short copiers
and the rule's median jump time (non-jumps counted as 16,000), one-sided (negative), α = 0.05. We give this
about a 40% chance (few rules, and the post hoc effect was weak at rule level).
**Descriptive:** offsets h − g (mod 128) of F rules; orientation of self-sufficient copiers; shifts of copiers
at the end of real jumps.

**Limits:** start-position variants of one language; 2^14 soups; 4 soups per rule.
