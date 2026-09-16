---
title: 'just_audio: controllable audio with streams'
description: 'Showcase just_audio in a production-minded Flutter architecture: queues,
  position streams, playlists, speed, and background integration.'
seoDescription: 'Showcase just_audio in a production-minded Flutter architecture:
  queues, position streams, playlists, speed, and background integration.'
keywords:
- just_audio
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
- name: just_audio on pub.dev
  url: https://pub.dev/packages/just_audio
- name: just_audio repository
  url: https://github.com/ryanheise/just_audio
related:
- slug: flutter-state-management-decision-guide
  title: State management decision guide
- slug: flutter-testing-widget-golden-integration
  title: Widget and golden testing
draft: false
---

# just_audio: controllable audio with streams

`just_audio` is useful because it focuses on queues, position streams, playlists, speed, and background integration. The important engineering move is to place the package behind a clear boundary, so your Flutter UI depends on a stable capability rather than a vendor-shaped API.

![FlutterCook open-source showcase](/blog/images/fluttercook-editorial-2026.svg)

## What the library should own

- Keep package calls inside a named adapter or feature boundary.
- Make lifecycle, errors, and loading state part of a testable contract.
- Expose only the capability the app needs; hide implementation details from the whole tree.

## A focused starting point

```dart
final player = AudioPlayer();
await player.setAudioSource(
  ConcatenatingAudioSource(children: [
    AudioSource.uri(Uri.parse(trackUrl)),
  ]),
);
player.play();
player.positionStream.listen(updateProgress);
```

## Production checklist

1. Read the README and changelog for the exact version you pin.
2. Add one test for lifecycle, failure, and app background/foreground behavior.
3. Verify every platform your product supports, not only the developer machine.
4. Record ownership, upgrade cadence, and rollback notes in the repository.

## Common pitfall

Own player lifecycle and audio focus explicitly; a disposed screen must not keep the stream alive.

## Takeaway

A good open-source library does not replace architecture. It makes one difficult boundary clearer, observable, and easier to replace.
