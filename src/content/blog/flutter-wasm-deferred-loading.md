---
title: "Flutter web Wasm: deferred loading for smaller first paint"
description: "Flutter is moving toward Wasm by default. Deferred loading lets you split modules and ship a smaller bootstrap."
seoDescription: "Flutter web Wasm deferred loading, flutter build web --wasm --enable-wasm-deferred-loading, package:web migration."
keywords:
  - flutter wasm
  - flutter deferred loading wasm
  - flutter web performance
  - dart2wasm flutter
  - package:web migration
tags: ["Flutter", "Web", "Wasm", "Performance"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Compile to WebAssembly"
    url: "https://docs.flutter.dev/platform-integration/web/wasm"
related:
  - slug: "flutter-platform-specific-assets"
    title: "Platform-specific Assets"
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
category: "Deep Dive"
topic: "Web"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🕸️"
draft: false
---

Wasm unlocks near-native graphics on the web — and a new packaging discipline. Flutter 3.47 adds **experimental deferred loading** for Wasm builds so you can split a large app into lazy modules.

![Diagram: Wasm Deferred Loading](/blog/images/flutter-wasm-deferred-loading.svg)


## Build commands

```bash
flutter build web --release --wasm
# experimental deferred modules (main channel flag in 3.47 era)
flutter build web --release --wasm --enable-wasm-deferred-loading
```

## Prerequisites

- Migrate off `dart:html` to **`package:web`** and modern JS interop.
- Update packages that still assume dart2js-only interop.

## Splitting strategy

1. Keep login/shell in the main module.
2. Defer heavy feature screens (admin, editors, maps).
3. Measure *time to interactive*, not just download size.

## Pitfalls

- Deferred libraries must not be required during first frame.
- Wasm + canvas/Skottie-heavy UIs still need careful asset budgets.
- Not every browser/flag combination is equal — test Chrome, Safari, Firefox.
