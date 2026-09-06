---
title: "Writing a custom lint for your Dart codebase"
description: "Team conventions that live in a wiki get broken. Conventions that live in the analyzer get fixed before the pull request opens. Here is how the Dart analysis pipeline works and where a custom rule fits into it."
seoDescription: "How to enforce team conventions in Dart: analysis_options.yaml, lint rule selection, severity overrides, excludes, and writing a custom lint with the analyzer AST plus a quick fix."
keywords:
  - dart custom lint rule
  - analysis_options.yaml guide
  - flutter lint rules team
  - dart analyzer plugin
  - dart ast visitor
  - dart analyze fatal infos
category: "Guide"
topic: "Dart"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-11"
emoji: "🔍"
tags: ["Dart", "Tooling", "Lint", "Code Quality", "CI"]
sources:
  - name: "Customizing static analysis — Dart documentation"
    url: "https://dart.dev/tools/analysis"
  - name: "Linter rules — Dart documentation"
    url: "https://dart.dev/tools/linter-rules"
  - name: "dart analyze — Dart tool documentation"
    url: "https://dart.dev/tools/dart-analyze"
  - name: "analyzer package — pub.dev"
    url: "https://pub.dev/packages/analyzer"
  - name: "flutter_lints package — pub.dev"
    url: "https://pub.dev/packages/flutter_lints"
  - name: "Diagnostic messages — Dart documentation"
    url: "https://dart.dev/tools/diagnostic-messages"
related:
  - slug: "dart-build-runner-codegen"
    title: "Code generation in Dart: build_runner without the frustration"
  - slug: "dart-records-and-patterns"
    title: "Records and patterns in Dart: what they replace"
draft: false
---

Every team has a rule that keeps getting broken. "Don't call `context` after an await." "Repositories return `Result`, never throw." "No `print` in `lib/`." These live in a code review comment, get re-explained to each new joiner, and get violated again the week after.

An analyzer rule does not get tired of saying it.

## First, exhaust the built-in rules

Before writing anything, check whether the rule already exists. The linter ships with well over two hundred rules, and most team conventions are among them. A configuration worth starting from:

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  language:
    strict-casts: true
    strict-raw-types: true
  errors:
    invalid_annotation_target: ignore
    unused_import: error
    dead_code: error
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"

linter:
  rules:
    - always_declare_return_types
    - avoid_print
    - prefer_final_locals
    - unawaited_futures
    - use_build_context_synchronously
    - cancel_subscriptions
    - close_sinks
```

Three parts deserve comment.

**`strict-casts` and `strict-raw-types`** are the highest-value settings on this page and are not enabled by default. `strict-casts` stops `dynamic` from silently flowing into typed positions — which is exactly where JSON parsing bugs hide. Turning it on in an existing codebase will produce a lot of diagnostics; that is information, not noise.

**The `errors:` block changes severity.** A lint that is a warning is a lint the team learns to scroll past. Promote the ones you actually mean to `error`, and demote or ignore the ones you have decided you do not care about — an explicit `ignore` is far better than a rule everyone silences with inline comments.

**`exclude` must cover generated files.** Linting a `.g.dart` reports problems in code nobody wrote and nobody can fix.

Then make CI enforce it:

```bash
dart analyze --fatal-infos --fatal-warnings
```

Without those flags, `dart analyze` exits zero on infos and warnings, and your carefully chosen rules become decoration.

## When a built-in rule doesn't exist

The remaining conventions are the ones specific to your architecture, and those need a custom rule. The mechanism is an analyzer plugin: a package that receives resolved ASTs and reports diagnostics, which your IDE and `dart analyze` then surface like any other lint.

The shape of a rule is always the same: register interest in a syntactic construct, examine it, report if it violates the convention.

```dart
class AvoidRepositoryThrows extends DartLintRule {
  const AvoidRepositoryThrows() : super(code: _code);

  static const _code = LintCode(
    name: 'avoid_repository_throws',
    problemMessage: 'Repository methods must return Result, not throw.',
    correctionMessage: 'Return Err(...) instead of throwing.',
    errorSeverity: ErrorSeverity.WARNING,
  );

  @override
  void run(CustomLintResolver resolver, ErrorReporter reporter,
      CustomLintContext context) {
    context.registry.addThrowExpression((node) {
      final unit = resolver.path;
      if (!unit.contains('/repositories/')) return;
      reporter.atNode(node, _code);
    });
  }
}
```

The `context.registry.addX` callbacks are the API surface you will spend your time in — there is one per AST node type, and picking the right one is most of the work. `addMethodInvocation`, `addClassDeclaration`, `addInstanceCreationExpression` and `addAwaitExpression` cover a large share of realistic rules.

**The path check above is the crude version.** A better rule inspects the resolved element — is this method declared on a class that implements `Repository`? — which is more work but does not break when someone reorganises directories. That distinction, between *syntactic* rules (fast, easy, brittle) and *semantic* rules (slower, harder, correct), is the main design decision in any lint you write.

## Adding a fix

A lint that reports is useful. A lint that fixes itself gets adopted.

```dart
class _UseResultFix extends DartFix {
  @override
  void run(CustomLintResolver resolver, ChangeReporter reporter,
      CustomLintContext context, AnalysisError analysisError,
      List<AnalysisError> others) {
    context.registry.addThrowExpression((node) {
      if (!analysisError.sourceRange.intersects(node.sourceRange)) return;

      final builder = reporter.createChangeBuilder(
        message: 'Convert to Err(...)',
        priority: 80,
      );
      builder.addDartFileEdit((b) {
        b.addSimpleReplacement(
          node.sourceRange,
          'return Err(${node.expression.toSource()})',
        );
      });
    });
  }
}
```

The `intersects` guard matters: the fix callback runs for every node of that type in the file, and without it you would offer a fix at every throw expression rather than the one the user's cursor is on.

## What is worth a custom rule, and what isn't

| Convention | Custom lint? |
| --- | --- |
| Layering — UI must not import `data/` | Yes. High value, purely syntactic, easy to write. |
| No `DateTime.now()` outside a clock abstraction | Yes. Catches untestable code at the source. |
| Naming conventions for files or classes | Usually yes, and easy — but consider whether it earns the maintenance. |
| Formatting | No. `dart format` owns this. |
| "Functions should be short" | No. Arbitrary thresholds generate arguments, not quality. |
| Anything requiring understanding of intent | No. You will write a rule with false positives and the team will disable it. |

**The failure mode to avoid is a rule with false positives.** One wrong report and developers start adding `// ignore:` comments, and once that habit forms the rule is worse than nothing, because it is now noise the team has trained itself to bypass. If you cannot make a rule precise, make it narrower — check a smaller, more certain case — rather than accepting misfires.

## Rolling it out without a revolt

A new rule on an existing codebase surfaces hundreds of violations. Do not open that pull request.

1. Add the rule at `info` severity first. It appears in the IDE, fails nothing.
2. Fix violations directory by directory, in separate reviewable commits.
3. Once the count is zero, promote to `warning` or `error` in `analysis_options.yaml`.
4. Only now make CI fatal on it.

The `errors:` block also accepts per-directory overrides through nested `analysis_options.yaml` files, so a legacy directory can keep the old severity while new code gets the strict one. That is often the only realistic path in a large codebase.

## FAQ

**Do custom lints slow down my IDE?**

They run in a separate analysis process, so the effect is modest, but a semantic rule that resolves elements on every keystroke is measurably heavier than a syntactic one. Prefer syntactic checks where they suffice.

**Can I ship a rule to other teams?**

Yes — publish the lint package and have consumers add it to `dev_dependencies` plus their analysis options.

**Does `dart analyze` run custom lints?**

Through the plugin mechanism, yes, provided the plugin is configured in `analysis_options.yaml`. Verify this explicitly before relying on CI to enforce a custom rule.

**What about `// ignore_for_file:`?**

It works on custom lints too. Consider grepping for it in CI and failing on new occurrences of your most important rules.

**Is `avoid_print` enough to stop logging in production?**

No — it catches `print`, not a logger someone configured to write to stdout. Rules catch patterns, not intent.

---

*The `analysis_options.yaml` structure, `strict-casts`/`strict-raw-types`, severity overrides, excludes and `dart analyze` flags are documented in the Dart references linked above. The custom-lint code illustrates the standard analyzer-plugin shape; the exact API surface depends on the lint framework package and version you use, so check its docs before copying. The rule-selection table, the false-positive warning and the staged rollout are my own judgement from introducing lint rules to existing teams.*
