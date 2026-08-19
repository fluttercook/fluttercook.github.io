---
title: "Creating a custom progress indicator in Flutter with CustomPaint"
description: "Build a circular progress ring from scratch with Container, Stack and CustomPaint — including the trigonometry behind startAngle and sweepAngle."
seoDescription: "Flutter CustomPaint tutorial: draw a circular progress indicator with canvas.drawArc, and work out startAngle and sweepAngle in radians or degrees. Full runnable code."
keywords:
  - flutter custom progress indicator
  - flutter custompaint tutorial
  - flutter drawarc
  - flutter custompainter
  - flutter circular progress indicator
  - flutter canvas arc
category: "Tutorial"
topic: "CustomPaint"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2021-08-23"
updatedDate: "2026-08-19"
emoji: "🎨"
tags: ["Flutter", "CustomPaint", "Canvas", "UI", "Animation"]
canonicalSource:
  name: "trunghieu-it.blogspot.com"
  url: "https://trunghieu-it.blogspot.com/2021/08/creating-custom-progress-indicator.html"
sources:
  - name: "Canvas class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/Canvas-class.html"
  - name: "Canvas.drawArc — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/Canvas/drawArc.html"
  - name: "StrokeCap — Flutter API docs"
    url: "https://api.flutter.dev/flutter/dart-ui/StrokeCap-class.html"
  - name: "Dan-Y-Ko/Flutter-Dart-Playground — banking_app_ui"
    url: "https://github.com/Dan-Y-Ko/Flutter-Dart-Playground/tree/master/flutter/ui/banking_app_ui"
draft: false
---

Flutter's built-in `CircularProgressIndicator` is fine until a designer hands you a ring that starts at four o'clock, stops at eight, and wraps a button. At that point you stop configuring a widget and start drawing one. This walkthrough builds that ring from scratch with `CustomPaint`, and — more usefully — explains the angle maths that trips most people up the first time.

This assumes you are comfortable with basic Flutter widgets. The focus here is the painting, not the scaffolding.

## The three widgets involved

Only three do the real work:

- **`Container`** — draws the static outer circle (the "track" the progress sits on).
- **`Stack`** — lets the painted arc overlap that circle instead of sitting next to it.
- **`CustomPaint`** — hands you a `Canvas` so you can draw the arc yourself.

## Start with the track

Before any painting, get a plain circle on screen. A `Container` with `BoxShape.circle` and a border is enough, and wrapping it in a `Stack` now saves a refactor in a minute.

```dart
import 'package:flutter/material.dart';

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
      ],
    );
  }
}
```

That gives you a thin white circle in the middle of a dark screen. Everything from here is painted on top of it.

## Writing the CustomPainter

A `CustomPaint` widget is only as interesting as the `CustomPainter` you give it. A painter needs three things:

1. extend `CustomPainter`
2. implement `paint`
3. implement `shouldRepaint`

`shouldRepaint` does exactly what it sounds like: return `true` when a new instance of the painter should trigger a repaint. For a static indicator nothing changes between builds, so `false` is correct — and cheaper. (Return `true`, or compare fields against `oldDelegate`, once you start animating the sweep.)

### Breaking down the paint method

`paint` receives the `Canvas` you draw on and the `Size` it was given. The canvas can draw rectangles, circles, lines and arbitrary paths; here we only want an arc.

```dart
void paint(Canvas canvas, Size size) {
    // 2
    final paint = Paint()
      // 3
      ..color = Colors.blue
      // 4
      ..strokeCap = StrokeCap.butt
      // 5
      ..style = PaintingStyle.stroke
      // 6
      ..strokeWidth = width;

    // 7
    final center = Offset(size.width / 2, size.height / 2);

    // 8
    final radius = (size.width / 2) - (width / 2);

    // 1
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      paint,
    );
  }
```

Line by line:

1. **`drawArc`** takes five arguments. The first is the `Rect` the arc is inscribed in — `Rect.fromCircle` keeps it perfectly round. The second is where the arc starts, the third how far it sweeps. The fourth (`useCenter`) decides whether the ends connect back to the centre; leave it `false` unless you want a pie slice. The fifth is the `Paint`.
2. **`Paint`** carries every visual property of the stroke and gets passed into `drawArc`.
3. **`color`** — the stroke colour.
4. **`strokeCap`** — how the two ends of the arc are finished. `StrokeCap.butt` cuts them flat; `StrokeCap.round` gives you the rounded caps most designs want.
5. **`style`** — `PaintingStyle.fill` floods the shape, `PaintingStyle.stroke` outlines it. A progress ring is an outline.
6. **`strokeWidth`** — the thickness of that outline. Pairs with `PaintingStyle.stroke`.
7. **`center`** — half the width and half the height, so the arc is centred in whatever box the painter was handed.
8. **`radius`** — half the width *minus half the stroke width*. Skip that subtraction and the stroke straddles the edge of the box and gets clipped.

Here is the whole file with the painter wired in, with the angle work still commented out so it compiles and runs:

```dart
import 'package:flutter/material.dart';
// import 'dart:math' as math;

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
//     required this.startAngle,
//     required this.endAngle,
  }) : super(key: key);

//   final double startAngle;
//   final double endAngle;

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
        SizedBox(
          width: buttonSize,
          height: buttonSize,
          child: CustomPaint(
            painter: ProgressIndicatorPainter(
              width: borderWidth,
//               startAngle: startAngle,
//               sweepAngle: endAngle,
            ),
            child: Center(
              child: Container(
                width: buttonSize - 20.0,
                height: buttonSize - 20.0,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.done,
                    size: 30.0,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProgressIndicatorPainter extends CustomPainter {
  const ProgressIndicatorPainter({
    required this.width,
//     required this.startAngle,
//     required this.sweepAngle,
  }) : super();

  final double width;
//   final double startAngle;
//   final double sweepAngle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeCap = StrokeCap.butt
      ..style = PaintingStyle.stroke
      ..strokeWidth = width;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - (width / 2);

//     canvas.drawArc(
//       Rect.fromCircle(center: center, radius: radius),
//       startAngle,
//       sweepAngle,
//       false,
//       paint,
//     );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

Keep those comments exactly where they are — uncommenting half of them will not compile.

## What startAngle and sweepAngle actually mean

This is the part worth slowing down for.

**`startAngle`** is measured in radians and starts at 0 — the three o'clock position on the unit circle. The catch is direction: `drawArc` sweeps **clockwise**, while the unit circle you remember from school runs counter-clockwise. Rather than re-deriving everything, the shortcut is to read the position off the unit circle as usual and then negate it. Want the arc to begin at π/2 (twelve o'clock)? Pass `-π/2`.

**`sweepAngle`** is not an end position — it is a length. Whatever you pass is *added* to `startAngle`, and that sum is where the arc stops. To draw from π/2 round to 0, you need `startAngle: -π/2` and `sweepAngle: π/2`, because −π/2 + π/2 = 0.

### Working out the sweep for an arbitrary arc

Take the ring from the top of this post: it starts around 2π/3 and ends around 11π/6 on the unit circle. There is no clean subtraction that always gives you the sweep for a custom start, so count the arc in slices instead:

- quadrant I is covered in full → π/2
- quadrants II and IV contribute one π/6 slice each → π/6 + π/6

π/6 + π/6 + π/2 = **5π/6**, and that is the sweep. The full code:

```dart
import 'package:flutter/material.dart';
import 'dart:math' as math;

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(
            startAngle: -2 * math.pi / 3,
            endAngle: 5 * math.pi / 6,
          ),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
    required this.startAngle,
    required this.endAngle,
  }) : super(key: key);

  final double startAngle;
  final double endAngle;

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
        SizedBox(
          width: buttonSize,
          height: buttonSize,
          child: CustomPaint(
            painter: ProgressIndicatorPainter(
              width: borderWidth,
              startAngle: startAngle,
              sweepAngle: endAngle,
            ),
            child: Center(
              child: Container(
                width: buttonSize - 20.0,
                height: buttonSize - 20.0,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.done,
                    size: 30.0,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProgressIndicatorPainter extends CustomPainter {
  const ProgressIndicatorPainter({
    required this.width,
    required this.startAngle,
    required this.sweepAngle,
  }) : super();

  final double width;
  final double startAngle;
  final double sweepAngle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeCap = StrokeCap.butt
      ..style = PaintingStyle.stroke
      ..strokeWidth = width;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - (width / 2);

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

## Prefer degrees? Convert at the edge

If radians make the calling code unreadable, take degrees into the painter and convert them right before `drawArc`. Nothing else changes — same concepts, friendlier numbers.

```dart
import 'package:flutter/material.dart';
import 'dart:math' as math;

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(
            startAngle: -120,
            endAngle: 150,
          ),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
    required this.startAngle,
    required this.endAngle,
  }) : super(key: key);

  final int startAngle;
  final int endAngle;

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
        SizedBox(
          width: buttonSize,
          height: buttonSize,
          child: CustomPaint(
            painter: ProgressIndicatorPainter(
              width: borderWidth,
              startAngle: startAngle,
              sweepAngle: endAngle,
            ),
            child: Center(
              child: Container(
                width: buttonSize - 20.0,
                height: buttonSize - 20.0,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.done,
                    size: 30.0,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProgressIndicatorPainter extends CustomPainter {
  const ProgressIndicatorPainter({
    required this.width,
    required this.startAngle,
    required this.sweepAngle,
  }) : super();

  final double width;
  final int startAngle;
  final int sweepAngle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeCap = StrokeCap.butt
      ..style = PaintingStyle.stroke
      ..strokeWidth = width;

    final startAngleRad = startAngle * (math.pi / 180.0);
    final sweepAngleRad = sweepAngle * (math.pi / 180.0);

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - (width / 2);

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngleRad,
      sweepAngleRad,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

## Two more to practise on

Same procedure, different numbers:

- **Starting at three o'clock.** `startAngle` is `0` (or `0.0` in code). The sweep covers all of quadrant IV plus a π/6 slice of quadrant III: π/6 + π/2 = **4π/6**.
- **Starting at −5π/4.** In quadrant II you take the full quadrant, then in quadrant III a π/6 slice and a π/12 slice: π/2 + π/6 + π/12 = **3π/4**.

## Wrapping up

Counting slices per quadrant is not the most elegant way to derive a sweep angle, but it is reliable and you can do it on paper next to the design. Once the static ring is right, animating it is a small step: drive `sweepAngle` from an `AnimationController`, and flip `shouldRepaint` to compare against `oldDelegate` so Flutter actually redraws.
