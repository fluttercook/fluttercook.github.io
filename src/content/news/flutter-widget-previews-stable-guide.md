---
title: "Flutter Widget Previews are stable: a practical guide to @Preview"
description: "Widget Previews graduated to stable in Flutter 3.47. Here is how @Preview works, every parameter it accepts, MultiPreview, custom annotations, and where it still falls short."
seoDescription: "Flutter Widget Previewer guide: @Preview annotation parameters, flutter widget-preview start, MultiPreview, theme and brightness variants, wrapper, and known limitations."
keywords: ["flutter widget preview", "@preview annotation flutter", "flutter widget previewer", "flutter 3.47 previews", "multipreview flutter", "preview themedata flutter"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🖼️"
tags: ["Flutter 3.47", "Flutter", "Widget Preview", "Tooling", "DevTools"]
sources:
  - name: "Flutter Widget Previewer — flutter.dev docs"
    url: "https://docs.flutter.dev/tools/widget-previewer"
  - name: "Preview class — Flutter API reference"
    url: "https://api.flutter.dev/flutter/widget_previews/Preview-class.html"
  - name: "widget_previews library — Flutter API reference"
    url: "https://api.flutter.dev/flutter/widget_previews/"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Widget Previews shipped as experimental back in 3.35, and a lot of developers tried it once, found it slow, and went back to hot reload. Flutter 3.47 marks it **stable**, with local build caching and an abstract theming API that makes the feature worth a second look. If you build design systems, component libraries, or anything with more than three visual states, this changes your inner loop.

The pitch is narrow and honest: the previewer renders **individual widgets** in isolation, without booting your app, navigating to the right screen, or faking the right state. That is a different job from hot reload, and it is the job hot reload has always been bad at.

## Starting the previewer

From your IDE — Android Studio, IntelliJ, or VS Code — the previewer starts automatically; open the **Flutter Widget Preview** tab in the sidebar. From a terminal:

```shell
flutter widget-preview start
```

That launches a local server and opens a live preview environment in your browser. Builds are cached in a `.widget_preview/` folder in your project — this cache is the reason startup got noticeably faster in 3.47, and it is the thing to add to `.gitignore` if your tooling has not already.

## What you can annotate

`@Preview` comes from `package:flutter/widget_previews.dart` and can be applied to:

- **top-level functions** returning a `Widget` or `WidgetBuilder`
- **static methods** in a class returning a `Widget` or `WidgetBuilder`
- **public widget constructors and factories** that take no required arguments

The simplest possible case:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/widget_previews.dart';

@Preview(name: 'My Sample Text')
Widget mySampleText() {
  return const Text('Hello, World!');
}
```

No app, no `MaterialApp`, no route. Save the file and the preview updates.

## Every parameter, and what it is actually for

The `Preview` class is small, which is a good sign. Here is the full surface:

| Parameter | Type | What it does |
| --- | --- | --- |
| `group` | `String` | Groups related previews in the UI. Defaults to `'Default'`. |
| `name` | `String?` | Label shown beside the preview. |
| `size` | `Size?` | Artificial constraints applied to the widget. |
| `textScaleFactor` | `double?` | Font scaling, for accessibility checks. |
| `wrapper` | `WidgetWrapper?` | Wraps the widget in a tree — scaffolds, providers, `InheritedWidget`. |
| `theme` | `PreviewTheme?` | Returns Material and Cupertino theming data to apply. |
| `brightness` | `Brightness?` | Initial light/dark brightness. |
| `localizations` | `PreviewLocalizations?` | Localization configuration for the preview. |

`wrapper` is the one that makes previews usable in a real codebase. Most widgets are not standalone — they expect a `Scaffold`, a theme, or an injected repository. You supply that once:

```dart
@Preview(
  name: 'Submit button — pressed state',
  group: 'Form Controls',
  size: Size(240, 56),
  textScaleFactor: 1.5,
  wrapper: _inScaffold,
)
Widget submitButtonPreview() => const SubmitButton(isBusy: true);

Widget _inScaffold(Widget child) => MaterialApp(
      home: Scaffold(body: Center(child: child)),
    );
```

## Rendering the same widget many ways

This is where previews beat hot reload outright. Stack annotations to get one widget rendered under several configurations at once:

```dart
@Preview(group: 'Brightness', name: 'Light', brightness: Brightness.light)
@Preview(group: 'Brightness', name: 'Dark', brightness: Brightness.dark)
Widget buttonPreview() => const ButtonShowcase();
```

When the same three or four variants repeat across dozens of components, promote them to a `MultiPreview`:

```dart
final class MultiBrightnessPreview extends MultiPreview {
  const MultiBrightnessPreview();

  @override
  List<Preview> get previews => const [
        Preview(group: 'Brightness', name: 'Light', brightness: Brightness.light),
        Preview(group: 'Brightness', name: 'Dark', brightness: Brightness.dark),
      ];
}

@MultiBrightnessPreview()
Widget buttonPreview() => const ButtonShowcase();
```

## Baking your design system into a custom annotation

The abstract theme API added in 3.47 is the piece that makes this scale. Rather than repeating `theme:` on every preview, subclass `Preview` and supply the builder once:

```dart
final class MyCustomPreview extends Preview {
  const MyCustomPreview({
    super.name,
    super.group,
    super.size,
    super.textScaleFactor,
    super.wrapper,
    super.brightness,
    super.localizations,
  }) : super(theme: MyCustomPreview.themeBuilder);

  static PreviewThemeData themeBuilder() {
    return PreviewThemeData(
      materialLight: ThemeData.light(),
      materialDark: ThemeData.dark(),
    );
  }
}
```

Now every `@MyCustomPreview(...)` in the codebase renders against your real tokens. `PreviewThemeData` carries both Material and Cupertino data, which matters more in 3.47 than it used to — with the design system moving into standalone `material_ui` and `cupertino_ui` packages, previews are a cheap way to see whether a component actually survives both.

There is also `transform()`, which lets a custom annotation rewrite the preview at runtime — useful for prefixing names or swapping themes across a whole class of previews without touching call sites.

## Previews are not golden tests

Worth being blunt about this, because teams confuse the two. Previews are an **authoring** tool: fast, visual, human-in-the-loop, no assertions. Golden tests are a **regression** tool: slow, headless, and they fail your CI when a pixel moves. Previews do not replace goldens, and a preview passing means nothing except that it rendered.

The useful pairing is previews while you build the component, goldens once its states are settled.

## The limitations you will hit

The previewer runs in a web-based environment, which sets hard boundaries:

1. **No native plugins**, and no `dart:io` or `dart:ffi`. Anything touching the filesystem, platform channels, or FFI will not render — inject a fake through `wrapper` instead.
2. **Callback arguments must be public and constant.** Private closures will not be picked up.
3. **Asset paths must be package-based**: use `'packages/my_package_name/assets/my_image.png'`, not `'assets/my_image.png'`.
4. **Unconstrained widgets** are automatically clamped to roughly 50% of the previewer's height and width. Pass `size` when that squashes your layout.
5. **Single project or Pub workspace only.** Multi-project IDE support is still being investigated, so a large monorepo may not light up entirely.

## Adopting it without a rewrite

1. **Upgrade to 3.47** and run `flutter widget-preview start` once to confirm the previewer builds your project.
2. **Add `.widget_preview/` to `.gitignore`.**
3. **Pick one leaf component** — a button, a badge, a list tile — and add a single `@Preview`. Do not start with a screen.
4. **Write one `wrapper`** that installs your app's theme and providers, and reuse it.
5. **Promote your recurring variants** (light/dark, text scale 1.0/2.0, LTR/RTL) into a `MultiPreview`.
6. **Subclass `Preview`** with your design system's `PreviewThemeData` and standardise on that annotation.
7. **Add goldens** for the states you now know are correct.

## The bottom line

Widget Previews stopped being a demo in 3.47. The caching makes startup tolerable, and the theme APIs are the difference between a toy and something a design-system team can standardise on. The limitations are real — no native code, package-based asset paths, single-workspace — but they are limitations of scope, not of maturity. If you tried previews in 3.35 and shrugged, the honest advice is to try again: this is the release where the feature earns its place in the loop.
