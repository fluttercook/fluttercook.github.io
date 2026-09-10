---
title: "Harmony Music: pattern player offline-first"
description: "Quét thư viện, hàng đợi và tách audio service trong app nhạc Flutter."
seoDescription: "Harmony Music kiến trúc Flutter: quét thư viện offline, quản lý queue, tách audio service."
keywords:
  - harmony music flutter
  - offline music player flutter
  - flutter audio service
  - flutter music queue
  - flutter local library
tags: ["Flutter", "OpenSource", "Music"]
sources:
  - name: "MediaKit"
    url: "https://github.com/media-kit/media-kit"
related:
  - slug: "oss-spotube-architecture"
    title: "Spotube Architecture"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎧"
draft: false
---

App nhạc offline là vấn đề storage, scan và lifecycle service. Player kiểu Harmony giữ index thư viện local và playback service sống sót khi UI điều hướng.

![Sơ đồ: Harmony Music](/blog/images/oss-harmony-music.svg)



## Pattern

1. Scan một lần, nghe filesystem event sau.
2. Queue nằm trong controller/service, không trong widget màn hình.
3. Notification/media session nền tảng là UX bắt buộc.

## Cạm bẫy

Thư viện lớn cần index tăng dần. Đừng chặn frame đầu bằng scan full SD.

So với Spotube nếu bạn còn cần catalog streaming.
