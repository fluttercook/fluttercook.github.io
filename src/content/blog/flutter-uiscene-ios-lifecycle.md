---
title: "UIScene lifecycle: the iOS 27 launch requirement Flutter apps must meet"
description: "Xcode 27 / iOS 27 require UIScene. Flutter migrates most apps automatically; custom AppDelegate paths need a manual pass."
seoDescription: "Flutter UIScene lifecycle iOS 27 Xcode 27, AppDelegate migration, min iOS 15 Flutter 3.47, launch failure without UIScene."
keywords:
  - flutter uiscene
  - flutter ios 27 lifecycle
  - flutter appdelegate migration
  - uiscenedelegate flutter
  - flutter min ios 15
tags: ["Flutter", "iOS", "UIScene", "Xcode"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "UIScene lifecycle guide"
    url: "https://docs.flutter.dev/release/breaking-changes/uiscene-lifecycle-ios"
  - name: "UISceneDelegate migration"
    url: "https://docs.flutter.dev/release/breaking-changes/uiscenedelegate"
related:
  - slug: "flutter-swift-package-manager-default"
    title: "Swift Package Manager Default"
  - slug: "flutter-content-sized-views"
    title: "Content-sized Views"
category: "Deep Dive"
topic: "iOS"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🍎"
draft: false
---

Apple’s scene-based lifecycle is no longer optional for apps built with the latest SDKs. **iOS 27 / Xcode 27 will fail launches** for UIKit apps that do not adopt `UIScene`.

![Diagram: UIScene iOS Lifecycle](/blog/images/flutter-uiscene-ios-lifecycle.svg)


## What Flutter 3.47 changes

- Minimums rise: **iOS 15**, **macOS 12** (from 13 / 10.15).
- The CLI migrates typical `AppDelegate` setups automatically.
- Manual work remains if you customized lifecycle hooks or use plugins that still assume the old model.

## Migration checklist

1. Update Xcode and Flutter to the supported pair.
2. Clean build and look for CLI migration output.
3. Audit plugins for UIApplicationDelegate-only APIs.
4. Test cold start, background→foreground, and permission dialogs.

## Pitfalls

- “It launches in the simulator” is not enough — test a device with the new SDK.
- Deep links and notification handlers often live in lifecycle code; retest them.
