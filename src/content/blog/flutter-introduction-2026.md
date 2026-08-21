---
title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
description: "A Google PM built a 3D tic-tac-toe game with Flutter and published every prompt. I checked the timestamps against the commit history — and used that repo as an introduction to Flutter: widgets, Dart, hot reload, Impeller, and four bugs that show why you still have to understand the framework."
seoDescription: "A 2026 introduction to Flutter for beginners: what Flutter is, widgets, Dart 3.13, hot reload, Impeller, flutter_scene, material_ui and cupertino_ui leaving the SDK, installing from scratch, and the real lesson from a 3D game built with AI in 15 minutes."
keywords:
  - what is flutter
  - learn flutter from scratch
  - flutter for beginners
  - flutter widgets explained
  - flutter hot reload
  - what is dart
  - flutter_scene 3d
  - flutter 3.47
category: "Tutorial"
topic: "Flutter"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-08-21"
emoji: "🐦"
tags: ["Flutter", "Dart", "Beginner", "Impeller", "3D", "AI"]
sources:
  - name: "Abdallah Shaban on X — the game built with flutter_scene"
    url: "https://x.com/AbdallahSh07/status/2090475954053513515"
  - name: "flutter_scene_tic_tac_toe — the full prompt log"
    url: "https://github.com/abdallahshaban557/flutter_scene_tic_tac_toe/blob/main/PROMPTS.md"
  - name: "flutter_scene on pub.dev"
    url: "https://pub.dev/packages/flutter_scene"
  - name: "Flutter Scene — installation guide"
    url: "https://fscene.dev/getting-started/installation/"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Google Antigravity"
    url: "https://antigravity.google/"
  - name: "Gemini 3.7 Flash in Google Antigravity"
    url: "https://antigravity.google/blog/gemini-3-7-flash-in-google-antigravity"
  - name: "Install Flutter — official docs"
    url: "https://docs.flutter.dev/get-started/install"
related:
  - slug: "web-tech-to-mobile-app-2026"
    title: "Using web technology to build mobile apps: the 2026 technical map"
draft: false
---

On 20 August 2026, **Abdallah Shaban** — who works on product for Flutter at Google — posted a video of a 3D tic-tac-toe game: the X and O pieces are characters with eyes that blink, they drop onto the board with an elastic bounce, and when one side wins, the winning pieces go and *eat* the losers. He said he built it in 15 minutes, and — the valuable part — **published every prompt in a public repo**.

<figure class="tweet-embed">
<blockquote class="twitter-tweet" data-theme="dark" data-media-max-width="620"><p lang="en" dir="ltr">I built this game in 15 minutes with flutter_scene and <a href="https://twitter.com/FlutterDev">@FlutterDev</a>, using <a href="https://twitter.com/antigravity">@antigravity</a> and Gemini 3.7!</p>&mdash; Abdallah Shaban (@AbdallahSh07) <a href="https://twitter.com/AbdallahSh07/status/2090475954053513515">August 20, 2026</a></blockquote>
<script>(function(){var b=document.querySelector('figure.tweet-embed blockquote.twitter-tweet');if(b&&window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches){b.setAttribute('data-theme','light');}})();</script>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
<noscript><a href="https://x.com/AbdallahSh07/status/2090475954053513515"><img src="https://pbs.twimg.com/amplify_video_thumb/2090475913079373824/img/-tqL0NKGpqizib_u.jpg" alt="3D tic-tac-toe game built with flutter_scene" loading="lazy" /></a></noscript>
<figcaption>The original demo video by <a href="https://x.com/AbdallahSh07/status/2090475954053513515">Abdallah Shaban</a>. Every prompt is public in the repo's <a href="https://github.com/abdallahshaban557/flutter_scene_tic_tac_toe/blob/main/PROMPTS.md">PROMPTS.md</a>.</figcaption>
</figure>

I checked that number. It holds up better than I expected, but the real story is more interesting than the number:

- First prompt: **19 Aug at 20:27:19** (−07:00).
- First commit, named `tic tac toe`: **20:39:36** the same evening.
- ⏱️ **12 minutes** from the first instruction to a committed, playable game.
- But the version in the video: **15 prompts, 11 commits, finishing at 23:16 — 2 hours and 49 minutes.**

Both numbers are true, and side by side they are the best introduction to Flutter I could find. The first 12 minutes show you how *fast* Flutter is. The remaining 2 hours 49 minutes — which include four bug reports — show that **you still have to understand the framework**.

This article uses that repo as its teaching material. Every figure here is checked against primary sources: the prompt log, the commit history, and the project's actual `pubspec.yaml`.

## What Flutter is, briefly

Flutter is Google's toolkit for writing **one** codebase that runs on **six** targets: iOS, Android, web, macOS, Windows, Linux. You write it in **Dart**.

But that sentence leaves out the part that matters most. What makes Flutter genuinely different is this:

> **Flutter does not use the operating system's widgets, and it does not embed a WebView. It ships its own graphics engine and paints every pixel onto a blank canvas.**

The consequences are large, and both the good and the bad come from the same root:

| Because Flutter paints its own pixels… | you get | and you give up |
| --- | --- | --- |
| No dependency on OS widgets | An interface identical on every device and OS version | Inheriting platform design changes automatically |
| Its own engine (Impeller) | Steady 60/120fps animation, and **a 3D engine can live inside it** | A bigger binary than an equivalent native app |
| No DOM, no WebView | None of the browser's limits | No reuse of your existing web code |

That middle row is why this article opens with a 3D game. Because Flutter owns the whole rendering pipeline, someone was able to **build a 3D engine inside it** — that is `flutter_scene`. No WebView-based "cross-platform" framework can do that; I went through the difference in detail in [the map of building mobile apps with web technology](/blog/web-tech-to-mobile-app-2026/).

## Everything is a widget

This is the first concept, and the most important one.

In Flutter, a **widget** is not just a button or a text field. Padding is a widget. Centering is a widget. A background colour is a widget. A screen is a widget. The app itself is a widget.

You do not *mutate* the interface — you **describe** it. You write a function that takes the current state and returns a widget tree describing the screen *for that state*. When state changes, the function runs again, Flutter diffs the new tree against the old one, and repaints only what differs.

```dart
class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Counter')),
      body: Center(
        child: Text('Tapped $_count times'),
      ),
      floatingActionButton: FloatingActionButton(
        // setState tells Flutter the state changed — run build() again.
        onPressed: () => setState(() => _count++),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

Three things to take from this, because they recur in every Flutter app:

1. **`build()` must be cheap and safe to call at any time.** It can run 60 times a second. Don't read files or call APIs in it.
2. **`setState()` is a declaration that data changed**, not a paint command. You never issue a paint command directly.
3. **Composition, not inheritance.** Need padding? Wrap it in `Padding`. Need centering? Wrap it in `Center`. Widget trees nest deeply as a result — that's normal, not bad code.

Anyone coming from React will feel at home immediately. Anyone coming from Android Views or UIKit will spend a few days unlearning the habit of holding a reference to a widget and setting properties on it — in Flutter you almost never do that.

## Dart, and why it exists

A fair question: why not JavaScript, or Kotlin?

Because Dart has one property Flutter needs, and few languages ship both modes:

- **During development: JIT compilation.** Change code, reload it into the running VM in under a second.
- **For release: AOT compilation** to real machine code. No interpreter, no runtime warm-up.

That pair is what produces **hot reload** — and hot reload is why those 12 minutes were possible.

Dart also has mandatory **sound null safety**: a `String` is guaranteed to hold a value, and if you want to allow absence you write `String?`. A whole family of null-pointer bugs is caught at compile time. The version shipping with Flutter 3.47.1 is **Dart 3.13.1**.

## Hot reload: the thing you'll use most

Change one line, hit save, and the interface updates **while the app keeps its state**. You're four screens deep, logged in, halfway through a form? All still there. Only the code changed.

Beginners underrate this until they try it. It turns UI work from "edit — build — tap back to where you were — look" (30–60 seconds per cycle) into "edit — look" (under a second). For interface tuning, that isn't a 10% difference; it's two orders of magnitude.

It is also exactly what made the AI loop in the tic-tac-toe repo so fast: the agent edits code, hot reload pushes it into the running app, the result is visible immediately. `flutter_scene` takes it further — it **hot-reloads `.glb` model files and materials too**, so tweaking a 3D character doesn't require a restart either.

Two things worth knowing so you don't get stuck:

- Changes to **UI and code inside functions**: hot reload picks them up instantly.
- Changes to **global variables, `static` initializers, or `main()`**: you need a **hot restart** (the app restarts, state is lost). This is the usual cause of "I changed it but nothing happened."

## Reading the 3D game repo as a real Flutter project

The whole game fits in **6 Dart files, about 65 KB**. The structure is very typical:

```text
lib/
├── main.dart                    # entry point, builds the root widget
├── game/
│   └── game_controller.dart     # rules, win checking, state
├── scene/
│   ├── tic_tac_toe_scene.dart   # the 3D scene, camera, tap picking
│   ├── animated_piece.dart      # piece animation
│   └── piece_builder.dart       # geometry for the X and O characters
└── ui/
    └── game_overlay.dart        # the 2D scoreboard layered on top
```

The most notable architectural point: **the 2D interface and the 3D scene are two separate widget trees, stacked with `Stack`.** The scoreboard, turn indicator and buttons are ordinary Flutter widgets — only the board itself is 3D. This is almost always the right call: don't build your buttons in 3D.

`pubspec.yaml` — the dependency manifest every Flutter project has — is surprisingly short too:

```yaml
environment:
  sdk: ^3.13.1

dependencies:
  flutter:
    sdk: flutter
  flutter_scene: ^0.22.2      # the 3D engine
  vector_math: ^2.4.2         # vector maths for ray casting
  hooks: ^2.2.0               # runs an asset step at build time
```

That `hooks` entry is new to many people: Flutter now supports **build hooks**. `flutter_scene` uses one to convert `.glb` files into an optimised binary format at build time rather than parsing glTF at runtime — `dart run flutter_scene:init` generates that hook file for you.

## The four bugs — and why they're the most important part of this article

Of the 15 prompts, **four were bug reports**. This is the part worth studying, because it answers the question every beginner is asking in 2026: *if AI can write it, why do I need to understand Flutter?*

**Bug 1 — taps landing on the wrong tile.** Tapping a square didn't reliably place a piece there after the first time. This is a **ray casting** problem: the tap is a 2D screen coordinate, the board lives in 3D, so you must cast a ray from the camera through that point and intersect it with the board's plane. Nothing about this is Flutter-specific — it is 3D graphics maths, and without knowing the concept you couldn't even describe the bug well enough for an AI to fix it.

**Bug 2 — `RenderFlex overflowed`.** The classic yellow-and-black stripes. This is **the most common beginner error in Flutter**, so learn it now:

Flutter lays out by the rule **"constraints go down, sizes go up."** A parent passes its children the width/height limits they may use; each child picks its own size within those limits and reports back up. A `Row` by default lets its children take their natural size. If their combined width exceeds the space available, the `Row` does **not** shrink them — it overflows, and Flutter raises an error rather than silently clipping your content away.

The fix is almost always one of three:

```dart
// 1. Let a child flex into the space that's actually left
Row(children: [Expanded(child: Text(veryLongName)), const Icon(Icons.star)])

// 2. Let the text wrap or truncate with an ellipsis
Expanded(child: Text(veryLongName, overflow: TextOverflow.ellipsis))

// 3. Scroll horizontally, if the content really is wider than the screen
SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(...))
```

Worth noting: the user simply **pasted the raw error message** to the AI. That worked only because Flutter's error messages are unusually well written — it names the overflowing widget, the axis, and suggests `Expanded`. **Reading Flutter error messages is a skill, and AI doesn't devalue it.**

**Bug 3 — characters facing backwards.** The pieces dropped in with their faces pointing away. Coordinate systems and rotation — again 3D knowledge, not Flutter.

**Bug 4 — cropping on small screens.** On smaller displays the camera cut off part of the board. That's **responsive design**, which every mobile app has to handle.

The summary: AI produced a playable build in 12 minutes, but **all four remaining bugs required a human to notice the problem, name it correctly, and describe it**. Exactly one is pure Flutter knowledge (layout), one is responsive design, and two are 3D maths. That is an honest picture of AI-assisted development today — it raises typing speed enormously. It does not replace knowing what you're looking at.

## Flutter today: four things a beginner needs to know now

The current stable release is **Flutter 3.47.1 (19 Aug 2026)** with Dart 3.13.1; 3.47.0 landed on 12 Aug 2026.

**1. The familiar import line is about to become legacy.** For nine years, nearly every Flutter file has started with `import 'package:flutter/material.dart';`. As of 3.47, **`material_ui` and `cupertino_ui` are standalone packages on pub.dev**, both at 1.0. The copies inside the SDK still work, but they are **formally scheduled for deprecation in the November stable release**. For a beginner this means: the tutorials you read right now are still correct, but their import line is on the way out. There's an automated migration:

```bash
flutter pub add material_ui cupertino_ui
dart fix --apply --code=migrate_design_widgets
```

The reason for the split isn't tidiness: bound to the SDK, the Cupertino widgets could only ship fixes four times a year, while Apple changes its design whenever it likes. I wrote about [that migration separately](/news/flutter-material-ui-cupertino-ui-migration-guide/).

**2. Impeller is now the default renderer on every platform except web.** This is the graphics engine that replaced Skia; it compiles shaders ahead of time at build so you don't get first-run frame hitches. It is also the foundation that makes `flutter_gpu` and `flutter_scene` possible at all.

**3. Minimum OS versions went up.** iOS 15+, macOS 12+. Older tutorials quoting lower numbers won't build without a config change.

**4. Widget Previews are stable.** Preview a widget in your IDE without running the whole app — worth turning on from day one.

## Actually starting: from zero to a running app

```bash
# 1. Install Flutter using the official guide for your OS:
#    https://docs.flutter.dev/get-started/install

# 2. Check your environment — this tells you exactly what's missing
flutter doctor

# 3. Create a project
flutter create my_app
cd my_app

# 4. Run it. Without -d, Flutter asks which device to use.
flutter run
```

`flutter doctor` is your best friend in week one. It doesn't just report what's missing, it prints the command to fix it. If you're stuck during setup it's almost always unaccepted Android SDK licences (`flutter doctor --android-licenses`) or missing Xcode command line tools.

Once the app runs, do exactly one thing to understand why people like Flutter: open `lib/main.dart`, change any string, and save. Watch the simulator. That's hot reload.

And if you want to run the 3D game from the top of this article:

```bash
git clone https://github.com/abdallahshaban557/flutter_scene_tic_tac_toe.git
cd flutter_scene_tic_tac_toe
flutter pub get
flutter run --enable-flutter-gpu
```

The `--enable-flutter-gpu` flag is required on native platforms — Flutter GPU is not on by default. On web (`flutter run -d chrome`) you don't need it, because the web path goes through WebGL2.

## Where Flutter is strong, and where it isn't

Plainly, because an introduction that only praises is useless.

**Strong:**

- **One codebase, six platforms, an identical interface.** Not "similar" — identical, because Flutter paints it.
- **Hot reload.** Still the fastest development loop in mobile.
- **Animation and custom interfaces.** Because you own the rendering pipeline, unusual designs don't fight the framework the way they do with OS widgets.
- **Desktop and embedded as serious targets**, not afterthoughts.

**Weak:**

- **Binary size.** You're shipping an engine, so a Flutter app is always larger than the equivalent native app.
- **Deep platform integration still needs native code.** Home screen widgets, Live Activities, App Intents — still Swift/Kotlin. Flutter doesn't remove that requirement.
- **Satisfaction with the iOS-style widgets is the lowest in the whole ecosystem** — the Q2 2026 survey puts Cupertino at **61%**, down 6 points, against Dart at 92% and the core framework at 90%. That is precisely why the packages were split out.
- **Web is still the weakest target.** Impeller isn't there yet, and the download is far heavier than an ordinary web page.
- **No reuse of existing web code.** If your biggest asset is a web app and a web team, Flutter doesn't help you leverage it.

## So is the 3D actually usable?

Yes, with the boundaries understood. `flutter_scene` is at **0.22.2**, published by the verified `bdero.dev` publisher, requires Flutter 3.47 or newer, and supports all six platforms (web through WebGL2). It has glTF model import, PBR lighting, skeletal animation and physics.

But the version number still starts with a zero, and that means something: the API will change. Using it for a 3D component inside an ordinary app is reasonable; betting a commercial game on it deserves a read of [the dedicated analysis of Flutter GPU and flutter_scene](/news/flutter-gpu-3d-rendering-flutter-scene/) first.

One small detail from the tic-tac-toe repo is worth noticing: `flutter_scene` **ships a set of agent skills** — documentation that teaches an AI assistant the library's idioms instead of letting it guess, installed with `dart run flutter_scene:skills`. That signals a spreading trend: packages now ship instructions for machines, not just docs for people.

## FAQ

**Can I learn Flutter with no programming experience?**
Yes, but learn a little Dart first. Dart is statically typed with syntax close to Java/JavaScript/C#, so it comes quickly if you know any of them. The hard part for beginners isn't syntax — it's the **declarative mindset**: describing the interface from state, rather than commanding individual elements to change.

**Flutter or React Native?**
If your team is already a JavaScript/React team, React Native is closer to home. If you're starting fresh and want a consistent interface and a fast development loop, Flutter is usually the more pleasant option. One common misconception is worth clearing up: **neither one reuses your existing web frontend** — that belongs to a different family of solutions, which I covered in [the article on web technology for mobile apps](/blog/web-tech-to-mobile-app-2026/).

**Do I need a Mac?**
Only to build for iOS or macOS — Xcode is macOS-only. To learn Flutter and ship Android, web, Windows and Linux apps, a Windows or Linux machine is entirely sufficient.

**How long until I can build a real app?**
For someone who already programs: about a week to be comfortable with widgets and layout, a few more weeks for state management, networking and navigation. The biggest time sink is usually not Flutter itself — it's **the release process for two app stores**.

**If AI can write Flutter apps, why learn it?**
Look again at the repo at the top. AI produced a playable build in 12 minutes, but the remaining 2 hours 49 minutes were four rounds of a human **spotting a bug, naming it, and describing it** — including `RenderFlex overflowed`, which you cannot fix without understanding Flutter's constraint model. AI makes the typing far faster. It does not yet do the part where you know what you're looking at.

**Should I start with the new `material_ui` or the SDK's `material.dart`?**
If you're starting today, use the new `material_ui` package. The SDK copy still works but is scheduled for deprecation from the November stable release, and there's no reason to start on something that's being replaced.

**Is Flutter dying? Will Google cancel it?**
A fair question to ask about any Google product. The current evidence points the other way: 3.47.0 and 3.47.1 both shipped in August 2026, Impeller just became the desktop default, the design system was split out so it can ship faster, and Google is wiring Flutter into its own AI tooling. These are not the signals of an abandoned project.
