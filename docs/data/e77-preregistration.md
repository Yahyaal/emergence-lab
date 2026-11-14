# E-77 pre-registration (written before running)

**Origin:** H1 ("the discovery engine finds more interesting rules than random search at equal compute",
`docs/research.md`) has rested since day one on E-03 to E-06: **2 master seeds per arm** (11, 12), with the
engine ahead 1.9× (self-propelled, after removing near-duplicates) and 4.2× (complex on every seed). Research plan
item "10–30 runs per arm for H1, with confidence intervals" was never done. This is that test.

**Timing and reproduction (seeds 11 and 12, not used in the test):** all four E-03 to E-06 runs were re-run on
this code (`7f0eacb`, `--workers 1`; three at a time, the fourth alone). Wall time 977–1126 s per run with three
in parallel, 672 s alone. **Raw counts reproduce exactly:** self-propelled 81 / 29 / 99 / 29, complex on every
seed 53 / 8 / 60 / 8, niches 34 / 27 / 32 / 23 (engine-s11 / random-s11 / engine-s12 / random-s12); generation 0
is identical within each seed; calibrated robustness thresholds 0.331 / 0.296 / 0.315 / 0.247 (published
"0.25–0.33"). Projected E-77 total with `--workers 2` and 3 runs at a time: about 650–750 s per run, 14 waves,
**about 2.5–3 hours**.

**Run (`scripts/h1_power.py run --seeds 101-120 --jobs 3 --out runs/e77`):** master seeds **101, 102, …, 120**
(fixed list of 20). On each seed, two arms, each one `emergence explore` process with its own database:

```
emergence --db runs/e77/<arm>-s<seed>.db explore --name e77-<arm>-s<seed> --seed <seed> --workers 2 \
    --generations 6 --steps 500 --followups 6 [--baseline-random]
```

Settings in full (identical to E-03 to E-06; everything not on the command line is the `ExploreConfig` default,
the same values recorded in the E-03 export): Life-like/Generations rules (`outer_totalistic`, B0 excluded,
70% 2-state, 30% C3–C8), soup start, 100 rules per generation × 2 seeds per rule (`screen_seeds` 2), 6
generations (600 rules per arm), 96×96 torus, 500 steps, observation window 100, densities uniform in 0.15–0.50,
immigrant fraction 0.2, novelty k = 10; 6 follow-ups (3 new seeds + 1 world 2× larger + 1 run 4× longer, plus
innovation and replication probes). Engine arm: MAP-Elites niche pick + binary tournament + mutation;
random arm (`--baseline-random`): every generation is 100 fresh random rules. Generation 0 is identical within a
seed (same `default_rng([seed, 0])`, all random in both arms); the script checks it by hashing the gen-0 rule
lists. `--workers 2` (3 runs at a time, 6 cores, to share the machine) changes nothing in the results:
`pool.map` keeps order, and a short check run (30 rules × 3 generations, seed 7) gave identical universes (spec,
final hash, class, priority for all 190) and discoveries under `--workers 1` and `--workers 2`. Code: this commit, `emergence/*.py` unchanged from `7f0eacb`.

The **calibrated robustness threshold** (D-010) is calibrated per experiment from that run's own same-rule seed
spread; it is not held fixed across the 40 runs. It only affects which follow-ups are labelled robust; none of
the outcomes below depends on it. It is recorded per run for reference.

**Counting (D-013, near-duplicates removed):** an outcome is counted per rule (primary universe + its screen), as
in `emergence.analysis._rule_stats`: *self-propelled* = at least one shape that travels alone in an isolated
clone; *complex on every seed* = class "complex" on both seeds. The E-03 to E-06 deduplication ("only rules at
least 2 mutations apart") was never committed, so it is re-implemented as
`scripts/h1_power.py:distinct_greedy`: mutation distance |B △ B′| + |S △ S′| + |C − C′| (the single steps of
`OuterTotalistic.mutate`); rules visited in exploration order (universe id), a rule kept only if it is ≥ 2 from
every rule already kept; applied within each run, separately per outcome.
**It reproduces the published distinct counts exactly** on the four E-03 to E-06 runs: self-propelled
50 / 27 / 55 / 29 and complex on every seed 34 / 8 / 33 / 8. (The alternative reading, single-mutation
clusters, gives 25 / 25 / 24 / 29 and 18 / 8 / 13 / 8, so it is not what was used.) It is pre-registered as the
definition.

**Primary:** distinct rules with self-propelled structures, engine vs random, paired by seed (n = 20).
**Pass** = one-sided exact Wilcoxon signed-rank test (engine > random; zero differences dropped, mid-ranks for
ties; `signed_rank_exact`) **p < 0.01 AND** median over seeds of the per-seed ratio engine/random **≥ 1.5**.
**Fail** = p ≥ 0.05 (no evidence of any advantage), or the upper end of the 95% bootstrap interval of the
median ratio (10,000 resamples of seeds, numpy seed 77, percentile) is below 1.5 (any advantage is smaller than
1.5×). **Undecided** = anything else (e.g. p < 0.01 with the median ratio below 1.5 but its interval reaching
1.5, or 0.01 ≤ p < 0.05). If any of the 40 runs cannot be completed the verdict is reported on the completed
pairs and marked as such. The exact sign test is reported alongside as a check, not as a second chance.
**Prediction:** pass. We put **~85%** on it: on seeds 11 and 12 the ratio is 1.85 and 1.90 with
the random arm steady (27, 29), so the Wilcoxon test should be far below 0.01 if most seeds look like these; the
risk is the 1.5 ratio bar, if seed-to-seed variation in the engine arm is larger than two seeds suggest. We
expect the secondary on complex rules to pass (ratio ~4) and niches to pass with a smaller ratio (~1.3).

**Secondary (reported with the same statistics, not part of the verdict):** distinct rules "complex on every
seed" (engine > random, one-sided, α = 0.01); niches filled at the end (engine > random, one-sided, α = 0.01).
**Descriptive:** raw (not deduplicated) counts of both outcomes and of "structured" rules; the alternative
deduplication (clusters linked by single mutations, `n_components`); the per-run robustness thresholds; wall
time per run.

**Limits:** one rule family (Life-like/Generations), one budget (600 rules per arm), one world size; the outcomes
are the engine's own objectives (self-propelled is optimised directly; "complex on every seed" is not), so a win
is partly circular, which is why the less circular secondary is reported.
