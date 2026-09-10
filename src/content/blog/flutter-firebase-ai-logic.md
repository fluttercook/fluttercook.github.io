---
title: "Firebase AI Logic in Flutter: Gemini without a custom backend"
description: "Call Gemini from Flutter via firebase_ai, keep prompts on the server, and learn from production patterns like MacroFactor."
seoDescription: "Flutter Firebase AI Logic firebase_ai package, Server Prompt Templates Gemini client-side, secure AI features in Flutter apps."
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

You do not always need a Node/Go proxy to call an LLM from a Flutter app. **Firebase AI Logic** (`firebase_ai`) gives you a typed client for Gemini with Firebase Auth, App Check, and quota controls already in the path.

![Diagram: Firebase AI Logic](/blog/images/flutter-firebase-ai-logic.svg)


## Why teams pick it

- Client-side multimodal calls (photos → structured nutrition logs, for example) without standing up infra.
- **Server Prompt Templates** keep system prompts and tool definitions out of the binary.
- Works with the same Firebase project you already use for Crashlytics/Auth.

## Minimal client shape

```dart
import 'package:firebase_ai/firebase_ai.dart';

final model = FirebaseAI.googleAI().generativeModel(model: 'gemini-2.5-flash');
final response = await model.generateContent([
  Content.text('Describe this UI screenshot for a bug report.'),
  Content.data('image/png', pngBytes),
]);
print(response.text);
```

(Exact API surface evolves — pin the package version and read the current docs.)

## Security checklist

1. App Check on.
2. Auth required for expensive models.
3. Server templates for prompts that encode business rules.
4. Client never holds long-lived provider keys.

## When to use Genkit instead

If flows, tools, and observability live server-side, prefer Genkit Dart. Firebase AI Logic shines when the *product* interaction is on-device and latency-sensitive.
