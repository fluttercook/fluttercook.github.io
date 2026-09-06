---
title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
description: "\"No Scaffold widget found\", \"called before initState\", \"do not use BuildContext across async gaps\" — ba lỗi nổi tiếng chung một gốc. BuildContext là tay cầm chỉ vị trí của bạn trong cây element, và mọi quy tắc về nó đều suy ra từ đó."
seoDescription: "BuildContext trong Flutter thực chất là gì, vì sao Scaffold.of lỗi ngay trong cùng một build, dependOnInheritedWidgetOfExactType hoạt động ra sao, và xử lý context sau await thế nào."
keywords:
  - buildcontext trong flutter
  - lỗi no scaffold widget found flutter
  - use_build_context_synchronously
  - dependoninheritedwidgetofexacttype
  - vì sao cần widget builder flutter
  - context mounted flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-05"
emoji: "🧭"
tags: ["Flutter", "Widgets", "Elements", "InheritedWidget", "Debugging"]
sources:
  - name: "BuildContext — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/BuildContext-class.html"
  - name: "Element — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Element-class.html"
  - name: "InheritedWidget — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/InheritedWidget-class.html"
  - name: "Builder — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Builder-class.html"
  - name: "Dart lint — use_build_context_synchronously"
    url: "https://dart.dev/tools/linter-rules/use_build_context_synchronously"
  - name: "Flutter — Architectural overview"
    url: "https://docs.flutter.dev/resources/architectural-overview"
related:
  - slug: "flutter-keys-when-they-matter"
    title: "Key trong Flutter: một quy tắc duy nhất giải thích mọi trường hợp"
  - slug: "flutter-state-management-decision-guide"
    title: "Riverpod, Bloc, signals hay setState: chọn cách quản lý state Flutter và sống chung với nó"
draft: false
---

`BuildContext` là tham số ai cũng gõ cả ngàn lần mà chẳng bao giờ hỏi nó là cái gì. Nó có mặt trong mọi hàm `build`, bị đòi bởi `Theme.of`, `Navigator.of`, `showDialog`, `MediaQuery.sizeOf` — rồi một ngày nó ném ra một lỗi chẳng hiểu nổi, kiểu `Scaffold.of()` thất bại ngay bên trong một widget rõ ràng đang được bọc bởi `Scaffold`.

Dòng khai báo giải đáp toàn bộ. Trong mã nguồn framework: `abstract class Element extends DiagnosticableTree implements BuildContext`. Một `BuildContext` **chính là** một `Element`, chỉ được phơi ra qua một giao diện hẹp để bạn không thể dùng nó sửa cây. Khi một hàm `build` nhận context, nó đang được trao **chính element của nó** — đúng vị trí của nó trong cây đang sống.

Mọi thứ khó hiểu về `BuildContext` trở nên hiển nhiên khi bạn đọc nó là "nút của tôi trong cây" thay vì "ứng dụng".

## Việc tra cứu đi ngược lên từ nút của bạn

`Theme.of(context)`, `MediaQuery.of(context)`, `Navigator.of(context)` và đồng bọn đều làm cùng một việc: bắt đầu từ element đó và đi **lên** chuỗi tổ tiên cho tới khi tìm thấy thứ cần tìm. Chúng không bao giờ nhìn xuống, cũng không nhìn ngang.

Điều đó giải thích thất bại kinh điển:

```dart
class MyPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            // Ném lỗi: không có Scaffold nào phía trên context NÀY.
            Scaffold.of(context).openDrawer();
          },
          child: const Text('Open'),
        ),
      ),
    );
  }
}
```

`context` trong closure đó là context của `MyPage`. `Scaffold` được tạo ra **bên dưới** nó, như một phần của thứ `MyPage` trả về. Đi ngược lên từ `MyPage` sẽ gặp bất cứ thứ gì bọc ngoài trang — chứ không bao giờ gặp cái `Scaffold` nằm trong nó.

Thông báo lỗi của framework nói đúng điều đó nếu bạn đọc nguyên văn: nó phàn nàn rằng context được dùng là một context "không bao gồm Scaffold". Cách sửa là tra cứu từ một nút thật sự nằm bên dưới:

```dart
Builder(
  builder: (innerContext) => ElevatedButton(
    onPressed: () => Scaffold.of(innerContext).openDrawer(),
    child: const Text('Open'),
  ),
)
```

`Builder` là widget mà toàn bộ mục đích tồn tại là tạo thêm một element để bạn có một context sâu hơn một tầng. Nó không có tác dụng thị giác nào. Nó tồn tại chỉ để đưa bạn xuống thấp hơn trong cây.

Hai lựa chọn thay thế đáng biết. Tách cây con thành một widget riêng cũng cho context mới đó và thường sạch hơn. Và riêng với `Scaffold`, `ScaffoldMessenger.of(context)` — cách hiện đại để hiện `SnackBar` — được thiết kế để tra cứu từ **phía trên** `Scaffold`, nên context ở tầng trang dùng vẫn tốt.

## `.of()` và `.maybeOf()` và `.sizeOf()`

Quy ước đặt tên xuyên suốt framework là nhất quán, và mỗi biến thể mang nghĩa khác nhau lúc chạy:

| Lời gọi | Trả về | Khi không tìm thấy | Có đăng ký nhận thay đổi |
| --- | --- | --- | --- |
| `X.of(context)` | Giá trị | Ném lỗi kèm chẩn đoán dài | Có |
| `X.maybeOf(context)` | `X?` | Trả về `null` | Có |
| `MediaQuery.sizeOf(context)` | Chỉ kích thước | Ném lỗi | Chỉ với thay đổi **kích thước** |

Dòng cuối là một công cụ hiệu năng thật sự. `MediaQuery.of(context)` khiến widget của bạn rebuild khi **bất cứ thứ gì** trong `MediaQueryData` đổi — tỉ lệ chữ, padding, view insets, độ sáng, và đáng chú ý là bàn phím trượt lên trượt xuống. Nếu tất cả những gì bạn cần là chiều rộng, `MediaQuery.sizeOf(context)` chỉ rebuild khi kích thước đổi. Cùng mẫu đó có ở `textScalerOf`, `paddingOf`, `viewInsetsOf`, `platformBrightnessOf` và nhiều hàm khác, và đổi sang bản cụ thể là một món hời miễn phí trong bất kỳ widget nào nằm phía trên bàn phím.

## "Phụ thuộc vào" một inherited widget nghĩa là gì

Chuyện đăng ký trong bảng trên không phải ẩn dụ. `Theme.of(context)` được cài đặt đại khái là:

```dart
static ThemeData of(BuildContext context) {
  final inherited = context.dependOnInheritedWidgetOfExactType<_InheritedTheme>();
  // ...
}
```

`dependOnInheritedWidgetOfExactType` làm hai việc: tìm tổ tiên gần nhất thuộc kiểu đó, **và đăng ký element của bạn làm một dependent**. Khi inherited widget đó về sau được dựng lại với dữ liệu mà `updateShouldNotify` trả về true, mọi dependent đã đăng ký sẽ bị đánh dấu bẩn. Đó là toàn bộ cơ chế lan truyền phản ứng có sẵn của Flutter — `InheritedWidget` cộng với một sổ đăng ký phụ thuộc lập chỉ mục theo element.

Vì vậy đoạn này ném lỗi:

```dart
@override
void initState() {
  super.initState();
  final theme = Theme.of(context);   // lỗi: gọi trước khi initState hoàn tất
}
```

Việc đăng ký phụ thuộc đòi hỏi element đã mount hẳn và có thể bị đánh dấu bẩn; trong lúc `initState` thì chưa. Chỗ đúng là `didChangeDependencies` (được gọi ngay sau `initState`, và gọi lại mỗi khi một phụ thuộc thay đổi) hoặc `build`.

Có một hàm anh em không đăng ký, dành cho những lúc hiếm hoi bạn muốn đọc một lần mà không gây rebuild: `getInheritedWidgetOfExactType`. Hãy dùng nó có chủ đích, và biết rằng bạn sẽ không được báo khi giá trị thay đổi.

## Context sau một `await` mới là thứ nguy hiểm

Đây là quy tắc sống sót được khi va chạm với code production, và cái lint bắt buộc nó — `use_build_context_synchronously` — bật sẵn trong `flutter_lints`.

```dart
Future<void> _save() async {
  await repository.save(draft);
  Navigator.of(context).pop();          // không an toàn
}
```

Giữa `await` và dòng kế tiếp, chuyện gì cũng có thể xảy ra: người dùng bấm back, một widget cha đã rebuild bỏ mất cây con này, route bị pop bởi một deep link. Nếu element đã bị gỡ, chuỗi tổ tiên của nó không còn, và tra cứu bất cứ thứ gì từ nó là hành vi không xác định — đó là nói nhẹ.

Cách sửa là kiểm tra, và phép kiểm tra phải nằm **sau** await, trong cùng một khối đồng bộ với chỗ sử dụng:

```dart
Future<void> _save() async {
  await repository.save(draft);
  if (!context.mounted) return;
  Navigator.of(context).pop();
}
```

`context.mounted` sinh ra đúng cho việc này và dùng được với một `BuildContext` trần, kể cả trong callback của `StatelessWidget`. Bên trong một `State`, thuộc tính `mounted` của state mang cùng ý nghĩa.

Câu trả lời tốt hơn về mặt cấu trúc, ở đâu làm được, là bắt lấy thứ bạn cần **trước** khi await:

```dart
Future<void> _save() async {
  final navigator = Navigator.of(context);
  final messenger = ScaffoldMessenger.of(context);

  await repository.save(draft);

  navigator.pop();
  messenger.showSnackBar(const SnackBar(content: Text('Đã lưu')));
}
```

`NavigatorState` và `ScaffoldMessengerState` sống lâu hơn widget đã tra cứu ra chúng, nên cách này an toàn kể cả khi widget gọi đã biến mất — và nó loại bỏ khỏi code toàn bộ loại suy nghĩ "context của tôi còn hợp lệ không".

## Dialog, và cái context bạn không được dùng lại

`showDialog` trao cho builder một context **khác**, thuộc về route của chính dialog. Nhầm lẫn hai cái đó sinh ra con bug dialog phổ biến nhất trong Flutter:

```dart
showDialog(
  context: context,
  builder: (dialogContext) => AlertDialog(
    actions: [
      TextButton(
        // Sai: pop cả trang, không phải dialog — hoặc pop cả hai.
        onPressed: () => Navigator.of(context).pop(),
        child: const Text('OK'),
      ),
    ],
  ),
);
```

Hãy dùng `dialogContext` để đóng dialog, và `context` bên ngoài cho bất cứ thứ gì thuộc về trang. Nếu dialog cần kích hoạt điều hướng sau khi đóng, hãy đóng trước rồi mới hành động trên context bên ngoài — có canh `context.mounted`, vì bản thân `showDialog` là thứ được await.

## Đọc các thông báo lỗi

Khi mô hình đã nằm sẵn trong đầu, ba lỗi lớn giải mã ngay lập tức:

- **"No Scaffold widget found. `X` widgets require a Scaffold widget ancestor."** Bạn tra cứu từ một context ngang hoặc cao hơn chỗ `Scaffold` được tạo. Thêm một `Builder`, hoặc tách widget con ra.
- **"No MaterialLocalizations found."** Gần như luôn là một lời gọi `showDialog` hay `Navigator` từ context nằm trên `MaterialApp` — thường là trong `builder:` của chính `MaterialApp`, hoặc trong widget **chính là** gốc ứng dụng. Hãy chuyển lời gọi xuống dưới `MaterialApp`.
- **"`dependOnInheritedWidgetOfExactType` was called before `initState` completed."** Một lời gọi `.of()` trong `initState` hoặc trong phần khởi tạo trường. Chuyển sang `didChangeDependencies` hoặc `build`.
- **"Looking up a deactivated widget's ancestor is unsafe."** Một context được dùng sau khi element của nó đã bị gỡ — chính là trường hợp async gap, hoặc một callback còn giữ lại sau khi đã dispose. Hãy canh `context.mounted`, hoặc bắt lấy đối tượng state từ sớm.

## Câu hỏi thường gặp

**Tôi có được cất `BuildContext` vào một trường rồi dùng sau không?**

Về kỹ thuật thì được, về thực tế thì không. Ngay khi element bị gỡ, cái context đã cất trở thành mối nguy, và chẳng có gì cảnh báo bạn. Hãy bắt lấy đúng đối tượng state bạn cần (`NavigatorState`, `ScaffoldMessengerState`) thay vào đó.

**`context` có phải cùng một đối tượng qua các lượt rebuild không?**

Với cùng một widget ở cùng vị trí thì có — element tồn tại chừng nào `Widget.canUpdate` còn trả về true. Đó chính là danh tính mà key điều khiển.

**Nếu `Builder` không vẽ gì thì nó tồn tại để làm gì?**

Để tạo ra một element, và do đó một context, thấp hơn hiện tại một tầng. Đó là toàn bộ công việc của nó: cho các lời gọi `.of()` một điểm xuất phát thấp hơn mà không phải tách ra một lớp widget mới.

**`context.mounted` đủ chưa, hay tôi cần `State.mounted`?**

Bên trong một `State` thì cái nào cũng được; chúng kiểm tra cùng một element. `context.mounted` là cái dùng được trong callback của `StatelessWidget`, nên nó là thói quen áp dụng rộng hơn.

**`MediaQuery.of` thật sự gây nhiều rebuild đến thế à?**

Trên một trang có ô nhập liệu thì có — mỗi frame animation bàn phím làm đổi `viewInsets`, và mọi dependent đều rebuild. Đổi sang `MediaQuery.sizeOf` hoặc `paddingOf` ở nơi bạn chỉ cần chừng đó là một trong những cách sửa hiệu năng rẻ nhất hiện có.

---

*Phần cơ chế mô tả ở đây — quan hệ `Element implements BuildContext`, việc đăng ký phụ thuộc trong `dependOnInheritedWidgetOfExactType`, và hành vi của lint — lấy từ tài liệu framework Flutter và trình lint Dart đã dẫn ở trên. Việc mẫu nào đáng áp dụng là nhận định riêng của tôi.*
