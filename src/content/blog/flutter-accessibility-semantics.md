---
title: "Flutter accessibility: what the semantics tree actually reports"
description: "Flutter draws pixels, so screen readers cannot inspect your widgets. They read a separate semantics tree that Flutter builds and sends to the platform. Knowing what lands in that tree — and what silently does not — is the whole job."
seoDescription: "How Flutter accessibility works: the semantics tree, Semantics and MergeSemantics, ExcludeSemantics, live regions, tap targets, text scale, and testing with SemanticsTester and the accessibility guidelines."
keywords:
  - flutter accessibility semantics
  - flutter screen reader talkback voiceover
  - flutter semantics widget usage
  - flutter mergesemantics excludesemantics
  - flutter accessibility testing meetsguideline
  - flutter tap target size accessibility
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-03"
emoji: "♿"
tags: ["Flutter", "Accessibility", "Semantics", "Testing", "UI"]
sources:
  - name: "Flutter — Accessibility"
    url: "https://docs.flutter.dev/ui/accessibility-and-internationalization/accessibility"
  - name: "Semantics — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Semantics-class.html"
  - name: "SemanticsProperties — Flutter API"
    url: "https://api.flutter.dev/flutter/semantics/SemanticsProperties-class.html"
  - name: "MergeSemantics — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/MergeSemantics-class.html"
  - name: "meetsGuideline — Flutter API"
    url: "https://api.flutter.dev/flutter/flutter_test/meetsGuideline.html"
  - name: "SemanticsService — Flutter API"
    url: "https://api.flutter.dev/flutter/semantics/SemanticsService-class.html"
related:
  - slug: "flutter-theming-material3-design-tokens"
    title: "Material 3 theming in Flutter: colour roles, not colour values"
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
draft: false
---

Turn on TalkBack or VoiceOver in a Flutter app that nobody has thought about, and the experience is usually one of three failures: the screen reader announces "button" with no label, it reads a decorative icon and its text as two separate stops, or it silently skips something the user needs. None of these are visible in a screenshot, which is why they survive so long.

The reason they happen is structural. A native Android or iOS app gives the accessibility service a tree of real platform views to inspect. Flutter gives it a canvas. What the screen reader actually reads is the **semantics tree** — a second tree, built alongside the render tree, that Flutter serialises and hands to the platform. If a piece of information is not in that tree, it does not exist as far as assistive technology is concerned.

## What the framework gives you for free

The good news first: most Material and Cupertino widgets already contribute semantics.

| Widget | What it contributes |
| --- | --- |
| `Text` | The string, as a label |
| `ElevatedButton`, `IconButton`, `TextButton` | `isButton`, the child's label, an `onTap` action |
| `TextField` | `isTextField`, `label`, `hint`, `value`, editing actions |
| `Checkbox`, `Switch`, `Radio` | Checked state, toggle action |
| `Image` | Only its `semanticLabel`, if you set one |
| `Icon` | Only its `semanticLabel`, if you set one |
| `Container`, `Padding`, `Row`, `SizedBox` | Nothing — they are invisible to semantics |

The last three rows are where most bugs come from. An `IconButton` whose child is a bare `Icon` and which has no `tooltip` produces a node with the button flag and **no label at all**. The screen reader says "button". That is a real, common, shipping bug, and it is a single missing string.

```dart
// Announces "button" — useless.
IconButton(icon: const Icon(Icons.delete), onPressed: _delete)

// Announces "Delete, button" — and shows a tooltip on long press.
IconButton(
  icon: const Icon(Icons.delete),
  tooltip: 'Delete',
  onPressed: _delete,
)
```

`tooltip` is the idiomatic fix for `IconButton` because it solves both the accessibility problem and the discoverability problem in one property.

## The four verbs of the `Semantics` widget

When the defaults are not enough, `Semantics` and its siblings do four distinct things. Choosing the wrong one is how people end up with a tree that reads worse than the default.

**Annotate.** `Semantics(label: ...)` adds meaning to a subtree that has none:

```dart
Semantics(
  label: 'Battery, 82 percent',
  excludeSemantics: true, // the painted gauge has nothing useful to say
  child: CustomPaint(painter: BatteryGaugePainter(level: 0.82)),
)
```

**Merge.** `MergeSemantics` collapses a subtree into one node, so a screen reader stops on it once instead of three times:

```dart
MergeSemantics(
  child: Row(
    children: [
      const Icon(Icons.schedule),
      const SizedBox(width: 8),
      Text('Arrives $eta'),
    ],
  ),
)
```

`ListTile` already does this internally, which is why a well-built tile reads as a single sentence. Hand-rolled rows do not, and that is the second most common complaint from screen-reader users.

**Exclude.** `ExcludeSemantics` removes a subtree entirely. Decorative images, background gradients, a shimmering placeholder — none of them should be stops in the reading order.

```dart
ExcludeSemantics(child: Image.asset('assets/hero_swirl.png'))
```

**Block.** `BlockSemantics` hides everything painted *behind* it in the same subtree. This is what makes a modal actually modal for a screen reader: without it, the user can swipe past the dialog into the page underneath, which is disorienting because the page is visually dimmed and untappable. `showDialog` handles this for you; a hand-built overlay does not.

## Values, hints, and the difference between them

`SemanticsProperties` distinguishes several strings that people tend to cram into `label`:

- **`label`** — what the thing *is*. "Volume".
- **`value`** — its current state. "60 percent".
- **`increasedValue` / `decreasedValue`** — what the value becomes after an adjust action, so the reader can announce the result of a swipe.
- **`hint`** — what happens if you act on it. "Double tap to mute". Prefer to leave this empty when the action is obvious; verbose hints are a common accessibility complaint in their own right.

A slider done properly:

```dart
Semantics(
  label: 'Volume',
  value: '${(volume * 100).round()} percent',
  increasedValue: '${((volume + 0.05) * 100).round()} percent',
  decreasedValue: '${((volume - 0.05) * 100).round()} percent',
  slider: true,
  onIncrease: () => _setVolume(volume + 0.05),
  onDecrease: () => _setVolume(volume - 0.05),
  child: ExcludeSemantics(child: _CustomVolumeBar(volume: volume)),
)
```

Material's own `Slider` does all of this. The example matters when you build a custom control — and building a custom control is exactly when accessibility gets dropped.

## Announcing things that change without a tap

Content that updates on its own — a form error, a "saved" confirmation, a countdown — is invisible to a screen reader unless you say so. Two mechanisms:

```dart
// Re-announce this node when its label changes.
Semantics(liveRegion: true, child: Text(errorMessage))

// Or announce a one-off event with no widget attached.
SemanticsService.announce('Message sent', TextDirection.ltr);
```

Use `liveRegion` for something that is on screen and changes; use `announce` for transient events. Both are easy to overuse — a live region that updates every frame will talk over everything else the user is trying to hear.

## Two rules that are not about the tree at all

**Tap targets.** Anything interactive needs to be at least 48×48 logical pixels on Android and 44×44 on iOS. A 24-pixel icon inside a `GestureDetector` fails this, and no semantics annotation fixes it. `IconButton` gets it right by default; `InkWell` around a small icon does not, unless you give it a size.

**Text scale.** Users can set text well above 100%. Flutter honours it automatically, which means layouts break rather than silently ignore the setting. That is the correct trade-off, but it means you have to test at high scale:

```dart
MediaQuery(
  data: MediaQuery.of(context).copyWith(
    textScaler: const TextScaler.linear(2.0),
  ),
  child: const MyScreen(),
)
```

If the answer to overflow is `textScaleFactor: 1.0`, the layout has been fixed by breaking the feature. Use `Flexible`, allow wrapping, and let vertical space grow.

## Testing it, so it does not regress

Flutter ships accessibility guidelines you can assert against in a widget test. This is the part almost nobody enables, and it catches the two mechanical failures above automatically:

```dart
testWidgets('home screen meets accessibility guidelines', (tester) async {
  final handle = tester.ensureSemantics();
  await tester.pumpWidget(const MyApp());

  await expectLater(tester, meetsGuideline(textContrastGuideline));
  await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  await expectLater(tester, meetsGuideline(iOSTapTargetGuideline));
  await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));

  handle.dispose();
});
```

`labeledTapTargetGuideline` is the one that catches the unlabelled `IconButton`. `ensureSemantics()` matters — without it the semantics tree is not built during the test, and the assertions have nothing to inspect.

For a specific node, assert on its properties directly:

```dart
expect(
  tester.getSemantics(find.byIcon(Icons.delete)),
  matchesSemantics(label: 'Delete', isButton: true, hasTapAction: true),
);
```

And when something reads wrongly on device, turn on the visual debugger to see the tree the platform is actually receiving:

```dart
MaterialApp(showSemanticsDebugger: true, home: const HomePage())
```

It overlays the semantics nodes on the UI. Nodes you expected to be separate but see merged — or the reverse — explain most confusing announcements immediately.

## FAQ

**Do I need to annotate every widget?**

No, and doing so makes things worse. Most of the tree should be silent structure. Annotate interactive controls, custom painters, and images that carry meaning; exclude decoration; merge rows that are logically one item.

**Why does my custom widget read as nothing?**

Because `Container`, `CustomPaint` and friends contribute no semantics on their own. Wrap it in `Semantics` with a `label`, and set `excludeSemantics: true` if the child produces noise.

**Is the semantics tree built when no screen reader is running?**

The framework builds and maintains it when an accessibility service requests it, or when a test calls `ensureSemantics()`. That is why it is not a constant cost in a normal session, and why tests need the handle.

**Does `Tooltip` help accessibility?**

Yes — a `Tooltip` contributes its message to the semantics node, which is why `IconButton(tooltip: ...)` is the recommended fix rather than wrapping in `Semantics`.

**What about `Semantics` inside a list?**

Each item should generally be one merged node. If a list item reads as five separate stops, wrap the item in `MergeSemantics`; if the whole list reads as one, you have merged too high up.

---

*The widget behaviours, guideline constants and `SemanticsService` API described here are from the Flutter accessibility documentation and API references linked above. The ordering advice, the view that verbose hints are their own accessibility problem, and the position that `textScaleFactor: 1.0` is a bug rather than a fix are my own judgement. Verify against the SDK version you ship — `textScaler` replaced `textScaleFactor` in a recent release, and the deprecated form may or may not still exist in yours.*
