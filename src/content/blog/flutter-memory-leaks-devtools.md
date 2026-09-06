---
title: "Finding a Flutter memory leak: the five objects that never get disposed"
description: "Flutter memory leaks are boring, which is why they survive. Almost all of them are one of five patterns, and DevTools can point at the exact retaining path if you know which two buttons to press."
seoDescription: "How to find and fix memory leaks in Flutter: DevTools memory view, heap snapshots and diffing, retaining paths, controllers and listeners that are never disposed, stream subscriptions, and image cache growth."
keywords:
  - flutter memory leak devtools
  - flutter heap snapshot diff
  - flutter dispose controller listener
  - flutter stream subscription cancel
  - flutter image cache memory
  - flutter retaining path leak
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-30"
emoji: "🧠"
tags: ["Flutter", "Performance", "Memory", "DevTools", "Debugging"]
sources:
  - name: "Flutter — Use the Memory view"
    url: "https://docs.flutter.dev/tools/devtools/memory"
  - name: "State.dispose — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/State/dispose.html"
  - name: "ChangeNotifier — Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/ChangeNotifier-class.html"
  - name: "StreamSubscription — Dart API"
    url: "https://api.dart.dev/stable/dart-async/StreamSubscription-class.html"
  - name: "ImageCache — Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ImageCache-class.html"
  - name: "WeakReference — Dart API"
    url: "https://api.dart.dev/stable/dart-core/WeakReference-class.html"
related:
  - slug: "flutter-lists-performance-builder"
    title: "Why your ListView is slow, and the four fixes that actually work"
  - slug: "flutter-startup-time-cold-start"
    title: "Flutter cold start: measuring the time before your first frame"
draft: false
---

A memory leak in Flutter rarely announces itself. The app works, tests pass, and then somebody navigates between two screens forty times and the process is at 900 MB. On a mid-range Android device that ends as an out-of-memory kill, reported to you as "the app closed by itself" with no stack trace.

Dart is garbage collected, so a leak here means exactly one thing: **something still holds a reference to an object you are done with**. The whole investigation is finding what that something is.

## The five patterns

In practice, almost every leak I have chased in a Flutter app was one of these.

**1. A controller that is never disposed.** `AnimationController`, `TextEditingController`, `ScrollController`, `TabController`, `PageController` — every one of them holds listeners and, in the animation case, a ticker registered with the scheduler.

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

An `AnimationController` without `dispose` keeps ticking after its widget is gone — that is both a leak and wasted frame work, and Flutter will eventually assert about a disposed `TickerProvider`.

**2. A listener added and never removed.** This is the same shape but easier to miss, because the object you leak is not the one you created.

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

The `ChangeNotifier` here outlives the widget — it is the app's model. Because it holds `_onModelChanged`, and that closure holds `this`, the model holds your `State`, which holds its `Element`, which holds a whole subtree. One missing `removeListener` retains an entire screen.

The variant that breaks in a subtler way: `didUpdateWidget` when `widget.model` changes identity. If you only add in `initState`, you listen to the old model forever.

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

**3. A stream subscription that is never cancelled.** Same mechanism, different API, and worse consequences because the callback keeps running.

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

A `setState` from a cancelled-too-late subscription is where "setState() called after dispose()" comes from. That error is the friendly version of this bug; the unfriendly version is silent retention.

**4. A global or singleton that accumulates.** A cache with no eviction, a list of past requests kept "for debugging", a static `Map<String, BuildContext>`. Anything reachable from a top-level variable is reachable forever by definition.

The `BuildContext` case deserves its own warning: storing a context outside the widget that owns it retains the entire element subtree, and the stored context is invalid the moment that widget unmounts. If you find yourself keeping one, the design is wrong.

**5. Images.** Flutter's `ImageCache` holds decoded images, and decoded size is width × height × 4 bytes, not file size. A 4000×3000 photograph is roughly 48 MB in memory regardless of the JPEG being 2 MB on disk. A gallery screen that decodes forty of those at full resolution is not leaking in the strict sense — it is doing exactly what you asked — but the outcome is the same.

## Finding it with DevTools

The memory view gives you three tools. Use them in this order.

**The chart, to confirm there is a leak at all.** Do the suspect action ten times — push a screen, pop it, repeat — with a manual GC between rounds. Memory that steps up and never comes down is a leak. Memory that saws up and down is normal allocation.

**Snapshot diffing, to find what class is leaking.** This is the part that turns guessing into knowing:

1. Take a heap snapshot.
2. Perform the suspect flow (open the screen, close it) several times.
3. Force a GC.
4. Take a second snapshot and diff.

Any class whose instance count went up by the number of repetitions is your leak. Seeing `_ProfileScreenState` at ten instances when only one screen ever exists is the entire diagnosis.

**The retaining path, to find who is holding it.** Select the leaked instance and DevTools shows the chain of references from a GC root down to it. Read it from the bottom up; the first entry that surprises you is the bug. In pattern 2 above, the path reads roughly: static app model → listener list → closure → `_ProfileScreenState`.

That path is the answer. Everything before this step is confirming a leak exists; this step says which line to fix.

## Making leaks fail loudly instead of quietly

The framework has a built-in leak tracker for exactly these object lifecycles. In tests, `flutter_test` can be configured to fail when a disposable object outlives its expected scope, which turns a class of production memory bugs into red CI. The available knobs move between releases, so check the version you are on — but if your project does not have this enabled anywhere, enabling it is a higher-value hour than any individual leak hunt.

Beyond tooling, three habits prevent most of the five patterns:

**Pair every `add` with a `remove` in the same class.** Write `dispose` immediately after `initState`, before the feature works. It is much harder to add later.

**Prefer widgets that own their lifecycle.** `StreamBuilder` cancels its own subscription. `AnimatedBuilder` with a controller you dispose is fine. A manual `listen` in `initState` is the risky shape.

**Give caches a bound.** An LRU with a size cap that you chose deliberately is a cache; a `Map` you only ever insert into is a leak with good intentions.

## Images specifically

```dart
Image.network(
  url,
  cacheWidth: 400,   // decode to what you display, not the source size
  cacheHeight: 300,
)

// Bound the global cache
PaintingBinding.instance.imageCache
  ..maximumSize = 100                 // entries
  ..maximumSizeBytes = 50 << 20;      // 50 MB

// Drop it when the OS is asking for memory back
PaintingBinding.instance.imageCache.clear();
```

`cacheWidth` is the single highest-leverage line in a media-heavy app. It changes the decode itself, so a thumbnail costs thumbnail memory instead of full-resolution memory. `ResizeImage` is the same idea wrapped as an `ImageProvider` for cases where you control the provider rather than the widget.

Also handle `didHaveMemoryPressure` if your app holds large caches of its own — the platform tells you, and ignoring it makes your app the one the OS kills.

## FAQ

**Does `setState` after dispose leak memory?**

The error itself is a symptom, not the leak — but the thing that could still call `setState` is by definition still holding your `State`, so it usually is one.

**Should I use `WeakReference`?**

Rarely. It exists, and it is the right tool for a cache that should not keep its keys alive, but reaching for it to "fix" a leak usually means the ownership model is unclear. Fix the ownership first.

**Do closures capture more than I think?**

Yes — this is the mechanism behind patterns 2 and 3. A closure captures the variables it references, and a method tear-off like `_onModelChanged` captures `this`, meaning the whole `State`.

**Is a growing heap always a leak?**

No. Dart's GC is generational and does not run on a schedule you can predict. Force a GC before concluding anything, and measure the floor after collection rather than the peak.

**Can I profile memory in release mode?**

DevTools needs the VM service, so use profile mode. Release-only leaks are possible but rare; the reference graph is the same.

---

*The DevTools workflow, disposal contracts and `ImageCache` behaviour described here are documented in the Flutter memory tooling guide and the API references linked above. The five-pattern framing, the ordering of the investigation, and the position that an unbounded cache is a leak are my own judgement from debugging apps this way. Leak-tracking APIs in `flutter_test` have changed across releases — check what your SDK exposes.*
