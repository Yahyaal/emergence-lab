"""Export experiments from a lab database into compact JSON for the research journal.

The SQLite databases are not committed (they are large and fully reproducible from
the command + commit). This script keeps what the journal needs: config,
environment, per-generation curves, and every discovery with its evidence.

Usage:
    python scripts/journal_export.py lab.db 1 2 3 --label r1-baseline --commit b77f873 \
        --command "emergence explore ... " --out docs/data/experiments/r1-baseline.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from emergence.analysis import experiment_summary
from emergence.storage import Store

KEEP_EVIDENCE = ["evidence_level", "evidence_level_name", "innovation_verdict", "innovation_noise_floor",
                 "persists", "torus_loop", "descriptor_spread", "robust_threshold", "spread_pct_within",
                 "spread_pct_between", "niche", "pareto_rank", "novelty", "replicate_classes", "extended_class"]


def export(db: str, ids: list[int], label: str, commit: str, command: str) -> dict:
    st = Store(db)
    out = {"label": label, "code_commit": commit, "command": command, "experiments": []}
    for i in ids:
        exp = st.experiment(i)
        summ = experiment_summary(st, i)
        discs = []
        for d in st.discoveries(i):
            ev = d["evidence"]
            rep = ev.get("replication") or {}
            inn = ev.get("innovation") or {}
            discs.append({
                "universe_id": d["universe_id"], "rule": d["rule"], "class": d["class"], "kind": d["kind"],
                "spec": st.universe(d["universe_id"])["spec"], "summary": d["summary"],
                "evidence": {k: ev.get(k) for k in KEEP_EVIDENCE if k in ev},
                "replication": {k: rep.get(k) for k in ("tested", "self_replicators", "rule_level_duplication",
                                                         "common_products", "explosive")} if rep else None,
                "innovation": {k: inn.get(k) for k in ("steps", "shapes_total", "new_second_half",
                                                        "established_late", "new_per_sample")} if inn else None,
            })
        out["experiments"].append({
            "id": i, "name": exp["name"], "master_seed": exp["master_seed"], "status": exp["status"],
            "config": exp["config"], "environment": exp["environment"],
            "selection": summ["selection"], "final": summ["final"], "curve": summ["curve"],
            "discoveries": discs,
        })
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("db")
    ap.add_argument("ids", type=int, nargs="+")
    ap.add_argument("--label", required=True)
    ap.add_argument("--commit", required=True, help="git commit the experiment ran on")
    ap.add_argument("--command", required=True, help="exact command(s) used")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = export(a.db, a.ids, a.label, a.commit, a.command)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(data, indent=1, default=str))
    print(f"wrote {a.out}")
