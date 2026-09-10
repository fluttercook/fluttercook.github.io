---
title: "Hiddify Next: Flutter UI over a tunnel core"
description: "A cross-platform proxy client shows how to pair Flutter with a Go/Sing-box style core."
seoDescription: "Hiddify Next Flutter architecture: Sing-box core, VPN client UX, multi-protocol proxy patterns."
keywords:
  - hiddify flutter
  - flutter vpn client
  - sing-box flutter
  - flutter network tunnel
  - proxy app architecture
tags: ["Flutter", "OpenSource", "Networking"]
sources:
  - name: "Hiddify GitHub"
    url: "https://github.com/hiddify/hiddify-app"
related:
  - slug: "oss-rustdesk-flutter"
    title: "RustDesk Hybrid"
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔐"
draft: false
---

Proxy/VPN clients live at the edge of OS permissions. Hiddify Next pairs a Flutter UI with a high-performance tunnel core (Sing-box/Go lineage) so the UI stays expressive while the data path stays boring and fast.

![Diagram: Hiddify Next](/blog/images/oss-hiddify-next.svg)



## Lessons

1. **Status is a stream.** Latency, connected server, and errors should be one consistent model.
2. **Config as data.** Import/export profiles; do not hardcode endpoints in widgets.
3. **Platform VPN APIs** are the hard part — isolate them behind a service interface.

## Pitfalls

- Battery and thermal costs of always-on tunnels.
- Store policy differences for VPN apps.

Use this repo when you need a reference for **service-backed Flutter** rather than a pure CRUD app.
