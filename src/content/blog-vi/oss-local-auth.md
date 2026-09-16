---
title: 'local_auth: biometric là step-up, không phải nơi lưu password'
description: 'Showcase local_auth trong kiến trúc Flutter thực tế: hỗ trợ thiết bị,
  prompt biometric, credential fallback và UX lỗi.'
seoDescription: 'Showcase local_auth trong kiến trúc Flutter thực tế: hỗ trợ thiết
  bị, prompt biometric, credential fallback và UX lỗi.'
keywords:
- local_auth
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
- Security
sources:
- name: local_auth on pub.dev
  url: https://pub.dev/packages/local_auth
- name: Flutter local_auth plugin
  url: https://github.com/flutter/packages/tree/main/packages/local_auth
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# local_auth: biometric là step-up, không phải nơi lưu password

`local_auth` đáng chú ý vì nó giải quyết hỗ trợ thiết bị, prompt biometric, credential fallback và UX lỗi. Bài này trình bày cách đặt package vào đúng boundary của một ứng dụng Flutter production thay vì chỉ copy một snippet vào màn hình.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## Package này sở hữu phần nào?

- Giữ API của package ở một adapter hoặc feature boundary có tên rõ ràng.
- Đưa lifecycle, lỗi và trạng thái loading vào contract mà UI có thể kiểm thử.
- Chỉ expose capability cần thiết; đừng để toàn app phụ thuộc vào chi tiết triển khai.

## Snippet bắt đầu

```dart
final auth = LocalAuthentication();
final supported = await auth.isDeviceSupported();
if (supported) {
  final ok = await auth.authenticate(
    localizedReason: 'Unlock your saved account',
    options: const AuthenticationOptions(biometricOnly: false),
  );
  if (ok) unlock();
}
```

## Checklist trước khi ship

1. Đọc README và changelog của package đúng version đang pin.
2. Viết một test cho lifecycle, lỗi và hành vi khi app về background.
3. Kiểm tra Android, iOS, web hoặc desktop đúng platform mà app hỗ trợ.
4. Ghi lại owner, upgrade cadence và kế hoạch rollback trong repo.

## Pitfall hay gặp

Biometric thành công chỉ chứng minh người dùng hiện diện trên máy; thao tác nhạy cảm vẫn cần session/server check.

## Kết luận

Thư viện OSS tốt không thay thế kiến trúc. Nó giúp một boundary khó trở nên rõ ràng, có thể quan sát và dễ thay thế hơn.
