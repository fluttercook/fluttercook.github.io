---
title: "Ente: end-to-end encrypted photos in Flutter"
description: "Crypto UX is a design problem. Ente shows how encrypted galleries stay usable."
seoDescription: "Ente photos Flutter architecture: E2EE gallery, key management UX, encrypted backup patterns."
keywords:
  - ente photos flutter
  - e2ee photo app
  - flutter encrypted gallery
  - ente architecture
  - privacy photo backup
tags: ["Flutter", "OpenSource", "Crypto", "Photos"]
sources:
  - name: "Ente GitHub"
    url: "https://github.com/ente/ente"
  - name: "Ente docs"
    url: "https://ente.io/"
related:
  - slug: "oss-immich-architecture"
    title: "Immich Architecture"
  - slug: "oss-saber-notes"
    title: "Saber Notes"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔐"
draft: false
---

If Immich is the self-hosted default, Ente is the privacy-first counterpart: clients (including Flutter mobile) encrypt before upload, and the server stores blobs it cannot read.

![Diagram: Ente Photos](/blog/images/oss-ente-photos.svg)



## What to study

1. **Key UX.** Recovery phrases and family sharing beat “trust us” dashboards.
2. **Encrypt-then-upload** pipelines with resumable transfers.
3. Product surfaces for Photos *and* Auth-style secrets.

## Pitfalls

- Users forget passphrases — design account recovery before launch.
- Thumbnail generation must not leak plaintext on shared devices.

Copy the **threat model conversation**, not just the cipher choices.
