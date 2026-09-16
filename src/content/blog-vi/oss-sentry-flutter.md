---
title: 'Sentry Flutter: lỗi đi kèm context của release'
description: 'Showcase sentry_flutter trong kiến trúc Flutter thực tế: crash report,
  trace hiệu năng, breadcrumb và source map.'
seoDescription: 'Showcase sentry_flutter trong kiến trúc Flutter thực tế: crash report,
  trace hiệu năng, breadcrumb và source map.'
keywords:
- sentry_flutter
- Flutter open source
- Flutter library
- Flutter tutorial
category: Open Source
topic: Flutter OSS
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-16'
emoji: 🧩
tags:
- Flutter
- OpenSource
- Observability
sources:
- name: sentry_flutter on pub.dev
  url: https://pub.dev/packages/sentry_flutter
- name: Sentry Flutter docs
  url: https://docs.sentry.io/platforms/flutter/
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Sentry Flutter: lỗi đi kèm context của release

`sentry_flutter` đáng chú ý vì nó giải quyết crash report, trace hiệu năng, breadcrumb và source map. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
await SentryFlutter.init(
  (options) {
    options.dsn = const String.fromEnvironment('SENTRY_DSN');
    options.tracesSampleRate = 0.1;
    options.environment = const String.fromEnvironment('APP_ENV');
  },
  appRunner: () => runApp(const App()),
);
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Không gửi token, password hay nội dung người dùng thô vào event; DSN không phải secret.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
