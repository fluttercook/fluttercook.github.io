---
title: "Flutter Widget Previews đã stable: hướng dẫn thực chiến với @Preview"
description: "Widget Previews lên stable ở Flutter 3.47. Đây là cách @Preview hoạt động, đầy đủ tham số, MultiPreview, annotation tuỳ biến, và những giới hạn còn lại."
seoDescription: "Hướng dẫn Flutter Widget Previewer: tham số annotation @Preview, flutter widget-preview start, MultiPreview, biến thể theme và brightness, wrapper, và các giới hạn."
keywords: ["flutter widget preview", "annotation @preview flutter", "flutter widget previewer", "flutter 3.47 preview", "multipreview flutter", "xem trước widget flutter"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🖼️"
tags: ["Flutter 3.47", "Flutter", "Widget Preview", "Tooling", "DevTools"]
sources:
  - name: "Flutter Widget Previewer — flutter.dev docs"
    url: "https://docs.flutter.dev/tools/widget-previewer"
  - name: "Preview class — Flutter API reference"
    url: "https://api.flutter.dev/flutter/widget_previews/Preview-class.html"
  - name: "widget_previews library — Flutter API reference"
    url: "https://api.flutter.dev/flutter/widget_previews/"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Widget Previews ra mắt dạng thử nghiệm từ 3.35, và khá nhiều lập trình viên thử một lần, thấy chậm, rồi quay về hot reload. Flutter 3.47 đánh dấu nó **stable**, kèm cache build cục bộ và một API theme trừu tượng khiến tính năng này đáng nhìn lại. Nếu bạn làm design system, thư viện component, hay bất cứ thứ gì có hơn ba trạng thái hiển thị, thứ này thay đổi vòng lặp làm việc của bạn.

Lời hứa của nó hẹp và trung thực: previewer render **từng widget riêng lẻ**, không cần khởi động app, không cần điều hướng tới đúng màn hình, không cần giả lập đúng state. Đó là việc khác với hot reload, và là việc hot reload xưa nay vẫn làm dở.

## Khởi động previewer

Từ IDE — Android Studio, IntelliJ, hay VS Code — previewer tự chạy; mở tab **Flutter Widget Preview** ở sidebar. Từ terminal:

```shell
flutter widget-preview start
```

Lệnh này dựng một server cục bộ và mở môi trường xem trước trực tiếp trong trình duyệt. Build được cache trong thư mục `.widget_preview/` của project — cache này chính là lý do khởi động nhanh lên rõ rệt ở 3.47, và là thứ bạn nên thêm vào `.gitignore` nếu tooling chưa tự làm.

## Bạn có thể annotate cái gì

`@Preview` đến từ `package:flutter/widget_previews.dart` và áp dụng được cho:

- **hàm top-level** trả về `Widget` hoặc `WidgetBuilder`
- **static method** trong class trả về `Widget` hoặc `WidgetBuilder`
- **constructor và factory public của widget** không có tham số bắt buộc

Trường hợp đơn giản nhất:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

@Preview(name: 'My Sample Text')
Widget mySampleText() {
  return const Text('Hello, World!');
}
```

Không app, không `MaterialApp`, không route. Lưu file là preview cập nhật.

## Đầy đủ tham số, và chúng thực sự dùng để làm gì

Class `Preview` nhỏ gọn, đó là dấu hiệu tốt. Đây là toàn bộ bề mặt API:

| Tham số | Kiểu | Tác dụng |
| --- | --- | --- |
| `group` | `String` | Gom nhóm các preview liên quan. Mặc định `'Default'`. |
| `name` | `String?` | Nhãn hiển thị cạnh preview. |
| `size` | `Size?` | Ràng buộc kích thước nhân tạo áp lên widget. |
| `textScaleFactor` | `double?` | Tỉ lệ phóng chữ, để kiểm tra accessibility. |
| `wrapper` | `WidgetWrapper?` | Bọc widget trong một cây widget — scaffold, provider, `InheritedWidget`. |
| `theme` | `PreviewTheme?` | Trả về dữ liệu theme Material và Cupertino để áp dụng. |
| `brightness` | `Brightness?` | Độ sáng sáng/tối ban đầu. |
| `localizations` | `PreviewLocalizations?` | Cấu hình localization cho preview. |

`wrapper` là thứ khiến preview dùng được trong codebase thật. Phần lớn widget không đứng một mình — chúng cần `Scaffold`, cần theme, hoặc cần một repository được inject. Bạn cung cấp một lần:

```dart
@Preview(
  name: 'Submit button — trạng thái đang bấm',
  group: 'Form Controls',
  size: Size(240, 56),
  textScaleFactor: 1.5,
  wrapper: _inScaffold,
)
Widget submitButtonPreview() => const SubmitButton(isBusy: true);

Widget _inScaffold(Widget child) => MaterialApp(
      home: Scaffold(body: Center(child: child)),
    );
```

## Render cùng một widget theo nhiều cách

Đây là chỗ preview thắng hot reload thẳng thừng. Xếp chồng annotation để có một widget được render dưới nhiều cấu hình cùng lúc:

```dart
@Preview(group: 'Brightness', name: 'Light', brightness: Brightness.light)
@Preview(group: 'Brightness', name: 'Dark', brightness: Brightness.dark)
Widget buttonPreview() => const ButtonShowcase();
```

Khi cùng ba bốn biến thể đó lặp lại qua hàng chục component, hãy nâng chúng thành một `MultiPreview`:

```dart
final class MultiBrightnessPreview extends MultiPreview {
  const MultiBrightnessPreview();

  @override
  List<Preview> get previews => const [
        Preview(group: 'Brightness', name: 'Light', brightness: Brightness.light),
        Preview(group: 'Brightness', name: 'Dark', brightness: Brightness.dark),
      ];
}

@MultiBrightnessPreview()
Widget buttonPreview() => const ButtonShowcase();
```

## Nhúng design system vào một annotation riêng

API theme trừu tượng thêm ở 3.47 là mảnh ghép giúp thứ này mở rộng được. Thay vì lặp `theme:` trên mọi preview, hãy kế thừa `Preview` và cấp builder một lần:

```dart
final class MyCustomPreview extends Preview {
  const MyCustomPreview({
    super.name,
    super.group,
    super.size,
    super.textScaleFactor,
    super.wrapper,
    super.brightness,
    super.localizations,
  }) : super(theme: MyCustomPreview.themeBuilder);

  static PreviewThemeData themeBuilder() {
    return PreviewThemeData(
      materialLight: ThemeData.light(),
      materialDark: ThemeData.dark(),
    );
  }
}
```

Giờ mọi `@MyCustomPreview(...)` trong codebase đều render theo token thật của bạn. `PreviewThemeData` mang cả dữ liệu Material lẫn Cupertino, điều này ở 3.47 quan trọng hơn trước — khi design system chuyển sang package độc lập `material_ui` và `cupertino_ui`, preview là cách rẻ để xem một component có thực sự sống sót ở cả hai hay không.

Còn có `transform()`, cho phép annotation tuỳ biến viết lại preview lúc chạy — hữu ích khi muốn thêm tiền tố vào tên hoặc đổi theme cho cả một lớp preview mà không đụng vào chỗ gọi.

## Preview không phải golden test

Cần nói thẳng, vì nhiều nhóm nhầm hai thứ này. Preview là công cụ **soạn thảo**: nhanh, trực quan, có con người trong vòng lặp, không có assertion. Golden test là công cụ **chống hồi quy**: chậm, headless, và làm đỏ CI khi một pixel xê dịch. Preview không thay thế golden, và một preview "chạy được" chẳng chứng minh gì ngoài việc nó render ra.

Cặp đôi hữu ích là: preview trong lúc xây component, golden khi các trạng thái đã ổn định.

## Những giới hạn bạn sẽ gặp

Previewer chạy trong môi trường nền web, nên có ranh giới cứng:

1. **Không dùng được native plugin**, và không có `dart:io` hay `dart:ffi`. Mọi thứ chạm tới filesystem, platform channel, hay FFI đều không render — hãy inject một bản giả qua `wrapper`.
2. **Tham số callback phải public và constant.** Closure private sẽ không được nhận diện.
3. **Đường dẫn asset phải theo package**: dùng `'packages/my_package_name/assets/my_image.png'`, không phải `'assets/my_image.png'`.
4. **Widget không có ràng buộc kích thước** sẽ tự bị giới hạn ở khoảng 50% chiều cao và chiều rộng previewer. Truyền `size` khi điều đó bóp méo layout.
5. **Chỉ hỗ trợ một project hoặc một Pub workspace.** Hỗ trợ đa project trong IDE vẫn đang được nghiên cứu, nên một monorepo lớn có thể không sáng đèn hết.

## Áp dụng mà không phải viết lại

1. **Nâng lên 3.47** và chạy `flutter widget-preview start` một lần để chắc previewer build được project.
2. **Thêm `.widget_preview/` vào `.gitignore`.**
3. **Chọn một component lá** — nút bấm, badge, list tile — và thêm đúng một `@Preview`. Đừng bắt đầu từ cả màn hình.
4. **Viết một `wrapper`** cài theme và provider của app, rồi tái sử dụng.
5. **Nâng các biến thể lặp lại** (sáng/tối, text scale 1.0/2.0, LTR/RTL) thành `MultiPreview`.
6. **Kế thừa `Preview`** với `PreviewThemeData` của design system và chuẩn hoá theo annotation đó.
7. **Thêm golden test** cho những trạng thái bạn đã biết là đúng.

## Kết luận

Widget Previews thôi là bản demo ở 3.47. Cache khiến thời gian khởi động chấp nhận được, và các API theme là ranh giới giữa một món đồ chơi với thứ mà một nhóm design system có thể chuẩn hoá. Các giới hạn là thật — không native code, asset phải theo package, chỉ một workspace — nhưng đó là giới hạn về phạm vi, không phải về độ chín. Nếu bạn từng thử preview ở 3.35 rồi nhún vai, lời khuyên thành thật là thử lại: đây là bản phát hành mà tính năng này xứng đáng có chỗ trong vòng lặp làm việc.
