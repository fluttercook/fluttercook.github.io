---
title: "RustDesk: lõi Rust, vỏ Flutter"
description: "Một sản phẩm remote desktop tách Rust hiệu năng cao khỏi UI Flutter ra sao."
seoDescription: "RustDesk kiến trúc hybrid Flutter: lõi Rust FFI, UI Flutter, pattern remote desktop open source."
keywords:
  - rustdesk flutter
  - rust flutter hybrid
  - flutter ffi desktop
  - open source remote desktop
  - rustdesk architecture
tags: ["Flutter", "OpenSource", "Rust", "Desktop"]
sources:
  - name: "RustDesk GitHub"
    url: "https://github.com/rustdesk/rustdesk"
  - name: "RustDesk docs"
    url: "https://rustdesk.com/docs/en/"
related:
  - slug: "oss-localsend-architecture"
    title: "LocalSend Architecture"
  - slug: "oss-hiddify-next"
    title: "Hiddify Next"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🖥️"
draft: false
---

Không phải mọi vấn đề pixel là vấn đề Dart. RustDesk giữ capture/encode/networking trong **Rust** và dùng Flutter làm shell tương tác — dạng hybrid bạn nên hiểu trước khi rewrite module native bằng Dart thuần.

![Sơ đồ: RustDesk Hybrid](/blog/images/oss-rustdesk-flutter.svg)



## Phân chia trách nhiệm

| Mục | Nơi |
| --- | --- |
| Capture màn, codec, relay | Lõi Rust |
| UX kết nối, settings, session UI | Flutter |
| Tích hợp OS | Platform channel / FFI |

## Học theo

1. Vẽ biên cứng: vòng UI nóng vs vòng data nóng.
2. Ưu tiên FFI cho throughput; channel cho event thưa.
3. Giữ session state ngoài cây widget.

## Cạm bẫy

- Build hybrid nhân đôi ma trận CI.
- ABI và packaging installer desktop không đơn giản.

App nặng UI có thể chỉ cần Flutter. App nặng pipeline hãy copy **biên giới** của RustDesk, chưa chắc đã copy Rust.
