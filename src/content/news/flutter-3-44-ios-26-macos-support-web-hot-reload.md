---
title: "Flutter 3.44 review: iOS 26 support, stateful hot reload on web, and Cupertino Squircles"
description: "Flutter 3.44 fully supports iOS 26, Xcode 26, and macOS 26, makes stateful hot reload the default on web, and adds Apple-matching Squircle shapes. A developer's review."
seoDescription: "Flutter 3.44 adds iOS 26/macOS 26 support, stateful hot reload on web, Cupertino Squircles, and Android screen-share protection. Full review for mobile developers."
keywords: ["flutter 3.44", "flutter latest version", "flutter ios 26", "flutter web hot reload", "cupertino squircles", "flutter mobile app"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-07-14"
updatedDate: "2026-07-14"
emoji: "🐦"
tags: ["Flutter 3.44", "Flutter", "iOS 26", "Web", "Release"]
sources:
  - name: "Flutter release notes"
    url: "https://docs.flutter.dev/release/release-notes"
  - name: "Flutter — What's new in the docs"
    url: "https://docs.flutter.dev/release/whats-new"
draft: false
---

The latest stable Flutter release, **Flutter 3.44**, is one of the most consequential updates of the year for teams shipping to Apple platforms and the web. The documentation was last refreshed on July 10, 2026, and the release notes read like a checklist of the pain points cross-platform developers have been asking Google to fix.

## Full iOS 26 and macOS 26 support

Flutter 3.44 (building on 3.38) **fully supports the iOS 26, Xcode 26, and macOS 26 releases**. That is the headline for most teams: as Apple shipped its Liquid Glass redesign and a new toolchain, Flutter kept pace so you can build and submit against the current SDK without hacks.

There is one migration to be aware of. Flutter now supports Apple's mandated **UIScene lifecycle**, and code migration is required to adopt it. If you maintain an iOS Flutter app, this is the upgrade task to schedule — it is mechanical, but it is not optional going forward.

## Cupertino Squircles land

Apple's rounded corners have never been simple circles — they use continuous curvature, the "squircle." Flutter 3.44 introduces **Cupertino Squircles** via a new `RSuperellipse` shape that matches Apple's native rounded corners. This required deep changes in the rendering engine, and it closes one of the last visible gaps between a Flutter iOS app and a native one. On iOS 26, where Liquid Glass makes shape and light more prominent, getting corners exactly right matters.

## Stateful hot reload becomes the default on web

For anyone who builds Flutter Web, this is the quality-of-life win of the release: **stateful hot reload on web is now the default**. You no longer lose your navigation stack, form inputs, or scroll position when you hot reload. It brings web development to parity with the native mobile experience Flutter developers have enjoyed for years — a genuinely different day-to-day feel.

## Security: Android screen-share protection

On Android, developers can now **protect sensitive content when users share their screen** — hiding customer information, account numbers, and other private data from screen recordings and casts. For fintech, healthcare, and banking apps, this is a feature that previously required native platform code and now ships in the framework.

## What to do with this release

- **Schedule the UIScene migration** if you ship to iOS. It is required for future compatibility.
- **Adopt `RSuperellipse`** for cards, buttons, and sheets on iOS to match native corner geometry.
- **Re-test your web build** with the new hot reload default — the workflow improvement is significant enough to change how you develop.
- **Add screen-share protection** to any screen that shows sensitive data on Android.

## The bottom line

Flutter 3.44 is a "catch up to the platforms and polish the edges" release, and that is exactly what mature cross-platform frameworks should ship. Full iOS 26 and macOS 26 support keeps you current with Apple; Squircles and screen protection close native gaps; and stateful web hot reload quietly makes Flutter Web a much nicer place to work. If you have been putting off an upgrade, 3.44 is worth the afternoon.
