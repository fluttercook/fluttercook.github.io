---
title: "Chỉ ship asset mà từng nền tảng cần"
description: "Flutter 3.41 cho phép pubspec khai báo platforms theo asset — APK nhỏ hơn khi loại file chỉ dành desktop."
seoDescription: "Flutter asset theo nền tảng pubspec platforms, giảm dung lượng APK, loại asset desktop khỏi build mobile."
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

Một danh sách `flutter:` assets từng khiến mọi nền tảng nhận mọi file. Từ 3.41 bạn lọc được:

![Sơ đồ: Platform-specific Assets](/blog/images/flutter-platform-specific-assets.svg)


```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

## Vì sao app đa nền tảng nên làm

- User mobile không nên tải PDF hướng dẫn desktop hay web worker.
- Metric dung lượng store và ma sát download cải thiện ngay.
- CI assert được ma trận asset theo nền tảng.

## Cách chia thực tế

| Loại asset | Nền tảng |
| --- | --- |
| Branding dùng chung | all |
| Web worker / helper wasm | web |
| Template in ấn độ phân giải cao | desktop |
| Nhạc notification iOS/Android | android, ios |

## Cạm bẫy

- `rootBundle.load` asset không tồn tại trên nền tảng sẽ throw — guard bằng platform check.
- Đây là lọc *đóng gói*, không phải theming runtime.
