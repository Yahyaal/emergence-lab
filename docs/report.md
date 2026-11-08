---
title: Report
description: Overnight research report, 7 November 2026. Lenia, spontaneous gliders, and what made them appear.
---

# Overnight report · 7 November 2026

<p class="lead"><b>Updated Sunday 2 a.m.</b> (section 11): <b>the first reproducer in Lenia</b>, dividing spots in one random multi-channel rule, and a clean held-out test of the fed-world fix. Section 10: no reproduction in 3000 random Lenia rules, a validated test for heredity, Flow-Lenia whose creatures carry their own rules, and a false alarm about reproduction in fed worlds, caught and fixed. Earlier: a third kind of mover, Chan's start reproduced in bigger worlds, a better slow-mover detector (section 8), and a birth detector (section 9).</p>

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
<div class="card"><div class="stat">3 kinds</div><p>Morning: a rule drawn <b>at random</b> made a third kind of mover, a slow, perfectly straight <b>"ring glider"</b>. Confirmed: 31 of 80 smooth-start worlds, 0 of 80 soups (E-26).</p></div>
<div class="card"><div class="stat">13 / 160</div><p>Morning: Chan's own start (sparse dense patches) <b>does</b> make gliders when the world is big enough: 0 of 40 at 128², 13 of 160 at 256². <b>Our prediction was wrong</b> (E-24).</p></div>
<div class="card"><div class="stat">0 / 568</div><p>Saturday: a new <b>birth detector</b>, validated on known reproducers, found <b>no reproduction</b> in 568 Lenia worlds, none among 285 movers. Its first version was fooled by blobs bursting into labyrinths; fixed and confirmed on held-out worlds (E-27, E-28).</p></div>
<div class="card"><div class="stat">0 / 3000</div><p>Saturday afternoon: <b>every rule drawn at random</b> got a chance to reproduce from a lone lump. None did, and none even came close (E-29). A new <b>heredity test</b> passed its controls, ready for physics that can reproduce.</p></div>
<div class="card"><div class="stat">17 → 0</div><p>Evening: in <b>fed Flow-Lenia</b>, the detector first found "reproducers" in 17 of 100 worlds. They were <b>food condensing</b>, which happens even with no creature present. Detector fixed (it now also checks a slightly disturbed empty world); <b>0 reproducers</b> (E-30).</p></div>
<div class="card"><div class="stat">0 / 97</div><p>Saturday night: the fed-world fix, tested on <b>400 new rules</b>: no false alarm, no reproducer, positive control still passes (E-31).</p></div>
<div class="card"><div class="stat">1 / 1000</div><p>Saturday night: one random <b>multi-channel</b> Lenia rule makes <b>spots that divide</b> until they tile the world. Verified over two generations and three fresh starts. <b>Our prediction (0) was wrong</b>. But every spot is the same type, so nothing can be inherited (E-32).</p></div>
<div class="card"><div class="stat">level 3</div><p>Highest evidence level reached in Lenia: <b>self-replication</b>, in its weakest form (one type, no heredity). Self-propelled structures (level 2) arise spontaneously. No heredity or evolution yet.</p></div>
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
<figcaption>E-13: gliders appeared only from smooth starts (18 of 240 worlds), not from soup, spots or Chan's patches (on these small worlds; in 4× larger worlds Chan's patches do make gliders, section 8).</figcaption>
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

**Does it go further? (E-23, pre-registered.)** No. In 312 collisions between a double glider and a single glider, nothing larger ever formed, and the double never survived intact; 37% of these collisions set off a world-filling blob field. Combination goes one step (1 + 1 = 1 double) and stops (J-027).

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

**When wanderers meet (E-22, pre-registered, 200 encounters):** usually **two become one**. In 71% of encounters a single ordinary wanderer is left, its mass back to normal; in 22% both survive; 5% destroy both. Unlike gliders, wanderers never formed a lasting double, and no encounter produced extra wanderers (J-026).

**The lesson:** the starting world decides what a search can see. E-12's "zero" was a property of the soup, not of rule space.

## 7 · A second continuous physics: Flow-Lenia

Lenia's gliders survive only in a narrow band of rules, partly because nothing stops matter from appearing or vanishing. **Flow-Lenia** (Plantec et al. 2023) changes that: matter is never created or destroyed, it only *flows*. Its authors report that moving creatures are common in it and that creatures can even evolve inside the simulation, but they give no counts and no comparison with chance. So we treat these as claims to test, not results to inherit.

Overnight a separate agent implemented Flow-Lenia from the paper's equations and put it through the project's validation (J-016):
- **Mass is conserved** to the limit of float precision (worst drift 1.5 parts in 100 million over 1000 steps).
- **Controls pass:** a static-blob rule is not called complex; pure diffusion spreads but produces no movers; a rotated starting world gives exactly the rotated result (so the grid itself does not create fake motion).
- **A first version stored cells with 256 levels and was rejected:** rounding stopped slow flows dead (pure diffusion froze after 50 steps). The engine now supports floating-point cells; all earlier results are byte-for-byte unchanged.
- **No mover found yet:** 168 random rules (80 of them in full float precision), started from the paper's own random patch, produced no structure that travels by itself. This agrees with the paper's remark that single-channel movement needed long optimisation, and it means Flow-Lenia does not yet have the positive control our rules require before running experiments on it.
- **Smooth starts don't help here (E-16):** 100 random rules × 4 kinds of start gave **0 movers in 400 worlds**. The authors' claim that moving patterns are "quite common" is not reproduced, either because of details the paper leaves unspecified, or because their "dynamic" patterns mostly wobble in place (J-018).

## 8 · Saturday morning: three more answers and one weakness

A second session picked up the open items from the night. Everything below was pre-registered except the held-out check, which was a planned diagnostic.

### A third kind of mover, found by chance (C-02, E-26)

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/heldout-mover.gif' | relative_url }}" alt="A small world where two ring-shaped creatures form from a smooth start; then one creature alone moving in a straight line with a faint trail"><p><b>The "ring glider"</b> (rule μ 0.277, three kernel rings). First its world, from a smooth start: two ring gliders form. Then one of them cut out and run alone for 1000 steps: it keeps its body (mass ~178) and travels in a <b>dead straight line</b> at ~0.085 cells per step.</p></div>
<div class="card"><p><b>Confirmed (E-26, pre-registered, 160 worlds):</b></p><p>Smooth starts: <b>13 of 40</b> worlds (density 0.35) and <b>18 of 40</b> (density 0.18) grew a verified ring glider. Soups: <b>0 of 80</b>; every one died. p = 4 × 10⁻⁵ and 3 × 10⁻⁷. All 36 survived 1000 steps alone.</p><p>It is as slow as the wanderer but never turns, and 2.5× heavier than a glider. The rule was one of 120 drawn <b>at random</b> for an unrelated check, not found by the search: from smooth starts, mover rules are not vanishingly rare.</p></div>
</div>

### Chan's own start works, given room (E-24)

Chan (2019), who discovered Orbium, says creatures emerge from random starts "given enough time". His start is 15–40 dense square patches in empty space. On our 128×128 worlds it had made nothing. In worlds 4× larger, run 1.5× longer, it made gliders in **13 of 160** worlds. We had predicted at most one or two, so the prediction was wrong.

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/e24-patches.gif' | relative_url }}" alt="Scattered square patches of random values fade away in an empty world; one turns into a glider and travels"><p><b>Patches → one glider</b> (Orbium rule, 256×256, first 600 steps). Most patches fade within ~50 steps; one becomes a glider and travels on. With 110 patches (as crowded as Chan's count on a small world), the blob field won every time.</p></div>
<div class="card"><img src="{{ '/assets/report/e24-patches.png' | relative_url }}" alt="Bar chart: worlds with a verified glider by start condition and world size"><p>Chan's start makes gliders in ~8% of big worlds, smooth starts in ~18%, the same rate as in small worlds. Both starts that work put matter in <b>isolated lumps with room around them</b>; fine-grained soups almost never do. All 51 movers survived 1000 steps alone.</p></div>
</div>

### A better detector for slow movers (E-25)

The detector missed about 8% of wanderers (J-022). We tried two fixes on **3,789 stored worlds**, checking every detection against a ten-times-longer test (1000 steps alone):
- **Letting a slow object run 300 steps alone instead of 100** found 3 more wanderer worlds (96 → 99 of 160). Every extra detection passed the long test, and no new false positive appeared in any of the 2,485 worlds with no known creature.
- **Loosening the "fairly straight path" rule** found nothing more and let one fragment of junk through.

The first fix is now part of the detector (D-027), with four new validation checks; the second was rejected. About 95% of wanderers are now detected.

### A weakness in one of our own thresholds (C-02)

To stop fields of motionless blobs from being ranked as interesting, the observer calls a world *quasi-static* when its activity outside still blobs is below 0.002 (the J-012 fix). That cut-off was set on 60 rules. On 120 **new** rules the values do not split cleanly at it:

<figure>
<img src="{{ '/assets/report/heldout-cutoff.png' | relative_url }}" alt="Dot plot of free activity for three sets of rules with a red cut-off line; many dots lie close to the line">
<figcaption>Free activity of every mover-free random rule; the red line is the cut-off. On new rules many fall close to it. About one in six static-looking soup fields lands just above it, mostly because creeping blob edges reach past the 3-cell margin the measure leaves around each blob.</figcaption>
</figure>

This does **not** create false creatures: a world is only called complex if something verifiably moves by itself. It means the search can still waste some effort on static fields. Recorded as an open problem (J-028), not yet fixed.

## 9 · Saturday: can anything here reproduce?

You asked what could give us **reproduction and heredity**. Before looking for it, we needed a way to recognise it: our old replication test only works for exact cell patterns, and Lenia creatures never repeat exactly.

**The birth detector.** It cuts one object out, puts it alone in an empty world and runs it. A **reproducer** must make copies that keep multiplying (similar mass, most of the matter in the world), and then one of those copies, put alone in a fresh world, must do it again. We checked it on systems where the answer is known:

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/e27-gray-scott.gif' | relative_url }}" alt="One round spot divides into two, then four, then more, filling an empty world"><p><b>A known reproducer.</b> In Gray-Scott reaction-diffusion (Pearson 1993), one spot grows and divides, and its daughters divide again. The detector says <b>reproducer</b>, as it does for HighLife's famous replicator. Note these copies are all identical: reproduction <i>without</i> heredity.</p></div>
<div class="card"><img src="{{ '/assets/report/e27-labyrinth.gif' | relative_url }}" alt="A small Lenia blob alone in an empty world bursts into a labyrinth of stripes and blobs that fills the world"><p><b>Not a reproducer.</b> A Lenia blob placed alone bursts into a labyrinth that fills the world in ~800 steps, then stops changing. Its ~80 pieces have about the parent's mass, and the <b>first version of our detector counted them as copies</b>.</p></div>
</div>

<figure>
<img src="{{ '/assets/report/e27-copy-counts.png' | relative_url }}" alt="Copies over time on a log scale: the Gray-Scott line climbs in steps 1, 2, 4, 8, 16; the Lenia line jumps to about 80 before step 1000 and then stays flat">
<figcaption>The difference in one picture. Real division doubles again and again (blue; the dips are moments when every spot is mid-division). The labyrinth jumps once and stops (orange). The detector now requires copies to at least double after the first quarter, and every copy is compared with the original parent.</figcaption>
</figure>

**What we found (E-27, E-28, both pre-registered):**
- **None of our creatures reproduces.** 0 of 285 movers (gliders, wanderers, ring gliders) in 218 worlds made even one generation of copies.
- **The first detector was fooled**, as shown above, in 2 blob-field worlds. We looked at the cases (as pre-registered), fixed the rule, and made the labyrinth a permanent trap in the benchmark.
- **The fixed detector, on 350 worlds it had never seen: 0 reproducers.** Its known positive (Gray-Scott) was found in 10 of 10 worlds both times.

So in the Lenia rules we have explored, things either travel, sit still, or spread. Nothing grows and divides into copies of itself. The literature points to where to look next: Lenia with several channels (Chan 2020 reports self-replicating creatures there), and Flow-Lenia where each creature **carries its own rule parameters**, so offspring can inherit them and differ (Plantec et al. 2023). That second one is the most direct route to heredity, and it is planned below.

## 10 · Saturday afternoon: looking for reproduction everywhere, and a test for heredity

**Is reproduction just somewhere else in rule space? (E-29, pre-registered)** Our earlier tests only looked at creatures we had already found. This time we gave **every rule drawn at random**, 3000 of them, the same chance: one smooth lump of matter alone in an empty world, then the birth detector on whatever it became.

<figure>
<img src="{{ '/assets/report/e29-lump-scan.png' | relative_url }}" alt="Scatter of 3000 rules by growth centre and width: grey extinct rules at narrow widths, blue tested rules over most of the map, red undecided rules at large mu and wide growth, orange world-filling rules at the top">
<figcaption>Each dot is a rule. <b>No reproducer anywhere</b> (none would show as a green star). Blue: an object was fully tested and did not reproduce (1453 rules). Red: every object grew into a front that filled the test world before the detector could decide (410). Orange: the lump itself filled the world (228). Grey: the lump died (909). The detector's known reproducer, Gray-Scott, was found 10 times out of 10.</figcaption>
</figure>

- **0 reproducers in 3000 rules**, and not one rule that even managed one generation. In Lenia's basic form, a lump dies, settles, travels, or spreads. It never grows and divides.
- **An honest limit:** for about a fifth of the rules the test cannot decide, because anything placed in them spreads across the world. We looked at the closest cases; none was dividing.
- **What this means:** a search that rewards "almost reproducing" has nothing to climb in this family. The next places to look are richer physics: several channels (where Chan reports self-replicating creatures) and Flow-Lenia.

**A test for heredity.** If something does reproduce one day, we will need to know whether offspring **inherit** something from their own parent. The trap is that neighbours look alike simply because they share a place. So the test **moves** each parent alone into an empty world, lets it reproduce there, and compares its offspring with it. We checked it on Gray-Scott spots carrying a coloured "trait" that does not affect them:

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/heredity-carried.gif' | relative_url }}" alt="Six coloured spots divide and spread into colonies; each colony keeps its founder's colour"><p><b>Inheritance you can see.</b> Six founder spots with different traits (blue to red). As they divide, each colony keeps its founder's colour. (The trait is a dye: it does not change what the spots do, so this is a test bench, not evolution.)</p></div>
<div class="card"><img src="{{ '/assets/report/heredity-controls.png' | relative_url }}" alt="Three scatter plots of offspring trait vs parent trait: on the diagonal for carried traits, a flat cloud for redrawn traits, no relation for traits set by position"><p><b>The test sorts the three cases.</b> Left: the trait travels with the spot, so offspring match their parent (r = 1.0). Middle: the trait is noise (no heredity). Right: the trait is set by <i>where</i> a spot is, so neighbours in the world look alike, but once moved, offspring no longer match their parent: <b>no heredity</b>, correctly.</p></div>
</div>

**Flow-Lenia where creatures carry their own rules.** We built the variant from Plantec et al. (2023) in which every cell carries its own rule parameters, which travel with its matter and mix where flows meet, plus an optional thin layer of "food" (mass is conserved, so copies need material). With everyone's parameters equal it behaves exactly like ordinary Flow-Lenia. Then we ran E-30: 100 random rules, worlds seeded with six "species", with and without food.

**A false alarm, caught (E-30).** In fed worlds the detector reported **reproducers in 17 of 100**, and even heredity in one. We did not believe it, and looked:

<figure>
<img src="{{ '/assets/report/e30-condensation.gif' | relative_url }}" alt="Two panels. Left: a single small lump in a thin layer of food; droplets appear around it and spread until they fill the world. Right: the same food layer with faint noise and no lump; droplets appear everywhere and fill the world too.">
<figcaption><b>Left:</b> one small lump in a fed world "reproduces" into a hundred droplets. <b>Right:</b> the same food with a faint ripple of noise and <b>no lump at all</b> does the same. The food itself is unstable: a perfectly even layer never changes, but any disturbance makes it condense. These are not offspring.</figcaption>
</figure>

- The detector's "empty world" control used a perfectly even food layer, which never changes. **It now also checks a slightly disturbed empty world** (D-030). Copies that appear there are not reproduction. The known reproducer, Gray-Scott, still passes.
- **Rescored: 0 reproducers.** All 17 false hits came from rules whose food is unstable, and that turned out to be **68 of the 100 rules**. In the 32 rules with stable food, nothing reproduced.
- **Lesson for what comes next:** feeding a world can make the food the most active thing in it. Future fed-world experiments will first check that their food is stable.

## 11 · Saturday night: the first reproducer in Lenia, and a clean negative

**A held-out check of the fix (E-31, pre-registered).** The fed-world false alarm (section 10) was fixed *after* we had seen the data, so we tested the fix on 400 new rules. First, each rule's food layer was checked on its own: only **36%** of rules have stable food at the usual amount, and **24%** with 60% more food. Then 97 worlds with stable food, six "species" each: **0 reproducers**, and no false alarm. The known reproducer (Gray-Scott spots carrying a trait) still passed, with heredity, 4 times out of 4.

**Several channels (E-32, pre-registered).** Chan reports self-replicating creatures in Lenia with several channels (several interacting fields). We repeated the 3000-rule lone-lump test on 1000 random rules with 2 or 3 channels. We predicted 0 reproducers. **We were wrong: one rule reproduces.**

<figure>
<img src="{{ '/assets/report/e32-divider-strip.png' | relative_url }}" alt="Nine frames: a small spot stretches, splits into two, and each half splits again into smaller spots">
<figcaption>Rule #970, one small spot alone in an empty world, every 50 steps. It stretches, <b>splits in two</b>, and the halves split again.</figcaption>
</figure>

<div class="cards two">
<div class="card"><img src="{{ '/assets/report/e32-divider.gif' | relative_url }}" alt="A single spot divides repeatedly until about a hundred spots tile the world"><p><b>From one spot to a hundred.</b> 2000 steps. The spots divide until they tile the world, then stop. New matter only appears next to existing spots; the empty world, even slightly disturbed, stays empty.</p></div>
<div class="card"><p><b>What we checked before believing it:</b></p><ul><li>both object types in the world passed <b>two generations</b> (copies of copies);</li><li>three <b>new</b> random starts: reproducer 3 times out of 3;</li><li>the empty and the disturbed empty world make <b>no copies</b> (the test that caught the food condensing);</li><li><b>but</b> scrambled lumps also turn into the same spots: the spot is the rule's single stable form, as in Gray-Scott. Offspring are copies of <i>the rule's</i> spot, not of their own parent, so <b>there is nothing to inherit</b>.</li></ul></div>
</div>

- **How rare:** 1 rule out of 450 we could decide on (about 0.2%). Single-channel Lenia had 0 of 1453; the difference is not statistically significant (p = 0.24).
- **A twist:** the rule's second channel dies out, so all the matter is in one channel. Yet the second channel still matters: in our version of multi-channel Lenia an empty channel still "votes" on growth, and its vote is always "shrink", acting as a uniform decay. Without it (same two kernels, one channel) the spots do not divide.
- **Evidence level 3, in its weakest form:** reproduction is real and verified, but heredity is impossible because there is only one type. It is the textbook reaction-diffusion reproducer, now found in Lenia by a random draw.

## Where this leaves the project

| Evidence level | Life-like rules (v0.1–v0.4) | Lenia (tonight) |
|---|---|---|
| 1 · persistent organisation | yes | yes |
| 2 · self-propelled structures | yes | **yes, arising spontaneously from correlated starts** (gliders; a turning "wanderer"; a straight "ring glider"); from Chan's sparse patches in big worlds too |
| 3 · self-replication | not observed | **yes, in one multi-channel rule (E-32): dividing spots of a single type**, like Gray-Scott; none in 3000 random single-channel rules from a lone lump (E-29), none in fed Flow-Lenia (E-30, after removing a false alarm; E-31 held out); no births in big worlds (E-15), in 500 glider collisions (E-20) or 200 wanderer encounters (E-22); gliders can *fuse* into a larger mover, wanderers absorb each other. A validated birth detector finds no reproducer in 568 worlds (E-27, E-28) |
| 4 · heredity and variation | not measured | a validated heredity test exists (J-033); the only Lenia reproducer has one attractor type, so nothing can be inherited |
| 5 · open-ended evolution | not observed (knockouts ≈ placebo) | not tested |

**Mistakes we caught and recorded:** two wrong predictions about Chan's start and world size (J-029); a cut-off whose safety margin did not survive new rules (J-028); an over-inclusive mover check in a new script (J-025); the inflated label (J-012); a pre-registered test that could not reach its own threshold (J-014); a glider speed documented 5× too low, because measuring across more than half the world wraps around (J-012); a quick glider counter whose "births" were artefacts (J-017).

## What next

1. **Map the ring glider's neighbourhood** in rule space, as E-18b did for the wanderer, and test whether patch starts work in the wanderer and ring-glider rules too.
1. **Interactions as a route to new structure:** gliders can fuse into double gliders (E-20), but the chain stops there (E-23); wanderers absorb each other (E-22). Other rules or physics (multi-channel Lenia) may allow deeper combination. A knockout test on fusion events (J-010 style) would show whether later structures depend on earlier ones.
2. ~~A better detector for slow, turning movers~~ done (E-25, D-027; ~95% detected). Remaining: wanderers that circle tightly. Also **fix the quasi-static margin** (C-02), e.g. a margin that scales with the kernel radius, with its own controls.
3. **Rates vs world size and run length**, measured with the validated detector at checkpoints (E-15 used a quick counter for its time series).
4. ~~Chan's patch protocol in larger worlds~~ done (E-24: 8% of 256² worlds). Next: separate world size from run length, and test the "isolated lump" mechanism directly.
5. ~~A replication detector for continuous physics~~ done (D-028, E-27/E-28: none found).
6. **Flow-Lenia:** find a positive control (several channels; check our implementation against the paper's figures), then run the same validated pipeline: does mass conservation make movers and evolution more common, as its authors claim?
7. **Heredity (Track D):** ~~a heredity measure~~, ~~Flow-Lenia with travelling parameters and food~~ (J-033, E-30, E-31: no reproducers), ~~multi-channel Lenia~~ (E-32: one rule of dividing spots, a single type). Next: search multi-channel rule space *around* the dividing rule for rules with **several** distinct reproducing types (the minimum for heredity), and test what the empty-channel decay term does across rules. In parallel, **program soups** (section 12, if E-40 finishes), where self-copying programs are reported to emerge from random code.

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
| 05:12 | E-22: wanderers absorb each other when they meet; no births (J-026) |
| 05:18 | E-23: double glider + glider never makes a triple; the chain stops at two (J-027) |
| 05:25–06:38 | First session ends; a scheduled task resumes the work |
| 06:41 | Held-out check of the quasi-static cut-off (C-02): no clean gap; a random rule makes a new mover |
| 06:41–08:16 | E-24: Chan's patches in big worlds make gliders (13/160) |
| 06:46–08:13 | E-25: detector calibration on 3,789 worlds; 300-step isolation adopted (D-027) |
| 08:22 | E-26: the "ring glider" confirmed, 31/80 smooth vs 0/80 soups |
| 08:30–09:05 | You asked about reproduction and heredity: birth detector and Gray-Scott control built; E-27 pre-registered |
| 09:06–09:47 | E-27: no mover reproduces; the first detector is fooled by labyrinth bursts; fixed, E-28 pre-registered |
| 10:18 | E-28: 0 reproducers in 350 held-out worlds |
| 12:38 | A scheduled session resumes; E-29 (3000 random rules) pre-registered and running |
| 12:50–13:30 | Heredity test and its controls; Flow-Lenia with travelling parameters (J-033) |
| 13:53 | E-29: 0 reproducers; E-30 (fed Flow-Lenia) starts |
| 16:35 | E-30: 17 apparent reproducers; inspection shows food condensing |
| 17:00–18:05 | Detector fixed (perturbed-vacuum null, D-030); rescore: 0 reproducers; only 32/100 rules have stable food |
| 20:55 | Multi-channel Lenia built (D-031); E-31 (held-out fed worlds) and E-32 (1000 multi-channel rules) start |
| 21:20 | Program soups (BFF) built in a parallel session: interpreter, replicator detector and its controls |
| 00:45 | E-40 (do self-copying programs emerge?) pre-registered and running |
| 01:10–01:45 | E-31: 0 reproducers on stable food. E-32: one rule makes dividing spots; checked by eye, from 3 new starts, and by reduction |

Everything was done on branches, checked with `pytest` and the validation benchmark, and merged by pull request. The benchmark now has 102 checks, all passing.

## Read more

- Journal entries [J-012 to J-037]({{ '/journal.html' | relative_url }}) (full numbers, caveats, commits); independent review [R-4]({{ '/reviews.html#r-4' | relative_url }}); [Decisions]({{ '/decisions.html' | relative_url }}) D-022 to D-031; [Experiments]({{ '/experiments.html' | relative_url }}) with exact commands and data.
- Pre-registrations: [E-13](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e13-preregistration.md), [E-14](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e14-preregistration.md), [E-17](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e17-preregistration.md), [E-18](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e18-preregistration.md), [E-19](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e19-preregistration.md), [E-20](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e20-preregistration.md), [E-21](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e21-preregistration.md), [E-22](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e22-preregistration.md), [E-23](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e23-preregistration.md), [E-24](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e24-preregistration.md), [E-25](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e25-preregistration.md), [E-26](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e26-preregistration.md), [E-27](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e27-preregistration.md), [E-28](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e28-preregistration.md), [E-29](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e29-preregistration.md), [E-30](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e30-preregistration.md), [E-31](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e31-preregistration.md), [E-32](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e32-preregistration.md).
- Every figure is regenerated by `python scripts/make_report_figures.py`.

**Glossary.** *Lenia*: a cellular automaton with continuous cell values and smooth, ring-shaped neighbourhoods (Chan 2019). *Glider*: a pattern that keeps its shape and travels. *Soup*: a random start where each cell is independently filled. *Smooth start*: random noise blurred over ℓ cells. *Pre-registered*: the test and its threshold were written down and committed before the data existed. *Evidence level*: the project's ladder from persistent organisation (1) to open-ended evolution (5).
