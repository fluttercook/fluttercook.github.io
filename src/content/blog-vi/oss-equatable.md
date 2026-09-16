---
title: 'Equatable: value semantics cho state object Dart'
description: 'Showcase equatable trong kiến trúc Flutter thực tế: equality, props,
  sealed state và kiểm tra rebuild dễ đoán.'
seoDescription: 'Showcase equatable trong kiến trúc Flutter thực tế: equality, props,
  sealed state và kiểm tra rebuild dễ đoán.'
keywords:
- equatable
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
- Dart
sources:
- name: equatable on pub.dev
  url: https://pub.dev/packages/equatable
- name: Equatable repository
  url: https://github.com/felangel/equatable
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Equatable: value semantics cho state object Dart

`equatable` đáng chú ý vì nó giải quyết equality, props, sealed state và kiểm tra rebuild dễ đoán. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
class UserLoaded extends Equatable {
  const UserLoaded(this.user);
  final User user;
  @override
  List<Object?> get props => [user.id, user.updatedAt];
}
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Đưa mọi field ảnh hưởng UI vào props; thiếu field sẽ tạo widget cũ và test khó hiểu.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
