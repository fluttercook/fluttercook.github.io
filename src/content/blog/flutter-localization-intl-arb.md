---
title: "Flutter localization with ARB files: plurals, genders, and the parts that bite"
description: "Adding a second language is easy. Adding the fifth, with plurals that are correct in Polish and dates that are correct in Vietnamese, is where the ARB format and the intl package start to matter."
seoDescription: "A practical guide to Flutter localization: gen_l10n and ARB files, ICU plurals and select, placeholders and date formats, locale resolution, RTL, and testing localized widgets."
keywords:
  - flutter localization arb
  - flutter gen_l10n tutorial
  - flutter intl plural select
  - flutter locale resolution callback
  - flutter date formatting intl
  - flutter rtl support
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-02"
emoji: "🌍"
tags: ["Flutter", "Localization", "i18n", "intl", "ARB"]
sources:
  - name: "Flutter — Internationalizing Flutter apps"
    url: "https://docs.flutter.dev/ui/accessibility-and-internationalization/internationalization"
  - name: "intl package"
    url: "https://pub.dev/packages/intl"
  - name: "DateFormat — intl API"
    url: "https://pub.dev/documentation/intl/latest/intl/DateFormat-class.html"
  - name: "Localizations — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Localizations-class.html"
  - name: "Directionality — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Directionality-class.html"
  - name: "ICU — Formatting messages"
    url: "https://unicode-org.github.io/icu/userguide/format_parse/messages/"
related:
  - slug: "flutter-forms-validation-at-scale"
    title: "Flutter forms past the toy example: async validation, focus, and autofill"
  - slug: "flutter-theming-material3-design-tokens"
    title: "Material 3 theming in Flutter: colour roles, not colour values"
draft: false
---

The first localization commit in most Flutter apps is a `Map<String, String>` keyed by language code, looked up through a global. It works for two languages and a hundred strings. It breaks the first time somebody needs "1 item" versus "2 items", and it breaks badly the first time a translator asks what `home_screen_label_2` is for.

Flutter's official answer is ARB files compiled by `gen_l10n` into a generated Dart class. The setup is short. What is worth understanding is the parts the quickstart does not cover: ICU plurals, placeholder types, locale resolution, and what happens on the day someone adds Arabic.

## Setup, once

```yaml
# pubspec.yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: any

flutter:
  generate: true
```

```yaml
# l10n.yaml at the project root
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
nullable-getter: false
```

`nullable-getter: false` is worth setting deliberately. With it, `AppLocalizations.of(context)` returns a non-nullable object and you write `AppLocalizations.of(context).greeting` instead of `AppLocalizations.of(context)!.greeting`. The cost is a runtime error rather than a null if you forget the delegates — which is the failure you want, because it is immediate and obvious.

```dart
MaterialApp(
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
  home: const HomePage(),
);
```

Strings then come from `AppLocalizations.of(context)`, which is an `InheritedWidget` lookup — meaning it needs a context below `MaterialApp`, and meaning a locale change rebuilds every widget that read it.

## The ARB format, past the obvious part

An ARB file is JSON where each key is a message and each `@key` is its metadata.

```json
{
  "@@locale": "en",

  "appTitle": "FlutterCook",
  "@appTitle": {
    "description": "Shown in the app bar and the task switcher"
  },

  "unreadCount": "{count, plural, =0{No new messages} one{1 new message} other{{count} new messages}}",
  "@unreadCount": {
    "description": "Badge text on the inbox tab",
    "placeholders": {
      "count": { "type": "int" }
    }
  },

  "lastSeen": "Last seen {when}",
  "@lastSeen": {
    "placeholders": {
      "when": {
        "type": "DateTime",
        "format": "yMMMd"
      }
    }
  }
}
```

Three things here decide how painful the next year is.

**`description` is not optional in practice.** It is the only context a translator gets. "Open" with no description will come back as a verb in one language and an adjective in another, and you will not find out until a user reports it.

**Placeholder `type` changes the generated signature.** `int` gives you `int count`; `DateTime` with a `format` gives you `DateTime when` and generates the `DateFormat` call for you. Without a type it is `Object` and you get `toString()`, which is how raw ISO timestamps end up in the UI.

**Plural categories are per-language.** English uses `one` and `other`. Vietnamese uses only `other`. Polish uses `one`, `few`, `many`, `other`. Russian and Arabic have their own sets. Writing `count == 1 ? 'item' : 'items'` in Dart bakes English grammar into your code; ICU plural syntax lets each translation file declare its own categories. This is the single strongest reason to use ARB rather than a map.

The generated call is ordinary Dart:

```dart
final l10n = AppLocalizations.of(context);
Text(l10n.unreadCount(inbox.unreadCount));
Text(l10n.lastSeen(user.lastSeenAt));
```

## `select` for gender and enumerated variants

`plural` has a sibling that people rarely reach for:

```json
{
  "invitedYou": "{gender, select, male{He invited you} female{She invited you} other{They invited you}}",
  "@invitedYou": {
    "placeholders": { "gender": { "type": "String" } }
  }
}
```

Use it for anything where the sentence structure changes with a value, not just gender — subscription tier, document status, delivery method. The alternative is three separate keys and an `if` chain in Dart, which pushes a grammar decision into code that translators cannot reach.

## Numbers, dates, and currency

`intl` formats these; do not hand-roll them.

```dart
final locale = Localizations.localeOf(context).toString();

NumberFormat.currency(locale: locale, symbol: '₫').format(120000);
NumberFormat.compact(locale: locale).format(1250000);       // 1.25M / 1,25 Tr
DateFormat.yMMMMd(locale).format(order.placedAt);
DateFormat.Hm(locale).format(order.placedAt);
```

The differences are not cosmetic. Decimal separators swap between `.` and `,`. Date order differs. Some locales use different digits entirely. A hard-coded `'${d.day}/${d.month}/${d.year}'` is wrong for roughly half the world.

Two practical notes. `DateFormat` needs locale data initialised for anything outside the default; in a Flutter app the `flutter_localizations` delegates handle that for the app's supported locales. And format the **local** time — store UTC, convert with `toLocal()` at the edge, or your "posted 2 hours ago" is wrong by the timezone offset.

## Locale resolution: what happens for `fr-CA`

`supportedLocales` is a list, and the device may report something not on it. The default resolution tries an exact match, then language-only, then falls back to the first entry in the list. That last part surprises people: an unsupported locale gets `supportedLocales.first`, so **put your real default first**.

When you need control — a regional variant that should map to a specific file, or a user-chosen language stored in preferences:

```dart
MaterialApp(
  locale: settings.overrideLocale, // null = follow the device
  supportedLocales: AppLocalizations.supportedLocales,
  localeResolutionCallback: (deviceLocale, supported) {
    if (deviceLocale == null) return supported.first;
    for (final l in supported) {
      if (l.languageCode == deviceLocale.languageCode) return l;
    }
    return supported.first;
  },
);
```

Setting `locale` explicitly overrides the device entirely — that is how an in-app language picker works. Persist the choice, and remember that `null` must be a valid stored value meaning "follow the system".

## Right-to-left, which is not just mirroring

Adding Arabic or Hebrew flips the layout direction. Flutter handles most of it if you have been using directional APIs:

| Use | Not |
| --- | --- |
| `EdgeInsetsDirectional.only(start: 16)` | `EdgeInsets.only(left: 16)` |
| `AlignmentDirectional.centerStart` | `Alignment.centerLeft` |
| `BorderRadiusDirectional` | `BorderRadius` |
| `Positioned.directional(start: ...)` | `Positioned(left: ...)` |

`Row` already reverses under RTL. Icons mostly should mirror — a back arrow points the other way — but not all of them: a play button, a clock, a logo should not. `Transform.flip` on the ones that should, and check the rest.

Test it without speaking the language:

```dart
Directionality(textDirection: TextDirection.rtl, child: MyScreen())
```

Anything that visibly stays put is a hard-coded `left`/`right`.

## Testing localized widgets

A widget test with no delegates throws the moment something calls `AppLocalizations.of`. Provide them:

```dart
Widget wrap(Widget child, {Locale locale = const Locale('en')}) => MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: child,
    );

testWidgets('inbox badge pluralises', (tester) async {
  await tester.pumpWidget(wrap(const InboxBadge(count: 1)));
  expect(find.text('1 new message'), findsOneWidget);

  await tester.pumpWidget(wrap(const InboxBadge(count: 5)));
  expect(find.text('5 new messages'), findsOneWidget);
});
```

Asserting on literal English strings in tests is a trade-off: it catches real regressions but breaks when copy changes. A reasonable middle ground is to assert on the localized value computed from the same source (`l10n.unreadCount(5)`), so the test checks wiring rather than wording.

## The workflow that keeps translators sane

1. **Only `app_en.arb` gets new keys by hand.** It is the template; the generator validates the others against it.
2. **Never reuse a key with different meaning.** Translations are attached to keys; changing the English text under a key silently invalidates every translation of it.
3. **Delete dead keys.** A stale key is a string a human is still being paid to translate.
4. **Check for missing keys in CI.** `flutter gen-l10n` reports untranslated messages; write them to a file with `untranslated-messages-file` in `l10n.yaml` and fail the build if it grows.

## FAQ

**Can I get a string outside a widget, in a repository or a background isolate?**

Not through `AppLocalizations.of(context)` — it needs a context. Either pass the string in from the UI layer, or return an error code and localize at the point of display. The second is usually correct: a repository should not know what language the user reads.

**What about `intl_translation` and `@@last_modified`?**

`intl_translation` is the older, separate toolchain that extracts messages from annotated Dart. `gen_l10n` is built into the Flutter tool and is what the current documentation targets. `@@last_modified` is metadata some tools write into ARB; it is harmless.

**Do I need to restart the app when the language changes?**

No. Setting `locale` on `MaterialApp` rebuilds the subtree and every `AppLocalizations.of(context)` read picks up the new value.

**Why is my generated file missing?**

`generate: true` must be under `flutter:` in `pubspec.yaml`, and the file appears after a build or `flutter gen-l10n`. It lives in the build directory by default, which is why it is not in source control.

**Should translation files be in the app or fetched from a server?**

Bundled ARB is simpler, works offline, and ships atomically with the code that uses it. Server-delivered strings let you fix a typo without a release, at the cost of a loading state, a cache, and a fallback path. Bundle by default; add remote overrides only when release cadence genuinely demands it.

---

*The ARB syntax, `l10n.yaml` options, resolution order and directional widget APIs described here are documented in the Flutter internationalization guide and the `intl` package docs linked above. The workflow rules, the recommendation to assert on computed strings in tests, and the bundled-versus-remote position are my own judgement. Tool behaviour changes between Flutter releases — run `flutter gen-l10n --help` against your SDK before copying options.*
