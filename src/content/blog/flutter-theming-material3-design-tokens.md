---
title: "Material 3 theming in Flutter: colour roles, not colour values"
description: "ColorScheme.fromSeed gives you a palette in one line and then people immediately override it back to hard-coded hex. Here is what the roles mean, when a seed is the wrong tool, and how ThemeExtension carries the tokens Material does not have."
seoDescription: "How Material 3 theming works in Flutter: ColorScheme roles, fromSeed vs fromSwatch, dark mode contrast, ThemeExtension for custom design tokens, and component themes."
keywords:
  - flutter material 3 theming
  - colorscheme fromseed flutter
  - flutter themeextension custom tokens
  - flutter dark mode colorscheme
  - flutter component theme cardtheme
  - material 3 color roles explained
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-04"
emoji: "🎨"
tags: ["Flutter", "Material 3", "Theming", "Design Systems", "UI"]
sources:
  - name: "Flutter — Material Design 3"
    url: "https://docs.flutter.dev/ui/design/material"
  - name: "ThemeData — Flutter API"
    url: "https://api.flutter.dev/flutter/material/ThemeData-class.html"
  - name: "ColorScheme.fromSeed — Flutter API"
    url: "https://api.flutter.dev/flutter/material/ColorScheme/ColorScheme.fromSeed.html"
  - name: "Material 3 — Color roles"
    url: "https://m3.material.io/styles/color/roles"
  - name: "ThemeExtension — Flutter API"
    url: "https://api.flutter.dev/flutter/material/ThemeExtension-class.html"
  - name: "TextTheme — Flutter API"
    url: "https://api.flutter.dev/flutter/material/TextTheme-class.html"
related:
  - slug: "flutter-accessibility-semantics"
    title: "Flutter accessibility: what the semantics tree actually reports"
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
draft: false
---

The Material 3 migration in Flutter produced a predictable pattern. Teams call `ColorScheme.fromSeed(seedColor: brandPurple)`, look at the result, decide it is not their brand, and start passing explicit colours to every widget again. Six months later the app has two hundred hard-coded hex values, dark mode is a separate list of two hundred more, and changing the brand colour is a week of work.

The thing that was skipped is the idea Material 3 is actually built on: you do not style widgets with colours, you assign them **roles**. A `FilledButton` does not have a purple background — it has a `primary` background with `onPrimary` content. Once that is true across the app, the palette becomes one object you can swap.

## The roles, and what each one is for

`ColorScheme` has about thirty members. They are not thirty independent choices; they are pairs and families.

| Role | Used for | Its "on" pair |
| --- | --- | --- |
| `primary` | The main action, filled buttons, active states | `onPrimary` |
| `primaryContainer` | A softer emphasis of the same idea | `onPrimaryContainer` |
| `secondary` / `tertiary` | Accents that need to differ from primary | `onSecondary` / `onTertiary` |
| `surface` | Every background: pages, cards, sheets | `onSurface` |
| `surfaceContainerLowest` … `Highest` | Elevation expressed as tone, not shadow | `onSurface` |
| `error` | Destructive and invalid states | `onError` |
| `outline` / `outlineVariant` | Borders and dividers | — |

The `on` prefix is the whole contract: **`onX` is guaranteed readable on `X`**. If you paint a container `colorScheme.primaryContainer` and its text `colorScheme.onPrimaryContainer`, contrast is handled — in light mode, in dark mode, and after someone changes the seed.

The one that changed most in Material 3 is surfaces. The old model raised elevation with a shadow; the new one raises it with **tone**. A dialog sitting on a page is a lighter (in light mode) or lighter-grey (in dark mode) surface, not a drop shadow. That is what the `surfaceContainer*` family is for, and it is why `background` and `surfaceVariant` were deprecated — use `surface` and `surfaceContainerHighest`.

## When a seed is right, and when it is not

`ColorScheme.fromSeed` runs the Material colour algorithm: it takes one colour, derives a tonal palette, and picks roles from it that are guaranteed to meet contrast requirements. It is genuinely good, and it is the right default for an app without a strict brand book.

```dart
final lightScheme = ColorScheme.fromSeed(seedColor: const Color(0xFF6750A4));
final darkScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.dark,
);
```

Two things people get wrong here. **The seed is not your primary colour** — the algorithm derives `primary` from the seed's hue and will happily return something noticeably different, because the exact seed may not have enough contrast against `onPrimary`. And **you need two calls**, one per brightness; a dark scheme is not the light one inverted.

When brand requirements are exact, do not fight the algorithm. Construct the scheme explicitly and let the analyser tell you what you missed:

```dart
const brandLight = ColorScheme(
  brightness: Brightness.light,
  primary: Color(0xFF0B5FFF),
  onPrimary: Color(0xFFFFFFFF),
  secondary: Color(0xFF00A37A),
  onSecondary: Color(0xFF00110B),
  error: Color(0xFFBA1A1A),
  onError: Color(0xFFFFFFFF),
  surface: Color(0xFFFDFCFF),
  onSurface: Color(0xFF1A1C1E),
  // ...
);
```

A middle path that works well in practice: seed the scheme, then `copyWith` only the two or three roles the brand actually pins. You keep the algorithm's contrast guarantees everywhere else.

There is also `ColorScheme.fromImageProvider`, which derives a scheme from an image asynchronously — useful for a player screen that themes itself from album art, and a bad idea for your whole app, since it must be awaited.

## Wiring it into `ThemeData` once

```dart
ThemeData _theme(ColorScheme scheme) => ThemeData(
      colorScheme: scheme,
      useMaterial3: true,
      textTheme: _textTheme,
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        color: scheme.surfaceContainerLow,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        filled: true,
        border: OutlineInputBorder(),
      ),
      extensions: const [AppTokens.light],
    );

MaterialApp(
  theme: _theme(lightScheme),
  darkTheme: _theme(darkScheme),
  themeMode: ThemeMode.system,
  home: const HomePage(),
);
```

Component themes are where a design system stops being a document and becomes code. `filledButtonTheme` with a 48-pixel minimum height means nobody has to remember the tap-target rule. `cardTheme` with a 16-pixel radius means the corner radius is one line, not two hundred.

Note `ThemeMode.system` — respecting the OS setting is the expected default, and the two-theme setup means it costs nothing.

## `ThemeExtension` for the tokens Material does not have

Every real design system has values Material has no slot for: a success colour, a brand gradient, a spacing scale, a chart palette. The wrong answer is a file of global constants, because they cannot vary by brightness. `ThemeExtension` is the right one:

```dart
@immutable
class AppTokens extends ThemeExtension<AppTokens> {
  const AppTokens({
    required this.success,
    required this.onSuccess,
    required this.spacingUnit,
  });

  final Color success;
  final Color onSuccess;
  final double spacingUnit;

  static const light = AppTokens(
    success: Color(0xFF116B3E),
    onSuccess: Color(0xFFFFFFFF),
    spacingUnit: 8,
  );

  static const dark = AppTokens(
    success: Color(0xFF7CDBA4),
    onSuccess: Color(0xFF00391E),
    spacingUnit: 8,
  );

  @override
  AppTokens copyWith({Color? success, Color? onSuccess, double? spacingUnit}) =>
      AppTokens(
        success: success ?? this.success,
        onSuccess: onSuccess ?? this.onSuccess,
        spacingUnit: spacingUnit ?? this.spacingUnit,
      );

  @override
  AppTokens lerp(AppTokens? other, double t) {
    if (other is! AppTokens) return this;
    return AppTokens(
      success: Color.lerp(success, other.success, t)!,
      onSuccess: Color.lerp(onSuccess, other.onSuccess, t)!,
      spacingUnit: lerpDouble(spacingUnit, other.spacingUnit, t)!,
    );
  }
}
```

Reading it is a one-liner, and an extension makes it pleasant:

```dart
extension ThemeX on BuildContext {
  ColorScheme get colors => Theme.of(this).colorScheme;
  AppTokens get tokens => Theme.of(this).extension<AppTokens>()!;
}

// Container(color: context.tokens.success)
```

Implementing `lerp` is not optional busywork — it is what makes your custom tokens animate smoothly when the theme changes, exactly like the built-in ones. Skip it and a light/dark transition shows Material colours crossfading while your brand green snaps.

## Typography, and the thing that breaks accessibility

Material 3's `TextTheme` has fifteen named styles in five families — `display`, `headline`, `title`, `body`, `label`, each in `Large`/`Medium`/`Small`. Define them once and reference by role:

```dart
Text('Total', style: Theme.of(context).textTheme.titleMedium)
```

The rule that matters more than any of them: **never set a font size that ignores the user's text-scale setting**, and never disable scaling to make a layout fit. If a label overflows at 200% scale, the layout is wrong, not the setting. Use `Flexible`, `FittedBox` where genuinely appropriate, and test at the extremes — the accessibility settings on both platforms go well past what most designs are checked against.

## Migration order that avoids a rewrite

Turning `useMaterial3` on in a mature app changes a lot at once. The sequence that keeps it reviewable:

1. **Switch to `useMaterial3: true`** and fix only what is visually broken. Expect button shapes, app bar colouring and elevation to shift.
2. **Replace deprecated members**: `background` → `surface`, `onBackground` → `onSurface`, `surfaceVariant` → `surfaceContainerHighest`.
3. **Grep for `Color(0x`** outside your theme file. Each hit is either a role you should be using or a token that belongs in a `ThemeExtension`.
4. **Move per-widget styling into component themes.** A `styleFrom` repeated in five places is a `filledButtonTheme` entry.
5. **Only then** tune the palette. Doing this first means retuning after every later step.

## FAQ

**Should I still use `primarySwatch`?**

No. It belongs to the Material 2 model and is ignored by most Material 3 components. Use `ColorScheme.fromSeed`, or an explicit `ColorScheme`.

**Why does my button look different from the design after `fromSeed`?**

Because the algorithm chose `primary` for contrast, not fidelity to your seed. If the exact value matters, `copyWith(primary: ..., onPrimary: ...)` after seeding — and check the contrast yourself, since you have opted out of the guarantee.

**How do I theme one screen differently?**

Wrap it in a `Theme` widget with a modified `ThemeData`. Everything below it, including dialogs opened from it, picks up the override — dialogs inherit from the context that opened them.

**Is `ThemeExtension` worth it for three colours?**

Yes, if those colours differ between light and dark. That is the whole distinction: constants cannot, extensions can, and the type safety means a missing token is a compile error rather than a wrong shade in production.

**What replaced `Theme.of(context).accentColor`?**

`colorScheme.secondary`, in most cases. The `ThemeData` colour fields from Material 2 are gone or deprecated; the `ColorScheme` is the single source now.

---

*Role semantics and the deprecations are from the Flutter Material documentation and the Material 3 colour guidance linked above. The migration order, the seed-then-`copyWith` compromise, and the view that a layout breaking at high text scale is a layout bug are my own judgement. Material widget APIs change between Flutter releases — check the API docs for the SDK you ship.*
