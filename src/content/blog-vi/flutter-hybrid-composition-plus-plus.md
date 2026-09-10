---
title: "Hybrid Composition++: sửa platform view Android hết jank"
description: "Flutter 3.44 giới thiệu HCPP — compositing cấp OS qua Vulkan SurfaceControl cho WebView, map và native view Android."
seoDescription: "Flutter Hybrid Composition++ HCPP bật cờ, SurfaceControl Vulkan platform view, scroll mượt hơn và hỗ trợ SurfaceView."
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

Nhúng WebView hoặc Google Map từng là đánh đổi: Virtual Display (rét hình, input lạ) hoặc Hybrid Composition (CPU cao hơn). **Hybrid Composition++ (HCPP)** để Android tự compositing layer qua Vulkan hardware-buffer swapchain và `SurfaceControl` transaction, đồng bộ với frame Flutter.

![Sơ đồ: Hybrid Composition Plus Plus](/blog/images/flutter-hybrid-composition-plus-plus.svg)


## Bật HCPP

```xml
<meta-data
    android:name="io.flutter.embedding.android.EnableHcpp"
    android:value="true" />
```

Hoặc chạy `--enable-hcpp`. **Không có API Dart mới** — platform view hiện có được nâng cấp.

## Yêu cầu và giới hạn

- Bị chặn bởi API level và phần cứng; không phải máy nào cũng dùng được dù đã opt-in.
- Nội dung `SurfaceView` trở nên khả thi — mode cũ rất khó.
- Sẽ thành mặc định sau này — hãy validate luồng map/WebView sản phẩm ngay.

## Đo gì

1. FPS scroll bên trong `WebView`/map, không chỉ list Flutter quanh nó.
2. Độ chính xác chạm gần mép view nhúng.
3. Bàn phím show/hide đè lên platform view.

Nếu vẫn rét hình, kiểm tra cờ có trong manifest **đã build** (flavor có thể ghi đè) và máy không nằm dưới ngưỡng hỗ trợ.
