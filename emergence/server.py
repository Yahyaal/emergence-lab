"""Local dashboard server (standard library only).

Frames are always produced by the same Python engine that ran the experiment,
replayed deterministically from the stored spec, so what you watch is exactly
what was measured.
"""
from __future__ import annotations

import base64
import json
import mimetypes
import threading
from collections import OrderedDict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

from .discovery import OBJECTIVES
from .engine import Universe, UniverseSpec
from .observatory import CLASS_HELP, CLASSES, DESCRIPTOR_FIELDS
from .physics import parse_rule, physics_from_dict
from .storage import Store

WEB = Path(__file__).parent / "web"
MAX_FRAMES = 400
MAX_SIDE = 512


class FrameCache:
    """Keeps recently used universes alive so sequential chunk requests are cheap."""

    def __init__(self, size: int = 256):
        self.size = size
        self.items: OrderedDict[str, Universe] = OrderedDict()
        self.lock = threading.Lock()

    def frames(self, spec: UniverseSpec, start: int, count: int) -> list[np.ndarray]:
        key = json.dumps(spec.to_dict(), sort_keys=True)
        with self.lock:
            u = self.items.pop(key, None)
        if u is None or u.t > start:
            u = Universe.from_spec(spec)
        u.step(start - u.t)
        out = [np.array(u.state)]
        for _ in range(count - 1):
            u.step()
            out.append(np.array(u.state))
        with self.lock:
            self.items[key] = u
            while len(self.items) > self.size:
                self.items.popitem(last=False)
        return out


def b64(a: np.ndarray) -> str:
    return base64.b64encode(np.ascontiguousarray(a, dtype=np.uint8).tobytes()).decode()


def make_handler(store: Store, cache: FrameCache):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # quiet
            pass

        def _json(self, obj, status=HTTPStatus.OK):
            body = json.dumps(obj).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _file(self, path: Path):
            if not path.is_file() or WEB not in path.resolve().parents:
                return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            body = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802
            url = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            parts = [p for p in url.path.split("/") if p]
            try:
                if not parts:
                    return self._file(WEB / "index.html")
                if parts[0] == "static":
                    return self._file(WEB / "/".join(parts[1:]))
                if parts[0] != "api":
                    return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
                return self._api(parts[1:], q)
            except (KeyError, ValueError) as e:
                return self._json({"error": str(e)}, HTTPStatus.BAD_REQUEST)

        def _api(self, parts, q):
            what = parts[0] if parts else ""
            if what == "meta":
                return self._json({"classes": CLASSES, "class_help": CLASS_HELP,
                                   "descriptor_fields": DESCRIPTOR_FIELDS, "objectives": list(OBJECTIVES)})
            if what == "experiments":
                return self._json(store.experiments())
            if what == "experiment":
                eid = int(parts[1])
                exp = store.experiment(eid)
                if exp is None:
                    return self._json({"error": "no such experiment"}, HTTPStatus.NOT_FOUND)
                univ = store.universes(eid, with_state=True)
                for u in univ:
                    u["thumb"] = b64(u.pop("final_state"))
                return self._json({"experiment": exp, "universes": univ, "discoveries": store.discoveries(eid)})
            if what == "universe":
                u = store.universe(int(parts[1]))
                if u is None:
                    return self._json({"error": "no such universe"}, HTTPStatus.NOT_FOUND)
                u.pop("final_state", None)
                lineage, p = [], u["parent_id"]
                while p is not None and len(lineage) < 50:
                    pu = store.universe(p)
                    if pu is None:
                        break
                    lineage.append({"id": pu["id"], "rule": pu["rule"], "class": pu["class"],
                                    "generation": pu["generation"], "role": pu["role"]})
                    p = pu["parent_id"]
                u["lineage"] = lineage
                u["children"] = [{"id": c["id"], "rule": c["rule"], "class": c["class"], "role": c["role"],
                                  "size": c["spec"]["width"], "steps": c["steps"]} for c in store.children(u["id"])]
                return self._json(u)
            if what == "frames":
                if "id" in q:
                    u = store.universe(int(q["id"]))
                    if u is None:
                        return self._json({"error": "no such universe"}, HTTPStatus.NOT_FOUND)
                    spec = UniverseSpec.from_dict(u["spec"])
                else:
                    rule = parse_rule(q["rule"])
                    w, h = int(q.get("w", 64)), int(q.get("h", q.get("w", 64)))
                    if not (4 <= w <= MAX_SIDE and 4 <= h <= MAX_SIDE):
                        raise ValueError("size out of range")
                    spec = UniverseSpec(rule.to_dict(), int(q.get("seed", 1)), w, h, float(q.get("density", 0.35)))
                start = max(0, int(q.get("start", 0)))
                count = min(MAX_FRAMES, max(1, int(q.get("count", 100))))
                frames = cache.frames(spec, start, count)
                n_states = physics_from_dict(spec.physics).num_states
                return self._json({"start": start, "count": len(frames), "width": spec.width, "height": spec.height,
                                   "num_states": n_states, "rule": spec.physics["rule"], "spec": spec.to_dict(),
                                   "frames": b64(np.stack(frames))})
            if what == "discoveries":
                return self._json(store.discoveries())
            return self._json({"error": "unknown endpoint"}, HTTPStatus.NOT_FOUND)

    return Handler


def serve(db_path: str, host: str = "127.0.0.1", port: int = 8000) -> None:
    store = Store(db_path)
    httpd = ThreadingHTTPServer((host, port), make_handler(store, FrameCache()))
    print(f"Dashboard: http://{host}:{port}   (database: {db_path})  Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
