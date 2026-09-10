---
title: "LocalSend: truyền file kiểu AirDrop không cần cloud"
description: "Protocol LAN Flutter + Rust trên cổng 53317 — bài học mạng local-first."
seoDescription: "LocalSend kiến trúc Flutter Rust: truyền file LAN HTTPS 53317, không cloud, desktop mobile."
keywords:
  - localsend architecture
  - flutter file sharing lan
  - localsend protocol
  - flutter rust hybrid
  - airdrop alternative flutter
tags: ["Flutter", "OpenSource", "Networking", "Rust"]
sources:
  - name: "LocalSend GitHub"
    url: "https://github.com/localsend/localsend"
  - name: "LocalSend site"
    url: "https://localsend.org/"
related:
  - slug: "oss-rustdesk-flutter"
    title: "RustDesk Hybrid"
  - slug: "oss-immich-architecture"
    title: "Immich Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📡"
draft: false
---

LocalSend hỏi một câu sản phẩm sắc: hai thiết bị đổi file không cần tài khoản server được không? Có — nếu bạn thiết kế discovery LAN, HTTPS và consent rõ ràng.

![Sơ đồ: LocalSend Architecture](/blog/images/oss-localsend-architecture.svg)



## Điểm thiết kế

- Peer protocol trên HTTPS cục bộ (thường gắn với cổng **53317**).
- UI Flutter với phần Rust/native cho đường nhạy hiệu năng.
- Không có control plane cloud — privacy là feature.

## Học theo

1. Discovery + consent UX là nửa sản phẩm.
2. Transfer phải resume được và hiện rõ; lỗi im lặng phá niềm tin.
3. Giữ CLI headless cho power user và automation.

## Cạm bẫy

- Giới hạn background mobile giết transfer dài ngây thơ.
- Mạng hỗn hợp (AP isolation, VPN, captive portal) sinh support load — hãy tài liệu hóa.

Học LocalSend khi cần pattern **local-first**, không chỉ một package để copy.
