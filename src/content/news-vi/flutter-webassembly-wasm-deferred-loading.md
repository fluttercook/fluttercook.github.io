---
title: "Ship Flutter Web trên WebAssembly: cuộc migrate, trình duyệt, và hai cái header"
description: "Wasm đang trên đường thành đích web mặc định của Flutter. Đây là pipeline build thật, cuộc migrate sang package:web, hỗ trợ trình duyệt kể cả lỗ hổng iOS, và deferred loading."
seoDescription: "Hướng dẫn WebAssembly cho Flutter: flutter build web --wasm, hỗ trợ WasmGC của trình duyệt, migrate dart:html sang package:web, header COOP/COEP cho đa luồng, và Wasm deferred loading."
keywords: ["flutter webassembly", "flutter build web wasm", "hỗ trợ wasmgc trình duyệt", "migrate package:web", "dart:js_interop", "deferred loading flutter web"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🕸️"
tags: ["Flutter 3.47", "Flutter", "Web", "WebAssembly", "Hiệu năng"]
sources:
  - name: "Compiling to WebAssembly — flutter.dev docs"
    url: "https://docs.flutter.dev/platform-integration/web/wasm"
  - name: "Announcing Dart 3.13 — Dart Blog"
    url: "https://dart.dev/blog/announcing-dart-3-13"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "package:web on pub.dev"
    url: "https://pub.dev/packages/web"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

WebAssembly là canh bạc lớn nhất trong lộ trình Flutter 2026, và 3.47 đẩy nó tiến thêm một bước với deferred loading thử nghiệm. Khảo sát Q2 2026 chấm Web ở mức **72% hài lòng** — điểm nền tảng thấp thứ nhì — và hiệu năng tải là một phần lớn của lý do. Wasm là phương án sửa được nhắm tới.

Nhưng ship Wasm hôm nay không phải là bật một cái cờ. Đó là một cuộc migrate, một ma trận hỗ trợ trình duyệt với một lỗ hổng lớn, và hai HTTP header mà phần lớn mọi người quên.

## Các lệnh build

```bash
# Phát triển
flutter run -d chrome --wasm

# Production
flutter build web --wasm

# Production, kèm symbolication cho giám sát lỗi
flutter build web --wasm --source-maps

# Staging/QA — stack trace đọc được, binary lớn hơn ~47%
flutter build web --wasm --no-strip-wasm
```

Dùng `--source-maps` cho bất cứ thứ gì bạn trỏ Sentry hay dịch vụ tương tự vào; nó sinh `main.dart.wasm.map`. Chỉ dùng `--no-strip-wasm` ở staging — chi phí dung lượng là thật.

Flutter 3.47 cũng thêm deferred loading thử nghiệm:

```bash
flutter build web --release --wasm --enable-wasm-deferred-loading
```

Ở tầng Dart, đây cùng là năng lực đã ra mắt dạng preview trong Dart 3.13 (`dart compile wasm -O2 --enable-deferred-loading`), được ghi nhận cho cải thiện đáng kể thời gian tải trang lần đầu so với `dart2js` với ứng dụng lớn. Với app lớn, đây là ranh giới giữa việc Wasm nhanh hơn trên lý thuyết và nhanh hơn thật ở chỉ số người dùng cảm nhận.

## Ma trận trình duyệt, và vấn đề iOS

Đầu ra Wasm của Flutter cần **WasmGC**. Hỗ trợ hiện tại:

| Trình duyệt | Trạng thái |
| --- | --- |
| Chromium / V8 | Hỗ trợ, từ bản 119+ |
| Firefox | Đã công bố, hiện bị chặn bởi một lỗi đã biết |
| Safari | Hỗ trợ WasmGC, nhưng có lỗi tương thích |
| Trình duyệt trên iOS | **Không chạy được** — mọi trình duyệt iOS đều dùng WebKit |

Hãy đọc lại dòng cuối. Không phải "Safari trên iOS"; là *mọi* trình duyệt trên iOS, vì Apple bắt buộc dùng WebKit. Nếu lưu lượng web của bạn nghiêng về di động, một phần đáng kể người dùng sẽ không chạy bản Wasm của bạn chút nào.

Chính vì thế fallback rất quan trọng: **ngay cả với `--wasm`, Flutter vẫn biên dịch ra JavaScript.** Nếu không phát hiện WasmGC lúc chạy, bản JS sẽ chạy. Bạn đang ship cả hai, và trình duyệt chọn. Điều đó tốt cho tính đúng đắn và tệ cho ai hy vọng Wasm giảm dung lượng triển khai.

Để xác nhận một phiên chạy theo đường nào:

```dart
const isRunningWithWasm = bool.fromEnvironment('dart.tool.dart2wasm');
```

Hãy log nó. Nếu không, bạn sẽ tối ưu một nhánh code mà phần lớn người dùng chẳng bao giờ chạm tới.

## Cuộc migrate thật sự: thoát khỏi dart:html

Đây mới là phần việc. Wasm sẽ không biên dịch nếu app của bạn import thư viện web không được hỗ trợ.

| Cũ | Thay bằng |
| --- | --- |
| `dart:html` | `package:web` |
| `dart:js`, `package:js` | `dart:js_interop` |

Flutter cho bạn cảnh báo sớm mà không cần build Wasm — chạy `flutter build web` thường sẽ thực hiện một lượt **Wasm dry run**:

```
Wasm dry run failed:
Found incompatibilities with WebAssembly.

package:my_app/main.dart 1:1 - dart:html unsupported (0)
```

Hãy chạy nó ngay hôm nay, kể cả khi bạn chưa có kế hoạch Wasm. Đó là một lượt kiểm toán miễn phí cho cây dependency của bạn.

Khi biên dịch đầy đủ thất bại, hãy bỏ qua stack trace và tìm **Context tree** — nó nêu tên chuỗi package đã kéo thư viện không tương thích vào:

```
Context: The unavailable library 'dart:html' is imported through these packages:
    main.dart => package:my_app => dart:html
```

Thường đó là một dependency gián tiếp, không phải code của bạn. Để migrate dần, conditional import cho phép hai thế giới cùng tồn tại:

```dart
import 'fallback.dart'
  if (dart.library.js) 'legacy_web_interop.dart'
  if (dart.library.js_interop) 'wasm_web_interop.dart';
```

## Hai cái header ai cũng quên

App Flutter Wasm có thể render trên **nhiều luồng** — nhưng chỉ khi server của bạn gửi đúng header cross-origin:

| Header | Giá trị |
| --- | --- |
| `Cross-Origin-Embedder-Policy` | `credentialless` hoặc `require-corp` |
| `Cross-Origin-Opener-Policy` | `same-origin` |

Thiếu một trong hai, đa luồng lặng lẽ không xảy ra. App vẫn chạy; chỉ là chậm hơn con số benchmark bạn đọc được. Hãy kiểm tra chúng trong cấu hình CDN hoặc reverse proxy, không chỉ ở môi trường dev — đây là cái bẫy kinh điển "nhanh trên localhost, chậm trên production".

Lưu ý `require-corp` sẽ làm hỏng các tài nguyên bên thứ ba nhúng vào mà không khai báo header CORP. Nếu bạn nhúng nhiều nội dung ngoài, `credentialless` thường là lựa chọn thực dụng.

## Khác biệt lúc chạy đáng biết

`package:web` và `dart:js_interop` dưới Wasm không giống hệt backend JS:

- **Kiểm tra `is` / `as` hành xử khác** trên các kiểu JS interop
- **Zone lan truyền trong callback khác đi**

Không cái nào làm hỏng một app thông thường, nhưng cả hai sẽ cắn đoạn code làm những trò thông minh với kiểm tra kiểu qua ranh giới interop. Hãy test riêng lớp interop thay vì cho rằng chúng ngang bằng.

## Kế hoạch triển khai của bạn

1. **Chạy `flutter build web` ngay hôm nay** và đọc kết quả Wasm dry run. Đó là backlog migrate của bạn.
2. **Cập nhật `web/index.html`** theo phần khởi tạo Flutter hiện hành, hoặc sinh lại bằng `flutter create . --platforms web`.
3. **Migrate code của chính bạn** từ `dart:html` sang `package:web` và từ `dart:js` sang `dart:js_interop`.
4. **Truy các thủ phạm gián tiếp** được nêu trong Context tree. Mở issue cho những dependency còn import `dart:html`.
5. **Cấu hình header COOP và COEP** ở tầng phục vụ production, rồi kiểm chứng bằng tab network.
6. **Build với `--wasm --source-maps`** và nối file map vào hệ thống giám sát lỗi.
7. **Log `dart.tool.dart2wasm`** và đo xem bao nhiêu phần trăm phiên thật sự đi đường Wasm.
8. **Thử `--enable-wasm-deferred-loading`** nếu bundle của bạn lớn, và đo thời gian tải trang lần đầu thay vì tổng dung lượng.

## Kết luận

Wasm nhanh hơn thật, và lộ trình chỉ tới việc nó thành mặc định. Nhưng hôm nay nó là một bản build cộng thêm, không phải thay thế: bạn vẫn ship JS, người dùng iOS vẫn nhận đường JS bất kể thế nào, và phần thắng hiệu năng phụ thuộc hai cái header mà phần lớn nhóm chưa đặt. Việc giá trị nhất bạn có thể làm tuần này chẳng tốn gì — chạy `flutter build web` và đọc kết quả dry run. Dù bạn có ship Wasm quý này hay không, danh sách dependency dính `dart:html` đó là món nợ sớm muộn cũng phải trả.
