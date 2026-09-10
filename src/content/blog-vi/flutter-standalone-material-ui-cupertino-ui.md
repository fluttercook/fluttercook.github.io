---
title: "material_ui và cupertino_ui độc lập: thay đổi gì ở bản 1.0"
description: "Flutter 3.47 tung package design độc lập dạng opt-in. Vì sao cần tách, cách migrate bằng dart fix, và compatibility bridge giữ dependency cũ build được."
seoDescription: "Cách migrate Flutter sang package material_ui và cupertino_ui độc lập trong 3.47: dart fix, compatibility bridge, và release design hàng tuần."
keywords:
  - flutter material_ui package
  - cupertino_ui 1.0
  - flutter decouple material
  - migrate design widgets flutter
  - MaterialUiCompatibilityBridge
  - flutter 3.47 material
tags: ["Flutter", "Material", "Cupertino", "Packages", "Migration"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "material_ui on pub.dev"
    url: "https://pub.dev/packages/material_ui"
  - name: "cupertino_ui on pub.dev"
    url: "https://pub.dev/packages/cupertino_ui"
  - name: "Tracking issue: decouple Material/Cupertino"
    url: "https://github.com/flutter/flutter/issues/172932"
related:
  - slug: "flutter-cupertino-menu-anchor"
    title: "Cupertino Menu Anchor"
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
category: "Deep Dive"
topic: "Framework"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🧱"
draft: false
---

Material và Cupertino từng bị “đóng băng” bên trong core SDK. Mọi cập nhật design phải đợi nhịp release quarterly của Flutter. Ở Flutter 3.47, cả hai thư viện đạt **1.0 dạng package độc lập** trên pub.dev: `material_ui` và `cupertino_ui`.

![Sơ đồ: Standalone Material UI and Cupertino UI](/blog/images/flutter-standalone-material-ui-cupertino-ui.svg)


Bản trong SDK vẫn còn ở release này. Package là **opt-in**. Đó là chủ đích — team đóng contribution từ tháng 4 để đường migrate nhàm chán nhất có thể.

## Vì sao cần tách trong năm 2026

1. **Release design hàng tuần.** Bugfix và component mới không còn chờ `flutter upgrade`.
2. **Upgrade độc lập.** App ghim SDK cũ vẫn update được look-and-feel mới.
3. **Core trung lập style.** Nền tảng gọn hơn cho design system riêng (và cú sốc Liquid Glass / M3 Expressive từ vendor).

## Migrate bằng dart fix

```bash
flutter pub add material_ui
# nếu dùng Cupertino:
flutter pub add cupertino_ui

dart fix --apply --code=migrate_design_widgets
```

Lệnh này rewrite import từ `package:flutter/material.dart` / `cupertino.dart` sang package mới. Nếu `pubspec.yaml` không tự đổi (bug sớm đã biết), thêm dependency thủ công rồi chạy lại `dart fix --apply`.

## Bridge khi dependency chưa kịp migrate

```dart
import 'package:material_ui/material_ui.dart';

MaterialApp(
  builder: (context, child) => MaterialUiCompatibilityBridge(child: child!),
  home: const HomeScreen(),
);
```

Localization cũng được tách — delegate Material/Cupertino giờ nằm trong package, và `GlobalMaterialLocalizations.delegates` đã gồm cả Cupertino lẫn Widgets.

## Cạm bẫy

- Coi đây là **major release** nếu bạn publish package.
- Bản trong SDK sẽ bị formal deprecation ở stable **tháng 11**.
- Chạy lại widget test sau khi rewrite import; API theme giống nhau nhưng URI thư viện thì không.
