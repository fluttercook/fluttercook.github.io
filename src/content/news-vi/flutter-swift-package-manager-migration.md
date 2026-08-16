---
title: "Swift Package Manager giờ là mặc định — và CocoaPods đã có hạn chót"
description: "Swift Package Manager bật mặc định từ Flutter 3.44, 92 trong 100 plugin iOS phổ biến nhất đã chuyển, và registry CocoaPods sẽ chỉ đọc từ 02/12/2026."
seoDescription: "Hướng dẫn migrate Swift Package Manager cho Flutter: SwiftPM đổi gì trong project Xcode, cách bật/tắt, tình trạng plugin, và hạn chót CocoaPods chuyển sang chỉ đọc."
keywords: ["flutter swift package manager", "migrate swiftpm flutter", "cocoapods chỉ đọc 2026", "plugin ios flutter spm", "FlutterGeneratedPluginSwiftPackage", "build ios flutter"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "📦"
tags: ["Flutter 3.47", "Flutter", "iOS", "Swift Package Manager", "Plugin"]
sources:
  - name: "Swift Package Manager for app developers — flutter.dev docs"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers"
  - name: "Swift Package Manager for plugin authors — flutter.dev docs"
    url: "https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-plugin-authors"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter release notes"
    url: "https://docs.flutter.dev/release/release-notes"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Phần lớn lập trình viên Flutter đã migrate sang Swift Package Manager mà không hay biết. Nó bật mặc định từ **Flutter 3.44**, và tooling tự thêm phần tích hợp vào project Xcode ngay lần build đầu sau khi nâng cấp. Lý do phải để ý lúc này là một cái mốc: **registry CocoaPods chuyển sang chỉ đọc ngày 02/12/2026**. Sau mốc đó, việc tắt SwiftPM không còn là lối thoát được hỗ trợ.

Flutter 3.47 công bố **92 trong 100 plugin iOS phổ biến nhất đã chuyển sang Swift Package Manager**. Cái đuôi dài mới là thứ cắn bạn, không phải phần đầu phân phối.

## Thực sự thay đổi gì trong project của bạn

Khi SwiftPM bật và bạn build, Flutter sửa project Xcode theo ba cách:

1. Thêm **`FlutterGeneratedPluginSwiftPackage`** làm package dependency của target `Runner`.
2. Thêm pre-action **Run Prepare Flutter Framework Script** vào build scheme.
3. Resolve và tải các Swift package mà plugin Flutter của bạn phụ thuộc.

Package sinh tự động đó nằm ở `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`. Chữ *ephemeral* ở đây có ý nghĩa thật — nó được sinh lại, không phải để sửa tay, và không thuộc về version control.

Quan trọng: **CocoaPods không biến mất**. Flutter tự động fallback về CocoaPods cho bất kỳ dependency nào chưa hỗ trợ SwiftPM, nên một project pha trộn là trạng thái bình thường trong giai đoạn chuyển tiếp, không phải cấu hình sai.

## Bật, tắt, và theo từng project

Nếu một phiên bản project trước đó đã tắt, bật lại toàn cục:

```bash
flutter config --enable-swift-package-manager
```

Tắt toàn cục:

```bash
flutter config --no-enable-swift-package-manager
```

Tắt cho riêng một project, trong `pubspec.yaml`:

```yaml
flutter:
  config:
    enable-swift-package-manager: false
```

Công tắc theo project mới là thứ hữu ích. Nếu chỉ đúng một app trong tổ chức phụ thuộc vào một plugin nội bộ chưa migrate, hãy ghim app đó và để mọi thứ còn lại theo mặc định.

## Gỡ bỏ hoàn toàn phần tích hợp

Nếu bạn cần rollback sạch — để bisect, hoặc vì build hỏng và bạn muốn một mốc chuẩn:

1. Tắt SwiftPM bằng một trong hai công tắc trên.
2. Chạy `flutter clean`.
3. Mở Xcode workspace.
4. Gỡ `FlutterGeneratedPluginSwiftPackage` khỏi **Package Dependencies**.
5. Gỡ nó khỏi **Frameworks, Libraries, and Embedded Content**.
6. Xoá pre-action **Run Prepare Flutter Framework Script**.

Bước 3 đến 6 là những bước hay bị quên, và một phần tích hợp gỡ dở dang sẽ sinh ra lỗi link rất khó hiểu.

## Khi migrate tự động thất bại

Tooling đôi khi không vá được project Xcode — scheme tuỳ biến nặng và file `project.pbxproj` sửa tay là thủ phạm thường gặp. Đường thủ công:

**Thêm package dependency.** Mở `ios/Runner.xcworkspace`, vào **Package Dependencies**, bấm thêm, chọn **Add Local…**, và chọn `ios/Flutter/ephemeral/Packages/FlutterGeneratedPluginSwiftPackage`. Xác nhận nó gắn vào target `Runner` và xuất hiện dưới **Frameworks, Libraries, and Embedded Content**.

**Thêm pre-action.** Vào **Product → Scheme → Edit Scheme**, mở **Build**, bấm **Pre-actions**, thêm một run script action tên `Run Prepare Flutter Framework Script`, đặt **Provide build settings from** thành `Runner`, và dùng:

```bash
"$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh" prepare
```

Sau đó chạy app và xác nhận pre-action có thực thi. Nếu migrate tự động thất bại, hãy báo lỗi kèm `project.pbxproj` và `.xcscheme` — đó là dữ liệu đội Flutter cần mà hiếm khi nhận được.

## Cái bẫy deployment target

Đây là lỗi thực tế hay gặp nhất, và không hiển nhiên từ thông báo lỗi. Một plugin SwiftPM có thể khai báo **phiên bản OS tối thiểu cao hơn** app của bạn. Khi đó build sẽ hỏng cho tới khi bạn nâng **Minimum Deployments** trong Xcode và sinh lại config:

```bash
flutter build ios --config-only
flutter build macos --config-only
```

Flutter 3.47 đã nâng sàn — **iOS 13 → 15** và **macOS 10.15 → 12** — nên nếu bạn nâng cấp từ SDK cũ, có thể bạn vượt rào này một cách tình cờ.

| Khía cạnh | CocoaPods | Swift Package Manager |
| --- | --- | --- |
| Manifest dependency | `Podfile` / `Podfile.lock` | `Package.swift` sinh tự động |
| Toolchain | Ruby gem, cài riêng | Tích hợp sẵn trong Xcode |
| Điểm tích hợp | `.xcworkspace` từ `pod install` | Package dependency + pre-action của scheme |
| Trạng thái registry | **Chỉ đọc từ 02/12/2026** | Đang phát triển tích cực |
| Mặc định của Flutter | Chỉ dùng làm fallback | **Mặc định từ 3.44** |

## Checklist migrate của bạn

1. **Xác nhận bạn đang ở mặc định.** Chạy `flutter config` và kiểm tra `enable-swift-package-manager` không bị tắt ở đâu, kể cả trong `pubspec.yaml`.
2. **Build sạch target iOS và macOS** và quan sát pre-action có chạy không.
3. **Rà soát danh sách plugin.** Với mỗi plugin iOS, kiểm tra repository của nó có kèm `Package.swift` không. Những cái không có chính là rủi ro tháng 12 của bạn.
4. **Migrate plugin của chính bạn trước** — plugin nội bộ là thứ không ai sửa hộ. Theo hướng dẫn cho plugin author và ship `Package.swift` song song với podspec hiện có.
5. **Mở hoặc upvote issue** cho các plugin bên thứ ba chưa migrate mà bạn phụ thuộc, ngay bây giờ thay vì tháng 11.
6. **Nâng deployment target** lên iOS 15 / macOS 12 và sinh lại bằng `--config-only`.
7. **Đừng đưa `ios/Flutter/ephemeral/` vào version control.**

## Kết luận

SwiftPM không phải tính năng bạn cần chủ động áp dụng — gần như chắc chắn bạn đã dùng rồi. Việc bạn cần làm là kiểm kê những plugin chưa chuyển, vì ngày 02/12/2026 sẽ biến câu "để sau tính" thành một lần build hỏng. Phần đầu hệ sinh thái đã xong: 92 trong 100 plugin phổ biến nhất đã chuyển. Bỏ một giờ cho cái đuôi — các plugin nội bộ và ba package ít tên tuổi không ai ngó từ 2024 — và cuộc chuyển đổi này chẳng tốn của bạn gì cả.
