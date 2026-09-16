---
title: 'Patrol: integration test có thể đi ra ngoài sandbox Flutter'
description: 'Showcase patrol trong kiến trúc Flutter thực tế: permission native,
  notification, deep link và tự động hóa thiết bị.'
seoDescription: 'Showcase patrol trong kiến trúc Flutter thực tế: permission native,
  notification, deep link và tự động hóa thiết bị.'
keywords:
- patrol
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
- Testing
sources:
- name: Patrol on pub.dev
  url: https://pub.dev/packages/patrol
- name: Patrol repository
  url: https://github.com/leancodepl/patrol
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Patrol: integration test có thể đi ra ngoài sandbox Flutter

`patrol` đáng chú ý vì nó giải quyết permission native, notification, deep link và tự động hóa thiết bị. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
patrolTest('camera permission flow', ($) async {
  await $.native.grantPermissionWhenInUse();
  await $.pumpWidgetAndSettle(const CameraApp());
  await $(#takePhoto).tap();
  expect(find.byType(PhotoPreview), findsOneWidget);
});
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Native setup phải deterministic; test dựa vào permission đã cấp từ trước sẽ flaky.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
