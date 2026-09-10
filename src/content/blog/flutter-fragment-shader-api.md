---
title: "Fragment shaders in Flutter: uniforms by name and sync textures"
description: "3.41–3.44 shader APIs get ergonomic: getUniformFloat by name, decodeImageFromPixelsSync, and high-bit textures for LUTs."
seoDescription: "Flutter FragmentShader getUniformFloat by name, decodeImageFromPixelsSync, high bitrate textures LUT Impeller shaders."
keywords:
  - flutter fragment shader
  - getUniformFloat flutter
  - decodeImageFromPixelsSync
  - flutter lut texture
  - flutter custom shader 2026
tags: ["Flutter", "Shaders", "Impeller", "Graphics"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "What's new in Flutter 3.41"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"
  - name: "Fragment shaders docs"
    url: "https://docs.flutter.dev/ui/design/graphics/fragment-shaders"
related:
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
  - slug: "flutter-widget-previews-stable"
    title: "Widget Previews Stable"
category: "Deep Dive"
topic: "Graphics"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🧬"
draft: false
---

Custom shaders stop being a niche once Impeller owns the stack. The recent API work removes the worst papercuts.

![Diagram: Fragment Shader API](/blog/images/flutter-fragment-shader-api.svg)


## Bind uniforms by name

```dart
void setUp(ui.FragmentShader shader) {
  shader.getUniformFloat('intensity').set(0.85);
}
```

No more counting float slots by hand — fewer off-by-one GPU bugs.

## Sync textures in the same frame

```dart
final image = picture.toImageSync(
  128,
  128,
  targetFormat: ui.TargetPixelFormat.rFloat32,
);
shader.setImageSampler(0, image);
```

`decodeImageFromPixelsSync` / `toImageSync` remove a frame of lag when creating sampler textures. High-bit formats (up to 128-bit float) unlock serious LUTs and SDFs.

## Workflow

1. Author `.frag` under `shaders/`.
2. Load via `ShaderLib` / asset API in docs.
3. Preview in isolation; then integrate behind a feature flag.

## Pitfalls

- Skia vs Impeller coordinate differences still bite ported shaders.
- Big LUTs need memory budgets — measure, do not assume.
