"""The Observer passively receives read-only frames and summarises them.

It never calls into the engine except through ``probes`` (which fork twins).
The output is deliberately *multi-dimensional*: a dictionary of metrics, a
descriptor vector used for novelty search, and a coarse human-readable class.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import log1p
from typing import Any

import numpy as np

from . import measures as M
from .recurrence import RecurrenceDetector
from .structures import analyse

DESCRIPTOR_FIELDS = [
    "density_late", "activity_late_sqrt", "entropy_late", "spatial_order",
    "spacetime_ratio", "cycle_found", "log_period", "transient_frac", "damage_norm",
    "movers", "vocabulary", "still", "activity_persistence", "local_periodic",
    "self_propelled", "activity_trend",
]

CLASSES = ["extinct", "saturated", "frozen", "periodic", "drifting", "chaotic", "complex", "active"]

CLASS_HELP = {
    "extinct": "everything died",
    "saturated": "space filled with a single state",
    "frozen": "reached a fixed point (period 1)",
    "periodic": "whole universe repeats exactly, or every changing cell oscillates on its own",
    "drifting": "whole universe repeats up to a translation",
    "chaotic": "sustained activity, nearly incompressible (noise-like)",
    "complex": "sustained (not fading), compressible activity with persistent or self-propelled structures",
    "active": "still changing at the horizon, no clear signature (long transient?)",
}


@dataclass
class Observation:
    metrics: dict[str, Any]
    timeseries: dict[str, list[float]]
    descriptor: list[float]
    cls: str
    final_hash: str
    final_state: np.ndarray = field(repr=False)


class Observer:
    def __init__(self, total_steps: int, window: int = 100, sample_every: int = 5, seed: int = 0):
        self.total_steps = total_steps
        self.window = window
        self.sample_every = sample_every
        self.rng = np.random.default_rng(seed)  # only used for surrogates, never for the universe
        self.prev: np.ndarray | None = None
        self.activity: list[float] = []
        self.ts: dict[str, list[float]] = {"t": [], "density": [], "activity": [], "entropy": [], "spatial_ratio": []}
        self.frames: deque[np.ndarray] = deque(maxlen=window)
        self.recur = RecurrenceDetector()
        self.last_t = 0

    def observe(self, t: int, state: np.ndarray) -> None:
        state = np.array(state, copy=True)  # observer keeps its own copy
        if self.prev is not None:
            self.activity.append(M.activity(self.prev, state))
        self.recur.update(t, state)
        if t % self.sample_every == 0:
            self.ts["t"].append(t)
            self.ts["density"].append(round(M.density(state), 5))
            self.ts["activity"].append(round(self.activity[-1] if self.activity else 0.0, 5))
            self.ts["entropy"].append(round(M.block_entropy(state), 5))
            self.ts["spatial_ratio"].append(round(M.compression_ratio(state, self.rng), 5))
        self.frames.append(state)
        self.prev = state
        self.last_t = t

    # ------------------------------------------------------------------ summary
    def finalize(self, damage: dict[str, Any] | None = None, num_states: int = 2, physics=None) -> Observation:
        final = self.prev
        frames = list(self.frames)
        W = len(frames)
        act = np.array(self.activity) if self.activity else np.zeros(1)
        late_act = float(act[-W:].mean())
        early_act = float(act[: max(1, min(50, len(act)))].mean())
        # Is activity holding up or fading? Compare the last window with the one before.
        prev_act = float(act[-2 * W:-W].mean()) if len(act) >= 2 * W else early_act
        trend = min(late_act / prev_act, 2.0) if prev_act > 0 else (1.0 if late_act > 0 else 0.0)
        t_arr = np.array(self.ts["t"])
        late_mask = t_arr >= self.last_t - W
        late = {k: float(np.mean(np.array(v)[late_mask])) for k, v in self.ts.items() if k != "t"}

        st = np.stack(frames)
        spacetime = M.compression_ratio(st, self.rng)
        local_periodic = M.local_periodicity(st)
        structs = analyse(frames, physics)
        rec = self.recur.result
        damage = damage or {}

        m: dict[str, Any] = {
            "steps": self.last_t,
            "alive_final": int(np.count_nonzero(final)),
            "density_final": M.density(final),
            "density_late": late["density"],
            "activity_early": early_act,
            "activity_late": late_act,
            "activity_persistence": min(late_act / early_act, 1.0) if early_act > 0 else 0.0,
            "activity_trend": trend,
            "entropy_late": late["entropy"],
            "spatial_ratio_late": late["spatial_ratio"],
            "spacetime_ratio": spacetime,
            "active_cell_frac": local_periodic["active_cell_frac"],
            "local_periodic_frac": local_periodic["local_periodic_frac"],
            "cycle_found": rec is not None,
            "period": rec["period"] if rec else None,
            "transient": rec["transient"] if rec else None,
            "cycle_shift": list(rec["shift"]) if rec else None,
            "damage": damage.get("damage"),
            "damage_norm": damage.get("damage_norm"),
            **structs,
        }
        m["class"] = classify(m, final, num_states)
        return Observation(
            metrics=m,
            timeseries={**self.ts, "damage_curve": damage.get("damage_curve", [])},
            descriptor=descriptor(m),
            cls=m["class"],
            final_hash="",
            final_state=final,
        )


def classify(m: dict[str, Any], final: np.ndarray, num_states: int) -> str:
    """Coarse, transparent labels for humans. The discovery engine does NOT
    optimise this label; it uses the full descriptor."""
    if m["alive_final"] == 0:
        return "extinct"
    if final.min() == final.max():
        return "saturated"
    if m["cycle_found"]:
        if any(m["cycle_shift"]):
            return "drifting"
        return "frozen" if m["period"] == 1 else "periodic"
    # Many independent oscillators: no global recurrence (periods don't align)
    # but every changing cell is individually periodic -> repetitive, not novel.
    if m["local_periodic_frac"] >= 0.95:
        return "periodic"
    if m["activity_late"] > 0.02 and m["spacetime_ratio"] > 0.85 and (m["damage_norm"] or 0) > 0.5:
        return "chaotic"
    movers = m.get("self_propelled_shapes")
    movers = m.get("mover_shapes", 0) if movers is None else movers
    if (m["activity_late"] > 0.0005 and m["spacetime_ratio"] <= 0.85 and m.get("activity_trend", 1.0) >= 0.5
            and (movers >= 1 or m.get("vocabulary", 0) >= 4)):
        return "complex"
    return "active"


def descriptor(m: dict[str, Any]) -> list[float]:
    """Behaviour vector, each component scaled to roughly [0, 1]."""
    steps = max(m["steps"], 1)
    clip = lambda x, hi=1.0: float(min(max(x, 0.0), hi))  # noqa: E731
    vec = [
        clip(m["density_late"]),
        clip(np.sqrt(m["activity_late"])),
        clip(m["entropy_late"]),
        clip(1.0 - m["spatial_ratio_late"]),
        clip(m["spacetime_ratio"], 1.2) / 1.2,
        1.0 if m["cycle_found"] else 0.0,
        clip(log1p(m["period"]) / log1p(steps)) if m["cycle_found"] else 0.0,
        clip(m["transient"] / steps) if m["cycle_found"] else 1.0,
        clip(m["damage_norm"] or 0.0, 1.5) / 1.5,
        clip(log1p(m.get("mover_events", 0)) / log1p(500)),
        clip(log1p(m.get("vocabulary", 0)) / log1p(100)),
        clip(log1p(m.get("still_structures", 0)) / log1p(100)),
        clip(m["activity_persistence"]),
        clip(m["local_periodic_frac"]),
        clip(log1p(m.get("self_propelled_shapes") or 0) / log1p(50)),
        clip(m.get("activity_trend", 1.0), 2.0) / 2.0,
    ]
    return [round(v, 5) for v in vec]
