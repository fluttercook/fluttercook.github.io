---
title: 'camera: pipeline chụp thật, không chỉ là preview'
description: 'Showcase camera trong kiến trúc Flutter thực tế: lifecycle controller,
  image stream, permission và orientation.'
seoDescription: 'Showcase camera trong kiến trúc Flutter thực tế: lifecycle controller,
  image stream, permission và orientation.'
keywords:
- camera
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
- Camera
sources:
- name: camera on pub.dev
  url: https://pub.dev/packages/camera
- name: Flutter camera package
  url: https://github.com/flutter/packages/tree/main/packages/camera
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# camera: pipeline chụp thật, không chỉ là preview

`camera` đáng chú ý vì nó giải quyết lifecycle controller, image stream, permission và orientation. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final cameras = await availableCameras();
final controller = CameraController(
  cameras.first,
  ResolutionPreset.high,
  enableAudio: false,
);
await controller.initialize();
final file = await controller.takePicture();
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Gắn capture flow với lifecycle và test xoay màn hình, background, cùng permission bị từ chối.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
