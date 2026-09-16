---
title: 'go_router: Điều hướng Flutter lấy URL làm trung tâm'
description: 'Showcase go_router trong kiến trúc Flutter thực tế: routing khai báo,
  deep link, redirect và ShellRoute.'
seoDescription: 'Showcase go_router trong kiến trúc Flutter thực tế: routing khai
  báo, deep link, redirect và ShellRoute.'
keywords:
- go_router
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
- Routing
sources:
- name: go_router on pub.dev
  url: https://pub.dev/packages/go_router
- name: go_router repository
  url: https://github.com/flutter/packages/tree/main/packages/go_router
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# go_router: Điều hướng Flutter lấy URL làm trung tâm

`go_router` đáng chú ý vì nó giải quyết routing khai báo, deep link, redirect và ShellRoute. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final router = GoRouter(
  redirect: (context, state) => isSignedIn || state.uri.path == '/login'
      ? null
      : '/login',
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomePage()),
    GoRoute(path: '/orders/:id', builder: (_, state) =>
        OrderPage(id: state.pathParameters['id']!)),
  ],
);
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Đừng giấu redirect xác thực trong widget; hãy đặt nó ở ranh giới route.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
