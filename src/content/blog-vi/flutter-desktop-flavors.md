---
title: "Product flavor trên Windows và Linux trong Flutter 3.47"
description: "Desktop bắt kịp Android/iOS với flavor thật — gồm asset theo flavor trong pubspec và cờ build --flavor."
seoDescription: "Flutter flavor desktop Windows Linux 3.47, asset theo flavor pubspec, flutter build windows --flavor."
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

Build dev/staging/prod từng là chuyện riêng mobile. Flutter 3.47 mang **flavor lên Windows và Linux**.

![Sơ đồ: Desktop Flavors](/blog/images/flutter-desktop-flavors.svg)


## Asset theo flavor trong pubspec

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

## Vì sao team desktop quan tâm

- App ID và icon tách biệt cho bản internal vs store.
- API base URL khác nhau không cần hack string trong Dart.
- CI matrix sinh được installer cạnh nhau.

## Cạm bẫy

- Ghép flavor với `dart-define` hoặc env compile-time — flavor tự nó không inject secret.
- Packaging desktop (MSIX, deb/rpm, AppImage) vẫn có luật identity riêng.
