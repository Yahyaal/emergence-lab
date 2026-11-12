---
title: Report
description: Overnight research report, 7 November 2026. Lenia, spontaneous gliders, and what made them appear.
---

# Overnight report · 7 November 2026

<p class="lead"><b>Updated Wednesday evening.</b> Section 25: we built a looser, validated replicator detector and re-scored all 392 soups of sections 22–24. <b>Whether</b> universes make replicators does not change at all. <b>How fast</b> does: the five-generation predictor that "failed" in section 24 now shows a <b>tenfold</b> speed difference in the predicted direction (163 vs 1,638 rounds), though still short of our significance bar; we report it as unresolved. Section 24 (Tuesday evening): following copies of copies for five generations explained why two predicted-fast universes were slow, but it <b>failed to predict</b> speed in 16 new ones (pre-registered). It also exposed a flaw in how we time replicators: in some universes the replicators copy 59 of 64 bytes, and our detector requires 60, so it reported "nothing" in soups that were full of them. Section 23 (Tuesday morning), corrected: more short self-copiers means faster replicators <b>within</b> one version of the language, under either way of timing. Whether it holds <b>across</b> versions depends on how jumps are timed. Section 22 (Monday night): the "copy that copies" property predicted which of five languages' versions make replicators: <b>60 of 60</b> predicted soups, against 15 of 60 others.</p>

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
<div class="card"><div class="stat">3 / 16</div><p>Sunday: in a <b>soup of random programs</b>, self-copying programs appeared on their own and took over, in <b>3 soups of 16</b>, all after thousands of rounds. In every soup that made the jump, the detector confirms <b>real replicators, in several variants</b>; in none of the others (E-40, E-41).</p></div>
<div class="card"><div class="stat">9 / 9</div><p>Sunday: every emergent replicator we tested <b>passes its mutations on</b> to its descendants (E-42). <b>Heritable variation, level 4</b>, a first for the project. In head-to-head races the variants look <b>neutral</b> (E-43).</p></div>
<div class="card"><div class="stat">7 : 3</div><p>Sunday morning: every replicator that emerged copies itself <b>backwards</b>, alternating between a program and its mirror image (E-44, E-46). Raced against each other, most are <b>equally fit</b>, but one species <b>wins about 7 races in 10</b> against another soup's replicators, and it beats a family that was common <b>earlier</b> in its own soup. Pre-registered, checked with fair counting and 24 neutral controls (E-45, E-46). The third ingredient of natural selection, <b>differences in success</b>, in one clear case.</p></div>
<div class="card"><div class="stat">100% → 10%</div><p>After the jump no single species takes over: a soup becomes a shifting cloud of variants whose most common code keeps <b>drifting away from the founder</b> (E-47). Is the later code fitter? In a first test, in one soup; in a cleaner, pre-registered confirmation, <b>not reliably</b>: later replicators win 51.6% of races (E-48, E-49). <b>Most of the change looks neutral</b>; cumulative evolution is not shown.</p></div>
<div class="card"><div class="stat">4 measures</div><p>Sunday late morning: two new <b>fitness instruments</b>, calibrated on variants whose copying odds we built in. With races, growth rate, and invasion into the soups themselves, <b>later replicators are not reliably fitter</b>. One apparent success (E-52) turned out to be <b>relatives in the count</b>; removing them removed the effect (E-53).</p></div>
<div class="card"><div class="stat">5 / 10</div><p>Sunday: in soups of <b>65,536 programs</b>, half made self-copying code within 24,000 rounds; in soups of 8,192, 2 of 12 in 48,000. The rate grows <b>in proportion to soup size</b>, as predicted (E-50). Our "jump" threshold was fooled three times by short bursts; now stricter.</p></div>
<div class="card"><div class="stat">55 : 0</div><p>Sunday afternoon: why do replicators copy <b>backwards</b>? Because the rule makes it easy: of 1.1 million short program kernels, <b>every copier copies backwards</b> (55 of 55). Move one pointer's starting point and <b>every copier copies forwards</b> (139 of 139). The emergent replicators use exactly these tricks (E-55).</p></div>
<div class="card"><div class="stat">16 / 16 vs 0 / 12</div><p>Sunday evening: change where one pointer starts and soups make (forward-copying) replicators <b>within a few hundred rounds</b>, against none in 16,000 under the normal rule. Under the normal rule the smallest replicator needs <b>two copiers facing opposite ways</b> (10 instructions instead of 5). A control rule with as many copiers, all backwards, is slow again: <b>3 of 24</b>, against <b>16 of 16</b>. Across all 128 versions of the rule, only the 4 that allow a short self-replicating copier make replicators fast (E-56–E-60).</p></div>
<div class="card"><div class="stat">36 / 40 vs 2 / 32</div><p>Monday early: the property "the simplest copier makes a copy that works", computed from the rule in seconds, <b>predicted which rules make replicators quickly in a second, new family of rules</b>, twice (E-64, E-65, pre-registered; all 10 such rules of 1,024; section 18).</p></div>
<div class="card"><div class="stat">p = 0.64</div><p>Monday early: in 7 soups run 20,000 rounds past their jump, replicators from late are <b>not fitter</b> than those from early on. The code drifts; we see no sign of it improving (E-54, section 19).</p></div>
<div class="card"><div class="stat">99.8%</div><p>Monday morning: repeat our replicator test 10 times and <b>almost every common program in a jumped soup copies itself</b>; the "non-replicators" of section 19 were bad luck in a single test. <b>No parasites</b> among them, nor among 420 rarer programs; the first version of our new parasite detector was fooled twice, and fixed (E-66, E-67, section 20).</p></div>
<div class="card"><div class="stat">0 / 24 vs 12 / 12</div><p>Monday afternoon: change the program length and the map of fast rules moves with it (pointers half a tape apart), but <b>16-byte programs made no replicators in 24 soups</b>, while 128-byte programs did in every predicted soup. Prediction failed (E-68, section 21). With the same amount of code, 16-byte programs: 4 of 12 (E-69).</p></div>
<div class="card"><div class="stat">60 / 60 vs 15 / 60</div><p>Monday night: change <b>what an instruction does</b>, five different ways, and the rule property still predicts which universes make replicators fast: <b>all 60 predicted soups did</b>, 15 of 60 others (pre-registered, E-70, section 22). Versions with more short self-copiers were faster.</p></div>
<div class="card"><div class="stat">p = 0.006</div><p>Tuesday: more short self-copiers means faster replicators <b>within</b> a language version (pre-registered, passed, and robust). Across versions it depends on how jumps are timed. 21 of 22 new predicted-fast versions made replicators; one made <b>none in 8 soups</b> (E-71, section 23).</p></div>
<div class="card"><div class="stat">59 / 64</div><p>Tuesday evening: a five-generation version of our predictor <b>failed</b> on 16 new universes (pre-registered). And in two of them, soups our detector called empty were full of replicators that copy <b>59 of 64 bytes</b>, one short of its threshold. Speed results now need two detectors to agree (E-72, section 24).</p></div>
<div class="card"><div class="stat">10× vs 1.1×</div><p>Wednesday: a looser replicator detector, checked against sloppy copiers, empty soups and decoys (the old one accepted <b>37 of 64 decoys</b>; the new one none). Re-scoring 392 soups changes no verdict about <b>whether</b> soups make replicators, but turns a 1.1× speed difference into <b>10×</b> (p = 0.06, unresolved; E-73, section 25).</p></div>
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

## 12 · Sunday early: self-copying programs, from random code

A completely different kind of universe. Instead of a field of matter, a **soup of 16,384 tiny programs**, each 64 random bytes, written in a ten-instruction language (BFF, from Agüera y Arcas et al., 2024). Every round, programs are paired at random, each pair is glued into one tape and run, so a program can read and **overwrite its partner**, and then the two are split again. A few bytes are randomly changed each round. Nothing rewards copying. The paper reports that self-copying programs nevertheless appear and take over. We built this, plus a **replicator detector** held to the same standard as the Lenia birth detector: copies of a candidate are put among random programs and must **multiply for two generations**, while random programs must not (D-040). The detector passed all its controls, including a hand-written self-copier and a deceptive "copying rule" in which every program is copied whether it does anything or not.

<figure>
<img src="{{ '/assets/report/e40-bff-entropy.png' | relative_url }}" alt="Line chart of soup repetitiveness over 48000 epochs: most grey lines stay flat near 0.3; one red line jumps to about 3 at epoch 8750; an orange control line sits near 7; a green control line at 0">
<figcaption>How repetitive each soup is (its "high-order entropy": near 0 for random bytes, high when the soup is full of repeated code). <b>Three soups in 16 made the jump</b>: a pilot run (purple) and, when run three times longer, two of our 12 pre-registered soups (red). The orange control shows why the entropy alone is not proof: a rule that blindly copies programs makes the soup very repetitive with <b>no replicator in it</b>.</figcaption>
</figure>

- **E-40 (pre-registered): 0 of 12 soups made the jump in 16,000 rounds.** We had predicted 2 to 6, based on 1 jump in 4 pilot runs. **Wrong again**: one success in four was luck. Our soups are 8 times smaller than the paper's, which probably makes the jump rarer.
- Something does happen in every soup before any jump: the share of bytes that are instructions rises from 3.9% to about 15%, and stays there. Code that does something survives encounters better than inert bytes. That is selection, but not yet copying.

**The soup that jumped, examined (E-41).** The simulation is exactly repeatable, so we replayed the pilot soup that jumped: the jump came back **at the same round, 8,750, bit for bit**. Then we ran the detector on it, 1,000 rounds later.

<figure>
<img src="{{ '/assets/report/e41-bff-soup.png' | relative_url }}" alt="Three panels of coloured pixel rows. Left: random speckle. Middle: more coloured instruction bytes but still varied rows. Right: most rows share the same instructions at the same positions, forming vertical stripes">
<figcaption>Pilot soup seed 901, replayed. Programs as rows of coloured bytes (colour = instruction type, dark = data). <b>Left:</b> the random start. <b>Middle:</b> just before the jump, richer in instructions but still all different. <b>Right:</b> 1,000 rounds after the jump, most programs carry the same code at the same positions (the vertical stripes): one family of self-copying programs and its variants has spread through the soup.</figcaption>
</figure>

- **The detector confirms emergent self-replicators.** Of the 4 most common programs, **2 are replicators** (8 copies became 116 and 71 among 1024 random programs, and their copies multiplied again), and the other 2 multiplied for one generation. Random programs never multiply under the same test.
- They are **variants of one family**: the common programs differ in a few bytes around a shared core. Different replicators, mutation, competition: that is the raw material for heredity and evolution (levels 4 and 5), which in Lenia we never had.
- **How often? (E-41, pre-registered).** We ran the 12 soups of E-40 three times longer (48,000 rounds). **Two of them made the jump** (at rounds 32,000 and 43,250; red in the chart above), as predicted (2 to 6). Both contain replicators confirmed by the detector. In the 10 soups that did not jump, the detector found **no** replicator. In all, 3 transitions in 16 soups, and every one of them produced real self-copying programs.
- **Evidence level 3, from random code, with no fitness function**, in a second universe and in a stronger form than Lenia's dividing spots: here there are many competing variants, not one fixed type.

**Do the variants pass on their differences? (E-42, pre-registered).** We took the 9 distinct replicators the detector had confirmed, and made 24 one-byte mutants of each. Each mutant was put alone, as 8 copies, in a fresh soup of random programs. Then we checked whether its descendants carry the mutation, and, as a control, how often that byte shows up there when the unmutated replicator is used instead.

<figure>
<img src="{{ '/assets/report/e42-bff-heredity.png' | relative_url }}" alt="Grid of nine rows (replicators) by 64 byte positions; most mutated positions are green (inherited), some grey (the mutation stops copying), one red">
<figcaption>Each coloured cell is one mutant. <b>Green:</b> the mutant still copies itself and its descendants carry the mutation. <b>Grey:</b> the mutation breaks copying (those bytes are the replicator's working code). <b>Red:</b> copies, but the mutation is lost (once in 141).</figcaption>
</figure>

- **All 9 replicators show heredity** (we predicted at least 7). 54–83% of mutants still copy themselves, and in 140 of those 141 the mutation is carried by the descendants, almost always by every one of them. Without the mutation, that byte never appears there.
- The test passed its controls first: a hand-written copier shows heredity; the same program in a world where nothing runs, or where the rule copies everything blindly, shows none.
- **Evidence level 4: heritable variation**, in replicators that arose by themselves from random code. This is the first time the project reaches level 4. What it is not yet: **evolution** (level 5) needs variants that compete and change over time; see the next test.

**Do some variants win? (E-43, pre-registered).** Evolution by natural selection also needs variants that spread better than others. We put each of the 141 working mutants in a head-to-head race against its parent (equal numbers at the start, 8 repeat races each). **Only 2 of 141 lost consistently, and none won**: no more than chance allows (a neutral control gave 0 of 24). We had predicted 5–30% losers. The races are winner-take-all, so the test only sees large differences. As far as it can tell, a one-byte change that leaves a replicator working is **neutral**. The third ingredient of natural selection, differences in success, is **not shown** by this test.

**Replicators from different soups (E-44, pre-registered).** Replicators from different soups share almost none of their bytes, so if some copy better than others, races between them should show it. We raced all 36 pairs of the 9 emergent replicators, 16 races per pair, everything done twice on fresh soups, and also raced each against our hand-written copier.

<figure>
<img src="{{ '/assets/report/e44-bff-contests.png' | relative_url }}" alt="Left: a 10 by 10 colour matrix of race results, mostly pale, with the bottom row (hand-written) blue and two columns (soup 5006 at 32k) reddish. Right: scatter of batch A against batch B results, points spread with little correlation">
<figcaption><b>Left:</b> how often the row replicator ends more common than the column one (log-ratio; blue = row wins). Most cells are pale: no consistent winner. The <b>hand-written copier (bottom row) beats every emergent replicator</b>. <b>Right:</b> the same race run twice on fresh soups gives weakly related results (Spearman 0.22): most differences between emergent replicators are noise.</figcaption>
</figure>

- **No pair of emergent replicators had a clear winner: 0 of 36** (we predicted at least 30%). Race results barely repeat between the two batches. At this resolution, replicators that arose separately are **about equally fit**.
- Our hand-written copier seemed to win most races against the emergent ones (222 of 287), but that was mostly a **counting mistake**, explained just below: with fair counting it wins only 56% (E-46).
- **A surprise: a mirror replicator.** Two of the replicators from soup 5006 are **exact reverses of each other**, byte for byte. When one runs, it leaves itself intact and writes its own reverse into its partner; the reverse does the same. Seed one form alone and the soup fills with both, in equal numbers. The species alternates between two forms every generation, a little like a DNA strand and its complement. We then checked the others: **all 9 emergent replicators do this.** In our soups, self-copying arose in the backwards form every time; only our hand-written copier copies forwards. That also means we had been counting each emergent species by half of its members.

<figure>
<img src="{{ '/assets/report/e44-mirror-replicator.png' | relative_url }}" alt="Five rows of coloured bytes: the replicator, a random partner, the partner after one interaction, the replicator read backwards, and replicator 6; the last three rows are identical">
<figcaption>The mirror replicator. After one interaction the random partner (row 2) has become the replicator <b>read backwards</b> (rows 3 and 4), which is exactly the other replicator the detector had found in that soup (row 5). Letters are instructions.</figcaption>
</figure>

**Does one species win? (E-45, E-46, pre-registered).** The race matrix above hinted that the species from soup 5006 at round 32,000 beats soup 901's replicators. We tested that on fresh soups with 64 races per pair (E-45). Then, having found that every emergent replicator has two forms, we **redid everything with both forms counted for every species**, raced all 28 pairs of the 8 emergent species, and added 24 neutral controls (E-46). We predicted that the advantage would turn out to be a counting artefact.

<figure>
<img src="{{ '/assets/report/e46-species-contests.png' | relative_url }}" alt="Left: a 9 by 9 matrix of race win shares, mostly pale near 0.5, with the 5006 at 32k row dark blue (0.56 to 0.79). Right: histogram of neutral controls centred on 0.5, emergent pairs mostly between 0.5 and 0.6, and red lines for the 5006 species between 0.56 and 0.79">
<figcaption><b>Left:</b> share of 64 races won by the row species, with both forms of every species counted. Most cells are near 0.5. The row of the species from soup 5006 at round 32,000 is blue across. <b>Right:</b> the 24 neutral controls (our copier against itself with a different inert tail, grey) sit around 0.5; that species (red lines) is ahead of all 7 other emergent species.</figcaption>
</figure>

- **Our prediction was wrong: the advantage is real.** With fair counting, the 5006 species wins **176 of 252 races against soup 901's species (70%; p = 10⁻¹⁰)**, the same as before. It is ahead of all 7 other emergent species (56–79% of races).
- **It beats an earlier family from its own soup.** In soup 5006, replicator #4 was one of the most common programs at round 28,250 and had disappeared by round 32,000, when this one was among the most common. In a race between the two, the later one wins **46 of 64** (72%). (Neither ever held more than ~2% of the soup; see E-47 below.)
- The neutral controls behave: **0 of 24** show a winner (pooled 50.9%). In E-45, one of 4 had; across all three experiments, 2 of 70 control pairs (~3%), so single-pair verdicts deserve some caution. The other emergent species are indistinguishable from each other.
- **What this means:** among replicators that arose by themselves from random code, we now have **variation, heredity (E-42) and differences in success (E-45, E-46)**, the three ingredients of natural selection, measured in controlled races, plus **one case** where a later family beats an earlier one from the same soup. We have **not** shown that selection keeps changing a soup over time, or that changes accumulate (cumulative evolution, level 5). That is the next question.

**What happens after the jump? (E-47, pre-registered).** We replayed the three soups that jumped, exactly (every earlier checkpoint came back bit for bit), to 40,000 rounds, saving the whole soup every 250 rounds. The plan was to list the dominant species one after another and race each newcomer against the one it displaced. **That plan failed: there is no dominant species to list.**

<figure>
<img src="{{ '/assets/report/e47-turnover.png' | relative_url }}" alt="Left: three jagged lines mostly between 1 and 5 percent, with a few spikes, below and around a dashed 5 percent line. Right: three lines falling from 100 percent to below 20 percent over thousands of rounds">
<figcaption><b>Left:</b> the share of the soup belonging to the family of the most common program, after the jump. It is usually about 2%: no family takes over. <b>Right:</b> how much the most common program still shares with the first one that took over (best of forward and backward reading). It falls steadily: after 10,000–20,000 rounds, the most common code shares only 2–20% of its bytes with the founder.</figcaption>
</figure>

- **No family dominates:** the most common program's family usually holds about 2% of the soup, and the most common program is a different family from one snapshot to the next most of the time. After the jump, a soup is a large, shifting **cloud of related variants**, not a series of species. Our prediction (at least 4 replacements) was wrong: we found 0, so the planned race test could not run.
- **The soups keep changing, far:** the most common code drifts steadily away from the code that started the takeover.
- **What this means:** the soups keep changing, steadily and a lot. We **cannot tell yet whether that change is adaptive or neutral drift**: copying with errors drifts on its own. Telling them apart needs a test with a drift control (for example: do programs from later rounds beat programs from earlier rounds more often than programs from the same round beat each other?). That is the next experiment.

**Is the later code fitter? (E-48, pre-registered).** From the same replays we took the 6 most common programs 1,000 rounds after each soup's jump and 6 from 10,000 rounds after, and raced every late program against every early one (32 races per pair). As a control for drift, we also raced programs from the same round against each other.

<figure>
<img src="{{ '/assets/report/e48-time-races.png' | relative_url }}" alt="Left: dot plot per soup; in soup 5006 most blue dots (late vs early) sit above 0.5, in 5010 they straddle 0.5, in 901 the mean is 0.35 with a group of dots at 0. Right: bars rising from 0.55 to 0.64 with the abundance-rank gap">
<figcaption><b>Left:</b> each blue dot is one late-vs-early pair: the share of races the late program won. Grey: two programs from the same round. Black bars are means. In soup 5006, later code wins most pairs. In soup 901, two late programs lost every race (the dots at 0): they are common in the soup but do not copy themselves in a fresh one. <b>Right (post hoc):</b> between programs of the same round, the more common one tends to win; this is weaker once the two non-copiers are removed.</figcaption>
</figure>

- **Overall, our prediction was not met:** the later program was ahead in 62 of 108 pairs (57%), not enough to rule out chance (p = 0.07).
- **In soup 5006, later code is clearly fitter:** ahead in 28 of 36 pairs (p = 0.0006). That fits E-46, where a later family of the same soup beat an earlier one. Soup 5010 leans the same way (22 of 36); soup 901 does not.
- **A flaw in our own design:** we sampled "the most common programs" without checking that they copy themselves. Two of soup 901's late programs do not, and lose every race. Without them, later code is ahead in 62 of 96 pairs (p = 0.003), but that is decided after looking, so it only motivates a new pre-registered test.
- **What this means so far:** in at least one soup, later code seemed fitter. We then tested that properly.

**The proper test (E-49, pre-registered).** We fixed both flaws: only programs that pass the replicator test, new time points (2,000, 6,000 and 12,000 rounds after the jump, programs never used before), and a same-round control with random order.

<figure>
<img src="{{ '/assets/report/e49-time-races.png' | relative_url }}" alt="Two bar charts around 0.5: by soup, 901 at 0.48, 5006 at 0.55, 5010 at 0.53, control 0.50; by gap, 2000 to 6000 at 0.52, 6000 to 12000 at 0.47, 2000 to 12000 at 0.55, control 0.50">
<figcaption>Average share of races won by the later replicator. Grey: two replicators from the same round (the control), exactly at 0.5. The differences are small: a few percentage points either way.</figcaption>
</figure>

- **Not confirmed:** later replicators were ahead in 24 of 44 cases (p = 0.33). On average they won **51.6%** of races: at most a slight edge.
- The control is clean (50.3%). Soup 5006 again leans towards later code (55%), and the longest gap (2,000 → 12,000 rounds) shows the clearest edge (54.5%); but from 6,000 to 12,000 rounds, later code did slightly *worse*.
- **What this means:** the soups change a lot, but in our races **most of that change looks neutral**. Adaptive, cumulative evolution after the jump is **not shown**. The differences in fitness are small compared with the noise of a race, so the next step is a more sensitive fitness measure, not more of the same.

## 13 · Sunday late morning: measuring fitness like a lab instrument

Races between two replicators (section 12) are noisy: each starts from 8 copies, and luck decides a lot. To ask "is later code fitter?" properly we needed a measure whose accuracy is known **before** it is used on emergent code.

**A calibrated growth rate (D-044, J-050).** We put 16 copies of a program among 4,096 others and measure how fast its copies multiply in the first rounds (the growth rate r, per round). To check the instrument, we built variants of the hand-written replicator whose copying odds we **set ourselves**: a small "trap" makes the copy fail unless a byte of the partner is a multiple of 2, 4, 8 or 16. In a background of programs that never run (so a copy is never damaged), theory then says exactly what r should be.

<figure>
<img src="{{ '/assets/report/d044-calibration.png' | relative_url }}" alt="Left: five blue dots lying on a grey theory curve that rises from 0 to 0.4 as the copying probability goes from 0 to 1. Right: horizontal bars; all ten replicators reach about 0.39 in the harmless background; in random code the hand-written one reaches 0.15 and the nine emergent ones 0.08 to 0.095">
<figcaption><b>Left:</b> measured growth rate of the five variants with known copying odds (dots) against theory (line): they agree within 0.02. <b>Right:</b> in a harmless background every replicator, hand-written or emergent, copies perfectly (grey, the ceiling). In random code (blue, orange), which damages a replicator when it runs second, the emergent replicators spread at about 60% of the hand-written one's rate.</figcaption>
</figure>

- **The instrument works:** measured and predicted rates agree for all five known variants, and two variants whose rates differ by 0.03 are told apart with 8 runs each (p < 0.001). Controls (a program that cannot copy, a rule where nothing runs, a rule that copies everything blindly, and repeated measurements of one program) all behave.
- **Every emergent replicator copies perfectly** when nothing disturbs it. What differs is how well it survives among random code.

**Is later code fitter? (E-51, pre-registered).** We measured r for all 47 replicators of E-49 (three soups, 2,000, 6,000 and 12,000 rounds after the jump).

<figure>
<img src="{{ '/assets/report/e51-growth-rates.png' | relative_url }}" alt="Left: dots by soup and time; in soup 5006 the means rise from 0.088 to 0.097; in 901 they stay at 0.083-0.085; in 5010 they rise then fall. Right: a cloud of points with a weak upward tilt">
<figcaption><b>Left:</b> growth rate of each replicator, by soup and time after the jump (black bars: means). Only soup 5006 rises. <b>Right:</b> the difference in growth rate between two replicators predicts which wins their races only weakly.</figcaption>
</figure>

- **No general trend (p = 0.38), as we predicted.** Soups 901 and 5010 do not rise; **soup 5006 does, by about 10%** (p = 0.005 for that soup alone, but decided after looking). It is the **fourth different measure** in which soup 5006's later code comes out ahead (E-46, E-48, E-49, E-51).
- **The growth rate explains only ~4% of who wins a race** (correlation 0.196; we predicted above 0.2). Races are decided mainly when replicators meet *each other*, which a growth rate into random code does not see.
- **What this means:** the instrument is precise, but it measures the wrong part of fitness for this question. The next measure puts each program back into the soup it actually lives in.

**Fitness in the soup itself (E-52, pre-registered).** We built a second instrument. It drops 64 copies of a program into a sample of a real soup and runs it beside an identical copy of that soup without them (same random pairings), then reads how much the program's family grew compared with the residents it replaced. It is calibrated the same way: a variant that copies 90%, 75% or 50% of the time loses clearly to a normal copier, and two equal programs score the same. We put every replicator into its own soup at an early time (2,000 rounds after the jump) and at a late time (12,000 rounds).

- **Later replicators did better, but only in the later soup** (all three soups; p = 0.045). In the earlier soup there was no difference. This is what adaptation to a changing soup would look like: later code fits the later soup.
- **But we then found a flaw in our own design.** A program's close relatives (≥ 90% identical) exist only in the soup of its own time; 2,000 rounds later none are left. When a relative overwrites one of the injected copies, it still counts as the same family, so relatives can protect a program's score. In the late soup only the late programs have relatives, so "later" and "has relatives here" are the same thing.
- **So the result is suggestive, not established.** We are re-running it (E-53, pre-registered) in soups from other times, where neither group has relatives.

**The re-run (E-53, pre-registered).** Same programs, same instrument, in each soup's snapshots 4,000 and 9,000 rounds after the jump and later still, where none of the programs has any relative.

<figure>
<img src="{{ '/assets/report/e52-e53-invasion.png' | relative_url }}" alt="Bar chart. Left of a dashed line: in the early soups the bars are near zero; in the late soups all three bars are positive, 0.11 to 0.22. Right of the line, three groups of blue bars scattered around zero, mostly slightly negative">
<figcaption>How much better later replicators invade than earlier ones (one bar per soup). <b>Left (E-52):</b> in their own soups, later code is ahead only in the late soup, where only it has relatives. <b>Right (E-53):</b> in soups where neither has relatives, there is no advantage.</figcaption>
</figure>

- **No advantage: later code does not invade better** (p = 0.88; 8 of 9 comparisons within ±0.1, most slightly negative). We had leaned towards this outcome.
- **What this means:** the E-52 effect was most likely produced by relatives in the count, not by adaptation. With four different measures (races, growth into random code, invasion with and without relatives), **later replicators are not reliably fitter than earlier ones.** After the jump, these soups change a lot, mostly by neutral drift. Cumulative evolution (level 5) is **not shown**, and over 10,000 rounds the evidence now weighs against a strong trend.

## 14 · Sunday: bigger soups make replicators sooner

Our soups of 16,384 programs rarely made the jump to self-copying code (3 of 16, after tens of thousands of rounds), while the original paper, with 8 times more programs, saw it within a few thousand. If a replicator arises by a rare accident in any one meeting of two programs, a soup with twice as many programs should jump about twice as often per round. **E-50 (pre-registered)** ran 34 new soups of 8,192, 32,768 and 65,536 programs.

<figure>
<img src="{{ '/assets/report/e50-soup-size.png' | relative_url }}" alt="Left: jump rate per million rounds on a log scale against soup size, rising from about 2 to about 20, with a grey fit line; the 32,768 arm has no jumps. Right: order (HOE) traces of the five largest soups that crossed 1: three orange lines jump to 2.5-4 and stay; two red dashed lines spike to 1.2-1.6 and fall back">
<figcaption><b>Left:</b> jumps per million rounds at each soup size (blue: as pre-registered; orange: only jumps where the detector found a replicator). The grey line is the fit: rate ∝ size<sup>1.02</sup>. <b>Right:</b> the five largest soups that crossed our threshold. Three really jumped (orange: order stays high, replicators found); two were a brief wave of programs writing zeros that died out (red).</figcaption>
</figure>

- **Bigger soups jump sooner, about in proportion to their size** (β = 1.02, p = 0.014, as predicted): half of the 65,536-program soups jumped within 24,000 rounds. A replicator is a rare accident per meeting, and bigger soups have more meetings.
- **Our threshold was fooled three times:** a brief burst of order with no replicator behind it. Counting only verified jumps, the trend is the same but weaker (β = 0.93, p = 0.049). The rule is now stricter: order must stay high for three checkpoints and the detector must confirm (D-045).
- Odd: the 32,768 arm made **no** jump in 12 soups (about 3 expected; chance gives that about 6% of the time).
- **What this means:** the slow start of our soups was mostly a matter of size. To study what happens **after** the jump with many soups, the next experiments should use 65,536 programs.

## 15 · Sunday afternoon: why every replicator copies backwards

Every replicator that emerged in our soups writes its copy **backwards**, so a species alternates between a program and its mirror image (section 12). Only our hand-written replicator copies forwards. Is that something the soups "chose", or a plain property of the rule?

**The idea, written down before the test.** In BFF both of a program's pointers ("heads") start at byte 0 of the 128-byte tape, and they wrap around: one step left from byte 0 lands on byte 127, the partner's **last** byte. So a five-instruction loop, `[{.>]`, copies byte 0 to byte 127, byte 1 to byte 126, and so on: a complete **backwards** copy of the program into its partner. A forwards copy needs a pointer 64 bytes ahead, which takes 64 moves or a counting loop; our hand-written replicator spends 27 bytes on it.

**E-55 (pre-registered)** tried **every** program kernel of 1 to 6 instructions (1.1 million) in two physics: the real rule, and a counterfactual in which one pointer starts at byte 64 instead of 0, nothing else changed.

<figure>
<img src="{{ '/assets/report/e55-copy-kernels.png' | relative_url }}" alt="Left: bar chart. Standard rule: 55 reverse copiers, 0 forward. Counterfactual: 0 reverse, 139 forward. Right: two pairs of colour strips (a 128-byte tape before and after). With kernel [{.>] under the standard rule, the partner half becomes the program's colours in reverse order; with [.>}] under the counterfactual, an exact copy">
<figcaption><b>Left:</b> among all 1.1 million kernels of up to 6 instructions, the copiers. Under the real rule every one copies backwards; move one pointer's starting point and every one copies forwards. <b>Right:</b> a tape (each colour is one byte value) before and after one run: the shortest copier under each rule.</figcaption>
</figure>

- **Real rule: 55 copiers, all backwards. Counterfactual: 139 copiers, all forwards.** The prediction held in both directions; the shortest copiers have 5 instructions in both physics.
- **The emergent replicators use exactly these tricks.** Tracing their runs, all 9 write their copy with a pointer moving **downwards** after it has wrapped around below byte 0; 7 use one pointer (`[<,}]`-style, pulling bytes into the partner), 2 the other (`[{.>]`-style, pushing them).
- Controls behaved: the hand-written replicator counts as forwards, random programs as neither, a program that floods its partner with one value as neither, and a palindrome as both (not counted).
- **What this means:** the backwards copying is a property of the rule, not something the soups learned or chose. The simplest copiers the rule allows are backwards ones, and the soups found those. It also explains the mirror pairs: a backwards copy of a backwards copier is its mirror image, and both must work for the species to persist.

## 16 · Sunday evening: change one detail of the rule, and replicators come 10–100× sooner

Section 15 showed that moving one pointer's starting point (byte 0 → byte 64) turns every short copier from backwards to forwards. Two questions followed: do **real soups** under that changed rule evolve forward copiers, and does anything else change?

**E-56 to E-59 (all pre-registered)** ran 20 soups under the changed rule, plus 24 under a control rule: 4 of 65,536 programs and 8 of 16,384. We first checked that the changed interpreter, with the pointer put back at 0, reproduces our normal soups bit for bit.

<figure>
<img src="{{ '/assets/report/e57-counterfactual-jumps.png' | relative_url }}" alt="Left: dot plot of the round at which each soup jumped, log scale. Pointer at 127, 16,384 programs: 3 of 24 jumped (rounds 3,750 to 11,500). Standard rule, 16,384 programs: 0 of 12 jumped by 16,000 rounds. Pointer at 64, 16,384 programs: 16 of 16 jumped, between rounds 250 and 3,750. Standard rule, 65,536 programs: 7 of 22 jumped, mostly between 10,000 and 22,000. Counterfactual, 65,536 programs: 4 of 4 jumped, by round 1,000. Right: bar chart. Of short copiers, 0 of 52 under the standard rule leave a copy that can itself copy; 97 of 133 under the counterfactual">
<figcaption><b>Left:</b> when each soup jumped (grey triangles: no jump by the end of the run). Orange: our normal rule (earlier sessions); blue: one pointer starting at byte 64 (forward copiers); purple: starting at byte 127 (backward copiers, the control). <b>Right:</b> of all short copiers, the share whose copy can itself copy.</figcaption>
</figure>

- **The soups evolve forward copiers:** in all 20, the most common programs copy forwards (780 of 800; none backwards; the rest are not copiers). In 7 soups under the normal rule, measured the same way: 247 backwards, none forwards. What evolves follows the rule's simplest copiers.
- **And they evolve them much sooner:** all 20 soups jumped within **250 to 3,750 rounds**. Under the normal rule, soups of 16,384 programs: **0 of 12** by 16,000 rounds (p = 8 × 10⁻⁶); of 65,536: 7 of 22 by 24,000 rounds, mostly after 10,000.
- **Why, we think:** a forward copier's copy is an exact copy of itself, so it copies again. A backward copier's copy is its mirror image, and in a mirror the copying loop runs the wrong way and stops working. **None of the 52 short backward copiers leaves a copy that can copy.** To replicate under the normal rule, a program needs a copier facing each way: at least **10 instructions**, against **5** under the changed rule. That is exactly what the 9 emergent replicators we studied are (section 12's mirror pairs).
- **A control rule settles it (E-58):** start the pointer at byte **127** instead. This rule has about as many short copiers as the fast one (127 vs 133), but **all copy backwards**, and **none** leaves a copy that can copy. Its soups are slow again: **1 of 8** made replicators by 16,000 rounds (at round 11,500; they copy backwards), against 8 of 8 with the pointer at 64. **Confirmed with 24 fresh soups (E-59, pre-registered): 2 of 16 vs 8 of 8** (p = 6 × 10⁻⁵). In all: pointer at 64, **16 of 16**; pointer at 127, **3 of 24**; normal rule, 0 of 12. So it is the **direction of copying**, not just any change to the rule, that sets the speed. (Honest note: our pre-registered jump criterion failed in this rule. The background "order" of these soups sits just under its threshold and crossed it in 4 soups with no copier at all; we checked each by replaying it to the end and counted only real jumps. The criterion is now tied to finding copiers, D-046.)
- **All 128 versions of the rule (E-60, pre-registered).** The pointer can start at any of the 128 bytes. For each version we listed every short copier and asked whether any is a full replicator. **Only four versions have one** (pointer starting at bytes 62–65); in **116 of 128** there is no short copier at all. Then we ran soups: in the three new "has one" versions, **12 of 12** soups made replicators, mostly within 2,500 rounds; in four versions picked at random from the rest, **2 of 16**, and those two barely contain copiers. A property you can compute from the rule in seconds predicted which universes make replicators quickly.

<figure>
<img src="{{ '/assets/report/e60-headstart.png' | relative_url }}" alt="Top: bar chart over h from 0 to 127 of short copiers per rule: backward copiers only near 0 and near 127, forward copiers only at 62 to 65, where green stars mark rules with a self-sufficient copier. Bottom: share of soups that jumped by 16,000 rounds: 100% at h = 62 to 65; 0 of 12 at h = 0; 1 of 4 at 7; 0 of 4 at 120; 1 of 4 at 125; 0 of 4 at 126; 3 of 24 at 127">
<figcaption><b>Top:</b> for each version of the rule (pointer 2 starts at byte h), the short copiers it allows; green stars mark versions with a copier whose copy also copies. <b>Bottom:</b> how many soups made replicators within 16,000 rounds, in the versions we ran. Caveat: our copier test only recognises copies placed exactly in the partner's half (or mirrored); one soup at h = 7 looked very active without any such copier, so it may have found a different kind.</figcaption>
</figure>

- **A prediction that failed:** we expected at least 90% of forward copiers to be full replicators; it was 73%. The rest skip their own first byte (they move a pointer before writing), so their copy lacks the start of its loop.
- **What this means for the research question:** how easily self-copying code arises is not a fixed property of "programs"; it hinges on an arbitrary detail of the rule. Rates measured in one rule do not carry over. The changed rule also alters everything else a program can do, so the 5-vs-10 explanation is supported, not proven; the control rule makes it much stronger.

## 17 · Sunday night: a sharp boundary, found after two wrong turns

Section 16 ended with a pattern across all 128 versions of the rule: soups make replicators quickly only in the versions whose simplest copier makes a copy that can copy again. One soup did not fit: under version 7 it looked busy for 7,000 rounds without a single copier.

- **A blind spot in our own instrument (E-60b, exploratory).** Our copier test only recognised copies placed exactly at the partner's first byte. Version 7's soup was in fact full of copiers whose copies sit **6–8 bytes off** (25 of its 40 most common programs). With a test that allows such shifts, **55 of 128 versions** have short copiers, not 12, and the versions with a copy that copies again are **h = 61–68**, not 62–65 (E-61, pre-registered; every such copier copies forwards).
- **A wrong turn: lineages (E-61, E-62).** A copier whose copy is shifted makes a grandchild shifted twice as far, so its line soon loses its loop. We guessed that what matters is a line that lasts. A census of 64-generation lines (E-62, pre-registered) put rules 62–66 in that class, and soups did not care: **all 28 fresh soups in 61–68 made replicators**, those in rules without lasting short lines included. In every one, the copiers that took over were **exact** (no shift): the soups evolve a longer, exact copier within a few thousand rounds.
- **A second wrong turn, in our criterion.** An earlier reading (J-062) had suggested rules 61, 66–68 were "in between" (7 of 16). That was an artefact: those soups were stopped after an early false alarm. Our jump test now drops a false alarm and lets the soup run on (D-047), and needs at least 10 copiers among the 40 most common programs.
- **The boundary holds (E-63, pre-registered).** Four versions drawn at random just outside the band (72, 74, 80, 82) have as many short forward copiers as the versions inside, but none whose copy copies. **1 of 16** of their soups made replicators by 16,000 rounds, against **32 of 32** inside the band (including 4 control soups run alongside).

<figure>
<img src="{{ '/assets/report/e63-boundary.png' | relative_url }}" alt="Top: bar chart over h from 52 to 90 of short forward copiers per rule: none below 59, about 140 per rule from 61 to 79, falling to 0 by 83. Green stars mark rules 61 to 68 (a copier whose copy copies again), on a shaded band. Bottom: share of soups with real replicators by 16,000 rounds: 100% for every tested rule in 61 to 68 (32 of 32), 1 of 4 at 72, 0 of 4 at 74, 80 and 82.">
<figcaption><b>Top:</b> short forward copiers in each version of the rule near byte 64 (copies up to 16 bytes off count); stars: a copier whose copy also copies. <b>Bottom:</b> soups with real replicators by 16,000 rounds under the strict criterion (rules not shown were not run). The number of copiers is the same on both sides of the band's right edge; whether a copy can copy is not.</figcaption>
</figure>

- **What this means for the research question:** within this family of rules, whether replicators arise quickly is predicted by one property that can be computed from the rule in seconds, before any soup is run: **does the rule's simplest copier make a copy that works?** How many copiers a rule has does not predict it. This is a "which rules make it likely" answer, though still for one narrow family of variations of one language.
- **What it cost to get here:** two hypotheses that failed their pre-registered tests (E-61's lineage reading, E-62's lineages) and one criterion that had to be fixed. All are in the journal (J-061 to J-064).

## 18 · Monday early: the predictor works in a second family of rules

A predictor found and tested in one family of rules could be a quirk of that family. So we moved **both** pointers: pointer 1 starts at byte g and pointer 2 at byte h, which gives 16,256 new versions of the rule, with copy geometries we had never looked at. Before running any soup, we wrote down the test (E-64, pre-registered): take 256 versions at random, compute for each whether its simplest copier makes a copy that copies again (class **F**), and predict that F versions make replicators quickly while versions that have short copiers but none like that (class **C**) do not.

- **The census (11 minutes):** of 256 versions, **3 are F**, 33 are C, and 220 have no short copier at all.
- **The soups:** 4 soups of 16,384 programs in each of the 3 F versions and in 4 C versions drawn at random, with the same strict jump test as section 17. **F: 10 of 12 soups made replicators** (4/4, 4/4, 2/4), mostly within 5,000 rounds. **C: 1 of 16** (at round 13,250). p = 5 × 10⁻⁵. **The prediction held.**
- **As predicted,** every self-sufficient short copier in the F versions copies forwards, and the replicators that took over were exact forward copiers. The single C soup that jumped did it differently: with backward copiers whose copies land 1–4 bytes off, a kind our short-copier census does not count.
- **A caution:** the F side rests on only 3 versions (F versions are rare: about 1 in 85). The slowest of them (2 of 4 soups) has the fewest self-sufficient copiers, which hints that the predictor could be graded rather than yes/no. Both points were tested next.

<figure>
<img src="{{ '/assets/report/e64-twoheads.png' | relative_url }}" alt="Left: scatter of 256 random rule versions by the start bytes of pointer 1 (g) and pointer 2 (h): 220 grey dots with no short copier, 33 blue dots with short copiers none of which makes a working copy, 3 green stars (g 2 h 64, g 60 h 126, g 67 h 127) with one that does. Right: bar chart of soups with real replicators by 16,000 rounds: 4 of 4, 4 of 4 and 2 of 4 in the three green versions; 0 of 4, 0 of 4, 0 of 4 and 1 of 4 in four blue versions.">
<figcaption><b>Left:</b> 256 versions of the rule drawn at random, classified in 11 minutes from the rule alone. <b>Right:</b> what their soups did (pre-registered test): the versions predicted to be fast (green) made replicators in 10 of 12 soups, the others (blue) in 1 of 16.</figcaption>
</figure>

- **A second test with every fast-looking version, not just 3 (E-65, pre-registered).** We classified **768 more** versions and ran soups in **all 7** F versions found, plus 4 C versions. **F: 26 of 28 soups** made replicators, and **every** F version did so in at least 3 of its 4 soups; **C: 1 of 16** (p = 9 × 10⁻⁹). Across the 1,024 versions: F 36 of 40 soups, C 2 of 32.
- **A graded version did not hold up.** We also guessed that versions with *more* short self-copying copiers would be faster. The trend went that way but was not significant (7 versions, p = 0.12): one F version with a single such copier made replicators in 3 of 4 soups, another with 80 was among the slowest. What matters is whether the rule allows one at all.
- **What the fast versions have in common (noticed afterwards, not tested):** in all 10, the two pointers start about **half a tape apart**, each within a few bytes of the start of a half (for example g = 64, h = 0, or g = 126, h = 63). A short loop can then copy one half onto the other. Many other versions with the same spacing but pointers in the middle of a half have no such copier.

<figure>
<img src="{{ '/assets/report/e65-twoheads.png' | relative_url }}" alt="Left: scatter of 1,024 random rule versions by start bytes g and h: 863 grey (no short copier), 151 blue (short copiers, none whose copy copies), 10 green stars, all at pointer positions half a tape apart near byte 0, 64 or 126. Right: for the 7 E-65 F versions, median jump round against the number of self-sufficient short copiers on a log scale: five versions jumped in 4 of 4 soups with medians under 2,000 rounds, two in 3 of 4 with medians 5,250 and 8,750; four C versions at the top, 1 of 16 soups.">
<figcaption><b>Left:</b> all 1,024 versions classified in E-64 and E-65; the 10 fast-looking ones (green stars) sit where the two pointers start at matching places in the two halves of the tape. <b>Right:</b> E-65 soups. Every F version made replicators (green: 3 or 4 of 4 soups); C versions did not (blue, top left). How many self-copying copiers a version has does not clearly predict how soon.</figcaption>
</figure>

- **What this means for the research question:** "does the simplest copier make a copy that works?" is the first property in this project that predicted, before anything was run, which universes make self-copying structure quickly, and it has now done so in **two** families of rules, three times with pre-registered tests. Both families vary only where pointers start in one programming language, so the next test should change the language itself (its instructions or tape length).

## 19 · Monday early: seven soups, 20,000 rounds after the jump, and still no sign of adaptation

The level-5 question (does evolution keep improving things?) had so far been asked of only 3 soups over 10,000 rounds, and the answer was "not reliably" (section 13). On Sunday afternoon we started a much bigger test (E-54, pre-registered): 12 new soups of 65,536 programs, plus 3 that had already jumped, each run for **20,000 rounds after its jump** (about 14 hours on 11 cores, interrupted once by the laptop's battery running out). From each soup we took 6 replicators from just after the jump and 6 from 16,000 rounds later, and measured how well each one invades a sample of the soup in which it has no close relatives (the kin-free invasion assay from section 13).

- **4 of the 12 new soups jumped** within 24,000 rounds (section 14 predicted about half), giving 7 jumped soups in all.
- **Later replicators are not fitter.** The difference, summed over soups, is slightly negative (D = −0.15, p = 0.64), and also in the soup's future (D = −0.50, p = 0.95). We had predicted no significant advantage, giving a real one a 30% chance.
- ~~**Soups stay mixed.**~~ **Corrected in section 20:** we reported that only **22–78%** of the 40 most common programs are verified replicators. Repeating the test 10 times shows that **99.8%** copy themselves; a single test misses about a fifth of them by chance.

<figure>
<img src="{{ '/assets/report/e54-long-soups.png' | relative_url }}" alt="Left: dot plot per soup (5301, 5302, 5308, 5401, 5402, 5406, 5410) of invasion scores of 6 replicators from 2,000 rounds after the jump (blue) and 6 from 18,000 rounds after (orange); the means are close in 6 soups, and in soup 5401 the later ones are clearly worse. Right: line chart, for each of the 7 soups, of the percentage of the 40 most common programs that are verified replicators, every 2,000 rounds from 2,000 to 20,000 rounds after the jump; values wander between 22% and 78% with no trend.">
<figcaption><b>Left:</b> how well replicators from early (blue) and late (orange) after the jump invade a sample of their soup taken in between (bars: means; 0 = holds its ground). No consistent advantage for later code. <b>Right:</b> the share of the soup's most common programs that passed a <i>single</i> replicator test; section 20 shows that this mostly measures the test's luck (with 10 repeats, nearly all copy themselves).</figcaption>
</figure>

- **What this means for the research question:** in this language, replicators arise on their own (level 3) and pass their mutations on (level 4), but over 20,000 rounds we see their code drift rather than improve. That is a firm negative at these scales, not a proof that it never happens: smaller advantages than our instrument can see, or much longer times, remain open.

## 20 · Monday morning: looking for parasites, and finding a flaw in our own test

Section 19 left a puzzle: if a fifth of a soup's most common programs cannot copy themselves, why are they common? In nature and in older digital-life systems (Tierra), the usual answer is **parasites**: code that gets copied by someone else's copying machinery. We built a detector for that (D-048): a program is a parasite if, paired with programs from its own soup, it ends up copied, more than scrambled versions of itself, mostly from its own template rather than made from scratch, and yet it never copies itself. It passed its checks: a parasite we wrote by hand for our hand-written replicator is found; inert and random programs are not; a rule that copies everything and a "product" made by many different makers are not mistaken for parasites; and the common programs of a soup before any replicator appears give none.

Then a pilot showed a bigger problem. **The same program passed our replicator test with one random seed and failed it with another.** The test starts from 8 copies, and often all 8 are lost by chance before they spread. So we pre-registered E-66: repeat the test 10 times on all 2,800 programs of section 19, then look for parasites only among programs that never copied.

- **99.8% of the common programs copy themselves** (2,795 of 2,800), including **597 of the 602** that the single test had called non-replicators. Over all 28,000 repeats, the mix of verdicts (52% "replicator", 27% "one generation", 22% "no replication") is almost exactly the single-test mix: the differences between programs were mostly **luck**. A typical program's copies grow in about 4 tests out of 5.
- Programs from soups before the jump never grew (0 of 80, 800 tests): the repeats do not invent copiers.
- **Only 5 true non-copiers** remained, all in one soup. The detector first called 2 of them parasites. Looking at them showed it was wrong: each **copies itself into any partner**, even one whose code never runs, but is destroyed whenever it runs second, so on its own its numbers shrink. It is a copier that survives only among partners that spare it. The detector now checks for this, and the soup program is one of its controls. Corrected count: **0 parasites**, 2 such copiers, 3 programs that nobody copies.

<figure>
<img src="{{ '/assets/report/e66-parasites.png' | relative_url }}" alt="Left: stacked bar chart of 2,800 programs by how many of 10 repeated tests their copies grew in; most grew in 6 to 10, whatever the first single test said (green replicator, blue one generation, orange no replication); only 5 never grew. Middle: per soup, the share of the 40 most common programs called replicators by one test (grey, 35 to 60%) against those that grew in any of 10 tests (green, 99 to 100%). Right: of the 5 programs that never grew, the first version of the parasite test called 2 parasites and 3 not copied; with the self-copy check, 0 parasites, 2 copiers that die when they run second, 3 not copied.">
<figcaption><b>Left:</b> how often each of the 2,800 programs copied itself in 10 more tests, coloured by what the single test had said: the colours are mixed in every bar. <b>Middle:</b> per soup, the share of common programs that copy themselves, one test (grey) vs ten (green). <b>Right:</b> the 5 programs that never did; the parasite test's first verdicts (grey) and after the fix (orange).</figcaption>
</figure>

- **Further down the ranking, still none (E-67, pre-registered).** We drew 420 rarer programs from the 7 soups' final states: 20 per soup with 6–40 copies, 20 with 2–5, and 20 that occur once. **0 parasites.** 99% of the moderately common ones and 96% of the rare ones copy themselves; among programs seen only once, 69% do. The rest are unrelated to the soup's main code (they differ from it in ~60 of 64 bytes): newly arisen programs that nothing copies, or that copy themselves but cannot hold their ground.
- **What this means:** after the jump, a soup is a population of self-copiers, with no parasites at any abundance we sampled. In Tierra, parasites were the first step towards an ecology; in this language at this scale, that step does not happen. We suspect the reason is mechanical: here a replicator copies a fixed window of the tape whatever is in it, so another program can only get copied by running first and handing control over, as our hand-made parasite does. It does change one sentence of section 19 (corrected there), and it is a lesson we keep relearning: a test with chance in it, run once per item, measures the chance as much as the item.

## 21 · Monday afternoon: change the language itself, and the map holds but the pace does not

Sections 17–18 found a rule property that predicts fast replicators, but every test kept programs at **64 bytes**. This time we changed the language itself: programs of **16, 32, 64 or 128 bytes** (the tape is two programs), and pointer 2 starting at any byte of the tape: 480 versions in all (E-68, pre-registered).

- **The map carries over exactly.** At every length, the versions where the simplest copier makes a copy that works (F) are those where pointer 2 starts **half a tape away**, at about byte L: bytes 14–17 for 16-byte programs, 30–34, 61–68 and 125–136 for the others. The same few short copying loops do it at every length. At 64 bytes the census reproduces our earlier one rule by rule, which checks the new code.
- **But the soups did not follow the map.** We predicted that F versions would make replicators in at least 3 of 4 soups. Overall it was **18 of 36** (other versions 6 of 36), so **the prediction failed**. With **16-byte programs nothing happened** in any version: 24 soups, 16,000 rounds each, not one copier among the common programs. With 32 bytes, half the F soups jumped. With 128 bytes **every** F soup jumped within 250–500 rounds, and so did 5 of 12 soups in versions the census calls slow (they used longer or slightly misaligned copiers that the census does not count).
- **Longer programs, faster replicators** (ρ = −0.90 between length and jump time). One explanation is that our soups had the same *number* of programs, so a soup of 128-byte programs holds 8× more code than a soup of 16-byte programs, and section 14 showed that bigger soups jump sooner. E-69 tested this directly (next bullet).

<figure>
<img src="{{ '/assets/report/e68-tapelength.png' | relative_url }}" alt="Left: for each program length (16, 32, 64, 128 bytes), every possible start byte of pointer 2 as a dot along a line from 0 to two program lengths; green stars (fast-looking F versions: 4, 5, 8 and 12) cluster around one program length, i.e. half a tape away; blue dots (short copiers, none whose copy copies) sit near the ends and next to the stars; grey dots have no short copier. Right: bar chart of soups that made replicators, with the same number of programs (solid) and the same number of bytes (hatched): L 16: F 0 of 12 and 4 of 12, other 0 of 12 and 0 of 12; L 32: F 6 of 12 and 10 of 12, other 1 of 12 and 0 of 12; L 64: F 4 of 4 (others not run here); L 128: F 12 of 12, other 5 of 12.">
<figcaption><b>Left:</b> every version of the rule at four program lengths; the fast-looking versions (green stars) always sit where pointer 2 starts half a tape away. <b>Right:</b> what their soups did. Solid bars: every soup had 16,384 programs (E-68); at 16 bytes nothing happened, and at 128 bytes even other versions often made replicators. Hatched bars: the same versions with as many bytes as the 128-byte soups (E-69); short programs catch up partly.</figcaption>
</figure>

<figure>
<img src="{{ '/assets/report/e68-soups.png' | relative_url }}" alt="Four panels of 48 programs each, one row per program and one cell per byte, instructions coloured and other bytes light grey. 16-byte programs at the start: a few scattered instructions. After 2,000 rounds: many orange copy instructions and green pointer moves, scattered differently in every row. 128-byte programs at the start: scattered instructions. After 2,000 rounds: the same pattern of instructions repeats in almost every row, forming vertical columns: one family of code has copied itself across the soup.">
<figcaption>Inside two soups of the same kind of rule (pointers half a tape apart), 48 programs each, one row per program. <b>16-byte programs</b> (left pair) fill up with copy instructions (orange), yet the rows stay different from each other: no program copies itself. <b>128-byte programs</b> (right pair): by round 2,000 nearly every row is the same code (the vertical stripes), because one self-copier has spread through the soup.</figcaption>
</figure>

- **Same amount of code, partly the same result (E-69, pre-registered).** We reran the 16- and 32-byte versions with as many bytes per soup as the 128-byte soups had (8× and 4× more programs). The F versions now made replicators in **4 of 12** soups at 16 bytes (before: 0) and **10 of 12** at 32 bytes (before: 6), and the other versions in **0 of 24**. So the amount of code explains much of the length effect, and once it is matched the map separates fast from slow versions cleanly (14 of 24 vs 0 of 24). But not all: with the same bytes, short programs still succeed less often (4/12 at 16 bytes, 10/12 at 32, 12/12 at 128). Our pre-registered test could not decide between the two explanations (4/12 fell between its thresholds).
- **What this means for the research question:** the rule property that predicts *which* universes can make self-copying code quickly has now held across three changes (start positions of one pointer, of both, and program length), all with pre-registered tests. *How soon* it happens also depends on how much raw material the soup has, and somewhat on how long each program is. The next change to try is the instruction set itself.

## 22 · Monday night: change what an instruction does, and the map still holds

Sections 17–21 changed where the pointers start and how long programs are, but the language's instructions always did the same thing. This time we changed **what one instruction does**, five different ways (E-70, pre-registered): the copy instruction `.` also moves both pointers forward (1) or backward (2) after copying; the other copy instruction `,` moves both forward (3); loops test pointer 2's byte instead of pointer 1's (4); add and subtract act on pointer 2's byte (5). Each of these was crossed with all 128 start positions of pointer 2: 640 new versions of the language.

- **The map holds again.** In every one of the five languages, the versions where the simplest copier makes a working copy of itself (F) are exactly those where pointer 2 starts **half a tape away** (bytes 60–68), and every such copier copies forwards, as in standard BFF (bytes 61–68). The languages differ in *how many* such copiers they allow: when the copy instruction moves the pointers itself, a three-instruction loop `[.]` is already a complete copier, and the census counts **3,893** self-sufficient short copiers at byte 64, against 137 in standard BFF. The census of standard BFF reproduces our earlier one rule by rule, which checks the new code. Pre-registered prediction 1: **passed**.
- **The soups followed the map.** In each language we ran soups in 3 F versions and 3 others, 4 soups each (16,384 programs, up to 16,000 rounds). **All 60 F soups made replicators**, most within 250–750 rounds; the other versions made them in **15 of 60**, and later (median 3,000 rounds). Pre-registered prediction 2 (F ≥ 75%, others ≤ 25%, p < 0.01, F ahead in every language): **passed**, p = 2 × 10⁻²⁰, though the others sat exactly at the 25% limit. Most of those 15 came from versions right next to the band (pointer 2 at byte 59 or 60, one step outside it: 8 of 8 soups), the other 7 from four versions elsewhere (bytes 7, 83, 123, 125), where the census sees short copiers but none whose copy copies.
- **More copiers, sooner (exploratory).** Across the 15 F versions, the more self-sufficient short copiers a version allows, the sooner its soups jump (ρ = −0.80, p = 0.0004): language 1 at byte 64, with 3,893 of them, jumped at round 250 in all 4 soups; language 5 at byte 67, with 51, took 1,500–3,500. In a single family (section 18) this link was not significant; here the counts span two orders of magnitude. It was not pre-registered as a test, so it needs confirming.
- **What this means for the research question:** a property computed from a universe's rules in seconds (does its simplest copier make a copy that copies?) has now predicted which universes make self-copying code quickly across **four** different kinds of change: where each pointer starts, how long programs are, and now what the instructions do. Every such universe so far has its two pointers half a tape apart. It does not yet say anything about what happens *after* the replicators appear (no sign of adaptation so far, section 19), and all of these universes are variants of one small language.

<figure>
<img src="{{ '/assets/report/e70-instrset.png' | relative_url }}" alt="Left: six rows, one per language (standard BFF and the five variants), each showing all 128 start bytes of pointer 2 as dots from 0 to 127; green stars (F versions: 8, 9, 5, 8, 7 and 8 of them) cluster around byte 64 in every row; blue dots (short copiers, none whose copy copies) sit near both ends and beside the stars; grey dots have no short copier. Right: bar chart per variant, F versions 12 of 12 soups made replicators in all five; other versions 1, 3, 3, 4 and 4 of 12.">
<figcaption><b>Left:</b> every version of each language; the versions predicted to be fast (green stars) always sit where pointer 2 starts half a tape away (byte 64), whatever the instructions do. <b>Right:</b> what their soups did, 4 soups per version.</figcaption>
</figure>

<figure>
<img src="{{ '/assets/report/e70-soups.png' | relative_url }}" alt="Four panels of 48 programs each, one row per program and one cell per byte, instructions coloured and other bytes light grey. Language 1 (copy then move forward), pointer 2 at byte 64: at the start, scattered instructions; after 500 rounds, the same few instructions sit in the same columns in nearly every row, a block of copy instructions at the left. Pointer 2 at byte 69: at the start, scattered instructions; after 500 rounds, every row is dense with copy and add instructions, but no two rows look alike.">
<figcaption>Inside two soups of language 1 (the copy instruction moves both pointers forward), 48 programs each, one row per program. <b>Pointer 2 at byte 64</b> (left pair, an F version): by round 500 nearly every row is the same code (vertical stripes): one self-copier has spread. <b>Pointer 2 at byte 69</b> (right pair, not F): the soup fills up with copy (orange) and add (red) instructions, yet every row is different; nothing copies itself whole, and in 16,000 rounds none of its 4 soups made a replicator.</figcaption>
</figure>

## 23 · Tuesday morning: more copiers, sooner? Within a language, yes; across languages, unclear

Section 22 ended with an exploratory link: versions of the language that allow more short self-copiers made replicators sooner (ρ = −0.80). But it pooled five languages, and one of them (the copy instruction moves the pointers itself) allows thousands of such copiers and is fast everywhere. So the link could just be "language 1 is fast". E-71 (pre-registered) tested it on the **22 predicted-fast versions that section 22 had not run soups in**, 8 soups each, timing each jump to within 50 rounds.

- **Across languages: failed as registered, but not robust.** Over the 22 versions, the correlation between the number of self-sufficient short copiers and the median jump time was ρ = −0.34 (p = 0.06). We had required ρ ≤ −0.4 and p < 0.01. *Correction (section 24):* timing the jumps another way (by HOE) gives ρ = −0.57, p = 0.003, which would have passed. So across languages the answer is "not shown either way".
- **Within each language: passed.** Compared only with versions of the same language, more copiers went with sooner jumps in all four languages that had at least 3 versions (ρ = −0.55, −0.60, −0.80, −0.50). Summed and tested against shuffles within each language, p = 0.006. So the count is a graded predictor *within* a language. This holds under both ways of timing jumps (section 24). Whether counts from different languages compare is open.
- **What does compare (exploratory):** the total number of copiers says nothing (ρ = 0.01). The *share* of copiers whose copy copies again does better, across languages too (ρ = −0.48, p = 0.01). This is a lead to test, not a result.
- **One predicted-fast version failed outright.** In language 1 with pointer 2 at byte 68, at the edge of the band, none of 8 soups made replicators in 16,000 rounds. Only 18 of its 4,317 short copiers pass the census test. Its neighbour at byte 67 (1,525 pass) was slow too (3 of 8 soups never jumped), while byte 60, with a single one, was fast. The census checks one generation of copying (does the copy copy?). Our guess, untested, is that at these offsets copies drift a little each generation and lose their place.
- Otherwise the property held well: **165 of 176** soups in predicted-fast versions made replicators.

<figure>
<img src="{{ '/assets/report/e71-copiercount.png' | relative_url }}" alt="Five panels, one per language variant. Each shows predicted-fast versions as points: horizontal axis the number of self-sufficient short copiers (log scale, 1 to several thousand), vertical axis the median round at which soups made replicators (log scale, 50 to 16,000). Filled green points are the 22 new versions, hollow grey points the 15 from section 22. Within each panel the points tend to fall from left to right. In the first panel (copy then move forward), byte 68 sits at the top (no jump) with 18 copiers and byte 67 near 7,000 rounds with 1,525, while bytes 63 and 65 jump at 50-75 rounds and byte 60 (1 copier) at 200.">
<figcaption>Each point is one predicted-fast version of a language: how many short self-copiers its census counts (horizontal) against how soon its soups made replicators (vertical; the dotted line means no replicator in 16,000 rounds). Filled: the 22 new versions of E-71, 8 soups each. Hollow: section 22's versions (4 soups, coarser timing). Within a panel, more copiers tends to mean sooner. Between panels the counts sit on different scales.</figcaption>
</figure>

## 24 · Tuesday evening: copies of copies, and replicators our detector could not see

The census asks whether a short copier's copy copies again: one generation. In language 1, versions with pointer 2 at bytes 67 and 68 pass that test but were slow or made nothing (section 23). E-72 follows **lineages of copies for five generations**: copy the kernel into a random partner, check that the copy copies, copy that copy, and so on. A kernel counts as *deep* if at least 4 of its 8 lineages still copy at generation 5.

- **After the fact, it explains the slow cases.** In versions 67 and 68, every copy of a copy stops copying: no deep kernel. In version 64, 89% of kernels are deep. Across the 37 versions with soups, the number of deep kernels tracked speed better than the one-generation count (ρ = −0.66 against −0.44). But those soups were already known.
- **On fresh universes, it failed.** We drew 240 versions never run before (the five languages, with pointer 1 also moved), found 27 predicted fast, and ran 6 soups in each of 8 *deep* and 8 *shallow* ones. Pre-registered prediction: shallow ones are at least 3× slower. They were not: median 1,675 rounds against 1,475 (p = 0.58). The plain one-generation count did better (ρ = −0.74).
- **Two "empty" universes were full of replicators.** Two deep versions scored 0 of 6 soups. Yet their soups became highly ordered within 500 rounds (HOE 6.4, higher than any jump we had seen) and nearly every pair of programs ran to the step limit. We re-ran one soup and looked. The most common programs are short loops that copy **59 or 60 of their 64 bytes**. They are sloppy replicators, and our detector requires 60 matching bytes. The pre-registered jump detector had missed them.
- **Timing jumps another way does not settle it.** With an HOE threshold instead (post hoc), deep versions take 188 rounds and shallow ones 1,500, the predicted direction, but p = 0.04, short of the bar. The HOE threshold has the opposite blind spot: in language 3 it misses take-overs the copier detector sees.
- **Update (section 25):** with a validated looser detector, the two "empty" versions jump at round 50, and the deep/shallow difference becomes tenfold (p = 0.06). The verdict stays "fail" by the pre-registered bar, but the speed question is now unresolved rather than negative.
- **What changes:** results about *whether* soups make replicators are less exposed than results about *how fast*. From now on we time jumps both ways and accept a speed result only if both agree (D-052). Before testing speed predictors again, the copy-fidelity threshold needs its own validation, with sloppy-copier controls.

## 25 · Wednesday: a better replicator detector, and re-scoring three experiments

Section 24 showed that our detector misses replicators that copy 59 of 64 bytes. Lowering the threshold is not safe on its own. A program can make its partner look like itself without copying any instructions, for example by writing one value over and over into a partner that is mostly that value already. So the new test (D-053) asks for **58 of 64** matching bytes **and** that the copy reproduces at least 75% of the program's actual instructions.

- **Checked first, against known cases** (pre-registered, E-73). Sloppy replicators: 38 and 40 of 40 detected, against 0 and 0 for the old test. Exact replicators: as before. The most common programs of soups without replicators: none. 64 decoys built to fool the test ("filler smears"): none accepted. **The old test accepted 37 of them**, so it had a false-positive weakness too. One check was changed after seeing it: a random program turned out to contain a genuine 3-instruction copier, so "0 of 200 random programs" became "at most 1%".
- **Then every soup of sections 22–24 was replayed from its seed** (392 soups, 8½ hours) and scored with both tests. The old test reproduced every stored result exactly. With the new one, 33 soups change: 12 that "never" jumped jump at round 50 (the two sloppy versions of section 24), and 21 jump earlier. **None loses its jump**, so no earlier result rested on a decoy.
- **Whether soups make replicators: unchanged.** Section 22's 60 of 60 vs 15 of 60 stands exactly. We had predicted it would fail, because hidden sloppy take-overs among the other 60 soups would push them over 25%. There were none: that prediction was wrong.
- **More copiers, sooner (section 23): unchanged.** Within a language version: yes (p = 0.011). Across versions: still unresolved (fails under this test, passes under the HOE timing).
- **Copies of copies (section 24): the effect reappears.** Deep versions now take a median **163 rounds**, shallow ones **1,638**: ten times slower, in the predicted direction (it was 1,475 vs 1,675). With 8 versions per group, p = 0.06, short of the pre-registered p < 0.01, so the verdict stays "fail". Because the old and new tests disagree about the size of the effect, we report the result as **unresolved, leaning towards a real effect**. A larger, fresh test is needed.
- **Lesson:** a detector threshold that works in one language can decide speed results in another. Before trusting a "nothing happened", validate the detector on that language.

## Where this leaves the project

| Evidence level | Life-like rules (v0.1–v0.4) | Lenia (tonight) | Program soups (BFF) |
|---|---|---|---|
| 1 · persistent organisation | yes | yes | after a transition: one family of code persists for thousands of rounds |
| 2 · self-propelled structures | yes | **yes, arising spontaneously from correlated starts** (gliders; a turning "wanderer"; a straight "ring glider"); from Chan's sparse patches in big worlds too | not applicable (no space) |
| 3 · self-replication | not observed | **yes, in one multi-channel rule (E-32): dividing spots of a single type**, like Gray-Scott; none in 3000 random single-channel rules from a lone lump (E-29), none in fed Flow-Lenia (E-30, after removing a false alarm; E-31 held out); no births in big worlds (E-15), in 500 glider collisions (E-20) or 200 wanderer encounters (E-22); gliders can *fuse* into a larger mover, wanderers absorb each other. A validated birth detector finds no reproducer in 568 worlds (E-27, E-28) | **yes, emergent from random code** in 3 of 16 soups of 16,384 programs (E-40, E-41) and in 4 of 34 more of other sizes (E-50), every real jump verified by the replicator detector; none in soups without one. **Bigger soups jump sooner, rate ∝ size** (E-50). **How soon depends on one detail of the rule:** only rule versions whose shortest copier also makes a working copy of itself produce replicators within a few thousand rounds: 32 of 32 soups inside that band, 1 of 16 just outside (E-55–E-63); the same property predicted fast rules in a second family (36 of 40 vs 2 of 32, E-64, E-65) and in five instruction-set variants (60 of 60 vs 15 of 60, E-70) |
| 4 · heredity and variation | not measured | a validated heredity test exists (J-033); the only Lenia reproducer has one attractor type, so nothing can be inherited | **yes: in 9 of 9 emergent replicators, one-byte mutations are carried by their descendants** (E-42); one emergent species out-competes the others in controlled races (E-45, E-46); nearly every common program after the jump copies itself, and no parasites were found at any abundance (E-66, E-67) |
| 5 · open-ended evolution | not observed (knockouts ≈ placebo) | not tested | **not shown**: after the jump the code keeps changing far from its founder, but later replicators are not reliably fitter than earlier ones, by races (E-48, E-49), a calibrated growth rate (E-51) or invasion of kin-free soups (E-53), including 7 soups 20,000 rounds after their jump (E-54); an apparent advantage in their own soups was kinship (E-52) |

**Mistakes we caught and recorded:** two wrong predictions about Chan's start and world size (J-029); a cut-off whose safety margin did not survive new rules (J-028); an over-inclusive mover check in a new script (J-025); the inflated label (J-012); a pre-registered test that could not reach its own threshold (J-014); a glider speed documented 5× too low, because measuring across more than half the world wraps around (J-012); a quick glider counter whose "births" were artefacts (J-017).

## What next

1. **Map the ring glider's neighbourhood** in rule space, as E-18b did for the wanderer, and test whether patch starts work in the wanderer and ring-glider rules too.
1. **Interactions as a route to new structure:** gliders can fuse into double gliders (E-20), but the chain stops there (E-23); wanderers absorb each other (E-22). Other rules or physics (multi-channel Lenia) may allow deeper combination. A knockout test on fusion events (J-010 style) would show whether later structures depend on earlier ones.
2. ~~A better detector for slow, turning movers~~ done (E-25, D-027; ~95% detected). Remaining: wanderers that circle tightly. Also **fix the quasi-static margin** (C-02), e.g. a margin that scales with the kernel radius, with its own controls.
3. **Rates vs world size and run length**, measured with the validated detector at checkpoints (E-15 used a quick counter for its time series).
4. ~~Chan's patch protocol in larger worlds~~ done (E-24: 8% of 256² worlds). Next: separate world size from run length, and test the "isolated lump" mechanism directly.
5. ~~A replication detector for continuous physics~~ done (D-028, E-27/E-28: none found).
6. **Flow-Lenia:** find a positive control (several channels; check our implementation against the paper's figures), then run the same validated pipeline: does mass conservation make movers and evolution more common, as its authors claim?
7. **Heredity (Track D):** ~~a heredity measure~~, ~~Flow-Lenia with travelling parameters and food~~ (J-033, E-30, E-31: no reproducers), ~~multi-channel Lenia~~ (E-32: one rule of dividing spots, a single type). Next: search multi-channel rule space *around* the dividing rule for rules with **several** distinct reproducing types (the minimum for heredity), and test what the empty-channel decay term does across rules. 

8. **Program soups, the most promising lead (section 12):** self-copying programs now appear on their own. Next: (a) ~~a heredity test for programs~~ done (E-42: heredity in 9/9); ~~one-byte variants in competition~~ (E-43: mostly neutral); ~~contests between soups~~ (E-44, E-46: mostly equal; one species wins, E-45/E-46); ~~track species over time~~ (E-47: no species dominates; the soups drift far from their founders); ~~is the drift adaptive?~~ (E-48, E-49: at most slightly; not confirmed); ~~a more sensitive fitness measure~~ (D-044 growth rate and an invasion assay, both calibrated; E-51–E-53: later code not reliably fitter). (b) ~~rates vs soup size~~ (E-50: rate ∝ size). (c) ~~many more jumped soups, run long after the jump~~ (E-54: 7 soups, 20,000 rounds, later code not fitter). ~~parasites~~ (E-66, E-67: a validated detector finds none among common or rarer programs; 99.8% of common programs copy themselves). (d) ~~why do all emergent replicators copy backwards?~~ ~~which rule versions make replicators fast?~~ (E-60–E-63: those whose simplest copier makes a copy that works; a sharp boundary). ~~test that predictor in another family~~ (E-64, E-65: both pointers moved, 36/40 vs 2/32; the count of copiers does not clearly matter). ~~a family that changes the tape length~~ (E-68: the map of fast rules carries over, but short programs make no replicators; E-69: matching the amount of code explains much of that). ~~a family that changes the instruction set~~ (E-70: five variants, F 60/60 vs other 15/60; more short self-copiers, faster). ~~confirm the copier-count link to speed~~ (E-71: within a language yes, across languages no; one predicted-fast version failed). ~~a census test over several generations~~ (E-72: explains old cases, fails on new ones; our detector misses sloppy copiers). ~~validate a copy-fidelity threshold and re-score E-70–E-72~~ (E-73: no verdict flips; the five-generation effect reappears, 10×, p = 0.06). Next: a larger fresh test of the five-generation predictor under both timings; then a language outside the BFF family; (E-55: the rule makes backwards copiers the simplest; a counterfactual rule flips it; E-56/E-57: under it replicators arise 10–100× sooner). Next: (e) measure the link between the size of the smallest replicator and the waiting time directly, e.g. in rules that need 6, 7, 8 instructions; (f) do counterfactual soups, with many more jumps per hour, show cumulative change after the jump (the level-5 question, with the kin-free invasion assay)?

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
| 01:55 | E-40: 0 of 12 program soups transition; E-41 (replay of the pilot that did, longer runs) starts |
| 02:30 | The replayed pilot transitions at the same round; the detector confirms emergent replicators |
| 03:20 | E-41: run 3× longer, 2 of the 12 soups transition, both full of verified replicators |
| 03:40–04:10 | Heredity test for programs (D-041) and its controls; E-42: mutations inherited in 9 of 9 replicators |
| 04:30 | E-43: head-to-head races between variants: mostly neutral; selection not shown |
| 04:40–04:48 | E-44: races between replicators from different soups: no clear winners; a mirror replicator found (the hand-written copier seemed to win: mostly a counting error, see E-46) |
| 04:48–04:52 | E-45 (pre-registered): the 5006 species wins 70% of races against another soup's replicators; one neutral control misbehaves |
| 04:53 | All 9 emergent replicators turn out to copy backwards: earlier counts were unfair; E-46 pre-registered to redo them |
| 04:55–05:12 | E-46: with fair counting the advantage holds (70%), and the winner beats an earlier family of its own soup; controls fine |
| 05:13–05:48 | E-47: exact replays of the three soups to 40,000 rounds; no species dominates (0 replacements, prediction wrong); the most common code drifts far from the founder |
| 05:49–05:57 | E-48: later vs earlier code: fitter in soup 5006, not overall (p = 0.07); two non-copying programs spoil soup 901's sample |
| 05:59–06:13 | E-49 (pre-registered confirmation, verified replicators, new time points): later code not reliably fitter (51.6% of races) |
| 06:15–10:37 | Session ends; you reviewed the open pull requests |
| 10:37 | A scheduled session resumes; E-50 (does soup size change how often the jump happens?) pre-registered and running |
| 10:45–11:04 | A calibrated growth-rate instrument (D-044): variants with built-in copying odds match theory; E-51: no general fitness trend, soup 5006 rises again |
| 11:16–11:47 | An invasion instrument, calibrated the same way; E-52: later code invades later soups better (p = 0.045)… then a kinship confound is found |
| 11:48–12:36 | E-53 (pre-registered, kin-free soups): no advantage, so E-52 was most likely kinship (one run lost to a seed bug and re-run) |
| 10:41–13:50 | E-50: 34 soups of three sizes; bigger soups jump sooner (rate ∝ size); three false "jumps" found and the criterion tightened (D-045) |

| 13:57–16:40 | E-54 (15 soups of 65,536 programs run 20,000 rounds past their jump) running |
| 16:40–17:00 | A scheduled session resumes; E-55: a census of 1.1 million short copiers explains the backwards copying |
| 16:45–17:40 | E-56: 4 soups under the changed rule all jump within 1,000 rounds, all forward copiers |
| 18:40–19:00 | A new scheduled session; E-57 (pre-registered): 8 of 8 smaller soups jump too; a backward copier is never a replicator by itself |
| 19:00–19:40 | E-58: a control rule with backward copiers is slow again (1 of 8); its jump threshold misfired in 4 soups, caught by replaying them (D-046) |
| 19:45–20:25 | E-59 (pre-registered confirmation, 24 fresh soups): 2 of 16 vs 8 of 8 |
| 20:25–21:10 | E-60: all 128 versions of the rule; only 4 allow a short self-sufficient copier, and only those make replicators quickly (12 of 12 vs 2 of 16) |
| 22:19 | The laptop's battery ran out; every run stopped. Resumed at 22:21 from saved snapshots (E-54) and from scratch (E-60b) |
| 22:25–22:50 | E-60b: the puzzling version-7 soup is full of copiers our test could not see (copies 6–8 bytes off) |
| 22:50–23:00 | E-61 (pre-registered): a shift-aware census widens the band to 61–68 |
| 23:05–23:27 | E-62 (pre-registered): lasting lines do not matter; all 28 soups in 61–68 make exact replicators. Both predictions failed |
| 23:28–23:42 | E-63 (pre-registered): just outside the band, 1 of 16 soups; inside, 32 of 32 |
| 23:48–00:42 | E-64 (pre-registered): a second family of rules (both pointers move); F versions 10 of 12 soups, C versions 1 of 16 |
| 01:21 | The last long soup of E-54 finished (resumed after the power loss) |
| 02:38–03:00 | E-54 analysis: 7 jumped soups, later replicators not fitter (p = 0.64) |
| 03:37–04:40 | E-65 (pre-registered): 768 more versions; all 7 predicted-fast versions make replicators (26 of 28 soups), others 1 of 16; the graded guess fails |
| 06:40–07:00 | A parasite detector with its controls; a pilot finds that our replicator test gives different answers for the same program |
| 07:00–09:45 | E-66 (pre-registered): 28,000 repeated tests (the first run crashed at the end and was rerun); 99.8% of common programs copy themselves; the detector's 2 "parasites" were copiers, caught by looking, detector fixed |
| 09:50–10:05 | E-67 (pre-registered): 420 rarer programs, 0 parasites |
| 12:38–14:40 | A scheduled session resumes; E-68 (pre-registered): 480 rule versions at four program lengths, then 76 soups; the map holds, the soup prediction fails (16-byte programs make nothing) |
| 14:45–18:05 | E-69 (pre-registered): the same rules with as much code per soup as the long programs; short programs catch up partly; verdict undecided |
| 20:38–23:35 | A scheduled session resumes; E-70 (pre-registered): five languages that change what one instruction does, 768 versions, then 120 soups; the map holds and predicts the soups (60 of 60 vs 15 of 60) |
| 09:35–12:10 (Tue) | On the owner's go-ahead, E-71 (pre-registered): 176 soups in 22 new predicted-fast versions; the copier count predicts speed within a language, not across languages; one predicted version makes nothing (the analysis crashed twice on saving and was rerun from the cache) |
| 12:15–18:20 (Tue) | E-72 (pre-registered): a five-generation version of the predictor; it explains the old slow cases but fails on 16 new universes; two soups scored empty turn out to hold sloppy replicators (59 of 64 bytes), so E-71's cross-language verdict is corrected |
| 09:00–19:00 (Wed) | On the owner's go-ahead, E-73 (pre-registered): a looser replicator test, validated against sloppy copiers, empty soups and decoys; then all 392 soups of E-70–E-72 replayed and re-scored; no verdict flips, but the five-generation speed effect reappears (10×, p = 0.06) |
Everything was done on branches, checked with `pytest` and the validation benchmark, and submitted by pull request (the newest are waiting for review before they appear here). The benchmark now has 148 checks (39 + 109), all passing.

## Read more

- Journal entries [J-012 to J-072]({{ '/journal.html' | relative_url }}) (full numbers, caveats, commits); independent review [R-4]({{ '/reviews.html#r-4' | relative_url }}); [Decisions]({{ '/decisions.html' | relative_url }}) D-022 to D-031, D-040 to D-051; [Experiments]({{ '/experiments.html' | relative_url }}) with exact commands and data.
- Pre-registrations: [E-13](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e13-preregistration.md), [E-14](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e14-preregistration.md), [E-17](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e17-preregistration.md), [E-18](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e18-preregistration.md), [E-19](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e19-preregistration.md), [E-20](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e20-preregistration.md), [E-21](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e21-preregistration.md), [E-22](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e22-preregistration.md), [E-23](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e23-preregistration.md), [E-24](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e24-preregistration.md), [E-25](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e25-preregistration.md), [E-26](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e26-preregistration.md), [E-27](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e27-preregistration.md), [E-28](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e28-preregistration.md), [E-29](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e29-preregistration.md), [E-30](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e30-preregistration.md), [E-31](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e31-preregistration.md), [E-32](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e32-preregistration.md), [E-40](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e40-preregistration.md), [E-41](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e41-preregistration.md), [E-42](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e42-preregistration.md), [E-43](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e43-preregistration.md), [E-44](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e44-preregistration.md), [E-45](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e45-preregistration.md), [E-46](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e46-preregistration.md), [E-47](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e47-preregistration.md), [E-48](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e48-preregistration.md), [E-49](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e49-preregistration.md), [E-50](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e50-preregistration.md), [E-51](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e51-preregistration.md), [E-52](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e52-preregistration.md), [E-53](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e53-preregistration.md), [E-54](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e54-preregistration.md), [E-55](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e55-preregistration.md), [E-56](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e56-preregistration.md), [E-57](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e57-preregistration.md), [E-58](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e58-preregistration.md), [E-59](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e59-preregistration.md), [E-60](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e60-preregistration.md), [E-61](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e61-preregistration.md), [E-62](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e62-preregistration.md), [E-63](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e63-preregistration.md), [E-64](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e64-preregistration.md), [E-65](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e65-preregistration.md), [E-66](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e66-preregistration.md), [E-67](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e67-preregistration.md), [E-68](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e68-preregistration.md), [E-69](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e69-preregistration.md), [E-70](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e70-preregistration.md), [E-71](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e71-preregistration.md), [E-72](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e72-preregistration.md), [E-73](https://github.com/Yahyaal/emergence-lab/blob/main/docs/data/e73-preregistration.md).
- Every figure is regenerated by `python scripts/make_report_figures.py`.

**Glossary.** *BFF*: a minimal programming language in which a program can read and write its own and its partner's bytes; *replicator*: a program whose copies multiply among random programs for two generations. *Lenia*: a cellular automaton with continuous cell values and smooth, ring-shaped neighbourhoods (Chan 2019). *Glider*: a pattern that keeps its shape and travels. *Soup*: a random start where each cell is independently filled. *Smooth start*: random noise blurred over ℓ cells. *Pre-registered*: the test and its threshold were written down and committed before the data existed. *Evidence level*: the project's ladder from persistent organisation (1) to open-ended evolution (5).
