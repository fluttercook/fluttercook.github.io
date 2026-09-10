---
title: "Harmony Music: offline-first player patterns"
description: "Library scan, queue, and audio service separation in a Flutter music app."
seoDescription: "Harmony Music Flutter architecture: offline library scan, queue management, audio service separation."
keywords:
  - harmony music flutter
  - offline music player flutter
  - flutter audio service
  - flutter music queue
  - flutter local library
tags: ["Flutter", "OpenSource", "Music"]
sources:
  - name: "MediaKit"
    url: "https://github.com/media-kit/media-kit"
related:
  - slug: "oss-spotube-architecture"
    title: "Spotube Architecture"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎧"
draft: false
---

Offline music apps are storage, scanning, and service lifecycle problems. Harmony-style players keep a local library index and a playback service that survives UI navigation.

![Diagram: Harmony Music](/blog/images/oss-harmony-music.svg)



## Patterns

1. Scan once, listen to filesystem events later.
2. Queue lives in a controller/service, not in a screen widget.
3. Platform notification/media sessions are required UX.

## Pitfalls

Large libraries need incremental indexing. Do not block first frame on a full SD card scan.

Compare with Spotube if you also need streaming catalogs.
