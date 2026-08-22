---
title: "Calling native code from Dart: platform channels, Pigeon, or FFI"
description: "Three tools, three different problems. MethodChannel and EventChannel talk to platform services. Pigeon generates the same thing without the string typos. dart:ffi calls a C library directly — synchronously, which is both the point and the danger."
seoDescription: "When to use MethodChannel, EventChannel, Pigeon or dart:ffi in Flutter — working examples, RootIsolateToken, Arena memory, and ffigen."
keywords:
  - flutter platform channel vs ffi
  - flutter methodchannel example
  - flutter pigeon tutorial
  - dart ffi tutorial
  - flutter call native code
  - rootisolatetoken background isolate
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
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
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "web-tech-to-mobile-app-2026"
    title: "Using web technology to build mobile apps: the 2026 technical map"
draft: false
---

Every Flutter app eventually needs something Dart cannot do on its own. Read the battery level. Open the camera. Ask for a permission. Decode an exotic video codec. Run an on-device model. Verify a signature with a crypto library that has been audited for twenty years and that nobody is going to reimplement in Dart.

The usual answer — "use a platform channel" — is right about a third of the time. Flutter ships three separate mechanisms for leaving Dart, and they are not competing implementations of the same idea. They solve different problems, and the most common mistake is picking the one you already know rather than the one that fits.

The short version: **`MethodChannel` and `EventChannel` are an asynchronous message queue** to Kotlin/Swift code, which is what you want when the thing on the other side is a *platform service*. **Pigeon** is the same message queue with the boilerplate and the string constants generated for you. **`dart:ffi`** is not a message queue at all — it is a direct, synchronous C function call into a *library* that happens to live in your process.

This article shows a working example of each, then spends the second half on the parts that actually cause bugs: threading, isolates, and who owns which bytes.

## What sits on the other side decides the tool

Before writing any code, answer one question: is the thing you need a **service** or a **library**?

A service is something the operating system owns. It has its own lifecycle, it may prompt the user, it may take arbitrarily long, and it is only reachable through Android's or Apple's own SDK — in Kotlin or Swift. Permissions, notifications, the camera, Bluetooth, in-app purchases, the share sheet. There is no C function to call; there is a Java class or an Objective-C object, and the only sane way to reach it is to send a message to code written in that language.

A library is a blob of compiled code with a C ABI. It has no lifecycle, it does not care about your app, and it does one job: bytes in, bytes out. SQLite, libwebp, a Rust image pipeline, a signal-processing kernel, whisper.cpp. Sending that a *message* would mean copying your buffer through a codec twice for no reason.

| | MethodChannel / EventChannel | Pigeon | dart:ffi |
| --- | --- | --- | --- |
| Other side is written in | Kotlin, Swift, Java, ObjC, C++ | same | C, C++, Rust, Zig — anything with a C ABI |
| Call shape | async — `Future` / `Stream` | async — `Future` / `Stream` | synchronous function call |
| Arguments | copied through a codec | copied through a generated codec | pointers — no copy |
| Type safety | method names are strings, payloads are `dynamic` | checked at compile time on **both** sides | checked in Dart, unchecked in C |
| Boilerplate you write | all of it | the native implementation only | the C header binding (or generate it) |
| Blocks the calling isolate | no | no | **yes** |
| Usable from a background isolate | only with a `RootIsolateToken` | same | yes, freely |

The last two rows are the ones that turn into production incidents. We come back to them.

## MethodChannel: a message queue with a codec

A `MethodChannel` is a named pipe. You give it a string name, you send it a method name and an argument, and some time later a `Future` completes. The name has to match on both sides exactly, and nothing checks that it does.

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

Handle `MissingPluginException` separately. It is not a runtime failure of the native code, it means nothing is listening on that channel name — a typo, a platform you forgot to implement, or a hot restart that lost the registration.

Android, in the plugin's `onAttachedToEngine`:

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

iOS, in `register(with:)`:

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

What crosses the wire is not an object. The default `StandardMessageCodec` serialises a fixed set of types — null, booleans, integers, doubles, strings, byte and number arrays, plus `List` and `Map` of those. Anything else you have to flatten into a map yourself, by hand, on both sides. Byte arrays are the one case worth knowing: a `Uint8List` goes through as a binary blob rather than a list of numbers, so returning image or audio data is far cheaper than it looks.

### EventChannel: when the native side does the talking

`MethodChannel` is Dart asking. `EventChannel` is the platform pushing — sensor readings, connectivity changes, a download's progress.

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

Two things bite here. `onListen` fires on the *first* subscriber and `onCancel` on the *last* one, so registering the OS listener anywhere else leaks it. And `EventSink` must be called from the platform's main thread — if your data arrives on a worker thread, hop back with `Handler(Looper.getMainLooper())` on Android or `DispatchQueue.main` on iOS, or you will get intermittent, unreproducible crashes.

## Hand-written channels rot, and Pigeon is why you stop writing them

The code above has four independent copies of the same contract: the channel name, the method name, the argument shape, and the return type — repeated in Dart, Kotlin and Swift. None of them is checked by any compiler. Rename a method in Dart and the app compiles, ships, and throws `MissingPluginException` on one platform. Change a map key from `id` to `userId` and you get a null on the other side at runtime. Add a field and forget iOS, and you find out from a crash report.

This is not a hypothetical failure mode; it is the normal life cycle of a hand-written channel in a codebase with more than one contributor.

[Pigeon](https://pub.dev/packages/pigeon) removes it. You describe the interface once, in Dart, as an abstract class. Pigeon generates the Dart caller and the Kotlin/Swift/C++ interface, both using a generated binary codec — no string method names anywhere.

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

On Android you now implement a generated interface instead of parsing a `MethodCall`, and register it with one line:

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

Now renaming `readBattery` breaks the Kotlin build, and forgetting to implement it on iOS breaks the Swift build. That is the entire value proposition, and it is worth more than it sounds. `@FlutterApi()` generates the other direction — native calling Dart — and recent versions can generate event-channel-backed streams too; check the README for the version you pin.

The one thing Pigeon does not change: it is still a platform channel underneath. Same async delivery, same codec copy, same isolate rules.

## dart:ffi: not a message, a function call

`dart:ffi` is a different mechanism entirely. There is no channel, no codec, no queue. Dart looks up a symbol in a shared library that is already mapped into your process and calls it — the same way C would.

Say you have a small C library:

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

That `__attribute__((used))` matters on iOS. Static libraries get dead-stripped at link time, and a symbol only referenced by name at runtime looks dead to the linker. `flutter create --template=plugin_ffi` scaffolds this macro for you, along with the CMake and podspec wiring.

Binding it:

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

Two typedefs, always. The first describes the **C** signature using `dart:ffi` marker types (`Void`, `Size`, `Pointer<Uint8>`); the second describes how Dart sees it (`void`, `int`). If they disagree you get a runtime error at `lookupFunction`, not a compile error, so it is worth being precise: `Size` is `size_t`, `Int32` is `int32_t`, `IntPtr` is a pointer-sized signed integer.

Calling it:

```dart
Uint8List toGrey(Uint8List rgba) => using((Arena arena) {
  final buffer = arena<Uint8>(rgba.length);
  buffer.asTypedList(rgba.length).setAll(0, rgba);

  _rgbaToGrey(buffer, rgba.length);           // synchronous — returns when C returns

  return Uint8List.fromList(buffer.asTypedList(rgba.length));
});
```

`asTypedList` is the interesting call. It does not copy — it hands you a `Uint8List` that is a *view* onto the native allocation. That is the zero-copy property FFI is chosen for, and also the trap: the moment the arena frees that memory, the view points at freed memory and reading it is undefined behaviour. Hence the `Uint8List.fromList` copy on the way out. If you want to skip that copy too, allocate the buffer once and keep it alive for as long as the Dart view does.

## ffigen writes the boring half

Hand-writing typedefs is fine for three functions and miserable for three hundred. [`ffigen`](https://pub.dev/packages/ffigen) parses your C headers with libclang and emits the bindings.

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

You get a class whose constructor takes a `DynamicLibrary` and whose methods mirror the header, structs and enums included. Regenerate when the header changes and the Dart analyzer tells you what broke — which is the same argument as Pigeon, applied to the other mechanism.

There is a parallel tool for the JVM: [`jnigen`](https://pub.dev/packages/jnigen) generates Dart bindings to Java and Kotlin classes over JNI, which lets you reach an Android SDK class without writing a channel. It is a genuinely different trade-off from a channel — synchronous, no codec — and it is Android-only by construction.

## Memory is yours now

Nothing about `dart:ffi` is garbage collected. If C allocated it, C has to free it, and Dart's GC has no idea it exists.

`package:ffi` gives you three tools, in increasing order of how much you should prefer them:

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

Rules that save you a week of debugging:

- **`Arena` by default.** The only reason not to use it is that the allocation must outlive the block.
- **A pointer returned from C has an owner.** Read the header. If the library `malloc`'d it, you call the library's own free function, not `malloc.free` — the allocator may differ.
- **`toNativeUtf8()` allocates.** So does `.toDartString()`, on the Dart side, but only the first one needs freeing.
- **`NativeFinalizer` is not a destructor.** It runs when the GC gets around to it, which may be never. Use it as a safety net under an explicit `dispose()`, not instead of one.

## The two threading traps everyone hits

Both mechanisms have exactly one threading failure that catches people, and they are opposites.

**Channels cannot be used from a background isolate — unless you hand them a token.** Platform channels are bound to the root isolate's binary messenger. Spawn an isolate to parse a large payload, call `invokeMethod` from it, and you get an error rather than a result. The fix is to capture a `RootIsolateToken` on the root isolate and initialise the messenger inside the new one:

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

`RootIsolateToken.instance` is null off the root isolate, which is why it is read outside the closure and captured.

**FFI blocks — that is what synchronous means.** A `MethodChannel` call cannot jank your UI, because it returns a `Future` and the event loop keeps turning. An FFI call to a function that takes 400ms simply does not return for 400ms, and every frame in that window is dropped. Long native work belongs on its own isolate:

```dart
Future<Uint8List> greyInBackground(Uint8List rgba) =>
    Isolate.run(() => toGrey(rgba));
```

Two details make this practical. Pointers are not sendable between isolates, so pass `pointer.address` as an `int` and rebuild it with `Pointer.fromAddress(address)` — all isolates in a Flutter app share one address space, so the address is valid. And a `Uint8List` sent through a port is copied; wrap large buffers in `TransferableTypedData` to move ownership instead.

If the native side needs to call *back* into Dart from its own thread — a decoder finishing a frame, say — use `NativeCallable.listener`. `Pointer.fromFunction` only works when the native code calls you on the same thread that called it, which a worker thread by definition does not.

One more, on the platform side: a channel handler runs on the platform's main thread by default, so heavy Kotlin or Swift work inside a `setMethodCallHandler` blocks the platform UI thread even though Dart is fine. Move it off with a background task queue — `binaryMessenger.makeBackgroundTaskQueue()` on both Android and iOS — and pass that queue when constructing the channel.

## FAQ

**Should I use Pigeon for everything instead of MethodChannel?**
For anything with more than one or two methods, yes. The generated code is the same mechanism with the string constants and the manual argument unpacking removed, and it turns a class of runtime failures into build failures. The cases where a raw channel still makes sense are a single throwaway call, or a dynamic protocol where the method name genuinely is not known at compile time.

**Is FFI faster than a platform channel?**
It avoids serialisation and the queue hop entirely, so for small frequent calls or for large buffers the difference is structural rather than marginal. But that is only the right comparison when both options exist — and they usually do not. You cannot FFI your way to the Android permission dialog, and you should not send a 20MB image through a codec to a C function.

**Can I call Swift or Kotlin directly with FFI?**
Not as such. `dart:ffi` speaks the C ABI. You can expose a C entry point from Swift or Kotlin/Native and call that, but you lose the ergonomics and take on the ABI details yourself. On Android, `jnigen` is the better-supported path to JVM classes; on iOS, `ffigen` can generate bindings to Objective-C, and Swift interop is still moving — verify the current state before designing around it.

**Do I need a plugin package, or can this live in my app?**
Both work. `flutter create --template=plugin` and `flutter create --template=plugin_ffi` scaffold the build wiring, which is most of the annoying part. Putting the code straight in your app's `android/` and `ios/` folders is fine for something app-specific, but a package is what makes it testable and reusable, and it forces you to define the contract.

**Why does my channel work in debug and fail after a hot restart?**
Hot restart tears down the Dart isolate but not the platform side. Handlers registered from Dart-triggered native setup can end up orphaned, and stream subscriptions on an `EventChannel` may leave the native listener registered with a dead sink. Register handlers in the plugin's `onAttachedToEngine` / `register(with:)` — not lazily on first use — and make `onCancel` genuinely clean up.

---

*The mechanism descriptions here are from the official Flutter and Dart documentation; the guidance about when to reach for which tool is my opinion, formed from shipping all three. APIs in this area move — `NativeCallable`, Pigeon's generated interfaces, and Dart's native-assets work have all changed shape recently — so check anything version-dependent against the current docs before you build on it.*
