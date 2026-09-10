---
title: "LocalSend: AirDrop-style transfer with zero cloud"
description: "A Flutter + Rust LAN protocol on port 53317 — lessons in local-first networking."
seoDescription: "LocalSend architecture Flutter Rust: LAN HTTPS file transfer protocol 53317, no cloud server, desktop mobile."
keywords:
  - localsend architecture
  - flutter file sharing lan
  - localsend protocol
  - flutter rust hybrid
  - airdrop alternative flutter
tags: ["Flutter", "OpenSource", "Networking", "Rust"]
sources:
  - name: "LocalSend GitHub"
    url: "https://github.com/localsend/localsend"
  - name: "LocalSend site"
    url: "https://localsend.org/"
related:
  - slug: "oss-rustdesk-flutter"
    title: "RustDesk Hybrid"
  - slug: "oss-immich-architecture"
    title: "Immich Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📡"
draft: false
---

LocalSend answers a sharp product question: can two devices exchange files without an account or a server? Yes — if you design for LAN discovery, HTTPS, and explicit consent.

![Diagram: LocalSend Architecture](/blog/images/oss-localsend-architecture.svg)



## Design highlights

- Peer protocol over local HTTPS (commonly associated with port **53317**).
- Flutter UI with Rust/native pieces for performance-critical paths.
- No cloud control plane — privacy is the feature.

## Steal this

1. Discovery + consent UX is half the product.
2. Make transfers resumable and visible; silent failures destroy trust.
3. Keep a CLI headless mode for power users and automation.

## Pitfalls

- Mobile OS background limits kill naive long transfers.
- Mixed networks (AP isolation, VPN, captive portals) will generate support load — document them.

Study LocalSend when you need **local-first** product patterns, not just a package to copy.
