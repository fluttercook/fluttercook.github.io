---
title: 'Drift: SQL có kiểu cho ứng dụng Flutter offline-first'
description: 'Showcase drift trong kiến trúc Flutter thực tế: table có kiểu, migration,
  query reactive và transaction.'
seoDescription: 'Showcase drift trong kiến trúc Flutter thực tế: table có kiểu, migration,
  query reactive và transaction.'
keywords:
- drift
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
- Database
sources:
- name: Drift on pub.dev
  url: https://pub.dev/packages/drift
- name: Drift documentation
  url: https://drift.simonbinder.eu/
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Drift: SQL có kiểu cho ứng dụng Flutter offline-first

`drift` đáng chú ý vì nó giải quyết table có kiểu, migration, query reactive và transaction. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
@DriftDatabase(tables: [Todos])
class AppDatabase extends _$AppDatabase {
  AppDatabase(super.e);
  @override
  int get schemaVersion => 1;

  Stream<List<Todo>> watchOpenTodos() =>
      (select(todos)..where((t) => t.done.equals(false))).watch();
}
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Migration là code production; hãy test schema cũ trước khi phát hành bản nâng cấp.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
