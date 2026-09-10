---
title: "FluffyChat: Matrix chat in Flutter with real E2EE"
description: "How a Matrix client handles rooms, encryption, and multi-platform delivery from Flutter."
seoDescription: "FluffyChat Matrix Flutter architecture: E2EE, room sync, multi-platform chat client patterns worth studying."
keywords:
  - fluffychat flutter
  - matrix client flutter
  - flutter e2ee chat
  - flutter matrix sdk
  - open source chat app
tags: ["Flutter", "OpenSource", "Chat", "Matrix"]
sources:
  - name: "FluffyChat GitHub"
    url: "https://github.com/krille-chan/fluffychat"
  - name: "Matrix spec"
    url: "https://spec.matrix.org/"
related:
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
  - slug: "oss-ente-photos"
    title: "Ente Photos"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "💬"
draft: false
---

Chat apps look simple until encryption and multi-device sync arrive. FluffyChat is a production Matrix client in Flutter — useful if you care about messaging architecture without inventing a protocol.

![Diagram: FluffyChat Architecture](/blog/images/oss-fluffychat-architecture.svg)



## Architecture beats

- **Matrix SDK** as the protocol brain (with Rust crypto such as Vodozemac underneath).
- Flutter as the shared shell for mobile and desktop form factors.
- Optional push (FCM etc.) layered on top of sync — not instead of it.

## Steal this

1. Keep protocol state out of widgets; expose streams/selectors.
2. Model rooms as first-class domain objects, not screens.
3. Treat device verification UX as a product surface, not a settings footnote.

## Pitfalls

E2EE bugs are trust bugs. Do not home-roll crypto. Offline queueing and out-of-order events will break naive `setState` UIs.

If you need chat, prefer Matrix (or another mature protocol) over a custom socket JSON soup.
