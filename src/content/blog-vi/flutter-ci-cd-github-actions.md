---
title: "Một pipeline CI cho Flutter thật sự bắt được lỗi"
description: "Phần lớn cấu hình CI cho Flutter chạy flutter test rồi dừng. Đây là pipeline bắt thêm cả lệch định dạng, phụ thuộc mục ruỗng, hồi quy golden, và những lỗi build chỉ xuất hiện trên máy sạch — kèm cách cache để giữ nó dưới năm phút."
seoDescription: "CI/CD cho Flutter trên GitHub Actions: cache SDK và pub cache, analyze với fatal-infos, golden test, build ma trận, ký artifact, và một file workflow bạn có thể sửa lại dùng."
keywords:
  - flutter github actions ci
  - pipeline ci cd flutter
  - subosito flutter-action cache
  - golden test flutter ci
  - ký ứng dụng android flutter ci
  - flutter analyze fatal infos
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-24"
emoji: "⚙️"
tags: ["Flutter", "CI/CD", "GitHub Actions", "Testing", "DevOps"]
sources:
  - name: "Continuous delivery với Flutter — tài liệu Flutter"
    url: "https://docs.flutter.dev/deployment/cd"
  - name: "flutter test — tài liệu Flutter"
    url: "https://docs.flutter.dev/testing/overview"
  - name: "Cache phụ thuộc — tài liệu GitHub Actions"
    url: "https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows"
  - name: "Secret được mã hoá — tài liệu GitHub Actions"
    url: "https://docs.github.com/en/actions/security-guides/encrypted-secrets"
  - name: "Build và phát hành ứng dụng Android — tài liệu Flutter"
    url: "https://docs.flutter.dev/deployment/android"
  - name: "dart format — tài liệu Dart"
    url: "https://dart.dev/tools/dart-format"
related:
  - slug: "flutter-flavors-build-config"
    title: "Flavor trong Flutter: một codebase, ba ứng dụng, không copy-paste cấu hình"
  - slug: "flutter-app-size-reduction"
    title: "Thu nhỏ ứng dụng Flutter: megabyte thật sự nằm ở đâu"
draft: false
---

Kho mã Flutter nào rồi cũng mọc ra một file `.github/workflows/ci.yml` chứa `flutter test`. Nó pass, mọi người thấy yên tâm, rồi một bản build phát hành hỏng trên máy build vì lý do mà không laptop nào có thể lộ ra.

CI đáng đồng tiền khi nó bắt được những lỗi mà môi trường phát triển cục bộ về mặt cấu trúc không thể bắt: mã sinh cũ, một phụ thuộc chỉ resolve được nhờ pub cache trên máy bạn, một thay đổi định dạng chưa ai chạy, một golden đã trôi. Đây là pipeline dựng quanh những thứ đó.

## Hình dạng tổng thể

Bốn job, chia hai đợt:

| Job | Chạy khi | Bắt được |
| --- | --- | --- |
| `analyze` | mọi push và PR | lệch định dạng, hồi quy lint, mã không dùng |
| `test` | mọi push và PR | lỗi unit, widget và golden |
| `build` | PR vào main và tag | lỗi biên dịch chỉ xảy ra trên máy sạch |
| `release` | chỉ tag | ký, tải artifact lên |

`analyze` và `test` chạy song song và nhanh. `build` chậm nên bị chặn cổng. Sự phân chia đó quan trọng: một pipeline mà mỗi lần push đều phải chờ tám phút build Android là pipeline mà người ta sẽ học cách phớt lờ.

## Analyze, nhưng có răng

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true

      - run: flutter pub get
      - run: dart format --output=none --set-exit-if-changed .
      - run: flutter analyze --fatal-infos
      - run: flutter pub outdated --exit-code-on-outdated-transitive || true
```

Bốn chi tiết đang gánh việc.

**`concurrency` kèm `cancel-in-progress`.** Push ba commit lên một PR thì bạn nhận một lần chạy, không phải ba. Trên kho bận rộn, đây là khoản tiết kiệm lớn nhất có được.

**`flutter-version-file: pubspec.yaml`** đọc ràng buộc SDK từ chính kho thay vì ghim phiên bản trong workflow. Bớt một chỗ phải cập nhật, và không có độ lệch giữa thứ CI build với thứ dự án khai báo.

**`dart format --set-exit-if-changed`** làm build đỏ khi mã chưa định dạng, thay vì lặng lẽ viết lại nó. `--output=none` ngăn nó ghi file trong CI, vì nếu ghi thì diff sẽ rối.

**`--fatal-infos`** nâng lint mức info thành lỗi. Nó nghiêm hơn mức phần lớn đội bắt đầu, và chính là thiết lập giữ cho nền lint khỏi mục ruỗng — những info không bao giờ làm hỏng gì sẽ chất đống tới khi chẳng ai buồn đọc đầu ra của analyzer nữa.

## Test, gồm cả golden

```yaml
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true

      - run: flutter pub get
      - run: flutter test --coverage --reporter github

      - name: Tải golden lỗi lên
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: golden-failures
          path: '**/failures/**'
```

`--reporter github` gắn chú thích lỗi thẳng lên diff, nên một test hỏng hiện ngay ở dòng nó thuộc về thay vì nằm chôn trong log.

Phần tải artifact là thứ người ta hay bỏ qua rồi tiếc. Khi một golden test hỏng trong CI, framework ghi ảnh mong đợi, ảnh thực tế và ảnh khác biệt vào thư mục `failures/`. Không tải chúng lên thì bạn chỉ còn nước đoán; có chúng thì bạn tải ba file PNG và nhìn ra vấn đề trong mười giây.

Golden cũng **phụ thuộc font và phụ thuộc nền tảng**. Hãy sinh chúng trên Linux trong CI, hoặc chấp nhận rằng golden sinh trên Mac sẽ hỏng trên runner Ubuntu. Nếu sinh cục bộ, chạy `flutter test --update-goldens` trên đúng hệ điều hành mà CI dùng là con đường đáng tin duy nhất.

## Canh gác mã sinh tự động

Nếu dự án dùng `build_runner`, CI phải kiểm tra đầu ra đã commit khớp với mã nguồn:

```yaml
      - name: Kiểm tra mã sinh còn mới
        run: |
          dart run build_runner build --delete-conflicting-outputs
          if ! git diff --quiet; then
            echo "Mã sinh đã cũ. Hãy chạy build_runner và commit."
            git diff --stat
            exit 1
          fi
```

Bước này bắt được lỗi "chạy trên máy tôi mà" phổ biến nhất trong dự án dùng sinh mã: ai đó sửa một model, quên sinh lại, và file `.g.dart` đã commit không còn khớp.

## Build theo ma trận

```yaml
  build:
    needs: [analyze, test]
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            target: apk
            cmd: flutter build apk --release --split-per-abi
          - os: macos-latest
            target: ios
            cmd: flutter build ios --release --no-codesign
          - os: ubuntu-latest
            target: web
            cmd: flutter build web --release
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true
      - run: flutter pub get
      - run: ${{ matrix.cmd }}
```

`fail-fast: false` là cố ý — khi bản web hỏng, bạn muốn biết iOS có hỏng theo không, chứ không muốn nó bị huỷ.

`--no-codesign` cho iOS cho phép kiểm tra biên dịch ở mọi PR mà không phải quản chứng chỉ. Việc ký thuộc về job release, nơi có secret.

## Ký mà không rò rỉ

Job release là nơi secret xuất hiện, và là nơi cần cẩn thận:

```yaml
  release:
    if: startsWith(github.ref, 'refs/tags/v')
    needs: [build]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version-file: pubspec.yaml
          cache: true

      - name: Khôi phục keystore
        env:
          KEYSTORE_B64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}
        run: echo "$KEYSTORE_B64" | base64 --decode > android/app/upload-keystore.jks

      - name: Ghi cấu hình ký
        env:
          STORE_PASSWORD: ${{ secrets.ANDROID_STORE_PASSWORD }}
          KEY_PASSWORD: ${{ secrets.ANDROID_KEY_PASSWORD }}
          KEY_ALIAS: ${{ secrets.ANDROID_KEY_ALIAS }}
        run: |
          cat > android/key.properties <<EOF
          storePassword=$STORE_PASSWORD
          keyPassword=$KEY_PASSWORD
          keyAlias=$KEY_ALIAS
          storeFile=upload-keystore.jks
          EOF

      - run: flutter build appbundle --release
```

Ba quy tắc không thương lượng:

1. **Secret đi qua `env:`, không bao giờ nhúng thẳng vào chuỗi `run:`.** Một `${{ secrets.X }}` nội tuyến trong lệnh shell có thể lọt vào trace hoặc thông báo lỗi.
2. **Không bao giờ `echo` một secret.** GitHub che các giá trị secret đã biết trong log, nhưng chỉ với bản khớp chính xác — một mảnh base64 hay một giá trị đã biến đổi thì không được che.
3. **Chặn cổng job bằng tag.** `if: startsWith(github.ref, 'refs/tags/v')` nghĩa là một PR từ fork không bao giờ chạm tới bước động vào vật liệu ký.

Nếu mục tiêu phân phối của bạn hỗ trợ OIDC và chứng thực ngắn hạn, hãy dùng cách đó thay cho secret lưu dài hạn.

## Điều gì khiến nó nhanh

`cache: true` của `subosito/flutter-action` cache chính SDK. Thêm pub cache và Gradle cache cho job Android:

```yaml
      - uses: actions/cache@v4
        with:
          path: |
            ~/.pub-cache
            ~/.gradle/caches
          key: ${{ runner.os }}-deps-${{ hashFiles('**/pubspec.lock', '**/*.gradle*') }}
          restore-keys: ${{ runner.os }}-deps-
```

Khoá theo `pubspec.lock` thay vì `pubspec.yaml` là điều quan trọng: chính file lock mới quyết định phiên bản đã resolve, nên cache khoá theo nó không bao giờ cũ theo nghĩa đáng lo. Tiền tố `restore-keys` cho bạn một lần trúng một phần khi lock đổi, tốt hơn nhiều so với cache nguội.

## Câu hỏi thường gặp

**CI có nên chạy integration test không?**

Chỉ khi bạn có dàn thiết bị thật hoặc thiết lập giả lập đáng tin, và chỉ chạy theo lịch hoặc trên main. Chạy integration test ở mọi PR là cách nhanh nhất dạy cả đội phớt lờ build đỏ.

**Vì sao `flutter analyze` pass ở máy tôi mà hỏng trong CI?**

Thường là analysis server cục bộ đã cũ, hoặc file sinh có ở máy nhưng chưa commit. Bước kiểm build_runner ở trên bắt trường hợp thứ hai; khởi động lại analyzer bắt trường hợp thứ nhất.

**`--fatal-infos` có quá nghiêm không?**

Với dự án mới thì không. Với dự án cũ đang có hàng trăm info, hãy áp dụng sau một đợt dọn dẹp, nếu không bạn sẽ chỉ tắt job đó đi.

**Làm sao để workflow không chạy khi chỉ đổi tài liệu?**

`paths-ignore` ở phần trigger. Cẩn thận: nếu một status check bắt buộc không bao giờ chạy thì PR không merge được. Hãy thêm một job luôn pass trùng tên, hoặc đừng đặt check đó là bắt buộc.

**Pipeline có nên tự động phát hành lên store không?**

Build và tải lên một kênh test nội bộ tự động thì hợp lý. Đẩy lên production tự động là quyết định chính sách nên có con người tham gia, và tôi sẽ không mặc định nối dây cho việc đó.

---

*Các tính năng GitHub Actions, lệnh build Flutter, cờ của `dart format` và cách thiết lập ký mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Cách chia bốn job, khuyến nghị `--fatal-infos`, bước canh gác mã sinh và các quy tắc xử lý secret là nhận định riêng của tôi khi duy trì pipeline dạng này. Phiên bản action và ảnh runner có thay đổi — hãy ghim thứ bạn phụ thuộc và kiểm tra lại phiên bản trước khi sao chép nguyên xi.*
