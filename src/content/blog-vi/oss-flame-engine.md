---
title: "Flame: vòng lặp game bên trong Flutter"
description: "Cây component, vòng game và package cầu nối — vị trí Flame trong sản phẩm Flutter."
seoDescription: "Flame kiến trúc Flutter: cây component, vòng game, package cầu nối audio bloc tiled rive."
keywords:
  - flame engine
  - flutter game development
  - flame component tree
  - flutter 2d game
  - flame architecture
tags: ["Flutter", "OpenSource", "Games"]
sources:
  - name: "Flame GitHub"
    url: "https://github.com/flame-engine/flame"
  - name: "Flame docs"
    url: "https://docs.flame-engine.org/"
related:
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
  - slug: "flutter-widget-previews-stable"
    title: "Widget Previews Stable"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎮"
draft: false
---

Flame là cách Flutter làm game mà không rời widget tree sang engine khác. `GameWidget` host cây component cập nhật bởi game loop; overlay giữ HUD/chat bằng Flutter thường.

![Sơ đồ: Flame Engine](/blog/images/oss-flame-engine.svg)



## Học theo

1. UI hybrid: canvas game + overlay Flutter cho menu/monetize.
2. Package cầu nối (audio, physics, tiled, bloc) giữ core nhỏ.
3. Update deterministic giúp test và replay.

## Cạm bẫy

- Trộn UI `setState` vào game loop sẽ đấu với kiến trúc.
- Ngân sách thermal mobile quan trọng hơn FPS desktop.

Dùng Flame cho mini-game 2D và canvas tương tác trong sản phẩm, không chỉ đồ chơi.
