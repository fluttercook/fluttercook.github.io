---
title: 'Equatable: value semantics for Dart state objects'
description: 'Showcase equatable in a production-minded Flutter architecture: equality,
  props, sealed states, and predictable rebuild checks.'
seoDescription: 'Showcase equatable in a production-minded Flutter architecture: equality,
  props, sealed states, and predictable rebuild checks.'
keywords:
- equatable
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
- Dart
sources:
- name: equatable on pub.dev
  url: https://pub.dev/packages/equatable
- name: Equatable repository
  url: https://github.com/felangel/equatable
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Equatable: value semantics for Dart state objects

`equatable` is useful because it focuses on equality, props, sealed states, and predictable rebuild checks. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
class UserLoaded extends Equatable {
  const UserLoaded(this.user);
  final User user;
  @override
  List<Object?> get props => [user.id, user.updatedAt];
}
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Include every field that changes UI meaning; incomplete props create stale widgets and confusing tests.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
