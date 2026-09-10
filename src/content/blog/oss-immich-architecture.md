---
title: "Immich: architecture lessons from a 100k-star Flutter photo stack"
description: "How Immich combines a Flutter mobile client, NestJS API, and ML pipeline — and which patterns you can steal."
seoDescription: "Immich Flutter architecture deep dive: mobile client, background sync, self-hosted photo backup patterns to steal."
keywords:
  - immich flutter
  - immich architecture
  - self hosted photo backup flutter
  - immich mobile client
  - flutter large scale app
tags: ["Flutter", "OpenSource", "Photos", "Architecture"]
sources:
  - name: "Immich GitHub"
    url: "https://github.com/immich-app/immich"
  - name: "Immich docs"
    url: "https://immich.app/docs"
related:
  - slug: "oss-ente-photos"
    title: "Ente Photos"
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📸"
draft: false
---

Immich is the rare Flutter app most self-hosters have heard of: Google-Photos-like backup, albums, ML search, and a mobile client that must survive flaky networks and huge libraries.

![Diagram: Immich Architecture](/blog/images/oss-immich-architecture.svg)



## What the stack actually is

- **Flutter mobile** clients for iOS/Android (plus web/desktop surfaces elsewhere in the monorepo).
- **NestJS** server with a generated API client — OpenAPI keeps mobile and server honest.
- **Python ML** services for CLIP-style search and recognition.
- **Docker** as the blessed install path for self-hosters.

## Patterns worth stealing

1. **Generated API clients.** Do not hand-write DTOs for a large domain.
2. **Background-first upload.** Treat sync as a product feature, not an afterthought.
3. **Server-owned thumbnails.** Mobile should not re-encode a 48MP original on a mid-range phone.

## Flutter-specific notes

Large galleries punish naive `GridView`s. Immich-style apps need aggressive view recycling, placeholder strategy, and careful isolate use for decode. Study how upload queues persist across app restarts.

## If you copy it naively

- Pulling the whole monorepo into a tiny app.
- Skipping authz on “local network” assumptions.
- Shipping ML search without a graceful empty/error path.

Steal the **client/server contract** and the **sync queue design**. Leave the Docker topology until you need it.
