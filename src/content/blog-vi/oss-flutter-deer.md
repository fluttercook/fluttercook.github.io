---
title: "Flutter Deer: dự án luyện tập dáng production"
description: "Template shop đa flavor từng dạy layering sạch và kỷ luật test."
seoDescription: "Flutter Deer kiến trúc: Provider, flavor, layer sạch, integration test, bài học template production."
keywords:
  - flutter deer
  - flutter production template
  - flutter clean architecture example
  - flutter flavor example
  - flutter provider architecture
tags: ["Flutter", "OpenSource", "Architecture", "Template"]
sources:
  - name: "flutter_deer GitHub"
    url: "https://github.com/simplezhli/flutter_deer"
related:
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
  - slug: "oss-forui"
    title: "Forui"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🦌"
draft: false
---

Không phải repo học tập nào cũng sống lâu. Deer vẫn hữu ích vì cho thấy **khung app hoàn chỉnh**: flavor, component dùng chung, integration test và domain shop nhàm chán một cách có chủ đích.

![Sơ đồ: Flutter Deer](/blog/images/oss-flutter-deer.svg)



## Nên copy

- Folder theo feature thay vì mega-folder chỉ theo layer khi scale.
- Thư viện widget dùng chung kèm token/mockup trong repo.
- Integration test là một phần của “done”.

## Nên cập nhật

Ý kiến state management đã dịch chuyển (Riverpod/bloc…). Giữ **cấu trúc** Deer, làm mới tầng state theo team bạn.

## Cạm bẫy

Đừng paste UI mà không trích design token. Template thối khi hardcode API host.
