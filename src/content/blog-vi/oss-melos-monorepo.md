---
title: 'Melos: biến Flutter monorepo thành ranh giới sản phẩm'
description: 'Showcase melos trong kiến trúc Flutter thực tế: script workspace, package
  graph, test chọn lọc và release.'
seoDescription: 'Showcase melos trong kiến trúc Flutter thực tế: script workspace,
  package graph, test chọn lọc và release.'
keywords:
- melos
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
- Monorepo
sources:
- name: melos on pub.dev
  url: https://pub.dev/packages/melos
- name: Melos documentation
  url: https://melos.invertase.dev/
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Melos: biến Flutter monorepo thành ranh giới sản phẩm

`melos` đáng chú ý vì nó giải quyết script workspace, package graph, test chọn lọc và release. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
name: flutter_workspace
packages:
  - apps/**
  - packages/**

scripts:
  analyze: melos exec -- flutter analyze
  test: melos exec --fail-fast -- flutter test
  changed: melos exec --since=main -- flutter test
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Monorepo không có ownership và luật dependency chỉ là folder lớn hơn; hãy enforce bằng CI.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
