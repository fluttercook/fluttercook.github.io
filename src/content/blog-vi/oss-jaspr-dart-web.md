---
title: "Jaspr: Dart server-driven cho web"
description: "Mental model Flutter trên server — gồm framework dựng docs site chính thức."
seoDescription: "Jaspr kiến trúc web Dart: component server, hydration, UI kiểu Flutter phía server."
keywords:
  - jaspr dart
  - dart web framework
  - flutter mental model server
  - jaspr architecture
  - dart ssr
tags: ["Dart", "OpenSource", "Web"]
sources:
  - name: "Jaspr GitHub"
    url: "https://github.com/schultek/jaspr"
  - name: "Jaspr site"
    url: "https://jaspr.site"
related:
  - slug: "oss-serverpod"
    title: "Serverpod"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🌐"
draft: false
---

Jaspr mang mental model component lên Dart phía server. Nếu bạn thích cấu trúc Flutter nhưng cần HTML/SEO, đây là hệ sinh thái kề cận — đáng chú ý khi góp phần vào hiện diện web của chính Flutter.

![Sơ đồ: Jaspr Dart Web](/blog/images/oss-jaspr-dart-web.svg)



## Bài học

1. Model Dart dùng chung giữa API, UI server và client Flutter giảm lệch DTO.
2. SSR/hydration là vấn đề đóng gói nhiều như vấn đề UI.
3. Server component khuyến khích trang nhàm chán, cache được.

## Cạm bẫy

Đừng giả định widget Flutter chạy nguyên xi. Constraint layout và lifecycle khác mobile.

Cân nhắc Jaspr cho site nội dung và dashboard nơi SEO quan trọng và Dart đã là ngôn ngữ của bạn.
