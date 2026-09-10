---
title: "Swift Package Manager là mặc định iOS/macOS — rời CocoaPods"
description: "Từ Flutter 3.44, SwiftPM thay CocoaPods cho build iOS/macOS mới. CLI migrate thế nào, plugin author cần ship gì, và cách opt-out tạm."
seoDescription: "Flutter Swift Package Manager mặc định 3.44: migrate từ CocoaPods, plugin Package.swift FlutterFramework, và cờ opt-out tạm."
keywords:
  - flutter swift package manager
  - flutter cocoa pods migration
  - swiftpm flutter default
  - flutter plugin Package.swift
  - disable swift package manager flutter
tags: ["Flutter", "iOS", "macOS", "SwiftPM", "CocoaPods"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "SwiftPM for app developers"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers"
  - name: "SwiftPM for plugin authors"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-plugin-authors"
  - name: "Goodbye CocoaPods post"
    url: "https://blog.flutter.dev/saying-goodbye-to-cocoapods-swift-package-manager-is-soon-the-default-in-flutter-645a92714a57"
related:
  - slug: "flutter-uiscene-ios-lifecycle"
    title: "UIScene iOS Lifecycle"
  - slug: "flutter-content-sized-views"
    title: "Content-sized Views"
category: "Deep Dive"
topic: "Platform"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📦"
draft: false
---

CocoaPods đang ở chế độ maintenance. Flutter 3.44 đặt **Swift Package Manager làm mặc định** cho dependency iOS và macOS. CLI migrate Xcode project ở lần `flutter run` / `flutter build` kế tiếp.

![Sơ đồ: Swift Package Manager Default](/blog/images/flutter-swift-package-manager-default.svg)


## App developer thấy gì

- Happy path không cần cài Ruby/CocoaPods.
- Add-to-App có `flutter build swift-package` để đóng gói module thành Swift Package.
- Plugin còn bắt buộc CocoaPods sẽ bị CLI cảnh báo và fallback tạm.

## Plugin author cần ship gì

1. Thêm `Package.swift`.
2. Depend `FlutterFramework` nếu đã migrate pilot 2024.
3. Nâng constraint Flutter tối thiểu lên **3.44** khi chuyển.

Plugin chưa migrate bị trừ điểm pub.dev và sẽ không resolve được nữa.

## Opt-out tạm

```yaml
# pubspec.yaml
flutter:
  enable-swift-package-manager: false
```

Hoặc `--no-enable-swift-package-manager` trên CLI. Opt-out sẽ bị gỡ; mở issue kèm Xcode project nếu SwiftPM làm hỏng tích hợp thật.

## Checklist trước khi xóa Podfile

- [ ] `flutter clean` rồi build iOS đầy đủ
- [ ] CI không còn cài CocoaPods cho app này
- [ ] Mọi plugin trong tree resolve bằng SwiftPM (hoặc đã thay)
- [ ] Code signing và entitlement vẫn đúng
