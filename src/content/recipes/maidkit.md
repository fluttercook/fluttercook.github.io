---
title: "MaidKit: a Flutter SSH toolkit for managing servers"
package: "MaidKit"
repo: "Solsynth/MaidKit"
githubUrl: "https://github.com/Solsynth/MaidKit"
category: "App/Template"
stars: 426
forks: 35
lastUpdate: "2026-08-26"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=maidkit+ssh+flutter"
priority: "High"
phase: "P1"
trendRank: 0
description: "MaidKit is a cross-platform SSH server manager built in Flutter - terminal, SFTP, systemd, firewall, containers and an AI agent, all over plain SSH with nothing installed on the server."
seoDescription: "MaidKit is an AGPL-3.0 Flutter app for server administration: split-pane SSH terminal, dual-pane SFTP, Docker and Podman, databases, an AES-GCM credential vault and a local MCP server."
keywords:
  - maidkit
  - flutter ssh client
  - open source server manager
  - flutter desktop app example
  - ssh terminal app flutter
  - docker manager mobile
topics:
  - ssh
  - devops
  - desktop
summary:
  - "**MaidKit** manages servers over plain SSH - no agent installed on the box unless you opt into the MaidCafe daemon."
  - "Terminal with split panes, dual-pane SFTP, systemd, nginx/Caddy, firewall, crontab, packages, Docker/Podman, Postgres/MySQL backups."
  - "Credentials live in an AES-GCM 256 vault with PBKDF2 at 310,000 iterations and biometric unlock."
  - "**426★**, AGPL-3.0, Flutter SDK `^3.12.2`. It is an app, not a package - `publish_to: none`."
related:
  - slug: flutter-server-box
    title: "flutter_server_box: a Flutter developer's guide"
  - slug: droiddesk
    title: "DroidDesk: a Flutter developer's guide"
  - slug: denial
    title: "Denial: a Wayland compositor with Flutter at the foundation"
faq:
  - q: Does MaidKit install anything on my servers?
    a: "Not for day-to-day work - management is 100% SSH-based and non-intrusive by design. The optional MaidCafe daemon adds fleet metrics, scheduled jobs and push alerts; it connects outbound only, so it opens no inbound ports."
  - q: Is MaidKit available on pub.dev?
    a: "No. Its pubspec sets `publish_to: \"none\"` because it is an application, not a package. Download builds from solsynth.dev or build it yourself with the Flutter SDK."
  - q: How are my SSH credentials stored?
    a: "In an AES-GCM 256-bit vault with PBKDF2 key derivation at 310,000 iterations, with biometric unlock, optional encrypted cloud sync and encrypted `.mkb` backup archives. GitHub access tokens go in the same vault."
  - q: What does the AI agent actually do?
    a: "It operates your servers through tools, with your own AI provider or Solar Network AI, extended by MCP servers and skills. Proposed actions require approval in review mode before running, and conversation history stays on-device outside the vault."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`MaidKit`](https://github.com/Solsynth/MaidKit) is a cross-platform SSH server manager written in Flutter, covering everything from a split-pane terminal to Postgres backups. **426★**, AGPL-3.0, last pushed **2026-08-26**.

## What is MaidKit?

MaidKit is the toolkit its author built for doing server maintenance — the name comes from "acting as a maid for servers". Its governing constraint is that day-to-day management is **100% SSH-based and installs nothing on the server**. Most server-management panels want an agent on every box; MaidKit's default is that your servers stay exactly as they were.

What that buys you, from one Flutter app on desktop or mobile:

- a server dashboard with live status, network and SSH round-trip latency, load, memory and uptime, grouped and taggable
- a full SSH terminal with split panes, drag-and-drop tabs, a command palette, OSC 52 clipboard support and colour schemes
- a dual-pane SFTP browser with drag-and-drop transfers, an in-app editor and keyboard shortcuts
- systemd units, nginx and Caddy config, crontab, packages (apt, dnf and more), processes
- firewall management across UFW, firewalld, nftables and iptables
- port forwarding with presets that auto-start on connect, HTTP CONNECT/SOCKS5 proxying, and jump hosts
- Docker and Podman containers with compose project grouping
- PostgreSQL, MySQL and MariaDB inspection, logical backup/restore and pgBackRest
- Tailscale via an embedded node — no Tailscale app required

If you want more than SSH can give you, the optional **MaidCafe** daemon adds fleet metrics streamed over SSE, scheduled jobs, container log tailing and alarm thresholds. It connects outbound only, so no inbound ports are opened.

## Why it is worth reading as a Flutter developer

Two reasons, and the first is that MaidKit is an unusually good specimen of a *serious* Flutter desktop application. Split-pane terminals, drag-and-drop tab reordering, dual-pane file management with keyboard shortcuts, a command palette, a selectable terminal renderer (Ghostty's libghostty-vt or xterm), and a vendored native library compiled from source for the iOS App Store. Most "Flutter desktop app" examples are a sidebar and a list view. This is not that.

The security model is worth studying too: an AES-GCM 256-bit credential vault, PBKDF2 at 310,000 iterations, biometric unlock, optional encrypted cloud sync of blobs only, and encrypted `.mkb` backup archives. There is even a "hide server addresses when screen sharing" setting, which tells you someone has actually demoed this on a call.

The second reason is the AI surface, which is more carefully designed than most. MaidKit's agent operates servers through tools with your own provider, extended by MCP servers and skills, and **proposed actions require approval in review mode** before they run. Separately, MaidKit exposes a *local MCP server* so Claude Desktop or any other MCP client can reach its SSH servers, snippets and skills. Both directions, with a human in the loop on the dangerous one.

## Getting started

MaidKit is an application, not a package — its pubspec carries `publish_to: "none"`. Download a build from [solsynth.dev](https://solsynth.dev/products/maid-kit), or build it yourself:

```bash
flutter pub get
flutter run
```

It needs Flutter SDK `^3.12.2`. Platform prerequisites are real:

- **Linux:** `ninja-build`, `libgtk-3-dev`, `libayatana-appindicator3-dev`, `keybinder-3.0`, `libnotify-dev`
- **Windows:** NASM, required by `webcrypto` native assets
- **iOS App Store archives:** Zig 0.15 (`brew install zig@0.15`) for the vendored Ghostty terminal — the current Ghostty source does not build with Zig 0.16

For Linux distribution there is an AppImage script:

```bash
flutter build linux
bash buildtools/build-appimage.sh
```

## When should you look at MaidKit?

- you administer a handful of servers and want one app that does terminal, files, services and containers
- you refuse to install a management agent on production hosts
- you want a real, large, actively developed Flutter desktop codebase to learn from
- you want an AI agent with server access that asks before acting

## Where it falls short

**AGPL-3.0** is the first thing to check. For using the app it changes nothing. For borrowing code into your own product — and the terminal, vault and SFTP implementations are genuinely tempting — it is a strong copyleft obligation that extends over a network. Read it before you copy anything.

The build has sharp edges. A pinned Zig version for iOS, NASM on Windows, five apt packages on Linux: this is a Flutter app with a native tail, and CI setup is not a five-minute job.

The MaidCafe layer, where the most interesting fleet features live, ties into Solarpass accounts and Solar Network workspaces. Self-hosted cloud endpoints are supported in settings, but the smooth path runs through the author's service — worth knowing before you build a workflow on it.

And the feature list is enormous for a project this young. Breadth like this usually means depth varies; verify the specific subsystem you care about rather than assuming the whole surface is equally solid.

## Alternatives worth comparing

- [flutter_server_box: a Flutter developer's guide](/recipes/flutter-server-box/) — the closest Flutter equivalent, lighter and narrower
- Termius, Royal TSX — mature commercial SSH clients
- [DroidDesk: a Flutter developer's guide](/recipes/droiddesk/) — a Linux desktop on the phone instead of a manager for remote ones

## Frequently asked questions

### Does MaidKit install anything on my servers?

Not for day-to-day work — management is 100% SSH-based and non-intrusive by design. The optional MaidCafe daemon adds fleet metrics, scheduled jobs and push alerts; it connects outbound only, so it opens no inbound ports.

### Is MaidKit available on pub.dev?

No. Its pubspec sets `publish_to: "none"` because it is an application, not a package. Download builds from solsynth.dev or build it yourself with the Flutter SDK.

### How are my SSH credentials stored?

In an AES-GCM 256-bit vault with PBKDF2 key derivation at 310,000 iterations, with biometric unlock, optional encrypted cloud sync and encrypted `.mkb` backup archives. GitHub access tokens go in the same vault.

### What does the AI agent actually do?

It operates your servers through tools, with your own AI provider or Solar Network AI, extended by MCP servers and skills. Proposed actions require approval in review mode before running, and conversation history stays on-device outside the vault.

## Resources & links

- **GitHub:** [Solsynth/MaidKit](https://github.com/Solsynth/MaidKit)
- **Downloads:** [solsynth.dev/products/maid-kit](https://solsynth.dev/products/maid-kit)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
