---
title: "GenUI và A2UI: agent ghép widget, không chỉ markdown"
description: "GenUI SDK và giao thức A2UI cho agent dựng UI Flutter sống — khác hẳn tường chữ chat."
seoDescription: "Flutter GenUI SDK giao thức A2UI, generative UI vượt chat, agent ghép widget, ví dụ Finnish It Hatcha."
keywords:
  - flutter genui
  - a2ui protocol
  - generative ui flutter
  - flutter ai ui agent
  - a2ui flutter sdk
tags: ["Flutter", "GenUI", "A2UI", "AI", "UX"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "genui package"
    url: "https://pub.dev/packages/genui"
  - name: "A2UI"
    url: "https://a2ui.org/"
related:
  - slug: "flutter-firebase-ai-logic"
    title: "Firebase AI Logic"
  - slug: "flutter-agentic-hot-reload"
    title: "Agentic Hot Reload"
category: "Deep Dive"
topic: "AI"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "✨"
draft: false
---

Chat UI dạy người dùng chấp nhận tường markdown. **Generative UI (GenUI)** đảo hợp đồng: model đề xuất *cấu trúc UI* — list, form, card — và Flutter render widget thật với state thật.

![Sơ đồ: GenUI and A2UI](/blog/images/flutter-genui-a2ui.svg)


## A2UI là gì

[A2UI](https://a2ui.org/) là protocol mở mô tả **agent** và **client** cùng nhau ghép UI và quản lý state. GenUI SDK của Flutter là client. Lượt tải package tăng mạnh trong 2026 khi team ship thật (ví dụ app học ngôn ngữ tự ghép UI bài học).

## Kiến thức kiến trúc

1. Intent người dùng tới backend/agent.
2. Agent emit cấu trúc A2UI (không phải text tự do).
3. GenUI map cấu trúc → widget Flutter trong catalog bị chặn.
4. Event trả về dạng action có cấu trúc agent xử lý được.

## Ràng buộc thiết kế

- **Catalog hơn hỗn loạn.** Chỉ cho phép widget bạn thiết kế; đừng để model bịa layout physics.
- **Vòng critic.** Validate output trước khi paint (empty state, overflow, nhãn a11y).
- **Template để nhanh.** Hybrid: template mạnh + slot model điền ổn định hơn generate thuần.

## Cạm bẫy

- Coi GenUI là engine theming — nó là protocol composition.
- Bỏ UI offline/error vì “model sẽ tự sửa”.
- Ship không có fallback đọc được khi catalog diễn đạt không nổi câu trả lời.
