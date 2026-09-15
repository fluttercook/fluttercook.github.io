---
title: Mobile observability cost control
description: Sampling, cardinality, and what to keep forever.
seoDescription: Mobile observability cost sampling cardinality retention. Practical guide for production Flutter teams.
keywords:
- observability cost
- log sampling
- metrics cardinality
- retention policy
- flutter
- dart
- mobile development
- flutter tutorial
category: Quality
topic: Quality
level: Intermediate
author: Trung Hieu
publishDate: '2026-09-11'
emoji: 🧭
tags:
- Quality
- Cost
sources:
- name: Sentry
  url: https://docs.sentry.io/platforms/flutter/
- name: Flutter documentation
  url: https://docs.flutter.dev/
- name: Dart documentation
  url: https://dart.dev/guides
related:
- slug: flutter-release-rollback-playbook
  title: Mobile rollback playbooks when stores are slow
- slug: flutter-incident-comms-mobile
  title: User communication during mobile incidents
draft: false
---

Telemetry can cost more than hosting if left unchecked. This article turns that observation into a small implementation model you can test, measure, and keep boring when the app grows.

## The problem in one sentence

Sampling, cardinality, and what to keep forever. The useful question is not whether the API or pattern looks elegant in isolation. It is where state lives, which boundary owns failure, and how a user recovers when the happy path disappears.

![Flutter architecture diagram for Mobile observability cost control](/blog/images/fluttercook-editorial-2026.svg)

## A practical model

Sample traces; keep 100% of errors.

Start with one explicit owner for the behavior. Keep widgets responsible for rendering and user intent; keep IO, persistence, permissions, and retries behind a small interface. That gives you a seam for a fake in tests and a place to record the facts that matter in production.

For a Flutter app, the boundary usually looks like this:

1. The widget emits an intent such as load, submit, refresh, or retry.
2. A controller or use case validates the intent and calls the boundary.
3. The boundary returns typed data or a typed failure, never a string meant only for logs.
4. The UI renders loading, empty, success, and failure states explicitly.

This shape is deliberately modest. It works with `setState`, Bloc, Riverpod, or another state layer because the important decision is ownership, not the brand of package.

## Minimal implementation

The smallest useful experiment is enough to expose the trade-off:

```text
// 1% success traces, 100% errors
```

Put this behind a feature-sized interface and add one test for the success path and one for the failure path. If the example needs global state before it can run, the boundary is probably in the wrong place.

## Production checklist

- Define the lifecycle: who starts work, who cancels it, and what survives a restart?
- Measure the user-visible result: frame time, bytes, latency, conversion, or recovery time.
- Keep platform-specific code at the edge and document the minimum OS/SDK assumptions.
- Add an empty state and an offline/error state before adding polish.
- Log identifiers and timings, but redact tokens, personal data, and full payloads.
- Prefer a reversible rollout: a flag, staged release, or server-side fallback.

## Pitfalls worth paying for early

Unbounded labels explode metrics bills. A common failure mode is to make the demo path correct while leaving cancellation, retries, permissions, accessibility, and upgrade behavior implicit. Those are not edge cases once the app has real users. Test at least one slow device, one interrupted network request, and one process restart where this topic affects lifecycle or storage.

## How to decide whether it worked

Write down the baseline before changing code. Compare the same user journey on the same device class, then inspect both the median and the worst visible failures. A smaller diff with a clear rollback is usually safer than a framework-wide rewrite. Keep the decision and its evidence near the code so the next upgrade does not restart the same argument.

For the neighboring ideas, read [Mobile rollback playbooks when stores are slow](/blog/flutter-release-rollback-playbook/) and [User communication during mobile incidents](/blog/flutter-incident-comms-mobile/).
