---
title: "Thu nhỏ ứng dụng Flutter: megabyte thật sự nằm ở đâu"
description: "Không ứng dụng Flutter nào nặng 40 MB vì code Dart cả. Đó là sàn kích thước của engine, là những asset chẳng ai soát, những font chẳng ai cắt bớt, và những ABI bạn đóng gói cho những thiết bị không thể chạy chúng."
seoDescription: "Cách giảm kích thước ứng dụng Flutter: sàn engine, --analyze-size và công cụ app size của DevTools, split ABI và app bundle, soát asset và font, tree shaking, và deferred component."
keywords:
  - giảm kích thước app flutter
  - flutter analyze-size devtools
  - flutter split per abi appbundle
  - flutter tree shaking icon font
  - flutter deferred components
  - tối ưu kích thước apk flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-01"
emoji: "📦"
tags: ["Flutter", "Hiệu năng", "Kích thước ứng dụng", "Build", "Phát hành"]
sources:
  - name: "Flutter — Measuring your app's size"
    url: "https://docs.flutter.dev/perf/app-size"
  - name: "Flutter — Build and release for Android"
    url: "https://docs.flutter.dev/deployment/android"
  - name: "Flutter — Deferred components"
    url: "https://docs.flutter.dev/perf/deferred-components"
  - name: "Flutter — Adding assets and images"
    url: "https://docs.flutter.dev/ui/assets/assets-and-images"
  - name: "Android Developers — Android App Bundle"
    url: "https://developer.android.com/guide/app-bundle"
  - name: "Flutter — DevTools app size tool"
    url: "https://docs.flutter.dev/tools/devtools/app-size"
related:
  - slug: "flutter-startup-time-cold-start"
    title: "Khởi động nguội trong Flutter: đo khoảng thời gian trước frame đầu tiên"
  - slug: "flutter-flavors-build-config"
    title: "Flavor trong Flutter: một codebase, ba ứng dụng, không copy-paste cấu hình"
draft: false
---

Câu chuyện về kích thước ứng dụng thường bắt đầu sau khi một người có tiếng nói so sánh file APK với đối thủ và hỏi vì sao một app ghi chú việc cần làm lại nặng 40 MB. Phản ứng của đội kỹ thuật thường là bắt đầu xoá package — vốn vừa là cần gạt đau đớn nhất, vừa thường không phải cần gạt quan trọng.

Ứng dụng Flutter có một sàn kích thước: engine, runtime Dart, Skia hoặc Impeller, và dữ liệu ICU. Cái sàn đó là thật và bạn không gỡ được. Mọi thứ nằm trên nó là của bạn, và trong hầu hết ứng dụng tôi từng xem, phần lớn cái "của bạn" đó là asset và mã native được đóng gói nhưng không dùng, chứ không phải Dart.

Nên nước đi đầu tiên không phải là xoá gì cả. Mà là đo.

## Đo trước: `--analyze-size`

```bash
flutter build apk --release --analyze-size
flutter build appbundle --release --analyze-size
flutter build ipa --release --analyze-size
```

Lệnh này in ra một bản tóm tắt và ghi một file JSON. Hãy mở file đó bằng công cụ app size trong DevTools — nó cho bạn một treemap với các ô tỉ lệ theo số byte, chia nhỏ theo package, theo asset và theo thư viện native.

Cái treemap chính là toàn bộ ý nghĩa của bước này. Nó trả lời "cái gì đang to" thay vì "mình đang thấy áy náy vì cái gì". Những phát hiện quen thuộc, đại khái theo tần suất:

- Vài file PNG xuất ở 3x từ công cụ thiết kế, không nén, mỗi cái vài megabyte.
- Hai bộ icon font, cả hai đều được nhúng đầy đủ, vì một package tự kéo bộ của nó vào.
- Một khối dữ liệu locale hoặc múi giờ mà chẳng ai biết là có.
- `libflutter.so` xuất hiện cho bốn ABI trong cùng một APK.

Không cái nào trong số đó được sửa bằng cách gỡ một dependency.

## Cần gạt lớn nhất trên Android: đừng đóng gói mọi ABI

Một APK "béo" chứa thư viện native cho `armeabi-v7a`, `arm64-v8a`, `x86_64` — mọi thiết bị tải hết về rồi dùng đúng một cái. Có hai cách sửa, và bạn nên dùng cách đầu:

```bash
# Ưu tiên: Play tự phân phối theo từng thiết bị.
flutter build appbundle --release

# Nếu bạn phát hành APK trực tiếp (sideload, chợ ứng dụng khác):
flutter build apk --release --split-per-abi
```

App bundle vốn dĩ là định dạng Play muốn, và nó tự tách theo ABI, mật độ điểm ảnh và ngôn ngữ. `--split-per-abi` cho bạn các APK riêng theo kiến trúc để phát hành trực tiếp — một khoản cắt giảm thật và tức thì, vì mỗi APK giờ chỉ mang một bản engine thay vì ba.

Nếu bạn thật sự không dùng được cách nào, tối thiểu hãy bỏ các ABI x86, vốn nhắm tới máy ảo chứ không phải điện thoại thật. Hãy làm điều đó một cách có chủ ý và ghi lại, vì nó đồng nghĩa app sẽ không cài được trên emulator x86.

## Asset: phần gần như luôn là thủ phạm nặng nhất

Asset được đóng gói nguyên xi. Không có gì nén chúng giúp bạn, không có gì thu nhỏ chúng, và không có gì cảnh báo bạn.

```bash
# Cái gì thật sự nằm trong gói, to nhất trước
find assets -type f -exec du -h {} + | sort -rh | head -30
```

Danh sách kiểm tra thu hồi được nhiều byte nhất:

**Đúng định dạng.** Ảnh chụp → WebP hoặc JPEG. Hình phẳng, logo, icon → SVG dựng lúc chạy (`flutter_svg`) hoặc PNG đã tối ưu đàng hoàng. Một file PNG 2 MB chứa ảnh chụp chính là một file JPEG 200 KB trông y hệt trên màn hình điện thoại.

**Đúng kích thước.** Một ảnh hiển thị ở 120 pixel logic không cần nguồn 2048 pixel. Hãy xuất ở kích thước lớn nhất bạn thật sự hiển thị, nhân ba, và không hơn.

**Đúng bộ độ phân giải.** Quy ước thư mục `2.0x` / `3.0x` của Flutter cho phép bạn đóng gói một ảnh vừa vặn cho mỗi mật độ thay vì một ảnh khổng lồ cho tất cả. Trên Android, app bundle sau đó chỉ phân phối đúng mật độ phù hợp.

**Không có file mồ côi.** `flutter:  assets: - assets/` nhúng cả thư mục, kể cả ba file mockup không dùng mà ai đó thả vào. Hãy khai báo thư mục một cách có chủ ý, và grep từng đường dẫn asset trước khi cho rằng nó đang được dùng.

**Font, hãy cắt bớt.** Một weight đầy đủ của font Latin nặng 150–400 KB; một họ sáu weight mà bạn dùng hai là lãng phí thuần tuý. Chỉ đóng gói những weight bạn tham chiếu. Nếu font phủ những hệ chữ bạn không hỗ trợ, dùng công cụ font để cắt bớt sẽ loại đi những glyph bạn không bao giờ vẽ.

Icon font thì được miễn phí khoản này: ở bản release, Flutter tree-shake `MaterialIcons` xuống chỉ còn những icon bạn thật sự tham chiếu, và in ra nó đã loại bao nhiêu. Tối ưu đó bị vô hiệu nếu bạn tạo `IconData` động — `IconData(codePoint)` từ một biến sẽ phá nó, vì công cụ không còn chứng minh được icon nào có thể được dùng tới.

## Tree shaking làm gì và không làm gì với Dart

Bản release được biên dịch AOT kèm tree shaking, và nó thật sự hiệu quả với code viết thẳng thắn. Những thứ đánh bại nó rất đáng biết, vì đó cũng là những thứ sinh ra câu hỏi "sao package này tận 3 MB":

- **Các mô hình giống reflection.** `dart:mirrors` hoàn toàn không có trong AOT; sinh mã tồn tại chính là vì lẽ đó.
- **Điểm vào động.** Một registry ánh xạ chuỗi sang constructor sẽ giữ sống mọi constructor.
- **Bảng const lớn.** Một bảng quốc gia/múi giờ/emoji được sinh ra là dữ liệu, và dữ liệu thì không bị rung bỏ.

Hệ quả thực dụng: hãy đo chi phí của một dependency trước và sau, thay vì phỏng đoán. Build có package, build không có, rồi so hai kết quả `--analyze-size`. Có package trông nặng nề mà chỉ tốn 30 KB; có package trông vô hại mà kéo theo cả một khối dữ liệu.

## Những cờ build thật sự thay đổi kết quả

| Cờ / thiết lập | Nền tảng | Tác dụng |
| --- | --- | --- |
| `--release` | tất cả | Không thương lượng. Bản debug chứa JIT và lớn hơn nhiều lần. |
| `--split-debug-info=<dir>` | tất cả | Đưa ký hiệu debug ra khỏi binary. Hãy giữ thư mục đó — bạn cần nó để giải mã crash. |
| `--obfuscate` | tất cả | Cần kèm `--split-debug-info`. Đổi tên ký hiệu; giảm kích thước vừa phải, mục đích thật là làm rối mã. |
| `--split-per-abi` | APK Android | Mỗi APK một bản engine thay vì nhiều bản. |
| `--tree-shake-icons` | tất cả | Bật mặc định ở release; hãy xác nhận nó không bị tắt. |
| R8 / `minifyEnabled` | Android | Thu gọn phần Java/Kotlin, gồm cả code của plugin. |

```bash
flutter build appbundle --release \
  --obfuscate --split-debug-info=build/symbols
```

Cái cần cẩn thận là `--split-debug-info`. Nó thật sự có lợi, và nó khiến stack trace trên production không đọc được trừ khi bạn giữ đúng thư mục ký hiệu của đúng bản build đó và nạp vào công cụ báo cáo crash. Hãy lưu nó trong CI cùng với artifact; một bản build mà ký hiệu đã mất là một bản build mà bạn không sửa được crash của nó.

## Deferred component, khi ứng dụng thật sự lớn

Android hỗ trợ tách một phần ứng dụng Flutter thành các module tính năng riêng, tải về theo yêu cầu, dùng import `deferred as` của Dart kết hợp Play Feature Delivery.

```dart
import 'package:my_app/admin/console.dart' deferred as admin;

Future<void> openAdminConsole() async {
  await admin.loadLibrary();
  runAdminConsole();
}
```

Đây là công cụ thật với chi phí thiết lập thật: cấu hình manifest và Gradle, một trạng thái đang tải ở mọi điểm vào, và một nhánh xử lý khi tải không xong. Nó đáng dùng cho một mảng tính năng thật sự tuỳ chọn và thật sự lớn — bảng quản trị, chế độ AR, một mô hình ML đóng kèm — và không đáng để cắt 300 KB khỏi màn hình cài đặt.

## Một trình tự thao tác

1. Chạy `--analyze-size` và mở treemap. Ghi lại mười mục đứng đầu.
2. Chuyển sang app bundle hoặc `--split-per-abi`. Đo lại.
3. Soát asset — định dạng, kích thước, file mồ côi, font. Đo lại.
4. Bật `--split-debug-info` và R8, lưu ký hiệu. Đo lại.
5. So sánh từng dependency bạn nghi ngờ, mỗi lần một cái.
6. Đến giờ mới cân nhắc deferred component.

Mỗi bước kết thúc bằng "đo lại" là có lý do: rất dễ tốn cả ngày cho một thay đổi đáng 40 KB trong khi một asset 6 MB vẫn nằm nguyên đó.

## Câu hỏi thường gặp

**Vì sao kích thước tải về nhỏ hơn file APK?**

Play báo kích thước phân phối đã nén, và app bundle loại bỏ những gì thiết bị đó không cần. Hãy so sánh cùng loại số liệu: con số quan trọng với người dùng là "download size" trên Play Console cho một thiết bị tiêu biểu, không phải file trên ổ đĩa của bạn.

**Chênh lệch kích thước giữa Skia và Impeller có đáng kể không?**

Cả hai đều thuộc sàn engine và bạn không chọn chúng vì kích thước. Thành phần engine thay đổi giữa các bản Flutter; hãy đo bản build của chính bạn thay vì suy luận từ một bài blog cũ.

**Ứng dụng nhỏ hơn có đáng đánh đổi thời gian kỹ thuật không?**

Nó tương quan với tỉ lệ cài đặt hoàn tất, đặc biệt trên kết nối chậm và máy giá rẻ, và là ràng buộc cứng ở những thị trường có giới hạn dung lượng cài qua mạng di động. Việc đó có đáng một tuần hay không là quyết định sản phẩm — nhưng đo thì mất một giờ, và hai cách sửa đầu tiên thường chỉ là đổi một cờ build.

**Gỡ package có giúp nhiều không?**

Ít hơn người ta tưởng, trừ khi package đó mang theo asset hoặc một bảng dữ liệu. Hãy đo chênh lệch trước khi mổ xẻ đồ thị dependency.

**Vì sao kích thước tăng vọt sau khi nâng cấp Flutter?**

Sàn engine dịch chuyển giữa các bản phát hành. Hãy so kết quả `--analyze-size` của hai phiên bản; nếu phần tăng nằm ở engine chứ không phải code của bạn, thì không có gì để sửa ở phía bạn.

---

*Các cờ build, công cụ và cơ chế deferred component mô tả ở đây được ghi trong các hướng dẫn về app size, phát hành Android và deferred components của Flutter đã dẫn ở trên. Trình tự thao tác, việc nhấn mạnh asset hơn dependency, và lời khuyên lưu thư mục ký hiệu trong CI là đánh giá riêng của tôi dựa trên việc phân tích ứng dụng theo cách này. Hành vi của cờ và kích thước engine thay đổi giữa các bản phát hành — hãy đo bản build của chính bạn.*
