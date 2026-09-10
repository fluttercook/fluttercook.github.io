---
title: "RustDesk: Rust core, Flutter shell"
description: "How a remote-desktop product splits performance-critical Rust from a Flutter UI."
seoDescription: "RustDesk Flutter hybrid architecture: Rust core FFI, Flutter UI, remote desktop open source patterns."
keywords:
  - rustdesk flutter
  - rust flutter hybrid
  - flutter ffi desktop
  - open source remote desktop
  - rustdesk architecture
tags: ["Flutter", "OpenSource", "Rust", "Desktop"]
sources:
  - name: "RustDesk GitHub"
    url: "https://github.com/rustdesk/rustdesk"
  - name: "RustDesk docs"
    url: "https://rustdesk.com/docs/en/"
related:
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
  - slug: "oss-hiddify-next"
    title: "Hiddify Next"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🖥️"
draft: false
---

Not every pixel problem is a Dart problem. RustDesk keeps capture/encode/networking in **Rust** and uses Flutter as the interactive shell — a hybrid you should understand before you rewrite a native module in pure Dart.

![Diagram: RustDesk Hybrid](/blog/images/oss-rustdesk-flutter.svg)



## Split of responsibilities

| Concern | Home |
| --- | --- |
| Screen capture, codecs, relay | Rust core |
| Connection UX, settings, session UI | Flutter |
| OS integration | Platform channels / FFI |

## Steal this

1. Draw a hard boundary: hot UI loop vs hot data loop.
2. Prefer FFI for throughput; channels for infrequent events.
3. Keep session state outside widget trees.

## Pitfalls

- Hybrid builds double your CI matrix.
- ABI and packaging for desktop installers are non-trivial.

If your app is UI-heavy, Flutter alone may suffice. If it is pipeline-heavy, copy RustDesk’s **boundary**, not necessarily Rust itself.
