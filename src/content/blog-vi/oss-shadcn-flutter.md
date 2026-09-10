---
title: "shadcn-flutter: port design system, không chỉ theme"
description: "Token, primitive và composite — port design system sao cho maintain được."
seoDescription: "shadcn-flutter kiến trúc: design token, primitive, composite, pattern port design system Flutter."
keywords:
  - shadcn flutter
  - flutter design system
  - flutter design tokens
  - port shadcn to flutter
  - flutter ui primitives
tags: ["Flutter", "OpenSource", "DesignSystem"]
sources:
  - name: "shadcn-flutter GitHub"
    url: "https://github.com/nank1ro/shadcn-flutter"
related:
  - slug: "oss-forui"
    title: "Forui"
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎛️"
draft: false
---

Copy design system web vào Flutter thất bại nếu chỉ copy màu. shadcn-flutter hữu ích vì ép câu chuyện phân lớp: token → primitive → composite → app của bạn.

![Sơ đồ: shadcn-flutter](/blog/images/oss-shadcn-flutter.svg)



## Học theo

1. Sở hữu source (mô hình copy-in) để sửa không đau fork.
2. Giữ accessibility và focus ring là primitive hạng nhất.
3. Tài liệu hóa variant; đừng giấu trong một mega-widget.

## Cạm bẫy

Giả định CSS web (cascade, :hover) không map 1:1. Ngân sách polish pointer desktop tách khỏi touch mobile.

Dùng khi default Material đấu với brand của bạn.
