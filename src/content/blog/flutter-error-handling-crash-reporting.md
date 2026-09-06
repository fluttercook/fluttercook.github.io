---
title: "Flutter error handling: catching what actually reaches users"
description: "Flutter has four separate places an error can escape: the framework, the current zone, the platform dispatcher, and the isolate. Wire all four, symbolicate the stack traces, and stop shipping crashes you never see."
seoDescription: "Flutter error handling and crash reporting: FlutterError.onError, PlatformDispatcher.onError, Isolate.addErrorListener, ErrorWidget.builder, obfuscation and symbolication, and what to log versus swallow."
keywords:
  - flutter error handling
  - fluttererror onerror crashlytics
  - platformdispatcher onerror
  - flutter isolate error listener
  - flutter errorwidget builder
  - flutter symbolicate obfuscated stack trace
category: "Deep Dive"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-16"
emoji: "🚨"
tags: ["Flutter", "Errors", "Monitoring", "Production", "Debugging"]
sources:
  - name: "Handling errors in Flutter — Flutter documentation"
    url: "https://docs.flutter.dev/testing/errors"
  - name: "FlutterError — Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/FlutterError-class.html"
  - name: "PlatformDispatcher — Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/PlatformDispatcher-class.html"
  - name: "Isolate.addErrorListener — Dart API"
    url: "https://api.dart.dev/stable/dart-isolate/Isolate/addErrorListener.html"
  - name: "Obfuscating Dart code — Flutter documentation"
    url: "https://docs.flutter.dev/deployment/obfuscate"
  - name: "ErrorWidget — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ErrorWidget-class.html"
related:
  - slug: "flutter-memory-leaks-devtools"
    title: "Finding a Flutter memory leak: the five objects that never get disposed"
  - slug: "flutter-ci-cd-github-actions"
    title: "A Flutter CI pipeline that catches real problems"
draft: false
---

A crash-free rate of 99.8% sounds excellent until you realise it only counts crashes your reporting tool was wired to see. In Flutter, an error can escape through four different doors, and most apps only guard one or two of them.

## The four doors

| Door | Catches | Missed if unwired |
| --- | --- | --- |
| `FlutterError.onError` | Errors inside the framework: build, layout, paint, gesture callbacks | Red screens, silent layout failures |
| `PlatformDispatcher.instance.onError` | Uncaught async errors in the root zone | Most `Future` failures |
| `Isolate.current.addErrorListener` | Errors in isolates you spawned | Every background-compute failure |
| Native crash handler | Platform-level crashes, plugin native code | Anything that kills the process |

Here is all four, wired once at startup:

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  final crashlytics = FirebaseCrashlytics.instance;

  // 1. Framework errors.
  FlutterError.onError = (details) {
    crashlytics.recordFlutterFatalError(details);
    if (kDebugMode) FlutterError.presentError(details);
  };

  // 2. Uncaught async errors reaching the platform.
  PlatformDispatcher.instance.onError = (error, stack) {
    crashlytics.recordError(error, stack, fatal: true);
    return true; // handled
  };

  // 3. Errors from isolates spawned by this one.
  Isolate.current.addErrorListener(RawReceivePort((List<dynamic> pair) {
    crashlytics.recordError(pair.first, StackTrace.fromString(pair.last));
  }).sendPort);

  runApp(const MyApp());
}
```

Three details worth pausing on.

**Returning `true` from `PlatformDispatcher.onError`** tells the engine the error is handled and should not be re-thrown. Returning `false` lets it propagate to the default handler as well, which usually means a duplicate report.

**`presentError` only in debug.** In release you do not want the framework's own error output; you want the report. In debug you very much want the red screen, because that is how you notice.

**The isolate listener only covers isolates you spawn**, and only those spawned after it is registered. A `compute()` call inherits nothing automatically — errors inside it surface as a failed `Future`, which door two catches, provided nobody swallowed it with an empty `catch`.

`runZonedGuarded` used to be the standard advice and is now largely superseded by `PlatformDispatcher.onError` for this purpose. Using both is not harmful, but is usually redundant; pick one and know which.

## The red screen your users see

In release builds, a build-method exception replaces the widget with a grey box. That is better than a crash and worse than a design decision:

```dart
ErrorWidget.builder = (FlutterErrorDetails details) {
  if (kDebugMode) return ErrorWidget(details.exception);

  return const Material(
    child: Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          'Something went wrong here. Try again in a moment.',
          textAlign: TextAlign.center,
        ),
      ),
    ),
  );
};
```

Set this once. It costs ten lines and turns an alarming grey rectangle into something that reads as intentional.

For a subtree that can fail independently — a feed item, a chart, a plugin-backed view — a small wrapper prevents one failure from blanking the screen:

```dart
class ErrorBoundary extends StatefulWidget {
  const ErrorBoundary({super.key, required this.child, required this.fallback});

  final Widget child;
  final Widget fallback;

  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}
```

Flutter has no built-in error boundary that catches child build errors the way React does — `FlutterError.onError` fires globally, so the practical version scopes by rebuilding a fallback when a known failure mode is detected, rather than by catching arbitrary child exceptions.

## Reports you can act on

A stack trace alone rarely tells you enough. The difference between a bug you can fix and one you stare at is context attached before the crash:

```dart
final class CrashContext {
  static Future<void> setUser(String? id) =>
      FirebaseCrashlytics.instance.setUserIdentifier(id ?? 'anonymous');

  static Future<void> setScreen(String route) =>
      FirebaseCrashlytics.instance.setCustomKey('current_route', route);

  static void breadcrumb(String message) =>
      FirebaseCrashlytics.instance.log(message);
}
```

Log the route on every navigation, the id of whatever record the screen is showing, and the last network call attempted. Then a report reads "crashed on /orders/882 after GET /orders/882 returned 500" rather than "null check operator on a null value".

Do not log personal data. A crash report is a copy of your users' information in a third-party system; user ids and record ids are usually appropriate, email addresses and message contents are not.

## Symbolication, or the reports are useless

Release builds compiled with `--obfuscate --split-debug-info=<dir>` produce stack traces of meaningless symbols. The mapping lives in the directory you specified, and it is different for every build:

```bash
flutter build appbundle --obfuscate --split-debug-info=build/symbols/$VERSION
```

Two rules that people learn the hard way:

1. **Archive the symbols directory per version, in CI**, alongside the artifact. Without the exact file for the exact build, a report cannot be decoded — and rebuilding from the same source does not reproduce it.
2. **Upload symbols as part of the release job**, not manually. A manual step is a step that gets skipped on the release where it matters.

`flutter symbolize -i trace.txt -d build/symbols/1.4.2/app.android-arm64.symbols` decodes a trace by hand when needed.

## What to catch and what to let crash

The instinct to wrap everything in `try`/`catch` produces an app that fails silently and behaves strangely. A rule that holds up:

- **Catch what you can act on.** A network timeout has a retry. A parse failure has a fallback. Catch those, handle them, report at a non-fatal level.
- **Let programming errors crash in debug.** A null assertion failing means your model of the code is wrong. Catching it hides that.
- **In release, degrade rather than die** — but always report. A `catch` block with no report is the mechanism by which a bug survives for months.

```dart
try {
  return await _api.fetchOrders();
} on TimeoutException catch (e, s) {
  FirebaseCrashlytics.instance.recordError(e, s, fatal: false);
  return _cache.orders ?? const [];
}
```

Catching `on TimeoutException` rather than bare `catch` is the part that matters. A bare catch also swallows the `NoSuchMethodError` from your own typo.

## FAQ

**Why do I see errors in the console that never reach Crashlytics?**

Almost always an unwired door — most often `PlatformDispatcher.onError`, or an error inside a `catch` that logs and continues.

**Does this work with Sentry or another tool instead?**

Yes. The four doors are Flutter's, not Firebase's; the SDKs differ only in the recording call.

**Should `FlutterError.onError` report as fatal?**

A framework error usually leaves the app running with broken UI. `recordFlutterFatalError` puts it in the crash-free metric, which is arguably right; `recordFlutterError` reports it as non-fatal. Choose one and be consistent, or your metrics will not mean anything.

**How do I test that reporting works?**

Add a hidden debug action that throws in each of the four contexts, run a release build, and confirm four reports arrive. Do this once per release cycle — reporting silently breaks after dependency upgrades.

**What about errors during `main()` before reporting is initialised?**

Initialise reporting as early as possible, and keep the work before it minimal. Anything failing before that point is invisible by construction.

---

*The four error-handling entry points, `ErrorWidget.builder`, obfuscation and symbolication commands described here are documented in the Flutter references linked above. The catch-what-you-can-act-on rule, the breadcrumb practice, the symbol-archiving advice and the release-cycle verification ritual are my own judgement from operating Flutter apps in production. Crash-reporting SDK APIs change — verify the recording calls against the version you depend on.*
