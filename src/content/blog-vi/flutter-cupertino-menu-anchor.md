---
title: "CupertinoMenuAnchor và menu Flutter hiện đại"
description: "RawMenuAnchor cấp nguồn cho CupertinoMenuAnchor và MenuAnchor Material có animation — menu tự nhiên không cần plugin."
seoDescription: "Flutter CupertinoMenuAnchor RawMenuAnchor, Material MenuAnchor hoverOpenDelay, menu iOS tự nhiên trong Flutter 3.44."
keywords:
  - flutter cupertino menu anchor
  - RawMenuAnchor
  - flutter ios context menu
  - MenuAnchor animation material
  - flutter submenu hoverOpenDelay
tags: ["Flutter", "Cupertino", "Material", "Menus"]
sources:
  - name: "What's new in Flutter 3.44"
    url: "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"
  - name: "CupertinoMenuAnchor API"
    url: "https://api.flutter.dev/flutter/cupertino/CupertinoMenuAnchor-class.html"
  - name: "MenuAnchor API"
    url: "https://api.flutter.dev/flutter/material/MenuAnchor-class.html"
related:
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
  - slug: "flutter-widget-previews-stable"
    title: "Widget Previews Stable"
category: "Deep Dive"
topic: "UI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "📋"
draft: false
---

Menu là nơi app Flutter hay “mở web” nhất. **RawMenuAnchor** là primitive chung; Cupertino và Material đều xây trên đó.

![Sơ đồ: Cupertino Menu Anchor](/blog/images/flutter-cupertino-menu-anchor.svg)


## Cupertino

`CupertinoMenuAnchor` (community dẫn dắt, nổi bật davidhicks980) cho app iOS menu đúng kiểu UIKit: dismiss physics, nesting và focus khớp kỳ vọng nền tảng.

## Material

`MenuAnchor` có animation Material 3 tùy chọn (`animated: true`) và `SubmenuButton.hoverOpenDelay` cho hover desktop.

## Bảng quyết định

| Mục tiêu | Ưu tiên |
| --- | --- |
| Sản phẩm iOS-first | CupertinoMenuAnchor |
| UI dày đặc desktop | MenuAnchor + hoverOpenDelay |
| Brand đa nền tảng | Wrapper adaptive chọn theo platform |

## Cạm bẫy

- Thứ tự callback close của RawMenuAnchor đã đổi — đọc breaking change trước khi upgrade.
- Đừng rebuild cả cây menu mỗi pointer event; giữ anchor ổn định.
