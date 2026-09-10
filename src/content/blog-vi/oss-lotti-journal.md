---
title: "Lotti: journal với audio, habit và local DB nghiêm túc"
description: "Model data local phức tạp trong Flutter — vượt tutorial todo-app."
seoDescription: "Lotti kiến trúc journal Flutter: database local, note audio, theo dõi habit, app offline phức tạp."
keywords:
  - lotti flutter
  - flutter journaling app
  - flutter local database complex
  - flutter audio notes
  - offline first journal
tags: ["Flutter", "OpenSource", "Productivity"]
sources:
  - name: "Lotti GitHub"
    url: "https://github.com/lotti/lotti"
related:
  - slug: "oss-saber-notes"
    title: "Saber Notes"
  - slug: "oss-cashew-budget"
    title: "Cashew Budget"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📔"
draft: false
---

Tutorial Flutter hay dừng ở CRUD. Lotti thú vị vì journaling buộc entry đa modal (text, audio, habit, đo lường) và lưu trữ local dài hạn.

![Sơ đồ: Lotti Journal](/blog/images/oss-lotti-journal.svg)



## Bài học

1. Kiểu entry phân cấp thắng một row nullable khổng lồ.
2. Capture + playback audio là surface platform, không phải widget.
3. Insight cần index — thiết kế query trước chart.

## Cạm bẫy

Migration trên dữ liệu cá nhân là thiêng; viết cẩn thận. Quyền ghi âm nền khác nhau theo OS.

Nhìn Lotti khi “app note đơn giản” của bạn hết đơn giản.
