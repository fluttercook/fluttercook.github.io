---
title: "Flutter Zero: Flutter with dart:ui taken out"
package: "flutter_zero"
repo: "knopp/flutter_zero"
githubUrl: "https://github.com/knopp/flutter_zero"
category: "Framework/Core"
stars: 274
forks: 9
lastUpdate: "2026-08-08"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+zero+dart+ui"
priority: "High"
phase: "P1"
trendRank: 0
description: "Flutter Zero strips dart:ui, Skia and Impeller out of Flutter, leaving a Dart runtime that still works with the flutter tool. An experiment in decoupling the UI layer from the engine."
seoDescription: "Flutter Zero is Flutter with dart:ui removed - no Skia, no Impeller, no widgets, but the same flutter tool and IDE plugins. What it is for, who should look at it, and what it cannot do yet."
keywords:
  - flutter zero
  - flutter without dart ui
  - dart runtime native ui
  - flutter engine embedder
  - dart ffi native ui
  - matej knopp flutter
topics:
  - dart
  - flutter-engine
  - ffi
summary:
  - "**Flutter Zero** is Flutter with most of `dart:ui` removed - no widgets, no Skia, no Impeller."
  - It keeps full compatibility with the `flutter` tool and the IDE plugins, so create, build and run work as usual.
  - The point is to explore Dart apps that draw their UI with native toolkits through interop, and to make `dart:ui` a package rather than an engine built-in.
  - "**274★**, BSD-3-Clause, by Matej Knopp. Engine builds exist for every supported platform, but this is an experiment, not a product."
related:
  - slug: denial
    title: "Denial: a Wayland compositor with Flutter at the foundation"
  - slug: dart-mcp
    title: "dart-lang/ai: Dart's official MCP packages"
  - slug: agent-plugins
    title: "agent-plugins: a Flutter developer's guide"
faq:
  - q: Can I use Flutter Zero in production?
    a: "No. The author describes it as very raw and experimental. Engine builds exist for every platform Flutter supports and you can build and run real applications, but there is no stability guarantee, no release cadence, and no ecosystem of packages that expect a UI-less dart:ui."
  - q: Does Flutter Zero still work with the flutter command and IDE plugins?
    a: "Yes, and that is the whole design constraint. flutter create, flutter build and flutter run behave normally, and the VS Code and IntelliJ plugins keep working apart from the parts that inspect the widget tree. Rewriting flutter_tool from scratch was explicitly avoided."
  - q: What is the threading model?
    a: "All Dart code runs on the platform thread. No other threading configuration is supported. That is a deliberate simplification, and it is very different from standard Flutter, where the UI thread is separate from the platform thread."
  - q: Why remove dart:ui at all?
    a: "Because it is tightly coupled to the engine and was designed under constraints that no longer hold. Threading changed, FFI got much better, synchronous Dart-to-platform calls are now possible, and native assets let packages ship their own native code. A modular dart:ui built as a package now looks feasible."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`flutter_zero`](https://github.com/knopp/flutter_zero) is the most interesting Flutter repository of 2026 that almost nobody will ship. It is Flutter with most of `dart:ui` cut out — no widgets, no Skia, no Impeller — leaving a Dart runtime that still builds and runs through the ordinary `flutter` command. **274★**, BSD-3-Clause, last pushed **2026-08-08**, from [Matej Knopp](https://github.com/knopp), whose `flutter_reorderable_list` has been in Flutter apps for years.

## What is Flutter Zero?

Flutter Zero is a stripped-down Flutter that makes no assumptions about the UI layer. What remains is a Dart runtime you can deploy to every platform Flutter supports, plus the entire toolchain around it.

That last part is the clever bit. Flutter Zero is not a fork of the Flutter repository — it is a new repository holding a very small subset of the code, chosen so that checkouts stay fast and disk usage stays small. But it keeps compatibility with `flutter_tool`, so `flutter create`, `flutter build` and `flutter run` work, and the VS Code and IntelliJ plugins keep working too, minus the widget-inspector parts that have nothing left to inspect.

## Why it matters in 2026

The argument in the README is worth reading in full, but the short version is this: `dart:ui` was designed under constraints that no longer hold.

The threading model has changed. FFI has improved enormously. Bidirectional synchronous interaction between Dart and platform APIs is possible now, which makes the untyped, asynchronous, ad-hoc platform-channel protocol far less necessary than it was. And `native assets` lets ordinary packages contribute native code with custom build steps.

Put those together and something that was impossible in 2018 looks feasible in 2026: a modular `dart:ui` that lives in a package, with proper Dart interfaces and platform-specific FFI or JNI implementations, instead of a monolithic blob compiled into the engine.

Flutter Zero is the experiment that tests whether the bottom half of that idea holds. It is also, quietly, the most credible route yet to writing a Dart application with a genuinely native UI toolkit — SwiftUI on Apple platforms, Jetpack Compose on Android — while keeping Dart, pub, and the Flutter toolchain.

## Getting started

There is no pub package to install; Flutter Zero is an engine and SDK variant, not a dependency. Clone the repository and follow its build instructions:

```bash
git clone https://github.com/knopp/flutter_zero.git
```

Prebuilt engine builds are available for every platform Flutter supports, so you do not need to compile the engine yourself to try it. From there the normal workflow applies — the `examples/hello_world` package in the repository workspace is the smallest thing that runs.

Expect to read source. The repository is small enough that this is realistic, which is more than can be said for the main Flutter engine.

## When should you look at Flutter Zero?

- you want a Dart application on mobile or desktop with a native UI, and Flutter's own rendering is a liability rather than an asset
- you are building a headless Dart process — a daemon, a CLI, an agent — and want Flutter's cross-platform build and deployment story without shipping a renderer
- you are curious about engine internals and want a codebase small enough to actually read
- you are prototyping an alternative `dart:ui` and need a host that does not already have one

## Where it falls short

Be honest about the state of it. The author's own answer to "can this be used right now?" is "yes, but it is very raw."

The single-threaded model is the sharpest edge: all Dart code runs on the platform thread, and no other configuration is supported. Anything that assumes the standard Flutter threading model will need rethinking.

Beyond that, essentially the entire package ecosystem assumes `dart:ui` exists. Any package that touches widgets, painting, images, or text layout will not work. You are building on a runtime, not a framework, and the missing pieces are yours to supply.

There is also no roadmap commitment. The README calls the naming question low priority and describes running normal Flutter apps on top of Flutter Zero as something that would need "a lot of luck and motivation." Treat that as the honest signal it is.

## Alternatives worth comparing

- [Denial: a Wayland compositor with Flutter at the foundation](/recipes/denial/) — the opposite bet, pushing Flutter *deeper* into the system rather than removing it
- [dart-lang/ai: Dart's official MCP packages](/recipes/dart-mcp/) — the other current example of Dart being used well away from the widget tree
- [agent-plugins: a Flutter developer's guide](/recipes/agent-plugins/)

## Frequently asked questions

### Can I use Flutter Zero in production?

No. The author describes it as very raw and experimental. Engine builds exist for every platform Flutter supports and you can build and run real applications, but there is no stability guarantee, no release cadence, and no ecosystem of packages that expect a UI-less `dart:ui`.

### Does Flutter Zero still work with the flutter command and IDE plugins?

Yes, and that is the whole design constraint. `flutter create`, `flutter build` and `flutter run` behave normally, and the VS Code and IntelliJ plugins keep working apart from the parts that inspect the widget tree. Rewriting `flutter_tool` from scratch was explicitly avoided.

### What is the threading model?

All Dart code runs on the platform thread. No other threading configuration is supported. That is a deliberate simplification, and it is very different from standard Flutter, where the UI thread is separate from the platform thread.

### Why remove dart:ui at all?

Because it is tightly coupled to the engine and was designed under constraints that no longer hold. Threading changed, FFI got much better, synchronous Dart-to-platform calls are now possible, and native assets let packages ship their own native code. A modular `dart:ui` built as a package now looks feasible.

## Resources & links

- **GitHub:** [knopp/flutter_zero](https://github.com/knopp/flutter_zero)
- **License:** BSD-3-Clause
- **Background reading:** [Dart interop](https://dart.dev/interop) and [dart-lang/native](https://github.com/dart-lang/native)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
