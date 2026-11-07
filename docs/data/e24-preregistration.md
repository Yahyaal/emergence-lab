# E-24 pre-registration (written before running)

**Question (open item 3 from the first overnight session):** Chan (2019) says gliders emerge
from random starts "given enough time". His start is 15-40 dense patches in vacuum (`patches`).
In 128x128 worlds over 2000 steps it gave 0 gliders in 40 worlds (E-13). Do larger worlds
help?

**Pilot (before this plan, scratch script, 48 worlds, 256x256, 400 steps):** in the 8 E-13 rules,
patch starts are bistable. With Chan's patch count (15-40), 9 of 24 worlds were extinct by
step 400 and 15 of 24 were filled by a blob field (mean value about 0.2). With 110 patches (the same
patch density as 27 patches on 128x128), 24 of 24 were filled. Gliders in a filling field are
swallowed (handoff pitfall), so a 10000-step run would measure a settled field. The planned
10000-step study is therefore replaced by this shorter one.

**Design:** the 8 E-13 rules (`rule-panel-e13.txt`) x 20 seeds x {`patches` (n = 15-40),
`patches:110`}, 256x256, 3000 steps, `--seed 24`. Comparison arm: `smooth:3` at density 0.10
(the best glider start in E-14/E-19), same size and steps, so the result says whether the
world size alone changes the smooth-start rate too.

**Primary outcome:** worlds with at least one self-propelled structure, verified 1000 steps
alone with `scripts/verify_movers.py`.

**Prediction:** patches give at most 1-2 glider worlds out of 160 per arm (the field wins or the
world dies); smooth:3 gives fewer than its 128x128 rate (23%) because the bigger world's field
grows (E-15).

**Analysis:** counts with 95% Clopper-Pearson intervals per arm; descriptive only (no test is
pre-registered, since the patch arms are not mass-matched to anything).
