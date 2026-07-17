---
title: "scratcher: hướng dẫn giao diện & thành phần UI trong Flutter"
package: "scratcher"
repo: "vintage/scratcher"
githubUrl: "https://github.com/vintage/scratcher"
category: "UI/Components"
stars: 669
forks: 76
lastUpdate: "2023-11-24"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+scratcher"
priority: "Low"
phase: "P9"
trendRank: 428
description: "Scratch card widget which temporarily hides content from user."
seoDescription: "scratcher: giao diện & thành phần UI cho Flutter, 669★ trên GitHub. Scratch card widget which temporarily hides content from user. Cài đặt, cách dùng, lựa…"
keywords:
  - flutter scratcher
  - scratcher flutter
  - flutter giao diện & thành phần ui
  - flutter ui
  - widget flutter
  - giao diện ứng dụng flutter
  - scratcher ví dụ
  - scratcher hướng dẫn
topics:
  - flutter
  - flutter-plugin
  - flutter-widget
summary:
  - '**scratcher** là một thư viện thành phần giao diện (UI) mã nguồn mở thuộc nhóm
    **UI/Components**.'
  - Dự án có **669★** và 76 fork, và trưởng thành và ổn định.
  - 'Cài bằng `scratcher: ^latest` trong pubspec.yaml.'
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
  - q: scratcher có miễn phí không?
    a: Có. scratcher là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn
      có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: scratcher có chạy trên cả iOS và Android không?
    a: scratcher được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy
      nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: scratcher phổ biến đến mức nào?
    a: Tính đến 2026, scratcher có khoảng 669 sao và 76 lượt fork trên GitHub, thuộc
      nhóm được dùng nhiều trong mảng giao diện & thành phần UI.
  - q: Có lựa chọn nào thay thế scratcher?
    a: Các lựa chọn phổ biến trong nhóm giao diện & thành phần UI gồm rustdesk, hiddify-app,
      best-flutter-ui-templates. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu
      cầu hiệu năng của bạn.
datePublished: "2019-07-22"
dateModified: "2023-11-24"
draft: false
---

[`scratcher`](https://github.com/vintage/scratcher) là một **thư viện thành phần giao diện (UI)** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **669★** trên GitHub và cập nhật lần cuối ngày **2023-11-24**. Bài viết này trình bày scratcher làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## scratcher là gì?

Scratch card widget which temporarily hides content from user. Nó tập trung vào việc dựng các widget giao diện đẹp, tái sử dụng nhanh hơn. Dự án nằm tại [vintage/scratcher](https://github.com/vintage/scratcher) và được duy trì bởi `vintage`.

## Vì sao nên biết scratcher trong năm 2026

scratcher có **669 sao GitHub**, **76 fork**, 11 issue đang mở. Dự án tồn tại từ năm 2019 và trưởng thành và ổn định. Với một lựa chọn giao diện & thành phần UI, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt scratcher

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  scratcher: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:scratcher/scratcher.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/vintage/scratcher) để biết API chính xác — scratcher được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng scratcher?

Hãy chọn scratcher khi:

- bạn cần một widget dựng sẵn thay vì tự viết từ đầu
- bạn muốn giao diện nhất quán giữa các màn hình
- bạn dựng nhanh giao diện ứng dụng di động

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `flutter`, `flutter-plugin`, `flutter-widget`.

## scratcher so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **giao diện & thành phần UI**, đây là những dự án thường được đem ra so sánh với scratcher:

- [Build better Flutter UI with rustdesk](/vi/recipes/rustdesk/)
- [Build better Flutter UI with hiddify-app](/vi/recipes/hiddify-app/)
- [Build better Flutter UI with Best-Flutter-UI-Templates](/vi/recipes/best-flutter-ui-templates/)
- [Build better Flutter UI with flet](/vi/recipes/flet/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm giao diện & thành phần UI](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### scratcher có miễn phí không?

Có. scratcher là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### scratcher có chạy trên cả iOS và Android không?

scratcher được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### scratcher phổ biến đến mức nào?

Tính đến 2026, scratcher có khoảng 669 sao và 76 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng giao diện & thành phần UI.

### Có lựa chọn nào thay thế scratcher?

Các lựa chọn phổ biến trong nhóm giao diện & thành phần UI gồm rustdesk, hiddify-app, best-flutter-ui-templates. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [vintage/scratcher](https://github.com/vintage/scratcher)
- **Video hướng dẫn:** [tìm scratcher trên YouTube](https://www.youtube.com/results?search_query=flutter+scratcher)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
