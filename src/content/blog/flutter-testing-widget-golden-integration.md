---
title: "Flutter tests that fail for a reason: widget, golden and integration"
description: "The test pyramid applied honestly to Flutter: what unit, widget, golden and integration tests each prove, why pumpAndSettle is the wrong default, why goldens diverge between your Mac and Linux CI, and the four things that make a Flutter suite flaky."
seoDescription: "A practical Flutter testing guide: pump vs pumpAndSettle, golden tests that survive CI font differences, integration_test, and fixing flaky tests."
keywords:
  - flutter widget testing
  - flutter golden test ci
  - pumpandsettle vs pump
  - flutter integration_test
  - flaky flutter tests
  - mocktail flutter test
category: "Guide"
topic: "Testing"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧪"
tags: ["Flutter", "Testing", "CI", "Golden Tests", "Dart"]
sources:
  - name: "Flutter — Testing Flutter apps"
    url: "https://docs.flutter.dev/testing/overview"
  - name: "Flutter — An introduction to widget testing"
    url: "https://docs.flutter.dev/cookbook/testing/widget/introduction"
  - name: "Flutter — Integration testing"
    url: "https://docs.flutter.dev/testing/integration-tests"
  - name: "WidgetTester — flutter_test API"
    url: "https://api.flutter.dev/flutter/flutter_test/WidgetTester-class.html"
  - name: "WidgetTester.pumpAndSettle — flutter_test API"
    url: "https://api.flutter.dev/flutter/flutter_test/WidgetTester/pumpAndSettle.html"
  - name: "WidgetTester.runAsync — flutter_test API"
    url: "https://api.flutter.dev/flutter/flutter_test/WidgetTester/runAsync.html"
  - name: "matchesGoldenFile — flutter_test API"
    url: "https://api.flutter.dev/flutter/flutter_test/matchesGoldenFile.html"
  - name: "LocalFileComparator — flutter_test API"
    url: "https://api.flutter.dev/flutter/flutter_test/LocalFileComparator-class.html"
  - name: "FontLoader — Flutter API"
    url: "https://api.flutter.dev/flutter/services/FontLoader-class.html"
  - name: "mocktail on pub.dev"
    url: "https://pub.dev/packages/mocktail"
  - name: "fake_async on pub.dev"
    url: "https://pub.dev/packages/fake_async"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
draft: false
---

There are two kinds of red test. One tells you a behaviour changed. The other tells you the machine was busy, or the CI runner has a different font, or somebody added a shimmer effect three screens away. The second kind is worse than no test at all, because a team that has learned to re-run the pipeline has also learned to ignore the pipeline.

Flutter makes this easy to get wrong in a specific way. `flutter_test` gives you a fake clock and a virtual screen, which is a gift — but the API surface hands you `pumpAndSettle()` on a plate, and `pumpAndSettle()` is a loop that pumps frames until nothing is scheduled. Point it at an indeterminate progress indicator and it will pump for ten minutes and then throw. Golden tests are the other trap: they are genuinely the cheapest way to catch visual regressions, and they are also the thing teams delete after the third week of "passes locally, fails on CI."

This is the pyramid applied to Flutter without the sales pitch: what each layer actually proves, a working example of each, and then a section on the four mechanisms that produce nearly all Flutter flake.

## What each layer can actually prove

The useful question is not "which tests should I write" but "what does this test still pass when it shouldn't."

| Layer | Runs on | Speed | Proves | Blind to |
|---|---|---|---|---|
| Unit (`test`) | Dart VM, no rendering | Milliseconds | Logic, edge cases, state machines | Anything about the tree or the screen |
| Widget (`testWidgets`) | Headless, fake clock, 800×600 virtual screen | Tens of ms | Build/layout/interaction wiring, semantics | Real device I/O, real fonts, real timing |
| Golden (`matchesGoldenFile`) | Same as widget, plus pixel compare | Tens of ms | Pixel-level visual regressions | Everything not in the captured frame |
| Integration (`integration_test`) | A real device or emulator | Seconds to minutes | Plugins, platform channels, startup, navigation across the whole app | Nothing much — which is why it is slow |

The proportions follow from that table, not from a diagram. Logic that can be pulled out of widgets should be tested where it is a thousand times cheaper. Widget tests are where most of your assertions belong, because most bugs in a Flutter app are wiring bugs. Goldens should cover a small, deliberately chosen set of components. And integration tests should cover the handful of flows where a broken plugin would be a production incident: launch, sign in, purchase, and whatever your app's one irreplaceable path is.

## Unit tests: the part that shouldn't need a widget tree

If pricing rules live in a `StatefulWidget`, every pricing test costs you a pump. Move them out and the test is boring, which is the goal.

```dart
// test/pricing_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:shop/pricing.dart';

void main() {
  group('Quote.forCart', () {
    test('applies a percentage promo before shipping', () {
      final quote = Quote.forCart(
        subtotalCents: 10000,
        shippingCents: 500,
        promo: const Promo.percentage('SPRING10', 10),
      );

      expect(quote.discountCents, 1000);
      expect(quote.totalCents, 9500);
    });

    test('a discount larger than the cart clamps at zero', () {
      final quote = Quote.forCart(
        subtotalCents: 300,
        shippingCents: 0,
        promo: const Promo.fixed('OVERKILL', 900),
      );

      expect(quote.discountCents, 300);
      expect(quote.totalCents, 0);
    });
  });
}
```

The interesting unit tests are the ones involving time. Do not use real delays for those — use `fake_async`, which gives you a zone where you advance the clock by hand:

```dart
// test/retry_test.dart
import 'dart:async';

import 'package:fake_async/fake_async.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shop/retry.dart';

void main() {
  test('retries three times with backoff, then gives up', () {
    fakeAsync((async) {
      var attempts = 0;
      Object? failure;

      retry(
        () async {
          attempts++;
          throw TimeoutException('upstream down');
        },
        maxAttempts: 3,
        backoff: const Duration(seconds: 2),
      ).then((_) {}, onError: (Object e) => failure = e);

      async.elapse(const Duration(milliseconds: 1));
      expect(attempts, 1, reason: 'first attempt is immediate');

      async.elapse(const Duration(seconds: 30));
      expect(attempts, 3);
      expect(failure, isA<TimeoutException>());
    });
  });
}
```

A test like this runs in under a millisecond and would take half a minute with real timers. `async.elapse` also fails loudly if your code left a timer running, which is a bug you want to hear about.

## Widget tests are the workhorse, and pump is the whole trick

`testWidgets` runs your test body inside a `FakeAsync` zone. The clock is fake — it starts at 1 January 2015 UTC — the screen is a virtual 800×600 surface, and `Timer` and `Future.delayed` only advance when you say so. That is what makes widget tests deterministic, and it is also why people get confused about how many times to pump.

Here is the mechanism, and it is worth internalising because it explains most "my test sees the old state" bugs. `tester.pump()` flushes pending microtasks and draws a frame — but **only if a frame has actually been scheduled**. So the number of pumps depends on what is on screen. If something is animating, a frame is always pending, and one pump both runs your `.then` callback and draws the result. If the tree is idle, the first pump has nothing to draw: it runs the callback, the callback calls `setState`, and *that* is what schedules the frame the second pump draws. Do not memorise a number — when an assertion is exactly one state behind, add a pump.

```dart
// test/promo_field_test.dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shop/promo_page.dart';
import 'package:shop/quote_repository.dart';

class MockQuoteRepository extends Mock implements QuoteRepository {}

void main() {
  late MockQuoteRepository repository;

  setUp(() {
    repository = MockQuoteRepository();
  });

  Future<void> pumpPage(WidgetTester tester) {
    return tester.pumpWidget(
      MaterialApp(home: PromoPage(repository: repository)),
    );
  }

  testWidgets('shows a spinner while the code is checked, then the discount',
      (WidgetTester tester) async {
    final completer = Completer<Quote>();
    when(() => repository.applyPromo('SPRING10'))
        .thenAnswer((_) => completer.future);

    await pumpPage(tester);
    await tester.enterText(find.byType(TextField), 'SPRING10');
    await tester.tap(find.widgetWithText(FilledButton, 'Apply'));

    // One frame is enough for the loading state to reach the screen.
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    completer.complete(const Quote(discountCents: 1000, totalCents: 9500));
    // The spinner keeps a frame scheduled, so this single pump both runs the
    // .then callback and draws the result. On an idle tree it would take two.
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text(r'-$10.00'), findsOneWidget);
    verify(() => repository.applyPromo('SPRING10')).called(1);
  });
}
```

Two things about that test are deliberate. `Completer` instead of a resolved future means the loading state genuinely exists for an assertable moment — with `thenAnswer((_) async => quote)` you are racing the microtask queue. And `verify(...).called(1)` catches the double-submit bug that a UI assertion never will.

Three habits keep widget tests readable at scale. Prefer semantic finders — `find.widgetWithText`, `find.bySemanticsLabel`, `find.byTooltip` — over `find.byType` on a private widget, because the semantic ones also fail when accessibility breaks. Reach for `find.descendant(of: find.byType(Card), matching: find.text('Total'))` instead of index-based lookups. And when a widget needs a bigger screen than 800×600, set it explicitly and register the reset:

```dart
tester.view.physicalSize = const Size(1600, 2400);
tester.view.devicePixelRatio = 2.0;
addTearDown(tester.view.reset);
```

`tester.runAsync` is the escape hatch for the rare case where fake async cannot help: code that spawns an isolate or hits a real OS thread — decoding an image, a `compute()` call, real file I/O. Inside `runAsync` the zone is real, so you **cannot** pump; do the real work, come back out, then pump.

```dart
// dart:ui as ui, package:flutter/material.dart, package:flutter/services.dart
testWidgets('renders a decoded thumbnail', (WidgetTester tester) async {
  late ui.Image image;
  await tester.runAsync(() async {
    final data = await rootBundle.load('test/fixtures/thumb.png');
    image = await decodeImageFromList(data.buffer.asUint8List());
  });

  await tester.pumpWidget(MaterialApp(home: RawImage(image: image)));
  expect(find.byType(RawImage), findsOneWidget);
});
```

If a test hangs and it uses `runAsync`, the cause is almost always a future created inside the fake zone that the real zone can never complete. Restructuring is the fix; more `runAsync` is not.

## Goldens break on other people's machines because of fonts and rasterization

A golden test is a screenshot committed to git. `matchesGoldenFile` renders the first `RepaintBoundary` ancestor of the matched widget and compares it byte-for-byte against the stored PNG; `flutter test --update-goldens` rewrites the PNGs. It is an asynchronous matcher, so it must be used with `await expectLater`.

The reason teams abandon goldens is almost always one of three things:

**Fonts.** By default `flutter test` renders text with a test font whose every glyph is a filled box — the framework docs still call it Ahem. That is deterministic, and also useless for reviewing a golden. So people load their real font, and then the app falls back to a *system* font for anything the loaded family does not cover — an emoji, a Vietnamese diacritic, a CJK character, a Material icon. System fonts differ between macOS, Linux and Windows, so the golden differs too.

**Rasterization.** Antialiasing of text and curves is not guaranteed to be identical across host platforms or across Flutter versions. A Flutter upgrade legitimately re-rasterizes your goldens. One source of nondeterminism the SDK removes for you: `flutter test` sets `debugDisableShadows = true`, so goldens have no shadows at all. That is also why a screenshot taken through `flutter drive` will never match a `flutter test` golden.

**Layout drift from the host.** Anything reading platform state — `Platform.isIOS`, locale, text scale — silently changes the picture.

The fix is a policy, not a package. Commit the font files, load them for every test, generate goldens on exactly one platform, and allow a small tolerance for the last mile. All of that belongs in `test/flutter_test_config.dart`, a file `flutter test` picks up automatically and applies to every test in that directory tree.

```dart
// test/flutter_test_config.dart
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  TestWidgetsFlutterBinding.ensureInitialized();
  await _loadAppFonts();

  final current = goldenFileComparator;
  if (current is LocalFileComparator) {
    goldenFileComparator = _TolerantComparator(
      Uri.parse('${current.basedir}test.dart'),
      // 0.5% of pixels may differ before the test fails.
      precisionTolerance: 0.005,
    );
  }

  await testMain();
}

Future<void> _loadAppFonts() async {
  const families = <String, List<String>>{
    'Inter': [
      'assets/fonts/Inter-Regular.ttf',
      'assets/fonts/Inter-SemiBold.ttf',
    ],
    // Register the fallback explicitly so nothing reaches for a system font.
    'NotoSans': ['assets/fonts/NotoSans-Regular.ttf'],
  };

  for (final entry in families.entries) {
    final loader = FontLoader(entry.key);
    for (final asset in entry.value) {
      loader.addFont(rootBundle.load(asset));
    }
    await loader.load();
  }
}

class _TolerantComparator extends LocalFileComparator {
  _TolerantComparator(super.testFile, {required this.precisionTolerance});

  final double precisionTolerance;

  @override
  Future<bool> compare(Uint8List imageBytes, Uri golden) async {
    final result = await GoldenFileComparator.compareLists(
      imageBytes,
      await getGoldenBytes(golden),
    );

    if (result.passed || result.diffPercent <= precisionTolerance) {
      result.dispose();
      return true;
    }

    final error = await generateFailureOutput(result, golden, basedir);
    result.dispose();
    throw FlutterError(error);
  }
}
```

Be honest about the tolerance: it is a blunt instrument. A 0.5% pixel budget hides a one-pixel border change as effectively as it hides an antialiasing difference. Use it to absorb rasterization noise, never as a substitute for pinning the platform.

The test itself stays small, and gets a tag so it can be run selectively:

```dart
// test/goldens/quote_card_golden_test.dart
@Tags(['golden'])
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shop/quote_card.dart';

void main() {
  testWidgets('QuoteCard with a discount', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: RepaintBoundary(
              child: QuoteCard(
                quote: Quote(discountCents: 1000, totalCents: 9500),
              ),
            ),
          ),
        ),
      ),
    );

    await expectLater(
      find.byType(QuoteCard),
      matchesGoldenFile('goldens/quote_card_discount.png'),
    );
  });
}
```

Declare the tag in `dart_test.yaml` so the runner does not warn about it:

```yaml
# dart_test.yaml
tags:
  golden:
```

Then goldens run in one place only. Developers run `flutter test --exclude-tags golden`; the Linux CI job — pinned to the same Flutter version that generated the files — runs `flutter test --tags golden`, and regenerates with `flutter test --tags golden --update-goldens` inside the same container image. If you want the ergonomics of device-size variants and a nicer diff report without building it yourself, `alchemist` on pub.dev wraps this pattern; the SDK alone is enough for most apps.

## integration_test: the three or four flows worth driving for real

`integration_test` ships with the SDK and reuses the `testWidgets` API, so the code looks familiar. What changes underneath is important: `IntegrationTestWidgetsFlutterBinding` extends the *live* binding, not the automated one. There is no fake clock. `pump()` waits real wall-clock time, real plugins answer real platform channels, and real network calls go out.

```yaml
# pubspec.yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  integration_test:
    sdk: flutter
```

```dart
// integration_test/checkout_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shop/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('a promo code applied on device reaches the total',
      (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('cart_tab')));
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('promo_field')), 'SPRING10');
    await tester.tap(find.widgetWithText(FilledButton, 'Apply'));

    // Real network, real time: poll for the result instead of guessing.
    await tester.pumpAndSettle(const Duration(milliseconds: 100));

    expect(find.textContaining(r'$95.00'), findsOneWidget);
  });
}
```

Run it with `flutter test integration_test/checkout_test.dart -d <device-id>`, or via `flutter drive` when you need Firebase Test Lab or a screenshot pipeline. Keep the list short. Every flow you add here is paid for on every pull request, and an integration test that fails intermittently teaches the team the same bad habit as a flaky widget test.

`IntegrationTestWidgetsFlutterBinding` also carries the performance hooks: `binding.traceAction(...)` records a timeline into `reportData`, and `binding.takeScreenshot('name')` captures the device screen (on Android you must call `binding.convertFlutterSurfaceToImage()` first). Those are the right tool for a scroll-jank budget; they are not a substitute for the widget layer.

## Where the flake actually comes from

Almost every flaky Flutter test I have looked at is one of these four.

**`pumpAndSettle` against something that never settles.** The documented behaviour is explicit: `pumpAndSettle` repeatedly pumps until no frames are scheduled, and if that takes longer than the timeout — ten minutes by default — it throws. An indeterminate `CircularProgressIndicator`, a shimmer placeholder, a looping Lottie, an `AnimationController.repeat()` — any of these makes it a ten-minute hang followed by a failure. The fix is to pump deliberately:

```dart
await tester.tap(find.byKey(const Key('submit')));
await tester.pump();                                  // loading state
await tester.pump(const Duration(milliseconds: 300)); // halfway through the transition
await tester.pump(const Duration(seconds: 1));        // past the end
```

`pumpAndSettle` also returns the number of pumps it performed, which makes `expect(await tester.pumpAndSettle(), 3)` a real assertion about animation length rather than a shrug.

**Timers that outlive the widget.** The automated binding asserts at the end of each test that nothing is pending, with the message *"A Timer is still pending even after the widget tree was disposed."* Its sibling is *"was disposed with an active Ticker"*, thrown when an `AnimationController` created with `SingleTickerProviderStateMixin` is never disposed. Both are real leaks in your app that only tests are strict enough to notice — cancel the `Timer` and dispose the controller in `dispose()`, and both go away.

**Network in tests.** The test binding installs an `HttpOverrides` whose client returns an empty response with status 400 for every request, precisely so that a test never depends on the network. That means `Image.network` renders an error, not your image, and any code path doing real HTTP takes its failure branch. Do not work around it with a live client — inject the client, or fake at the repository boundary as in the widget test above. If you must exercise a real image, pass the bytes in through `runAsync` and a fixture file.

**Unawaited futures.** `tester.tap` dispatches pointer events and does not pump. `tester.enterText` flushes microtasks but does not draw a frame. Code that fires a request without awaiting it leaves a completion callback sitting in the microtask queue, and if your next line is an `expect`, you are asserting against the frame before the one you meant. Two rules cover it: never write `unawaited(...)` in code a test drives without also giving the test a way to observe completion, and when an assertion is off by one state, add a `pump()` rather than reaching for `pumpAndSettle()`.

A fifth, less common source: tests that depend on execution order because they share a top-level variable or a singleton. `setUp` should construct everything the test touches; `addTearDown` should undo anything global.

## Wiring it up so CI stays green

```bash
# Everything except goldens — what developers run, on any OS.
flutter test --exclude-tags golden

# Goldens, on the pinned Linux image only.
flutter test --tags golden

# Regenerate goldens (same image, same Flutter version, or don't bother).
flutter test --tags golden --update-goldens

# Integration tests, against a booted device or emulator.
flutter test integration_test -d emulator-5554
```

Two rules make the difference between a suite people trust and one they mute. First, a flaky test gets deleted or fixed the day it flakes — never retried, because a retry annotation converts a real race in your app into invisible latency. Second, pin the Flutter version everywhere goldens are produced or verified; an SDK bump that changes rasterization should show up as one deliberate commit regenerating the PNGs, not as noise on an unrelated pull request.

For mocks, `mocktail` needs no code generation and reads well with closures; `mockito` needs `build_runner` and `@GenerateNiceMocks`, but its generated mocks are analyzer-visible, which some teams prefer. Either is fine. What is not fine is mocking your own widgets — if you find yourself doing that, the widget is doing too much, and the fix belongs in `lib/`, not in `test/`.

## FAQ

**Should I just use `pumpAndSettle` everywhere?**
No, and the API docs say so directly: it is better practice to work out exactly why each frame is needed and pump exactly that many. `pumpAndSettle` hides regressions where an animation starts a frame later than it should, and it turns any infinite animation into a ten-minute timeout. Use it at the top of an integration test, where real time is unavoidable, and use explicit pumps in widget tests.

**Why does my widget test sometimes need two pumps after a future completes?**
Because `pump` flushes microtasks but only draws a frame if one has been scheduled. On an idle tree the first pump runs your `.then`/`setState` — and that call is what schedules the frame — so the second pump is the one that draws it. If something is already animating on screen, a frame is always pending and one pump does both. Don't memorise a number; when an assertion is one state behind, add a pump.

**Can I run golden tests on macOS and Linux and expect the same bytes?**
Not reliably. Text antialiasing and font fallback differ by host, so the practical answer is to nominate one platform — usually a pinned Linux container, since that is also what most CI runs — generate there, verify there, and skip goldens elsewhere with a tag. A tolerance in a custom `LocalFileComparator` absorbs the remaining noise; it does not replace pinning.

**mocktail or mockito?**
`mocktail` if you want zero code generation and don't need null-safety-driven stubs to be checked by the analyzer. `mockito` if your team already runs `build_runner` and wants generated, statically typed mocks. Both are actively maintained on pub.dev; the choice rarely matters as much as where you draw the seam you are mocking.

**How many integration tests should an app have?**
Few enough that you can list them from memory. They exist to prove that plugins, platform channels and app startup work on a real device — things widget tests structurally cannot see. Everything else is faster, more precise and less flaky one layer down.

---

*The API behaviour described here — pump semantics, the 400-response HTTP override, disabled shadows in `flutter test`, the `pumpAndSettle` timeout — comes from the `flutter_test` documentation and source. The policy recommendations (one golden platform, delete flaky tests, keep integration tests few) are my opinion, formed from maintaining suites rather than from a study. Anything version-dependent should be checked against the docs for the Flutter version you are actually on.*
