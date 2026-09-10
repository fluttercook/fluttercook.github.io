---
title: "Flame: game loops inside Flutter"
description: "Component trees, game loops, and bridge packages — Flame’s place in a Flutter product."
seoDescription: "Flame engine Flutter architecture: component tree, game loop, bridge packages for audio bloc tiled rive."
keywords:
  - flame engine
  - flutter game development
  - flame component tree
  - flutter 2d game
  - flame architecture
tags: ["Flutter", "OpenSource", "Games"]
sources:
  - name: "Flame GitHub"
    url: "https://github.com/flame-engine/flame"
  - name: "Flame docs"
    url: "https://docs.flame-engine.org/"
related:
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
  - slug: "flutter-widget-previews-stable"
    title: "Widget Previews Stable"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎮"
draft: false
---

Flame is how Flutter does games without abandoning the widget tree for a different engine. A `GameWidget` hosts a component tree updated by a game loop; overlays keep HUD/chat in normal Flutter.

![Diagram: Flame Engine](/blog/images/oss-flame-engine.svg)



## Steal this

1. Hybrid UI: game canvas + Flutter overlays for menus/monetization.
2. Bridge packages (audio, physics, tiled, bloc) keep the core small.
3. Deterministic updates help tests and replays.

## Pitfalls

- Mixing `setState` UIs into the game loop fights the architecture.
- Mobile thermal budgets matter more than desktop FPS flexes.

Use Flame for 2D product mini-games and interactive canvases, not only toys.
