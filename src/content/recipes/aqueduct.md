---
title: "State management in Flutter with aqueduct: a practical guide"
package: "aqueduct"
repo: "stablekernel/aqueduct"
githubUrl: "https://github.com/stablekernel/aqueduct"
category: "State management"
stars: 2386
forks: 271
lastUpdate: "2021-03-26"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+aqueduct"
priority: "Medium"
phase: "P6"
trendRank: 269
description: "Dart HTTP server framework for building REST APIs. Includes PostgreSQL ORM and OAuth2 provider."
seoDescription: "aqueduct: State management for Flutter with 2,386★ on GitHub. Dart HTTP server framework for building REST APIs. Includes PostgreSQL ORM and OAuth2 provider.…"
keywords:
  - flutter aqueduct
  - aqueduct flutter
  - flutter state management
  - flutter app state
  - flutter mobile app
  - aqueduct example
  - aqueduct tutorial
topics:
  - dart
  - framework
  - http
  - oauth2
  - orm
  - rest
summary:
  - '**aqueduct** is an open-source state-management library in the **State management**
    category.'
  - It has **2,386★** and 271 forks, and is mature and stable.
  - 'Install it with `aqueduct: ^latest` in your pubspec.yaml.'
  - Best when your widget tree needs to react to shared, changing data.
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
  - q: Is aqueduct free to use?
    a: Yes. aqueduct is open source and free to use in your Flutter projects. You can
      view the source, report issues, and contribute on GitHub.
  - q: Does aqueduct work on both iOS and Android?
    a: aqueduct is built for Flutter, so it targets iOS and Android from a single codebase,
      and typically web and desktop too depending on the project's platform support.
  - q: How popular is aqueduct?
    a: As of 2026, aqueduct has around 2,386 stars and 271 forks on GitHub, which puts
      it among the more widely used options in the State management space.
  - q: What are good alternatives to aqueduct?
    a: Popular alternatives in the State management category include bloc, getx, flutter-architecture-samples.
      The best choice depends on your app's size, team, and performance needs.
datePublished: "2015-05-29"
dateModified: "2021-03-26"
draft: false
---

[`aqueduct`](https://github.com/stablekernel/aqueduct) is an open-source **state-management library** for Flutter mobile app development, with **2,386★** on GitHub and last updated on **2021-03-26**. This guide covers what aqueduct does, why it matters in 2026, how to add it to your project, when to reach for it, and how it compares to the alternatives — plus a quick FAQ.

## What is aqueduct?

Dart HTTP server framework for building REST APIs. Includes PostgreSQL ORM and OAuth2 provider. It focuses on keeping your UI in sync with your app state as it changes. The project lives at [stablekernel/aqueduct](https://github.com/stablekernel/aqueduct) and is maintained by `stablekernel`.

## Why aqueduct is worth knowing in 2026

aqueduct carries **2,386 GitHub stars**, **271 forks**, 176 open issues. It has been around since 2015, and is mature and stable. For a State management option, that combination of adoption and upkeep usually means a healthy community, production usage, and plenty of examples to learn from — the things that make a dependency safe to build on.

## Installing aqueduct

Add the package to your `pubspec.yaml`:

```yaml
dependencies:
  aqueduct: ^latest
```

Then fetch it and import it in your Dart code:

```bash
flutter pub get
```
```dart
import 'package:aqueduct/aqueduct.dart';
```

Check the package's `example/` directory and its [GitHub repo](https://github.com/stablekernel/aqueduct) for the exact API — aqueduct is versioned there with full docs so you always integrate against the current release.

## When should you use aqueduct?

Reach for aqueduct when:

- your widget tree needs to react to shared, changing data
- you want to separate business logic from presentation
- you're scaling past `setState` and need predictable rebuilds

It's especially relevant if your project touches `dart`, `framework`, `http`, `oauth2`, `orm`, `rest`.

## aqueduct vs. the alternatives

If you're weighing options in the **State management** space, these are the other projects developers most often compare aqueduct against:

- [State management in Flutter with bloc: a practical guide](/recipes/bloc/)
- [State management in Flutter with getx: a practical guide](/recipes/getx/)
- [State management in Flutter with flutter_architecture_samples: a practical guide](/recipes/flutter-architecture-samples/)
- [State management in Flutter with riverpod: a practical guide](/recipes/riverpod/)

There's no single winner — the right pick depends on your app's size, your team's familiarity, and your performance budget. Browse the full [State management collection](/recipes/) to compare them side by side.

## Frequently asked questions

### Is aqueduct free to use?

Yes. aqueduct is open source and free to use in your Flutter projects. You can view the source, report issues, and contribute on GitHub.

### Does aqueduct work on both iOS and Android?

aqueduct is built for Flutter, so it targets iOS and Android from a single codebase, and typically web and desktop too depending on the project's platform support.

### How popular is aqueduct?

As of 2026, aqueduct has around 2,386 stars and 271 forks on GitHub, which puts it among the more widely used options in the State management space.

### What are good alternatives to aqueduct?

Popular alternatives in the State management category include bloc, getx, flutter-architecture-samples. The best choice depends on your app's size, team, and performance needs.

## Resources & links

- **GitHub:** [stablekernel/aqueduct](https://github.com/stablekernel/aqueduct)
- **Video tutorials:** [search YouTube for aqueduct](https://www.youtube.com/results?search_query=flutter+aqueduct)

---

*Part of [FlutterCook](/recipes/) — 500 hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
