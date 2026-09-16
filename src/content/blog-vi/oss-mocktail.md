---
title: 'Mocktail: mock Dart dễ đọc mà không cần file generated'
description: 'Showcase mocktail trong kiến trúc Flutter thực tế: fake, stub, verify,
  fallback value và ranh giới test.'
seoDescription: 'Showcase mocktail trong kiến trúc Flutter thực tế: fake, stub, verify,
  fallback value và ranh giới test.'
keywords:
- mocktail
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
- name: mocktail on pub.dev
  url: https://pub.dev/packages/mocktail
- name: Mocktail repository
  url: https://github.com/felangel/mocktail
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Mocktail: mock Dart dễ đọc mà không cần file generated

`mocktail` đáng chú ý vì nó giải quyết fake, stub, verify, fallback value và ranh giới test. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
class MockUserApi extends Mock implements UserApi {}

final api = MockUserApi();
when(() => api.fetchUser('42')).thenAnswer((_) async => user);
final result = await repository.load('42');
verify(() => api.fetchUser('42')).called(1);
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Mock ở boundary do bạn sở hữu; mock mọi class nội bộ làm refactor đắt đỏ.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
