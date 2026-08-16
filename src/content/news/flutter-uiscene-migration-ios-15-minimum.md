---
title: "The UIScene migration: the iOS change that will crash unmigrated Flutter apps"
description: "Apple is requiring the UIScene lifecycle, and Flutter 3.47 raises the iOS floor to 15. Here is the full migration — Info.plist, AppDelegate, plugins, and the APIs that stop working."
seoDescription: "Flutter UIScene migration guide: UIApplicationSceneManifest, FlutterSceneDelegate, didInitializeImplicitFlutterEngine, plugin scene lifecycle callbacks, and iOS 15 / macOS 12 minimums."
keywords: ["flutter uiscene migration", "UISceneDelegate flutter", "FlutterSceneDelegate", "didInitializeImplicitFlutterEngine", "flutter ios 15 minimum", "flutter ios 27 requirement"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🍎"
tags: ["Flutter 3.47", "Flutter", "iOS", "Migration", "UIScene"]
sources:
  - name: "UISceneDelegate adoption — Flutter breaking changes"
    url: "https://docs.flutter.dev/release/breaking-changes/uiscenedelegate"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Flutter release notes"
    url: "https://docs.flutter.dev/release/release-notes"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Most Flutter migrations are optional until they are annoying. This one is different: once Apple enforces the requirement, **apps that have not adopted the UIScene lifecycle will crash on startup**. Not degrade. Crash.

Apple requires UIKit apps built with the latest SDK to use the UIScene lifecycle starting in the release following iOS 26. Apple has not announced the exact enforcement date. Flutter has supported the migration since **3.38**, and 3.47 makes the surrounding platform changes concrete by raising the floors: **iOS 13 → 15** and **macOS 10.15 → 12**, to support Xcode 27.

## What UIScene actually changes

The conceptual shift is a split of responsibilities that used to live in one object:

- **`AppDelegate`** now handles process events and overall application lifecycle
- **`UISceneDelegate`** handles UI lifecycle — foreground, background, active, resign

Two consequences follow, and both break code:

1. **Plugin registration moves.** Register in `didInitializeImplicitFlutterEngine`, not `application:didFinishLaunchingWithOptions:`.
2. **Launch options become `nil`** in `application:didFinishLaunchingWithOptions:` after migration. They are delivered to `scene:willConnectToSession:options:` instead.

That second one is the silent killer. Deep links, push notification payloads, and shortcut items that arrived through launch options simply stop arriving, with no compile error.

## The good news: it is often automatic

As of **Flutter 3.41**, if your `AppDelegate` has not been customised, the Flutter CLI migrates your app automatically when you run `flutter run` or `flutter build ios`. A large fraction of apps are already done and did not notice.

You have work to do if you customised `AppDelegate`, ship an add-to-app integration, or maintain a plugin.

## Info.plist

The migration adds an Application Scene Manifest:

```xml
<key>UIApplicationSceneManifest</key>
<dict>
  <key>UIApplicationSupportsMultipleScenes</key>
  <false/>
  <key>UISceneConfigurations</key>
  <dict>
    <key>UIWindowSceneSessionRoleApplication</key>
    <array>
      <dict>
        <key>UISceneClassName</key>
        <string>UIWindowScene</string>
        <key>UISceneDelegateClassName</key>
        <string>FlutterSceneDelegate</string>
        <key>UISceneConfigurationName</key>
        <string>flutter</string>
        <key>UISceneStoryboardFile</key>
        <string>Main</string>
      </dict>
    </array>
  </dict>
</dict>
```

A useful debugging trick: prefix `UIApplicationSceneManifest` with an underscore to temporarily disable UIScene support, and remove the underscore to re-enable. That gives you a fast A/B when something breaks.

## AppDelegate

Move plugin registration out of `didFinishLaunchingWithOptions` and into the new delegate callback:

```swift
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // GeneratedPluginRegistrant no longer belongs here
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)

    let batteryChannel = FlutterMethodChannel(
      name: "samples.flutter.dev/battery",
      binaryMessenger: engineBridge.applicationRegistrar.messenger()
    )
  }
}
```

Method channels and platform view factories both need the messenger from `engineBridge.applicationRegistrar`, not the old application-level one.

For add-to-app, add a scene delegate — usually a one-liner:

```swift
import UIKit
import Flutter

class SceneDelegate: FlutterSceneDelegate {}
```

If your host app cannot subclass `FlutterSceneDelegate`, implement `FlutterSceneLifeCycleProvider` and forward each scene callback to a `FlutterPluginSceneLifeCycleDelegate` instance.

## If you maintain a plugin

Plugin authors carry the heaviest load, because every app depending on you inherits your migration state.

Bump your constraints, then adopt the protocol and register for scene callbacks:

```yaml
environment:
  sdk: ^3.10.0
  flutter: ">=3.38.0"
```

```swift
public final class MyPlugin: NSObject, FlutterPlugin, FlutterSceneLifeCycleDelegate {
  public static func register(with registrar: FlutterPluginRegistrar) {
    registrar.addApplicationDelegate(instance)
    registrar.addSceneDelegate(instance)
  }
}
```

Then map your old callbacks:

| AppDelegate method | Scene delegate equivalent |
| --- | --- |
| `applicationDidBecomeActive` | `sceneDidBecomeActive` |
| `applicationWillResignActive` | `sceneWillResignActive` |
| `applicationWillEnterForeground` | `sceneWillEnterForeground` |
| `applicationDidEnterBackground` | `sceneDidEnterBackground` |
| `application:openURL:options:` | `scene:openURLContexts:` |
| `application:continueUserActivity:` | `scene:continueUserActivity:` |
| `application:didFinishLaunchingWithOptions:` | `scene:willConnectToSession:options:` |

## The APIs that stop working

A set of long-standing UIKit singletons are deprecated under the scene model. Each has a scene-scoped replacement:

| Deprecated | Replacement |
| --- | --- |
| `UIScreen.main` | `UIWindowScene.screen` |
| `UIApplication.shared.delegate.window` | `registrar.viewController.view.window` |
| `UIApplication.shared.keyWindow` | `UIWindowScene.keyWindow` (iOS 15+) |
| `UIApplication.shared.windows` | `UIWindowScene.windows` |

Note that `UIWindowScene.keyWindow` requires iOS 15 — which is exactly the floor Flutter 3.47 just raised you to. The two changes are related, not coincidental.

## The genuinely hard case: early initialisation

Some Apple APIs must be configured before `application:didFinishLaunchingWithOptions:` returns — `BGTaskScheduler`, `UNUserNotificationCenterDelegate`, `HKHealthStore`. Under the scene model, plugin registration happens later than that.

There is no way for a plugin to solve this alone. The documented pattern is for the plugin to expose a public method that the app developer calls from their own `AppDelegate`:

```swift
class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    BGTaskPlugin.shared.registerBackgroundHandler(identifier: "com.example.task")
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

If you use background tasks, health data, or notification delegates, check your plugin's docs for exactly this pattern. It is the migration step most likely to be missed and least likely to be caught by a test.

## Your migration checklist

1. **Build on 3.47** and let the automatic migration run if your `AppDelegate` is stock.
2. **Add the `UIApplicationSceneManifest`** to `Info.plist` if it is not there.
3. **Move `GeneratedPluginRegistrant`** into `didInitializeImplicitFlutterEngine`, along with method channels and platform view factories.
4. **Re-test every entry point**: deep links, universal links, push notification taps, home-screen quick actions. Launch options are `nil` now.
5. **Grep for the deprecated singletons** — `UIScreen.main`, `keyWindow`, `UIApplication.shared.windows` — in your code and your plugins.
6. **Raise deployment targets** to iOS 15 and macOS 12, then run `flutter build ios --config-only`.
7. **Check plugins that need early init** and add the required call in your `AppDelegate`.
8. **Do not use `enable-uiscene-migration: false`** as anything other than a short-term unblock — it hides the warning, not the eventual crash.

## The bottom line

This is the one migration in Flutter 3.47 with a hard failure mode. The mechanical parts are well documented and largely automated, so most apps will pass with a rebuild. The parts that will actually bite are the untested paths: a deep link that no longer carries its payload, a plugin that registers a background task too late, a `keyWindow` call buried in a dependency. Do the rebuild today, then spend an hour opening your app from every external entry point you support. That hour is much cheaper than a launch-day crash report.
