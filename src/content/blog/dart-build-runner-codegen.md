---
title: "Code generation in Dart: build_runner without the frustration"
description: "build_runner is slow, opaque, and occasionally wrong — until you understand what it caches, why it conflicts, and which generators actually earn their build time. A practical guide to the whole pipeline."
seoDescription: "A practical guide to build_runner in Dart and Flutter: part files, build.yaml configuration, generator conflicts, watch mode, cache invalidation, CI setup, and deciding when code generation is worth it."
keywords:
  - dart build_runner guide
  - flutter code generation
  - build.yaml configuration
  - build_runner slow fix
  - json_serializable freezed
  - dart part file generated
category: "Guide"
topic: "Dart"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-12"
emoji: "⚙️"
tags: ["Dart", "Tooling", "Build", "Codegen", "CI"]
sources:
  - name: "build_runner package — pub.dev"
    url: "https://pub.dev/packages/build_runner"
  - name: "build_config — build.yaml reference"
    url: "https://pub.dev/packages/build_config"
  - name: "json_serializable package — pub.dev"
    url: "https://pub.dev/packages/json_serializable"
  - name: "source_gen package — pub.dev"
    url: "https://pub.dev/packages/source_gen"
  - name: "Libraries and parts — Dart documentation"
    url: "https://dart.dev/language/libraries"
  - name: "dart run — Dart tool documentation"
    url: "https://dart.dev/tools/dart-run"
related:
  - slug: "dart-streams-in-depth"
    title: "Dart streams in depth: backpressure, broadcast, and the leaks in between"
  - slug: "dart-custom-lints-analyzer"
    title: "Writing a custom lint for your Dart codebase"
draft: false
---

You add `json_serializable`, run `dart run build_runner build`, and get:

```
Conflicting outputs were detected and the build will be terminated.
```

You run it with `--delete-conflicting-outputs`, it works, and you type that flag forever afterwards without knowing what it deleted. That is the typical relationship developers have with build_runner, and it is worth fixing, because the tool is more predictable than it looks.

## The model: one asset in, one asset out

build_runner is not a script runner. It is a build system over *assets* — files identified as `package:name|path`. Every builder declares which extensions it consumes and which it produces, and build_runner constructs a graph from that.

`json_serializable` says: for every `.dart`, maybe produce a `.g.dart`. `freezed` says: for every `.dart`, maybe produce a `.freezed.dart`. Because outputs are keyed by path, **two builders that claim the same output path conflict** — and so does one builder whose previous output is still on disk from a run with different configuration.

That is what `--delete-conflicting-outputs` does: it removes generated files that the current build wants to write but that it did not itself create in this run's cache. It is safe for genuinely generated files, and it is why you should never hand-edit a `.g.dart`.

The cache lives in `.dart_tool/build/`. When builds behave impossibly, that directory is the thing to delete:

```bash
rm -rf .dart_tool/build && dart run build_runner build --delete-conflicting-outputs
```

## Part files, and the error everyone hits first

Most generators emit *part* files, which means the generated code shares a library with your source:

```dart
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';   // required, and the name must match the file exactly

@JsonSerializable()
class User {
  const User({required this.id, required this.name});
  final String id;
  final String name;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

`Target of URI hasn't been generated` before the first build is expected — the analyser is reporting a file that does not exist yet. Run the build; it resolves.

Because it's a part, the generated code can see your private members, and your file can see the generated `_$…` functions. It also means one generated file per source file, which is why a package with 200 models has 200 `.g.dart` files.

## Making it fast

Build time is the main complaint, and most of it is fixable through configuration. `build.yaml` at the package root:

```yaml
targets:
  $default:
    builders:
      json_serializable:
        generate_for:
          - lib/models/**.dart
        options:
          explicit_to_json: true
          field_rename: snake
      freezed:
        generate_for:
          - lib/models/**.dart
```

`generate_for` is the highest-leverage setting in the file. By default a builder is offered **every** Dart file in your package, and it must at minimum parse each one to decide there is nothing to do. Restricting it to the directory that actually contains annotated classes routinely cuts build time by more than half on a large package.

Other practical measures:

- **Use `watch` during development**, not repeated `build`. It keeps the asset graph warm and rebuilds only what changed.
  ```bash
  dart run build_runner watch --delete-conflicting-outputs
  ```
- **Split large packages.** build_runner works per package; a monorepo of five packages rebuilds only the one you touched.
- **Audit your generators.** Every codegen dependency taxes every build. A generator saving you thirty lines of boilerplate in two files is not paying for itself.

## Which generators earn their keep

My honest ranking, from a codebase-maintenance perspective rather than a feature-count one:

| Generator | Verdict |
| --- | --- |
| `json_serializable` | Worth it above ~10 models. Hand-written `fromJson` is where silent field-name typos live. |
| `freezed` | Worth it if you use sealed unions and `copyWith` heavily. Records and sealed classes in modern Dart cover part of what it used to be needed for. |
| `retrofit` / API clients | Worth it for large, stable APIs. Overhead for five endpoints. |
| `mockito` codegen | Prefer hand-written fakes for anything with meaningful behaviour; generated mocks are best for wide interfaces you barely use. |
| Asset/localisation generators | Almost always worth it — they turn runtime string typos into compile errors. |

The question I ask before adding one: **what class of bug does this prevent?** "Less typing" is a weak answer; "a typo in a JSON key is now a compile error" is a strong one.

## CI and version control

Two defensible policies, and you should pick one deliberately:

**Do not commit generated files** (my default). `.gitignore` gets `*.g.dart`, `*.freezed.dart`, and CI runs the build before analysis and tests:

```yaml
- run: dart pub get
- run: dart run build_runner build --delete-conflicting-outputs
- run: dart analyze --fatal-infos
- run: dart test
```

Pros: no generated-file diffs in review, no chance of stale output being committed. Cons: every clean checkout pays the build cost, and a generator version bump can break CI without any source change.

**Commit them.** Checkout is instantly buildable and diffs show exactly what a generator version change did. Cons: noisy pull requests, and merge conflicts in files nobody should be editing.

If you publish a package to pub.dev you must commit the generated files, since consumers do not run your builders.

Either way, **pin your generator versions**. `json_serializable: ^6.0.0` will happily pick up a minor release that changes output formatting and produce a thousand-line diff on an unrelated PR.

## Debugging a build that does nothing

When a build reports success but your `.g.dart` is missing or stale, work through this in order:

1. Is the `part` directive present and spelled exactly right?
2. Is the annotation on the class, and imported from the right package?
3. Does `generate_for` in `build.yaml` actually include this file's path?
4. Is the builder in `dev_dependencies`? A generator in `dependencies` still runs but bloats consumers.
5. Run with `--verbose` and look for the builder's name against your file.
6. Delete `.dart_tool/build` and rebuild.

Step 3 catches more cases than you'd expect, because adding a `generate_for` for speed and then creating models in a new directory is a very easy sequence to walk into.

## FAQ

**Why is the first build after `pub get` so slow?**

build_runner compiles the build script itself, including every builder. That kernel is then cached — subsequent builds skip it unless dependencies change.

**Can I run build_runner from a Flutter project?**

Yes: `dart run build_runner build`. `flutter pub run build_runner` is the older form and still works, but `dart run` is the current spelling.

**Is `part` required?**

No — some generators emit standalone libraries you import instead. Part files are the common case because they can access private members.

**Does codegen affect app size?**

The generated code is real code and is tree-shaken like any other. Serialisation code for models you never use gets removed if nothing references it.

**Should I write my own builder?**

Only for something specific to your codebase that no package covers, and expect `source_gen` to take a day to learn. It is a reasonable investment for, say, generating a route table from annotations in a large app.

---

*Asset-graph semantics, `build.yaml` options including `generate_for`, part-file requirements, and the behaviour of `--delete-conflicting-outputs` are documented in the build_runner and build_config references linked above. The generator ranking, the commit-or-not trade-off, the debugging order and the "what class of bug does this prevent" test are my own judgement from maintaining Dart codebases with heavy code generation.*
