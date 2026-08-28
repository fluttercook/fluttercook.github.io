---
title: "simvyn: one dashboard for every simulator, emulator and device"
package: "simvyn"
repo: "pranshuchittora/simvyn"
githubUrl: "https://github.com/pranshuchittora/simvyn"
category: "Library/Tooling"
stars: 351
forks: 24
lastUpdate: "2026-08-05"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=simvyn+ios+simulator+android+emulator"
priority: "High"
phase: "P1"
trendRank: 0
description: "simvyn puts iOS Simulators, Android Emulators and USB devices behind one web dashboard and one CLI - logs, GPS, databases, files, push, screenshots - without opening Xcode or Android Studio."
seoDescription: "simvyn is a universal mobile devtool for iOS Simulators, Android Emulators and real devices. Database inspector, log viewer, location simulation and a full CLI, all from npx simvyn."
keywords:
  - simvyn
  - ios simulator manager
  - android emulator dashboard
  - flutter device tools
  - sqlite inspector flutter
  - mobile devtools cli
topics:
  - devtools
  - simulator
  - cli
summary:
  - "**simvyn** is one dashboard and one CLI for iOS Simulators, Android Emulators and USB-connected physical devices."
  - "Run it with `npx simvyn` - no install, no config, devices are discovered automatically."
  - "The parts you will actually use daily: the SQLite and SharedPreferences inspector, streaming logs with regex search, GPS route playback, and app sandbox file browsing."
  - "**351★**, Node 22+, macOS for full iOS and Android support or Linux for Android only."
related:
  - slug: tapflow
    title: "tapflow: self-hosted simulator streaming for your whole team"
  - slug: flutter-skill
    title: "flutter-skill: let an AI agent drive your running app"
  - slug: simutil
    title: "Build better Flutter UI with simutil"
faq:
  - q: Do I need to install simvyn?
    a: "No. `npx simvyn` starts the local server, opens the dashboard in your browser and discovers every connected simulator, emulator and USB device. A global install with `npm install -g simvyn` is available if you use it daily."
  - q: Does simvyn work on Windows?
    a: "No. It needs macOS for full iOS and Android support, or Linux for Android only. iOS simulator control depends on Xcode command-line tools, which do not exist off macOS."
  - q: Is simvyn Flutter-specific?
    a: "No, and that is the point. It drives the simulator and the device, not the framework, so the same dashboard works for Flutter, React Native, native SwiftUI and Jetpack Compose apps."
  - q: Can it inspect my app's local database?
    a: "Yes. The database inspector browses SQLite tables and runs SQL queries, and it reads SharedPreferences on Android and NSUserDefaults on iOS. For a Flutter app using sqflite or Drift, that is your local store without adding any debug code."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`simvyn`](https://github.com/pranshuchittora/simvyn) is a single dashboard and CLI for every mobile device you develop against — iOS Simulators, Android Emulators, and physical devices over USB. **351★**, last pushed **2026-08-05**. It runs with one command and no configuration.

## What is simvyn?

Mobile development scatters device control across too many tools. Booting a simulator means Xcode. Wiping an emulator means Android Studio. Reading logs means `adb logcat` in one window and Console.app in another. Setting a fake GPS location means a different dialog on each platform. Inspecting the app's SQLite file means pulling it off the device by hand.

simvyn collapses all of that into one web dashboard, and mirrors every feature in a CLI so it works headlessly too:

```bash
npx simvyn
```

That starts a local server, opens the dashboard, and discovers everything connected — simulators, emulators, and USB devices — automatically.

## Why it matters for Flutter developers

Flutter already abstracts the *app* across platforms. simvyn abstracts the *device*, which is the half Flutter never touched. `flutter run` picks a device but gives you nothing for the surrounding work.

Three features earn their place immediately in a Flutter workflow:

**The database inspector.** Browse SQLite tables and run SQL queries against them, plus SharedPreferences on Android and NSUserDefaults on iOS. If your app uses `sqflite`, Drift or `shared_preferences`, that is your entire local persistence layer, inspectable without writing a debug screen.

**The file browser.** Browse the app sandbox, upload and download files, edit text inline. Reproducing a corrupt-cache bug stops being archaeology.

**Location simulation.** Set coordinates, or play a GPX or KML route with speed control. Testing a maps or delivery feature no longer means walking around the office.

Beyond those: streaming logs with level filtering and regex search, screenshots and screen recording with history, deep-link launching with saved favourites, push notification payloads to iOS simulators, clipboard read and write, crash logs, and pushing photos and videos into the camera roll.

The Collections feature is the sleeper. Bundle a sequence of device actions — set locale, set dark mode, seed a location, install a build — and apply it to several devices at once. That is your QA setup as a reusable object.

## When should you use simvyn?

- you switch between iOS and Android constantly and are tired of two IDEs for device chores
- you need to inspect on-device state — database rows, preferences, sandbox files — without building a debug UI
- you test location, deep links, or push and want it repeatable rather than manual
- you want an AI agent to drive devices; the full CLI surface is what makes that possible

## Where it falls short

No Windows. macOS gives you iOS and Android; Linux gives you Android only. For a Windows-based Flutter team this is a non-starter, and no amount of configuration changes that — iOS simulator control needs Xcode's command-line tools.

Node 22.12 or newer is required, which is more current than many machines default to.

The repository also carries no licence file, which for a tool you run against internal builds is worth noting before it goes into a team workflow. That is a paperwork gap rather than a technical one, but it is the kind of gap that a security review will stop on.

## Alternatives worth comparing

- [tapflow: self-hosted simulator streaming for your whole team](/recipes/tapflow/) — the multi-user version of the same problem
- [flutter-skill: let an AI agent drive your running app](/recipes/flutter-skill/) — drives the app rather than the device
- [Build better Flutter UI with simutil](/recipes/simutil/) — a lighter TUI for the boot-a-device case alone

## Frequently asked questions

### Do I need to install simvyn?

No. `npx simvyn` starts the local server, opens the dashboard in your browser and discovers every connected simulator, emulator and USB device. A global install with `npm install -g simvyn` is available if you use it daily.

### Does simvyn work on Windows?

No. It needs macOS for full iOS and Android support, or Linux for Android only. iOS simulator control depends on Xcode command-line tools, which do not exist off macOS.

### Is simvyn Flutter-specific?

No, and that is the point. It drives the simulator and the device, not the framework, so the same dashboard works for Flutter, React Native, native SwiftUI and Jetpack Compose apps.

### Can it inspect my app's local database?

Yes. The database inspector browses SQLite tables and runs SQL queries, and it reads SharedPreferences on Android and NSUserDefaults on iOS. For a Flutter app using `sqflite` or Drift, that is your local store without adding any debug code.

## Resources & links

- **GitHub:** [pranshuchittora/simvyn](https://github.com/pranshuchittora/simvyn)
- **npm:** [simvyn](https://www.npmjs.com/package/simvyn)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
