---
title: A mobile analytics event schema that survives redesigns — hướng dẫn Flutter
description: Naming, required properties, and versioning.
seoDescription: Mobile analytics event schema naming versioning properties. Practical guide for production Flutter teams.
keywords:
- analytics schema
- event naming
- mobile analytics
- tracking plan
- flutter
- dart
- mobile development
- flutter tutorial
category: Analytics
topic: Analytics
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-11'
emoji: 🧭
tags:
- Analytics
- Product
sources:
- name: Analytics
  url: https://firebase.google.com/docs/analytics
- name: Flutter documentation
  url: https://docs.flutter.dev/
- name: Dart documentation
  url: https://dart.dev/guides
related:
- slug: flutter-crash-free-rate-slo
  title: Crash-free session SLOs for mobile teams
- slug: flutter-feature-flag-cleanup
  title: Feature flag cleanup sprints that actually happen
draft: false
---

Analytics without a tracking plan becomes unusable noise. Bài này chuyển quan sát đó thành một mô hình nhỏ để bạn có thể kiểm thử, đo lường và giữ cho code dễ bảo trì khi app lớn lên.

## Vấn đề cốt lõi

Naming, required properties, and versioning. Câu hỏi hữu ích không phải API hay pattern có đẹp riêng lẻ hay không, mà là state nằm ở đâu, boundary nào chịu trách nhiệm khi lỗi xảy ra, và người dùng phục hồi thế nào khi happy path biến mất.

![Sơ đồ kiến trúc Flutter cho A mobile analytics event schema that survives redesigns](/blog/images/fluttercook-editorial-2026.svg)

## Mô hình thực tế

Version the schema and review changes in PRs.

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
logEvent('checkout_start', {'cart_value': 12.5});
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

PII in properties is a privacy bug. Lỗi thường gặp là demo chạy đúng nhưng cancellation, retry, permission, accessibility và hành vi khi upgrade lại bị bỏ ngỏ. Khi app có user thật, đó không còn là edge case. Hãy test ít nhất một thiết bị chậm, một request bị ngắt mạng và một process restart nếu chủ đề này ảnh hưởng lifecycle hoặc storage.

## Đánh giá kết quả

Ghi baseline trước khi sửa. So sánh cùng user journey trên cùng nhóm thiết bị, rồi xem cả median lẫn failure tệ nhất mà người dùng nhìn thấy. Một diff nhỏ có rollback rõ thường an toàn hơn rewrite toàn framework. Lưu quyết định và bằng chứng cạnh code để lần upgrade sau không phải tranh luận lại từ đầu.

Đọc thêm các chủ đề liên quan: [Crash-free session SLOs for mobile teams](/vi/blog/flutter-crash-free-rate-slo/) và [Feature flag cleanup sprints that actually happen](/vi/blog/flutter-feature-flag-cleanup/).
