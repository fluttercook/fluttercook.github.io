---
title: "Public release windows: when your Flutter PR ships to stable"
description: "Flutter 3.41 publishes branch cutoff dates so contributors know which stable train their change boards."
seoDescription: "Flutter public release windows 2026 branch cutoff dates 3.41 3.44 3.47 3.50 stable schedule."
keywords:
  - flutter release windows
  - flutter branch cutoff
  - flutter stable schedule 2026
  - flutter 3.50 november
  - when does pr land flutter
tags: ["Flutter", "Releases", "OSS", "Planning"]
sources:
  - name: "What's new in Flutter 3.41"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"
  - name: "Release notes"
    url: "https://docs.flutter.dev/release/release-notes"
related:
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
  - slug: "flutter-agent-skills-mcp"
    title: "Agent Skills and MCP"
category: "Deep Dive"
topic: "Process"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🗓️"
draft: false
---

Open-source planning used to be fuzzy. Flutter now publishes **release windows** — branch cutoff dates that guarantee inclusion in the next stable.

![Diagram: Public Release Windows](/blog/images/flutter-public-release-windows.svg)


## 2026 stable train (as announced with 3.41)

| Release | Target | Branch cutoff |
| --- | --- | --- |
| 3.41 | February | 06 January |
| 3.44 | May | 07 April |
| 3.47 | August | 07 July |
| 3.50 | November | 06 October |

Merge before cutoff → ships in that stable. Merge after → next train.

## How teams should use this

- Plugin authors: align breaking changes with cutoffs, not with your sprint end.
- App teams: schedule upgrades after each stable + a bake week.
- Contributors: say the target release in the PR description.

## Pitfalls

- Cutoff is not “code freeze forever” — cherry-picks still exist, but do not plan on them.
- Beta/main features can slip; read the release notes each time.
