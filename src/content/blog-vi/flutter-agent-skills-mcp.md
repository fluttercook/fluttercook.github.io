---
title: "Agent Skills cho Dart và Flutter: workflow agent rẻ và chuẩn hơn"
description: "Skill chính thức cung cấp bước production-grade cho agent: localization, integration test… kèm MCP tools gọn hơn."
seoDescription: "Flutter Agent Skills cho coding agent, package skills, MCP tools gọn, tiết kiệm token theo best practice Flutter."
keywords:
  - flutter agent skills
  - dart agent skills
  - flutter mcp tools
  - ai skills flutter localization
  - coding agent flutter best practices
tags: ["Flutter", "Dart", "AI", "MCP", "Skills"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "Introducing skills for Dart and Flutter"
    url: "https://blog.flutter.dev/introducing-skills-for-dart-and-flutter-23837c6ec0ae"
  - name: "Package skills"
    url: "https://dart.dev/tools/pub/package-skills"
related:
  - slug: "flutter-agentic-hot-reload"
    title: "Agentic Hot Reload"
  - slug: "flutter-genui-a2ui"
    title: "GenUI and A2UI"
category: "Deep Dive"
topic: "AI Tooling"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🧰"
draft: false
---

Agent giỏi gõ phím nhưng kém gu. **Agent Skills** mã hóa gu Flutter/Dart thành hướng dẫn ngắn theo task mà agent load được: cách thêm integration test, setup localization, cấu trúc feature.

![Sơ đồ: Agent Skills and MCP](/blog/images/flutter-agent-skills-mcp.svg)


## Vì sao skill thắng system prompt khổng lồ

- **Theo scope.** Chỉ load việc đang cần.
- **Version cùng hệ sinh thái.** Skill ship kèm package và docs.
- **Rẻ token.** Mặt phẳng tool MCP cũng được gộp để agent dành budget cho code của bạn.

## Dùng hàng ngày

1. Cài/cấu hình Dart & Flutter MCP server cho agent (Claude Code, Gemini CLI, Cursor…).
2. Ưu tiên invoke skill chính thức hơn prompt tự do “viết màn login”.
3. Giữ skill local cho luật nhà (folder layout, convention Riverpod, style test).

## Package skills

Pub package có thể ship skill riêng để agent biết idioms *của package đó*, không phải Flutter chung chung. Nếu bạn maintain plugin phổ biến, skill đang thành một phần DX tốt — và giảm API bị bịa.

## Anti-pattern

- Một prompt vừa redesign kiến trúc, vừa add feature, vừa viết test. Hãy tách.
- Tắt skill để “tiết kiệm token” rồi trả giá bằng ba lần viết sai.
