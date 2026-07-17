---
title: "State management in Flutter with fish-redux: a practical guide"
package: "fish-redux"
repo: "alibaba/fish-redux"
githubUrl: "https://github.com/alibaba/fish-redux"
category: "State management"
stars: 7273
forks: 832
lastUpdate: "2022-02-17"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=flutter+fish-redux"
priority: "Medium"
phase: "P4"
trendRank: 160
description: "An assembled flutter application framework."
seoDescription: "fish-redux: State management for Flutter with 7,273★ on GitHub. An assembled flutter application framework. Install, usage, alternatives & FAQ."
keywords:
  - flutter fish-redux
  - fish-redux flutter
  - flutter state management
  - flutter app state
  - flutter mobile app
  - fish-redux example
  - fish-redux tutorial
topics:
  - adapter
  - aop
  - component
  - flutter
  - framework
  - functional-programming
summary:
  - '**fish-redux** is an open-source state-management library in the **State management**
    category.'
  - It has **7,273★** and 832 forks, and is mature and stable.
  - 'Install it with `fish-redux: ^latest` in your pubspec.yaml.'
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
  - q: Is fish-redux free to use?
    a: Yes. fish-redux is open source and free to use in your Flutter projects. You
      can view the source, report issues, and contribute on GitHub.
  - q: Does fish-redux work on both iOS and Android?
    a: fish-redux is built for Flutter, so it targets iOS and Android from a single
      codebase, and typically web and desktop too depending on the project's platform
      support.
  - q: How popular is fish-redux?
    a: As of 2026, fish-redux has around 7,273 stars and 832 forks on GitHub, which
      puts it among the more widely used options in the State management space.
  - q: What are good alternatives to fish-redux?
    a: Popular alternatives in the State management category include bloc, getx, flutter-architecture-samples.
      The best choice depends on your app's size, team, and performance needs.
datePublished: "2019-03-05"
dateModified: "2022-02-17"
draft: false
---

[`fish-redux`](https://github.com/alibaba/fish-redux) is an open-source **state-management library** for Flutter mobile app development, with **7,273★** on GitHub and last updated on **2022-02-17**. This guide covers what fish-redux does, why it matters in 2026, how to add it to your project, when to reach for it, and how it compares to the alternatives — plus a quick FAQ.

## What is fish-redux?

An assembled flutter application framework. It focuses on keeping your UI in sync with your app state as it changes. The project lives at [alibaba/fish-redux](https://github.com/alibaba/fish-redux) and is maintained by `alibaba`.

## Why fish-redux is worth knowing in 2026

fish-redux carries **7,273 GitHub stars**, **832 forks**, 164 open issues. It has been around since 2019, and is mature and stable. For a State management option, that combination of adoption and upkeep usually means a healthy community, production usage, and plenty of examples to learn from — the things that make a dependency safe to build on.

## Installing fish-redux

Add the package to your `pubspec.yaml`:

```yaml
dependencies:
  fish-redux: ^latest
```

Then fetch it and import it in your Dart code:

```bash
flutter pub get
```
```dart
import 'package:fish_redux/fish_redux.dart';
```

Check the package's `example/` directory and its [GitHub repo](https://github.com/alibaba/fish-redux) for the exact API — fish-redux is versioned there with full docs so you always integrate against the current release.

## When should you use fish-redux?

Reach for fish-redux when:

- your widget tree needs to react to shared, changing data
- you want to separate business logic from presentation
- you're scaling past `setState` and need predictable rebuilds

It's especially relevant if your project touches `adapter`, `aop`, `component`, `flutter`, `framework`, `functional-programming`.

## fish-redux vs. the alternatives

If you're weighing options in the **State management** space, these are the other projects developers most often compare fish-redux against:

- [State management in Flutter with bloc: a practical guide](/recipes/bloc/)
- [State management in Flutter with getx: a practical guide](/recipes/getx/)
- [State management in Flutter with flutter_architecture_samples: a practical guide](/recipes/flutter-architecture-samples/)
- [State management in Flutter with riverpod: a practical guide](/recipes/riverpod/)

There's no single winner — the right pick depends on your app's size, your team's familiarity, and your performance budget. Browse the full [State management collection](/recipes/) to compare them side by side.

## Frequently asked questions

### Is fish-redux free to use?

Yes. fish-redux is open source and free to use in your Flutter projects. You can view the source, report issues, and contribute on GitHub.

### Does fish-redux work on both iOS and Android?

fish-redux is built for Flutter, so it targets iOS and Android from a single codebase, and typically web and desktop too depending on the project's platform support.

### How popular is fish-redux?

As of 2026, fish-redux has around 7,273 stars and 832 forks on GitHub, which puts it among the more widely used options in the State management space.

### What are good alternatives to fish-redux?

Popular alternatives in the State management category include bloc, getx, flutter-architecture-samples. The best choice depends on your app's size, team, and performance needs.

## Resources & links

- **GitHub:** [alibaba/fish-redux](https://github.com/alibaba/fish-redux)
- **Video tutorials:** [search YouTube for fish-redux](https://www.youtube.com/results?search_query=flutter+fish-redux)

---

*Part of [FlutterCook](/recipes/) — 500 hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
