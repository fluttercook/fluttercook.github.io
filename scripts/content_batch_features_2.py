"""Features 11–20 for the 2026 batch."""

FEATURES_2 = [
    {
        "slug": "flutter-multi-window-desktop",
        "emoji": "🪟",
        "category": "Deep Dive",
        "topic": "Desktop",
        "level": "Advanced",
        "tags": ["Flutter", "Desktop", "MultiWindow", "Canonical"],
        "title_en": "Desktop multi-window APIs: popups, dialogs, and windowHandle",
        "title_vi": "API multi-window desktop: popup, dialog và windowHandle",
        "desc_en": "Flutter’s experimental windowing APIs grow with Canonical: popups on Linux/Windows, content-sized windows, and native handle access.",
        "desc_vi": "API windowing experimental của Flutter lớn dần cùng Canonical: popup trên Linux/Windows, cửa sổ theo nội dung, truy cập native handle.",
        "seo_en": "Flutter multi-window desktop APIs, popup windows Linux Windows, windowHandle HWND NSWindow GtkWindow Canonical partnership.",
        "seo_vi": "Flutter API multi-window desktop, popup Linux Windows, windowHandle HWND NSWindow GtkWindow hợp tác Canonical.",
        "keywords": [
            "flutter multi window desktop",
            "flutter popup window linux",
            "windowHandle flutter",
            "canonical flutter desktop",
            "flutter dialog window",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("multiple_windows example", "https://github.com/flutter/flutter/tree/master/examples/multiple_windows"),
        ],
        "related": ["flutter-desktop-flavors", "flutter-impeller-default-desktop"],
        "body_en": """Desktop apps need more than one surface: context menus, tool palettes, detached inspectors. Flutter’s **experimental windowing APIs**, accelerated by Canonical as Strategic Steward for Flutter Desktop, are how you get there.

## What landed through 3.44 → 3.47

- Tooltip and dialog windows across Linux/macOS/Windows.
- **Popup windows on Linux and Windows** (macOS earlier).
- `showDialog` can create a real child window on platforms that support windowing.
- Content-sized windows and `windowHandle` (`HWND` / `NSWindow` / `GtkWindow`) for advanced native integration.

## When to use it

| Need | API direction |
| --- | --- |
| Context menu / palette | Popup window |
| Detached tool | Regular window + multi-window tests |
| Native docking | `windowHandle` + platform code |

## Status warning

These APIs have been **main-channel / experimental**. Do not ship production multi-window as your only UX path without a fallback. Track the `multiple_windows` example and file issues against the embedders.

## Practical tip

Design your feature so the *primary* workflow still works single-window. Multi-window should be an accelerator, not a hard dependency, until the APIs graduate.
""",
        "body_vi": """App desktop cần nhiều surface: context menu, palette công cụ, inspector tách rời. **API windowing experimental** của Flutter — được Canonical đẩy nhanh với vai trò Strategic Steward cho Flutter Desktop — là đường đi.

## Đã landing từ 3.44 → 3.47

- Cửa sổ tooltip và dialog trên Linux/macOS/Windows.
- **Popup trên Linux và Windows** (macOS có sớm hơn).
- `showDialog` có thể tạo cửa sổ con thật trên nền tảng hỗ trợ windowing.
- Cửa sổ theo nội dung và `windowHandle` (`HWND` / `NSWindow` / `GtkWindow`) cho tích hợp native nâng cao.

## Khi nào dùng

| Nhu cầu | Hướng API |
| --- | --- |
| Context menu / palette | Popup window |
| Tool tách rời | Regular window + test multi-window |
| Docking native | `windowHandle` + code platform |

## Cảnh báo trạng thái

Các API này ở **main-channel / experimental**. Đừng ship multi-window production làm UX duy nhất khi chưa có fallback. Theo dõi example `multiple_windows` và file issue vào embedder.

## Mẹo thực tế

Thiết kế feature sao cho workflow *chính* vẫn chạy được single-window. Multi-window nên là gia tốc, không phải hard dependency, cho tới khi API graduate.
""",
    },
    {
        "slug": "flutter-desktop-flavors",
        "emoji": "🍨",
        "category": "Deep Dive",
        "topic": "Desktop",
        "level": "Intermediate",
        "tags": ["Flutter", "Desktop", "Flavors", "Build"],
        "title_en": "Product flavors on Windows and Linux in Flutter 3.47",
        "title_vi": "Product flavor trên Windows và Linux trong Flutter 3.47",
        "desc_en": "Desktop joins Android/iOS with real flavors — including per-flavor assets in pubspec and --flavor build flags.",
        "desc_vi": "Desktop bắt kịp Android/iOS với flavor thật — gồm asset theo flavor trong pubspec và cờ build --flavor.",
        "seo_en": "Flutter desktop flavors Windows Linux 3.47, per-flavor assets pubspec, flutter build windows --flavor.",
        "seo_vi": "Flutter flavor desktop Windows Linux 3.47, asset theo flavor pubspec, flutter build windows --flavor.",
        "keywords": [
            "flutter desktop flavors",
            "flutter windows flavor",
            "flutter linux flavor",
            "flutter build --flavor desktop",
            "per flavor assets flutter",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("Flavors guide", "https://docs.flutter.dev/deployment/flavors"),
        ],
        "related": ["flutter-platform-specific-assets", "flutter-multi-window-desktop"],
        "body_en": """Dev/staging/prod builds were a mobile-only story for a long time. Flutter 3.47 brings **flavors to Windows and Linux**.

## pubspec assets per flavor

```yaml
flutter:
  assets:
    - path: assets/flavor_a/images
      flavors:
        - flavor_a
    - path: assets/flavor_b/images
      flavors:
        - flavor_b
```

## Build

```bash
flutter build windows --flavor flavor_a
flutter build linux --flavor flavor_a
```

## Why desktop teams care

- Separate app IDs and icons for internal vs store builds.
- Different API base URLs without string hacks in Dart.
- CI matrix can produce side-by-side installers.

## Pitfalls

- Pair flavors with `dart-define` or compile-time env — flavors alone do not inject secrets.
- Remember desktop packaging (MSIX, deb/rpm, AppImage) still has its own identity rules.
""",
        "body_vi": """Build dev/staging/prod từng là chuyện riêng mobile. Flutter 3.47 mang **flavor lên Windows và Linux**.

## Asset theo flavor trong pubspec

```yaml
flutter:
  assets:
    - path: assets/flavor_a/images
      flavors:
        - flavor_a
    - path: assets/flavor_b/images
      flavors:
        - flavor_b
```

## Build

```bash
flutter build windows --flavor flavor_a
flutter build linux --flavor flavor_a
```

## Vì sao team desktop quan tâm

- App ID và icon tách biệt cho bản internal vs store.
- API base URL khác nhau không cần hack string trong Dart.
- CI matrix sinh được installer cạnh nhau.

## Cạm bẫy

- Ghép flavor với `dart-define` hoặc env compile-time — flavor tự nó không inject secret.
- Packaging desktop (MSIX, deb/rpm, AppImage) vẫn có luật identity riêng.
""",
    },
    {
        "slug": "flutter-wasm-deferred-loading",
        "emoji": "🕸️",
        "category": "Deep Dive",
        "topic": "Web",
        "level": "Advanced",
        "tags": ["Flutter", "Web", "Wasm", "Performance"],
        "title_en": "Flutter web Wasm: deferred loading for smaller first paint",
        "title_vi": "Flutter web Wasm: deferred loading để first paint nhẹ hơn",
        "desc_en": "Flutter is moving toward Wasm by default. Deferred loading lets you split modules and ship a smaller bootstrap.",
        "desc_vi": "Flutter đang tiến tới Wasm mặc định. Deferred loading cho phép tách module và bootstrap nhỏ hơn.",
        "seo_en": "Flutter web Wasm deferred loading, flutter build web --wasm --enable-wasm-deferred-loading, package:web migration.",
        "seo_vi": "Flutter web Wasm deferred loading, flutter build web --wasm --enable-wasm-deferred-loading, migrate package:web.",
        "keywords": [
            "flutter wasm",
            "flutter deferred loading wasm",
            "flutter web performance",
            "dart2wasm flutter",
            "package:web migration",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("Compile to WebAssembly", "https://docs.flutter.dev/platform-integration/web/wasm"),
        ],
        "related": ["flutter-platform-specific-assets", "flutter-impeller-default-desktop"],
        "body_en": """Wasm unlocks near-native graphics on the web — and a new packaging discipline. Flutter 3.47 adds **experimental deferred loading** for Wasm builds so you can split a large app into lazy modules.

## Build commands

```bash
flutter build web --release --wasm
# experimental deferred modules (main channel flag in 3.47 era)
flutter build web --release --wasm --enable-wasm-deferred-loading
```

## Prerequisites

- Migrate off `dart:html` to **`package:web`** and modern JS interop.
- Update packages that still assume dart2js-only interop.

## Splitting strategy

1. Keep login/shell in the main module.
2. Defer heavy feature screens (admin, editors, maps).
3. Measure *time to interactive*, not just download size.

## Pitfalls

- Deferred libraries must not be required during first frame.
- Wasm + canvas/Skottie-heavy UIs still need careful asset budgets.
- Not every browser/flag combination is equal — test Chrome, Safari, Firefox.
""",
        "body_vi": """Wasm mở khóa đồ họa gần native trên web — kèm kỷ luật đóng gói mới. Flutter 3.47 thêm **deferred loading experimental** cho build Wasm để tách app lớn thành module lazy.

## Lệnh build

```bash
flutter build web --release --wasm
flutter build web --release --wasm --enable-wasm-deferred-loading
```

## Điều kiện tiên quyết

- Rời `dart:html` sang **`package:web`** và JS interop hiện đại.
- Update package còn giả định interop chỉ dart2js.

## Chiến lược tách module

1. Giữ login/shell ở module chính.
2. Defer màn nặng (admin, editor, map).
3. Đo *time to interactive*, không chỉ dung lượng tải.

## Cạm bẫy

- Library deferred không được bắt buộc ở frame đầu.
- UI nặng canvas/Skottie vẫn cần ngân sách asset chặt.
- Không phải tổ hợp browser/flag nào cũng giống nhau — test Chrome, Safari, Firefox.
""",
    },
    {
        "slug": "flutter-platform-specific-assets",
        "emoji": "📁",
        "category": "Deep Dive",
        "topic": "Performance",
        "level": "Beginner",
        "tags": ["Flutter", "Assets", "AppSize", "pubspec"],
        "title_en": "Ship only the assets each platform needs",
        "title_vi": "Chỉ ship asset mà từng nền tảng cần",
        "desc_en": "Flutter 3.41 lets pubspec declare platforms per asset — smaller APKs by excluding desktop-only files.",
        "desc_vi": "Flutter 3.41 cho phép pubspec khai báo platforms theo asset — APK nhỏ hơn khi loại file chỉ dành desktop.",
        "seo_en": "Flutter platform-specific assets pubspec platforms key, reduce APK size, exclude desktop assets from mobile builds.",
        "seo_vi": "Flutter asset theo nền tảng pubspec platforms, giảm dung lượng APK, loại asset desktop khỏi build mobile.",
        "keywords": [
            "flutter platform specific assets",
            "pubspec platforms assets",
            "reduce flutter apk size",
            "flutter asset optimization",
            "flutter web_worker assets",
        ],
        "sources": [
            ("What's new in Flutter 3.41", "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"),
            ("Assets and images", "https://docs.flutter.dev/ui/assets/assets-and-images"),
        ],
        "related": ["flutter-desktop-flavors", "flutter-app-size-reduction"],
        "body_en": """One `flutter:` assets list used to mean every platform received every file. From 3.41 you can filter:

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

## Why this is not optional for multi-platform apps

- Mobile users should not download desktop help PDFs or web workers.
- Store size metrics and download friction improve immediately.
- CI can assert platform asset matrices in tests.

## Practical split

| Asset type | Platforms |
| --- | --- |
| Shared branding | all |
| Web workers / wasm helpers | web |
| High-res print templates | desktop |
| iOS/Android notification sounds | android, ios |

## Pitfalls

- Conditional `rootBundle.load` of a missing platform asset throws — guard with a platform check.
- This is *packaging* filtering, not runtime theming.
""",
        "body_vi": """Một danh sách `flutter:` assets từng khiến mọi nền tảng nhận mọi file. Từ 3.41 bạn lọc được:

```yaml
flutter:
  assets:
    - path: assets/logo.png
    - path: assets/web_worker.js
      platforms: [web]
    - path: assets/desktop_icon.png
      platforms: [windows, linux, macos]
```

## Vì sao app đa nền tảng nên làm

- User mobile không nên tải PDF hướng dẫn desktop hay web worker.
- Metric dung lượng store và ma sát download cải thiện ngay.
- CI assert được ma trận asset theo nền tảng.

## Cách chia thực tế

| Loại asset | Nền tảng |
| --- | --- |
| Branding dùng chung | all |
| Web worker / helper wasm | web |
| Template in ấn độ phân giải cao | desktop |
| Nhạc notification iOS/Android | android, ios |

## Cạm bẫy

- `rootBundle.load` asset không tồn tại trên nền tảng sẽ throw — guard bằng platform check.
- Đây là lọc *đóng gói*, không phải theming runtime.
""",
    },
    {
        "slug": "flutter-uiscene-ios-lifecycle",
        "emoji": "🍎",
        "category": "Deep Dive",
        "topic": "iOS",
        "level": "Intermediate",
        "tags": ["Flutter", "iOS", "UIScene", "Xcode"],
        "title_en": "UIScene lifecycle: the iOS 27 launch requirement Flutter apps must meet",
        "title_vi": "UIScene lifecycle: yêu cầu khởi động iOS 27 mà app Flutter phải đạt",
        "desc_en": "Xcode 27 / iOS 27 require UIScene. Flutter migrates most apps automatically; custom AppDelegate paths need a manual pass.",
        "desc_vi": "Xcode 27 / iOS 27 bắt buộc UIScene. Flutter migrate tự động đa số app; AppDelegate tùy chỉnh cần migrate tay.",
        "seo_en": "Flutter UIScene lifecycle iOS 27 Xcode 27, AppDelegate migration, min iOS 15 Flutter 3.47, launch failure without UIScene.",
        "seo_vi": "Flutter UIScene lifecycle iOS 27 Xcode 27, migrate AppDelegate, min iOS 15 Flutter 3.47, không UIScene sẽ không launch.",
        "keywords": [
            "flutter uiscene",
            "flutter ios 27 lifecycle",
            "flutter appdelegate migration",
            "uiscenedelegate flutter",
            "flutter min ios 15",
        ],
        "sources": [
            ("What's new in Flutter 3.47", "https://flutter.dev/blog/whats-new-in-flutter-3-47"),
            ("UIScene lifecycle guide", "https://docs.flutter.dev/release/breaking-changes/uiscene-lifecycle-ios"),
            ("UISceneDelegate migration", "https://docs.flutter.dev/release/breaking-changes/uiscenedelegate"),
        ],
        "related": ["flutter-swift-package-manager-default", "flutter-content-sized-views"],
        "body_en": """Apple’s scene-based lifecycle is no longer optional for apps built with the latest SDKs. **iOS 27 / Xcode 27 will fail launches** for UIKit apps that do not adopt `UIScene`.

## What Flutter 3.47 changes

- Minimums rise: **iOS 15**, **macOS 12** (from 13 / 10.15).
- The CLI migrates typical `AppDelegate` setups automatically.
- Manual work remains if you customized lifecycle hooks or use plugins that still assume the old model.

## Migration checklist

1. Update Xcode and Flutter to the supported pair.
2. Clean build and look for CLI migration output.
3. Audit plugins for UIApplicationDelegate-only APIs.
4. Test cold start, background→foreground, and permission dialogs.

## Pitfalls

- “It launches in the simulator” is not enough — test a device with the new SDK.
- Deep links and notification handlers often live in lifecycle code; retest them.
""",
        "body_vi": """Lifecycle theo scene của Apple không còn tùy chọn với app build bằng SDK mới nhất. **iOS 27 / Xcode 27 sẽ không launch** app UIKit chưa dùng `UIScene`.

## Flutter 3.47 đổi gì

- Nâng minimum: **iOS 15**, **macOS 12** (từ 13 / 10.15).
- CLI migrate `AppDelegate` thường tự động.
- Việc tay còn lại nếu bạn customize lifecycle hook hoặc plugin còn giả định model cũ.

## Checklist migrate

1. Update Xcode và Flutter về cặp được hỗ trợ.
2. Clean build và đọc output migrate của CLI.
3. Rà plugin có API chỉ UIApplicationDelegate.
4. Test cold start, background→foreground, dialog quyền.

## Cạm bẫy

- “Chạy được trên simulator” là chưa đủ — test device với SDK mới.
- Deep link và notification handler thường nằm trong lifecycle code; test lại.
""",
    },
    {
        "slug": "flutter-fragment-shader-api",
        "emoji": "🧬",
        "category": "Deep Dive",
        "topic": "Graphics",
        "level": "Advanced",
        "tags": ["Flutter", "Shaders", "Impeller", "Graphics"],
        "title_en": "Fragment shaders in Flutter: uniforms by name and sync textures",
        "title_vi": "Fragment shader trong Flutter: uniform theo tên và texture đồng bộ",
        "desc_en": "3.41–3.44 shader APIs get ergonomic: getUniformFloat by name, decodeImageFromPixelsSync, and high-bit textures for LUTs.",
        "desc_vi": "API shader 3.41–3.44 tiện hơn: getUniformFloat theo tên, decodeImageFromPixelsSync, texture high-bit cho LUT.",
        "seo_en": "Flutter FragmentShader getUniformFloat by name, decodeImageFromPixelsSync, high bitrate textures LUT Impeller shaders.",
        "seo_vi": "Flutter FragmentShader getUniformFloat theo tên, decodeImageFromPixelsSync, texture high-bit LUT shader Impeller.",
        "keywords": [
            "flutter fragment shader",
            "getUniformFloat flutter",
            "decodeImageFromPixelsSync",
            "flutter lut texture",
            "flutter custom shader 2026",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("What's new in Flutter 3.41", "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"),
            ("Fragment shaders docs", "https://docs.flutter.dev/ui/design/graphics/fragment-shaders"),
        ],
        "related": ["flutter-impeller-default-desktop", "flutter-widget-previews-stable"],
        "body_en": """Custom shaders stop being a niche once Impeller owns the stack. The recent API work removes the worst papercuts.

## Bind uniforms by name

```dart
void setUp(ui.FragmentShader shader) {
  shader.getUniformFloat('intensity').set(0.85);
}
```

No more counting float slots by hand — fewer off-by-one GPU bugs.

## Sync textures in the same frame

```dart
final image = picture.toImageSync(
  128,
  128,
  targetFormat: ui.TargetPixelFormat.rFloat32,
);
shader.setImageSampler(0, image);
```

`decodeImageFromPixelsSync` / `toImageSync` remove a frame of lag when creating sampler textures. High-bit formats (up to 128-bit float) unlock serious LUTs and SDFs.

## Workflow

1. Author `.frag` under `shaders/`.
2. Load via `ShaderLib` / asset API in docs.
3. Preview in isolation; then integrate behind a feature flag.

## Pitfalls

- Skia vs Impeller coordinate differences still bite ported shaders.
- Big LUTs need memory budgets — measure, do not assume.
""",
        "body_vi": """Custom shader hết “ngách” khi Impeller nắm stack. API gần đây gỡ các nốt đau tồi tệ nhất.

## Bind uniform theo tên

```dart
void setUp(ui.FragmentShader shader) {
  shader.getUniformFloat('intensity').set(0.85);
}
```

Không còn đếm slot float thủ công — bớt bug off-by-one trên GPU.

## Texture đồng bộ trong cùng frame

```dart
final image = picture.toImageSync(
  128,
  128,
  targetFormat: ui.TargetPixelFormat.rFloat32,
);
shader.setImageSampler(0, image);
```

`decodeImageFromPixelsSync` / `toImageSync` bỏ một frame lag khi tạo texture sampler. Format high-bit (tới 128-bit float) mở khóa LUT và SDF nghiêm túc.

## Workflow

1. Viết `.frag` trong `shaders/`.
2. Load theo docs (ShaderLib / asset API).
3. Preview cách ly; rồi mới integrate sau feature flag.

## Cạm bẫy

- Khác biệt tọa độ Skia vs Impeller vẫn cắn shader port.
- LUT lớn cần ngân sách memory — phải đo.
""",
    },
    {
        "slug": "flutter-cupertino-menu-anchor",
        "emoji": "📋",
        "category": "Deep Dive",
        "topic": "UI",
        "level": "Intermediate",
        "tags": ["Flutter", "Cupertino", "Material", "Menus"],
        "title_en": "CupertinoMenuAnchor and modern Flutter menus",
        "title_vi": "CupertinoMenuAnchor và menu Flutter hiện đại",
        "desc_en": "RawMenuAnchor powers CupertinoMenuAnchor and animated Material MenuAnchor — native-feeling menus without plugin stacks.",
        "desc_vi": "RawMenuAnchor cấp nguồn cho CupertinoMenuAnchor và MenuAnchor Material có animation — menu tự nhiên không cần plugin.",
        "seo_en": "Flutter CupertinoMenuAnchor RawMenuAnchor, Material MenuAnchor hoverOpenDelay, native iOS menus in Flutter 3.44.",
        "seo_vi": "Flutter CupertinoMenuAnchor RawMenuAnchor, Material MenuAnchor hoverOpenDelay, menu iOS tự nhiên trong Flutter 3.44.",
        "keywords": [
            "flutter cupertino menu anchor",
            "RawMenuAnchor",
            "flutter ios context menu",
            "MenuAnchor animation material",
            "flutter submenu hoverOpenDelay",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("CupertinoMenuAnchor API", "https://api.flutter.dev/flutter/cupertino/CupertinoMenuAnchor-class.html"),
            ("MenuAnchor API", "https://api.flutter.dev/flutter/material/MenuAnchor-class.html"),
        ],
        "related": ["flutter-standalone-material-ui-cupertino-ui", "flutter-widget-previews-stable"],
        "body_en": """Menus are where Flutter apps most often feel “webby.” **RawMenuAnchor** is the shared primitive; Cupertino and Material both build on it.

## Cupertino

`CupertinoMenuAnchor` (community-led, notably davidhicks980) gives iOS apps a menu that behaves like UIKit: dismiss physics, nesting, and focus that match platform expectations.

## Material

`MenuAnchor` gains optional Material 3 animations (`animated: true`) and `SubmenuButton.hoverOpenDelay` for desktop hover behavior.

## Decision table

| Target | Prefer |
| --- | --- |
| iOS-first product | CupertinoMenuAnchor |
| Desktop dense UI | MenuAnchor + hoverOpenDelay |
| Cross-platform brand | Adaptive wrapper choosing by platform |

## Pitfalls

- Callback close order changed on RawMenuAnchor — read the breaking-change note before upgrading.
- Do not rebuild the entire menu tree on every pointer event; keep anchors stable.
""",
        "body_vi": """Menu là nơi app Flutter hay “mở web” nhất. **RawMenuAnchor** là primitive chung; Cupertino và Material đều xây trên đó.

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
""",
    },
    {
        "slug": "flutter-content-sized-views",
        "emoji": "📐",
        "category": "Deep Dive",
        "topic": "Add-to-App",
        "level": "Advanced",
        "tags": ["Flutter", "AddToApp", "iOS", "Android"],
        "title_en": "Content-sized Flutter views in native parents",
        "title_vi": "Flutter view co theo nội dung trong native parent",
        "desc_en": "Flutter 3.41 lets embedded views size to content — critical for Flutter inside native scrollables.",
        "desc_vi": "Flutter 3.41 cho view nhúng size theo nội dung — then chốt khi Flutter nằm trong scrollable native.",
        "seo_en": "Flutter content-sized views Add-to-App, isAutoResizable iOS, content_wrap Android FlutterView, embed Flutter in native scroll.",
        "seo_vi": "Flutter view size theo nội dung Add-to-App, isAutoResizable iOS, content_wrap Android FlutterView, nhúng Flutter vào scroll native.",
        "keywords": [
            "flutter content sized views",
            "flutter add to app scroll",
            "FlutterViewController isAutoResizable",
            "content_wrap flutterview",
            "embed flutter native scrollview",
        ],
        "sources": [
            ("What's new in Flutter 3.41", "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"),
            ("Add a Flutter screen — iOS", "https://docs.flutter.dev/add-to-app/ios/add-flutter-screen"),
            ("Add a Flutter View — Android", "https://docs.flutter.dev/add-to-app/android/add-flutter-view"),
        ],
        "related": ["flutter-uiscene-ios-lifecycle", "flutter-swift-package-manager-default"],
        "body_en": """Historically an embedded Flutter view needed a fixed size from its native parent. That made Flutter-inside-`UIScrollView` or `RecyclerView` painful.

## Enable content sizing

- **iOS:** `FlutterViewController.isAutoResizable = true`
- **Android:** set width/height of `FlutterView` to `content_wrap` and enable content sizing in the manifest/docs flow.

## Root widget constraints

Your Flutter root must tolerate unbounded height (or width). Avoid a top-level `ListView` that expects a bounded viewport; prefer intrinsic-height layouts or a single-column with shrink-wrapped content.

## Pitfalls

- Animations that assume a phone-sized viewport can overflow inside a native list cell.
- Measure jank: multiple embedded Flutter engines/views still cost memory.
- Coordinate with keyboard insets from the native side.
""",
        "body_vi": """Trước đây view Flutter nhúng cần size cố định từ native parent. Điều đó khiến Flutter bên trong `UIScrollView` hay `RecyclerView` rất đau.

## Bật content sizing

- **iOS:** `FlutterViewController.isAutoResizable = true`
- **Android:** đặt width/height của `FlutterView` là `content_wrap` và bật content sizing theo docs.

## Ràng buộc root widget

Root Flutter phải chịu được unbounded height (hoặc width). Tránh `ListView` top-level kỳ vọng viewport bị chặn; ưu tiên layout intrinsic-height hoặc shrink-wrapped.

## Cạm bẫy

- Animation giả định viewport cỡ phone có thể overflow trong cell list native.
- Đo jank: nhiều engine/view Flutter nhúng vẫn tốn memory.
- Đồng bộ keyboard inset từ phía native.
""",
    },
    {
        "slug": "flutter-public-release-windows",
        "emoji": "🗓️",
        "category": "Deep Dive",
        "topic": "Process",
        "level": "Beginner",
        "tags": ["Flutter", "Releases", "OSS", "Planning"],
        "title_en": "Public release windows: when your Flutter PR ships to stable",
        "title_vi": "Public release windows: PR Flutter của bạn lên stable khi nào",
        "desc_en": "Flutter 3.41 publishes branch cutoff dates so contributors know which stable train their change boards.",
        "desc_vi": "Flutter 3.41 công bố branch cutoff để contributor biết stable nào chứa change của mình.",
        "seo_en": "Flutter public release windows 2026 branch cutoff dates 3.41 3.44 3.47 3.50 stable schedule.",
        "seo_vi": "Flutter public release windows 2026 branch cutoff 3.41 3.44 3.47 3.50 lịch stable.",
        "keywords": [
            "flutter release windows",
            "flutter branch cutoff",
            "flutter stable schedule 2026",
            "flutter 3.50 november",
            "when does pr land flutter",
        ],
        "sources": [
            ("What's new in Flutter 3.41", "https://blog.flutter.dev/whats-new-in-flutter-3-41-302ec140e632"),
            ("Release notes", "https://docs.flutter.dev/release/release-notes"),
        ],
        "related": ["flutter-standalone-material-ui-cupertino-ui", "flutter-agent-skills-mcp"],
        "body_en": """Open-source planning used to be fuzzy. Flutter now publishes **release windows** — branch cutoff dates that guarantee inclusion in the next stable.

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
""",
        "body_vi": """Lập kế hoạch open-source từng mập mờ. Flutter giờ công bố **release windows** — branch cutoff date bảo đảm inclusion vào stable kế tiếp.

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
""",
    },
    {
        "slug": "flutter-gemma-litert-ondevice",
        "emoji": "📱",
        "category": "Deep Dive",
        "topic": "AI",
        "level": "Advanced",
        "tags": ["Flutter", "AI", "Gemma", "OnDevice"],
        "title_en": "On-device Gemma in Flutter: flutter_gemma and LiteRT-LM",
        "title_vi": "Gemma on-device trong Flutter: flutter_gemma và LiteRT-LM",
        "desc_en": "Run Gemma models on-device across Flutter’s six platforms with GPU/NPU acceleration via LiteRT-LM.",
        "desc_vi": "Chạy model Gemma on-device trên cả sáu nền tảng Flutter với tăng tốc GPU/NPU qua LiteRT-LM.",
        "seo_en": "Flutter flutter_gemma LiteRT-LM on-device Gemma 4, GPU NPU inference Android iOS web desktop, privacy AI Flutter.",
        "seo_vi": "Flutter flutter_gemma LiteRT-LM Gemma 4 on-device, suy luận GPU NPU Android iOS web desktop, AI privacy Flutter.",
        "keywords": [
            "flutter_gemma",
            "litert-lm flutter",
            "on device ai flutter",
            "gemma 4 flutter",
            "flutter local llm",
        ],
        "sources": [
            ("What's new in Flutter 3.44", "https://blog.flutter.dev/whats-new-in-flutter-3-44-b0cc1ad3c527"),
            ("flutter_gemma package", "https://pub.dev/packages/flutter_gemma"),
            ("LiteRT-LM", "https://ai.google.dev/edge/litert-lm/overview"),
        ],
        "related": ["flutter-firebase-ai-logic", "flutter-genkit-dart"],
        "body_en": """Cloud AI is not the only path. **On-device models** keep data local, work offline, and cut per-request cost. Flutter’s story here is `flutter_gemma` plus Google’s **LiteRT-LM** inference runtime.

## Why LiteRT-LM matters

It abstracts hardware differences and aims at GPU/NPU acceleration across Android, iOS, Web, Windows, Linux, and macOS — the same six targets Flutter ships.

## Product patterns that work

1. **Vision assist** — camera frames → short structured descriptions (Gemma Vision style).
2. **Task coaching** — local multi-step planning without a round trip.
3. **Privacy-sensitive dictation/notes** — text never leaves the device.

## Engineering checklist

- Model download UX (multi-hundred MB) with resume.
- Thermal/battery budgets on mid-tier phones.
- Fallback path when NPU/driver is missing.
- Clear user messaging that processing is local.

## Pitfalls

- Do not block the UI isolate on token generation.
- Quantization tradeoffs: measure quality on *your* tasks, not benchmarks alone.
""",
        "body_vi": """AI cloud không phải đường duy nhất. **Model on-device** giữ dữ liệu cục bộ, chạy offline và cắt cost theo request. Câu chuyện Flutter ở đây là `flutter_gemma` cộng runtime **LiteRT-LM** của Google.

## Vì sao LiteRT-LM quan trọng

Nó trừu tượng hóa khác biệt phần cứng và nhắm tăng tốc GPU/NPU trên Android, iOS, Web, Windows, Linux, macOS — đúng sáu đích Flutter ship.

## Pattern sản phẩm hiệu quả

1. **Trợ giúp thị giác** — frame camera → mô tả ngắn có cấu trúc (kiểu Gemma Vision).
2. **Huấn luyện task** — kế hoạch nhiều bước local, không round trip.
3. **Dictation/note nhạy privacy** — text không rời máy.

## Checklist kỹ thuật

- UX tải model (vài trăm MB) có resume.
- Ngân sách thermal/battery trên phone tầm trung.
- Path fallback khi thiếu NPU/driver.
- Thông điệp rõ: xử lý nằm trên máy.

## Cạm bẫy

- Đừng chặn UI isolate khi sinh token.
- Đánh đổi quantization: đo chất lượng trên *task của bạn*, không chỉ benchmark.
""",
    },
]
