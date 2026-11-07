# E-23 pre-registration: double glider + glider -> triple? (written before running)

**Question:** two gliders can fuse into a stable double glider (E-20). Can a double glider and a
single glider fuse into a stable triple (a chain of combination)?

**Design:** Orbium rule. Double glider = the E-20 fusion product (glider + transposed glider,
offset -2, phase 0, after 1000 steps), cut out; it moves diagonally. Single glider from
`emergent_glider`, oriented by the 8 exact symmetries (k), placed at distance 60 along a direction
chosen so that the paths cross: 8 symmetries x lateral offsets -12..12 (step 2) x phases 0, 10, 20
= 312 collisions on a 224x224 torus, 1500 steps after placement.

**Outcome:** final objects (mass), classified: world filled (total mass > 1000: excluded from
mover claims, J-025); otherwise by object masses: single ~70, double ~135, **triple ~190-230**.
A triple claim requires an object of mass 180-240 that moves >= 20 cells in 1000 further steps and
keeps its mass within the tracker tolerance. Descriptive.
