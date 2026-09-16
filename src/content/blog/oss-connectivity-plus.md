---
title: 'connectivity_plus: network type is not internet reachability'
description: 'Showcase connectivity_plus in a production-minded Flutter architecture:
  connectivity streams, offline UX, reachability checks, and platform nuance.'
seoDescription: 'Showcase connectivity_plus in a production-minded Flutter architecture:
  connectivity streams, offline UX, reachability checks, and platform nuance.'
keywords:
- connectivity_plus
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
- Offline
sources:
- name: connectivity_plus on pub.dev
  url: https://pub.dev/packages/connectivity_plus
- name: connectivity_plus repository
  url: https://github.com/fluttercommunity/plus_plugins/tree/main/packages/connectivity_plus
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# connectivity_plus: network type is not internet reachability

`connectivity_plus` is useful because it focuses on connectivity streams, offline UX, reachability checks, and platform nuance. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
final subscription = Connectivity().onConnectivityChanged.listen((types) {
  final hasTransport = types.any((type) =>
      type == ConnectivityResult.wifi || type == ConnectivityResult.mobile);
  banner.show(hasTransport ? 'Online' : 'Offline');
});

// Cancel subscription in dispose().
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Do not use connectivity type as proof that an API call will succeed; confirm with a request or health check.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
