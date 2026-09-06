---
title: "Flutter flavors: one codebase, three apps, zero copy-pasted config"
description: "Dev, staging and production should be three installable apps with different icons, bundle ids and endpoints — built from the same source, with no runtime if-statement deciding which backend to call. Here is the full wiring on both platforms."
seoDescription: "Flutter flavors end to end: Android productFlavors, Xcode schemes and configurations, --dart-define-from-file, per-flavor icons and Firebase config, and the launch.json that ties it together."
keywords:
  - flutter flavors setup
  - flutter android productflavors
  - flutter ios scheme configuration
  - dart-define-from-file flutter
  - flutter per flavor app icon
  - flutter environment config
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-23"
emoji: "🍦"
tags: ["Flutter", "Build", "Android", "iOS", "DevOps"]
sources:
  - name: "Flavors for Flutter — Flutter documentation"
    url: "https://docs.flutter.dev/deployment/flavors"
  - name: "Build and release an Android app — Flutter documentation"
    url: "https://docs.flutter.dev/deployment/android"
  - name: "Build and release an iOS app — Flutter documentation"
    url: "https://docs.flutter.dev/deployment/ios"
  - name: "Configure build variants — Android developer documentation"
    url: "https://developer.android.com/build/build-variants"
  - name: "String.fromEnvironment — Dart API"
    url: "https://api.dart.dev/stable/dart-core/String/String.fromEnvironment.html"
  - name: "flutter run — Flutter documentation"
    url: "https://docs.flutter.dev/reference/flutter-cli"
related:
  - slug: "flutter-ci-cd-github-actions"
    title: "A Flutter CI pipeline that catches real problems"
  - slug: "flutter-secure-storage-secrets"
    title: "Secrets in a Flutter app: what you can store, and what you cannot"
draft: false
---

The bad version of environment handling looks like this:

```dart
const bool isProd = false;
final apiBase = isProd
    ? 'https://api.example.com'
    : 'https://staging.api.example.com';
```

It works until someone ships with the flag flipped the wrong way, or until QA needs staging and production installed side by side and discovers both have the same bundle id. Flavors fix both problems at the build layer: three separate installable apps, each compiled with its own configuration baked in.

## The Dart side, first

Start here because it is the part that determines everything else.

```dart
// lib/config/app_config.dart
enum Flavor { dev, staging, prod }

final class AppConfig {
  const AppConfig._({
    required this.flavor,
    required this.apiBase,
    required this.appName,
  });

  final Flavor flavor;
  final String apiBase;
  final String appName;

  static const _flavorName = String.fromEnvironment(
    'FLAVOR',
    defaultValue: 'dev',
  );

  static final AppConfig current = AppConfig._(
    flavor: Flavor.values.byName(_flavorName),
    apiBase: const String.fromEnvironment('API_BASE'),
    appName: const String.fromEnvironment('APP_NAME', defaultValue: 'App Dev'),
  );

  bool get isProduction => flavor == Flavor.prod;
}
```

`String.fromEnvironment` must be `const` and must be read from a const context — that is what lets the compiler tree-shake branches away. Writing `String.fromEnvironment(name)` with a runtime `name` variable silently returns the default value, which is a genuinely nasty bug because it looks correct.

Values come from `--dart-define`, and for anything more than two of them, from a file:

```json
// config/dev.json
{
  "FLAVOR": "dev",
  "API_BASE": "https://dev.api.example.com",
  "APP_NAME": "MyApp Dev"
}
```

```bash
flutter run --flavor dev --dart-define-from-file=config/dev.json
```

**These JSON files are build configuration, not a secret store.** Everything in them is embedded in the binary and extractable. API base URLs, feature flags and app names are fine; signing keys and API secrets are not — that is a separate problem with a separate answer.

## Android

`android/app/build.gradle.kts`:

```kotlin
android {
    flavorDimensions += "env"

    productFlavors {
        create("dev") {
            dimension = "env"
            applicationIdSuffix = ".dev"
            resValue("string", "app_name", "MyApp Dev")
        }
        create("staging") {
            dimension = "env"
            applicationIdSuffix = ".staging"
            resValue("string", "app_name", "MyApp Staging")
        }
        create("prod") {
            dimension = "env"
            resValue("string", "app_name", "MyApp")
        }
    }
}
```

Then make the manifest use it, in `android/app/src/main/AndroidManifest.xml`:

```xml
<application
    android:label="@string/app_name"
    android:icon="@mipmap/ic_launcher">
```

`applicationIdSuffix` is what makes side-by-side installation work — `com.example.myapp.dev` and `com.example.myapp` are different apps to Android. Note that `prod` has no suffix; the production id must stay exactly what the Play Store already knows.

Per-flavor icons and Firebase config go in flavor-specific source sets, which Gradle merges automatically:

```
android/app/src/dev/res/mipmap-xxxhdpi/ic_launcher.png
android/app/src/dev/google-services.json
android/app/src/prod/google-services.json
```

The `google-services.json` placement catches people out: a single file at `android/app/` applies to all flavors and will have the wrong package name for the suffixed ones, producing a Firebase initialisation failure that reads as a networking error.

## iOS

iOS is the fiddlier half because Xcode's model is schemes plus build configurations, and Flutter expects a specific naming pattern.

For each flavor you need **three build configurations** — `Debug-dev`, `Release-dev`, `Profile-dev`, and the same for staging and prod. Flutter's tooling looks for exactly `<Mode>-<flavor>`; a configuration named `dev-Debug` will not be found, and the error message is not obvious about why.

In Xcode:

1. Duplicate the existing Debug/Release/Profile configurations, renaming with the `-dev`, `-staging`, `-prod` suffixes.
2. Create a scheme per flavor, pointing each at its matching configurations.
3. Set `PRODUCT_BUNDLE_IDENTIFIER` per configuration — for example `com.example.myapp.dev`.
4. Set `PRODUCT_NAME` or the Info.plist `CFBundleDisplayName` per configuration for the home-screen label.

A user-defined build setting keeps the Firebase file selection tidy. Add `FIREBASE_CONFIG_DIR` per configuration, then a run-script build phase:

```bash
cp "${SRCROOT}/config/${FIREBASE_CONFIG_DIR}/GoogleService-Info.plist" \
   "${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/GoogleService-Info.plist"
```

Everything above is Xcode project state, which lives in `project.pbxproj` — a file that merges badly. Do flavor setup in one commit, by one person, and review the diff rather than trusting it.

## Tying it together

A `.vscode/launch.json` so nobody has to remember the flags:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "dev",
      "request": "launch",
      "type": "dart",
      "args": [
        "--flavor", "dev",
        "--dart-define-from-file", "config/dev.json"
      ]
    },
    {
      "name": "prod",
      "request": "launch",
      "type": "dart",
      "flutterMode": "release",
      "args": [
        "--flavor", "prod",
        "--dart-define-from-file", "config/prod.json"
      ]
    }
  ]
}
```

And in CI, the flavor becomes a matrix axis:

```yaml
      - run: |
          flutter build appbundle \
            --flavor ${{ matrix.flavor }} \
            --dart-define-from-file=config/${{ matrix.flavor }}.json
```

## The guardrail worth adding

The failure mode flavors do not prevent by themselves is shipping a dev build to production users. Add an assertion that runs at startup:

```dart
void main() {
  final config = AppConfig.current;

  assert(() {
    // Only runs in debug/profile; in release this whole block is removed.
    debugPrint('Running flavor: ${config.flavor.name} → ${config.apiBase}');
    return true;
  }());

  if (config.isProduction && config.apiBase.contains('staging')) {
    throw StateError('Production flavor pointed at a staging endpoint');
  }

  runApp(MyApp(config: config));
}
```

The `assert(() { ... }())` idiom is worth knowing generally: the closure runs only when assertions are enabled, so debug-only logging costs nothing in release. The second check is a real runtime guard, deliberately not an assert, because it is the one that must fire in a release build.

Making the flavor visible in the UI helps too — a coloured banner in non-production builds is a one-line `Banner` widget and eliminates a whole category of "wait, which environment am I testing?" confusion.

## FAQ

**Do I need flavors if I only have dev and prod?**

If the two ever need to be installed at once, or need different Firebase projects, yes. If dev is only ever `flutter run` on your machine, `--dart-define` alone is enough.

**Why does `--flavor` fail with "no flavor named X"?**

Android and iOS have separate flavor definitions and both must know the name. Missing `productFlavors` on Android or missing schemes on iOS each produce this, from different halves of the build.

**Can I put secrets in the dart-define file?**

No. Anything passed via `--dart-define` is in the compiled binary. Use platform secure storage for user-scoped secrets, and a backend for anything that must remain server-side.

**How do I handle per-flavor app icons on iOS?**

Multiple asset catalogs, with `ASSETCATALOG_COMPILER_APPICON_NAME` set per build configuration. This is cleaner than a script that swaps files at build time.

**Does the flavor name reach native code?**

Not automatically. On Android, `BuildConfig.FLAVOR` is available; on iOS, read the bundle identifier or a per-configuration Info.plist key. Do not assume the Dart-side value is visible to platform code.

---

*The flavor mechanism, Gradle `productFlavors`, Xcode configuration naming requirement, and `String.fromEnvironment` semantics described here are documented in the references linked above. The Dart config class shape, the production-endpoint guard, the `assert(() {}())` logging idiom, and the warning about `project.pbxproj` merges are my own judgement from setting this up on several projects. Gradle and Xcode syntax shift between versions — verify against your current templates.*
