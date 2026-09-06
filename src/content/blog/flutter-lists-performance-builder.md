---
title: "Why your ListView is slow, and the four fixes that actually work"
description: "A janky list is almost never the list widget's fault. It is one of four things: you built everything at once, each item is too expensive, the scroll extent is unknown, or you are decoding full-size images per row."
seoDescription: "Fixing slow Flutter lists: ListView.builder versus ListView, itemExtent and prototypeItem, const items and RepaintBoundary, image decode size, keys and addAutomaticKeepAlives, and how to profile scroll jank."
keywords:
  - flutter listview performance
  - flutter listview builder vs listview
  - flutter itemextent prototypeitem
  - flutter scroll jank profiling
  - flutter repaintboundary list
  - flutter list keepalive
category: "Deep Dive"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-28"
emoji: "📜"
tags: ["Flutter", "Performance", "ListView", "Scrolling", "DevTools"]
sources:
  - name: "ListView — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ListView-class.html"
  - name: "SliverChildBuilderDelegate — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/SliverChildBuilderDelegate-class.html"
  - name: "RepaintBoundary — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/RepaintBoundary-class.html"
  - name: "Flutter — Performance best practices"
    url: "https://docs.flutter.dev/perf/best-practices"
  - name: "AutomaticKeepAliveClientMixin — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/AutomaticKeepAliveClientMixin-mixin.html"
  - name: "Flutter — UI performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
related:
  - slug: "flutter-image-caching-precache"
    title: "The Flutter image pipeline: from a URL to pixels on screen"
  - slug: "flutter-slivers-custom-scroll"
    title: "Slivers, properly: the protocol behind every Flutter scroll effect"
draft: false
---

Every Flutter team hits this. The list works fine with twenty items in development, ships, and then a user with eight hundred saved items reports that scrolling stutters and the app feels heavy. The instinct is to blame `ListView`, or Flutter, or the device.

`ListView` is fine. In every slow list I have profiled, the cause was one of four things, and they are distinguishable in about ten minutes.

## First: find out which thread is late

Before changing anything, run in **profile mode on a real device** and open the DevTools performance view. Each frame is drawn as two bars:

- **UI thread long** → build and layout are expensive. Your `itemBuilder` is doing too much.
- **Raster thread long** → painting is expensive. Shadows, blurs, opacity layers, saveLayer, large images.

That distinction eliminates half the possible fixes immediately. Adding `RepaintBoundary` to a list whose UI thread is the bottleneck does nothing; simplifying widget structure in a list whose raster thread is saturated by a `BackdropFilter` does nothing either.

## Fix 1: build lazily

```dart
// Builds all 800 children immediately, on the first frame.
ListView(children: items.map(ItemTile.new).toList())

// Builds only what is near the viewport.
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, i) => ItemTile(items[i]),
)
```

`ListView(children: ...)` takes an eagerly constructed list. Every child widget is instantiated, and every one is laid out, before the first frame appears. At twenty items that is invisible; at eight hundred it is a multi-second stall on open and a permanent memory cost.

`ListView.builder` uses a `SliverChildBuilderDelegate`, which calls your builder only for the children in and near the viewport, and disposes those that scroll far enough away. This is the single most common cause of a slow list, and the fix is one line.

The same applies to `Column` inside `SingleChildScrollView`: it builds everything, always. For a long list it is the wrong tool no matter how the children are produced. For a short, mixed-content screen it is exactly right — the boundary is roughly "does this fit in two or three screens".

## Fix 2: make each item cheap

Once building is lazy, the cost per item matters. The usual offenders:

**Work inside `itemBuilder`.** Formatting a date, parsing, sorting, filtering, or computing a derived value inside the builder runs for every visible item on every frame that rebuilds. Do it once, upstream:

```dart
// Wrong: DateFormat is constructed per item, per rebuild.
itemBuilder: (context, i) =>
    Text(DateFormat.yMMMd().format(items[i].date)),

// Right: build the formatter once.
final _fmt = DateFormat.yMMMd();
itemBuilder: (context, i) => Text(_fmt.format(items[i].date)),
```

**Missing `const`.** A `const` widget is not rebuilt and not re-created. In a list of a hundred rows, the `const Icon`, `const SizedBox` and `const Divider` add up.

**Deep, unnecessary nesting.** Six nested `Container`s with padding and decoration are six render objects per row. A single `Container` with `EdgeInsets` and a `BoxDecoration` does the same job with one.

**Expensive paint.** `Opacity`, `ClipRRect`, `BackdropFilter` and `BoxShadow` each cost real raster time, and in a list you pay per visible row. `Opacity` in particular triggers a `saveLayer`; if you only need a faded colour, `Color.withValues(alpha: ...)` is far cheaper. If you need rounded corners on a solid colour, `BoxDecoration(borderRadius: ...)` beats a `ClipRRect`.

**`RepaintBoundary` on items that animate.** If one row repaints — a progress bar, a shimmer, a like animation — without a boundary it can force the whole list layer to repaint.

```dart
itemBuilder: (context, i) => RepaintBoundary(child: ItemTile(items[i])),
```

This is a raster-thread fix, not a UI-thread one. Applied everywhere by default it adds layers and can make things worse; applied to the rows that actually animate it is a clear win.

## Fix 3: tell the list how tall items are

A scroll view has to know its total extent to draw a correct scrollbar and to jump to an offset. If every item's height is unknown, it must lay items out to find out.

```dart
// Best, when every row is the same height:
ListView.builder(itemExtent: 72, ...)

// When rows are uniform but you would rather not hard-code a number:
ListView.builder(prototypeItem: const ItemTile.placeholder(), ...)
```

`itemExtent` lets the framework compute positions arithmetically instead of laying out. On a long list this is a substantial saving, and it makes `jumpTo` and scrollbar dragging exact rather than approximate. `prototypeItem` measures one instance and uses that extent, which is the same optimisation without a magic number.

Neither works if rows genuinely vary in height. In that case, accept the cost — or normalise the design so they do not, which is often the better answer for a feed anyway.

## Fix 4: size images to the cell

This is the one that turns a technically-fine list into a memory disaster.

```dart
itemBuilder: (context, i) => Image.network(
  items[i].thumbUrl,
  cacheWidth: 160,   // physical pixels, matched to the cell
  width: 56,
  height: 56,
  fit: BoxFit.cover,
),
```

Decoded image memory is width × height × 4 bytes, regardless of file size. Forty rows each decoding a 3000-pixel source is gigabytes of pixels for a screen showing 56-pixel thumbnails. `cacheWidth` changes the decode, not just the display, and it is usually the difference between a list that survives on a low-end device and one that does not.

## The `keepAlive` question

By default, `ListView.builder` disposes item state once an item scrolls far outside the cache extent. That is what makes it memory-efficient — and it is also why a video in row 3 stops, or a partially typed text field loses its content, when you scroll away and back.

`addAutomaticKeepAlives` is true by default, which means items that *ask* to be kept alive are kept. An item asks by mixing in `AutomaticKeepAliveClientMixin`:

```dart
class _VideoRowState extends State<VideoRow>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => _controller.value.isPlaying;

  @override
  Widget build(BuildContext context) {
    super.build(context); // required by the mixin
    return VideoPlayer(_controller);
  }
}
```

Note `wantKeepAlive` returning a *condition*, not a constant `true`. Keeping every row alive turns the lazy list back into an eager one, one scroll at a time — it is the fix that quietly recreates fix 1's problem.

The alternative, and usually the better one, is to lift the state out of the item entirely. Scroll position, expansion state, selection and draft text belong in your state layer, keyed by item id, not in the row's `State`.

## Keys, and when they matter in lists

For a static list, no keys are needed. For a list that reorders, inserts or removes, and whose items hold state, keys are what let Flutter match the right element to the right item:

```dart
itemBuilder: (context, i) => ItemTile(key: ValueKey(items[i].id), items[i]),
```

Without a key, removing the first item makes every subsequent element take on the next item's data while keeping the previous item's state — which shows up as a checkbox that appears to move, or an animation that plays on the wrong row.

## A checklist

1. Profile in **profile mode** on a **real device**. Note which thread is long.
2. `ListView.builder` (or `.separated`) — never an eager `children` list for long content.
3. `itemExtent` or `prototypeItem` if rows are uniform.
4. Hoist work out of `itemBuilder`; add `const` everywhere it compiles.
5. `cacheWidth`/`cacheHeight` on every image in a cell.
6. `RepaintBoundary` on rows that animate — only those.
7. `ValueKey` on items in a mutable list.
8. Re-profile. If the raster thread is still long, look for `Opacity`, `ClipRRect` and shadows.

## FAQ

**Does `ListView.separated` cost more?**

It builds separators as additional children, so a list of *n* items builds roughly 2n−1 children. That is fine — separators are cheap `const` widgets if you make them so.

**What is `cacheExtent` for?**

It controls how far beyond the viewport the list keeps children built. Raising it makes fast scrolling smoother at the cost of memory and build work; it is a tuning knob, not a fix.

**Is `ListView` slower than a native list?**

The comparison rarely holds up once both are doing the same work. A correctly built `ListView.builder` recycles like a `RecyclerView`; an eagerly built `ListView` is comparable to adding eight hundred views to a `LinearLayout`, which is also slow on Android.

**Should I paginate?**

Yes, for anything unbounded. Lazy building solves rendering cost, not the cost of holding eight hundred parsed models in memory or fetching them over the network.

**Why is the first scroll janky and later scrolls fine?**

Usually shader compilation or image decoding on first appearance, not list logic. Check the raster thread on that specific frame before changing list code.

---

*The widget behaviours, delegate semantics and keep-alive mechanism described here are documented in the Flutter API references and performance guides linked above. The four-fix framing, the checklist order and the recommendation to lift item state out of the row are my own judgement from profiling lists this way. Always confirm with your own profile-mode trace — the right fix depends on which thread is late.*
