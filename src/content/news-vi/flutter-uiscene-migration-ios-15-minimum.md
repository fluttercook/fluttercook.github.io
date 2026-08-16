---
title: "Migrate UIScene: thay đổi iOS sẽ làm app Flutter chưa chuyển bị crash"
description: "Apple bắt buộc vòng đời UIScene, và Flutter 3.47 nâng sàn iOS lên 15. Đây là toàn bộ cuộc migrate — Info.plist, AppDelegate, plugin, và những API ngừng hoạt động."
seoDescription: "Hướng dẫn migrate UIScene cho Flutter: UIApplicationSceneManifest, FlutterSceneDelegate, didInitializeImplicitFlutterEngine, callback vòng đời scene cho plugin, và sàn iOS 15 / macOS 12."
keywords: ["migrate uiscene flutter", "UISceneDelegate flutter", "FlutterSceneDelegate", "didInitializeImplicitFlutterEngine", "flutter ios tối thiểu 15", "yêu cầu ios 27 flutter"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🍎"
tags: ["Flutter 3.47", "Flutter", "iOS", "Migration", "UIScene"]
sources:
  - name: "UISceneDelegate adoption — Flutter breaking changes"
    url: "https://docs.flutter.dev/release/breaking-changes/uiscenedelegate"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Flutter release notes"
    url: "https://docs.flutter.dev/release/release-notes"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Phần lớn các cuộc migrate trong Flutter là tuỳ chọn cho tới khi chúng gây phiền. Cái này khác: khi Apple bắt đầu cưỡng chế, **app chưa áp dụng vòng đời UIScene sẽ crash ngay lúc khởi động**. Không phải giảm chất lượng. Là crash.

Apple yêu cầu app UIKit build bằng SDK mới nhất phải dùng vòng đời UIScene kể từ bản phát hành sau iOS 26. Apple chưa công bố ngày cưỡng chế chính xác. Flutter đã hỗ trợ migrate từ **3.38**, và 3.47 làm các thay đổi nền tảng xung quanh trở nên cụ thể bằng cách nâng sàn: **iOS 13 → 15** và **macOS 10.15 → 12**, để hỗ trợ Xcode 27.

## UIScene thực sự thay đổi điều gì

Sự dịch chuyển về khái niệm là việc tách trách nhiệm vốn nằm trong một đối tượng:

- **`AppDelegate`** giờ xử lý sự kiện tiến trình và vòng đời tổng thể của ứng dụng
- **`UISceneDelegate`** xử lý vòng đời UI — foreground, background, active, resign

Hai hệ quả đi kèm, và cả hai đều làm hỏng code:

1. **Đăng ký plugin dời chỗ.** Đăng ký trong `didInitializeImplicitFlutterEngine`, không phải `application:didFinishLaunchingWithOptions:`.
2. **Launch options trở thành `nil`** trong `application:didFinishLaunchingWithOptions:` sau khi migrate. Chúng được chuyển tới `scene:willConnectToSession:options:`.

Cái thứ hai mới là sát thủ thầm lặng. Deep link, payload push notification, và shortcut item vốn đến qua launch options đơn giản là ngừng đến, không có lỗi biên dịch nào.

## Tin tốt: thường là tự động

Từ **Flutter 3.41**, nếu `AppDelegate` của bạn chưa bị tuỳ biến, Flutter CLI tự migrate app khi bạn chạy `flutter run` hoặc `flutter build ios`. Một phần lớn app đã xong mà không hề hay biết.

Bạn có việc phải làm nếu bạn đã tuỳ biến `AppDelegate`, ship một tích hợp add-to-app, hoặc duy trì một plugin.

## Info.plist

Cuộc migrate thêm một Application Scene Manifest:

```xml
<key>UIApplicationSceneManifest</key>
<dict>
  <key>UIApplicationSupportsMultipleScenes</key>
  <false/>
  <key>UISceneConfigurations</key>
  <dict>
    <key>UIWindowSceneSessionRoleApplication</key>
    <array>
      <dict>
        <key>UISceneClassName</key>
        <string>UIWindowScene</string>
        <key>UISceneDelegateClassName</key>
        <string>FlutterSceneDelegate</string>
        <key>UISceneConfigurationName</key>
        <string>flutter</string>
        <key>UISceneStoryboardFile</key>
        <string>Main</string>
      </dict>
    </array>
  </dict>
</dict>
```

Một mẹo debug hữu ích: thêm dấu gạch dưới vào trước `UIApplicationSceneManifest` để tạm tắt hỗ trợ UIScene, và bỏ dấu gạch dưới để bật lại. Điều đó cho bạn một phép so sánh A/B nhanh khi có gì đó hỏng.

## AppDelegate

Chuyển việc đăng ký plugin ra khỏi `didFinishLaunchingWithOptions` và vào callback mới:

```swift
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // GeneratedPluginRegistrant không còn thuộc về đây
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)

    let batteryChannel = FlutterMethodChannel(
      name: "samples.flutter.dev/battery",
      binaryMessenger: engineBridge.applicationRegistrar.messenger()
    )
  }
}
```

Method channel và platform view factory đều cần messenger từ `engineBridge.applicationRegistrar`, không phải cái ở cấp application cũ.

Với add-to-app, hãy thêm một scene delegate — thường chỉ một dòng:

```swift
import UIKit
import Flutter

class SceneDelegate: FlutterSceneDelegate {}
```

Nếu app chủ của bạn không kế thừa được `FlutterSceneDelegate`, hãy cài đặt `FlutterSceneLifeCycleProvider` và chuyển tiếp từng callback scene tới một instance `FlutterPluginSceneLifeCycleDelegate`.

## Nếu bạn duy trì một plugin

Tác giả plugin gánh phần nặng nhất, vì mọi app phụ thuộc vào bạn đều thừa hưởng trạng thái migrate của bạn.

Nâng ràng buộc, rồi áp dụng protocol và đăng ký nhận callback scene:

```yaml
environment:
  sdk: ^3.10.0
  flutter: ">=3.38.0"
```

```swift
public final class MyPlugin: NSObject, FlutterPlugin, FlutterSceneLifeCycleDelegate {
  public static func register(with registrar: FlutterPluginRegistrar) {
    registrar.addApplicationDelegate(instance)
    registrar.addSceneDelegate(instance)
  }
}
```

Rồi ánh xạ các callback cũ:

| Method của AppDelegate | Tương đương ở scene delegate |
| --- | --- |
| `applicationDidBecomeActive` | `sceneDidBecomeActive` |
| `applicationWillResignActive` | `sceneWillResignActive` |
| `applicationWillEnterForeground` | `sceneWillEnterForeground` |
| `applicationDidEnterBackground` | `sceneDidEnterBackground` |
| `application:openURL:options:` | `scene:openURLContexts:` |
| `application:continueUserActivity:` | `scene:continueUserActivity:` |
| `application:didFinishLaunchingWithOptions:` | `scene:willConnectToSession:options:` |

## Những API ngừng hoạt động

Một loạt singleton UIKit lâu đời bị deprecate dưới mô hình scene. Mỗi cái có bản thay thế theo phạm vi scene:

| Bị deprecate | Thay bằng |
| --- | --- |
| `UIScreen.main` | `UIWindowScene.screen` |
| `UIApplication.shared.delegate.window` | `registrar.viewController.view.window` |
| `UIApplication.shared.keyWindow` | `UIWindowScene.keyWindow` (iOS 15+) |
| `UIApplication.shared.windows` | `UIWindowScene.windows` |

Lưu ý `UIWindowScene.keyWindow` cần iOS 15 — đúng bằng cái sàn Flutter 3.47 vừa nâng bạn lên. Hai thay đổi này liên quan tới nhau, không phải trùng hợp.

## Trường hợp thật sự khó: khởi tạo sớm

Một số API của Apple phải được cấu hình trước khi `application:didFinishLaunchingWithOptions:` trả về — `BGTaskScheduler`, `UNUserNotificationCenterDelegate`, `HKHealthStore`. Dưới mô hình scene, việc đăng ký plugin xảy ra muộn hơn thời điểm đó.

Không có cách nào để plugin tự giải quyết một mình. Mẫu được tài liệu hoá là plugin phơi ra một method public để lập trình viên app gọi từ `AppDelegate` của chính họ:

```swift
class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    BGTaskPlugin.shared.registerBackgroundHandler(identifier: "com.example.task")
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
```

Nếu bạn dùng background task, dữ liệu sức khoẻ, hay notification delegate, hãy kiểm tra tài liệu plugin đúng theo mẫu này. Đây là bước migrate dễ bị bỏ sót nhất và ít có khả năng bị test bắt được nhất.

## Checklist migrate của bạn

1. **Build trên 3.47** và để migrate tự động chạy nếu `AppDelegate` của bạn còn nguyên bản.
2. **Thêm `UIApplicationSceneManifest`** vào `Info.plist` nếu chưa có.
3. **Chuyển `GeneratedPluginRegistrant`** vào `didInitializeImplicitFlutterEngine`, cùng với method channel và platform view factory.
4. **Test lại mọi lối vào**: deep link, universal link, chạm vào push notification, quick action ở màn hình chính. Launch options giờ là `nil`.
5. **Grep các singleton bị deprecate** — `UIScreen.main`, `keyWindow`, `UIApplication.shared.windows` — trong code của bạn và trong plugin.
6. **Nâng deployment target** lên iOS 15 và macOS 12, rồi chạy `flutter build ios --config-only`.
7. **Kiểm tra các plugin cần khởi tạo sớm** và thêm lời gọi bắt buộc trong `AppDelegate` của bạn.
8. **Đừng dùng `enable-uiscene-migration: false`** như gì khác ngoài một cách gỡ kẹt ngắn hạn — nó giấu cảnh báo, không giấu cú crash sẽ tới.

## Kết luận

Đây là cuộc migrate duy nhất trong Flutter 3.47 có chế độ hỏng dứt khoát. Các phần cơ học được tài liệu hoá tốt và phần lớn đã tự động, nên hầu hết app sẽ qua chỉ bằng một lần build lại. Thứ thực sự cắn bạn là những đường chưa được test: một deep link không còn mang theo payload, một plugin đăng ký background task quá muộn, một lời gọi `keyWindow` chôn trong dependency. Hãy build lại ngay hôm nay, rồi bỏ một giờ mở app của bạn từ mọi lối vào bên ngoài mà bạn hỗ trợ. Một giờ đó rẻ hơn nhiều so với một báo cáo crash vào ngày phát hành.
