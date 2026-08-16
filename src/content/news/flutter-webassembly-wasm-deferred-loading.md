---
title: "Shipping Flutter Web on WebAssembly: the migration, the browsers, the headers"
description: "Wasm is on the path to becoming Flutter's default web target. Here is the real build pipeline, the package:web migration, browser support including the iOS gap, and deferred loading."
seoDescription: "Flutter WebAssembly guide: flutter build web --wasm, WasmGC browser support, dart:html to package:web migration, COOP/COEP headers for threading, and Wasm deferred loading."
keywords: ["flutter webassembly", "flutter build web wasm", "wasmgc browser support", "package:web migration", "dart:js_interop", "flutter web deferred loading"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🕸️"
tags: ["Flutter 3.47", "Flutter", "Web", "WebAssembly", "Performance"]
sources:
  - name: "Compiling to WebAssembly — flutter.dev docs"
    url: "https://docs.flutter.dev/platform-integration/web/wasm"
  - name: "Announcing Dart 3.13 — Dart Blog"
    url: "https://dart.dev/blog/announcing-dart-3-13"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "package:web on pub.dev"
    url: "https://pub.dev/packages/web"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

WebAssembly is the largest single bet in Flutter's 2026 roadmap, and 3.47 moves it forward again with experimental deferred loading. The Q2 2026 survey rates Web at **72% satisfaction** — the second-lowest platform score — and load performance is a big part of why. Wasm is the intended fix.

But shipping Wasm today is not a flag. It is a migration, a browser support matrix with a large hole in it, and two HTTP headers that most people forget.

## The build commands

```bash
# Development
flutter run -d chrome --wasm

# Production
flutter build web --wasm

# Production, with symbolication for error monitoring
flutter build web --wasm --source-maps

# Staging/QA — readable stack traces, ~47% larger binary
flutter build web --wasm --no-strip-wasm
```

Use `--source-maps` for anything you point Sentry or a similar service at; it produces `main.dart.wasm.map`. Use `--no-strip-wasm` only in staging — the size cost is real.

Flutter 3.47 also adds experimental deferred loading:

```bash
flutter build web --release --wasm --enable-wasm-deferred-loading
```

At the Dart layer this is the same capability that landed as a preview in Dart 3.13 (`dart compile wasm -O2 --enable-deferred-loading`), reported to give meaningful initial-page-load improvements over `dart2js` for large applications. For a big app this is the difference between Wasm being theoretically faster and actually faster in the metric users feel.

## The browser matrix, and the iOS problem

Flutter's Wasm output needs **WasmGC**. Support today:

| Browser | Status |
| --- | --- |
| Chromium / V8 | Supported, version 119+ |
| Firefox | Announced, currently blocked by a known bug |
| Safari | Supports WasmGC, but has a compatibility bug |
| iOS browsers | **Cannot run it** — every iOS browser uses WebKit |

Read the last row again. It is not "Safari on iOS"; it is *all* browsers on iOS, because Apple requires WebKit. If your web traffic skews mobile, a meaningful share of your users will not execute your Wasm build at all.

Which is why the fallback matters: **even with `--wasm`, Flutter still compiles to JavaScript.** If WasmGC is not detected at runtime, the JS build runs. You are shipping both, and the browser picks. That is good for correctness and bad for anyone hoping Wasm reduces their deployment size.

To confirm which path a session took:

```dart
const isRunningWithWasm = bool.fromEnvironment('dart.tool.dart2wasm');
```

Log it. Otherwise you will be optimising a code path most of your users never hit.

## The actual migration: get off dart:html

This is the work. Wasm will not compile if your app imports unsupported web libraries.

| Legacy | Replacement |
| --- | --- |
| `dart:html` | `package:web` |
| `dart:js`, `package:js` | `dart:js_interop` |

Flutter gives you an early warning without needing a Wasm build at all — running plain `flutter build web` performs a **Wasm dry run**:

```
Wasm dry run failed:
Found incompatibilities with WebAssembly.

package:my_app/main.dart 1:1 - dart:html unsupported (0)
```

Run that today, even if you have no Wasm plans. It is a free audit of your dependency tree.

When a full compilation fails, ignore the stack trace and find the **Context tree** — it names the package chain that pulled in the incompatible library:

```
Context: The unavailable library 'dart:html' is imported through these packages:
    main.dart => package:my_app => dart:html
```

That is usually a transitive dependency, not your code. For a gradual migration, conditional imports let both worlds coexist:

```dart
import 'fallback.dart'
  if (dart.library.js) 'legacy_web_interop.dart'
  if (dart.library.js_interop) 'wasm_web_interop.dart';
```

## The two headers everyone forgets

Flutter Wasm apps can render across **multiple threads** — but only if your server sends the right cross-origin headers:

| Header | Value |
| --- | --- |
| `Cross-Origin-Embedder-Policy` | `credentialless` or `require-corp` |
| `Cross-Origin-Opener-Policy` | `same-origin` |

Without both, multi-threading silently does not happen. Your app works; it is just slower than the benchmark you read. Check them in your CDN or reverse proxy config, not just in local dev — this is a classic "fast on localhost, slow in production" trap.

Note that `require-corp` will break embedded third-party resources that do not opt in via CORP headers. If you embed a lot of external content, `credentialless` is usually the pragmatic choice.

## Runtime differences worth knowing

`package:web` and `dart:js_interop` under Wasm are not bit-identical to the JS backend:

- **`is` / `as` checks behave differently** on JS interop types
- **Zone propagation in callbacks differs**

Neither breaks a typical app, but both will bite code that does clever things with type checks across the interop boundary. Test your interop layer specifically rather than assuming parity.

## Your rollout plan

1. **Run `flutter build web` today** and read the Wasm dry run output. That is your migration backlog.
2. **Update `web/index.html`** to the current Flutter initialization, or regenerate with `flutter create . --platforms web`.
3. **Migrate your own code** from `dart:html` to `package:web` and from `dart:js` to `dart:js_interop`.
4. **Chase the transitive offenders** named in the Context tree. File issues on dependencies that still import `dart:html`.
5. **Configure COOP and COEP headers** in your production serving layer, then verify them with the network tab.
6. **Build with `--wasm --source-maps`** and wire the map file into your error monitoring.
7. **Log `dart.tool.dart2wasm`** and measure what fraction of real sessions actually get the Wasm path.
8. **Try `--enable-wasm-deferred-loading`** if your bundle is large, and measure initial page load rather than total size.

## The bottom line

Wasm is genuinely faster, and the roadmap points at it becoming the default. But today it is an additive build, not a replacement: you ship JS as well, iOS users get the JS path regardless, and the performance win depends on two headers most teams have not set. The single highest-value thing you can do this week costs nothing — run `flutter build web` and read the dry-run output. Whether or not you ship Wasm this quarter, that list of `dart:html` dependencies is a debt you will pay eventually.
