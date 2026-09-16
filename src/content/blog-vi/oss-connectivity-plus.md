---
title: 'connectivity_plus: loại mạng không đồng nghĩa có internet'
description: 'Showcase connectivity_plus trong kiến trúc Flutter thực tế: stream kết
  nối, UX offline, kiểm tra reachability và khác biệt platform.'
seoDescription: 'Showcase connectivity_plus trong kiến trúc Flutter thực tế: stream
  kết nối, UX offline, kiểm tra reachability và khác biệt platform.'
keywords:
- connectivity_plus
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
- Offline
sources:
- name: connectivity_plus on pub.dev
  url: https://pub.dev/packages/connectivity_plus
- name: connectivity_plus repository
  url: https://github.com/fluttercommunity/plus_plugins/tree/main/packages/connectivity_plus
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# connectivity_plus: loại mạng không đồng nghĩa có internet

`connectivity_plus` đáng chú ý vì nó giải quyết stream kết nối, UX offline, kiểm tra reachability và khác biệt platform. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final subscription = Connectivity().onConnectivityChanged.listen((types) {
  final hasTransport = types.any((type) =>
      type == ConnectivityResult.wifi || type == ConnectivityResult.mobile);
  banner.show(hasTransport ? 'Online' : 'Offline');
});

// Cancel subscription in dispose().
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Đừng xem connectivity type là bằng chứng API sẽ chạy; hãy xác nhận bằng request hoặc health check.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
