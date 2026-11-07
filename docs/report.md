---
title: Report
description: Overnight research report, 7 November 2026. Lenia, spontaneous gliders, and what made them appear.
---

# Overnight report · 7 November 2026

<p class="lead">Can things that move by themselves arise on their own from simple rules? Overnight we tested this in <b>Lenia</b>, a continuous cousin of the Game of Life. For the first time in this project, they did: gliders formed spontaneously, but only when the random starting world was <i>smooth</i>. Starting from the usual fine-grained noise, they never formed.</p>

<figure>
<img src="{{ '/assets/report/emergence-soup-vs-smooth.gif' | relative_url }}" alt="Two Lenia worlds side by side. Left: fine random noise freezes into a maze of static blobs. Right: smooth random noise breaks into lumps, a few become gliders, and one glider survives.">
<figcaption>Same rule (Orbium), same random seed, same total amount of matter. <b>Left:</b> a fine-grained random start freezes into static blobs. <b>Right:</b> a smooth random start breaks into lumps, several become gliders, they collide and die off, and one survives and keeps travelling. 2000 steps.</figcaption>
</figure>

## In five points

<div class="cards">
<div class="card"><div class="stat">bug fixed</div><p>Our "complex" label had been calling <b>fields of motionless blobs</b> complex: 27 of 60 random Lenia rules. Fixed and re-validated before any new experiment (J-012).</p></div>
<div class="card"><div class="stat">0 / 2085</div><p>Two full searches (the discovery engine and a random-search baseline, 1000 rules in all) found <b>no rule that makes gliders from ordinary random soup</b> (E-12).</p></div>
<div class="card"><div class="stat">8 / 99</div><p>Gliders <i>can</i> exist in only a <b>small island of rule space</b> around the known glider Orbium (E-13a).</p></div>
<div class="card"><div class="stat">49 vs 0</div><p>In that island, <b>smooth random starts produced gliders in 49 of 320 worlds, matched ordinary soups in 0 of 320</b>. Pre-registered, fresh seeds, p &lt; 10⁻⁶ (E-14).</p></div>
<div class="card"><div class="stat">level 2</div><p>Highest evidence level reached in Lenia: <b>spontaneous self-propelled structures</b>. No reproduction, heredity or evolution yet.</p></div>
</div>

---

## 1 · First we fixed a measurement that was fooling us

Before running anything new, we found that our automatic "complex" label had been tuned for the on/off cells of the Game of Life. On Lenia, whose cells take any value between 0 and 1, it called **fields of motionless blobs "complex"**: every blob counted as a "persistent structure", and the slow wobbling of their edges counted as activity.

<figure>
<img src="{{ '/assets/report/static-vs-glider.png' | relative_url }}" alt="Four panels: a blob field at two times, the few cells that changed, and two gliders">
<figcaption>Left three panels: a Lenia "blob field" 100 steps apart. Only the edges of the blobs change (third panel); nothing travels. Right: two gliders, each shown at the start and 100 steps later. The old label called both "complex".</figcaption>
</figure>

We checked whether the blob-edge activity was a rounding artefact (Lenia here stores 256 levels per cell). **It is not**: the same simulation in full floating-point precision does exactly the same thing. It is real, slow relaxation at the blob edges. The fix (for continuous physics only; the Game-of-Life results are byte-for-byte unchanged):
- "complex" now requires something that **travels by itself** (verified by cutting it out and running it alone);
- fields of still objects whose edges only creep are labelled **quasi-static** and are no longer rewarded by the search;
- every change has a positive control, a negative control, a control built to fool it, and a test against the way the search picks candidates (8 new checks, all passing).

<figure>
<img src="{{ '/assets/report/labels-before-after.png' | relative_url }}" alt="Bar chart: 27 of 60 rules complex before the fix, 0 after">
<figcaption>The same 60 random Lenia rules, labelled before and after the fix. None of them has anything that moves.</figcaption>
</figure>

An earlier Lenia search that reported "44% complex" had used the inflated label; its data was lost with a cloud container and is recorded as invalid.

## 2 · A full search finds no gliders from random soup

**E-12** ran the discovery engine on Lenia rule space (500 rules × 2 seeds, 5 generations) and, as a control, random search with the same computing budget.

<figure>
<img src="{{ '/assets/report/e12-engine-vs-random.png' | relative_url }}" alt="Bar chart comparing engine and random search">
<figcaption>Engine vs random search. Neither found a rule where gliders arise from soup. The engine finds about twice as many rules with structured (non-random, non-static) dynamics after removing near-duplicates, and it sends 6.6× more of its rules into the region where gliders can exist (section 3), without being told to.</figcaption>
</figure>

<figure>
<img src="{{ '/assets/report/dashboard-e12-engine.jpg' | relative_url }}" alt="Screenshot of the Emergence Lab dashboard showing a gallery of Lenia universes and one universe open">
<figcaption>The project dashboard on the E-12 engine run: a gallery of the universes the search tried (blob fields, mazes, textures) and one opened at step 500. Lots of structure, nothing that travels.</figcaption>
</figure>

## 3 · Where can a glider exist at all?

Zero gliders could mean two different things: the rules can't support gliders, or they can but random starts never make one. To separate them we grew gliders **by hand** (from a lopsided seed, left to settle on its own) in a grid of 99 rules.

<figure>
<img src="{{ '/assets/report/viability-map.png' | relative_url }}" alt="Grid of rules; 8 green dots near Orbium">
<figcaption>Only 8 of 99 rules support a glider (green), all in a small island around Chan's Orbium (red circle). The gliders move at 0.54–0.69 cells per step. The discovery engine had found this island: 59 of its 500 rules were in it.</figcaption>
</figure>

So in these 8 rules gliders **can** exist, yet E-12's soups never made one there. **The bottleneck is emergence, not the search.**

<figure>
<img src="{{ '/assets/report/gliders.gif' | relative_url }}" alt="Two Orbium-like gliders moving to the right">
<figcaption>Two gliders under the Orbium rule. Each keeps its shape and mass and travels about half a cell per step.</figcaption>
</figure>

## 4 · What makes gliders appear: smooth starts

What we read in the literature (J-013): Lenia's creator reports that gliders emerge "given enough time" from random starts, but gives no rate, and his random starts were dense patches in empty space, not soup. Nobody has published how often it happens. We designed **E-13** and wrote its analysis down **before running it**: the 8 glider-capable rules, started six different ways with the same amount of matter where applicable:

- **soup**: each cell randomly filled (what E-12 used);
- **smooth**: random noise blurred over 3, 6 or 10 cells (lumpy hills and valleys), scaled to the soup's total mass;
- **spots** and **Chan's patches** (the creator's own protocol).

<figure>
<img src="{{ '/assets/report/e13-glider-rates.png' | relative_url }}" alt="Bar chart: only smooth starts produce gliders">
<figcaption>E-13: gliders appeared only from smooth starts (18 of 240 worlds) and never from soup, spots or Chan's patches.</figcaption>
</figure>

E-13's planned statistics could not confirm this: with only 8 rules, the planned test could never reach its significance threshold (a planning mistake, recorded). So we wrote a new plan with a test that can, and ran it with **fresh random seeds** (**E-14**):

<figure>
<img src="{{ '/assets/report/e14-per-rule.png' | relative_url }}" alt="Per-rule glider rates from smooth starts; zero from soup">
<figcaption>E-14 (pre-registered, 640 new worlds): smooth starts made gliders in 28/160 and 21/160 worlds; ordinary soups with the same mass in 0/160 and 0/160 (p = 10⁻⁹ and 2·10⁻⁷). 6 of the 8 rules produced gliders. Bars show 95% intervals.</figcaption>
</figure>

**Every one of the 49 gliders was cut out and run alone for 1000 steps; all 49 kept going.** They are the same creatures we grew by hand in section 3 (for one rule: 0.637 cells/step by hand, 0.638 spontaneous).

**Why smooth starts work.** A glider needs an isolated lump of about the right size and mass, with empty space around it. Smooth noise makes lumps; fine-grained noise averages out into an even film of matter that either freezes into blobs (dense) or dies (sparse). Here, unlike our Game-of-Life study (J-009), **how matter is arranged matters**, not only how much there is.

**What it is not.** The gliders mostly destroy each other: 47 of 49 glider worlds end with exactly one glider alone in an empty world. Spontaneous movement, yes; an ecology of interacting creatures, not yet.

## 5 · Glider populations in bigger worlds

If gliders destroy each other in small worlds, what happens with more room? **E-15** ran 30 worlds nine times larger (384×384) for 5000 steps.

<figure>
<img src="{{ '/assets/report/e15-fates.png' | relative_url }}" alt="Mass over time for 30 big worlds, and a bar chart of how they ended">
<figcaption>Left: total matter in each world over time. Red worlds were taken over by a growing field of static blobs (Lenia does not conserve mass, so the field grows to fill the world). Green worlds end with one or two gliders: their matter only ever drops, one glider at a time. Right: the field won in 23 of 30 worlds.</figcaption>
</figure>

<div class="cards">
<div class="card"><img src="{{ '/assets/report/e15-field-takeover.gif' | relative_url }}" alt="A blob field spreading over a large world"><p><b>The field wins.</b> One surviving patch of static blobs spreads over the whole world within ~600 steps.</p></div>
<div class="card"><img src="{{ '/assets/report/e15-collision.gif' | relative_url }}" alt="Two gliders colliding in an empty world"><p><b>Gliders collide.</b> In the worlds the field never reached, gliders meet and merge or destroy each other. No collision ever made a new glider.</p></div>
</div>

So a glider is a **fragile in-between state**: the world must collapse enough to leave isolated lumps, but not so much that nothing survives, and no blob field may survive anywhere. In bigger worlds that last condition fails more often. Gliders interact only destructively. **No births, no growing population**: the step from moving things to reproducing things is not happening here.

*A note on our own mistake:* the script's quick glider counter (no isolation test) reported hundreds of "births". Looking at the frames showed they were moving edges inside blob fields and count flicker during collisions. Only the mass traces and the pictures are used above.

## 6 · A second continuous physics: Flow-Lenia

Lenia's gliders survive only in a narrow band of rules, partly because nothing stops matter from appearing or vanishing. **Flow-Lenia** (Plantec et al. 2023) changes that: matter is never created or destroyed, it only *flows*. Its authors report that moving creatures are common in it and that creatures can even evolve inside the simulation, but they give no counts and no comparison with chance. So we treat these as claims to test, not results to inherit.

Overnight a separate agent implemented Flow-Lenia from the paper's equations and put it through the project's validation (J-016):
- **Mass is conserved** to the limit of float precision (worst drift 1.5 parts in 100 million over 1000 steps).
- **Controls pass:** a static-blob rule is not called complex; pure diffusion spreads but produces no movers; a rotated starting world gives exactly the rotated result (so the grid itself does not create fake motion).
- **A first version stored cells with 256 levels and was rejected:** rounding stopped slow flows dead (pure diffusion froze after 50 steps). The engine now supports floating-point cells; all earlier results are byte-for-byte unchanged.
- **No mover found yet:** 168 random rules (80 of them in full float precision), started from the paper's own random patch, produced no structure that travels by itself. This agrees with the paper's remark that single-channel movement needed long optimisation, and it means Flow-Lenia does not yet have the positive control our rules require before running experiments on it.

## Where this leaves the project

| Evidence level | Life-like rules (v0.1–v0.4) | Lenia (tonight) |
|---|---|---|
| 1 · persistent organisation | yes | yes |
| 2 · self-propelled structures | yes | **yes, arising spontaneously from smooth starts** |
| 3 · self-replication | not observed | not tested yet (needs a continuous replication detector) |
| 4 · heredity and variation | not measured | not measured |
| 5 · open-ended evolution | not observed (knockouts ≈ placebo) | not tested |

**Mistakes we caught and recorded:** the inflated label (J-012); a pre-registered test that could not reach its own threshold (J-014); a glider speed documented 5× too low, because measuring across more than half the world wraps around (J-012).

## What next

1. **Rates vs world size and run length**, measured with the validated detector at checkpoints (E-15 used a quick counter for its time series).
2. **Chan's own patch protocol in larger worlds and longer runs** (it produced nothing in 2000 steps on 128×128).
3. **A replication detector for continuous physics** (our exact-shape probes do not work for Lenia).
4. **Flow-Lenia:** find a positive control (smooth starts, as in Lenia; several channels), then run the same validated pipeline: does mass conservation make movers and evolution more common, as its authors claim?

## Read more

- Journal entries [J-012 to J-017]({{ '/journal.html' | relative_url }}) (full numbers, caveats, commits); [Decisions]({{ '/decisions.html' | relative_url }}) D-022 to D-026; [Experiments]({{ '/experiments.html' | relative_url }}) with exact commands and data.
- Pre-registrations: [E-13](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e13-preregistration.md), [E-14](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e14-preregistration.md).
- Every figure is regenerated by `python scripts/make_report_figures.py`.

**Glossary.** *Lenia*: a cellular automaton with continuous cell values and smooth, ring-shaped neighbourhoods (Chan 2019). *Glider*: a pattern that keeps its shape and travels. *Soup*: a random start where each cell is independently filled. *Smooth start*: random noise blurred over ℓ cells. *Pre-registered*: the test and its threshold were written down and committed before the data existed. *Evidence level*: the project's ladder from persistent organisation (1) to open-ended evolution (5).
