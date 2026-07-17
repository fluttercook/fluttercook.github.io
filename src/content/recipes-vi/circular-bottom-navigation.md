---
title: "circular_bottom_navigation: hướng dẫn hoạt ảnh trong Flutter"
package: "circular_bottom_navigation"
repo: "benyaminbeyzaie/circular_bottom_navigation"
githubUrl: "https://github.com/benyaminbeyzaie/circular_bottom_navigation"
category: "Animation"
stars: 691
forks: 100
lastUpdate: "2024-03-18"
pubDev: "https://pub.dev/packages/circular_bottom_navigation"
youtube: "https://www.youtube.com/results?search_query=flutter+circular-bottom-navigation"
priority: "Low"
phase: "P9"
trendRank: 425
description: "Circular bottom navigation is a bottom navigation library for flutter with circular indicator and cool animations."
seoDescription: "circular_bottom_navigation: hoạt ảnh cho Flutter, 691★ trên GitHub. Circular bottom navigation is a bottom navigation library for flutter with circular…"
keywords:
  - flutter circular_bottom_navigation
  - circular_bottom_navigation flutter
  - flutter hoạt ảnh
  - flutter animation
  - hoạt ảnh flutter
  - ứng dụng di động flutter
  - circular_bottom_navigation ví dụ
  - circular_bottom_navigation hướng dẫn
topics:
  - flutter
  - hacktoberfest
  - ui
summary:
  - '**circular_bottom_navigation** là một thư viện hoạt ảnh mã nguồn mở thuộc nhóm
    **Animation**.'
  - Dự án có **691★** và 100 fork, và trưởng thành và ổn định.
  - 'Cài bằng `circular_bottom_navigation: ^latest` trong pubspec.yaml.'
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
  - q: circular_bottom_navigation có miễn phí không?
    a: Có. circular_bottom_navigation là mã nguồn mở và miễn phí dùng trong dự án Flutter
      của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: circular_bottom_navigation có chạy trên cả iOS và Android không?
    a: circular_bottom_navigation được xây cho Flutter nên chạy trên iOS và Android
      từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng
      của dự án.
  - q: circular_bottom_navigation phổ biến đến mức nào?
    a: Tính đến 2026, circular_bottom_navigation có khoảng 691 sao và 100 lượt fork
      trên GitHub, thuộc nhóm được dùng nhiều trong mảng hoạt ảnh.
  - q: Có lựa chọn nào thay thế circular_bottom_navigation?
    a: Các lựa chọn phổ biến trong nhóm hoạt ảnh gồm miru-app, anich, flutter-ui-nice.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
  - q: Cài đặt circular_bottom_navigation thế nào?
    a: Thêm circular_bottom_navigation vào mục dependencies trong pubspec.yaml rồi chạy
      flutter pub get. Phiên bản và tài liệu API đầy đủ có trên pub.dev.
datePublished: "2019-02-12"
dateModified: "2024-03-18"
draft: false
---

[`circular_bottom_navigation`](https://github.com/benyaminbeyzaie/circular_bottom_navigation) là một **thư viện hoạt ảnh** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **691★** trên GitHub và cập nhật lần cuối ngày **2024-03-18**. Bài viết này trình bày circular_bottom_navigation làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## circular_bottom_navigation là gì?

Circular bottom navigation is a bottom navigation library for flutter with circular indicator and cool animations. Nó tập trung vào việc thêm chuyển động mượt mà, sinh động cho ứng dụng Flutter. Dự án nằm tại [benyaminbeyzaie/circular_bottom_navigation](https://github.com/benyaminbeyzaie/circular_bottom_navigation) và được duy trì bởi `benyaminbeyzaie`.

## Vì sao nên biết circular_bottom_navigation trong năm 2026

circular_bottom_navigation có **691 sao GitHub**, **100 fork**, 5 issue đang mở. Dự án tồn tại từ năm 2019 và trưởng thành và ổn định. Với một lựa chọn hoạt ảnh, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt circular_bottom_navigation

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  circular_bottom_navigation: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:circular_bottom_navigation/circular_bottom_navigation.dart';
```

Xem thư mục `example/` và [trang pub.dev](https://pub.dev/packages/circular_bottom_navigation) để biết API chính xác — circular_bottom_navigation được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng circular_bottom_navigation?

Hãy chọn circular_bottom_navigation khi:

- bạn muốn micro-interaction đẹp mà không phải tự viết tween
- bạn cần hiệu ứng chuyển trang hoặc loading
- bạn muốn làm sống động giao diện tĩnh

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `flutter`, `hacktoberfest`, `ui`.

## circular_bottom_navigation so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **hoạt ảnh**, đây là những dự án thường được đem ra so sánh với circular_bottom_navigation:

- [Beautiful Flutter animations with miru-app](/vi/recipes/miru-app/)
- [Beautiful Flutter animations with AniCh](/vi/recipes/anich/)
- [Beautiful Flutter animations with flutter-ui-nice](/vi/recipes/flutter-ui-nice/)
- [Beautiful Flutter animations with mangayomi](/vi/recipes/mangayomi/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm hoạt ảnh](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### circular_bottom_navigation có miễn phí không?

Có. circular_bottom_navigation là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### circular_bottom_navigation có chạy trên cả iOS và Android không?

circular_bottom_navigation được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### circular_bottom_navigation phổ biến đến mức nào?

Tính đến 2026, circular_bottom_navigation có khoảng 691 sao và 100 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng hoạt ảnh.

### Có lựa chọn nào thay thế circular_bottom_navigation?

Các lựa chọn phổ biến trong nhóm hoạt ảnh gồm miru-app, anich, flutter-ui-nice. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

### Cài đặt circular_bottom_navigation thế nào?

Thêm circular_bottom_navigation vào mục dependencies trong pubspec.yaml rồi chạy flutter pub get. Phiên bản và tài liệu API đầy đủ có trên pub.dev.

## Tài nguyên & liên kết

- **GitHub:** [benyaminbeyzaie/circular_bottom_navigation](https://github.com/benyaminbeyzaie/circular_bottom_navigation)
- **pub.dev:** [circular_bottom_navigation](https://pub.dev/packages/circular_bottom_navigation)
- **Video hướng dẫn:** [tìm circular_bottom_navigation trên YouTube](https://www.youtube.com/results?search_query=flutter+circular-bottom-navigation)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
