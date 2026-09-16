---
title: 'Pigeon: platform channel có kiểu sinh từ một schema'
description: 'Showcase pigeon trong kiến trúc Flutter thực tế: codegen Dart/native,
  contract API, task queue và versioning.'
seoDescription: 'Showcase pigeon trong kiến trúc Flutter thực tế: codegen Dart/native,
  contract API, task queue và versioning.'
keywords:
- pigeon
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
- name: pigeon on pub.dev
  url: https://pub.dev/packages/pigeon
- name: Pigeon repository
  url: https://github.com/flutter/packages/tree/main/packages/pigeon
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Pigeon: platform channel có kiểu sinh từ một schema

`pigeon` đáng chú ý vì nó giải quyết codegen Dart/native, contract API, task queue và versioning. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
@HostApi()
abstract class SecureBiometrics {
  bool isAvailable();
  @async
  bool authenticate(String reason);
}

// dart run pigeon --input pigeons/biometrics.dart
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Version schema như một API; thêm method breaking có thể làm lệch binary native đã phát hành.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
