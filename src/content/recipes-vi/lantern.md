---
title: "lantern: hướng dẫn điều hướng trong Flutter"
package: "lantern"
repo: "getlantern/lantern"
githubUrl: "https://github.com/getlantern/lantern"
category: "Navigation"
stars: 15800
forks: 11076
lastUpdate: "2026-07-15"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+lantern"
priority: "High"
phase: "P1"
trendRank: 22
description: "Open-source VPN for speed, privacy, and censorship circumvention. Free to download on Android, iOS, Windows, macOS, and Linux."
seoDescription: "lantern: điều hướng cho Flutter, 15,800★ trên GitHub. Open-source VPN for speed, privacy, and censorship circumvention. Free to download on Android, iOS,…"
keywords:
  - flutter lantern
  - lantern flutter
  - flutter điều hướng
  - flutter navigation
  - định tuyến flutter
  - ứng dụng di động flutter
  - lantern ví dụ
  - lantern hướng dẫn
topics:
  - accelerator
  - censorship
  - circumvention
  - gfw
  - lantern
  - router
related:
  - slug: fluro
    title: 'fluro: hướng dẫn điều hướng trong Flutter'
  - slug: google-nav-bar
    title: 'google_nav_bar: hướng dẫn điều hướng trong Flutter'
  - slug: luci-mobile
    title: 'luci-mobile: hướng dẫn điều hướng trong Flutter'
  - slug: flow-builder
    title: 'flow_builder: hướng dẫn điều hướng trong Flutter'
faq:
  - q: lantern có miễn phí không?
    a: Có. lantern là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn
      có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: lantern có chạy trên cả iOS và Android không?
    a: lantern được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy
      nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: lantern phổ biến đến mức nào?
    a: Tính đến 2026, lantern có khoảng 15,800 sao và 11,076 lượt fork trên GitHub,
      thuộc nhóm được dùng nhiều trong mảng điều hướng.
  - q: Có lựa chọn nào thay thế lantern?
    a: Các lựa chọn phổ biến trong nhóm điều hướng gồm fluro, google-nav-bar, luci-mobile.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
datePublished: "2011-02-17"
dateModified: "2026-07-15"
draft: false
---

[`lantern`](https://github.com/getlantern/lantern) là một **thư viện điều hướng & định tuyến** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **15,800★** trên GitHub và cập nhật lần cuối ngày **2026-07-15**. Bài viết này trình bày lantern làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## lantern là gì?

Open-source VPN for speed, privacy, and censorship circumvention. Free to download on Android, iOS, Windows, macOS, and Linux. Nó tập trung vào việc tổ chức màn hình, route và deep link. Dự án nằm tại [getlantern/lantern](https://github.com/getlantern/lantern) và được duy trì bởi `getlantern`.

## Vì sao nên biết lantern trong năm 2026

lantern có **15,800 sao GitHub**, **11,076 fork**, 44 issue đang mở. Dự án tồn tại từ năm 2011 và được bảo trì tích cực (cập nhật trong tháng qua). Với một lựa chọn điều hướng, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt lantern

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  lantern: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:lantern/lantern.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/getlantern/lantern) để biết API chính xác — lantern được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng lantern?

Hãy chọn lantern khi:

- bạn cần định tuyến khai báo, theo URL
- bạn xử lý deep link hoặc điều hướng lồng nhau
- bạn muốn route an toàn kiểu (type-safe)

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `accelerator`, `censorship`, `circumvention`, `gfw`, `lantern`, `router`.

## lantern so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **điều hướng**, đây là những dự án thường được đem ra so sánh với lantern:

- [Flutter navigation done right with fluro](/vi/recipes/fluro/)
- [Flutter navigation done right with google_nav_bar](/vi/recipes/google-nav-bar/)
- [Flutter navigation done right with luci-mobile](/vi/recipes/luci-mobile/)
- [Flutter navigation done right with flow_builder](/vi/recipes/flow-builder/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm điều hướng](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### lantern có miễn phí không?

Có. lantern là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### lantern có chạy trên cả iOS và Android không?

lantern được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### lantern phổ biến đến mức nào?

Tính đến 2026, lantern có khoảng 15,800 sao và 11,076 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng điều hướng.

### Có lựa chọn nào thay thế lantern?

Các lựa chọn phổ biến trong nhóm điều hướng gồm fluro, google-nav-bar, luci-mobile. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [getlantern/lantern](https://github.com/getlantern/lantern)
- **Video hướng dẫn:** [tìm lantern trên YouTube](https://www.youtube.com/results?search_query=flutter+lantern)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
