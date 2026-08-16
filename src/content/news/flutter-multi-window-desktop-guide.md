---
title: "Multi-window on Flutter desktop: what shipped in 3.47, and what to use today"
description: "Flutter 3.47 added popup windows on Win32 and Linux, sized-to-content windows, and renamed the windowing API. The multi-window APIs are still experimental — here is the practical picture."
seoDescription: "Flutter desktop multi-window guide: popup windows on Windows and Linux, sized-to-content, size and constraints API rename, --flavor support, and the experimental main-channel status."
keywords: ["flutter multi window", "flutter desktop windows", "flutter popup window", "desktop_multi_window package", "flutter windowing api", "flutter desktop flavor"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🪟"
tags: ["Flutter 3.47", "Flutter", "Desktop", "Windows", "Linux"]
sources:
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Add experimental APIs for multi-window scenarios — flutter/flutter#171720"
    url: "https://github.com/flutter/flutter/issues/171720"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "desktop_multi_window on pub.dev"
    url: "https://pub.dev/packages/desktop_multi_window"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Multi-window is the oldest item on the Flutter desktop wishlist. A desktop app that cannot open a second window is not really a desktop app — no detached inspector, no tear-off panel, no floating tool palette, no proper context menu that escapes the main window's bounds.

Flutter 3.41 shipped experimental multi-window APIs for desktop. Flutter 3.47 fills in a large amount of the plumbing underneath them. What it does not do is make them stable, and being clear about that distinction will save you a painful quarter.

## What actually landed in 3.47

The desktop work in this release is mostly engine-level, and it is substantial:

**Popup windows.** Win32 and Linux both got popup window implementations. This is the foundation for menus, tooltips, and dropdowns that render outside the parent window's bounds — a category of UI that Flutter desktop has faked with overlays until now.

**Sized-to-content windows.** Regular and dialog windows can now size themselves to their content on Win32, and the `decorated` flag was removed from the windowing API in the process. A dialog that is exactly as tall as its text is a small thing that makes an app feel native.

**An API rename.** `preferredSize` became **`size`**, and `preferredConstraints` became **`constraints`**. If you have been tracking the experimental API on main, this one will break your code, and the rename is a signal in itself: the team is tidying the surface, which usually precedes stabilisation.

**Platform handles are now exposed.** The multi-window API can hand you platform-specific window handles — the escape hatch you need for native integration that Flutter does not model.

**A public API to post tasks to the platform thread** on Windows. Unglamorous, and necessary for anything that has to touch Win32 from Dart.

**`--flavor` support for Windows and Linux desktop builds.** Long overdue. Multiple build flavors — dev, staging, production — finally work on desktop the way they do on mobile.

## The status you need to internalise

The Flutter team's own framing on the tracking issue is explicit. The multi-window APIs are **experimental**, and the stated goals are to build confidence by letting customers dogfood them **on Flutter's main release channel**, while retaining the ability to change them.

Both halves of that sentence matter:

- **Main channel**, not stable. You are not getting these APIs on the stable release you ship from.
- **Ability to change them.** The `preferredSize` → `size` rename in this very release is proof that they mean it.

| | Experimental framework API | `desktop_multi_window` and similar packages |
| --- | --- | --- |
| Channel | main | works on stable |
| API stability | explicitly subject to change | package-versioned, semver |
| Long-term direction | this is where Flutter is going | community-maintained |
| Suitable for shipping now | no | yes, with the usual package caveats |

## So what do you actually use today

If you need multi-window in a production app on the stable channel, the answer is still a community package — `desktop_multi_window` being the most established of them. It creates additional native windows and runs a separate Flutter engine instance in each, with a message channel between them.

That architecture has a consequence worth understanding before you adopt it: **each window is a separate engine, so they do not share Dart state.** Your `Provider`, your `Bloc`, your singletons — none of them cross the window boundary. Everything is message passing:

```dart
// Conceptually: each window runs its own engine and entry point.
// Shared state must be serialised across a channel, not read directly.
void main(List<String> args) {
  if (args.firstOrNull == 'multi_window') {
    // Secondary window entry point — separate isolate, separate state.
    runApp(const SecondaryWindowApp());
    return;
  }
  runApp(const MainApp());
}
```

Design for that from the start. Teams that bolt multi-window onto an app with a single global store spend most of their time reimplementing state synchronisation.

The experimental framework API takes a different approach — multiple windows within one engine — which is why it is the better long-term answer and why it is taking time to get right.

## Where desktop stands more broadly

Some context from the Q2 2026 survey: **Windows satisfaction is 74%, Linux is 73%** — the lowest platform scores after Cupertino. The top developer pain point overall is platform and ecosystem maturity at **44%**.

Multi-window is a big part of why. Flutter desktop has been production-capable for years, but the gap between "works" and "feels native" has been filled with missing window management primitives. The 3.47 changes — popup windows, sized-to-content, flavors — are unglamorous and directly target that gap.

## A practical plan

1. **If you ship on stable today**, use a community multi-window package and design for message passing between engines from day one.
2. **If you are tracking main**, adopt the experimental API now and expect to fix renames each release. The `preferredSize` → `size` change is a template for what is coming.
3. **Adopt `--flavor` on Windows and Linux immediately.** This one is not experimental and it is a straightforward win for your build pipeline.
4. **Audit your overlay-based menus and tooltips.** Once popup windows are available on your channel, anything that currently clips at the window edge can be fixed properly.
5. **Do not architect around shared global state** across windows. Serialise, or you will rewrite it.
6. **Test window behaviour on multi-monitor setups with mixed DPI.** This is where desktop window bugs actually live.
7. **File bugs against the experimental API.** Dogfooding is the stated purpose; feedback now shapes what stabilises.

## The bottom line

Flutter 3.47 is a serious desktop release even though the headline feature list barely mentions desktop. Popup windows on two platforms, sized-to-content windows, exposed platform handles, and flavor support are exactly the unexciting primitives that separate a port from a native-feeling application. The multi-window API itself is still experimental and still main-channel, so ship with a package for now — but the direction is unambiguous, and the API rename in this release suggests the team is cleaning up ahead of stabilisation rather than still exploring.
