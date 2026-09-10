---
title: "Firebase AI Logic trong Flutter: Gemini không cần backend riêng"
description: "Gọi Gemini từ Flutter qua firebase_ai, giữ prompt trên server, học pattern production như MacroFactor."
seoDescription: "Flutter Firebase AI Logic package firebase_ai, Server Prompt Templates Gemini client-side, feature AI an toàn trong app Flutter."
keywords:
  - flutter firebase ai logic
  - firebase_ai gemini
  - flutter gemini api
  - server prompt templates firebase
  - flutter multimodal ai
tags: ["Flutter", "Firebase", "Gemini", "AI"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "Firebase AI Logic"
    url: "https://firebase.google.com/docs/ai-logic/get-started?platform=flutter"
  - name: "MacroFactor case study"
    url: "https://cloud.google.com/customers/macrofactor"
related:
  - slug: "flutter-genkit-dart"
    title: "Genkit Dart"
  - slug: "flutter-gemma-litert-ondevice"
    title: "On-device Gemma"
category: "Deep Dive"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔥"
draft: false
---

Bạn không phải lúc nào cũng cần proxy Node/Go để gọi LLM từ Flutter. **Firebase AI Logic** (`firebase_ai`) cung cấp client typed cho Gemini, sẵn Auth, App Check và quota.

![Sơ đồ: Firebase AI Logic](/blog/images/flutter-firebase-ai-logic.svg)


## Vì sao team chọn

- Gọi multimodal phía client (ảnh → log dinh dưỡng có cấu trúc) không phải dựng infra.
- **Server Prompt Templates** giữ system prompt và tool definition ngoài binary.
- Cùng project Firebase bạn đã dùng cho Crashlytics/Auth.

## Dáng client tối thiểu

```dart
import 'package:firebase_ai/firebase_ai.dart';

final model = FirebaseAI.googleAI().generativeModel(model: 'gemini-2.5-flash');
final response = await model.generateContent([
  Content.text('Mô tả screenshot UI này cho bug report.'),
  Content.data('image/png', pngBytes),
]);
print(response.text);
```

(API surface thay đổi theo version — ghim package và đọc docs hiện tại.)

## Checklist bảo mật

1. Bật App Check.
2. Yêu cầu Auth cho model đắt.
3. Server template cho prompt chứa business rule.
4. Client không giữ provider key dài hạn.

## Khi nào dùng Genkit

Nếu flow, tool và observability ở server, ưu tiên Genkit Dart. Firebase AI Logic mạnh khi *trải nghiệm sản phẩm* ở trên device và nhạy latency.
