"""SQLite lab notebook: every experiment, universe spec, measurement and discovery.
A single file, no server, readable with any SQLite tool."""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import zlib
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY,
    name TEXT,
    created_at REAL,
    finished_at REAL,
    status TEXT,
    master_seed INTEGER,
    config TEXT,
    environment TEXT
);
CREATE TABLE IF NOT EXISTS universes (
    id INTEGER PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    generation INTEGER,
    role TEXT,
    parent_id INTEGER,
    rule TEXT,
    spec TEXT,
    steps INTEGER,
    window INTEGER,
    class TEXT,
    metrics TEXT,
    descriptor TEXT,
    timeseries TEXT,
    final_hash TEXT,
    final_state BLOB,
    novelty REAL,
    pareto_rank INTEGER,
    priority INTEGER,
    aggregate TEXT,
    created_at REAL
);
CREATE INDEX IF NOT EXISTS ix_univ_exp ON universes(experiment_id);
CREATE TABLE IF NOT EXISTS discoveries (
    id INTEGER PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    universe_id INTEGER REFERENCES universes(id),
    kind TEXT,
    summary TEXT,
    evidence TEXT,
    created_at REAL
);
"""


def pack_state(state: np.ndarray) -> bytes:
    return zlib.compress(np.ascontiguousarray(state, dtype=np.uint8).tobytes(), 9)


def unpack_state(blob: bytes, height: int, width: int) -> np.ndarray:
    return np.frombuffer(zlib.decompress(blob), dtype=np.uint8).reshape(height, width)


class Store:
    """One SQLite connection per thread (the dashboard server is multi-threaded)."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self._local = threading.local()
        self.db.executescript(SCHEMA)
        cols = {r[1] for r in self.db.execute("PRAGMA table_info(universes)")}
        if "aggregate" not in cols:  # databases from v0.1
            self.db.execute("ALTER TABLE universes ADD COLUMN aggregate TEXT")
        self.db.commit()

    @property
    def db(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.path, timeout=30)
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return conn

    def close(self) -> None:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    # ---------------------------------------------------------- experiments
    def create_experiment(self, name: str, master_seed: int, config: dict, environment: dict) -> int:
        cur = self.db.execute(
            "INSERT INTO experiments(name, created_at, status, master_seed, config, environment) VALUES (?,?,?,?,?,?)",
            (name, time.time(), "running", master_seed, json.dumps(config), json.dumps(environment)),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def finish_experiment(self, exp_id: int, status: str = "finished") -> None:
        self.db.execute("UPDATE experiments SET status=?, finished_at=? WHERE id=?", (status, time.time(), exp_id))
        self.db.commit()

    def experiments(self) -> list[dict[str, Any]]:
        rows = self.db.execute(
            "SELECT e.*, (SELECT COUNT(*) FROM universes u WHERE u.experiment_id=e.id) AS n_universes, "
            "(SELECT COUNT(*) FROM discoveries d WHERE d.experiment_id=e.id) AS n_discoveries "
            "FROM experiments e ORDER BY e.id DESC"
        ).fetchall()
        return [self._exp(r) for r in rows]

    def experiment(self, exp_id: int) -> dict[str, Any] | None:
        r = self.db.execute("SELECT * FROM experiments WHERE id=?", (exp_id,)).fetchone()
        return self._exp(r) if r else None

    @staticmethod
    def _exp(r: sqlite3.Row) -> dict[str, Any]:
        d = dict(r)
        d["config"] = json.loads(d["config"])
        d["environment"] = json.loads(d["environment"])
        return d

    # ---------------------------------------------------------- universes
    def add_universe(self, exp_id: int, generation: int, role: str, parent_id: int | None, spec: dict,
                     steps: int, window: int, obs: dict) -> int:
        cur = self.db.execute(
            "INSERT INTO universes(experiment_id, generation, role, parent_id, rule, spec, steps, window, class, "
            "metrics, descriptor, timeseries, final_hash, final_state, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (exp_id, generation, role, parent_id, spec["physics"]["rule"], json.dumps(spec), steps, window,
             obs["cls"], json.dumps(obs["metrics"]), json.dumps(obs["descriptor"]), json.dumps(obs["timeseries"]),
             obs["final_hash"], pack_state(obs["final_state"]), time.time()),
        )
        return int(cur.lastrowid)

    def set_rankings(self, rows: list[tuple[float, int | None, int | None, str | None, int]]) -> None:
        self.db.executemany("UPDATE universes SET novelty=?, pareto_rank=?, priority=?, aggregate=? WHERE id=?", rows)

    def commit(self) -> None:
        self.db.commit()

    _LIST_COLS = ("id, experiment_id, generation, role, parent_id, rule, spec, steps, class, metrics, "
                  "descriptor, novelty, pareto_rank, priority, aggregate, final_hash")

    def universes(self, exp_id: int, role: str | None = None, with_state: bool = False) -> list[dict[str, Any]]:
        cols = self._LIST_COLS + (", final_state" if with_state else "")
        q, args = f"SELECT {cols} FROM universes WHERE experiment_id=?", [exp_id]
        if role:
            q += " AND role=?"
            args.append(role)
        return [self._univ(r) for r in self.db.execute(q + " ORDER BY id", args).fetchall()]

    def universe(self, uid: int) -> dict[str, Any] | None:
        r = self.db.execute("SELECT * FROM universes WHERE id=?", (uid,)).fetchone()
        return self._univ(r) if r else None

    @staticmethod
    def _univ(r: sqlite3.Row) -> dict[str, Any]:
        d = dict(r)
        for k in ("spec", "metrics", "descriptor", "timeseries", "aggregate"):
            if k in d and d[k] is not None:
                d[k] = json.loads(d[k])
        if "final_state" in d and d["final_state"] is not None:
            spec = d["spec"]
            d["final_state"] = unpack_state(d["final_state"], spec["height"], spec["width"])
        return d

    def children(self, uid: int) -> list[dict[str, Any]]:
        rows = self.db.execute(f"SELECT {self._LIST_COLS} FROM universes WHERE parent_id=? ORDER BY id", (uid,))
        return [self._univ(r) for r in rows.fetchall()]

    # ---------------------------------------------------------- discoveries
    def add_discovery(self, exp_id: int, uid: int, kind: str, summary: str, evidence: dict) -> int:
        cur = self.db.execute(
            "INSERT INTO discoveries(experiment_id, universe_id, kind, summary, evidence, created_at) VALUES (?,?,?,?,?,?)",
            (exp_id, uid, kind, summary, json.dumps(evidence), time.time()),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def discoveries(self, exp_id: int | None = None) -> list[dict[str, Any]]:
        q = ("SELECT d.*, u.rule, u.class FROM discoveries d JOIN universes u ON u.id=d.universe_id")
        rows = (self.db.execute(q + " WHERE d.experiment_id=? ORDER BY d.id", (exp_id,)) if exp_id is not None
                else self.db.execute(q + " ORDER BY d.id"))
        out = []
        for r in rows.fetchall():
            d = dict(r)
            d["evidence"] = json.loads(d["evidence"])
            out.append(d)
        return out
