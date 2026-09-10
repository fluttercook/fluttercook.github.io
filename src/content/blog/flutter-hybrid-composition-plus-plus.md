---
title: "Hybrid Composition++: fixing Android platform views without the jank"
description: "Flutter 3.44 introduces HCPP — OS-level compositing via Vulkan SurfaceControl for WebView, maps, and other native Android views."
seoDescription: "Flutter Hybrid Composition++ HCPP enable flag, SurfaceControl Vulkan platform views, better scrolling and SurfaceView support."
keywords:
  - flutter hybrid composition++
  - flutter HCPP enable
  - flutter platform views android
  - EnableHcpp
  - flutter surfaceview webview
tags: ["Flutter", "Android", "PlatformViews", "Vulkan", "Performance"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "Platform views docs"
    url: "https://docs.flutter.dev/platform-integration/android/platform-views"
related:
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
  - slug: "flutter-content-sized-views"
    title: "Content-sized Views"
category: "Deep Dive"
topic: "Android"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🖼️"
draft: false
---

Embedding a WebView or Google Map used to force a tradeoff: Virtual Display (tearing, input quirks) or Hybrid Composition (higher CPU). **Hybrid Composition++ (HCPP)** lets Android own layer compositing through Vulkan hardware-buffer swapchains and `SurfaceControl` transactions, synchronized with the Flutter frame.

![Diagram: Hybrid Composition Plus Plus](/blog/images/flutter-hybrid-composition-plus-plus.svg)


## Enable HCPP

```xml
<meta-data
    android:name="io.flutter.embedding.android.EnableHcpp"
    android:value="true" />
```

Or run with `--enable-hcpp`. There is **no new Dart API** — existing platform views upgrade.

## Requirements and limits

- API level and hardware support gates apply; not every device can use HCPP even when opted in.
- `SurfaceView`-based content becomes realistic, which older modes struggled with.
- Expect this to become the default rendering mode later — validate your maps/WebView product flows now.

## What to measure

1. Scroll FPS inside a `WebView` or map, not only the Flutter list around it.
2. Touch accuracy near the edges of the embedded view.
3. Keyboard show/hide over the platform view.

If you still see tearing, confirm the flag is applied in the **built** manifest (flavors can overwrite it) and that you are not on a device below the support floor.
