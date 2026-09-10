---
title: "Impeller thành renderer desktop mặc định — thực sự đổi gì"
description: "Flutter 3.47 bật Impeller mặc định trên macOS, Windows, Linux. Jank shader biến mất; chữ SDF sắc hơn; opt-out Skia chỉ là tạm thời."
seoDescription: "Flutter 3.47 Impeller mặc định desktop: Metal và Vulkan, chữ SDF, cách opt-out trên macOS Windows Linux và ghi chú migrate."
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

Impeller mặc định trên mobile đã có từ trước. Flutter 3.47 hoàn tất trên **macOS, Windows và Linux**. App desktop giờ nhắm Metal (macOS) và Vulkan (Windows/Linux) với tập shader cố định, compile lúc build engine.

![Sơ đồ: Impeller Default on Desktop](/blog/images/flutter-impeller-default-desktop.svg)


## Bạn được gì

- **Hết jank compile shader** khi animation chạy lần đầu.
- **Chữ SDF** — glyph sắc hơn trên màn desktop mật độ pixel thấp hơn.
- **Wide Gamut Color mặc định trên macOS** khi phần cứng hỗ trợ.

## Opt-out Skia tạm thời

| Nền tảng | Cách tắt |
| --- | --- |
| macOS | `FLTEnableImpeller=false` trong `Info.plist` |
| Windows | `project.set_impeller_switch(flutter::ImpellerSwitch::Disabled)` trong `main.cpp` |
| Linux | `fl_dart_project_set_enable_impeller(project, FALSE)` trong `my_application.cc` |

Hãy file bug. Fallback sẽ bị gỡ.

## Nên test lại

1. `FragmentShader` tùy chỉnh và effect nặng `saveLayer`.
2. Platform view / external texture.
3. Luồng print/export từng giả định color management của Skia.

Chạy profile mode trước. Frame vẫn dài thì vẫn là UI vs raster — Impeller chỉ lấy việc ở nhánh *compile shader*, không lấy việc trong `build()` của bạn.
