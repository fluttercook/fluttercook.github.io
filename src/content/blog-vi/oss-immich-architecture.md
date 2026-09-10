---
title: "Immich: bài học kiến trúc từ stack ảnh Flutter 100k sao"
description: "Immich ghép client Flutter, API NestJS và pipeline ML thế nào — và pattern nào bạn học được."
seoDescription: "Immich kiến trúc Flutter: client mobile, background sync, pattern backup ảnh self-hosted đáng học."
keywords:
  - immich flutter
  - immich architecture
  - self hosted photo backup flutter
  - immich mobile client
  - flutter large scale app
tags: ["Flutter", "OpenSource", "Photos", "Architecture"]
sources:
  - name: "Immich GitHub"
    url: "https://github.com/immich-app/immich"
  - name: "Immich docs"
    url: "https://immich.app/docs"
related:
  - slug: "oss-ente-photos"
    title: "Ente Photos"
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📸"
draft: false
---

Immich là app Flutter hiếm hoi dân self-host đều biết: backup kiểu Google Photos, album, tìm kiếm ML, và client mobile phải sống sót giữa mạng chập chờn cùng thư viện khổng lồ.

![Sơ đồ: Immich Architecture](/blog/images/oss-immich-architecture.svg)



## Stack thực tế

- Client **Flutter** iOS/Android (cùng surface web/desktop trong monorepo).
- Server **NestJS** với API client sinh tự động — OpenAPI giữ mobile và server trung thực.
- Service **Python ML** cho tìm kiếm kiểu CLIP và nhận diện.
- **Docker** là đường cài đặt chính thức.

## Pattern đáng học

1. **API client sinh tự động.** Đừng viết tay DTO cho domain lớn.
2. **Upload theo nền.** Coi sync là feature sản phẩm, không phải việc thêm.
3. **Thumbnail do server giữ.** Mobile không nên re-encode ảnh 48MP trên phone tầm trung.

## Ghi chú Flutter

Gallery lớn phạt `GridView` ngây thơ. App kiểu Immich cần recycle view mạnh, chiến lược placeholder và isolate decode cẩn thận. Hãy học cách hàng đợi upload sống sót qua restart app.

## Nếu copy một cách ngây thơ

- Kéo cả monorepo vào app nhỏ.
- Bỏ authz vì giả định “mạng cục bộ”.
- Ship tìm kiếm ML không có path rỗng/lỗi.

Hãy học **hợp đồng client/server** và **thiết kế hàng đợi sync**. Docker topology để sau.
