"""Build inline-SVG figures for the journal from exported experiment data.

Writes docs/_includes/fig-baseline.svg (included inline by Jekyll so it follows the
page's light/dark colours). Usage: python scripts/make_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def panel(x0, y0, w, h, runs, key, title, ymax):
    out = [f'<g transform="translate({x0},{y0})">', f'<text x="0" y="-10" class="label">{title}</text>']
    gens = max(len(r["curve"]) for r in runs)
    X = lambda g: g / (gens - 1) * w  # noqa: E731
    Y = lambda v: h - v / ymax * h  # noqa: E731
    for t in range(0, ymax + 1, max(1, ymax // 4)):
        out.append(f'<g class="grid"><line x1="0" x2="{w}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/></g>'
                   f'<text x="-6" y="{Y(t) + 4:.1f}" text-anchor="end">{t}</text>')
    for g in range(gens):
        out.append(f'<text x="{X(g):.1f}" y="{h + 18}" text-anchor="middle">{g}</text>')
    out.append(f'<text x="{w / 2}" y="{h + 36}" text-anchor="middle">generation</text>')
    for r in runs:
        cls = r["selection"]
        dash = " seed2" if r["master_seed"] == 12 else ""
        pts = [(X(c["generation"]), Y(c[key]), c[key], c["generation"]) for c in r["curve"]]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, _, _ in pts)
        out.append(f'<path class="{"engine" if cls == "engine" else "random"}{dash}" d="{d}"/>')
        for x, y, v, g in pts:
            out.append(f'<circle class="{cls}-dot" cx="{x:.1f}" cy="{y:.1f}" r="4"><title>{cls} search, seed '
                       f'{r["master_seed"]}, generation {g}: {v}</title></circle>')
        x, y, v, _ = pts[-1]
        out.append(f'<text x="{x + 8:.1f}" y="{y + 4:.1f}">{v}</text>')
    out.append("</g>")
    return "\n".join(out)


def baseline():
    data = json.loads((ROOT / "docs/data/experiments/2026-11-05-r1-baseline.json").read_text())
    runs = data["experiments"]
    W, H, pw, ph = 900, 300, 340, 190
    svg = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Cumulative rules found per generation, '
           f'discovery engine versus random search, two seeds each">']
    svg.append(panel(50, 40, pw, ph, runs, "self_propelled", "Rules with self-propelled shapes (cumulative)", 100))
    svg.append(panel(510, 40, pw, ph, runs, "complex_all_seeds", "Rules 'complex' on every seed (cumulative)", 60))
    svg.append("</svg>")
    (ROOT / "docs/_includes").mkdir(exist_ok=True)
    (ROOT / "docs/_includes/fig-baseline.svg").write_text("\n".join(svg))
    print("wrote docs/_includes/fig-baseline.svg")


if __name__ == "__main__":
    baseline()
