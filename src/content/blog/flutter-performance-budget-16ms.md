---
title: "A Flutter frame budget you can hold yourself to, instead of \"optimise later\""
description: "Performance is not a debugging session you schedule after the feature ships. It is a budget with line items: 16.6 ms a frame at 60 Hz, 8.3 ms at 120 Hz, split across the UI and raster threads. Six rules, the code that enforces each one, and how to measure it so you can verify instead of trust."
seoDescription: "Treat Flutter performance as a 16.6 ms frame budget with line items: const constructors, rebuild scope, ListView.builder, image decode size, saveLayer, RepaintBoundary."
keywords:
  - flutter frame budget
  - flutter 16ms frame
  - flutter performance best practices
  - flutter repaintboundary
  - flutter listview builder performance
  - flutter cachewidth image memory
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "⏱️"
tags: ["Flutter", "Performance", "Rendering", "DevTools"]
sources:
  - name: "Flutter — Performance best practices"
    url: "https://docs.flutter.dev/perf/best-practices"
  - name: "Flutter — Using the performance overlay"
    url: "https://docs.flutter.dev/perf/ui-performance"
  - name: "FrameTiming — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/FrameTiming-class.html"
  - name: "RepaintBoundary — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/RepaintBoundary-class.html"
  - name: "ResizeImage — Flutter API docs"
    url: "https://api.flutter.dev/flutter/painting/ResizeImage-class.html"
  - name: "Clip — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/Clip.html"
  - name: "ImageCache — Flutter API docs"
    url: "https://api.flutter.dev/flutter/painting/ImageCache-class.html"
  - name: "TimelineSummary — flutter_driver API docs"
    url: "https://api.flutter.dev/flutter/flutter_driver/TimelineSummary-class.html"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
draft: false
---

"We'll optimise later" is a plan to do the hardest possible version of the work. Later means the list view already has six nested builders, the image URLs already come from three different services, and nobody remembers which of the twelve widgets on screen is the one repainting. You end up bisecting a timeline instead of writing code.

The alternative is not heroics. It is a budget. A frame has a fixed amount of time in it, that time is divided between two threads, and every widget you write spends some of it. If you know the number and you know the line items, you can decide at the moment you write the code whether you can afford it — the same way you decide whether a network call belongs on the main path.

This is the budget I hold myself to, the six line items that account for nearly all of it, and how to measure each one. Measuring matters more than the rules: a rule you cannot verify is superstition, and Flutter has enough performance folklore already.

## The budget is 16.6 ms, and it is split in two

A 60 Hz display asks for a new frame every 16.6 ms. A 120 Hz display asks every 8.3 ms. That is the whole budget — not for your code, for everything: animation ticks, your `build` methods, layout, paint, and then turning the result into GPU commands.

Flutter does that work on two threads. The **UI thread** runs Dart: it ticks animations, rebuilds dirty widgets, lays out and paints the render tree, and produces a layer tree describing what to draw. The **raster thread** takes that layer tree and turns it into actual GPU work. They pipeline — while the raster thread rasterises frame *n*, the UI thread can already be building frame *n+1* — so the constraint is not that their sum fits in 16.6 ms. It is that **each one, on its own, fits in 16.6 ms**. Whichever is slower sets your frame rate.

That distinction decides where you look. A `build` method that allocates a thousand objects is a UI-thread problem and no amount of shader tuning will fix it. A full-screen blur is a raster-thread problem and shaving rebuilds will not touch it.

Because you want headroom for the frames that aren't average — the one where a route pushes, an image finishes decoding, and a GC runs — I budget half:

| Refresh rate | Frame budget | UI thread target | Raster thread target |
|---|---|---|---|
| 60 Hz | 16.6 ms | ≤ 8 ms | ≤ 8 ms |
| 90 Hz | 11.1 ms | ≤ 5.5 ms | ≤ 5.5 ms |
| 120 Hz | 8.3 ms | ≤ 4 ms | ≤ 4 ms |

The halving is a choice, not a law. The refresh rates are the law.

One platform note while you are picking a row: on iPhone models with ProMotion, apps are capped at 60 Hz unless the app opts in. Add this to `ios/Runner/Info.plist` if you actually want the 120 Hz row to apply:

```xml
<key>CADisableMinimumFrameDurationOnPhone</key>
<true/>
```

Here are the six line items, each with the rule and the check.

| Line item | Rule | Check |
|---|---|---|
| `const` constructors | Every widget that can be `const` is `const` | `flutter analyze` with the const lints |
| Rebuild scope | The rebuilt subtree is the subtree that changed | `debugPrintRebuildDirtyWidgets` |
| Lists | Lazy by default; fixed extent where possible | Count builder calls |
| Images | Decode at display size, not source size | `debugInvertOversizedImages` |
| `saveLayer` | Zero offscreen passes on scrolling content | `checkerboardOffscreenLayers` |
| `RepaintBoundary` | Placed for a reason you can name | `debugRepaintRainbowEnabled` |

## `const` is a diff optimisation, not a style preference

Most people learn `const` as "the linter wants it". What it actually does is change the shape of the element diff.

Dart canonicalises const expressions: two const expressions of the same type with the same arguments evaluate to *the same instance*. So a `const` widget in a `build` method is not rebuilt on the next frame — it is the identical object, allocated once, forever.

That identity is what the framework checks. When a parent rebuilds, each child element compares the new widget against the one it is already holding. If they are the same object, the element returns immediately: no `update`, no recursion into that subtree, no work at all. Drop the `const` and you get a fresh instance every rebuild, so the framework has to walk in and compare fields even when nothing changed.

```dart
// New instance every parent rebuild; the diff walks into this subtree.
Padding(
  padding: EdgeInsets.all(16),
  child: Text('Total'),
)

// One instance for the lifetime of the program; the diff stops here.
const Padding(
  padding: EdgeInsets.all(16),
  child: Text('Total'),
)
```

Be honest about the size of the win: for one `Padding` it is nothing. For a list row with fifteen static children, rebuilt for every one of forty visible rows during a fling, it is not nothing. And the cost of getting it right is zero, because you can make the analyser do it.

```yaml
# analysis_options.yaml
linter:
  rules:
    - prefer_const_constructors
    - prefer_const_constructors_in_immutables
    - prefer_const_literals_to_create_immutables
    - prefer_const_declarations
```

**Measure it:** `flutter analyze` fails the build on a missed `const`. To see the effect rather than the lint, set `debugPrintRebuildDirtyWidgets = true` in `main()` and scroll — every rebuilt widget prints. The widgets you expected to be inert should not be in that log.

What `const` does *not* do is prevent painting. A const widget still paints when its layer repaints. That is line item six.

## `setState` has a blast radius; make it small

`setState` marks the whole `State` dirty. If that `State` is your page, one changing integer rebuilds the page. The framework is fast at this, which is exactly why it goes unnoticed until the page has grown a chart and a list.

The fix is not to avoid `setState`. It is to make the rebuilding thing small — either by extracting the changing part into its own small widget, or by rebuilding from a listenable at the point of use.

```dart
class CartBar extends StatelessWidget {
  const CartBar({super.key, required this.itemCount});

  final ValueListenable<int> itemCount;

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<int>(
      valueListenable: itemCount,
      // `child` is built once and handed to every builder call.
      child: const Icon(Icons.shopping_cart),
      builder: (context, count, child) {
        return Badge(label: Text('$count'), child: child!);
      },
    );
  }
}
```

Two things are doing work there. `ValueListenableBuilder` keeps the rebuild inside the builder — everything above it in the tree is untouched. The `child` parameter passes a subtree *through* the builder without rebuilding it — `AnimatedBuilder` and `ListenableBuilder` take one too. `AnimatedBuilder` is where it matters most, because an animation rebuilds sixty or a hundred and twenty times a second.

```dart
AnimatedBuilder(
  animation: controller,
  child: const ExpensiveStaticContent(),   // built once
  builder: (context, child) => Transform.rotate(
    angle: controller.value * math.pi,
    child: child,
  ),
)
```

If you use `provider`, `Selector` is the same idea applied to a model: it rebuilds only when the value you select out of the model actually changes, rather than on every `notifyListeners()`.

```dart
Selector<CartModel, int>(
  selector: (_, cart) => cart.itemCount,
  builder: (context, count, child) => Badge(label: Text('$count'), child: child!),
  child: const Icon(Icons.shopping_cart),
)
```

**Measure it:** `debugPrintRebuildDirtyWidgets` again, or DevTools' rebuild tracking. Trigger the state change once and read the list of what rebuilt. If a widget you did not touch is in there, the listener is attached too high.

## Lazy by default, and the `Column` that isn't

This is the mistake that shows up in every performance review, and it is a one-line mistake:

```dart
// Builds, lays out and paints all 400 rows. Every one of them. Now.
SingleChildScrollView(
  child: Column(
    children: [for (final r in rows) RowTile(data: r)],
  ),
)
```

A `Column` inside a scroll view gets unbounded height, so it lays out every child to find out how tall it is. There is no viewport culling to save you, because as far as the `Column` is concerned everything is on screen. Forty rows is survivable; four hundred is a visible freeze on the frame that builds it.

`ListView.builder` inverts this: it builds children on demand as they approach the viewport, and disposes them as they leave. Adding `itemExtent` goes further — when the sliver knows every child is exactly 72 logical pixels tall, it can compute which indices are visible with arithmetic instead of laying children out to find out, and the scrollbar and `jumpTo` become exact.

```dart
ListView.builder(
  itemCount: rows.length,
  itemExtent: 72,                       // or prototypeItem, if the height is derived
  itemBuilder: (context, index) => RowTile(data: rows[index]),
)
```

The related trap is `shrinkWrap: true`. It exists so a list can size itself to its content — which means laying out *all* of its children, which is exactly the laziness you wanted. It is fine for six settings rows and wrong for a feed. When you need a header above a long list, use slivers instead of nesting scrollables:

```dart
CustomScrollView(
  slivers: [
    const SliverToBoxAdapter(child: ProfileHeader()),
    SliverFixedExtentList(
      itemExtent: 72,
      delegate: SliverChildBuilderDelegate(
        (context, index) => RowTile(data: rows[index]),
        childCount: rows.length,
      ),
    ),
  ],
)
```

**Measure it:** count the builder calls. Put this at the top of `itemBuilder`, open the screen, and check that the number of lines printed is roughly the visible rows plus the cache extent, not the length of the list.

```dart
itemBuilder: (context, index) {
  assert(() {
    debugPrint('build row $index');
    return true;
  }());
  return RowTile(data: rows[index]);
}
```

The `assert` wrapper means the whole thing is compiled out of release builds.

## Images cost four bytes per pixel, at whatever size you let them decode

A decoded image lives in memory as raw pixels, four bytes each. A 4032 × 3024 photo from a phone camera is about 12.2 million pixels, so roughly 48 MB decoded — and it costs that whether you display it full screen or in a 96 px avatar, because the default is to decode at the source resolution.

Flutter's `ImageCache` holds decoded images, up to 1000 entries or 100 MiB by default. Fill it with unresized photos and you are evicting and re-decoding constantly. Decoding runs off the UI thread, but the eviction churn, the allocation pressure and the resulting GC do not stay off it.

`cacheWidth` and `cacheHeight` tell the decoder the target size. They are in *device* pixels, not logical ones, so scale by the device pixel ratio:

```dart
final dpr = MediaQuery.devicePixelRatioOf(context);

Image.network(
  avatarUrl,
  width: 96,
  height: 96,
  cacheWidth: (96 * dpr).round(),
)
```

For an `ImageProvider` you are passing around rather than an `Image` widget, `ResizeImage` is the same mechanism as a provider wrapper:

```dart
Image(image: ResizeImage(AssetImage('assets/hero.png'), width: 640))
```

If your app is image-heavy on low-memory devices, it is also reasonable to shrink the cache itself, so that a burst of large images cannot claim 100 MiB:

```dart
PaintingBinding.instance.imageCache.maximumSizeBytes = 50 << 20; // 50 MiB
```

**Measure it:** set `debugInvertOversizedImages = true` (from `package:flutter/painting.dart`). Any image decoded substantially larger than the size it is drawn at renders upside down and logs the details. It is impossible to miss, which is the point. DevTools exposes the same flag as a toggle in the Inspector.

## `saveLayer` is the expense you incur by accident

Most drawing in Flutter goes straight into the current layer. Some effects cannot: they need the subtree rendered into an offscreen buffer first, then composited back. That is `saveLayer`, and it means an extra render target allocation, an extra pass, and a texture upload — per frame, on the raster thread. One of them in a static screen is nothing. One of them inside a list row is one per visible row, per frame, during a fling.

The widgets that commonly trigger it: `Opacity` over a subtree, `ShaderMask`, `ColorFilter`, `BackdropFilter`, `Text` with a fading overflow shader, and any clip configured as `Clip.antiAliasWithSaveLayer` — which the enum documentation itself flags as the most expensive option.

The alternatives are usually more specific, not more clever:

| Instead of | Use | Why |
|---|---|---|
| `Opacity` over a solid colour | the colour's own alpha | drawn in the same layer |
| `Opacity` over an image | `Image(color: …, colorBlendMode: BlendMode.modulate)` | the blend happens in the image paint |
| `ClipRRect` around a coloured box | `DecoratedBox` with `borderRadius` | the painter rounds the corners itself |
| `ClipRRect` around an image | `BoxDecoration(image: DecorationImage(…), borderRadius: …)` | same, clipped inside the paint |
| `Clip.antiAliasWithSaveLayer` | `Clip.antiAlias`, or `Clip.hardEdge` | only the first form forces the offscreen pass |

Two details worth knowing. `Opacity` with a value of exactly `0.0` or `1.0` does not composite at all — the render object short-circuits — so an opacity animation is only expensive in between. And `ClipRRect` defaults to `Clip.antiAlias`, which is not the saveLayer form; you have to ask for `antiAliasWithSaveLayer` explicitly, so if you see it in your codebase, someone probably pasted it to fix an edge artefact.

**Measure it:** turn on the checkerboard.

```dart
MaterialApp(
  checkerboardOffscreenLayers: true,     // saveLayer passes
  checkerboardRasterCacheImages: true,   // cached layers
  home: const HomePage(),
)
```

Every region rendered into an offscreen buffer gets a checkerboard pattern over it. Scroll your list. If the rows are checkered, you have a per-row offscreen pass, and that is where your raster milliseconds went.

## `RepaintBoundary` is a trade, not a free win

When a render object needs to repaint, it calls `markNeedsPaint`, and that walks up the tree until it finds a repaint boundary. Everything under that boundary repaints. So on a screen where a small playhead moves over an expensive static chart, the chart repaints too — sixty times a second, for nothing.

A `RepaintBoundary` stops that walk. Its subtree gets its own layer and repaints independently of its siblings.

```dart
Stack(
  children: [
    const ExpensiveStaticChart(),
    RepaintBoundary(
      child: Playhead(position: position),   // repaints alone
    ),
  ],
)
```

The trade is real: each boundary is another layer, another surface to allocate and composite. Sprinkling them everywhere moves cost from repaint to composition and can make things worse. It also duplicates work you already have — `ListView` and friends already wrap each child in a `RepaintBoundary` by default (`addRepaintBoundaries: true`), so adding your own around list items buys nothing.

The rule I use: add a boundary when you can name the two things it separates — *this* animates, *that* is expensive and static — and delete it otherwise.

**Measure it:** `debugRepaintRainbowEnabled = true` draws a rotating-colour border around each layer as it repaints. A border that changes colour is a layer repainting that frame. Watch which regions flash while only one thing is moving.

For a specific boundary, `RenderRepaintBoundary` keeps counters of how often it painted together with its parent versus independently, and its diagnostics print a plain-language verdict on whether the boundary is earning its keep:

```dart
final box = boundaryKey.currentContext!.findRenderObject()! as RenderRepaintBoundary;
debugPrint(box.toStringDeep());   // debug builds only
```

## Make the budget fail the build, not your memory

Rules you have to remember are rules you will stop applying in month three. Two mechanisms turn this budget into something automatic.

The first is a runtime assertion. `SchedulerBinding.addTimingsCallback` hands you a `FrameTiming` for every frame that completed, with the UI-thread build duration and the raster duration separated:

```dart
import 'package:flutter/scheduler.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  assert(() {
    SchedulerBinding.instance.addTimingsCallback((timings) {
      for (final t in timings) {
        final build = t.buildDuration.inMicroseconds / 1000;
        final raster = t.rasterDuration.inMicroseconds / 1000;
        if (build > 8 || raster > 8) {
          debugPrint('over budget — build ${build}ms, raster ${raster}ms');
        }
      }
    });
    return true;
  }());
  runApp(const MyApp());
}
```

The `assert` keeps it out of release builds. In debug the absolute numbers are inflated — debug builds are not compiled the way releases are — so treat this as a *relative* alarm and confirm anything it flags in profile mode.

The second is CI. The `integration_test` and `flutter_driver` packages can record a timeline for a scripted interaction and summarise it, including a count of frames that blew the budget:

```dart
final timeline = await driver.traceAction(() async {
  await driver.scroll(listFinder, 0, -3000, const Duration(seconds: 2));
});

final summary = TimelineSummary.summarize(timeline);
await summary.writeTimelineToFile('scroll_perf', pretty: true);

expect(summary.computeMissedFrameBuildBudgetCount(), 0);
```

`computeMissedFrameBuildBudgetCount` defaults to a 16 ms budget; it takes an optional `Duration` if you are holding yourself to the 120 Hz row. `computeMissedFrameRasterizerBudgetCount` is the raster-thread twin, and there are percentile helpers so you can assert on p90 rather than the mean — which is the right thing to assert on, because jank is a tail problem.

Run these on a real device in profile mode (`flutter drive --profile`). Numbers from a simulator or a debug build tell you almost nothing about shipping performance.

When something does go over budget, that is when you open DevTools' Performance view, look at the frame chart, and find out which thread and which phase — but the whole point of the budget is that this should be a rare, targeted trip, not the way you develop.

## FAQ

**Does `const` actually make a measurable difference, or is it cargo cult?**

Both, depending on where. The mechanism is real and specific: a const widget is the same object on every rebuild, so the element diff short-circuits instead of walking the subtree. Whether that is measurable depends on how often the subtree is rebuilt — imperceptible on a settings screen, meaningful for rows rebuilt during a fling. Since the lints make it free to apply everywhere, the cost-benefit does not require you to guess correctly.

**Should I wrap every list item in a `RepaintBoundary`?**

No, and `ListView` already does it for you — `addRepaintBoundaries` defaults to true. Adding your own gives you a redundant layer. Boundaries earn their place where a small animating region sits over expensive static content, or the reverse, and you should be able to name both halves before you add one.

**My UI thread is fine but the raster thread is over budget. What's the usual cause?**

Offscreen passes and overdraw. Look for `saveLayer` first — `Opacity` over subtrees, `ShaderMask`, `BackdropFilter`, `Clip.antiAliasWithSaveLayer` — using `checkerboardOffscreenLayers` to find them, especially on scrolling content where the cost multiplies by the number of visible items. Large images composited at full resolution and deeply stacked translucent layers are the next places to look.

**Is 8 ms per thread too strict?**

It is a target with headroom, not a hard requirement — the hard requirement is that each thread stays under the full frame budget. Half is a useful place to aim because real frames are not average: a route transition, an image decode landing, and a garbage collection can coincide, and if your steady state is already at 15 ms there is nothing left to absorb that.

**Do these rules change with Impeller?**

The rendering backend changes the raster-side cost model — most visibly by removing the first-run shader compilation stalls that Skia had. It does not change the UI-thread rules at all: rebuild scope, list laziness and image decode size are framework-level and backend-independent. Offscreen passes are still the raster thread's most expensive routine operation.

---

*The six line items and the mechanisms behind them are documented Flutter behaviour; the specific 8 ms per-thread allocation is my own convention and you should set your own. Anything version-dependent — default cache sizes, lint names, DevTools toggle locations — should be checked against the docs for the Flutter version you are actually on.*
