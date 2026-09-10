---
title: "Public release windows: PR Flutter của bạn lên stable khi nào"
description: "Flutter 3.41 công bố branch cutoff để contributor biết stable nào chứa change của mình."
seoDescription: "Flutter public release windows 2026 branch cutoff 3.41 3.44 3.47 3.50 lịch stable."
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

Lập kế hoạch open-source từng mập mờ. Flutter giờ công bố **release windows** — branch cutoff date bảo đảm inclusion vào stable kế tiếp.

![Sơ đồ: Public Release Windows](/blog/images/flutter-public-release-windows.svg)


## Lịch stable 2026 (công bố cùng 3.41)

| Release | Mốc | Branch cutoff |
| --- | --- | --- |
| 3.41 | Tháng 2 | 06/01 |
| 3.44 | Tháng 5 | 07/04 |
| 3.47 | Tháng 8 | 07/07 |
| 3.50 | Tháng 11 | 06/10 |

Merge trước cutoff → có mặt trong stable đó. Merge sau → chuyến sau.

## Team dùng thế nào

- Plugin author: align breaking change với cutoff, không phải cuối sprint.
- App team: lên lịch upgrade sau mỗi stable + một tuần bake.
- Contributor: ghi target release trong mô tả PR.

## Cạm bẫy

- Cutoff không phải “đóng băng vĩnh viễn” — cherry-pick vẫn có, nhưng đừng dựa vào.
- Feature beta/main có thể trượt; đọc release notes mỗi lần.
