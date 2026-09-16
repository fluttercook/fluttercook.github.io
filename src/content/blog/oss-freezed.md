---
title: 'Freezed: safer immutable models and unions'
description: 'Showcase freezed in a production-minded Flutter architecture: immutable
  data classes, JSON unions, copyWith, and exhaustive UI states.'
seoDescription: 'Showcase freezed in a production-minded Flutter architecture: immutable
  data classes, JSON unions, copyWith, and exhaustive UI states.'
keywords:
- freezed
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
- Codegen
sources:
- name: freezed on pub.dev
  url: https://pub.dev/packages/freezed
- name: Freezed repository
  url: https://github.com/rrousselGit/freezed
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Freezed: safer immutable models and unions

`freezed` is useful because it focuses on immutable data classes, JSON unions, copyWith, and exhaustive UI states. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
@freezed
sealed class LoadState<T> with _$LoadState<T> {
  const factory LoadState.idle() = Idle<T>;
  const factory LoadState.loading() = Loading<T>;
  const factory LoadState.data(T value) = Data<T>;
  const factory LoadState.failure(Object error) = Failure<T>;
}
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Commit generated files only when your repository policy requires it; otherwise make code generation part of CI.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
