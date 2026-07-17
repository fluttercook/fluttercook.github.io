---
title: "mcg: hướng dẫn giao diện & thành phần UI trong Flutter"
package: "mcg"
repo: "mbitson/mcg"
githubUrl: "https://github.com/mbitson/mcg"
category: "UI/Components"
stars: 634
forks: 110
lastUpdate: "2020-05-27"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+mcg"
priority: "Low"
phase: "P9"
trendRank: 432
description: "Material Design Palette/Theme Generator - AngularJS, React, Ember, Vue, Android, Flutter & More!"
seoDescription: "mcg: giao diện & thành phần UI cho Flutter, 634★ trên GitHub. Material Design Palette/Theme Generator - AngularJS, React, Ember, Vue, Android, Flutter &…"
keywords:
  - flutter mcg
  - mcg flutter
  - flutter giao diện & thành phần ui
  - flutter ui
  - widget flutter
  - giao diện ứng dụng flutter
  - mcg ví dụ
  - mcg hướng dẫn
topics:
  - angular
  - angular-2-material-2
  - angular-material
  - angularjs-material
  - ember-paper
  - flutter
summary:
  - '**mcg** là một thư viện thành phần giao diện (UI) mã nguồn mở thuộc nhóm **UI/Components**.'
  - Dự án có **634★** và 110 fork, và trưởng thành và ổn định.
  - 'Cài bằng `mcg: ^latest` trong pubspec.yaml.'
  - Phù hợp nhất khi bạn cần một widget dựng sẵn thay vì tự viết từ đầu.
related:
  - slug: rustdesk
    title: 'rustdesk: hướng dẫn giao diện & thành phần UI trong Flutter'
  - slug: hiddify-app
    title: 'hiddify-app: hướng dẫn giao diện & thành phần UI trong Flutter'
  - slug: best-flutter-ui-templates
    title: 'Best-Flutter-UI-Templates: hướng dẫn giao diện & thành phần UI trong Flutter'
  - slug: flet
    title: 'flet: hướng dẫn giao diện & thành phần UI trong Flutter'
faq:
  - q: mcg có miễn phí không?
    a: Có. mcg là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể
      xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: mcg có chạy trên cả iOS và Android không?
    a: mcg được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất,
      và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: mcg phổ biến đến mức nào?
    a: Tính đến 2026, mcg có khoảng 634 sao và 110 lượt fork trên GitHub, thuộc nhóm
      được dùng nhiều trong mảng giao diện & thành phần UI.
  - q: Có lựa chọn nào thay thế mcg?
    a: Các lựa chọn phổ biến trong nhóm giao diện & thành phần UI gồm rustdesk, hiddify-app,
      best-flutter-ui-templates. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu
      cầu hiệu năng của bạn.
datePublished: "2015-04-14"
dateModified: "2020-05-27"
draft: false
---

[`mcg`](https://github.com/mbitson/mcg) là một **thư viện thành phần giao diện (UI)** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **634★** trên GitHub và cập nhật lần cuối ngày **2020-05-27**. Bài viết này trình bày mcg làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## mcg là gì?

Material Design Palette/Theme Generator - AngularJS, React, Ember, Vue, Android, Flutter & More! Nó tập trung vào việc dựng các widget giao diện đẹp, tái sử dụng nhanh hơn. Dự án nằm tại [mbitson/mcg](https://github.com/mbitson/mcg) và được duy trì bởi `mbitson`.

## Vì sao nên biết mcg trong năm 2026

mcg có **634 sao GitHub**, **110 fork**, 8 issue đang mở. Dự án tồn tại từ năm 2015 và trưởng thành và ổn định. Với một lựa chọn giao diện & thành phần UI, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt mcg

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  mcg: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:mcg/mcg.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/mbitson/mcg) để biết API chính xác — mcg được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng mcg?

Hãy chọn mcg khi:

- bạn cần một widget dựng sẵn thay vì tự viết từ đầu
- bạn muốn giao diện nhất quán giữa các màn hình
- bạn dựng nhanh giao diện ứng dụng di động

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `angular`, `angular-2-material-2`, `angular-material`, `angularjs-material`, `ember-paper`, `flutter`.

## mcg so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **giao diện & thành phần UI**, đây là những dự án thường được đem ra so sánh với mcg:

- [Build better Flutter UI with rustdesk](/vi/recipes/rustdesk/)
- [Build better Flutter UI with hiddify-app](/vi/recipes/hiddify-app/)
- [Build better Flutter UI with Best-Flutter-UI-Templates](/vi/recipes/best-flutter-ui-templates/)
- [Build better Flutter UI with flet](/vi/recipes/flet/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm giao diện & thành phần UI](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### mcg có miễn phí không?

Có. mcg là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### mcg có chạy trên cả iOS và Android không?

mcg được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### mcg phổ biến đến mức nào?

Tính đến 2026, mcg có khoảng 634 sao và 110 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng giao diện & thành phần UI.

### Có lựa chọn nào thay thế mcg?

Các lựa chọn phổ biến trong nhóm giao diện & thành phần UI gồm rustdesk, hiddify-app, best-flutter-ui-templates. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [mbitson/mcg](https://github.com/mbitson/mcg)
- **Video hướng dẫn:** [tìm mcg trên YouTube](https://www.youtube.com/results?search_query=flutter+mcg)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
