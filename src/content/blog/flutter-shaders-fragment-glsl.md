---
title: "Fragment shaders in Flutter: the GPU escape hatch, and its costs"
description: "Flutter can load GLSL fragment shaders and run them on the GPU. That unlocks effects the widget layer cannot express — and introduces a compilation cost, a uniform-plumbing chore, and a set of platform caveats worth knowing before you commit."
seoDescription: "Using fragment shaders in Flutter: FragmentProgram, uniforms, the flutter: shaders pubspec entry, AnimatedSampler, sampler2D inputs, and when a shader is the wrong answer."
keywords:
  - flutter fragment shader
  - flutter fragmentprogram glsl
  - flutter shader uniforms
  - flutter animatedsampler
  - flutter gpu effects
  - flutter shader performance
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-25"
emoji: "🌈"
tags: ["Flutter", "Shaders", "GPU", "Graphics", "Performance"]
sources:
  - name: "Writing and using fragment shaders — Flutter documentation"
    url: "https://docs.flutter.dev/ui/design/graphics/fragment-shaders"
  - name: "FragmentProgram — Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/FragmentProgram-class.html"
  - name: "FragmentShader — Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/FragmentShader-class.html"
  - name: "ShaderMask — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ShaderMask-class.html"
  - name: "CustomPainter — Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/CustomPainter-class.html"
  - name: "Impeller rendering engine — Flutter documentation"
    url: "https://docs.flutter.dev/perf/impeller"
related:
  - slug: "flutter-custom-renderobject"
    title: "When widget composition runs out: writing your own RenderObject"
  - slug: "flutter-custom-scroll-physics"
    title: "Custom scroll physics: making a list stop where you want it to"
draft: false
---

There is a category of visual effect that widgets simply cannot produce: per-pixel distortion, procedural gradients that animate without rebuilding, dissolves, ripples, chromatic aberration. You can approximate some of them with enough `Transform` and `Opacity` layers, and the result will be slow and wrong.

Flutter's answer is a GLSL fragment shader compiled at build time and executed on the GPU. It is a genuinely powerful escape hatch. It is also a different programming model with its own costs, and the honest version of this article covers both.

## The minimum viable shader

A fragment shader is a program that runs once per pixel and returns a colour. Flutter's dialect is GLSL ES with a small set of Flutter-specific helpers from `flutter/runtime_effect.glsl`.

`shaders/ripple.frag`:

```glsl
#version 460 core
#include <flutter/runtime_effect.glsl>

precision highp float;

uniform vec2 uSize;
uniform float uTime;
uniform vec4 uColor;

out vec4 fragColor;

void main() {
  vec2 uv = FlutterFragCoord().xy / uSize;
  float d = distance(uv, vec2(0.5));
  float wave = sin(d * 40.0 - uTime * 4.0) * 0.5 + 0.5;
  fragColor = uColor * wave;
}
```

Two lines are Flutter-specific and both matter. `#include <flutter/runtime_effect.glsl>` brings in `FlutterFragCoord()`, which you must use instead of the raw `gl_FragCoord` — the raw value is not in the coordinate space you expect once Flutter's own transforms are applied. And `uSize` is not automatic: Flutter gives you no built-in resolution uniform, so you pass the size yourself.

Register it in `pubspec.yaml` under the `flutter:` key, not under `assets:`:

```yaml
flutter:
  shaders:
    - shaders/ripple.frag
```

That entry is what invokes the shader compiler during the build. A shader listed under `assets:` will load as bytes and fail at `FragmentProgram.fromAsset` in a way that reads as a missing-file error.

## Loading and driving it

`FragmentProgram.fromAsset` is asynchronous and returns a program you use to create shader instances:

```dart
class RipplePainter extends CustomPainter {
  RipplePainter(this.program, this.time, this.color)
      : super(repaint: null);

  final ui.FragmentProgram program;
  final double time;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final shader = program.fragmentShader()
      ..setFloat(0, size.width)   // uSize.x
      ..setFloat(1, size.height)  // uSize.y
      ..setFloat(2, time)         // uTime
      ..setFloat(3, color.r)      // uColor.r
      ..setFloat(4, color.g)
      ..setFloat(5, color.b)
      ..setFloat(6, color.a);

    canvas.drawRect(Offset.zero & size, Paint()..shader = shader);
  }

  @override
  bool shouldRepaint(RipplePainter old) =>
      old.time != time || old.color != color;
}
```

Look at the indices. **Uniforms are addressed by flat float index, in declaration order, with vectors expanded.** `uSize` is a `vec2` and occupies indices 0 and 1; `uTime` is 2; `uColor` is a `vec4` and takes 3 through 6. There is no name-based setter. Insert a uniform in the middle of the shader and every index below it shifts — silently, with no compile error, producing an effect that is merely wrong.

The mitigation is a small constant block right next to the shader source:

```dart
abstract final class RippleUniforms {
  static const sizeX = 0;
  static const sizeY = 1;
  static const time = 2;
  static const colorR = 3;
}
```

It costs four lines and removes an entire class of debugging.

## Wiring it into a widget

Load the program once, high up, and animate the time uniform with a ticker:

```dart
class RippleBox extends StatefulWidget {
  const RippleBox({super.key, required this.color});
  final Color color;

  @override
  State<RippleBox> createState() => _RippleBoxState();
}

class _RippleBoxState extends State<RippleBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(seconds: 4),
  )..repeat();

  ui.FragmentProgram? _program;

  @override
  void initState() {
    super.initState();
    ui.FragmentProgram.fromAsset('shaders/ripple.frag').then((p) {
      if (mounted) setState(() => _program = p);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final program = _program;
    if (program == null) return const SizedBox.expand();

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) => CustomPaint(
        painter: RipplePainter(
          program,
          _controller.value * 4,
          widget.color,
        ),
        size: Size.infinite,
      ),
    );
  }
}
```

`fromAsset` caches per asset path, so calling it from several widgets is not a disaster — but loading it once and passing it down is still cleaner and makes the null-while-loading state explicit in one place.

## Sampling the widget tree

The more interesting use is applying a shader to something Flutter already painted — a dissolve over a real widget, not a procedural pattern. That needs a `sampler2D` uniform:

```glsl
uniform sampler2D uTexture;
uniform float uProgress;

void main() {
  vec2 uv = FlutterFragCoord().xy / uSize;
  vec4 src = texture(uTexture, uv);
  float noise = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
  fragColor = noise < uProgress ? vec4(0.0) : src;
}
```

Samplers use a separate index space from floats — `setImageSampler(0, image)`, not `setFloat`. Mixing the two up produces a black result with no error.

Capturing the widget subtree as an image is the fiddly part. `AnimatedSampler` from the `flutter_shaders` package wraps the `SnapshotWidget` machinery and is the pragmatic choice; doing it by hand means a `RepaintBoundary` plus `toImage`, which is asynchronous and therefore a frame behind.

## What it costs

| Cost | Detail |
| --- | --- |
| First-use compilation | The shader is compiled for the target GPU on first use; Impeller compiles ahead of time where it can, but a first-frame hitch is still possible |
| No hot reload of `.frag` | Changing shader source generally needs a restart, not a reload |
| Debugging | No `print`. You debug by outputting values as colours |
| Platform variance | Precision qualifiers and float behaviour differ across GPUs; test on a real low-end Android device, not just a simulator |
| Web | Support depends on the web renderer in use; verify on your target before designing around it |

The one that bites teams is the second: the iteration loop for shader work is slow enough that it changes how you should work — build the effect in a shader playground first, port it once it looks right.

## When not to reach for one

A shader is the right tool for per-pixel work over a continuous surface. It is the wrong tool for:

- **A gradient.** `LinearGradient` and friends are already GPU-accelerated and far simpler.
- **A blur.** `BackdropFilter` with `ImageFilter.blur` exists and is optimised.
- **Masking one widget with another shape.** `ShaderMask` or `ClipPath` handles this without GLSL.
- **Anything that changes layout.** Shaders paint; they cannot move or size a widget.

The heuristic I use: if you can describe the effect in terms of shapes and transforms, use widgets. If you can only describe it as "for each pixel, compute…", write a shader.

## FAQ

**Why is my shader completely black?**

Most often uniforms never set — an unset uniform is zero, and a zero size means every `uv` divides by zero. Set every declared uniform, including ones you are not animating yet.

**Why does it look right on my phone and wrong on another?**

Precision. `precision highp float` is a request, not a guarantee, and low-end mobile GPUs vary. Avoid very large coordinate values and long accumulations of floats.

**Can I use a vertex shader?**

Flutter's runtime effects are fragment shaders only. Vertex-level control means going to `dart:ui` vertices or a custom `RenderObject` instead.

**Does using a shader hurt battery?**

A full-screen shader running every frame is continuous GPU work. Pause the animation controller when the effect is off-screen or the app is inactive — this is the single largest win available.

**How do I test a shader?**

Golden tests over a `CustomPaint` at fixed uniform values catch regressions. They are GPU-dependent, so pin the test environment or they will flake.

---

*The `FragmentProgram` API, the `flutter: shaders:` pubspec entry, `FlutterFragCoord()`, and the flat-index uniform model described here are documented in the Flutter references linked above. The uniform-constant-block practice, the cost table's weighting, and the heuristic for when a shader is the wrong tool are my own judgement from building effects this way. Shader support and Impeller behaviour move quickly between releases — verify on your target platforms before committing to an effect.*
