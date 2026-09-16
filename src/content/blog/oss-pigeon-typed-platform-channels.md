---
title: 'Pigeon: typed platform channels generated from one schema'
description: 'Showcase pigeon in a production-minded Flutter architecture: Dart/native
  codegen, API contracts, task queues, and versioning.'
seoDescription: 'Showcase pigeon in a production-minded Flutter architecture: Dart/native
  codegen, API contracts, task queues, and versioning.'
keywords:
- pigeon
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
- Platform
sources:
- name: pigeon on pub.dev
  url: https://pub.dev/packages/pigeon
- name: Pigeon repository
  url: https://github.com/flutter/packages/tree/main/packages/pigeon
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Pigeon: typed platform channels generated from one schema

`pigeon` is useful because it focuses on Dart/native codegen, API contracts, task queues, and versioning. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
@HostApi()
abstract class SecureBiometrics {
  bool isAvailable();
  @async
  bool authenticate(String reason);
}

// dart run pigeon --input pigeons/biometrics.dart
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Version the schema like an API; adding a breaking method can desync released native binaries.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
