---
title: 'url_launcher: platform intent với hợp đồng fallback'
description: 'Showcase url_launcher trong kiến trúc Flutter thực tế: canLaunchUrl,
  launch mode, web URL và handler không khả dụng.'
seoDescription: 'Showcase url_launcher trong kiến trúc Flutter thực tế: canLaunchUrl,
  launch mode, web URL và handler không khả dụng.'
keywords:
- url_launcher
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
- Platform
sources:
- name: url_launcher on pub.dev
  url: https://pub.dev/packages/url_launcher
- name: Flutter url_launcher package
  url: https://github.com/flutter/packages/tree/main/packages/url_launcher/url_launcher
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# url_launcher: platform intent với hợp đồng fallback

`url_launcher` đáng chú ý vì nó giải quyết canLaunchUrl, launch mode, web URL và handler không khả dụng. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final uri = Uri.parse('mailto:support@example.com');
if (await canLaunchUrl(uri)) {
  await launchUrl(uri, mode: LaunchMode.externalApplication);
} else {
  showUnsupportedAction();
}
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

canLaunch chỉ mang tính gợi ý; vẫn phải xử lý launch fail và khai báo query của platform.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
