---
title: "Tìm rò rỉ bộ nhớ trong Flutter: năm loại đối tượng không bao giờ được dispose"
description: "Rò rỉ bộ nhớ trong Flutter rất nhàm chán, và đó là lý do chúng sống dai. Gần như tất cả đều thuộc một trong năm mô-típ, và DevTools chỉ đúng đường tham chiếu giữ lại nếu bạn biết bấm hai nút nào."
seoDescription: "Cách tìm và sửa rò rỉ bộ nhớ trong Flutter: memory view của DevTools, chụp và so sánh heap, đường tham chiếu giữ lại, controller và listener không được dispose, stream subscription, và bộ nhớ ảnh."
keywords:
  - rò rỉ bộ nhớ flutter devtools
  - so sánh heap snapshot flutter
  - flutter dispose controller listener
  - huỷ stream subscription flutter
  - bộ nhớ image cache flutter
  - đường giữ tham chiếu flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-30"
emoji: "🧠"
tags: ["Flutter", "Hiệu năng", "Bộ nhớ", "DevTools", "Gỡ lỗi"]
sources:
  - name: "Flutter — Use the Memory view"
    url: "https://docs.flutter.dev/tools/devtools/memory"
  - name: "State.dispose — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/State/dispose.html"
  - name: "ChangeNotifier — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/ChangeNotifier-class.html"
  - name: "StreamSubscription — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-async/StreamSubscription-class.html"
  - name: "ImageCache — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ImageCache-class.html"
  - name: "WeakReference — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-core/WeakReference-class.html"
related:
  - slug: "flutter-lists-performance-builder"
    title: "Vì sao ListView của bạn chậm, và bốn cách sửa thật sự có tác dụng"
  - slug: "flutter-startup-time-cold-start"
    title: "Khởi động nguội trong Flutter: đo khoảng thời gian trước frame đầu tiên"
draft: false
---

Rò rỉ bộ nhớ trong Flutter hiếm khi tự khai báo. Ứng dụng chạy được, test xanh, rồi ai đó chuyển qua lại giữa hai màn hình bốn mươi lần và tiến trình đứng ở mức 900 MB. Trên một máy Android tầm trung, kết cục là bị hệ thống giết vì hết bộ nhớ, và bạn nhận được báo cáo "app tự đóng" mà không có stack trace nào.

Dart có bộ thu gom rác, nên rò rỉ ở đây chỉ có đúng một nghĩa: **vẫn còn thứ gì đó giữ tham chiếu tới một đối tượng bạn đã dùng xong**. Toàn bộ cuộc điều tra là đi tìm cái "thứ gì đó" ấy.

## Năm mô-típ

Trên thực tế, gần như mọi vụ rò rỉ tôi từng truy trong ứng dụng Flutter đều thuộc một trong số này.

**1. Controller không bao giờ được dispose.** `AnimationController`, `TextEditingController`, `ScrollController`, `TabController`, `PageController` — cái nào cũng giữ listener và, với trường hợp animation, còn giữ một ticker đã đăng ký với bộ lập lịch.

```dart
class _EditorState extends State<Editor> with SingleTickerProviderStateMixin {
  late final _text = TextEditingController();
  late final _anim = AnimationController(vsync: this, duration: _kFade);
  late final _scroll = ScrollController();

  @override
  void dispose() {
    _text.dispose();
    _anim.dispose();
    _scroll.dispose();
    super.dispose();
  }
}
```

Một `AnimationController` không `dispose` sẽ tiếp tục tick sau khi widget của nó biến mất — vừa là rò rỉ vừa là công việc frame lãng phí, và cuối cùng Flutter sẽ assert về một `TickerProvider` đã bị huỷ.

**2. Listener được thêm mà không bao giờ gỡ.** Cùng hình dạng nhưng dễ bỏ sót hơn, vì đối tượng bạn làm rò rỉ không phải cái bạn tạo ra.

```dart
@override
void initState() {
  super.initState();
  widget.model.addListener(_onModelChanged);
}

@override
void dispose() {
  widget.model.removeListener(_onModelChanged);
  super.dispose();
}
```

`ChangeNotifier` ở đây sống lâu hơn widget — nó là model của ứng dụng. Vì nó giữ `_onModelChanged`, và closure đó giữ `this`, nên model giữ `State` của bạn, cái này giữ `Element` của nó, cái này giữ cả một nhánh cây. Một lần thiếu `removeListener` giữ lại nguyên một màn hình.

Biến thể hỏng theo cách tinh vi hơn: `didUpdateWidget` khi `widget.model` đổi danh tính. Nếu bạn chỉ thêm trong `initState`, bạn sẽ nghe cái model cũ mãi mãi.

```dart
@override
void didUpdateWidget(covariant MyWidget old) {
  super.didUpdateWidget(old);
  if (old.model != widget.model) {
    old.model.removeListener(_onModelChanged);
    widget.model.addListener(_onModelChanged);
  }
}
```

**3. Stream subscription không bao giờ được huỷ.** Cùng cơ chế, khác API, và hậu quả tệ hơn vì callback vẫn tiếp tục chạy.

```dart
StreamSubscription<Position>? _sub;

@override
void initState() {
  super.initState();
  _sub = locationStream.listen(_onPosition);
}

@override
void dispose() {
  _sub?.cancel();
  super.dispose();
}
```

Một lệnh `setState` từ subscription huỷ quá muộn chính là nguồn gốc của "setState() called after dispose()". Lỗi đó là phiên bản thân thiện của con bug này; phiên bản không thân thiện là giữ lại bộ nhớ trong im lặng.

**4. Biến toàn cục hoặc singleton tích tụ dần.** Một cache không có cơ chế loại bỏ, một danh sách các request cũ giữ lại "để gỡ lỗi", một `static Map<String, BuildContext>`. Bất cứ thứ gì với tới được từ biến cấp cao nhất, theo định nghĩa, sẽ với tới được mãi mãi.

Trường hợp `BuildContext` đáng được cảnh báo riêng: lưu một context ra ngoài widget sở hữu nó sẽ giữ lại nguyên nhánh element, và context đã lưu trở nên vô hiệu ngay khoảnh khắc widget đó bị gỡ. Nếu bạn thấy mình đang giữ một cái, thì thiết kế đã sai.

**5. Ảnh.** `ImageCache` của Flutter giữ ảnh đã giải mã, và kích thước sau giải mã là rộng × cao × 4 byte, không phải kích thước file. Một tấm ảnh 4000×3000 chiếm khoảng 48 MB bộ nhớ bất kể file JPEG chỉ 2 MB trên đĩa. Một màn hình thư viện ảnh giải mã bốn mươi tấm như thế ở độ phân giải gốc không rò rỉ theo nghĩa chặt — nó đang làm đúng điều bạn yêu cầu — nhưng kết cục thì như nhau.

## Tìm nó bằng DevTools

Memory view cho bạn ba công cụ. Hãy dùng theo thứ tự này.

**Biểu đồ, để xác nhận có rò rỉ hay không.** Thực hiện thao tác bị nghi ngờ mười lần — đẩy một màn hình vào, pop ra, lặp lại — với một lần GC thủ công giữa các vòng. Bộ nhớ bậc thang đi lên và không bao giờ xuống là rò rỉ. Bộ nhớ răng cưa lên xuống là cấp phát bình thường.

**So sánh snapshot, để tìm class nào đang rò.** Đây là phần biến việc đoán thành việc biết:

1. Chụp một heap snapshot.
2. Thực hiện luồng bị nghi ngờ (mở màn hình, đóng lại) vài lần.
3. Ép GC.
4. Chụp snapshot thứ hai và so sánh.

Class nào có số thể hiện tăng đúng bằng số lần lặp chính là chỗ rò của bạn. Thấy `_ProfileScreenState` có mười thể hiện trong khi chỉ tồn tại một màn hình duy nhất — đó là toàn bộ chẩn đoán.

**Đường tham chiếu giữ lại, để tìm ai đang giữ nó.** Chọn thể hiện bị rò và DevTools hiện chuỗi tham chiếu từ một gốc GC xuống tới nó. Hãy đọc từ dưới lên; mục đầu tiên khiến bạn ngạc nhiên chính là con bug. Ở mô-típ 2 phía trên, đường đó đọc đại khái: model tĩnh của ứng dụng → danh sách listener → closure → `_ProfileScreenState`.

Đường đó chính là câu trả lời. Mọi thứ trước bước này chỉ để xác nhận có rò rỉ; bước này nói cho bạn phải sửa dòng nào.

## Làm cho rò rỉ ồn ào lên thay vì im lặng

Framework có sẵn một bộ theo dõi rò rỉ dành đúng cho các vòng đời đối tượng này. Trong test, `flutter_test` có thể được cấu hình để fail khi một đối tượng cần huỷ sống lâu hơn phạm vi mong đợi, biến cả một lớp lỗi bộ nhớ trên production thành CI màu đỏ. Các nút điều chỉnh có sẵn thay đổi giữa các bản phát hành, nên hãy kiểm tra phiên bản bạn đang dùng — nhưng nếu dự án của bạn chưa bật nó ở đâu cả, thì bật nó là một giờ đáng giá hơn bất kỳ cuộc săn rò rỉ đơn lẻ nào.

Ngoài công cụ, ba thói quen ngăn được phần lớn năm mô-típ trên:

**Mỗi `add` phải có một `remove` trong cùng class.** Hãy viết `dispose` ngay sau `initState`, trước cả khi tính năng chạy được. Thêm sau sẽ khó hơn nhiều.

**Ưu tiên widget tự quản vòng đời của nó.** `StreamBuilder` tự huỷ subscription của mình. `AnimatedBuilder` với một controller mà bạn dispose thì ổn. Một lệnh `listen` thủ công trong `initState` mới là hình dạng rủi ro.

**Hãy đặt giới hạn cho cache.** Một LRU có ngưỡng kích thước do bạn chọn có chủ ý là một cache; một `Map` mà bạn chỉ có chèn vào là một chỗ rò rỉ với ý định tốt.

## Riêng về ảnh

```dart
Image.network(
  url,
  cacheWidth: 400,   // giải mã theo kích thước hiển thị, không theo kích thước gốc
  cacheHeight: 300,
)

// Giới hạn cache toàn cục
PaintingBinding.instance.imageCache
  ..maximumSize = 100                 // số mục
  ..maximumSizeBytes = 50 << 20;      // 50 MB

// Xả nó khi hệ điều hành đòi bộ nhớ về
PaintingBinding.instance.imageCache.clear();
```

`cacheWidth` là dòng có đòn bẩy cao nhất trong một ứng dụng nhiều media. Nó thay đổi chính quá trình giải mã, nên một thumbnail tốn bộ nhớ của thumbnail thay vì bộ nhớ của ảnh gốc. `ResizeImage` là cùng ý tưởng nhưng gói dưới dạng `ImageProvider`, cho những trường hợp bạn kiểm soát provider chứ không phải widget.

Cũng hãy xử lý `didHaveMemoryPressure` nếu ứng dụng của bạn tự giữ cache lớn — nền tảng có báo cho bạn, và phớt lờ nó khiến ứng dụng của bạn thành cái bị hệ điều hành giết.

## Câu hỏi thường gặp

**`setState` sau `dispose` có làm rò rỉ bộ nhớ không?**

Bản thân lỗi đó là triệu chứng, không phải chỗ rò — nhưng thứ vẫn còn có thể gọi `setState` thì theo định nghĩa vẫn đang giữ `State` của bạn, nên nó thường đúng là một chỗ rò.

**Tôi có nên dùng `WeakReference` không?**

Hiếm khi. Nó tồn tại, và là công cụ đúng cho một cache không nên giữ sống các khoá của nó, nhưng dùng nó để "sửa" một chỗ rò thường có nghĩa là mô hình sở hữu chưa rõ ràng. Hãy sửa quyền sở hữu trước.

**Closure có bắt nhiều hơn tôi tưởng không?**

Có — đó chính là cơ chế đứng sau mô-típ 2 và 3. Closure bắt các biến nó tham chiếu, và một tear-off phương thức như `_onModelChanged` bắt `this`, nghĩa là bắt cả `State`.

**Heap phình lên có luôn là rò rỉ không?**

Không. GC của Dart theo thế hệ và không chạy theo một lịch mà bạn đoán trước được. Hãy ép GC trước khi kết luận bất cứ điều gì, và đo cái đáy sau khi thu gom thay vì đo đỉnh.

**Tôi phân tích bộ nhớ ở chế độ release được không?**

DevTools cần VM service, nên hãy dùng chế độ profile. Rò rỉ chỉ xảy ra ở release là có thể nhưng hiếm; đồ thị tham chiếu vẫn như nhau.

---

*Quy trình DevTools, hợp đồng huỷ đối tượng và hành vi `ImageCache` mô tả ở đây được ghi trong hướng dẫn công cụ bộ nhớ của Flutter và các trang API đã dẫn. Cách chia năm mô-típ, thứ tự điều tra, và lập trường rằng một cache không giới hạn là một chỗ rò là đánh giá riêng của tôi từ việc gỡ lỗi ứng dụng theo cách này. Các API theo dõi rò rỉ trong `flutter_test` đã đổi qua các bản phát hành — hãy kiểm tra SDK của bạn cung cấp những gì.*
