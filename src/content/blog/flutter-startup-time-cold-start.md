---
title: "Flutter cold start: measuring the time before your first frame"
description: "Startup feels slow long before anyone profiles it. The fix starts with knowing which of the four phases you are actually in — process launch, engine init, Dart main, or your first frame — because each has a different lever."
seoDescription: "How to measure and reduce Flutter startup time: --trace-startup timeline events, the four phases of cold start, what belongs in main(), splash screens, deferred initialisation, and shader warm-up."
keywords:
  - flutter startup time optimization
  - flutter trace-startup timeline
  - flutter cold start first frame
  - flutter main async initialization
  - flutter splash screen native
  - timeToFirstFrameRasterizedMicros
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-31"
emoji: "🚀"
tags: ["Flutter", "Performance", "Startup", "Profiling", "DevTools"]
sources:
  - name: "Flutter — Performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
  - name: "Flutter — Measuring app startup time"
    url: "https://docs.flutter.dev/perf/appendix#measuring-app-startup-time"
  - name: "Flutter — Adding a splash screen"
    url: "https://docs.flutter.dev/platform-integration/android/splash-screen"
  - name: "WidgetsBinding — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/WidgetsBinding-class.html"
  - name: "SchedulerBinding — Flutter API"
    url: "https://api.flutter.dev/flutter/scheduler/SchedulerBinding-class.html"
  - name: "Timeline — Dart API"
    url: "https://api.flutter.dev/flutter/dart-developer/Timeline-class.html"
related:
  - slug: "flutter-app-size-reduction"
    title: "Shrinking a Flutter app: where the megabytes actually are"
  - slug: "flutter-isolates-off-main-thread"
    title: "Flutter isolates: what actually goes off the UI thread, and what doesn't"
draft: false
---

"The app takes three seconds to open" is a complaint, not a measurement. Three seconds from what — the tap, the process spawning, the engine coming up, or the moment your `main()` runs? Each of those is a different problem with a different fix, and optimising the wrong one is how teams spend a sprint moving startup from 2.9 s to 2.8 s.

Cold start in a Flutter app has four phases, and they are separable.

## The four phases

**1. Process launch.** The OS creates the process, loads the executable and its shared libraries, and hands control to the platform runner. Nothing in your Dart code affects this. What does affect it is binary size (see the app size discussion) and, on Android, the number of libraries to link.

**2. Engine initialisation.** The Flutter engine starts, the Dart VM comes up, and — in release builds — the AOT snapshot is mapped in. Plugin registration happens on the platform side here.

**3. Dart `main()` to `runApp()`.** Your code. This is the phase you control completely, and the one people quietly fill with `await`s.

**4. First frame.** Build, layout, paint, rasterise. The user sees something.

The number that matters to a user is the end of phase 4. The number you can move most easily is phase 3.

## Measuring it properly

```bash
flutter run --profile --trace-startup
```

This writes `start_up_info.json` in the build directory with four values in microseconds:

| Key | Meaning |
| --- | --- |
| `engineEnterTimestampMicros` | Absolute timestamp when the engine started |
| `timeToFrameworkInitMicros` | Engine start → framework initialised |
| `timeToFirstFrameRasterizedMicros` | Engine start → first frame on screen |
| `timeToFirstFrameMicros` | Engine start → first frame built |

The gap between `timeToFirstFrameMicros` and `timeToFirstFrameRasterizedMicros` is diagnostic: if it is large, your first frame is expensive to *rasterise* (shaders, large images, complex clipping), not expensive to build. Those are different fixes.

Two rules for the measurement to mean anything: **profile mode, real device**. Debug builds run the Dart JIT and are several times slower to start; a simulator or emulator has different I/O and GPU characteristics from the phone your users have. And measure a genuine cold start — force-stop the app first, not just background it.

For finer detail inside phase 3, add your own timeline events:

```dart
Future<void> main() async {
  Timeline.startSync('bootstrap');
  WidgetsFlutterBinding.ensureInitialized();

  Timeline.startSync('prefs');
  final prefs = await SharedPreferences.getInstance();
  Timeline.finishSync();

  Timeline.startSync('db-open');
  final db = await openDatabase();
  Timeline.finishSync();

  Timeline.finishSync();
  runApp(MyApp(prefs: prefs, db: db));
}
```

These show up as named slices in the DevTools timeline, and they usually end the argument immediately — one of those `await`s is almost always 80% of phase 3.

## What belongs in `main()`, and what does not

The default failure mode is a `main()` that awaits six things before `runApp`. Every one of those awaits is time on a blank screen.

The test for each initialisation is simple: **does the first frame depend on it?**

| Must be before `runApp` | Can be after |
| --- | --- |
| Anything `MyApp`'s constructor requires | Analytics and crash reporter (register the handler early, initialise lazily) |
| The stored theme mode and locale, if you refuse to flash the wrong one | Remote config fetch |
| A synchronous check of "is the user signed in" | Database migrations for screens not shown yet |
| `WidgetsFlutterBinding.ensureInitialized()` | Push notification registration |
| | Preloading images for screen three |

Everything in the right column can move behind the first frame:

```dart
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());

  // After the first frame is on screen.
  WidgetsBinding.instance.addPostFrameCallback((_) {
    unawaited(_initAnalytics());
    unawaited(_warmCaches());
  });
}
```

`addPostFrameCallback` runs after the frame is built. For work that should not compete with the first few frames of animation at all, `SchedulerBinding.instance.scheduleTask` with a low priority defers it until the scheduler is idle.

For the things that genuinely must be awaited, run them concurrently rather than in sequence:

```dart
final (prefs, db, keys) = await (
  SharedPreferences.getInstance(),
  openDatabase(),
  loadSigningKeys(),
).wait;
```

Three 60 ms awaits in sequence are 180 ms; in parallel they are 60. This one line is frequently the largest single win available, because sequential `await`s are the default way people write `main()`.

Heavy synchronous work — parsing a large bundled JSON, deriving a key — belongs in an isolate, not on the startup path of the main thread.

## The blank screen, and what to put on it

Phases 1 and 2 happen before any Dart runs, so no Flutter widget can cover them. What covers them is the **native splash screen**: a launch theme on Android, a launch storyboard on iOS. That is not a hack, it is the platform mechanism, and it is what turns "blank white screen" into "the app is opening".

The important detail is continuity. If the native splash shows a centred logo on brand blue, the first Flutter frame should be a centred logo on brand blue — then transition. A native splash that hard-cuts to a different Flutter splash looks slower than one screen held slightly longer, because the user perceives the flash as a restart.

A related trap: an app that shows its own animated Flutter splash for a fixed 1.5 seconds has *added* 1.5 seconds to startup. If the animation is the brand's, fine — but do not gate it on a timer when the data is already loaded.

## The first frame's own cost

If `timeToFirstFrameRasterizedMicros` is much larger than `timeToFirstFrameMicros`, the problem is on the raster thread.

**Shader compilation.** The first time a particular shader is needed, it must be compiled, and that can stall the frame. Impeller was built specifically to address this class of jank by avoiding runtime shader compilation for its supported cases; on the older Skia backend this was the classic "first run of an animation is janky" cause. Which backend you get depends on platform and Flutter version — check what your build actually uses rather than assuming.

**A too-heavy first screen.** A home screen that builds forty widgets, decodes six images and lays out a complex grid will take a while to produce. A common, honest fix is to make the first frame cheap on purpose: render the shell — app bar, background, skeletons — immediately, and fill in content on the next frames. The perceived improvement is larger than the measured one, which is fine, because perception is the actual goal.

**Large image decodes.** Decoding a 4000-pixel hero image blocks. Ship it pre-sized, and use `cacheWidth`/`cacheHeight` so the decoder produces only what you display.

## A workflow

1. `flutter run --profile --trace-startup` on a real device, three cold runs, take the median.
2. Read `start_up_info.json`. Decide whether your problem is phase 3 (`timeToFrameworkInitMicros` → `timeToFirstFrameMicros`) or phase 4 (build → rasterised).
3. If phase 3: instrument `main()` with `Timeline`, then parallelise or defer.
4. If phase 4: simplify the first screen, check image decode sizes, check the raster thread in the DevTools timeline.
5. Re-measure the same way. Record the number somewhere the team can see it, or it will regress within two sprints.

## FAQ

**Why is my debug build so much slower to start?**

Debug builds use the Dart JIT and include the service isolate, observatory and assertions. The ratio to release is large and not proportional — never tune startup against a debug measurement.

**Does `WidgetsFlutterBinding.ensureInitialized()` cost much?**

It is fast, and it is required before you touch platform channels (which is what `SharedPreferences`, path providers and most plugins do). Call it first in `main()`.

**Should I preload data during the splash?**

Only what the first screen needs. Preloading screen two during the splash trades a measurable startup cost for a benefit the user may never reach.

**Is a smaller app faster to start?**

It affects phase 1, and it matters most on low-end devices and cold filesystem caches. It is a real effect but usually a smaller lever than a sequential `await` chain in `main()`.

**How do I track this over time?**

`--trace-startup` produces a machine-readable file; run it in CI on a fixed device profile and assert on a threshold. A number in a dashboard is the only thing that stops startup time from drifting back up.

---

*The `--trace-startup` output fields, binding APIs and splash screen mechanisms described here are documented in the Flutter performance and platform integration guides linked above. The four-phase framing, the "does the first frame depend on it" test, and the advice to make the first frame deliberately cheap are my own judgement from profiling apps this way. Engine behaviour — including which renderer runs on which platform — changes between Flutter releases; measure your own build in profile mode on a real device.*
