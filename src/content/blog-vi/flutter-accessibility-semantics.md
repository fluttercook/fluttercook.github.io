---
title: "Trợ năng trong Flutter: cây semantics thật sự báo cáo những gì"
description: "Flutter vẽ pixel, nên trình đọc màn hình không thể soi widget của bạn. Nó đọc một cây semantics riêng mà Flutter dựng rồi gửi sang nền tảng. Biết cái gì rơi vào cây đó — và cái gì lặng lẽ không rơi vào — chính là toàn bộ công việc."
seoDescription: "Cách trợ năng Flutter hoạt động: cây semantics, Semantics và MergeSemantics, ExcludeSemantics, live region, vùng chạm, tỉ lệ chữ, và kiểm thử bằng meetsGuideline."
keywords:
  - trợ năng flutter semantics
  - flutter trình đọc màn hình talkback voiceover
  - cách dùng widget semantics flutter
  - flutter mergesemantics excludesemantics
  - kiểm thử trợ năng flutter meetsguideline
  - kích thước vùng chạm flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-03"
emoji: "♿"
tags: ["Flutter", "Trợ năng", "Semantics", "Kiểm thử", "UI"]
sources:
  - name: "Flutter — Accessibility"
    url: "https://docs.flutter.dev/ui/accessibility-and-internationalization/accessibility"
  - name: "Semantics — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Semantics-class.html"
  - name: "SemanticsProperties — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/semantics/SemanticsProperties-class.html"
  - name: "MergeSemantics — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/MergeSemantics-class.html"
  - name: "meetsGuideline — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/flutter_test/meetsGuideline.html"
  - name: "SemanticsService — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/semantics/SemanticsService-class.html"
related:
  - slug: "flutter-theming-material3-design-tokens"
    title: "Theming Material 3 trong Flutter: vai trò màu, không phải giá trị màu"
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
draft: false
---

Bật TalkBack hoặc VoiceOver trong một ứng dụng Flutter mà chưa ai từng nghĩ tới, trải nghiệm thường rơi vào một trong ba kiểu hỏng: trình đọc màn hình đọc "nút" mà không có nhãn, nó đọc một icon trang trí và phần chữ thành hai điểm dừng riêng biệt, hoặc nó lặng lẽ bỏ qua thứ mà người dùng cần. Không cái nào trong số đó nhìn thấy được trên ảnh chụp màn hình, và đó là lý do chúng sống dai đến vậy.

Nguyên nhân nằm ở cấu trúc. Một ứng dụng Android hay iOS thuần cung cấp cho dịch vụ trợ năng một cây view thật của nền tảng để soi. Flutter thì đưa cho nó một tấm canvas. Thứ mà trình đọc màn hình thật sự đọc là **cây semantics** — một cây thứ hai, dựng song song với cây render, được Flutter tuần tự hoá rồi trao cho nền tảng. Nếu một mẩu thông tin không nằm trong cây đó, với công nghệ hỗ trợ nó không tồn tại.

## Framework cho bạn sẵn những gì

Tin tốt trước: hầu hết widget Material và Cupertino đã đóng góp semantics.

| Widget | Đóng góp gì |
| --- | --- |
| `Text` | Chuỗi chữ, dưới dạng nhãn |
| `ElevatedButton`, `IconButton`, `TextButton` | Cờ `isButton`, nhãn của con, hành động `onTap` |
| `TextField` | `isTextField`, `label`, `hint`, `value`, các hành động soạn thảo |
| `Checkbox`, `Switch`, `Radio` | Trạng thái chọn, hành động bật/tắt |
| `Image` | Chỉ `semanticLabel`, nếu bạn đặt |
| `Icon` | Chỉ `semanticLabel`, nếu bạn đặt |
| `Container`, `Padding`, `Row`, `SizedBox` | Không gì cả — chúng vô hình với semantics |

Ba dòng cuối là nơi phần lớn lỗi sinh ra. Một `IconButton` có con là `Icon` trần và không có `tooltip` sẽ tạo ra một node mang cờ nút và **hoàn toàn không có nhãn**. Trình đọc màn hình đọc "nút". Đó là một lỗi có thật, phổ biến, đang chạy trên production, và nó chỉ là một chuỗi bị thiếu.

```dart
// Đọc thành "nút" — vô dụng.
IconButton(icon: const Icon(Icons.delete), onPressed: _delete)

// Đọc thành "Xoá, nút" — và hiện tooltip khi nhấn giữ.
IconButton(
  icon: const Icon(Icons.delete),
  tooltip: 'Xoá',
  onPressed: _delete,
)
```

`tooltip` là cách sửa đúng chất Flutter cho `IconButton`, vì nó giải quyết cả vấn đề trợ năng lẫn vấn đề dễ khám phá trong cùng một thuộc tính.

## Bốn động từ của widget `Semantics`

Khi mặc định chưa đủ, `Semantics` và các anh em của nó làm bốn việc khác hẳn nhau. Chọn nhầm việc chính là cách người ta tạo ra một cây đọc lên còn tệ hơn mặc định.

**Chú thích.** `Semantics(label: ...)` thêm ý nghĩa cho một nhánh không có ý nghĩa nào:

```dart
Semantics(
  label: 'Pin, 82 phần trăm',
  excludeSemantics: true, // đồng hồ pin được vẽ ra không có gì hữu ích để nói
  child: CustomPaint(painter: BatteryGaugePainter(level: 0.82)),
)
```

**Gộp.** `MergeSemantics` gom một nhánh thành một node duy nhất, để trình đọc màn hình dừng ở đó một lần thay vì ba lần:

```dart
MergeSemantics(
  child: Row(
    children: [
      const Icon(Icons.schedule),
      const SizedBox(width: 8),
      Text('Đến nơi lúc $eta'),
    ],
  ),
)
```

`ListTile` đã tự làm điều này bên trong, nên một tile dựng đúng cách sẽ đọc thành một câu duy nhất. Các `Row` tự ghép thì không, và đó là phàn nàn phổ biến thứ hai từ người dùng trình đọc màn hình.

**Loại trừ.** `ExcludeSemantics` gỡ bỏ hẳn một nhánh. Ảnh trang trí, nền gradient, khối placeholder nhấp nháy — không cái nào nên là điểm dừng trong thứ tự đọc.

```dart
ExcludeSemantics(child: Image.asset('assets/hero_swirl.png'))
```

**Chặn.** `BlockSemantics` giấu mọi thứ được vẽ *phía sau* nó trong cùng nhánh. Đây là thứ khiến một modal thật sự là modal với trình đọc màn hình: không có nó, người dùng có thể vuốt qua dialog xuống trang bên dưới, gây mất phương hướng vì trang đó đang bị làm mờ và không bấm được. `showDialog` lo giúp bạn việc này; một lớp overlay tự dựng thì không.

## `value`, `hint`, và sự khác nhau giữa chúng

`SemanticsProperties` phân biệt nhiều chuỗi mà người ta hay nhét chung vào `label`:

- **`label`** — thứ đó *là gì*. "Âm lượng".
- **`value`** — trạng thái hiện tại. "60 phần trăm".
- **`increasedValue` / `decreasedValue`** — giá trị sẽ thành gì sau một hành động điều chỉnh, để trình đọc thông báo kết quả của cú vuốt.
- **`hint`** — điều gì xảy ra nếu tác động lên nó. "Nhấn đúp để tắt tiếng". Nên để trống khi hành động đã quá rõ; hint dài dòng tự nó cũng là một phàn nàn trợ năng phổ biến.

Một thanh trượt làm cho đúng:

```dart
Semantics(
  label: 'Âm lượng',
  value: '${(volume * 100).round()} phần trăm',
  increasedValue: '${((volume + 0.05) * 100).round()} phần trăm',
  decreasedValue: '${((volume - 0.05) * 100).round()} phần trăm',
  slider: true,
  onIncrease: () => _setVolume(volume + 0.05),
  onDecrease: () => _setVolume(volume - 0.05),
  child: ExcludeSemantics(child: _CustomVolumeBar(volume: volume)),
)
```

`Slider` của Material đã làm hết những thứ này. Ví dụ trên có ý nghĩa khi bạn tự dựng một control riêng — và tự dựng control riêng đúng là lúc trợ năng hay bị bỏ quên nhất.

## Thông báo những thứ tự thay đổi mà không cần chạm

Nội dung tự cập nhật — một lỗi form, một xác nhận "đã lưu", một bộ đếm ngược — là vô hình với trình đọc màn hình trừ khi bạn nói ra. Có hai cơ chế:

```dart
// Đọc lại node này mỗi khi nhãn của nó đổi.
Semantics(liveRegion: true, child: Text(errorMessage))

// Hoặc thông báo một sự kiện đơn lẻ, không gắn với widget nào.
SemanticsService.announce('Đã gửi tin nhắn', TextDirection.ltr);
```

Dùng `liveRegion` cho thứ đang ở trên màn hình và có thay đổi; dùng `announce` cho sự kiện thoáng qua. Cả hai đều rất dễ bị lạm dụng — một live region cập nhật mỗi frame sẽ nói đè lên mọi thứ khác mà người dùng đang cố nghe.

## Hai quy tắc không liên quan gì tới cây semantics

**Vùng chạm.** Mọi thứ tương tác được cần tối thiểu 48×48 pixel logic trên Android và 44×44 trên iOS. Một icon 24 pixel bên trong `GestureDetector` không đạt, và không chú thích semantics nào sửa được chuyện đó. `IconButton` mặc định đã đúng; `InkWell` bọc quanh một icon nhỏ thì không, trừ khi bạn cấp kích thước cho nó.

**Tỉ lệ chữ.** Người dùng có thể đặt cỡ chữ cao hơn 100% rất nhiều. Flutter tôn trọng điều đó một cách tự động, nghĩa là layout sẽ vỡ chứ không âm thầm bỏ qua thiết lập. Đó là đánh đổi đúng, nhưng nó buộc bạn phải kiểm thử ở mức phóng cao:

```dart
MediaQuery(
  data: MediaQuery.of(context).copyWith(
    textScaler: const TextScaler.linear(2.0),
  ),
  child: const MyScreen(),
)
```

Nếu câu trả lời cho việc tràn chữ là `textScaleFactor: 1.0`, thì layout đã được "sửa" bằng cách phá vỡ chính tính năng đó. Hãy dùng `Flexible`, cho phép xuống dòng, và để chiều dọc được nở ra.

## Kiểm thử để nó không tái phát

Flutter có sẵn các guideline trợ năng mà bạn có thể assert trong widget test. Đây là phần gần như không ai bật, và nó bắt tự động cả hai lỗi cơ học ở trên:

```dart
testWidgets('màn hình chính đạt các guideline trợ năng', (tester) async {
  final handle = tester.ensureSemantics();
  await tester.pumpWidget(const MyApp());

  await expectLater(tester, meetsGuideline(textContrastGuideline));
  await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
  await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));

  handle.dispose();
});
```

`labeledTapTargetGuideline` chính là cái bắt được `IconButton` không nhãn. `ensureSemantics()` là bắt buộc — không có nó, cây semantics không được dựng trong lúc test và các assert chẳng có gì để soi.

Với một node cụ thể, hãy assert thẳng vào thuộc tính của nó:

```dart
expect(
  tester.getSemantics(find.byIcon(Icons.delete)),
  matchesSemantics(label: 'Xoá', isButton: true, hasTapAction: true),
);
```

Và khi có thứ đọc sai trên thiết bị thật, hãy bật trình gỡ lỗi trực quan để nhìn đúng cái cây mà nền tảng đang nhận:

```dart
MaterialApp(showSemanticsDebugger: true, home: const HomePage())
```

Nó phủ các node semantics lên giao diện. Những node bạn tưởng là tách rời mà lại thấy bị gộp — hoặc ngược lại — sẽ giải thích ngay lập tức phần lớn các câu đọc khó hiểu.

## Câu hỏi thường gặp

**Tôi có phải chú thích mọi widget không?**

Không, và làm vậy còn khiến mọi thứ tệ hơn. Phần lớn cây nên là cấu trúc câm lặng. Hãy chú thích các control tương tác, các custom painter, và những ảnh mang ý nghĩa; loại trừ phần trang trí; gộp những `Row` mà về mặt logic là một mục.

**Vì sao widget tự viết của tôi đọc lên không có gì?**

Vì `Container`, `CustomPaint` và các widget cùng loại không tự đóng góp semantics. Hãy bọc nó trong `Semantics` với một `label`, và đặt `excludeSemantics: true` nếu phần con sinh ra tạp âm.

**Cây semantics có được dựng khi không có trình đọc màn hình nào chạy không?**

Framework dựng và duy trì nó khi một dịch vụ trợ năng yêu cầu, hoặc khi test gọi `ensureSemantics()`. Đó là lý do nó không phải chi phí thường trực trong phiên chạy bình thường, và là lý do test cần cái handle kia.

**`Tooltip` có giúp ích cho trợ năng không?**

Có — `Tooltip` đóng góp thông điệp của nó vào node semantics, và đó là lý do `IconButton(tooltip: ...)` là cách sửa được khuyến nghị thay vì bọc bằng `Semantics`.

**Còn `Semantics` bên trong danh sách thì sao?**

Mỗi mục nên là một node đã gộp. Nếu một mục danh sách đọc thành năm điểm dừng, hãy bọc mục đó trong `MergeSemantics`; nếu cả danh sách đọc thành một, bạn đã gộp ở mức quá cao.

---

*Hành vi của các widget, các hằng guideline và API `SemanticsService` mô tả ở đây lấy từ tài liệu trợ năng cùng các trang API của Flutter đã dẫn ở trên. Lời khuyên về thứ tự ưu tiên, quan điểm rằng hint dài dòng tự nó là một vấn đề trợ năng, và lập trường rằng `textScaleFactor: 1.0` là lỗi chứ không phải cách sửa — đó là đánh giá riêng của tôi. Hãy đối chiếu với bản SDK bạn phát hành — `textScaler` đã thay thế `textScaleFactor` ở một bản gần đây, và dạng cũ có thể còn hoặc không còn trong bản của bạn.*
