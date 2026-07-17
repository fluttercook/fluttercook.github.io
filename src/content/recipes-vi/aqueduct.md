---
title: "aqueduct: hướng dẫn quản lý trạng thái trong Flutter"
package: "aqueduct"
repo: "stablekernel/aqueduct"
githubUrl: "https://github.com/stablekernel/aqueduct"
category: "State management"
stars: 2386
forks: 271
lastUpdate: "2021-03-26"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+aqueduct"
priority: "Medium"
phase: "P6"
trendRank: 269
description: "Dart HTTP server framework for building REST APIs. Includes PostgreSQL ORM and OAuth2 provider."
seoDescription: "aqueduct: quản lý trạng thái cho Flutter, 2,386★ trên GitHub. Dart HTTP server framework for building REST APIs. Includes PostgreSQL ORM and OAuth2 provider.…"
keywords:
  - flutter aqueduct
  - aqueduct flutter
  - flutter quản lý trạng thái
  - flutter state management
  - ứng dụng di động flutter
  - aqueduct ví dụ
  - aqueduct hướng dẫn
topics:
  - dart
  - framework
  - http
  - oauth2
  - orm
  - rest
summary:
  - '**aqueduct** là một thư viện quản lý trạng thái mã nguồn mở thuộc nhóm **State
    management**.'
  - Dự án có **2,386★** và 271 fork, và trưởng thành và ổn định.
  - 'Cài bằng `aqueduct: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi cây widget cần phản ứng theo dữ liệu dùng chung thay đổi.
related:
  - slug: bloc
    title: 'bloc: hướng dẫn quản lý trạng thái trong Flutter'
  - slug: getx
    title: 'getx: hướng dẫn quản lý trạng thái trong Flutter'
  - slug: flutter-architecture-samples
    title: 'flutter_architecture_samples: hướng dẫn quản lý trạng thái trong Flutter'
  - slug: riverpod
    title: 'riverpod: hướng dẫn quản lý trạng thái trong Flutter'
faq:
  - q: aqueduct có miễn phí không?
    a: Có. aqueduct là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn
      có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: aqueduct có chạy trên cả iOS và Android không?
    a: aqueduct được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy
      nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: aqueduct phổ biến đến mức nào?
    a: Tính đến 2026, aqueduct có khoảng 2,386 sao và 271 lượt fork trên GitHub, thuộc
      nhóm được dùng nhiều trong mảng quản lý trạng thái.
  - q: Có lựa chọn nào thay thế aqueduct?
    a: Các lựa chọn phổ biến trong nhóm quản lý trạng thái gồm bloc, getx, flutter-architecture-samples.
      Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
datePublished: "2015-05-29"
dateModified: "2021-03-26"
draft: false
---

[`aqueduct`](https://github.com/stablekernel/aqueduct) là một **thư viện quản lý trạng thái** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **2,386★** trên GitHub và cập nhật lần cuối ngày **2021-03-26**. Bài viết này trình bày aqueduct làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## aqueduct là gì?

Dart HTTP server framework for building REST APIs. Includes PostgreSQL ORM and OAuth2 provider. Nó tập trung vào việc giữ giao diện đồng bộ với trạng thái ứng dụng khi dữ liệu thay đổi. Dự án nằm tại [stablekernel/aqueduct](https://github.com/stablekernel/aqueduct) và được duy trì bởi `stablekernel`.

## Vì sao nên biết aqueduct trong năm 2026

aqueduct có **2,386 sao GitHub**, **271 fork**, 176 issue đang mở. Dự án tồn tại từ năm 2015 và trưởng thành và ổn định. Với một lựa chọn quản lý trạng thái, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt aqueduct

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  aqueduct: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:aqueduct/aqueduct.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/stablekernel/aqueduct) để biết API chính xác — aqueduct được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng aqueduct?

Hãy chọn aqueduct khi:

- cây widget cần phản ứng theo dữ liệu dùng chung thay đổi
- bạn muốn tách logic nghiệp vụ khỏi giao diện
- bạn vượt quá `setState` và cần rebuild có kiểm soát

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `dart`, `framework`, `http`, `oauth2`, `orm`, `rest`.

## aqueduct so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **quản lý trạng thái**, đây là những dự án thường được đem ra so sánh với aqueduct:

- [State management in Flutter with bloc: a practical guide](/vi/recipes/bloc/)
- [State management in Flutter with getx: a practical guide](/vi/recipes/getx/)
- [State management in Flutter with flutter_architecture_samples: a practical guide](/vi/recipes/flutter-architecture-samples/)
- [State management in Flutter with riverpod: a practical guide](/vi/recipes/riverpod/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm quản lý trạng thái](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### aqueduct có miễn phí không?

Có. aqueduct là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### aqueduct có chạy trên cả iOS và Android không?

aqueduct được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### aqueduct phổ biến đến mức nào?

Tính đến 2026, aqueduct có khoảng 2,386 sao và 271 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng quản lý trạng thái.

### Có lựa chọn nào thay thế aqueduct?

Các lựa chọn phổ biến trong nhóm quản lý trạng thái gồm bloc, getx, flutter-architecture-samples. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [stablekernel/aqueduct](https://github.com/stablekernel/aqueduct)
- **Video hướng dẫn:** [tìm aqueduct trên YouTube](https://www.youtube.com/results?search_query=flutter+aqueduct)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
