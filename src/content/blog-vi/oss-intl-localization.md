---
title: 'intl: format data theo locale một cách có chủ đích'
description: 'Showcase intl trong kiến trúc Flutter thực tế: date, number, plural,
  khởi tạo locale và format có thể test.'
seoDescription: 'Showcase intl trong kiến trúc Flutter thực tế: date, number, plural,
  khởi tạo locale và format có thể test.'
keywords:
- intl
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
- Localization
sources:
- name: intl on pub.dev
  url: https://pub.dev/packages/intl
- name: Dart intl package
  url: https://github.com/dart-lang/i18n/tree/main/pkgs/intl
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# intl: format data theo locale một cách có chủ đích

`intl` đáng chú ý vì nó giải quyết date, number, plural, khởi tạo locale và format có thể test. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final amount = NumberFormat.currency(
  locale: 'vi_VN',
  symbol: '₫',
).format(1250000);
final date = DateFormat.yMMMMd('en_US').format(order.createdAt);
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Đừng nối chuỗi dịch với number/date; dùng ICU message và formatter theo locale.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
