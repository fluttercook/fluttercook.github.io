---
title: "Stream trong Dart chuyên sâu: backpressure, broadcast và những rò rỉ ở giữa"
description: "Hầu hết lỗi stream đều rơi vào bốn loại: một subscription không bao giờ được huỷ, một stream đơn-đăng-ký bị nghe hai lần, một lỗi giết chết stream, và một nguồn phát phớt lờ pause. Đây là cách từng loại vận hành."
seoDescription: "Giải thích nội bộ Stream trong Dart: đơn đăng ký và broadcast, pause và backpressure, vòng đời StreamController, xử lý lỗi với cancelOnError, transformer, và cách tránh rò rỉ subscription."
keywords:
  - stream dart huong dan
  - stream controller broadcast
  - backpressure pause stream dart
  - ro ri stream subscription flutter
  - async generator yield dart
  - cancelOnError dart
category: "Chuyên sâu"
topic: "Dart"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-13"
emoji: "🌊"
tags: ["Dart", "Bất đồng bộ", "Stream", "Hiệu năng", "Kiến trúc"]
sources:
  - name: "Stream class — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-async/Stream-class.html"
  - name: "StreamController class — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-async/StreamController-class.html"
  - name: "StreamSubscription class — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-async/StreamSubscription-class.html"
  - name: "Asynchronous programming: streams — tài liệu Dart"
    url: "https://dart.dev/libraries/async/using-streams"
  - name: "Creating streams in Dart"
    url: "https://dart.dev/libraries/async/creating-streams"
  - name: "StreamTransformer class — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-async/StreamTransformer-class.html"
related:
  - slug: "flutter-isolates-off-main-thread"
    title: "Isolate trong Flutter: cái gì thật sự rời khỏi UI thread, cái gì thì không"
  - slug: "dart-records-and-patterns"
    title: "Record và pattern trong Dart: chúng thay thế những gì"
draft: false
---

`Bad state: Stream has already been listened to.` là lỗi đẩy phần lớn mọi người lên Stack Overflow, và câu trả lời họ tìm thấy — "dùng `.asBroadcastStream()`" — thường là cách sửa sai. Nó làm lỗi biến mất và âm thầm thay đổi ngữ nghĩa phân phối dữ liệu của bạn.

## Hai loại stream, và vì sao mặc định là loại nghiêm ngặt

Stream **đơn đăng ký** chỉ được nghe đúng một lần. Nó đệm sự kiện cho tới khi có listener, và giao mọi sự kiện cho listener đó. Đọc file, thân phản hồi HTTP và các hàm `async*` đều sinh ra loại này.

Stream **broadcast** có bao nhiêu listener cũng được, chỉ giao sự kiện cho những listener đang đăng ký, và không đệm gì cả. Listener tới muộn thì đơn giản là lỡ mất những gì đã qua.

```dart
final single = StreamController<int>();       // đơn đăng ký
final bus    = StreamController<int>.broadcast();
```

Cụm "không đệm gì cả" là mấu chốt. Chuyển một stream đơn đăng ký sang broadcast để làm im lỗi nghĩa là các sự kiện phát ra trước khi listener thứ hai gắn vào sẽ mất — không phải chậm lại, mà mất hẳn. Nếu stream mang kết quả đăng nhập và widget thứ hai của bạn đăng ký chậm một frame, nó sẽ chờ mãi mãi một sự kiện đã bắn xong.

Các cách sửa đúng, theo thứ tự ưu tiên:

1. **Nghe một lần, ở một chỗ**, rồi toả ra từ đó — một repository giữ giá trị, một `ValueNotifier`, một state container.
2. Nếu bạn thật sự cần nhiều listener độc lập, hãy tạo nguồn dưới dạng broadcast **ngay khi khởi tạo**, không phải bằng cách chuyển đổi, để mọi phía dưới đều thấy cùng một ngữ nghĩa.
3. Nếu listener tới muộn phải thấy giá trị cuối, bạn cần hành vi phát lại — tự giữ giá trị mới nhất và phát nó khi có đăng ký, hoặc dùng một package cung cấp sẵn.

## Backpressure: `pause` là một lời đề nghị, không phải bảo đảm

`StreamSubscription.pause()` đề nghị nguồn phát dừng lại. Việc nó có dừng được hay không phụ thuộc hoàn toàn vào ai đang phát.

```dart
final sub = stream.listen(handle);
sub.pause();          // đề nghị
sub.pause(future);    // tự resume khi `future` hoàn tất
sub.resume();
```

Ba nhóm nguồn phát hành xử khác nhau:

| Nguồn phát | Tôn trọng pause? | Chuyện gì xảy ra với sự kiện |
| --- | --- | --- |
| generator `async*` | có | generator dừng lại ở `yield` |
| `StreamController` có handler `onPause` | nếu bạn tự cài | mã của bạn phải ngừng đẩy |
| `StreamController` không có handler | không | sự kiện dồn trong controller, không giới hạn |
| Controller broadcast | không | sự kiện bị bỏ với listener đang tạm dừng |

Dòng thứ ba là rò rỉ bộ nhớ không ai lường trước. Nếu controller không có `onPause` và nguồn phát cứ gọi `add()`, sự kiện xếp hàng trong bộ đệm nội bộ của controller. Không có gì chặn bộ đệm đó. Nguồn phát nhanh cộng bên tiêu thụ chậm sẽ làm nó phình ra tới khi tiến trình chết.

`await for` tự động tạm dừng subscription trong suốt thời gian chạy thân vòng lặp, và đó là lý do nó là cách an toàn nhất để tiêu thụ một stream mà bạn có thể xử lý chậm:

```dart
await for (final chunk in fileStream) {
  await writeToDatabase(chunk);   // subscription đang tạm dừng ở đây
}
```

So với `stream.listen((chunk) async { await writeToDatabase(chunk); })` — callback trả về một `Future` mà stream không bao giờ chờ, nên sự kiện vẫn ùn ùn tới trong khi các lệnh ghi chất đống. **Đây là lỗi bất đồng bộ tôi gặp nhiều nhất khi review mã Flutter**, và nó không sinh ra lỗi nào cả; nó chỉ ngốn thêm bộ nhớ và hoàn thành sai thứ tự.

Nếu buộc phải dùng `listen`, hãy tạm dừng tường minh:

```dart
late final StreamSubscription<Chunk> sub;
sub = stream.listen((chunk) {
  sub.pause(writeToDatabase(chunk));  // resume khi future hoàn tất
});
```

## Lỗi kết thúc stream, trừ khi bạn nói khác đi

Mặc định, một lỗi trên stream giao tới `listen` **không** kết thúc subscription — nhưng lỗi bên trong `await for` sẽ ném ra khỏi vòng lặp, và lỗi trên subscription có `cancelOnError: true` sẽ huỷ nó.

```dart
stream.listen(
  onData,
  onError: (Object e, StackTrace s) => log(e),
  onDone: cleanUp,
  cancelOnError: false,   // mặc định: tiếp tục nghe sau lỗi
);
```

`onDone` chạy khi stream đóng lại bình thường. Nó **không** chạy khi chính bạn huỷ subscription — một sự phân biệt khiến nhiều người dọn dẹp trong `onDone` rồi thắc mắc vì sao nó chẳng bao giờ chạy.

Để giữ stream sống qua các lỗi từ một phép biến đổi, hãy xử lý lỗi ngay bên trong phép biến đổi thay vì để nó thoát ra:

```dart
stream.asyncMap((item) async {
  try {
    return Ok(await process(item));
  } catch (e) {
    return Err<Result>(e.toString());
  }
});
```

## Danh sách kiểm tra vòng đời

Gần như mọi rò rỉ stream trong ứng dụng Flutter đều là một trong số này:

- **Một subscription tạo trong `initState` mà không huỷ trong `dispose`.** Widget biến mất; callback vẫn bắn và chạm vào `setState` trên một element đã chết.
- **Một `StreamController` không bao giờ được đóng.** Hãy đóng nó trong `dispose`, và nhớ rằng đóng không huỷ listener — nó hoàn tất chúng.
- **Một subscription tạo bên trong `build`.** Nó được tạo lại mỗi lần rebuild và những cái cũ không bao giờ bị huỷ. Không bao giờ đăng ký trong `build`, không bao giờ.
- **Một controller mà `onCancel` không giải phóng tài nguyên bên dưới** — một socket, một timer, một listener nền tảng.

Hình mẫu có kỷ luật:

```dart
class _FeedState extends State<Feed> {
  StreamSubscription<Post>? _sub;

  @override
  void initState() {
    super.initState();
    _sub = widget.repository.posts.listen(_onPost, onError: _onError);
  }

  @override
  void didUpdateWidget(Feed old) {
    super.didUpdateWidget(old);
    if (old.repository != widget.repository) {
      _sub?.cancel();
      _sub = widget.repository.posts.listen(_onPost, onError: _onError);
    }
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }
  // ...
}
```

Nhánh `didUpdateWidget` là chỗ người ta hay quên. Một widget có cấu hình thay đổi vẫn giữ nguyên subscription cũ trỏ vào nguồn cũ.

Tốt hơn nữa: dùng `StreamBuilder`, nó lo hết những việc này, và chỉ với tới subscription thủ công khi bạn cần tác dụng phụ chứ không phải để render.

## Tự viết transformer

`StreamTransformer.fromHandlers` đáp ứng hầu hết nhu cầu và dễ viết đúng hơn là tự cài `bind`:

```dart
StreamTransformer<T, T> throttle<T>(Duration duration) {
  DateTime? last;
  return StreamTransformer.fromHandlers(
    handleData: (data, sink) {
      final now = DateTime.now();
      if (last == null || now.difference(last!) >= duration) {
        last = now;
        sink.add(data);
      }
    },
  );
}

searchInput.transform(throttle(const Duration(milliseconds: 300))).listen(search);
```

Chú ý điều nó không làm: nó bỏ sự kiện chứ không hoãn chúng, và nó không phát ở cuối. Đó là throttle chứ không phải debounce, và khác biệt này quan trọng với ô tìm kiếm — debounce gửi ký tự *cuối cùng*, throttle gửi ký tự *đầu tiên*. Với tìm kiếm bạn hầu như luôn muốn debounce.

## Câu hỏi thường gặp

**Khi nào dùng `async*` thay vì `StreamController`?**

`async*` khi sự kiện đến từ một vòng lặp bạn kiểm soát — nó xử lý pause đúng cách mà bạn không cần làm gì. Dùng controller khi sự kiện tới từ callback bạn không điều khiển.

**`StreamBuilder` có huỷ subscription của nó không?**

Có, khi dispose và khi thuộc tính `stream` thay đổi. Nó không đóng controller — cái đó vẫn là việc của bạn.

**Vì sao stream broadcast của tôi bỏ lỡ sự kiện đầu tiên?**

Vì listener gắn vào sau `add()` không bao giờ nhận được nó. Stream broadcast không có bộ đệm. Hãy phát sau khi đã đăng ký, hoặc tự giữ giá trị.

**`await for` có chậm hơn `listen` không?**

Không đáng kể, và nó an toàn hơn. Hạn chế thật sự của nó là bạn khó nghe hai stream song song trong cùng một hàm.

**Làm sao gộp hai stream?**

Các combinator kiểu `Stream.zip` không có trong SDK; hoặc bạn tự gộp bằng một controller, hoặc dùng package cung cấp các toán tử reactive.

---

*Ngữ nghĩa đơn đăng ký và broadcast, hành vi pause/resume, `cancelOnError`, sự khác nhau giữa `onDone` và huỷ, cùng `StreamTransformer.fromHandlers` đều nằm trong các tài liệu Dart API liên kết bên trên. Danh sách kiểm tra rò rỉ, thứ tự ưu tiên khi sửa lỗi "already listened to", cảnh báo về `didUpdateWidget` và nhận định throttle-so-với-debounce là của riêng tôi từ việc gỡ những lỗi này trong ứng dụng thật.*
