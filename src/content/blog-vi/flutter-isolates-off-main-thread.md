---
title: "Isolate trong Flutter: cái gì thật sự rời khỏi UI thread, cái gì thì không"
description: "async/await không đẩy việc sang thread khác — nó chỉ tạo ra điểm tạm dừng. Bài này giải thích điều đó gây jank ra sao, và compute, Isolate.run, worker sống lâu, TransferableTypedData cùng BackgroundIsolateBinaryMessenger ghép vào nhau thế nào."
seoDescription: "Vì sao async/await vẫn chặn UI thread của Flutter, và cách dùng compute, Isolate.run, isolate sống lâu với SendPort/ReceivePort, cùng platform channel từ background isolate."
keywords:
  - isolate trong flutter
  - async await có tạo thread không
  - flutter compute và isolate run
  - isolate sống lâu sendport flutter
  - backgroundisolatebinarymessenger ensureinitialized
  - transferabletypeddata flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧵"
tags: ["Flutter", "Dart", "Isolates", "Performance", "Concurrency"]
sources:
  - name: "Flutter — Concurrency and isolates"
    url: "https://docs.flutter.dev/perf/isolates"
  - name: "Dart — Isolates"
    url: "https://dart.dev/language/isolates"
  - name: "Isolate.run — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-isolate/Isolate/run.html"
  - name: "compute — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/compute.html"
  - name: "TransferableTypedData — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-isolate/TransferableTypedData-class.html"
  - name: "BackgroundIsolateBinaryMessenger — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/services/BackgroundIsolateBinaryMessenger-class.html"
  - name: "RootIsolateToken — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/RootIsolateToken-class.html"
  - name: "Flutter — Performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
draft: false
---

Hiểu lầm đắt đỏ nhất khi tối ưu hiệu năng Flutter là nghĩ `async` nghĩa là "chạy ở thread khác". Không phải. Đánh dấu một hàm là `async` không thay đổi chút nào chuyện thân hàm chạy ở đâu — mọi câu lệnh vẫn chạy trên isolate đã gọi nó, mà trong app Flutter thì gần như luôn là **UI isolate**, chính cái isolate đang build widget và chạy animation cho bạn.

Thứ `await` mang lại là một **điểm tạm dừng** (suspension point). Hàm chạy tới `await` đầu tiên, trả quyền điều khiển về event loop, rồi tiếp tục khi future được await hoàn tất. Giữa hai điểm tạm dừng, code của bạn chiếm trọn thread và không có gì khác — không cú chạm nào, không frame nào — được chen vào. Một `jsonDecode` mất 200 ms bên trong hàm `async` sẽ chặn đủ 200 ms, rắc bao nhiêu `await` xung quanh cũng không đổi.

Cách sửa là dùng isolate thứ hai: bộ nhớ riêng, event loop riêng, chạy song song thật trên máy nhiều nhân. Phần đó dễ. Phần khiến người ta mắc kẹt là mọi thứ xung quanh nó — cái gì được phép đi qua ranh giới, vì sao một closure bắt `this` lại ném lỗi, vì sao `rootBundle` biến mất ở phía kia, và vì sao lời gọi plugin thất bại cho tới khi bạn đưa cho background isolate một **root isolate token**.

## `async` cho bạn một điểm tạm dừng, không phải một thread

Đây là hình dạng của đoạn code gây ra phần lớn jank lẽ ra tránh được:

```dart
Future<List<Photo>> loadPhotos(Uri uri) async {
  final response = await http.get(uri);                    // really off-thread
  final decoded = jsonDecode(response.body) as List<Object?>;  // UI thread
  return decoded                                            // UI thread
      .cast<Map<String, Object?>>()
      .map(Photo.fromJson)
      .toList();
}
```

Chỉ dòng đầu là chạy song song thật, và không phải nhờ `await` — mà vì phần việc socket diễn ra ngoài Dart heap, VM chỉ hoàn tất future khi bytes về tới. Dòng hai và ba là Dart đồng bộ thuần túy chạy trên UI isolate. Nếu payload nặng vài megabyte, phần decode cộng với việc cấp phát trong `map` là một khối công việc liền mạch nằm chắn giữa hai frame.

Bạn có thể quan sát cơ chế này trực tiếp:

```dart
Future<void> demo() async {
  await null;                          // really suspends: drains microtasks
  for (var i = 0; i < 500000000; i++) {} // no awaits, no yields, no frames
}
```

`await null` đúng là tạm dừng và lên lịch lại. Vòng lặp sau nó thì không nhường gì cả. Dart không có preemption: event loop chỉ chạy được event kế tiếp khi code của bạn trả quyền về cho nó.

Cái giá phải trả phụ thuộc vào tần số quét bạn nhắm tới:

| Tần số quét | Ngân sách frame | Số frame mất vì khối 200 ms |
| --- | --- | --- |
| 60 Hz | 16,7 ms | ~12 |
| 90 Hz | 11,1 ms | ~18 |
| 120 Hz | 8,3 ms | ~24 |

Trên điện thoại 120 Hz, ngân sách chỉ còn khoảng một nửa so với giả định của phần lớn lời khuyên về hiệu năng, và cùng khối lượng công việc đó khiến bạn mất gấp đôi số frame.

## Một phần việc của bạn vốn đã nằm ngoài UI thread

Trước khi chuyển bất cứ thứ gì đi, hãy kiểm tra xem nó có từng nằm trên UI thread hay không. Engine của Flutter chạy nhiều task runner, và Dart UI isolate chỉ là một trong số đó. Những việc vốn đã ở nơi khác:

- **I/O socket và file** qua các API bất đồng bộ của `dart:io`. `File.readAsBytes()` không chặn isolate của bạn trong lúc đọc đĩa.
- **Rasterization.** Việc biến layer tree thành lệnh GPU diễn ra trên raster thread. Frame chậm ở đó là một bug khác, cách sửa khác.
- **Giải mã ảnh.** Flutter decode và resize ảnh ngoài UI thread; `dart:ui` phơi ra API bất đồng bộ chính là để làm được điều đó.

Thứ *không* sẵn nằm ngoài UI thread là mọi việc CPU thuần Dart do chính bạn viết: `jsonDecode`/`jsonEncode` trên payload lớn và phần map sang object sau đó, hashing, mã hóa và nén viết bằng Dart, xử lý ảnh theo từng pixel (khác với giải mã), sắp xếp hay gom nhóm danh sách hàng chục nghìn phần tử, và regex trên chuỗi lớn — thứ có thể chậm hơn nhiều so với kích thước đầu vào gợi ý.

Quy tắc trong tài liệu Flutter thẳng thắn một cách dễ chịu: chỉ dùng isolate khi một phép tính mất nhiều thời gian hơn khoảng cách giữa hai frame. Không sớm hơn.

## `Isolate.run` là câu trả lời trọn vẹn cho việc chạy một lần

`Isolate.run` sinh một isolate, chạy callback, trả về giá trị, rồi tắt isolate đó. Áp vào ví dụ trên:

```dart
import 'dart:convert';
import 'dart:isolate';

Future<List<Photo>> loadPhotos(Uri uri) async {
  final response = await http.get(uri);
  final body = response.body;                 // capture the String, not `this`
  return Isolate.run(() {
    final decoded = jsonDecode(body) as List<Object?>;
    return decoded.cast<Map<String, Object?>>().map(Photo.fromJson).toList();
  });
}
```

`compute` là API cũ hơn nhưng vẫn có ích, chủ yếu vì nó biên dịch được cho web:

```dart
import 'package:flutter/foundation.dart';

List<Photo> parsePhotos(String body) {        // top-level or static
  final decoded = jsonDecode(body) as List<Object?>;
  return decoded.cast<Map<String, Object?>>().map(Photo.fromJson).toList();
}

final photos = await compute(parsePhotos, response.body);
```

Trong Flutter hiện tại, bản cài đặt native của `compute` chỉ là một lớp bọc một dòng: nó gọi `Isolate.run(() => callback(message))`. Điều đáng chú ý là bản cài đặt cho **web**, nơi nó chạy `await null;` rồi gọi callback của bạn **ngay trên cùng một thread**. Dart trên web không có isolate. `compute` trên Flutter web giữ cho code của bạn biên dịch được; nó không giữ được frame cho bạn.

| | `compute` | `Isolate.run` | `Isolate.spawn` |
| --- | --- | --- | --- |
| Vòng đời | Một lời gọi | Một lời gọi | Tới khi bạn tắt nó |
| Thông điệp | Một vào, một ra | Một ra | Bao nhiêu tùy bạn |
| Nhận closure | Một tham số, một callback | Closure không tham số | Entry point + một message |
| Biên dịch cho web | Có (chạy nội tuyến) | Không | Không |
| Hợp cho | Code cũ, code dùng chung với web | Mọi việc chạy một lần | Worker sống lâu |

Cả `Isolate.run` lẫn `compute` đều trả kết quả qua `Isolate.exit`, tức là chuyển giao đồ thị object thay vì sao chép nó. Vì vậy chiều *kết quả* rẻ bất kể kích thước. Chiều *tham số* thì không — mọi thứ closure bắt được đều bị sao chép khi đi vào.

## Worker sống lâu: ports, một cú bắt tay, và bảng request

Spawn không miễn phí, và nếu bạn parse một message mỗi 100 ms trong app chat thì bạn trả cái giá đó liên tục. Một worker sống lâu sẽ khấu hao nó. Hai nguyên thủy ở đây là `ReceivePort` (bên lắng nghe) và `SendPort` (cái tay cầm mà bạn gửi được sang isolate khác).

Phần lấn cấn là cú bắt tay: để nói chuyện hai chiều, mỗi bên phải giữ `SendPort` của bên kia, mà một `ReceivePort` thì chỉ `listen` được một lần. Mẹo chuẩn là dùng `RawReceivePort`, gán handler trước khi spawn, rồi nâng cấp thành `ReceivePort` thật.

```dart
import 'dart:async';
import 'dart:convert';
import 'dart:isolate';

class JsonWorker {
  JsonWorker._(this._responses, this._commands) {
    _responses.listen(_handleResponse);
  }

  final ReceivePort _responses;
  final SendPort _commands;
  final Map<int, Completer<Object?>> _pending = {};
  int _nextId = 0;
  bool _closed = false;

  static Future<JsonWorker> spawn() async {
    final initPort = RawReceivePort();
    final connection = Completer<(ReceivePort, SendPort)>.sync();
    initPort.handler = (Object? commandPort) {
      connection.complete((
        ReceivePort.fromRawReceivePort(initPort),
        commandPort! as SendPort,
      ));
    };
    await Isolate.spawn(_entryPoint, initPort.sendPort);
    final (responses, commands) = await connection.future;
    return JsonWorker._(responses, commands);
  }

  Future<Object?> parse(String source) {
    if (_closed) throw StateError('Worker is closed');
    final completer = Completer<Object?>.sync();
    final id = _nextId++;
    _pending[id] = completer;
    _commands.send((id, source));
    return completer.future;
  }

  void _handleResponse(Object? message) {
    final (int id, Object? response) = message! as (int, Object?);
    final completer = _pending.remove(id)!;
    if (response is RemoteError) {
      completer.completeError(response);
    } else {
      completer.complete(response);
    }
  }

  void close() {
    if (_closed) return;
    _closed = true;
    _commands.send(null);                 // shutdown sentinel
    if (_pending.isEmpty) _responses.close();
  }

  static void _entryPoint(SendPort responses) {
    final commands = ReceivePort();
    responses.send(commands.sendPort);    // completes the handshake
    commands.listen((Object? message) {
      if (message == null) {
        commands.close();
        Isolate.exit();
      }
      final (int id, String source) = message! as (int, String);
      try {
        responses.send((id, jsonDecode(source)));
      } catch (error, stack) {
        responses.send((id, RemoteError(error.toString(), stack.toString())));
      }
    });
  }
}
```

Ba điểm đáng để ý. **Id của request** rất quan trọng: một khi bên trong worker có bất kỳ thao tác bất đồng bộ nào thì thứ tự trả về không còn được đảm bảo trùng thứ tự gửi, nên hãy ghép mỗi response với đúng completer đã hỏi. Lỗi không tự lan qua ranh giới — một exception ném ra trong worker chỉ giết message đó, trừ khi bạn bắt lấy rồi gửi về một `RemoteError`. Và worker có event loop riêng của nó, nên một message chậm vẫn chặn các message *tiếp theo của chính worker đó*; một worker là hàng đợi tuần tự, không phải một pool.

Nếu bạn thấy mình đang tự dựng pool kèm backpressure và hủy tác vụ, tài liệu Flutter chỉ thẳng sang [`worker_manager`](https://pub.dev/packages/worker_manager) thay vì để bạn viết lại lần nữa.

## Ranh giới thì sao chép — và vài thứ nhất định không chịu bị sao chép

Isolate không chia sẻ gì hết. Khi bạn `send()` một object khả biến, toàn bộ đồ thị object chạm tới được sẽ bị deep-copy vào heap của isolate nhận. Sửa nó ở một bên không ảnh hưởng bên kia, kể cả biến toàn cục: isolate được sinh ra có bản sao riêng của state top-level, nên một biến `configuration` bị sửa trong worker vẫn nguyên vẹn ở UI isolate.

Giá trị bất biến là ngoại lệ. String và dữ liệu byte không sửa được sẽ truyền theo tham chiếu chứ không sao chép — đó chính là lý do ví dụ `Isolate.run` phía trên bắt lấy `response.body`: chuỗi vài megabyte đó không bị nhân đôi khi đi vào.

| Qua được bình thường | Ném lỗi hoặc chạy sai |
| --- | --- |
| `null`, `num`, `bool`, `String` | `BuildContext`, `State`, mọi widget |
| List, map, set chứa giá trị gửi được | Object của `dart:ui` như `Image`, `Picture` |
| `TypedData` (`Uint8List`, `ByteData`, …) | `Socket` đang mở và các handle tài nguyên native |
| Record và instance của class bạn viết | Closure bắt bất kỳ thứ nào ở cột này |
| `SendPort`, `Capability`, `RootIsolateToken` | `ReceivePort` (gửi `sendPort` của nó thay thế) |

Lỗi mà người ta gặp đầu tiên trông như thế này:

```dart
class _FeedPageState extends State<FeedPage> {
  String _raw = '';

  Future<void> _parse() async {
    // Throws: the closure captures `this`, and `this` reaches the whole
    // State object — element, context, widget tree, subscriptions.
    final data = await Isolate.run(() => jsonDecode(_raw));
  }
}
```

Closure trông như chỉ bắt một chuỗi. Thực ra nó bắt `this`, vì `_raw` là field của instance. Copy giá trị ra biến cục bộ trước, closure sẽ chỉ bắt biến cục bộ đó:

```dart
Future<void> _parse() async {
  final raw = _raw;
  final data = await Isolate.run(() => jsonDecode(raw));
}
```

Cùng quy tắc đó giết luôn hai mẫu code hấp dẫn khác. **Không có `rootBundle` trong isolate được sinh ra** — hãy nạp asset ở UI isolate rồi gửi bytes sang. Và bạn không thể build, layout, paint hay chạm vào object của `dart:ui` ở đó. Nếu worker tạo ra ảnh, hãy gửi về bytes pixel thô và decode trên UI isolate.

## `TransferableTypedData` chuyển giao bytes thay vì sao chép

Với payload nhị phân lớn đi *vào* worker — frame camera, buffer âm thanh, file vừa tải — phần đắt chính là bản sao. `TransferableTypedData` chuyển giao quyền sở hữu thay vì sao chép:

```dart
import 'dart:isolate';
import 'dart:typed_data';

// Sending isolate
final Uint8List frame = await grabFrame();
port.send(TransferableTypedData.fromList([frame]));

// Receiving isolate
void onMessage(Object? message) {
  final transferable = message! as TransferableTypedData;
  final ByteBuffer buffer = transferable.materialize();
  final Uint8List bytes = buffer.asUint8List();
  // ...
}
```

Hai quy tắc khiến nó an toàn và cũng rất dễ vấp: `materialize()` chỉ được gọi **đúng một lần**, và sau khi bạn bọc một danh sách vào `TransferableTypedData` thì phải coi như các buffer gốc đã mất. Materialize hai lần, hoặc materialize ngay trong isolate đã gửi đi, sẽ ném lỗi. Chỉ dùng khi buffer đủ lớn để bản sao lộ ra trong profile; với vài kilobyte thì `Uint8List` thường đơn giản hơn và đủ nhanh.

## Plugin trong background isolate cần root isolate token

Đây mới là chỗ đa số thật sự mắc kẹt. Platform channel được nối vào binary messenger của root isolate. Một isolate vừa sinh ra thì không có cái đó, nên lời gọi `MethodChannel` đầu tiên từ worker sẽ thất bại — kể cả những lời gọi nằm sâu bên trong plugin như `shared_preferences` hay `path_provider`.

Cách sửa gọn trong hai dòng, nhưng phải đặt đúng ở hai isolate:

```dart
import 'dart:isolate';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<String?> readTokenInBackground() async {
  // On the root isolate: grab the token. It is sendable.
  final rootIsolateToken = RootIsolateToken.instance!;

  return Isolate.run(() async {
    // On the worker: register before touching any plugin.
    BackgroundIsolateBinaryMessenger.ensureInitialized(rootIsolateToken);
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('auth_token');
  });
}
```

`RootIsolateToken.instance` chỉ khác null **trên root isolate**, nên hãy đọc nó trước khi spawn và để closure bắt lấy. Còn `ensureInitialized` phải chạy bên trong worker, trước lời gọi channel đầu tiên.

Những thứ cách này *không* cho bạn:

- **Không nhận được message chủ động từ phía host.** Bạn gọi ra được và nhận được phản hồi. Bạn không nhận được những gì nền tảng tự đẩy sang — một listener snapshot của Firestore hay event stream của plugin sẽ không chạy trong background isolate. Hãy query, đừng subscribe.
- **Không đảm bảo cho mọi plugin.** Plugin cần `Activity`, hoặc giữ state theo từng engine ở phía host, vẫn có thể chạy sai. Hãy thử đúng plugin đó thay vì mặc định là được.
- **Không có gì trên web**, nơi `RootIsolateToken.instance` vô nghĩa vì không có isolate nào để đăng ký.

Nếu bạn cần nền tảng *đánh thức* mình, đó là cơ chế khác — một plugin chạy nền tự đăng ký entry point riêng — chứ không phải `BackgroundIsolateBinaryMessenger`.

## Đo trước khi trả giá cho một lần spawn

Spawn tốn thời gian và bộ nhớ, còn bản sao đi vào thì càng lớn message càng đắt. Với công việc chỉ vài mili-giây, isolate hoàn toàn có thể chậm hơn là làm luôn tại chỗ. Hai cách rẻ để biết chắc:

```dart
import 'dart:developer';

Timeline.timeSync('parse feed', () {
  result = jsonDecode(body);
});
```

Khối đó hiện lên thành một lát cắt có tên trong timeline của DevTools, ở lane UI, kèm thời lượng thật. Thoải mái nằm dưới ngân sách frame: cứ để yên. Vắt ngang ranh giới frame: bạn đã tìm ra ứng viên cho isolate. Performance overlay là bước kiểm nhanh hơn — cột cao ở đồ thị **UI** nghĩa là việc Dart kiểu này, còn cột cao ở đồ thị **raster** nghĩa là shader hoặc overdraw, và isolate không giúp được gì cả.

Có một lựa chọn trung gian ít người dùng: chia việc thành từng khối và `await null` giữa các khối. Nó vẫn nằm trên một isolate — không sao chép, không luật gửi được/không gửi được, không rắc rối plugin — và cho frame lọt qua giữa các khối. Nó không dùng thêm nhân CPU nào nên thông lượng kém hơn, nhưng với một khối lượng công việc chỉ hơi khó chịu thì đây thường là thay đổi nhỏ hơn.

## FAQ

**`async`/`await` có bao giờ đẩy việc sang thread khác không?**

Không. `await` tạm dừng hàm hiện tại và để event loop chạy các event khác; thân hàm luôn thực thi trên isolate đã gọi nó. Có những thứ bạn await — socket mạng, đọc file, giải mã ảnh — thật sự diễn ra ở nơi khác, nhưng đó là runtime làm việc bên ngoài Dart, không phải `await` tạo ra thread.

**Code mới nên dùng `compute` hay `Isolate.run`?**

Dùng `Isolate.run` cho mọi thứ chạy trên mobile và desktop: nó nhận closure bình thường và không bắt bạn phải tách ra một hàm top-level. Dùng `compute` khi cùng một file phải biên dịch được cho web, và nhớ rằng trên web nó chạy nội tuyến, chỉ đem lại khả năng tương thích chứ không đem lại hiệu năng.

**Nên spawn bao nhiêu isolate?**

Một worker sống lâu xử lý tốt một dòng công việc tương tự nhau và chỉ tốn một lần spawn. Mở rộng ra nhiều isolate chỉ có ích khi công việc thật sự song song được và máy còn nhân rảnh — mà mỗi isolate mang theo heap riêng, nên một pool tám isolate là quyết định về bộ nhớ, không hề miễn phí.

**Vì sao plugin vẫn lỗi dù đã gọi `ensureInitialized`?**

Kiểm tra ba thứ: bạn đã đọc `RootIsolateToken.instance` trên root isolate chứ không phải bên trong worker, `ensureInitialized` chạy trước lời gọi channel đầu tiên, và plugin đó không cố đẩy event sang cho bạn. Platform channel trong background isolate chỉ hỗ trợ request/response; bất cứ thứ gì host tự khởi xướng đều không tới nơi.

**Background isolate có nạp asset bằng `rootBundle` được không?**

Không. Việc nạp asset đi qua bundle của root isolate. Hãy đọc asset trên UI isolate rồi truyền `String` hoặc `Uint8List` vào worker — chuỗi được gửi theo tham chiếu, còn buffer byte lớn có thể chuyển giao bằng `TransferableTypedData`.

---

*Phần hành vi API trong bài lấy từ tài liệu chính thức của Flutter và Dart đã dẫn ở trên; còn phần đánh giá khi nào isolate đáng dùng, và gợi ý chia nhỏ công việc thay vì spawn, là quan điểm riêng của tôi. API isolate và cách cài đặt `compute` đã thay đổi qua các bản phát hành — hãy kiểm chứng mọi thứ phụ thuộc phiên bản với tài liệu của đúng SDK bạn đang ship.*
