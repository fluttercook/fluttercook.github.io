---
title: "Lotti: journaling with audio, habits, and a serious local DB"
description: "Complex local data models in Flutter — beyond todo-app tutorials."
seoDescription: "Lotti journal Flutter architecture: local database, audio notes, habit tracking, complex offline app."
keywords:
  - lotti flutter
  - flutter journaling app
  - flutter local database complex
  - flutter audio notes
  - offline first journal
tags: ["Flutter", "OpenSource", "Productivity"]
sources:
  - name: "Lotti GitHub"
    url: "https://github.com/lotti/lotti"
related:
  - slug: "oss-saber-notes"
    title: "Saber Notes"
  - slug: "oss-cashew-budget"
    title: "Cashew Budget"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📔"
draft: false
---

Most Flutter tutorials stop at CRUD. Lotti is interesting because journaling forces multi-modal entries (text, audio, habits, measurements) and long-term local storage.

![Diagram: Lotti Journal](/blog/images/oss-lotti-journal.svg)



## Lessons

1. Entry type hierarchies beat one giant nullable row.
2. Audio capture + playback is a platform surface, not a widget.
3. Insights need indexes — design queries before charts.

## Pitfalls

Migrations on personal data are sacred; write them carefully. Background recording permissions vary by OS.

Look at Lotti when your “simple notes app” is no longer simple.
