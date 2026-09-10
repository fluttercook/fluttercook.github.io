---
title: "Fragment shader trong Flutter: uniform theo tên và texture đồng bộ"
description: "API shader 3.41–3.44 tiện hơn: getUniformFloat theo tên, decodeImageFromPixelsSync, texture high-bit cho LUT."
seoDescription: "Flutter FragmentShader getUniformFloat theo tên, decodeImageFromPixelsSync, texture high-bit LUT shader Impeller."
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

Custom shader hết “ngách” khi Impeller nắm stack. API gần đây gỡ các nốt đau tồi tệ nhất.

![Sơ đồ: Fragment Shader API](/blog/images/flutter-fragment-shader-api.svg)


## Bind uniform theo tên

```dart
void setUp(ui.FragmentShader shader) {
  shader.getUniformFloat('intensity').set(0.85);
}
```

Không còn đếm slot float thủ công — bớt bug off-by-one trên GPU.

## Texture đồng bộ trong cùng frame

```dart
final image = picture.toImageSync(
  128,
  128,
  targetFormat: ui.TargetPixelFormat.rFloat32,
);
shader.setImageSampler(0, image);
```

`decodeImageFromPixelsSync` / `toImageSync` bỏ một frame lag khi tạo texture sampler. Format high-bit (tới 128-bit float) mở khóa LUT và SDF nghiêm túc.

## Workflow

1. Viết `.frag` trong `shaders/`.
2. Load theo docs (ShaderLib / asset API).
3. Preview cách ly; rồi mới integrate sau feature flag.

## Cạm bẫy

- Khác biệt tọa độ Skia vs Impeller vẫn cắn shader port.
- LUT lớn cần ngân sách memory — phải đo.
