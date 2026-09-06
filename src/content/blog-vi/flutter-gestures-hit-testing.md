---
title: "Vì sao cú chạm của bạn không ăn: hit testing và đấu trường cử chỉ"
description: "Một GestureDetector phớt lờ cú chạm không phải là bị hỏng. Hoặc nó chưa từng được hit-test, hoặc nó đã thua một đấu trường mà nó không biết mình đã bước vào. Cả hai đều nhìn thấy được khi bạn biết nhìn vào đâu."
seoDescription: "Cách xử lý cử chỉ trong Flutter thật sự hoạt động: quy tắc hit testing, HitTestBehavior, đấu trường cử chỉ và phân định, detector lồng nhau, RawGestureDetector với recognizer tự viết, và chạm ra ngoài khung cha."
keywords:
  - gesturedetector flutter không hoạt động
  - giải thích hittestbehavior flutter
  - đấu trường cử chỉ flutter
  - gesturedetector lồng nhau flutter
  - chạm ngoài khung cha flutter
  - flutter rawgesturedetector recognizer
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-27"
emoji: "👆"
tags: ["Flutter", "Cử chỉ", "Hit Testing", "UI", "Gỡ lỗi"]
sources:
  - name: "Flutter — Handling gestures"
    url: "https://docs.flutter.dev/ui/interactivity/gestures"
  - name: "GestureDetector — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/GestureDetector-class.html"
  - name: "HitTestBehavior — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/HitTestBehavior.html"
  - name: "GestureArenaManager — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/gestures/GestureArenaManager-class.html"
  - name: "RawGestureDetector — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/RawGestureDetector-class.html"
  - name: "Listener — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Listener-class.html"
related:
  - slug: "flutter-custom-scroll-physics"
    title: "Scroll physics tự viết: khiến danh sách dừng đúng chỗ bạn muốn"
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
draft: false
---

Có một loại bug Flutter rất đặc trưng, đủ để ngốn cả buổi chiều. Widget đang hiển thị trên màn hình. `onTap` đã được nối. Bạn thêm một lệnh print và nó không bao giờ chạy. Không có gì trong console, không lỗi, không cảnh báo — cú chạm đơn giản là không tồn tại.

Mọi trường hợp như vậy đều thuộc một trong hai nguyên nhân. Hoặc con trỏ chưa từng tới được detector của bạn trong lúc hit testing, hoặc nó đã tới nơi và detector thua **đấu trường cử chỉ** trước một đối thủ khác. Đó là hai vấn đề khác nhau với hai cách sửa khác nhau, và chúng phân biệt được.

## Con trỏ tìm đến một widget như thế nào

Khi ngón tay chạm xuống, framework duyệt cây render từ gốc, hỏi từng render object xem điểm đó có nằm trong nó không. Kết quả là một **đường hit test**: một danh sách có thứ tự từ đối tượng sâu nhất trúng đích lên tới gốc. Sự kiện con trỏ sau đó được phát dọc theo đường này.

Ba quy tắc giải thích phần lớn những bất ngờ:

1. **Hit testing là hình học, và nó dùng cái hộp của render object.** Không phải dùng hình dạng nhìn thấy được. Một `Container` không màu và không con thì có kích thước bằng không, nên không gì trúng nó được.
2. **Cái sâu nhất trúng trước**, và sự kiện đi ngược lên từ đó.
3. **Một con nằm ngoài khung của cha thì không bị trúng**, kể cả khi nó vẫn được vẽ ra. Đây là điều bắt hụt tất cả mọi người.

Quy tắc thứ ba xứng đáng có một ví dụ, vì nó tạo ra một widget bạn nhìn thấy mà không chạm được:

```dart
SizedBox(
  height: 40,
  child: Stack(
    clipBehavior: Clip.none,   // huy hiệu được vẽ ra ngoài khung 40px
    children: [
      const Icon(Icons.notifications),
      Positioned(
        top: -12,
        child: GestureDetector(
          onTap: _dismiss,       // không bao giờ chạy: nằm ngoài khung của cha
          child: const _Badge(),
        ),
      ),
    ],
  ),
)
```

`Clip.none` cho phép huy hiệu *được vẽ* ra ngoài khung cha, nhưng hit testing vẫn dừng ở khung của cha. Cách sửa là làm cho cha đủ lớn để chứa phần bạn muốn chạm được — vẽ và hit testing là hai hệ thống riêng biệt, và chỉ một trong hai tôn trọng `Clip.none`.

## `HitTestBehavior`: công tắc ba nấc

`GestureDetector` nhận một `behavior`, và giá trị mặc định của nó phụ thuộc vào việc có con hay không. Đây là cách sửa phổ biến nhất cho tình huống "cú chạm của tôi không làm gì cả".

| Giá trị | Ý nghĩa |
| --- | --- |
| `deferToChild` | Chỉ trúng ở nơi có con bị trúng. **Mặc định khi có con.** |
| `opaque` | Trúng ở bất kỳ đâu trong khung của detector; chặn phép thử đi tiếp xuống các widget phía sau. **Mặc định khi không có con.** |
| `translucent` | Trúng ở bất kỳ đâu trong khung, và *đồng thời* cho các widget phía sau cũng trúng. |

Kiểu hỏng kinh điển:

```dart
// Chạm vào khoảng trống quanh chữ thì không có gì xảy ra.
GestureDetector(
  onTap: _select,
  child: Container(
    height: 80,
    alignment: Alignment.centerLeft,
    child: const Text('Chạm bất cứ đâu trên dòng này'),
  ),
)
```

`Container` không có màu, nên bản thân nó không tham gia hit testing; `deferToChild` nghĩa là chỉ đúng cái hộp chữ của `Text` mới chạm được. Có hai cách sửa, và cách đầu tốt hơn:

```dart
GestureDetector(
  behavior: HitTestBehavior.opaque,   // cả dòng 80px đều chạm được
  onTap: _select,
  child: /* ... */,
)
```

hoặc cấp cho `Container` một màu — kể cả `Colors.transparent` cũng tham gia, và đó là lý do `color: Colors.transparent` "sửa được một cách thần kỳ" các vùng chạm, cũng là lý do mẹo đó làm bối rối những ai chưa đọc phần này.

`translucent` dành cho trường hợp hai thứ chồng nhau đều muốn nhận sự kiện: một nền dùng để đóng panel trong khi chính panel đó vẫn nhận cú chạm.

## Đấu trường cử chỉ

Giờ tới nguyên nhân thứ hai. Giả sử con trỏ *đã* tới được detector của bạn. Nhiều recognizer dọc theo đường hit test có thể cùng quan tâm tới một con trỏ — chạm, kéo ngang, kéo dọc, nhấn giữ. Không thể tất cả cùng thắng.

Flutter giải quyết bằng một **đấu trường**. Mọi recognizer quan tâm đều bước vào, rồi:

- Một recognizer **tuyên bố thắng** khi nó đã chắc chắn (một cú kéo đã vượt `kTouchSlop`).
- Một recognizer **bỏ cuộc** khi nó chắc chắn đây không phải cử chỉ của mình (một cú chạm mà con trỏ đã di chuyển quá xa).
- Nếu tới lúc nhấc tay mà mọi bên vẫn chưa ngã ngũ, **người vào đấu trường đầu tiên thắng** theo mặc định.

Hệ quả thực dụng:

**Chạm thua kéo một khi có chuyển động.** Đó là lý do một dòng chạm được nằm trong danh sách cuộn vẫn cuộn: recognizer kéo dọc của scroll view thắng ngay khi ngón tay dịch chuyển, và cú chạm bỏ cuộc. Đó là hành vi đúng, và là lý do bạn không nên chống lại nó.

**Một `GestureDetector` nằm trong một cái khác thì cái bên trong thường thắng** với cùng loại cử chỉ, vì nó sâu hơn. Nếu bạn muốn cả hai cùng phản ứng, chúng phải là hai cử chỉ khác nhau — hoặc bạn cần `RawGestureDetector`.

**Hai cú kéo cạnh tranh trên cùng một trục là vấn đề thiết kế**, không phải vấn đề code. Một thẻ vuốt ngang được nằm trong một danh sách cuộn ngang sẽ luôn mơ hồ với cả người dùng lẫn framework.

## Gỡ lỗi: bật sự kiện lên

Flutter có một cờ toàn cục in ra mọi sự kiện con trỏ và mọi quyết định của đấu trường:

```dart
import 'package:flutter/gestures.dart';

void main() {
  debugPrintGestureArenaDiagnostics = true;
  debugPrintHitTestResults = true;   // cũng có sẵn
  runApp(const MyApp());
}
```

`debugPrintGestureArenaDiagnostics` cho thấy từng recognizer bước vào, và cái nào được "chấp nhận". Nếu recognizer của bạn không bao giờ xuất hiện, vấn đề nằm ở hit testing — hãy quay lại `HitTestBehavior` và khung bao. Nếu nó xuất hiện rồi bị từ chối, vấn đề là cạnh tranh trong đấu trường — hãy đi tìm xem cái gì đã đánh bại nó.

Chỉ một cờ này thôi đã biến phiên bản "cả buổi chiều" của con bug này thành phiên bản hai phút.

## `Listener`: nằm dưới hệ thống cử chỉ

`GestureDetector` ngồi trên một tầng thấp hơn. `Listener` cho bạn sự kiện con trỏ thô, không đấu trường, không phân định, không semantics:

```dart
Listener(
  onPointerDown: (e) => _trace('down tại ${e.position}'),
  onPointerMove: (e) => _trace('move ${e.delta}'),
  onPointerUp: (e) => _trace('up'),
  behavior: HitTestBehavior.translucent,
  child: child,
)
```

Hãy dùng nó để *quan sát* — một bản đồ nhiệt, một lớp phủ gỡ lỗi, một lớp bọc "chạm bất kỳ đâu thì reset bộ đếm nhàn rỗi". Đừng dùng nó để cài đặt hành vi chạm: bạn sẽ phải tự viết lại ngưỡng dung sai, việc tham gia đấu trường, semantics trợ năng và phản hồi theo nền tảng — những thứ `GestureDetector` đã có sẵn.

## `RawGestureDetector` và recognizer tự viết

Nằm giữa hai thứ trên là `RawGestureDetector`, cho phép bạn cấp recognizer trực tiếp — kể cả các lớp con thay đổi hành vi trong đấu trường.

Cách dùng kinh điển là "hãy để con này thắng cú kéo dọc dù phía trên có một scroll view":

```dart
RawGestureDetector(
  gestures: {
    _EagerVerticalDrag: GestureRecognizerFactoryWithHandlers<_EagerVerticalDrag>(
      () => _EagerVerticalDrag(),
      (instance) => instance
        ..onUpdate = _onDragUpdate
        ..onEnd = _onDragEnd,
    ),
  },
  child: child,
);

class _EagerVerticalDrag extends VerticalDragGestureRecognizer {
  @override
  void rejectGesture(int pointer) {
    // Giành lấy con trỏ thay vì nhường cho scrollable ở trên.
    acceptGesture(pointer);
  }
}
```

Đây là một công cụ sắc. Ghi đè `rejectGesture` nghĩa là recognizer của bạn từ chối thua, điều đó hoàn toàn đúng cho một sheet kéo được nằm trong scroll view và hoàn toàn sai ở gần như mọi chỗ khác. Chỉ dùng tới nó sau khi `debugPrintGestureArenaDiagnostics` đã cho bạn thấy bạn đang cạnh tranh với recognizer nào.

## `IgnorePointer` và `AbsorbPointer`

Hai widget cố ý phá vỡ hit testing, và liên tục bị nhầm lẫn:

- **`IgnorePointer`** — cả nhánh trở nên vô hình với hit testing. Sự kiện xuyên qua tới bất cứ thứ gì phía sau.
- **`AbsorbPointer`** — cả nhánh vẫn bị trúng, nhưng sự kiện dừng lại ở đó. Không gì phía sau nhận được, và không gì bên trong phản ứng.

Dùng `IgnorePointer` cho một lớp phủ trang trí mà bạn muốn chạm xuyên qua được. Dùng `AbsorbPointer` cho một lớp che kiểu "form đang gửi, chặn hết". Chọn nhầm cái sẽ tạo ra hoặc một giao diện chết, hoặc một giao diện mà màn hình bị vô hiệu hoá vẫn tương tác được ở dưới.

## Trình tự chẩn đoán

1. Widget có kích thước khác không chứ? Hãy kiểm tra bằng widget inspector, đừng nhìn bằng mắt.
2. Nó có nằm trong khung của cha không? `Clip.none` và các giá trị `Positioned` âm là những nghi phạm quen thuộc.
3. Có `IgnorePointer`, `AbsorbPointer`, hay một tổ tiên trong suốt nhưng `opaque` chắn đường không?
4. Đặt `behavior: HitTestBehavior.opaque`. Nếu giờ nó chạy, thì đó chính là nguyên nhân.
5. Bật `debugPrintGestureArenaDiagnostics`. Nếu recognizer của bạn không bao giờ vào đấu trường, vấn đề vẫn là hit testing. Nếu nó vào rồi thua, hãy tìm kẻ thắng.

## Câu hỏi thường gặp

**Vì sao cú chạm của tôi ăn ở giữa dòng nhưng không ăn ở mép?**

`deferToChild` với một con nhỏ hơn cả dòng. Hãy đặt `behavior: HitTestBehavior.opaque` cho detector.

**Vì sao một nút trong `ListView` lại cuộn thay vì được nhấn?**

Đấu trường đang chạy đúng như thiết kế: bất kỳ chuyển động nào vượt ngưỡng dung sai đều khiến cú kéo thắng. Một cú chạm không di chuyển vẫn kích hoạt bình thường. Đây là hành vi đúng chuẩn nền tảng trên cả Android lẫn iOS.

**Tôi nên dùng `InkWell` hay `GestureDetector`?**

`InkWell` cho bất cứ thứ gì cần trông như một control Material — nó thêm hiệu ứng gợn sóng, trạng thái focus và hover, cùng semantics đúng. `GestureDetector` cho những cử chỉ không cần phản hồi thị giác. `InkWell` cần một tổ tiên `Material` để vẽ được vệt mực.

**Hai widget cùng xử lý một cú chạm được không?**

Không, với cùng một cử chỉ trong đấu trường; kẻ thắng lấy tất. Hãy chồng thêm một `Listener` để quan sát, hoặc dùng behavior `translucent` để cả hai cùng nằm trên đường hit test cho *các loại cử chỉ khác nhau*.

**Vì sao `onTapDown` chạy mà `onTap` thì không?**

`onTapDown` chạy theo kiểu lạc quan; `onTap` chỉ chạy nếu recognizer thắng đấu trường. Thấy cái này mà không thấy cái kia là dấu hiệu rõ ràng nhất rằng có thứ khác đã thắng.

---

*Các quy tắc hit testing, ngữ nghĩa `HitTestBehavior`, cách phân định trong đấu trường và các cờ gỡ lỗi mô tả ở đây được ghi trong hướng dẫn cử chỉ cùng các trang API của Flutter đã dẫn. Trình tự chẩn đoán, cách quy về hai nguyên nhân gốc, và lời cảnh báo quanh việc ghi đè `rejectGesture` là đánh giá riêng của tôi từ việc gỡ lỗi cử chỉ theo cách này. Hành vi của recognizer có thể thay đổi giữa các bản phát hành — hãy đối chiếu với SDK bạn dùng.*
