---
title: "fluro: hướng dẫn điều hướng trong Flutter"
package: "fluro"
repo: "lukepighetti/fluro"
githubUrl: "https://github.com/lukepighetti/fluro"
category: "Navigation"
stars: 3713
forks: 409
lastUpdate: "2023-03-22"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+fluro"
priority: "Medium"
phase: "P5"
trendRank: 224
description: "Fluro is a Flutter routing library that adds flexible routing options like wildcards, named parameters and clear route definitions."
seoDescription: "fluro: điều hướng cho Flutter, 3,713★ trên GitHub. Fluro is a Flutter routing library that adds flexible routing options like wildcards, named parameters and…"
keywords:
  - flutter fluro
  - fluro flutter
  - flutter điều hướng
  - flutter navigation
  - định tuyến flutter
  - ứng dụng di động flutter
  - fluro ví dụ
  - fluro hướng dẫn
topics:
  - flutter
  - flutter-routing
  - parameters
  - router
  - routing
summary:
  - '**fluro** là một thư viện điều hướng & định tuyến mã nguồn mở thuộc nhóm **Navigation**.'
  - Dự án có **3,713★** và 409 fork, và trưởng thành và ổn định.
  - 'Cài bằng `fluro: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi bạn cần định tuyến khai báo, theo URL.
related:
  - slug: lantern
    title: 'lantern: hướng dẫn điều hướng trong Flutter'
  - slug: google-nav-bar
    title: 'google_nav_bar: hướng dẫn điều hướng trong Flutter'
  - slug: luci-mobile
    title: 'luci-mobile: hướng dẫn điều hướng trong Flutter'
  - slug: flow-builder
    title: 'flow_builder: hướng dẫn điều hướng trong Flutter'
faq:
  - q: fluro có miễn phí không?
    a: Có. fluro là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có
      thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: fluro có chạy trên cả iOS và Android không?
    a: fluro được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất,
      và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: fluro phổ biến đến mức nào?
    a: Tính đến 2026, fluro có khoảng 3,713 sao và 409 lượt fork trên GitHub, thuộc
      nhóm được dùng nhiều trong mảng điều hướng.
  - q: Có lựa chọn nào thay thế fluro?
    a: Các lựa chọn phổ biến trong nhóm điều hướng gồm lantern, google-nav-bar, luci-mobile.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
datePublished: "2017-04-25"
dateModified: "2023-03-22"
draft: false
---

[`fluro`](https://github.com/lukepighetti/fluro) là một **thư viện điều hướng & định tuyến** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **3,713★** trên GitHub và cập nhật lần cuối ngày **2023-03-22**. Bài viết này trình bày fluro làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## fluro là gì?

Fluro is a Flutter routing library that adds flexible routing options like wildcards, named parameters and clear route definitions. Nó tập trung vào việc tổ chức màn hình, route và deep link. Dự án nằm tại [lukepighetti/fluro](https://github.com/lukepighetti/fluro) và được duy trì bởi `lukepighetti`.

## Vì sao nên biết fluro trong năm 2026

fluro có **3,713 sao GitHub**, **409 fork**, 43 issue đang mở. Dự án tồn tại từ năm 2017 và trưởng thành và ổn định. Với một lựa chọn điều hướng, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt fluro

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  fluro: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:fluro/fluro.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/lukepighetti/fluro) để biết API chính xác — fluro được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng fluro?

Hãy chọn fluro khi:

- bạn cần định tuyến khai báo, theo URL
- bạn xử lý deep link hoặc điều hướng lồng nhau
- bạn muốn route an toàn kiểu (type-safe)

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `flutter`, `flutter-routing`, `parameters`, `router`, `routing`.

## fluro so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **điều hướng**, đây là những dự án thường được đem ra so sánh với fluro:

- [Flutter navigation done right with lantern](/vi/recipes/lantern/)
- [Flutter navigation done right with google_nav_bar](/vi/recipes/google-nav-bar/)
- [Flutter navigation done right with luci-mobile](/vi/recipes/luci-mobile/)
- [Flutter navigation done right with flow_builder](/vi/recipes/flow-builder/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm điều hướng](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### fluro có miễn phí không?

Có. fluro là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### fluro có chạy trên cả iOS và Android không?

fluro được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### fluro phổ biến đến mức nào?

Tính đến 2026, fluro có khoảng 3,713 sao và 409 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng điều hướng.

### Có lựa chọn nào thay thế fluro?

Các lựa chọn phổ biến trong nhóm điều hướng gồm lantern, google-nav-bar, luci-mobile. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [lukepighetti/fluro](https://github.com/lukepighetti/fluro)
- **Video hướng dẫn:** [tìm fluro trên YouTube](https://www.youtube.com/results?search_query=flutter+fluro)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
