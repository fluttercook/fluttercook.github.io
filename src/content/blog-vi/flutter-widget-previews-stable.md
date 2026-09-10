---
title: "Widget Previews đã stable: sửa UI không cần chạy cả app"
description: "Flutter 3.47 đưa Widget Previewer lên stable: khởi động nhanh, ma trận theme, đồng bộ asset web."
seoDescription: "Flutter Widget Previews stable 3.47, PreviewThemeData, widget previewer khởi động nhanh, lặp UI cách ly."
keywords:
  - flutter widget previews
  - flutter widget previewer
  - PreviewThemeData
  - flutter ui preview stable
  - isolated widget preview
tags: ["Flutter", "DevTools", "WidgetPreview", "DX"]
sources:
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Widget Previewer docs"
    url: "https://docs.flutter.dev/tools/widget-previewer"
related:
  - slug: "flutter-standalone-material-ui-cupertino-ui"
    title: "Standalone Material UI and Cupertino UI"
  - slug: "flutter-agentic-hot-reload"
    title: "Agentic Hot Reload"
category: "Deep Dive"
topic: "Tooling"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🔍"
draft: false
---

Chạy cả app chỉ để sửa một nút rất chậm. **Widget Preview** render widget riêng lẻ cách ly. Sau các bản experimental, nó **stable trong Flutter 3.47**.

![Sơ đồ: Widget Previews Stable](/blog/images/flutter-widget-previews-stable.svg)


## Stable nghĩa là gì

- Khởi động nhanh nhờ cache local `.widget_preview/`.
- `PreviewThemeData` để layer theme tuần tự (ma trận test theo seed/contrast).
- Tự đồng bộ asset `web/` khi preview widget web.

## Workflow đáng tiền

1. Tách widget đang sửa thành class preview được.
2. Thêm preview cho mặc định / dark / chữ to / data rỗng.
3. Lặp tới khi preview nhàm chán — rồi mới ghép vào app.

Đây cũng là vòng nhanh nhất cho design-system trên `material_ui` / catalog tùy chỉnh.

## Cạm bẫy

- Preview đụng `dart:io` hoặc platform channel sẽ không chạy — giữ UI thuần.
- Đừng nhét business logic vào preview; chỉ fixture.
