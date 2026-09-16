---
title: 'Very Good CLI: opinionated Flutter scaffolding'
description: 'Showcase very_good_cli in a production-minded Flutter architecture:
  project templates, flavors, testing defaults, and CI conventions.'
seoDescription: 'Showcase very_good_cli in a production-minded Flutter architecture:
  project templates, flavors, testing defaults, and CI conventions.'
keywords:
- very_good_cli
- Flutter open source
- Flutter library
- Flutter tutorial
category: Open Source
topic: Flutter OSS
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-16'
emoji: 🧩
tags:
- Flutter
- OpenSource
- Tooling
sources:
- name: very_good_cli on pub.dev
  url: https://pub.dev/packages/very_good_cli
- name: Very Good CLI repository
  url: https://github.com/VeryGoodOpenSource/very_good_cli
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Very Good CLI: opinionated Flutter scaffolding

`very_good_cli` is useful because it focuses on project templates, flavors, testing defaults, and CI conventions. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
dart pub global activate very_good_cli
very_good create flutter_app my_app
cd my_app
very_good packages get
very_good test --coverage
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Adopt the conventions selectively; the generator should reduce decisions, not erase your architecture.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
