---
title: "Dart 3.13 primary constructors: less boilerplate, one real breaking change"
description: "Primary constructors are stable in Dart 3.13. Here is the full syntax, how declaring parameters work, the const and named forms, and the breaking change to final and var on function parameters."
seoDescription: "Dart 3.13 primary constructors guide: declaring parameters with var and final, named and const primary constructors, super parameters, scoping rules, and the parameter_assignments lint."
keywords: ["dart 3.13", "dart primary constructors", "declaring parameters dart", "dart const constructor syntax", "parameter_assignments lint", "dart 3.13 breaking change"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🎯"
tags: ["Dart 3.13", "Dart", "Language", "Flutter 3.47", "Refactoring"]
sources:
  - name: "Announcing Dart 3.13 — Dart Blog"
    url: "https://dart.dev/blog/announcing-dart-3-13"
  - name: "Primary constructors — Dart language docs"
    url: "https://dart.dev/language/primary-constructors"
  - name: "Constructors — Dart language docs"
    url: "https://dart.dev/language/constructors"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material and Cupertino leave the SDK, Impeller takes over desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Flutter's 2026 roadmap: WebAssembly by default, LG smart TVs, and the push for platform parity"
draft: false
---

Dart 3.13 ships alongside Flutter 3.47, and its headline feature is the one Dart developers have been asking for since the language got null safety: **primary constructors are stable**. Declare your fields and your constructor in the class header, and delete the three-line ceremony that every model class in your codebase currently repeats.

There is also a breaking change hiding in the release, and it is not the one most people expect.

## The basic shape

The traditional form:

```dart
class Point {
  int x;
  int y;
  Point(this.x, this.y);
}
```

The primary constructor form:

```dart
class Point(var int x, var int y);
```

That is the entire class. Note the ordering — the modifier comes first, then the type, then the name: `var int x`, not `int var x`.

## Declaring parameters are the actual feature

This is the part worth understanding properly, because it is where the design is subtler than "shorter syntax".

A parameter prefixed with `var` or `final` is a **declaring parameter**: it induces an instance field. A parameter without either modifier behaves like an ordinary constructor argument and creates no field at all.

```dart
// Creates fields x and y
class Point(var int x, var int y);

// No field created — `name` is just an argument
class User(String name);
```

That distinction gives you a validation-only constructor for free, without the usual trick of a private field you never read.

For immutable models — which is most of them in a Flutter codebase — use `final`:

```dart
class ConstPoint(final int x, final int y);
```

## Named parameters, and the underscore trick

Named parameters work as you would expect, with one nice detail: a private named parameter automatically exposes a public name to callers.

```dart
class User({required var String _name});
// Called as: User(name: 'John Doe')
```

The field is `_name`, private to the library. The argument label is `name`, public. You get encapsulation without writing a constructor that maps one to the other.

## Named and private primary constructors

Append a dot and a name after the class identifier:

```dart
class Point.custom(var int x, var int y);

// Private — restricts direct instantiation from outside the library
class Point._(var int x, var int y);
```

The private form is the sealed-ish pattern many packages implement by hand today.

## Const primary constructors

Put `const` before the parameter list:

```dart
class ConstPoint const (final int x, final int y) {
  final int z;
  this : z = x + y;
}
```

The constraints are the ones you would guess from `const` semantics:

- no body block
- every field must be `final` and definitely initialised
- initialising expressions must be potentially constant

For Flutter this matters more than it looks. Const widget constructors are a real performance lever, and anything that makes them cheaper to write means more of them get written.

## Adding a body without giving up the header

You are not choosing between a primary constructor and constructor logic. `this :` introduces an initializer list, a body, or both:

```dart
class Point(var int x, var int y) {
  this : assert(x >= 0 && y >= 0) {
    print('Point initialized at ($x, $y)');
  }
}
```

Super parameters forward cleanly:

```dart
class Person(final String name, final int age);

class Employee(super.name, super.age, final String role) extends Person;
```

## The scoping rule that will trip you up

There are two scopes, and they resolve the same identifier differently:

| Scope | Where | `x` refers to |
| --- | --- | --- |
| Primary initializer scope | Field initializers, initializer list | the **parameter** |
| Primary parameter scope | Constructor body | the **field** (for declaring parameters) |

Concretely:

```dart
class ScopingDemo(var String x, String suffix) {
  final String field = x;  // 'x' is the parameter

  this : {
    x = x.toUpperCase();   // 'x' now refers to the field
    print('$x$suffix');    // 'suffix' is still the parameter
  }
}
```

Read that twice before you refactor a class with a non-trivial initializer list. It is consistent, but it is not obvious.

## Restrictions

Compile-time constraints worth knowing before you start converting classes:

- declaring parameters cannot be `late` or `external`
- parameter names cannot collide with existing methods or fields
- parameters are read-only inside the primary initializer scope
- you cannot initialise a field both at its declaration and in the primary constructor
- mixin classes may only declare trivial primary constructors — no parameters, no initializer list, no body
- `covariant` only works with mutable (`var`) declaring parameters

## The breaking change

Here is the part to plan for. **`final` and `var` on regular function parameters are now reserved exclusively for primary constructor declaring parameters.** Existing code that wrote `void f(final int x)` becomes invalid.

The lint story changed accordingly: `parameter_assignments` (Dart 3.13+) replaces the older `avoid_final_parameters` and `var_with_no_type_annotation` from 3.12 and earlier.

There is a second, quieter hazard: a method named `factory` without an explicit return type can now be misparsed as a factory constructor. If you have one, add the return type annotation.

## What else is in 3.13

Beyond the language change:

- **dart2wasm deferred loading (preview)** — `dart compile wasm -O2 --enable-deferred-loading`, with meaningful initial-page-load improvements over `dart2js` for large apps
- **`@RecordUse()`** in `package:meta`, enabling native libraries to be tree-shaken alongside Dart code
- **formatter refinements** — a fix for misformatting around large collection literals, better method-chain split heuristics, and blank lines between import sections per Effective Dart
- **type promotion soundness fix** for nested functions
- **faster dartdoc rendering** on pub.dev via a two-level hash index

## Adopting it without churn

1. **Upgrade and build.** Fix any `void f(final int x)` parameters the analyzer now rejects.
2. **Add explicit return types** to any method named `factory`.
3. **Enable `parameter_assignments`** and remove `avoid_final_parameters` / `var_with_no_type_annotation` from `analysis_options.yaml`.
4. **Start with plain data classes** — DTOs, value objects, `freezed`-adjacent models. Highest boilerplate reduction, lowest risk.
5. **Use the four IDE refactorings** to move between primary and in-body constructors rather than editing by hand.
6. **Convert const widget constructors next**, once you are comfortable with the const form's constraints.
7. **Leave classes with complex initializer lists for last**, and re-read the scoping table before you touch them.

## The bottom line

Primary constructors are the rare language feature that is purely subtractive: same semantics, less typing, no new concepts once you understand declaring parameters. The `var`/`final` restriction on function parameters is a genuine breaking change, but a mechanical one your analyzer will find in a single build. Convert your data classes this week; leave the gnarly ones until you have internalised the two-scope rule.
