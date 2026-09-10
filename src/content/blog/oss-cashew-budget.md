---
title: "Cashew: finance UI that stays local"
description: "Charts, budgets, and local persistence patterns for a Flutter finance app."
seoDescription: "Cashew budget Flutter architecture: charts, local database, budgeting UI patterns offline."
keywords:
  - cashew flutter
  - flutter budget app
  - flutter finance charts
  - flutter local database finance
  - open source budget app
tags: ["Flutter", "OpenSource", "Finance"]
sources:
  - name: "Cashew GitHub"
    url: "https://github.com/guysmiley7/cashew"
related:
  - slug: "oss-lotti-journal"
    title: "Lotti Journal"
  - slug: "oss-bloc-architecture"
    title: "Bloc Architecture"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "💸"
draft: false
---

Budget apps fail on trust and clarity. Cashew-style products keep data local, show honest charts, and make month boundaries explicit.

![Diagram: Cashew Budget](/blog/images/oss-cashew-budget.svg)



## Lessons

1. Money is integers/minor units — never raw doubles for storage.
2. Recurring transactions need a rule engine, not copied rows.
3. Chart libraries need dark mode and accessibility tables.

## Pitfalls

Timezone and locale break “this month” logic. Export CSV early so users feel ownership.

Useful when building any **local-first personal data** app with charts.
