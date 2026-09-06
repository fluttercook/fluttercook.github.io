---
title: "Custom scroll physics: making a list stop where you want it to"
description: "ScrollPhysics is the smallest interface in Flutter that controls the most-felt behaviour. Four methods decide whether a list snaps, bounces, resists, or refuses to fling — and you rarely need to override more than one."
seoDescription: "How Flutter ScrollPhysics works: applyPhysicsToUserOffset, applyBoundaryConditions, createBallisticSimulation, and tolerance — plus a working snapping physics, page snapping, and platform defaults."
keywords:
  - flutter custom scrollphysics
  - flutter snapping scroll list
  - createballisticsimulation flutter
  - flutter bouncingscrollphysics clamping
  - flutter scroll simulation spring
  - flutter pagescrollphysics snap
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-26"
emoji: "🎢"
tags: ["Flutter", "Scrolling", "Physics", "Animation", "UI"]
sources:
  - name: "ScrollPhysics — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollPhysics-class.html"
  - name: "ScrollMetrics — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollMetrics-class.html"
  - name: "Simulation — Flutter API"
    url: "https://api.flutter.dev/flutter/physics/Simulation-class.html"
  - name: "ScrollSpringSimulation — Flutter API"
    url: "https://api.flutter.dev/flutter/physics/ScrollSpringSimulation-class.html"
  - name: "PageScrollPhysics — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/PageScrollPhysics-class.html"
  - name: "ScrollConfiguration — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollConfiguration-class.html"
related:
  - slug: "flutter-slivers-custom-scroll"
    title: "Slivers, properly: the protocol behind every Flutter scroll effect"
  - slug: "flutter-gestures-hit-testing"
    title: "Why your tap doesn't register: hit testing and the gesture arena"
draft: false
---

Scrolling is the interaction users feel most and describe least. "It feels sluggish", "it doesn't stop where I expect", "it bounces wrong on Android". Those complaints all point at one small class: `ScrollPhysics`.

Most Flutter developers only ever meet it through the three named subclasses — `BouncingScrollPhysics`, `ClampingScrollPhysics`, `NeverScrollableScrollPhysics`. Underneath, it is a compact interface with four decision points, and understanding those turns "the list stops in a weird place" from a mystery into a two-line fix.

## What the class actually decides

| Method | Decides |
| --- | --- |
| `applyPhysicsToUserOffset` | How a finger's movement maps to scroll offset — resistance when overscrolling |
| `applyBoundaryConditions` | How much of a requested offset to refuse at the edges |
| `createBallisticSimulation` | What happens after the finger lifts: fling, settle, snap, or nothing |
| `tolerance` | When a simulation is considered finished |

Plus two properties worth knowing: `shouldAcceptUserOffset` (can this be dragged at all) and `minFlingVelocity` / `maxFlingVelocity` (what counts as a fling).

The three built-ins differ almost entirely in the first three:

- **`ClampingScrollPhysics`** — Android-style. `applyBoundaryConditions` refuses everything past the edge, producing a hard stop plus the glow indicator.
- **`BouncingScrollPhysics`** — iOS-style. Boundary conditions allow going past the edge, `applyPhysicsToUserOffset` makes it progressively harder, and the ballistic simulation springs back.
- **`NeverScrollableScrollPhysics`** — `shouldAcceptUserOffset` returns false. Note that this stops *user* scrolling only; a `ScrollController.animateTo` still works, which is exactly what you want for a programmatically driven view.

Which one you get by default depends on the platform, via `ScrollConfiguration`. That is why the same code feels different on iOS and Android — and why forcing one everywhere is a decision, not a fix.

## Composition: the `applyTo` pattern

`ScrollPhysics` composes through a `parent`, and every override is expected to call through. This is why you write physics as a thin layer rather than a replacement:

```dart
class SnapScrollPhysics extends ScrollPhysics {
  const SnapScrollPhysics({required this.itemExtent, super.parent});

  final double itemExtent;

  @override
  SnapScrollPhysics applyTo(ScrollPhysics? ancestor) =>
      SnapScrollPhysics(itemExtent: itemExtent, parent: buildParent(ancestor));

  // ...
}
```

Forgetting `applyTo` is the most common mistake. Without it, your physics is silently replaced when the framework rebuilds the chain — for example when a `ScrollConfiguration` applies the platform default — and your customisation appears to work in some places and not others.

Usage is then ordinary:

```dart
ListView.builder(
  physics: const SnapScrollPhysics(itemExtent: 120)
      .applyTo(const BouncingScrollPhysics()),
  itemExtent: 120,
  itemCount: items.length,
  itemBuilder: /* ... */,
)
```

## A snapping physics, complete

The most-requested custom physics is "snap to item boundaries". Here it is in full, because the pieces only make sense together:

```dart
class SnapScrollPhysics extends ScrollPhysics {
  const SnapScrollPhysics({required this.itemExtent, super.parent});

  final double itemExtent;

  @override
  SnapScrollPhysics applyTo(ScrollPhysics? ancestor) =>
      SnapScrollPhysics(itemExtent: itemExtent, parent: buildParent(ancestor));

  double _snapTarget(ScrollMetrics position, double velocity) {
    // Where the fling would naturally land, then round to the nearest item.
    final current = position.pixels;
    final index = (current / itemExtent).round();
    final biased = velocity.abs() < tolerance.velocity
        ? index
        : (velocity > 0 ? index + 1 : index - 1);
    return (biased * itemExtent)
        .clamp(position.minScrollExtent, position.maxScrollExtent);
  }

  @override
  Simulation? createBallisticSimulation(
    ScrollMetrics position,
    double velocity,
  ) {
    // Let the parent handle overscroll — do not fight bounce-back.
    if (position.outOfRange) {
      return super.createBallisticSimulation(position, velocity);
    }

    final target = _snapTarget(position, velocity);
    if ((target - position.pixels).abs() < tolerance.distance) return null;

    return ScrollSpringSimulation(
      spring,
      position.pixels,
      target,
      velocity,
      tolerance: toleranceFor(position),
    );
  }

  @override
  bool get allowImplicitScrolling => false;
}
```

Three details carry the whole thing.

**Returning `null` means "stop here".** If the current position is already within tolerance of the target, do not animate. Returning a simulation that immediately completes causes a visible micro-stutter.

**Deferring to `super` when `outOfRange`.** The parent physics owns bounce-back. Overriding it means writing your own spring back from overscroll, which will not match the platform.

**`ScrollSpringSimulation` carries the incoming velocity.** Passing `velocity` through is what makes a fast fling feel fast and a gentle release feel gentle. Dropping it — animating to the target with a fixed duration — is why hand-rolled snapping so often feels dead.

For paged content, do not write this at all: `PageScrollPhysics` already snaps to viewport-sized pages, and `PageView` uses it by default.

## Resistance and boundaries

The other two methods matter less often, but when they do, nothing else will do.

```dart
class ResistantEdgePhysics extends ScrollPhysics {
  const ResistantEdgePhysics({super.parent});

  @override
  ResistantEdgePhysics applyTo(ScrollPhysics? ancestor) =>
      ResistantEdgePhysics(parent: buildParent(ancestor));

  @override
  double applyPhysicsToUserOffset(ScrollMetrics position, double offset) {
    if (position.outOfRange) {
      // Halve finger movement once past the edge.
      return offset * 0.5;
    }
    return super.applyPhysicsToUserOffset(position, offset);
  }

  @override
  double applyBoundaryConditions(ScrollMetrics position, double value) {
    const maxOverscroll = 120.0;
    if (value < position.minScrollExtent - maxOverscroll) {
      return value - (position.minScrollExtent - maxOverscroll);
    }
    if (value > position.maxScrollExtent + maxOverscroll) {
      return value - (position.maxScrollExtent + maxOverscroll);
    }
    return super.applyBoundaryConditions(position, value);
  }
}
```

`applyBoundaryConditions` returns the amount of the requested change to **refuse**, not the amount to allow. Returning `0.0` means "allow it all". Getting this backwards produces a list that cannot be scrolled at all, which is a memorably confusing five minutes.

## Applying physics widely

For an app-wide feel, override `ScrollConfiguration` rather than passing `physics:` everywhere:

```dart
class AppScrollBehavior extends MaterialScrollBehavior {
  @override
  ScrollPhysics getScrollPhysics(BuildContext context) =>
      const BouncingScrollPhysics(parent: AlwaysScrollableScrollPhysics());
}

MaterialApp(
  scrollBehavior: AppScrollBehavior(),
  home: const HomePage(),
);
```

`ScrollBehavior` is also where you control the overscroll indicator, the scrollbar, and which input devices can drag — the last being the fix for "my desktop app cannot be scrolled by dragging with the mouse", which is a `dragDevices` setting, not a physics one.

`AlwaysScrollableScrollPhysics` as a parent is worth knowing on its own: it makes a list scrollable even when its content is shorter than the viewport, which is what makes pull-to-refresh work on a nearly empty list.

## Testing it

Physics is felt, not read, but the parts that matter can be asserted:

```dart
testWidgets('fling settles on an item boundary', (tester) async {
  await tester.pumpWidget(const SnapList());
  await tester.fling(find.byType(ListView), const Offset(0, -300), 800);
  await tester.pumpAndSettle();

  final position = tester
      .state<ScrollableState>(find.byType(Scrollable))
      .position;
  expect(position.pixels % 120, moreOrLessEquals(0, epsilon: 0.5));
});
```

`pumpAndSettle` runs the simulation to completion, so the assertion is on the resting position — which is exactly the property a snapping physics promises.

## FAQ

**Why does my custom physics work on one screen and not another?**

Almost always a missing or incorrect `applyTo`. The framework rebuilds the physics chain in several places, and without `applyTo` yours is dropped.

**Should I force iOS bouncing on Android?**

It is a product decision, but the default is platform-matched for a reason: users compare your list to every other list on their device. Forcing one feel makes the app consistent with itself and inconsistent with the platform.

**How do I disable scrolling temporarily?**

`NeverScrollableScrollPhysics` for user input while keeping controller-driven scrolling. If you also want to block programmatic scrolling, do not scroll programmatically — physics is not the enforcement point.

**Why does `pumpAndSettle` time out on my scroll test?**

Usually a simulation that never reaches tolerance — a spring with the wrong parameters, or a `createBallisticSimulation` that keeps returning a new simulation. Return `null` when you are close enough.

**Can I animate to a snapped position from a controller instead?**

Yes, and for a one-off "snap after this action" that is simpler. Custom physics is for when *every* release should snap, which is a property of the scroll view, not of one interaction.

---

*The `ScrollPhysics` interface, boundary-condition semantics, simulation classes and `ScrollBehavior` hooks described here are documented in the Flutter API references linked above. The snapping implementation, the emphasis on passing velocity through, and the diagnostic that a broken customisation is usually a missing `applyTo` are my own judgement from writing physics this way. Physics internals shift between Flutter releases — verify the class members against your SDK before copying.*
