---
title: "proxypin: hướng dẫn backend & dữ liệu trong Flutter"
package: "proxypin"
repo: "wanghongenpin/proxypin"
githubUrl: "https://github.com/wanghongenpin/proxypin"
category: "Backend/Data"
stars: 13537
forks: 1160
lastUpdate: "2026-07-16"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+proxypin"
priority: "High"
phase: "P1"
trendRank: 26
description: "Open source free capture HTTP(S) traffic  software ProxyPin, supporting full platform systems."
seoDescription: "proxypin: backend & dữ liệu cho Flutter, 13,537★ trên GitHub. Open source free capture HTTP(S) traffic  software ProxyPin, supporting full platform systems.…"
keywords:
  - flutter proxypin
  - proxypin flutter
  - flutter backend & dữ liệu
  - flutter http
  - backend flutter
  - cơ sở dữ liệu flutter
  - ứng dụng di động flutter
  - proxypin ví dụ
  - proxypin hướng dẫn
topics:
  - capture-traffic
  - charles
  - fiddler
  - proxy
  - proxypin
  - zhuabao
related:
  - slug: gopeed
    title: 'gopeed: hướng dẫn backend & dữ liệu trong Flutter'
  - slug: mmkv
    title: 'MMKV: hướng dẫn backend & dữ liệu trong Flutter'
  - slug: dio
    title: 'dio: hướng dẫn backend & dữ liệu trong Flutter'
  - slug: nhost
    title: 'nhost: hướng dẫn backend & dữ liệu trong Flutter'
faq:
  - q: proxypin có miễn phí không?
    a: Có. proxypin là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn
      có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.
  - q: proxypin có chạy trên cả iOS và Android không?
    a: proxypin được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy
      nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.
  - q: proxypin phổ biến đến mức nào?
    a: Tính đến 2026, proxypin có khoảng 13,537 sao và 1,160 lượt fork trên GitHub,
      thuộc nhóm được dùng nhiều trong mảng backend & dữ liệu.
  - q: Có lựa chọn nào thay thế proxypin?
    a: Các lựa chọn phổ biến trong nhóm backend & dữ liệu gồm gopeed, mmkv, dio. Lựa
      chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.
datePublished: "2023-06-05"
dateModified: "2026-07-16"
draft: false
---

[`proxypin`](https://github.com/wanghongenpin/proxypin) là một **thư viện backend & dữ liệu** mã nguồn mở cho phát triển ứng dụng di động Flutter, với **13,537★** trên GitHub và cập nhật lần cuối ngày **2026-07-16**. Bài viết này trình bày proxypin làm gì, vì sao đáng quan tâm năm 2026, cách thêm vào dự án, khi nào nên dùng, so sánh với các lựa chọn thay thế — kèm phần FAQ ngắn.

## proxypin là gì?

Open source free capture HTTP(S) traffic  software ProxyPin, supporting full platform systems. Nó tập trung vào việc làm việc với API, cơ sở dữ liệu và lưu trữ. Dự án nằm tại [wanghongenpin/proxypin](https://github.com/wanghongenpin/proxypin) và được duy trì bởi `wanghongenpin`.

## Vì sao nên biết proxypin trong năm 2026

proxypin có **13,537 sao GitHub**, **1,160 fork**, 71 issue đang mở. Dự án tồn tại từ năm 2023 và được bảo trì tích cực (cập nhật trong tháng qua). Với một lựa chọn backend & dữ liệu, mức độ được dùng và bảo trì như vậy thường đồng nghĩa với cộng đồng khỏe mạnh, được dùng thực tế và nhiều ví dụ để học.

## Cài đặt proxypin

Thêm gói vào `pubspec.yaml`:

```yaml
dependencies:
  proxypin: ^latest
```

Rồi tải về và import trong mã Dart:

```bash
flutter pub get
```
```dart
import 'package:proxypin/proxypin.dart';
```

Xem thư mục `example/` và [repo GitHub](https://github.com/wanghongenpin/proxypin) để biết API chính xác — proxypin được đánh phiên bản kèm tài liệu đầy đủ nên bạn luôn tích hợp đúng bản phát hành hiện tại.

## Khi nào nên dùng proxypin?

Hãy chọn proxypin khi:

- bạn gọi API REST/GraphQL từ ứng dụng Flutter
- bạn cần lưu trữ cục bộ, cache hoặc đồng bộ offline
- bạn muốn truy cập dữ liệu có kiểu và dễ kiểm thử

Đặc biệt phù hợp nếu dự án của bạn liên quan tới `capture-traffic`, `charles`, `fiddler`, `proxy`, `proxypin`, `zhuabao`.

## proxypin so với các lựa chọn thay thế

Nếu bạn đang cân nhắc các lựa chọn trong nhóm **backend & dữ liệu**, đây là những dự án thường được đem ra so sánh với proxypin:

- [Data & backend in Flutter using gopeed](/vi/recipes/gopeed/)
- [Data & backend in Flutter using MMKV](/vi/recipes/mmkv/)
- [Data & backend in Flutter using dio](/vi/recipes/dio/)
- [Data & backend in Flutter using nhost](/vi/recipes/nhost/)

Không có lựa chọn nào thắng tuyệt đối — điều đó tùy quy mô app, mức quen thuộc của đội ngũ và ngân sách hiệu năng. Xem toàn bộ [nhóm backend & dữ liệu](/vi/recipes/) để so sánh trực tiếp.

## Câu hỏi thường gặp

### proxypin có miễn phí không?

Có. proxypin là mã nguồn mở và miễn phí dùng trong dự án Flutter của bạn. Bạn có thể xem mã nguồn, báo lỗi và đóng góp trên GitHub.

### proxypin có chạy trên cả iOS và Android không?

proxypin được xây cho Flutter nên chạy trên iOS và Android từ một codebase duy nhất, và thường cả web lẫn desktop tùy mức hỗ trợ nền tảng của dự án.

### proxypin phổ biến đến mức nào?

Tính đến 2026, proxypin có khoảng 13,537 sao và 1,160 lượt fork trên GitHub, thuộc nhóm được dùng nhiều trong mảng backend & dữ liệu.

### Có lựa chọn nào thay thế proxypin?

Các lựa chọn phổ biến trong nhóm backend & dữ liệu gồm gopeed, mmkv, dio. Lựa chọn tốt nhất tùy vào quy mô app, đội ngũ và yêu cầu hiệu năng của bạn.

## Tài nguyên & liên kết

- **GitHub:** [wanghongenpin/proxypin](https://github.com/wanghongenpin/proxypin)
- **Video hướng dẫn:** [tìm proxypin trên YouTube](https://www.youtube.com/results?search_query=flutter+proxypin)

---

*Thuộc [FlutterCook](/vi/recipes/) — 500 hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
