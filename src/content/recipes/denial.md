---
title: "Denial: a Wayland compositor with Flutter at the foundation"
package: "Denial"
repo: "denialwm/denial"
githubUrl: "https://github.com/denialwm/denial"
category: "Framework/Core"
stars: 501
forks: 15
lastUpdate: "2026-08-27"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=denial+wayland+compositor+flutter"
priority: "High"
phase: "P1"
trendRank: 0
description: "Denial is a Flutter-native Wayland compositor: the Dart shell runs AOT inside the compositor process, Wayland clients arrive as external textures, and Impeller renders straight to KMS."
seoDescription: "Denial embeds the Flutter Engine through the native Embedder API and renders an entire Linux desktop with Impeller into a shared GBM atlas. Rust and Smithay own Wayland state; Flutter owns desktop policy."
keywords:
  - denial wayland compositor
  - flutter linux desktop
  - flutter wayland
  - impeller compositor
  - smithay rust flutter
  - flutter desktop environment
topics:
  - wayland
  - linux
  - compositor
summary:
  - "**Denial** is not a Flutter app on a desktop - it *is* the desktop, embedding the Flutter Engine inside the compositor process."
  - "Rust and Smithay own Wayland protocol, input, DRM/KMS; Flutter owns shell layout, motion and window composition."
  - "Impeller renders the whole desktop into a shared GBM atlas that each display scans out directly - no second compositor pass."
  - "**501★**, GPLv3, public beta. Signed x86-64 packages for Arch, Debian 13, Ubuntu 24.04 and Fedora 44."
related:
  - slug: flutter-zero
    title: "Flutter Zero: Flutter with dart:ui taken out"
  - slug: pangolin-desktop
    title: "Build better Flutter UI with pangolin_desktop"
  - slug: maidkit
    title: "MaidKit: a Flutter SSH toolkit for managing servers"
faq:
  - q: Is Denial a Flutter app running on a Wayland compositor?
    a: "No, and that is the whole point. `deniald` embeds the Flutter Engine through its native Embedder API and runs the Dart shell AOT-compiled inside the compositor process. It is not a Wayland client and does not need another compositor beneath it."
  - q: How do Wayland applications get drawn?
    a: "Their client buffers stay native resources. Denial imports the contents as external textures and places them in the same Flutter scene as the shell UI, which renders into a desktop-wide GBM atlas that each display scans out through KMS."
  - q: Can I hot reload the desktop shell?
    a: "On Arch, yes. The `denial-ui-development` package plus `denialctl ui setup` gives you a JIT shell with hot reload on save. Debugging is deliberately non-pausing - pausing the root isolate would pause the interactive desktop."
  - q: Is Denial ready to use as my daily desktop?
    a: "It is a public beta. It already runs as a full Wayland session with Xwayland, multi-output presentation and portal-based screen sharing, but the native APIs, Flutter bundle contract, configuration and wire protocol may still change before 1.0."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`Denial`](https://github.com/denialwm/denial) is a Flutter-native Wayland compositor — Flutter is not running *on* the desktop, it is part of the compositor's foundation. **501★**, GPLv3, last pushed **2026-08-27**.

## What is Denial?

A normal Flutter desktop app asks an existing compositor for a window. Denial goes one layer down. `deniald` embeds the Flutter Engine directly through its native Embedder API, and the Dart shell runs AOT-compiled inside the compositor process. There is no Hyprland or Mutter underneath.

The responsibilities split cleanly along a Rust/Dart line:

- **Rust**, built on [Smithay](https://github.com/Smithay/smithay), owns Wayland protocol state, client buffers, input devices, focus and grabs, output configuration, DRM/KMS presentation and native resource lifetimes.
- **Flutter** owns desktop *policy*: shell layout, windows, system surfaces, settings, motion, gestures, and which regions participate in shell interaction.

Wayland clients never hand pixels to Dart. Their buffers stay native; Denial imports the contents as external textures and drops them into the same Flutter scene as the shell UI:

```text
Wayland clients ──> Rust / Smithay ──> external textures ──> Flutter scene
       input <──── native routing <──── shell hit regions <──────┘
                                                               │
Displays <────────────── DRM / KMS <────────────── shared GBM atlas
```

## Why this is technically interesting

The Impeller story is the part worth reading twice. Impeller was designed to render *an application inside a window*. Denial asks it to render an entire desktop into compositor-owned, rotating GBM framebuffers. Their locked Flutter fork wires Impeller's GLES path directly into the shared KMS atlas — embedder FBO presentation, no-target frame handling, preserved partial damage, native fences, external-texture lifetimes. Each display scans out its own region of that atlas directly. There is no second compositor pass over a finished frame.

Skia/Ganesh stays in the same engine generation as a fallback, selectable with `--flutter-renderer skia` or `DENIA_FLUTTER_RENDERER=skia`.

The bridge between Rust and Dart is also deliberately narrow. It carries immutable scene state and bounded commands; Dart never owns file descriptors, Wayland objects, EGL images or KMS buffers. The Settings app is a separate ordinary Wayland process talking to `deniald` over a versioned Unix control socket, so its rendering workload cannot stall the compositor's engine. That bundle boundary is also the intended path to third-party shells: once the compatibility contract stabilises, a compatible bundle should be able to replace the reference shell without replacing the compositor.

## Getting started

Denial ships signed first-party x86-64 repositories. Review [the setup script](https://github.com/denialwm/denial/blob/main/install.sh) first — it verifies the release-key fingerprint and adds the repo, but installs nothing:

```bash
curl -fsSL https://install.denialwm.org | sh
```

Then, for your distribution:

```bash
sudo pacman -Syu denial
```

```bash
sudo apt update && sudo apt install denial
```

```bash
sudo dnf install denial
```

Signed x86-64 packages cover Arch and CachyOS, Debian 13, Ubuntu 24.04 LTS, Fedora 44, and Alpine 3.24 via GitHub Releases. NixOS and Void are tested but unpackaged; ARM64 is fully supported from source only.

For shell hacking on Arch there is a separate package:

```bash
sudo pacman -S denial-ui-development
denialctl ui setup
```

That creates a source checkout and starts a JIT shell — open `dart_shell/` in your editor and you get hot reload on save while Wayland applications keep running. `denialctl ui restore` puts the packaged optimized shell back if your edits leave you without a usable window.

## When should you look at Denial?

- you write Flutter and have wondered how far below the application layer it can go
- you want a Linux desktop whose shell you can hot reload
- you are interested in the Embedder API, external textures, or Impeller outside the app-in-a-window case
- you are on Arch, Debian 13, Ubuntu 24.04 or Fedora 44 on x86-64 and enjoy running beta desktops

## Where it falls short

It is a public beta, and the README says so plainly: native APIs, the Flutter bundle contract, configuration and the wire protocol may all still change before 1.0. This is a compositor — when it breaks, it does not break in a window.

It depends on a **locked Flutter fork** with a pinned engine generation. That is unavoidable given what it does to Impeller's presentation path, but it means Denial's engine moves on Denial's schedule, not Flutter's.

Coverage is narrower than the distro table first suggests: ARM64 works but has no published binaries, NixOS and Void have no first-party packages, and Alpine gets signed release downloads rather than a repository. The debug story is intentionally limited too — the editor debug adapter cannot pause, break or evaluate, because pausing the root isolate would freeze the desktop you are sitting in front of.

And the licence is GPLv3, which is the right choice for a compositor but worth knowing before you plan anything derivative.

## Alternatives worth comparing

- [Flutter Zero: Flutter with dart:ui taken out](/recipes/flutter-zero/) — the other project asking what Flutter is underneath the framework
- [Build better Flutter UI with pangolin_desktop](/recipes/pangolin-desktop/) — a Flutter desktop *environment* rather than a compositor
- Hyprland, Sway, niri — mature Wayland compositors, if you want a desktop rather than an experiment

## Frequently asked questions

### Is Denial a Flutter app running on a Wayland compositor?

No, and that is the whole point. `deniald` embeds the Flutter Engine through its native Embedder API and runs the Dart shell AOT-compiled inside the compositor process. It is not a Wayland client and does not need another compositor beneath it.

### How do Wayland applications get drawn?

Their client buffers stay native resources. Denial imports the contents as external textures and places them in the same Flutter scene as the shell UI, which renders into a desktop-wide GBM atlas that each display scans out through KMS.

### Can I hot reload the desktop shell?

On Arch, yes. The `denial-ui-development` package plus `denialctl ui setup` gives you a JIT shell with hot reload on save. Debugging is deliberately non-pausing — pausing the root isolate would pause the interactive desktop.

### Is Denial ready to use as my daily desktop?

It is a public beta. It already runs as a full Wayland session with Xwayland, multi-output presentation and portal-based screen sharing, but the native APIs, Flutter bundle contract, configuration and wire protocol may still change before 1.0.

## Resources & links

- **GitHub:** [denialwm/denial](https://github.com/denialwm/denial)
- **Website:** [denialwm.org](https://denialwm.org)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
