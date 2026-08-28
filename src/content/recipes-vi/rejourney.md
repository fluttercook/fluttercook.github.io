---
title: "Rejourney: session replay và báo cáo crash mã nguồn mở cho Flutter"
package: "rejourney"
repo: "rejourneyco/rejourney"
githubUrl: "https://github.com/rejourneyco/rejourney"
category: "Backend/Data"
stars: 277
forks: 16
lastUpdate: "2026-08-28"
pubDev: "https://pub.dev/packages/rejourney"
youtube: "https://www.youtube.com/watch?v=Z95MDxBXMjk"
priority: "High"
phase: "P1"
trendRank: 0
description: "Rejourney là nền tảng mã nguồn mở cho session replay, phân tích sản phẩm và báo cáo crash/ANR, với SDK Flutter hạng nhất — ưu tiên quyền riêng tư, tự host được, và thành thật về quan hệ nhân quả."
seoDescription: "SDK Flutter của Rejourney bổ sung session replay, báo cáo crash và ANR native, sự kiện sản phẩm và đo thời gian mạng. SDK client giấy phép Apache 2.0, backend SSPL, cài bằng flutter pub add rejourney."
keywords:
  - rejourney flutter
  - session replay flutter
  - báo cáo crash flutter mã nguồn mở
  - giám sát anr flutter
  - phân tích sản phẩm flutter
  - thay thế posthog cho mobile
topics:
  - analytics
  - session-replay
  - monitoring
summary:
  - "**Rejourney** gộp session replay, sự kiện sản phẩm và tín hiệu kỹ thuật — crash, ANR, lỗi API — vào chung một luồng vấn đề."
  - "SDK Flutter thu thập dữ liệu ở tầng native; còn API công khai, navigator observer, lớp che dữ liệu và HTTP client đều là Dart đúng chất."
  - "`flutter pub add rejourney`, rồi `Rejourney.init()` và — chỉ sau khi có sự đồng ý — `Rejourney.start()`."
  - "**277★**. SDK client và tài liệu theo giấy phép Apache 2.0; backend và dashboard theo SSPL."
related:
  - slug: appwrite
    title: "appwrite: hướng dẫn AI/ML trong Flutter"
  - slug: serverpod
    title: "serverpod: hướng dẫn giao diện & thành phần UI trong Flutter"
  - slug: simvyn
    title: "simvyn: một bảng điều khiển cho mọi simulator, emulator và thiết bị"
faq:
  - q: Thêm Rejourney vào ứng dụng Flutter thế nào?
    a: "`flutter pub add rejourney`, rồi `await Rejourney.init('pk_live_...')` lúc khởi động và `await Rejourney.start()` chỉ sau khi bạn đã có quyết định về sự đồng ý. `init` cố tình không bao giờ bắt đầu thu thập. Yêu cầu tối thiểu là Flutter 3.22, Dart 3.3, iOS 15.1 và Android API 24."
  - q: Rejourney có thật sự là mã nguồn mở không?
    a: "Một phần, và họ nói thẳng điều đó. API Flutter, cầu nối nền tảng, lõi native, ví dụ và tài liệu theo Apache 2.0. Backend và dashboard theo SSPL 1.0 — tự chạy nội bộ thì miễn phí, nhưng nếu cung cấp nó như một dịch vụ thì bạn buộc phải công bố mã nguồn dịch vụ của mình."
  - q: Nó xử lý các trường dữ liệu nhạy cảm ra sao?
    a: "Bọc nhánh widget trong `RejourneyMask`, nó che một vùng trong khung hình được ghi mà không thay đổi những gì người dùng nhìn thấy. Lớp này nằm trên cơ chế nhận diện trường bảo mật ở tầng native và các quy tắc riêng tư về văn bản, media ở cấp dự án; chính sách từ xa chỉ có thể làm việc thu thập chặt hơn, không bao giờ lỏng hơn."
  - q: Session replay có chạy ổn định trên Android không?
    a: "Phần lớn là có. Một số tổ hợp bộ kết xuất và thiết bị báo `PixelCopy` thành công nhưng trả về ảnh đen. Từ 0.2.1 SDK phát hiện được điều đó và chuyển sang ghi lại cây layer lưu giữ của Flutter ở độ phân giải thấp hơn. Hãy kiểm tra `getSdkMetrics().lastCaptureSource` khi kiểm chứng trên một thiết bị."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`Rejourney`](https://github.com/rejourneyco/rejourney) là nền tảng mã nguồn mở cho session replay, phân tích sản phẩm và báo cáo crash/ANR, với một SDK Flutter được làm kỹ hơn phần lớn sản phẩm cùng loại. **277★**, cập nhật lần cuối **2026-08-28**.

## Rejourney là gì?

Phần lớn nhóm gỡ lỗi vấn đề chuyển đổi bằng ba công cụ rời rạc: một dashboard phân tích nói rằng phễu bị rớt, một trình báo crash nói rằng có gì đó văng lỗi, và một sản phẩm session replay cho xem một buổi chiều của một người dùng. Việc nối chúng lại với nhau là làm tay.

Tiền đề của Rejourney là giữ tất cả ở một chỗ. Bạn gắn vài **sự kiện chuyển đổi trọng yếu** — `checkout_started`, `purchase_completed` — và nó ghi lại hành trình xung quanh, dữ liệu tương tác (chạm, cuộn, kéo, rage tap) và bằng chứng kỹ thuật (độ trễ và mã trạng thái API, lỗi, vết crash, ANR). Các phiên giống nhau được gom thành nhóm, và khi một nhóm diễn biến xấu quanh một sự kiện chuyển đổi, các bản replay cùng bằng chứng nổi lên thành một vấn đề đã xếp hạng.

Bên cạnh bàn làm việc replay là bản đồ hành trình, heatmap tương tác, khung nhìn theo endpoint, nhóm theo thiết bị và địa lý, cùng phân tích cấp dự án về mức độ áp dụng phiên bản, tỉ lệ giữ chân và — nếu có nối nguồn doanh thu — tác động doanh thu.

## Vì sao SDK Flutter đáng xem

Nhiều sản phẩm phân tích chỉ gắn một lớp bọc Dart mỏng lên SDK native. Rejourney chia theo hướng ngược lại: phần thu thập chạy trong code native, còn API công khai, tích hợp điều hướng, lớp che dữ liệu, hook lỗi và HTTP client đều là Flutter đúng chất.

Điều đó thể hiện ở các chi tiết:

- `RejourneyNavigatorObserver` cắm vào `navigatorObservers` và xử lý push, pop, replace, remove, đồng thời loại bỏ tên màn hình trùng lặp. Với Router khai báo, bạn gọi `Rejourney.trackScreen('checkout')` từ callback đổi route thay thế.
- `RejourneyMask` che một nhánh widget do Flutter vẽ khỏi khung hình được ghi mà không đổi những gì người dùng thấy, đồng thời theo dõi thay đổi bố cục, cuộn và hủy widget.
- `RejourneyHttpClient` bọc `package:http` để ghi phương thức, URL, trạng thái, thời gian, kiểu nội dung và kích thước byte — không ghi nội dung. Với Dio, gRPC hay GraphQL, bạn gọi `Rejourney.logNetworkRequest(...)` từ một interceptor.
- `RejourneyErrorCapture.install()` đặt trước `runApp`.

Đường thu thập trên Android xứng đáng được nhắc riêng. Một số tổ hợp bộ kết xuất và thiết bị báo `PixelCopy` thành công nhưng trả về một ảnh bitmap đen hoàn toàn. Thay vì bảo bạn đổi chế độ kết xuất, SDK phát hiện cái "thành công giả" đó và chuyển sang ghi cây layer lưu giữ của Flutter ở độ phân giải thấp hơn, để yên `FlutterSurfaceView` đang chạy. `getSdkMetrics().lastCaptureSource` cho biết đường nào đang hoạt động. Đó là loại vấn đề chỉ sửa được sau khi đã phát hành lên máy thật.

## Bắt đầu

```bash
flutter pub add rejourney
```

Yêu cầu tối thiểu: Flutter 3.22, Dart 3.3, iOS 15.1, Android API 24. Trên một app iOS có sẵn, bạn có thể cần `cd ios && pod install`.

```dart
import 'package:rejourney/rejourney.dart';

await Rejourney.init('pk_live_your_public_key');
await Rejourney.start();
```

`init` không bao giờ bắt đầu thu thập — sự tách biệt đó tồn tại để bạn chờ được sự đồng ý:

```dart
if (await consentStore.canRecord()) {
  final result = await Rejourney.start();
  debugPrint('session=${result.sessionId} replay=${!result.telemetryOnly}');
}
```

Gọi `Rejourney.stop()` nếu người dùng rút lại sự đồng ý. Sau đó thêm navigator observer, bọc các ô nhập nhạy cảm trong `RejourneyMask`, và ghi các sự kiện chuyển đổi của bạn:

```dart
await Rejourney.logEvent('purchase_completed', <String, Object?>{
  'transactionId': order.id,
  'amount': order.total,
  'currency': 'USD',
});
```

## Khi nào nên dùng Rejourney?

- bạn muốn replay, phân tích và báo cáo crash được liên hệ với nhau thay vì nằm ở ba tab
- ANR và crash native quan trọng với bạn không kém gì ngoại lệ ở tầng Dart
- quy định về nơi lưu dữ liệu hoặc chi phí khiến bạn không dùng được dịch vụ phân tích thuê ngoài
- bạn cần che dữ liệu theo từng widget chứ không phải một công tắc "ẩn hết chữ" toàn cục

## Điểm còn hạn chế

Giấy phép là kép, và ranh giới đó quan trọng. SDK client, ví dụ và tài liệu theo Apache 2.0 — an toàn để phát hành. Backend và dashboard theo **SSPL 1.0**: dùng nội bộ thì ổn, nhưng nếu bạn cung cấp Rejourney như một dịch vụ thì phải công bố mã nguồn dịch vụ của mình. Ai đang hiểu "mã nguồn mở" đồng nghĩa với "không ràng buộc gì" thì nên đọc file `LICENSE` trước khi xây sản phẩm trên nó.

Tự host một backend replay cũng không phải việc làm trong một cuối tuần. Bạn đang vận hành khâu nạp dữ liệu, lưu trữ và một dashboard cho loại dữ liệu gần như video, và hóa đơn lưu trữ tăng theo lưu lượng chứ không theo quy mô nhóm.

Dự án cũng thành thật rằng các báo cáo vấn đề của nó mang tính suy đoán — một mẫu hình được báo là "điểm khởi đầu để điều tra, không phải bằng chứng nhân quả". Hãy xem trọng điều đó. Một tương quan theo nhóm cộng một gợi ý sửa chỉ là giả thuyết, và triển khai nó mà không đối chiếu với trạng thái sản phẩm hay thanh toán có thẩm quyền chính là cách người ta tự tin sửa nhầm chỗ.

Cuối cùng: session replay trên một sản phẩm thật là quyết định về quyền riêng tư trước khi là quyết định kỹ thuật. Sự đồng ý, việc che dữ liệu và kiểm thử replay trên đúng các luồng đăng nhập, thanh toán và sức khỏe mà bạn phát hành không phải phần tùy chọn.

## Các lựa chọn đáng so sánh

- Sentry — giám sát crash và hiệu năng đã chín, nhưng không có phân tích sản phẩm hay khung nhìn hành trình
- PostHog — bản tương đương mã nguồn mở gần nhất, mạnh hơn ở web, mỏng hơn ở thu thập native trên mobile
- [appwrite: hướng dẫn AI/ML trong Flutter](/vi/recipes/appwrite/) và [serverpod: hướng dẫn giao diện & thành phần UI trong Flutter](/vi/recipes/serverpod/) — những backend tự host bạn có thể đã đang chạy

## Câu hỏi thường gặp

### Thêm Rejourney vào ứng dụng Flutter thế nào?

`flutter pub add rejourney`, rồi `await Rejourney.init('pk_live_...')` lúc khởi động và `await Rejourney.start()` chỉ sau khi bạn đã có quyết định về sự đồng ý. `init` cố tình không bao giờ bắt đầu thu thập. Yêu cầu tối thiểu là Flutter 3.22, Dart 3.3, iOS 15.1 và Android API 24.

### Rejourney có thật sự là mã nguồn mở không?

Một phần, và họ nói thẳng điều đó. API Flutter, cầu nối nền tảng, lõi native, ví dụ và tài liệu theo Apache 2.0. Backend và dashboard theo SSPL 1.0 — tự chạy nội bộ thì miễn phí, nhưng nếu cung cấp nó như một dịch vụ thì bạn buộc phải công bố mã nguồn dịch vụ của mình.

### Nó xử lý các trường dữ liệu nhạy cảm ra sao?

Bọc nhánh widget trong `RejourneyMask`, nó che một vùng trong khung hình được ghi mà không thay đổi những gì người dùng nhìn thấy. Lớp này nằm trên cơ chế nhận diện trường bảo mật ở tầng native và các quy tắc riêng tư về văn bản, media ở cấp dự án; chính sách từ xa chỉ có thể làm việc thu thập chặt hơn, không bao giờ lỏng hơn.

### Session replay có chạy ổn định trên Android không?

Phần lớn là có. Một số tổ hợp bộ kết xuất và thiết bị báo `PixelCopy` thành công nhưng trả về ảnh đen; từ 0.2.1 SDK phát hiện được điều đó và chuyển sang ghi lại cây layer lưu giữ của Flutter ở độ phân giải thấp hơn. Hãy kiểm tra `getSdkMetrics().lastCaptureSource` khi kiểm chứng trên một thiết bị.

## Tài nguyên & liên kết

- **GitHub:** [rejourneyco/rejourney](https://github.com/rejourneyco/rejourney)
- **pub.dev:** [rejourney](https://pub.dev/packages/rejourney)
- **Website:** [rejourney.co](https://rejourney.co/)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
