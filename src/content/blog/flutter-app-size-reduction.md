---
title: "Shrinking a Flutter app: where the megabytes actually are"
description: "Nobody's Flutter app is 40 MB because of their Dart code. It is the engine floor, the assets nobody audited, the fonts nobody subset, and the ABIs you shipped to devices that cannot run them."
seoDescription: "How to reduce Flutter app size: the engine baseline, --analyze-size and the DevTools app size tool, split ABIs and app bundles, asset and font auditing, tree shaking, and deferred components."
keywords:
  - flutter app size reduction
  - flutter analyze-size devtools
  - flutter split per abi appbundle
  - flutter font tree shaking icons
  - flutter deferred components
  - flutter apk size optimization
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-01"
emoji: "📦"
tags: ["Flutter", "Performance", "App Size", "Build", "Release"]
sources:
  - name: "Flutter — Measuring your app's size"
    url: "https://docs.flutter.dev/perf/app-size"
  - name: "Flutter — Build and release for Android"
    url: "https://docs.flutter.dev/deployment/android"
  - name: "Flutter — Deferred components"
    url: "https://docs.flutter.dev/perf/deferred-components"
  - name: "Flutter — Adding assets and images"
    url: "https://docs.flutter.dev/ui/assets/assets-and-images"
  - name: "Android Developers — Android App Bundle"
    url: "https://developer.android.com/guide/app-bundle"
  - name: "Flutter — DevTools app size tool"
    url: "https://docs.flutter.dev/tools/devtools/app-size"
related:
  - slug: "flutter-startup-time-cold-start"
    title: "Flutter cold start: measuring the time before your first frame"
  - slug: "flutter-flavors-build-config"
    title: "Flutter flavors: one codebase, three apps, zero copy-pasted config"
draft: false
---

The app size conversation usually starts after a stakeholder compares the APK to a competitor's and asks why a to-do list is 40 MB. The engineering response is often to start deleting packages, which is both the most painful lever and usually not the one that matters.

Flutter apps have a size floor: the engine, the Dart runtime, Skia or Impeller, and the ICU data. That floor is real and you cannot remove it. Everything above it is yours, and in most apps I have looked at, the majority of "yours" is assets and shipped-but-unused native code, not Dart.

So the first move is not to delete anything. It is to measure.

## Measure first: `--analyze-size`

```bash
flutter build apk --release --analyze-size
flutter build appbundle --release --analyze-size
flutter build ipa --release --analyze-size
```

This prints a summary and writes a JSON file. Open that file in DevTools' app size tool — it gives you a treemap where the boxes are proportional to bytes, broken down by package, by asset, and by native library.

The treemap is the whole point. It answers "what is big" rather than "what do I feel guilty about". The usual reveals, roughly in order of frequency:

- A handful of PNGs exported at 3x from a design tool, uncompressed, several megabytes each.
- Two icon fonts, both fully included, because one package pulled in its own.
- A localisation or timezone data blob nobody knew was there.
- `libflutter.so` present for four ABIs in a single APK.

None of those are fixed by removing a dependency.

## The single biggest Android lever: stop shipping every ABI

A fat APK contains native libraries for `armeabi-v7a`, `arm64-v8a`, `x86_64` — every device downloads all of them and uses one. Two fixes, and you should be using the first:

```bash
# Preferred: Play handles per-device delivery.
flutter build appbundle --release

# If you distribute APKs directly (sideload, other stores):
flutter build apk --release --split-per-abi
```

An app bundle is the format Play wants anyway, and it splits by ABI, density and language automatically. `--split-per-abi` gives you separate APKs per architecture for direct distribution — a real, immediate cut, since each APK now carries one copy of the engine instead of three.

If you genuinely cannot use either, at minimum drop the x86 ABIs, which target emulators rather than shipping phones. Do that deliberately and document it, because it does mean the app will not install on an x86 emulator.

## Assets: the part that is almost always the worst offender

Assets are shipped verbatim. Nothing compresses them for you, nothing resizes them, and nothing warns you.

```bash
# What is actually in the bundle, biggest first
find assets -type f -exec du -h {} + | sort -rh | head -30
```

The checklist that recovers the most bytes:

**Right format.** Photographs → WebP or JPEG. Flat graphics, logos, icons → SVG rendered at runtime (`flutter_svg`) or a properly optimised PNG. A 2 MB PNG of a photograph is a 200 KB JPEG that looks identical on a phone screen.

**Right size.** An image displayed at 120 logical pixels does not need a 2048-pixel source. Export at the largest size you actually display, times three, and no more.

**Right resolution set.** Flutter's `2.0x` / `3.0x` directory convention lets you ship one appropriately sized image per density instead of one huge one for everyone. On Android, app bundles then deliver only the matching density.

**No orphans.** `flutter:  assets: - assets/` includes the whole directory, including the three unused mockups someone dropped in. Declare directories deliberately, and grep for each asset path before assuming it is used.

**Fonts, subset.** A full weight of a Latin font is 150–400 KB; a family of six weights you use two of is pure waste. Ship only the weights you reference. If a font covers scripts you do not support, subsetting it with a font tool removes glyphs you will never draw.

Icon fonts get this for free: Flutter tree-shakes `MaterialIcons` down to the icons you actually reference in release builds, and prints how much it removed. That optimisation is disabled if you construct `IconData` dynamically — `IconData(codePoint)` from a variable defeats it, because the tool can no longer prove which icons are reachable.

## What tree shaking does and does not do to Dart

Release builds are AOT-compiled with tree shaking, and it is genuinely effective on straightforward code. The things that defeat it are worth knowing, because they are also the things that produce "why is this package 3 MB" surprises:

- **Reflection-like patterns.** `dart:mirrors` is not available in AOT at all; code generation exists precisely because of this.
- **Dynamic entry points.** A registry mapping strings to constructors keeps every constructor alive.
- **Large const tables.** A generated country/timezone/emoji table is data, and data is not shaken.

The practical consequence: measure a dependency's cost before and after, rather than assuming. Build with the package, build without it, diff the two `--analyze-size` outputs. Some heavyweight-looking packages cost 30 KB; some innocuous ones bring a data blob.

## Build flags that actually change the output

| Flag / setting | Platform | Effect |
| --- | --- | --- |
| `--release` | all | Non-negotiable. Debug builds include the JIT and are multiples larger. |
| `--split-debug-info=<dir>` | all | Moves debug symbols out of the binary. Keep the directory — you need it to symbolise crashes. |
| `--obfuscate` | all | Requires `--split-debug-info`. Renames symbols; a modest size win, its real purpose is obfuscation. |
| `--split-per-abi` | Android APK | One engine copy per APK instead of several. |
| `--tree-shake-icons` | all | On by default in release; verify it is not disabled. |
| R8 / `minifyEnabled` | Android | Shrinks the Java/Kotlin side, including plugin code. |

```bash
flutter build appbundle --release \
  --obfuscate --split-debug-info=build/symbols
```

The one to be careful with is `--split-debug-info`. It is a real win, and it makes production stack traces unreadable unless you keep the symbol directory for that exact build and feed it to your crash reporter. Archive it in CI alongside the artifact; a build whose symbols are gone is a build whose crashes you cannot fix.

## Deferred components, when the app is genuinely large

Android supports deferring parts of a Flutter app into separate feature modules downloaded on demand, using Dart's `deferred as` imports plus Play Feature Delivery.

```dart
import 'package:my_app/admin/console.dart' deferred as admin;

Future<void> openAdminConsole() async {
  await admin.loadLibrary();
  runAdminConsole();
}
```

This is a real tool with real setup cost: manifest and Gradle configuration, a loading state at every entry point, and a failure path for when the download does not complete. It is worth it for a genuinely optional, genuinely large surface — an admin console, an AR mode, a bundled ML model — and not worth it to shave 300 KB off a settings screen.

## An order of operations

1. `--analyze-size` and open the treemap. Write down the top ten entries.
2. Switch to app bundle or `--split-per-abi`. Re-measure.
3. Audit assets — format, dimensions, orphans, fonts. Re-measure.
4. Enable `--split-debug-info` and R8, archiving symbols. Re-measure.
5. Diff dependencies you suspect, one at a time.
6. Only now consider deferred components.

Every step ends in "re-measure" for a reason: it is very easy to spend a day on a change worth 40 KB while a 6 MB asset sits untouched.

## FAQ

**Why is the download size smaller than the APK?**

Play reports compressed delivery size, and app bundles strip what a given device does not need. Compare like with like: the number that matters to users is the Play Console's "download size" for a representative device, not the file on your disk.

**Does the size difference between Skia and Impeller matter?**

Both are part of the engine floor and you do not choose them for size. Engine composition changes between Flutter versions; measure your own build rather than reasoning from an older blog post.

**Is a smaller app actually worth engineering time?**

It correlates with install completion, particularly on slow connections and cheap devices, and it is a hard constraint in markets with per-install size limits on cellular. Whether that is worth a week is a product decision — but measuring is an hour, and the first two fixes are usually a single build-flag change.

**Does removing packages help much?**

Less than people expect, unless the package ships assets or a data table. Measure the diff before doing surgery on your dependency graph.

**Why did my size jump after a Flutter upgrade?**

The engine floor moves between releases. Compare the `--analyze-size` output from both versions; if the growth is in the engine rather than your code, there is nothing local to fix.

---

*The build flags, tooling and deferred-component mechanism described here are documented in the Flutter app size, Android deployment and deferred components guides linked above. The ordering, the emphasis on assets over dependencies, and the advice to archive symbol directories in CI are my own judgement based on profiling apps this way. Flag behaviour and engine size change between releases — measure your own build.*
