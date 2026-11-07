# E-20 pre-registration: can glider collisions make new gliders? (written before running)

**Why:** E-15 saw collisions only destroy or merge gliders, but in 6 worlds, with an unvalidated
counter (review R-4). A controlled scan gives many collisions per CPU-hour.

**Design:** Orbium rule (`LENIA/R13/T10/m0.150/s0.0150/b1`) and the best E-14 rule
(`m0.140/s0.0140`). Glider = `continuous.emergent_glider` for that rule (moves +x). Partner
oriented exactly by flip (head-on, moving -x) or transpose (perpendicular, moving +y).
Lateral offset -24..24 cells (step 2), partner phase 0..20 steps (step 5); 192x192 torus;
1000 steps after placement. Head-on: 25 offsets x 5 phases; perpendicular: same.
500 collisions in total (2 rules x 2 geometries x 125).

**Outcome:** number of verified gliders at t = 1000 (objects of mass 50-100 that pass the
observatory's isolation test). Categories: 0 (annihilation), 1 (merge or survivor), 2 (both
survive or pass through), >= 3 (**birth**). Also any other persistent object type (new shape).
A birth claim requires: >= 3 verified gliders at t = 1000, each surviving 1000 steps alone, and
inspection of frames. Descriptive; no test.
**Prediction:** no births (E-15).
