---
title: 'go_router: URL-first navigation for Flutter'
description: 'Showcase go_router in a production-minded Flutter architecture: declarative
  routing, deep links, redirects, and ShellRoute.'
seoDescription: 'Showcase go_router in a production-minded Flutter architecture: declarative
  routing, deep links, redirects, and ShellRoute.'
keywords:
- go_router
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
- Routing
sources:
- name: go_router on pub.dev
  url: https://pub.dev/packages/go_router
- name: go_router repository
  url: https://github.com/flutter/packages/tree/main/packages/go_router
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# go_router: URL-first navigation for Flutter

`go_router` is useful because it focuses on declarative routing, deep links, redirects, and ShellRoute. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
final router = GoRouter(
  redirect: (context, state) => isSignedIn || state.uri.path == '/login'
      ? null
      : '/login',
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomePage()),
    GoRoute(path: '/orders/:id', builder: (_, state) =>
        OrderPage(id: state.pathParameters['id']!)),
  ],
);
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Do not hide auth redirects inside widgets; they belong at the route boundary.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
