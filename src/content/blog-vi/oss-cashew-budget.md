---
title: "Cashew: UI tài chính giữ dữ liệu local"
description: "Chart, ngân sách và pattern lưu local cho app tài chính Flutter."
seoDescription: "Cashew kiến trúc ngân sách Flutter: chart, database local, pattern UI budget offline."
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

App budget fail ở niềm tin và sự rõ ràng. Sản phẩm kiểu Cashew giữ data local, chart trung thực và mốc tháng tường minh.

![Sơ đồ: Cashew Budget](/blog/images/oss-cashew-budget.svg)



## Bài học

1. Tiền là integer/đơn vị nhỏ — không lưu double thô.
2. Giao dịch định kỳ cần rule engine, không phải copy row.
3. Chart cần dark mode và bảng accessibility.

## Cạm bẫy

Timezone và locale phá logic “tháng này”. Export CSV sớm để user cảm thấy sở hữu dữ liệu.

Hữu ích khi xây app **dữ liệu cá nhân local-first** có chart.
