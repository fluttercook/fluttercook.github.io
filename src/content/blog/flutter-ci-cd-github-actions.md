---
title: "A Flutter CI pipeline that catches real problems"
description: "Most Flutter CI configs run flutter test and stop. Here is a pipeline that also catches formatting drift, dependency rot, golden regressions, and the build failures that only appear on a clean machine — with the caching that keeps it under five minutes."
seoDescription: "Flutter CI/CD on GitHub Actions: caching the SDK and pub cache, analyze with fatal-infos, golden tests, matrix builds, signing artifacts, and a workflow file you can adapt."
keywords:
  - flutter github actions ci
  - flutter ci cd pipeline
  - subosito flutter-action cache
  - flutter golden test ci
  - flutter build android ci signing
  - flutter analyze fatal infos
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-24"
emoji: "⚙️"
tags: ["Flutter", "CI/CD", "GitHub Actions", "Testing", "DevOps"]
sources:
  - name: "Continuous delivery with Flutter — Flutter documentation"
    url: "https://docs.flutter.dev/deployment/cd"
  - name: "flutter test — Flutter documentation"
    url: "https://docs.flutter.dev/testing/overview"
  - name: "Caching dependencies — GitHub Actions documentation"
    url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
  - name: "Encrypted secrets — GitHub Actions documentation"
    url: "https://docs.github.com/en/actions/security-guides/encrypted-secrets"
  - name: "Build and release an Android app — Flutter documentation"
    url: "https://docs.flutter.dev/deployment/android"
  - name: "dart format — Dart documentation"
    url: "https://dart.dev/tools/dart-format"
related:
  - slug: "flutter-flavors-build-config"
    title: "Flutter flavors: one codebase, three apps, zero copy-pasted config"
  - slug: "flutter-app-size-reduction"
    title: "Shrinking a Flutter app: where the megabytes actually are"
draft: false
---

Every Flutter repository eventually grows a `.github/workflows/ci.yml` containing `flutter test`. It passes, everyone feels covered, and then a release build fails on the build machine for a reason nobody's laptop could have surfaced.

CI earns its keep by catching the failures that local development structurally cannot: stale generated code, a dependency that only resolves because of your local pub cache, a formatting change nobody ran, a golden that drifted. This is a pipeline built around those.

## The shape of it

Four jobs, in two waves:

| Job | Runs | Catches |
| --- | --- | --- |
| `analyze` | every push and PR | format drift, lint regressions, unused code |
| `test` | every push and PR | unit, widget, and golden failures |
| `build` | PRs to main and tags | compile failures that only occur on a clean machine |
| `release` | tags only | signing, artifact upload |

`analyze` and `test` run in parallel and are fast. `build` is slow and gated. That split matters: a pipeline where every push waits eight minutes for an Android build is a pipeline people learn to ignore.

## Analyze, with teeth

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true

      - run: flutter pub get
      - run: dart format --output=none --set-exit-if-changed .
      - run: flutter analyze --fatal-infos
      - run: flutter pub outdated --exit-code-on-outdated-transitive || true
```

Four details are doing the work.

**`concurrency` with `cancel-in-progress`.** Push three commits to a PR and you get one run, not three. On a busy repo this is the single largest saving available.

**`flutter-version-file: pubspec.yaml`** reads the SDK constraint from the repo rather than pinning a version in the workflow. One fewer place to update, and no drift between what CI builds and what the project declares.

**`dart format --set-exit-if-changed`** fails the build on unformatted code instead of quietly rewriting it. The `--output=none` stops it from writing files in CI, which would otherwise make the diff confusing.

**`--fatal-infos`** promotes info-level lints to failures. This is stricter than most teams start with, and it is the setting that keeps a lint baseline from decaying — infos that never fail anything accumulate until nobody reads the analyzer output at all.

## Test, including goldens

```yaml
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true

      - run: flutter pub get
      - run: flutter test --coverage --reporter github

      - name: Upload failed goldens
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: golden-failures
          path: '**/failures/**'
```

`--reporter github` annotates failures directly on the diff, so a failing test shows up on the line it belongs to rather than buried in a log.

The artifact upload is the part people skip and then regret. When a golden test fails in CI, the framework writes the expected, actual, and diff images into a `failures/` directory. Without uploading them you are reduced to guessing; with them, you download three PNGs and see the problem in ten seconds.

Goldens are also **font-dependent and platform-dependent**. Generate them on Linux in CI, or accept that a Mac-generated golden will fail on an Ubuntu runner. If you generate locally, `flutter test --update-goldens` on the same OS the CI uses is the only reliable path.

## Guarding generated code

If the project uses `build_runner`, CI must verify the committed output matches the sources:

```yaml
      - name: Verify generated code is current
        run: |
          dart run build_runner build --delete-conflicting-outputs
          if ! git diff --quiet; then
            echo "Generated code is stale. Run build_runner and commit."
            git diff --stat
            exit 1
          fi
```

This catches the single most common "works on my machine" failure in code-generation projects: someone edited a model, forgot to regenerate, and the committed `.g.dart` no longer matches.

## Build, on a matrix

```yaml
  build:
    needs: [analyze, test]
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            target: apk
            cmd: flutter build apk --release --split-per-abi
          - os: macos-latest
            target: ios
            cmd: flutter build ios --release --no-codesign
          - os: ubuntu-latest
            target: web
            cmd: flutter build web --release
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true
      - run: flutter pub get
      - run: ${{ matrix.cmd }}
```

`fail-fast: false` is deliberate — when the web build breaks you want to know whether iOS also broke, not have it cancelled.

`--no-codesign` for iOS lets you verify compilation on every PR without managing certificates. Signing belongs in the release job, where the secrets are.

## Signing, without leaking

The release job is where secrets appear, and where care is warranted:

```yaml
  release:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: [build]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true

      - name: Restore keystore
        env:
          KEYSTORE_B64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}
        run: echo "$KEYSTORE_B64" | base64 --decode > android/app/upload-keystore.jks

      - name: Write signing config
        env:
          STORE_PASSWORD: ${{ secrets.ANDROID_STORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.ANDROID_KEY_PASSWORD }}
          KEY_ALIAS: ${{ secrets.ANDROID_KEY_ALIAS }}
        run: |
          cat > android/key.properties <<EOF
          storePassword=$STORE_PASSWORD
          keyPassword=$KEY_PASSWORD
          keyAlias=$KEY_ALIAS
          storeFile=upload-keystore.jks
          EOF

      - run: flutter build appbundle --release
```

Three rules that are not optional:

1. **Secrets go through `env:`, never inline in a `run:` string.** An inline `${{ secrets.X }}` inside a shell command can end up in a trace or an error message.
2. **Never `echo` a secret.** GitHub masks known secret values in logs, but only exact matches — a base64 fragment or a transformed value is not masked.
3. **Gate the job on the tag.** `if: startsWith(github.ref, 'refs/tags/v')` means a PR from a fork never reaches the step that touches signing material.

If you can use OIDC and short-lived credentials for your distribution target, prefer that over long-lived stored secrets entirely.

## What makes it fast

The `cache: true` on `subosito/flutter-action` caches the SDK itself. Add the pub cache and the Gradle cache for the Android job:

```yaml
      - uses: actions/cache@v4
        with:
          path: |
            ~/.pub-cache
            ~/.gradle/caches
          key: ${{ runner.os }}-deps-${{ hashFiles('**/pubspec.lock', '**/*.gradle*') }}
          restore-keys: ${{ runner.os }}-deps-
```

Keying on `pubspec.lock` rather than `pubspec.yaml` matters: the lock file is what actually determines resolved versions, so a cache keyed on it is never stale in the way that counts. The `restore-keys` prefix gives you a partial hit when the lock changes, which is far better than a cold cache.

## FAQ

**Should CI run integration tests?**

Only if you have a real device farm or a reliable emulator setup, and only on a schedule or on main. Integration tests on every PR are the fastest way to teach a team to ignore a red build.

**Why does `flutter analyze` pass locally and fail in CI?**

Usually a stale local analysis server, or generated files present locally but not committed. The build_runner check above catches the second; restarting your analyzer catches the first.

**Is `--fatal-infos` too strict?**

For a new project, no. For an existing one with hundreds of infos, adopt it after a cleanup pass, or you will just disable the job.

**How do I keep the workflow from running on documentation-only changes?**

`paths-ignore` on the trigger. Be careful: if a required status check never runs, the PR cannot merge. Use a separate always-passing job with the same name, or make the check non-required.

**Should the pipeline publish to the stores automatically?**

Building and uploading to an internal test track automatically is reasonable. Promoting to production automatically is a policy decision that should involve a human, and I would not wire it up by default.

---

*The GitHub Actions features, Flutter build commands, `dart format` flags and signing setup described here are documented in the references linked above. The four-job split, the `--fatal-infos` recommendation, the generated-code guard, and the secret-handling rules are my own judgement from maintaining pipelines of this shape. Action versions and runner images change — pin what you depend on and re-check the versions before copying this wholesale.*
