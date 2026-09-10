---
title: "Spotube: client nhạc Flutter ưu tiên privacy"
description: "Riverpod, drift, media_kit và story release đa store — Spotube ship nhạc không backend riêng ra sao."
seoDescription: "Spotube kiến trúc Flutter: state Riverpod, database drift, media_kit audio, pattern client nhạc đa nền tảng."
keywords:
  - spotube flutter
  - spotube architecture
  - flutter music player open source
  - media_kit flutter
  - riverpod music app
tags: ["Flutter", "OpenSource", "Music", "Riverpod"]
sources:
  - name: "Spotube GitHub"
    url: "https://github.com/KRTirtho/spotube"
  - name: "media_kit"
    url: "https://github.com/media-kit/media-kit"
related:
  - slug: "oss-harmony-music"
    title: "Harmony Music"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎵"
draft: false
---

Spotube chứng minh bạn ship được trải nghiệm nhạc bóng bẩy đa mobile/desktop từ một codebase Flutter — không cần sở hữu backend catalog.

![Sơ đồ: Spotube Architecture](/blog/images/oss-spotube-architecture.svg)



## Tín hiệu stack

- **Riverpod** cho state và DI.
- **drift** cho dữ liệu thư viện bền vững.
- **media_kit** (và plugin liên quan) cho playback đa nền tảng.
- Release store gồm F-Droid/Flathub — packaging là một phần sản phẩm.

## Đáng học

1. Tách *tìm catalog* khỏi *thư viện local*.
2. Playback là service headless, UI chỉ là shell mỏng.
3. Persist queue và vị trí — app nhạc bị resume liên tục.

## Cạm bẫy

- API audio nền tảng khác nhau nhiều (background mode, lock screen, Bluetooth).
- Ràng buộc pháp lý/ToS với catalog bên thứ ba không phải vấn đề Flutter, nhưng giết app nhanh hơn một frame jank.

Dùng Spotube như bản đồ **mặt phẳng plugin** mà app media thật cần.
