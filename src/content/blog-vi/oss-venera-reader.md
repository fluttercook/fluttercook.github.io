---
title: "Venera: layout reader tùy chỉnh trong Flutter"
description: "App đọc comic/manga đòi layout engine tùy chỉnh, cache và UX thư viện."
seoDescription: "Venera kiến trúc đọc comic Flutter: layout tùy chỉnh, image cache, pattern quản lý thư viện."
keywords:
  - venera flutter
  - flutter comic reader
  - flutter custom layout
  - flutter image cache reader
  - manga app flutter
tags: ["Flutter", "OpenSource", "Reader"]
sources:
  - name: "Venera GitHub"
    url: "https://github.com/venera-app/venera"
related:
  - slug: "oss-saber-notes"
    title: "Saber Notes"
  - slug: "oss-immich-architecture"
    title: "Immich Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📚"
draft: false
---

App đọc trông như “chỉ là ảnh” cho tới khi page mode, RTL, zoom và pre-cache va nhau. Venera là nghiên cứu hay về layout tùy chỉnh + quản lý thư viện.

![Sơ đồ: Venera Reader](/blog/images/oss-venera-reader.svg)



## Học theo

1. Page model độc lập với page widget.
2. Pre-cache trang kề mạnh kèm memory cap.
3. Thư viện là local DB + nguồn remote tùy chọn.

## Cạm bẫy

Pinch-zoom và lật trang đấu nhau; định nghĩa gesture arena sớm. Decode off UI isolate.

Tham chiếu tốt khi xây viewer **media scroll dài**.
