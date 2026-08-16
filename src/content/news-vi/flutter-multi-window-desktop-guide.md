---
title: "Đa cửa sổ trên Flutter desktop: 3.47 có gì, và hôm nay nên dùng gì"
description: "Flutter 3.47 thêm popup window trên Win32 và Linux, cửa sổ tự co theo nội dung, và đổi tên windowing API. API đa cửa sổ vẫn thử nghiệm — đây là bức tranh thực dụng."
seoDescription: "Hướng dẫn đa cửa sổ Flutter desktop: popup window trên Windows và Linux, sized-to-content, đổi tên API size và constraints, hỗ trợ --flavor, và trạng thái thử nghiệm trên channel main."
keywords: ["flutter đa cửa sổ", "flutter desktop nhiều cửa sổ", "popup window flutter", "package desktop_multi_window", "windowing api flutter", "flavor desktop flutter"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🪟"
tags: ["Flutter 3.47", "Flutter", "Desktop", "Windows", "Linux"]
sources:
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Add experimental APIs for multi-window scenarios — flutter/flutter#171720"
    url: "https://github.com/flutter/flutter/issues/171720"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "desktop_multi_window on pub.dev"
    url: "https://pub.dev/packages/desktop_multi_window"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Đa cửa sổ là món cũ nhất trong danh sách mong ước của Flutter desktop. Một app desktop không mở nổi cửa sổ thứ hai thì chưa thật sự là app desktop — không có inspector tách rời, không có panel kéo ra, không có bảng công cụ nổi, không có context menu tử tế thoát ra khỏi biên cửa sổ chính.

Flutter 3.41 ra mắt API đa cửa sổ thử nghiệm cho desktop. Flutter 3.47 lấp một lượng lớn phần đường ống bên dưới chúng. Thứ nó không làm là biến chúng thành stable, và rạch ròi được điều đó sẽ cứu bạn khỏi một quý đau đớn.

## Thực sự có gì trong 3.47

Phần việc desktop ở bản này chủ yếu ở tầng engine, và khá dày:

**Popup window.** Cả Win32 lẫn Linux đều có bản cài đặt popup window. Đây là nền móng cho menu, tooltip, và dropdown render ra ngoài biên cửa sổ cha — một loại UI mà Flutter desktop tới giờ vẫn giả lập bằng overlay.

**Cửa sổ tự co theo nội dung.** Cửa sổ regular và dialog giờ tự co theo nội dung trên Win32, và cờ `decorated` bị gỡ khỏi windowing API trong quá trình đó. Một dialog cao đúng bằng đoạn chữ của nó là chi tiết nhỏ khiến app có cảm giác bản địa.

**Một lần đổi tên API.** `preferredSize` thành **`size`**, và `preferredConstraints` thành **`constraints`**. Nếu bạn đang bám theo API thử nghiệm trên main, thay đổi này sẽ làm hỏng code của bạn, và bản thân việc đổi tên là một tín hiệu: đội ngũ đang dọn dẹp bề mặt API, thứ thường xảy ra trước khi ổn định hoá.

**Handle nền tảng giờ được phơi ra.** API đa cửa sổ có thể trao cho bạn handle cửa sổ đặc thù nền tảng — lối thoát bạn cần cho những tích hợp native mà Flutter không mô hình hoá.

**Một API public để post task sang platform thread** trên Windows. Không hào nhoáng, và cần thiết cho mọi thứ phải chạm tới Win32 từ Dart.

**Hỗ trợ `--flavor` cho build desktop Windows và Linux.** Quá muộn nhưng đã tới. Nhiều flavor build — dev, staging, production — cuối cùng cũng chạy trên desktop như trên mobile.

## Trạng thái bạn cần thấm

Cách chính đội Flutter diễn đạt trên issue theo dõi là rõ ràng. Các API đa cửa sổ là **thử nghiệm**, và mục tiêu được nêu là xây dựng độ tin cậy bằng cách để khách hàng dùng thử **trên channel main**, đồng thời giữ quyền thay đổi chúng.

Cả hai vế đều quan trọng:

- **Channel main**, không phải stable. Bạn không có các API này trên bản stable mà bạn ship.
- **Quyền thay đổi.** Việc đổi tên `preferredSize` → `size` ngay trong bản này là bằng chứng họ nói thật.

| | API thử nghiệm trong framework | `desktop_multi_window` và các package tương tự |
| --- | --- | --- |
| Channel | main | chạy trên stable |
| Ổn định API | nói rõ là có thể đổi | đánh phiên bản package, theo semver |
| Hướng dài hạn | đây là nơi Flutter đang đi tới | do cộng đồng duy trì |
| Ship được ngay | không | được, kèm các lưu ý thường thấy của package |

## Vậy hôm nay dùng gì

Nếu bạn cần đa cửa sổ trong app production trên channel stable, câu trả lời vẫn là một package cộng đồng — `desktop_multi_window` là cái phổ biến nhất. Nó tạo thêm cửa sổ native và chạy một instance engine Flutter riêng trong mỗi cửa sổ, với một kênh nhắn tin giữa chúng.

Kiến trúc đó có một hệ quả đáng hiểu trước khi áp dụng: **mỗi cửa sổ là một engine riêng, nên chúng không dùng chung state Dart.** `Provider` của bạn, `Bloc` của bạn, các singleton — không cái nào vượt qua ranh giới cửa sổ. Mọi thứ là truyền thông điệp:

```dart
// Về mặt khái niệm: mỗi cửa sổ chạy engine và entry point riêng.
// State dùng chung phải được tuần tự hoá qua một kênh, không đọc trực tiếp.
void main(List<String> args) {
  if (args.firstOrNull == 'multi_window') {
    // Entry point cửa sổ phụ — isolate riêng, state riêng.
    runApp(const SecondaryWindowApp());
    return;
  }
  runApp(const MainApp());
}
```

Hãy thiết kế theo hướng đó ngay từ đầu. Những nhóm gắn đa cửa sổ lên một app có store toàn cục duy nhất sẽ dành phần lớn thời gian để cài đặt lại việc đồng bộ state.

API thử nghiệm trong framework đi hướng khác — nhiều cửa sổ trong cùng một engine — và đó là lý do nó là câu trả lời dài hạn tốt hơn, cũng là lý do nó cần thời gian để làm cho đúng.

## Desktop đang đứng ở đâu, nhìn rộng hơn

Chút bối cảnh từ khảo sát Q2 2026: **mức hài lòng Windows là 74%, Linux 73%** — hai điểm nền tảng thấp nhất sau Cupertino. Điểm đau hàng đầu nói chung là độ trưởng thành nền tảng và hệ sinh thái, ở mức **44%**.

Đa cửa sổ là một phần lớn của lý do. Flutter desktop đã dùng được cho production nhiều năm, nhưng khoảng cách giữa "chạy được" và "cảm giác bản địa" bị lấp bằng những nguyên thuỷ quản lý cửa sổ còn thiếu. Các thay đổi ở 3.47 — popup window, sized-to-content, flavor — không hào nhoáng và nhắm thẳng vào khoảng cách đó.

## Một kế hoạch thực dụng

1. **Nếu bạn ship trên stable hôm nay**, hãy dùng một package đa cửa sổ của cộng đồng và thiết kế theo hướng truyền thông điệp giữa các engine ngay từ ngày đầu.
2. **Nếu bạn bám theo main**, hãy dùng API thử nghiệm ngay và chuẩn bị sửa các lần đổi tên ở mỗi bản. Thay đổi `preferredSize` → `size` là bản mẫu cho những gì sắp tới.
3. **Áp dụng `--flavor` trên Windows và Linux ngay lập tức.** Cái này không phải thử nghiệm và là một khoản lợi thẳng cho pipeline build của bạn.
4. **Rà lại các menu và tooltip dựa trên overlay.** Khi popup window có mặt trên channel của bạn, mọi thứ đang bị cắt ở mép cửa sổ đều sửa được cho đúng.
5. **Đừng thiết kế quanh state toàn cục dùng chung** giữa các cửa sổ. Hãy tuần tự hoá, nếu không bạn sẽ viết lại.
6. **Test hành vi cửa sổ trên thiết lập nhiều màn hình với DPI khác nhau.** Đó mới là nơi bug cửa sổ trên desktop thực sự sống.
7. **Báo lỗi cho API thử nghiệm.** Dùng thử là mục đích được nêu; phản hồi bây giờ định hình thứ sẽ ổn định hoá.

## Kết luận

Flutter 3.47 là một bản phát hành nghiêm túc cho desktop dù danh sách tính năng tiêu điểm gần như không nhắc tới desktop. Popup window trên hai nền tảng, cửa sổ tự co theo nội dung, handle nền tảng được phơi ra, và hỗ trợ flavor chính là những nguyên thuỷ buồn tẻ phân biệt một bản port với một ứng dụng có cảm giác bản địa. Bản thân API đa cửa sổ vẫn thử nghiệm và vẫn ở channel main, nên hãy ship bằng package trước — nhưng hướng đi thì không mập mờ, và việc đổi tên API ở bản này gợi ý đội ngũ đang dọn dẹp trước khi ổn định hoá chứ không còn đang dò đường.
