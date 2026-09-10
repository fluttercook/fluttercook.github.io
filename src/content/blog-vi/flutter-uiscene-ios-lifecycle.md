---
title: "UIScene lifecycle: yêu cầu khởi động iOS 27 mà app Flutter phải đạt"
description: "Xcode 27 / iOS 27 bắt buộc UIScene. Flutter migrate tự động đa số app; AppDelegate tùy chỉnh cần migrate tay."
seoDescription: "Flutter UIScene lifecycle iOS 27 Xcode 27, migrate AppDelegate, min iOS 15 Flutter 3.47, không UIScene sẽ không launch."
keywords:
  - flutter uiscene
  - flutter ios 27 lifecycle
  - flutter appdelegate migration
  - uiscenedelegate flutter
  - flutter min ios 15
tags: ["Flutter", "iOS", "UIScene", "Xcode"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "UIScene lifecycle guide"
    url: "https://docs.flutter.dev/release/breaking-changes/uiscene-lifecycle-ios"
  - name: "UISceneDelegate migration"
    url: "https://docs.flutter.dev/release/breaking-changes/uiscenedelegate"
related:
  - slug: "flutter-swift-package-manager-default"
    title: "Swift Package Manager Default"
  - slug: "flutter-content-sized-views"
    title: "Content-sized Views"
category: "Deep Dive"
topic: "iOS"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🍎"
draft: false
---

Lifecycle theo scene của Apple không còn tùy chọn với app build bằng SDK mới nhất. **iOS 27 / Xcode 27 sẽ không launch** app UIKit chưa dùng `UIScene`.

![Sơ đồ: UIScene iOS Lifecycle](/blog/images/flutter-uiscene-ios-lifecycle.svg)


## Flutter 3.47 đổi gì

- Nâng minimum: **iOS 15**, **macOS 12** (từ 13 / 10.15).
- CLI migrate `AppDelegate` thường tự động.
- Việc tay còn lại nếu bạn customize lifecycle hook hoặc plugin còn giả định model cũ.

## Checklist migrate

1. Update Xcode và Flutter về cặp được hỗ trợ.
2. Clean build và đọc output migrate của CLI.
3. Rà plugin có API chỉ UIApplicationDelegate.
4. Test cold start, background→foreground, dialog quyền.

## Cạm bẫy

- “Chạy được trên simulator” là chưa đủ — test device với SDK mới.
- Deep link và notification handler thường nằm trong lifecycle code; test lại.
