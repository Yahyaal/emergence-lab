import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import numpy as np

from emergence.discovery import ExploreConfig, Explorer, novelty_scores, pareto_ranks, reproduce
from emergence.server import FrameCache, make_handler
from emergence.storage import Store


def test_pareto_ranks():
    obj = np.array([[1, 0], [0, 1], [0.5, 0.5], [0.2, 0.2], [0, 0]])
    assert pareto_ranks(obj).tolist() == [0, 0, 0, 1, 2]


def test_novelty_outlier_scores_highest():
    d = np.array([[0, 0], [0.01, 0], [0, 0.01], [1, 1]])
    assert int(np.argmax(novelty_scores(d, k=2))) == 3


def small_cfg(seed=7):
    return ExploreConfig(population=12, generations=2, steps=120, window=60, width=32, height=32,
                         followups=2, followup_seeds=1, seed=seed, workers=1)


def run_exp(path, seed=7):
    store = Store(path)
    eid = Explorer(store, small_cfg(seed), log=lambda *_: None).run()
    return store, eid


def test_exploration_is_deterministic(tmp_path):
    s1, e1 = run_exp(tmp_path / "a.db")
    s2, e2 = run_exp(tmp_path / "b.db")
    key = lambda s, e: [(u["rule"], u["spec"]["seed"], u["final_hash"], u["priority"]) for u in s.universes(e)]
    assert key(s1, e1) == key(s2, e2)
    assert len(s1.universes(e1, role="explore")) == 24
    assert [d["summary"] for d in s1.discoveries(e1)] == [d["summary"] for d in s2.discoveries(e2)]


def test_reproduce_and_server(tmp_path):
    store, eid = run_exp(tmp_path / "c.db")
    u = store.universes(eid)[3]
    r = reproduce(store, u["id"])
    assert r["hash_match"] and not r["metric_diffs"]

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store, FrameCache()))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    get = lambda p: json.loads(urllib.request.urlopen(base + p).read())
    try:
        assert get("/api/experiments")[0]["id"] == eid
        exp = get(f"/api/experiment/{eid}")
        assert len(exp["universes"]) == len(store.universes(eid))
        det = get(f"/api/universe/{u['id']}")
        assert det["rule"] == u["rule"] and "lineage" in det
        # replayed final frame must equal the stored final state
        fr = get(f"/api/frames?id={u['id']}&start={u['steps']}&count=1")
        import base64
        frame = np.frombuffer(base64.b64decode(fr["frames"]), np.uint8).reshape(32, 32)
        assert np.array_equal(frame, store.universe(u["id"])["final_state"])
        a = get("/api/frames?rule=B3/S23&seed=1&w=16&start=0&count=5")
        assert a["count"] == 5 and a["width"] == 16
        assert urllib.request.urlopen(base + "/").status == 200
    finally:
        httpd.shutdown()
