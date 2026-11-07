# Agent instructions: Emergence Lab

You are continuing a research project. **Goal:** find out whether complex, persistent and possibly evolving structure emerges spontaneously from simple fixed rules, and which rules or initial conditions make it likely. We don't simulate our universe or design life; complexity must come from each universe's own rules. Full goal, objectives and principles: `docs/research.md` ("Goal and objectives").

Before changing anything, read:

1. `docs/handoff.md`: state, how to run, repo map, conventions, pitfalls, open problems.
2. The newest entries in `docs/journal.md`, plus `docs/decisions.md`.

Published at https://yahyaal.github.io/emergence-lab/ once GitHub Pages is enabled.

## Rules that matter most

- Work on a branch and open a PR; never commit to `main`. Commit author: `yahyaal`.
- Run `pytest` and `emergence benchmark --probes` before claiming a detector or ranking change works.
- Every new detector needs a positive, a negative, a deceptive control, and a null that accounts for how its candidates are selected (`emergence/benchmark_probes.py`).
- Observation is passive. Interventions run only on forked clones (`Universe.fork`, isolated worlds).
- State claims at the evidence level reached (see `docs/research.md`). Levels 4–5 are never assigned without a validated measurement.
- Keep the journal current. After each meaningful change or experiment:
  - add a `docs/journal.md` entry (template at the bottom);
  - add a decision row if you chose between alternatives;
  - add an experiment row plus a JSON export via `scripts/journal_export.py`.
- Disagree with reviewers or the owner when the evidence says so, and record the disagreement in `docs/reviews.md`.
