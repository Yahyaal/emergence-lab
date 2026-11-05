---
title: Gallery
description: Videos and time-lapse strips of notable universes and controls, each reproducible from its exact spec.
---

# Gallery

Each clip below is regenerated bit-for-bit by `python scripts/make_media.py` from the specs in
[`docs/_data/media.json`](https://github.com/Yahyaal/emergence-lab/blob/main/docs/_data/media.json).
Colours: dark = vacuum, light = alive, orange fading to brown = refractory ("dying") states in multi-state rules.
To watch any of them interactively, paste the rule into the dashboard's **Open** box, or run the spec with the engine.

<div class="media">
<video controls muted playsinline preload="none" poster="{{ '/assets/media/dashboard-demo-poster.png' | relative_url }}">
  <source src="{{ '/assets/media/dashboard-demo.mp4' | relative_url }}" type="video/mp4">
</video>
<p>Dashboard walkthrough: open a universe, add a second with Shift+click, sync and play both, zoom in, then open the Discoveries tab.</p>
</div>

<figure>
<img src="{{ '/assets/media/dashboard.png' | relative_url }}" alt="Dashboard: gallery of universes, a universe viewer, measurements, history charts and lineage">
<figcaption>The local dashboard (<code>emergence serve</code>) on the R3 experiment (universe #1181 open): sortable gallery, viewer with playback, rewind, zoom and comparison, measurements, history charts and lineage.</figcaption>
</figure>

{% for m in site.data.media.items %}
<div class="media" id="{{ m.id }}">
<h3>{{ m.title }}</h3>
<video controls loop muted playsinline preload="none" poster="{{ '/assets/media/' | append: m.id | append: '-poster.png' | relative_url }}">
  <source src="{{ '/assets/media/' | append: m.id | append: '.mp4' | relative_url }}" type="video/mp4">
</video>
<img class="strip" src="{{ '/assets/media/' | append: m.id | append: '.png' | relative_url }}" alt="Time-lapse of {{ m.title }} at five moments" loading="lazy">
<p>{{ m.caption }}</p>
<p class="spec">{% if m.kind == "universe" %}spec: rule {{ m.spec.physics.rule }}, seed {{ m.spec.seed }}, {{ m.spec.width }}×{{ m.spec.height }}, density {{ m.spec.density }}{% else %}planted pattern under {{ m.rule }} in an empty {{ m.side }}×{{ m.side }} world{% endif %} · {{ m.steps }} steps</p>
</div>
{% endfor %}
