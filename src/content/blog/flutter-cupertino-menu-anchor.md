---
title: "CupertinoMenuAnchor and modern Flutter menus"
description: "RawMenuAnchor powers CupertinoMenuAnchor and animated Material MenuAnchor — native-feeling menus without plugin stacks."
seoDescription: "Flutter CupertinoMenuAnchor RawMenuAnchor, Material MenuAnchor hoverOpenDelay, native iOS menus in Flutter 3.44."
keywords:
  - flutter cupertino menu anchor
  - RawMenuAnchor
  - flutter ios context menu
  - MenuAnchor animation material
  - flutter submenu hoverOpenDelay
tags: ["Flutter", "Cupertino", "Material", "Menus"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "CupertinoMenuAnchor API"
    url: "https://api.flutter.dev/flutter/cupertino/CupertinoMenuAnchor-class.html"
  - name: "MenuAnchor API"
    url: "https://api.flutter.dev/flutter/material/MenuAnchor-class.html"
related:
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
  - slug: "flutter-widget-previews-stable"
    title: "Widget Previews Stable"
category: "Deep Dive"
topic: "UI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📋"
draft: false
---

Menus are where Flutter apps most often feel “webby.” **RawMenuAnchor** is the shared primitive; Cupertino and Material both build on it.

![Diagram: Cupertino Menu Anchor](/blog/images/flutter-cupertino-menu-anchor.svg)


## Cupertino

`CupertinoMenuAnchor` (community-led, notably davidhicks980) gives iOS apps a menu that behaves like UIKit: dismiss physics, nesting, and focus that match platform expectations.

## Material

`MenuAnchor` gains optional Material 3 animations (`animated: true`) and `SubmenuButton.hoverOpenDelay` for desktop hover behavior.

## Decision table

| Target | Prefer |
| --- | --- |
| iOS-first product | CupertinoMenuAnchor |
| Desktop dense UI | MenuAnchor + hoverOpenDelay |
| Cross-platform brand | Adaptive wrapper choosing by platform |

## Pitfalls

- Callback close order changed on RawMenuAnchor — read the breaking-change note before upgrading.
- Do not rebuild the entire menu tree on every pointer event; keep anchors stable.
