"""Regenerate the journal's videos and stills from docs/_data/media.json.

For every item it writes, into docs/assets/media/:
  <id>.mp4        the run (h264), nearest-neighbour upscaled
  <id>.png        a time-lapse strip of 5 frames (t = 0, 1/4, 1/2, 3/4, end)
  <id>-poster.png the final frame (video poster)

Requires ffmpeg on PATH and Pillow (pip install pillow). Deterministic: the same
spec always yields the same frames (the encoded file bytes may differ by ffmpeg version).

Usage: python scripts/make_media.py [id ...]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from emergence.engine import Universe, UniverseSpec
from emergence.physics import OuterTotalistic

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "media"


def palette(n: int) -> np.ndarray:
    """Same colours as the dashboard: vacuum dark, alive light, dying states fade orange."""
    pal = [(16, 17, 19), (242, 239, 230)]
    for s in range(2, max(n, 2)):
        f = (s - 2) / max(1, n - 3)
        pal.append((round(235 - 165 * f), round(104 - 60 * f), round(52 - 10 * f)))
    return np.array(pal, np.uint8)


def rle(s: str) -> np.ndarray:
    rows, row = [], []
    for n, ch in re.findall(r"(\d*)([bo$!])", s):
        n = int(n or 1)
        if ch in "bo":
            row += [1 if ch == "o" else 0] * n
        else:
            rows.append(row)
            if ch == "$":
                rows += [[] for _ in range(n - 1)]
            row = []
    w = max(len(r) for r in rows)
    return np.array([r + [0] * (w - len(r)) for r in rows], np.uint8)


def make_universe(item: dict) -> Universe:
    if item["kind"] == "universe":
        return Universe.from_spec(UniverseSpec.from_dict(item["spec"]))
    pat = rle(item["rle"])
    side = item["side"]
    g = np.zeros((side, side), np.uint8)
    r0, c0 = side // 2 - pat.shape[0] // 2, side // 2 - pat.shape[1] // 2
    if "gun" in item["id"]:
        r0, c0 = 8, 8
    g[r0:r0 + pat.shape[0], c0:c0 + pat.shape[1]] = pat
    return Universe(OuterTotalistic.parse(item["rule"]), g)


def frames_of(item: dict) -> list[np.ndarray]:
    u = make_universe(item)
    out = [u.state.copy()]
    for t in range(1, item["steps"] + 1):
        u.step()
        if t % item["stride"] == 0 or t == item["steps"]:
            out.append(u.state.copy())
    return out, u.physics.num_states


def render(state: np.ndarray, pal: np.ndarray, scale: int) -> np.ndarray:
    img = pal[np.minimum(state, len(pal) - 1)]
    return np.kron(img, np.ones((scale, scale, 1), np.uint8))


def build(item: dict) -> None:
    frames, n = frames_of(item)
    pal, scale = palette(n), item["scale"]
    h, w = frames[0].shape[0] * scale, frames[0].shape[1] * scale
    # video
    mp4 = OUT / f"{item['id']}.mp4"
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{w}x{h}", "-r", "24", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                             "-crf", "28", "-preset", "slow", "-movflags", "+faststart", str(mp4)],
                            stdin=subprocess.PIPE)
    for f in frames:
        proc.stdin.write(render(f, pal, scale).tobytes())
    proc.stdin.close()
    proc.wait()
    # poster + time-lapse strip with time labels
    Image.fromarray(render(frames[-1], pal, scale)).save(OUT / f"{item['id']}-poster.png", optimize=True)
    idx = [0, len(frames) // 4, len(frames) // 2, 3 * len(frames) // 4, len(frames) - 1]
    small = max(2, scale // 2)
    tiles = [render(frames[i], pal, small) for i in idx]
    gap, label_h = 6, 18
    th, tw = tiles[0].shape[:2]
    strip = Image.new("RGB", (len(tiles) * tw + (len(tiles) - 1) * gap, th + label_h), (250, 250, 248))
    draw = ImageDraw.Draw(strip)
    for k, (i, tile) in enumerate(zip(idx, tiles)):
        x = k * (tw + gap)
        strip.paste(Image.fromarray(tile), (x, label_h))
        t = min(i * item["stride"], item["steps"])
        draw.text((x + 2, 3), f"t = {t}", fill=(60, 60, 58))
    strip.save(OUT / f"{item['id']}.png", optimize=True)
    print(f"{item['id']}: {len(frames)} frames, {mp4.stat().st_size // 1024} KB video")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "docs" / "_data" / "media.json").read_text())
    want = set(sys.argv[1:])
    for item in manifest["items"]:
        if not want or item["id"] in want:
            build(item)
