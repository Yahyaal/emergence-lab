# E-18 pre-registration (written before running)

**E-18a (confirmatory):** does the E-17 "wanderer" rule (`LENIA/R13/T10/m0.243/s0.0224/b1,0.5,0.5`)
reliably produce self-propelled structures from smooth starts but not from soups?
40 fresh seeds (master seed 18) per condition: `uniform` (soup), `smooth:3`, `smooth:6`,
`smooth:10`; density 0.18 (close to E-17's 0.177), 128x128, 2000 steps.
Primary test: universes with >= 1 self-propelled structure, `smooth:6` vs `uniform`,
one-sided Fisher exact, alpha = 0.05 (single primary contrast). Other smooth arms descriptive.
Validity: every self-propelled structure re-isolated, must survive 1000 steps alone.

**E-18b (exploratory):** emergence map of the wanderer's neighbourhood: 42 rules with the same
rings (1, 0.5, 0.5), mu in {0.200, 0.215, 0.230, 0.243, 0.255, 0.270, 0.285} x sigma/mu in
{0.06, 0.075, 0.092, 0.11, 0.13, 0.15}; `uniform` and `smooth:6`, 6 seeds, density 0.18,
128x128, 2000 steps, master seed 181. Outcome: fraction of universes with a verified mover per
rule; reported as a map, no test.
