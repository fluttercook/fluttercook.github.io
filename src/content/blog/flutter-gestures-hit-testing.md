---
title: "Why your tap doesn't register: hit testing and the gesture arena"
description: "A GestureDetector that ignores taps is not broken. It either was never hit-tested, or it lost an arena it did not know it entered. Both are visible once you know where to look."
seoDescription: "How Flutter gesture handling really works: hit testing rules, HitTestBehavior, the gesture arena and disambiguation, nested detectors, RawGestureDetector with custom recognizers, and taps outside parent bounds."
keywords:
  - flutter gesture detector not working
  - flutter hittestbehavior explained
  - flutter gesture arena disambiguation
  - flutter nested gesturedetector
  - flutter tap outside parent bounds
  - flutter rawgesturedetector recognizer
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-27"
emoji: "👆"
tags: ["Flutter", "Gestures", "Hit Testing", "UI", "Debugging"]
sources:
  - name: "Flutter — Handling gestures"
    url: "https://docs.flutter.dev/ui/interactivity/gestures"
  - name: "GestureDetector — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/GestureDetector-class.html"
  - name: "HitTestBehavior — Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/HitTestBehavior.html"
  - name: "GestureArenaManager — Flutter API"
    url: "https://api.flutter.dev/flutter/gestures/GestureArenaManager-class.html"
  - name: "RawGestureDetector — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/RawGestureDetector-class.html"
  - name: "Listener — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Listener-class.html"
related:
  - slug: "flutter-custom-scroll-physics"
    title: "Custom scroll physics: making a list stop where you want it to"
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
draft: false
---

There is a specific kind of Flutter bug that eats an afternoon. The widget is on screen. The `onTap` is wired. You add a print statement and it never fires. Nothing in the console, no error, no warning — the tap simply does not exist.

Every instance of this is one of two causes. Either the pointer never reached your detector during hit testing, or it reached it and the detector lost the **gesture arena** to something else. They are different problems with different fixes, and they are distinguishable.

## How a pointer finds a widget

When a finger goes down, the framework walks the render tree from the root, asking each render object whether the point is inside it. The result is a **hit test path**: an ordered list from the deepest hit object up to the root. Pointer events are then dispatched along that path.

Three rules explain most surprises:

1. **Hit testing is geometric, and it uses the render object's box.** Not its visual appearance. A `Container` with no colour and no child has zero size, so nothing can hit it.
2. **The deepest hit wins first**, and events travel up from there.
3. **A child outside its parent's bounds is not hit**, even if it is painted. This is the one that catches everybody.

That third rule deserves an example, because it produces a widget you can see and cannot tap:

```dart
SizedBox(
  height: 40,
  child: Stack(
    clipBehavior: Clip.none,   // the badge is painted outside the 40px box
    children: [
      const Icon(Icons.notifications),
      Positioned(
        top: -12,
        child: GestureDetector(
          onTap: _dismiss,       // never fires: outside the parent's box
          child: const _Badge(),
        ),
      ),
    ],
  ),
)
```

`Clip.none` lets the badge *paint* outside the parent, but hit testing still stops at the parent's box. The fix is to make the parent big enough to contain what you want tappable — painting and hit testing are separate systems, and only one of them respects `Clip.none`.

## `HitTestBehavior`: the three-way switch

`GestureDetector` takes a `behavior`, and its default depends on whether it has a child. This is the single most common fix for "my tap does nothing".

| Value | Meaning |
| --- | --- |
| `deferToChild` | Hit only where a child is hit. **Default when there is a child.** |
| `opaque` | Hit anywhere in the detector's box; stops the test from continuing to widgets behind. **Default when there is no child.** |
| `translucent` | Hit anywhere in the box, and *also* let widgets behind be hit. |

The classic failure:

```dart
// Taps in the empty space around the text do nothing.
GestureDetector(
  onTap: _select,
  child: Container(
    height: 80,
    alignment: Alignment.centerLeft,
    child: const Text('Tap anywhere on this row'),
  ),
)
```

The `Container` has no colour, so it does not participate in hit testing itself; `deferToChild` means only the `Text`'s actual glyph box is tappable. Two fixes, and the first is better:

```dart
GestureDetector(
  behavior: HitTestBehavior.opaque,   // the whole 80px row is tappable
  onTap: _select,
  child: /* ... */,
)
```

or give the `Container` a colour — even `Colors.transparent` participates, which is why `color: Colors.transparent` "magically fixes" tap targets and why that trick confuses people who have not read this.

`translucent` is for the case where two stacked things both want the event: a background that dismisses a panel while the panel itself still receives taps.

## The gesture arena

Now the second cause. Suppose the pointer *did* reach your detector. Multiple recognizers along the hit test path may all be interested in the same pointer — a tap, a horizontal drag, a vertical drag, a long press. They cannot all win.

Flutter resolves this with an **arena**. Every interested recognizer enters, and then:

- A recognizer **declares victory** when it is certain (a drag that has moved past `kTouchSlop`).
- A recognizer **gives up** when it is certain it is not the gesture (a tap whose pointer moved too far).
- If everyone is still undecided when the pointer lifts, the **first entrant in the arena wins** by default.

The practical consequences:

**Tap loses to drag once movement starts.** This is why a tappable row inside a scrollable list still scrolls: the vertical drag recognizer of the scroll view wins as soon as the finger moves, and the tap gives up. That is correct behaviour, and it is why you should not fight it.

**A `GestureDetector` inside another usually means the inner one wins** for the same gesture type, because it is deeper. If you want both to react, they must be different gestures — or you need `RawGestureDetector`.

**Two competing drags in the same axis is a design problem**, not a code problem. A horizontally-swipeable card inside a horizontally-scrolling list will always be ambiguous to the user as well as to the framework.

## Debugging: turn the events on

Flutter has a global flag that prints every pointer event and every arena decision:

```dart
import 'package:flutter/gestures.dart';

void main() {
  debugPrintGestureArenaDiagnostics = true;
  debugPrintHitTestResults = true;   // also available
  runApp(const MyApp());
}
```

`debugPrintGestureArenaDiagnostics` shows each recognizer entering, and which one is "accepted". If your recognizer never appears, the problem is hit testing — go back to `HitTestBehavior` and bounds. If it appears and is rejected, the problem is arena competition — go and look at what beat it.

This single flag converts the afternoon-long version of this bug into a two-minute one.

## `Listener`: below the gesture system

`GestureDetector` sits on top of a lower layer. `Listener` gives you raw pointer events with no arena, no disambiguation, and no semantics:

```dart
Listener(
  onPointerDown: (e) => _trace('down at ${e.position}'),
  onPointerMove: (e) => _trace('move ${e.delta}'),
  onPointerUp: (e) => _trace('up'),
  behavior: HitTestBehavior.translucent,
  child: child,
)
```

Use it to *observe* — a heat map, a debug overlay, a "reset the idle timer on any touch" wrapper. Do not use it to implement tapping: you would be re-implementing slop tolerance, arena participation, accessibility semantics and platform feedback, all of which `GestureDetector` already has.

## `RawGestureDetector` and custom recognizers

Between the two sits `RawGestureDetector`, which lets you supply recognizers directly — including subclasses that change arena behaviour.

The canonical use is "let this child win a vertical drag even though a scroll view is above it":

```dart
RawGestureDetector(
  gestures: {
    _EagerVerticalDrag: GestureRecognizerFactoryWithHandlers<_EagerVerticalDrag>(
      () => _EagerVerticalDrag(),
      (instance) => instance
        ..onUpdate = _onDragUpdate
        ..onEnd = _onDragEnd,
    ),
  },
  child: child,
);

class _EagerVerticalDrag extends VerticalDragGestureRecognizer {
  @override
  void rejectGesture(int pointer) {
    // Claim the pointer instead of yielding to the ancestor scrollable.
    acceptGesture(pointer);
  }
}
```

This is a sharp tool. Overriding `rejectGesture` means your recognizer refuses to lose, which is exactly right for a draggable sheet inside a scroll view and exactly wrong almost everywhere else. Reach for it only after `debugPrintGestureArenaDiagnostics` has shown you which recognizer you are actually competing with.

## `IgnorePointer` and `AbsorbPointer`

Two widgets that intentionally break hit testing, and are constantly confused:

- **`IgnorePointer`** — the subtree is invisible to hit testing. Events pass through to whatever is behind.
- **`AbsorbPointer`** — the subtree is hit, but events stop there. Nothing behind gets them, and nothing inside reacts.

Use `IgnorePointer` for a decorative overlay you want to be able to tap through. Use `AbsorbPointer` for a "form is submitting, block everything" scrim. Choosing the wrong one produces either a dead UI or a UI where a disabled screen is still interactive underneath.

## A diagnostic order

1. Does the widget have non-zero size? Check with the widget inspector, not by looking.
2. Is it inside its parent's bounds? `Clip.none` and negative `Positioned` offsets are the usual suspects.
3. Is there an `IgnorePointer`, `AbsorbPointer`, or a transparent-but-opaque ancestor in the way?
4. Set `behavior: HitTestBehavior.opaque`. If it now works, that was it.
5. Turn on `debugPrintGestureArenaDiagnostics`. If your recognizer never enters, it is still hit testing. If it enters and loses, find the winner.

## FAQ

**Why does my tap work in the middle of a row but not at the edges?**

`deferToChild` with a child smaller than the row. Set `behavior: HitTestBehavior.opaque` on the detector.

**Why does a button inside a `ListView` scroll instead of pressing?**

The arena is working as designed: any movement past the touch slop makes the drag win. A tap without movement still fires. This is the platform-correct behaviour on both Android and iOS.

**Should I use `InkWell` or `GestureDetector`?**

`InkWell` for anything that should look like a Material control — it adds the ripple, focus and hover states, and correct semantics. `GestureDetector` for gestures without visual feedback. `InkWell` needs a `Material` ancestor to paint its ink.

**Can two widgets both handle the same tap?**

Not for the same gesture in the arena; the winner takes it. Stack a `Listener` for observation, or use `translucent` behaviour so both are on the hit test path for *different* gesture types.

**Why does `onTapDown` fire but not `onTap`?**

`onTapDown` fires optimistically; `onTap` only fires if the recognizer wins the arena. Seeing one without the other is the clearest possible sign that something else won.

---

*The hit testing rules, `HitTestBehavior` semantics, arena resolution and debug flags described here are documented in the Flutter gesture guide and API references linked above. The diagnostic ordering, the framing of the two root causes, and the caution around overriding `rejectGesture` are my own judgement from debugging gesture problems this way. Recognizer behaviour can change between releases — verify against the SDK you use.*
