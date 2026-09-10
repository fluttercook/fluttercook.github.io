---
title: "Ente: ảnh mã hóa đầu-cuối trên Flutter"
description: "UX crypto là vấn đề thiết kế. Ente cho thấy gallery mã hóa vẫn dùng được."
seoDescription: "Ente kiến trúc Flutter: gallery E2EE, UX quản lý khóa, pattern backup mã hóa."
keywords:
  - ente photos flutter
  - e2ee photo app
  - flutter encrypted gallery
  - ente architecture
  - privacy photo backup
tags: ["Flutter", "OpenSource", "Crypto", "Photos"]
sources:
  - name: "Ente GitHub"
    url: "https://github.com/ente/ente"
  - name: "Ente docs"
    url: "https://ente.io/"
related:
  - slug: "oss-immich-architecture"
    title: "Immich Architecture"
  - slug: "oss-saber-notes"
    title: "Saber Notes"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔐"
draft: false
---

Nếu Immich là mặc định self-host, Ente là bản đối trọng privacy-first: client (gồm Flutter mobile) mã hóa trước khi upload, server chỉ giữ blob không đọc được.

![Sơ đồ: Ente Photos](/blog/images/oss-ente-photos.svg)



## Nên học

1. **UX khóa.** Recovery phrase và chia sẻ gia đình thắng dashboard “tin chúng tôi”.
2. Pipeline **encrypt-then-upload** có resume.
3. Surface sản phẩm cho Photos *và* secret kiểu Auth.

## Cạm bẫy

- User quên passphrase — thiết kế khôi phục tài khoản trước khi launch.
- Sinh thumbnail không được lộ plaintext trên thiết bị dùng chung.

Hãy copy **cuộc đối thoại threat model**, không chỉ lựa chọn cipher.
