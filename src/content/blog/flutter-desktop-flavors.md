---
title: "Product flavors on Windows and Linux in Flutter 3.47"
description: "Desktop joins Android/iOS with real flavors — including per-flavor assets in pubspec and --flavor build flags."
seoDescription: "Flutter desktop flavors Windows Linux 3.47, per-flavor assets pubspec, flutter build windows --flavor."
keywords:
  - flutter desktop flavors
  - flutter windows flavor
  - flutter linux flavor
  - flutter build --flavor desktop
  - per flavor assets flutter
tags: ["Flutter", "Desktop", "Flavors", "Build"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flavors guide"
    url: "https://docs.flutter.dev/deployment/flavors"
related:
  - slug: "flutter-platform-specific-assets"
    title: "Platform-specific Assets"
  - slug: "flutter-multi-window-desktop"
    title: "Desktop Multi-window APIs"
category: "Deep Dive"
topic: "Desktop"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🍨"
draft: false
---

Dev/staging/prod builds were a mobile-only story for a long time. Flutter 3.47 brings **flavors to Windows and Linux**.

![Diagram: Desktop Flavors](/blog/images/flutter-desktop-flavors.svg)


## pubspec assets per flavor

```yaml
flutter:
  assets:
    - path: assets/flavor_a/images
      flavors:
        - flavor_a
    - path: assets/flavor_b/images
      flavors:
        - flavor_b
```

## Build

```bash
flutter build windows --flavor flavor_a
flutter build linux --flavor flavor_a
```

## Why desktop teams care

- Separate app IDs and icons for internal vs store builds.
- Different API base URLs without string hacks in Dart.
- CI matrix can produce side-by-side installers.

## Pitfalls

- Pair flavors with `dart-define` or compile-time env — flavors alone do not inject secrets.
- Remember desktop packaging (MSIX, deb/rpm, AppImage) still has its own identity rules.
