---
title: "Swift Package Manager is the iOS/macOS default — leave CocoaPods behind"
description: "From Flutter 3.44, SwiftPM replaces CocoaPods for new iOS and macOS builds. How the CLI migrates you, what plugin authors must ship, and how to opt out briefly."
seoDescription: "Flutter Swift Package Manager default 3.44: migrate from CocoaPods, plugin Package.swift FlutterFramework, and temporary opt-out flag."
keywords:
  - flutter swift package manager
  - flutter cocoa pods migration
  - swiftpm flutter default
  - flutter plugin Package.swift
  - disable swift package manager flutter
tags: ["Flutter", "iOS", "macOS", "SwiftPM", "CocoaPods"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "SwiftPM for app developers"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers"
  - name: "SwiftPM for plugin authors"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-plugin-authors"
  - name: "Goodbye CocoaPods post"
    url: "https://blog.flutter.dev/saying-goodbye-to-cocoapods-swift-package-manager-is-soon-the-default-in-flutter-645a92714a57"
related:
  - slug: "flutter-uiscene-ios-lifecycle"
    title: "UIScene iOS Lifecycle"
  - slug: "flutter-content-sized-views"
    title: "Content-sized Views"
category: "Deep Dive"
topic: "Platform"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📦"
draft: false
---

CocoaPods is in maintenance mode. Flutter 3.44 makes **Swift Package Manager the default** for iOS and macOS dependency resolution. The CLI migrates the Xcode project on the next `flutter run` / `flutter build`.

![Diagram: Swift Package Manager Default](/blog/images/flutter-swift-package-manager-default.svg)


## What app developers see

- No Ruby/CocoaPods install required for the happy path.
- Add-to-App gains `flutter build swift-package` to emit a Swift Package for native hosts.
- Plugins that still require CocoaPods trigger a CLI warning and temporary fallback.

## What plugin authors must ship

If you maintain an iOS/macOS plugin:

1. Add a `Package.swift`.
2. Depend on `FlutterFramework` if you migrated in the 2024 pilot.
3. Raise the minimum Flutter constraint to **3.44** when you switch.

Unmigrated plugins score lower on pub.dev and will eventually stop resolving.

## Temporary opt-out

```yaml
# pubspec.yaml
flutter:
  # temporary escape hatch — file a bug if you need it
  enable-swift-package-manager: false
```

Or pass `--no-enable-swift-package-manager` on the command line. Opt-outs will be removed; open an issue with your Xcode project if SwiftPM breaks a real integration.

## Checklist before you delete Podfile

- [ ] `flutter clean` then a full iOS build
- [ ] CI runners no longer install CocoaPods for this app
- [ ] Every plugin in the tree resolves under SwiftPM (or is replaced)
- [ ] Code signing and entitlements still apply
