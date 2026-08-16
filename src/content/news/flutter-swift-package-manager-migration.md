---
title: "Swift Package Manager is the default now — and CocoaPods has a deadline"
description: "Swift Package Manager has been on by default since Flutter 3.44, 92 of the top 100 iOS plugins have migrated, and the CocoaPods registry goes read-only on December 2, 2026."
seoDescription: "Flutter Swift Package Manager migration guide: what SwiftPM changes in your Xcode project, how to enable or disable it, plugin migration status, and the CocoaPods read-only deadline."
keywords: ["flutter swift package manager", "flutter swiftpm migration", "cocoapods read only 2026", "flutter ios plugin spm", "FlutterGeneratedPluginSwiftPackage", "flutter ios build"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "📦"
tags: ["Flutter 3.47", "Flutter", "iOS", "Swift Package Manager", "Plugins"]
sources:
  - name: "Swift Package Manager for app developers — flutter.dev docs"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers"
  - name: "Swift Package Manager for plugin authors — flutter.dev docs"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-plugin-authors"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter release notes"
    url: "https://docs.flutter.dev/release/release-notes"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Most Flutter developers have already migrated to Swift Package Manager without noticing. It has been enabled by default since **Flutter 3.44**, and the tooling adds the integration to your Xcode project the first time you build after upgrading. The reason to pay attention now is a date: the **CocoaPods registry becomes read-only on December 2, 2026**. After that, opting out stops being a supported escape hatch.

Flutter 3.47 reports that **92 of the top 100 iOS plugins have migrated to Swift Package Manager**. The long tail is what will bite you, not the head of the distribution.

## What actually changes in your project

When SwiftPM is enabled and you build, Flutter modifies your Xcode project in three ways:

1. Adds **`FlutterGeneratedPluginSwiftPackage`** as a package dependency of the `Runner` target.
2. Adds a **Run Prepare Flutter Framework Script** pre-action to your build scheme.
3. Resolves and downloads the Swift packages your Flutter plugins depend on.

That generated package lives at `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`. The word *ephemeral* is doing real work there — it is regenerated, not hand-edited, and it does not belong in version control.

Crucially, **CocoaPods does not disappear**. Flutter falls back to CocoaPods automatically for any dependency that does not yet support SwiftPM, so a mixed project is the normal state during the transition, not a misconfiguration.

## Turning it on, off, and per-project

If a previous version of your project disabled it, re-enable globally:

```bash
flutter config --enable-swift-package-manager
```

To disable globally:

```bash
flutter config --no-enable-swift-package-manager
```

To disable for one project only, in `pubspec.yaml`:

```yaml
flutter:
  config:
    enable-swift-package-manager: false
```

The per-project switch is the useful one. If exactly one app in your organisation depends on an unmigrated internal plugin, pin that app and leave everything else on the default.

## Removing the integration entirely

If you need a clean rollback — for a bisect, or because a build broke and you want a known-good baseline:

1. Turn SwiftPM off using one of the switches above.
2. Run `flutter clean`.
3. Open your Xcode workspace.
4. Remove `FlutterGeneratedPluginSwiftPackage` from **Package Dependencies**.
5. Remove it from **Frameworks, Libraries, and Embedded Content**.
6. Delete the **Run Prepare Flutter Framework Script** pre-action.

Steps 3 through 6 are the ones people forget, and a half-removed integration produces confusing link errors.

## When automatic migration fails

The tooling occasionally cannot patch an Xcode project — heavily customised schemes and hand-edited `project.pbxproj` files are the usual culprits. The manual path:

**Add the package dependency.** Open `ios/Runner.xcworkspace`, go to **Package Dependencies**, click add, choose **Add Local…**, and select `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`. Confirm it is attached to the `Runner` target and appears under **Frameworks, Libraries, and Embedded Content**.

**Add the pre-action.** Go to **Product → Scheme → Edit Scheme**, expand **Build**, click **Pre-actions**, add a run script action titled `Run Prepare Flutter Framework Script`, set **Provide build settings from** to `Runner`, and use:

```bash
"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh" prepare
```

Then run the app and confirm the pre-action executes. If automatic migration failed, file a bug with your `project.pbxproj` and `.xcscheme` attached — that is the data the Flutter team needs and rarely gets.

## The deployment target trap

This is the most common real-world failure, and it is not obvious from the error message. A SwiftPM plugin can declare a **higher minimum OS version** than your app. When it does, the build fails until you raise **Minimum Deployments** in Xcode and regenerate the config:

```bash
flutter build ios --config-only
flutter build macos --config-only
```

Flutter 3.47 already raised the floors — **iOS 13 → 15** and **macOS 10.15 → 12** — so if you are upgrading from an older SDK you may clear this hurdle by accident.

| Concern | CocoaPods | Swift Package Manager |
| --- | --- | --- |
| Dependency manifest | `Podfile` / `Podfile.lock` | Generated `Package.swift` |
| Toolchain | Ruby gem, installed separately | Built into Xcode |
| Integration point | `.xcworkspace` from `pod install` | Package dependency + scheme pre-action |
| Registry status | **Read-only from Dec 2, 2026** | Actively developed |
| Flutter default | Fallback only | **Default since 3.44** |

## Your migration checklist

1. **Confirm you are on the default.** Run `flutter config` and check that `enable-swift-package-manager` is not disabled anywhere, including `pubspec.yaml`.
2. **Build a clean iOS and macOS target** and watch for the pre-action running.
3. **Audit your plugin list.** For each iOS plugin, check whether its repository ships a `Package.swift`. The ones that do not are your December risk.
4. **Migrate your own plugins first** — internal plugins are the ones nobody else will fix for you. Follow the plugin-author guide and ship a `Package.swift` alongside the existing podspec.
5. **File or upvote issues** on the unmigrated third-party plugins you depend on, now rather than in November.
6. **Raise deployment targets** to iOS 15 / macOS 12 and regenerate with `--config-only`.
7. **Do not add `ios/Flutter/ephemeral/` to version control.**

## The bottom line

SwiftPM is not a feature you need to adopt — you almost certainly already have. What you need to do is inventory the plugins that have not, because December 2, 2026 turns "we'll handle it later" into a build break. The head of the ecosystem is done: 92 of the top 100 plugins have moved. Spend an hour on the tail — your internal plugins and the three obscure packages nobody has looked at since 2024 — and this transition costs you nothing at all.
