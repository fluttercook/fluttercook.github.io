---
title: "Flutter Zero: Flutter khi bỏ đi dart:ui"
package: "flutter_zero"
repo: "knopp/flutter_zero"
githubUrl: "https://github.com/knopp/flutter_zero"
category: "Framework/Core"
stars: 274
forks: 9
lastUpdate: "2026-08-08"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+zero+dart+ui"
priority: "High"
phase: "P1"
trendRank: 0
description: "Flutter Zero gỡ dart:ui, Skia và Impeller khỏi Flutter, chỉ để lại một runtime Dart vẫn chạy được với lệnh flutter. Một thử nghiệm tách lớp UI khỏi engine."
seoDescription: "Flutter Zero là Flutter đã bỏ dart:ui — không Skia, không Impeller, không widget, nhưng vẫn dùng lệnh flutter và plugin IDE như cũ. Nó dùng để làm gì và chưa làm được gì."
keywords:
  - flutter zero
  - flutter không có dart ui
  - dart runtime giao diện native
  - flutter engine embedder
  - dart ffi native ui
  - matej knopp flutter
topics:
  - dart
  - flutter-engine
  - ffi
summary:
  - "**Flutter Zero** là Flutter đã gỡ gần hết `dart:ui` — không widget, không Skia, không Impeller."
  - Nó giữ nguyên khả năng tương thích với công cụ `flutter` và plugin IDE, nên create, build và run vẫn chạy như thường.
  - Mục tiêu là thử nghiệm ứng dụng Dart vẽ giao diện bằng toolkit native qua interop, và biến `dart:ui` thành một package thay vì thứ dựng sẵn trong engine.
  - "**274★**, giấy phép BSD-3-Clause, tác giả Matej Knopp. Có sẵn bản engine build cho mọi nền tảng, nhưng đây là thử nghiệm chứ không phải sản phẩm."
related:
  - slug: denial
    title: "Denial: trình quản lý cửa sổ Wayland đặt Flutter làm nền móng"
  - slug: dart-mcp
    title: "dart-lang/ai: bộ gói MCP chính thức của Dart"
  - slug: agent-plugins
    title: "agent-plugins: hướng dẫn thư viện & công cụ trong Flutter"
faq:
  - q: Có dùng Flutter Zero cho sản phẩm thật được không?
    a: "Không. Chính tác giả mô tả dự án là rất thô và mang tính thử nghiệm. Đã có bản engine build cho mọi nền tảng Flutter hỗ trợ và bạn build/run ứng dụng thật được, nhưng không có cam kết ổn định, không có lịch phát hành, và không có hệ sinh thái package nào được viết cho một `dart:ui` không có UI."
  - q: Flutter Zero còn dùng được lệnh flutter và plugin IDE không?
    a: "Có, và đó chính là ràng buộc thiết kế cốt lõi. `flutter create`, `flutter build` và `flutter run` hoạt động bình thường; plugin VS Code và IntelliJ vẫn chạy, trừ phần kiểm tra cây widget. Tác giả cố tình không viết lại `flutter_tool` từ đầu."
  - q: Mô hình luồng (threading) ra sao?
    a: "Toàn bộ mã Dart chạy trên platform thread. Không hỗ trợ cấu hình luồng nào khác. Đây là sự đơn giản hóa có chủ đích, và khác hẳn Flutter tiêu chuẩn nơi UI thread tách khỏi platform thread."
  - q: Vì sao lại gỡ bỏ dart:ui?
    a: "Vì nó gắn chặt với engine và được thiết kế trong những ràng buộc nay đã khác. Mô hình luồng đã thay đổi, FFI tốt hơn nhiều, gọi đồng bộ giữa Dart và nền tảng đã khả thi, và native assets cho phép package tự mang mã native. Một `dart:ui` mô-đun đóng gói dạng package giờ trông khả thi."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`flutter_zero`](https://github.com/knopp/flutter_zero) có lẽ là repo Flutter thú vị nhất năm 2026 mà gần như không ai đưa lên production. Đây là Flutter đã cắt gần hết `dart:ui` — không widget, không Skia, không Impeller — chỉ còn một runtime Dart vẫn build và chạy được bằng lệnh `flutter` thông thường. **274★**, BSD-3-Clause, cập nhật lần cuối **2026-08-08**, của [Matej Knopp](https://github.com/knopp), tác giả `flutter_reorderable_list` đã có mặt trong các app Flutter nhiều năm nay.

## Flutter Zero là gì?

Flutter Zero là một bản Flutter rút gọn, không giả định gì về lớp UI. Thứ còn lại là một runtime Dart bạn có thể triển khai tới mọi nền tảng Flutter hỗ trợ, cộng với toàn bộ chuỗi công cụ quanh nó.

Phần cuối mới là chỗ khéo. Flutter Zero không phải bản fork của repo Flutter — nó là repo mới chứa một tập con rất nhỏ, chọn sao cho checkout nhanh và dung lượng đĩa thấp. Nhưng nó vẫn tương thích với `flutter_tool`, nên `flutter create`, `flutter build` và `flutter run` đều chạy, và plugin VS Code lẫn IntelliJ vẫn hoạt động, trừ phần widget inspector vốn chẳng còn gì để kiểm tra.

## Vì sao đáng quan tâm trong năm 2026

Lập luận trong README đáng đọc trọn vẹn, nhưng tóm gọn thế này: `dart:ui` được thiết kế trong những ràng buộc nay không còn đúng nữa.

Mô hình luồng đã thay đổi. FFI tiến bộ rất nhiều. Tương tác đồng bộ hai chiều giữa Dart và API nền tảng giờ đã khả thi, khiến giao thức platform channel — bất đồng bộ, không kiểu, đặc thù từng chỗ — bớt cần thiết hẳn. Và `native assets` cho phép package thường cũng đóng góp mã native với bước build riêng.

Cộng lại, một điều bất khả thi năm 2018 nay trông khả thi năm 2026: một `dart:ui` mô-đun nằm trong package, với interface Dart tử tế và phần hiện thực FFI hoặc JNI theo từng nền tảng, thay vì một khối nguyên biên dịch thẳng vào engine.

Flutter Zero là thử nghiệm kiểm chứng nửa dưới của ý tưởng đó. Và lặng lẽ, nó cũng là con đường khả tín nhất tới lúc này để viết ứng dụng Dart với giao diện native thật sự — SwiftUI trên nền tảng Apple, Jetpack Compose trên Android — mà vẫn giữ Dart, pub và toolchain Flutter.

## Bắt đầu như thế nào

Không có package nào trên pub để cài; Flutter Zero là một biến thể engine và SDK, không phải dependency. Hãy clone repo và làm theo hướng dẫn build:

```bash
git clone https://github.com/knopp/flutter_zero.git
```

Đã có sẵn bản engine dựng trước cho mọi nền tảng Flutter hỗ trợ, nên bạn không cần tự biên dịch engine để thử. Sau đó quy trình vẫn như thường — package `examples/hello_world` trong workspace của repo là thứ nhỏ nhất chạy được.

Hãy chuẩn bị tinh thần đọc mã nguồn. Repo đủ nhỏ để việc đó là khả thi, điều không thể nói về engine Flutter chính.

## Khi nào nên nhìn tới Flutter Zero?

- bạn muốn một ứng dụng Dart trên mobile hoặc desktop với giao diện native, và phần render của Flutter là gánh nặng chứ không phải lợi thế
- bạn xây một tiến trình Dart chạy nền — daemon, CLI, agent — và muốn câu chuyện build/triển khai đa nền tảng của Flutter mà không phải mang theo bộ render
- bạn tò mò về nội tại engine và muốn một codebase đủ nhỏ để thực sự đọc hết
- bạn đang thử nghiệm một `dart:ui` thay thế và cần một môi trường chưa có sẵn cái nào

## Điểm còn hạn chế

Hãy thành thật về hiện trạng. Câu trả lời của chính tác giả cho "dùng được ngay chưa?" là "được, nhưng rất thô".

Mô hình đơn luồng là điểm gai nhất: toàn bộ mã Dart chạy trên platform thread và không hỗ trợ cấu hình nào khác. Mọi thứ giả định mô hình luồng chuẩn của Flutter đều phải nghĩ lại.

Ngoài ra, gần như cả hệ sinh thái package đều giả định `dart:ui` tồn tại. Bất kỳ package nào đụng tới widget, vẽ, ảnh hay dàn chữ đều không chạy. Bạn đang xây trên một runtime, không phải một framework, và phần thiếu là việc của bạn.

Cũng không có cam kết lộ trình nào. README xếp chuyện đặt tên vào ưu tiên thấp và mô tả việc chạy app Flutter bình thường trên nền Flutter Zero là thứ cần "rất nhiều may mắn và động lực". Hãy hiểu đúng tín hiệu đó.

## Các lựa chọn đáng so sánh

- [Denial: trình quản lý cửa sổ Wayland đặt Flutter làm nền móng](/vi/recipes/denial/) — canh bạc ngược lại, đẩy Flutter *sâu hơn* vào hệ thống thay vì gỡ nó ra
- [dart-lang/ai: bộ gói MCP chính thức của Dart](/vi/recipes/dart-mcp/) — ví dụ hiện tại khác về việc dùng Dart tốt ở nơi rất xa cây widget
- [agent-plugins: hướng dẫn thư viện & công cụ trong Flutter](/vi/recipes/agent-plugins/)

## Câu hỏi thường gặp

### Có dùng Flutter Zero cho sản phẩm thật được không?

Không. Chính tác giả mô tả dự án là rất thô và mang tính thử nghiệm. Đã có bản engine build cho mọi nền tảng Flutter hỗ trợ và bạn build/run ứng dụng thật được, nhưng không có cam kết ổn định, không có lịch phát hành, và không có hệ sinh thái package nào được viết cho một `dart:ui` không có UI.

### Flutter Zero còn dùng được lệnh flutter và plugin IDE không?

Có, và đó chính là ràng buộc thiết kế cốt lõi. `flutter create`, `flutter build` và `flutter run` hoạt động bình thường; plugin VS Code và IntelliJ vẫn chạy, trừ phần kiểm tra cây widget. Tác giả cố tình không viết lại `flutter_tool` từ đầu.

### Mô hình luồng (threading) ra sao?

Toàn bộ mã Dart chạy trên platform thread. Không hỗ trợ cấu hình luồng nào khác. Đây là sự đơn giản hóa có chủ đích, và khác hẳn Flutter tiêu chuẩn nơi UI thread tách khỏi platform thread.

### Vì sao lại gỡ bỏ dart:ui?

Vì nó gắn chặt với engine và được thiết kế trong những ràng buộc nay đã khác. Mô hình luồng đã thay đổi, FFI tốt hơn nhiều, gọi đồng bộ giữa Dart và nền tảng đã khả thi, và native assets cho phép package tự mang mã native. Một `dart:ui` mô-đun đóng gói dạng package giờ trông khả thi.

## Tài nguyên & liên kết

- **GitHub:** [knopp/flutter_zero](https://github.com/knopp/flutter_zero)
- **Giấy phép:** BSD-3-Clause
- **Đọc thêm:** [Dart interop](https://dart.dev/interop) và [dart-lang/native](https://github.com/dart-lang/native)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
