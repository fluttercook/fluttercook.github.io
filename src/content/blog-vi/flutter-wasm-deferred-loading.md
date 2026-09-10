---
title: "Flutter web Wasm: deferred loading để first paint nhẹ hơn"
description: "Flutter đang tiến tới Wasm mặc định. Deferred loading cho phép tách module và bootstrap nhỏ hơn."
seoDescription: "Flutter web Wasm deferred loading, flutter build web --wasm --enable-wasm-deferred-loading, migrate package:web."
keywords:
  - flutter wasm
  - flutter deferred loading wasm
  - flutter web performance
  - dart2wasm flutter
  - package:web migration
tags: ["Flutter", "Web", "Wasm", "Performance"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Compile to WebAssembly"
    url: "https://docs.flutter.dev/platform-integration/web/wasm"
related:
  - slug: "flutter-platform-specific-assets"
    title: "Platform-specific Assets"
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
category: "Deep Dive"
topic: "Web"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🕸️"
draft: false
---

Wasm mở khóa đồ họa gần native trên web — kèm kỷ luật đóng gói mới. Flutter 3.47 thêm **deferred loading experimental** cho build Wasm để tách app lớn thành module lazy.

![Sơ đồ: Wasm Deferred Loading](/blog/images/flutter-wasm-deferred-loading.svg)


## Lệnh build

```bash
flutter build web --release --wasm
flutter build web --release --wasm --enable-wasm-deferred-loading
```

## Điều kiện tiên quyết

- Rời `dart:html` sang **`package:web`** và JS interop hiện đại.
- Update package còn giả định interop chỉ dart2js.

## Chiến lược tách module

1. Giữ login/shell ở module chính.
2. Defer màn nặng (admin, editor, map).
3. Đo *time to interactive*, không chỉ dung lượng tải.

## Cạm bẫy

- Library deferred không được bắt buộc ở frame đầu.
- UI nặng canvas/Skottie vẫn cần ngân sách asset chặt.
- Không phải tổ hợp browser/flag nào cũng giống nhau — test Chrome, Safari, Firefox.
