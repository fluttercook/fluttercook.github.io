---
title: 'build_runner: biến code generation thành build step deterministic'
description: 'Showcase build_runner trong kiến trúc Flutter thực tế: watch mode, delete-conflicting-outputs,
  CI và ownership file generated.'
seoDescription: 'Showcase build_runner trong kiến trúc Flutter thực tế: watch mode,
  delete-conflicting-outputs, CI và ownership file generated.'
keywords:
- build_runner
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
- name: build_runner on pub.dev
  url: https://pub.dev/packages/build_runner
- name: build repository
  url: https://github.com/dart-lang/build
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# build_runner: biến code generation thành build step deterministic

`build_runner` đáng chú ý vì nó giải quyết watch mode, delete-conflicting-outputs, CI và ownership file generated. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
dart run build_runner build --delete-conflicting-outputs
dart run build_runner watch --delete-conflicting-outputs
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Không sửa file generated bằng tay; hãy sửa annotation hoặc cấu hình builder.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
