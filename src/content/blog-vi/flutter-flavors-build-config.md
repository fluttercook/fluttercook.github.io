---
title: "Flavor trong Flutter: một codebase, ba ứng dụng, không copy-paste cấu hình"
description: "Dev, staging và production nên là ba ứng dụng cài được với icon, bundle id và endpoint khác nhau — build từ cùng một mã nguồn, không có câu lệnh if lúc chạy quyết định gọi backend nào. Đây là toàn bộ cách nối dây trên cả hai nền tảng."
seoDescription: "Flavor trong Flutter từ đầu tới cuối: productFlavors trên Android, scheme và configuration trong Xcode, --dart-define-from-file, icon và cấu hình Firebase theo flavor, cùng file launch.json gắn kết tất cả."
keywords:
  - thiết lập flavor flutter
  - productflavors android flutter
  - scheme configuration ios flutter
  - dart-define-from-file flutter
  - icon ứng dụng theo flavor flutter
  - cấu hình môi trường flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-23"
emoji: "🍦"
tags: ["Flutter", "Build", "Android", "iOS", "DevOps"]
sources:
  - name: "Flavor cho Flutter — tài liệu Flutter"
    url: "https://docs.flutter.dev/deployment/flavors"
  - name: "Build và phát hành ứng dụng Android — tài liệu Flutter"
    url: "https://docs.flutter.dev/deployment/android"
  - name: "Build và phát hành ứng dụng iOS — tài liệu Flutter"
    url: "https://docs.flutter.dev/deployment/ios"
  - name: "Cấu hình build variant — tài liệu Android"
    url: "https://developer.android.com/build/build-variants"
  - name: "String.fromEnvironment — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-core/String/String.fromEnvironment.html"
  - name: "flutter run — tài liệu Flutter"
    url: "https://docs.flutter.dev/reference/flutter-cli"
related:
  - slug: "flutter-ci-cd-github-actions"
    title: "Một pipeline CI cho Flutter thật sự bắt được lỗi"
  - slug: "flutter-secure-storage-secrets"
    title: "Bí mật trong ứng dụng Flutter: cái gì lưu được, cái gì thì không"
draft: false
---

Phiên bản tệ của việc xử lý môi trường trông như thế này:

```dart
const bool isProd = false;
final apiBase = isProd
    ? 'https://api.example.com'
    : 'https://staging.api.example.com';
```

Nó chạy được cho tới khi ai đó phát hành với cờ bật sai chiều, hoặc tới khi QA cần cài song song staging và production rồi phát hiện cả hai có cùng bundle id. Flavor giải quyết cả hai vấn đề ở tầng build: ba ứng dụng cài được riêng biệt, mỗi cái được biên dịch kèm cấu hình của chính nó.

## Phía Dart trước đã

Bắt đầu từ đây vì đây là phần quyết định mọi thứ còn lại.

```dart
// lib/config/app_config.dart
enum Flavor { dev, staging, prod }

final class AppConfig {
  const AppConfig._({
    required this.flavor,
    required this.apiBase,
    required this.appName,
  });

  final Flavor flavor;
  final String apiBase;
  final String appName;

  static const _flavorName = String.fromEnvironment(
    'FLAVOR',
    defaultValue: 'dev',
  );

  static final AppConfig current = AppConfig._(
    flavor: Flavor.values.byName(_flavorName),
    apiBase: const String.fromEnvironment('API_BASE'),
    appName: const String.fromEnvironment('APP_NAME', defaultValue: 'App Dev'),
  );

  bool get isProduction => flavor == Flavor.prod;
}
```

`String.fromEnvironment` phải là `const` và phải được đọc trong ngữ cảnh const — đó là thứ cho phép trình biên dịch cắt bỏ các nhánh không dùng. Viết `String.fromEnvironment(name)` với biến `name` lúc chạy sẽ âm thầm trả về giá trị mặc định, và đó là lỗi thật sự khó chịu vì nhìn nó có vẻ đúng.

Giá trị đến từ `--dart-define`, và với nhiều hơn hai giá trị thì đến từ một file:

```json
// config/dev.json
{
  "FLAVOR": "dev",
  "API_BASE": "https://dev.api.example.com",
  "APP_NAME": "MyApp Dev"
}
```

```bash
flutter run --flavor dev --dart-define-from-file=config/dev.json
```

**Những file JSON này là cấu hình build, không phải kho bí mật.** Mọi thứ trong đó được nhúng vào binary và trích ra được. URL nền của API, cờ tính năng và tên ứng dụng thì không sao; khoá ký và secret API thì không — đó là bài toán khác với lời giải khác.

## Android

`android/app/build.gradle.kts`:

```kotlin
android {
    flavorDimensions += "env"

    productFlavors {
        create("dev") {
            dimension = "env"
            applicationIdSuffix = ".dev"
            resValue("string", "app_name", "MyApp Dev")
        }
        create("staging") {
            dimension = "env"
            applicationIdSuffix = ".staging"
            resValue("string", "app_name", "MyApp Staging")
        }
        create("prod") {
            dimension = "env"
            resValue("string", "app_name", "MyApp")
        }
    }
}
```

Rồi cho manifest dùng nó, trong `android/app/src/main/AndroidManifest.xml`:

```xml
<application
    android:label="@string/app_name"
    android:icon="@mipmap/ic_launcher">
```

`applicationIdSuffix` chính là thứ khiến cài song song hoạt động — với Android, `com.example.myapp.dev` và `com.example.myapp` là hai ứng dụng khác nhau. Lưu ý `prod` không có hậu tố; id production phải giữ nguyên đúng thứ mà Play Store đã biết.

Icon và cấu hình Firebase theo từng flavor nằm trong source set riêng của flavor, Gradle sẽ tự trộn:

```
android/app/src/dev/res/mipmap-xxxhdpi/ic_launcher.png
android/app/src/dev/google-services.json
android/app/src/prod/google-services.json
```

Chỗ đặt `google-services.json` hay làm người ta vấp: một file duy nhất ở `android/app/` áp cho mọi flavor và sẽ mang sai tên package với các flavor có hậu tố, gây lỗi khởi tạo Firebase mà đọc lên lại giống lỗi mạng.

## iOS

iOS là nửa lắt léo hơn vì mô hình của Xcode là scheme cộng build configuration, còn Flutter thì mong đợi một quy ước đặt tên cụ thể.

Với mỗi flavor bạn cần **ba build configuration** — `Debug-dev`, `Release-dev`, `Profile-dev`, và tương tự cho staging và prod. Bộ công cụ Flutter tìm đúng dạng `<Mode>-<flavor>`; một configuration đặt tên `dev-Debug` sẽ không được tìm thấy, và thông báo lỗi không nói rõ vì sao.

Trong Xcode:

1. Nhân bản các configuration Debug/Release/Profile sẵn có, đổi tên với hậu tố `-dev`, `-staging`, `-prod`.
2. Tạo một scheme cho mỗi flavor, trỏ mỗi cái tới đúng bộ configuration của nó.
3. Đặt `PRODUCT_BUNDLE_IDENTIFIER` theo từng configuration — ví dụ `com.example.myapp.dev`.
4. Đặt `PRODUCT_NAME` hoặc khoá `CFBundleDisplayName` trong Info.plist theo từng configuration để đổi nhãn ngoài màn hình chính.

Một build setting do người dùng định nghĩa giúp việc chọn file Firebase gọn gàng. Thêm `FIREBASE_CONFIG_DIR` cho từng configuration, rồi một run-script build phase:

```bash
cp "${SRCROOT}/config/${FIREBASE_CONFIG_DIR}/GoogleService-Info.plist" \
   "${BUILT_PRODUCTS_DIR}/${PRODUCT_NAME}.app/GoogleService-Info.plist"
```

Toàn bộ phần trên là trạng thái dự án Xcode, nằm trong `project.pbxproj` — một file trộn nhánh rất tệ. Hãy làm phần thiết lập flavor trong một commit, do một người làm, và soát diff thay vì tin tưởng nó.

## Gắn kết mọi thứ

Một file `.vscode/launch.json` để không ai phải nhớ các cờ:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "dev",
      "request": "launch",
      "type": "dart",
      "args": [
        "--flavor", "dev",
        "--dart-define-from-file", "config/dev.json"
      ]
    },
    {
      "name": "prod",
      "request": "launch",
      "type": "dart",
      "flutterMode": "release",
      "args": [
        "--flavor", "prod",
        "--dart-define-from-file", "config/prod.json"
      ]
    }
  ]
}
```

Còn trong CI, flavor trở thành một trục của ma trận:

```yaml
      - run: |
          flutter build appbundle \
            --flavor ${{ matrix.flavor }} \
            --dart-define-from-file=config/${{ matrix.flavor }}.json
```

## Lan can đáng thêm

Kiểu hỏng mà bản thân flavor không ngăn được là phát hành bản dev tới người dùng thật. Hãy thêm một phép kiểm tra lúc khởi động:

```dart
void main() {
  final config = AppConfig.current;

  assert(() {
    // Chỉ chạy ở debug/profile; ở release cả khối này bị loại bỏ.
    debugPrint('Đang chạy flavor: ${config.flavor.name} → ${config.apiBase}');
    return true;
  }());

  if (config.isProduction && config.apiBase.contains('staging')) {
    throw StateError('Flavor production đang trỏ tới endpoint staging');
  }

  runApp(MyApp(config: config));
}
```

Thành ngữ `assert(() { ... }())` đáng biết nói chung: closure chỉ chạy khi assertion được bật, nên log chỉ-dành-cho-debug không tốn gì ở bản release. Phép kiểm tra thứ hai là lan can thật lúc chạy, cố ý không dùng assert, vì đó chính là thứ phải nổ trong bản release.

Làm flavor hiện rõ trên giao diện cũng có ích — một dải băng màu ở các bản không phải production chỉ tốn một widget `Banner` và xoá sổ cả nhóm nhầm lẫn kiểu "khoan đã, tôi đang test môi trường nào?".

## Câu hỏi thường gặp

**Chỉ có dev và prod thì có cần flavor không?**

Nếu hai bản có lúc cần cài cùng lúc, hoặc cần hai dự án Firebase khác nhau, thì có. Nếu dev chỉ luôn là `flutter run` trên máy bạn, riêng `--dart-define` là đủ.

**Vì sao `--flavor` báo "no flavor named X"?**

Android và iOS có định nghĩa flavor riêng và cả hai đều phải biết tên đó. Thiếu `productFlavors` bên Android hoặc thiếu scheme bên iOS đều gây lỗi này, từ hai nửa khác nhau của bản build.

**Có thể để secret trong file dart-define không?**

Không. Mọi thứ truyền qua `--dart-define` đều nằm trong binary đã biên dịch. Hãy dùng kho lưu an toàn của nền tảng cho bí mật thuộc về người dùng, và dùng backend cho bất cứ thứ gì phải ở lại phía máy chủ.

**Làm icon riêng cho từng flavor trên iOS thế nào?**

Nhiều asset catalog, với `ASSETCATALOG_COMPILER_APPICON_NAME` đặt theo từng build configuration. Cách này sạch hơn một script tráo file lúc build.

**Tên flavor có tới được mã native không?**

Không tự động. Trên Android có `BuildConfig.FLAVOR`; trên iOS thì đọc bundle identifier hoặc một khoá Info.plist theo configuration. Đừng cho rằng giá trị phía Dart nhìn thấy được từ mã nền tảng.

---

*Cơ chế flavor, `productFlavors` của Gradle, yêu cầu đặt tên configuration trong Xcode và ngữ nghĩa của `String.fromEnvironment` mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Hình dạng lớp cấu hình phía Dart, lan can kiểm tra endpoint production, thành ngữ log `assert(() {}())` và cảnh báo về việc trộn `project.pbxproj` là nhận định riêng của tôi khi dựng phần này ở vài dự án. Cú pháp Gradle và Xcode thay đổi giữa các phiên bản — hãy đối chiếu với template hiện tại của bạn.*
