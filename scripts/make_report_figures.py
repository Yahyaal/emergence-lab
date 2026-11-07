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
def e27_births() -> None:
    """Birth detector (J-032): a Gray-Scott spot dividing vs a Lenia blob bursting into a labyrinth,
    and their copy counts over time (the doubling rule)."""
    from emergence.engine import UniverseSpec
    from emergence.observatory import births as B
    from emergence.physics import GrayScott
    gs = GrayScott()
    st = gs.seed_spot((128, 128))
    for _ in range(1000):
        st = gs.step(st)
    o = max(B.find(gs, st), key=lambda o: o["mass"])
    w_gs = B.alone(gs, st, o["mask"], 160, 4)
    spec = UniverseSpec({"kind": "lenia", "rule": "LENIA/R13/T10/m0.150/s0.0195/b1"}, 1497778031414372656,
                        128, 128, 0.1, init={"kind": "smooth", "ell": 3.0})
    u = Universe.from_spec(spec)
    u.step(1999)
    lst = np.array(u.state)
    lo = min(B.find(u.physics, lst), key=lambda o: abs(o["mass"] - 71.83))
    w_lab = B.alone(u.physics, lst, lo["mask"], 160, 4)
    for ph, w, name, steps, every in ((gs, w_gs, "e27-gray-scott.gif", 4000, 40), (u.physics, w_lab, "e27-labyrinth.gif", 1500, 15)):
        fr, cur = [], w
        for t in range(steps + 1):
            if t % every == 0:
                fr.append(B.field(ph, cur))
            if t < steps:
                cur = ph.step(cur)
        save_gif(fr, name, scale=2, ms=50)
    s_gs, _, _ = B.copy_series(gs, w_gs, max(B.find(gs, w_gs), key=lambda o: o["mass"]), 4000, 50)
    s_lab, _, _ = B.copy_series(u.physics, w_lab, max(B.find(u.physics, w_lab), key=lambda o: o["mass"]), 4000, 50)
    fig, ax = plt.subplots(figsize=(7, 3.4))
    t = np.arange(len(s_gs)) * 50
    ax.plot(t, s_gs, color=BLUE, lw=2, label="Gray-Scott spot: keeps doubling (reproducer)")
    ax.plot(np.arange(len(s_lab)) * 50, s_lab, color=ORANGE, lw=2, label="Lenia blob: bursts, then stops (not a reproducer)")
    ax.axvspan(0, 1000, color=GREY, alpha=0.12)
    ax.text(500, 120, "first quarter", ha="center", fontsize=9, color=GREY)
    ax.set_yscale("symlog", linthresh=1)
    ax.set_yticks([0, 1, 2, 4, 8, 16, 32, 64, 128])
    ax.set_yticklabels(["0", "1", "2", "4", "8", "16", "32", "64", "128"])
    ax.set_ylim(0, 200)
    ax.set_xlabel("steps alone in an empty world")
    ax.set_ylabel("copies (mass within 2x of parent)")
    ax.legend(frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=1)
    fig.savefig(OUT / "e27-copy-counts.png")
    plt.close(fig)


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
                 f"speeds {min(sp):.2f}-{max(sp):.2f} cells/step; grey = no glider from 12 seed shapes",
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
FUSION_SEED = 806560575985726156  # E-19 universe #204 (smooth:3, density 0.10)


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


def e15_fates() -> None:
    d = json.load(open(DATA / "2026-11-07-e15-glider-population.json"))["runs"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.9), gridspec_kw={"width_ratios": [1.5, 1]})
    for r in d:
        t = [s["t"] for s in r["series"]]
        m = [max(s["mass"], 1) for s in r["series"]]
        a1.plot(t, m, color=RED if m[-1] > 600 else (GREEN if m[-1] > 1 else GREY), lw=1, alpha=0.7)
    a1.set_yscale("log")
    a1.axhline(72, color=GREEN, ls=":", lw=1)
    a1.text(5000, 80, "one glider", color=GREEN, ha="right", fontsize=9)
    a1.set_xlabel("step")
    a1.set_ylabel("total mass in the world (log)")
    a1.set_title("Each line is one 384×384 world started smooth")
    rules = sorted({r["rule"] for r in d})
    fates = {"blob field takes over": RED, "only gliders left": GREEN, "everything dies": GREY}
    counts = {f: [] for f in fates}
    for rule in rules:
        ends = [r["series"][-1]["mass"] for r in d if r["rule"] == rule]
        counts["blob field takes over"].append(sum(e > 600 for e in ends))
        counts["only gliders left"].append(sum(1 <= e <= 600 for e in ends))
        counts["everything dies"].append(sum(e < 1 for e in ends))
    left = np.zeros(len(rules))
    labels = [f"μ {r.split('/')[3][1:]}" for r in rules]
    for f, col in fates.items():
        a2.barh(labels, counts[f], left=left, color=col, label=f)
        left += counts[f]
    a2.set_xlabel("worlds (of 10)")
    a2.legend(frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    a2.set_title("How the 30 big worlds ended")
    fig.suptitle("E-15: in big worlds a growing blob field usually wins; gliders survive only where it never starts",
                 y=1.03, fontsize=12, fontweight="bold")
    fig.savefig(OUT / "e15-fates.png")
    plt.close(fig)


def e15_clips() -> None:
    def frames(rule, seed, t0, t1, every, crop=None):
        u = Universe.from_spec(UniverseSpec(parse_rule(rule).to_dict(), seed, 384, 384, 0.10,
                                            init={"kind": "smooth", "ell": 3.0}))
        u.step(t0)
        out = []
        for _ in range(t0, t1, every):
            s = u.state
            out.append(s[crop[0]:crop[1], crop[2]:crop[3]].copy() if crop else s[::2, ::2].copy())
            u.step(every)
        return out
    save_gif(frames("LENIA/R13/T10/m0.150/s0.0150/b1", 15001, 1500, 1900, 4), "e15-collision.gif", scale=1, ms=50)
    save_gif(frames("LENIA/R13/T10/m0.140/s0.0140/b1", 15000, 0, 1000, 10), "e15-field-takeover.gif", scale=2, ms=60)


WANDERER = "LENIA/R13/T10/m0.243/s0.0224/b1,0.5,0.5"  # found by E-17's engine arm (universe #1014)


def e17_wanderer() -> None:
    """The E-17 wanderer, cut out of its world and run alone (it turns as it moves)."""
    spec = json.load(open(DATA / "2026-11-07-e17-verified.json"))["wanderer_spec"]
    u = Universe.from_spec(UniverseSpec.from_dict(spec))
    phys = u.physics
    u.step(500)
    o = min(C.objects(u.state), key=lambda x: abs(x["mass"] - 115))
    alone = C.isolate(u.state, o)
    rr, cc = np.nonzero(alone)
    sub = alone[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    world = np.zeros((160, 160), np.uint8)
    world[80 - sub.shape[0] // 2:80 - sub.shape[0] // 2 + sub.shape[0],
          80 - sub.shape[1] // 2:80 - sub.shape[1] // 2 + sub.shape[1]] = sub
    frames, trail = [], np.zeros(world.shape)
    for t in range(0, 2001):
        if t % 5 == 0:
            ob = max(C.objects(world), key=lambda x: x["mass"])
            trail[int(ob["c"][0]) % 160, int(ob["c"][1]) % 160] = 255
        if t % 20 == 0:
            frames.append(np.maximum(world, (trail * 0.35).astype(np.uint8)))
        world = phys.step(world)
    save_gif(frames, "e17-wanderer.gif", scale=2, ms=60)


def e18_wanderer() -> None:
    d = json.load(open(DATA / "2026-11-07-e18-wanderer.json"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.4), gridspec_kw={"width_ratios": [1, 1.3], "wspace": 0.3})
    names = [("uniform", "soup"), ("smooth:3", "smooth\nℓ=3"), ("smooth:6", "smooth\nℓ=6"), ("smooth:10", "smooth\nℓ=10")]
    ks = [d["e18a"][k][0] / d["e18a"][k][1] for k, _ in names]
    bars = a1.bar([n for _, n in names], ks, color=[GREY, ORANGE, BLUE, GREEN])
    for b, (k, _) in zip(bars, names):
        a1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.02, f"{d['e18a'][k][0]}/{d['e18a'][k][1]}",
                ha="center", fontsize=9)
    a1.set_ylim(0, 1.05)
    a1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a1.set_ylabel("worlds with a verified wanderer")
    a1.set_title("E-18a: the wanderer's rule\n(40 fresh seeds per start)", fontsize=11)
    mus = sorted({r["mu"] for r in d["e18b_map"]})
    rs = sorted({r["sigma_over_mu"] for r in d["e18b_map"]})
    grid = np.zeros((len(mus), len(rs)))
    for r in d["e18b_map"]:
        grid[mus.index(r["mu"]), rs.index(r["sigma_over_mu"])] = r["smooth6_verified"] / r["n"]
    im = a2.imshow(grid, origin="lower", cmap="Greens", vmin=0, vmax=1, aspect="auto")
    a2.set_xticks(range(len(rs)), [f"{x:.3f}" for x in rs])
    a2.set_yticks(range(len(mus)), [f"{x:.3f}" for x in mus])
    a2.set_xlabel("growth width σ / μ")
    a2.set_ylabel("growth centre μ")
    for i in range(len(mus)):
        for j in range(len(rs)):
            if grid[i, j]:
                a2.text(j, i, f"{grid[i, j]:.0%}", ha="center", va="center", fontsize=8,
                        color="white" if grid[i, j] > 0.5 else "black")
    a2.set_title("E-18b: where wanderers arise\n(3-ring rules, smooth ℓ=6 starts; soups: 0 everywhere)", fontsize=11)
    fig.colorbar(im, ax=a2, fraction=0.04, format=matplotlib.ticker.PercentFormatter(1.0))
    fig.savefig(OUT / "e18-wanderer.png")
    plt.close(fig)


def e19_null_and_sweep() -> None:
    d = json.load(open(DATA / "2026-11-07-e19-shuffled-null-and-soup-sweep.json"))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw={"wspace": 0.28})
    arms = [("d0.1", "density 0.10", ["uniform", "smooth_shuffled:3", "smooth:3"]),
            ("d0.35", "density 0.35", ["uniform", "smooth_shuffled:6", "smooth:6"])]
    lab = {"uniform": "soup", "smooth_shuffled:3": "shuf-\nfled", "smooth_shuffled:6": "shuf-\nfled",
           "smooth:3": "smooth\nℓ=3", "smooth:6": "smooth\nℓ=6"}
    x = 0
    ticks, names = [], []
    for key, title, conds in arms:
        c = d["e19a"][key]["counts"]
        for k, col in zip(conds, (GREY, "#b07cc6", BLUE)):
            h, n = c[k]
            a1.bar(x, h / n, color=col)
            a1.text(x, h / n + 0.008, f"{h}/{n}", ha="center", fontsize=8.5)
            ticks.append(x)
            names.append(lab[k])
            x += 1
        a1.text(x - 2, -0.2, title, ha="center", fontsize=10, fontweight="bold", transform=a1.get_xaxis_transform())
        x += 0.8
    a1.set_xticks(ticks, names, fontsize=9)
    a1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a1.set_ylabel("worlds with a verified glider")
    a1.set_title("E-19a: same values, scrambled positions → no gliders", fontsize=11)
    sw = d["e19b_soup_sweep"]
    dens = [s["density"] for s in sw]
    ext = [s["classes"].get("extinct", 0) / s["n"] for s in sw]
    act = [1 - e for e in ext]
    a2.plot(dens, ext, "-o", color=GREY, label="dies")
    a2.plot(dens, act, "-o", color=RED, label="survives (blob field)")
    for s in sw:
        if s["mover_worlds"]:
            a2.annotate(f"{s['mover_worlds']} glider world\n(of {s['n']})", (s["density"], 0.5), xytext=(s["density"] + 0.03, 0.5),
                        arrowprops={"arrowstyle": "->"}, fontsize=9, color=GREEN)
    a2.set_xlabel("soup density")
    a2.set_ylabel("fraction of worlds")
    a2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    a2.legend(frameon=False, loc="lower left")
    a2.set_title("E-19b: soups die or freeze; one glider at the transition", fontsize=11)
    fig.savefig(OUT / "e19-null-and-sweep.png")
    plt.close(fig)


def e20_collisions() -> None:
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import collision_scan as cs
    d = json.load(open(DATA / "2026-11-07-e20-collisions.json"))
    fused = {(f"LENIA/R13/T10/{f['rule']}/s0.0150/b1" if f["rule"] == "m0.150" else f"LENIA/R13/T10/{f['rule']}/s0.0140/b1",
              f["offset"], f["phase"]) for f in d["fusions_followed_1000_more_steps"] if f["persists_1000"]}
    cats = [("both destroyed", GREY), ("one survives", "#9fb3c8"), ("both survive / pass", BLUE),
            ("fuse into a double glider", GREEN), ("explode into a blob field", RED)]
    groups = []
    for rule in cs.RULES:
        for geo in ("head-on", "perpendicular"):
            runs = [r for r in d["runs"] if r["rule"] == rule and r["geometry"] == geo]
            c = dict.fromkeys([k for k, _ in cats], 0)
            for r in runs:
                if r["mass"] > 1000:
                    c["explode into a blob field"] += 1
                elif geo == "perpendicular" and (rule, r["offset"], r["phase"]) in fused:  # fusions: perpendicular only
                    c["fuse into a double glider"] += 1
                elif r["gliders"] == 0:
                    c["both destroyed"] += 1
                elif r["gliders"] == 1:
                    c["one survives"] += 1
                else:
                    c["both survive / pass"] += 1
            groups.append((f"μ {rule.split('/')[3][1:]}\n{geo}", c, len(runs)))
    fig, ax = plt.subplots(figsize=(10, 3.6))
    left = np.zeros(len(groups))
    for k, col in cats:
        vals = np.array([g[1][k] / g[2] for g in groups])
        ax.barh([g[0] for g in groups], vals, left=left, color=col, label=k)
        left += vals
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_xlabel("collisions (125 per row)")
    ax.legend(ncol=3, frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    ax.set_title("E-20: 500 controlled glider collisions. No births; some fuse into a stable double glider")
    fig.savefig(OUT / "e20-collisions.png")
    plt.close(fig)
    # the fusion, as a clip (μ 0.150, offset -2, phase 0)
    rule = cs.RULES[0]
    phys = parse_rule(rule)
    g = cs.glider(rule)
    w = np.zeros((cs.SIDE, cs.SIDE), np.uint8)
    cs.place(w, g, 96, 51)
    cs.place(w, g.T, 51, 94)
    frames = []
    for t in range(0, 401):
        if t % 4 == 0:
            frames.append(w[16:176, 16:176].copy())
        w = phys.step(w)
    save_gif(frames, "e20-fusion.gif", scale=2, ms=50)


def e19_spontaneous_fusion() -> None:
    """E-19 universe #204: two gliders emerge from a smooth start, then fuse (t ~ 530)."""
    spec = UniverseSpec(parse_rule(ORBIUM).to_dict(), FUSION_SEED, 128, 128, 0.1, init={"kind": "smooth", "ell": 3.0})
    u = Universe.from_spec(spec)
    frames = []
    for t in range(0, 801):
        if t % 8 == 0:
            frames.append(u.state.copy())
        u.step()
    save_gif(frames, "e19-spontaneous-fusion.gif", scale=2, ms=60)


HELDOUT_MOVER = "LENIA/R13/T10/m0.277/s0.0316/b1,0.5,1"


def heldout_mover() -> None:
    """The mover rule found in the held-out cut-off check (J-028): its world from a smooth start
    (96x96, seed 1, density 0.35), then one mover cut out and run alone with its trail."""
    phys = parse_rule(HELDOUT_MOVER)
    u = Universe.from_spec(UniverseSpec(phys.to_dict(), 1, 96, 96, 0.35, init={"kind": "smooth", "ell": 6.0}))
    frames = []
    for t in range(0, 501):
        if t % 5 == 0:
            frames.append(np.pad(u.state, 32))
        if t < 500:
            u.step()
    o = max(C.objects(u.state), key=lambda x: x["mass"])
    alone = C.isolate(u.state, o)
    rr, cc = np.nonzero(alone)
    sub = alone[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    world = np.zeros((160, 160), np.uint8)
    world[80 - sub.shape[0] // 2:80 - sub.shape[0] // 2 + sub.shape[0],
          80 - sub.shape[1] // 2:80 - sub.shape[1] // 2 + sub.shape[1]] = sub
    trail = np.zeros(world.shape)
    for t in range(0, 1001):
        if t % 5 == 0:
            ob = max(C.objects(world), key=lambda x: x["mass"])
            trail[int(ob["c"][0]) % 160, int(ob["c"][1]) % 160] = 255
        if t % 10 == 0:
            frames.append(np.maximum(world, (trail * 0.35).astype(np.uint8)))
        world = phys.step(world)
    save_gif(frames, "heldout-mover.gif", scale=2, ms=60)


def heldout_cutoff() -> None:
    """Free activity of non-extinct, mover-free random Lenia rules: the 60 rules that set the 0.002
    quasi-static cut-off (C-01, rule seed 7) and 120 held-out rules (seed 8) from soups and smooth starts."""
    def vals(path):
        d = json.load(open(path))["part2_random_rules"]
        return [max(r["new"]["free_activity"], 1e-5) for r in d["per_rule"]
                if r["new"]["class"] not in ("extinct", "chaotic") and not r["new"]["self_propelled"]]
    sets = [("C-01 (set the cut-off)\n60 rules, soup", vals(DATA / "2026-11-06-c01-lenia-static-fields.json"), GREY),
            ("held out\n120 rules, soup", vals(DATA / "2026-11-07-c02-heldout-cutoff-uniform.json"), BLUE),
            ("held out\n120 rules, smooth ℓ=6", vals(DATA / "2026-11-07-c02-heldout-cutoff-smooth6.json"), ORANGE)]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    rng = np.random.default_rng(0)
    for i, (name, v, col) in enumerate(sets):
        ax.scatter(v, i + rng.uniform(-0.18, 0.18, len(v)), s=16, color=col, alpha=0.8)
    ax.axvline(0.002, color=RED, lw=1.5)
    ax.axvspan(0.0016, 0.0025, color=RED, alpha=0.08)
    ax.text(0.00205, 2.45, "cut-off 0.002", color=RED, fontsize=9)
    ax.set_xscale("log")
    ax.set_yticks(range(len(sets)), [n for n, _, _ in sets])
    ax.set_ylim(-0.5, 2.7)
    ax.set_xlabel("free activity (fraction of cells changing per step outside still blobs; 1e-5 = none)")
    ax.set_title("Quasi-static cut-off: no clean gap on new rules", fontsize=11)
    fig.savefig(OUT / "heldout-cutoff.png")
    plt.close(fig)


E24_PATCH_SEED = 662005294854461657  # E-24 universe #183: Orbium rule, Chan's patches, 256x256


def e24_patches() -> None:
    """E-24: worlds with a verified glider by start condition and world size, and a clip of a glider
    forming from Chan's patches in a 256x256 world."""
    d = json.load(open(DATA / "2026-11-07-e24-chan-patches.json"))["verified_by_arm"]
    bars = [("Chan patches\n128², 2000 steps\n(E-13)", 0, 40, GREY),
            ("Chan patches\n256², 3000 steps", d["patches"]["verified_worlds"], d["patches"]["worlds"], BLUE),
            ("110 patches\n256², 3000 steps", d["patches:110"]["verified_worlds"], d["patches:110"]["worlds"], GREY),
            ("smooth ℓ=3\n128², 2000 steps\n(E-14)", 28, 160, ORANGE),
            ("smooth ℓ=3\n256², 3000 steps", d["smooth"]["verified_worlds"], d["smooth"]["worlds"], ORANGE)]
    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    for i, (name, k, n, col) in enumerate(bars):
        lo, hi = wilson(k, n)
        ax.bar(i, k / n, color=col, alpha=0.9 if "256" in name else 0.45)
        ax.errorbar(i, k / n, yerr=[[k / n - lo], [hi - k / n]], color="black", capsize=4, lw=1)
        ax.text(i, hi + 0.01, f"{k}/{n}", ha="center", fontsize=9)
    ax.set_xticks(range(len(bars)), [b[0] for b in bars], fontsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_ylabel("worlds with a verified glider")
    ax.set_title("E-24: Chan's patch start makes gliders, given room and time", fontsize=11)
    fig.savefig(OUT / "e24-patches.png")
    plt.close(fig)
    spec = UniverseSpec(parse_rule(ORBIUM).to_dict(), E24_PATCH_SEED, 256, 256, 0.1, init={"kind": "patches"})
    u = Universe.from_spec(spec)
    frames = []
    for t in range(0, 601):
        if t % 6 == 0:
            frames.append(u.state.copy())
        u.step()
    save_gif(frames, "e24-patches.gif", scale=2, ms=70)


FIGS = {"e27_births": e27_births, "e24_patches": e24_patches, "heldout_mover": heldout_mover, "heldout_cutoff": heldout_cutoff, "e19_spontaneous_fusion": e19_spontaneous_fusion, "e20_collisions": e20_collisions, "e19_null_and_sweep": e19_null_and_sweep, "e18_wanderer": e18_wanderer, "e17_wanderer": e17_wanderer, "e15_fates": e15_fates, "e15_clips": e15_clips, "e14_per_rule": e14_per_rule, "static_vs_glider": static_vs_glider, "labels_before_after": labels_before_after,
        "viability_map": viability_map, "e12_engine_vs_random": e12_engine_vs_random,
        "emergence_clip": emergence_clip, "e13_rates": e13_rates}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or list(FIGS):
        FIGS[name]()
        print("wrote", name)


if __name__ == "__main__":
    main()
