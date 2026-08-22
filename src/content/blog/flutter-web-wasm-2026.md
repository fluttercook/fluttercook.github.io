---
title: "Flutter on the web compiled to WebAssembly: what you get, what you give up"
description: "flutter build web --wasm is not an optimization flag — it swaps dart2js for dart2wasm, requires WasmGC in the browser, and drops dart:html from under your dependency graph. Here is the mechanism, a real package:web and @JS interop example, and the limits that no compiler flag removes."
seoDescription: "flutter build web --wasm in practice: dart2wasm vs dart2js, the WasmGC gate and JS fallback, moving off dart:html to package:web, and Flutter web's real limits."
keywords:
  - flutter build web wasm
  - dart2wasm vs dart2js
  - wasmgc browser support
  - package web dart js interop
  - migrate from dart html
  - flutter web seo limitations
category: "Analysis"
topic: "Flutter Web"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🌐"
tags: ["Flutter", "Web", "WebAssembly", "Dart", "Interop"]
sources:
  - name: "Flutter — Support for WebAssembly (Wasm)"
    url: "https://docs.flutter.dev/platform-integration/web/wasm"
  - name: "Flutter — Web renderers"
    url: "https://docs.flutter.dev/platform-integration/web/renderers"
  - name: "Dart — JavaScript interop"
    url: "https://dart.dev/interop/js-interop"
  - name: "Dart — package:web"
    url: "https://dart.dev/interop/js-interop/package-web"
  - name: "package:web on pub.dev"
    url: "https://pub.dev/packages/web"
  - name: "MDN — WebAssembly"
    url: "https://developer.mozilla.org/en-US/docs/WebAssembly"
  - name: "WebAssembly — feature roadmap"
    url: "https://webassembly.org/roadmap/"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "web-tech-to-mobile-app-2026"
    title: "Using web technology to build mobile apps: the 2026 technical map"
draft: false
---

`flutter build web --wasm` reads like a flag you turn on for speed. It is closer to switching runtimes. Behind it sits **dart2wasm**, a different compiler from dart2js, emitting code for a different machine, with a different set of core libraries available to you. Code that compiled yesterday can stop compiling today — not because it is wrong, but because it imports a library that no longer exists on the target.

The migration cost is almost never in your own code. Most application code never touches `dart:html` directly; it calls a package, which calls a package, which does. So the first `--wasm` build of a real app usually fails somewhere three levels down your dependency graph, in a file you have never opened, in a package you did not choose deliberately.

And past all of that sits the part no compiler flag changes: a Flutter web app paints into a canvas. The bytes that arrive in the browser are an application, not a document. That single fact drives most of the honest limitations below — first paint, SEO, find-in-page, autofill — and it is unaffected by which compiler produced them.

This post covers what the flag actually does, what the WasmGC requirement means for who can run your build, what the `dart:html` removal costs in an app that already ships, a working interop example, and the cases where the right answer is not Flutter at all.

## `--wasm` swaps the compiler, not the optimizer

dart2js takes your program and emits JavaScript. Dart's class model gets flattened onto JS objects, and the resulting code lives at the mercy of the JS engine's dynamic behaviour: hidden classes, megamorphic call sites, and numbers that are all doubles underneath.

dart2wasm emits a WebAssembly module instead. Importantly, it does not target the old linear-memory model — the Emscripten style, where a program brings its own heap in a big `ArrayBuffer` and ships its own garbage collector inside the binary. It targets **WasmGC**, the proposal that gives WebAssembly engine-managed struct and array types collected by the browser's own garbage collector.

That choice has consequences worth understanding, because they explain both the upside and the gate:

- Dart objects become Wasm structs. Field offsets and virtual dispatch are resolved by the compiler against declared types, rather than by a JS engine guessing object shapes at runtime.
- No garbage collector ships in your bundle. The browser's existing collector manages Dart objects directly.
- `int` is a real 64-bit integer, like it is on the Dart VM, instead of a JavaScript double wearing a Dart type.

What it is not is "native speed". Wasm is a compilation target with a good instruction set and a typed memory model. It removes a class of overhead in the *language runtime*. It does nothing about layout, rasterisation, network latency, or how much you download before the first pixel.

| | dart2js | dart2wasm (`--wasm`) |
|---|---|---|
| Output | `main.dart.js` | `main.dart.wasm` plus a `.mjs` support module |
| Memory | JS objects, JS engine GC | WasmGC structs, browser GC |
| `int` | JavaScript double underneath | true 64-bit integer |
| `dart:html`, `dart:js`, `dart:js_util` | available (deprecated) | not available |
| Browser requirement | any modern browser | WasmGC support |
| JS interop | calls land directly in JS | values convert at the Wasm/JS boundary |

That last row is the one people trip over. Interop is not free under dart2wasm: strings, lists and Dart closures have to be marshalled across the boundary. A per-frame interop call in a hot path that felt free under dart2js is no longer free. It is still fast — it is just no longer nothing.

## WasmGC is a hard gate, and the JS fallback is why you can ship anyway

WasmGC is a browser engine feature. You cannot polyfill it, shim it, or ask a bundler to work around it. Either the engine implements the proposal or your module does not instantiate.

Chromium shipped it in version 119 and Firefox in version 120, both in late 2023. Safari came considerably later, and if a meaningful share of your traffic is on older iOS or macOS Safari, check the current state on MDN or the WebAssembly roadmap rather than trusting any blog post, including this one.

Flutter's answer is to ship both. A `--wasm` build produces the WebAssembly output *and* a dart2js fallback, and the bootstrap script feature-detects the browser and loads whichever one it can run. Build your app and list `build/web` to confirm exactly what your Flutter version emitted — this behaviour has changed across releases, and the directory listing is the ground truth.

Two practical consequences follow.

**Your deploy carries two compiled copies of the app.** Any given visitor downloads only one — the loader decides before fetching the large artefacts — but your bucket, your CDN, and your build time all carry both. If you know your entire audience has WasmGC (an internal tool with a managed browser fleet, say), the fallback is dead weight you are paying to store and invalidate.

**You now have two builds with two numeric semantics.** dart2js maps `int` onto JS doubles; dart2wasm uses real 64-bit integers. Code that touches large integers, bit manipulation, hashing, or ID values near or past 2^53 can behave differently depending on which artefact the visitor loaded. If you ship the fallback, your test matrix has to include a browser that takes it.

One deployment detail that costs an afternoon if you miss it: your server must send `.wasm` files with the `application/wasm` content type. Some static hosts do not do this by default, and the failure surfaces as an instantiation error rather than anything that says "MIME type".

## `dart:html` is out, so the migration is really a dependency audit

Under dart2wasm the old web libraries are simply not there: `dart:html`, `dart:js`, `dart:js_util`, `dart:svg`, `dart:indexed_db`, `dart:web_audio`, `dart:web_gl`. The replacements are **`package:web`** for browser APIs and **`dart:js_interop`** for the JavaScript boundary.

`package:web` is generated from the Web IDL definitions, which means its names follow the platform rather than Dart's older hand-written wrappers. You get `document.querySelector(...)`, `window.localStorage.setItem(...)`, `element.remove()` — fewer Dart-flavoured conveniences, and a much more predictable mapping when you are reading MDN with one hand.

Your own code is usually a small diff. The dependency graph is the work. Two things help:

- pub.dev marks packages that are compatible with WebAssembly on the package page, so you can check a candidate before you adopt it.
- The compiler names the offending library and the package it came from, so the first failing build is a to-do list rather than a mystery.

If you maintain a package that supports both web and native, the conditional import key changed too. `dart.library.html` is false under dart2wasm; the condition that is true on every web compiler is `dart.library.js_interop`:

```dart
export 'src/storage_stub.dart'
    if (dart.library.js_interop) 'src/storage_web.dart'
    if (dart.library.io) 'src/storage_io.dart';
```

For runtime branching inside shared code, `package:flutter/foundation.dart` exposes `kIsWeb` for "am I on the web at all" and `kIsWasm` for "was this compiled by dart2wasm". They answer different questions and you usually want the first one.

When a transitive dependency has not migrated, you have four options and no fifth: upgrade to a version that has, override to a fork that has, replace the package, or vendor the handful of functions you actually use into your own codebase. Budget for at least one of these on any app with a non-trivial dependency list.

## What interop actually looks like

Two layers. Use `package:web` when the thing you want is a browser API. Reach for `dart:js_interop` and `@JS` only when the thing you want is a JavaScript library you loaded yourself.

Browser APIs first — this is ordinary, boring code:

```dart
import 'package:web/web.dart' as web;

/// Removes the static loading markup you put in web/index.html.
void hideBootSplash() {
  web.document.querySelector('#boot-splash')?.remove();
}

void rememberTheme(String value) {
  web.window.localStorage.setItem('theme', value);
}

String? savedTheme() => web.window.localStorage.getItem('theme');
```

Now a third-party JS library. Say your analytics vendor ships a script tag and exposes a global, which you load from `web/index.html`:

```html
<script src="https://cdn.example-vendor.com/telemetry.js"></script>
```

You describe its shape to Dart with an extension type and an `external` declaration. Nothing is generated, nothing is checked against the real library — an extension type is a compile-time view over a `JSObject`, so you are asserting a shape, and you are responsible for asserting it correctly:

```dart
import 'dart:js_interop';

/// A typed view over the plain JS object the vendor expects.
extension type TrackProps._(JSObject _) implements JSObject {
  external factory TrackProps({String screen, String locale});
}

/// Binds to `window.appTelemetry.track(name, props)`.
@JS('appTelemetry.track')
external void track(String name, TrackProps props);

void logScreenView(String screen, String locale) {
  track('screen_view', TrackProps(screen: screen, locale: locale));
}
```

Three rules that save time here. Primitives — `String`, `int`, `double`, `bool` — may appear directly in `external` signatures and are converted for you. Anything richer crosses explicitly: `.toJS` going out, `.toDart` coming back, including `JSPromise` to `Future` and Dart closures to `JSFunction`. And when the shape is genuinely dynamic, `jsify()` / `dartify()` and the `getProperty` / `setProperty` helpers in `dart:js_interop_unsafe` will do it — at the price of moving every mistake from compile time to runtime, which is exactly the trade the library's name is warning you about.

## Budgeting the migration in an app that already ships

The sequence that wastes the least time:

1. Run `flutter build web --wasm` on the current codebase and read the failures. Do this before estimating anything.
2. Split the list into code you own and code you do not. The first half is work you can schedule; the second half is work you can only negotiate.
3. For each failing dependency, check pub.dev for a newer version, then the issue tracker, then a maintained alternative. Decide fork-versus-replace early, because a fork is a permanent cost.
4. Rewrite your own web-only files against `package:web`.
5. Test the runtime, not just the build. Old `dart:js_util` code that looked up members by string compiles happily and fails at runtime; the compiler cannot help you there.
6. Test the fallback path too, on a browser without WasmGC, if you are serving it.

Some things do not change and are worth stating so nobody plans around them: there are no isolates on the web under either compiler, `dart:io` is unavailable, `compute()` runs your callback inline on the main thread rather than moving it anywhere, and `dart:mirrors` does not exist. Also check the release notes for your Flutter version before you plan around `deferred as` code splitting — how dart2wasm handles deferred imports has not always matched dart2js, and if lazy-loading a heavy route is a core part of your size strategy, verify it holds rather than assuming.

## The renderer is a canvas, and that is where the real ceiling is

Flutter web draws through Skia. With `--wasm` that means **skwasm**, the Wasm-native rendering path, rather than the JS-driven CanvasKit build. The DOM-based HTML renderer was removed in Flutter 3.29, so "just render to real DOM elements" is no longer an available answer.

The multithreaded rendering path requires **cross-origin isolation** — the `COOP` and `COEP` response headers. Turning those on is not a local change: every third-party iframe, image, font and script your page loads must then carry the right CORP or CORS headers, or it stops loading. Embedded YouTube players, payment iframes and ad tags are the usual casualties. Check what your page embeds before you commit to the headers.

Then the properties that follow from painting into a canvas, all of which are true regardless of compiler:

- **First paint is bootstrap-bound.** The browser downloads the engine and the app, initialises them, and only then paints. There is no server-rendered HTML to look at in the meantime, and no streaming.
- **There is no text in the DOM.** Search crawlers and social preview bots that do not execute JavaScript see your `index.html` and nothing else. Route-specific Open Graph tags require server-side work, because whatever your server sends for `index.html` is the whole story as far as the bot is concerned.
- **Browser features that operate on the DOM do not see your content.** Ctrl+F, native text selection, page translation extensions, and password manager autofill are all working against markup that does not contain what the user sees.
- **Accessibility is a parallel tree.** Flutter builds a semantics tree in the DOM for assistive technology, and you can force it on with `SemanticsBinding.instance.ensureSemantics()`. It exists for screen readers. It is not an SEO surface, and building a content strategy on it is a bad bet.

## When a Flutter web app is the wrong choice

The decision rule is short. If the page's value is its **content and its discoverability**, the DOM is the product and you should use a tool that produces DOM. If the page's value is an **application that happens to run in a tab**, canvas is a reasonable substrate and Flutter buys you one codebase across platforms.

| What you are building | Flutter web with `--wasm` | Better served elsewhere |
|---|---|---|
| Internal dashboard behind a login | Good fit — no SEO requirement, known browsers | |
| Design, diagram or canvas-style editor | Good fit — you were going to paint pixels anyway | |
| Companion web build of an existing Flutter app | Good fit — the codebase already exists | |
| Marketing site, blog, docs | | React/Next, Astro, plain HTML — content must be in the DOM |
| Storefront or anything ranked by search | | A server-rendered web framework |
| Long public form flows | | HTML forms, for autofill and password managers |
| Widget embedded on someone else's page | | Plain JS — the payload is too heavy otherwise |

The uncomfortable middle case is the consumer product that is genuinely an app but also needs to be found. Splitting it — a static marketing and content site at the root, the Flutter app on a subpath or subdomain — is usually cheaper and more honest than trying to make a canvas rank.

## FAQ

**Do I have to migrate to `package:web` even if I never use `--wasm`?**
Eventually, yes, and you should decouple the two decisions. `dart:html` is deprecated for everyone, not only for Wasm targets, so the migration to `package:web` and `dart:js_interop` is maintenance you owe regardless. Doing it first also turns the `--wasm` question into a build-flag experiment instead of a project.

**Will `--wasm` make my app faster?**
It changes where the language runtime spends time — typed field access, no shipped garbage collector, real integers — and it does nothing for layout, rasterisation, asset download, or network round trips. Whether that shows up in your app depends entirely on whether Dart execution was your bottleneck. Profile the build you actually ship rather than trusting a number from someone else's app.

**What happens on a browser without WasmGC?**
It loads the dart2js fallback that the same build produced, so the app still runs. That means part of your audience is running a different compiler's output, with different `int` semantics, and it needs to be in your test matrix. Check `build/web` to confirm your Flutter version emitted the fallback before relying on it.

**Can I use an npm library from a Flutter web app?**
Yes, by loading it yourself with a script tag in `web/index.html` and declaring its shape with extension types and `@JS`. There is no bundler integration and no module resolution — you own the load order, and you own the correctness of the shape you declared, because nothing verifies your `external` declarations against the real library.

**Is Flutter web viable for SEO?**
For an application behind a login, the question does not arise. For public content, treat it as not viable: the content is not in the DOM, crawlers that do not execute JavaScript see an empty shell, and prerendering workarounds are fragile and easy to get wrong. Serve content from something that emits HTML and reserve Flutter for the application surface.

---

*The mechanisms described here — WasmGC, the compiler split, the interop boundary, the canvas rendering model — are stable properties of the approach. The version-dependent details are not: browser support levels, exactly what a `--wasm` build emits into `build/web`, renderer names and flags, and deferred-loading behaviour have all moved across Flutter releases and will move again. Verify those against the linked Flutter and Dart documentation for your version. The recommendations about when not to use Flutter web are my opinion, formed from the constraints above rather than from any benchmark.*
