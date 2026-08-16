---
title: "Impeller is now the default on macOS, Windows and Linux"
description: "Flutter 3.47 makes Impeller the default renderer on all three desktop platforms. Here is what changes, which backend runs where, how to opt out, and why you should not plan on it."
seoDescription: "Flutter Impeller desktop guide: Metal on macOS, Vulkan on Windows and Linux, build-time shader compilation, wide gamut color, and the exact opt-out flags per platform."
keywords: ["flutter impeller desktop", "impeller vs skia", "flutter shader jank", "FLTEnableImpeller", "flutter vulkan windows", "flutter 3.47 renderer"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "⚡"
tags: ["Flutter 3.47", "Flutter", "Impeller", "Desktop", "Performance"]
sources:
  - name: "Impeller rendering engine — flutter.dev docs"
    url: "https://docs.flutter.dev/perf/impeller"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Impeller README — flutter/flutter engine"
    url: "https://github.com/flutter/flutter/blob/main/engine/src/flutter/impeller/README.md"
  - name: "Flutter Q2 2026 survey results"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Impeller has been the only renderer on iOS for years and the default on Android API 29+ for a while. Flutter 3.47 finishes the job: **Impeller is now the default on macOS, Windows and Linux**. Only Flutter Web still runs on Skia.

If you ship desktop apps, this is the change in 3.47 most likely to alter how your app actually looks and feels — and the one most likely to surface a rendering bug you have never seen before.

## The problem Impeller was built to solve

Skia compiles shaders **at runtime**, on demand, the first time a particular drawing operation appears. That is why a Flutter app could stutter the first time you opened a specific screen, ran a specific animation, or applied a specific blur — and then run perfectly forever after. It was not your code. It was the renderer compiling a program mid-frame.

Impeller compiles a **smaller, simpler set of shaders offline, at engine build time**. Pipeline state objects are built upfront rather than per frame. Caching is explicit and engine-controlled rather than implicit. The result is not necessarily a higher peak frame rate — it is *predictable* frame timing, which is what users actually perceive as smoothness.

The design goals are worth naming because they explain the trade-offs:

- **Predictable performance** — everything compiled offline
- **Instrumentable** — graphics resources are tagged, and animations can be captured and persisted without perturbing frame times
- **Portable** — shaders authored once, converted per backend
- **Modern APIs** — uses Metal and Vulkan features without requiring them
- **Concurrent** — a single frame's work is spread across threads

## Which backend runs where

| Platform | Status | Backend |
| --- | --- | --- |
| iOS | Default, and the only option | Metal |
| Android | Default on API 29+ | Vulkan, OpenGL fallback below 29 |
| **macOS** | **Default from 3.47** | Metal |
| **Linux** | **Default from 3.47** | Vulkan |
| **Windows** | **Default from 3.47** | Vulkan |
| Web | Not available | Skia |

Vulkan on Windows and Linux is the line to read twice. Your users' driver situation is now part of your rendering stack in a way it was not before, and that variability is exactly why you should test on real hardware rather than one developer machine.

## Wide gamut color on macOS

Alongside the renderer switch, **wide gamut color is enabled by default on macOS**. On a P3 display, saturated colors will render more saturated than they did under the previous default. This is correct behaviour, but it is a visible change: if your brand colors were tuned by eye against an sRGB-clamped render, they will look different. Check your palette against design before assuming it is a bug.

## How to opt out, per platform

The escape hatches exist, and the release notes are explicit that **fallback options will be removed in a future release**. Use them to unblock a shipping deadline and to file a bug — not as a long-term configuration.

For debugging on any desktop platform:

```bash
flutter run --no-enable-impeller
```

For release builds, macOS — in `Info.plist`, under the top-level `<dict>`:

```xml
<key>FLTEnableImpeller</key>
<false />
```

For release builds, Linux — in `linux/runner/my_application.cc`:

```c
g_autoptr(FlDartProject) project = fl_dart_project_new();
fl_dart_project_set_enable_impeller(project, FALSE);
```

For release builds, Windows — in `windows\runner\main.cpp`:

```cpp
flutter::DartProject project(L"data");
project.set_impeller_switch(flutter::ImpellerSwitch::Disabled);
```

On Android the equivalent is a manifest entry (`io.flutter.embedding.android.EnableImpeller` set to `false`). On iOS there is no opt-out at all — which is a preview of where desktop is heading.

## What to actually re-test

Renderer swaps surface issues in a predictable set of places. Prioritise:

- **Blurs and shadows** — `BackdropFilter`, `ImageFilter.blur`, elevation shadows. Historically the highest-variance area between renderers.
- **Custom painters and shaders** — anything using `CustomPainter`, `FragmentProgram`, or blend modes beyond `srcOver`.
- **Text rendering at small sizes** — subpixel positioning and hinting differ.
- **Colors on P3 displays** — see wide gamut above.
- **Clipping and anti-aliasing edges** — especially nested clips with rounded corners.
- **Startup on low-end GPUs** — the Vulkan path on Windows and Linux is the new variable.

The Q2 2026 survey puts Windows satisfaction at **74%** and Linux at **73%** — the two lowest platform scores after Cupertino. Desktop is where Flutter has the most ground to make up, which cuts both ways: this release is a real investment in those platforms, and it is also the area with the thinnest prior testing.

## Filing a useful bug

If you find a regression, the Flutter team asks for a specific bundle, and reports missing it tend to stall:

1. **Prefix the issue title with `[Impeller]`.**
2. Include **device specifications, including the exact chip and GPU driver version**.
3. Attach **screenshots or a screen recording**, ideally side by side with `--no-enable-impeller`.
4. Attach a **zipped performance trace export**.
5. State the **Flutter version and channel** from `flutter --version`.

The side-by-side comparison is the highest-value item. It converts "this looks wrong" into a reproducible rendering difference.

## Your upgrade checklist

1. **Build your desktop targets on 3.47** before touching anything else.
2. **Run your visual regression suite**, or if you do not have one, walk your five most complex screens manually.
3. **Compare against `--no-enable-impeller`** for anything that looks off, so you know whether the renderer is actually the cause.
4. **Test on at least one low-end Windows GPU** and one Linux distribution you do not develop on.
5. **Re-check brand colors on a P3 display** if you ship on macOS.
6. **File `[Impeller]`-prefixed bugs now**, while the fallback still exists.
7. **Do not ship the opt-out permanently.** Track it as technical debt with a removal date.

## The bottom line

Impeller on desktop is the right change and a slightly risky one. The upside is structural: shader jank stops being a category of bug you have to chase, and frame timing becomes predictable. The cost is a one-time re-verification pass over your visual layer, and a new dependency on Vulkan driver quality on Windows and Linux. Do that pass now, while `--no-enable-impeller` still exists to tell you whether the renderer is at fault — because it will not exist forever.
