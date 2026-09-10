---
title: "Gemma on-device trong Flutter: flutter_gemma và LiteRT-LM"
description: "Chạy model Gemma on-device trên cả sáu nền tảng Flutter với tăng tốc GPU/NPU qua LiteRT-LM."
seoDescription: "Flutter flutter_gemma LiteRT-LM Gemma 4 on-device, suy luận GPU NPU Android iOS web desktop, AI privacy Flutter."
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

AI cloud không phải đường duy nhất. **Model on-device** giữ dữ liệu cục bộ, chạy offline và cắt cost theo request. Câu chuyện Flutter ở đây là `flutter_gemma` cộng runtime **LiteRT-LM** của Google.

![Sơ đồ: On-device Gemma](/blog/images/flutter-gemma-litert-ondevice.svg)


## Vì sao LiteRT-LM quan trọng

Nó trừu tượng hóa khác biệt phần cứng và nhắm tăng tốc GPU/NPU trên Android, iOS, Web, Windows, Linux, macOS — đúng sáu đích Flutter ship.

## Pattern sản phẩm hiệu quả

1. **Trợ giúp thị giác** — frame camera → mô tả ngắn có cấu trúc (kiểu Gemma Vision).
2. **Huấn luyện task** — kế hoạch nhiều bước local, không round trip.
3. **Dictation/note nhạy privacy** — text không rời máy.

## Checklist kỹ thuật

- UX tải model (vài trăm MB) có resume.
- Ngân sách thermal/battery trên phone tầm trung.
- Path fallback khi thiếu NPU/driver.
- Thông điệp rõ: xử lý nằm trên máy.

## Cạm bẫy

- Đừng chặn UI isolate khi sinh token.
- Đánh đổi quantization: đo chất lượng trên *task của bạn*, không chỉ benchmark.
