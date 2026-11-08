# E-42 pre-registration (written before running)

**Origin (J-041):** self-replicating programs emerged in 3 of 16 BFF soups, every time confirmed
by the replicator detector (D-040), in several variants. Level 4 asks whether variation is
heritable: when a replicator carries a mutation, do its copies carry it too, or do they revert
(an attractor, as Lenia's dividing spots, J-037) or lose it?

**Measure (`observatory/program_heredity.py`, D-041, new):** for a replicator x, 24 single-byte
mutants (random position, random new value). Each mutant is seeded as 8 copies among 1024 random
programs, 96 epochs without mutation (the detector's growth set-up). Family = programs >= 90%
identical to x. Viable: the family reaches >= 64. f_mut = share of the family carrying the mutant
byte; f_base = the same share when unmutated x is seeded. Inherited: f_mut >= 0.5 and
f_base <= 0.1. Verdict "heredity" if >= 6 viable mutants, at least half of them inherited, and
f_mut > f_base in significantly more viable mutants than not (sign test, p < 0.01); "no
variation" if fewer than 6 viable; otherwise "no heredity".
Controls (benchmark section 12, all passing before this run): hand-written replicator ->
heredity (12 viable, 12 inherited); noexec and copyall -> no variation; a random program -> no
variation.

**Candidates:** all 9 distinct programs with a "replicator" verdict in E-41's scans (soups 901,
5006, 5010; hex in `docs/data/experiments/2026-11-08-e41-bff-longer.json`). Random stream seed
42 + candidate index. Script `scripts/bff_heredity.py`.

**Predictions:** "heredity" for at least 7 of 9 (emergent BFF replicators are described as
copying their whole tape, so mutations outside the copying code should be carried); viable
mutants 30-70% of 24 per candidate; f_base about 0 everywhere.

**Evidence level if confirmed:** level 4 (heritable variation) for program replicators: the
mutations are carried by descendants in a fresh soup. It does not show selection among variants
or open-ended evolution (level 5).

**Limits:** single-byte mutations only; 96 epochs (a few generations); the replicators were
selected from soups that transitioned; the hand-written positive is a simple linear copier, while
emergent replicators may copy in other ways (e.g. in reverse, or only when run second).
