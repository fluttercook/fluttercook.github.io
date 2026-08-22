---
title: "When widget composition runs out: writing your own RenderObject"
description: "The escalation ladder from Row/Column to CustomPaint to CustomMultiChildLayout to a real RenderBox — then a complete, tested staggered-flow layout with performLayout, computeDryLayout, paint, hit testing and ParentData."
seoDescription: "Write a custom RenderBox in Flutter: performLayout, computeDryLayout, paint, hitTestChildren, ParentData and markNeedsLayout vs markNeedsPaint, with full code."
keywords:
  - flutter custom renderobject
  - flutter renderbox performlayout
  - multichildrenderobjectwidget example
  - flutter computedrylayout
  - containerrenderobjectmixin parentdata
  - flutter custom layout widget
category: "Deep Dive"
topic: "Rendering"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧩"
tags: ["Flutter", "RenderObject", "Layout", "Rendering"]
sources:
  - name: "RenderBox class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/rendering/RenderBox-class.html"
  - name: "MultiChildRenderObjectWidget class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/MultiChildRenderObjectWidget-class.html"
  - name: "ContainerRenderObjectMixin — Flutter API docs"
    url: "https://api.flutter.dev/flutter/rendering/ContainerRenderObjectMixin-mixin.html"
  - name: "ParentDataWidget class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/ParentDataWidget-class.html"
  - name: "Understanding constraints — Flutter docs"
    url: "https://docs.flutter.dev/ui/layout/constraints"
  - name: "Inside Flutter — Flutter docs"
    url: "https://docs.flutter.dev/resources/inside-flutter"
related:
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
draft: false
---

You know the moment. The design is a two-column masonry feed: cards of different heights, each new card dropping into whichever column is currently shortest, with the occasional full-width banner cutting across both. You try `Wrap` — every row gets the height of its tallest child, so you get gaps. You try two `Column`s inside a `Row` and split the list yourself — but you cannot split it correctly without knowing how tall each card renders, and you only know that after layout. You try `Stack` with `Positioned`, and now you need every card's height as a number, in the build method, before anything has been measured.

The trap is that these are all *composition* answers to a *measurement* problem. Row, Column, Stack and Wrap are themselves render objects with fixed layout algorithms. Nesting them does not produce a new algorithm; it produces a taller tree running the same three algorithms. When the shape you need is genuinely a different algorithm — a placement decision that depends on the measured size of previously laid-out siblings — no amount of nesting gets there.

This is the point where you write a `RenderBox`. It is less exotic than its reputation: about 120 lines for the layout below, using APIs that have been stable for years. The parts people get wrong are the parts nobody tells them about — dry layout, intrinsics, and which "mark dirty" call to make in a setter.

Everything here was written against Flutter 3.44 stable, analyzed clean, and verified with widget tests that assert the exact child offsets, the dry-layout size and the hit-test result.

## The ladder: most problems stop before the last rung

Climb this in order. Each rung costs more to write and more to maintain than the one below it, and stopping early is not a compromise — it is the correct answer for most layouts.

| Rung | Use it when | Where it stops |
| --- | --- | --- |
| Compose (`Row`, `Column`, `Stack`, `Wrap`, `LayoutBuilder`) | The shape is expressible as nesting | Placement can't depend on a sibling's measured size |
| `CustomPaint` | You need *pixels* — arcs, gradients, ticks — not children | It paints; it does not lay out children |
| `Flow` | You want to reposition already-sized children cheaply, often per-frame | `FlowDelegate.getSize` sees only constraints, never children |
| `CustomMultiChildLayout` | You position children yourself against a known parent size | Same limit — its own size cannot reflect its children |
| Custom `RenderBox` | The parent's size depends on its children, or you need intrinsics, baselines, or custom hit testing | Nowhere — you own the whole algorithm |

That fourth row is the one that pushes people over the edge. `CustomMultiChildLayout` looks like it should work for a masonry, and it can place the cards perfectly — but its own height comes from `MultiChildLayoutDelegate.getSize(constraints)`, which is called *before* any child is laid out and cannot see them. A masonry that cannot size itself to its content is useless inside a scroll view.

## Three trees, but you only need two facts about them

Flutter keeps three parallel trees. The **Widget** tree is immutable configuration, rebuilt constantly and cheap to throw away. The **Element** tree is the long-lived middle layer that decides whether a new widget updates an existing element or replaces it. The **RenderObject** tree is where layout, painting and hit testing actually happen, and it is mutable and expensive to create.

Two consequences matter for the code below. First, a `RenderObjectWidget` does not *contain* a render object; it *creates and configures* one. `createRenderObject` runs once when the element is first mounted. Every rebuild after that calls `updateRenderObject` with the same render object instance — so the render object needs settable fields, not final ones.

Second, because the render object survives rebuilds, changing one of those fields must explicitly tell the pipeline what is now stale. Nothing does this for you. That is the entire reason every setter in a render object follows the same shape: bail if unchanged, assign, then mark dirty.

| Call | Meaning | Typical trigger |
| --- | --- | --- |
| `markNeedsLayout()` | Sizes or positions changed; the paint that follows is implied | Spacing, column count, anything feeding `performLayout` |
| `markNeedsPaint()` | Same geometry, different pixels | Colors, stroke widths, decoration-only settings |
| `markNeedsSemanticsUpdate()` | The accessibility description changed | Labels, flags |

Calling `markNeedsLayout` where `markNeedsPaint` would do costs you a needless layout pass over the subtree; calling `markNeedsPaint` where layout was needed leaves stale geometry on screen. The second bug is far harder to spot, so when in doubt, mark layout.

## Constraints go down, sizes go up, the parent sets position

This one sentence governs everything. Concretely, in `performLayout`:

- Your parent handed you `constraints` (a `BoxConstraints`: min/max width and height). You must produce a `size` that satisfies them. `constraints.constrain(someSize)` clamps for you.
- You build a `BoxConstraints` for each child and call `child.layout(childConstraints, parentUsesSize: true)`. The `parentUsesSize` flag is not decoration — it tells the framework your layout depends on the child's size, so the child's relayout must propagate up to you. Get it wrong and you get stale layouts that only appear under specific rebuild orders.
- After laying a child out you may read `child.size` — but **only** if you passed `parentUsesSize: true`.
- A child never knows or sets its own position. The parent writes it into the child's `parentData.offset`.

The `ChildLayoutHelper.layoutChild` helper used below is exactly `child.layout(constraints, parentUsesSize: true)` followed by returning `child.size`, and its sibling `ChildLayoutHelper.dryLayoutChild` is `child.getDryLayout(constraints)`. Using the pair lets one function serve both real and dry layout, which is the trick that keeps them from drifting apart.

## A leaf render object: the smallest useful example

Start with no children at all. `LeafRenderObjectWidget` is the base for widgets whose render object has no children — the same base `Text`'s internals and `CustomPaint`-less painters use. Here is a ruler that fills its available width and draws ticks:

```dart
import 'dart:math' as math;

import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';

class Ruler extends LeafRenderObjectWidget {
  const Ruler({super.key, this.thickness = 24.0, this.color = const Color(0xFF546E7A)});

  final double thickness;
  final Color color;

  @override
  RenderRuler createRenderObject(BuildContext context) =>
      RenderRuler(thickness: thickness, color: color);

  @override
  void updateRenderObject(BuildContext context, RenderRuler renderObject) {
    renderObject
      ..thickness = thickness
      ..color = color;
  }
}

class RenderRuler extends RenderBox {
  RenderRuler({required double thickness, required Color color})
      : _thickness = thickness,
        _color = color;

  static const double _tickSpacing = 8.0;

  double _thickness;
  double get thickness => _thickness;
  set thickness(double value) {
    if (_thickness == value) return;
    _thickness = value;
    markNeedsLayout(); // changes the size we ask for
  }

  Color _color;
  Color get color => _color;
  set color(Color value) {
    if (_color == value) return;
    _color = value;
    markNeedsPaint(); // same size, different pixels
  }

  @override
  bool get sizedByParent => true;

  @override
  Size computeDryLayout(BoxConstraints constraints) =>
      constraints.constrain(Size(double.infinity, thickness));

  @override
  void paint(PaintingContext context, Offset offset) {
    final Paint paint = Paint()
      ..color = color
      ..strokeWidth = 1.0;
    final int tickCount = (size.width / _tickSpacing).floor();
    for (int i = 0; i <= tickCount; i++) {
      final double x = i * _tickSpacing;
      final double height = i % 5 == 0 ? size.height : size.height / 2;
      context.canvas.drawLine(offset + Offset(x, size.height - height),
          offset + Offset(x, size.height), paint);
    }
  }
}
```

Two details worth stealing. `sizedByParent => true` declares that the size is a pure function of the incoming constraints; the framework then calls `computeDryLayout` from `performResize`, and `RenderBox`'s default `performLayout` becomes a legal no-op, so you do not write one. And `offset` in `paint` is not your position on screen — it is where the parent decided you should draw. Add it to every coordinate. Forgetting it produces a widget that renders correctly at the top-left of the screen and nowhere else.

## The layout Row, Column and Stack cannot express

Now the real thing: children packed into N columns, each one landing in whichever column is currently shortest, plus full-width banners. Multiple children means three extra pieces — a `ParentData` subclass to hold each child's offset, `ContainerRenderObjectMixin` to manage the linked list of children, and `RenderBoxContainerDefaultsMixin` for the default paint and hit-test walks.

```dart
class StaggeredFlowParentData extends ContainerBoxParentData<RenderBox> {
  bool fullWidth = false;
}

class StaggeredFlow extends MultiChildRenderObjectWidget {
  const StaggeredFlow({
    super.key,
    this.columnCount = 2,
    this.spacing = 8.0,
    super.children,
  }) : assert(columnCount > 0);

  final int columnCount;
  final double spacing;

  @override
  RenderStaggeredFlow createRenderObject(BuildContext context) {
    return RenderStaggeredFlow(columnCount: columnCount, spacing: spacing);
  }

  @override
  void updateRenderObject(
      BuildContext context, RenderStaggeredFlow renderObject) {
    renderObject
      ..columnCount = columnCount
      ..spacing = spacing;
  }
}
```

`ContainerBoxParentData<RenderBox>` already carries `offset` (from `BoxParentData`) and `nextSibling` / `previousSibling` (from `ContainerParentDataMixin`). You subclass it only to add your own per-child fields — here, one boolean.

The render object's declaration and setters:

```dart
class RenderStaggeredFlow extends RenderBox
    with
        ContainerRenderObjectMixin<RenderBox, StaggeredFlowParentData>,
        RenderBoxContainerDefaultsMixin<RenderBox, StaggeredFlowParentData> {
  RenderStaggeredFlow({required int columnCount, required double spacing})
      : assert(columnCount > 0),
        _columnCount = columnCount,
        _spacing = spacing;

  int _columnCount;
  int get columnCount => _columnCount;
  set columnCount(int value) {
    assert(value > 0);
    if (_columnCount == value) return;
    _columnCount = value;
    markNeedsLayout();
  }

  double _spacing;
  double get spacing => _spacing;
  set spacing(double value) {
    if (_spacing == value) return;
    _spacing = value;
    markNeedsLayout();
  }

  @override
  void setupParentData(RenderObject child) {
    if (child.parentData is! StaggeredFlowParentData) {
      child.parentData = StaggeredFlowParentData();
    }
  }
```

`setupParentData` is called by the framework for each child as it is adopted. The `is!` guard matters: without it, a child moving between two parents of the same type gets its parent data thrown away and rebuilt on every attach.

## One algorithm, two entry points

`performLayout` and `computeDryLayout` must agree, or `IntrinsicHeight`, `Table` and various slivers will measure one thing and render another. The only difference between them is that dry layout may not mutate anything — no `size =`, no writing offsets, and children are measured with `getDryLayout` instead of being laid out. So write the algorithm once with a `dry` flag:

```dart
  double _columnWidth(double maxWidth) {
    final double available = maxWidth - spacing * (columnCount - 1);
    return math.max(0.0, available / columnCount);
  }

  Size _runLayout(BoxConstraints constraints, {required bool dry}) {
    assert(() {
      if (constraints.hasBoundedWidth) return true;
      throw FlutterError(
        'StaggeredFlow was given unbounded width.\n'
        'It divides the incoming maxWidth into columns, so it cannot be '
        'placed directly inside a horizontal ListView or an unconstrained Row. '
        'Wrap it in a SizedBox or an Expanded first.',
      );
    }());

    final ChildLayouter layoutChild =
        dry ? ChildLayoutHelper.dryLayoutChild : ChildLayoutHelper.layoutChild;
    final double width = constraints.maxWidth;
    final double columnWidth = _columnWidth(width);
    final List<double> columnBottoms = List<double>.filled(columnCount, 0.0);

    RenderBox? child = firstChild;
    while (child != null) {
      final StaggeredFlowParentData childParentData =
          child.parentData! as StaggeredFlowParentData;

      if (childParentData.fullWidth) {
        double top = 0.0;
        for (final double bottom in columnBottoms) {
          top = math.max(top, bottom);
        }
        final Size childSize =
            layoutChild(child, BoxConstraints.tightFor(width: width));
        if (!dry) {
          childParentData.offset = Offset(0.0, top);
        }
        final double next = top + childSize.height + spacing;
        for (int i = 0; i < columnCount; i++) {
          columnBottoms[i] = next;
        }
      } else {
        int target = 0;
        for (int i = 1; i < columnCount; i++) {
          if (columnBottoms[i] < columnBottoms[target]) target = i;
        }
        final Size childSize =
            layoutChild(child, BoxConstraints.tightFor(width: columnWidth));
        if (!dry) {
          childParentData.offset =
              Offset(target * (columnWidth + spacing), columnBottoms[target]);
        }
        columnBottoms[target] += childSize.height + spacing;
      }

      child = childParentData.nextSibling;
    }

    double contentHeight = 0.0;
    for (final double bottom in columnBottoms) {
      contentHeight = math.max(contentHeight, bottom);
    }
    if (contentHeight > 0.0) {
      contentHeight -= spacing; // drop the trailing gap
    }
    return constraints.constrain(Size(width, contentHeight));
  }

  @override
  void performLayout() {
    size = _runLayout(constraints, dry: false);
  }

  @override
  Size computeDryLayout(BoxConstraints constraints) {
    return _runLayout(constraints, dry: true);
  }
```

Read the constraint flow carefully, because this is where custom layouts break. Each child gets `BoxConstraints.tightFor(width: columnWidth)` — a tight width, and height left at `0..infinity`. That is the whole point: the child is forced to a column's width and allowed to be exactly as tall as it wants, which is what makes the staggering possible. The parent's own height is then the tallest column, and the parent's width is the incoming `maxWidth`, clamped through `constraints.constrain` so we can never violate what our own parent asked for.

If your algorithm genuinely cannot be computed without laying out children — for example it depends on a child's baseline — do not fake a dry layout. Call `debugCannotComputeDryLayout` inside an assert and return `Size.zero`, so misuse fails loudly in debug instead of silently mis-measuring in release.

## Painting and hit testing are two views of the same offsets

Because every child's position lives in `parentData.offset`, both walks are one-liners from `RenderBoxContainerDefaultsMixin`:

```dart
  @override
  void paint(PaintingContext context, Offset offset) {
    defaultPaint(context, offset);
  }

  @override
  bool hitTestChildren(BoxHitTestResult result, {required Offset position}) {
    return defaultHitTestChildren(result, position: position);
  }
```

`defaultPaint` walks children in insertion order and calls `context.paintChild(child, childParentData.offset + offset)`. `defaultHitTestChildren` walks them in **reverse** — last painted, first hit — and translates the test position into each child's coordinate space via `BoxHitTestResult.addWithPaintOffset`. That reversal is why the topmost overlapping child wins a tap, and it is the single most common thing hand-rolled hit tests get wrong.

Write these by hand only when you have done something the defaults do not know about: applied a clip or a transform, pushed a layer, or painted children out of order. If you painted with a transform, hit test with the inverse of that transform, or taps land in the wrong place.

Two behaviours are worth knowing rather than discovering in production. `hitTestSelf` returns `false` by default, so gaps between your children are transparent to taps; return `true` if the whole box should absorb them. And children are not clipped to your bounds — if the incoming constraints cap your height below the content height, `constrain` shrinks your `size` but the children keep painting past the edge. Put the flow in a scroll view, or wrap it in a `ClipRect`.

## ParentData: per-child information the parent owns

The `fullWidth` flag has to live somewhere. It cannot be a field on the child widget — a child does not know it is inside a `StaggeredFlow` — and it cannot be a constructor argument on the parent, because it varies per child. That is exactly what `ParentData` is for: a slot on each child, owned and written by the parent, which is how `Positioned` and `Expanded` work too.

The bridge is a `ParentDataWidget`:

```dart
class StaggeredBanner extends ParentDataWidget<StaggeredFlowParentData> {
  const StaggeredBanner({super.key, required super.child});

  @override
  void applyParentData(RenderObject renderObject) {
    final StaggeredFlowParentData parentData =
        renderObject.parentData! as StaggeredFlowParentData;
    if (parentData.fullWidth) return;
    parentData.fullWidth = true;
    renderObject.parent?.markNeedsLayout();
  }

  @override
  Type get debugTypicalAncestorWidgetClass => StaggeredFlow;
}
```

Two obligations. `applyParentData` must compare before it writes and must dirty the *parent*, not the child — the value it changed is an input to the parent's layout algorithm, not the child's. And `debugTypicalAncestorWidgetClass` is what produces the readable "incorrect use of ParentDataWidget" error when someone drops a `StaggeredBanner` outside a `StaggeredFlow`, instead of a cast failure deep inside the render tree.

Usage is then unremarkable:

```dart
StaggeredFlow(
  columnCount: 2,
  spacing: 8,
  children: [
    NoteCard(height: 100),
    NoteCard(height: 40),
    StaggeredBanner(child: SectionHeader('Archive')),
    NoteCard(height: 30),
  ],
)
```

## The methods nobody mentions until they bite

**Intrinsics default to zero.** `RenderBox.computeMinIntrinsicWidth` and friends return `0.0` unless you override them, and nothing warns you. That is fine until someone wraps your widget in `IntrinsicHeight`, drops it in a `Table` row, or puts it inside an unbounded parent — then it silently measures as zero. Because our dry layout is exact and side-effect free, the height intrinsics can simply delegate to it, and intrinsic width is the widest child times the column count plus the gaps:

```dart
  @override
  double computeMinIntrinsicWidth(double height) {
    double widest = 0.0;
    for (RenderBox? child = firstChild; child != null; child = childAfter(child)) {
      widest = math.max(widest, child.getMinIntrinsicWidth(double.infinity));
    }
    return widest * columnCount + spacing * (columnCount - 1);
  }

  @override
  double computeMaxIntrinsicWidth(double height) =>
      computeMinIntrinsicWidth(height);

  @override
  double computeMinIntrinsicHeight(double width) => width.isFinite
      ? _runLayout(BoxConstraints.tightFor(width: width), dry: true).height
      : 0.0;

  @override
  double computeMaxIntrinsicHeight(double width) =>
      computeMinIntrinsicHeight(width);
```

Drop those four overrides and the flow measures as zero height inside `IntrinsicHeight` — a widget test asserting the rendered size catches it immediately. Intrinsic queries walk the subtree and are not cheap, so implement them because correctness demands it, not for performance.

**Baselines are separate from intrinsics.** If your widget should align text with a sibling under `CrossAxisAlignment.baseline`, override `computeDistanceToActualBaseline` (and, on modern Flutter, `computeDryBaseline` to match). A masonry has no meaningful baseline, so leaving the default is right here.

**Test the geometry, not the pixels.** Widget tests can assert layout directly: `tester.getTopLeft(find.byKey(...))` for child offsets, `tester.getSize(find.byType(StaggeredFlow))` for the parent, `renderObject.getDryLayout(constraints)` compared against `renderObject.size` for dry/real agreement, and a `tapAt` on an overlapping region for hit-test order. Four such tests catch nearly every mistake in this article, and they run in milliseconds.

## FAQ

**When is `CustomMultiChildLayout` genuinely enough?**
When the parent's size does not depend on its children — a dial with labels arranged around a fixed-size circle, a chat bubble with a tail positioned against a known box, a HUD overlay filling the viewport. Its delegate's `getSize` receives only constraints, and the docs are explicit that the returned size cannot reflect child sizes. The moment you need "as tall as the tallest column", you need a `RenderBox`.

**Do I have to implement `computeDryLayout`?**
Not always, but skipping it has a cost. Without it, `getDryLayout` hits the default implementation, which throws in debug via `debugCannotComputeDryLayout` and returns zero. Anything that measures speculatively — `IntrinsicHeight`, some slivers, `Table` — will then fail or mis-measure. If the algorithm can run without mutating, factor it out with a flag as shown; if it truly cannot, fail loudly rather than returning a guess.

**Should I use a package instead?**
Often, yes. `flutter_staggered_grid_view` on pub.dev covers the masonry case with sliver support, and reaching for it is the right call when the layout is standard. Write your own when the algorithm is specific to your product, when you need it inside your own render pipeline, or when a dependency's constraints do not match yours. Understanding the render layer is also what lets you read a package's source and judge whether it does the right thing.

**Why is my custom layout laying out children twice?**
Usually `parentUsesSize`. If you read `child.size` after `child.layout(constraints)` without `parentUsesSize: true`, the framework does not register the dependency, so a child relayout may not propagate up — and the mismatch surfaces as stale or repeated layout. Use `ChildLayoutHelper.layoutChild`, which passes the flag for you, and check whether an ancestor is re-measuring you with different constraints each pass.

**Is a custom `RenderBox` faster than nesting widgets?**
Sometimes, but that is the wrong reason to write one. Collapsing five nested layout widgets into one render object does remove nodes from the layout and paint walks, and `RelayoutBoundary` behaviour can improve. But the real justification is expressiveness — a layout you could not otherwise write. If you only want speed, measure first with the DevTools timeline; the cost is usually elsewhere.

---

*The code here was written and verified against Flutter 3.44 stable — analyzed clean, with widget tests asserting the exact child offsets, dry-layout size and hit-test result. The escalation ladder and the "stop at rung two" advice are opinion informed by experience, not rules from the Flutter team. Render-layer APIs do shift between major versions (`RenderObject.parent` changed type, dry baselines were added), so check anything version-dependent against api.flutter.dev for the version you actually ship.*
