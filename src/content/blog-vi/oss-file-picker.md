---
title: 'file_picker: một user intent trên sáu platform'
description: 'Showcase file_picker trong kiến trúc Flutter thực tế: filter, chọn nhiều
  file, bytes và path theo platform.'
seoDescription: 'Showcase file_picker trong kiến trúc Flutter thực tế: filter, chọn
  nhiều file, bytes và path theo platform.'
keywords:
- file_picker
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
- Files
sources:
- name: file_picker on pub.dev
  url: https://pub.dev/packages/file_picker
- name: file_picker repository
  url: https://github.com/miguelpruivo/flutter_file_picker
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# file_picker: một user intent trên sáu platform

`file_picker` đáng chú ý vì nó giải quyết filter, chọn nhiều file, bytes và path theo platform. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final result = await FilePicker.platform.pickFiles(
  allowMultiple: true,
  type: FileType.custom,
  allowedExtensions: ['pdf', 'png'],
);
for (final file in result?.files ?? <PlatformFile>[]) {
  upload(file.name, file.bytes, file.path);
}
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Trên web và mobile, filesystem path có thể không tồn tại; API nên nhận bytes hoặc stream.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
