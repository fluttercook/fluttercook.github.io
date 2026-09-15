---
title: 'Wasm deferred loading: split Flutter web for first paint — hướng dẫn Flutter'
description: Opt into --wasm and --enable-wasm-deferred-loading for smaller boot bundles.
seoDescription: Flutter web Wasm deferred loading, package:web migration, flutter build web --wasm enable-wasm-deferred-loading.
  Practical guide for production Flutter teams.
keywords:
- flutter wasm
- deferred loading flutter web
- dart2wasm
- package:web migration
- flutter web first paint
- flutter
- dart
- mobile development
category: Web
topic: Web
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-11'
emoji: 🧭
tags:
- Flutter
- Web
- Wasm
sources:
- name: WebAssembly docs
  url: https://docs.flutter.dev/platform-integration/web/wasm
- name: Flutter documentation
  url: https://docs.flutter.dev/
- name: Dart documentation
  url: https://dart.dev/guides
related:
- slug: flutter-platform-assets-reduce-apk
  title: Ship only the assets each platform needs
- slug: flutter-uiscene-ios-27-checklist
  title: 'UIScene lifecycle: the iOS 27 launch gate for Flutter apps'
draft: false
---

Wasm unlocks near-native graphics and a new packaging discipline. Bài này chuyển quan sát đó thành một mô hình nhỏ để bạn có thể kiểm thử, đo lường và giữ cho code dễ bảo trì khi app lớn lên.

## Vấn đề cốt lõi

Opt into --wasm and --enable-wasm-deferred-loading for smaller boot bundles. Câu hỏi hữu ích không phải API hay pattern có đẹp riêng lẻ hay không, mà là state nằm ở đâu, boundary nào chịu trách nhiệm khi lỗi xảy ra, và người dùng phục hồi thế nào khi happy path biến mất.

![Sơ đồ kiến trúc Flutter cho Wasm deferred loading: split Flutter web for first paint](/blog/images/fluttercook-editorial-2026.svg)

## Mô hình thực tế

Keep login/shell in the main module; defer admin and heavy editors.

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
flutter build web --release --wasm --enable-wasm-deferred-loading
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

Migrate off dart:html. Deferred libraries must not be required on first frame. Lỗi thường gặp là demo chạy đúng nhưng cancellation, retry, permission, accessibility và hành vi khi upgrade lại bị bỏ ngỏ. Khi app có user thật, đó không còn là edge case. Hãy test ít nhất một thiết bị chậm, một request bị ngắt mạng và một process restart nếu chủ đề này ảnh hưởng lifecycle hoặc storage.

## Đánh giá kết quả

Ghi baseline trước khi sửa. So sánh cùng user journey trên cùng nhóm thiết bị, rồi xem cả median lẫn failure tệ nhất mà người dùng nhìn thấy. Một diff nhỏ có rollback rõ thường an toàn hơn rewrite toàn framework. Lưu quyết định và bằng chứng cạnh code để lần upgrade sau không phải tranh luận lại từ đầu.

Đọc thêm các chủ đề liên quan: [Ship only the assets each platform needs](/vi/blog/flutter-platform-assets-reduce-apk/) và [UIScene lifecycle: the iOS 27 launch gate for Flutter apps](/vi/blog/flutter-uiscene-ios-27-checklist/).
