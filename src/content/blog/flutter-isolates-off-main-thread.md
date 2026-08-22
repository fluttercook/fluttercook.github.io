---
title: "Flutter isolates: what actually goes off the UI thread, and what doesn't"
description: "async/await does not move work to another thread — it only creates a suspension point. Here is what that means for jank, and how compute, Isolate.run, long-lived workers, TransferableTypedData and BackgroundIsolateBinaryMessenger fit together."
seoDescription: "Why async/await still blocks the Flutter UI thread, and how to use compute, Isolate.run, long-lived isolates with SendPort/ReceivePort, and platform channels from a background isolate."
keywords:
  - flutter isolate
  - does async await create a thread in dart
  - flutter compute vs isolate run
  - flutter long lived isolate sendport
  - backgroundisolatebinarymessenger ensureinitialized
  - transferabletypeddata flutter
category: "Deep Dive"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧵"
tags: ["Flutter", "Dart", "Isolates", "Performance", "Concurrency"]
sources:
  - name: "Flutter — Concurrency and isolates"
    url: "https://docs.flutter.dev/perf/isolates"
  - name: "Dart — Isolates"
    url: "https://dart.dev/language/isolates"
  - name: "Isolate.run — Dart API"
    url: "https://api.dart.dev/stable/dart-isolate/Isolate/run.html"
  - name: "compute — Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/compute.html"
  - name: "TransferableTypedData — Dart API"
    url: "https://api.dart.dev/stable/dart-isolate/TransferableTypedData-class.html"
  - name: "BackgroundIsolateBinaryMessenger — Flutter API"
    url: "https://api.flutter.dev/flutter/services/BackgroundIsolateBinaryMessenger-class.html"
  - name: "RootIsolateToken — Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/RootIsolateToken-class.html"
  - name: "Flutter — Performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
draft: false
---

The most expensive misconception in Flutter performance work is that `async` means "on another thread." It does not. Marking a function `async` changes nothing about where its body runs — every statement still executes on the isolate that called it, which in a Flutter app is almost always the **UI isolate**, the one that also builds your widgets and drives your animations.

What `await` gives you is a **suspension point**. The function runs until the first `await`, hands control back to the event loop, and resumes later when the awaited future completes. Between two suspension points, your code owns the thread completely and nothing else — not a tap, not a frame — gets to run. A `jsonDecode` that takes 200 ms inside an `async` function blocks for the full 200 ms, and no amount of `await` sprinkled around it changes that.

The fix is a second isolate: separate memory, separate event loop, real parallelism on a multi-core device. That part is easy. The part people get stuck on is everything around it — what can legally cross the boundary, why a closure that captures `this` throws, why `rootBundle` is missing over there, and why a plugin call fails until you have handed the background isolate a **root isolate token**.

## `async` buys you a suspension point, not a thread

Here is the shape of the code that causes most avoidable jank:

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

Only the first line is genuinely concurrent, and not because of `await` — it is because the socket work happens outside the Dart heap and the VM completes a future when the bytes arrive. Lines two and three are plain synchronous Dart running on the UI isolate. If the payload is a few megabytes, the decode plus the `map` allocation is one uninterrupted block of work sitting between two frames.

You can watch the mechanism directly:

```dart
Future<void> demo() async {
  await null;                          // really suspends: drains microtasks
  for (var i = 0; i < 500000000; i++) {} // no awaits, no yields, no frames
}
```

`await null` does suspend and reschedule. The loop after it is unyielding. There is no preemption in Dart: the event loop can only run the next event once your code returns to it.

How much that costs depends on the refresh rate you are targeting:

| Refresh rate | Frame budget | Frames lost to a 200 ms block |
| --- | --- | --- |
| 60 Hz | 16.7 ms | ~12 |
| 90 Hz | 11.1 ms | ~18 |
| 120 Hz | 8.3 ms | ~24 |

On a 120 Hz phone the budget is roughly half of what most performance advice assumes, and the same work costs you twice as many dropped frames.

## Some of your work is already off the UI thread

Before moving anything, check whether it was ever on the UI thread to begin with. Flutter's engine runs several task runners, and the Dart UI isolate is only one of them. Work that is already elsewhere:

- **Socket and file I/O** through the async `dart:io` APIs. `File.readAsBytes()` does not block your isolate while the disk is read.
- **Rasterization.** Turning your layer tree into GPU commands happens on the raster thread. A slow frame there is a different bug with a different fix.
- **Image decode.** Flutter decodes and resizes images off the UI thread; `dart:ui` exposes async APIs precisely so it can.

What is *not* already off-thread is any pure-Dart CPU work you wrote yourself: `jsonDecode`/`jsonEncode` on large payloads and the object mapping after it, hashing and encryption and compression implemented in Dart, per-pixel image manipulation (as opposed to decoding), sorting or grouping lists with tens of thousands of elements, and regular expressions over large strings — which can be far slower than the input size suggests.

The rule from the Flutter docs is refreshingly blunt: reach for an isolate when a computation takes longer than a frame gap. Not before.

## `Isolate.run` is the whole answer for one-shot work

`Isolate.run` spawns an isolate, runs a callback, returns the value, and shuts the isolate down. Applied to the example above:

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

`compute` is the older API and still useful, mostly because it also compiles for web:

```dart
import 'package:flutter/foundation.dart';

List<Photo> parsePhotos(String body) {        // top-level or static
  final decoded = jsonDecode(body) as List<Object?>;
  return decoded.cast<Map<String, Object?>>().map(Photo.fromJson).toList();
}

final photos = await compute(parsePhotos, response.body);
```

In current Flutter, the native implementation of `compute` is a one-line wrapper: it calls `Isolate.run(() => callback(message))`. The interesting difference is the **web** implementation, which does `await null;` and then calls your callback **on the same thread**. Dart web has no isolates. `compute` on Flutter web keeps your code compiling; it does not keep your frames.

| | `compute` | `Isolate.run` | `Isolate.spawn` |
| --- | --- | --- | --- |
| Lifetime | One call | One call | Until you kill it |
| Messages | One in, one out | One out | As many as you like |
| Takes a closure | One argument, one callback | Any zero-arg closure | Entry point + one message |
| Compiles for web | Yes (runs inline) | No | No |
| Right for | Legacy code, web-shared code | Everything one-shot | Long-lived workers |

Both `Isolate.run` and `compute` return their result through `Isolate.exit`, which hands over the object graph instead of copying it. The *result* direction is therefore cheap regardless of size. The *argument* direction is not — everything the closure captures is copied on the way in.

## A worker that stays alive: ports, a handshake, and a request table

Spawning is not free, and if you parse a message every 100 ms in a chat app you will pay that cost constantly. A long-lived worker amortises it. The two primitives are `ReceivePort` (the listener) and `SendPort` (the handle you can send to another isolate).

The awkward part is the handshake: to talk both ways you need each side to hold the other's `SendPort`, and a `ReceivePort` can only be listened to once. The standard trick is a `RawReceivePort` whose handler you set before spawning, then upgrade to a real `ReceivePort`.

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

Three things worth noticing. The **request id** matters: messages are not guaranteed to come back in send order once you do anything asynchronous inside the worker, so pair each response with the completer that asked for it. Errors do not propagate across the boundary — a thrown exception in the worker just kills that message unless you catch it and send back a `RemoteError` yourself. And the worker has its own event loop, so a single slow message still blocks the *worker's* subsequent messages; one worker is a serial queue, not a pool.

If you find yourself building a pool with backpressure and cancellation, the Flutter docs point at [`worker_manager`](https://pub.dev/packages/worker_manager) rather than having you write it again.

## The boundary copies — and some things refuse to be copied

Isolates share nothing. When you `send()` a mutable object, the whole reachable graph is deep-copied into the receiving isolate's heap. Mutating it on one side does not affect the other, and that includes global variables: a spawned isolate gets its own copy of your top-level state, so a `configuration` global mutated in the worker stays unchanged in the UI isolate.

Immutable values are the exception. Strings and unmodifiable byte data are passed by reference rather than copied, which is why the `Isolate.run` example above captures `response.body` — the multi-megabyte string is not duplicated on the way in.

| Crosses fine | Throws or misbehaves |
| --- | --- |
| `null`, `num`, `bool`, `String` | `BuildContext`, `State`, any widget |
| Lists, maps, sets of sendable values | `dart:ui` objects such as `Image` and `Picture` |
| `TypedData` (`Uint8List`, `ByteData`, …) | Open `Socket`s and other native-resource handles |
| Records and instances of your own classes | Closures capturing any of the above |
| `SendPort`, `Capability`, `RootIsolateToken` | `ReceivePort` (send its `sendPort` instead) |

The failure people hit first looks like this:

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

The closure looks like it captures a string. It captures `this`, because `_raw` is an instance field. Copy the value into a local first and the closure captures only the local:

```dart
Future<void> _parse() async {
  final raw = _raw;
  final data = await Isolate.run(() => jsonDecode(raw));
}
```

The same rule kills two other tempting patterns. There is **no `rootBundle` in a spawned isolate** — load the asset on the UI isolate and send the bytes. And you cannot build, lay out, paint or touch `dart:ui` objects there. If a worker produces an image, send back the raw pixel bytes and decode on the UI isolate.

## `TransferableTypedData` moves bytes instead of copying them

For large binary payloads going *into* a worker — camera frames, audio buffers, downloaded files — the copy is the expensive part. `TransferableTypedData` transfers ownership instead:

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

Two rules make it safe and are easy to trip over: `materialize()` may be called **exactly once**, and after you have wrapped a list in a `TransferableTypedData` the original buffers must be treated as gone. Materialising twice, or in the isolate that sent it, throws. Use it when the buffer is large enough that the copy shows up in a profile; for a few kilobytes a plain `Uint8List` is simpler and fast enough.

## Plugins in a background isolate need a root isolate token

This is where most people actually get stuck. Platform channels are wired to the root isolate's binary messenger. A freshly spawned isolate has none, so the first `MethodChannel` call from a worker fails — including calls buried inside plugins like `shared_preferences` or `path_provider`.

The fix is two lines, but they have to be in the right two isolates:

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

`RootIsolateToken.instance` is only non-null **on the root isolate**, so read it before you spawn and capture it in the closure. Calling `ensureInitialized` must happen inside the worker, before the first channel call.

What this does not buy you:

- **No unsolicited messages from the host.** You can call out and get a reply. You cannot receive pushes the platform initiates on its own — a Firestore snapshot listener or a plugin's event stream will not work from a background isolate. Query, don't subscribe.
- **No guarantee for every plugin.** Plugins that require an `Activity`, or that keep per-engine state on the host side, can still misbehave. Test the specific plugin rather than assuming.
- **Nothing on web**, where `RootIsolateToken.instance` has no meaning because there are no isolates to register.

If you need the host platform to wake *you*, that is a different mechanism — a background execution plugin registering its own entry point — not `BackgroundIsolateBinaryMessenger`.

## Measure before you pay for a spawn

Spawning costs time and memory, and the copy in costs more the bigger the message. For work in the single-digit milliseconds, an isolate can easily be slower than doing it inline. Two cheap ways to find out:

```dart
import 'dart:developer';

Timeline.timeSync('parse feed', () {
  result = jsonDecode(body);
});
```

That block shows up as a named slice in the DevTools timeline, in the UI lane, with its real duration. Comfortably under your frame budget: leave it alone. Straddling frame boundaries: you have found your isolate candidate. The performance overlay is the faster first check — a tall bar in the **UI** graph means Dart work like this, while a tall bar in the **raster** graph means shaders or overdraw, and an isolate will not help at all.

One middle option is underused: split the work into chunks and `await null` between them. It stays on one isolate — no copying, no sendability rules, no plugin problems — and lets frames through between chunks. It does not use a second core, so it is worse for throughput, but for a merely awkward workload it is often the smaller change.

## FAQ

**Does `async`/`await` ever move work to another thread?**

No. `await` suspends the current function and lets the event loop run other events; the function body always executes on the isolate that called it. Some things you await — network sockets, file reads, image decode — genuinely happen elsewhere, but that is the runtime doing the work outside Dart, not `await` creating a thread.

**Should I use `compute` or `Isolate.run` in new code?**

`Isolate.run` for anything mobile or desktop: it takes an ordinary closure and does not force you to hoist a top-level function. Use `compute` when the same file has to compile for web, remembering that on web it runs inline and buys you nothing but compatibility.

**How many isolates should I spawn?**

One long-lived worker handles a stream of similar jobs well and costs one spawn. Going wider only helps if the work is genuinely parallel and the device has cores to spare — and each isolate carries its own heap, so a pool of eight is a real memory decision, not a free one.

**Why does my plugin still fail after calling `ensureInitialized`?**

Check three things: that you read `RootIsolateToken.instance` on the root isolate rather than inside the worker, that `ensureInitialized` runs before the first channel call, and that the plugin is not trying to push events to you. Background isolate channels support request/response only; anything the host initiates unsolicited will not arrive.

**Can a background isolate load assets with `rootBundle`?**

No. Asset loading goes through the root isolate's bundle. Read the asset on the UI isolate and pass the `String` or `Uint8List` into the worker — strings are sent by reference, and large byte buffers can be transferred with `TransferableTypedData`.

---

*The API behaviour here is from the official Flutter and Dart documentation linked above; the guidance about when an isolate is worth it, and the suggestion to chunk work instead, is my own judgement. Isolate APIs and the `compute` implementation have changed across releases — verify anything version-dependent against the docs for the SDK you ship.*
