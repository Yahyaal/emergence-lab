# E-26 pre-registration (written before running)

**Origin:** in the held-out check of the quasi-static cut-off (J-028; 120 rules drawn by
`Lenia.random` with seed 8, 96x96, seed 1, 500 steps), one rule was `complex` from a smooth
start: `LENIA/R13/T10/m0.277/s0.0316/b1,0.5,1` (3 rings, sigma/mu = 0.114). Its two movers (mass
about 178, about 0.085 cells/step) each survive 1000 steps alone. From a soup it went extinct. Its
mu and sigma/mu lie on the upper band of the E-18b "wanderer ridge" (sigma/mu about 0.11 for mu
0.255-0.285), but its ring weights differ (b1,0.5,1 vs b1,0.5,0.5). It was not found by a search;
it is one draw of 120.

**Question:** is it a reliable source of movers, and does the smooth-start effect hold for it?

**Design:** this rule x 40 seeds x {`uniform`, `smooth:6`} at density 0.35 (where it was found)
and, as a second run, at density 0.18 (E-18a's density); 128x128, 2000 steps, `--seed 26`.

**Primary outcome:** worlds with a verified mover (`scripts/verify_movers.py`: in-world track,
then 1000 steps alone), smooth:6 vs uniform at density 0.35, one-sided Fisher exact test, alpha 0.05.

**Secondary:** the same at 0.18; mass and path speed of the verified movers, compared with the
wanderer (mass 104-137, about 0.085 cells/step).

**Prediction:** smooth > soup at both densities (soups die or freeze, as for every other mover rule).
