---
title: "Agentic Hot Reload: when your coding agent reloads the running app"
description: "Flutter 3.44 lets MCP-aware agents discover running apps and trigger hot reload — closing the loop from prompt to pixels."
seoDescription: "Flutter Agentic Hot Reload MCP server, coding agents auto connect and hot reload running apps, Antigravity Gemini CLI Claude Code."
keywords:
  - flutter agentic hot reload
  - flutter mcp server
  - ai coding agent flutter
  - hot reload ai agent
  - dart mcp hot reload
tags: ["Flutter", "AI", "MCP", "HotReload", "Agents"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "Dart & Flutter MCP server"
    url: "https://docs.flutter.dev/ai/mcp-server"
related:
  - slug: "flutter-agent-skills-mcp"
    title: "Agent Skills and MCP"
  - slug: "flutter-genui-a2ui"
    title: "GenUI and A2UI"
category: "Deep Dive"
topic: "AI Tooling"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🤖"
draft: false
---

The old AI loop was: paste error → agent edits file → you manually `r` in the terminal. **Agentic Hot Reload** removes the last step. The Dart/Flutter MCP server helps agents find and connect to a running app, then trigger reload after an edit.

![Diagram: Agentic Hot Reload](/blog/images/flutter-agentic-hot-reload.svg)


## The new loop

1. `flutter run` (debug) with the MCP server available to your agent.
2. Prompt: “make the login button cyan and larger.”
3. Agent edits Dart, triggers reload, you judge the pixels.

No extra glue scripts. Dependency search is hardened so agents can read package sources without full pub-cache access, and tool definitions were consolidated to cut token cost.

## Practical setup tips

- Keep one debug session per device you care about; agents attach to what is running.
- Prefer small UI-scoped prompts — Agentic Hot Reload rewards incremental diffs.
- Pair with Agent Skills so the agent follows your architecture instead of inventing a new one.

## Limits

Hot reload is not hot *restart*. State and native-channel changes still need a restart. If the agent’s change does not appear, check that the session is still connected and that the edit was in a reloadable library (not `main()` reordering that requires restart).
