---
title: "Dart streams in depth: backpressure, broadcast, and the leaks in between"
description: "Most stream bugs are one of four things: a subscription never cancelled, a single-subscription stream listened to twice, an error that kills the stream, or a producer that ignores pause. Here is how each one works."
seoDescription: "Dart Stream internals explained: single-subscription vs broadcast, pause and backpressure, StreamController lifecycle, error handling with cancelOnError, transformers, and how to avoid subscription leaks."
keywords:
  - dart stream tutorial
  - stream controller broadcast
  - dart stream backpressure pause
  - stream subscription leak flutter
  - dart async generator yield
  - cancelOnError dart
category: "Deep Dive"
topic: "Dart"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-13"
emoji: "🌊"
tags: ["Dart", "Async", "Streams", "Performance", "Architecture"]
sources:
  - name: "Stream class — Dart API docs"
    url: "https://api.dart.dev/stable/dart-async/Stream-class.html"
  - name: "StreamController class — Dart API docs"
    url: "https://api.dart.dev/stable/dart-async/StreamController-class.html"
  - name: "StreamSubscription class — Dart API docs"
    url: "https://api.dart.dev/stable/dart-async/StreamSubscription-class.html"
  - name: "Asynchronous programming: streams — Dart documentation"
    url: "https://dart.dev/libraries/async/using-streams"
  - name: "Creating streams in Dart"
    url: "https://dart.dev/libraries/async/creating-streams"
  - name: "StreamTransformer class — Dart API docs"
    url: "https://api.dart.dev/stable/dart-async/StreamTransformer-class.html"
related:
  - slug: "flutter-isolates-off-main-thread"
    title: "Flutter isolates: what actually goes off the UI thread, and what doesn't"
  - slug: "dart-records-and-patterns"
    title: "Records and patterns in Dart: what they replace"
draft: false
---

`Bad state: Stream has already been listened to.` is the error that sends most people to Stack Overflow, and the answer they find — "use `.asBroadcastStream()`" — is usually the wrong fix. It makes the error go away and quietly changes the delivery semantics of your data.

## Two kinds of stream, and why the default is the strict one

A **single-subscription** stream can be listened to exactly once. It buffers events until a listener arrives, and it delivers every event to that listener. File reads, HTTP response bodies, and `async*` functions produce these.

A **broadcast** stream can have any number of listeners, delivers events only to those currently subscribed, and buffers nothing. A listener that arrives late has simply missed what came before.

```dart
final single = StreamController<int>();       // single-subscription
final bus    = StreamController<int>.broadcast();
```

That "buffers nothing" is the crux. Converting a single-subscription stream to broadcast to silence an error means events emitted before your second listener attaches are gone — not delayed, gone. If the stream carries a login result and your second widget subscribes one frame later, it will wait forever for an event that already fired.

The right fixes, in order of preference:

1. **Listen once, in one place**, and fan out from there — a repository holding the value, a `ValueNotifier`, a state container.
2. If you genuinely need multiple independent listeners, make the source broadcast **at creation**, not by conversion, so the semantics are the ones everyone downstream sees.
3. If late listeners must see the last value, you need a replay behaviour — hold the latest value yourself and emit it on subscribe, or use a package that provides it.

## Backpressure: `pause` is a request, not a guarantee

`StreamSubscription.pause()` asks the producer to stop. Whether it can depends entirely on who is producing.

```dart
final sub = stream.listen(handle);
sub.pause();          // ask
sub.pause(future);    // resume automatically when `future` completes
sub.resume();
```

Three producer categories behave differently:

| Producer | Honours pause? | What happens to events |
| --- | --- | --- |
| `async*` generator | yes | generator suspends at `yield` |
| `StreamController` with `onPause` handler | if you implement it | your code must stop pushing |
| `StreamController` without handlers | no | events buffer in the controller, unbounded |
| Broadcast controller | no | events are dropped for paused listeners |

That third row is the memory leak nobody sees coming. If a controller has no `onPause` and the producer keeps calling `add()`, the events queue in the controller's internal buffer. Nothing bounds that buffer. A fast producer and a slow consumer will grow it until the process dies.

`await for` pauses the subscription automatically for the duration of the loop body, which is why it is the safest way to consume a stream you might process slowly:

```dart
await for (final chunk in fileStream) {
  await writeToDatabase(chunk);   // subscription is paused here
}
```

Compare to `stream.listen((chunk) async { await writeToDatabase(chunk); })` — the callback returns a `Future` the stream never awaits, so events keep arriving while writes pile up. **This is the single most common async mistake I see in Flutter code review**, and it produces no error at all; it just uses more memory and finishes in the wrong order.

If you must use `listen`, pause explicitly:

```dart
late final StreamSubscription<Chunk> sub;
sub = stream.listen((chunk) {
  sub.pause(writeToDatabase(chunk));  // resumes when the future completes
});
```

## Errors end streams, unless you say otherwise

By default, an error on a stream delivered to `listen` **does not** end the subscription — but an error inside `await for` throws out of the loop, and an error in a subscription with `cancelOnError: true` cancels it.

```dart
stream.listen(
  onData,
  onError: (Object e, StackTrace s) => log(e),
  onDone: cleanUp,
  cancelOnError: false,   // default: keep listening after errors
);
```

`onDone` fires when the stream closes normally. It does **not** fire when you cancel the subscription yourself — a distinction that catches people cleaning up in `onDone` and wondering why it never runs.

To keep a stream alive across errors from a transformation, handle the error inside the transformation rather than letting it escape:

```dart
stream.asyncMap((item) async {
  try {
    return Ok(await process(item));
  } catch (e) {
    return Err<Result>(e.toString());
  }
});
```

## The lifecycle checklist

Almost every stream leak in a Flutter app is one of these:

- **A subscription created in `initState` and not cancelled in `dispose`.** The widget goes away; the callback keeps firing and touches `setState` on a dead element.
- **A `StreamController` never closed.** Close it in `dispose`, and remember that closing does not cancel listeners — it completes them.
- **A subscription created inside `build`.** It gets recreated on every rebuild and the old ones are never cancelled. Nothing subscribes in `build`, ever.
- **A controller whose `onCancel` never releases the underlying resource** — a socket, a timer, a platform listener.

The disciplined shape:

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

The `didUpdateWidget` branch is the one people forget. A widget whose configuration changes keeps its old subscription pointed at the old source.

Better still: use `StreamBuilder`, which handles all of this, and reach for a manual subscription only when you need side effects rather than rendering.

## Writing your own transformer

`StreamTransformer.fromHandlers` covers most needs and is easier to get right than implementing `bind`:

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

Note what this does not do: it drops events rather than delaying them, and it has no trailing emission. That is a throttle, not a debounce, and the difference matters for search inputs — a debounce sends the *last* keystroke, a throttle sends the *first*. For search you almost always want debounce.

## FAQ

**When should I use `async*` versus a `StreamController`?**

`async*` when the events come from a loop you control — it handles pause correctly for free. A controller when events arrive from callbacks you don't drive.

**Does `StreamBuilder` cancel its subscription?**

Yes, on dispose and when the `stream` property changes. It does not close the controller — that is still yours.

**Why does my broadcast stream miss the first event?**

Because listeners attached after `add()` never receive it. Broadcast streams have no buffer. Emit after subscribing, or hold the value yourself.

**Is `await for` slower than `listen`?**

Not meaningfully, and it is safer. Its real limitation is that you cannot easily listen to two streams concurrently in one function.

**How do I combine two streams?**

`Stream.zip`-style combinators are not in the SDK; either merge manually with a controller, or use a package for the reactive operators.

---

*Single-subscription and broadcast semantics, pause/resume behaviour, `cancelOnError`, `onDone` versus cancel, and `StreamTransformer.fromHandlers` are documented in the Dart API references linked above. The leak checklist, the ordering of fixes for the "already listened to" error, the `didUpdateWidget` caution and the throttle-versus-debounce judgement are my own from debugging these in production apps.*
