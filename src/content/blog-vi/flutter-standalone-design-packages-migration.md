---
title: Migrating to standalone material_ui and cupertino_ui in Flutter 3.47 — hướng dẫn Flutter
description: How to move off SDK-bundled Material/Cupertino with dart fix and the compatibility bridge.
seoDescription: 'Flutter 3.47 material_ui cupertino_ui migration: dart fix --code=migrate_design_widgets, MaterialUiCompatibilityBridge,
  weekly design releases.'
keywords:
- flutter material_ui migration
- cupertino_ui package
- dart fix migrate_design_widgets
- MaterialUiCompatibilityBridge
- flutter 3.47 material
- flutter
- dart
- mobile development
category: Deep Dive
topic: Framework
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-11'
emoji: 🧭
tags:
- Flutter
- Material
- Migration
sources:
- name: What's new in Flutter 3.47
  url: https://flutter.dev/blog/whats-new-in-flutter-3-47
- name: material_ui
  url: https://pub.dev/packages/material_ui
- name: Flutter documentation
  url: https://docs.flutter.dev/
- name: Dart documentation
  url: https://dart.dev/guides
related:
- slug: flutter-impeller-desktop-sdf-text
  title: 'Impeller on desktop: SDF text and Metal/Vulkan defaults'
- slug: flutter-swiftpm-plugin-migration-checklist
  title: Swift Package Manager plugin migration checklist for Flutter
draft: false
---

Flutter 3.47 ships opt-in standalone design packages at 1.0. Design updates no longer wait on the quarterly SDK train. Bài này chuyển quan sát đó thành một mô hình nhỏ để bạn có thể kiểm thử, đo lường và giữ cho code dễ bảo trì khi app lớn lên.

## Vấn đề cốt lõi

How to move off SDK-bundled Material/Cupertino with dart fix and the compatibility bridge. Câu hỏi hữu ích không phải API hay pattern có đẹp riêng lẻ hay không, mà là state nằm ở đâu, boundary nào chịu trách nhiệm khi lỗi xảy ra, và người dùng phục hồi thế nào khi happy path biến mất.

![Sơ đồ kiến trúc Flutter cho Migrating to standalone material_ui and cupertino_ui in Flutter 3.47](/blog/images/fluttercook-editorial-2026.svg)

## Mô hình thực tế

Weekly releases, independent upgrades, and a style-neutral core for custom design systems and platform design shocks.

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
dart fix --apply --code=migrate_design_widgets
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

Core SDK copies deprecate in November. Package authors: treat as a major release. Lỗi thường gặp là demo chạy đúng nhưng cancellation, retry, permission, accessibility và hành vi khi upgrade lại bị bỏ ngỏ. Khi app có user thật, đó không còn là edge case. Hãy test ít nhất một thiết bị chậm, một request bị ngắt mạng và một process restart nếu chủ đề này ảnh hưởng lifecycle hoặc storage.

## Đánh giá kết quả

Ghi baseline trước khi sửa. So sánh cùng user journey trên cùng nhóm thiết bị, rồi xem cả median lẫn failure tệ nhất mà người dùng nhìn thấy. Một diff nhỏ có rollback rõ thường an toàn hơn rewrite toàn framework. Lưu quyết định và bằng chứng cạnh code để lần upgrade sau không phải tranh luận lại từ đầu.

Đọc thêm các chủ đề liên quan: [Impeller on desktop: SDF text and Metal/Vulkan defaults](/vi/blog/flutter-impeller-desktop-sdf-text/) và [Swift Package Manager plugin migration checklist for Flutter](/vi/blog/flutter-swiftpm-plugin-migration-checklist/).
