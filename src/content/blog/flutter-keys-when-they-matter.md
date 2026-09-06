---
title: "Keys in Flutter: the one rule that explains every case"
description: "Keys are not an optimisation and they are not decoration. They exist because element reuse is decided by position and runtime type — and that decision is wrong exactly when your children can be reordered, inserted or removed."
seoDescription: "When to use ValueKey, ObjectKey, UniqueKey and GlobalKey in Flutter, why widget state jumps to the wrong row without them, and why PageStorageKey is a different thing."
keywords:
  - flutter keys explained
  - when to use valuekey flutter
  - flutter globalkey vs valuekey
  - flutter state jumps to wrong list item
  - pagestoragekey flutter
  - widget canupdate flutter
category: "Deep Dive"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-06"
emoji: "🔑"
tags: ["Flutter", "Widgets", "State", "Elements", "Debugging"]
sources:
  - name: "Flutter — Architectural overview"
    url: "https://docs.flutter.dev/resources/architectural-overview"
  - name: "Key — Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/Key-class.html"
  - name: "GlobalKey — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/GlobalKey-class.html"
  - name: "Widget.canUpdate — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Widget/canUpdate.html"
  - name: "PageStorageKey — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/PageStorageKey-class.html"
  - name: "Flutter — When to use keys (Widget of the Week)"
    url: "https://www.youtube.com/watch?v=kn0EOS-ZiIc"
related:
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
  - slug: "flutter-lists-performance-builder"
    title: "Why your ListView is slow, and the four fixes that actually work"
draft: false
---

There is a specific bug that teaches everyone about keys. You have a list of stateful rows — each with a checkbox, or an expansion tile, or a text field. You delete the second row. The row disappears correctly, but the *checkmark* that belonged to it is now sitting on a different row. Nothing about your data is wrong. Reload the page and everything is fine.

That bug is not a Flutter defect. It is the framework doing exactly what it was told, and the fix is one word long. But the fix only sticks if you understand the rule underneath it, because the same rule explains why keys sometimes do nothing at all, why `GlobalKey` is expensive, and why a `PageStorageKey` is not really a key in the same sense.

## Three trees, and the one that holds your state

Flutter maintains three parallel structures. The **widget tree** is your `build` output: immutable configuration objects, thrown away and recreated constantly. The **render tree** does layout and painting. Between them sits the **element tree**, and that is the one that matters here, because an `Element` is long-lived and — for a `StatefulWidget` — it is what owns the `State` object.

When a rebuild happens, Flutter walks the old element tree alongside the new widget tree and, for each position, asks one question:

```dart
static bool canUpdate(Widget oldWidget, Widget newWidget) {
  return oldWidget.runtimeType == newWidget.runtimeType
      && oldWidget.key == newWidget.key;
}
```

That is the whole mechanism. If the answer is yes, the existing element (and its `State`, and its render object) is **kept** and handed the new widget. If the answer is no, the old element is deactivated and a fresh one is inflated.

Notice what the comparison does *not* include: any of your data. Two `TodoRow` widgets with completely different todos are interchangeable as far as `canUpdate` is concerned, provided both have `key == null`. And notice that the comparison is made **per position in the child list**. Child zero is compared to child zero.

Which gives the rule, and it is the only rule:

> Flutter matches children by position and type. A key overrides "by position" with "by identity."

Everything else is a consequence.

## Why the bug happens, in slow motion

```dart
Column(
  children: [
    for (final todo in todos) TodoRow(todo: todo),   // no keys
  ],
)
```

Before deletion the element tree is `[TodoRow#0, TodoRow#1, TodoRow#2]`, holding state `[unchecked, checked, unchecked]`. You remove `todos[1]` and rebuild. The new widget list has two entries. Flutter compares position 0 to position 0 — same type, both keys null, `canUpdate` is true, keep element #0 and give it `todos[0]`. Position 1 to position 1 — same type, keys null, true — so element #1, which is holding **the checked state that belonged to the deleted row**, is kept and handed `todos[2]`. Element #2 is disposed.

Result: the right rows render with the right text, because text comes from the widget. The wrong rows carry the state, because state comes from the element. Add a key and position stops being the matcher:

```dart
Column(
  children: [
    for (final todo in todos) TodoRow(key: ValueKey(todo.id), todo: todo),
  ],
)
```

Now `canUpdate` compares `ValueKey('b')` to `ValueKey('c')` at position 1 and says no. Flutter then searches the old children for an element with a matching key, finds element #2, and moves it. State follows identity.

## When you need a key, and when you do not

Skip the key when:

- The children are **stateless all the way down**. No `State`, no `AnimationController`, no scroll position, nothing to move to the wrong place. A list of `Text` widgets never needs keys.
- The list never reorders, and items are only ever appended at the end. Position-matching is correct in that case.
- You are keying the *outside* of a `ListView.builder`. Its children already get implicit keys from their index for the purposes of the sliver child delegate; what you need is a key on the item widget, not on the list.

Use a key when **any** of these is true:

- Children are stateful **and** the collection can be reordered, filtered, or have items removed from anywhere but the end.
- You are swapping between two widgets of the same type and want a fresh `State` — a `UniqueKey` forces the old element to be discarded.
- You are animating items in and out with `AnimatedList`, `AnimatedSwitcher` or an implicit animation that needs to tell "the same widget, changed" apart from "a different widget."

The `AnimatedSwitcher` case catches people:

```dart
AnimatedSwitcher(
  duration: const Duration(milliseconds: 300),
  child: Text('$counter', key: ValueKey(counter)),   // without the key: no animation
)
```

Both children are `Text`. Without a key, `canUpdate` is true, the element is reused, and `AnimatedSwitcher` concludes nothing changed. The key is what makes the change visible to the framework.

## Choosing between the key types

| Type | Equality based on | Reach for it when |
| --- | --- | --- |
| `ValueKey<T>` | A value you supply (`==`) | You have a stable id: `ValueKey(todo.id)` |
| `ObjectKey` | Object **identity** of what you pass | The model has no id but instances are stable |
| `UniqueKey` | Nothing — never equal to anything | You want to force a rebuild-from-scratch |
| `GlobalKey` | Identity, but globally unique in the whole app | You must reach an element or state from outside |
| `PageStorageKey` | A value, but used for scroll-position storage | Preserving scroll offset across navigation |

Two traps in that table.

**`ValueKey` on the wrong value.** `ValueKey(index)` is the most common mistake, because the index is exactly the positional information you were trying to escape. Delete an item and every subsequent index shifts, so the keys shift with it and you are back to matching by position. Key on something intrinsic to the item — a database id, a UUID, a filename.

**`UniqueKey` in a `build` method.** A `UniqueKey` created during `build` is different on every rebuild, so `canUpdate` is always false, so the element and all its state and its subtree are destroyed and rebuilt every single frame. This produces a widget that visibly resets, animations that never finish, and a real performance cost. `UniqueKey` belongs in a field, or in a deliberate "reset this form" action.

## `GlobalKey` costs more than it looks

A `GlobalKey` gives you `key.currentState`, `key.currentContext` and `key.currentWidget` from anywhere. The standard use is a `Form`:

```dart
final _formKey = GlobalKey<FormState>();          // a field, not a local

// ...
if (_formKey.currentState!.validate()) {
  _formKey.currentState!.save();
}
```

That is legitimate. What is not free:

- The framework maintains a **global registry** from key to element, checked and updated on every mount and unmount.
- Moving a widget with a `GlobalKey` to a new position triggers a full deactivate/reactivate cycle for that subtree — a *global* tree search rather than a local sibling comparison.
- Two widgets with the same `GlobalKey` mounted at once is an error, and it happens easily when a `GlobalKey` is created inside `build` and the widget appears twice.

Before reaching for one, check whether you actually needed to reach *into* a subtree, or whether the state belongs one level up. Most `GlobalKey` usage that is not a `Form` or a `Scaffold`/`Navigator` handle is a state-placement problem in disguise — lift the state, or pass a callback down.

## `PageStorageKey` is a different animal

```dart
ListView(
  key: const PageStorageKey<String>('feed'),
  children: [ /* ... */ ],
)
```

This is a `Key`, so it participates in `canUpdate`, but its real job is to name a slot in `PageStorage` where the scroll offset is written. That is what makes a tab's scroll position survive switching away and back, or a list restore its offset after a `Navigator.push` and `pop`.

Two things follow. The string must be **stable across rebuilds** and **unique among sibling scrollables** — two tabs sharing `'feed'` will share a scroll offset, which looks like a haunting. And a `PageStorageKey` only works where a `PageStorage` exists above it, which `MaterialApp` and `Navigator` provide by default.

## Debugging: how to tell it is a key problem

The symptom pattern is specific enough to diagnose from behaviour alone. Suspect keys when **the data is right and something attached to the data is wrong**: text correct, checkbox wrong; the right item removed but the wrong row animating out; a text field keeping its content after you switched which record is being edited; a video keeping playing after you swapped the item.

Confirm it in one minute:

```dart
@override
void initState() {
  super.initState();
  debugPrint('initState for ${widget.todo.id} on $hashCode');
}

@override
void didUpdateWidget(TodoRow old) {
  super.didUpdateWidget(old);
  debugPrint('${old.todo.id} -> ${widget.todo.id} on $hashCode');
}
```

If you see `didUpdateWidget` reporting a change of id on the same `hashCode`, an element is being recycled across two different logical items. That is the bug, and a proper `ValueKey` is the fix. The Flutter Inspector shows the same thing visually — select a row before and after the mutation and watch whether the element identity moves.

## FAQ

**Where do I put the key — on the item, or on something inside it?**

On the **outermost** widget returned for that item, at the level where siblings are compared. A key on a child inside the row does not help, because the mismatch already happened one level up.

**Does adding keys everywhere hurt performance?**

`ValueKey` and `ObjectKey` are cheap: one extra `==` during reconciliation. Keys on a large list can actually be *faster* on reorder, since elements move instead of rebuilding. `GlobalKey` is the one with real overhead.

**Why did adding a key not fix my problem?**

Usually the key value is not stable — `ValueKey(index)`, `ValueKey(DateTime.now())`, or a key built from a field that changes when the item is edited. Print the keys across the mutation and check they identify the same logical item before and after.

**Are keys needed inside `ListView.builder`?**

Yes, for the same reasons, if the items are stateful and the collection mutates. The builder's index is positional; it does not give your item widget an identity.

**What is `Key` versus `LocalKey`?**

`Key` is the base type. `LocalKey` is the branch that only has to be unique among siblings — `ValueKey`, `ObjectKey`, `UniqueKey`, `PageStorageKey` all extend it. `GlobalKey` is the other branch, unique across the entire app.

---

*The reconciliation behaviour described here is `Widget.canUpdate` and the element update logic in the Flutter framework, linked above. The guidance on when a `GlobalKey` signals misplaced state, and the debugging recipe, are my own. Check the API docs for the SDK you ship — key types are stable, but the widgets around them are not.*
