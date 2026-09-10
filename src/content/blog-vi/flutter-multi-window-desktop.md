---
title: "API multi-window desktop: popup, dialog và windowHandle"
description: "API windowing experimental của Flutter lớn dần cùng Canonical: popup trên Linux/Windows, cửa sổ theo nội dung, truy cập native handle."
seoDescription: "Flutter API multi-window desktop, popup Linux Windows, windowHandle HWND NSWindow GtkWindow hợp tác Canonical."
keywords:
  - flutter multi window desktop
  - flutter popup window linux
  - windowHandle flutter
  - canonical flutter desktop
  - flutter dialog window
tags: ["Flutter", "Desktop", "MultiWindow", "Canonical"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "multiple_windows example"
    url: "https://github.com/flutter/flutter/tree/master/examples/multiple_windows"
related:
  - slug: "flutter-desktop-flavors"
    title: "Desktop Flavors"
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
category: "Deep Dive"
topic: "Desktop"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🪟"
draft: false
---

App desktop cần nhiều surface: context menu, palette công cụ, inspector tách rời. **API windowing experimental** của Flutter — được Canonical đẩy nhanh với vai trò Strategic Steward cho Flutter Desktop — là đường đi.

![Sơ đồ: Desktop Multi-window APIs](/blog/images/flutter-multi-window-desktop.svg)


## Đã landing từ 3.44 → 3.47

- Cửa sổ tooltip và dialog trên Linux/macOS/Windows.
- **Popup trên Linux và Windows** (macOS có sớm hơn).
- `showDialog` có thể tạo cửa sổ con thật trên nền tảng hỗ trợ windowing.
- Cửa sổ theo nội dung và `windowHandle` (`HWND` / `NSWindow` / `GtkWindow`) cho tích hợp native nâng cao.

## Khi nào dùng

| Nhu cầu | Hướng API |
| --- | --- |
| Context menu / palette | Popup window |
| Tool tách rời | Regular window + test multi-window |
| Docking native | `windowHandle` + code platform |

## Cảnh báo trạng thái

Các API này ở **main-channel / experimental**. Đừng ship multi-window production làm UX duy nhất khi chưa có fallback. Theo dõi example `multiple_windows` và file issue vào embedder.

## Mẹo thực tế

Thiết kế feature sao cho workflow *chính* vẫn chạy được single-window. Multi-window nên là gia tốc, không phải hard dependency, cho tới khi API graduate.
