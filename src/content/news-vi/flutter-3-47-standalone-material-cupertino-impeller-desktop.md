---
title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
description: "Flutter 3.47 đưa Material và Cupertino thành package độc lập trên pub.dev, biến Impeller thành renderer mặc định trên macOS, Windows và Linux, và đưa Widget Previews lên stable."
seoDescription: "Đánh giá Flutter 3.47: package material_ui và cupertino_ui độc lập, Impeller mặc định trên desktop, Widget Previews stable, iOS tối thiểu 15, Dart 3.13 — kèm số liệu khảo sát Q2 2026."
keywords: ["flutter 3.47", "phiên bản flutter mới nhất", "material_ui package", "cupertino_ui package", "impeller desktop", "flutter widget previews", "dart 3.13"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🧩"
tags: ["Flutter 3.47", "Flutter", "Impeller", "Material", "Cupertino", "Phát hành"]
sources:
  - name: "What's new in Flutter 3.47 — Flutter Blog"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Khảo sát Flutter Q2 2026"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
  - name: "Introducing Skills for Dart and Flutter"
    url: "https://flutter.dev/blog/introducing-skills-for-dart-and-flutter"
  - name: "@FlutterDev trên X"
    url: "https://x.com/FlutterDev"
related:
  - slug: "flutter-3-44-ios-26-macos-support-web-hot-reload"
    title: "Đánh giá Flutter 3.44: hỗ trợ iOS 26, stateful hot reload trên web, và Cupertino Squircles"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Flutter 3.47 ra mắt ngày 13/08/2026, và lần này tiêu điểm không phải một tính năng — mà là một cú tách kiến trúc. Hệ thống thiết kế đang rời khỏi SDK. Cộng thêm việc Impeller thành renderer mặc định trên mọi nền tảng desktop và Widget Previews lên stable, đây là bản phát hành có ý nghĩa cấu trúc nhất của Flutter trong nhiều năm.

Con số đứng sau: **1.356 commit từ 169 người đóng góp, 66 người lần đầu tham gia**, phát hành dưới dạng `Flutter 3.47.0 • Dart 3.13.0 • DevTools 2.60.0`.

## Material và Cupertino thành package bạn tự chọn

Thay đổi ai cũng đang bàn: **`material_ui` và `cupertino_ui` giờ là package độc lập trên pub.dev**, cả hai đều đạt 1.0. Các thư viện cũ vẫn nằm trong SDK ở thời điểm này, nhưng bản trong SDK **đã được lên lịch deprecate chính thức ở bản stable tháng 11**.

Vì sao điều này quan trọng hơn vẻ ngoài của nó:

- **Design system giờ chạy theo nhịp riêng.** Thay vì chờ bản SDK hàng quý, Material và Cupertino có thể ra bản mới hàng tuần. Cupertino đặc biệt cần điều này — xem số liệu khảo sát bên dưới.
- **Bạn pin được design system độc lập với phiên bản framework.** Nâng cấp Flutter không còn đồng nghĩa nuốt trọn mọi thay đổi widget cùng lúc.
- **App không dùng cả hai thì bỏ được cả hai.** Nếu bạn ship design system tự viết hoàn toàn, cây Material thôi là dependency bắt buộc.

Việc migrate chỉ một dòng:

```bash
dart fix --apply --code=migrate_design_widgets
```

Cho giai đoạn lưng chừng — app bạn đã migrate nhưng dependency vẫn import đường dẫn cũ — có `MaterialUiCompatibilityBridge` để hai thế giới còn nói chuyện được với nhau.

## Impeller là mặc định trên macOS, Windows và Linux

Impeller thay Skia làm renderer mặc định trên cả ba nền tảng desktop. Lợi ích thực tế giống hệt thứ mobile đã nhận: **shader được biên dịch lúc build, nên hiện tượng giật do biên dịch shader biến mất**. Trên macOS, **wide gamut color cũng bật mặc định**.

Vẫn có tuỳ chọn quay lại theo từng nền tảng, nhưng blog nói thẳng rằng **các phương án fallback sẽ bị gỡ trong một bản phát hành tương lai**. Hãy coi opt-out là cửa sổ để báo lỗi, không phải chiến lược dài hạn.

## Widget Previews lên stable

Widget Preview không còn là thử nghiệm. Bản stable thêm **cache cục bộ giúp khởi động nhanh hơn** và **API theme trừu tượng**, nên một preview có thể render với nhiều theme mà không cần dựng cả vỏ ứng dụng. Nếu bạn từng thử preview ở bản trước và thấy chậm, đây là bản đáng thử lại.

## Cái giá của nâng cấp: tối thiểu iOS 15 và macOS 12

Để hỗ trợ Xcode 27, sàn phiên bản đã dâng lên:

| Nền tảng | Tối thiểu cũ | Tối thiểu mới |
| --- | --- | --- |
| iOS | 13 | **15** |
| macOS | 10.15 | **12** |

App cũng cần **áp dụng vòng đời UIScene** để tuân thủ iOS 27. Nếu bạn đã bỏ qua việc migrate này khi 3.44 cảnh báo, đây là lúc nó không còn là tuỳ chọn.

## Web: Wasm tiếp tục tiến gần mặc định

Câu chuyện WebAssembly từ lộ trình 2026 vẫn tiếp diễn. Bạn build bằng:

```bash
flutter build web --release --wasm
```

Mới ở bản này: **deferred loading thử nghiệm cho Wasm** sau cờ `--enable-wasm-deferred-loading`. Điều kiện tiên quyết vẫn vậy — chuyển khỏi `dart:html` cũ sang `package:web` trước khi mong mọi thứ chạy sạch.

Phía plugin, **92 trong 100 plugin iOS phổ biến nhất đã chuyển sang Swift Package Manager**. Kỷ nguyên CocoaPods đang kết thúc nhanh hơn phần lớn hướng dẫn nâng cấp giả định.

## Khảo sát Q2 2026 nói gì về chỗ Flutter thực sự đau

Google công bố kết quả khảo sát Q2 2026 ngay trong tuần đó — **hơn 3.500 phản hồi hoàn chỉnh, thu thập 8–22/06/2026** — và nó đọc như phần ngầm của bản phát hành này.

Tin tốt thì tốt bất thường:

- **93% hài lòng tổng thể**, trong đó **58% "rất hài lòng"** (tăng 6 điểm so với Q4 2025)
- **83% tin tưởng Flutter** đáp ứng được nhu cầu, tăng từ 77%
- Lần đầu tiên, **mọi nhóm lập trình viên đều vượt mốc 90% hài lòng**

Rồi đến ngoại lệ:

- **Cupertino widgets: 61% hài lòng, giảm 6 điểm** — mảng bị chấm thấp nhất khảo sát, so với 92% cho Dart, 91% cho Android, 90% cho core framework.

Đó chính là lý do tách Cupertino thành package ra bản hàng tuần là cách sửa, chứ không phải refactor cho vui.

Các điểm đau hàng đầu cũng gọi tên phần còn lại của bản phát hành: **độ trưởng thành nền tảng/hệ sinh thái (44%)**, do độ phức tạp của ma trận phiên bản khi nâng cấp, rồi **trải nghiệm tooling và IDE (33%)**, rồi **lỗi và độ ổn định (24%)**.

Một con số nữa đáng ngồi lại: lập trình viên tin các tính năng đã được cộng đồng "thử lửa" ở mức **41%** so với **26%** cho tính năng do Google xây, và niềm tin vào Flutter cao hơn niềm tin vào Google **hơn 20 điểm** (83% so với 62%).

## Đường xu hướng AI: agent giờ là quy trình Flutter hạng nhất

Phần AI của khảo sát là tín hiệu rõ nhất về hướng đi của hệ sinh thái. Về mức độ sử dụng:

- **Claude Code — 32%**
- **Antigravity — 23%**
- GitHub Copilot — 19%
- Cursor — 18%
- Codex — 17%

Công cụ dạng agent giờ dẫn đầu, vượt thế hệ autocomplete. VS Code (66%) và Android Studio (40%) vẫn là editor mà các agent đó chạy bên trong.

Google đang xây trực tiếp cho xu hướng đó. **Skills for Dart and Flutter**, công bố tháng 5/2026, là các bộ chỉ dẫn theo tác vụ dạy AI agent *cách* làm một việc Flutter cụ thể — năm skill đầu tiên phủ integration testing, localization, layout responsive, refactor pattern matching, và đo test coverage. Cách diễn đạt trong bài công bố là mô hình tư duy hữu ích: MCP đưa cho agent bộ công cụ; một Skill đưa cho nó bản vẽ và tay nghề. Chúng nạp dần, chỉ khi liên quan, nên giữ token ở mức thấp.

Vấn đề đang được giải là điều mọi lập trình viên Flutter dùng LLM đều gặp: framework đi nhanh hơn dữ liệu huấn luyện mô hình. Một bản như 3.47, vốn đổi đường dẫn import của hai thư viện được dùng nhiều nhất hệ sinh thái, đúng là loại thay đổi mà mô hình cũ sẽ trả lời sai một cách rất tự tin.

## Checklist nâng cấp của bạn

1. **Chạy `dart fix --apply --code=migrate_design_widgets`** và chuyển sang `material_ui` / `cupertino_ui` trước đợt deprecate tháng 11.
2. **Rà soát dependency** xem package nào còn import thư viện design trong SDK; dùng `MaterialUiCompatibilityBridge` trong lúc chờ họ.
3. **Nâng deployment target** lên iOS 15 / macOS 12 và hoàn tất migrate UIScene.
4. **Chạy thử build desktop với Impeller** — và báo lỗi ngay khi fallback Skia còn tồn tại.
5. **Thử lại Widget Previews** nếu bản thử nghiệm từng làm bạn nản.
6. **Test một bản build Wasm** và xem deferred loading có giúp bundle của bạn không.
7. **Trỏ AI agent của bạn tới Dart & Flutter Skills** để nó thôi sinh ra import kiểu 3.44.

## Kết luận

Flutter 3.47 là bản phát hành mà Flutter thôi là một khối liền. Material và Cupertino thành package bạn tự chọn phiên bản, Impeller hoàn tất cuộc tiếp quản trên desktop, và preview trở thành phần bình thường của vòng lặp phát triển. Khảo sát giải thích chiến lược: mức hài lòng cao gần như mọi nơi, Cupertino là ngoại lệ, và cho design system chạy theo lịch riêng là cách sửa mà không bắt cả SDK làm con tin. Hãy dành một buổi chiều cho việc migrate — nhưng làm trước tháng 11, khi các import cũ bắt đầu cảnh báo.
