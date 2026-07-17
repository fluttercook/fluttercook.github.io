---
title: "lottie-flutter: hướng dẫn hoạt ảnh trong Flutter"
package: "lottie-flutter"
repo: "xvrh/lottie-flutter"
githubUrl: "https://github.com/xvrh/lottie-flutter"
category: "Animation"
stars: 1291
forks: 223
lastUpdate: "2026-07-08"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+lottie-flutter"
priority: "Medium"
phase: "P4"
trendRank: 190
description: "Render After Effects animations natively on Flutter. This package is a pure Dart implementation of a Lottie player."
seoDescription: "lottie-flutter: hoạt ảnh cho Flutter, 1,291★ trên GitHub. Render After Effects animations natively on Flutter. This package is a pure Dart implementation of…"
keywords:
  - flutter lottie-flutter
  - lottie-flutter flutter
  - flutter hoạt ảnh
  - flutter animation
  - hoạt ảnh flutter
  - ứng dụng di động flutter
  - lottie-flutter ví dụ
  - lottie-flutter hướng dẫn
topics:
  - dart
  - flutter
  - flutter-web
  - flutter-widget
  - lottie
  - lottie-android
summary:
  - '**lottie-flutter** là một thư viện hoạt ảnh mã nguồn mở thuộc nhóm **Animation**.'
  - Dự án có **1,291★** và 223 fork, và được bảo trì tích cực (cập nhật trong tháng
    qua).
  - 'Cài bằng `lottie-flutter: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi bạn muốn micro-interaction đẹp mà không phải tự viết tween.
related:
  - slug: miru-app
    title: 'miru-app: hướng dẫn hoạt ảnh trong Flutter'
  - slug: anich
    title: 'AniCh: hướng dẫn hoạt ảnh trong Flutter'
  - slug: flutter-ui-nice
    title: 'flutter-ui-nice: hướng dẫn hoạt ảnh trong Flutter'
  - slug: mangayomi
    title: 'mangayomi: hướng dẫn hoạt ảnh trong Flutter'
faq:
  - q: lottie-flutter có miễn phí không?
    a: Có. lottie-flutter là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn.
      Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: lottie-flutter có chạy trên cả iOS và Android không?
    a: lottie-flutter được xây cho Flutter nên chạy trên iOS và Android từ một codebase
      duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: lottie-flutter phổ biến đến mức nào?
    a: Tính đến 2026, lottie-flutter có khoảng 1,291 sao và 223 lượt fork trên GitHub,
      thuộc nhóm được dùng nhiều trong mảng hoạt ảnh.
  - q: Có lựa chọn nào thay thế lottie-flutter?
    a: Các lựa chọn phổ biến trong nhóm hoạt ảnh gồm miru-app, anich, flutter-ui-nice.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
datePublished: "2020-01-23"
dateModified: "2026-07-08"
draft: false
---

[`lottie-flutter`](https://github.com/xvrh/lottie-flutter) là một **thư viện hoạt ảnh** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **1,291★** trên GitHub và cập nhật lần cuối ngày **2026-07-08**. Bài viết này trình bày lottie-flutter làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## lottie-flutter là gì?

Render After Effects animations natively on Flutter. This package is a pure Dart implementation of a Lottie player. Nó tập trung vào việc thêm chuyển động mượt mà, sinh động cho ứng dụng Flutter. Dự án nằm tại [xvrh/lottie-flutter](https://github.com/xvrh/lottie-flutter) và được duy trì bởi `xvrh`.

## Vì sao nên biết lottie-flutter trong năm 2026

lottie-flutter có **1,291 sao GitHub**, **223 fork**, 154 issue đang mở. Dự án tồn tại từ năm 2020 và được bảo trì tích cực (cập nhật trong tháng qua). Với một lựa chọn hoạt ảnh, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt lottie-flutter

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  lottie-flutter: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:lottie_flutter/lottie_flutter.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/xvrh/lottie-flutter) để biết API chính xác — lottie-flutter được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng lottie-flutter?

Hãy chọn lottie-flutter khi:

- bạn muốn micro-interaction đẹp mà không phải tự viết tween
- bạn cần hiệu ứng chuyển trang hoặc loading
- bạn muốn làm sống động giao diện tĩnh

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `dart`, `flutter`, `flutter-web`, `flutter-widget`, `lottie`, `lottie-android`.

## lottie-flutter so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **hoạt ảnh**, đây là những dự án thường được đem ra so sánh với lottie-flutter:

- [Beautiful Flutter animations with miru-app](/vi/recipes/miru-app/)
- [Beautiful Flutter animations with AniCh](/vi/recipes/anich/)
- [Beautiful Flutter animations with flutter-ui-nice](/vi/recipes/flutter-ui-nice/)
- [Beautiful Flutter animations with mangayomi](/vi/recipes/mangayomi/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm hoạt ảnh](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### lottie-flutter có miễn phí không?

Có. lottie-flutter là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### lottie-flutter có chạy trên cả iOS và Android không?

lottie-flutter được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### lottie-flutter phổ biến đến mức nào?

Tính đến 2026, lottie-flutter có khoảng 1,291 sao và 223 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng hoạt ảnh.

### Có lựa chọn nào thay thế lottie-flutter?

Các lựa chọn phổ biến trong nhóm hoạt ảnh gồm miru-app, anich, flutter-ui-nice. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [xvrh/lottie-flutter](https://github.com/xvrh/lottie-flutter)
- **Video hướng dẫn:** [tìm lottie-flutter trên YouTube](https://www.youtube.com/results?search_query=flutter+lottie-flutter)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
