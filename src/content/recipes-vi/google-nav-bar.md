---
title: "google_nav_bar: hướng dẫn điều hướng trong Flutter"
package: "google_nav_bar"
repo: "sooxt98/google_nav_bar"
githubUrl: "https://github.com/sooxt98/google_nav_bar"
category: "Navigation"
stars: 790
forks: 117
lastUpdate: "2024-11-30"
pubDev: "https://pub.dev/packages/google_nav_bar"
youtube: "https://www.youtube.com/results?search_query=flutter+google-nav-bar"
priority: "Low"
phase: "P9"
trendRank: 415
description: "A modern google style nav bar for flutter."
seoDescription: "google_nav_bar: điều hướng cho Flutter, 790★ trên GitHub. A modern google style nav bar for flutter. Cài đặt, cách dùng, lựa chọn thay thế & FAQ."
keywords:
  - flutter google_nav_bar
  - google_nav_bar flutter
  - flutter điều hướng
  - flutter navigation
  - định tuyến flutter
  - ứng dụng di động flutter
  - google_nav_bar ví dụ
  - google_nav_bar hướng dẫn
topics:
  - bottombar
  - bottomnavigationbar
  - bubble-navigation
  - flutter
  - flutter-apps
  - flutter-material
summary:
  - '**google_nav_bar** là một thư viện điều hướng & định tuyến mã nguồn mở thuộc nhóm
    **Navigation**.'
  - Dự án có **790★** và 117 fork, và trưởng thành và ổn định.
  - 'Cài bằng `google_nav_bar: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi bạn cần định tuyến khai báo, theo URL.
related:
  - slug: lantern
    title: 'lantern: hướng dẫn điều hướng trong Flutter'
  - slug: fluro
    title: 'fluro: hướng dẫn điều hướng trong Flutter'
  - slug: luci-mobile
    title: 'luci-mobile: hướng dẫn điều hướng trong Flutter'
  - slug: flow-builder
    title: 'flow_builder: hướng dẫn điều hướng trong Flutter'
faq:
  - q: google_nav_bar có miễn phí không?
    a: Có. google_nav_bar là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn.
      Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: google_nav_bar có chạy trên cả iOS và Android không?
    a: google_nav_bar được xây cho Flutter nên chạy trên iOS và Android từ một codebase
      duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: google_nav_bar phổ biến đến mức nào?
    a: Tính đến 2026, google_nav_bar có khoảng 790 sao và 117 lượt fork trên GitHub,
      thuộc nhóm được dùng nhiều trong mảng điều hướng.
  - q: Có lựa chọn nào thay thế google_nav_bar?
    a: Các lựa chọn phổ biến trong nhóm điều hướng gồm lantern, fluro, luci-mobile.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
  - q: Cài đặt google_nav_bar thế nào?
    a: Thêm google_nav_bar vào mục dependencies trong pubspec.yaml rồi chạy flutter
      pub get. Phiên bản và tài liệu API đầy đủ có trên pub.dev.
datePublished: "2019-12-22"
dateModified: "2024-11-30"
draft: false
---

[`google_nav_bar`](https://github.com/sooxt98/google_nav_bar) là một **thư viện điều hướng & định tuyến** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **790★** trên GitHub và cập nhật lần cuối ngày **2024-11-30**. Bài viết này trình bày google_nav_bar làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## google_nav_bar là gì?

A modern google style nav bar for flutter. Nó tập trung vào việc tổ chức màn hình, route và deep link. Dự án nằm tại [sooxt98/google_nav_bar](https://github.com/sooxt98/google_nav_bar) và được duy trì bởi `sooxt98`.

## Vì sao nên biết google_nav_bar trong năm 2026

google_nav_bar có **790 sao GitHub**, **117 fork**, 20 issue đang mở. Dự án tồn tại từ năm 2019 và trưởng thành và ổn định. Với một lựa chọn điều hướng, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt google_nav_bar

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  google_nav_bar: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:google_nav_bar/google_nav_bar.dart';
```

Xem thư mục `example/` và [trang pub.dev](https://pub.dev/packages/google_nav_bar) để biết API chính xác — google_nav_bar được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng google_nav_bar?

Hãy chọn google_nav_bar khi:

- bạn cần định tuyến khai báo, theo URL
- bạn xử lý deep link hoặc điều hướng lồng nhau
- bạn muốn route an toàn kiểu (type-safe)

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `bottombar`, `bottomnavigationbar`, `bubble-navigation`, `flutter`, `flutter-apps`, `flutter-material`.

## google_nav_bar so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **điều hướng**, đây là những dự án thường được đem ra so sánh với google_nav_bar:

- [Flutter navigation done right with lantern](/vi/recipes/lantern/)
- [Flutter navigation done right with fluro](/vi/recipes/fluro/)
- [Flutter navigation done right with luci-mobile](/vi/recipes/luci-mobile/)
- [Flutter navigation done right with flow_builder](/vi/recipes/flow-builder/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm điều hướng](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### google_nav_bar có miễn phí không?

Có. google_nav_bar là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### google_nav_bar có chạy trên cả iOS và Android không?

google_nav_bar được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### google_nav_bar phổ biến đến mức nào?

Tính đến 2026, google_nav_bar có khoảng 790 sao và 117 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng điều hướng.

### Có lựa chọn nào thay thế google_nav_bar?

Các lựa chọn phổ biến trong nhóm điều hướng gồm lantern, fluro, luci-mobile. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

### Cài đặt google_nav_bar thế nào?

Thêm google_nav_bar vào mục dependencies trong pubspec.yaml rồi chạy flutter pub get. Phiên bản và tài liệu API đầy đủ có trên pub.dev.

## Tài nguyên & liên kết

- **GitHub:** [sooxt98/google_nav_bar](https://github.com/sooxt98/google_nav_bar)
- **pub.dev:** [google_nav_bar](https://pub.dev/packages/google_nav_bar)
- **Video hướng dẫn:** [tìm google_nav_bar trên YouTube](https://www.youtube.com/results?search_query=flutter+google-nav-bar)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
