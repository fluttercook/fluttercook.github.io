---
title: Secure storage and biometrics for Flutter tokens — hướng dẫn Flutter
description: Keychain/Keystore, biometric gates, and token rotation.
seoDescription: Flutter secure storage biometrics keychain keystore, token rotation local auth. Practical guide for production
  Flutter teams.
keywords:
- flutter secure storage
- local_auth biometrics
- flutter keychain
- token security flutter
- biometric unlock flutter
- flutter
- dart
- mobile development
category: Security
topic: Security
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-11'
emoji: 🧭
tags:
- Flutter
- Security
sources:
- name: secure_storage
  url: https://pub.dev/packages/flutter_secure_storage
- name: Flutter documentation
  url: https://docs.flutter.dev/
- name: Dart documentation
  url: https://dart.dev/guides
related:
- slug: flutter-feature-flags-config
  title: Feature flags and remote config without a mess
- slug: flutter-codegen-freezed-json
  title: 'Codegen that pays for itself: freezed and json_serializable'
draft: false
---

Refresh tokens in SharedPreferences are a security incident waiting to happen. Bài này chuyển quan sát đó thành một mô hình nhỏ để bạn có thể kiểm thử, đo lường và giữ cho code dễ bảo trì khi app lớn lên.

## Vấn đề cốt lõi

Keychain/Keystore, biometric gates, and token rotation. Câu hỏi hữu ích không phải API hay pattern có đẹp riêng lẻ hay không, mà là state nằm ở đâu, boundary nào chịu trách nhiệm khi lỗi xảy ra, và người dùng phục hồi thế nào khi happy path biến mất.

![Sơ đồ kiến trúc Flutter cho Secure storage and biometrics for Flutter tokens](/blog/images/fluttercook-editorial-2026.svg)

## Mô hình thực tế

Use platform keystores and optional biometric unlock for sensitive vaults.

Hãy bắt đầu bằng một owner rõ ràng cho behavior. Widget chỉ nên render và phát intent; IO, persistence, permission và retry nên nằm sau một interface nhỏ. Nhờ vậy bạn có seam để fake trong test và một chỗ ghi lại các dữ kiện cần theo dõi ở production.

Trong app Flutter, boundary thường có dạng:

1. Widget phát intent như load, submit, refresh hoặc retry.
2. Controller hoặc use case validate intent rồi gọi boundary.
3. Boundary trả về data có kiểu hoặc failure có kiểu, không trả string chỉ dành cho log.
4. UI render tường minh loading, empty, success và failure.

Hình dạng này không phụ thuộc bạn dùng `setState`, Bloc, Riverpod hay state layer khác. Quyết định quan trọng là ownership, không phải tên package.

## Ví dụ tối thiểu

Thử nghiệm nhỏ nhất thường đủ để lộ trade-off:

```text
FlutterSecureStorage().write(key: 'refresh', value: token);
```

Đặt ví dụ sau một interface theo feature, rồi thêm một test cho success và một test cho failure. Nếu ví dụ cần global state mới chạy được thì boundary có thể đang đặt sai chỗ.

## Checklist trước khi ship

- Xác định lifecycle: ai bắt đầu, ai hủy, và cái gì sống qua restart?
- Đo kết quả người dùng thấy: frame time, bytes, latency, conversion hoặc thời gian hồi phục.
- Giữ code platform-specific ở edge và ghi rõ yêu cầu OS/SDK tối thiểu.
- Viết empty state và offline/error state trước khi chăm chút polish.
- Log id và timing, nhưng phải redact token, dữ liệu cá nhân và payload đầy đủ.
- Rollout có đường lui: feature flag, staged release hoặc fallback phía server.

## Cạm bẫy nên xử lý sớm

Biometrics can be disabled by policy — always have a passcode fallback. Lỗi thường gặp là demo chạy đúng nhưng cancellation, retry, permission, accessibility và hành vi khi upgrade lại bị bỏ ngỏ. Khi app có user thật, đó không còn là edge case. Hãy test ít nhất một thiết bị chậm, một request bị ngắt mạng và một process restart nếu chủ đề này ảnh hưởng lifecycle hoặc storage.

## Đánh giá kết quả

Ghi baseline trước khi sửa. So sánh cùng user journey trên cùng nhóm thiết bị, rồi xem cả median lẫn failure tệ nhất mà người dùng nhìn thấy. Một diff nhỏ có rollback rõ thường an toàn hơn rewrite toàn framework. Lưu quyết định và bằng chứng cạnh code để lần upgrade sau không phải tranh luận lại từ đầu.

Đọc thêm các chủ đề liên quan: [Feature flags and remote config without a mess](/vi/blog/flutter-feature-flags-config/) và [Codegen that pays for itself: freezed and json_serializable](/vi/blog/flutter-codegen-freezed-json/).
