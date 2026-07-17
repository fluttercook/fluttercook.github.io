---
title: "sdk: hướng dẫn framework lõi trong Flutter"
package: "sdk"
repo: "dart-lang/sdk"
githubUrl: "https://github.com/dart-lang/sdk"
category: "Framework/Core"
stars: 11211
forks: 1849
lastUpdate: "2026-07-16"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+sdk"
priority: "High"
phase: "P1"
trendRank: 33
description: "The Dart SDK, including the VM, JS and Wasm compilers, analysis, core libraries, and more."
seoDescription: "sdk: framework lõi cho Flutter, 11,211★ trên GitHub. The Dart SDK, including the VM, JS and Wasm compilers, analysis, core libraries, and more. Cài đặt, cách…"
keywords:
  - flutter sdk
  - sdk flutter
  - flutter framework lõi
  - flutter framework
  - ứng dụng di động flutter
  - sdk ví dụ
  - sdk hướng dẫn
topics:
  - dart
  - language
  - programming-language
  - sdk
summary:
  - '**sdk** là một dự án framework lõi mã nguồn mở thuộc nhóm **Framework/Core**.'
  - Dự án có **11,211★** và 1,849 fork, và được bảo trì tích cực (cập nhật trong tháng
    qua).
  - 'Cài bằng `sdk: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi bạn muốn hiểu điều gì vận hành chính Flutter.
related:
  - slug: flutter
    title: 'flutter: hướng dẫn framework lõi trong Flutter'
faq:
  - q: sdk có miễn phí không?
    a: Có. sdk là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể
      xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: sdk có chạy trên cả iOS và Android không?
    a: sdk được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất,
      và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: sdk phổ biến đến mức nào?
    a: Tính đến 2026, sdk có khoảng 11,211 sao và 1,849 lượt fork trên GitHub, thuộc
      nhóm được dùng nhiều trong mảng framework lõi.
  - q: Có lựa chọn nào thay thế sdk?
    a: Các lựa chọn phổ biến trong nhóm framework lõi gồm flutter. Lựa chọn tốt nhất
      tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
datePublished: "2015-05-16"
dateModified: "2026-07-16"
draft: false
---

[`sdk`](https://github.com/dart-lang/sdk) là một **dự án framework lõi** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **11,211★** trên GitHub và cập nhật lần cuối ngày **2026-07-16**. Bài viết này trình bày sdk làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## sdk là gì?

The Dart SDK, including the VM, JS and Wasm compilers, analysis, core libraries, and more. Nó tập trung vào việc nền tảng mà toàn bộ hệ sinh thái Flutter xây trên đó. Dự án nằm tại [dart-lang/sdk](https://github.com/dart-lang/sdk) và được duy trì bởi `dart-lang`.

## Vì sao nên biết sdk trong năm 2026

sdk có **11,211 sao GitHub**, **1,849 fork**, 8,409 issue đang mở. Dự án tồn tại từ năm 2015 và được bảo trì tích cực (cập nhật trong tháng qua). Với một lựa chọn framework lõi, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt sdk

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  sdk: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:sdk/sdk.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/dart-lang/sdk) để biết API chính xác — sdk được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng sdk?

Hãy chọn sdk khi:

- bạn muốn hiểu điều gì vận hành chính Flutter
- bạn đóng góp hoặc theo dõi dự án lõi
- bạn cần nguồn chuẩn về cách Flutter hoạt động

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `dart`, `language`, `programming-language`, `sdk`.

## sdk so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **framework lõi**, đây là những dự án thường được đem ra so sánh với sdk:

- [flutter: what powers Flutter and why it matters](/vi/recipes/flutter/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm framework lõi](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### sdk có miễn phí không?

Có. sdk là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### sdk có chạy trên cả iOS và Android không?

sdk được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### sdk phổ biến đến mức nào?

Tính đến 2026, sdk có khoảng 11,211 sao và 1,849 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng framework lõi.

### Có lựa chọn nào thay thế sdk?

Các lựa chọn phổ biến trong nhóm framework lõi gồm flutter. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [dart-lang/sdk](https://github.com/dart-lang/sdk)
- **Video hướng dẫn:** [tìm sdk trên YouTube](https://www.youtube.com/results?search_query=flutter+sdk)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
