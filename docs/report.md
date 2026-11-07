---
title: Report
description: Overnight research report, 7 November 2026. Lenia, spontaneous gliders, and what made them appear.
---

# Overnight report · 7 November 2026

<p class="lead">Can things that move by themselves arise on their own from simple rules? Overnight we tested this in <b>Lenia</b>, a continuous cousin of the Game of Life. For the first time in this project, they did: gliders formed spontaneously, mostly when the random starting world was <i>smooth</i>, with matter clumped in space. From the usual fine-grained noise they almost never formed: once in 1,120 worlds, right at the density where soups switch from dying to freezing.</p>

<figure>
<img src="{{ '/assets/report/emergence-soup-vs-smooth.gif' | relative_url }}" alt="Two Lenia worlds side by side. Left: fine random noise freezes into a maze of static blobs. Right: smooth random noise breaks into lumps, a few become gliders, and one glider survives.">
<figcaption>Same rule (Orbium), same random seed, same total amount of matter. <b>Left:</b> a fine-grained random start freezes into static blobs. <b>Right:</b> a smooth random start breaks into lumps, several become gliders, they collide and die off, and one survives and keeps travelling. 2000 steps.</figcaption>
</figure>

## In short

<div class="cards">
<div class="card"><div class="stat">bug fixed</div><p>Our "complex" label had been calling <b>fields of motionless blobs</b> complex: 27 of 60 random Lenia rules. Fixed and re-validated before any new experiment (J-012).</p></div>
<div class="card"><div class="stat">0 / 2085</div><p>Two full searches (the discovery engine and a random-search baseline, 1000 rules in all) found <b>no rule that makes gliders from ordinary random soup</b> (E-12).</p></div>
<div class="card"><div class="stat">8 / 99</div><p>Among simple <b>single-ring</b> rules, gliders <i>can</i> exist only in a <b>small island</b> around the known glider Orbium (E-13a). Richer rules hold others (section 6).</p></div>
<div class="card"><div class="stat">49 vs 0</div><p>In that island, <b>smooth random starts produced gliders in 49 of 320 worlds, matched ordinary soups in 0 of 320</b>. Pre-registered, fresh seeds, p &lt; 10⁻⁶ (E-14). Scrambling the positions of the same values removes every glider: <b>it is the arrangement</b> (E-19).</p></div>
<div class="card"><div class="stat">23 / 30</div><p>In <b>bigger worlds</b>, a growing field of static blobs usually takes over; gliders <b>collide and die</b>; we saw no new ones form (E-15).</p></div>
<div class="card"><div class="stat">1 new mover</div><p>Searching again from smooth starts, the engine found a <b>different kind of mover</b>: a slow, turning "wanderer" in another part of rule space. Random search found none (E-17). Confirmed with fresh seeds: 36 of 40 worlds (E-18).</p></div>
<div class="card"><div class="stat">1 + 1 = 1</div><p>Gliders never multiplied in 500 controlled collisions, but two can <b>fuse into a stable double glider</b>, and this also happened <b>on its own</b> in a smooth-start world (E-20, J-024).</p></div>
<div class="card"><div class="stat">0 / 400</div><p><b>Flow-Lenia</b>, a mass-conserving variant said to make movers easily, was built and validated, but produced <b>no movers</b> in 400 worlds (E-16).</p></div>
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
- "complex" now requires something that **travels by itself**: seen moving in its own world, then verified by cutting it out and running it alone;
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
<figcaption>Only 8 of 99 single-ring rules support a glider (green), all in a small island around Chan's Orbium (red circle). The gliders move at 0.54–0.69 cells per step. The discovery engine had found this island: 59 of its 500 rules were in or near it (7 of them single-ring; not deduplicated).</figcaption>
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
<figcaption>E-13: gliders appeared only from smooth starts (18 of 240 worlds), not from soup, spots or Chan's patches.</figcaption>
</figure>

E-13's planned statistics could not confirm this: with only 8 rules, the planned test could never reach its significance threshold (a planning mistake, recorded). So we wrote a new plan with a test that can, and ran it with **fresh random seeds** (**E-14**):

<figure>
<img src="{{ '/assets/report/e14-per-rule.png' | relative_url }}" alt="Per-rule glider rates from smooth starts; zero from soup">
<figcaption>E-14 (pre-registered, 640 new worlds): smooth starts made gliders in 28/160 and 21/160 worlds; ordinary soups with the same mass in 0/160 and 0/160 (p = 10⁻⁹ and 2·10⁻⁷). 6 of the 8 rules produced gliders. Bars show 95% intervals.</figcaption>
</figure>

**Every one of the 51 gliders (in 49 worlds) was cut out and run alone for 1000 steps; all 51 kept going.** They are the same creatures we grew by hand in section 3 (for one rule: 0.637 cells/step by hand, 0.638 spontaneous).

**Is it really the arrangement?** Our independent reviewer (R-4) spotted a gap: a smooth start differs from a soup in its *mix of cell values* (more weakly-filled cells), not only in where matter sits. So we ran **E-19** (pre-registered): the same smooth starts, plus a **shuffled** version with exactly the same cell values scattered at random. We also swept soup density finely, because soups seemed to either die or freeze.

<figure>
<img src="{{ '/assets/report/e19-null-and-sweep.png' | relative_url }}" alt="Left: gliders only from smooth starts, none from shuffled or soup. Right: soups die below density 0.18 and freeze above 0.24; one glider world at 0.20">
<figcaption>Left: scrambling the positions of exactly the same values removes every glider (0/160 at both densities; smooth: 37/160 and 11/160; p = 7·10⁻¹³ and 4·10⁻⁴). Right: soups die below density ~0.18 and freeze into blob fields above ~0.24. Right at the switch, one soup world in 40 did make a glider, so "never from soup" was too strong.</figcaption>
</figure>

So it is **the spatial arrangement**, not the value mix. Here, unlike our Game-of-Life study (J-009), arrangement matters at the same total amount of matter. A likely mechanism, still a hypothesis: a glider needs an isolated lump of about its own size with empty space around it. Smooth noise makes such lumps; fine-grained noise averages into an even film that dies or freezes, except, rarely, right at the switch between the two.

**What it is not.** The gliders mostly destroy each other: 47 of 49 glider worlds end with exactly one glider alone in an empty world. Spontaneous movement, yes; an ecology of interacting creatures, not yet.

## 5 · Glider populations in bigger worlds

If gliders destroy each other in small worlds, what happens with more room? **E-15** ran 30 worlds nine times larger (384×384) for 5000 steps.

<figure>
<img src="{{ '/assets/report/e15-fates.png' | relative_url }}" alt="Mass over time for 30 big worlds, and a bar chart of how they ended">
<figcaption>Left: total matter in each world over time. Red worlds were taken over by a growing field of static blobs (Lenia does not conserve mass, so the field grows to fill the world). Green worlds end with one or two gliders: their matter falls in steps of about one glider (with small bumps during collisions). Right: the field won in 23 of 30 worlds.</figcaption>
</figure>

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/e15-field-takeover.gif' | relative_url }}" alt="A blob field spreading over a large world"><p><b>The field wins.</b> One surviving patch of static blobs spreads over the whole world within ~600 steps.</p></div>
<div class="card"><img src="{{ '/assets/report/e15-collision.gif' | relative_url }}" alt="Two gliders colliding in an empty world"><p><b>Gliders collide.</b> In the worlds the field never reached, gliders meet and merge or destroy each other. We saw no collision make a new glider.</p></div>
</div>

So a glider is a **fragile in-between state**: the world must collapse enough to leave isolated lumps, but not so much that nothing survives, and no blob field may survive anywhere. In bigger worlds that last condition fails more often. In the collisions we looked at, gliders merged or destroyed each other. **We saw no births and no growing population**, though with only 6 glider-only worlds that is weak evidence, not proof.

*A note on our own mistake:* the script's quick glider counter (no isolation test) reported hundreds of "births". Looking at the frames showed they were moving edges inside blob fields and count flicker during collisions. Only the mass traces and the pictures are used above.

**Controlled collisions (E-20, pre-registered).** To settle the "births" question we crashed gliders into each other on purpose: 500 collisions, head-on and at right angles, at many offsets and timings.

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/e20-fusion.gif' | relative_url }}" alt="Two gliders meet at right angles and fuse into one double glider that moves diagonally"><p><b>Two become one.</b> In 7 right-angle collisions the gliders <b>fused into a stable double glider</b> (twice the mass, same speed) that kept going for 1000+ steps: a collision built a new, larger mover.</p></div>
<div class="card"><img src="{{ '/assets/report/e20-collisions.png' | relative_url }}" alt="Outcomes of 500 collisions"><p><b>No births.</b> No collision ever produced extra gliders. Most destroy one or both gliders or let them pass; 6 set off a blob field that took over the whole world. Combination yes, reproduction no.</p></div>
</div>

**It also happens on its own.** Looking back through all 121 verified movers from E-13, E-14 and E-19, three were double gliders, each the last survivor of a smooth-start world. In one of them we can watch the whole sequence with nothing planted: two gliders form from the smooth start, travel for ~500 steps, then meet and fuse (J-024).

<figure>
<img src="{{ '/assets/report/e19-spontaneous-fusion.gif' | relative_url }}" alt="Two spontaneous gliders travel, collide and fuse into one double glider">
<figcaption>E-19 world #204 (Orbium rule, smooth start): lumps → two gliders → one double glider (fusion at step ~530). Structure built on earlier structure, spontaneously, observed once.</figcaption>
</figure>

**How common is it? (E-21, pre-registered.)** Rare. In 320 fresh smooth-start worlds, one double glider formed (directly from the start, not by fusion), so spontaneous double gliders appear in about 0.6% of such worlds and the fusion route has been seen once. A mistake caught on the way: our new script's check ("cut it out, does it move?") also counted fragments of blob fields, so it first reported 116 glider worlds and 2 doubles. A mover has to be seen moving *in its own world* first, as our main detector requires (J-025).

## 6 · Searching again, from smooth starts: a different kind of mover

E-12 searched rule space from soups, and E-14 showed that soups (almost) never make gliders. So we repeated the search (**E-17**, pre-registered) with every world started smooth.

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/e17-wanderer.gif' | relative_url }}" alt="A compact patterned creature moving in a loop, leaving a faint trail"><p><b>The "wanderer"</b> (rule μ 0.243, three kernel rings), found by the discovery engine. Cut out and run alone, it keeps its body (mass ~115) and moves along its path at about 0.07 cells per step, <b>turning as it goes</b>, as its faint trail shows (net progress is only 0.02–0.05 cells per step). Found in 4 worlds, including runs with fresh seeds and a 2× larger world.</p></div>
<div class="card"><p><b>Engine vs random search, from smooth starts:</b></p><p>Engine: <b>1 rule with a verified mover</b> (the wanderer). Random search: <b>0</b>. A second candidate, found by both, was a drifting chunk of blob field that fell apart when run alone.</p><p>The wanderer lives far from Orbium's island (3 rings, larger μ). It is slower and turns, unlike the straight-line gliders: a different kind of mover from Orbium (new to this project; similar slow, turning Lenia species may already be known). The numbers are tiny (one seed per search), so this is a lead, not a statistical result.</p></div>
</div>

**Confirmed (E-18, pre-registered).** With 40 fresh seeds, the wanderer's rule produced a verified wanderer in **36 of 40 smooth-start worlds, and 0 of 40 soups** (p ≈ 10⁻¹⁸). Mapping the rules around it shows wanderers live on a **narrow diagonal ridge** of rule space, as Orbium's gliders live on their island:

<figure>
<img src="{{ '/assets/report/e18-wanderer.png' | relative_url }}" alt="Bar chart: wanderers in 36/40 smooth-start worlds and 0/40 soups; heat map of a narrow ridge of rules producing wanderers">
<figcaption>Left: the wanderer's rule almost always makes a wanderer from a smooth start, never from soup (our detector misses about 8% of wanderers because they turn, so these are slight undercounts, J-022). Right: across 42 neighbouring rules, wanderers arise only on a thin ridge (green). Soups made none anywhere (252 worlds). 190 of 192 wanderers survived 1000 steps alone.</figcaption>
</figure>

**The lesson:** the starting world decides what a search can see. E-12's "zero" was a property of the soup, not of rule space.

## 7 · A second continuous physics: Flow-Lenia

Lenia's gliders survive only in a narrow band of rules, partly because nothing stops matter from appearing or vanishing. **Flow-Lenia** (Plantec et al. 2023) changes that: matter is never created or destroyed, it only *flows*. Its authors report that moving creatures are common in it and that creatures can even evolve inside the simulation, but they give no counts and no comparison with chance. So we treat these as claims to test, not results to inherit.

Overnight a separate agent implemented Flow-Lenia from the paper's equations and put it through the project's validation (J-016):
- **Mass is conserved** to the limit of float precision (worst drift 1.5 parts in 100 million over 1000 steps).
- **Controls pass:** a static-blob rule is not called complex; pure diffusion spreads but produces no movers; a rotated starting world gives exactly the rotated result (so the grid itself does not create fake motion).
- **A first version stored cells with 256 levels and was rejected:** rounding stopped slow flows dead (pure diffusion froze after 50 steps). The engine now supports floating-point cells; all earlier results are byte-for-byte unchanged.
- **No mover found yet:** 168 random rules (80 of them in full float precision), started from the paper's own random patch, produced no structure that travels by itself. This agrees with the paper's remark that single-channel movement needed long optimisation, and it means Flow-Lenia does not yet have the positive control our rules require before running experiments on it.
- **Smooth starts don't help here (E-16):** 100 random rules × 4 kinds of start gave **0 movers in 400 worlds**. The authors' claim that moving patterns are "quite common" is not reproduced, either because of details the paper leaves unspecified, or because their "dynamic" patterns mostly wobble in place (J-018).

## Where this leaves the project

| Evidence level | Life-like rules (v0.1–v0.4) | Lenia (tonight) |
|---|---|---|
| 1 · persistent organisation | yes | yes |
| 2 · self-propelled structures | yes | **yes, arising spontaneously from smooth starts** (gliders; a turning "wanderer") |
| 3 · self-replication | not observed | none: no births in big worlds (E-15) or in 500 controlled collisions (E-20); collisions can *fuse* two gliders into one larger mover |
| 4 · heredity and variation | not measured | not measured |
| 5 · open-ended evolution | not observed (knockouts ≈ placebo) | not tested |

**Mistakes we caught and recorded:** an over-inclusive mover check in a new script (J-025); the inflated label (J-012); a pre-registered test that could not reach its own threshold (J-014); a glider speed documented 5× too low, because measuring across more than half the world wraps around (J-012); a quick glider counter whose "births" were artefacts (J-017).

## What next

1. **Interactions as a route to new structure:** gliders can fuse into double gliders (E-20). Do wanderers fuse, with each other or with gliders? Is there a chain (double → triple)? A knockout test on fusion events (J-010 style) would show whether later structures depend on earlier ones.
2. **A better detector for slow, turning movers** (it misses ~8% of wanderers, J-022), with its own deceptive controls.
3. **Rates vs world size and run length**, measured with the validated detector at checkpoints (E-15 used a quick counter for its time series).
4. **Chan's own patch protocol in larger worlds and longer runs** (it produced nothing in 2000 steps on 128×128).
5. **A replication detector for continuous physics** (our exact-shape probes do not work for Lenia).
6. **Flow-Lenia:** find a positive control (several channels; check our implementation against the paper's figures), then run the same validated pipeline: does mass conservation make movers and evolution more common, as its authors claim?

## How the night went

| Time (CST) | What |
|---|---|
| 23:50–00:04 | Label fix merged (PR #4); E-12 (Lenia search, engine vs random) running |
| 00:10 | Glider-viability map (E-13a); literature review; E-13 pre-registered |
| 00:33 | E-13: first spontaneous gliders, from smooth starts only |
| 01:07 | E-14 confirms (pre-registered, fresh seeds) |
| 01:32 | Report page live (PR #5) |
| 01:45 | Flow-Lenia merged after a float-precision rewrite (PR #6) |
| 02:33 | E-15: big worlds are taken over by blob fields (PR #7) |
| 02:47 | E-16: no Flow-Lenia movers |
| 03:02 | E-17: the wanderer (PR #8); E-18 and an independent review start |
| ~03:15–04:00 | Usage limit reached; work paused |
| 04:07 | Review R-4: all points accepted and corrections made; E-18 confirms the wanderer (PR #9) |
| 04:32 | E-19: the shuffled control confirms spatial correlation; soups rarely make gliders (PR #10) |
| 04:39 | Detector sensitivity for slow movers measured, ≈ 92% (PR #11) |
| 04:45 | E-20: 500 controlled collisions; no births, but gliders can fuse |
| 04:50 | Double gliders also found arising spontaneously, once via fusion of two spontaneous gliders (J-024) |
| 05:05 | E-21: spontaneous double gliders are rare (~0.6% of worlds); a flawed check caught (J-025) |

Everything was done on branches, checked with `pytest` and the validation benchmark, and merged by pull request. The benchmark now has 77 checks, all passing.

## Read more

- Journal entries [J-012 to J-025]({{ '/journal.html' | relative_url }}) (full numbers, caveats, commits); independent review [R-4]({{ '/reviews.html#r-4' | relative_url }}); [Decisions]({{ '/decisions.html' | relative_url }}) D-022 to D-026; [Experiments]({{ '/experiments.html' | relative_url }}) with exact commands and data.
- Pre-registrations: [E-13](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e13-preregistration.md), [E-14](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e14-preregistration.md), [E-17](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e17-preregistration.md), [E-18](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e18-preregistration.md), [E-19](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e19-preregistration.md), [E-20](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e20-preregistration.md), [E-21](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e21-preregistration.md).
- Every figure is regenerated by `python scripts/make_report_figures.py`.

**Glossary.** *Lenia*: a cellular automaton with continuous cell values and smooth, ring-shaped neighbourhoods (Chan 2019). *Glider*: a pattern that keeps its shape and travels. *Soup*: a random start where each cell is independently filled. *Smooth start*: random noise blurred over ℓ cells. *Pre-registered*: the test and its threshold were written down and committed before the data existed. *Evidence level*: the project's ladder from persistent organisation (1) to open-ended evolution (5).
