---
title: 'image_picker: API nhỏ cho các nguồn media phức tạp'
description: 'Showcase image_picker trong kiến trúc Flutter thực tế: intent camera/gallery,
  khôi phục lost data, nén ảnh và permission.'
seoDescription: 'Showcase image_picker trong kiến trúc Flutter thực tế: intent camera/gallery,
  khôi phục lost data, nén ảnh và permission.'
keywords:
- image_picker
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
- Media
sources:
- name: image_picker on pub.dev
  url: https://pub.dev/packages/image_picker
- name: Flutter image_picker package
  url: https://github.com/flutter/packages/tree/main/packages/image_picker
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# image_picker: API nhỏ cho các nguồn media phức tạp

`image_picker` đáng chú ý vì nó giải quyết intent camera/gallery, khôi phục lost data, nén ảnh và permission. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final picker = ImagePicker();
final image = await picker.pickImage(
  source: ImageSource.gallery,
  maxWidth: 2000,
  imageQuality: 85,
);
if (image != null) upload(await image.readAsBytes());
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Xử lý activity recreation Android bằng retrieveLostData và kiểm tra size trước khi upload.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
