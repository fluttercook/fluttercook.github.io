---
title: "Three kinds of Flutter animation, and how to pick the right one"
description: "Implicit, explicit and physics-based animation in Flutter, shown as the same card built three ways — plus the AnimatedBuilder child parameter, the dispose discipline, and why animating layout is not free."
seoDescription: "Implicit vs explicit vs physics-based Flutter animation: AnimatedContainer, AnimationController, SpringSimulation, and the mistakes reviewers keep finding."
keywords:
  - flutter implicit vs explicit animation
  - flutter animationcontroller dispose
  - flutter springsimulation animatewith
  - animatedbuilder child parameter
  - flutter tweenanimationbuilder
  - flutter animation curves
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🎬"
tags: ["Flutter", "Animation", "Performance", "UI"]
sources:
  - name: "Introduction to animations — Flutter docs"
    url: "https://docs.flutter.dev/ui/animations"
  - name: "Implicit animations — Flutter docs"
    url: "https://docs.flutter.dev/ui/animations/implicit-animations"
  - name: "AnimationController class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/animation/AnimationController-class.html"
  - name: "AnimatedBuilder class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/AnimatedBuilder-class.html"
  - name: "SpringSimulation class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/physics/SpringSimulation-class.html"
  - name: "Curves class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/animation/Curves-class.html"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
draft: false
---

Flutter gives you at least three separate ways to move a pixel, and the docs present them as a menu rather than a decision. So most codebases end up with all three, chosen by whoever wrote the widget that day, and the reviewer has no principle to push back with.

There is a principle. It is not "implicit is for simple things". It is: **who owns the value between two frames?** With implicit animations the framework owns it — you declare a target and the widget interpolates. With explicit animations you own it, through an `AnimationController` you create, drive and destroy. With physics-based animation neither of you owns it: a `Simulation` computes the value from mass, velocity and time, and you do not get to specify how long it takes.

To make the comparison concrete, this article builds the same interaction three times: a card that expands when you tap it, and can be flung sideways off the screen. It is a good test case because it has a *state change* (collapsed to expanded), which implicit animation handles well, and a *gesture with velocity* (the fling), which it cannot handle at all.

## Who owns the value between two frames

| | Value comes from | You specify | Interruption |
|---|---|---|---|
| **Implicit** | An internal controller inside the widget | Target value, duration, curve | Automatic — re-targets from the current value |
| **Explicit** | An `AnimationController` you hold | Duration, curve, when to start/stop/reverse | Yours to handle |
| **Physics** | A `Simulation` (spring, friction) | Starting position and velocity, plus material properties | Feed the new velocity into a new simulation |

The last column is where the choice usually gets made in practice. A tap that toggles a boolean is not interruptible in any interesting way, so implicit wins on line count. A drag that the user releases mid-flight *is*, and the animation has to continue from the finger's exact velocity — which is a thing a duration cannot express.

## The card, done implicitly

`AnimatedContainer` is a `Container` that watches its own properties and animates any that change between builds. There is no controller to see, and nothing to dispose.

```dart
class ImplicitCard extends StatefulWidget {
  const ImplicitCard({super.key});
  @override
  State<ImplicitCard> createState() => _ImplicitCardState();
}

class _ImplicitCardState extends State<ImplicitCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => setState(() => _expanded = !_expanded),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
        width: _expanded ? 320.0 : 200.0,
        height: _expanded ? 220.0 : 96.0,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: _expanded ? Colors.indigo.shade700 : Colors.indigo.shade400,
          borderRadius: BorderRadius.circular(_expanded ? 24.0 : 12.0),
        ),
        child: AnimatedOpacity(
          duration: const Duration(milliseconds: 320),
          opacity: _expanded ? 1.0 : 0.0,
          child: const Text('Details that only make sense when open'),
        ),
      ),
    );
  }
}
```

Two things about this that people get wrong. First, `AnimatedContainer` rejects `color` and `decoration` together — put the colour inside the `BoxDecoration`. Second, interruption is handled better than you would guess: when the target changes mid-flight, the internal tween's `begin` is reset to the *currently evaluated* value and the controller restarts from zero. The position never jumps. The duration does restart, so a rapidly re-tapped card takes the full 320 ms from wherever it happens to be.

When none of the `Animated*` widgets covers the property you need, `TweenAnimationBuilder` gives you the same declarative model over an arbitrary value:

```dart
TweenAnimationBuilder<double>(
  tween: Tween<double>(begin: 0.0, end: _expanded ? 1.0 : 0.0),
  duration: const Duration(milliseconds: 320),
  curve: Curves.easeOutCubic,
  builder: (context, t, child) =>
      Transform.rotate(angle: t * math.pi, child: child),
  child: const Icon(Icons.expand_more),
)
```

The trap here is `begin`. It is honoured only on the first build. On every rebuild after that, the widget animates from wherever it currently is to the new `end`, and changing `begin` does nothing. People write `begin: _expanded ? 1 : 0` and then spend an afternoon wondering why nothing changes.

## The same card with a controller you own

The explicit version costs about fifteen more lines and buys you a clock you can point at: reverse it halfway, run two widgets from it, read its status, hand it to a simulation later.

```dart
// The StatefulWidget shell is identical to the one above; the State is
// where everything interesting happens.
class _ExplicitCardState extends State<ExplicitCard>
    with SingleTickerProviderStateMixin {
  static final _width = Tween<double>(begin: 200, end: 320);
  static final _height = Tween<double>(begin: 96, end: 220);
  static final _radius = Tween<double>(begin: 12, end: 24);
  static final _color =
      ColorTween(begin: Colors.indigo.shade400, end: Colors.indigo.shade700);

  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 320),
    reverseDuration: const Duration(milliseconds: 220),
  );

  late final CurvedAnimation _open = CurvedAnimation(
    parent: _controller,
    curve: Curves.easeOutCubic,
    reverseCurve: Curves.easeInCubic,
  );

  @override
  void dispose() {
    _open.dispose();
    _controller.dispose();
    super.dispose();
  }

  void _toggle() {
    final status = _controller.status;
    if (status == AnimationStatus.completed ||
        status == AnimationStatus.forward) {
      _controller.reverse();
    } else {
      _controller.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _toggle,
      child: AnimatedBuilder(
        animation: _open,
        builder: (context, child) => Container(
          width: _width.evaluate(_open),
          height: _height.evaluate(_open),
          decoration: BoxDecoration(
            color: _color.evaluate(_open),
            borderRadius: BorderRadius.circular(_radius.evaluate(_open)),
          ),
          child: Opacity(opacity: _open.value, child: child),
        ),
        // Built once, not once per frame. See the next section.
        child: const Padding(
          padding: EdgeInsets.all(16),
          child: Text('Details that only make sense when open'),
        ),
      ),
    );
  }
}
```

`vsync: this` is what stops this animation from running while the widget is off-screen. `SingleTickerProviderStateMixin` supplies a `Ticker` that is muted when the enclosing `TickerMode` is disabled — which is what happens to a route pushed under another one. Use `SingleTickerProviderStateMixin` for exactly one controller; it asserts if you create a second. `TickerProviderStateMixin` handles several.

`dispose()` is not hygiene, it is correctness. An `AnimationController` holds a `Ticker` registered with the scheduler, and it is a `ChangeNotifier` that your widget subscribed to. Drop the `State` without disposing and the ticker keeps requesting frames for a widget that is gone; in debug builds the ticker provider asserts loudly when the `State` is disposed with a ticker still active, which is Flutter telling you about a real leak rather than being fussy. `CurvedAnimation` also has a `dispose()` — it attaches a status listener to its parent — so type the field as `CurvedAnimation`, not `Animation<double>`, or you will not be able to call it.

If the animated widget is small and self-contained, `AnimatedWidget` says the same thing with less indentation:

```dart
class _SlidingCard extends AnimatedWidget {
  const _SlidingCard({required Animation<double> offset, required this.child})
      : super(listenable: offset);

  final Widget child;
  Animation<double> get _offset => listenable as Animation<double>;

  @override
  Widget build(BuildContext context) =>
      Transform.translate(offset: Offset(_offset.value, 0), child: child);
}
```

The `child` field here is passed in already-constructed by the parent, so it survives every rebuild for the same reason `AnimatedBuilder`'s `child` does — the framework compares widget instances and skips subtrees that did not change identity.

## Flinging needs a simulation, not a duration

Now the part implicit animation cannot do. The user drags the card and lets go at 1,400 logical pixels per second. What duration do you pass? There isn't one — the correct answer is "however long a body moving at that speed takes to settle", which is a physics question.

```dart
class FlingableCard extends StatefulWidget {
  const FlingableCard({super.key, this.onDismissed});
  final VoidCallback? onDismissed;
  @override
  State<FlingableCard> createState() => _FlingableCardState();
}

class _FlingableCardState extends State<FlingableCard>
    with SingleTickerProviderStateMixin {
  // The controller's value is a horizontal offset in logical pixels,
  // not a 0..1 progress value. Hence `unbounded`.
  late final AnimationController _drag =
      AnimationController.unbounded(vsync: this);

  static final _returnSpring = SpringDescription.withDampingRatio(
    mass: 1,
    stiffness: 400,
    ratio: 0.75, // under 1.0 = a little overshoot on the way back
  );

  @override
  void dispose() {
    _drag.dispose();
    super.dispose();
  }

  void _onDragUpdate(DragUpdateDetails details) {
    // Assigning to `value` stops any running simulation first.
    _drag.value += details.delta.dx;
  }

  void _onDragEnd(DragEndDetails details) {
    final velocity = details.velocity.pixelsPerSecond.dx;
    final width = MediaQuery.sizeOf(context).width;

    // Both numbers are product decisions, not framework constants.
    const dismissVelocity = 800.0;
    final dismissed =
        velocity.abs() > dismissVelocity || _drag.value.abs() > width / 3;

    if (dismissed) {
      final target = _drag.value.isNegative ? -width : width;
      // Nobody watches a card that is already leaving: a curve is fine here.
      _drag
          .animateTo(target,
              duration: const Duration(milliseconds: 180),
              curve: Curves.easeOut)
          .whenComplete(() {
        if (mounted) widget.onDismissed?.call();
      });
    } else {
      // The card comes back. This is where physics earns its keep: the
      // spring starts at the finger's exact position *and* velocity.
      _drag.animateWith(
        SpringSimulation(_returnSpring, _drag.value, 0, velocity),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onHorizontalDragUpdate: _onDragUpdate,
      onHorizontalDragEnd: _onDragEnd,
      child: AnimatedBuilder(
        animation: _drag,
        builder: (context, child) =>
            Transform.translate(offset: Offset(_drag.value, 0), child: child),
        child: const _CardBody(),
      ),
    );
  }
}
```

Three details worth internalising.

**Units have to match.** `details.velocity.pixelsPerSecond` is in logical pixels per second. The simulation's velocity argument is in *the controller's* units per second. Because this controller counts pixels, you can pass the value straight through. If your controller runs 0 to 1 across a 300-pixel travel, you must divide by 300 first — and if a fling feels either instant or glacial, this is almost always why.

**`fling()` is the shortcut, not the general case.** `AnimationController.fling(velocity: v)` runs a stiff built-in spring toward `upperBound` when `v` is positive and `lowerBound` when it is negative. That is perfect for a bounded 0-to-1 toggle thrown by a gesture, and useless when the target is neither bound.

**`animateWith` returns a `TickerFuture` that completes even when cancelled.** Disposing the controller mid-animation cancels the ticker, and the plain future still completes — so a `.whenComplete` callback that calls `setState` or a parent callback needs the `mounted` guard above. Use `.orCancel` if you want cancellation to surface as an error instead.

For the specific case of swipe-to-dismiss in a list, the framework already ships `Dismissible`, which does all of this with `onDismissed` and configurable thresholds. Write the simulation yourself when the motion is genuinely custom, not to reimplement a list row.

## The `child` parameter is the whole point of AnimatedBuilder

`AnimatedBuilder`'s builder runs once per frame. At 120 Hz that is 120 rebuilds a second of everything inside it. This is the single most common performance mistake in Flutter animation code:

```dart
// Every frame rebuilds the Column, the Text widgets, the icons, all of it.
AnimatedBuilder(
  animation: _controller,
  builder: (context, child) => Transform.scale(
    scale: _controller.value,
    child: ExpensiveCardBody(item: item),
  ),
)

// ExpensiveCardBody is constructed once. The builder wraps the same
// instance every frame, and the element layer skips it entirely.
AnimatedBuilder(
  animation: _controller,
  builder: (context, child) =>
      Transform.scale(scale: _controller.value, child: child),
  child: ExpensiveCardBody(item: item),
)
```

The mechanism is worth knowing because it explains the limits: when Flutter reconciles the tree it compares the new widget against the old one, and an *identical instance* short-circuits the update. The `child` you hand to `AnimatedBuilder` is stored by its `State` and passed back unchanged, so the subtree is never rebuilt. It only works for parts of the subtree that do not depend on the animation value. If half the card depends on it, split the card.

`ListenableBuilder` is the same widget generalised to any `Listenable`, and the built-in transition widgets — `FadeTransition`, `ScaleTransition`, `SlideTransition`, `SizeTransition`, `DecoratedBoxTransition` — do the same trick internally without a builder at all. If a transition widget covers your case, use it; it is fewer moving parts and it will not tempt anyone into rebuilding the world.

## Animate paint before you animate layout

`AnimatedContainer(width: ...)` looks harmless and is the most expensive snippet in this article. Changing a width marks the render object dirty for **layout**, so every frame runs layout, then paint, then compositing. Worse, layout propagates: a card that grows inside a `Column` pushes its siblings, so the parent relayouts too, and inside a `ListView` that can mean recomputing item positions on every single frame of the animation.

`Transform.scale`, `Transform.translate`, `FadeTransition` and `DecoratedBoxTransition` change nothing about layout. They only affect paint, so the layout pass is skipped entirely and the work is a matrix or an opacity layer.

The rules I actually apply:

- Press feedback, hover lift, shake, slide-in, cross-fade → transform or fade. Never size.
- Disclosure that must *reflow real content* → `AnimatedSize` or `SizeTransition`, and accept the layout cost, because scaling text is not the same as revealing it.
- Wrap the animating subtree in a `RepaintBoundary` so its repaints do not dirty the rest of the screen. Note that this helps paint only — it does nothing for a layout-driven animation.
- If you are animating size across many list items at once, you have a design problem, not a Flutter problem.

One related trap: a widget faded to zero opacity is still in the tree. It still builds, still takes up layout space, and still participates in hit testing unless you also wrap it in `IgnorePointer`. "Invisible" and "gone" are different states, and an invisible card that swallows taps is a bug users will report as "the button doesn't work".

## Curves are a design decision, not a default

Every implicit widget defaults to `Curves.linear`, and `CurvedAnimation` makes you name a curve because there is no sensible default. Linear motion is the visual signature of an animation nobody thought about — real objects accelerate and decelerate, and the eye notices immediately when they don't.

| Situation | Reasonable starting point |
|---|---|
| Element entering, expanding, arriving | `Curves.easeOut` / `Curves.easeOutCubic` |
| Element leaving, collapsing | `Curves.easeIn` / `Curves.easeInCubic` |
| Moving between two on-screen positions | `Curves.fastOutSlowIn` |
| Material 3 emphasized motion | `Curves.easeInOutCubicEmphasized` |
| Playful confirmation, a badge popping in | `Curves.easeOutBack`, `Curves.elasticOut` |

Three things to keep in mind. Entrances and exits usually want *different* curves and different durations — that is what `reverseCurve` and `reverseDuration` are for, and closing faster than opening is the common asymmetry. Second, the overshoot curves emit values outside 0 to 1; `Opacity` asserts on that range in debug, so a `Curves.elasticOut` fade will crash where a `FadeTransition`, which clamps, would not. Third, do not apply a curve twice — a `CurvedAnimation` feeding a tween that was already `.chain`ed with a `CurveTween` produces motion nobody designed.

## When each one is the wrong tool

| | Reach for it when | Wrong when |
|---|---|---|
| **Implicit** | A widget property changes with state, the motion is short, nothing else needs to be in sync | You need to reverse from an arbitrary point, coordinate several widgets, react to completion beyond `onEnd`, or continue a gesture |
| **Explicit** | Several properties or widgets share one clock, you need `status`, staggering, `repeat()`, or precise control over start and stop | A single property toggles on a bool — you are writing a controller, a mixin and a `dispose` to replace four lines |
| **Physics** | The animation continues a gesture, or the motion should feel like it has mass — springs, flings, snapping, rubber-banding | The motion has a fixed spec ("300 ms ease-out"), because a simulation's duration falls out of the maths and cannot be dictated |

This shows up in tests too. `tester.pumpAndSettle()` pumps frames until none are scheduled, so it works fine for implicit and explicit animations and for spring simulations — springs terminate because `Simulation.isDone` compares against a tolerance. It will time out on anything driven by `repeat()`, and on a controller nobody stopped. When a widget test hangs for no obvious reason, an animation that never ends is the first place to look.

## FAQ

**Is implicit animation slower than explicit?**

No — under the hood an implicit widget is a `StatefulWidget` with its own private `AnimationController`, so the per-frame cost is the same machinery. The performance difference comes from *what* you animate (layout versus paint) and how much subtree you rebuild per frame, not from which API you picked.

**Can I combine a gesture with an implicit animation?**

Only crudely. You can update state on drag end and let `AnimatedContainer` glide to the new target, but the animation starts at zero velocity, so the motion visibly disconnects from the finger. Any interaction where the release velocity should carry through needs a controller and a simulation.

**Do I need `dispose()` if I use `TweenAnimationBuilder` or `AnimatedOpacity`?**

No. Those widgets own their controller internally and dispose it with their own `State`. You only take on the dispose obligation when you construct an `AnimationController`, a `CurvedAnimation`, or anything else that registers a listener or a ticker on your behalf.

**How do I pick spring constants that feel right?**

Start from `SpringDescription.withDampingRatio` rather than raw damping: a ratio of 1.0 is critically damped and stops without overshooting, below 1.0 bounces, above 1.0 crawls in slowly. Then adjust `stiffness` for speed and leave `mass` at 1 unless you have a reason. Tuning by feel on a real device beats reasoning about the numbers.

**Should I respect the system "reduce motion" setting?**

Yes. `MediaQuery.disableAnimationsOf(context)` tells you when the user has asked for it, and an `AnimationController` created with the default `AnimationBehavior.normal` already shortens its duration drastically when that flag is set. Physics-driven motion is not covered automatically, so check the flag and jump straight to the end state.

---

*The API behaviour described here — the tolerance-based end of a spring simulation, the identity check that makes the `child` parameter work, the `Opacity` range assert — is how the framework works, not opinion. The curve recommendations, the spring constants and the dismiss thresholds are taste, and yours may differ. Anything version-dependent should be checked against the current Flutter API docs before you rely on it.*
