---
title: "Forui: hệ thống UI Flutter có chủ kiến"
description: "Widget ưu tiên cấu trúc và theming — lựa chọn thay Material đáng đánh giá."
seoDescription: "Forui kiến trúc design system Flutter: widget có chủ kiến, theming, component accessible."
keywords:
  - forui flutter
  - flutter ui library
  - material alternative flutter
  - forui design system
  - flutter accessible widgets
tags: ["Flutter", "OpenSource", "DesignSystem"]
sources:
  - name: "Forui GitHub"
    url: "https://github.com/forui-dev/forui"
  - name: "Forui docs"
    url: "https://forui.dev/"
related:
  - slug: "oss-shadcn-flutter"
    title: "shadcn-flutter"
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🧩"
draft: false
---

Forui đặt cược khác “Material ở khắp nơi”: cấu trúc chặt, default mạnh và theme được thiết kế như một hệ thống.

![Sơ đồ: Forui](/blog/images/oss-forui.svg)



## Khi nào nên đánh giá

- Sản phẩm muốn một look nhất quán mobile/desktop.
- Bạn chán override internal component Material.
- Accessibility là yêu cầu launch, không phải backlog.

## Cạm bẫy

Adopt hệ thống UI đầy đủ là migration. Pilot một luồng (settings + form) trước khi rewrite cả app.

So Forui với package `material_ui` độc lập nếu team vẫn muốn Material của Google làm nền.
