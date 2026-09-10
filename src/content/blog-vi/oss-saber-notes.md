---
title: "Saber: ghi chú viết tay và file local-first"
description: "Input canvas, composite highlighter và sync tùy chọn — stack ghi chú Flutter."
seoDescription: "Saber kiến trúc Flutter: canvas viết tay, lưu local-first, sync Nextcloud tùy chọn."
keywords:
  - saber notes flutter
  - flutter handwriting app
  - flutter canvas notes
  - local first flutter
  - stylus flutter
tags: ["Flutter", "OpenSource", "Notes", "Canvas"]
sources:
  - name: "Saber GitHub"
    url: "https://github.com/saber-notes/saber"
related:
  - slug: "oss-lotti-journal"
    title: "Lotti Journal"
  - slug: "oss-ente-photos"
    title: "Ente Photos"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "✍️"
draft: false
---

App viết tay là vấn đề sâu tới RenderObject: input nét, blend highlighter, export và định dạng file đều quan trọng.

![Sơ đồ: Saber Notes](/blog/images/oss-saber-notes.svg)



## Bài học

1. File local trước; sync sau. Note phải mở được offline.
2. Model nét là data (điểm/áp lực), không phải screenshot.
3. Composite highlighter hai lớp là bài học graphics cổ điển trong sản phẩm.

## Cạm bẫy

- Latency stylus cảm nhận được ở ~1 frame.
- Lock-in định dạng file làm user giận hơn thiếu cloud.

Học Saber khi xây công cụ Flutter **lõi canvas**.
