---
title: "Impeller and a janky frame: how to find where the 16ms actually went"
description: "Impeller is the default renderer now, which killed the shader-compilation class of jank and made most of the old warmup advice useless. Here is what is left: profile mode, the UI-versus-raster split, and the five things that actually blow a frame budget — each with a fix."
seoDescription: "Diagnose Flutter jank under Impeller: profile mode, DevTools Performance view, UI vs raster thread, and fixes for build, layout, saveLayer and image decode."
keywords:
  - flutter jank profiling
  - impeller performance
  - flutter devtools performance view
  - flutter raster thread vs ui thread
  - flutter savelayer performance
  - flutter frame budget 16ms
category: "Deep Dive"
topic: "Performance"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧩"
tags: ["Flutter", "Impeller", "Performance", "DevTools", "Profiling"]
sources:
  - name: "Impeller rendering engine — Flutter docs"
    url: "https://docs.flutter.dev/perf/impeller"
  - name: "Flutter performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
  - name: "Use the Performance view — DevTools"
    url: "https://docs.flutter.dev/tools/devtools/performance"
  - name: "Improving rendering performance"
    url: "https://docs.flutter.dev/perf/rendering-performance"
  - name: "Canvas.saveLayer — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/Canvas/saveLayer.html"
  - name: "Clip enum — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/Clip.html"
  - name: "FrameTiming — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/FrameTiming-class.html"
  - name: "ResizeImage — Flutter API docs"
    url: "https://api.flutter.dev/flutter/painting/ResizeImage-class.html"
  - name: "flutter/flutter#114853 — deprecate --trace-skia for a --trace-graphics flag"
    url: "https://github.com/flutter/flutter/issues/114853"
  - name: "flutter/flutter#140310 — cache-sksl cannot be used with Impeller"
    url: "https://github.com/flutter/flutter/issues/140310"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
draft: false
---

A tester files a bug that says "the product list stutters when I scroll fast on the Pixel." You search for *flutter jank*, and the first three results tell you to run `flutter run --profile --cache-sksl`, capture an SkSL file, and bundle it into your release build. You try it. The flag is gone, or it is ignored, and the stutter is exactly where it was.

That advice was correct for Skia. It is not correct for your app, because your app is almost certainly rendering with Impeller, and Impeller does not compile shaders at runtime at all. The Flutter docs are direct about it: Impeller "precompiles a smaller, simpler set of shaders at engine-build time so they don't compile at runtime." There is nothing to warm up. The `--cache-sksl` and `--bundle-sksl-path` workflow is a Skia-only mechanism, and [issue #140310](https://github.com/flutter/flutter/issues/140310) exists specifically because people kept trying to use it with Impeller.

So one entire category of jank is gone. The other categories are not. A `build()` method that does JSON parsing is still slow. An `IntrinsicHeight` around a big `Row` is still an extra layout pass. `Canvas.saveLayer` is still, in the framework's own words, "one of the most expensive methods in the Flutter framework." A 4032×3024 photo drawn into a 96-pixel avatar is still a bad idea. Impeller changed *which* problems you have, not *whether* you have them.

This is the diagnostic path for the ones that are left: get a reproducible measurement, work out which thread ran long, then narrow to a named widget. Everything after that is mechanical.

## What Impeller removed, and what it left behind

Impeller's stated design goal is predictable cost. From the docs: "Impeller compiles all shaders and reflection offline at build time. It builds all pipeline state objects upfront. The engine controls caching and caches explicitly." That is the sentence that killed the first-run-of-an-animation stutter — the one where the first time a user opened a page with a blur or a gradient, the frame took 200ms while the GPU driver compiled a program.

Where it runs, as of the current docs:

| Platform | Renderer | Notes |
| --- | --- | --- |
| iOS | Impeller only | The docs say there is "no ability to switch to Skia" |
| Android API 29+ | Impeller, by default | Default for iOS and Android API 29+ since Flutter 3.27 |
| Older / non-Vulkan Android | Automatic fallback | Docs: "Impeller falls back to the legacy OpenGL renderer" |
| macOS, Linux, Windows | Impeller, by default | "as of Flutter 3.47" |
| Web | Skia | "It might use Impeller in the future" |

Two practical consequences. First, if you still see a **Shader compilation** marker in the DevTools frames chart, you are not on the Impeller path — check the platform row above and whether something in your build is passing `--no-enable-impeller` or setting `io.flutter.embedding.android.EnableImpeller` to `false` in the manifest. Second, `--trace-skia` is a Skia flag. Under Impeller it will not give you the Skia draw-op breakdown that older blog posts show screenshots of; [issue #114853](https://github.com/flutter/flutter/issues/114853) proposes a renderer-agnostic `--trace-graphics` to replace it. Impeller still emits raster-thread timeline events, so the Timeline events tab is useful — the flag just is not the lever it used to be.

## A frame is a pipeline, and jank is a question about which stage ran long

"16ms" is a budget for the whole pipeline, not for one function. At 60Hz you have 16.67ms per frame; on a 120Hz display it is 8.33ms, which is why a bug report from someone with a high-refresh phone can describe stutter you cannot see on your own device.

Two threads split that budget, and the docs define them precisely. The **UI thread** "executes Dart code in the Dart VM… When your app creates and displays a scene, the UI thread creates a *layer tree*, a lightweight object containing device-agnostic painting commands, and sends the layer tree to the raster thread." The **raster thread** "takes the layer tree and displays it by talking to the GPU." Impeller runs on the raster thread. Note the docs' own caveat: "while the raster thread rasterizes for the GPU, the thread itself runs on the CPU" — a slow raster thread is not automatically a GPU problem.

You can read those two numbers programmatically, which is worth wiring up before you open DevTools at all, because it tells you instantly whether you are hunting a Dart problem or a painting problem:

```dart
import 'package:flutter/scheduler.dart';
import 'package:flutter/widgets.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SchedulerBinding.instance.addTimingsCallback((List<FrameTiming> timings) {
    for (final t in timings) {
      if (t.totalSpan > const Duration(milliseconds: 16)) {
        debugPrint('frame ${t.frameNumber} '
            'build=${t.buildDuration.inMicroseconds}us '
            'raster=${t.rasterDuration.inMicroseconds}us '
            'total=${t.totalSpan.inMicroseconds}us');
      }
    }
  });
  runApp(const MyApp());
}
```

`buildDuration` is "the duration to build the frame on the UI thread"; `rasterDuration` is "the duration to rasterize the frame on the raster thread"; `totalSpan` is the whole span from vsync to raster finish. `FrameTiming` also exposes `layerCacheBytes` and `pictureCacheBytes`, which matter later when you get to images.

## Profile mode, on a real device, before you believe any number

Debug-mode timings are meaningless for this. Debug builds run Dart in the VM's JIT with assertions on and no optimization, and the framework itself does extra work — `debugPrint` of paint bounds, tree integrity checks, the lot. A widget that takes 9ms in debug can take under 1ms in profile.

```bash
flutter devices
flutter run --profile -d <device-id>
```

Profile mode is not available on simulators or emulators for the purpose you care about — you want the actual GPU and the actual thermal behaviour of the device the bug was filed against. Then, from the running terminal, press `P` to toggle the performance overlay, or open the DevTools URL that `flutter run` prints and go to the **Performance** view.

Read the overlay the way the docs describe it: two graphs of the last 300 frames, white lines at 16ms increments, and red bars where a frame blew the budget. Red on the UI graph means your Dart is too expensive. Red on the raster graph means the scene is too complex to draw. That is a two-second triage and it is usually enough to pick which of the next three sections you read. One other flag is still worth knowing: `--trace-systrace` routes timeline events into the platform's own tracer (systrace on Android, os_signpost on iOS), which is what you want when you suspect the jank is happening outside the Dart side entirely — a plugin doing blocking work on the platform thread, for instance.

## Turn on the tracing that names the widget

The frames chart tells you a frame was slow. The **Frame analysis** tab tells you why, in words: select a janky frame and DevTools shows hints for expensive operations it detected in that frame. Start there — it is free and often correct.

When it is not enough, use **Enhance tracing**, the dropdown in the Performance view. It has three toggles:

- **Track widget builds** — every `build()` becomes a timeline event labelled with the widget's name.
- **Track layouts** — every render object layout becomes an event.
- **Track paints** — every render object paint becomes an event.

With these on, the Timeline events tab stops saying "Build" and starts saying "ProductCard.build" nested under "ProductList.build", with durations. That is the moment the investigation becomes trivial.

Two warnings. These toggles add real instrumentation overhead, so the absolute numbers get worse while they are on — use them to find the *name*, then turn them off and re-measure to confirm the fix. And they are per-frame in scope; for a stretch of your own code that spans frames, instrument it yourself:

```dart
import 'dart:developer' as developer;

developer.Timeline.timeSync('decodePriceHistory', () {
  history = PriceHistory.fromJson(payload);
});
```

That event appears on the UI thread in the Timeline events tab with its own bar, next to the framework's.

## UI-thread jank: builds that do too much, layouts that measure twice

Once **Track widget builds** points at a widget, there are only a few shapes this takes.

**A build that does work.** Parsing, sorting, formatting, regex, `DateFormat` construction — anything that is not "describe the UI" — inside `build()`. It runs on every rebuild, which during an animation is every frame. The fix is not clever: hoist it into `initState`, a memoised field, or a `compute()` isolate call, and let `build()` only read the result.

**A rebuild scope that is too wide.** A `setState` at the top of a page rebuilds the page. If the thing that changed is a counter in one corner, wrap only that corner. `AnimatedBuilder` and `AnimatedWidget` take a `child` that is built once and passed through the builder untouched:

```dart
AnimatedBuilder(
  animation: _controller,
  child: const ExpensiveProductCard(),   // built once, not per frame
  builder: (context, child) => Transform.rotate(
    angle: _controller.value * math.pi,
    child: child,
  ),
)
```

`const` constructors do the same job statically: a `const` widget is canonicalised, so the framework can skip its subtree during rebuild rather than diffing it.

**A layout that measures the tree twice.** `IntrinsicHeight` and `IntrinsicWidth` ask every child for its intrinsic size before they can lay anything out — a second walk of the subtree, per frame. The framework's own API docs call the intrinsic-sizing widgets relatively expensive and advise avoiding them where possible. If you are using `IntrinsicHeight` to make two cards in a `Row` the same height, a `SizedBox` with a known height, or `CrossAxisAlignment.stretch` inside a bounded parent, does the job with one pass.

Long lists have a matching fix. A `ListView.builder` whose items are all the same height should say so, because then the scroll machinery can compute offsets arithmetically instead of laying out children to find out where they are:

```dart
ListView.builder(
  itemExtent: 72,
  itemCount: items.length,
  itemBuilder: (context, i) => RowTile(item: items[i]),
)
```

Use `prototypeItem` if the extent is uniform but you would rather not hardcode it. And `shrinkWrap: true` on a list inside another scrollable is the single most common self-inflicted layout cost in Flutter — it forces the list to lay out all of its children to measure itself, which defeats the entire point of `.builder`.

## Raster-thread jank: saveLayer is still the most expensive call in the framework

If the red is on the raster graph, the layer tree is expensive to draw. The dominant cause, on Impeller as on Skia, is an offscreen render pass: the engine draws a subtree into a separate texture, then composites that texture back. That costs an extra pass and a lot of memory bandwidth, and it is exactly what `Canvas.saveLayer` does.

You rarely call it. The docs are explicit that "even if you don't call `saveLayer` explicitly, implicit calls might happen on your behalf, for example when specifying `Clip.antiAliasWithSaveLayer` (typically as a `clipBehavior`)." `Opacity` over a group, `ShaderMask`, `BackdropFilter`, and `ColorFiltered` are the other usual suspects.

DevTools gives you a bisection tool for this that most people never touch. Under **More debugging options** there are toggles to disable whole classes of layer: **Render Clip layers**, **Render Opacity layers**, **Render Physical Shape layers**. Turn one off, re-record, and look at the raster bar. If turning off opacity layers makes the jank vanish, you have your answer in about thirty seconds, without reading a single timeline event.

The fixes are all the same idea — fold the effect into the paint instead of wrapping a subtree in one.

```dart
// Offscreen pass: the subtree is drawn to a texture, then composited.
Opacity(opacity: 0.4, child: Image.asset('assets/hero.jpg'))

// No offscreen pass: alpha is folded into the image's own paint.
Image.asset('assets/hero.jpg', opacity: _fade)   // Animation<double>
```

```dart
// A clip layer, plus a full offscreen pass because of the clipBehavior.
ClipRRect(
  borderRadius: BorderRadius.circular(16),
  clipBehavior: Clip.antiAliasWithSaveLayer,
  child: ColoredBox(color: Colors.indigo, child: child),
)

// The same rounded rectangle, drawn directly. No clip, no layer.
DecoratedBox(
  decoration: BoxDecoration(
    color: Colors.indigo,
    borderRadius: BorderRadius.circular(16),
  ),
  child: child,
)
```

The general rule the docs give is to apply opacity, clipping and shadows to individual widgets rather than to a group higher in the tree, and to ask whether the effect is needed at all. `Clip.antiAlias` — the default `clipBehavior` for most widgets — is far cheaper than `Clip.antiAliasWithSaveLayer`; if someone changed it to the `WithSaveLayer` variant to fix a hairline seam, check whether the seam is still there.

`RepaintBoundary` is the other tool here: it isolates a subtree so that repainting it does not repaint its neighbours, and it lets the raster cache keep the result. But it costs GPU memory per boundary. The docs' framing is right — cache "only where absolutely necessary." A `RepaintBoundary` around every list item is a memory bug wearing a performance-fix costume.

## Images decoded at the wrong size

The last common cause is an image whose decoded size has nothing to do with its displayed size. Flutter decodes images off the UI thread, so this rarely shows up as a tall UI bar; it shows up as a one-frame spike when the image first appears, as memory pressure that causes GC pauses later, and as a raster thread sampling a texture far larger than the box it is drawing into.

The fix is to decode at display size. Both forms are one line:

```dart
// Decode at 320 logical pixels wide instead of whatever the server sent.
Image.network(url, cacheWidth: 320)

// Same thing when you are holding an ImageProvider.
ResizeImage(NetworkImage(url), width: 320)
```

`cacheWidth` and `cacheHeight` are `int?` and, per the docs, "indicate to the engine that the image should be decoded at the specified size," primarily to reduce `ImageCache` memory. Note they are disregarded on web, where decoding is delegated to the browser.

For a hero image you know is coming — the next page in a flow, the first card in a carousel — move the decode out of the frame that needs it:

```dart
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(const AssetImage('assets/hero.jpg'), context);
}
```

If you suspect the image cache is the problem rather than any individual image, `FrameTiming.layerCacheBytes` and `pictureCacheBytes` from the callback earlier will show you the cache growing frame over frame, and `PaintingBinding.instance.imageCache.maximumSizeBytes` lets you cap it.

## FAQ

**Impeller is the default now — do I still need to profile at all?**

Yes. Impeller removed the shader-compilation class of jank, which was the one you could not fix from Dart. Expensive builds, extra layout passes, `saveLayer`, and oversized image decodes are all still yours to fix, and they are all visible in the same DevTools view they were visible in five years ago.

**Why does `--trace-skia` not show me anything useful anymore?**

Because it is a Skia flag and your app is drawing with Impeller. Impeller still emits timeline events on the raster thread, so the Timeline events tab works; you just do not get the Skia draw-op breakdown that flag was built for. There is an open proposal, [flutter/flutter#114853](https://github.com/flutter/flutter/issues/114853), for a renderer-agnostic `--trace-graphics` flag.

**The jank only happens on one specific Android phone. Where do I start?**

Check whether that device is getting the Vulkan path. The docs say Impeller falls back to the legacy OpenGL renderer on Android versions below API 29 or on devices without Vulkan, and the fallback path does not have the same characteristics. Reproduce with `flutter run --profile` on that exact device, and include the chip in any issue you file — the Impeller docs explicitly ask for device and chip details.

**Should I put `RepaintBoundary` everywhere to be safe?**

No. Each boundary is a separate layer with its own GPU memory cost, and the raster cache entries the docs describe as "expensive to construct." Add one where a small subtree animates independently of a large static one — a spinner over a complex page — and measure the raster bar before and after. If the number does not move, take it back out.

**Does any of this apply to Flutter web?**

Partly. The UI-thread half does: builds, layouts, and rebuild scope behave the same. The rendering half does not — web still renders with Skia rather than Impeller, `cacheWidth`/`cacheHeight` are ignored because decoding is delegated to the browser, and DevTools cannot attach in profile mode on web, so you use Chrome DevTools instead.

---

*Everything about renderer defaults, flags, thread definitions and API behaviour above is drawn from the official Flutter docs linked in the sources; the diagnostic order — measure, split by thread, then name the widget — is my own working habit, not a documented procedure. Renderer defaults and flag availability move between releases, so check `docs.flutter.dev/perf/impeller` against the version in your `pubspec.lock` before concluding that something is or is not enabled for you.*
