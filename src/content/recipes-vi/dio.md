---
title: "dio: hướng dẫn backend & dữ liệu trong Flutter"
package: "dio"
repo: "cfug/dio"
githubUrl: "https://github.com/cfug/dio"
category: "Backend/Data"
stars: 12830
forks: 1560
lastUpdate: "2026-07-14"
pubDev: "https://pub.dev/packages/dio"
youtube: "https://www.youtube.com/results?search_query=flutter+dio"
priority: "High"
phase: "P1"
trendRank: 29
description: "A powerful HTTP client for Dart and Flutter, which supports global settings, Interceptors, FormData, aborting and canceling a request, files uploading and downl."
seoDescription: "dio: backend & dữ liệu cho Flutter, 12,830★ trên GitHub. A powerful HTTP client for Dart and Flutter, which supports global settings, Interceptors, FormData,…"
keywords:
  - flutter dio
  - dio flutter
  - flutter backend & dữ liệu
  - flutter http
  - backend flutter
  - cơ sở dữ liệu flutter
  - ứng dụng di động flutter
  - dio ví dụ
  - dio hướng dẫn
topics:
  - adapter
  - cancellable
  - dart
  - dio
  - flutter
  - http
summary:
  - '**dio** là một thư viện backend & dữ liệu mã nguồn mở thuộc nhóm **Backend/Data**.'
  - Dự án có **12,830★** và 1,560 fork, và được bảo trì tích cực (cập nhật trong tháng
    qua).
  - 'Cài bằng `dio: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi bạn gọi API REST/GraphQL từ ứng dụng Flutter.
related:
  - slug: gopeed
    title: 'gopeed: hướng dẫn backend & dữ liệu trong Flutter'
  - slug: mmkv
    title: 'MMKV: hướng dẫn backend & dữ liệu trong Flutter'
  - slug: proxypin
    title: 'proxypin: hướng dẫn backend & dữ liệu trong Flutter'
  - slug: nhost
    title: 'nhost: hướng dẫn backend & dữ liệu trong Flutter'
faq:
  - q: dio có miễn phí không?
    a: Có. dio là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể
      xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: dio có chạy trên cả iOS và Android không?
    a: dio được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất,
      và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: dio phổ biến đến mức nào?
    a: Tính đến 2026, dio có khoảng 12,830 sao và 1,560 lượt fork trên GitHub, thuộc
      nhóm được dùng nhiều trong mảng backend & dữ liệu.
  - q: Có lựa chọn nào thay thế dio?
    a: Các lựa chọn phổ biến trong nhóm backend & dữ liệu gồm gopeed, mmkv, proxypin.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
  - q: Cài đặt dio thế nào?
    a: Thêm dio vào mục dependencies trong pubspec.yaml rồi chạy flutter pub get. Phiên
      bản và tài liệu API đầy đủ có trên pub.dev.
datePublished: "2018-04-20"
dateModified: "2026-07-14"
draft: false
---

[`dio`](https://github.com/cfug/dio) là một **thư viện backend & dữ liệu** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **12,830★** trên GitHub và cập nhật lần cuối ngày **2026-07-14**. Bài viết này trình bày dio làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## dio là gì?

A powerful HTTP client for Dart and Flutter, which supports global settings, Interceptors, FormData, aborting and canceling a request, files uploading and downl. Nó tập trung vào việc làm việc với API, cơ sở dữ liệu và lưu trữ. Dự án nằm tại [cfug/dio](https://github.com/cfug/dio) và được duy trì bởi `cfug`.

## Vì sao nên biết dio trong năm 2026

dio có **12,830 sao GitHub**, **1,560 fork**, 34 issue đang mở. Dự án tồn tại từ năm 2018 và được bảo trì tích cực (cập nhật trong tháng qua). Với một lựa chọn backend & dữ liệu, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt dio

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  dio: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:dio/dio.dart';
```

Xem thư mục `example/` và [trang pub.dev](https://pub.dev/packages/dio) để biết API chính xác — dio được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng dio?

Hãy chọn dio khi:

- bạn gọi API REST/GraphQL từ ứng dụng Flutter
- bạn cần lưu trữ cục bộ, cache hoặc đồng bộ offline
- bạn muốn truy cập dữ liệu có kiểu và dễ kiểm thử

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `adapter`, `cancellable`, `dart`, `dio`, `flutter`, `http`.

## dio so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **backend & dữ liệu**, đây là những dự án thường được đem ra so sánh với dio:

- [Data & backend in Flutter using gopeed](/vi/recipes/gopeed/)
- [Data & backend in Flutter using MMKV](/vi/recipes/mmkv/)
- [Data & backend in Flutter using proxypin](/vi/recipes/proxypin/)
- [Data & backend in Flutter using nhost](/vi/recipes/nhost/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm backend & dữ liệu](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### dio có miễn phí không?

Có. dio là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### dio có chạy trên cả iOS và Android không?

dio được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### dio phổ biến đến mức nào?

Tính đến 2026, dio có khoảng 12,830 sao và 1,560 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng backend & dữ liệu.

### Có lựa chọn nào thay thế dio?

Các lựa chọn phổ biến trong nhóm backend & dữ liệu gồm gopeed, mmkv, proxypin. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

### Cài đặt dio thế nào?

Thêm dio vào mục dependencies trong pubspec.yaml rồi chạy flutter pub get. Phiên bản và tài liệu API đầy đủ có trên pub.dev.

## Tài nguyên & liên kết

- **GitHub:** [cfug/dio](https://github.com/cfug/dio)
- **pub.dev:** [dio](https://pub.dev/packages/dio)
- **Video hướng dẫn:** [tìm dio trên YouTube](https://www.youtube.com/results?search_query=flutter+dio)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
