---
title: 'Dio: composeable networking with interceptors'
description: 'Showcase dio in a production-minded Flutter architecture: interceptors,
  cancellation, retries, and typed error mapping.'
seoDescription: 'Showcase dio in a production-minded Flutter architecture: interceptors,
  cancellation, retries, and typed error mapping.'
keywords:
- dio
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
- Networking
sources:
- name: Dio on pub.dev
  url: https://pub.dev/packages/dio
- name: Dio repository
  url: https://github.com/cfug/dio
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# Dio: composeable networking with interceptors

`dio` is useful because it focuses on interceptors, cancellation, retries, and typed error mapping. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
final dio = Dio(BaseOptions(baseUrl: apiBaseUrl));

dio.interceptors.add(InterceptorsWrapper(
  onRequest: (options, handler) {
    options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  },
  onError: (error, handler) {
    logApiFailure(error);
    handler.next(error);
  },
));
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Retries must be limited to idempotent operations or guarded by an idempotency key.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
