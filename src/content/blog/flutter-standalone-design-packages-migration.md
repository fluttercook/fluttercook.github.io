---
title: Migrating to standalone material_ui and cupertino_ui in Flutter 3.47
description: How to move off SDK-bundled Material/Cupertino with dart fix and the compatibility bridge.
seoDescription: 'Flutter 3.47 material_ui cupertino_ui migration: dart fix --code=migrate_design_widgets, MaterialUiCompatibilityBridge,
  weekly design releases.'
keywords:
- flutter material_ui migration
- cupertino_ui package
- dart fix migrate_design_widgets
- MaterialUiCompatibilityBridge
- flutter 3.47 material
- flutter
- dart
- mobile development
category: Deep Dive
topic: Framework
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-11'
emoji: 🧭
tags:
- Flutter
- Material
- Migration
sources:
- name: What's new in Flutter 3.47
  url: https://flutter.dev/blog/whats-new-in-flutter-3-47
- name: material_ui
  url: https://pub.dev/packages/material_ui
- name: Flutter documentation
  url: https://docs.flutter.dev/
- name: Dart documentation
  url: https://dart.dev/guides
related:
- slug: flutter-impeller-desktop-sdf-text
  title: 'Impeller on desktop: SDF text and Metal/Vulkan defaults'
- slug: flutter-swiftpm-plugin-migration-checklist
  title: Swift Package Manager plugin migration checklist for Flutter
draft: false
---

Flutter 3.47 ships opt-in standalone design packages at 1.0. Design updates no longer wait on the quarterly SDK train. This article turns that observation into a small implementation model you can test, measure, and keep boring when the app grows.

## The problem in one sentence

How to move off SDK-bundled Material/Cupertino with dart fix and the compatibility bridge. The useful question is not whether the API or pattern looks elegant in isolation. It is where state lives, which boundary owns failure, and how a user recovers when the happy path disappears.

![Flutter architecture diagram for Migrating to standalone material_ui and cupertino_ui in Flutter 3.47](/blog/images/fluttercook-editorial-2026.svg)

## A practical model

Weekly releases, independent upgrades, and a style-neutral core for custom design systems and platform design shocks.

Start with one explicit owner for the behavior. Keep widgets responsible for rendering and user intent; keep IO, persistence, permissions, and retries behind a small interface. That gives you a seam for a fake in tests and a place to record the facts that matter in production.

For a Flutter app, the boundary usually looks like this:

1. The widget emits an intent such as load, submit, refresh, or retry.
2. A controller or use case validates the intent and calls the boundary.
3. The boundary returns typed data or a typed failure, never a string meant only for logs.
4. The UI renders loading, empty, success, and failure states explicitly.

This shape is deliberately modest. It works with `setState`, Bloc, Riverpod, or another state layer because the important decision is ownership, not the brand of package.

## Minimal implementation

The smallest useful experiment is enough to expose the trade-off:

```text
dart fix --apply --code=migrate_design_widgets
```

Put this behind a feature-sized interface and add one test for the success path and one for the failure path. If the example needs global state before it can run, the boundary is probably in the wrong place.

## Production checklist

- Define the lifecycle: who starts work, who cancels it, and what survives a restart?
- Measure the user-visible result: frame time, bytes, latency, conversion, or recovery time.
- Keep platform-specific code at the edge and document the minimum OS/SDK assumptions.
- Add an empty state and an offline/error state before adding polish.
- Log identifiers and timings, but redact tokens, personal data, and full payloads.
- Prefer a reversible rollout: a flag, staged release, or server-side fallback.

## Pitfalls worth paying for early

Core SDK copies deprecate in November. Package authors: treat as a major release. A common failure mode is to make the demo path correct while leaving cancellation, retries, permissions, accessibility, and upgrade behavior implicit. Those are not edge cases once the app has real users. Test at least one slow device, one interrupted network request, and one process restart where this topic affects lifecycle or storage.

## How to decide whether it worked

Write down the baseline before changing code. Compare the same user journey on the same device class, then inspect both the median and the worst visible failures. A smaller diff with a clear rollback is usually safer than a framework-wide rewrite. Keep the decision and its evidence near the code so the next upgrade does not restart the same argument.

For the neighboring ideas, read [Impeller on desktop: SDF text and Metal/Vulkan defaults](/blog/flutter-impeller-desktop-sdf-text/) and [Swift Package Manager plugin migration checklist for Flutter](/blog/flutter-swiftpm-plugin-migration-checklist/).
