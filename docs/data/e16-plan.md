# E-16 plan (exploratory; written before running)

**Question:** E-14 showed that in Lenia smooth (spatially correlated) random starts produce
gliders where soups never do. Does the same hold in Flow-Lenia, where no positive control
(self-propelled structure) has been found yet (J-016)?

**Design:** 100 random Flow-Lenia rules (`rule-panel-e16.txt`, `FlowLenia.random` with
seed 16, the paper's ranges, R = 13), each started as `uniform` (soup), `smooth:3`,
`smooth:6` and `patches` (Chan-style patches; Flow-Lenia's own paper uses one central
patch), density 0.35, 1 seed, 128x128, 1000 steps, `--seed 16`.

**Outcome:** universes with >= 1 self-propelled structure (observatory test); every one is
re-isolated and must survive 1000 steps alone. Exploratory: no significance test. A rule
that passes becomes a Flow-Lenia positive-control candidate, to be confirmed with fresh
seeds before use.
