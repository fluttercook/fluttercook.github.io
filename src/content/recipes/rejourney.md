---
title: "Rejourney: open-source session replay and crash reporting for Flutter"
package: "rejourney"
repo: "rejourneyco/rejourney"
githubUrl: "https://github.com/rejourneyco/rejourney"
category: "Backend/Data"
stars: 277
forks: 16
lastUpdate: "2026-08-28"
pubDev: "https://pub.dev/packages/rejourney"
youtube: "https://www.youtube.com/watch?v=Z95MDxBXMjk"
priority: "High"
phase: "P1"
trendRank: 0
description: "Rejourney is an open-source session replay, product analytics and crash/ANR reporting platform with a first-class Flutter SDK - privacy-first, self-hostable, and honest about causality."
seoDescription: "Rejourney's Flutter SDK adds session replay, native crash and ANR reporting, product events and network timing. Apache 2.0 client SDK, SSPL backend, install with flutter pub add rejourney."
keywords:
  - rejourney flutter
  - flutter session replay
  - flutter crash reporting open source
  - flutter anr monitoring
  - flutter product analytics
  - open source posthog alternative mobile
topics:
  - analytics
  - session-replay
  - monitoring
summary:
  - "**Rejourney** combines session replay, product events and technical signals - crashes, ANRs, API failures - into one issue feed."
  - "The Flutter SDK captures natively; the public API, navigator observer, privacy masks and HTTP client are idiomatic Dart."
  - "`flutter pub add rejourney`, then `Rejourney.init()` and - only after consent - `Rejourney.start()`."
  - "**277★**. Client SDKs and docs are Apache 2.0; the backend and dashboard are SSPL."
related:
  - slug: appwrite
    title: "Add AI to your Flutter app with appwrite"
  - slug: serverpod
    title: "Build better Flutter UI with serverpod"
  - slug: simvyn
    title: "simvyn: one dashboard for every simulator, emulator and device"
faq:
  - q: How do I add Rejourney to a Flutter app?
    a: "`flutter pub add rejourney`, then `await Rejourney.init('pk_live_...')` at startup and `await Rejourney.start()` only after your consent decision. `init` deliberately never starts capture. Minimums are Flutter 3.22, Dart 3.3, iOS 15.1 and Android API 24."
  - q: Is Rejourney really open source?
    a: "Partly, and it is upfront about it. The Flutter API, platform bridges, native core, examples and documentation are Apache 2.0. The backend and dashboard are SSPL 1.0 - free to run internally, but offering it as a service obliges you to publish your service source."
  - q: How does it handle sensitive fields?
    a: "Wrap the subtree in `RejourneyMask`, which hides a region in captured frames without changing what the user sees. That sits on top of native secure-field detection and project-level text and media privacy rules, and remote policy can only make capture more restrictive, never less."
  - q: Does session replay work reliably on Android?
    a: "Mostly. Some renderer and device combinations report a successful `PixelCopy` while returning a black bitmap; from 0.2.1 the SDK detects that and falls back to capturing Flutter's retained layer tree at reduced resolution. Check `getSdkMetrics().lastCaptureSource` when validating a device."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`Rejourney`](https://github.com/rejourneyco/rejourney) is an open-source platform for session replay, product analytics and crash/ANR reporting, with a Flutter SDK that is more carefully built than most. **277★**, last pushed **2026-08-28**.

## What is Rejourney?

Most teams debug conversion problems with three disconnected tools: an analytics dashboard that says the funnel dropped, a crash reporter that says something threw, and a session replay product that shows one user's afternoon. Correlating them is manual work.

Rejourney's premise is to keep them in one place. You instrument a handful of **critical conversion events** — `checkout_started`, `purchase_completed` — and it records the surrounding journey, the interaction data (touches, scrolls, pans, rage taps), and the technical evidence (API latency and status codes, errors, crash traces, ANRs). Similar sessions get grouped into cohorts, and when a cohort trends badly around a conversion event, the replays and evidence surface as a ranked issue.

Beside the replay workbench sit journey maps, interaction heatmaps, endpoint views, device and geographic cohorts, and project-level analytics for version adoption, retention and — where a revenue source is connected — revenue impact.

## Why the Flutter SDK is worth a look

Plenty of analytics products bolt a thin Dart wrapper onto a native SDK. Rejourney splits it the other way round: capture runs in native code, while the public API, navigation integration, privacy masks, error hooks and HTTP client are idiomatic Flutter.

That shows up in the details:

- `RejourneyNavigatorObserver` plugs into `navigatorObservers` and handles push, pop, replace and remove, suppressing duplicate screen names. With a declarative Router, you call `Rejourney.trackScreen('checkout')` from its route-change callback instead.
- `RejourneyMask` hides a Flutter-rendered subtree from captured frames without changing what the user sees, and tracks layout changes, scrolling and disposal.
- `RejourneyHttpClient` wraps `package:http` to record method, URL, status, timing, content type and byte sizes — not bodies. For Dio, gRPC or GraphQL you call `Rejourney.logNetworkRequest(...)` from an interceptor.
- `RejourneyErrorCapture.install()` goes in before `runApp`.

The Android capture path deserves special mention. Some renderer and device combinations report a successful `PixelCopy` while handing back an entirely black bitmap. Rather than telling you to switch render modes, the SDK detects the false success and captures Flutter's retained layer tree at reduced resolution instead, leaving your live `FlutterSurfaceView` alone. `getSdkMetrics().lastCaptureSource` tells you which path is active. That is the kind of problem you only fix after shipping to real devices.

## Getting started

```bash
flutter pub add rejourney
```

Minimums: Flutter 3.22, Dart 3.3, iOS 15.1, Android API 24. On an existing iOS app you may need `cd ios && pod install`.

```dart
import 'package:rejourney/rejourney.dart';

await Rejourney.init('pk_live_your_public_key');
await Rejourney.start();
```

`init` never starts capture — that separation exists so you can wait for consent:

```dart
if (await consentStore.canRecord()) {
  final result = await Rejourney.start();
  debugPrint('session=${result.sessionId} replay=${!result.telemetryOnly}');
}
```

Call `Rejourney.stop()` if consent is revoked. Then add the navigator observer, wrap sensitive inputs in `RejourneyMask`, and log your conversion events:

```dart
await Rejourney.logEvent('purchase_completed', <String, Object?>{
  'transactionId': order.id,
  'amount': order.total,
  'currency': 'USD',
});
```

## When should you use Rejourney?

- you want replay, analytics and crash reporting correlated rather than in three tabs
- ANRs and native crashes matter to you as much as Dart exceptions
- data residency or cost rules you out of a hosted analytics vendor
- you need per-widget masking rather than a global "hide all text" switch

## Where it falls short

The licence is dual, and the split matters. Client SDKs, examples and docs are Apache 2.0 — safe to ship. The backend and dashboard are **SSPL 1.0**: fine for internal use, but if you offer Rejourney as a service you must publish your service source. Anyone treating "open source" as a synonym for "no obligations" should read `LICENSE` before building a product on it.

Self-hosting a replay backend is not a weekend job either. You are running ingestion, storage and a dashboard for video-like data, and the storage bill grows with your traffic, not your team.

The project is also honest that its issue reports are heuristic — a reported pattern is "a starting point for investigation, not proof of causality". Take that seriously. A cohort correlation plus a suggested fix is a hypothesis, and shipping it without checking your authoritative product or payment state is how you fix the wrong thing confidently.

Finally: session replay on a real product is a privacy decision before it is a technical one. Consent, masking and replay QA on the exact login, checkout and health flows you ship are not optional extras here.

## Alternatives worth comparing

- Sentry — mature crash and performance monitoring, no product analytics or journey view
- PostHog — the closest open-source analogue, stronger on web, thinner on native mobile capture
- [Add AI to your Flutter app with appwrite](/recipes/appwrite/) and [Build better Flutter UI with serverpod](/recipes/serverpod/) — self-hosted backends you might already run

## Frequently asked questions

### How do I add Rejourney to a Flutter app?

`flutter pub add rejourney`, then `await Rejourney.init('pk_live_...')` at startup and `await Rejourney.start()` only after your consent decision. `init` deliberately never starts capture. Minimums are Flutter 3.22, Dart 3.3, iOS 15.1 and Android API 24.

### Is Rejourney really open source?

Partly, and it is upfront about it. The Flutter API, platform bridges, native core, examples and documentation are Apache 2.0. The backend and dashboard are SSPL 1.0 — free to run internally, but offering it as a service obliges you to publish your service source.

### How does it handle sensitive fields?

Wrap the subtree in `RejourneyMask`, which hides a region in captured frames without changing what the user sees. That sits on top of native secure-field detection and project-level text and media privacy rules, and remote policy can only make capture more restrictive, never less.

### Does session replay work reliably on Android?

Mostly. Some renderer and device combinations report a successful `PixelCopy` while returning a black bitmap; from 0.2.1 the SDK detects that and falls back to capturing Flutter's retained layer tree at reduced resolution. Check `getSdkMetrics().lastCaptureSource` when validating a device.

## Resources & links

- **GitHub:** [rejourneyco/rejourney](https://github.com/rejourneyco/rejourney)
- **pub.dev:** [rejourney](https://pub.dev/packages/rejourney)
- **Website:** [rejourney.co](https://rejourney.co/)

---

*Part of [FlutterCook](/recipes/) — hands-on guides to the best open-source Flutter libraries, UI kits, and apps. Explore the live [GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*
