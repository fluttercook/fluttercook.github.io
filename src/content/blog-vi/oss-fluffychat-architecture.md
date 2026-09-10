---
title: "FluffyChat: chat Matrix trên Flutter với E2EE thật"
description: "Một client Matrix xử lý room, mã hóa và đa nền tảng từ Flutter ra sao."
seoDescription: "FluffyChat kiến trúc Matrix Flutter: E2EE, sync room, pattern client chat đa nền tảng đáng học."
keywords:
  - fluffychat flutter
  - matrix client flutter
  - flutter e2ee chat
  - flutter matrix sdk
  - open source chat app
tags: ["Flutter", "OpenSource", "Chat", "Matrix"]
sources:
  - name: "FluffyChat GitHub"
    url: "https://github.com/krille-chan/fluffychat"
  - name: "Matrix spec"
    url: "https://spec.matrix.org/"
related:
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
  - slug: "oss-ente-photos"
    title: "Ente Photos"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "💬"
draft: false
---

Chat trông đơn giản cho tới khi mã hóa và sync đa thiết bị xuất hiện. FluffyChat là client Matrix production bằng Flutter — hữu ích nếu bạn quan tâm kiến trúc messaging mà không tự bịa protocol.

![Sơ đồ: FluffyChat Architecture](/blog/images/oss-fluffychat-architecture.svg)



## Nhịp kiến trúc

- **Matrix SDK** là bộ não protocol (crypto Rust như Vodozemac bên dưới).
- Flutter là shell chung cho mobile và desktop.
- Push tùy chọn (FCM…) xếp lên sync — không thay sync.

## Học theo

1. Giữ protocol state ngoài widget; expose stream/selector.
2. Room là domain object hạng nhất, không phải màn hình.
3. UX verify thiết bị là surface sản phẩm, không phải footnote settings.

## Cạm bẫy

Bug E2EE là bug niềm tin. Đừng tự viết crypto. Offline queue và event lệch thứ tự sẽ phá UI `setState` ngây thơ.

Nếu cần chat, ưu tiên Matrix (hoặc protocol trưởng thành) hơn soup JSON socket tự chế.
