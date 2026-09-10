---
title: "shadcn-flutter: porting a design system, not a theme"
description: "Tokens, primitives, and composites — how a design-system port stays maintainable."
seoDescription: "shadcn-flutter architecture: design tokens, primitives, composites, Flutter design system port patterns."
keywords:
  - shadcn flutter
  - flutter design system
  - flutter design tokens
  - port shadcn to flutter
  - flutter ui primitives
tags: ["Flutter", "OpenSource", "DesignSystem"]
sources:
  - name: "shadcn-flutter GitHub"
    url: "https://github.com/nank1ro/shadcn-flutter"
related:
  - slug: "oss-forui"
    title: "Forui"
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🎛️"
draft: false
---

Copying a web design system into Flutter fails when you only copy colors. shadcn-flutter is useful because it forces a layered story: tokens → primitives → composites → your app.

![Diagram: shadcn-flutter](/blog/images/oss-shadcn-flutter.svg)



## Steal this

1. Own the source (copy-in model) so you can edit without fork pain.
2. Keep accessibility and focus rings as first-class primitives.
3. Document variants; do not hide them in one mega-widget.

## Pitfalls

Web CSS assumptions (cascading, :hover) do not map 1:1. Budget for desktop pointer polish separately from mobile touch.

Use this when Material defaults fight your brand.
