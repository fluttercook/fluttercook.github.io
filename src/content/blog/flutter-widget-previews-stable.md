---
title: "Widget Previews are stable: iterate on UI without booting the whole app"
description: "Flutter 3.47 graduates Widget Previewer to stable with faster startup, theme matrices, and web asset sync."
seoDescription: "Flutter Widget Previews stable 3.47, PreviewThemeData, widget previewer faster startup isolated UI iteration."
keywords:
  - flutter widget previews
  - flutter widget previewer
  - PreviewThemeData
  - flutter ui preview stable
  - isolated widget preview
tags: ["Flutter", "DevTools", "WidgetPreview", "DX"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Widget Previewer docs"
    url: "https://docs.flutter.dev/tools/widget-previewer"
related:
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
  - slug: "flutter-agentic-hot-reload"
    title: "Agentic Hot Reload"
category: "Deep Dive"
topic: "Tooling"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔍"
draft: false
---

Booting a full app to tweak a button is slow. **Widget Preview** renders individual widgets in isolation. After experimental cycles, it is **stable in Flutter 3.47**.

![Diagram: Widget Previews Stable](/blog/images/flutter-widget-previews-stable.svg)


## What stable means here

- Faster startup via a local `.widget_preview/` cache.
- `PreviewThemeData` for sequential theme layering (matrix tests across seeds/contrast).
- Automatic `web/` asset sync when previewing web widgets.

## Workflow that pays off

1. Extract the widget you are changing into a previewable class.
2. Add previews for default / dark / large-text / empty-data.
3. Iterate until the preview is boring — then wire it into the app.

This is also the fastest loop for design-system work on `material_ui` / custom catalogs.

## Pitfalls

- Previews that hit `dart:io` or platform channels will not run — isolate pure UI.
- Do not put business logic in previews; put fixtures there.
