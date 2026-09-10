---
title: "Flutter view co theo nội dung trong native parent"
description: "Flutter 3.41 cho view nhúng size theo nội dung — then chốt khi Flutter nằm trong scrollable native."
seoDescription: "Flutter view size theo nội dung Add-to-App, isAutoResizable iOS, content_wrap Android FlutterView, nhúng Flutter vào scroll native."
keywords:
  - flutter content sized views
  - flutter add to app scroll
  - FlutterViewController isAutoResizable
  - content_wrap flutterview
  - embed flutter native scrollview
tags: ["Flutter", "AddToApp", "iOS", "Android"]
sources:
  - name: "What's new in Flutter 3.41"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"
  - name: "Add a Flutter screen — iOS"
    url: "https://docs.flutter.dev/add-to-app/ios/add-flutter-screen"
  - name: "Add a Flutter View — Android"
    url: "https://docs.flutter.dev/add-to-app/android/add-flutter-view"
related:
  - slug: "flutter-uiscene-ios-lifecycle"
    title: "UIScene iOS Lifecycle"
  - slug: "flutter-swift-package-manager-default"
    title: "Swift Package Manager Default"
category: "Deep Dive"
topic: "Add-to-App"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📐"
draft: false
---

Trước đây view Flutter nhúng cần size cố định từ native parent. Điều đó khiến Flutter bên trong `UIScrollView` hay `RecyclerView` rất đau.

![Sơ đồ: Content-sized Views](/blog/images/flutter-content-sized-views.svg)


## Bật content sizing

- **iOS:** `FlutterViewController.isAutoResizable = true`
- **Android:** đặt width/height của `FlutterView` là `content_wrap` và bật content sizing theo docs.

## Ràng buộc root widget

Root Flutter phải chịu được unbounded height (hoặc width). Tránh `ListView` top-level kỳ vọng viewport bị chặn; ưu tiên layout intrinsic-height hoặc shrink-wrapped.

## Cạm bẫy

- Animation giả định viewport cỡ phone có thể overflow trong cell list native.
- Đo jank: nhiều engine/view Flutter nhúng vẫn tốn memory.
- Đồng bộ keyboard inset từ phía native.
