"""Command line interface: ``emergence <command>`` (or ``python -m emergence``)."""
from __future__ import annotations

import argparse
import json
import sys
import time

from .discovery import ExploreConfig, Explorer, reproduce
from .engine import UniverseSpec
from .lab import study
from .physics import OuterTotalistic
from .storage import Store

DEFAULT_DB = "lab.db"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="emergence", description="Artificial-universe explorer")
    ap.add_argument("--db", default=DEFAULT_DB, help="SQLite lab notebook (default: lab.db)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("explore", help="run an automated exploration experiment")
    d = ExploreConfig()
    ex.add_argument("--name", default=d.name)
    ex.add_argument("--universes", type=int, default=d.population, help="universes per generation")
    ex.add_argument("--generations", type=int, default=d.generations)
    ex.add_argument("--steps", type=int, default=d.steps)
    ex.add_argument("--size", type=int, default=d.width, help="grid side length")
    ex.add_argument("--seed", type=int, default=d.seed, help="master random seed")
    ex.add_argument("--workers", type=int, default=d.workers, help="processes (0 = all cores, 1 = no multiprocessing)")
    ex.add_argument("--followups", type=int, default=d.followups, help="candidates to re-test for robustness")

    sub.add_parser("list", help="list experiments")

    top = sub.add_parser("top", help="show highest-priority universes of an experiment")
    top.add_argument("experiment", type=int)
    top.add_argument("-n", type=int, default=15)

    disc = sub.add_parser("discoveries", help="list recorded discoveries")
    disc.add_argument("experiment", type=int, nargs="?")

    rep = sub.add_parser("reproduce", help="re-run stored universes and verify the record")
    rep.add_argument("ids", type=int, nargs="+")

    ob = sub.add_parser("observe", help="observe one rule, e.g. B3/S23")
    ob.add_argument("rule")
    ob.add_argument("--seed", type=int, default=1)
    ob.add_argument("--size", type=int, default=64)
    ob.add_argument("--density", type=float, default=0.35)
    ob.add_argument("--steps", type=int, default=500)

    exp = sub.add_parser("export", help="export an experiment as JSON")
    exp.add_argument("experiment", type=int)
    exp.add_argument("out")

    sv = sub.add_parser("serve", help="start the dashboard")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8000)

    a = ap.parse_args(argv)

    if a.cmd == "serve":
        from .server import serve
        serve(a.db, a.host, a.port)
        return 0
    if a.cmd == "observe":
        rule = OuterTotalistic.parse(a.rule)
        t = time.time()
        o = study(UniverseSpec(rule.to_dict(), a.seed, a.size, a.size, a.density), steps=a.steps)
        print(json.dumps({"rule": rule.label(), "class": o.cls, "final_hash": o.final_hash, "metrics": o.metrics},
                         indent=2, default=str))
        print(f"({time.time() - t:.2f}s)", file=sys.stderr)
        return 0

    store = Store(a.db)
    if a.cmd == "explore":
        cfg = ExploreConfig(name=a.name, population=a.universes, generations=a.generations, steps=a.steps,
                            width=a.size, height=a.size, seed=a.seed, workers=a.workers, followups=a.followups)
        t = time.time()
        eid = Explorer(store, cfg).run()
        print(f"done: experiment #{eid} in {time.time() - t:.1f}s. View with: emergence --db {a.db} serve")
    elif a.cmd == "list":
        for e in store.experiments():
            print(f"#{e['id']:<4} {e['name']:<20} {e['status']:<9} seed={e['master_seed']:<8} "
                  f"universes={e['n_universes']:<5} discoveries={e['n_discoveries']}")
    elif a.cmd == "top":
        rows = sorted((u for u in store.universes(a.experiment, role="explore") if u["priority"]),
                      key=lambda u: u["priority"])[: a.n]
        print(f"{'prio':>4} {'id':>5} {'rule':<18} {'class':<9} {'front':>5} {'novelty':>7} {'activity':>8} "
              f"{'movers':>6} {'vocab':>5}")
        for u in rows:
            m = u["metrics"]
            print(f"{u['priority']:>4} {u['id']:>5} {u['rule']:<18} {u['class']:<9} "
                  f"{'-' if u['pareto_rank'] is None else u['pareto_rank']:>5} {u['novelty']:>7.3f} "
                  f"{m['activity_late']:>8.4f} {m.get('mover_events', 0):>6.0f} {m.get('vocabulary', 0):>5.0f}")
    elif a.cmd == "discoveries":
        for dsc in store.discoveries(a.experiment):
            print(f"[{dsc['kind']}] universe #{dsc['universe_id']}: {dsc['summary']}")
    elif a.cmd == "reproduce":
        ok = True
        for uid in a.ids:
            r = reproduce(store, uid)
            good = r["hash_match"] and not r["metric_diffs"]
            ok &= good
            print(f"#{uid} {r['rule']}: {'REPRODUCED' if good else 'MISMATCH'} (final state hash "
                  f"{'matches' if r['hash_match'] else 'differs'}; {len(r['metric_diffs'])} metric differences)")
            for k, (v, w) in r["metric_diffs"].items():
                print(f"    {k}: stored={v} fresh={w}")
        return 0 if ok else 1
    elif a.cmd == "export":
        data = {"experiment": store.experiment(a.experiment),
                "universes": store.universes(a.experiment),
                "discoveries": store.discoveries(a.experiment)}
        with open(a.out, "w") as f:
            json.dump(data, f, indent=1, default=str)
        print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
