---
title: "Hiddify Next: UI Flutter trên lõi tunnel"
description: "Client proxy đa nền tảng cho thấy cách ghép Flutter với lõi kiểu Go/Sing-box."
seoDescription: "Hiddify Next kiến trúc Flutter: lõi Sing-box, UX VPN client, pattern proxy đa giao thức."
keywords:
  - hiddify flutter
  - flutter vpn client
  - sing-box flutter
  - flutter network tunnel
  - proxy app architecture
tags: ["Flutter", "OpenSource", "Networking"]
sources:
  - name: "Hiddify GitHub"
    url: "https://github.com/hiddify/hiddify-app"
related:
  - slug: "oss-rustdesk-flutter"
    title: "RustDesk Hybrid"
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔐"
draft: false
---

Client proxy/VPN sống ở rìa quyền OS. Hiddify Next ghép UI Flutter với lõi tunnel hiệu năng cao (dòng Sing-box/Go) để UI vẫn biểu đạt trong khi data path nhàm chán và nhanh.

![Sơ đồ: Hiddify Next](/blog/images/oss-hiddify-next.svg)



## Bài học

1. **Status là stream.** Latency, server đang nối, lỗi phải là một model nhất quán.
2. **Config là data.** Import/export profile; đừng hardcode endpoint trong widget.
3. **API VPN nền tảng** là phần khó — cô lập sau service interface.

## Cạm bẫy

- Pin và thermal khi tunnel always-on.
- Chính sách store khác nhau cho app VPN.

Dùng repo này khi cần tham chiếu **Flutter backed by service**, không chỉ CRUD thuần.
