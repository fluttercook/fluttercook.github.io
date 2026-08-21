---
title: "Using web technology to build mobile apps: the 2026 technical map"
description: "Four ways to get HTML/CSS/JS onto a phone — pure PWA, WebView shell, server-rendered shell, and the not-actually-WebView option. With verified numbers, store deadlines, hard limits, and a list of famous case studies that are dead but still being cited."
seoDescription: "A 2026 guide to building mobile apps with web technology: PWAs on iOS 26, Capacitor 8.5, Hotwire Native, TWA and Bubblewrap, the 31 Aug 2026 targetSdk 36 deadline, App Store guideline 4.2, WKWebView's 60fps ceiling, payment rules after Epic v. Apple, and OTA updates now that CodePush is dead."
keywords:
  - build mobile app with web technology
  - pwa 2026
  - what is capacitor
  - trusted web activity
  - hotwire native
  - web app on app store
  - will apple reject a webview app
  - react native ota updates
category: "Tutorial"
topic: "Cross-platform"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-21"
emoji: "🌐"
tags: ["Web", "Mobile", "PWA", "Capacitor", "React Native", "App Store", "Hotwire"]
sources:
  - name: "WebKit — WebKit features in Safari 26.0 (every website can be a web app)"
    url: "https://webkit.org/blog/17333/webkit-features-in-safari-26-0/"
  - name: "WebKit — Tracking Prevention (home screen web apps exempt from the 7-day cap)"
    url: "https://webkit.org/tracking-prevention/"
  - name: "Apple — App Review Guidelines"
    url: "https://developer.apple.com/app-store/review/guidelines/"
  - name: "Google Play — target API level requirements"
    url: "https://developer.android.com/google/play/requirements/target-sdk"
  - name: "Google Play — Spam policy: webviews and affiliate traffic"
    url: "https://support.google.com/googleplay/android-developer/answer/9899034"
  - name: "Android — Android vitals quality thresholds"
    url: "https://developer.android.com/topic/performance/vitals"
  - name: "Google Play — policy update for developers serving US users"
    url: "https://support.google.com/googleplay/android-developer/answer/15582165"
  - name: "Ionic — Announcing Capacitor 8"
    url: "https://ionic.io/blog/announcing-capacitor-8"
  - name: "Ionic — The future of Ionic's commercial products (Appflow sunset)"
    url: "https://ionic.io/blog/important-announcement-the-future-of-ionics-commercial-products"
  - name: "37signals — Announcing Hotwire Native"
    url: "https://dev.37signals.com/announcing-hotwire-native/"
  - name: "DHH — Native mobile apps are optional for B2B startups in 2024"
    url: "https://world.hey.com/dhh/native-mobile-apps-are-optional-for-b2b-startups-in-2024-4c870d3e"
  - name: "Found Engineering — Migrating from Cordova to Capacitor"
    url: "https://found.com/engineering/migrating-from-cordova-to-capacitor"
  - name: "WebKit Bugzilla 294338 — WKWebView pinned near 60 FPS"
    url: "https://bugs.webkit.org/show_bug.cgi?id=294338"
  - name: "Microsoft — App Center retirement (CodePush shut down 31 Mar 2025)"
    url: "https://learn.microsoft.com/en-us/appcenter/retirement"
  - name: "Shorebird — App Store compliance FAQ, quoting DPLA 3.3.1(b)"
    url: "https://docs.shorebird.dev/code-push/faq/"
  - name: "Shopify Engineering — Five years of React Native at Shopify"
    url: "https://shopify.engineering/five-years-of-react-native-at-shopify"
  - name: "Discord — Supercharging Discord Mobile: our journey to a faster app"
    url: "https://discord.com/blog/supercharging-discord-mobile-our-journey-to-a-faster-app"
  - name: "Joe Masilotti — Rails developers' guide to mobile app frameworks"
    url: "https://masilotti.com/rails-developers-guide-to-mobile-app-frameworks/"
  - name: "Expo — EAS Update documentation"
    url: "https://docs.expo.dev/eas-update/introduction/"
  - name: "Chrome for Developers — Trusted Web Activity"
    url: "https://developer.chrome.com/docs/android/trusted-web-activity/"
draft: false
---

"Can web technology build a mobile app?" expired as a question years ago. The question that still earns its keep is: **which of the four paths are you on, and do you know what you're trading away?**

This is a technical map, not a pitch for anyone's framework. Every number here carries a source and a date — and you'll find that most of the work in this article goes into **removing dead evidence the industry is still citing**.

## Four paths, not one

People lump everything under "hybrid." They differ at the architectural layer, and that difference decides everything downstream:

1. **Pure PWA** — nothing packaged. Users arrive via URL and add to home screen. No store involved.
2. **Native shell + WebView** — your web code runs inside `WKWebView` (iOS) or Android System WebView, with a JS ↔ native bridge for camera, push, biometrics. This is Capacitor, Cordova, Tauri mobile.
3. **Native shell + server-rendered HTML** — no SPA bundle. The server returns HTML; the native shell turns every link tap into a native screen. This is Hotwire Native.
4. **JS driving real native views, no WebView** — React Native, Expo, NativeScript. You write JS/TS, but what gets drawn is a `UIView`/`ViewGroup`, not a DOM.

Group 4 gets filed under "web technology" because it uses JavaScript. Technically it isn't web: no DOM, no CSS, no WebView. Flutter is further still — Dart compiles AOT to machine code and renders through Impeller. **If a comparison article files React Native or Flutter under "hybrid webview," that's your fast reliability test: it fails.**

| | Pure PWA | WebView shell | Hotwire Native | React Native |
| --- | --- | --- | --- | --- |
| Ships to App Store | No | Yes | Yes | Yes |
| Ships to Google Play | Via TWA | Yes | Yes | Yes |
| Updates without review | Everything | The web part | The entire UI | Via EAS Update |
| Native access | Browser-limited | Full, via plugins | Full, hand-written | Full |
| macOS needed for iOS builds | No | Yes | Yes | Yes |
| Reuses your existing web code | 100% | ~100% | 100% (if server-rendered) | Roughly 0% |

That last row deserves a pause: **React Native does not reuse your web frontend.** If your driving motivation is "leverage the web team we already have," RN doesn't solve that — it only saves you from writing iOS and Android twice.

## Path 1: pure PWA — and the iOS 26 reversal

This is where every article older than September 2025 is now wrong.

**iOS 26 removed the installability requirements entirely.** WebKit's own words: *"By default, every website added to the Home Screen opens as a web app,"* and *"nothing is required beyond the basics of an HTML file and a URL."* No manifest, no service worker ([WebKit, Safari 26](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/)).

The trade is double-edged: users now get an **"Open as Web App"** toggle, and they can **turn it off**. `display: standalone` is no longer a guarantee.

But the important part of PWAs on iOS was never the pretty install. It's four things that unlock **only after the user adds it to the home screen**:

- **Web Push** — since iOS 16.4 (16 Feb 2023), and still **only for installed web apps**, never in a Safari tab. No Apple Developer account required.
- **Icon badging** — `navigator.setAppBadge()`. This is one of the rare places **iOS beats Android**: Chrome on Android doesn't support the Badging API.
- **Browser-tier storage quota** — roughly 60% of disk per origin, versus the embedded-WebView tier's ~15%.
- **And the most valuable one: exemption from the 7-day data purge.**

That last point deserves emphasis because nearly every guide misses it. Safari's ITP deletes all script-writable storage — IndexedDB, LocalStorage, service worker registrations, caches — after 7 days without interaction. But WebKit states plainly: *"The first-party domain of home screen web applications is exempt from ITP's 7-day cap on all script-writeable storage"* ([WebKit Tracking Prevention](https://webkit.org/tracking-prevention/)).

Short version: **on iOS, convincing a user to tap "Add to Home Screen" is the single highest-leverage technical decision available to you.** It converts your PWA from "a tab that can be wiped" into "an app with durable data, push, and badges."

### What iOS still doesn't have

The following APIs carry the literal status string `"Not Considering"` in WebKit's feature database — Apple has no intention of building them: **Web Bluetooth, WebUSB, WebHID, Web Serial, Web NFC.**

Plus things that exist on iOS in no browser at all: **Background Sync, Periodic Background Sync, Web Share Target** (iOS PWAs can *send* shares but not *receive* them), and **`beforeinstallprompt`** — there is no way to trigger the install dialog from code; users must find the Share menu themselves.

If your app needs Bluetooth to talk to a device, path 1 ends here.

The good news also needs updating, because many comparison tables have it wrong:

| API | Chrome Android | Safari iOS |
| --- | --- | --- |
| OPFS (origin private file system) | 109 | 16.4 |
| WebGPU | 121 (Android 12+) | **Safari 26, no flag** |
| Same-document View Transitions | 111 | 18 |
| Cross-document `@view-transition` | 126 | 18.2 |
| File System Access (file picker) | **132 (Jan 2025)** | No |
| Web Share | 61 | 12.2 |
| Web Share Target (receiving shares) | Yes | **No** |

WebGPU landed on iOS in Safari 26 and WebKit says outright that it *"supersedes WebGL."* File System Access went the other way — it only reached Android in Chrome 132 in early 2025, and iOS doesn't have it. **OPFS is the common denominator**: if you need large file storage on both sides, use OPFS. Always feature-detect `navigator.gpu`.

### Reality check: how are the legendary PWAs doing?

This is the least comfortable section of the article, and the most valuable. Every "PWA success" post cites the same five cases. I checked each of them on 21 Aug 2026:

| Case | The stat everyone quotes | Status today |
| --- | --- | --- |
| **Twitter Lite** (2017) | +65% pages/session, 600 KB vs a 23.5 MB Android app | ☠️ **Dead.** `lite.twitter.com` returns 404; the `com.twitter.android.lite` Play listing disappeared around early 2024. `x.com` is still installable, **but its service worker is a self-destroying stub** — the code literally comments itself as a *"self-destroying service worker,"* calls `skipWaiting()`, deletes every cache, and unregisters. |
| **Starbucks** (2017) | "233 KB, 99.84% smaller than the 148 MB iOS app" | ☠️ **Dead.** `app.starbucks.com` now 301s to `www.starbucks.com`; the old host stopped serving around Sept–Nov 2025. The new site has a `manifest.json` but **no `display` key and no service worker** → by Chrome's criteria it is **not installable**. |
| **Flipkart Lite** (2015) | +70% conversions for installed users | ✅ **Genuinely alive.** `sw.js` is a real 87 KB file and the manifest is **still literally named "Flipkart Lite."** But the stats are a **ten-year-old** snapshot. |
| **Pinterest** (2017) | +44% ad revenue, TTI 23s → 5.6s | ✅ **Genuinely alive.** ~1.2 MB service worker, `standalone` manifest, push wired up. Stats are still from 2017–2018. |
| **Uber m.uber** (2017) | 50 KB gzipped, interactive in 3s on 2G | ✅ **Alive**, moved to `/go/`; `sw.js` is a real 283 KB file. |

Two lessons:

1. **Stop citing Starbucks and Twitter Lite.** They are now evidence for the opposite conclusion. And the "Starbucks doubled daily active users" figure half the internet repeats **is not in the primary source** and traces back to nothing.
2. **The three that survived are all content-browsing, network-dependent, large-scale apps in bandwidth-constrained markets.** That is precisely the zone where PWAs win.

## Path 2: native shell + WebView

The most common path, and Capacitor is the current default.

**Current state (checked 21 Aug 2026):**

- `@capacitor/core` **8.5.0**, released **31 Jul 2026** — a "breaking minor" that touches iOS only, moving to **UIScene** so it builds against Xcode 27/iOS 27.
- **Capacitor 8.0** shipped 8 Dec 2025: **Swift Package Manager is now the default** for new iOS projects instead of CocoaPods, plus automatic Android edge-to-edge. Ionic reported Capacitor **nearing one million downloads per week**.
- **Capacitor 9 alpha**: **Cordova is no longer pulled in by default.**
- v8 minimums: **iOS 15+, Android 7 (API 24)+, Node 22, Xcode 26**.
- **Ionic Framework 9.0.0** shipped **19 Aug 2026**.

The actual workflow, surprisingly short if you already have a web app:

```bash
npm i @capacitor/core
npm i -D @capacitor/cli
npx cap init                  # asks for app name + package ID

npm i @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios               # --packagemanager SPM | Cocoapods

npm run build                 # your bundler
npx cap sync                  # copy web bundle + update native deps
npx cap run ios
```

One small trap that costs an afternoon: the `index.html` in your build output **must contain a `<head>` tag**, or plugins silently fail to work.

### One real case, with numbers

This is rare: an engineering post rather than marketing, with before/after measurements. Fintech **Found** migrated from Cordova to Capacitor (2 Jun 2025):

| Metric | Before | After |
| --- | --- | --- |
| iOS cold start (p95) | 20–40 seconds | ~10 seconds |
| Android ANR rate | 0.60% | 0.20% |

The ANR number matters more than it looks, because **Google Play's bad-behavior threshold is 0.47%** — they crossed from violating to compliant. Their reason for not rewriting natively is refreshingly blunt: *"as an organization we didn't want to invest the resources in a full rewrite, or switch to a cross-platform framework like Flutter or React Native due to the steep learning curve for most engineers at the company (we typically hire full stack developers…)"* ([Found Engineering](https://found.com/engineering/migrating-from-cordova-to-capacitor)).

But read the other number carefully too: **p95 after optimization is still 10 seconds.** That is the reality of a large WebView app on weak hardware, not a marketing figure.

### The JIT story: almost everyone has it backwards

The familiar line is "WebViews are slow because JavaScript isn't JIT-compiled on iOS." **It's backwards.**

- JavaScript inside `WKWebView` **does get JIT**. Each WKWebView runs in its own OS-managed `WebContent` process where JavaScriptCore runs all four tiers, LLInt → Baseline → DFG → FTL.
- **Hermes, React Native's default engine, has no JIT** — it compiles AOT to bytecode at build time.

Which means **on raw long-running JavaScript throughput, a WebView app can beat a React Native app on iOS.** That doesn't make RN slower overall — it wins back time by not building a DOM and not doing CSS layout — but it demolishes the "WebViews are slow because no JIT" argument entirely.

### Where WebViews genuinely lose (1): the 60fps ceiling on iOS

This is the hard limit, and it has a bug number.

**`WKWebView`'s page rendering is pinned near 60fps, and no public API lifts it.** WebKit Bugzilla **294338**, filed 11 Jun 2025, status **NEW, P2, with no reply from Apple**. The reporter shows that disabling the internal preference `PreferPageRenderingUpdatesNear60FPSEnabled` *"easily allows 120 FPS, whereas the default behavior remains near 60 FPS."* Developers from Tauri, Capacitor, Ionic and Construct 3 are in the thread ([WebKit Bugzilla 294338](https://bugs.webkit.org/show_bug.cgi?id=294338)).

The nuance matters: compositor-driven CSS `transform`/`opacity` animations and scrolling **can still hit 120Hz**. What's pinned at 60Hz is **`requestAnimationFrame`** — "by design."

Put plainly: **on a ProMotion display, native/Flutter/RN interfaces run at 120Hz by default; a JS animation loop inside a WebView does not.** The only escape is private API — non-zero App Store rejection risk, and the equivalent Tauri plugin was rejected from the Mac App Store.

### Where WebViews genuinely lose (2): the iOS/Android asymmetry

The second problem is that **you don't get to choose the engine on iOS**:

- **Android**: the WebView is Chromium, updated through Play on Chrome's cadence. In 2026 alone, through 13 Aug, there have been **19 Android WebView updates**. But **Chrome/WebView 138 is the last version supporting Android 8.0/8.1/9**, so a slice of devices is permanently frozen on an old WebView.
- **iOS**: WebKit, welded to the OS version. Guideline **2.5.6** is explicit: *"Apps that browse the web must use the appropriate WebKit framework and WebKit JavaScript."*

And there is now a number that quantifies the cost. In June 2026 Microsoft's Edge team published results from an experimental Blink build on iOS using BrowserEngineKit, measured on the same device against Safari:

| Benchmark | Delta vs Safari |
| --- | --- |
| Speedometer 3.1 | **+28.6%** (49.27 vs 38.3) |
| JetStream 3 | +13.1% |
| MotionMark 1.3.1 | +2.1% |

Microsoft explicitly labels this a research prototype on personal hardware, not lab conditions. But ~29% on Speedometer is the best available estimate of **the performance a WebView app on iOS is leaving on the table**.

As for "alternative engines thanks to the DMA": two and a half years after BrowserEngineKit shipped in iOS 17.4, **nobody has shipped an alternative engine on iOS, not even in the EU**. And there's a detail that's easy to misread: Apple's two entitlements are for **browsers** and for **in-app browsing of third-party content**. **A Capacitor app rendering its own bundled UI cannot qualify.** BrowserEngineKit is not an escape hatch for hybrid apps.

### Where WebViews genuinely lose (3): scroll, swipe, keyboard

This is maintenance tax rather than a hard limit — but it's real and it costs time:

- **iOS swipe-back isn't built into Capacitor.** The GitHub discussion has been open since 4 Nov 2022 with **no reply**. Enabling `allowsBackForwardNavigationGestures` gives you WebKit's history gesture, not your SPA's route stack — and combined with Ionic's own gesture it **navigates back twice**.
- **WebKit bug 158325** — `position: fixed` elements drift out of their hit-test region when rubber-banding is disabled, exactly the configuration hybrid apps use. Filed **2 Jun 2016**, still **NEW**. Ten years.
- **Keyboard**: Capacitor ships **four** iOS resize strategies (`native`/`body`/`ionic`/`none`) precisely because none is universally correct. On iOS, `window.resize` doesn't fire when the keyboard appears — only `visualViewport` changes.
- **Edge-to-edge**: Android 15 (API 35) forces edge-to-edge and Android 16 **removes the opt-out flag entirely**. `env(safe-area-inset-*)` reports wrong values on Android WebView below 140, so Capacitor has to inject its own CSS variables from native `WindowInsets` — patched across **four releases: 8.3.0 / 8.3.1 / 8.3.2 / 8.4.0**.

The fairest framing: native/Flutter/RN apps get Android 15's inset handling from the platform; the WebView stack needed four patch releases plus a CSS shim because the WebView's own `env()` is broken.

## Path 3: Hotwire Native — web content, native navigation

If your app is server-rendered (Rails, Laravel, Django, Phoenix), this is the least-known path and often the best fit.

The tagline captures the whole idea: **"Content is all web. Navigation is all native."**

The mechanism: the native shell intercepts every link tap, screenshots the current page, pushes a new screen onto the native stack with platform-correct animation, then loads that screen's HTML into a web view. On swipe-back it uses the captured screenshot, so the interactive pop gesture feels genuinely native. Navigation is configured with **a single JSON file** mapping URL patterns to screen presentations.

Status: **iOS and Android are both at 1.3.x** (Jul/Aug 2026), built by 37signals and used in **Basecamp, HEY, and ONCE**.

The one number they published says plenty: moving **a single** screen to web **deleted 1,436 lines across 10 files**. *"All changes to this page now happen entirely on the web side. Need a fourth filter? Add it on the web and deploy immediately."*

**But here is where you need to read carefully, because it's the biggest citation trap in the entire topic.**

The "90% HTML, 10% native" figure that every Hotwire article quotes is **DHH, May 2014, about Basecamp 2** — the `UIWebView` era, before `WKWebView` even existed. **37signals has never published a web/native ratio for HEY or for modern Basecamp.** Their most recent architecture post (2017, on Basecamp 3) explicitly declines to give one, calling it *"a spectrum rather than a binary,"* and states that **all four main tabs are 100% native**.

And there's another fact they volunteered: DHH disclosed that 37signals maintains **a team of nine native developers** for Basecamp and HEY. In that same post, on their newest product line: *"we're going all-in on PWAs for our new ONCE products."*

Read that again: **the company that builds Hotwire Native chose PWAs — not Hotwire Native — for its own newest product line.** That doesn't make Hotwire Native bad. It means even its authors treat it as a tool for a specific class of problem rather than a universal answer.

On ecosystem scale, be honest: `hotwired/hotwire-native-ios` has roughly **300 stars**, and **no large enterprise outside 37signals is verifiably using it**. The public adopter list (The StoryGraph, Context Travel, Strety) is all small companies, and the only source compiling it is a consultant who sells Hotwire Native services.

*(Secondary trap: lists claiming "Shopify, Coinbase, GitLab use Hotwire" are about **Turbo/Stimulus on the web** and have nothing to do with mobile apps.)*

## Path 4: JavaScript, but not web

Briefly, because it's categorically different:

- **React Native 0.87** (11 Aug 2026). The New Architecture became the default in **0.76** (Oct 2024), became the **only** option in **0.82** (Oct 2025), and the legacy code was **deleted outright in 0.84** (Feb 2026). If you have an unmigrated RN app, the deadline has passed.
- **Expo SDK 57** (30 Jun 2026), bundling RN 0.86.
- The "write once, run on web too" story goes through **React Native for Web**, which powers the entire X website. But `react-native-web`'s latest release is **0.21.2, from 16 Oct 2025** — nearly a year without a release.

On operating cost at scale, Shopify is the most honest source available. After five years on RN they report **>99.9% crash-free sessions** and **sub-500ms P75 screen loads**, and they publish the downsides themselves: *"Updating an app to each new version of React Native takes a significant amount of work and often requires refactoring the codebase,"* and *"Mobile engineers who specialize in iOS and Android are essential… There is no substitute for experience."* They state that 100% React Native is a deliberate **anti-goal**: *"Native is still the best way for building cutting-edge features that leverage device hardware like 2D/3D scanning and running AI models on-device."*

One detail worth noting for anyone weighing RN: **Shopify still uses a WebView — for checkout.** Their Checkout Sheet Kit preloads checkout in a *"background webview."* That's the most sensible pattern I've seen: an RN shell for the app, web for the one surface that must stay server-controlled.

## Store gauntlets: where the two platforms diverge most

### Google Play: yes, but three deadlines are closing

The canonical path is **Trusted Web Activity** — your PWA is rendered by **the actual Chrome browser**, not a WebView, so you get the full modern web platform. The tool is **Bubblewrap** (`@bubblewrap/cli` **1.25.0**, 31 Jul 2026) or PWABuilder, which is a wrapper around Bubblewrap.

**Things you must get right:**

1. **The targetSdk deadline.** From **31 Aug 2026**, new apps and updates on Play **must target Android 16 (API 36)** or higher; extensions are available until **1 Nov 2026**. Bubblewrap **1.25.0 meets this; 1.24.x and earlier target SDK 35 and do not.**
2. **The Play Billing deadline.** On the same day, **31 Aug 2026**, all new apps and updates must use **Billing Library 8 or later**. This kills a range of older IAP plugins — RevenueCat's Cordova SDK says outright: *"Billing Client v7 will be the last version this SDK supports… meaning Google will not allow updates to your app after August 31, 2026."*
3. **Digital Asset Links.** `assetlinks.json` must live at `https://<host>/.well-known/assetlinks.json` carrying the SHA-256 fingerprint of the **Play App Signing key**, not your local build key. Get it wrong and the TWA silently degrades to a Custom Tab — with a visible URL bar.
4. **Quality thresholds.** Exceed them and you lose store visibility **and get a warning printed on your store listing**:

| Metric | Overall | Per device model |
| --- | --- | --- |
| User-perceived crash rate | **1.09%** | 8% |
| User-perceived ANR rate | **0.47%** | 8% |

The ANR threshold is particularly dangerous for WebView apps, because Google **documents** that WebView initialization blocks the UI thread and causes ANRs — they had to ship `WebViewCompat.startUpWebView()` to mitigate it.

On policy, one widespread rumor needs correcting: **Play does not ban WebView shell apps.** The actual clause targets wrapping *someone else's* website: *"We don't allow apps whose primary purpose is to drive affiliate traffic to a website or provide a webview of a website **without permission from the website owner or administrator**."* Wrapping your own PWA is not what that targets. What Play does ban is apps with "limited content and functionality."

*(Minor note: the "minimum Lighthouse score of 80" requirement for TWAs that many blogs cite **does not appear in Google's current documentation** — the separate quality-criteria page was removed.)*

### App Store: this is the weak link

There is no way to submit a PWA to the App Store. You submit a native app that renders your web content in a WKWebView.

And that app is judged under **guideline 4.2 Minimum Functionality**: *"Your app should include features, content, and UI that elevate it beyond a repackaged website. If your app is not particularly useful, unique, or 'app-like,' it doesn't belong on the App Store."*

**This clause is human-judged, subjective, and outcomes vary by reviewer.** Some real cases:

- An Ionic app rejected in Dec 2020: *"Your app provides a limited experience as it is not sufficiently different from a mobile browsing experience. Specifically, we noticed that most of the app content links out to Safari."* It passed on the **third submission**; the author admits they don't know which change did it.
- A WebView app rejected **10 consecutive times** under 4.2 (Nov 2025). The official forum response was an offer to book a 1:1 consultation.
- Multiple developers report adding push notifications, Core Location, and share sheets and **still** being rejected.

Which means: **"just add push notifications" is not a reliable cure.**

Three clauses that are less known and bite hard:

- **4.2.6**: *"Apps created from a commercialized template or app generation service will be rejected unless they are submitted directly by the provider of the app's content."* Using an app-generation service to wrap a client's site and submitting under your account — broken. The permitted route is bundling all clients into **a single binary** using a picker model.
- **4.2.3(ii)**: if you download resources on first run, you **must disclose the size and ask the user first**.
- **4.7.2** — the trap for anyone planning a mini-app platform: *"Your app may not extend or expose native platform APIs or technologies to the software without prior permission from Apple."* (Your own web content bundled in the binary isn't governed by 4.7 at all — you're judged under 4.2. Plenty of articles misread 4.7 as "the HTML5 loophole.")

And on **9 Jun 2026 Apple revised 4.3(b)**, adding an explicit removal threat: apps not meaningfully different from what already exists *"may [be removed] from the App Store going forward,"* while repeatedly submitting low-quality apps *"may lead to removal from the Apple Developer Program."*

**How people who actually ship WebView apps get through:** ship the thinnest possible v1, then build up. Concretely: a native tab bar with 3–5 entry points, every core feature within two taps, **no links that bounce out to Safari**, decent offline handling (a blank WebView with no network reads exactly like "a browser"), and hide the web-only chrome — marketing footers, cookie banners, and especially the **"download our app on the App Store" banner**, which Apple genuinely rejects apps over.

The governing principle: **if you removed the WebView and the app still had value, you're fine.**

## Selling inside the app: the rules just flipped, and it's in your favor

If your app takes money, this is the area that has changed most in the last 18 months — and most articles online still describe the old world.

**The defaults haven't changed.** Apple 3.1.1: *"If you want to unlock features or functionality within your app… you must use in-app purchase,"* with your own mechanisms — license keys, QR codes — explicitly banned. Google: *"Google Play's billing system is required for developers offering in-app purchases of digital goods and services distributed on Google Play."*

**But in the US market, both have been forced open — by courts, not goodwill.**

**Apple's side.** After the 30 Apr 2025 contempt ruling in Epic v. Apple, the current guidelines (updated 8 Jun 2026) contain a clause spliced mid-sentence: *"In all other storefronts, **except for the United States storefront, where this prohibition does not apply**, apps and their metadata may not include buttons, external links, or other calls to action that direct customers to purchasing mechanisms other than in-app purchase."*

In other words: **apps on the US storefront may include buttons, links, and calls to action sending users to web checkout, with no entitlement required.** And **the guidelines currently name no commission at all** on those linked-out purchases. The Ninth Circuit (11 Dec 2025) upheld the contempt findings but struck the blanket commission ban, permitting a "reasonable" rate **to be set by the district court on remand**. Apple has **proposed** 15% / 10% / 5% (13 Aug 2026) but **no court has approved it**. The Supreme Court granted certiorari on 30 Jun 2026, but only on the **standard for civil contempt** — not on the commission question.

**Google's side.** Effective **29 Oct 2025**, Google stated it *"will not require the use of Google Play Billing… or prohibit the use of in-app payment methods other than Google Play Billing"* for US users. Two programs are live, but **they carry fees**:

| | Recurring subscriptions | Other digital content |
| --- | --- | --- |
| First $1M in annual earnings | 10% | 10% |
| Standard service fees | 10% | 20–25% |
| Play Games Level Up / Apps Experience | 10% | 15–20% |

Plus a fixed fee per install via external link: **$3.65 for games, $2.85 for apps**. And **from 1 Oct 2026, developers enrolled in these programs must report transactions and pay the service fees.**

**Three practical takeaways:**

1. **Don't architect your payment strategy around a commission number you read on a blog.** Apple's US rate is currently **legally undetermined** and under active review. Re-verify against primary sources before every financial plan.
2. **Apple's 3.1.3(b) is the multiplatform app's friend**: you may let users access content purchased elsewhere — *"provided those items are also available as in-app purchases within the app."* Allowed, but you need the parallel IAP.
3. **Technically, Capacitor has no official IAP plugin.** Capacitor's own docs point you at the third-party `cordova-plugin-purchase`, or `@revenuecat/purchases-capacitor` (requires a paid backend). If selling is your business model, treat this as a real risk, not a footnote.

## Native access: what's ready, what you'll write yourself

This is the section comparison tables render as "Full native access ✅" and then skip. The details are where projects die.

**Fine, ready to use:**

- **Deep links / Universal Links / App Links** — identical to native apps, no hybrid tax. The only failure mode is **silent failure**: misconfigure it and links just open the browser.
- **Push** — `@capacitor/push-notifications` v8.1.2. But read the docs: *"This plugin does not support iOS Silent Push,"* and data-only notifications **will NOT fire the callback if the app has been killed**.

**Available, but narrower than you think:**

- **Camera** — `@capacitor/camera` is **the OS photo-capture dialog and gallery picker, not a camera feed**. No custom viewfinder, no per-frame access. QR scanning, AR, document edge detection, real-time filters — all need `getUserMedia` in the WebView (weaker) or an entirely different plugin.
- **Biometrics** — the plugin every tutorial links to (`capacitor-native-biometric`) **was last released 14 Jun 2023 and is abandoned**. The maintained one is `@aparajita/capacitor-biometric-auth` (v10, Feb 2026). This is the ecosystem's general pattern: **the most famous plugin is not the maintained one.**

**Weakest of all: background execution.**

`@capacitor/background-runner` is **a separate headless JS runtime, not your WebView**: no DOM APIs at all, most Web APIs absent. The docs say plainly *"iOS will determine when and how often your task will ultimately run,"* each run is capped at roughly **30 seconds**, and it **does not execute in the simulator**. Minimum repeat interval: 15 minutes.

**And these have no path at all, for architectural reasons:** app extensions, widgets, and CarPlay on iOS are **separate binaries using declarative UI APIs (SwiftUI/templates) — they structurally cannot host a WKWebView.**

| Feature | Reality |
| --- | --- |
| **Home screen widgets** | No official plugin. Community plugins bridge **data only**, via App Groups. **Widget UI can never be web** — you write SwiftUI (WidgetKit) and RemoteViews (Android). |
| **Live Activities** | Community only. ActivityKit caps payloads at **4 KB** and requires a hand-written SwiftUI widget extension. |
| **watchOS** | The *official* `@capacitor/watch` plugin is **v0.1.12, released 8 Apr 2024**, peer-depending on `@capacitor/core ^5.0.0` — three majors behind 8.5. The repo labels itself *"experimental, unsupported."* |
| **App Clips / Instant Apps** | **No plugin exists.** A community proposal opened Apr 2021 and never materialized. |
| **Siri / App Intents** | No maintained plugin. |
| **CarPlay / Android Auto** | **Nothing on npm at all.** CarPlay UI is template-based and cannot host a WebView. |

If any of these is a product requirement, **the "no native engineers needed" premise collapses** — you'll need a Swift developer *on top of* the hybrid stack, combining the downsides of both.

## OTA updates: correcting a clause number everyone gets wrong

This is the single biggest reason people choose web technology. But both the legal basis and the infrastructure just got shaken up.

### What the clause is actually called

Nearly every article cites **"Apple guideline 3.3.2."** Two things are wrong with that sentence:

1. It's **not a Review Guideline** — it lives in the **Apple Developer Program License Agreement**, a different contract.
2. It has **been renumbered**. In the current DPLA, **§3.3.2 is "Regulatory Compliance"**; the code-download clause is **§3.3.1(b)**.

The clause that is actually **enforced at review time** is **Review Guideline 2.5.2**: *"Apps should be self-contained in their bundles… nor may they download, install, or execute code which introduces or changes features or functionality of the app."*

The escape hatch lives in DPLA 3.3.1(b): *"interpreted code may be downloaded to an Application but only so long as such code: (a) does not change the primary purpose of the Application… (b) does not create a store or storefront for other code or applications, and (c) does not bypass signing, sandbox, or other security features of the OS."*

**The pragmatic rule: JS/HTML/CSS pushed into a WebKit WebView is permitted, as long as it doesn't change the app's primary purpose.** Bug fixes, copy changes, layout changes are safe. Shipping a whole new product area over the air is not. And **don't use forced-update dialogs on iOS** — requiring users to pass through an update flow before using the app is its own separate violation.

### What's still alive

| Tool | Status |
| --- | --- |
| **Microsoft CodePush** | ☠️ **Dead.** App Center shut down **31 Mar 2025**; `microsoft/react-native-code-push` was **archived read-only on 20 May 2025**. |
| **Ionic Appflow** | 🔴 **Sunsetting.** Stopped selling **11 Feb 2025**; existing customers have access through **31 Dec 2027**. `@capacitor/live-updates` sits at 0.5.0. |
| **Expo EAS Update** | 🟢 Very active. Free at 1,000 MAU, $19/mo for 3,000, $199/mo for 50,000. |
| **`@capgo/capacitor-updater`** | 🟢 Very active (8.51.14, 20 Aug 2026). AGPL backend, self-hostable. From $12/mo. |
| **Shorebird** (Flutter) | 🟢 Active. |
| **Tauri** | ❌ The Updater plugin **supports neither Android nor iOS**. |
| Self-hosted `lisong/code-push-server` | 🔴 **Don't.** It looks alive but that's dependabot; the **last functional commit is from 2019**, with 195 open issues. |

Two things stand out about compliance claims, because they differ sharply:

- **Shorebird is the only vendor that quotes the governing clause in full and explains its own technical mechanism against it** (they fork the Dart VM into an on-device interpreter, landing squarely in the "interpreted code" carve-out), then put abuse in their terms of service.
- **Expo deliberately warrants nothing**: *"your updates need to follow the App Store and Play Store guidelines… you are ultimately responsible for your app's behavior."*
- **Ionic asserts "fully compliant" without citing any clause.** On their own forum, someone asked for the citation on 22 May 2024 — no Ionic staff ever replied.

On actual risk: the documented rejections arrive under **2.3.1 "hidden features"** first, with 2.5.2 appearing only on appeal. One reported case involved an app **that wasn't even serving OTA updates**, which suggests a scanner with false positives. The mitigation every source agrees on: **describe your update mechanism in Notes for Review**, don't ship undeclared dormant features, and keep shipping binaries regularly.

## Four myths worth dropping

**1. "Cordova is dead."** False. Cordova is **not** in the Apache Attic. The June 2026 Apache board minutes record *"community health is strong"*; `cordova-ios@8.1.1` shipped 7 Jul 2026, `cordova-android@15.1.0` shipped 22 Jul 2026, plus a CVE fix in June 2026. What died was **Adobe PhoneGap** (2020) and **Microsoft App Center's Cordova support** (2022 — Microsoft's stated reason: Cordova SDK calls were *"less than 1%"* of the service). New projects should still pick Capacitor.

**2. "OutSystems bought Ionic and killed Capacitor."** Half wrong. What closed was the **commercial tier** (Appflow, Identity Vault, Auth Connect, Secure Storage, Portals); that same announcement affirms Ionic Framework and Capacitor *"will remain free and open source."* The evidence: Capacitor 8.5 on 31 Jul 2026, Ionic 9 on 19 Aug 2026, nearly a million weekly downloads.

**3. "Apple banned PWAs in the EU."** False. Apple **did** announce removing Home Screen web apps in the EU in Feb 2024, then **reversed it on 1 Mar 2024**.

**4. "The Amazon app is mostly WebViews."** This one gets repeated constantly, and **it has no source at all**. Trace it back and you reach exactly two places: a blog post by a company that **sells website-to-app wrapping services**, and an anonymous post on Blind. Amazon has never stated it. What Amazon *has* stated points the other way: they've used **React Native** since around 2016, and their new Vega OS puts React Native in the OS layer.

*(Companion trap: "Amazon WebView" is real, but it's the replacement WebView engine in **Fire OS** for Fire TV/Tablet — not evidence about the shopping app.)*

## Who's actually running web technology in production

Read this section closely if you're planning to use case studies to convince a manager.

**Ionic's case study library has a property few people notice: the pages render no dates, but the HTML meta tags carry them.** Extract them and you find that **Ionic's newest customer case study is from September 2023.** They have published no new ones in roughly three years.

There's a deeper problem: **most of those case studies sell live updates, Identity Vault, or Portals as the payoff — products that stopped selling in Feb 2025 and die at the end of 2027.** They are architecturally stale even where the apps still exist.

The three most-misused names:

- **"Southwest Airlines uses Ionic"** — the sourced app is **SWA U**, an **internal new-hire onboarding app** (shuttles, hotels, campus maps), documented only on an undated agency portfolio page. Not the booking app.
- **"T-Mobile uses Ionic"** — that's **T-Mobile Cast**, an internal podcast/video app built by a five-person HR team.
- **"Volkswagen uses Ionic"** — that's **GroupUI**, a **design system** built with Stencil. Not a mobile app.

Also: the "Disney" case study is about **Disney's Magical Express**, a service Disney discontinued on 31 Dec 2021. The "NHS" case study covers two internal apps written in **AngularJS**, which reached end of life in Dec 2021.

**The more trustworthy entries in that library:** **AAA** (a genuine consumer app, 62M members, store rating went from 2.1 to 4.3), **Breeze Airways** (a genuine consumer airline app, launched May 2021, one team covering iOS + Android + web), **H&R Block MyBlock** (three codebases consolidated into one), **BBC Children's Games**, and **Bestinvest**. Even these date from 2021–2023 and none has been re-verified for 2026.

**In the other direction, one case is more instructive than all of them:** in 2018 Discord published *"Why Discord is Sticking with React Native,"* explaining they used RN **on iOS only** because the Android attempt didn't meet their bar. That post still ranks at the top of search results. But in 2025 Discord themselves wrote: *"The Android client transitioned to React Native in 2022."* They reversed their own conclusion three years later, and the industry is still citing the old post.

That's the biggest methodological lesson in this whole topic: **engineering blog posts have no expiry date, but their conclusions do.**

The three anti-web citations that appear in nearly every comparison suffer the same fate: **Zuckerberg's "HTML5 was our biggest mistake" (2012 — 14 years old), LinkedIn abandoning mobile web (2013 — 13 years), and Airbnb's "Sunsetting React Native" (2018 — 8 years).** All three predate `WKWebView`, Service Workers, PWAs, Hermes, and the New Architecture. The Airbnb post also contains a detail few people reach: RN at Airbnb was **80,000 lines across 220 screens**, while the **native codebase was roughly 10× larger** — RN was never the majority of that app, and Airbnb say themselves the decision reflected **their organization**, not RN's viability.

## Cost and timeline: the only published numbers

Joe Masilotti (30+ shipped Rails-backed apps) is the only person I found publishing comparative timelines. **He's a Hotwire Native consultant, so he isn't neutral** — but his stated downsides are specific enough to check:

| Option | Timeline | Downside he names himself |
| --- | --- | --- |
| Native (Swift + Kotlin) | **6–12+ months** | Build everything **three times**; three codebases forever |
| React Native | **4–8 months** | Still **a codebase entirely separate from your web app** |
| PWA | **~1 week** | No IAP, limited iOS push, **no store presence** |
| Hotwire Native | **1–2 months** | Still managing Xcode + Android Studio; **no offline support yet** |
| Flutter | — | Learn Dart; **"overkill"** for a web business adding mobile |
| Capacitor | — | Fits **JavaScript** teams; **"a mismatch"** with server-rendered Rails |

Cross-checked against two enterprise sources:

- **Shopify** reported in 2020 that its Compass app shared ~99% of code and launched on both platforms in **three months**. But in 2025 they also published the cost of *staying*: the New Architecture migration raised Android startup ~10% and iOS ~3%, made some components **up to 20% slower**, and dropped stability below their 99.95% target for weeks.
- **SoFi** (~15M users) migrated from separate native apps to Flutter, reporting a **60% reduction in lines of code** feature-for-feature and **over 1 million lines eliminated** overall. **talabat** completed its Flutter migration in 2024 and reports a **4× release cadence**. These are Google-published case studies — credible that the migrations happened, worth reading skeptically on the numbers.

As for the cold-start benchmark you keep seeing — "Ionic 400–800ms vs Flutter 200–400ms" — **it has no source.** It traces only to SEO posts that describe no methodology. **There is no credible public webview-vs-native cold-start benchmark for 2024–2026.** The only real number is Found's above — and it's 10 seconds.

The academic evidence is thin but directionally consistent: the ICWE 2021 study (Huber/Demetz/Felderer) compared five implementations of the same app. Native used the least energy; notably, **Capacitor used less energy than the PWA running in Chrome**. It's the only study I found with a Capacitor arm — and it's from 2021.

## There's a fifth path that rarely makes these comparisons

If what you actually want is **to not write business logic twice** — rather than "reuse HTML" — there's an option these articles rarely include: **Kotlin Multiplatform**.

Google officially supports KMP on Android as of I/O 2024, and scopes it precisely: **share business logic, not UI**. **Google Docs** on Android, iOS and Web uses KMP for shared logic. **Netflix** does the same — shared logic in Kotlin, with UI still in native **Jetpack Compose and SwiftUI**.

This inverts every path above: instead of sharing the presentation layer and accepting that it doesn't quite feel native, KMP shares the layer underneath and lets each platform draw its own. The cost is writing UI twice and needing engineers on both sides. The benefit is a UI that never feels "almost native."

## Which one to pick

| Your situation | Pick |
| --- | --- |
| Existing SPA web app, need both stores | **Capacitor** |
| Server-rendered app (Rails/Laravel/Django) | **Hotwire Native** |
| No store needed, fast install, bandwidth-constrained market | **Pure PWA** + prompt users to add to home screen |
| Android only, want the latest web platform | **TWA + Bubblewrap ≥ 1.25.0** |
| Animation-heavy, gesture-heavy, very long lists, need 120Hz | **React Native / Expo** or native |
| Need Bluetooth, USB, or NFC on iOS | Not web — native plugin or native app |
| Need widgets, Live Activities, watch, CarPlay | Native (or native + hybrid, paying both costs) |
| Want to eliminate duplicated *logic*, not duplicated *UI* | **Kotlin Multiplatform** |
| Desktop-first, mobile secondary | **Tauri 2** — but note it has no mobile OTA |

There's one rule that sources with opposing interests — Ionic's CEO, the Expo team (competitors), a Hotwire consultant, and vocal critics on Hacker News — **independently agree on**:

> **Betting on WebViews is safest for data-dense, always-connected, B2B-leaning apps. It's most dangerous for consumer-facing, gesture-heavy, offline-required, or animation-heavy apps.**

And the governing rule: **don't choose by framework, choose by what you're not allowed to sacrifice.** If that's shipping speed and an existing web team, path 2 or 3 almost always wins. If it's 120fps touch feel and a ten-thousand-row list, no web path will save you.

## FAQ

**Will Apple reject a WebView app?**
Not automatically, but the risk is real and unpredictable — one developer was rejected 10 times in a row. Guideline 4.2 rejects *"repackaged websites,"* not WebViews. What decides it is whether your app does anything a browser can't. The most effective tactic is a thin v1 with no links bouncing out to Safari, then building up. Watch 4.2.6 specifically if you're using an app-generation service.

**Do PWAs get push notifications on iOS?**
Yes, since iOS 16.4, but **only once the user has added the web app to the home screen**. Never in a Safari tab, still true today.

**Does iOS delete PWA data after 7 days?**
In a browser tab, yes. **Installed home screen web apps are exempt** — WebKit states that ITP skips those domains when purging. This is the strongest technical reason to push users to install.

**Can a WebView app run at 120Hz on an iPhone Pro?**
Scrolling and compositor-driven CSS animations can. **`requestAnimationFrame` cannot — it's pinned at 60Hz by design**, and WebKit bug 294338, open since June 2025, still has no reply from Apple. If your UI depends on a JS animation loop, this is a hard ceiling.

**Do I have to use IAP to sell in my app?**
By default, yes, on both stores. But **on the US storefront Apple now permits buttons and links to web checkout with no entitlement**, and the guidelines currently name no commission — because the courts haven't set one. Google also opened up on 29 Oct 2025, but **with fees** (10–25% plus a fixed per-install fee). This area is moving fast; re-verify against primary sources before making financial plans.

**Capacitor or Cordova for a new project?**
Capacitor. Cordova is alive and still shipping releases, but Capacitor is where the ecosystem is flowing, and from Capacitor 9 onward Cordova becomes opt-in rather than default.

**Can I build a home screen widget in HTML?**
No, and you never will be able to. iOS WidgetKit uses declarative UI APIs in a separate binary that structurally cannot host a WKWebView. Widgets, Live Activities and CarPlay all require native code. If your product needs them, budget for a Swift engineer from the start.

**Is CodePush still usable?**
No. App Center shut down on 31 Mar 2025 and the repo was archived on 20 May 2025. On React Native, move to **EAS Update**; on Capacitor, **Capgo**; on Flutter, **Shorebird**. Don't self-host `lisong/code-push-server` — its real code is from 2019.

**Do I need macOS to build an iOS app with web technology?**
Yes. Every path to the App Store goes through Xcode, and Xcode is macOS-only. Only pure PWAs avoid it — and they don't reach the App Store either.

**How long until the native shell is unnecessary?**
On Android, it nearly is already, if you accept distribution outside Play. On iOS, don't wait: BrowserEngineKit has existed for over two years without a single shipped alternative engine, and its two entitlements were never meant for hybrid apps. Plan as if the status quo holds.
