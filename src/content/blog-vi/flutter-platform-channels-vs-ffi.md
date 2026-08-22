---
title: "Gọi code native từ Dart: platform channel, Pigeon hay FFI"
description: "Ba công cụ cho ba bài toán khác nhau. MethodChannel và EventChannel nói chuyện với dịch vụ của hệ điều hành. Pigeon làm đúng việc đó nhưng sinh code tự động, hết gõ nhầm chuỗi. dart:ffi gọi thẳng thư viện C — đồng bộ, vừa là điểm mạnh vừa là cái bẫy."
seoDescription: "Khi nào dùng MethodChannel, EventChannel, Pigeon hay dart:ffi trong Flutter — ví dụ chạy được, RootIsolateToken, quản lý bộ nhớ với Arena, và ffigen."
keywords:
  - platform channel và ffi trong flutter
  - ví dụ methodchannel flutter
  - hướng dẫn pigeon flutter
  - hướng dẫn dart ffi
  - gọi code native từ flutter
  - rootisolatetoken background isolate
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🔌"
tags: ["Flutter", "Dart", "FFI", "Pigeon", "Native"]
sources:
  - name: "Flutter — Writing custom platform-specific code"
    url: "https://docs.flutter.dev/platform-integration/platform-channels"
  - name: "Dart — C interop using dart:ffi"
    url: "https://dart.dev/interop/c-interop"
  - name: "MethodChannel — Flutter API docs"
    url: "https://api.flutter.dev/flutter/services/MethodChannel-class.html"
  - name: "BackgroundIsolateBinaryMessenger — Flutter API docs"
    url: "https://api.flutter.dev/flutter/services/BackgroundIsolateBinaryMessenger-class.html"
  - name: "pigeon on pub.dev"
    url: "https://pub.dev/packages/pigeon"
  - name: "ffigen on pub.dev"
    url: "https://pub.dev/packages/ffigen"
  - name: "ffi on pub.dev"
    url: "https://pub.dev/packages/ffi"
  - name: "jnigen on pub.dev"
    url: "https://pub.dev/packages/jnigen"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "web-tech-to-mobile-app-2026"
    title: "Dùng công nghệ web để làm app mobile: bản đồ kỹ thuật 2026"
draft: false
---

App Flutter nào rồi cũng đến lúc cần một thứ mà Dart tự nó không làm được. Đọc mức pin. Mở camera. Xin quyền. Giải mã một codec video lạ. Chạy model on-device. Kiểm tra chữ ký bằng một thư viện crypto đã được audit hai mươi năm và chẳng ai định viết lại bằng Dart.

Câu trả lời quen thuộc — "dùng platform channel" — chỉ đúng khoảng một phần ba số trường hợp. Flutter có ba cơ chế riêng biệt để rời khỏi Dart, và chúng không phải ba cách hiện thực cùng một ý tưởng. Chúng giải quyết những bài toán khác nhau, và lỗi phổ biến nhất là chọn cái bạn đã biết thay vì cái phù hợp.

Nói ngắn gọn: **`MethodChannel` và `EventChannel` là một hàng đợi tin nhắn bất đồng bộ** tới code Kotlin/Swift, đúng thứ bạn cần khi bên kia là một *dịch vụ của hệ điều hành*. **Pigeon** vẫn là hàng đợi đó, nhưng phần boilerplate và các hằng chuỗi được sinh ra tự động. **`dart:ffi`** thì không phải hàng đợi gì cả — nó là một lời gọi hàm C trực tiếp, đồng bộ, vào một *thư viện* đang nằm sẵn trong tiến trình của bạn.

Bài này đưa một ví dụ chạy được cho từng cơ chế, rồi dành nửa sau cho những phần thực sự sinh bug: thread, isolate, và ai sở hữu byte nào.

## Thứ nằm ở đầu bên kia quyết định công cụ

Trước khi viết dòng code nào, trả lời một câu: thứ bạn cần là một **dịch vụ** hay một **thư viện**?

Dịch vụ là thứ hệ điều hành sở hữu. Nó có vòng đời riêng, có thể hiện dialog hỏi người dùng, có thể chạy lâu tùy ý, và chỉ tiếp cận được qua SDK của Android hoặc Apple — bằng Kotlin hoặc Swift. Permission, notification, camera, Bluetooth, in-app purchase, share sheet. Không có hàm C nào để gọi; chỉ có một class Java hoặc một object Objective-C, và cách tỉnh táo duy nhất để chạm tới nó là gửi một tin nhắn cho code viết bằng chính ngôn ngữ đó.

Thư viện là một khối code đã biên dịch với C ABI. Nó không có vòng đời, không quan tâm app của bạn, và làm đúng một việc: byte vào, byte ra. SQLite, libwebp, một pipeline xử lý ảnh viết bằng Rust, một kernel xử lý tín hiệu, whisper.cpp. Gửi *tin nhắn* cho thứ đó nghĩa là copy buffer qua codec hai lần mà chẳng để làm gì.

| | MethodChannel / EventChannel | Pigeon | dart:ffi |
| --- | --- | --- | --- |
| Bên kia viết bằng | Kotlin, Swift, Java, ObjC, C++ | như trên | C, C++, Rust, Zig — bất cứ thứ gì có C ABI |
| Dạng lời gọi | bất đồng bộ — `Future` / `Stream` | bất đồng bộ — `Future` / `Stream` | gọi hàm đồng bộ |
| Tham số | copy qua codec | copy qua codec được sinh ra | pointer — không copy |
| An toàn kiểu | tên method là chuỗi, payload là `dynamic` | kiểm tra lúc biên dịch ở **cả hai** phía | kiểm tra ở Dart, không kiểm tra ở C |
| Boilerplate bạn phải viết | toàn bộ | chỉ phần hiện thực native | phần binding header C (hoặc sinh tự động) |
| Chặn isolate đang gọi | không | không | **có** |
| Dùng được từ background isolate | chỉ khi có `RootIsolateToken` | như trên | có, thoải mái |

Hai dòng cuối là hai dòng biến thành sự cố production. Sẽ quay lại.

## MethodChannel: một hàng đợi tin nhắn kèm codec

`MethodChannel` là một cái ống có tên. Bạn đặt cho nó một chuỗi làm tên, gửi vào một tên method và một tham số, rồi lát sau một `Future` hoàn tất. Tên phải khớp chính xác ở cả hai phía, và không có gì kiểm tra chuyện đó cả.

```dart
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

const _battery = MethodChannel('dev.fluttercook/battery');

Future<int?> batteryLevel() async {
  try {
    return await _battery.invokeMethod<int>('getBatteryLevel');
  } on PlatformException catch (e) {
    // The native side called result.error(...)
    debugPrint('battery unavailable: ${e.code} ${e.message}');
    return null;
  } on MissingPluginException {
    // No handler registered — wrong platform, or the plugin isn't wired up.
    return null;
  }
}
```

Hãy bắt `MissingPluginException` riêng. Nó không phải lỗi runtime của code native, nó có nghĩa là không ai đang lắng nghe trên tên channel đó — gõ sai, một nền tảng bạn quên hiện thực, hoặc một lần hot restart làm mất đăng ký.

Phía Android, trong `onAttachedToEngine` của plugin:

```kotlin
val channel = MethodChannel(binding.binaryMessenger, "dev.fluttercook/battery")
channel.setMethodCallHandler { call, result ->
    when (call.method) {
        "getBatteryLevel" -> {
            val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
            result.success(bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY))
        }
        else -> result.notImplemented()
    }
}
```

Phía iOS, trong `register(with:)`:

```swift
let channel = FlutterMethodChannel(
    name: "dev.fluttercook/battery",
    binaryMessenger: registrar.messenger())

channel.setMethodCallHandler { call, result in
    switch call.method {
    case "getBatteryLevel":
        UIDevice.current.isBatteryMonitoringEnabled = true
        let level = UIDevice.current.batteryLevel
        if level < 0 {
            result(FlutterError(code: "UNAVAILABLE",
                                message: "Battery level unavailable",
                                details: nil))
        } else {
            result(Int(level * 100))
        }
    default:
        result(FlutterMethodNotImplemented)
    }
}
```

Thứ đi qua đường ống không phải là object. `StandardMessageCodec` mặc định chỉ serialise một tập kiểu cố định — null, boolean, số nguyên, số thực, chuỗi, mảng byte và mảng số, cùng `List` và `Map` của những kiểu đó. Mọi thứ khác bạn phải tự dàn phẳng thành map, bằng tay, ở cả hai phía. Mảng byte là trường hợp đáng nhớ: `Uint8List` đi qua dưới dạng blob nhị phân chứ không phải một list số, nên trả về dữ liệu ảnh hay audio rẻ hơn nhiều so với vẻ ngoài của nó.

### EventChannel: khi phía native mới là bên nói

`MethodChannel` là Dart hỏi. `EventChannel` là nền tảng đẩy — dữ liệu cảm biến, thay đổi kết nối mạng, tiến độ một lượt tải.

```dart
const _status = EventChannel('dev.fluttercook/battery/status');

Stream<String> batteryStatus() =>
    _status.receiveBroadcastStream().map((event) => event as String);
```

```kotlin
EventChannel(binding.binaryMessenger, "dev.fluttercook/battery/status")
    .setStreamHandler(object : EventChannel.StreamHandler {
        private var receiver: BroadcastReceiver? = null

        override fun onListen(args: Any?, events: EventChannel.EventSink) {
            receiver = object : BroadcastReceiver() {
                override fun onReceive(ctx: Context, intent: Intent) {
                    events.success(describeStatus(intent))
                }
            }
            context.registerReceiver(receiver, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        }

        override fun onCancel(args: Any?) {
            context.unregisterReceiver(receiver)
            receiver = null
        }
    })
```

Có hai chỗ cắn ở đây. `onListen` chạy khi có subscriber *đầu tiên* và `onCancel` khi subscriber *cuối cùng* hủy, nên đăng ký listener của hệ điều hành ở bất kỳ chỗ nào khác là rò rỉ. Và `EventSink` phải được gọi từ main thread của nền tảng — nếu dữ liệu của bạn về trên một worker thread, hãy nhảy ngược lại bằng `Handler(Looper.getMainLooper())` trên Android hoặc `DispatchQueue.main` trên iOS, nếu không bạn sẽ gặp những cú crash rời rạc, không tái hiện được.

## Channel viết tay sẽ mục, và đó là lý do có Pigeon

Đoạn code phía trên có bốn bản sao độc lập của cùng một hợp đồng: tên channel, tên method, hình dạng tham số, và kiểu trả về — lặp lại trong Dart, Kotlin và Swift. Không cái nào được compiler kiểm tra. Đổi tên một method trong Dart thì app vẫn build, vẫn phát hành, rồi ném `MissingPluginException` trên một nền tảng. Đổi một key trong map từ `id` thành `userId` thì bên kia nhận null lúc runtime. Thêm một field mà quên iOS thì bạn biết tin qua crash report.

Đây không phải kịch bản giả định; đó là vòng đời bình thường của một channel viết tay trong codebase có nhiều hơn một người đóng góp.

[Pigeon](https://pub.dev/packages/pigeon) xóa bỏ chuyện đó. Bạn mô tả interface đúng một lần, bằng Dart, dưới dạng abstract class. Pigeon sinh ra phía gọi bằng Dart và phần interface Kotlin/Swift/C++, cả hai dùng một codec nhị phân được sinh ra — không còn tên method dạng chuỗi ở đâu cả.

```dart
// pigeons/battery.dart — this file is a spec, it never runs.
import 'package:pigeon/pigeon.dart';

@ConfigurePigeon(PigeonOptions(
  dartOut: 'lib/src/battery.g.dart',
  kotlinOut: 'android/src/main/kotlin/dev/fluttercook/battery/Battery.g.kt',
  kotlinOptions: KotlinOptions(package: 'dev.fluttercook.battery'),
  swiftOut: 'ios/Classes/Battery.g.swift',
  dartPackageName: 'fc_battery',
))
class BatteryInfo {
  int? level;
  bool? isCharging;
}

@HostApi()
abstract class BatteryApi {
  @async
  BatteryInfo readBattery();
}
```

```bash
dart run pigeon --input pigeons/battery.dart
```

Trên Android bây giờ bạn hiện thực một interface được sinh ra thay vì bóc tách `MethodCall`, và đăng ký nó bằng đúng một dòng:

```kotlin
class BatteryImpl(private val context: Context) : BatteryApi {
    override fun readBattery(callback: (Result<BatteryInfo>) -> Unit) {
        val bm = context.getSystemService(Context.BATTERY_SERVICE) as BatteryManager
        callback(Result.success(BatteryInfo(
            level = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY).toLong(),
            isCharging = bm.isCharging,
        )))
    }
}

// in onAttachedToEngine
BatteryApi.setUp(binding.binaryMessenger, BatteryImpl(context))
```

Giờ đổi tên `readBattery` sẽ làm hỏng bản build Kotlin, và quên hiện thực nó trên iOS sẽ làm hỏng bản build Swift. Toàn bộ giá trị của Pigeon nằm ở đó, và nó đáng giá hơn vẻ ngoài. `@FlutterApi()` sinh chiều ngược lại — native gọi Dart — và các phiên bản gần đây còn sinh được stream dựa trên event channel; hãy đọc README của phiên bản bạn pin.

Điều Pigeon không thay đổi: bên dưới nó vẫn là platform channel. Vẫn giao bất đồng bộ, vẫn copy qua codec, vẫn cùng luật về isolate.

## dart:ffi: không phải tin nhắn, mà là lời gọi hàm

`dart:ffi` là một cơ chế hoàn toàn khác. Không channel, không codec, không hàng đợi. Dart tra một symbol trong shared library đã được map sẵn vào tiến trình rồi gọi nó — đúng như cách C gọi.

Giả sử bạn có một thư viện C nhỏ:

```c
// src/image_tools.h
#include <stdint.h>
#include <stddef.h>

#if _WIN32
#define FFI_EXPORT __declspec(dllexport)
#else
#define FFI_EXPORT __attribute__((visibility("default"))) __attribute__((used))
#endif

// Converts an RGBA8888 buffer to greyscale, in place.
FFI_EXPORT void rgba_to_grey(uint8_t *pixels, size_t length);
```

Cái `__attribute__((used))` đó quan trọng trên iOS. Thư viện tĩnh bị dead-strip lúc link, và một symbol chỉ được tham chiếu bằng tên lúc runtime trông như đã chết dưới mắt linker. `flutter create --template=plugin_ffi` dựng sẵn macro này cho bạn, cùng với phần cấu hình CMake và podspec.

Binding nó:

```dart
import 'dart:ffi';
import 'dart:io';
import 'dart:typed_data';
import 'package:ffi/ffi.dart';

final DynamicLibrary _lib = () {
  if (Platform.isAndroid || Platform.isLinux) return DynamicLibrary.open('libimage_tools.so');
  if (Platform.isWindows) return DynamicLibrary.open('image_tools.dll');
  if (Platform.isMacOS) return DynamicLibrary.open('libimage_tools.dylib');
  return DynamicLibrary.process(); // iOS: statically linked into the app
}();

typedef _RgbaToGreyC = Void Function(Pointer<Uint8> pixels, Size length);
typedef _RgbaToGrey = void Function(Pointer<Uint8> pixels, int length);

final _rgbaToGrey = _lib.lookupFunction<_RgbaToGreyC, _RgbaToGrey>('rgba_to_grey');
```

Luôn luôn hai typedef. Cái đầu mô tả chữ ký **C** bằng các kiểu đánh dấu của `dart:ffi` (`Void`, `Size`, `Pointer<Uint8>`); cái thứ hai mô tả cách Dart nhìn nó (`void`, `int`). Nếu hai cái lệch nhau bạn nhận lỗi runtime tại `lookupFunction` chứ không phải lỗi biên dịch, nên đáng để chính xác: `Size` là `size_t`, `Int32` là `int32_t`, `IntPtr` là số nguyên có dấu rộng bằng một pointer.

Gọi nó:

```dart
Uint8List toGrey(Uint8List rgba) => using((Arena arena) {
  final buffer = arena<Uint8>(rgba.length);
  buffer.asTypedList(rgba.length).setAll(0, rgba);

  _rgbaToGrey(buffer, rgba.length);           // synchronous — returns when C returns

  return Uint8List.fromList(buffer.asTypedList(rgba.length));
});
```

`asTypedList` mới là chỗ thú vị. Nó không copy — nó đưa bạn một `Uint8List` là một *view* lên vùng nhớ native. Đó chính là tính chất zero-copy khiến người ta chọn FFI, và cũng là cái bẫy: ngay khi arena giải phóng vùng nhớ đó, view trỏ vào bộ nhớ đã free và đọc nó là undefined behaviour. Vì vậy mới có bản copy `Uint8List.fromList` lúc trả về. Nếu muốn bỏ luôn bản copy đó, hãy cấp phát buffer một lần và giữ nó sống chừng nào view Dart còn sống.

## ffigen viết hộ bạn nửa phần chán nhất

Viết tay typedef thì ổn với ba hàm và khổ sở với ba trăm hàm. [`ffigen`](https://pub.dev/packages/ffigen) đọc header C của bạn bằng libclang rồi sinh ra binding.

```yaml
# ffigen.yaml
name: ImageToolsBindings
description: Bindings for image_tools.h
output: 'lib/src/image_tools_bindings.dart'
headers:
  entry-points:
    - 'src/image_tools.h'
```

```bash
dart run ffigen --config ffigen.yaml
```

Bạn nhận được một class có constructor nhận `DynamicLibrary` và các method phản chiếu đúng header, kèm cả struct và enum. Sinh lại khi header đổi, rồi analyzer của Dart sẽ chỉ cho bạn chỗ nào vỡ — cùng một lập luận như Pigeon, áp cho cơ chế còn lại.

Có một công cụ song song cho phía JVM: [`jnigen`](https://pub.dev/packages/jnigen) sinh binding Dart tới class Java và Kotlin qua JNI, cho phép bạn chạm tới một class trong Android SDK mà không cần viết channel. Đây là một đánh đổi thực sự khác với channel — đồng bộ, không codec — và về bản chất chỉ chạy trên Android.

## Bộ nhớ giờ là của bạn

Không có gì trong `dart:ffi` được garbage collect. Nếu C cấp phát thì C phải giải phóng, và GC của Dart hoàn toàn không biết vùng nhớ đó tồn tại.

`package:ffi` cho bạn ba công cụ, xếp theo thứ tự tăng dần mức độ nên ưu tiên:

```dart
// 1. Manual — you must free on every path, including the throwing ones.
final p = malloc<Uint8>(1024);
try { /* ... */ } finally { malloc.free(p); }

// 2. Arena — everything allocated inside is freed when the block exits,
//    including on an exception. Use this by default.
using((arena) {
  final name = 'hello'.toNativeUtf8(allocator: arena);
  final buf = arena<Float>(256);
  // ...
}); // both freed here

// 3. NativeFinalizer — ties a native free() to a Dart object's collection,
//    for handles whose lifetime you cannot bracket.
final _finalizer = NativeFinalizer(_lib.lookup('image_tools_free'));
```

Vài quy tắc tiết kiệm cho bạn một tuần debug:

- **Mặc định dùng `Arena`.** Lý do duy nhất để không dùng là vùng nhớ phải sống lâu hơn khối lệnh.
- **Pointer do C trả về đều có chủ.** Đọc header. Nếu thư viện `malloc` nó thì bạn gọi hàm free của chính thư viện đó, không phải `malloc.free` — allocator có thể khác nhau.
- **`toNativeUtf8()` có cấp phát.** `.toDartString()` cũng cấp phát, nhưng ở phía Dart; chỉ cái đầu tiên cần được free.
- **`NativeFinalizer` không phải destructor.** Nó chạy khi GC rảnh, mà có thể là không bao giờ. Hãy dùng nó như lưới an toàn dưới một `dispose()` tường minh, đừng dùng thay cho `dispose()`.

## Hai cái bẫy thread ai cũng dính

Mỗi cơ chế có đúng một kiểu hỏng về thread hay tóm người ta, và hai kiểu đó ngược nhau.

**Không dùng được channel từ background isolate — trừ khi bạn đưa cho nó một token.** Platform channel gắn với binary messenger của root isolate. Spawn một isolate để parse một payload lớn, gọi `invokeMethod` từ đó, và bạn nhận về lỗi thay vì kết quả. Cách sửa là lấy `RootIsolateToken` trên root isolate rồi khởi tạo messenger bên trong isolate mới:

```dart
import 'dart:isolate';
import 'package:flutter/services.dart';

Future<String> savePayload(Map<String, Object?> payload) async {
  final token = RootIsolateToken.instance!;   // must be read on the root isolate

  return Isolate.run(() async {
    BackgroundIsolateBinaryMessenger.ensureInitialized(token);
    // path_provider and friends work from here on
    final dir = await getApplicationDocumentsDirectory();
    // ... heavy encode, then write
    return dir.path;
  });
}
```

`RootIsolateToken.instance` là null nếu không ở root isolate, đó là lý do nó được đọc bên ngoài closure rồi mới bị capture vào.

**FFI chặn — đồng bộ nghĩa là như vậy.** Một lời gọi `MethodChannel` không thể làm giật UI, vì nó trả về `Future` và event loop vẫn quay. Một lời gọi FFI tới hàm chạy 400ms thì đơn giản là không trả về trong 400ms, và mọi frame trong khoảng đó bị rớt. Việc native nặng thuộc về isolate riêng của nó:

```dart
Future<Uint8List> greyInBackground(Uint8List rgba) =>
    Isolate.run(() => toGrey(rgba));
```

Hai chi tiết khiến cách này dùng được trong thực tế. Pointer không gửi được giữa các isolate, nên hãy truyền `pointer.address` dưới dạng `int` rồi dựng lại bằng `Pointer.fromAddress(address)` — mọi isolate trong một app Flutter dùng chung một không gian địa chỉ, nên địa chỉ đó hợp lệ. Và `Uint8List` gửi qua port thì bị copy; hãy bọc buffer lớn trong `TransferableTypedData` để chuyển quyền sở hữu thay vì copy.

Nếu phía native cần gọi *ngược* vào Dart từ thread của chính nó — ví dụ một decoder vừa xong một frame — hãy dùng `NativeCallable.listener`. `Pointer.fromFunction` chỉ hoạt động khi code native gọi bạn trên đúng thread đã gọi vào nó, mà một worker thread thì theo định nghĩa là không.

Còn một chỗ nữa, ở phía nền tảng: handler của channel mặc định chạy trên main thread của nền tảng, nên làm việc nặng bằng Kotlin hay Swift bên trong `setMethodCallHandler` sẽ chặn UI thread của nền tảng dù Dart vẫn khỏe. Hãy đẩy nó ra một background task queue — `binaryMessenger.makeBackgroundTaskQueue()` có trên cả Android lẫn iOS — rồi truyền queue đó vào lúc tạo channel.

## FAQ

**Có nên dùng Pigeon cho mọi thứ thay vì MethodChannel không?**
Với bất cứ thứ gì có hơn một hai method thì nên. Code sinh ra vẫn là đúng cơ chế đó, chỉ bỏ đi các hằng chuỗi và phần bóc tách tham số thủ công, và nó biến một lớp lỗi runtime thành lỗi build. Những chỗ channel thô vẫn hợp lý là một lời gọi dùng một lần rồi bỏ, hoặc một protocol động mà tên method thực sự không biết trước lúc biên dịch.

**FFI có nhanh hơn platform channel không?**
Nó bỏ hẳn phần serialise và bước nhảy qua hàng đợi, nên với những lời gọi nhỏ mà dày, hoặc với buffer lớn, khác biệt là về cấu trúc chứ không phải chút ít. Nhưng đó chỉ là phép so sánh đúng khi cả hai lựa chọn đều tồn tại — mà thường thì không. Bạn không thể dùng FFI để mở dialog xin quyền của Android, và bạn cũng không nên đẩy một tấm ảnh 20MB qua codec để tới một hàm C.

**Gọi thẳng Swift hay Kotlin bằng FFI được không?**
Không hẳn. `dart:ffi` nói chuyện bằng C ABI. Bạn có thể phơi một entry point C từ Swift hoặc Kotlin/Native rồi gọi cái đó, nhưng bạn mất phần tiện dụng và tự gánh các chi tiết ABI. Trên Android, `jnigen` là con đường được hỗ trợ tốt hơn để tới các class JVM; trên iOS, `ffigen` sinh được binding cho Objective-C, còn phần interop với Swift vẫn đang chuyển động — hãy kiểm tra trạng thái hiện tại trước khi thiết kế dựa vào nó.

**Tôi cần một package plugin, hay code này để trong app cũng được?**
Cả hai đều được. `flutter create --template=plugin` và `flutter create --template=plugin_ffi` dựng sẵn phần cấu hình build, vốn là phần phiền nhất. Đặt code thẳng vào thư mục `android/` và `ios/` của app thì ổn với thứ đặc thù cho app đó, nhưng package mới là thứ khiến nó test được và tái dùng được, đồng thời buộc bạn phải định nghĩa rõ hợp đồng.

**Vì sao channel của tôi chạy ở debug nhưng hỏng sau hot restart?**
Hot restart phá isolate Dart nhưng không phá phía nền tảng. Handler được đăng ký từ phần khởi tạo native do Dart kích hoạt có thể trở thành mồ côi, và subscription trên một `EventChannel` có thể để lại listener native vẫn đăng ký với một sink đã chết. Hãy đăng ký handler trong `onAttachedToEngine` / `register(with:)` của plugin — đừng đăng ký lười lúc dùng lần đầu — và làm cho `onCancel` dọn dẹp thật sự.

---

*Phần mô tả cơ chế trong bài lấy từ tài liệu chính thức của Flutter và Dart; phần khuyến nghị khi nào nên chọn công cụ nào là quan điểm của tôi, hình thành từ việc đã ship cả ba. API ở khu vực này thay đổi liên tục — `NativeCallable`, các interface Pigeon sinh ra, và phần native assets của Dart đều vừa đổi hình dạng gần đây — nên hãy đối chiếu mọi thứ phụ thuộc phiên bản với tài liệu hiện hành trước khi xây dựng dựa trên nó.*
