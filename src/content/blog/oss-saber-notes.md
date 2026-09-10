---
title: "Saber: handwriting notes and local-first files"
description: "Canvas input, highlighter compositing, and optional sync — a Flutter notes stack."
seoDescription: "Saber notes Flutter architecture: handwriting canvas, local-first storage, optional Nextcloud sync."
keywords:
  - saber notes flutter
  - flutter handwriting app
  - flutter canvas notes
  - local first flutter
  - stylus flutter
tags: ["Flutter", "OpenSource", "Notes", "Canvas"]
sources:
  - name: "Saber GitHub"
    url: "https://github.com/saber-notes/saber"
related:
  - slug: "oss-lotti-journal"
    title: "Lotti Journal"
  - slug: "oss-ente-photos"
    title: "Ente Photos"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "✍️"
draft: false
---

Handwriting apps are RenderObject-deep problems: stroke input, highlighter blend, export, and file format choices all matter.

![Diagram: Saber Notes](/blog/images/oss-saber-notes.svg)



## Lessons

1. Local files first; sync second. Notes must open offline.
2. Model strokes as data (points/pressure), not screenshots.
3. Dual-layer highlighter compositing is a classic graphics lesson in a product.

## Pitfalls

- Stylus latency is perceptible at ~1 frame.
- File format lock-in will anger users more than missing cloud features.

Study Saber when building **canvas-centric** Flutter tools.
