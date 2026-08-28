---
title: "adaptive_platform_ui: one widget tree, native iOS 26 and Material"
package: "adaptive_platform_ui"
repo: "berkaycatak/adaptive_platform_ui"
githubUrl: "https://github.com/berkaycatak/adaptive_platform_ui"
category: "UI/Components"
stars: 235
forks: 85
lastUpdate: "2026-07-25"
pubDev: "https://pub.dev/packages/adaptive_platform_ui"
youtube: "https://www.youtube.com/results?search_query=flutter+adaptive_platform_ui+liquid+glass"
priority: "High"
phase: "P1"
trendRank: 0
description: "adaptive_platform_ui renders real iOS 26 UIKit toolbars and tab bars with Liquid Glass on new iPhones, Cupertino on older ones and Material 3 on Android - from one widget tree."
seoDescription: "adaptive_platform_ui is a Flutter plugin with version-aware adaptive widgets: native iOS 26 UIToolbar and UITabBar with Liquid Glass, Cupertino fallback for iOS 18 and below, Material 3 on Android."
keywords:
  - adaptive_platform_ui
  - flutter liquid glass
  - ios 26 flutter
  - flutter adaptive widgets
  - cupertino material one codebase
  - flutter uitoolbar uitabbar
topics:
  - ui
  - ios
  - liquid-glass
summary:
  - "**adaptive_platform_ui** picks the right widget per platform *and per OS version* - no `Platform.isIOS` branches in your code."
  - "On iOS 26+ it embeds real UIKit `UIToolbar` and `UITabBar`, so you get Liquid Glass and native gestures rather than a recreation."
  - "Falls back to Cupertino on iOS 18 and below, and Material 3 on Android and web."
  - "**235★**, MIT, version 0.1.111 on pub.dev, Dart SDK `^3.9.2`."
related:
  - slug: liquid-glass-widgets
    title: "Beautiful Flutter animations with liquid_glass_widgets"
  - slug: forui
    title: "Build better Flutter UI with forui"
  - slug: adaptive-theme
    title: "Build better Flutter UI with adaptive_theme"
faq:
  - q: Does adaptive_platform_ui really use native iOS controls?
    a: "For the iOS 26 toolbar and tab bar, yes - it is a Flutter plugin that embeds UIKit's `UIToolbar` and `UITabBar`, which is why you get real Liquid Glass blur, the minimize behaviour and native gesture handling instead of an approximation."
  - q: What happens on iOS 18 or older?
    a: "It renders traditional Cupertino widgets. The version-aware rendering is automatic - you set `useNativeToolbar: true` and the package decides at runtime whether the device can honour it."
  - q: Do I still need to configure localization?
    a: "Yes, and this catches people out. Add `GlobalMaterialLocalizations`, `GlobalCupertinoLocalizations` and `GlobalWidgetsLocalizations` delegates to `AdaptiveApp` or date and time pickers show English regardless of the system language."
  - q: Is it production ready?
    a: "Treat it as promising rather than settled. It is MIT-licensed and actively developed, but the version number is 0.1.111 - the API is still moving, and embedding platform views has real performance and testing costs."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`adaptive_platform_ui`](https://github.com/berkaycatak/adaptive_platform_ui) gives you one widget tree that renders native iOS 26 Liquid Glass components on new iPhones, Cupertino on older ones, and Material 3 on Android. **235★**, MIT, last pushed **2026-07-25**.

## What is adaptive_platform_ui?

Flutter has always let you build a Cupertino UI and a Material UI, but never comfortably in the same app. The usual result is `Platform.isIOS ? CupertinoButton(...) : ElevatedButton(...)` scattered through the widget tree, and a Cupertino layer that lags a year or two behind whatever Apple shipped.

iOS 26 made that worse. Liquid Glass is not a colour scheme you can approximate with a `BackdropFilter`; the toolbar's blur, its minimize-on-scroll behaviour and its gesture handling come from UIKit itself.

adaptive_platform_ui takes the position that the only honest way to match it is to embed the real control. It is a Flutter *plugin*, not a pure-Dart widget library, and on iOS 26 `useNativeToolbar: true` puts an actual `UIToolbar` on screen — likewise `UITabBar` for the bottom bar, with `UIButton`, `UISegmentedControl`, `UISwitch` and `UISlider` alongside them.

Where that is not possible, it degrades: Cupertino widgets on iOS 18 and below, Material 3 on Android and web. The decision is made at runtime by the package, not by you.

## Why it matters in 2026

The value is in the *version* axis, not just the platform axis. Most adaptive packages branch on `Platform.isIOS` and stop there, which means the moment Apple ships a new design language your "adaptive" UI is adaptive to the wrong iOS.

The API is shaped around one app-level widget and a handful of adaptive components:

```dart
AdaptiveScaffold(
  appBar: AdaptiveAppBar(
    title: 'My App',
    useNativeToolbar: true,
    actions: [
      AdaptiveAppBarAction(
        onPressed: () {},
        iosSymbol: 'gear',
        icon: Icons.settings,
      ),
    ],
  ),
  bottomNavigationBar: AdaptiveBottomNavigationBar(
    items: [
      AdaptiveNavigationDestination(icon: 'house.fill', label: 'Home'),
      AdaptiveNavigationDestination(icon: 'person.fill', label: 'Profile'),
    ],
    selectedIndex: 0,
    onTap: (index) {},
  ),
  body: YourContent(),
)
```

Note `iosSymbol: 'gear'` next to `icon: Icons.settings` — you supply both, and the right one is used. `AdaptiveApp` takes separate Material and Cupertino themes, supports light/dark/system, and has an `AdaptiveApp.router()` constructor for go_router.

## Getting started

```bash
flutter pub add adaptive_platform_ui
```

The package needs Dart `^3.9.2`. Then set up localization delegates — the README flags this as the most common mistake:

```dart
import 'package:flutter_localizations/flutter_localizations.dart';

AdaptiveApp(
  localizationsDelegates: const [
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ],
  supportedLocales: const [Locale('en'), Locale('de'), Locale('tr')],
  // ...
)
```

Miss `GlobalCupertinoLocalizations` and every date and time picker shows English no matter what the device language is.

## When should you use adaptive_platform_ui?

- your app should feel genuinely native on iOS rather than "Material with rounded corners"
- you want iOS 26 Liquid Glass chrome without writing platform-channel code yourself
- you are tired of maintaining parallel Cupertino and Material widget trees
- you support a wide iOS version range and want the fallback handled for you

## Where it falls short

Embedding UIKit views has costs that a pure-Dart package does not. Platform views composite differently, they can be awkward inside scrollables and transitions, and they are effectively invisible to Flutter's widget tests — you cannot assert on a `UITabBar` from `flutter_test`. Budget for real-device verification.

Version `0.1.111` is not a stability signal. The package is young, the API surface is broad, and 85 forks against 235 stars with 44 open issues suggests a lot of people are patching things locally.

And this is an iOS-forward package. The Android side is standard Material 3 — perfectly fine, but nobody is choosing this library for what it does on Android.

## Alternatives worth comparing

- [Beautiful Flutter animations with liquid_glass_widgets](/recipes/liquid-glass-widgets/) — Liquid Glass rendered in Dart, no platform views
- [Build better Flutter UI with forui](/recipes/forui/) — one consistent design system instead of per-platform native
- [Build better Flutter UI with adaptive_theme](/recipes/adaptive-theme/) — theme switching only, if that is all you needed
- Flutter's own `Adaptive*` widgets — free, much narrower, and no iOS 26 support

## Frequently asked questions

### Does adaptive_platform_ui really use native iOS controls?

For the iOS 26 toolbar and tab bar, yes — it is a Flutter plugin that embeds UIKit's `UIToolbar` and `UITabBar`, which is why you get real Liquid Glass blur, the minimize behaviour and native gesture handling instead of an approximation.

### What happens on iOS 18 or older?

It renders traditional Cupertino widgets. The version-aware rendering is automatic — you set `useNativeToolbar: true` and the package decides at runtime whether the device can honour it.

### Do I still need to configure localization?

Yes, and this catches people out. Add `GlobalMaterialLocalizations`, `GlobalCupertinoLocalizations` and `GlobalWidgetsLocalizations` delegates to `AdaptiveApp` or date and time pickers show English regardless of the system language.

### Is it production ready?

Treat it as promising rather than settled. It is MIT-licensed and actively developed, but the version number is `0.1.111` — the API is still moving, and embedding platform views has real performance and testing costs.

## Resources & links

- **GitHub:** [berkaycatak/adaptive_platform_ui](https://github.com/berkaycatak/adaptive_platform_ui)
- **pub.dev:** [adaptive_platform_ui](https://pub.dev/packages/adaptive_platform_ui)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
