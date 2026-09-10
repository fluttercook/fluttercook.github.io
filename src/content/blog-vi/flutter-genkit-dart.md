---
title: "Genkit Dart: app AI full-stack không rời Dart"
description: "Genkit Dart mang flow AI model-agnostic, tool và structured output lên cả server lẫn client Flutter."
seoDescription: "Genkit Dart Flutter AI full-stack, googleAI gemini generate, tool và flow type-safe bằng Dart cho app AI."
keywords:
  - genkit dart flutter
  - flutter ai framework
  - dart genkit gemini
  - full stack ai dart
  - flutter tool calling ai
tags: ["Flutter", "Dart", "Genkit", "AI"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "Genkit Dart announcement"
    url: "https://dart.dev/blog/announcing-genkit-dart-build-full-stack-ai-apps-with-dart-and-flutter"
  - name: "Genkit docs"
    url: "https://genkit.dev/docs/dart/get-started"
related:
  - slug: "flutter-firebase-ai-logic"
    title: "Firebase AI Logic"
  - slug: "flutter-agent-skills-mcp"
    title: "Agent Skills and MCP"
category: "Deep Dive"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🧠"
draft: false
---

**Genkit Dart** là framework mã nguồn mở cho app AI với API model-agnostic (Google, Anthropic, OpenAI…). Chạy được cả server lẫn bên trong client Flutter — một ngôn ngữ từ prototype tới production.

![Sơ đồ: Genkit Dart](/blog/images/flutter-genkit-dart.svg)


## Ý tưởng lõi

- `Genkit()` + plugin provider.
- Structured output type-safe và tool calling.
- Hội thoại nhiều lượt và observability sẵn có.

```dart
import 'package:genkit/genkit.dart';
import 'package:genkit_google_genai/genkit_google_genai.dart';

void main() async {
  final ai = Genkit(plugins: [googleAI()]);
  final response = await ai.generate(
    model: googleAI.gemini('gemini-flash-latest'),
    prompt: 'Vì sao Dart hợp với ứng dụng AI?',
  );
  print(response.text);
}
```

## Ghép vào sản phẩm Flutter

| Tầng | Lựa chọn |
| --- | --- |
| UI nhạy latency | Genkit client / Firebase AI Logic |
| Tool, RAG, billing, audit | Genkit server |
| Contract chung | Model Dart sinh một lần |

## Cạm bẫy

- Ship prompt server khổng lồ trong bundle app.
- Trộn SDK provider lung tung thay vì plugin — mất tính di động.
- Bỏ qua trace tới khi sự cố production.
