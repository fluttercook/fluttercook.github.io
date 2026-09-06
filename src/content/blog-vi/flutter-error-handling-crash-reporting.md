---
title: "Xử lý lỗi trong Flutter: bắt được thứ thật sự tới tay người dùng"
description: "Flutter có bốn chỗ riêng biệt để một lỗi thoát ra: framework, zone hiện tại, platform dispatcher, và isolate. Nối đủ bốn, giải mã stack trace, và ngừng phát hành những cú sập mà bạn không bao giờ nhìn thấy."
seoDescription: "Xử lý lỗi và báo cáo sự cố trong Flutter: FlutterError.onError, PlatformDispatcher.onError, Isolate.addErrorListener, ErrorWidget.builder, làm rối mã và giải mã stack trace, cùng chuyện nên bắt gì và nên để lỗi nổ."
keywords:
  - xử lý lỗi flutter
  - fluttererror onerror crashlytics
  - platformdispatcher onerror
  - lắng nghe lỗi isolate flutter
  - errorwidget builder flutter
  - giải mã stack trace đã làm rối flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-16"
emoji: "🚨"
tags: ["Flutter", "Errors", "Monitoring", "Production", "Debugging"]
sources:
  - name: "Xử lý lỗi trong Flutter — tài liệu Flutter"
    url: "https://docs.flutter.dev/testing/errors"
  - name: "FlutterError — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/FlutterError-class.html"
  - name: "PlatformDispatcher — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/PlatformDispatcher-class.html"
  - name: "Isolate.addErrorListener — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-isolate/Isolate/addErrorListener.html"
  - name: "Làm rối mã Dart — tài liệu Flutter"
    url: "https://docs.flutter.dev/deployment/obfuscate"
  - name: "ErrorWidget — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ErrorWidget-class.html"
related:
  - slug: "flutter-memory-leaks-devtools"
    title: "Tìm rò rỉ bộ nhớ trong Flutter: năm loại đối tượng không bao giờ được dispose"
  - slug: "flutter-ci-cd-github-actions"
    title: "Một pipeline CI cho Flutter thật sự bắt được lỗi"
draft: false
---

Tỉ lệ không-sập 99,8% nghe rất đẹp cho tới khi bạn nhận ra nó chỉ đếm những cú sập mà công cụ báo cáo của bạn được nối để nhìn thấy. Trong Flutter, một lỗi có thể thoát ra qua bốn cánh cửa khác nhau, và phần lớn ứng dụng chỉ canh một hoặc hai.

## Bốn cánh cửa

| Cánh cửa | Bắt được gì | Bỏ sót gì nếu không nối |
| --- | --- | --- |
| `FlutterError.onError` | Lỗi bên trong framework: build, layout, paint, callback cử chỉ | Màn hình đỏ, lỗi bố cục âm thầm |
| `PlatformDispatcher.instance.onError` | Lỗi bất đồng bộ chưa bắt ở zone gốc | Phần lớn lỗi `Future` |
| `Isolate.current.addErrorListener` | Lỗi trong các isolate bạn sinh ra | Mọi lỗi tính toán chạy nền |
| Bộ xử lý sập native | Sập ở tầng nền tảng, mã native của plugin | Bất cứ thứ gì giết tiến trình |

Đây là cả bốn, nối một lần lúc khởi động:

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  final crashlytics = FirebaseCrashlytics.instance;

  // 1. Lỗi của framework.
  FlutterError.onError = (details) {
    crashlytics.recordFlutterFatalError(details);
    if (kDebugMode) FlutterError.presentError(details);
  };

  // 2. Lỗi bất đồng bộ chưa bắt tới được nền tảng.
  PlatformDispatcher.instance.onError = (error, stack) {
    crashlytics.recordError(error, stack, fatal: true);
    return true; // đã xử lý
  };

  // 3. Lỗi từ các isolate do isolate này sinh ra.
  Isolate.current.addErrorListener(RawReceivePort((List<dynamic> pair) {
    crashlytics.recordError(pair.first, StackTrace.fromString(pair.last));
  }).sendPort);

  runApp(const MyApp());
}
```

Ba chi tiết đáng dừng lại.

**Trả về `true` từ `PlatformDispatcher.onError`** báo cho engine biết lỗi đã được xử lý và không nên ném lại. Trả về `false` sẽ để nó lan tới cả bộ xử lý mặc định, thường dẫn tới một báo cáo trùng.

**Chỉ gọi `presentError` ở debug.** Ở bản release bạn không muốn đầu ra lỗi của framework; bạn muốn bản báo cáo. Ở debug thì bạn rất muốn màn hình đỏ, vì đó là cách bạn nhận ra vấn đề.

**Bộ lắng nghe isolate chỉ phủ những isolate bạn sinh ra**, và chỉ những cái sinh sau khi nó được đăng ký. Một lời gọi `compute()` không tự kế thừa gì — lỗi bên trong nó lộ ra dưới dạng một `Future` thất bại, và cánh cửa thứ hai bắt được, miễn là không ai nuốt mất nó bằng một `catch` rỗng.

`runZonedGuarded` từng là lời khuyên chuẩn và giờ phần lớn đã được `PlatformDispatcher.onError` thay thế cho mục đích này. Dùng cả hai không gây hại, nhưng thường là dư; hãy chọn một và biết rõ mình chọn cái nào.

## Màn hình đỏ mà người dùng nhìn thấy

Ở bản release, một ngoại lệ trong phương thức build sẽ thay widget bằng một ô xám. Thế thì tốt hơn sập, nhưng tệ hơn một quyết định thiết kế:

```dart
ErrorWidget.builder = (FlutterErrorDetails details) {
  if (kDebugMode) return ErrorWidget(details.exception);

  return const Material(
    child: Center(
      child: Padding(
        padding: EdgeInsets.all(24),
        child: Text(
          'Chỗ này có gì đó không ổn. Vui lòng thử lại sau ít phút.',
          textAlign: TextAlign.center,
        ),
      ),
    ),
  );
};
```

Đặt nó một lần. Nó tốn mười dòng và biến một hình chữ nhật xám đáng sợ thành thứ đọc lên có vẻ là cố ý.

Với một cây con có thể hỏng độc lập — một mục trong feed, một biểu đồ, một khung nhìn do plugin cung cấp — một lớp bọc nhỏ ngăn một lỗi làm trắng cả màn hình:

```dart
class ErrorBoundary extends StatefulWidget {
  const ErrorBoundary({super.key, required this.child, required this.fallback});

  final Widget child;
  final Widget fallback;

  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}
```

Flutter không có error boundary dựng sẵn bắt được lỗi build của widget con theo kiểu React — `FlutterError.onError` nổ ở phạm vi toàn cục, nên phiên bản thực dụng là khoanh vùng bằng cách dựng lại phần dự phòng khi phát hiện một kiểu hỏng đã biết, chứ không phải bắt ngoại lệ tuỳ ý của widget con.

## Báo cáo mà bạn hành động được

Riêng một stack trace hiếm khi nói đủ. Khác biệt giữa một lỗi bạn sửa được và một lỗi bạn chỉ biết nhìn chằm chằm là phần ngữ cảnh được gắn vào trước khi sập:

```dart
final class CrashContext {
  static Future<void> setUser(String? id) =>
      FirebaseCrashlytics.instance.setUserIdentifier(id ?? 'anonymous');

  static Future<void> setScreen(String route) =>
      FirebaseCrashlytics.instance.setCustomKey('current_route', route);

  static void breadcrumb(String message) =>
      FirebaseCrashlytics.instance.log(message);
}
```

Hãy ghi lại route ở mỗi lần điều hướng, id của bản ghi mà màn hình đang hiển thị, và lời gọi mạng gần nhất đã thử. Khi đó báo cáo đọc lên thành "sập ở /orders/882 sau khi GET /orders/882 trả về 500" thay vì "toán tử kiểm tra null trên một giá trị null".

Đừng ghi dữ liệu cá nhân. Một báo cáo sự cố là bản sao thông tin người dùng nằm trong hệ thống bên thứ ba; id người dùng và id bản ghi thường là phù hợp, còn địa chỉ email và nội dung tin nhắn thì không.

## Giải mã stack trace, nếu không báo cáo là vô dụng

Bản release biên dịch với `--obfuscate --split-debug-info=<dir>` cho ra stack trace toàn ký hiệu vô nghĩa. Bảng ánh xạ nằm trong thư mục bạn chỉ định, và nó khác nhau ở mỗi lần build:

```bash
flutter build appbundle --obfuscate --split-debug-info=build/symbols/$VERSION
```

Hai quy tắc mà người ta thường học theo cách đau đớn:

1. **Lưu trữ thư mục symbol theo từng phiên bản, ngay trong CI**, cạnh artifact. Không có đúng file cho đúng bản build đó thì báo cáo không giải mã được — và build lại từ cùng mã nguồn cũng không tái tạo được nó.
2. **Tải symbol lên như một phần của job release**, không làm thủ công. Một bước thủ công là bước sẽ bị bỏ quên đúng vào bản phát hành quan trọng.

Khi cần, `flutter symbolize -i trace.txt -d build/symbols/1.4.2/app.android-arm64.symbols` giải mã một trace bằng tay.

## Nên bắt gì và nên để cái gì nổ

Bản năng bọc mọi thứ trong `try`/`catch` tạo ra ứng dụng hỏng trong im lặng và hành xử kỳ quặc. Một quy tắc đứng vững:

- **Bắt thứ bạn hành động được.** Một lần hết giờ mạng thì có phương án thử lại. Một lỗi phân tích dữ liệu thì có phương án dự phòng. Hãy bắt những cái đó, xử lý chúng, và báo cáo ở mức không nghiêm trọng.
- **Để lỗi lập trình nổ ở debug.** Một phép khẳng định null thất bại nghĩa là mô hình của bạn về đoạn mã đó đang sai. Bắt nó lại là che giấu điều đó.
- **Ở bản release, hãy suy giảm chức năng chứ đừng chết** — nhưng luôn báo cáo. Một khối `catch` không báo cáo chính là cơ chế giúp một lỗi sống sót suốt nhiều tháng.

```dart
try {
  return await _api.fetchOrders();
} on TimeoutException catch (e, s) {
  FirebaseCrashlytics.instance.recordError(e, s, fatal: false);
  return _cache.orders ?? const [];
}
```

Bắt `on TimeoutException` thay vì `catch` trần mới là phần quan trọng. Một `catch` trần cũng sẽ nuốt luôn `NoSuchMethodError` sinh từ chính lỗi gõ nhầm của bạn.

## Câu hỏi thường gặp

**Vì sao tôi thấy lỗi trong console mà chúng không bao giờ tới Crashlytics?**

Gần như luôn là một cánh cửa chưa nối — thường nhất là `PlatformDispatcher.onError`, hoặc một lỗi nằm trong `catch` chỉ ghi log rồi đi tiếp.

**Cách này có dùng được với Sentry hay công cụ khác không?**

Có. Bốn cánh cửa là của Flutter, không phải của Firebase; các SDK chỉ khác nhau ở lời gọi ghi nhận.

**`FlutterError.onError` có nên báo là nghiêm trọng không?**

Một lỗi framework thường để ứng dụng chạy tiếp với giao diện hỏng. `recordFlutterFatalError` đưa nó vào chỉ số không-sập, và điều đó có thể coi là đúng; `recordFlutterError` báo nó ở mức không nghiêm trọng. Hãy chọn một và nhất quán, nếu không chỉ số của bạn chẳng có ý nghĩa gì.

**Kiểm thử xem báo cáo có chạy không bằng cách nào?**

Thêm một hành động gỡ lỗi ẩn ném lỗi ở cả bốn ngữ cảnh, chạy bản release, và xác nhận bốn báo cáo tới nơi. Hãy làm điều này mỗi chu kỳ phát hành — cơ chế báo cáo âm thầm hỏng sau các lần nâng cấp phụ thuộc.

**Còn lỗi trong `main()` trước khi khởi tạo báo cáo thì sao?**

Hãy khởi tạo báo cáo sớm nhất có thể, và giữ phần việc trước đó ở mức tối thiểu. Bất cứ thứ gì hỏng trước điểm đó đều vô hình về mặt cấu trúc.

---

*Bốn điểm vào xử lý lỗi, `ErrorWidget.builder`, các lệnh làm rối mã và giải mã stack trace mô tả ở đây đều nằm trong tài liệu Flutter dẫn ở trên. Quy tắc chỉ-bắt-thứ-hành-động-được, thói quen ghi dấu vết, lời khuyên lưu trữ symbol và nghi thức kiểm chứng mỗi chu kỳ phát hành là nhận định riêng của tôi từ việc vận hành ứng dụng Flutter trong môi trường thật. API của các SDK báo cáo sự cố có thay đổi — hãy đối chiếu lời gọi ghi nhận với phiên bản bạn phụ thuộc.*
