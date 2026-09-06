---
title: "Records and patterns in Dart: what they replace"
description: "Records give you multiple return values without a class. Patterns give you destructuring and exhaustive switches. Together they delete a category of boilerplate — and introduce a few habits worth forming early."
seoDescription: "Dart records and pattern matching explained: positional and named fields, destructuring, switch expressions, exhaustiveness with sealed classes, guards, and when a record is the wrong choice."
keywords:
  - dart records tutorial
  - dart pattern matching switch
  - dart destructuring
  - dart sealed class exhaustive
  - dart switch expression
  - dart multiple return values
category: "Deep Dive"
topic: "Dart"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-15"
emoji: "🎯"
tags: ["Dart", "Language", "Patterns", "Records", "Types"]
sources:
  - name: "Records — Dart documentation"
    url: "https://dart.dev/language/records"
  - name: "Patterns — Dart documentation"
    url: "https://dart.dev/language/patterns"
  - name: "Pattern types — Dart documentation"
    url: "https://dart.dev/language/pattern-types"
  - name: "Branches — Dart documentation"
    url: "https://dart.dev/language/branches"
  - name: "Class modifiers — Dart documentation"
    url: "https://dart.dev/language/class-modifiers"
  - name: "Destructuring — Dart language tour"
    url: "https://dart.dev/language/patterns#destructuring"
related:
  - slug: "dart-extension-types-zero-cost"
    title: "Extension types in Dart: a new name for an old value"
  - slug: "flutter-state-management-decision-guide"
    title: "Choosing Flutter state management without the holy war"
draft: false
---

Before records, returning two values from a function meant one of three unappealing options: a class you use once, a `List<Object>` you index into, or two out-parameters via a wrapper. Records make it one line.

```dart
({int width, int height}) measure(String text) {
  // ...
  return (width: 120, height: 40);
}

final size = measure('hello');
print(size.width);
```

That is the headline feature, and it is the smallest part of what records and patterns changed.

## Records: structural, not nominal

A record's type is its shape. `(int, String)` and `(int, String)` are the same type regardless of where they were created, which is what distinguishes a record from a class.

```dart
// Positional
(String, int) parseEntry(String line) {
  final parts = line.split(':');
  return (parts[0], int.parse(parts[1]));
}

// Named — clearer at the call site
({String name, int score}) parseNamed(String line) {
  final parts = line.split(':');
  return (name: parts[0], score: int.parse(parts[1]));
}

// Mixed
(String, {bool valid}) check(String input) => (input.trim(), valid: true);
```

Records are **immutable and have structural equality**, which is more useful than it first appears:

```dart
final a = (1, 'x');
final b = (1, 'x');
print(a == b); // true — no operator== to write
```

That makes them excellent as composite map keys:

```dart
final cache = <(int, int), Tile>{};
cache[(3, 7)] = tile;
```

Before records this required a key class with `==` and `hashCode`, or a string like `'3,7'`. Both work; neither is as good.

## Patterns: destructuring

A pattern on the left of `=` takes a value apart:

```dart
final (name, score) = parseEntry(line);
final (:width, :height) = measure(text);   // named shorthand

// In a for loop over a map
for (final MapEntry(key: id, value: user) in users.entries) {
  print('$id → ${user.name}');
}
```

The `:width` shorthand binds a variable of the same name as the field, which is the form you will use most.

Patterns also work in `if-case`, which is the cleanest way to combine a type test with destructuring:

```dart
if (response case {'data': {'items': List<Map<String, Object?>> items}}) {
  return items.map(Item.fromJson).toList();
}
```

That single line checks that `response` is a map, that it has a `data` key holding a map, that the map has an `items` key, and that its value is a list of maps — binding `items` only if all of it holds. The alternative is five nested null-and-type checks.

**This is the most practically useful pattern feature for anyone parsing JSON.** It does not replace a real model class, but it makes the boundary code where you validate untyped data far shorter and considerably harder to get subtly wrong.

## Switch expressions and exhaustiveness

Switch became an expression, which changes how you write mapping code:

```dart
String describe(Shape shape) => switch (shape) {
  Circle(radius: final r) when r > 100 => 'huge circle',
  Circle(radius: final r) => 'circle of radius $r',
  Rectangle(width: final w, height: final h) when w == h => 'square of $w',
  Rectangle() => 'rectangle',
};
```

Three things are happening: type test, destructuring, and a `when` guard, all in the case pattern.

The feature that makes this genuinely safer is **exhaustiveness checking over sealed hierarchies**:

```dart
sealed class Result<T> {}
final class Ok<T> extends Result<T> {
  const Ok(this.value);
  final T value;
}
final class Err<T> extends Result<T> {
  const Err(this.message);
  final String message;
}

String render(Result<int> r) => switch (r) {
  Ok(value: final v) => 'Got $v',
  Err(message: final m) => 'Failed: $m',
};
```

No default case. Add a third subclass and **every** switch over `Result` becomes a compile error, listing exactly which files need updating. That is a materially different experience from discovering the gap at runtime, and it is the strongest argument for modelling states as a sealed hierarchy rather than as a class with nullable fields.

Note the deliberate absence of a `default:` — adding one silences exhaustiveness checking and gives back the guarantee you came for.

## Where records are the wrong tool

Records are anonymous, and anonymity has a cost:

- **They cannot have methods.** `(double lat, double lng)` cannot carry `distanceTo`. A class can.
- **They cannot enforce invariants.** No constructor means no validation. A record cannot guarantee that `lat` is within range.
- **The field names are the API.** Rename `width` to `w` and every call site breaks with no deprecation path.
- **They are poor documentation.** `({String, String})` at a public API boundary tells the reader nothing about which is which.

My rule: **records for local plumbing, classes for concepts.** A function returning "the parsed value and whether it was cached" is plumbing. A `User` is a concept. Anything crossing a package boundary or appearing in public API should be a named type.

## Migration, incrementally

None of this requires rewriting anything. Three changes that pay off immediately in existing code:

1. Replace `Map<String, dynamic>` returns from private helpers with records — same shape, actual type safety.
2. Replace long `if/else if` type-check chains with a switch expression.
3. Turn state classes with `isLoading`/`error`/`data` fields into sealed hierarchies, so impossible states stop compiling.

The third is the one that changes how code feels. A state class with three nullable fields has eight representable combinations and typically three legal ones; a sealed hierarchy has exactly the legal ones.

## FAQ

**Do records have runtime overhead?**

They are objects, so there is an allocation, but they are lightweight and the compiler optimises common cases. This is not a reason to avoid them in ordinary code.

**Can I use a record in a `const` context?**

Yes, if all fields are constant: `const point = (x: 1, y: 2);`.

**How do patterns interact with null safety?**

Well. `case final String s?` matches a non-null string; `case null` matches null. Exhaustiveness accounts for nullability, so a switch over `String?` needs a null case or a catch-all.

**Should sealed classes replace enums?**

Only when the variants carry data. An enum with no payload is still simpler, and enums support exhaustive switches too.

**Is `when` the same as a nested `if`?**

Functionally yes, but the guard participates in the case, so ordering and readability improve. Note that a guard does not count towards exhaustiveness — the compiler cannot prove a guarded case always matches.

---

*Record syntax, structural equality, pattern forms, and exhaustiveness rules for sealed hierarchies described here are documented in the Dart references linked above. The records-for-plumbing rule, the JSON-boundary recommendation, the migration list and the warning about `default:` defeating exhaustiveness are my own judgement from using these features in production code. Language features evolve — check the Dart SDK version your project targets.*
