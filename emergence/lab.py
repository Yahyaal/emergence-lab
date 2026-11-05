"""The lab wires an engine run to an observer. This is the only place where the
two meet, and data flows one way: engine -> read-only frames -> observer.
"""
from __future__ import annotations

import numpy as np

from .engine import Universe, UniverseSpec, state_hash
from .observatory import Observation, Observer
from .observatory.probes import damage_spreading

DAMAGE_STEPS = 64


def study(spec: UniverseSpec, steps: int = 500, window: int = 100) -> Observation:
    return study_universe(Universe.from_spec(spec), spec.seed, steps, window)


def study_universe(u: Universe, seed: int, steps: int = 500, window: int = 100) -> Observation:
    """Observe an already-constructed universe (used for controls with hand-made initial states)."""
    window = min(window, steps + 1)
    # the observer's own randomness (surrogates, probe locations) is derived from
    # the seed but kept in a separate stream from the universe's randomness
    obs = Observer(total_steps=steps, window=window, seed=seed ^ 0x5EED)
    probe_rng = np.random.default_rng([seed, 7])
    dmg_steps = min(DAMAGE_STEPS, steps, window - 1) if window > 1 else 0
    t_probe = steps - dmg_steps
    snapshot = None
    obs.observe(u.t, u.state)
    if t_probe == 0:
        snapshot = np.array(u.state)
    for _ in range(steps):
        u.step()
        obs.observe(u.t, u.state)
        if u.t == t_probe:
            snapshot = np.array(u.state)
    reference = list(obs.frames)[-dmg_steps:] if dmg_steps else []
    damage = damage_spreading(u.physics, snapshot, reference, probe_rng) if dmg_steps else None
    result = obs.finalize(damage, num_states=u.physics.num_states, physics=u.physics)
    result.final_hash = state_hash(u.state)
    result.metrics.update(u.physics.rule_features())
    return result
