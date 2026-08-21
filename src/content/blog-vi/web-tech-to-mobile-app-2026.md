---
title: "Dùng công nghệ web để làm app mobile: bản đồ kỹ thuật 2026"
description: "Bốn con đường đưa HTML/CSS/JS lên điện thoại — PWA thuần, vỏ WebView, vỏ server-rendered, và loại không dùng WebView. Kèm số liệu đã kiểm chứng, hạn chót của cửa hàng, giới hạn cứng, và một danh sách những case study nổi tiếng đã chết mà ai cũng còn trích."
seoDescription: "Hướng dẫn 2026 về làm app mobile bằng công nghệ web: PWA trên iOS 26, Capacitor 8.5, Hotwire Native, TWA và Bubblewrap, hạn targetSdk 36 ngày 31/08/2026, guideline 4.2 của App Store, trần 60fps của WKWebView, luật thanh toán sau Epic v. Apple, và chuyện OTA sau khi CodePush chết."
keywords:
  - làm app mobile bằng web
  - pwa 2026
  - capacitor là gì
  - trusted web activity
  - hotwire native
  - web app lên app store
  - webview app có bị từ chối không
  - ota update react native
category: "Hướng dẫn"
topic: "Cross-platform"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-21"
emoji: "🌐"
tags: ["Web", "Mobile", "PWA", "Capacitor", "React Native", "App Store", "Hotwire"]
sources:
  - name: "WebKit — Tính năng mới trong Safari 26: mọi website đều có thể là web app"
    url: "https://webkit.org/blog/17333/webkit-features-in-safari-26-0/"
  - name: "WebKit — Tracking Prevention (web app trên Home Screen được miễn giới hạn 7 ngày)"
    url: "https://webkit.org/tracking-prevention/"
  - name: "Apple — App Review Guidelines"
    url: "https://developer.apple.com/app-store/review/guidelines/"
  - name: "Google Play — yêu cầu target API level"
    url: "https://developer.android.com/google/play/requirements/target-sdk"
  - name: "Google Play — chính sách Spam: webview và affiliate"
    url: "https://support.google.com/googleplay/android-developer/answer/9899034"
  - name: "Android — ngưỡng chất lượng của Android vitals"
    url: "https://developer.android.com/topic/performance/vitals"
  - name: "Google Play — cập nhật chính sách cho nhà phát triển phục vụ người dùng Mỹ"
    url: "https://support.google.com/googleplay/android-developer/answer/15582165"
  - name: "Ionic — Announcing Capacitor 8"
    url: "https://ionic.io/blog/announcing-capacitor-8"
  - name: "Ionic — Tương lai các sản phẩm thương mại của Ionic (ngừng bán Appflow)"
    url: "https://ionic.io/blog/important-announcement-the-future-of-ionics-commercial-products"
  - name: "37signals — Announcing Hotwire Native"
    url: "https://dev.37signals.com/announcing-hotwire-native/"
  - name: "DHH — Native mobile apps are optional for B2B startups in 2024"
    url: "https://world.hey.com/dhh/native-mobile-apps-are-optional-for-b2b-startups-in-2024-4c870d3e"
  - name: "Found Engineering — Migrating from Cordova to Capacitor"
    url: "https://found.com/engineering/migrating-from-cordova-to-capacitor"
  - name: "WebKit Bugzilla 294338 — WKWebView bị ghim quanh 60 FPS"
    url: "https://bugs.webkit.org/show_bug.cgi?id=294338"
  - name: "Microsoft — App Center retirement (CodePush ngừng hoạt động 31/03/2025)"
    url: "https://learn.microsoft.com/en-us/appcenter/retirement"
  - name: "Shorebird — FAQ về tuân thủ App Store, có trích DPLA 3.3.1(b)"
    url: "https://docs.shorebird.dev/code-push/faq/"
  - name: "Shopify Engineering — Five years of React Native at Shopify"
    url: "https://shopify.engineering/five-years-of-react-native-at-shopify"
  - name: "Discord — Supercharging Discord Mobile: our journey to a faster app"
    url: "https://discord.com/blog/supercharging-discord-mobile-our-journey-to-a-faster-app"
  - name: "Joe Masilotti — Rails developers' guide to mobile app frameworks"
    url: "https://masilotti.com/rails-developers-guide-to-mobile-app-frameworks/"
  - name: "Expo — Tài liệu EAS Update"
    url: "https://docs.expo.dev/eas-update/introduction/"
  - name: "Chrome for Developers — Trusted Web Activity"
    url: "https://developer.chrome.com/docs/android/trusted-web-activity/"
draft: false
---

Câu hỏi "công nghệ web có làm được app mobile không" đã hết hạn từ lâu. Câu hỏi còn giá trị là: **bạn đang chọn con đường nào trong bốn con đường, và bạn có biết mình đánh đổi cái gì không.**

Bài này là bản đồ kỹ thuật, không phải bài quảng cáo cho framework nào. Mọi con số đều có nguồn và mốc thời gian — và bạn sẽ thấy phần lớn công sức của bài nằm ở chỗ **gỡ bỏ những dẫn chứng đã chết mà cả ngành vẫn còn trích**.

## Bốn con đường, không phải một

Người ta hay gộp tất cả vào một chữ "hybrid". Thực ra chúng khác nhau ở tầng kiến trúc, và sự khác nhau đó quyết định mọi thứ về sau:

1. **PWA thuần** — không đóng gói gì cả. Người dùng vào bằng URL, thêm vào màn hình chính. Không qua cửa hàng.
2. **Vỏ native + WebView** — code web của bạn chạy trong `WKWebView` (iOS) hoặc Android System WebView, cầu nối JS ↔ native cho phép gọi camera, push, sinh trắc học. Đây là Capacitor, Cordova, Tauri mobile.
3. **Vỏ native + HTML render từ server** — không có bundle SPA. Server trả HTML, vỏ native biến mỗi lần bấm link thành một màn hình native. Đây là Hotwire Native.
4. **JS điều khiển view native thật, không có WebView** — React Native, Expo, NativeScript. Bạn viết JS/TS nhưng cái được vẽ ra là `UIView`/`ViewGroup`, không phải DOM.

Nhóm 4 thường bị nhét chung vào "công nghệ web" vì nó dùng JavaScript. Về mặt kỹ thuật nó không phải web: không DOM, không CSS, không WebView. Flutter còn xa hơn nữa — Dart biên dịch AOT ra mã máy, render bằng Impeller. **Nếu bạn đọc một bài so sánh nào xếp React Native hay Flutter vào nhóm "hybrid webview", đó là phép thử nhanh để biết bài đó không đáng tin.**

| | PWA thuần | Vỏ WebView | Hotwire Native | React Native |
| --- | --- | --- | --- | --- |
| Lên được App Store | Không | Có | Có | Có |
| Lên được Google Play | Qua TWA | Có | Có | Có |
| Cập nhật không qua duyệt | Toàn bộ | Phần web | Toàn bộ giao diện | Qua EAS Update |
| Truy cập native | Giới hạn theo trình duyệt | Đầy đủ qua plugin | Đầy đủ, tự viết | Đầy đủ |
| Cần macOS để build iOS | Không | Có | Có | Có |
| Dùng lại code web sẵn có | 100% | ~100% | 100% (nếu server-rendered) | Gần như 0% |

Điểm cuối cùng đáng dừng lại: **React Native không dùng lại được frontend web của bạn.** Nếu động lực chính của bạn là "tận dụng đội web sẵn có", RN không giải quyết chuyện đó — nó chỉ giúp bạn không phải viết hai lần cho iOS và Android.

## Con đường 1: PWA thuần — và cú đảo chiều của iOS 26

Đây là phần mà mọi bài viết cũ hơn tháng 9/2025 đều đã lỗi thời.

**iOS 26 xóa sạch điều kiện cài đặt.** WebKit nói nguyên văn: *"By default, every website added to the Home Screen opens as a web app"* — và *"nothing is required beyond the basics of an HTML file and a URL"*. Không cần manifest, không cần service worker ([WebKit, Safari 26](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/)).

Đổi lại là một con dao hai lưỡi: người dùng giờ có công tắc **"Open as Web App"** và họ có thể **tắt** nó. `display: standalone` không còn là bảo đảm.

Nhưng phần quan trọng nhất của PWA trên iOS không phải chuyện cài đặt cho đẹp. Nó là bốn thứ chỉ mở khóa **sau khi người dùng cài lên màn hình chính**:

- **Web Push** — có từ iOS 16.4 (16/02/2023), và đến giờ **vẫn chỉ chạy cho web app đã cài**, không chạy trong tab Safari. Không cần tài khoản Apple Developer.
- **Badge số trên icon** — `navigator.setAppBadge()`. Đây là một trong số rất ít chỗ **iOS hơn Android**: Chrome trên Android không hỗ trợ Badging API.
- **Hạn mức lưu trữ bậc trình duyệt** — khoảng 60% dung lượng đĩa cho mỗi origin, thay vì bậc WebView nhúng chỉ ~15%.
- **Và thứ đáng giá nhất: được miễn luật xóa dữ liệu sau 7 ngày.**

Điểm cuối cần nhấn mạnh vì gần như mọi tài liệu tiếng Việt đều bỏ sót. ITP của Safari xóa toàn bộ storage ghi được bằng script — IndexedDB, LocalStorage, đăng ký service worker, cache — sau 7 ngày không tương tác. Nhưng WebKit ghi rõ: *"The first-party domain of home screen web applications is exempt from ITP's 7-day cap on all script-writeable storage"* ([WebKit Tracking Prevention](https://webkit.org/tracking-prevention/)).

Nói gọn: **trên iOS, thuyết phục người dùng bấm "Thêm vào màn hình chính" là quyết định kỹ thuật có đòn bẩy cao nhất bạn có.** Nó đổi PWA của bạn từ "một tab có thể bị dọn sạch" thành "một ứng dụng có dữ liệu bền, có push, có badge".

### Cái iOS vẫn không có

Danh sách sau lấy thẳng từ cơ sở dữ liệu tính năng của WebKit, nơi chúng mang đúng trạng thái `"Not Considering"` — tức Apple không có ý định làm: **Web Bluetooth, WebUSB, WebHID, Web Serial, Web NFC.**

Cộng thêm những thứ không tồn tại trên iOS ở bất kỳ trình duyệt nào: **Background Sync, Periodic Background Sync, Web Share Target** (PWA trên iOS *gửi* chia sẻ được nhưng không *nhận* được), và **`beforeinstallprompt`** — không có cách nào bật hộp thoại cài đặt bằng code, người dùng phải tự vào menu Chia sẻ.

Nếu app của bạn cần Bluetooth để nói chuyện với thiết bị, con đường 1 dừng ở đây.

Phần tin tốt, cũng cần cập nhật vì nhiều bảng so sánh cũ ghi sai:

| API | Chrome Android | Safari iOS |
| --- | --- | --- |
| OPFS (file riêng của origin) | 109 | 16.4 |
| WebGPU | 121 (Android 12+) | **Safari 26, không cần flag** |
| View Transitions cùng trang | 111 | 18 |
| `@view-transition` khác trang | 126 | 18.2 |
| File System Access (hộp chọn file) | **132 (01/2025)** | Không |
| Web Share | 61 | 12.2 |
| Web Share Target (nhận chia sẻ) | Có | **Không** |

WebGPU đã có trên iOS từ Safari 26 và WebKit nói thẳng nó *"supersedes WebGL"*. File System Access thì ngược lại — mới lên Android từ Chrome 132 đầu 2025, iOS không có. **OPFS là mẫu số chung**: cần lưu file lớn ở cả hai bên thì dùng OPFS. Luôn feature-detect `navigator.gpu` trước khi dùng.

### Kiểm tra thực tế: những PWA huyền thoại giờ ra sao

Đây là phần khó chịu nhất của bài, và cũng là phần có giá trị nhất. Mọi bài "PWA thành công" đều trích cùng năm ca. Tôi đi kiểm từng cái, ngày 21/08/2026:

| Ca | Số liệu hay được trích | Trạng thái hôm nay |
| --- | --- | --- |
| **Twitter Lite** (2017) | +65% trang/phiên, 600 KB so với app Android 23,5 MB | ☠️ **Đã chết.** `lite.twitter.com` trả 404, app `com.twitter.android.lite` bị gỡ khỏi Play khoảng đầu 2024. `x.com` vẫn cài được **nhưng service worker của nó là một stub tự hủy** — code tự chú thích là *"self-destroying service worker"*, gọi `skipWaiting()`, xóa sạch cache rồi tự gỡ đăng ký. |
| **Starbucks** (2017) | "233 KB, nhỏ hơn 99,84% so với app iOS 148 MB" | ☠️ **Đã chết.** `app.starbucks.com` giờ 301 về `www.starbucks.com`; host cũ ngừng phục vụ khoảng 09–11/2025. Trang mới có `manifest.json` nhưng **không có khóa `display`, không có service worker** → theo tiêu chí của Chrome thì **không cài được**. |
| **Flipkart Lite** (2015) | +70% chuyển đổi với người dùng đã cài | ✅ **Còn sống thật.** `sw.js` là file thật 87 KB, manifest đến nay **vẫn mang tên "Flipkart Lite"**. Nhưng số liệu là ảnh chụp của **10 năm trước**. |
| **Pinterest** (2017) | +44% doanh thu quảng cáo, TTI 23s → 5,6s | ✅ **Còn sống thật.** Service worker ~1,2 MB, manifest `standalone`, push đã nối. Số liệu vẫn từ 2017–2018. |
| **Uber m.uber** (2017) | 50 KB nén, tương tác được trong 3 giây trên 2G | ✅ **Còn sống**, đã dời sang `/go/`; `sw.js` là file thật 283 KB. |

Hai bài học:

1. **Đừng trích Starbucks và Twitter Lite nữa.** Chúng là bằng chứng cho điều ngược lại. Và con số "Starbucks tăng gấp đôi người dùng hoạt động hằng ngày" mà nửa Internet đang lặp lại **không nằm trong nguồn gốc** và không truy được về đâu cả.
2. **Ba ca còn sống đều là app duyệt nội dung, có mạng, quy mô lớn ở thị trường mạng yếu.** Đó chính xác là vùng mà PWA thắng.

## Con đường 2: vỏ native + WebView

Đây là con đường phổ biến nhất, và Capacitor là lựa chọn mặc định hiện nay.

**Trạng thái hiện tại (kiểm ngày 21/08/2026):**

- `@capacitor/core` **8.5.0**, phát hành **31/07/2026** — bản "breaking minor" chỉ động vào iOS, chuyển sang **UIScene** để build được với Xcode 27/iOS 27.
- **Capacitor 8.0** ra 08/12/2025: **Swift Package Manager thành mặc định** cho project iOS mới thay CocoaPods, Android edge-to-edge tự động. Ionic công bố Capacitor đang **gần một triệu lượt tải mỗi tuần**.
- **Capacitor 9 alpha**: **Cordova không còn được kéo vào mặc định.**
- Yêu cầu tối thiểu của v8: **iOS 15+, Android 7 (API 24)+, Node 22, Xcode 26**.
- **Ionic Framework 9.0.0** ra ngày **19/08/2026**.

Quy trình thật, gọn đến mức đáng ngạc nhiên nếu bạn đã có sẵn một web app:

```bash
npm i @capacitor/core
npm i -D @capacitor/cli
npx cap init                  # hỏi tên app + package ID

npm i @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios               # --packagemanager SPM | Cocoapods

npm run build                 # build bundler của bạn
npx cap sync                  # copy bundle web + cập nhật dependency native
npx cap run ios
```

Một cái bẫy nhỏ nhưng gây mất buổi chiều: file `index.html` trong thư mục build **bắt buộc phải có thẻ `<head>`**, nếu không plugin sẽ không hoạt động.

### Một ca thật, có số liệu

Đây là thứ hiếm: một bài kỹ thuật không phải marketing, có số đo trước-sau. Fintech **Found** migrate từ Cordova sang Capacitor (02/06/2025):

| Chỉ số | Trước | Sau |
| --- | --- | --- |
| Cold start iOS (p95) | 20–40 giây | ~10 giây |
| Tỷ lệ ANR Android | 0,60% | 0,20% |

Con số ANR quan trọng hơn vẻ ngoài của nó, vì **ngưỡng "hành vi xấu" của Google Play là 0,47%** — họ đi từ vi phạm sang đạt. Lý do họ không chọn viết lại native cũng rất thẳng thắn: *"chúng tôi không muốn đầu tư nguồn lực cho một bản viết lại toàn bộ, cũng không muốn chuyển sang Flutter hay React Native vì đường cong học tập quá dốc với phần lớn kỹ sư trong công ty… Chúng tôi thường tuyển full-stack"* ([Found Engineering](https://found.com/engineering/migrating-from-cordova-to-capacitor)).

Nhưng cũng đọc con số kia cho kỹ: **p95 sau khi tối ưu vẫn là 10 giây.** Đó là thực tế của một app WebView lớn trên máy yếu, không phải con số marketing.

### Chuyện JIT: điều gần như mọi người nói ngược

Câu quen thuộc là "WebView chậm vì JavaScript không được JIT trên iOS". **Nó ngược.**

- JavaScript chạy trong `WKWebView` **có JIT**. Mỗi WKWebView có một tiến trình `WebContent` riêng do hệ thống quản lý, JavaScriptCore chạy đủ bốn tầng LLInt → Baseline → DFG → FTL trong đó.
- **Hermes, engine mặc định của React Native, không có JIT** — nó biên dịch AOT ra bytecode lúc build.

Nghĩa là **về throughput JavaScript thuần chạy dài, một app WebView có thể nhanh hơn một app React Native trên iOS.** Điều này không có nghĩa RN chậm hơn nói chung — nó bù lại bằng việc không phải dựng cây DOM và không phải layout bằng CSS — nhưng nó phá bỏ hoàn toàn cái lý lẽ "WebView chậm vì thiếu JIT".

### Chỗ WebView thật sự yếu (1): trần 60fps trên iOS

Đây mới là giới hạn cứng, và nó có số hiệu bug đàng hoàng.

**Phần render trang của `WKWebView` bị ghim quanh 60fps, và không có API công khai nào gỡ được.** WebKit Bugzilla **294338**, mở ngày 11/06/2025, trạng thái **NEW, P2, chưa ai từ Apple trả lời**. Người báo cáo chỉ ra: tắt tùy chọn nội bộ `PreferPageRenderingUpdatesNear60FPSEnabled` thì *"WKWebView dễ dàng đạt 120 FPS, còn hành vi mặc định vẫn quanh 60 FPS"*. Trong luồng thảo luận có lập trình viên của Tauri, Capacitor, Ionic và Construct 3 ([WebKit Bugzilla 294338](https://bugs.webkit.org/show_bug.cgi?id=294338)).

Chi tiết cần phân biệt cho đúng: animation CSS `transform`/`opacity` do compositor lo, và cuộn trang, **vẫn đạt 120Hz được**. Cái bị ghim ở 60Hz là **`requestAnimationFrame`** — "by design".

Nói cách khác: **trên màn hình ProMotion, giao diện native/Flutter/RN chạy 120Hz mặc định; vòng lặp animation viết bằng JS trong WebView thì không.** Cách duy nhất gỡ là gọi private API — rủi ro bị App Store từ chối không bằng không, và plugin tương đương cho Tauri đã bị Mac App Store từ chối.

### Chỗ WebView thật sự yếu (2): sự bất đối xứng iOS/Android

Vấn đề thứ hai là **bạn không chọn được engine trên iOS**:

- **Android**: WebView là Chromium, cập nhật qua Play theo nhịp Chrome. Riêng năm 2026, tính đến 13/08 đã có **19 bản cập nhật Android WebView**. Nhưng **Chrome/WebView 138 là bản cuối hỗ trợ Android 8.0/8.1/9**, nên có một tỷ lệ máy vĩnh viễn đóng băng ở WebView cũ.
- **iOS**: WebKit, gắn chặt với phiên bản hệ điều hành. Guideline **2.5.6** nói thẳng: *"Apps that browse the web must use the appropriate WebKit framework and WebKit JavaScript."*

Và có một con số định lượng được cái giá đó. Tháng 6/2026, đội Edge của Microsoft công bố kết quả một bản dựng thử nghiệm Blink trên iOS bằng BrowserEngineKit, đo trên cùng một máy so với Safari:

| Benchmark | Chênh lệch so với Safari |
| --- | --- |
| Speedometer 3.1 | **+28,6%** (49,27 so với 38,3) |
| JetStream 3 | +13,1% |
| MotionMark 1.3.1 | +2,1% |

Microsoft tự nói rõ đây là bản prototype trên máy cá nhân, không phải điều kiện phòng lab. Nhưng ~29% trên Speedometer là ước lượng tốt nhất hiện có cho **phần hiệu năng mà một app WebView trên iOS đang để lại trên bàn**.

Còn về "engine thay thế nhờ DMA": hai năm rưỡi sau khi BrowserEngineKit ra mắt trong iOS 17.4, **chưa hãng nào ship engine thay thế trên iOS, kể cả ở EU**. Và có một chi tiết dễ hiểu nhầm: hai entitlement của Apple dành cho **trình duyệt** và cho **duyệt web nội dung bên thứ ba trong app**. **App Capacitor render giao diện của chính nó không đủ điều kiện xin.** BrowserEngineKit không phải lối thoát cho app hybrid.

### Chỗ WebView thật sự yếu (3): cuộn, vuốt, bàn phím

Đây là thuế bảo trì, không phải giới hạn cứng — nhưng nó có thật và tốn thời gian:

- **Vuốt-quay-lại kiểu iOS không có sẵn trong Capacitor.** Thảo luận trên GitHub mở từ 04/11/2022, **chưa ai trả lời**. Bật `allowsBackForwardNavigationGestures` cho bạn cử chỉ history của WebKit, không phải stack route của SPA — kết hợp với gesture của Ionic thì **quay lại hai lần**.
- **WebKit bug 158325** — phần tử `position: fixed` lệch khỏi vùng nhận chạm khi tắt rubber-banding, đúng cấu hình app hybrid hay dùng. Mở từ **02/06/2016**, đến nay **vẫn NEW**. Mười năm.
- **Bàn phím**: Capacitor phải cung cấp **bốn** chiến lược resize trên iOS (`native`/`body`/`ionic`/`none`) chính vì không có cái nào đúng phổ quát. Trên iOS, `window.resize` không bắn khi bàn phím hiện — chỉ `visualViewport` đổi.
- **Edge-to-edge**: Android 15 (API 35) ép edge-to-edge, Android 16 **bỏ luôn cờ opt-out**. `env(safe-area-inset-*)` trả sai giá trị trên Android WebView dưới bản 140, nên Capacitor phải tự bơm biến CSS từ `WindowInsets` native — sửa rải qua **bốn bản 8.3.0 / 8.3.1 / 8.3.2 / 8.4.0**.

Cách nói công bằng nhất: app native/Flutter/RN được nền tảng lo giúp phần inset của Android 15; stack WebView cần bốn bản vá cộng một lớp CSS đệm vì `env()` của chính WebView bị hỏng.

## Con đường 3: Hotwire Native — web nội dung, native điều hướng

Nếu app của bạn render từ server (Rails, Laravel, Django, Phoenix), đây là con đường ít người biết nhất mà lại hợp nhất.

Khẩu hiệu tóm gọn toàn bộ ý tưởng: **"Content is all web. Navigation is all native."**

Cơ chế: vỏ native chặn mọi cú bấm link, chụp ảnh màn hình trang hiện tại, đẩy một màn hình mới lên native stack với animation đúng chuẩn nền tảng, rồi mới nạp HTML vào web view. Khi vuốt quay lại, nó dùng ảnh đã chụp nên cử chỉ pop mượt như native thật. Điều hướng cấu hình bằng **một file JSON** ánh xạ pattern URL sang kiểu màn hình.

Trạng thái: **iOS và Android đều 1.3.x** (07/2026 và 27/07/2026), do 37signals làm và dùng trong **Basecamp, HEY, ONCE**.

Con số duy nhất họ công bố cũng đủ nói lên vấn đề: chuyển **một** màn hình sang web **xóa 1.436 dòng code trải trên 10 file**. *"Từ nay mọi thay đổi cho trang này diễn ra hoàn toàn ở phía web. Cần thêm bộ lọc thứ tư? Thêm trên web và deploy ngay lập tức."*

**Nhưng đây là chỗ cần đọc kỹ, vì nó là cái bẫy trích dẫn lớn nhất trong toàn bộ chủ đề.**

Con số "90% HTML, 10% native" mà mọi bài viết về Hotwire đều dẫn là của **DHH, tháng 5/2014, nói về Basecamp 2** — thời `UIWebView`, trước cả `WKWebView`. **37signals chưa bao giờ công bố tỷ lệ web/native cho HEY hay cho Basecamp hiện đại.** Bài kỹ thuật gần nhất của họ (2017, về Basecamp 3) còn từ chối đưa con số, gọi đó là *"một dải phổ chứ không phải nhị phân"*, và ghi rõ **cả bốn tab chính đều 100% native**.

Và có một sự thật nữa họ tự nói ra: DHH tiết lộ 37signals **duy trì một đội chín lập trình viên native** cho Basecamp và HEY. Trong cùng bài đó, ông nói về dòng sản phẩm mới nhất: *"chúng tôi đặt cược hoàn toàn vào PWA cho các sản phẩm ONCE mới."*

Đọc lại cho rõ: **công ty làm ra Hotwire Native đã chọn PWA — không phải Hotwire Native — cho dòng sản phẩm mới của chính họ.** Điều đó không có nghĩa Hotwire Native tệ. Nó có nghĩa là ngay cả tác giả của nó cũng coi đây là công cụ cho một loại bài toán cụ thể, chứ không phải câu trả lời phổ quát.

Về quy mô hệ sinh thái, cần thẳng thắn: repo `hotwired/hotwire-native-ios` khoảng **300 sao**, và **không có doanh nghiệp lớn nào ngoài 37signals dùng nó mà kiểm chứng được**. Danh sách adopter công khai (The StoryGraph, Context Travel, Strety) đều là công ty nhỏ, và nguồn duy nhất tổng hợp chúng là một nhà tư vấn bán dịch vụ Hotwire Native.

*(Bẫy phụ: các danh sách kiểu "Shopify, Coinbase, GitLab dùng Hotwire" nói về **Turbo/Stimulus trên web**, hoàn toàn không liên quan tới app mobile.)*

## Con đường 4: JS nhưng không phải web

Nói ngắn, vì nó khác hẳn về bản chất:

- **React Native 0.87** (11/08/2026). New Architecture thành mặc định từ **0.76** (10/2024), thành thứ **duy nhất** từ **0.82** (10/2025), và code kiến trúc cũ bị **xóa hẳn ở 0.84** (02/2026). Nếu bạn còn app RN chưa migrate, thời hạn đã qua.
- **Expo SDK 57** (30/06/2026), gói RN 0.86.
- Câu chuyện "viết một lần chạy cả web" đi qua **React Native for Web**, thứ đang chạy toàn bộ website X. Nhưng `react-native-web` bản mới nhất là **0.21.2, ra 16/10/2025** — gần một năm không có bản phát hành nào.

Về chi phí vận hành ở quy mô lớn, Shopify là nguồn trung thực nhất. Sau 5 năm dùng RN họ báo **>99,9% phiên không crash** và **tải màn hình dưới 500ms (P75)**, nhưng cũng tự công bố mặt trái: *"Nâng app lên mỗi phiên bản React Native mới tốn công đáng kể và thường đòi tái cấu trúc codebase"*, và *"Kỹ sư mobile chuyên iOS và Android là thiết yếu… Không có gì thay thế được kinh nghiệm."* Họ nói thẳng **100% React Native là mục tiêu họ cố tình không theo đuổi**: *"Native vẫn là cách tốt nhất để xây các tính năng tiên phong dùng phần cứng như quét 2D/3D và chạy mô hình AI trên máy."*

Và một chi tiết đáng chú ý cho ai đang cân nhắc RN: **Shopify vẫn dùng WebView — cho phần thanh toán.** Checkout Sheet Kit của họ nạp trước checkout trong một *"background webview"*. Đây là mô hình hợp lý nhất tôi thấy: vỏ RN cho app, web cho đúng một bề mặt bắt buộc phải do server kiểm soát.

## Cửa ải cửa hàng: chỗ hai nền tảng lệch nhau nhiều nhất

### Google Play: được, nhưng có ba hạn chót đang đến

Con đường chuẩn là **Trusted Web Activity** — PWA của bạn được render bởi **chính trình duyệt Chrome**, không phải WebView, nên có đủ nền tảng web mới nhất. Công cụ là **Bubblewrap** (`@bubblewrap/cli` **1.25.0**, 31/07/2026) hoặc PWABuilder (vốn là lớp bọc quanh Bubblewrap).

**Những thứ phải làm đúng:**

1. **Hạn targetSdk.** Từ **31/08/2026**, app mới và bản cập nhật trên Play **phải target Android 16 (API 36)** trở lên; có thể xin gia hạn đến **01/11/2026**. Bubblewrap **1.25.0 đạt yêu cầu này; 1.24.x trở về trước target SDK 35 và không đạt.**
2. **Hạn Play Billing.** Cùng ngày **31/08/2026**, mọi app mới và bản cập nhật phải dùng **Billing Library 8 trở lên**. Điều này giết một loạt plugin IAP cũ — plugin Cordova của RevenueCat nói thẳng: *"Billing Client v7 sẽ là bản cuối cùng SDK này hỗ trợ… nghĩa là Google sẽ không cho cập nhật app của bạn sau 31/08/2026."*
3. **Digital Asset Links.** File `assetlinks.json` phải nằm ở `https://<host>/.well-known/assetlinks.json` với vân tay SHA-256 **của khóa Play App Signing**, không phải khóa bạn ký lúc build. Sai chỗ này thì TWA lặng lẽ tụt xuống thành Custom Tab — hiện thanh địa chỉ như trình duyệt.
4. **Ngưỡng chất lượng.** Vượt ngưỡng thì bị giảm hiển thị **và bị dán cảnh báo ngay trên trang cửa hàng**:

| Chỉ số | Toàn bộ | Theo từng dòng máy |
| --- | --- | --- |
| Tỷ lệ crash người dùng cảm nhận | **1,09%** | 8% |
| Tỷ lệ ANR người dùng cảm nhận | **0,47%** | 8% |

Ngưỡng ANR đặc biệt đáng lo với app WebView, vì Google **tự tài liệu hóa** rằng khởi tạo WebView chặn UI thread và gây ANR — họ còn phải ship hẳn `WebViewCompat.startUpWebView()` để giảm nhẹ.

Về chính sách, cần đính chính một lời đồn phổ biến: **Play không cấm app dạng vỏ WebView.** Điều khoản thật nhắm vào việc bọc website *của người khác*: *"We don't allow apps whose primary purpose is to drive affiliate traffic to a website or provide a webview of a website **without permission from the website owner or administrator**"*. Bọc PWA của chính bạn không phải thứ điều khoản này nhắm tới. Cái Play cấm là app "chỉ có nội dung và chức năng hạn chế".

*(Lưu ý nhỏ: yêu cầu "điểm Lighthouse tối thiểu 80" cho TWA mà nhiều blog nhắc đến **không có trong tài liệu hiện tại của Google** — trang quality-criteria riêng đã bị gỡ.)*

### App Store: đây mới là mắt xích yếu

Không có cách nào nộp một PWA lên App Store. Bạn phải nộp một app native render web của bạn trong WKWebView.

Và app đó bị xét theo **guideline 4.2 Minimum Functionality**: *"Your app should include features, content, and UI that elevate it beyond a repackaged website. If your app is not particularly useful, unique, or 'app-like,' it doesn't belong on the App Store."*

**Đây là điều khoản do con người xét, theo cảm tính, và kết quả thay đổi theo người duyệt.** Vài ca có thật:

- Một app Ionic bị từ chối tháng 12/2020: *"App của bạn cho trải nghiệm hạn chế vì không đủ khác biệt so với duyệt web trên di động. Cụ thể, chúng tôi thấy phần lớn nội dung app dẫn ra Safari."* Qua được ở **lần nộp thứ ba**; chính tác giả thừa nhận không biết thay đổi nào có tác dụng.
- Một app WebView bị từ chối **10 lần** liên tiếp dưới 4.2 (11/2025). Trả lời chính thức trên diễn đàn Apple chỉ là lời mời đặt lịch tư vấn 1:1.
- Nhiều lập trình viên báo cáo đã thêm push notification, Core Location, share sheet mà **vẫn** bị từ chối.

Nghĩa là: **"cứ thêm push notification là qua" không phải một phương thuốc đáng tin.**

Ba điều khoản ít người biết nhưng cắn đau:

- **4.2.6**: *"Apps created from a commercialized template or app generation service will be rejected unless they are submitted directly by the provider of the app's content."* Dùng dịch vụ sinh app tự động để bọc web của khách hàng rồi nộp dưới tài khoản của bạn — hỏng. Lối được phép là gộp mọi khách vào **một binary duy nhất** theo mô hình "picker".
- **4.2.3(ii)**: nếu phải tải thêm tài nguyên lúc chạy lần đầu, **phải báo dung lượng và hỏi người dùng trước**.
- **4.7.2** — bẫy cho ai định làm nền tảng mini-app: *"Your app may not extend or expose native platform APIs or technologies to the software without prior permission from Apple."* (Nội dung web của chính bạn đóng gói trong binary thì không thuộc 4.7 — bạn bị xét theo 4.2. Rất nhiều bài viết nhầm 4.7 là "cửa cho HTML5".)

Và **ngày 09/06/2026 Apple sửa 4.3(b)**, thêm lời đe dọa gỡ bỏ: app không phân biệt được với thứ đã có sẵn *"may [be removed] from the App Store going forward"*, còn nộp lặp lại nhiều app chất lượng thấp *"may lead to removal from the Apple Developer Program"*.

**Cách qua cửa, theo người thật sự ship app WebView:** ship bản v1 mỏng nhất có thể, rồi mới nâng dần. Cụ thể: có tab bar native với 3–5 điểm vào, mọi tính năng lõi trong 2 lần chạm, **không có link nào bắn ra Safari**, xử lý offline tử tế (WebView trắng khi mất mạng đọc y hệt "trình duyệt"), và ẩn phần chrome chỉ dành cho web — footer marketing, banner cookie, và đặc biệt là **banner "tải app trên App Store"**, thứ Apple thực sự từ chối app vì nó.

Nguyên tắc bao trùm: **nếu gỡ WebView ra mà app vẫn còn giá trị, bạn ổn.**

## Bán hàng trong app: luật vừa lật ngược, và nó đang có lợi cho bạn

Nếu app của bạn thu tiền, đây là phần thay đổi nhiều nhất trong 18 tháng qua — và phần lớn bài viết trên mạng vẫn đang mô tả thế giới cũ.

**Mặc định vẫn không đổi.** Apple 3.1.1: *"If you want to unlock features or functionality within your app… you must use in-app purchase"*, và cấm dùng cơ chế riêng như license key hay QR. Google: *"Google Play's billing system is required for developers offering in-app purchases of digital goods and services distributed on Google Play."*

**Nhưng ở thị trường Mỹ, cả hai đã phải mở cửa — do tòa án, không phải do thiện chí.**

**Phía Apple.** Sau bản án phạt vi phạm lệnh tòa ngày 30/04/2025 trong vụ Epic v. Apple, guideline hiện hành (cập nhật 08/06/2026) có một mệnh đề cắt ngang giữa câu: *"In all other storefronts, **except for the United States storefront, where this prohibition does not apply**, apps and their metadata may not include buttons, external links, or other calls to action that direct customers to purchasing mechanisms other than in-app purchase."*

Nói cách khác: **app trên storefront Mỹ được đặt nút, link, lời kêu gọi dẫn người dùng ra web thanh toán, không cần xin entitlement.** Và **guideline hiện không nêu bất kỳ mức hoa hồng nào** cho các giao dịch link-out đó. Tòa phúc thẩm Vòng 9 (11/12/2025) giữ nguyên phán quyết vi phạm nhưng bác lệnh cấm-mọi-hoa-hồng, cho phép một mức "hợp lý" **do tòa sơ thẩm quyết định khi xét lại**. Apple đã **đề xuất** 15% / 10% / 5% (13/08/2026) nhưng **tòa chưa duyệt**. Tối cao Pháp viện đã nhận đơn ngày 30/06/2026, nhưng chỉ về **chuẩn xét vi phạm lệnh tòa**, không phải về chuyện hoa hồng.

**Phía Google.** Từ **29/10/2025**, Google tuyên bố *"sẽ không yêu cầu dùng Google Play Billing… và không cấm dùng phương thức thanh toán trong app khác"* cho người dùng ở Mỹ. Hai chương trình đã mở, nhưng **có phí**:

| | Đăng ký định kỳ | Nội dung số khác |
| --- | --- | --- |
| 1 triệu USD doanh thu đầu tiên | 10% | 10% |
| Mức chuẩn | 10% | 20–25% |
| Play Games Level Up / Apps Experience | 10% | 15–20% |

Cộng thêm phí cố định mỗi lượt cài qua link ngoài: **game 3,65 USD, app 2,85 USD**. Và **từ 01/10/2026, nhà phát triển tham gia hai chương trình này phải báo cáo giao dịch và trả phí.**

**Ba điều thực dụng rút ra:**

1. **Đừng chốt kiến trúc thanh toán dựa trên một con số hoa hồng đọc trên blog.** Mức phí của Apple ở Mỹ hiện là **chưa xác định về mặt pháp lý** và đang được xét lại. Kiểm lại nguồn gốc trước mỗi lần lập kế hoạch tài chính.
2. **Điều khoản 3.1.3(b) của Apple là bạn của app đa nền tảng**: bạn được cho người dùng dùng nội dung đã mua ở nơi khác — *"provided those items are also available as in-app purchases within the app"*. Tức là được, nhưng phải có bản IAP song song.
3. **Về kỹ thuật, Capacitor không có plugin IAP chính thức.** Tài liệu của chính Capacitor chỉ bạn sang `cordova-plugin-purchase` của bên thứ ba, hoặc `@revenuecat/purchases-capacitor` (cần backend trả phí). Nếu bán hàng là mô hình kinh doanh của bạn, hãy tính đây là một rủi ro thật, không phải chi tiết nhỏ.

## Truy cập native: cái gì có sẵn, cái gì phải tự viết

Đây là phần các bảng so sánh hay ghi "Full native access ✅" rồi bỏ qua chi tiết. Chi tiết mới là chỗ dự án chết.

**Ổn, dùng được ngay:**

- **Deep link / Universal Links / App Links** — giống hệt app native, không có thuế hybrid. Kiểu hỏng duy nhất là **hỏng im lặng**: cấu hình sai thì link chỉ mở trình duyệt.
- **Push** — `@capacitor/push-notifications` v8.1.2. Nhưng đọc kỹ tài liệu: *"Plugin này không hỗ trợ iOS Silent Push"*, và thông báo chỉ-dữ liệu **sẽ KHÔNG gọi callback nếu app đã bị kill**.

**Được, nhưng hẹp hơn bạn tưởng:**

- **Camera** — `@capacitor/camera` là **hộp thoại chụp ảnh và bộ chọn thư viện của hệ điều hành, không phải luồng camera**. Không có viewfinder tùy biến, không truy cập từng khung hình. Quét QR, AR, dò biên tài liệu, filter thời gian thực — tất cả đều cần `getUserMedia` trong WebView (yếu hơn) hoặc một plugin khác hẳn.
- **Sinh trắc học** — plugin mà mọi bài hướng dẫn dẫn link (`capacitor-native-biometric`) **phát hành lần cuối 14/06/2023, đã bỏ hoang**. Bản còn sống là `@aparajita/capacitor-biometric-auth` (v10, 02/2026). Đây là mẫu chung của hệ sinh thái plugin: **cái nổi tiếng nhất không phải cái được bảo trì.**

**Yếu nhất: chạy nền.**

`@capacitor/background-runner` là một **runtime JS headless riêng, không phải WebView của bạn**: không có DOM API nào cả, phần lớn Web API vắng mặt. Tài liệu nói nguyên văn *"iOS sẽ quyết định khi nào và bao lâu tác vụ của bạn chạy"*, mỗi lần chạy **tối đa khoảng 30 giây**, và **không chạy được trên simulator**. Chu kỳ lặp tối thiểu 15 phút.

**Và đây là những thứ không có cửa, vì lý do kiến trúc:** app extension, widget và CarPlay trên iOS là **binary riêng với API giao diện khai báo (SwiftUI/template) — về cấu trúc không thể chứa một WKWebView.**

| Tính năng | Thực tế |
| --- | --- |
| **Widget màn hình chính** | Không có plugin chính thức. Plugin cộng đồng chỉ bắc cầu **dữ liệu** qua App Groups. **Giao diện widget vĩnh viễn không thể là web** — bạn viết SwiftUI (WidgetKit) và RemoteViews (Android). |
| **Live Activities** | Chỉ có cộng đồng. ActivityKit giới hạn dữ liệu **4 KB**, cần widget extension SwiftUI viết tay. |
| **watchOS** | Plugin *chính thức* `@capacitor/watch` là **v0.1.12, phát hành 08/04/2024**, peer-depend `@capacitor/core ^5.0.0` — lùi ba major so với 8.5. Repo tự dán nhãn *"thử nghiệm, không hỗ trợ"*. |
| **App Clips / Instant Apps** | **Không có plugin nào tồn tại.** Đề xuất cộng đồng mở từ 04/2021, chưa bao giờ thành hình. |
| **Siri / App Intents** | Không có plugin được bảo trì. |
| **CarPlay / Android Auto** | **Không có gì trên npm cả.** Giao diện CarPlay là template, không chứa được WebView. |

Nếu một trong số này là yêu cầu sản phẩm, **tiền đề "không cần kỹ sư native" sụp đổ** — bạn cần một dev Swift *cộng thêm* stack hybrid, tức là kết hợp mặt dở của cả hai bên.

## Cập nhật không qua duyệt (OTA): đính chính một con số ai cũng trích sai

Đây là lý do lớn nhất người ta chọn công nghệ web. Nhưng cả cơ sở pháp lý lẫn hạ tầng đều vừa xáo trộn.

### Điều khoản thật tên là gì

Gần như mọi bài viết đều trích **"Apple guideline 3.3.2"**. Có hai chỗ sai trong câu đó:

1. Nó **không phải Review Guideline**, nó nằm trong **Apple Developer Program License Agreement** — một hợp đồng khác.
2. Nó **đã bị đánh số lại**. Trong bản DPLA hiện hành, **§3.3.2 là "Regulatory Compliance"**; điều khoản về tải code nằm ở **§3.3.1(b)**.

Điều khoản thật sự **được đem ra thi hành khi duyệt app** là **Review Guideline 2.5.2**: *"Apps should be self-contained in their bundles… nor may they download, install, or execute code which introduces or changes features or functionality of the app."*

Lối thoát nằm ở DPLA 3.3.1(b): *"interpreted code may be downloaded to an Application but only so long as such code: (a) does not change the primary purpose of the Application… (b) does not create a store or storefront for other code or applications, and (c) does not bypass signing, sandbox, or other security features of the OS."*

**Quy tắc thực dụng: JS/HTML/CSS đẩy vào một WebView của WebKit là được phép, miễn là không đổi mục đích chính của app.** Sửa lỗi, sửa chữ, sửa layout thì an toàn. Ship nguyên một mảng sản phẩm mới qua OTA thì không. Và **đừng dùng hộp thoại ép cập nhật trên iOS** — bắt người dùng đi qua luồng cập nhật mới dùng được app là một vi phạm riêng.

### Công cụ nào còn sống

| Công cụ | Trạng thái |
| --- | --- |
| **Microsoft CodePush** | ☠️ **Chết.** App Center ngừng hoạt động **31/03/2025**; repo `microsoft/react-native-code-push` **bị archive 20/05/2025, chỉ đọc**. |
| **Ionic Appflow** | 🔴 **Đang tắt dần.** Ngừng bán từ **11/02/2025**; khách hiện hữu dùng đến **31/12/2027**. Plugin `@capacitor/live-updates` đứng ở 0.5.0. |
| **Expo EAS Update** | 🟢 Rất tích cực. Miễn phí 1.000 MAU, $19/tháng cho 3.000, $199/tháng cho 50.000. |
| **`@capgo/capacitor-updater`** | 🟢 Rất tích cực (8.51.14, 20/08/2026). Backend AGPL, tự host được. Từ $12/tháng. |
| **Shorebird** (Flutter) | 🟢 Tích cực. |
| **Tauri** | ❌ Plugin Updater **không hỗ trợ cả Android lẫn iOS**. |
| `lisong/code-push-server` tự host | 🔴 **Đừng.** Nhìn thì như còn sống nhưng đó là dependabot; **commit thực chất cuối cùng là 2019**, 195 issue mở. |

Hai điểm đáng chú ý về lời hứa tuân thủ, vì chúng khác nhau rõ rệt:

- **Shorebird là bên duy nhất trích thẳng điều khoản chi phối và giải thích cơ chế kỹ thuật của mình đối chiếu với nó** (họ fork Dart VM để làm trình thông dịch on-device, đúng cái lỗ "interpreted code"), rồi ghi việc lạm dụng vào điều khoản dịch vụ.
- **Expo cố tình không bảo hành gì cả**: *"cập nhật của bạn cần tuân thủ hướng dẫn của App Store và Play Store… bạn chịu trách nhiệm cuối cùng cho hành vi của app."*
- **Ionic khẳng định "fully compliant" mà không trích một điều khoản nào.** Trên chính diễn đàn của họ có người hỏi xin dẫn chứng từ 22/05/2024 — không nhân viên Ionic nào trả lời.

Về mức độ rủi ro thật: các ca từ chối có tài liệu đều đến dưới nhãn **2.3.1 "hidden features"** trước, chỉ khi khiếu nại Apple mới nêu 2.5.2. Có ca app **còn không hề bật OTA** vẫn bị dính, cho thấy đây là máy quét và có dương tính giả. Cách giảm rủi ro mà mọi nguồn đều đồng ý: **mô tả cơ chế cập nhật trong phần Notes for Review**, đừng ship tính năng ngủ đông không khai báo, và vẫn phát hành binary định kỳ.

## Bốn ngộ nhận nên bỏ

**1. "Cordova chết rồi."** Sai. Cordova **không** nằm trong Apache Attic. Biên bản họp của Apache tháng 6/2026 ghi *"community health is strong"*; `cordova-ios@8.1.1` ra 07/07/2026, `cordova-android@15.1.0` ra 22/07/2026, còn có bản vá CVE tháng 6/2026. Cái chết là **Adobe PhoneGap** (2020) và **hỗ trợ Cordova của Microsoft App Center** (2022 — lý do Microsoft nêu: lệnh gọi SDK Cordova chiếm *"dưới 1%"* dịch vụ của họ). Dù vậy, dự án mới vẫn nên chọn Capacitor.

**2. "OutSystems mua Ionic rồi bỏ Capacitor."** Sai một nửa. Thứ bị đóng là **tầng thương mại** (Appflow, Identity Vault, Auth Connect, Secure Storage, Portals); chính thông báo đó khẳng định Ionic Framework và Capacitor *"sẽ vẫn miễn phí và mã nguồn mở"*. Bằng chứng: Capacitor 8.5 ra 31/07/2026, Ionic 9 ra 19/08/2026, gần một triệu lượt tải mỗi tuần.

**3. "Apple cấm PWA ở EU."** Sai. Apple **có** thông báo gỡ Home Screen web app ở EU tháng 2/2024, rồi **đảo ngược ngày 01/03/2024**.

**4. "App Amazon chủ yếu là WebView."** Đây là ngộ nhận tôi thấy được lặp lại nhiều nhất trong các bài tiếng Việt, và **nó không có nguồn gốc nào cả**. Truy ngược thì chỉ đến hai chỗ: một bài blog của công ty **bán dịch vụ bọc website thành app**, và một bài đăng ẩn danh trên Blind. Amazon chưa bao giờ công bố điều đó. Thứ Amazon *có* công bố thì ngược lại: họ dùng **React Native** từ khoảng 2016, và Vega OS mới của họ đặt React Native ở tầng hệ điều hành.

*(Bẫy đi kèm: "Amazon WebView" là thật, nhưng nó là engine WebView thay thế trong **Fire OS** cho Fire TV/Tablet — không phải bằng chứng gì về app mua sắm.)*

## Ai thật sự đang chạy công nghệ web trong sản xuất

Đây là phần tôi khuyên bạn đọc kỹ nhất nếu đang định dùng case study để thuyết phục sếp.

**Thư viện case study của Ionic có một đặc điểm ít ai để ý: các trang không hiển thị ngày, nhưng thẻ meta trong HTML thì có.** Trích ra thì thấy: **case study mới nhất của Ionic là tháng 9/2023.** Ionic đã không xuất bản case study khách hàng mới nào trong khoảng ba năm.

Và có một vấn đề sâu hơn: **phần lớn các case study đó bán điểm hấp dẫn là live update, Identity Vault hoặc Portals — tức những sản phẩm đã ngừng bán từ 02/2025 và sẽ chết cuối 2027.** Chúng đã lỗi thời về mặt kiến trúc ngay cả khi app vẫn còn sống.

Ba cái tên bị dùng sai nhiều nhất:

- **"Southwest Airlines dùng Ionic"** — app được dẫn nguồn là **SWA U**, một app **định hướng nhân viên mới nội bộ** (xe đưa đón, khách sạn, bản đồ khuôn viên), tài liệu duy nhất là trang portfolio của một agency, không ghi ngày. Không phải app đặt vé.
- **"T-Mobile dùng Ionic"** — là **T-Mobile Cast**, app podcast/video nội bộ do một đội nhân sự 5 người làm.
- **"Volkswagen dùng Ionic"** — là **GroupUI**, một **design system** bằng Stencil. Không phải app mobile.

Ngoài ra: case study "Disney" nói về **Disney's Magical Express**, dịch vụ Disney đã ngừng từ 31/12/2021. Case study "NHS" là hai app nội bộ viết bằng **AngularJS**, framework đã hết vòng đời từ 12/2021.

**Những ca đáng tin hơn trong danh sách đó:** **AAA** (app tiêu dùng thật, 62 triệu hội viên, điểm store đi từ 2,1 lên 4,3), **Breeze Airways** (app hàng không tiêu dùng thật, ra mắt 05/2021, một đội cho cả iOS + Android + web), **H&R Block MyBlock** (gộp 3 codebase thành 1), **BBC Children's Games**, và **Bestinvest**. Nhưng ngay cả những ca này cũng từ 2021–2023 và chưa ai kiểm lại cho 2026.

**Ở hướng ngược lại, có một ca đáng nhớ hơn tất cả:** Discord công bố năm 2018 một bài tên *"Why Discord is Sticking with React Native"* — giải thích họ dùng RN **chỉ trên iOS** vì bản thử trên Android không đạt. Bài đó đến nay vẫn đứng đầu kết quả tìm kiếm. Nhưng năm 2025 chính Discord viết: *"client Android đã chuyển sang React Native năm 2022."* Họ đã tự đảo ngược kết luận của mình từ ba năm trước, và cả ngành vẫn đang trích bài cũ.

Đó là bài học phương pháp lớn nhất của toàn bộ chủ đề này: **blog kỹ thuật không có ngày hết hạn, nhưng kết luận của chúng thì có.**

Ba dẫn chứng chống-web mà gần như mọi bài so sánh đều dùng cũng chịu chung số phận: **Zuckerberg "HTML5 là sai lầm lớn nhất" (2012 — 14 năm), LinkedIn bỏ mobile web (2013 — 13 năm), và Airbnb "Sunsetting React Native" (2018 — 8 năm).** Cả ba đều có trước `WKWebView`, Service Worker, PWA, Hermes và New Architecture. Riêng bài Airbnb còn có một chi tiết ít ai đọc tới: RN ở Airbnb là **80.000 dòng trên 220 màn hình**, trong khi **codebase native lớn gấp khoảng 10 lần** — tức RN chưa bao giờ là phần chính của app đó, và Airbnb tự nói quyết định phản ánh **tổ chức của họ**, không phải khả năng của RN.

## Chi phí và thời gian: con số duy nhất công khai

Joe Masilotti (30+ app Rails-backed đã ship) là người duy nhất tôi tìm được có công bố mốc thời gian so sánh. **Ông ấy là tư vấn Hotwire Native nên không trung lập** — nhưng phần "nhược điểm" của ông cụ thể đủ để kiểm chứng:

| Lựa chọn | Thời gian | Nhược điểm ông ấy tự nêu |
| --- | --- | --- |
| Native (Swift + Kotlin) | **6–12+ tháng** | Xây mọi thứ **ba lần**; ba codebase vĩnh viễn |
| React Native | **4–8 tháng** | Vẫn là **codebase hoàn toàn tách khỏi web app của bạn** |
| PWA | **~1 tuần** | Không IAP, push iOS hạn chế, **không có mặt trên cửa hàng** |
| Hotwire Native | **1–2 tháng** | Vẫn phải quản Xcode + Android Studio; **chưa hỗ trợ offline** |
| Flutter | — | Phải học Dart; **"quá mức cần thiết"** với một business web muốn thêm mobile |
| Capacitor | — | Hợp đội **JavaScript**; **"lệch pha"** với Rails render từ server |

Đối chiếu chéo với hai nguồn doanh nghiệp:

- **Shopify** năm 2020 báo app Compass chia sẻ ~99% code và ra mắt cả hai nền tảng trong **ba tháng**. Nhưng năm 2025 họ cũng công bố cái giá của việc *ở lại*: bản migrate New Architecture khiến khởi động Android tăng ~10%, iOS ~3%, vài component **chậm đi tới 20%**, độ ổn định tụt dưới mục tiêu 99,95% mất vài tuần mới hồi.
- **SoFi** (~15 triệu người dùng) migrate từ native riêng lẻ sang Flutter, công bố **giảm 60% số dòng code** cho cùng tính năng và **xóa hơn 1 triệu dòng** tổng cộng. **talabat** hoàn tất migrate sang Flutter năm 2024, báo **nhịp phát hành nhanh gấp 4 lần**. Đây là các case study do Google xuất bản — đáng tin về *việc migrate có xảy ra*, nên đọc dè dặt về *con số*.

Còn về benchmark cold start "Ionic 400–800ms vs Flutter 200–400ms" mà bạn hay thấy: **nó không có nguồn**. Truy ngược chỉ đến các bài SEO không mô tả phương pháp đo. **Không tồn tại một benchmark cold-start webview-vs-native công khai đáng tin nào cho giai đoạn 2024–2026.** Số duy nhất có thật là của Found ở trên — và nó là 10 giây.

Bằng chứng học thuật thì mỏng nhưng nhất quán về hướng: nghiên cứu ICWE 2021 (Huber/Demetz/Felderer) so năm bản hiện thực của cùng một app. Native tốn ít năng lượng nhất; đáng chú ý là **Capacitor tốn ít năng lượng hơn PWA chạy trong Chrome**. Đây là nghiên cứu duy nhất tôi tìm được có nhánh Capacitor — và nó từ 2021.

## Còn một con đường thứ năm ít ai đưa vào bảng so sánh

Nếu điều bạn thật sự muốn là **không viết logic nghiệp vụ hai lần** — chứ không phải "dùng lại HTML" — thì có một lựa chọn hiếm khi xuất hiện trong các bài kiểu này: **Kotlin Multiplatform**.

Google chính thức hỗ trợ KMP trên Android từ I/O 2024, và định phạm vi rất rõ: **chia sẻ logic nghiệp vụ, không chia sẻ giao diện**. **Google Docs** trên Android, iOS và Web dùng KMP cho phần logic dùng chung. **Netflix** cũng vậy — logic dùng chung bằng Kotlin, còn giao diện vẫn là **Jetpack Compose và SwiftUI** nguyên bản.

Đây là hướng ngược với mọi con đường ở trên: thay vì chia sẻ tầng trình bày và chấp nhận nó không giống native, KMP chia sẻ tầng dưới và để mỗi nền tảng tự vẽ. Cái giá là bạn viết giao diện hai lần và cần kỹ sư của cả hai bên. Cái được là giao diện không bao giờ có cảm giác "gần giống native".

## Chọn cái nào

| Tình huống của bạn | Chọn |
| --- | --- |
| Đã có web app SPA, cần lên hai cửa hàng | **Capacitor** |
| App render từ server (Rails/Laravel/Django) | **Hotwire Native** |
| Không cần lên cửa hàng, cần cài nhanh, thị trường mạng yếu | **PWA thuần** + nhắc người dùng cài lên màn hình chính |
| Chỉ cần Android, muốn giữ nguyên web platform mới nhất | **TWA + Bubblewrap ≥ 1.25.0** |
| App nặng animation, cử chỉ, danh sách rất dài, cần 120Hz | **React Native / Expo** hoặc native |
| Cần Bluetooth, USB, NFC trên iOS | Không phải web — plugin native hoặc viết native |
| Cần widget, Live Activities, watch, CarPlay | Native (hoặc native + hybrid, chấp nhận chi phí kép) |
| Muốn hết trùng lặp *logic* chứ không phải trùng lặp *giao diện* | **Kotlin Multiplatform** |
| Ưu tiên desktop, mobile là phụ | **Tauri 2** — nhớ nó không có OTA trên mobile |

Có một quy luật mà nhiều nguồn đối lập nhau — CEO Ionic, đội Expo (đối thủ), nhà tư vấn Hotwire, và những người phản đối gay gắt trên Hacker News — **đều độc lập đồng ý**:

> **Đặt cược vào WebView an toàn nhất khi app thiên về dữ liệu, luôn có mạng, và nghiêng về B2B. Nguy hiểm nhất khi app hướng người tiêu dùng, nặng cử chỉ, cần offline, hoặc nặng animation.**

Và quy tắc bao trùm: **đừng chọn theo framework, chọn theo thứ bạn không được phép hy sinh.** Nếu đó là tốc độ ship và một đội web sẵn có, con đường 2 hoặc 3 gần như luôn thắng. Nếu đó là cảm giác chạm 120fps và một danh sách mười nghìn dòng, không con đường web nào cứu bạn được.

## Câu hỏi thường gặp

**App làm bằng WebView có bị App Store từ chối không?**
Không tự động, nhưng rủi ro là thật và khó đoán — có ca bị từ chối 10 lần liên tiếp. Guideline 4.2 từ chối *"repackaged website"* chứ không từ chối WebView. Điều quyết định là app của bạn có làm được gì mà trình duyệt không làm được hay không. Chiến thuật hiệu quả nhất là ship bản v1 mỏng, không có link nào bắn ra Safari, rồi nâng dần. Cẩn thận riêng với 4.2.6 nếu bạn dùng dịch vụ sinh app tự động.

**PWA trên iOS có nhận được push không?**
Có, từ iOS 16.4, nhưng **chỉ khi người dùng đã thêm web app vào màn hình chính**. Trong tab Safari thì không, đến hôm nay vẫn vậy.

**Dữ liệu PWA trên iOS có bị xóa sau 7 ngày không?**
Trong tab trình duyệt thì có. **Web app đã cài lên màn hình chính được miễn** — WebKit ghi rõ ITP bỏ qua domain đó khi dọn dữ liệu. Đây là lý do kỹ thuật mạnh nhất để đẩy người dùng cài app.

**App WebView có chạy được 120Hz trên iPhone Pro không?**
Cuộn và animation CSS do compositor lo thì được. **`requestAnimationFrame` thì không — nó bị ghim ở 60Hz theo thiết kế**, và bug WebKit 294338 mở từ tháng 6/2025 vẫn chưa có ai từ Apple trả lời. Nếu giao diện của bạn phụ thuộc vào vòng lặp animation JS, đây là trần cứng.

**Bán hàng trong app thì phải dùng IAP à?**
Mặc định là có, ở cả hai cửa hàng. Nhưng **ở storefront Mỹ, Apple hiện cho phép đặt nút và link dẫn ra web thanh toán mà không cần entitlement**, và guideline hiện không nêu mức hoa hồng nào — vì tòa chưa quyết. Google cũng đã mở từ 29/10/2025 nhưng **có thu phí** (10–25% cộng phí cố định mỗi lượt cài). Đây là vùng luật đang chuyển động rất nhanh; kiểm lại nguồn gốc trước khi lập kế hoạch tài chính.

**Capacitor hay Cordova cho dự án mới?**
Capacitor. Cordova vẫn sống và vẫn ra bản mới, nhưng Capacitor là nơi hệ sinh thái đang đổ vào, và từ Capacitor 9 thì Cordova trở thành tùy chọn phải bật thay vì mặc định.

**Tôi có thể làm widget màn hình chính bằng HTML không?**
Không, và sẽ không bao giờ. WidgetKit của iOS dùng API giao diện khai báo trong một binary riêng, về cấu trúc không chứa được WKWebView. Widget, Live Activities và CarPlay đều phải viết native. Nếu sản phẩm của bạn cần chúng, hãy tính chi phí một kỹ sư Swift ngay từ đầu.

**CodePush còn dùng được không?**
Không. App Center ngừng hoạt động 31/03/2025 và repo bị archive 20/05/2025. Nếu bạn dùng React Native, chuyển sang **EAS Update**; Capacitor thì **Capgo**; Flutter thì **Shorebird**. Đừng tự host `lisong/code-push-server` — code thực chất của nó từ 2019.

**Tôi cần macOS để build app iOS bằng công nghệ web không?**
Có. Mọi con đường dẫn tới App Store đều cần Xcode, và Xcode chỉ chạy trên macOS. Chỉ có PWA thuần là không cần — nhưng nó cũng không lên App Store.

**Bao lâu nữa thì hết cần vỏ native?**
Trên Android, gần như đã hết cần rồi nếu bạn chấp nhận phân phối ngoài Play. Trên iOS thì đừng đợi: BrowserEngineKit đã tồn tại hơn hai năm mà chưa hãng nào ship engine thay thế, và hai entitlement của nó vốn không dành cho app hybrid. Kế hoạch của bạn nên giả định hiện trạng này giữ nguyên.
