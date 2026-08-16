---
title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
description: "Flutter 3.47 ships Material and Cupertino as standalone pub.dev packages, makes Impeller the default renderer on macOS, Windows and Linux, and graduates Widget Previews to stable."
seoDescription: "Flutter 3.47 release review: standalone material_ui and cupertino_ui packages, Impeller default on desktop, stable Widget Previews, iOS 15 minimum, Dart 3.13 — plus Q2 2026 survey data."
keywords: ["flutter 3.47", "flutter latest version", "material_ui package", "cupertino_ui package", "impeller desktop", "flutter widget previews", "dart 3.13"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🧩"
tags: ["Flutter 3.47", "Flutter", "Impeller", "Material", "Cupertino", "Release"]
sources:
  - name: "What's new in Flutter 3.47 — Flutter Blog"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Flutter Q2 2026 survey — trust, transparency, and an evolving community"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
  - name: "Introducing Skills for Dart and Flutter"
    url: "https://flutter.dev/blog/introducing-skills-for-dart-and-flutter"
  - name: "@FlutterDev on X"
    url: "https://x.com/FlutterDev"
related:
  - slug: "flutter-3-44-ios-26-macos-support-web-hot-reload"
    title: "Flutter 3.44 review: iOS 26 support, stateful hot reload on web, and Cupertino Squircles"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Flutter 3.47 landed on August 13, 2026, and for once the headline is not a feature — it is an architectural split. The design system is moving out of the SDK. Add Impeller becoming the default renderer on every desktop platform and Widget Previews going stable, and this is the most structurally significant Flutter release in years.

The numbers behind it: **1,356 commits from 169 contributors, 66 of them first-timers**, shipping as `Flutter 3.47.0 • Dart 3.13.0 • DevTools 2.60.0`.

## Material and Cupertino become packages you choose

The change everyone is talking about: **`material_ui` and `cupertino_ui` are now standalone packages on pub.dev**, both at 1.0. The libraries still live inside the SDK for now, but the SDK copies are **scheduled for formal deprecation in the November stable release**.

Why this matters more than it sounds:

- **Design systems can now ship on their own clock.** Instead of waiting for a quarterly SDK release, Material and Cupertino can iterate weekly. Cupertino in particular needs it — see the survey numbers below.
- **You can pin your design system independently of your framework version.** Upgrading Flutter no longer means swallowing every widget change at the same time.
- **Apps that use neither can drop both.** If you ship a fully custom design system, the Material tree stops being a mandatory dependency.

Migration is a one-liner:

```bash
dart fix --apply --code=migrate_design_widgets
```

For the messy middle — your app migrated but a dependency still imports the old paths — there is a `MaterialUiCompatibilityBridge` to keep both worlds talking.

## Impeller is now the default on macOS, Windows and Linux

Impeller replaces Skia as the default renderer across all three desktop platforms. The practical payoff is the same one mobile got: **shaders are compiled at build time, so shader compilation jank goes away**. On macOS, **wide gamut color is on by default** as well.

There are opt-outs per platform, but the blog is blunt that **fallback options will be removed in a future release**. Treat the opt-out as a bug-reporting window, not a long-term strategy.

## Widget Previews graduate to stable

Widget Preview is no longer experimental. The stable version adds **local caching for faster startup** and **abstract theme APIs**, so a preview can be rendered against multiple themes without wiring up a full app shell. If you tried previews in an earlier release and found them slow, this is the version to retry.

## The upgrade tax: iOS 15 and macOS 12 minimums

To support Xcode 27, the floors moved:

| Platform | Old minimum | New minimum |
| --- | --- | --- |
| iOS | 13 | **15** |
| macOS | 10.15 | **12** |

Apps also need to **adopt the UIScene lifecycle** for iOS 27 compliance. If you skipped that migration when 3.44 flagged it, this is where it stops being optional.

## Web: Wasm keeps inching toward default

The WebAssembly story from the 2026 roadmap continues. You can build with:

```bash
flutter build web --release --wasm
```

New this release: **experimental deferred loading for Wasm** behind `--enable-wasm-deferred-loading`. The prerequisite is still the same — migrate off legacy `dart:html` to `package:web` before you expect any of this to work cleanly.

On the plugin side, **92 of the top 100 iOS plugins have migrated to Swift Package Manager**. The CocoaPods era is ending faster than most upgrade guides assume.

## What the Q2 2026 survey says about where Flutter actually hurts

Google published the Q2 2026 survey results the same week — **3,500+ complete responses collected June 8–22, 2026** — and it reads as the subtext for this release.

The good news is unusually good:

- **93% overall satisfaction**, with **58% "very satisfied"** (up 6 points from Q4 2025)
- **83% trust Flutter** to meet their needs, up from 77%
- For the first time, **every developer subgroup cleared 90% satisfaction**

Then the outlier:

- **Cupertino widgets: 61% satisfaction, down 6 points** — the lowest-rated area in the survey, against 92% for Dart, 91% for Android, 90% for the core framework.

Which is exactly why decoupling Cupertino into a package that can ship weekly is the fix, not a refactor for its own sake.

The top pain points name the rest of the release, too: **platform/ecosystem maturity (44%)**, driven by version-matrix complexity during upgrades, then **tooling and IDE experience (33%)**, then **bugs and stability (24%)**.

One more number worth sitting with: developers trust community "battle-tested" features at **41%** versus **26%** for Google-built features, and trust in Flutter runs **20+ points ahead of trust in Google** (83% vs 62%).

## The AI trend line: agents are now a first-class Flutter workflow

The survey's AI section is the clearest signal of where the ecosystem is heading. On adoption:

- **Claude Code — 32%**
- **Antigravity — 23%**
- GitHub Copilot — 19%
- Cursor — 18%
- Codex — 17%

Agentic tools now lead the pack, ahead of the autocomplete generation. VS Code (66%) and Android Studio (40%) remain the editors those agents run inside.

Google is building for that directly. **Skills for Dart and Flutter**, announced in May 2026, are task-oriented instruction sets that teach an AI agent *how* to do a specific Flutter job — the initial five cover integration testing, localization, responsive layouts, pattern-matching refactors, and test coverage. The framing from the announcement is the useful mental model: MCP gives an agent tools; a Skill gives it the blueprint and the professional know-how. They load progressively, only when relevant, which keeps token usage down.

The problem being solved is the one every Flutter developer using an LLM has hit: the framework moves faster than model training data. A release like 3.47, which changes import paths for the two most-used libraries in the ecosystem, is exactly the kind of change a stale model will get confidently wrong.

## Your upgrade checklist

1. **Run `dart fix --apply --code=migrate_design_widgets`** and move to `material_ui` / `cupertino_ui` before the November deprecation.
2. **Audit dependencies** for packages still importing the SDK design libraries; use `MaterialUiCompatibilityBridge` while you wait on them.
3. **Bump your deployment targets** to iOS 15 / macOS 12 and finish the UIScene migration.
4. **Smoke-test desktop builds under Impeller** — and file bugs now while the Skia fallback still exists.
5. **Retry Widget Previews** if the experimental version put you off.
6. **Test a Wasm build** and check whether deferred loading helps your bundle.
7. **Point your AI agent at the Dart & Flutter Skills** so it stops generating 3.44-era imports.

## The bottom line

Flutter 3.47 is the release where Flutter stops being one monolith. Material and Cupertino become packages you version yourself, Impeller finishes its takeover on desktop, and previews become a normal part of the loop. The survey explains the strategy: satisfaction is high almost everywhere, Cupertino is the exception, and shipping design systems on their own schedule is how you fix that without holding the SDK hostage. Budget an afternoon for the migration — but do it before November, when the old imports start warning.
