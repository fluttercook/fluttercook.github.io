---
title: 'image_picker: a small API over messy media sources'
description: 'Showcase image_picker in a production-minded Flutter architecture: camera/gallery
  intent, lost data recovery, compression, and permissions.'
seoDescription: 'Showcase image_picker in a production-minded Flutter architecture:
  camera/gallery intent, lost data recovery, compression, and permissions.'
keywords:
- image_picker
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
- Media
sources:
- name: image_picker on pub.dev
  url: https://pub.dev/packages/image_picker
- name: Flutter image_picker package
  url: https://github.com/flutter/packages/tree/main/packages/image_picker
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# image_picker: a small API over messy media sources

`image_picker` is useful because it focuses on camera/gallery intent, lost data recovery, compression, and permissions. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
final picker = ImagePicker();
final image = await picker.pickImage(
  source: ImageSource.gallery,
  maxWidth: 2000,
  imageQuality: 85,
);
if (image != null) upload(await image.readAsBytes());
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Handle Android activity recreation with retrieveLostData and validate file size before upload.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
