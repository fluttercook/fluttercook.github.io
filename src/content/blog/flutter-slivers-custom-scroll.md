---
title: "Slivers, properly: the protocol behind every Flutter scroll effect"
description: "A sliver is not a widget with a strange name — it is a layout protocol with its own constraints and geometry. Understand SliverConstraints and SliverGeometry and collapsing headers, sticky sections and pinned toolbars stop being magic."
seoDescription: "How slivers actually work in Flutter: CustomScrollView, SliverConstraints, SliverGeometry, SliverPersistentHeader, and writing a RenderSliver by hand."
keywords:
  - flutter slivers explained
  - customscrollview flutter
  - sliverpersistentheader example
  - sliverconstraints slivergeometry
  - flutter collapsing toolbar
  - custom rendersliver flutter
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-06"
emoji: "🪟"
tags: ["Flutter", "Slivers", "Scrolling", "Layout", "Performance"]
sources:
  - name: "Flutter — Slivers"
    url: "https://docs.flutter.dev/ui/layout/scrolling/slivers"
  - name: "CustomScrollView — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/CustomScrollView-class.html"
  - name: "SliverConstraints — Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/SliverConstraints-class.html"
  - name: "SliverGeometry — Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/SliverGeometry-class.html"
  - name: "SliverPersistentHeader — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/SliverPersistentHeader-class.html"
  - name: "RenderSliver — Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/RenderSliver-class.html"
related:
  - slug: "flutter-lists-performance-builder"
    title: "Why your ListView is slow, and the four fixes that actually work"
  - slug: "flutter-custom-renderobject"
    title: "When widget composition runs out: writing your own RenderObject"
draft: false
---

Most Flutter developers meet slivers the way you meet a pothole: something in a design calls for a header that shrinks as you scroll, the search turns up `SliverAppBar`, it is pasted in, it works, and the mental model stops there. Then the next design needs a header that sticks *per section*, or a grid that becomes a list halfway down, and the pasted answer has nothing to say.

The thing worth understanding is that a sliver is not a special widget. It is a **different layout protocol**, running inside the same framework. Ordinary widgets ask "how big may I be?" and answer "this big." Slivers ask a much richer question — "how much of the viewport is left, how far have I been scrolled past, how much of me is visible?" — and give a much richer answer. Once you can read those two objects, every scroll effect in the framework becomes a small variation on a theme.

## Box layout versus sliver layout

Regular Flutter layout is the box protocol: a parent passes down `BoxConstraints` (min/max width and height), the child returns a `Size`. Two numbers in each direction, in, and one size out. Simple, and completely unable to describe a widget that is partially scrolled off the top of the screen.

Slivers replace both halves:

| | Box protocol | Sliver protocol |
| --- | --- | --- |
| Constraints | `BoxConstraints` | `SliverConstraints` |
| Result | `Size` | `SliverGeometry` |
| Render object | `RenderBox` | `RenderSliver` |
| Knows about scrolling | No | Yes |
| Can lay out lazily | Only via a viewport | Natively |

The bridge between the two worlds is `RenderSliverToBoxAdapter` — which is exactly what `SliverToBoxAdapter` wraps — and the lazy builders like `SliverList` and `SliverGrid`, which lay out box children on demand as the viewport moves.

## What a sliver is told: `SliverConstraints`

`SliverConstraints` has a dozen fields. Four of them carry the ideas:

```dart
class MyRenderSliver extends RenderSliver {
  @override
  void performLayout() {
    final SliverConstraints c = constraints;

    c.scrollOffset;      // how far this sliver's start is above the viewport top
    c.remainingPaintExtent; // how much visible room is left in the viewport
    c.overlap;           // how much earlier slivers are painting over my start
    c.precedingScrollExtent; // total scroll extent of everything before me
  }
}
```

`scrollOffset` is the field that unlocks the mental model. It is **not** the scroll position of the list. It is how much of *this particular sliver* has already scrolled out of view. For the first sliver in a list it equals the scroll controller's offset; for the fifth sliver it is zero until you have scrolled past the first four, and then it starts climbing. A sliver never has to know where it sits in the list — it is told how much of itself is gone.

`remainingPaintExtent` is the other half: the visible space still available below the previous sliver. When it reaches zero, later slivers are told to lay out nothing, which is exactly the laziness that makes an infinite list cheap.

Two more fields matter in practice. `axisDirection` and `growthDirection` combine into `c.normalizedGrowthDirection`; use the helper `constraints.axis` rather than assuming vertical, or your sliver breaks in a horizontal `CustomScrollView`. And `cacheOrigin`/`remainingCacheExtent` describe the invisible band above and below the viewport that Flutter lays out early so scrolling does not stutter — roughly 250 logical pixels by default.

## What a sliver reports: `SliverGeometry`

The return value is where people go wrong, because several fields sound like synonyms and are not:

```dart
geometry = SliverGeometry(
  scrollExtent: 300,    // how much scroll distance I consume, total
  paintExtent: 120,     // how much of the viewport I am painting into now
  maxPaintExtent: 300,  // the largest paintExtent I could ever want
  layoutExtent: 120,    // how much space I push later slivers down by
  hasVisualOverflow: false,
);
```

- **`scrollExtent`** is the sliver's contribution to the total scrollable length. A 300-pixel header contributes 300 whether it is on screen or not.
- **`paintExtent`** is how many pixels of the visible viewport it occupies *right now*. It must never exceed `remainingPaintExtent`.
- **`layoutExtent`** defaults to `paintExtent` and is how far the next sliver is pushed down. Making it *smaller* than `paintExtent` is the entire trick behind pinned and floating headers: the header keeps painting 56 pixels of toolbar while telling the list "I take zero space, carry on."

That asymmetry is worth sitting with. A pinned `SliverAppBar` at full scroll reports `paintExtent: 56, layoutExtent: 0`. It is drawn, but the content below behaves as though it were not there — and so it slides underneath.

The mistakes that produce a blank screen are nearly always in this object: returning a `paintExtent` larger than `remainingPaintExtent`, or forgetting to set `maxPaintExtent` (which breaks the scrollbar and the overscroll glow), or returning `SliverGeometry.zero` on a frame where the sliver is actually visible.

## The 90% case: `SliverPersistentHeader`

You very rarely need a hand-written `RenderSliver`. `SliverPersistentHeader` gives you the shrink-and-pin behaviour with a delegate that receives the one number you need:

```dart
class _SectionHeaderDelegate extends SliverPersistentHeaderDelegate {
  const _SectionHeaderDelegate({required this.title});

  final String title;

  @override
  double get minExtent => 48;

  @override
  double get maxExtent => 140;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    final t = (shrinkOffset / (maxExtent - minExtent)).clamp(0.0, 1.0);
    return Material(
      elevation: overlapsContent ? 4 : 0,
      color: Color.lerp(
        Theme.of(context).colorScheme.surfaceContainerLow,
        Theme.of(context).colorScheme.surface,
        t,
      ),
      child: Align(
        alignment: Alignment.lerp(
          Alignment.bottomLeft, Alignment.centerLeft, t)!,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            title,
            style: TextStyle.lerp(
              Theme.of(context).textTheme.headlineMedium,
              Theme.of(context).textTheme.titleMedium,
              t,
            ),
          ),
        ),
      ),
    );
  }

  @override
  bool shouldRebuild(_SectionHeaderDelegate old) => old.title != title;
}
```

`shrinkOffset` runs from `0` to `maxExtent - minExtent`. Normalise it to `0..1` and every animation you want is a `lerp`. `overlapsContent` tells you whether list content is currently sliding beneath you, which is the honest signal for when to raise the elevation — much better than comparing scroll offsets in a listener.

Then compose:

```dart
CustomScrollView(
  slivers: [
    SliverPersistentHeader(
      pinned: true,
      delegate: _SectionHeaderDelegate(title: 'Recipes'),
    ),
    const SliverPadding(
      padding: EdgeInsets.symmetric(horizontal: 16),
      sliver: SliverList.separated(
        // ...
      ),
    ),
  ],
)
```

Note `SliverPadding` rather than `Padding`. Inside a `CustomScrollView` every direct child must speak the sliver protocol; wrapping a sliver in a box widget throws at layout time with the famously unhelpful message about a `RenderSliver` expecting a `RenderSliver` parent. The sliver-flavoured wrappers you will reach for are `SliverPadding`, `SliverOpacity`, `SliverIgnorePointer`, `SliverAnimatedOpacity`, `SliverSafeArea`, `SliverVisibility`, and `SliverMainAxisGroup` / `SliverCrossAxisGroup` for grouping.

## Sticky section headers without a package

The recurring request — headers that pin, then get pushed off by the *next* header — needs nothing more than one `SliverPersistentHeader` per section, all in a flat list:

```dart
CustomScrollView(
  slivers: [
    for (final section in sections) ...[
      SliverPersistentHeader(
        pinned: true,
        delegate: _SectionHeaderDelegate(title: section.title),
      ),
      SliverList.builder(
        itemCount: section.items.length,
        itemBuilder: (context, i) => ItemTile(section.items[i]),
      ),
    ],
  ],
)
```

The push-off happens for free. Each pinned header clamps itself to the top while `remainingPaintExtent` allows, and when the next header arrives it takes the space, squeezing the previous one out. There is no coordination between them and no scroll listener anywhere.

## When you do write a `RenderSliver`

The case that justifies it is a sliver whose geometry is not a function of a single extent — a parallax band, a sliver that reveals itself only after a threshold, a header that resizes based on its own painted content. The skeleton:

```dart
class RenderFadeAwaySliver extends RenderSliverSingleBoxAdapter {
  RenderFadeAwaySliver({RenderBox? child}) : super(child: child);

  @override
  void performLayout() {
    if (child == null) {
      geometry = SliverGeometry.zero;
      return;
    }

    child!.layout(constraints.asBoxConstraints(), parentUsesSize: true);
    final double childExtent = switch (constraints.axis) {
      Axis.vertical => child!.size.height,
      Axis.horizontal => child!.size.width,
    };

    final double paintedChildSize =
        calculatePaintOffset(constraints, from: 0, to: childExtent);
    final double cacheExtent =
        calculateCacheOffset(constraints, from: 0, to: childExtent);

    geometry = SliverGeometry(
      scrollExtent: childExtent,
      paintExtent: paintedChildSize,
      cacheExtent: cacheExtent,
      maxPaintExtent: childExtent,
      hitTestExtent: paintedChildSize,
      hasVisualOverflow: childExtent > constraints.remainingPaintExtent ||
          constraints.scrollOffset > 0,
    );

    setChildParentData(child!, constraints, geometry!);
  }

  @override
  void paint(PaintingContext context, Offset offset) {
    if (child == null || geometry!.visible == false) return;
    final double t =
        (constraints.scrollOffset / geometry!.scrollExtent).clamp(0.0, 1.0);
    context.pushOpacity(
      offset, ((1 - t) * 255).round(), (ctx, o) => ctx.paintChild(child!, o));
  }
}
```

The two helpers earn their keep. `calculatePaintOffset` works out how much of a range `from..to` is currently visible given `scrollOffset` and `remainingPaintExtent`; `calculateCacheOffset` does the same for the cache band. Writing those by hand is where the off-by-one bugs live — use them.

`hitTestExtent` is easy to forget and produces a very confusing bug: a sliver that is visible but ignores taps in the region that scrolled past. Set it alongside `paintExtent`.

## Performance notes that actually change numbers

Slivers make laziness possible; they do not enforce it.

- **`SliverList` vs `SliverList.builder`.** The default constructor with `SliverChildListDelegate` builds every child eagerly, exactly like a `Column`. Only the builder form is lazy. Same for `SliverGrid`.
- **`addAutomaticKeepAlives`.** On by default, and it means a child that opts into `AutomaticKeepAliveClientMixin` — including anything with a `TextField` — is never disposed as it scrolls away. Deliberate for form state; expensive if it happens to hundreds of rows.
- **`cacheExtent`.** Raising it on the `CustomScrollView` trades memory and build time for smoother fast scrolling. It is one of the few knobs where measuring before and after in DevTools gives an unambiguous answer.
- **Nesting scroll views.** A `ListView` inside a `SliverToBoxAdapter` forces the inner list to be unbounded or shrink-wrapped, and shrink-wrapping lays out every child. Flatten to sibling slivers instead — that is what `SliverMainAxisGroup` is for.

## FAQ

**Why does my widget throw "A RenderSliver expected a RenderSliver child"?**

You put a box widget directly in a `slivers:` list, or a sliver directly inside a box widget. Wrap box content in `SliverToBoxAdapter`, and use the `Sliver`-prefixed versions of wrappers like `Padding` and `Opacity`.

**What is the difference between `pinned` and `floating` on a header?**

`pinned` keeps `minExtent` pixels on screen no matter how far you scroll down. `floating` brings the header back as soon as you scroll *up*, without having to return to the top. They combine, and with `snap: true` the return is animated rather than tied to the finger.

**Do I need a `CustomScrollView` to use slivers?**

`ListView` and `GridView` are already thin wrappers around a `CustomScrollView` with one sliver. You need the explicit form as soon as you want two different sliver types in one scroll view — which is the moment the wrappers stop paying for themselves.

**Why is my scrollbar the wrong size?**

Almost always a `maxPaintExtent` that does not reflect the sliver's real maximum, or a `scrollExtent` that changes every frame. The scrollbar is computed from the summed geometry, so an inconsistent sliver shows up there first.

**Can slivers be horizontal?**

Yes — set `scrollDirection: Axis.horizontal` on the `CustomScrollView`. Custom slivers must read `constraints.axis` rather than assuming vertical, and must not hard-code `size.height`.

---

*The protocol details here come from the Flutter framework documentation and the `rendering` library source linked above. The judgement calls — when a hand-written `RenderSliver` is worth it, and which performance knobs are worth measuring — are mine. Sliver APIs are stable but the widget-level wrappers gain members regularly; check the API docs for the SDK you ship.*
