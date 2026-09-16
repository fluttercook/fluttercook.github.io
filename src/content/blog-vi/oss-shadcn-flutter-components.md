---
title: 'shadcn_flutter: UI primitive có thể ghép cho Flutter'
description: 'Showcase shadcn_flutter trong kiến trúc Flutter thực tế: primitive ít
  áp đặt style, phong cách New York, Material interop và theme.'
seoDescription: 'Showcase shadcn_flutter trong kiến trúc Flutter thực tế: primitive
  ít áp đặt style, phong cách New York, Material interop và theme.'
keywords:
- shadcn_flutter
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
- UI
sources:
- name: shadcn_flutter on pub.dev
  url: https://pub.dev/packages/shadcn_flutter
- name: shadcn_flutter repository
  url: https://github.com/sunarya-thito/shadcn_flutter
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# shadcn_flutter: UI primitive có thể ghép cho Flutter

`shadcn_flutter` đáng chú ý vì nó giải quyết primitive ít áp đặt style, phong cách New York, Material interop và theme. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
runApp(
  ShadcnApp(
    theme: ThemeData(colorScheme: ColorSchemes.lightZinc()),
    home: Scaffold(
      body: Center(
        child: PrimaryButton(child: const Text('Continue')),
      ),
    ),
  ),
);
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Hãy xác định Material dừng ở đâu và shadcn bắt đầu ở đâu; màn hình trộn cần một spacing system rõ ràng.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
