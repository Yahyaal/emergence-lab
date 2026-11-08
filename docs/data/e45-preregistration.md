# E-45 pre-registration (written before running)

**Origin (J-044, post hoc):** in E-44, replicators #5 and #6 of soup 5006 (epoch 32000) turned out
to be exact byte-reversals of each other: either one, run first, writes its own reverse into its
partner, so the species alternates between two forms (a "mirror replicator"). In E-44 each was
counted alone (half its species), yet pooled over its 8 pairs with the four soup-901 replicators
the mirror pair ended more common in 162 of 250 informative races (binomial p = 3e-6). That
pattern was found by looking at the data, so it needs a fresh test.

**Measure:** `program_selection.compete_families` (D-043) with species counting: the mirror
species is seeded as 8 copies of #5 and counted as programs >= 90% identical to #5 **or** #6
(`a_alt`). 64 replicate soups per pair (instead of 16), fresh random stream (seed 45).
Verdict as D-043: favoured if >= 8 informative replicates, two-sided sign test p < 0.01, mean
|s| > ln 2.

**Pairs:**
- Primary: mirror species (a) vs each soup-901 replicator #0-#3 (b) of E-42; 4 pairs.
- Secondary: mirror species vs #4 (soup 5006, epoch 28250), #7 and #8 (soup 5010), and vs the
  hand-written replicator; 4 pairs.
- Null: 4 pairs hand-written replicator vs `retail(H)` (independent tails), same 64 replicates,
  with the reverse of `retail(H)` added as an alternative form (checks that species counting does
  not create an advantage).

**Primary outcome:** pooled over the 4 primary pairs, the share of informative replicates won by
the mirror species (s < 0), one-sided binomial test against 1/2 at p < 0.01.
**Predictions:** pooled share >= 0.6 and p < 0.01; at least 2 of the 4 primary pairs "a favoured"
and none "b favoured"; null pairs: no favoured verdict, pooled share within 0.4-0.6. Secondary:
no prediction (the hand-written replicator beat every emergent one in E-44, so it is expected to
beat the mirror species too).

**Evidence level if confirmed:** a reproducible fitness difference between two emergent
replicator species from different soups in a common environment. Differential reproduction is the
third condition for natural selection; combined with E-42 (heredity) this is level 4 with a
selection component, not level 5 (no cumulative change shown).

**Limits:** one species against one soup's family; a fresh random soup is not the soup of origin;
64 replicates give power for win shares of roughly 0.65 or more per pair.
