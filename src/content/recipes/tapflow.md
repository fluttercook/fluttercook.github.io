---
title: "tapflow: self-hosted simulator streaming for your whole team"
package: "tapflow"
repo: "jo-duchan/tapflow"
githubUrl: "https://github.com/jo-duchan/tapflow"
category: "Library/Tooling"
stars: 530
forks: 65
lastUpdate: "2026-08-28"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=tapflow+simulator+streaming+qa"
priority: "High"
phase: "P1"
trendRank: 0
description: "tapflow streams iOS Simulators and Android emulators from your own Macs into any browser, so designers, PMs and backend developers can QA a Flutter build without Xcode."
seoDescription: "tapflow is a self-hosted, MIT-licensed alternative to Appetize and BrowserStack. Stream simulators to the browser over H.264, no WebDriverAgent, builds never leave your infrastructure."
keywords:
  - tapflow
  - self-hosted appetize alternative
  - browserstack alternative open source
  - flutter qa tooling
  - ios simulator streaming
  - android emulator browser
topics:
  - qa
  - devtools
  - self-hosted
summary:
  - "**tapflow** streams the iOS Simulator and Android emulator from a Mac you already own into any teammate's browser."
  - "Three parts: a self-hosted relay, a macOS agent that connects outbound, and a browser dashboard."
  - "`npm install -g tapflow`, then `tapflow setup` and `tapflow start` - no WebDriverAgent, no cloud upload."
  - "**530★**, MIT, still v0.x, and the agent side is macOS-only."
related:
  - slug: simvyn
    title: "simvyn: one dashboard for every simulator, emulator and device"
  - slug: flutter-skill
    title: "flutter-skill: let an AI agent drive your running app"
  - slug: maidkit
    title: "MaidKit: a Flutter SSH toolkit for managing servers"
faq:
  - q: Is tapflow a device farm?
    a: "No. It streams simulators and emulators that run on Macs you already own; it does not manage a pool of physical phones. The project says so explicitly - it makes running simulators reachable from a browser, nothing more."
  - q: Do my Flutter builds get uploaded anywhere?
    a: "No. tapflow is self-hosted by design. App binaries, device streams and session recordings stay on the relay you run. That is the main reason to pick it over Appetize or BrowserStack."
  - q: Does the whole team need a Mac?
    a: "Only the machines running agents. The relay runs on any OS with Node 22+, and QA users need nothing but a modern browser - no Xcode, no Android Studio, no Flutter SDK."
  - q: Can an AI agent drive tapflow?
    a: "Yes. `@tapflowio/mcp-server` exposes simulator control as MCP tools for Claude Code and other agents, and there is a REST screenshot endpoint at `/api/v1/sessions/:sessionId/screenshot` for CI."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`tapflow`](https://github.com/jo-duchan/tapflow) is a self-hosted alternative to Appetize and BrowserStack: it streams iOS Simulators and Android emulators running on your own Macs into any browser. **530★**, MIT, last pushed **2026-08-28**.

## What is tapflow?

Every Flutter team hits the same wall eventually. The mobile developers can run the app whenever they like. Everyone else — the designer checking a layout, the PM comparing two builds, the backend developer who wants to see what actually shipped to sandbox — has to ask a mobile developer, every single time.

The usual answers all cost something. Physical devices cost money and OS coverage and someone's afternoon. Appetize and BrowserStack cost a subscription *and* require uploading internal builds to a third party. Giving everyone Xcode costs everyone a Mac and a full toolchain.

tapflow's answer is to reuse the Macs you already have. It has three pieces:

1. a **relay** (Linux or macOS) that also serves the dashboard on the same port
2. a **macOS agent** that drives the simulator or emulator, connecting *outbound* to the relay — no inbound firewall rules, and no WebDriverAgent, because it injects iOS touch directly
3. a **browser dashboard** for everyone else

## Why it matters for Flutter teams

Flutter's promise is that one team ships to both platforms. In practice, QA stays stuck on whoever owns the Mac. tapflow moves that bottleneck without moving your builds off your own infrastructure.

The streaming is more considered than you would expect from a v0.x project. Both platforms stream H.264 through a two-tier decoder — WebCodecs on a secure context, a WASM decoder on plain HTTP — deliberately skipping Media Source Extensions so the media element's buffer never enters the decode path. The project publishes its own latency measurements: p50 around 11–17 ms decode-to-present with the software decoder, plus your network round trip. Older browsers fall back to JPEG rather than failing.

Around the stream sit the things a QA workflow actually needs: touch, swipe and pinch forwarded live; a deeplink toolbar; an App Center that takes `.app.zip` and `.apk` uploads and tracks builds through Backlog / In Progress / Done / Rejected; session recordings kept ~72 hours then purged; per-agent CPU and RAM so you can see which Mac is overloaded; and roles — Admin, Developer, QA, Viewer — with invite links and personal access tokens.

## Getting started

```bash
npm install -g tapflow
```

On the Mac that will run an agent, install the simulator prerequisites:

```bash
tapflow setup
```

Then start the relay and agent together:

```bash
tapflow start
```

That prints the relay URL (`http://localhost:4000` by default). Open it and tapflow redirects you to `/setup` to create the first admin account — or use `tapflow admin init` on a headless server. `tapflow doctor` re-checks prerequisites if something looks wrong.

Skip `tapflow setup` on a relay-only Linux box; it only needs Node 22+ and about 512 MB of RAM.

## When should you use tapflow?

- non-developers on your team need to try a Flutter build and currently cannot
- you are paying for Appetize or BrowserStack mainly for simulator access, not real hardware
- policy or client contract says internal builds must not be uploaded to a third-party cloud
- you want an LLM agent or CI job to drive a simulator through MCP or REST

## Where it falls short

Agents are macOS-only, and always will be — they drive Xcode's simulator and the Android emulator on a Mac. The relay runs anywhere; the machines doing the actual work do not.

It is v0.x and says so. The maintainers promise backward compatibility by default and note breaking changes in the changelog, but that is a promise, not a track record.

And it is explicitly not a device farm and not an Appium replacement. It ships a minimal flow runner of its own; wiring in WebDriverAgent or Appium is out of scope by design. If your QA plan depends on real hardware quirks — a specific OEM's camera stack, a real modem, thermal throttling — a simulator stream will not find those bugs no matter how good the latency is.

## Alternatives worth comparing

- [simvyn: one dashboard for every simulator, emulator and device](/recipes/simvyn/) — single-developer local control rather than team streaming
- [flutter-skill: let an AI agent drive your running app](/recipes/flutter-skill/) — agent access to the app instead of the device
- Appetize and BrowserStack — the hosted originals, if you would rather pay than run a relay

## Frequently asked questions

### Is tapflow a device farm?

No. It streams simulators and emulators that run on Macs you already own; it does not manage a pool of physical phones. The project says so explicitly — it makes running simulators reachable from a browser, nothing more.

### Do my Flutter builds get uploaded anywhere?

No. tapflow is self-hosted by design. App binaries, device streams and session recordings stay on the relay you run. That is the main reason to pick it over Appetize or BrowserStack.

### Does the whole team need a Mac?

Only the machines running agents. The relay runs on any OS with Node 22+, and QA users need nothing but a modern browser — no Xcode, no Android Studio, no Flutter SDK.

### Can an AI agent drive tapflow?

Yes. `@tapflowio/mcp-server` exposes simulator control as MCP tools for Claude Code and other agents, and there is a REST screenshot endpoint at `/api/v1/sessions/:sessionId/screenshot` for CI.

## Resources & links

- **GitHub:** [jo-duchan/tapflow](https://github.com/jo-duchan/tapflow)
- **Docs:** [tapflow.dev](https://www.tapflow.dev)
- **npm:** [tapflow](https://www.npmjs.com/package/tapflow)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
