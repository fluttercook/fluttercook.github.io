---
title: "Ship only the assets each platform needs"
description: "Flutter 3.41 lets pubspec declare platforms per asset — smaller APKs by excluding desktop-only files."
seoDescription: "Flutter platform-specific assets pubspec platforms key, reduce APK size, exclude desktop assets from mobile builds."
keywords:
  - flutter platform specific assets
  - pubspec platforms assets
  - reduce flutter apk size
  - flutter asset optimization
  - flutter web_worker assets
tags: ["Flutter", "Assets", "AppSize", "pubspec"]
sources:
  - name: "What's new in Flutter 3.41"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"
  - name: "Assets and images"
    url: "https://docs.flutter.dev/ui/assets/assets-and-images"
related:
  - slug: "flutter-desktop-flavors"
    title: "Desktop Flavors"
  - slug: "flutter-app-size-reduction"
    title: "flutter-app-size-reduction"
category: "Deep Dive"
topic: "Performance"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📁"
draft: false
---

One `flutter:` assets list used to mean every platform received every file. From 3.41 you can filter:

![Diagram: Platform-specific Assets](/blog/images/flutter-platform-specific-assets.svg)


```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

## Why this is not optional for multi-platform apps

- Mobile users should not download desktop help PDFs or web workers.
- Store size metrics and download friction improve immediately.
- CI can assert platform asset matrices in tests.

## Practical split

| Asset type | Platforms |
| --- | --- |
| Shared branding | all |
| Web workers / wasm helpers | web |
| High-res print templates | desktop |
| iOS/Android notification sounds | android, ios |

## Pitfalls

- Conditional `rootBundle.load` of a missing platform asset throws — guard with a platform check.
- This is *packaging* filtering, not runtime theming.
