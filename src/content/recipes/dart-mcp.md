---
title: "dart-lang/ai: Dart's official MCP packages"
package: "dart_mcp"
repo: "dart-lang/ai"
githubUrl: "https://github.com/dart-lang/ai"
category: "AI/ML"
stars: 279
forks: 73
lastUpdate: "2026-08-28"
pubDev: "https://pub.dev/packages/dart_mcp"
youtube: "https://www.youtube.com/results?search_query=dart+mcp+server+flutter"
priority: "High"
phase: "P1"
trendRank: 0
description: "The Dart team's own repository for AI and GenAI packages: dart_mcp for building MCP servers and clients, dart_mcp_server exposing Dart tooling to AI models, and skills for managing agent skills."
seoDescription: "dart-lang/ai holds Dart's official MCP packages - dart_mcp, dart_mcp_server and skills. What each one does, how to wire dart_mcp_server into Claude Code or Cursor, and when to build your own server."
keywords:
  - dart mcp
  - dart_mcp_server
  - flutter mcp server
  - model context protocol dart
  - flutter ai agent tooling
  - dart ai packages
topics:
  - mcp
  - ai
  - dart
summary:
  - "**dart-lang/ai** is the Dart team's official home for AI and GenAI packages, maintained under `dart-lang`."
  - "It ships three: `dart_mcp` (build MCP servers and clients), `dart_mcp_server` (exposes Dart developer tools to AI models), and `skills` (a CLI for skills shipped in packages or git repos)."
  - "`dart_mcp_server` is the one most Flutter developers want first - it gives an AI agent real access to analysis, tests and pub."
  - "**279★**, BSD-3-Clause, actively developed with 81 open issues across the three packages."
related:
  - slug: flutter-skill
    title: "flutter-skill: let an AI agent drive your running app"
  - slug: agent-plugins
    title: "agent-plugins: a Flutter developer's guide"
  - slug: genui
    title: "Build better Flutter UI with genui"
  - slug: flutter-zero
    title: "Flutter Zero: Flutter with dart:ui taken out"
faq:
  - q: What is the difference between dart_mcp and dart_mcp_server?
    a: "dart_mcp is a library - you use it to write your own MCP servers and clients in Dart. dart_mcp_server is a finished server built with it, which exposes Dart and Flutter developer tooling to an AI model. If you want an agent that can analyse and test your project, you want dart_mcp_server. If you want to expose your own domain to an agent, you want dart_mcp."
  - q: Is this an official Dart team project?
    a: "Yes. It lives under the dart-lang organisation alongside the SDK and core packages, and all three packages are published to pub.dev under the same BSD-3-Clause licence as the rest of Dart."
  - q: Which AI tools can use dart_mcp_server?
    a: "Any MCP client that speaks stdio. The README gives setup steps for Gemini CLI, Gemini Code Assist, Cursor and GitHub Copilot in VS Code, but the protocol is the interface - the server does not care which client connects, as long as it supports Tools and Resources."
  - q: What is the skills package for?
    a: "It is a CLI for managing skills shipped inside packages and pulled from git repositories. It is the newest of the three and the least settled, so check its own README before depending on its interface."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`dart-lang/ai`](https://github.com/dart-lang/ai) is where the Dart team keeps its AI and GenAI work. It is not a framework and not a product — it is a monorepo of three focused packages, and one of them is probably the single highest-leverage thing a Flutter developer can install this year. **279★**, BSD-3-Clause, last pushed **2026-08-28**.

## What is in the repository?

Three published packages, each with its own scope:

| Package | What it does |
| --- | --- |
| [`dart_mcp`](https://pub.dev/packages/dart_mcp) | A library for building MCP servers *and* clients in Dart |
| [`dart_mcp_server`](https://pub.dev/packages/dart_mcp_server) | A finished MCP server that exposes Dart project tooling to AI models |
| [`skills`](https://pub.dev/packages/skills) | A CLI for managing skills shipped in packages and from git repos |

The Model Context Protocol is the plumbing that lets an AI assistant call real tools instead of guessing. `dart_mcp` is the Dart implementation of both halves of that protocol.

## Why it matters in 2026

Most "AI in your editor" setups are still working from text alone. The model reads your files, predicts what the analyzer would say, and is wrong often enough to be annoying. An MCP server closes that loop: the agent stops predicting the analyzer's output and starts *running* it.

`dart_mcp_server` is the practical version of that for Dart and Flutter. Point an agent at it and the agent gains real access to your project's tooling rather than a plausible impression of it. Analysis errors are actual analysis errors. A test result is an actual test result.

That it comes from `dart-lang` rather than a third party matters more than it might sound. Tooling that shells out to `dart` and `flutter` breaks whenever the SDK changes its output format. A server maintained next to the SDK does not have that problem.

## Getting started

The server is the thing most people want first, and there is nothing to install — it ships inside the Dart SDK from 3.9 onwards and runs as `dart mcp-server`. You only have to register it with your client. For Gemini CLI or Cursor, that is a block in `.gemini/settings.json` or `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dart": {
      "command": "dart",
      "args": ["mcp-server"]
    }
  }
}
```

For GitHub Copilot in VS Code there is a shortcut — one setting, and the Dart extension registers the server for you:

```json
"dart.mcpServer": true
```

Any MCP client that speaks stdio will work; the server needs Tools and Resources support, and behaves best with Roots. Once it is connected you can usually just ask the agent to connect to your running app — it discovers Dart Tooling Daemon instances on your machine and finds the Flutter or Dart applications registered with them.

To build your own server, depend on the library:

```bash
dart pub add dart_mcp
```

## When should you use these?

- you want your coding agent to run the analyzer and the test suite for real, not imagine them
- you are building a Dart or Flutter tool and want AI clients to drive it through a standard protocol
- you maintain internal tooling and would rather expose it once over MCP than write an integration per assistant
- you are packaging reusable agent skills and want them versioned with the package that owns them

## Where it falls short

The three packages are at very different maturities, and the server's own README opens by calling itself experimental and likely to evolve quickly. Take that at face value: the tool list and flags still move between releases. `skills` is newer still and the least settled — read its README rather than assuming its interface will hold.

The repository also carries 81 open issues, which is a fair reflection of how quickly the MCP surface is changing rather than any neglect. If you pin versions anywhere, pin them here.

And a scoping note: this is *Dart* AI tooling, not *Flutter UI* AI tooling. For generating interfaces from a model, see [genui](/recipes/genui/); for driving a running app, see [flutter-skill](/recipes/flutter-skill/).

## Alternatives worth comparing

- [flutter-skill: let an AI agent drive your running app](/recipes/flutter-skill/) — MCP for the runtime rather than the toolchain
- [agent-plugins: a Flutter developer's guide](/recipes/agent-plugins/)
- [Build better Flutter UI with genui](/recipes/genui/)

## Frequently asked questions

### What is the difference between dart_mcp and dart_mcp_server?

`dart_mcp` is a library — you use it to write your own MCP servers and clients in Dart. `dart_mcp_server` is a finished server built with it, which exposes Dart and Flutter developer tooling to an AI model. If you want an agent that can analyse and test your project, you want `dart_mcp_server`. If you want to expose your own domain to an agent, you want `dart_mcp`.

### Is this an official Dart team project?

Yes. It lives under the `dart-lang` organisation alongside the SDK and core packages, and all three packages are published to pub.dev under the same BSD-3-Clause licence as the rest of Dart.

### Which AI tools can use dart_mcp_server?

Any MCP client that speaks stdio. The README gives setup steps for Gemini CLI, Gemini Code Assist, Cursor and GitHub Copilot in VS Code, but the protocol is the interface — the server does not care which client connects, as long as it supports Tools and Resources.

### What is the skills package for?

It is a CLI for managing skills shipped inside packages and pulled from git repositories. It is the newest of the three and the least settled, so check its own README before depending on its interface.

## Resources & links

- **GitHub:** [dart-lang/ai](https://github.com/dart-lang/ai)
- **pub.dev:** [dart_mcp](https://pub.dev/packages/dart_mcp) · [dart_mcp_server](https://pub.dev/packages/dart_mcp_server) · [skills](https://pub.dev/packages/skills)
- **Protocol:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
