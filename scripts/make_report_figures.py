"""Figures, stills and GIF clips for the research report (docs/report.md).

Everything is regenerated from committed experiment exports (docs/data/experiments/) and
from deterministic simulations, so the report's pictures are reproducible.
Requires matplotlib and Pillow (pip install matplotlib pillow).

Usage: python scripts/make_report_figures.py [name ...]     (default: all)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

from emergence.engine import Universe, UniverseSpec  # noqa: E402
from emergence.observatory import continuous as C  # noqa: E402
from emergence.physics import parse_rule  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data" / "experiments"
OUT = ROOT / "docs" / "assets" / "report"
ORBIUM = "LENIA/R13/T10/m0.150/s0.0150/b1"
BLUE, ORANGE, GREY, GREEN, RED = "#2f6db5", "#e08a1e", "#8a8f98", "#3a9a5b", "#c8453c"
CMAP = matplotlib.colormaps["magma"]

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titleweight": "bold", "axes.titlesize": 12, "figure.dpi": 110,
                     "savefig.bbox": "tight", "savefig.dpi": 140})


def colour(state: np.ndarray) -> np.ndarray:
    """uint8 Lenia state -> RGB with a perceptual colour map (0 = black)."""
    return (CMAP(state / 255.0)[..., :3] * 255).astype(np.uint8)


def save_png(rgb: np.ndarray, name: str, scale: int = 3) -> None:
    Image.fromarray(rgb).resize((rgb.shape[1] * scale, rgb.shape[0] * scale), Image.NEAREST).save(OUT / name)


def save_gif(frames: list[np.ndarray], name: str, scale: int = 3, ms: int = 60) -> None:
    ims = [Image.fromarray(colour(f)).resize((f.shape[1] * scale, f.shape[0] * scale), Image.NEAREST)
           .convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    ims[0].save(OUT / name, save_all=True, append_images=ims[1:], duration=ms, loop=0, optimize=True)


def run_frames(physics, state, steps: int, every: int) -> list[np.ndarray]:
    u, out = Universe(physics, state), [state.copy()]
    for t in range(1, steps + 1):
        u.step()
        if t % every == 0:
            out.append(u.state.copy())
    return out


# ------------------------------------------------------------------ figures
def static_vs_glider() -> None:
    """The J-012 bug in one picture: a static blob field (old label: complex) vs gliders."""
    orb = parse_rule(ORBIUM)
    soup = Universe.from_spec(UniverseSpec(orb.to_dict(), 1, 128, 128, 0.35))
    soup.step(1000)
    a = soup.state.copy()
    soup.step(100)
    b = soup.state.copy()
    gl = C.emergent_glider(orb)
    two = np.maximum(np.roll(gl, (-32, -60), axis=(0, 1)), np.roll(gl, (32, -60), axis=(0, 1)))
    g = run_frames(orb, two, 100, 100)
    fig, ax = plt.subplots(1, 4, figsize=(13, 3.6))
    panels = [(a, "Blob field, t = 1000"), (b, "Same field, t = 1100"),
              ((np.abs(b.astype(int) - a.astype(int)) > 32).astype(np.uint8) * 255, "Cells changed > 32 levels"),
              (np.maximum(g[0], g[-1]), "2 gliders, each at t=0 (left), t=100")]
    for axis, (img, title) in zip(ax, panels):
        axis.imshow(img, cmap="magma" if "changed" not in title else "Greys_r", vmin=0, vmax=255)
        axis.set_title(title, fontsize=10)
        axis.axis("off")
    fig.suptitle("Old label: both 'complex'.  New label: blob field = quasi-static, gliders = complex", y=1.02)
    fig.savefig(OUT / "static-vs-glider.png")
    plt.close(fig)
    save_gif(run_frames(orb, two, 240, 3), "gliders.gif", scale=2, ms=40)
    u = Universe.from_spec(UniverseSpec(orb.to_dict(), 1, 96, 96, 0.35))
    save_gif(run_frames(orb, u.state.copy(), 600, 6), "orbium-soup.gif", scale=3, ms=50)


def labels_before_after() -> None:
    d = json.load(open(DATA / "2026-11-06-c01-lenia-static-fields.json"))["part2_random_rules"]
    order = ["complex", "active", "chaotic", "extinct"]
    old = [d["old_classes"].get(k, 0) for k in order]
    qs = d["new_quasi_static_not_extinct"]
    new_active = d["new_classes"].get("active", 0)
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    y = [1, 0]
    left = 0
    for k, v in zip(order, old):
        ax.barh(1, v, left=left, color={"complex": RED, "active": BLUE, "chaotic": ORANGE, "extinct": GREY}[k])
        if v >= 4:
            ax.text(left + v / 2, 1, f"{k}\n{v}", ha="center", va="center", color="white", fontsize=9)
        left += v
    segs = [("complex", d["new_classes"].get("complex", 0), RED), ("quasi-static", qs, "#6c8ebf"),
            ("active", new_active - qs, BLUE), ("chaotic", d["new_classes"].get("chaotic", 0), ORANGE),
            ("extinct", d["new_classes"].get("extinct", 0), GREY)]
    left = 0
    for k, v, c in segs:
        ax.barh(0, v, left=left, color=c, label=k)
        if v >= 4:
            ax.text(left + v / 2, 0, f"{k}\n{v}", ha="center", va="center", color="white", fontsize=9)
        left += v
    ax.set_yticks(y, ["old label", "new label"])
    ax.set_xlabel("random Lenia rules (of 60)")
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.25), frameon=False, fontsize=9)
    ax.set_title("Same 60 random Lenia rules: 27 'complex' before the fix, 0 after (none has a mover)")
    fig.savefig(OUT / "labels-before-after.png")
    plt.close(fig)


def viability_map() -> None:
    d = json.load(open(DATA / "2026-11-07-e13a-glider-viability.json"))["grid"]
    mus = sorted({r["mu"] for r in d})
    ratios = sorted({round(r["sigma"] / r["mu"], 2) for r in d})
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for r in d:
        x, y = r["mu"], r["sigma"] / r["mu"]
        if r["viable"]:
            ax.scatter(x, y, s=170, color=GREEN, edgecolor="black", zorder=3)
        else:
            ax.scatter(x, y, s=40, color="#d9dce1", zorder=2)
    ax.scatter([0.15], [0.10], s=420, facecolor="none", edgecolor=RED, lw=2, zorder=4, label="Orbium (Chan 2019)")
    ax.set_xlabel("growth centre μ")
    ax.set_ylabel("growth width σ / μ")
    sp = [r["speed"] for r in d if r["viable"]]
    ax.set_title(f"Where can a glider exist? {len(sp)} of {len(d)} single-ring rules (green)\n"
                 f"speeds {min(sp):.2f}-{max(sp):.2f} cells/step; grey = no glider from 8 seed shapes",
                 fontsize=11)
    ax.legend(loc="upper right", frameon=False)
    ax.set_xticks(mus[::2])
    ax.set_yticks(ratios)
    fig.savefig(OUT / "viability-map.png")
    plt.close(fig)


def e12_engine_vs_random() -> None:
    """E-12 numbers (from runs/e12.db, summarised in journal J-013; the export holds the curves)."""
    cats = ["self-propelled\nrules", "'complex' on\nevery seed", "structured\n(raw)", "structured\n(near-duplicates\nremoved)",
            "rules in the\nglider island", "behaviour\nniches"]
    engine = [0, 0, 103, 58, 59, 11]
    random = [0, 0, 27, 27, 9, 9]
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=(10, 3.8))
    b1 = ax.bar(x - 0.2, engine, 0.4, color=BLUE, label="discovery engine")
    b2 = ax.bar(x + 0.2, random, 0.4, color=ORANGE, label="random search (same compute)")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{int(b.get_height())}", ha="center", fontsize=9)
    ax.set_xticks(x, cats, fontsize=9)
    ax.set_ylabel("count (of 500 rules per arm)")
    ax.legend(frameon=False)
    ax.set_title("E-12, Lenia: the engine finds more structure and the right region, but no rule makes gliders")
    fig.savefig(OUT / "e12-engine-vs-random.png")
    plt.close(fig)


E13_SEED = 2178225922393047501  # E-13 universes #104 (smooth:6, density 0.35) and #324 (smooth:3, 0.10)


def emergence_clip() -> None:
    """Same rule (Orbium), same seed, same total mass: soup vs smooth start (E-13 #104)."""
    orb = parse_rule(ORBIUM).to_dict()
    soup = Universe.from_spec(UniverseSpec(orb, E13_SEED, 128, 128, 0.35))
    smooth = Universe.from_spec(UniverseSpec(orb, E13_SEED, 128, 128, 0.35, init={"kind": "smooth", "ell": 6.0}))
    frames, stills = [], {}
    for t in range(0, 2001):
        if t % 20 == 0:
            sep = np.full((128, 4), 90, np.uint8)
            frames.append(np.concatenate([soup.state, sep, smooth.state], 1))
        if t in (0, 100, 400, 2000):
            stills[t] = (soup.state.copy(), smooth.state.copy())
        soup.step()
        smooth.step()
    save_gif(frames, "emergence-soup-vs-smooth.gif", scale=2, ms=70)
    fig, ax = plt.subplots(2, 4, figsize=(12, 6.4))
    for j, t in enumerate(sorted(stills)):
        for i, name in enumerate(("soup", "smooth start (ℓ = 6)")):
            ax[i, j].imshow(stills[t][i], cmap="magma", vmin=0, vmax=255)
            ax[i, j].set_xticks([])
            ax[i, j].set_yticks([])
            if i == 0:
                ax[i, j].set_title(f"t = {t}")
            if j == 0:
                ax[i, j].set_ylabel(name, fontsize=11)
    fig.suptitle("Orbium rule, same seed, same total mass: the soup freezes into blobs; "
                 "the smooth start collapses to one glider", y=0.99)
    fig.savefig(OUT / "emergence-soup-vs-smooth.png")
    plt.close(fig)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def e13_rates() -> None:
    tab = json.load(open(DATA / "2026-11-07-e13-movers.json"))["table"]
    conds = ["uniform", "smooth:3", "smooth:6", "smooth:10", "spots", "patches"]
    names = {"uniform": "soup", "smooth:3": "smooth ℓ=3", "smooth:6": "smooth ℓ=6", "smooth:10": "smooth ℓ=10",
             "spots": "spots", "patches": "Chan's patches"}
    fig, ax = plt.subplots(figsize=(10, 3.8))
    for k, (exp, lab, col) in enumerate(((1, "density 0.35", BLUE), (2, "density 0.10", ORANGE))):
        xs, ys, lo, hi = [], [], [], []
        for i, c in enumerate(conds):
            key = f"{exp}|{c}"
            if key not in tab:
                continue
            n, hits = tab[key]
            a, b = wilson(hits, n)
            xs.append(i + (k - 0.5) * 0.36)
            ys.append(hits / n)
            lo.append(hits / n - a)
            hi.append(b - hits / n)
            ax.text(xs[-1], b + 0.015, f"{hits}/{n}", ha="center", fontsize=8)
        ax.bar(xs, ys, 0.34, color=col, label=lab, yerr=[lo, hi], capsize=3, ecolor="#444")
    ax.set_xticks(range(len(conds)), [names[c] for c in conds])
    ax.set_ylabel("universes with a glider")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False)
    ax.set_title("E-13: gliders emerged only from smooth starts (8 glider-viable rules × 5 seeds; 95% intervals)")
    fig.savefig(OUT / "e13-glider-rates.png")
    plt.close(fig)


def e14_per_rule() -> None:
    d = json.load(open(DATA / "2026-11-07-e14-movers.json"))["per_rule"]
    arms = [("1|smooth:3", "smooth ℓ=3, density 0.10", ORANGE), ("2|smooth:6", "smooth ℓ=6, density 0.35", BLUE)]
    rules = [r["rule"] for r in d[arms[0][0]]]
    short = [f"μ {r.split('/')[3][1:]}\nσ {r.split('/')[4][1:]}" for r in rules]
    x = np.arange(len(rules))
    fig, ax = plt.subplots(figsize=(10.5, 3.9))
    for k, (key, lab, col) in enumerate(arms):
        rows = d[key]
        y = [r["gliders"] / r["n"] for r in rows]
        lo = [yy - r["ci95"][0] for yy, r in zip(y, rows)]
        hi = [r["ci95"][1] - yy for yy, r in zip(y, rows)]
        ax.bar(x + (k - 0.5) * 0.38, y, 0.36, color=col, label=lab, yerr=[lo, hi], capsize=3, ecolor="#444")
    ax.axhline(0, color="black", lw=0.8)
    ax.text(len(rules) - 0.6, 0.66, "soup with the same mass: 0 of 160 at both densities", ha="right", fontsize=9.5,
            color=RED, fontweight="bold")
    ax.set_xticks(x, short, fontsize=9)
    ax.set_xlabel("rule (growth centre μ, width σ)")
    ax.set_ylabel("universes with a glider")
    ax.set_ylim(0, 0.72)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.12, 0.98))
    ax.set_title("E-14 (pre-registered, fresh seeds): gliders arise from smooth starts in 6 of 8 rules, never from soup")
    fig.savefig(OUT / "e14-per-rule.png")
    plt.close(fig)


FIGS = {"e14_per_rule": e14_per_rule, "static_vs_glider": static_vs_glider, "labels_before_after": labels_before_after,
        "viability_map": viability_map, "e12_engine_vs_random": e12_engine_vs_random,
        "emergence_clip": emergence_clip, "e13_rates": e13_rates}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or list(FIGS):
        FIGS[name]()
        print("wrote", name)


if __name__ == "__main__":
    main()
