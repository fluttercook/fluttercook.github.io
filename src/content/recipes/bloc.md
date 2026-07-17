---
title: "State management in Flutter with bloc: a practical guide"
package: "bloc"
repo: "felangel/bloc"
githubUrl: "https://github.com/felangel/bloc"
category: "State management"
stars: 12474
forks: 3417
lastUpdate: "2026-07-15"
pubDev: "https://pub.dev/packages/bloc"
youtube: "https://www.youtube.com/results?search_query=flutter+bloc"
priority: "High"
phase: "P1"
trendRank: 30
description: "A predictable state management library that helps implement the BLoC design pattern."
seoDescription: "bloc: State management for Flutter with 12,474★ on GitHub. A predictable state management library that helps implement the BLoC design pattern. Install,…"
keywords:
  - flutter bloc
  - bloc flutter
  - flutter state management
  - flutter app state
  - flutter mobile app
  - bloc example
  - bloc tutorial
topics:
  - angulardart
  - bloc
  - concurrency
  - dart
  - dart-library
  - dart-web
related:
  - slug: getx
    title: 'State management in Flutter with getx: a practical guide'
  - slug: flutter-architecture-samples
    title: 'State management in Flutter with flutter_architecture_samples: a practical
      guide'
  - slug: riverpod
    title: 'State management in Flutter with riverpod: a practical guide'
  - slug: fish-redux
    title: 'State management in Flutter with fish-redux: a practical guide'
faq:
  - q: Is bloc free to use?
    a: Yes. bloc is open source and free to use in your Flutter projects. You can view
      the source, report issues, and contribute on GitHub.
  - q: Does bloc work on both iOS and Android?
    a: bloc is built for Flutter, so it targets iOS and Android from a single codebase,
      and typically web and desktop too depending on the project's platform support.
  - q: How popular is bloc?
    a: As of 2026, bloc has around 12,474 stars and 3,417 forks on GitHub, which puts
      it among the more widely used options in the State management space.
  - q: What are good alternatives to bloc?
    a: Popular alternatives in the State management category include getx, flutter-architecture-samples,
      riverpod. The best choice depends on your app's size, team, and performance needs.
  - q: How do I install bloc?
    a: Add bloc to the dependencies section of your pubspec.yaml and run flutter pub
      get. Full versions and API docs are on pub.dev.
datePublished: "2018-10-07"
dateModified: "2026-07-15"
draft: false
---

[`bloc`](https://github.com/felangel/bloc) is an open-source **state-management library** for Flutter mobile app development, with **12,474★** on GitHub and last updated on **2026-07-15**. This guide covers what bloc does, why it matters in 2026, how to add it to your project, when to reach for it, and how it compares to the alternatives — plus a quick FAQ.

## What is bloc?

A predictable state management library that helps implement the BLoC design pattern. It focuses on keeping your UI in sync with your app state as it changes. The project lives at [felangel/bloc](https://github.com/felangel/bloc) and is maintained by `felangel`.

## Why bloc is worth knowing in 2026

bloc carries **12,474 GitHub stars**, **3,417 forks**, 71 open issues. It has been around since 2018, and is actively maintained (updated within the last month). For a State management option, that combination of adoption and upkeep usually means a healthy community, production usage, and plenty of examples to learn from — the things that make a dependency safe to build on.

## Installing bloc

Add the package to your `pubspec.yaml`:

```yaml
dependencies:
  bloc: ^latest
```

Then fetch it and import it in your Dart code:

```bash
flutter pub get
```
```dart
import 'package:bloc/bloc.dart';
```

Check the package's `example/` directory and its [pub.dev page](https://pub.dev/packages/bloc) for the exact API — bloc is versioned there with full docs so you always integrate against the current release.

## When should you use bloc?

Reach for bloc when:

- your widget tree needs to react to shared, changing data
- you want to separate business logic from presentation
- you're scaling past `setState` and need predictable rebuilds

It's especially relevant if your project touches `angulardart`, `bloc`, `concurrency`, `dart`, `dart-library`, `dart-web`.

## bloc vs. the alternatives

If you're weighing options in the **State management** space, these are the other projects developers most often compare bloc against:

- [State management in Flutter with getx: a practical guide](/recipes/getx/)
- [State management in Flutter with flutter_architecture_samples: a practical guide](/recipes/flutter-architecture-samples/)
- [State management in Flutter with riverpod: a practical guide](/recipes/riverpod/)
- [State management in Flutter with fish-redux: a practical guide](/recipes/fish-redux/)

There's no single winner — the right pick depends on your app's size, your team's familiarity, and your performance budget. Browse the full [State management collection](/recipes/) to compare them side by side.

## Frequently asked questions

### Is bloc free to use?

Yes. bloc is open source and free to use in your Flutter projects. You can view the source, report issues, and contribute on GitHub.

### Does bloc work on both iOS and Android?

bloc is built for Flutter, so it targets iOS and Android from a single codebase, and typically web and desktop too depending on the project's platform support.

### How popular is bloc?

As of 2026, bloc has around 12,474 stars and 3,417 forks on GitHub, which puts it among the more widely used options in the State management space.

### What are good alternatives to bloc?

Popular alternatives in the State management category include getx, flutter-architecture-samples, riverpod. The best choice depends on your app's size, team, and performance needs.

### How do I install bloc?

Add bloc to the dependencies section of your pubspec.yaml and run flutter pub get. Full versions and API docs are on pub.dev.

## Resources & links

- **GitHub:** [felangel/bloc](https://github.com/felangel/bloc)
- **pub.dev:** [bloc](https://pub.dev/packages/bloc)
- **Video tutorials:** [search YouTube for bloc](https://www.youtube.com/results?search_query=flutter+bloc)

---

*Part of [FlutterCook](/recipes/) — 500 hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
