---
title: "Impeller giờ là mặc định trên macOS, Windows và Linux"
description: "Flutter 3.47 đưa Impeller thành renderer mặc định trên cả ba nền tảng desktop. Đây là những gì thay đổi, backend nào chạy ở đâu, cách tắt, và vì sao đừng trông cậy vào nó."
seoDescription: "Hướng dẫn Impeller trên desktop Flutter: Metal trên macOS, Vulkan trên Windows và Linux, biên dịch shader lúc build, wide gamut color, và cờ tắt chính xác theo từng nền tảng."
keywords: ["impeller desktop flutter", "impeller so với skia", "giật shader flutter", "FLTEnableImpeller", "flutter vulkan windows", "renderer flutter 3.47"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "⚡"
tags: ["Flutter 3.47", "Flutter", "Impeller", "Desktop", "Hiệu năng"]
sources:
  - name: "Impeller rendering engine — flutter.dev docs"
    url: "https://docs.flutter.dev/perf/impeller"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Impeller README — flutter/flutter engine"
    url: "https://github.com/flutter/flutter/blob/main/engine/src/flutter/impeller/README.md"
  - name: "Flutter Q2 2026 survey results"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Impeller đã là renderer duy nhất trên iOS nhiều năm và mặc định trên Android API 29+ được một thời gian. Flutter 3.47 hoàn tất công việc: **Impeller giờ là mặc định trên macOS, Windows và Linux**. Chỉ còn Flutter Web chạy trên Skia.

Nếu bạn ship app desktop, đây là thay đổi trong 3.47 dễ làm app của bạn nhìn và cảm nhận khác nhất — và cũng dễ làm lộ ra một lỗi render bạn chưa từng thấy nhất.

## Vấn đề Impeller sinh ra để giải

Skia biên dịch shader **lúc chạy**, theo yêu cầu, ngay lần đầu một thao tác vẽ cụ thể xuất hiện. Đó là lý do một app Flutter có thể giật ở lần đầu bạn mở một màn hình, chạy một animation, hay áp một hiệu ứng blur cụ thể — rồi sau đó chạy mượt mãi mãi. Không phải do code của bạn. Là do renderer biên dịch một chương trình ngay giữa khung hình.

Impeller biên dịch một **tập shader nhỏ hơn, đơn giản hơn, ngoại tuyến, lúc build engine**. Các pipeline state object được dựng trước thay vì dựng theo từng khung hình. Cache là tường minh và do engine kiểm soát thay vì ngầm định. Kết quả không nhất thiết là frame rate đỉnh cao hơn — mà là nhịp khung hình *dự đoán được*, thứ mà người dùng thực sự cảm nhận là mượt.

Các mục tiêu thiết kế đáng gọi tên vì chúng giải thích những đánh đổi:

- **Hiệu năng dự đoán được** — mọi thứ biên dịch ngoại tuyến
- **Đo đạc được** — tài nguyên đồ hoạ được gắn nhãn, và animation có thể được ghi lại, lưu trữ mà không làm nhiễu thời gian khung hình
- **Khả chuyển** — shader viết một lần, chuyển đổi theo từng backend
- **API hiện đại** — dùng tính năng của Metal và Vulkan mà không bắt buộc phải có
- **Đồng thời** — công việc của một khung hình được trải ra nhiều luồng

## Backend nào chạy ở đâu

| Nền tảng | Trạng thái | Backend |
| --- | --- | --- |
| iOS | Mặc định, và là lựa chọn duy nhất | Metal |
| Android | Mặc định trên API 29+ | Vulkan, fallback OpenGL dưới 29 |
| **macOS** | **Mặc định từ 3.47** | Metal |
| **Linux** | **Mặc định từ 3.47** | Vulkan |
| **Windows** | **Mặc định từ 3.47** | Vulkan |
| Web | Chưa có | Skia |

Vulkan trên Windows và Linux là dòng đáng đọc hai lần. Tình trạng driver của người dùng giờ là một phần trong stack render của bạn theo cách trước đây không phải, và chính sự biến thiên đó là lý do bạn nên test trên phần cứng thật thay vì một máy dev duy nhất.

## Wide gamut color trên macOS

Song song với việc đổi renderer, **wide gamut color bật mặc định trên macOS**. Trên màn hình P3, các màu bão hoà sẽ render bão hoà hơn so với mặc định trước đây. Đây là hành vi đúng, nhưng là thay đổi nhìn thấy được: nếu màu thương hiệu của bạn từng được canh bằng mắt trên bản render bị kẹp về sRGB, chúng sẽ trông khác. Hãy đối chiếu bảng màu với design trước khi kết luận đó là lỗi.

## Cách tắt, theo từng nền tảng

Các lối thoát vẫn tồn tại, và release notes nói rõ rằng **các phương án fallback sẽ bị gỡ trong một bản phát hành tương lai**. Hãy dùng chúng để gỡ kẹt một mốc phát hành và để báo lỗi — không phải làm cấu hình dài hạn.

Để debug trên mọi nền tảng desktop:

```bash
flutter run --no-enable-impeller
```

Bản release, macOS — trong `Info.plist`, dưới `<dict>` cấp cao nhất:

```xml
<key>FLTEnableImpeller</key>
<false />
```

Bản release, Linux — trong `linux/runner/my_application.cc`:

```c
g_autoptr(FlDartProject) project = fl_dart_project_new();
fl_dart_project_set_enable_impeller(project, FALSE);
```

Bản release, Windows — trong `windows\runner\main.cpp`:

```cpp
flutter::DartProject project(L"data");
project.set_impeller_switch(flutter::ImpellerSwitch::Disabled);
```

Trên Android tương đương là một mục trong manifest (`io.flutter.embedding.android.EnableImpeller` đặt `false`). Trên iOS thì không có lối tắt nào cả — và đó là bản xem trước của nơi desktop đang đi tới.

## Nên test lại những gì

Đổi renderer thường làm lộ vấn đề ở một nhóm chỗ có thể đoán trước. Ưu tiên:

- **Blur và đổ bóng** — `BackdropFilter`, `ImageFilter.blur`, bóng theo elevation. Trong lịch sử đây là vùng lệch nhiều nhất giữa các renderer.
- **Custom painter và shader** — mọi thứ dùng `CustomPainter`, `FragmentProgram`, hoặc blend mode ngoài `srcOver`.
- **Render chữ ở cỡ nhỏ** — định vị subpixel và hinting khác nhau.
- **Màu trên màn hình P3** — xem phần wide gamut ở trên.
- **Cạnh clip và khử răng cưa** — nhất là clip lồng nhau với góc bo.
- **Khởi động trên GPU yếu** — đường Vulkan trên Windows và Linux là biến số mới.

Khảo sát Q2 2026 đặt mức hài lòng Windows ở **74%** và Linux ở **73%** — hai điểm nền tảng thấp nhất sau Cupertino. Desktop là nơi Flutter còn phải bù nhiều nhất, và điều đó có hai mặt: bản phát hành này là một khoản đầu tư thật cho các nền tảng đó, đồng thời cũng là vùng có nền tảng kiểm thử mỏng nhất trước đây.

## Báo lỗi cho hữu ích

Nếu bạn tìm thấy hồi quy, đội Flutter cần một bộ dữ liệu cụ thể, và các báo cáo thiếu nó thường bị đứng:

1. **Thêm tiền tố `[Impeller]` vào tiêu đề issue.**
2. Ghi **cấu hình thiết bị, gồm cả chip chính xác và phiên bản driver GPU**.
3. Đính kèm **ảnh chụp màn hình hoặc video**, lý tưởng là đặt cạnh bản `--no-enable-impeller`.
4. Đính kèm **bản export performance trace đã nén**.
5. Nêu **phiên bản và channel Flutter** từ `flutter --version`.

Bản so sánh cạnh nhau là thứ giá trị nhất. Nó biến "cái này trông sai" thành một khác biệt render tái hiện được.

## Checklist nâng cấp của bạn

1. **Build các target desktop trên 3.47** trước khi động vào bất cứ thứ gì khác.
2. **Chạy bộ visual regression**, hoặc nếu chưa có, đi tay qua năm màn hình phức tạp nhất.
3. **So với `--no-enable-impeller`** cho bất cứ chỗ nào trông lạ, để biết renderer có thực sự là nguyên nhân không.
4. **Test trên ít nhất một GPU Windows yếu** và một bản phân phối Linux bạn không dùng để phát triển.
5. **Kiểm tra lại màu thương hiệu trên màn hình P3** nếu bạn ship trên macOS.
6. **Mở issue có tiền tố `[Impeller]` ngay bây giờ**, khi fallback còn tồn tại.
7. **Đừng ship bản tắt Impeller vĩnh viễn.** Hãy ghi nó là nợ kỹ thuật kèm ngày gỡ.

## Kết luận

Impeller trên desktop là thay đổi đúng và hơi rủi ro. Mặt lợi mang tính cấu trúc: giật do shader thôi là một loại bug bạn phải săn, và nhịp khung hình trở nên dự đoán được. Cái giá là một lượt kiểm chứng lại toàn bộ lớp hiển thị, cộng thêm một phụ thuộc mới vào chất lượng driver Vulkan trên Windows và Linux. Hãy làm lượt đó ngay bây giờ, khi `--no-enable-impeller` còn tồn tại để cho bạn biết renderer có phải thủ phạm hay không — vì nó sẽ không tồn tại mãi.
