---
title: "Agent Skills for Dart and Flutter: teaching your AI the framework it keeps getting wrong"
description: "Google shipped official Agent Skills for Dart and Flutter. Here is what a Skill is, how it differs from MCP, the ten Flutter skills available, and how to install them."
seoDescription: "Guide to Flutter and Dart Agent Skills: npx skills add flutter/skills, the ten official skills, how Skills differ from MCP servers, and why stale model knowledge breaks on Flutter 3.47."
keywords: ["flutter agent skills", "dart agent skills", "flutter ai coding", "npx skills add flutter", "flutter mcp server", "ai coding tools flutter 2026"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🤖"
tags: ["Flutter 3.47", "Flutter", "AI", "Agent Skills", "Tooling"]
sources:
  - name: "Introducing Skills for Dart and Flutter — Flutter Blog"
    url: "https://flutter.dev/blog/introducing-skills-for-dart-and-flutter"
  - name: "flutter/skills on GitHub"
    url: "https://github.com/flutter/skills"
  - name: "dart-lang/skills on GitHub"
    url: "https://github.com/dart-lang/skills"
  - name: "Flutter Q2 2026 survey results"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

The Q2 2026 survey contains one statistic that reframes how Flutter tooling should be designed: **Claude Code at 32% adoption and Antigravity at 23%**, both ahead of GitHub Copilot (19%), Cursor (18%) and Codex (17%). Agentic tools have overtaken the autocomplete generation. Roughly a third of Flutter developers now have an agent writing meaningful amounts of their code.

Which creates a problem the framework itself has to solve, because Flutter moves faster than model training data. Flutter 3.47 just changed the import path for the two most-used libraries in the ecosystem. Every model trained before August 2026 will confidently write `package:flutter/material.dart` forever.

**Agent Skills** are Google's answer.

## What a Skill actually is

A Skill is a task-oriented instruction set that teaches an agent *how* to perform a specific development job — not reference documentation, but a procedure.

The framing from the announcement is the clearest way to hold this in your head: **MCP provides the hammer and nails; a Skill provides the blueprint and the professional know-how to build the house.** An MCP server gives an agent capabilities — run the analyzer, launch a simulator, read a file. A Skill tells it what good work looks like when using those capabilities.

The practical consequence is token efficiency. Skills load progressively, only when relevant to what you asked for. You are not pasting a style guide into every prompt and paying for it on every turn.

| | MCP server | Agent Skill |
| --- | --- | --- |
| Provides | Tools and capabilities | Procedure and judgement |
| Analogy | Hammer and nails | Blueprint and know-how |
| Loaded | Connected for the session | Progressively, when relevant |
| Answers | "What can I do?" | "How should I do this well?" |

## The ten Flutter skills

The `flutter/skills` repository ships these:

- **`flutter-add-integration-test`** — configures Flutter Driver and converts interactions into permanent integration tests
- **`flutter-add-widget-test`** — component-level testing with `WidgetTester` to verify rendering and interaction
- **`flutter-add-widget-preview`** — adds interactive widget previews for UI component validation
- **`flutter-apply-architecture-best-practices`** — structures an app along the recommended UI / Logic / Data layering
- **`flutter-build-responsive-layout`** — adaptive layouts using `LayoutBuilder`, `MediaQuery`, or `Expanded`/`Flexible`
- **`flutter-fix-layout-issues`** — resolves overflow and unbounded-constraint errors
- **`flutter-implement-json-serialization`** — model classes with `fromJson` and `toJson`
- **`flutter-setup-declarative-routing`** — configures `MaterialApp.router` with a package like `go_router`
- **`flutter-setup-localization`** — initialises localization with `flutter_localizations` and `intl`
- **`flutter-use-http-package`** — REST requests with the `http` package

The Dart skills live separately in `dart-lang/skills`, covering language-level work such as pattern-matching refactors and collecting LCOV coverage.

Look at that list as a set and the selection logic becomes obvious. These are not exotic tasks. They are the jobs where an agent left to its own devices produces something that compiles, runs, and is subtly wrong — a layout that works on one screen size, a router configured imperatively, a model class that silently drops a nullable field.

## Installing them

Skills install through a single command per repository:

```bash
npx skills add flutter/skills --skill '*' --agent universal
npx skills add dart-lang/skills --skill '*' --agent universal
```

You then select the skills you want and the agent you use. The `--agent universal` target is what makes this portable across the tools in that survey chart rather than tied to one vendor.

Installing everything with `'*'` is the fast path. For a team repository, being selective is usually better — install the skills that match your actual conventions, and leave out the ones that would fight your existing architecture.

## Where this pays off most

The highest-value case is exactly the situation Flutter 3.47 created. Consider what an agent with stale knowledge produces today:

```dart
// What a model trained before August 2026 writes
import 'package:flutter/material.dart';
```

```dart
// What Flutter 3.47 wants
import 'package:material_ui/material_ui.dart';
```

Both compile right now, because the SDK libraries still exist. One of them starts emitting deprecation warnings in November. An agent has no way to know which is current unless something tells it — and "something" is either a Skill, an MCP server exposing live docs, or you correcting it every single time.

The same applies to `@Preview` annotations, Impeller-aware performance advice, and Swift Package Manager rather than CocoaPods. Every one of those changed inside the last two releases.

## Skills do not replace review

Worth stating plainly, because the survey has a relevant number: developers trust community "battle-tested" features at **41%** versus **26%** for Google-built features. That scepticism is healthy and should extend here.

A Skill improves the *distribution* of an agent's output — fewer wrong-by-default answers, more consistency with framework conventions. It does not make the output correct. `flutter-apply-architecture-best-practices` will impose a layering on your codebase; whether that layering suits your app is your call, not the agent's.

Read the generated diff. Run the tests. The Skill has made the agent a better junior, not a senior.

## Getting set up

1. **Check which agent you actually use.** VS Code (66%) and Android Studio (40%) remain where most Flutter work happens; install for the agent running inside your editor.
2. **Run both `npx skills add` commands** for `flutter/skills` and `dart-lang/skills`.
3. **Start selective.** Install `flutter-fix-layout-issues` and `flutter-add-widget-test` first — the two with the least architectural opinion.
4. **Test on a known task.** Ask the agent to write a widget test for an existing component and compare against what you would have written.
5. **Add the opinionated ones** — architecture, routing — only after you have confirmed they match your conventions.
6. **Pin your framework version in the prompt** when working on migration-sensitive code. Skills help; explicit context helps more.
7. **Re-run the install after major releases** so the skill definitions track the framework.

## The bottom line

The interesting thing about Agent Skills is not that Google shipped an AI feature. It is the admission behind it: a third of the user base now writes code through an agent, and the framework's release cadence has outrun the models' knowledge cutoffs. Skills are infrastructure for that gap. They will not make your agent a senior Flutter engineer, but they will stop it confidently importing a library that gets deprecated in November — and on a codebase of any size, that is worth the two commands.
