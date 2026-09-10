---
title: "Standalone material_ui and cupertino_ui: what the 1.0 split changes"
description: "Flutter 3.47 ships opt-in standalone design packages. Here is why the split exists, how to migrate with dart fix, and how the compatibility bridge keeps mixed dependencies building."
seoDescription: "Migrate Flutter to standalone material_ui and cupertino_ui packages in 3.47: dart fix code, compatibility bridge, and weekly design releases."
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

Material and Cupertino used to be frozen inside the core SDK. That made design updates wait on the quarterly Flutter release train. In Flutter 3.47 both libraries reach **1.0 as standalone packages** on pub.dev: `material_ui` and `cupertino_ui`.

![Diagram: Standalone Material UI and Cupertino UI](/blog/images/flutter-standalone-material-ui-cupertino-ui.svg)


You still get the SDK copies this release. The packages are **opt-in**. That is deliberate — the team froze contributions in April so the migration path could be boring.

## Why the split matters in 2026

Three concrete outcomes:

1. **Weekly design releases.** Bugfixes and new components no longer wait for `flutter upgrade`.
2. **Independent upgrades.** An app pinned to an older SDK can still take the latest look and feel.
3. **Style-neutral core.** A leaner foundation for custom design systems (and for Liquid Glass / M3 Expressive-style shocks from platform vendors).

## Migrate with dart fix

```bash
flutter pub add material_ui
# if you use Cupertino:
flutter pub add cupertino_ui

dart fix --apply --code=migrate_design_widgets
```

The fix rewrites imports from `package:flutter/material.dart` / `cupertino.dart` to the standalone packages. If `pubspec.yaml` is not updated automatically (an early known bug), add the deps by hand and run `dart fix --apply` again.

## Bridge while dependencies catch up

Not every package you depend on will migrate on day one. Wrap the app:

```dart
import 'package:material_ui/material_ui.dart';

MaterialApp(
  builder: (context, child) => MaterialUiCompatibilityBridge(child: child!),
  home: const HomeScreen(),
);
```

Localization unbundles with the same move — Material/Cupertino delegates now live in the packages, and `GlobalMaterialLocalizations.delegates` includes the Cupertino and Widgets delegates.

## Pitfalls

- Treat this as a **major release** if you publish packages.
- Core SDK copies are scheduled for formal deprecation in the **November** stable.
- Run widget tests after import rewrites; theme APIs are the same, but library URIs are not.
