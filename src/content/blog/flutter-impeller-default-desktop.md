---
title: "Impeller is now the default desktop renderer — what actually changes"
description: "Flutter 3.47 turns Impeller on by default for macOS, Windows, and Linux. Shader jank dies; SDF text sharpens; Skia opt-outs are temporary."
seoDescription: "Flutter 3.47 Impeller default on desktop: Metal and Vulkan, SDF text, how to opt out on macOS Windows Linux, and migration notes."
keywords:
  - flutter impeller desktop
  - impeller windows linux macos default
  - flutter 3.47 impeller
  - sdf text flutter desktop
  - disable impeller desktop
tags: ["Flutter", "Impeller", "Desktop", "Rendering", "Performance"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Impeller docs"
    url: "https://docs.flutter.dev/perf/impeller"
related:
  - slug: "flutter-impeller-jank-profiling"
    title: "flutter-impeller-jank-profiling"
  - slug: "flutter-fragment-shader-api"
    title: "Fragment Shader API"
category: "Deep Dive"
topic: "Performance"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎨"
draft: false
---

Mobile Impeller defaults landed earlier. Flutter 3.47 finishes the job on **macOS, Windows, and Linux**. Desktop apps now target Metal (macOS) and Vulkan (Windows/Linux) with a fixed shader set compiled at engine-build time.

![Diagram: Impeller Default on Desktop](/blog/images/flutter-impeller-default-desktop.svg)


## What you gain

- **No shader-compilation jank** on first run of an animation.
- **Signed Distance Function text** — sharper glyphs on lower-density desktop displays.
- **Wide Gamut Color on by default on macOS** where hardware supports it.

## Temporary Skia opt-outs

If a regression blocks you:

| Platform | Opt-out |
| --- | --- |
| macOS | `FLTEnableImpeller=false` in `Info.plist` |
| Windows | `project.set_impeller_switch(flutter::ImpellerSwitch::Disabled)` in `main.cpp` |
| Linux | `fl_dart_project_set_enable_impeller(project, FALSE)` in `my_application.cc` |

File a bug. Fallbacks are scheduled for removal.

## What to retest

1. Custom `FragmentShader`s and `saveLayer`-heavy effects.
2. Platform views and external textures.
3. Print/export paths that assumed Skia color management.

Profile mode first. If a frame is still long, the split is still UI vs raster — Impeller moved work off the *shader compile* path, not off your `build()` method.
