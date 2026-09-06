---
title: "BuildContext is an element: reading the error messages that mention it"
description: "\"No Scaffold widget found\", \"called before initState\", \"do not use BuildContext across async gaps\" — three famous errors with one root cause. BuildContext is a handle on your position in the element tree, and every rule about it follows from that."
seoDescription: "What BuildContext actually is in Flutter, why Scaffold.of fails in the same build method, how dependOnInheritedWidgetOfExactType works, and how to handle context after an await."
keywords:
  - flutter buildcontext explained
  - no scaffold widget found error flutter
  - use_build_context_synchronously
  - dependoninheritedwidgetofexacttype
  - flutter builder widget why
  - context mounted flutter
category: "Deep Dive"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-05"
emoji: "🧭"
tags: ["Flutter", "Widgets", "Elements", "InheritedWidget", "Debugging"]
sources:
  - name: "BuildContext — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/BuildContext-class.html"
  - name: "Element — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Element-class.html"
  - name: "InheritedWidget — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/InheritedWidget-class.html"
  - name: "Builder — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Builder-class.html"
  - name: "Dart lint — use_build_context_synchronously"
    url: "https://dart.dev/tools/linter-rules/use_build_context_synchronously"
  - name: "Flutter — Architectural overview"
    url: "https://docs.flutter.dev/resources/architectural-overview"
related:
  - slug: "flutter-keys-when-they-matter"
    title: "Keys in Flutter: the one rule that explains every case"
  - slug: "flutter-state-management-decision-guide"
    title: "Riverpod, Bloc, signals or setState: choosing Flutter state management and living with it"
draft: false
---

`BuildContext` is the parameter everyone types a thousand times without ever asking what it is. It shows up in every `build` method, it is required by `Theme.of`, `Navigator.of`, `showDialog`, `MediaQuery.sizeOf` — and then one day it produces an error that makes no sense, like `Scaffold.of()` failing inside a widget that is very obviously wrapped in a `Scaffold`.

The declaration answers the whole thing. In the framework source, `abstract class Element extends DiagnosticableTree implements BuildContext`. A `BuildContext` **is** an `Element`, exposed through a narrow interface so you cannot mutate the tree with it. When a `build` method receives a context, it is being handed *its own element* — its exact position in the live tree.

Everything confusing about `BuildContext` becomes obvious once you read it as "my node in the tree" rather than "the app."

## Lookups walk upward from your node

`Theme.of(context)`, `MediaQuery.of(context)`, `Navigator.of(context)` and friends all do the same thing: start at that element and walk **up** the ancestor chain until they find what they are looking for. They never look down, and they never look sideways.

Which explains the classic failure:

```dart
class MyPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ElevatedButton(
          onPressed: () {
            // Throws: no Scaffold above THIS context.
            Scaffold.of(context).openDrawer();
          },
          child: const Text('Open'),
        ),
      ),
    );
  }
}
```

The `context` in that closure is `MyPage`'s context. The `Scaffold` is created *below* it, as part of what `MyPage` returns. Walking up from `MyPage` finds whatever wraps the page — never the `Scaffold` inside it.

The framework's own error message says this clearly if you read it as written: it complains that the context used was one "that does not include the Scaffold." The fix is to look up from a node that is genuinely underneath:

```dart
Builder(
  builder: (innerContext) => ElevatedButton(
    onPressed: () => Scaffold.of(innerContext).openDrawer(),
    child: const Text('Open'),
  ),
)
```

`Builder` is a widget whose entire purpose is to create one extra element so you get a context one level deeper. It has no visual effect at all. It exists solely to move you down the tree.

Two alternatives worth knowing. Splitting the subtree into its own widget gives the same new context and is usually cleaner. And for `Scaffold` specifically, `ScaffoldMessenger.of(context)` — the modern way to show a `SnackBar` — is deliberately looked up from *above* the `Scaffold`, so page-level contexts work fine.

## `.of()` versus `.maybeOf()` versus `.sizeOf()`

The naming convention across the framework is consistent, and each variant means something different at runtime:

| Call | Returns | When it is missing | Subscribes to changes |
| --- | --- | --- | --- |
| `X.of(context)` | The value | Throws with a long diagnostic | Yes |
| `X.maybeOf(context)` | `X?` | Returns `null` | Yes |
| `MediaQuery.sizeOf(context)` | Just the size | Throws | Only to **size** changes |

That last row is a real performance tool. `MediaQuery.of(context)` makes your widget rebuild when *anything* in the `MediaQueryData` changes — text scale, padding, view insets, brightness, and notably the keyboard sliding in and out. If all you wanted was the width, `MediaQuery.sizeOf(context)` rebuilds only when the size changes. The same pattern exists for `textScalerOf`, `paddingOf`, `viewInsetsOf`, `platformBrightnessOf` and others, and swapping to the specific one is a free win in any widget that sits above a keyboard.

## What "depending on" an inherited widget means

The subscription in that table is not a metaphor. `Theme.of(context)` is implemented roughly as:

```dart
static ThemeData of(BuildContext context) {
  final inherited = context.dependOnInheritedWidgetOfExactType<_InheritedTheme>();
  // ...
}
```

`dependOnInheritedWidgetOfExactType` does two things: it finds the nearest ancestor of that type, **and it registers your element as a dependent**. When that inherited widget is later rebuilt with data for which `updateShouldNotify` returns true, every registered dependent is marked dirty. That is the whole of Flutter's built-in reactive propagation — `InheritedWidget` plus a dependency registry keyed by element.

Which is why this throws:

```dart
@override
void initState() {
  super.initState();
  final theme = Theme.of(context);   // error: called before initState completed
}
```

Registering a dependency requires the element to be fully mounted and able to be marked dirty; during `initState` it is not yet. The right places are `didChangeDependencies` (called immediately after `initState`, and again whenever a dependency changes) or `build`.

There is a non-subscribing sibling for the rare cases where you want a one-shot read that will not cause rebuilds: `getInheritedWidgetOfExactType`. Use it deliberately, and know that you will not be notified when the value changes.

## Context after an `await` is the dangerous one

This is the rule that survives contact with production code, and the lint that enforces it — `use_build_context_synchronously` — is on by default in `flutter_lints`.

```dart
Future<void> _save() async {
  await repository.save(draft);
  Navigator.of(context).pop();          // unsafe
}
```

Between the `await` and the next line, anything can happen: the user pressed back, a parent rebuilt this subtree away, the route was popped by a deep link. If the element was unmounted, its ancestor chain is gone and looking anything up from it is undefined at best.

The fix is to check, and the check has to come **after** the await, in the same synchronous block as the use:

```dart
Future<void> _save() async {
  await repository.save(draft);
  if (!context.mounted) return;
  Navigator.of(context).pop();
}
```

`context.mounted` was added precisely for this and works for a plain `BuildContext`, including inside a `StatelessWidget`'s callbacks. Inside a `State`, `mounted` on the state object means the same thing.

The better structural answer, where you can take it, is to capture what you need **before** the await:

```dart
Future<void> _save() async {
  final navigator = Navigator.of(context);
  final messenger = ScaffoldMessenger.of(context);

  await repository.save(draft);

  navigator.pop();
  messenger.showSnackBar(const SnackBar(content: Text('Saved')));
}
```

`NavigatorState` and `ScaffoldMessengerState` outlive the widget that looked them up, so this is safe even if the calling widget is gone — and it removes the whole class of "is my context still valid" reasoning from the code.

## Dialogs, and the context you must not reuse

`showDialog` hands the builder a **different** context, belonging to the dialog's own route. Mixing the two up produces the most common dialog bug in Flutter:

```dart
showDialog(
  context: context,
  builder: (dialogContext) => AlertDialog(
    actions: [
      TextButton(
        // Wrong: pops the page, not the dialog — or pops both.
        onPressed: () => Navigator.of(context).pop(),
        child: const Text('OK'),
      ),
    ],
  ),
);
```

Use `dialogContext` to close the dialog and the outer `context` for anything that belongs to the page. If the dialog needs to trigger navigation after closing, close it first, then act on the outer context — guarded by `context.mounted`, since `showDialog` is itself awaited.

## Reading the error messages

Once the model is in place, the three big ones decode instantly:

- **"No Scaffold widget found. `X` widgets require a Scaffold widget ancestor."** You looked up from a context at or above where the `Scaffold` was created. Add a `Builder`, or extract a child widget.
- **"No MaterialLocalizations found."** Almost always a `showDialog` or `Navigator` call from a context above `MaterialApp` — typically in the `builder:` of `MaterialApp` itself, or in a widget that *is* the app root. Move the call below `MaterialApp`.
- **"`dependOnInheritedWidgetOfExactType` was called before `initState` completed."** An `.of()` call in `initState` or in a field initialiser. Move it to `didChangeDependencies` or `build`.
- **"Looking up a deactivated widget's ancestor is unsafe."** A context used after its element was removed — the async-gap case, or a callback held past disposal. Guard with `context.mounted`, or capture the state object earlier.

## FAQ

**Can I store a `BuildContext` in a field and use it later?**

Technically yes, practically no. The moment the element is unmounted the stored context is a liability, and nothing warns you. Capture the specific state object you need (`NavigatorState`, `ScaffoldMessengerState`) instead.

**Is `context` the same object across rebuilds?**

For the same widget in the same position, yes — the element persists while `Widget.canUpdate` keeps returning true. That is exactly the identity that keys control.

**Why does `Builder` exist if it renders nothing?**

To create an element, and therefore a context, one level below the current one. That is its entire job: giving `.of()` lookups a lower starting point without extracting a new widget class.

**Is `context.mounted` enough, or do I need `State.mounted`?**

Inside a `State`, either works; they check the same underlying element. `context.mounted` is the one available in a `StatelessWidget` callback, so it is the more generally applicable habit.

**Does `MediaQuery.of` really cause that many rebuilds?**

On a page with a text field, yes — every keyboard animation frame changes `viewInsets`, and every dependent rebuilds. Switching to `MediaQuery.sizeOf` or `paddingOf` where that is all you need is one of the cheapest performance fixes available.

---

*The mechanics described here — the `Element implements BuildContext` relationship, the dependency registration in `dependOnInheritedWidgetOfExactType`, and the lint behaviour — are from the Flutter framework and Dart linter documentation linked above. Which patterns are worth adopting is my own judgement.*
