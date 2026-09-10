---
title: "Spotube: a privacy-minded Flutter music client"
description: "Riverpod, drift, media_kit, and a multi-store release story — how Spotube ships music without a first-party backend."
seoDescription: "Spotube Flutter architecture: Riverpod state, drift database, media_kit audio, all-platform music client patterns."
keywords:
  - spotube flutter
  - spotube architecture
  - flutter music player open source
  - media_kit flutter
  - riverpod music app
tags: ["Flutter", "OpenSource", "Music", "Riverpod"]
sources:
  - name: "Spotube GitHub"
    url: "https://github.com/KRTirtho/spotube"
  - name: "media_kit"
    url: "https://github.com/media-kit/media-kit"
related:
  - slug: "oss-harmony-music"
    title: "Harmony Music"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎵"
draft: false
---

Spotube proves you can ship a polished music experience across mobile and desktop from one Flutter codebase — without owning the catalog backend.

![Diagram: Spotube Architecture](/blog/images/oss-spotube-architecture.svg)



## Stack signals

- **Riverpod** for state and DI.
- **drift** for durable local library data.
- **media_kit** (and related plugins) for playback across platforms.
- Store releases including F-Droid/Flathub — packaging is part of the product.

## What to steal

1. Separate *catalog search* from *local library* state.
2. Make playback a headless service with a thin UI shell.
3. Persist queue and position — music apps are resumed constantly.

## Pitfalls

- Platform audio APIs differ wildly (background modes, lock screens, Bluetooth).
- Legal/ToS constraints around third-party catalogs are not a Flutter problem, but they will kill the app faster than a jank frame.

Use Spotube as a map of the **plugin surface** a real media app needs.
