---
title: "Content-sized Flutter views in native parents"
description: "Flutter 3.41 lets embedded views size to content — critical for Flutter inside native scrollables."
seoDescription: "Flutter content-sized views Add-to-App, isAutoResizable iOS, content_wrap Android FlutterView, embed Flutter in native scroll."
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

Historically an embedded Flutter view needed a fixed size from its native parent. That made Flutter-inside-`UIScrollView` or `RecyclerView` painful.

![Diagram: Content-sized Views](/blog/images/flutter-content-sized-views.svg)


## Enable content sizing

- **iOS:** `FlutterViewController.isAutoResizable = true`
- **Android:** set width/height of `FlutterView` to `content_wrap` and enable content sizing in the manifest/docs flow.

## Root widget constraints

Your Flutter root must tolerate unbounded height (or width). Avoid a top-level `ListView` that expects a bounded viewport; prefer intrinsic-height layouts or a single-column with shrink-wrapped content.

## Pitfalls

- Animations that assume a phone-sized viewport can overflow inside a native list cell.
- Measure jank: multiple embedded Flutter engines/views still cost memory.
- Coordinate with keyboard insets from the native side.
