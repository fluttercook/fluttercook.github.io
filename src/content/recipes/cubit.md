---
title: "State management in Flutter with cubit: a practical guide"
package: "cubit"
repo: "felangel/cubit"
githubUrl: "https://github.com/felangel/cubit"
category: "State management"
stars: 597
forks: 25
lastUpdate: "2020-07-09"
pubDev: "https://pub.dev/packages/cubit"
youtube: "https://www.youtube.com/results?search_query=flutter+cubit"
priority: "Low"
phase: "P9"
trendRank: 439
description: "Cubit is a lightweight state management solution. It is a subset of the bloc package that does not rely on events and instead uses methods to emit new states."
seoDescription: "cubit: State management for Flutter with 597★ on GitHub. Cubit is a lightweight state management solution. It is a subset of the bloc package that does not…"
keywords:
  - flutter cubit
  - cubit flutter
  - flutter state management
  - flutter app state
  - flutter mobile app
  - cubit example
  - cubit tutorial
topics:
  - dart
  - dart-library
  - dart-package
  - dartlang
  - flutter
  - flutter-package
related:
  - slug: bloc
    title: 'State management in Flutter with bloc: a practical guide'
  - slug: getx
    title: 'State management in Flutter with getx: a practical guide'
  - slug: flutter-architecture-samples
    title: 'State management in Flutter with flutter_architecture_samples: a practical
      guide'
  - slug: riverpod
    title: 'State management in Flutter with riverpod: a practical guide'
faq:
  - q: Is cubit free to use?
    a: Yes. cubit is open source and free to use in your Flutter projects. You can view
      the source, report issues, and contribute on GitHub.
  - q: Does cubit work on both iOS and Android?
    a: cubit is built for Flutter, so it targets iOS and Android from a single codebase,
      and typically web and desktop too depending on the project's platform support.
  - q: How popular is cubit?
    a: As of 2026, cubit has around 597 stars and 25 forks on GitHub, which puts it
      among the more widely used options in the State management space.
  - q: What are good alternatives to cubit?
    a: Popular alternatives in the State management category include bloc, getx, flutter-architecture-samples.
      The best choice depends on your app's size, team, and performance needs.
  - q: How do I install cubit?
    a: Add cubit to the dependencies section of your pubspec.yaml and run flutter pub
      get. Full versions and API docs are on pub.dev.
datePublished: "2020-06-04"
dateModified: "2020-07-09"
draft: false
---

[`cubit`](https://github.com/felangel/cubit) is an open-source **state-management library** for Flutter mobile app development, with **597★** on GitHub and last updated on **2020-07-09**. This guide covers what cubit does, why it matters in 2026, how to add it to your project, when to reach for it, and how it compares to the alternatives — plus a quick FAQ.

## What is cubit?

Cubit is a lightweight state management solution. It is a subset of the bloc package that does not rely on events and instead uses methods to emit new states. It focuses on keeping your UI in sync with your app state as it changes. The project lives at [felangel/cubit](https://github.com/felangel/cubit) and is maintained by `felangel`.

## Why cubit is worth knowing in 2026

cubit carries **597 GitHub stars**, **25 forks**, 0 open issues. It has been around since 2020, and is mature and stable. For a State management option, that combination of adoption and upkeep usually means a healthy community, production usage, and plenty of examples to learn from — the things that make a dependency safe to build on.

## Installing cubit

Add the package to your `pubspec.yaml`:

```yaml
dependencies:
  cubit: ^latest
```

Then fetch it and import it in your Dart code:

```bash
flutter pub get
```
```dart
import 'package:cubit/cubit.dart';
```

Check the package's `example/` directory and its [pub.dev page](https://pub.dev/packages/cubit) for the exact API — cubit is versioned there with full docs so you always integrate against the current release.

## When should you use cubit?

Reach for cubit when:

- your widget tree needs to react to shared, changing data
- you want to separate business logic from presentation
- you're scaling past `setState` and need predictable rebuilds

It's especially relevant if your project touches `dart`, `dart-library`, `dart-package`, `dartlang`, `flutter`, `flutter-package`.

## cubit vs. the alternatives

If you're weighing options in the **State management** space, these are the other projects developers most often compare cubit against:

- [State management in Flutter with bloc: a practical guide](/recipes/bloc/)
- [State management in Flutter with getx: a practical guide](/recipes/getx/)
- [State management in Flutter with flutter_architecture_samples: a practical guide](/recipes/flutter-architecture-samples/)
- [State management in Flutter with riverpod: a practical guide](/recipes/riverpod/)

There's no single winner — the right pick depends on your app's size, your team's familiarity, and your performance budget. Browse the full [State management collection](/recipes/) to compare them side by side.

## Frequently asked questions

### Is cubit free to use?

Yes. cubit is open source and free to use in your Flutter projects. You can view the source, report issues, and contribute on GitHub.

### Does cubit work on both iOS and Android?

cubit is built for Flutter, so it targets iOS and Android from a single codebase, and typically web and desktop too depending on the project's platform support.

### How popular is cubit?

As of 2026, cubit has around 597 stars and 25 forks on GitHub, which puts it among the more widely used options in the State management space.

### What are good alternatives to cubit?

Popular alternatives in the State management category include bloc, getx, flutter-architecture-samples. The best choice depends on your app's size, team, and performance needs.

### How do I install cubit?

Add cubit to the dependencies section of your pubspec.yaml and run flutter pub get. Full versions and API docs are on pub.dev.

## Resources & links

- **GitHub:** [felangel/cubit](https://github.com/felangel/cubit)
- **pub.dev:** [cubit](https://pub.dev/packages/cubit)
- **Video tutorials:** [search YouTube for cubit](https://www.youtube.com/results?search_query=flutter+cubit)

---

*Part of [FlutterCook](/recipes/) — 500 hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
