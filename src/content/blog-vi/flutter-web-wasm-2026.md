---
title: "Flutter web biên dịch sang WebAssembly: được gì, mất gì"
description: "flutter build web --wasm không phải một cờ tối ưu — nó đổi dart2js lấy dart2wasm, đòi trình duyệt hỗ trợ WasmGC, và rút dart:html ra khỏi cây dependency của bạn. Đây là cơ chế bên dưới, một ví dụ interop thật với package:web và @JS, cùng những giới hạn mà không cờ biên dịch nào xoá được."
seoDescription: "flutter build web --wasm thực tế: dart2wasm so với dart2js, cửa ải WasmGC và bản dự phòng JS, bỏ dart:html sang package:web, và giới hạn thật của Flutter web."
keywords:
  - flutter build web wasm
  - dart2wasm và dart2js
  - wasmgc trình duyệt hỗ trợ
  - package web dart js interop
  - thay thế dart html
  - flutter web seo hạn chế
category: "Phân tích"
topic: "Flutter Web"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🌐"
tags: ["Flutter", "Web", "WebAssembly", "Dart", "Interop"]
sources:
  - name: "Flutter — Support for WebAssembly (Wasm)"
    url: "https://docs.flutter.dev/platform-integration/web/wasm"
  - name: "Flutter — Web renderers"
    url: "https://docs.flutter.dev/platform-integration/web/renderers"
  - name: "Dart — JavaScript interop"
    url: "https://dart.dev/interop/js-interop"
  - name: "Dart — package:web"
    url: "https://dart.dev/interop/js-interop/package-web"
  - name: "package:web trên pub.dev"
    url: "https://pub.dev/packages/web"
  - name: "MDN — WebAssembly"
    url: "https://developer.mozilla.org/en-US/docs/WebAssembly"
  - name: "WebAssembly — lộ trình tính năng"
    url: "https://webassembly.org/roadmap/"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "web-tech-to-mobile-app-2026"
    title: "Dùng công nghệ web để làm app mobile: bản đồ kỹ thuật 2026"
draft: false
---

`flutter build web --wasm` trông như một cờ bạn bật lên cho nhanh. Thực chất nó gần với đổi runtime hơn. Đứng sau cờ đó là **dart2wasm**, một compiler khác dart2js, sinh mã cho một cỗ máy khác, với một tập thư viện lõi khác hẳn. Code hôm qua build được hôm nay có thể hỏng — không phải vì nó sai, mà vì nó import một thư viện không còn tồn tại trên target mới.

Chi phí migration hầu như không nằm ở code của bạn. Phần lớn code ứng dụng không đụng trực tiếp vào `dart:html`; nó gọi một package, package đó gọi một package khác, và cái cuối cùng mới đụng. Nên lần build `--wasm` đầu tiên của một app thật thường chết ở đâu đó ba tầng sâu trong cây dependency, trong một file bạn chưa từng mở, thuộc một package bạn không hề chủ động chọn.

Và nằm sau tất cả những chuyện đó là điều không cờ biên dịch nào thay đổi được: app Flutter web vẽ lên một canvas. Thứ tới trình duyệt là một ứng dụng, không phải một tài liệu. Riêng sự thật đó kéo theo hầu hết các giới hạn thẳng thắn ở dưới — first paint, SEO, tìm trong trang, autofill — và nó không phụ thuộc vào compiler nào sinh ra chúng.

Bài này nói về việc cờ đó thực sự làm gì, yêu cầu WasmGC nghĩa là ai chạy được bản build của bạn, việc mất `dart:html` tốn bao nhiêu trong một app đang chạy thật, một ví dụ interop dùng được, và những trường hợp mà câu trả lời đúng không phải Flutter.

## `--wasm` đổi compiler, không phải đổi mức tối ưu

dart2js nhận chương trình của bạn và sinh ra JavaScript. Mô hình class của Dart bị dàn phẳng lên các object JS, và code sinh ra sống theo luật động của JS engine: hidden class, call site megamorphic, và mọi con số bên dưới đều là double.

dart2wasm thì sinh ra một module WebAssembly. Điều quan trọng: nó không nhắm mô hình linear memory kiểu cũ — kiểu Emscripten, nơi chương trình mang theo heap riêng trong một `ArrayBuffer` lớn và nhét luôn garbage collector của mình vào binary. Nó nhắm **WasmGC**, đề xuất cho WebAssembly các kiểu struct và array do engine quản lý và do chính garbage collector của trình duyệt thu hồi.

Lựa chọn đó kéo theo vài hệ quả đáng hiểu, vì chúng giải thích cả cái được lẫn cái cửa ải:

- Object Dart trở thành struct Wasm. Offset của field và dispatch ảo được compiler giải quyết dựa trên kiểu đã khai báo, thay vì để JS engine đoán hình dạng object lúc chạy.
- Không có garbage collector nào nằm trong bundle của bạn. Collector sẵn có của trình duyệt quản lý trực tiếp object Dart.
- `int` là số nguyên 64-bit thật, giống trên Dart VM, thay vì một double JavaScript khoác kiểu Dart.

Cái nó không phải là "tốc độ native". Wasm là một target biên dịch với tập lệnh tốt và mô hình bộ nhớ có kiểu. Nó bỏ đi một nhóm overhead trong *runtime của ngôn ngữ*. Nó không làm gì cho layout, rasterisation, độ trễ mạng, hay số byte bạn phải tải trước khi có pixel đầu tiên.

| | dart2js | dart2wasm (`--wasm`) |
|---|---|---|
| Output | `main.dart.js` | `main.dart.wasm` cộng một module `.mjs` hỗ trợ |
| Bộ nhớ | object JS, GC của JS engine | struct WasmGC, GC của trình duyệt |
| `int` | bên dưới là double JavaScript | số nguyên 64-bit thật |
| `dart:html`, `dart:js`, `dart:js_util` | còn dùng được (đã deprecated) | không có |
| Yêu cầu trình duyệt | mọi trình duyệt hiện đại | phải hỗ trợ WasmGC |
| JS interop | gọi thẳng sang JS | giá trị phải chuyển đổi ở ranh giới Wasm/JS |

Dòng cuối là chỗ nhiều người vấp. Interop dưới dart2wasm không miễn phí: string, list và closure Dart đều phải marshal qua ranh giới. Một lời gọi interop mỗi frame nằm trong hot path, vốn cảm giác miễn phí dưới dart2js, giờ không còn miễn phí nữa. Nó vẫn nhanh — chỉ là không còn bằng không.

## WasmGC là cửa ải cứng, và bản dự phòng JS là lý do bạn vẫn ship được

WasmGC là tính năng của engine trình duyệt. Bạn không polyfill được, không shim được, không nhờ bundler lách được. Hoặc engine hiện thực đề xuất đó, hoặc module của bạn không instantiate nổi.

Chromium ship nó ở bản 119 và Firefox ở bản 120, đều vào cuối 2023. Safari đến muộn hơn khá nhiều, và nếu một phần đáng kể traffic của bạn nằm trên iOS hoặc macOS Safari đời cũ, hãy kiểm tra tình trạng hiện tại trên MDN hoặc lộ trình WebAssembly thay vì tin bất kỳ bài blog nào, kể cả bài này.

Cách Flutter xử lý là ship cả hai. Một bản build `--wasm` sinh ra output WebAssembly *và* một bản dự phòng dart2js, rồi script bootstrap dò tính năng của trình duyệt và nạp bản nào chạy được. Hãy build app rồi liệt kê thư mục `build/web` để xác nhận phiên bản Flutter của bạn thực sự sinh ra những gì — hành vi này đã đổi qua các bản phát hành, và nội dung thư mục mới là sự thật.

Kéo theo hai hệ quả thực tế.

**Bản deploy của bạn mang hai bản biên dịch của cùng một app.** Mỗi người dùng chỉ tải một bản — loader quyết định trước khi fetch các artefact lớn — nhưng bucket, CDN và thời gian build của bạn gánh cả hai. Nếu bạn biết chắc toàn bộ người dùng đều có WasmGC (ví dụ một công cụ nội bộ với đội máy được quản lý), bản dự phòng là gánh nặng chết mà bạn vẫn trả tiền để lưu và để invalidate.

**Bạn có hai bản build với hai ngữ nghĩa số học khác nhau.** dart2js ánh xạ `int` lên double JS; dart2wasm dùng số nguyên 64-bit thật. Code đụng tới số nguyên lớn, thao tác bit, hashing, hay các giá trị ID gần hoặc vượt 2^53 có thể hành xử khác nhau tuỳ người dùng nạp artefact nào. Nếu bạn ship bản dự phòng, ma trận test phải có một trình duyệt rơi vào nhánh đó.

Một chi tiết triển khai tốn cả buổi chiều nếu bỏ sót: server phải trả file `.wasm` với content type `application/wasm`. Một số static host không làm mặc định, và lỗi hiện ra dưới dạng lỗi instantiate chứ không nói gì tới "MIME type".

## `dart:html` biến mất, nên migration thật ra là một cuộc rà soát dependency

Dưới dart2wasm, các thư viện web cũ đơn giản là không có: `dart:html`, `dart:js`, `dart:js_util`, `dart:svg`, `dart:indexed_db`, `dart:web_audio`, `dart:web_gl`. Thay thế là **`package:web`** cho các API trình duyệt và **`dart:js_interop`** cho ranh giới với JavaScript.

`package:web` được sinh từ các định nghĩa Web IDL, nghĩa là tên gọi bám theo nền tảng chứ không theo lớp bọc viết tay đời cũ của Dart. Bạn dùng `document.querySelector(...)`, `window.localStorage.setItem(...)`, `element.remove()` — ít đường tắt kiểu Dart hơn, nhưng ánh xạ dễ đoán hơn hẳn khi bạn vừa code vừa mở MDN.

Code của chính bạn thường chỉ là một diff nhỏ. Cây dependency mới là phần việc. Hai thứ giúp được:

- pub.dev đánh dấu package tương thích WebAssembly ngay trên trang package, nên bạn kiểm tra được trước khi quyết định dùng.
- Compiler nêu đích danh thư viện gây lỗi và package chứa nó, nên lần build hỏng đầu tiên là một danh sách việc cần làm chứ không phải một bí ẩn.

Nếu bạn maintain một package hỗ trợ cả web lẫn native, khoá điều kiện trong conditional import cũng đổi. `dart.library.html` là false dưới dart2wasm; điều kiện đúng trên mọi compiler web là `dart.library.js_interop`:

```dart
export 'src/storage_stub.dart'
    if (dart.library.js_interop) 'src/storage_web.dart'
    if (dart.library.io) 'src/storage_io.dart';
```

Để rẽ nhánh lúc chạy trong code dùng chung, `package:flutter/foundation.dart` cung cấp `kIsWeb` cho câu hỏi "tôi có đang ở trên web không" và `kIsWasm` cho câu hỏi "cái này có phải do dart2wasm biên dịch không". Hai câu hỏi khác nhau, và thường bạn cần câu đầu.

Khi một dependency gián tiếp chưa migrate, bạn có bốn lựa chọn và không có cái thứ năm: nâng lên phiên bản đã migrate, override sang một fork đã migrate, thay package khác, hoặc bê thẳng vài hàm bạn thực sự dùng vào codebase của mình. Hãy dự trù ít nhất một trong bốn cho bất kỳ app nào có danh sách dependency không tầm thường.

## Interop thực tế trông như thế nào

Hai tầng. Dùng `package:web` khi thứ bạn cần là một API của trình duyệt. Chỉ với tay sang `dart:js_interop` và `@JS` khi thứ bạn cần là một thư viện JavaScript do chính bạn nạp vào.

API trình duyệt trước — code này bình thường và nhàm chán:

```dart
import 'package:web/web.dart' as web;

/// Removes the static loading markup you put in web/index.html.
void hideBootSplash() {
  web.document.querySelector('#boot-splash')?.remove();
}

void rememberTheme(String value) {
  web.window.localStorage.setItem('theme', value);
}

String? savedTheme() => web.window.localStorage.getItem('theme');
```

Giờ tới một thư viện JS bên thứ ba. Giả sử nhà cung cấp analytics của bạn phát hành một script tag và expose một biến global, bạn nạp nó từ `web/index.html`:

```html
<script src="https://cdn.example-vendor.com/telemetry.js"></script>
```

Bạn mô tả hình dạng của nó cho Dart bằng một extension type và một khai báo `external`. Không có gì được sinh tự động, không có gì được đối chiếu với thư viện thật — extension type là một góc nhìn ở compile time lên một `JSObject`, nên bạn đang khẳng định một hình dạng, và bạn chịu trách nhiệm khẳng định cho đúng:

```dart
import 'dart:js_interop';

/// A typed view over the plain JS object the vendor expects.
extension type TrackProps._(JSObject _) implements JSObject {
  external factory TrackProps({String screen, String locale});
}

/// Binds to `window.appTelemetry.track(name, props)`.
@JS('appTelemetry.track')
external void track(String name, TrackProps props);

void logScreenView(String screen, String locale) {
  track('screen_view', TrackProps(screen: screen, locale: locale));
}
```

Ba quy tắc tiết kiệm thời gian ở đây. Kiểu nguyên thuỷ — `String`, `int`, `double`, `bool` — được phép xuất hiện thẳng trong chữ ký `external` và sẽ được chuyển đổi hộ bạn. Thứ phức tạp hơn thì phải qua ranh giới một cách tường minh: `.toJS` khi đi ra, `.toDart` khi đi vào, kể cả `JSPromise` sang `Future` và closure Dart sang `JSFunction`. Còn khi hình dạng thực sự động, `jsify()` / `dartify()` cùng các hàm `getProperty` / `setProperty` trong `dart:js_interop_unsafe` làm được việc — với cái giá là mọi lỗi bị đẩy từ compile time xuống runtime, đúng cái đánh đổi mà chữ "unsafe" trong tên thư viện đang cảnh báo bạn.

## Dự trù chi phí migration cho một app đang chạy

Trình tự ít lãng phí thời gian nhất:

1. Chạy `flutter build web --wasm` trên codebase hiện tại và đọc lỗi. Làm việc này trước khi ước lượng bất cứ thứ gì.
2. Chia danh sách thành code bạn sở hữu và code bạn không. Nửa đầu là việc bạn xếp lịch được; nửa sau là việc bạn chỉ có thể thương lượng.
3. Với mỗi dependency hỏng, xem pub.dev có bản mới không, rồi tới issue tracker, rồi tới một lựa chọn thay thế còn được maintain. Quyết định fork hay thay sớm, vì fork là một khoản chi phí vĩnh viễn.
4. Viết lại các file web-only của bạn theo `package:web`.
5. Test lúc chạy, không chỉ lúc build. Code `dart:js_util` cũ tra cứu thành viên bằng chuỗi vẫn compile ngon lành rồi chết lúc runtime; compiler không cứu bạn ở đó được.
6. Test cả nhánh dự phòng, trên một trình duyệt không có WasmGC, nếu bạn có phục vụ nhánh đó.

Vài thứ không đổi và đáng nói ra để không ai lên kế hoạch dựa vào chúng: web không có isolate dưới cả hai compiler, `dart:io` không dùng được, `compute()` chạy callback ngay trên main thread chứ không chuyển đi đâu cả, và `dart:mirrors` không tồn tại. Ngoài ra hãy đọc release notes phiên bản Flutter của bạn trước khi lên kế hoạch dựa vào code splitting bằng `deferred as` — cách dart2wasm xử lý deferred import không phải lúc nào cũng giống dart2js, và nếu lazy-load một route nặng là phần cốt lõi trong chiến lược giảm dung lượng của bạn, hãy kiểm chứng thay vì giả định.

## Renderer vẫn là canvas, và đó mới là trần thật sự

Flutter web vẽ qua Skia. Với `--wasm`, nghĩa là **skwasm**, đường vẽ chạy thuần Wasm, thay cho bản CanvasKit do JS điều khiển. Renderer HTML dựa trên DOM đã bị gỡ ở Flutter 3.29, nên "cứ render ra element DOM thật đi" không còn là một câu trả lời có sẵn nữa.

Đường render đa luồng đòi **cross-origin isolation** — hai header `COOP` và `COEP`. Bật chúng lên không phải một thay đổi cục bộ: mọi iframe, ảnh, font và script bên thứ ba mà trang bạn nạp đều phải mang header CORP hoặc CORS phù hợp, nếu không chúng ngừng tải. Player YouTube nhúng, iframe thanh toán và tag quảng cáo là những nạn nhân quen thuộc. Hãy kiểm kê những gì trang bạn nhúng trước khi cam kết với mấy cái header đó.

Rồi tới các đặc tính đi kèm chuyện vẽ lên canvas, tất cả đều đúng bất kể compiler nào:

- **First paint bị buộc vào bootstrap.** Trình duyệt tải engine và app, khởi tạo, rồi mới vẽ. Không có HTML render sẵn từ server để nhìn trong lúc chờ, và không có streaming.
- **Không có chữ trong DOM.** Crawler tìm kiếm và bot xem trước link không chạy JavaScript sẽ chỉ thấy `index.html` của bạn, hết. Thẻ Open Graph riêng cho từng route đòi xử lý phía server, vì với con bot thì thứ server trả về cho `index.html` là toàn bộ câu chuyện.
- **Các tính năng trình duyệt làm việc trên DOM không thấy nội dung của bạn.** Ctrl+F, bôi đen chọn chữ, extension dịch trang, và autofill của trình quản lý mật khẩu đều đang làm việc với một mớ markup không chứa thứ người dùng đang nhìn.
- **Accessibility là một cây song song.** Flutter dựng một cây semantics trong DOM cho công nghệ trợ giúp, và bạn có thể bật cưỡng bức bằng `SemanticsBinding.instance.ensureSemantics()`. Nó tồn tại cho screen reader. Nó không phải bề mặt SEO, và xây chiến lược nội dung lên đó là một canh bạc tồi.

## Khi nào Flutter web là lựa chọn sai

Quy tắc quyết định rất ngắn. Nếu giá trị của trang nằm ở **nội dung và khả năng được tìm thấy**, thì DOM chính là sản phẩm, và bạn nên dùng công cụ sinh ra DOM. Nếu giá trị của trang nằm ở **một ứng dụng tình cờ chạy trong tab trình duyệt**, canvas là nền hợp lý và Flutter đổi lại cho bạn một codebase dùng chung mọi nền tảng.

| Bạn đang làm gì | Flutter web với `--wasm` | Nên dùng thứ khác |
|---|---|---|
| Dashboard nội bộ sau màn đăng nhập | Hợp — không cần SEO, trình duyệt đã biết trước | |
| Công cụ thiết kế, vẽ sơ đồ, kiểu canvas | Hợp — đằng nào bạn cũng phải vẽ pixel | |
| Bản web đi kèm của một app Flutter sẵn có | Hợp — codebase đã có rồi | |
| Trang marketing, blog, tài liệu | | React/Next, Astro, HTML thuần — nội dung phải nằm trong DOM |
| Cửa hàng hoặc bất cứ thứ gì sống nhờ thứ hạng tìm kiếm | | Một web framework render phía server |
| Luồng form công khai dài | | Form HTML, để có autofill và trình quản lý mật khẩu |
| Widget nhúng vào trang của người khác | | JS thuần — payload của Flutter quá nặng cho việc này |

Trường hợp giữa khó chịu nhất là sản phẩm tiêu dùng vừa thực sự là một app vừa cần được tìm thấy. Tách đôi — một site marketing và nội dung tĩnh ở đường dẫn gốc, app Flutter đặt ở subpath hoặc subdomain — thường rẻ hơn và thành thật hơn là cố bắt một tấm canvas lên top tìm kiếm.

## FAQ

**Tôi có phải chuyển sang `package:web` không nếu không bao giờ dùng `--wasm`?**
Cuối cùng thì có, và bạn nên tách hai quyết định này ra. `dart:html` đã deprecated với tất cả mọi người, không riêng gì target Wasm, nên chuyển sang `package:web` và `dart:js_interop` là phần bảo trì bạn nợ dù thế nào. Làm việc đó trước cũng biến câu hỏi `--wasm` thành một thí nghiệm bật cờ build thay vì cả một dự án.

**`--wasm` có làm app tôi nhanh hơn không?**
Nó đổi chỗ mà runtime của ngôn ngữ tiêu thời gian — truy cập field có kiểu, không phải ship garbage collector, số nguyên thật — và nó không làm gì cho layout, rasterisation, tải asset hay số vòng round trip mạng. Việc đó có hiện lên trong app của bạn hay không phụ thuộc hoàn toàn vào chuyện thực thi Dart có phải nút thắt của bạn không. Hãy profile chính bản build bạn ship, đừng tin một con số lấy từ app của người khác.

**Trình duyệt không có WasmGC thì sao?**
Nó nạp bản dự phòng dart2js do chính lần build đó sinh ra, nên app vẫn chạy. Nghĩa là một phần người dùng của bạn đang chạy output của một compiler khác, với ngữ nghĩa `int` khác, và nhánh đó phải nằm trong ma trận test. Kiểm tra `build/web` để xác nhận phiên bản Flutter của bạn có sinh ra bản dự phòng trước khi trông cậy vào nó.

**Tôi dùng được thư viện npm trong app Flutter web không?**
Được, bằng cách tự nạp nó qua script tag trong `web/index.html` rồi khai báo hình dạng của nó bằng extension type và `@JS`. Không có tích hợp bundler và không có module resolution — bạn tự lo thứ tự nạp, và bạn tự chịu trách nhiệm về độ đúng của hình dạng đã khai, vì không có gì đối chiếu khai báo `external` của bạn với thư viện thật.

**Flutter web có làm SEO được không?**
Với một ứng dụng sau màn đăng nhập thì câu hỏi không đặt ra. Với nội dung công khai, hãy coi như không: nội dung không nằm trong DOM, crawler không chạy JavaScript chỉ thấy một cái vỏ rỗng, và các cách prerender chữa cháy thì mong manh và rất dễ làm sai. Hãy phục vụ nội dung từ thứ gì đó sinh ra HTML, và để dành Flutter cho phần ứng dụng.

---

*Các cơ chế mô tả ở đây — WasmGC, chuyện tách compiler, ranh giới interop, mô hình render bằng canvas — là những đặc tính ổn định của cách tiếp cận này. Các chi tiết phụ thuộc phiên bản thì không: mức hỗ trợ của trình duyệt, chính xác một bản build `--wasm` sinh ra những gì trong `build/web`, tên và cờ của renderer, cùng hành vi deferred loading đều đã đổi qua các bản Flutter và sẽ còn đổi. Hãy kiểm chứng những thứ đó với tài liệu Flutter và Dart đã dẫn ở trên cho đúng phiên bản của bạn. Phần khuyến nghị về khi nào không nên dùng Flutter web là ý kiến của tôi, rút ra từ các ràng buộc phía trên chứ không từ bất kỳ benchmark nào.*
