# E-46 pre-registration (written before running)

**Origin (correction of E-44 and E-45):** after E-45 we found that **every** emergent replicator
of E-42 is a mirror replicator: seeded alone, each one produces its exact byte-reverse in about
equal numbers (4 soups each; checked in the session log of J-046). Only the hand-written
replicator copies forwards. E-44 counted each emergent replicator by one form only (half its
species), and E-45 counted the mirror species #5/#6 by both forms but its opponents by one form.
So:
- E-45's advantage of the mirror species (173/249) may be a counting artefact;
- E-44's advantage of the hand-written replicator (222/287) may be a counting artefact;
- E-44's emergent-vs-emergent comparisons were symmetric (both halves) and stand.

**Measure:** `program_selection.compete_families` (D-043) with **species counting for every
competitor**: each emergent replicator x is counted as programs >= 90% identical to x or to
reverse(x); the hand-written replicator (H) likewise (its reverse never appears; harmless).
#5 and #6 are one species (seeded as #5). 64 replicate races per pair, seed 46.

**Species:** 8 emergent species (E-42 #0, #1, #2, #3, #4, #5/#6, #7, #8) and H.
- Primary: all 28 pairs of the 8 emergent species.
- Secondary: H vs each emergent species (8 pairs).
- Null: 24 designed-null pairs, H vs `retail(H)` with independent tails, both counted with
  reverses (the larger null set R-E45 asked for).

**Outcomes and predictions:**
1. Mirror species (#5/#6) vs the four soup-901 species (the E-45 primary, now unbiased): pooled
   share of races won by the mirror. Prediction: **not** above 1/2 at p < 0.01 (we expect the
   E-45 effect to disappear once counting is symmetric).
2. H vs emergent species, pooled share won by H: prediction: not above 1/2 at p < 0.01.
3. Emergent pairs: number with a favoured verdict, compared with the 24 null pairs (Fisher
   one-sided p < 0.05). Prediction: not significant (E-44's batch disagreement suggests no
   large differences).
4. Null pairs: false-positive rate of the verdict (expected ~1%; E-44/E-45 saw 2/46).

**If prediction 1 fails** (the mirror species still wins with symmetric counting), the E-45 claim
stands with a corrected measurement; otherwise J-045's claim is withdrawn.
