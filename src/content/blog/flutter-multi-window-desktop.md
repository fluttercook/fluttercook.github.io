---
title: "Desktop multi-window APIs: popups, dialogs, and windowHandle"
description: "Flutter’s experimental windowing APIs grow with Canonical: popups on Linux/Windows, content-sized windows, and native handle access."
seoDescription: "Flutter multi-window desktop APIs, popup windows Linux Windows, windowHandle HWND NSWindow GtkWindow Canonical partnership."
keywords:
  - flutter multi window desktop
  - flutter popup window linux
  - windowHandle flutter
  - canonical flutter desktop
  - flutter dialog window
tags: ["Flutter", "Desktop", "MultiWindow", "Canonical"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "multiple_windows example"
    url: "https://github.com/flutter/flutter/tree/master/examples/multiple_windows"
related:
  - slug: "flutter-desktop-flavors"
    title: "Desktop Flavors"
  - slug: "flutter-impeller-default-desktop"
    title: "Impeller Default on Desktop"
category: "Deep Dive"
topic: "Desktop"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🪟"
draft: false
---

Desktop apps need more than one surface: context menus, tool palettes, detached inspectors. Flutter’s **experimental windowing APIs**, accelerated by Canonical as Strategic Steward for Flutter Desktop, are how you get there.

![Diagram: Desktop Multi-window APIs](/blog/images/flutter-multi-window-desktop.svg)


## What landed through 3.44 → 3.47

- Tooltip and dialog windows across Linux/macOS/Windows.
- **Popup windows on Linux and Windows** (macOS earlier).
- `showDialog` can create a real child window on platforms that support windowing.
- Content-sized windows and `windowHandle` (`HWND` / `NSWindow` / `GtkWindow`) for advanced native integration.

## When to use it

| Need | API direction |
| --- | --- |
| Context menu / palette | Popup window |
| Detached tool | Regular window + multi-window tests |
| Native docking | `windowHandle` + platform code |

## Status warning

These APIs have been **main-channel / experimental**. Do not ship production multi-window as your only UX path without a fallback. Track the `multiple_windows` example and file issues against the embedders.

## Practical tip

Design your feature so the *primary* workflow still works single-window. Multi-window should be an accelerator, not a hard dependency, until the APIs graduate.
