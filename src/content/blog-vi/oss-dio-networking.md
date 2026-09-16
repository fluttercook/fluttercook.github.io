---
title: 'Dio: networking có thể ghép bằng interceptor'
description: 'Showcase dio trong kiến trúc Flutter thực tế: interceptor, hủy request,
  retry và ánh xạ lỗi có kiểu.'
seoDescription: 'Showcase dio trong kiến trúc Flutter thực tế: interceptor, hủy request,
  retry và ánh xạ lỗi có kiểu.'
keywords:
- dio
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
- Networking
sources:
- name: Dio on pub.dev
  url: https://pub.dev/packages/dio
- name: Dio repository
  url: https://github.com/cfug/dio
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Dio: networking có thể ghép bằng interceptor

`dio` đáng chú ý vì nó giải quyết interceptor, hủy request, retry và ánh xạ lỗi có kiểu. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final dio = Dio(BaseOptions(baseUrl: apiBaseUrl));

dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) {
    options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  },
  onError: (error, handler) {
    logApiFailure(error);
    handler.next(error);
  },
));
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Retry chỉ nên áp dụng cho thao tác idempotent hoặc có idempotency key.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
