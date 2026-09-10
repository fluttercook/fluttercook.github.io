#!/usr/bin/env python3
"""Generate EN+VI blog posts for the 2026 OSS + Flutter feature batch.

Writes:
  src/content/blog/<slug>.md
  src/content/blog-vi/<slug>.md
"""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EN = ROOT / "src" / "content" / "blog"
VI = ROOT / "src" / "content" / "blog-vi"
DATE = "2026-09-10"
AUTHOR = "Trung Hieu"

# ---------------------------------------------------------------------------
# Shared article shells
# ---------------------------------------------------------------------------

FEATURES = [
    {
        "slug": "flutter-standalone-material-ui-cupertino-ui",
        "emoji": "🧱",
        "category": "Deep Dive",
        "topic": "Framework",
        "level": "Intermediate",
        "tags": ["Flutter", "Material", "Cupertino", "Packages", "Migration"],
        "title_en": "Standalone material_ui and cupertino_ui: what the 1.0 split changes",
        "title_vi": "material_ui và cupertino_ui độc lập: thay đổi gì ở bản 1.0",
        "desc_en": "Flutter 3.47 ships opt-in standalone design packages. Here is why the split exists, how to migrate with dart fix, and how the compatibility bridge keeps mixed dependencies building.",
        "desc_vi": "Flutter 3.47 tung package design độc lập dạng opt-in. Vì sao cần tách, cách migrate bằng dart fix, và compatibility bridge giữ dependency cũ build được.",
        "seo_en": "Migrate Flutter to standalone material_ui and cupertino_ui packages in 3.47: dart fix code, compatibility bridge, and weekly design releases.",
        "seo_vi": "Cách migrate Flutter sang package material_ui và cupertino_ui độc lập trong 3.47: dart fix, compatibility bridge, và release design hàng tuần.",
        "keywords": [
            "flutter material_ui package",
            "cupertino_ui 1.0",
            "flutter decouple material",
            "migrate design widgets flutter",
            "MaterialUiCompatibilityBridge",
            "flutter 3.47 material",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("material_ui on pub.dev", "https://pub.dev/packages/material_ui"),
            ("cupertino_ui on pub.dev", "https://pub.dev/packages/cupertino_ui"),
            ("Tracking issue: decouple Material/Cupertino", "https://github.com/flutter/flutter/issues/172932"),
        ],
        "related": ["flutter-cupertino-menu-anchor", "flutter-impeller-default-desktop"],
        "body_en": """Material and Cupertino used to be frozen inside the core SDK. That made design updates wait on the quarterly Flutter release train. In Flutter 3.47 both libraries reach **1.0 as standalone packages** on pub.dev: `material_ui` and `cupertino_ui`.

You still get the SDK copies this release. The packages are **opt-in**. That is deliberate — the team froze contributions in April so the migration path could be boring.

## Why the split matters in 2026

Three concrete outcomes:

1. **Weekly design releases.** Bugfixes and new components no longer wait for `flutter upgrade`.
2. **Independent upgrades.** An app pinned to an older SDK can still take the latest look and feel.
3. **Style-neutral core.** A leaner foundation for custom design systems (and for Liquid Glass / M3 Expressive-style shocks from platform vendors).

## Migrate with dart fix

```bash
flutter pub add material_ui
# if you use Cupertino:
flutter pub add cupertino_ui

dart fix --apply --code=migrate_design_widgets
```

The fix rewrites imports from `package:flutter/material.dart` / `cupertino.dart` to the standalone packages. If `pubspec.yaml` is not updated automatically (an early known bug), add the deps by hand and run `dart fix --apply` again.

## Bridge while dependencies catch up

Not every package you depend on will migrate on day one. Wrap the app:

```dart
import 'package:material_ui/material_ui.dart';

MaterialApp(
  builder: (context, child) => MaterialUiCompatibilityBridge(child: child!),
  home: const HomeScreen(),
);
```

Localization unbundles with the same move — Material/Cupertino delegates now live in the packages, and `GlobalMaterialLocalizations.delegates` includes the Cupertino and Widgets delegates.

## Pitfalls

- Treat this as a **major release** if you publish packages.
- Core SDK copies are scheduled for formal deprecation in the **November** stable.
- Run widget tests after import rewrites; theme APIs are the same, but library URIs are not.
""",
        "body_vi": """Material và Cupertino từng bị “đóng băng” bên trong core SDK. Mọi cập nhật design phải đợi nhịp release quarterly của Flutter. Ở Flutter 3.47, cả hai thư viện đạt **1.0 dạng package độc lập** trên pub.dev: `material_ui` và `cupertino_ui`.

Bản trong SDK vẫn còn ở release này. Package là **opt-in**. Đó là chủ đích — team đóng contribution từ tháng 4 để đường migrate nhàm chán nhất có thể.

## Vì sao cần tách trong năm 2026

1. **Release design hàng tuần.** Bugfix và component mới không còn chờ `flutter upgrade`.
2. **Upgrade độc lập.** App ghim SDK cũ vẫn update được look-and-feel mới.
3. **Core trung lập style.** Nền tảng gọn hơn cho design system riêng (và cú sốc Liquid Glass / M3 Expressive từ vendor).

## Migrate bằng dart fix

```bash
flutter pub add material_ui
# nếu dùng Cupertino:
flutter pub add cupertino_ui

dart fix --apply --code=migrate_design_widgets
```

Lệnh này rewrite import từ `package:flutter/material.dart` / `cupertino.dart` sang package mới. Nếu `pubspec.yaml` không tự đổi (bug sớm đã biết), thêm dependency thủ công rồi chạy lại `dart fix --apply`.

## Bridge khi dependency chưa kịp migrate

```dart
import 'package:material_ui/material_ui.dart';

MaterialApp(
  builder: (context, child) => MaterialUiCompatibilityBridge(child: child!),
  home: const HomeScreen(),
);
```

Localization cũng được tách — delegate Material/Cupertino giờ nằm trong package, và `GlobalMaterialLocalizations.delegates` đã gồm cả Cupertino lẫn Widgets.

## Cạm bẫy

- Coi đây là **major release** nếu bạn publish package.
- Bản trong SDK sẽ bị formal deprecation ở stable **tháng 11**.
- Chạy lại widget test sau khi rewrite import; API theme giống nhau nhưng URI thư viện thì không.
""",
    },
    {
        "slug": "flutter-impeller-default-desktop",
        "emoji": "🎨",
        "category": "Deep Dive",
        "topic": "Performance",
        "level": "Intermediate",
        "tags": ["Flutter", "Impeller", "Desktop", "Rendering", "Performance"],
        "title_en": "Impeller is now the default desktop renderer — what actually changes",
        "title_vi": "Impeller thành renderer desktop mặc định — thực sự đổi gì",
        "desc_en": "Flutter 3.47 turns Impeller on by default for macOS, Windows, and Linux. Shader jank dies; SDF text sharpens; Skia opt-outs are temporary.",
        "desc_vi": "Flutter 3.47 bật Impeller mặc định trên macOS, Windows, Linux. Jank shader biến mất; chữ SDF sắc hơn; opt-out Skia chỉ là tạm thời.",
        "seo_en": "Flutter 3.47 Impeller default on desktop: Metal and Vulkan, SDF text, how to opt out on macOS Windows Linux, and migration notes.",
        "seo_vi": "Flutter 3.47 Impeller mặc định desktop: Metal và Vulkan, chữ SDF, cách opt-out trên macOS Windows Linux và ghi chú migrate.",
        "keywords": [
            "flutter impeller desktop",
            "impeller windows linux macos default",
            "flutter 3.47 impeller",
            "sdf text flutter desktop",
            "disable impeller desktop",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("Impeller docs", "https://docs.flutter.dev/perf/impeller"),
        ],
        "related": ["flutter-impeller-jank-profiling", "flutter-fragment-shader-api"],
        "body_en": """Mobile Impeller defaults landed earlier. Flutter 3.47 finishes the job on **macOS, Windows, and Linux**. Desktop apps now target Metal (macOS) and Vulkan (Windows/Linux) with a fixed shader set compiled at engine-build time.

## What you gain

- **No shader-compilation jank** on first run of an animation.
- **Signed Distance Function text** — sharper glyphs on lower-density desktop displays.
- **Wide Gamut Color on by default on macOS** where hardware supports it.

## Temporary Skia opt-outs

If a regression blocks you:

| Platform | Opt-out |
| --- | --- |
| macOS | `FLTEnableImpeller=false` in `Info.plist` |
| Windows | `project.set_impeller_switch(flutter::ImpellerSwitch::Disabled)` in `main.cpp` |
| Linux | `fl_dart_project_set_enable_impeller(project, FALSE)` in `my_application.cc` |

File a bug. Fallbacks are scheduled for removal.

## What to retest

1. Custom `FragmentShader`s and `saveLayer`-heavy effects.
2. Platform views and external textures.
3. Print/export paths that assumed Skia color management.

Profile mode first. If a frame is still long, the split is still UI vs raster — Impeller moved work off the *shader compile* path, not off your `build()` method.
""",
        "body_vi": """Impeller mặc định trên mobile đã có từ trước. Flutter 3.47 hoàn tất trên **macOS, Windows và Linux**. App desktop giờ nhắm Metal (macOS) và Vulkan (Windows/Linux) với tập shader cố định, compile lúc build engine.

## Bạn được gì

- **Hết jank compile shader** khi animation chạy lần đầu.
- **Chữ SDF** — glyph sắc hơn trên màn desktop mật độ pixel thấp hơn.
- **Wide Gamut Color mặc định trên macOS** khi phần cứng hỗ trợ.

## Opt-out Skia tạm thời

| Nền tảng | Cách tắt |
| --- | --- |
| macOS | `FLTEnableImpeller=false` trong `Info.plist` |
| Windows | `project.set_impeller_switch(flutter::ImpellerSwitch::Disabled)` trong `main.cpp` |
| Linux | `fl_dart_project_set_enable_impeller(project, FALSE)` trong `my_application.cc` |

Hãy file bug. Fallback sẽ bị gỡ.

## Nên test lại

1. `FragmentShader` tùy chỉnh và effect nặng `saveLayer`.
2. Platform view / external texture.
3. Luồng print/export từng giả định color management của Skia.

Chạy profile mode trước. Frame vẫn dài thì vẫn là UI vs raster — Impeller chỉ lấy việc ở nhánh *compile shader*, không lấy việc trong `build()` của bạn.
""",
    },
    {
        "slug": "flutter-swift-package-manager-default",
        "emoji": "📦",
        "category": "Deep Dive",
        "topic": "Platform",
        "level": "Intermediate",
        "tags": ["Flutter", "iOS", "macOS", "SwiftPM", "CocoaPods"],
        "title_en": "Swift Package Manager is the iOS/macOS default — leave CocoaPods behind",
        "title_vi": "Swift Package Manager là mặc định iOS/macOS — rời CocoaPods",
        "desc_en": "From Flutter 3.44, SwiftPM replaces CocoaPods for new iOS and macOS builds. How the CLI migrates you, what plugin authors must ship, and how to opt out briefly.",
        "desc_vi": "Từ Flutter 3.44, SwiftPM thay CocoaPods cho build iOS/macOS mới. CLI migrate thế nào, plugin author cần ship gì, và cách opt-out tạm.",
        "seo_en": "Flutter Swift Package Manager default 3.44: migrate from CocoaPods, plugin Package.swift FlutterFramework, and temporary opt-out flag.",
        "seo_vi": "Flutter Swift Package Manager mặc định 3.44: migrate từ CocoaPods, plugin Package.swift FlutterFramework, và cờ opt-out tạm.",
        "keywords": [
            "flutter swift package manager",
            "flutter cocoa pods migration",
            "swiftpm flutter default",
            "flutter plugin Package.swift",
            "disable swift package manager flutter",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("SwiftPM for app developers", "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers"),
            ("SwiftPM for plugin authors", "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-plugin-authors"),
            ("Goodbye CocoaPods post", "https://blog.flutter.dev/saying-goodbye-to-cocoapods-swift-package-manager-is-soon-the-default-in-flutter-645a92714a57"),
        ],
        "related": ["flutter-uiscene-ios-lifecycle", "flutter-content-sized-views"],
        "body_en": """CocoaPods is in maintenance mode. Flutter 3.44 makes **Swift Package Manager the default** for iOS and macOS dependency resolution. The CLI migrates the Xcode project on the next `flutter run` / `flutter build`.

## What app developers see

- No Ruby/CocoaPods install required for the happy path.
- Add-to-App gains `flutter build swift-package` to emit a Swift Package for native hosts.
- Plugins that still require CocoaPods trigger a CLI warning and temporary fallback.

## What plugin authors must ship

If you maintain an iOS/macOS plugin:

1. Add a `Package.swift`.
2. Depend on `FlutterFramework` if you migrated in the 2024 pilot.
3. Raise the minimum Flutter constraint to **3.44** when you switch.

Unmigrated plugins score lower on pub.dev and will eventually stop resolving.

## Temporary opt-out

```yaml
# pubspec.yaml
flutter:
  # temporary escape hatch — file a bug if you need it
  enable-swift-package-manager: false
```

Or pass `--no-enable-swift-package-manager` on the command line. Opt-outs will be removed; open an issue with your Xcode project if SwiftPM breaks a real integration.

## Checklist before you delete Podfile

- [ ] `flutter clean` then a full iOS build
- [ ] CI runners no longer install CocoaPods for this app
- [ ] Every plugin in the tree resolves under SwiftPM (or is replaced)
- [ ] Code signing and entitlements still apply
""",
        "body_vi": """CocoaPods đang ở chế độ maintenance. Flutter 3.44 đặt **Swift Package Manager làm mặc định** cho dependency iOS và macOS. CLI migrate Xcode project ở lần `flutter run` / `flutter build` kế tiếp.

## App developer thấy gì

- Happy path không cần cài Ruby/CocoaPods.
- Add-to-App có `flutter build swift-package` để đóng gói module thành Swift Package.
- Plugin còn bắt buộc CocoaPods sẽ bị CLI cảnh báo và fallback tạm.

## Plugin author cần ship gì

1. Thêm `Package.swift`.
2. Depend `FlutterFramework` nếu đã migrate pilot 2024.
3. Nâng constraint Flutter tối thiểu lên **3.44** khi chuyển.

Plugin chưa migrate bị trừ điểm pub.dev và sẽ không resolve được nữa.

## Opt-out tạm

```yaml
# pubspec.yaml
flutter:
  enable-swift-package-manager: false
```

Hoặc `--no-enable-swift-package-manager` trên CLI. Opt-out sẽ bị gỡ; mở issue kèm Xcode project nếu SwiftPM làm hỏng tích hợp thật.

## Checklist trước khi xóa Podfile

- [ ] `flutter clean` rồi build iOS đầy đủ
- [ ] CI không còn cài CocoaPods cho app này
- [ ] Mọi plugin trong tree resolve bằng SwiftPM (hoặc đã thay)
- [ ] Code signing và entitlement vẫn đúng
""",
    },
    {
        "slug": "flutter-hybrid-composition-plus-plus",
        "emoji": "🖼️",
        "category": "Deep Dive",
        "topic": "Android",
        "level": "Advanced",
        "tags": ["Flutter", "Android", "PlatformViews", "Vulkan", "Performance"],
        "title_en": "Hybrid Composition++: fixing Android platform views without the jank",
        "title_vi": "Hybrid Composition++: sửa platform view Android hết jank",
        "desc_en": "Flutter 3.44 introduces HCPP — OS-level compositing via Vulkan SurfaceControl for WebView, maps, and other native Android views.",
        "desc_vi": "Flutter 3.44 giới thiệu HCPP — compositing cấp OS qua Vulkan SurfaceControl cho WebView, map và native view Android.",
        "seo_en": "Flutter Hybrid Composition++ HCPP enable flag, SurfaceControl Vulkan platform views, better scrolling and SurfaceView support.",
        "seo_vi": "Flutter Hybrid Composition++ HCPP bật cờ, SurfaceControl Vulkan platform view, scroll mượt hơn và hỗ trợ SurfaceView.",
        "keywords": [
            "flutter hybrid composition++",
            "flutter HCPP enable",
            "flutter platform views android",
            "EnableHcpp",
            "flutter surfaceview webview",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("Platform views docs", "https://docs.flutter.dev/platform-integration/android/platform-views"),
        ],
        "related": ["flutter-impeller-default-desktop", "flutter-content-sized-views"],
        "body_en": """Embedding a WebView or Google Map used to force a tradeoff: Virtual Display (tearing, input quirks) or Hybrid Composition (higher CPU). **Hybrid Composition++ (HCPP)** lets Android own layer compositing through Vulkan hardware-buffer swapchains and `SurfaceControl` transactions, synchronized with the Flutter frame.

## Enable HCPP

```xml
<meta-data
    android:name="io.flutter.embedding.android.EnableHcpp"
    android:value="true" />
```

Or run with `--enable-hcpp`. There is **no new Dart API** — existing platform views upgrade.

## Requirements and limits

- API level and hardware support gates apply; not every device can use HCPP even when opted in.
- `SurfaceView`-based content becomes realistic, which older modes struggled with.
- Expect this to become the default rendering mode later — validate your maps/WebView product flows now.

## What to measure

1. Scroll FPS inside a `WebView` or map, not only the Flutter list around it.
2. Touch accuracy near the edges of the embedded view.
3. Keyboard show/hide over the platform view.

If you still see tearing, confirm the flag is applied in the **built** manifest (flavors can overwrite it) and that you are not on a device below the support floor.
""",
        "body_vi": """Nhúng WebView hoặc Google Map từng là đánh đổi: Virtual Display (rét hình, input lạ) hoặc Hybrid Composition (CPU cao hơn). **Hybrid Composition++ (HCPP)** để Android tự compositing layer qua Vulkan hardware-buffer swapchain và `SurfaceControl` transaction, đồng bộ với frame Flutter.

## Bật HCPP

```xml
<meta-data
    android:name="io.flutter.embedding.android.EnableHcpp"
    android:value="true" />
```

Hoặc chạy `--enable-hcpp`. **Không có API Dart mới** — platform view hiện có được nâng cấp.

## Yêu cầu và giới hạn

- Bị chặn bởi API level và phần cứng; không phải máy nào cũng dùng được dù đã opt-in.
- Nội dung `SurfaceView` trở nên khả thi — mode cũ rất khó.
- Sẽ thành mặc định sau này — hãy validate luồng map/WebView sản phẩm ngay.

## Đo gì

1. FPS scroll bên trong `WebView`/map, không chỉ list Flutter quanh nó.
2. Độ chính xác chạm gần mép view nhúng.
3. Bàn phím show/hide đè lên platform view.

Nếu vẫn rét hình, kiểm tra cờ có trong manifest **đã build** (flavor có thể ghi đè) và máy không nằm dưới ngưỡng hỗ trợ.
""",
    },
    {
        "slug": "flutter-agentic-hot-reload",
        "emoji": "🤖",
        "category": "Deep Dive",
        "topic": "AI Tooling",
        "level": "Intermediate",
        "tags": ["Flutter", "AI", "MCP", "HotReload", "Agents"],
        "title_en": "Agentic Hot Reload: when your coding agent reloads the running app",
        "title_vi": "Agentic Hot Reload: khi coding agent tự reload app đang chạy",
        "desc_en": "Flutter 3.44 lets MCP-aware agents discover running apps and trigger hot reload — closing the loop from prompt to pixels.",
        "desc_vi": "Flutter 3.44 cho agent biết MCP tìm app đang chạy và trigger hot reload — khép kín vòng từ prompt tới pixel.",
        "seo_en": "Flutter Agentic Hot Reload MCP server, coding agents auto connect and hot reload running apps, Antigravity Gemini CLI Claude Code.",
        "seo_vi": "Flutter Agentic Hot Reload MCP server, coding agent tự kết nối và hot reload app đang chạy.",
        "keywords": [
            "flutter agentic hot reload",
            "flutter mcp server",
            "ai coding agent flutter",
            "hot reload ai agent",
            "dart mcp hot reload",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("Dart & Flutter MCP server", "https://docs.flutter.dev/ai/mcp-server"),
        ],
        "related": ["flutter-agent-skills-mcp", "flutter-genui-a2ui"],
        "body_en": """The old AI loop was: paste error → agent edits file → you manually `r` in the terminal. **Agentic Hot Reload** removes the last step. The Dart/Flutter MCP server helps agents find and connect to a running app, then trigger reload after an edit.

## The new loop

1. `flutter run` (debug) with the MCP server available to your agent.
2. Prompt: “make the login button cyan and larger.”
3. Agent edits Dart, triggers reload, you judge the pixels.

No extra glue scripts. Dependency search is hardened so agents can read package sources without full pub-cache access, and tool definitions were consolidated to cut token cost.

## Practical setup tips

- Keep one debug session per device you care about; agents attach to what is running.
- Prefer small UI-scoped prompts — Agentic Hot Reload rewards incremental diffs.
- Pair with Agent Skills so the agent follows your architecture instead of inventing a new one.

## Limits

Hot reload is not hot *restart*. State and native-channel changes still need a restart. If the agent’s change does not appear, check that the session is still connected and that the edit was in a reloadable library (not `main()` reordering that requires restart).
""",
        "body_vi": """Vòng AI cũ: dán lỗi → agent sửa file → bạn tự bấm `r` trong terminal. **Agentic Hot Reload** bỏ bước cuối. Dart/Flutter MCP server giúp agent tìm và kết nối app đang chạy, rồi trigger reload sau khi sửa.

## Vòng mới

1. `flutter run` (debug) với MCP server sẵn cho agent.
2. Prompt: “làm nút login màu cyan và to hơn.”
3. Agent sửa Dart, trigger reload, bạn nhìn pixel.

Không cần script keo dán. Dependency search được siết để agent đọc source package không cần full pub-cache; tool definition được gộp để giảm token.

## Mẹo setup

- Một debug session cho mỗi device bạn quan tâm; agent attach vào session đang chạy.
- Prompt nhỏ theo scope UI — Agentic Hot Reload thưởng cho diff nhỏ.
- Ghép Agent Skills để agent theo kiến trúc của bạn thay vì bịa mới.

## Giới hạn

Hot reload không phải hot *restart*. State và native channel vẫn cần restart. Nếu đổi không hiện, kiểm tra session còn kết nối và edit nằm trong library reloadable (không phải rearrange `main()` bắt buộc restart).
""",
    },
    {
        "slug": "flutter-agent-skills-mcp",
        "emoji": "🧰",
        "category": "Deep Dive",
        "topic": "AI Tooling",
        "level": "Intermediate",
        "tags": ["Flutter", "Dart", "AI", "MCP", "Skills"],
        "title_en": "Dart and Flutter Agent Skills: cheaper, better agent workflows",
        "title_vi": "Agent Skills cho Dart và Flutter: workflow agent rẻ và chuẩn hơn",
        "desc_en": "Official skills give coding agents production-grade steps for localization, integration tests, and more — with leaner MCP tools.",
        "desc_vi": "Skill chính thức cung cấp bước production-grade cho agent: localization, integration test… kèm MCP tools gọn hơn.",
        "seo_en": "Flutter Agent Skills for coding agents, package skills, MCP tool consolidation, save tokens while following Flutter best practices.",
        "seo_vi": "Flutter Agent Skills cho coding agent, package skills, MCP tools gọn, tiết kiệm token theo best practice Flutter.",
        "keywords": [
            "flutter agent skills",
            "dart agent skills",
            "flutter mcp tools",
            "ai skills flutter localization",
            "coding agent flutter best practices",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("Introducing skills for Dart and Flutter", "https://blog.flutter.dev/introducing-skills-for-dart-and-flutter-23837c6ec0ae"),
            ("Package skills", "https://dart.dev/tools/pub/package-skills"),
        ],
        "related": ["flutter-agentic-hot-reload", "flutter-genui-a2ui"],
        "body_en": """Agents are good at typing and bad at taste. **Agent Skills** encode Flutter/Dart taste as short, task-oriented instructions your agent can load: how to add integration tests, how to set up localization, how to structure a feature.

## Why skills beat a giant system prompt

- **Scoped.** Load only what the task needs.
- **Versioned with the ecosystem.** Skills ship alongside packages and docs.
- **Token-cheap.** The MCP tool surface was also consolidated so the agent spends budget on your code, not on boilerplate tool schemas.

## How to use them day to day

1. Install/configure the Dart & Flutter MCP server for your agent (Claude Code, Gemini CLI, Cursor, etc.).
2. Prefer invoking an official skill over free-form “write me a login screen.”
3. Keep project-local skills for house rules (folder layout, Riverpod conventions, test style).

## Package skills

Pub packages can ship their own skills so an agent knows *this* package’s idioms, not generic Flutter. If you maintain a popular plugin, a skill is becoming part of a good developer experience — and it reduces hallucinated APIs.

## Anti-patterns

- Asking one prompt to redesign architecture, add features, and write tests. Split it.
- Disabling the skill layer to “save tokens” then paying for three wrong rewrites.
""",
        "body_vi": """Agent giỏi gõ phím nhưng kém gu. **Agent Skills** mã hóa gu Flutter/Dart thành hướng dẫn ngắn theo task mà agent load được: cách thêm integration test, setup localization, cấu trúc feature.

## Vì sao skill thắng system prompt khổng lồ

- **Theo scope.** Chỉ load việc đang cần.
- **Version cùng hệ sinh thái.** Skill ship kèm package và docs.
- **Rẻ token.** Mặt phẳng tool MCP cũng được gộp để agent dành budget cho code của bạn.

## Dùng hàng ngày

1. Cài/cấu hình Dart & Flutter MCP server cho agent (Claude Code, Gemini CLI, Cursor…).
2. Ưu tiên invoke skill chính thức hơn prompt tự do “viết màn login”.
3. Giữ skill local cho luật nhà (folder layout, convention Riverpod, style test).

## Package skills

Pub package có thể ship skill riêng để agent biết idioms *của package đó*, không phải Flutter chung chung. Nếu bạn maintain plugin phổ biến, skill đang thành một phần DX tốt — và giảm API bị bịa.

## Anti-pattern

- Một prompt vừa redesign kiến trúc, vừa add feature, vừa viết test. Hãy tách.
- Tắt skill để “tiết kiệm token” rồi trả giá bằng ba lần viết sai.
""",
    },
    {
        "slug": "flutter-genui-a2ui",
        "emoji": "✨",
        "category": "Deep Dive",
        "topic": "AI",
        "level": "Advanced",
        "tags": ["Flutter", "GenUI", "A2UI", "AI", "UX"],
        "title_en": "GenUI and A2UI: agents that compose widgets, not markdown",
        "title_vi": "GenUI và A2UI: agent ghép widget, không chỉ markdown",
        "desc_en": "The GenUI SDK and A2UI protocol let agents build live Flutter UI — a shift from chat walls of text to structured, interactive experiences.",
        "desc_vi": "GenUI SDK và giao thức A2UI cho agent dựng UI Flutter sống — khác hẳn tường chữ chat.",
        "seo_en": "Flutter GenUI SDK A2UI protocol, generative UI beyond chat, compose widgets from agent responses, Finnish It Hatcha examples.",
        "seo_vi": "Flutter GenUI SDK giao thức A2UI, generative UI vượt chat, agent ghép widget, ví dụ Finnish It Hatcha.",
        "keywords": [
            "flutter genui",
            "a2ui protocol",
            "generative ui flutter",
            "flutter ai ui agent",
            "a2ui flutter sdk",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("genui package", "https://pub.dev/packages/genui"),
            ("A2UI", "https://a2ui.org/"),
        ],
        "related": ["flutter-firebase-ai-logic", "flutter-agentic-hot-reload"],
        "body_en": """Chat UIs trained users to accept walls of markdown. **Generative UI (GenUI)** flips the contract: the model proposes *UI structure* — lists, forms, cards — and Flutter renders real widgets with real state.

## What A2UI is

[A2UI](https://a2ui.org/) is an open protocol describing how an **agent** and a **client** collaborate on UI composition and state. Flutter’s GenUI SDK implements the client side. Package downloads grew sharply through 2026 as teams shipped beyond demos (for example language-learning apps that compose lesson UI on the fly).

## Architecture sketch

1. User intent goes to your backend/agent.
2. Agent emits A2UI structure (not free text).
3. GenUI maps structure → Flutter widgets in a constrained catalog.
4. Events flow back as structured actions the agent can handle.

## Design constraints that make it work

- **Catalog over chaos.** Allow only widgets you designed; do not let the model invent layout physics.
- **Critic loop.** Validate agent output before paint (empty states, overflow, a11y labels).
- **Templates for speed.** Hybrid: strong templates + model-filled slots beats pure generation for reliability.

## Pitfalls

- Treating GenUI as a theming engine — it is a composition protocol.
- Skipping offline/error UI because “the model will fix it.”
- Shipping without human-readable fallbacks when the catalog cannot express the answer.
""",
        "body_vi": """Chat UI dạy người dùng chấp nhận tường markdown. **Generative UI (GenUI)** đảo hợp đồng: model đề xuất *cấu trúc UI* — list, form, card — và Flutter render widget thật với state thật.

## A2UI là gì

[A2UI](https://a2ui.org/) là protocol mở mô tả **agent** và **client** cùng nhau ghép UI và quản lý state. GenUI SDK của Flutter là client. Lượt tải package tăng mạnh trong 2026 khi team ship thật (ví dụ app học ngôn ngữ tự ghép UI bài học).

## Kiến thức kiến trúc

1. Intent người dùng tới backend/agent.
2. Agent emit cấu trúc A2UI (không phải text tự do).
3. GenUI map cấu trúc → widget Flutter trong catalog bị chặn.
4. Event trả về dạng action có cấu trúc agent xử lý được.

## Ràng buộc thiết kế

- **Catalog hơn hỗn loạn.** Chỉ cho phép widget bạn thiết kế; đừng để model bịa layout physics.
- **Vòng critic.** Validate output trước khi paint (empty state, overflow, nhãn a11y).
- **Template để nhanh.** Hybrid: template mạnh + slot model điền ổn định hơn generate thuần.

## Cạm bẫy

- Coi GenUI là engine theming — nó là protocol composition.
- Bỏ UI offline/error vì “model sẽ tự sửa”.
- Ship không có fallback đọc được khi catalog diễn đạt không nổi câu trả lời.
""",
    },
    {
        "slug": "flutter-firebase-ai-logic",
        "emoji": "🔥",
        "category": "Deep Dive",
        "topic": "AI",
        "level": "Intermediate",
        "tags": ["Flutter", "Firebase", "Gemini", "AI"],
        "title_en": "Firebase AI Logic in Flutter: Gemini without a custom backend",
        "title_vi": "Firebase AI Logic trong Flutter: Gemini không cần backend riêng",
        "desc_en": "Call Gemini from Flutter via firebase_ai, keep prompts on the server, and learn from production patterns like MacroFactor.",
        "desc_vi": "Gọi Gemini từ Flutter qua firebase_ai, giữ prompt trên server, học pattern production như MacroFactor.",
        "seo_en": "Flutter Firebase AI Logic firebase_ai package, Server Prompt Templates Gemini client-side, secure AI features in Flutter apps.",
        "seo_vi": "Flutter Firebase AI Logic package firebase_ai, Server Prompt Templates Gemini client-side, feature AI an toàn trong app Flutter.",
        "keywords": [
            "flutter firebase ai logic",
            "firebase_ai gemini",
            "flutter gemini api",
            "server prompt templates firebase",
            "flutter multimodal ai",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("Firebase AI Logic", "https://firebase.google.com/docs/ai-logic/get-started?platform=flutter"),
            ("MacroFactor case study", "https://cloud.google.com/customers/macrofactor"),
        ],
        "related": ["flutter-genkit-dart", "flutter-gemma-litert-ondevice"],
        "body_en": """You do not always need a Node/Go proxy to call an LLM from a Flutter app. **Firebase AI Logic** (`firebase_ai`) gives you a typed client for Gemini with Firebase Auth, App Check, and quota controls already in the path.

## Why teams pick it

- Client-side multimodal calls (photos → structured nutrition logs, for example) without standing up infra.
- **Server Prompt Templates** keep system prompts and tool definitions out of the binary.
- Works with the same Firebase project you already use for Crashlytics/Auth.

## Minimal client shape

```dart
import 'package:firebase_ai/firebase_ai.dart';

final model = FirebaseAI.googleAI().generativeModel(model: 'gemini-2.5-flash');
final response = await model.generateContent([
  Content.text('Describe this UI screenshot for a bug report.'),
  Content.data('image/png', pngBytes),
]);
print(response.text);
```

(Exact API surface evolves — pin the package version and read the current docs.)

## Security checklist

1. App Check on.
2. Auth required for expensive models.
3. Server templates for prompts that encode business rules.
4. Client never holds long-lived provider keys.

## When to use Genkit instead

If flows, tools, and observability live server-side, prefer Genkit Dart. Firebase AI Logic shines when the *product* interaction is on-device and latency-sensitive.
""",
        "body_vi": """Bạn không phải lúc nào cũng cần proxy Node/Go để gọi LLM từ Flutter. **Firebase AI Logic** (`firebase_ai`) cung cấp client typed cho Gemini, sẵn Auth, App Check và quota.

## Vì sao team chọn

- Gọi multimodal phía client (ảnh → log dinh dưỡng có cấu trúc) không phải dựng infra.
- **Server Prompt Templates** giữ system prompt và tool definition ngoài binary.
- Cùng project Firebase bạn đã dùng cho Crashlytics/Auth.

## Dáng client tối thiểu

```dart
import 'package:firebase_ai/firebase_ai.dart';

final model = FirebaseAI.googleAI().generativeModel(model: 'gemini-2.5-flash');
final response = await model.generateContent([
  Content.text('Mô tả screenshot UI này cho bug report.'),
  Content.data('image/png', pngBytes),
]);
print(response.text);
```

(API surface thay đổi theo version — ghim package và đọc docs hiện tại.)

## Checklist bảo mật

1. Bật App Check.
2. Yêu cầu Auth cho model đắt.
3. Server template cho prompt chứa business rule.
4. Client không giữ provider key dài hạn.

## Khi nào dùng Genkit

Nếu flow, tool và observability ở server, ưu tiên Genkit Dart. Firebase AI Logic mạnh khi *trải nghiệm sản phẩm* ở trên device và nhạy latency.
""",
    },
    {
        "slug": "flutter-genkit-dart",
        "emoji": "🧠",
        "category": "Deep Dive",
        "topic": "AI",
        "level": "Intermediate",
        "tags": ["Flutter", "Dart", "Genkit", "AI"],
        "title_en": "Genkit Dart: full-stack AI apps without leaving Dart",
        "title_vi": "Genkit Dart: app AI full-stack không rời Dart",
        "desc_en": "Genkit Dart brings model-agnostic AI flows, tools, and structured output to both servers and Flutter clients.",
        "desc_vi": "Genkit Dart mang flow AI model-agnostic, tool và structured output lên cả server lẫn client Flutter.",
        "seo_en": "Genkit Dart Flutter full-stack AI, googleAI gemini generate, type-safe tools and flows in Dart for AI apps.",
        "seo_vi": "Genkit Dart Flutter AI full-stack, googleAI gemini generate, tool và flow type-safe bằng Dart cho app AI.",
        "keywords": [
            "genkit dart flutter",
            "flutter ai framework",
            "dart genkit gemini",
            "full stack ai dart",
            "flutter tool calling ai",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("Genkit Dart announcement", "https://dart.dev/blog/announcing-genkit-dart-build-full-stack-ai-apps-with-dart-and-flutter"),
            ("Genkit docs", "https://genkit.dev/docs/dart/get-started"),
        ],
        "related": ["flutter-firebase-ai-logic", "flutter-agent-skills-mcp"],
        "body_en": """**Genkit Dart** is an open-source framework for AI-powered apps with a model-agnostic API (Google, Anthropic, OpenAI, …). It runs server-side *or* inside Flutter clients, so one language covers prototype to production.

## Core ideas

- `Genkit()` + plugins for providers.
- Type-safe structured output and tool calling.
- Multi-turn conversations and built-in observability.

```dart
import 'package:genkit/genkit.dart';
import 'package:genkit_google_genai/genkit_google_genai.dart';

void main() async {
  final ai = Genkit(plugins: [googleAI()]);
  final response = await ai.generate(
    model: googleAI.gemini('gemini-flash-latest'),
    prompt: 'Why is Dart a great language for AI applications?',
  );
  print(response.text);
}
```

## How it fits a Flutter product

| Layer | Choice |
| --- | --- |
| Latency-sensitive UI polish | Client Genkit / Firebase AI Logic |
| Tools, RAG, billing, audit | Server Genkit |
| Shared contracts | Dart models generated once |

## Pitfalls

- Shipping a giant server prompt inside the app bundle.
- Mixing provider SDKs ad hoc instead of plugins — you lose portability.
- Ignoring traces until production incidents.
""",
        "body_vi": """**Genkit Dart** là framework mã nguồn mở cho app AI với API model-agnostic (Google, Anthropic, OpenAI…). Chạy được cả server lẫn bên trong client Flutter — một ngôn ngữ từ prototype tới production.

## Ý tưởng lõi

- `Genkit()` + plugin provider.
- Structured output type-safe và tool calling.
- Hội thoại nhiều lượt và observability sẵn có.

```dart
import 'package:genkit/genkit.dart';
import 'package:genkit_google_genai/genkit_google_genai.dart';

void main() async {
  final ai = Genkit(plugins: [googleAI()]);
  final response = await ai.generate(
    model: googleAI.gemini('gemini-flash-latest'),
    prompt: 'Vì sao Dart hợp với ứng dụng AI?',
  );
  print(response.text);
}
```

## Ghép vào sản phẩm Flutter

| Tầng | Lựa chọn |
| --- | --- |
| UI nhạy latency | Genkit client / Firebase AI Logic |
| Tool, RAG, billing, audit | Genkit server |
| Contract chung | Model Dart sinh một lần |

## Cạm bẫy

- Ship prompt server khổng lồ trong bundle app.
- Trộn SDK provider lung tung thay vì plugin — mất tính di động.
- Bỏ qua trace tới khi sự cố production.
""",
    },
    {
        "slug": "flutter-widget-previews-stable",
        "emoji": "🔍",
        "category": "Deep Dive",
        "topic": "Tooling",
        "level": "Beginner",
        "tags": ["Flutter", "DevTools", "WidgetPreview", "DX"],
        "title_en": "Widget Previews are stable: iterate on UI without booting the whole app",
        "title_vi": "Widget Previews đã stable: sửa UI không cần chạy cả app",
        "desc_en": "Flutter 3.47 graduates Widget Previewer to stable with faster startup, theme matrices, and web asset sync.",
        "desc_vi": "Flutter 3.47 đưa Widget Previewer lên stable: khởi động nhanh, ma trận theme, đồng bộ asset web.",
        "seo_en": "Flutter Widget Previews stable 3.47, PreviewThemeData, widget previewer faster startup isolated UI iteration.",
        "seo_vi": "Flutter Widget Previews stable 3.47, PreviewThemeData, widget previewer khởi động nhanh, lặp UI cách ly.",
        "keywords": [
            "flutter widget previews",
            "flutter widget previewer",
            "PreviewThemeData",
            "flutter ui preview stable",
            "isolated widget preview",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("Widget Previewer docs", "https://docs.flutter.dev/tools/widget-previewer"),
        ],
        "related": ["flutter-standalone-material-ui-cupertino-ui", "flutter-agentic-hot-reload"],
        "body_en": """Booting a full app to tweak a button is slow. **Widget Preview** renders individual widgets in isolation. After experimental cycles, it is **stable in Flutter 3.47**.

## What stable means here

- Faster startup via a local `.widget_preview/` cache.
- `PreviewThemeData` for sequential theme layering (matrix tests across seeds/contrast).
- Automatic `web/` asset sync when previewing web widgets.

## Workflow that pays off

1. Extract the widget you are changing into a previewable class.
2. Add previews for default / dark / large-text / empty-data.
3. Iterate until the preview is boring — then wire it into the app.

This is also the fastest loop for design-system work on `material_ui` / custom catalogs.

## Pitfalls

- Previews that hit `dart:io` or platform channels will not run — isolate pure UI.
- Do not put business logic in previews; put fixtures there.
""",
        "body_vi": """Chạy cả app chỉ để sửa một nút rất chậm. **Widget Preview** render widget riêng lẻ cách ly. Sau các bản experimental, nó **stable trong Flutter 3.47**.

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
""",
    },
]

# Remaining features + OSS are appended by FEATURES_2 / OSS lists below for manageability.
print(f"batch1 features defined: {len(FEATURES)}")
