---
title: "Jaspr: server-driven Dart for the web"
description: "The Flutter mental model on the server — including the framework that builds Flutter’s own docs site."
seoDescription: "Jaspr Dart web framework architecture: server components, hydration, Flutter-like UI on the server."
keywords:
  - jaspr dart
  - dart web framework
  - flutter mental model server
  - jaspr architecture
  - dart ssr
tags: ["Dart", "OpenSource", "Web"]
sources:
  - name: "Jaspr GitHub"
    url: "https://github.com/schultek/jaspr"
  - name: "Jaspr site"
    url: "https://jaspr.site"
related:
  - slug: "oss-serverpod"
    title: "Serverpod"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🌐"
draft: false
---

Jaspr brings a component mental model to Dart on the server. If you like Flutter’s structure but need HTML/SEO, this is the adjacent ecosystem — notably powering parts of Flutter’s own web presence.

![Diagram: Jaspr Dart Web](/blog/images/oss-jaspr-dart-web.svg)



## Lessons

1. Shared Dart models between API, server UI, and Flutter clients reduce DTO drift.
2. SSR/hydration is a packaging problem as much as a UI problem.
3. Server components encourage boring, cacheable pages.

## Pitfalls

Do not assume Flutter widgets work unchanged. Layout constraints and lifecycle differ from mobile.

Consider Jaspr for content sites and dashboards where SEO matters and Dart is already your language.
