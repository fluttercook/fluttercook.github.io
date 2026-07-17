---
title: "bloc: hướng dẫn quản lý trạng thái trong Flutter"
package: "bloc"
repo: "felangel/bloc"
githubUrl: "https://github.com/felangel/bloc"
category: "State management"
stars: 12474
forks: 3417
lastUpdate: "2026-07-15"
pubDev: "https://pub.dev/packages/bloc"
youtube: "https://www.youtube.com/results?search_query=flutter+bloc"
priority: "High"
phase: "P1"
trendRank: 30
description: "A predictable state management library that helps implement the BLoC design pattern."
seoDescription: "bloc: quản lý trạng thái cho Flutter, 12,474★ trên GitHub. A predictable state management library that helps implement the BLoC design pattern. Cài đặt, cách…"
keywords:
  - flutter bloc
  - bloc flutter
  - flutter quản lý trạng thái
  - flutter state management
  - ứng dụng di động flutter
  - bloc ví dụ
  - bloc hướng dẫn
topics:
  - angulardart
  - bloc
  - concurrency
  - dart
  - dart-library
  - dart-web
related:
  - slug: getx
    title: 'getx: hướng dẫn quản lý trạng thái trong Flutter'
  - slug: flutter-architecture-samples
    title: 'flutter_architecture_samples: hướng dẫn quản lý trạng thái trong Flutter'
  - slug: riverpod
    title: 'riverpod: hướng dẫn quản lý trạng thái trong Flutter'
  - slug: fish-redux
    title: 'fish-redux: hướng dẫn quản lý trạng thái trong Flutter'
faq:
  - q: bloc có miễn phí không?
    a: Có. bloc là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có
      thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: bloc có chạy trên cả iOS và Android không?
    a: bloc được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất,
      và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: bloc phổ biến đến mức nào?
    a: Tính đến 2026, bloc có khoảng 12,474 sao và 3,417 lượt fork trên GitHub, thuộc
      nhóm được dùng nhiều trong mảng quản lý trạng thái.
  - q: Có lựa chọn nào thay thế bloc?
    a: Các lựa chọn phổ biến trong nhóm quản lý trạng thái gồm getx, flutter-architecture-samples,
      riverpod. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của
      bạn.
  - q: Cài đặt bloc thế nào?
    a: Thêm bloc vào mục dependencies trong pubspec.yaml rồi chạy flutter pub get. Phiên
      bản và tài liệu API đầy đủ có trên pub.dev.
datePublished: "2018-10-07"
dateModified: "2026-07-15"
draft: false
---

[`bloc`](https://github.com/felangel/bloc) là một **thư viện quản lý trạng thái** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **12,474★** trên GitHub và cập nhật lần cuối ngày **2026-07-15**. Bài viết này trình bày bloc làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## bloc là gì?

A predictable state management library that helps implement the BLoC design pattern. Nó tập trung vào việc giữ giao diện đồng bộ với trạng thái ứng dụng khi dữ liệu thay đổi. Dự án nằm tại [felangel/bloc](https://github.com/felangel/bloc) và được duy trì bởi `felangel`.

## Vì sao nên biết bloc trong năm 2026

bloc có **12,474 sao GitHub**, **3,417 fork**, 71 issue đang mở. Dự án tồn tại từ năm 2018 và được bảo trì tích cực (cập nhật trong tháng qua). Với một lựa chọn quản lý trạng thái, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt bloc

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  bloc: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:bloc/bloc.dart';
```

Xem thư mục `example/` và [trang pub.dev](https://pub.dev/packages/bloc) để biết API chính xác — bloc được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng bloc?

Hãy chọn bloc khi:

- cây widget cần phản ứng theo dữ liệu dùng chung thay đổi
- bạn muốn tách logic nghiệp vụ khỏi giao diện
- bạn vượt quá `setState` và cần rebuild có kiểm soát

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `angulardart`, `bloc`, `concurrency`, `dart`, `dart-library`, `dart-web`.

## bloc so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **quản lý trạng thái**, đây là những dự án thường được đem ra so sánh với bloc:

- [State management in Flutter with getx: a practical guide](/vi/recipes/getx/)
- [State management in Flutter with flutter_architecture_samples: a practical guide](/vi/recipes/flutter-architecture-samples/)
- [State management in Flutter with riverpod: a practical guide](/vi/recipes/riverpod/)
- [State management in Flutter with fish-redux: a practical guide](/vi/recipes/fish-redux/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm quản lý trạng thái](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### bloc có miễn phí không?

Có. bloc là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### bloc có chạy trên cả iOS và Android không?

bloc được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### bloc phổ biến đến mức nào?

Tính đến 2026, bloc có khoảng 12,474 sao và 3,417 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng quản lý trạng thái.

### Có lựa chọn nào thay thế bloc?

Các lựa chọn phổ biến trong nhóm quản lý trạng thái gồm getx, flutter-architecture-samples, riverpod. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

### Cài đặt bloc thế nào?

Thêm bloc vào mục dependencies trong pubspec.yaml rồi chạy flutter pub get. Phiên bản và tài liệu API đầy đủ có trên pub.dev.

## Tài nguyên & liên kết

- **GitHub:** [felangel/bloc](https://github.com/felangel/bloc)
- **pub.dev:** [bloc](https://pub.dev/packages/bloc)
- **Video hướng dẫn:** [tìm bloc trên YouTube](https://www.youtube.com/results?search_query=flutter+bloc)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
