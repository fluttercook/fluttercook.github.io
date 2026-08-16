---
title: "Migrating to material_ui and cupertino_ui: the design system leaves the SDK"
description: "Flutter 3.47 ships Material and Cupertino as standalone 1.0 packages. Here is what changes in your imports, how the automated fix works, and how to survive the mixed-dependency phase."
seoDescription: "Flutter material_ui and cupertino_ui migration guide: dart fix --apply --code=migrate_design_widgets, MaterialUiCompatibilityBridge, localizations changes, and the November deprecation."
keywords: ["material_ui package flutter", "cupertino_ui package", "migrate_design_widgets", "MaterialUiCompatibilityBridge", "flutter 3.47 migration", "flutter design system package"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🧱"
tags: ["Flutter 3.47", "Flutter", "Material", "Cupertino", "Migration"]
sources:
  - name: "material_ui 1.0.0 on pub.dev"
    url: "https://pub.dev/packages/material_ui"
  - name: "cupertino_ui on pub.dev"
    url: "https://pub.dev/packages/cupertino_ui"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter Q2 2026 survey results"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

For nine years, `import 'package:flutter/material.dart';` has been the first line of almost every Flutter file ever written. Flutter 3.47 begins ending that. **`material_ui` and `cupertino_ui` are now standalone packages on pub.dev**, both at 1.0, both published by the verified `flutter.dev` publisher. The copies inside the SDK still work — and are **scheduled for formal deprecation in the November stable release**.

This is a bigger change than the diff suggests, so it is worth understanding the reasoning before you run the migration tool.

## Why decouple at all

The Q2 2026 survey answers this more clearly than any blog post. Across every focus area, satisfaction is high: **Dart at 92%, Android at 91%, the core framework at 90%**. One number breaks the pattern — **Cupertino widgets at 61%, down 6 points**, the lowest-rated area in the survey.

The structural cause is release cadence. Bound to the SDK, Cupertino could only ship fixes on the quarterly stable train. Apple ships design changes whenever it likes. A design system that can only respond four times a year will always trail the platform it is imitating.

Unbundled, `material_ui` and `cupertino_ui` can release weekly. That is the whole strategy: not a refactor for elegance, but a fix for a cadence mismatch that shows up directly in developer satisfaction.

The second benefit is version independence. Today, upgrading Flutter means accepting every widget change at the same time. Once the design system is a normal dependency, you can pin it:

```yaml
dependencies:
  flutter:
    sdk: flutter
  material_ui: ^1.0.0
  cupertino_ui: ^1.0.0
```

Upgrade the framework for an engine fix without inheriting a `ListTile` layout change in the same afternoon.

## What actually changes in your code

The import path, mostly:

| Before | After |
| --- | --- |
| `package:flutter/material.dart` | `package:material_ui/material_ui.dart` |
| `package:flutter/cupertino.dart` | `package:cupertino_ui/cupertino_ui.dart` |
| `GlobalMaterialLocalizations` from `flutter_localizations` | the version provided by `material_ui` |

Widget APIs are unchanged. This is a packaging move, not an API break — which is exactly why it can be automated.

## Running the migration

Add the packages, then let `dart fix` rewrite the imports:

```bash
flutter pub add material_ui cupertino_ui
dart fix --apply --code=migrate_design_widgets
```

The `migrate_design_widgets` fix rewrites imports from the old framework location to the new packages across your project. Review the diff — it should be almost entirely import lines. Anything else is worth a second look.

The one thing the fix does not fully handle for you is **localizations**. If you use `GlobalMaterialLocalizations`, move to the version `material_ui` provides rather than the one from `flutter_localizations`. Mixing them produces confusing "no localizations found" failures at runtime rather than compile time, so grep for it explicitly:

```bash
grep -rn "GlobalMaterialLocalizations" lib/
```

## Surviving the mixed-dependency phase

Here is the realistic problem. You migrate your app in twenty minutes. Then you discover that four of your dependencies still import `package:flutter/material.dart`, and their widget trees and yours now come from different libraries.

That is what **`MaterialUiCompatibilityBridge`** exists for. Wrap your app — or just the subtree containing the legacy widgets — and the old and new trees interoperate:

```dart
import 'package:material_ui/material_ui.dart';

void main() {
  runApp(
    MaterialUiCompatibilityBridge(
      child: const MyApp(),
    ),
  );
}
```

Treat the bridge as scaffolding with a demolition date, not architecture. Every wrapped subtree is a dependency you are waiting on. Keep a list.

## The deprecation timeline

Nothing breaks today. The sequence to plan around:

- **Now (3.47):** both paths work. Packages are at 1.0. Migration is opt-in.
- **November stable:** the SDK's Material and Cupertino libraries are **formally deprecated**. Expect analyzer warnings on every unmigrated import.
- **Later:** deprecated APIs eventually get removed. No date has been announced, and you should not wait for one.

The honest cost estimate is an afternoon for an app, longer for a plugin ecosystem you do not control.

## If you ship a package

Package authors carry the real burden here, because your choice propagates to every consumer. A few rules of thumb:

- **Do not migrate and immediately publish a breaking major** if your package only touches a handful of widgets — you will fragment your users across two worlds for no benefit.
- **Do migrate promptly** if your package *is* a UI library. Your users cannot finish their migration until you finish yours.
- **Widen your constraints** rather than pinning tightly, so consumers can pick up design-system fixes without waiting for your release.

## Your migration checklist

1. **Upgrade to Flutter 3.47** and confirm a clean build before changing anything.
2. **Run `flutter pub add material_ui cupertino_ui`.**
3. **Run `dart fix --apply --code=migrate_design_widgets`** and read the diff.
4. **Search for `GlobalMaterialLocalizations`** and switch it to the `material_ui` version.
5. **Build and run** on at least one iOS and one Android target. Watch for theme and localization regressions specifically.
6. **Identify dependencies still on the SDK libraries.** File issues on them today.
7. **Wrap with `MaterialUiCompatibilityBridge`** only where you must, and record why.
8. **Set a calendar reminder for October** to re-check the list before the November deprecation lands.

## The bottom line

This migration is mechanical, and the tooling does most of it. The part that needs judgement is the dependency graph: your app is easy, your dependencies are not, and `MaterialUiCompatibilityBridge` is a bridge rather than a destination. Do the mechanical part now while it is optional and the analyzer is quiet — it is a much less pleasant task in November, with warnings on every file and a deprecation clock running.
