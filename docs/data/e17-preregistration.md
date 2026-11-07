# E-17 pre-registration (written before running)

**Question:** E-12 searched Lenia rule space from soups and found no self-propelled structure,
but E-14 showed soups never make gliders even where they are possible. With smooth starts
(D-025), does the discovery engine find glider rules, does it beat random search at equal
compute, and does it find gliders OUTSIDE the single-ring island mapped in E-13a (e.g.
multi-ring rules)?

**Design:** identical to E-12 except the start: `emergence explore --physics lenia --init smooth:6
--seed 17` (engine) and the same with `--baseline-random`; 100 rules x 2 seeds x 5 generations,
96x96, 500 steps, densities drawn per rule from [0.15, 0.5] as in E-12 (the smooth start is
mass-matched to that density).

**Primary outcome:** number of distinct rules (near-duplicates removed: mu and sigma/mu to 0.01,
same ring count) with >= 1 self-propelled structure in any of their runs, engine vs random.
Reported descriptively with the D-013 dedup; one seed per arm, so no significance claim (as
J-004/J-013).
**Secondary:** how many such rules lie outside the E-13a island (mu 0.135-0.165 and sigma/mu
0.095-0.135, single ring); every self-propelled structure in those is re-isolated and must
survive 1000 steps alone before being reported as a new glider rule.
**Prediction:** both arms find some; the engine finds more (it rewards self-propelled
structures directly), including multi-ring rules.
