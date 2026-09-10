---
title: "GenUI and A2UI: agents that compose widgets, not markdown"
description: "The GenUI SDK and A2UI protocol let agents build live Flutter UI — a shift from chat walls of text to structured, interactive experiences."
seoDescription: "Flutter GenUI SDK A2UI protocol, generative UI beyond chat, compose widgets from agent responses, Finnish It Hatcha examples."
keywords:
  - flutter genui
  - a2ui protocol
  - generative ui flutter
  - flutter ai ui agent
  - a2ui flutter sdk
tags: ["Flutter", "GenUI", "A2UI", "AI", "UX"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "genui package"
    url: "https://pub.dev/packages/genui"
  - name: "A2UI"
    url: "https://a2ui.org/"
related:
  - slug: "flutter-firebase-ai-logic"
    title: "Firebase AI Logic"
  - slug: "flutter-agentic-hot-reload"
    title: "Agentic Hot Reload"
category: "Deep Dive"
topic: "AI"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "✨"
draft: false
---

Chat UIs trained users to accept walls of markdown. **Generative UI (GenUI)** flips the contract: the model proposes *UI structure* — lists, forms, cards — and Flutter renders real widgets with real state.

![Diagram: GenUI and A2UI](/blog/images/flutter-genui-a2ui.svg)


## What A2UI is

[A2UI](https://a2ui.org/) is an open protocol describing how an **agent** and a **client** collaborate on UI composition and state. Flutter’s GenUI SDK implements the client side. Package downloads grew sharply through 2026 as teams shipped beyond demos (for example language-learning apps that compose lesson UI on the fly).

## Architecture sketch

1. User intent goes to your backend/agent.
2. Agent emits A2UI structure (not free text).
3. GenUI maps structure → Flutter widgets in a constrained catalog.
4. Events flow back as structured actions the agent can handle.

## Design constraints that make it work

- **Catalog over chaos.** Allow only widgets you designed; do not let the model invent layout physics.
- **Critic loop.** Validate agent output before paint (empty states, overflow, a11y labels).
- **Templates for speed.** Hybrid: strong templates + model-filled slots beats pure generation for reliability.

## Pitfalls

- Treating GenUI as a theming engine — it is a composition protocol.
- Skipping offline/error UI because “the model will fix it.”
- Shipping without human-readable fallbacks when the catalog cannot express the answer.
