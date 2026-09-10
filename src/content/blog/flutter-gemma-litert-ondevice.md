---
title: "On-device Gemma in Flutter: flutter_gemma and LiteRT-LM"
description: "Run Gemma models on-device across Flutter’s six platforms with GPU/NPU acceleration via LiteRT-LM."
seoDescription: "Flutter flutter_gemma LiteRT-LM on-device Gemma 4, GPU NPU inference Android iOS web desktop, privacy AI Flutter."
keywords:
  - flutter_gemma
  - litert-lm flutter
  - on device ai flutter
  - gemma 4 flutter
  - flutter local llm
tags: ["Flutter", "AI", "Gemma", "OnDevice"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "flutter_gemma package"
    url: "https://pub.dev/packages/flutter_gemma"
  - name: "LiteRT-LM"
    url: "https://ai.google.dev/edge/litert-lm/overview"
related:
  - slug: "flutter-firebase-ai-logic"
    title: "Firebase AI Logic"
  - slug: "flutter-genkit-dart"
    title: "Genkit Dart"
category: "Deep Dive"
topic: "AI"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📱"
draft: false
---

Cloud AI is not the only path. **On-device models** keep data local, work offline, and cut per-request cost. Flutter’s story here is `flutter_gemma` plus Google’s **LiteRT-LM** inference runtime.

![Diagram: On-device Gemma](/blog/images/flutter-gemma-litert-ondevice.svg)


## Why LiteRT-LM matters

It abstracts hardware differences and aims at GPU/NPU acceleration across Android, iOS, Web, Windows, Linux, and macOS — the same six targets Flutter ships.

## Product patterns that work

1. **Vision assist** — camera frames → short structured descriptions (Gemma Vision style).
2. **Task coaching** — local multi-step planning without a round trip.
3. **Privacy-sensitive dictation/notes** — text never leaves the device.

## Engineering checklist

- Model download UX (multi-hundred MB) with resume.
- Thermal/battery budgets on mid-tier phones.
- Fallback path when NPU/driver is missing.
- Clear user messaging that processing is local.

## Pitfalls

- Do not block the UI isolate on token generation.
- Quantization tradeoffs: measure quality on *your* tasks, not benchmarks alone.
