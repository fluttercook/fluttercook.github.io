---
title: 'Freezed: model bất biến và union an toàn hơn'
description: 'Showcase freezed trong kiến trúc Flutter thực tế: data class bất biến,
  JSON union, copyWith và state UI exhaustive.'
seoDescription: 'Showcase freezed trong kiến trúc Flutter thực tế: data class bất
  biến, JSON union, copyWith và state UI exhaustive.'
keywords:
- freezed
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
- Codegen
sources:
- name: freezed on pub.dev
  url: https://pub.dev/packages/freezed
- name: Freezed repository
  url: https://github.com/rrousselGit/freezed
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Freezed: model bất biến và union an toàn hơn

`freezed` đáng chú ý vì nó giải quyết data class bất biến, JSON union, copyWith và state UI exhaustive. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
@freezed
sealed class LoadState<T> with _$LoadState<T> {
  const factory LoadState.idle() = Idle<T>;
  const factory LoadState.loading() = Loading<T>;
  const factory LoadState.data(T value) = Data<T>;
  const factory LoadState.failure(Object error) = Failure<T>;
}
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Chỉ commit file generated khi policy repo yêu cầu; nếu không, hãy chạy codegen trong CI.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
