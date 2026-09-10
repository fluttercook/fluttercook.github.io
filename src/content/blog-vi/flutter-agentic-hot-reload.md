---
title: "Agentic Hot Reload: khi coding agent tự reload app đang chạy"
description: "Flutter 3.44 cho agent biết MCP tìm app đang chạy và trigger hot reload — khép kín vòng từ prompt tới pixel."
seoDescription: "Flutter Agentic Hot Reload MCP server, coding agent tự kết nối và hot reload app đang chạy."
keywords:
  - flutter agentic hot reload
  - flutter mcp server
  - ai coding agent flutter
  - hot reload ai agent
  - dart mcp hot reload
tags: ["Flutter", "AI", "MCP", "HotReload", "Agents"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "Dart & Flutter MCP server"
    url: "https://docs.flutter.dev/ai/mcp-server"
related:
  - slug: "flutter-agent-skills-mcp"
    title: "Agent Skills and MCP"
  - slug: "flutter-genui-a2ui"
    title: "GenUI and A2UI"
category: "Deep Dive"
topic: "AI Tooling"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🤖"
draft: false
---

Vòng AI cũ: dán lỗi → agent sửa file → bạn tự bấm `r` trong terminal. **Agentic Hot Reload** bỏ bước cuối. Dart/Flutter MCP server giúp agent tìm và kết nối app đang chạy, rồi trigger reload sau khi sửa.

![Sơ đồ: Agentic Hot Reload](/blog/images/flutter-agentic-hot-reload.svg)


## Vòng mới

1. `flutter run` (debug) với MCP server sẵn cho agent.
2. Prompt: “làm nút login màu cyan và to hơn.”
3. Agent sửa Dart, trigger reload, bạn nhìn pixel.

Không cần script keo dán. Dependency search được siết để agent đọc source package không cần full pub-cache; tool definition được gộp để giảm token.

## Mẹo setup

- Một debug session cho mỗi device bạn quan tâm; agent attach vào session đang chạy.
- Prompt nhỏ theo scope UI — Agentic Hot Reload thưởng cho diff nhỏ.
- Ghép Agent Skills để agent theo kiến trúc của bạn thay vì bịa mới.

## Giới hạn

Hot reload không phải hot *restart*. State và native channel vẫn cần restart. Nếu đổi không hiện, kiểm tra session còn kết nối và edit nằm trong library reloadable (không phải rearrange `main()` bắt buộc restart).
