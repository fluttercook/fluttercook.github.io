---
title: "Extension types in Dart: a new name for an old value"
description: "Extension types give a primitive a distinct static type with no runtime allocation. That is a genuinely useful tool for ID confusion and unit errors — and a trap if you expect them to behave like classes."
seoDescription: "Dart extension types explained: zero-cost wrappers over a representation type, why they are not runtime types, how they differ from extension methods and wrapper classes, and where they break down."
keywords:
  - dart extension types
  - dart zero cost wrapper
  - dart typedef vs extension type
  - dart primitive obsession
  - dart representation type
  - dart extension methods difference
category: "Deep Dive"
topic: "Dart"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-14"
emoji: "🧬"
tags: ["Dart", "Language", "Types", "Performance", "API Design"]
sources:
  - name: "Extension types — Dart documentation"
    url: "https://dart.dev/language/extension-types"
  - name: "Extension methods — Dart documentation"
    url: "https://dart.dev/language/extension-methods"
  - name: "Typedefs — Dart documentation"
    url: "https://dart.dev/language/typedefs"
  - name: "Class modifiers — Dart documentation"
    url: "https://dart.dev/language/class-modifiers"
  - name: "dart:js_interop — Dart API docs"
    url: "https://api.dart.dev/stable/dart-js_interop/dart-js_interop-library.html"
  - name: "Type system — Dart documentation"
    url: "https://dart.dev/language/type-system"
related:
  - slug: "dart-records-and-patterns"
    title: "Records and patterns in Dart: what they replace"
  - slug: "dart-streams-in-depth"
    title: "Dart streams in depth: backpressure, broadcast, and the leaks in between"
draft: false
---

Every codebase past a certain size has this bug at least once:

```dart
void transfer(String fromUserId, String toAccountId, int cents) { ... }

transfer(accountId, userId, 500); // compiles fine, wrong at runtime
```

Both are `String`, so the type system has nothing to say. The usual fix is a wrapper class, which costs an allocation on every ID you touch. Extension types are the same fix without the allocation.

```dart
extension type UserId(String value) {}
extension type AccountId(String value) {}

void transfer(UserId from, AccountId to, int cents) { ... }

transfer(accountId, userId, 500); // compile error
```

At runtime, `UserId` **is** a `String`. There is no wrapper object, no field access indirection, nothing allocated. The distinction exists only in the static type system, and is erased before the program runs.

## What "erased" actually means

This is the part that decides whether extension types fit your problem. The compiler replaces the extension type with its representation type. Consequences follow directly:

```dart
extension type UserId(String value) {}

final id = UserId('u_123');

print(id is String);       // true
print(id.runtimeType);     // String
print(id is UserId);       // this is a compile-time check, not a runtime one

// And crucially:
final list = <Object>[UserId('a'), 'a'];
print(list[0] == list[1]); // true — both are the string 'a'
```

So an extension type gives you **compile-time** distinctness only. If your code branches on `runtimeType`, stores values in a heterogeneous list and switches on their type, or relies on `is` checks at runtime to tell IDs apart, extension types will not do it. A wrapper class will.

A second consequence: extension types are not subtypes in the usual sense, and you cannot make one implement an interface unless the representation type does. `extension type UserId(String value) implements Comparable<UserId>` will not compile just because you'd like it to.

## Controlling the surface

By default an extension type exposes **nothing** from its representation type:

```dart
extension type UserId(String value) {}

final id = UserId('u_123');
id.length;        // compile error — String members are not inherited
id.value.length;  // fine
```

That is usually what you want for an ID: `UserId` is not a string you should be uppercasing. When you do want the underlying API, declare it explicitly:

```dart
extension type Meters(double value) implements Comparable<num> {
  Meters operator +(Meters other) => Meters(value + other.value);
  Meters operator *(double k) => Meters(value * k);
  double get inFeet => value * 3.28084;

  @override
  int compareTo(num other) => value.compareTo(other);
}

final total = Meters(4.5) + Meters(2.0);
print(total.inFeet);
```

`implements` here does not mean subclassing — it means "also allow these members through, and treat this type as assignable to that one." Note that `implements num` would make `Meters` freely assignable to `num`, which throws away the safety you added; be sparing with what you expose.

The comparison to alternatives:

| Approach | Runtime cost | Distinct at compile time | Distinct at runtime | Can add methods |
| --- | --- | --- | --- | --- |
| `typedef UserId = String` | none | no | no | no |
| `extension on String` | none | no | no | yes (on all Strings) |
| `extension type UserId(String)` | none | yes | no | yes |
| `class UserId { final String v; }` | allocation | yes | yes | yes |

The row worth staring at is the second: an extension method adds `userIdish` behaviour to **every** `String` in your program. Extension types add it to one named type.

## The interop case

Extension types were designed alongside `dart:js_interop`, and that is where they are least optional. A JavaScript object arriving in Dart has no Dart class; modelling it as an extension type over `JSObject` gives you a typed API with no marshalling cost:

```dart
extension type DomRect._(JSObject _) implements JSObject {
  external double get width;
  external double get height;
}
```

The `._` names a private constructor, which is the idiom for "this value comes from somewhere else, do not construct it yourself."

## Where I use them, and where I don't

Use them for:

- **IDs and opaque handles.** `UserId`, `SessionToken`, `Sku`. The classic case.
- **Units.** `Meters`, `Cents`, `Milliseconds`. Mixing units is a real bug class, and an allocation per value is a real cost in hot paths.
- **Validated strings** where validation happens once at the boundary — `Email`, `Slug` — via a factory that throws or returns null.
- **Interop wrappers**, as above.

Do not use them for:

- Anything you need to `is`-check at runtime.
- Anything stored heterogeneously and dispatched on type.
- Domain models. A `User` should be a class; it has invariants an extension type cannot enforce and identity semantics an extension type cannot give.
- Values you serialise with a code generator that reflects over runtime types — the generator sees `String`, not `UserId`.

**The honest summary is that extension types solve a narrow problem completely.** They are not a lighter class; they are a static-only naming layer with an escape hatch. Reaching for them where you actually wanted a class produces code that compiles beautifully and behaves surprisingly.

A validated example, since it's the pattern most worth copying:

```dart
extension type const Email._(String value) {
  static final _re = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

  factory Email(String raw) {
    final trimmed = raw.trim();
    if (!_re.hasMatch(trimmed)) {
      throw FormatException('Not an email: $raw');
    }
    return Email._(trimmed);
  }

  static Email? tryParse(String raw) =>
      _re.hasMatch(raw.trim()) ? Email._(raw.trim()) : null;
}
```

Now a function taking `Email` has a static guarantee that validation already ran, at zero runtime cost, and there is exactly one place in the codebase where that validation lives.

## FAQ

**Are extension types the same as Kotlin's value classes?**

Similar intent, different mechanics. Kotlin's inline classes can box in some situations; Dart's extension types never exist at runtime at all.

**Can I use one as a map key?**

Yes, and it behaves as the representation type does — `UserId('a')` and the plain string `'a'` are the same key. That is occasionally convenient and occasionally a bug.

**Do they work with `const`?**

Yes: `extension type const Email._(String value)` allows const construction where the representation is const.

**Can two extension types over the same representation be assigned to each other?**

Not directly — that is the entire point. Convert explicitly through `.value`.

**Should I add `implements` to get the underlying methods?**

Only for the ones you actually want. Every member you expose is a way for the distinction to leak away.

---

*Erasure semantics, the default member surface, `implements` behaviour, and the `dart:js_interop` usage described here are documented in the Dart references linked above. The use/don't-use lists, the comparison table's practical readings, and the validated-`Email` pattern are my own judgement from applying extension types in production code. Verify behaviour against the Dart SDK version your project targets.*
