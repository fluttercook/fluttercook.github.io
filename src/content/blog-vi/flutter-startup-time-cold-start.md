---
title: "Khởi động nguội trong Flutter: đo khoảng thời gian trước frame đầu tiên"
description: "Khởi động bị cảm thấy chậm từ rất lâu trước khi có ai đó đo đạc. Cách sửa bắt đầu bằng việc biết bạn đang ở giai đoạn nào trong bốn giai đoạn — khởi tạo tiến trình, khởi tạo engine, hàm main của Dart, hay frame đầu tiên — vì mỗi giai đoạn có một cần gạt khác nhau."
seoDescription: "Cách đo và giảm thời gian khởi động Flutter: sự kiện timeline của --trace-startup, bốn giai đoạn khởi động nguội, cái gì thuộc về main(), splash screen, khởi tạo trì hoãn và làm nóng shader."
keywords:
  - tối ưu thời gian khởi động flutter
  - flutter trace-startup timeline
  - flutter khởi động nguội frame đầu tiên
  - flutter main khởi tạo bất đồng bộ
  - splash screen native flutter
  - timeToFirstFrameRasterizedMicros
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-31"
emoji: "🚀"
tags: ["Flutter", "Hiệu năng", "Khởi động", "Profiling", "DevTools"]
sources:
  - name: "Flutter — Performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
  - name: "Flutter — Measuring app startup time"
    url: "https://docs.flutter.dev/perf/appendix#measuring-app-startup-time"
  - name: "Flutter — Adding a splash screen"
    url: "https://docs.flutter.dev/platform-integration/android/splash-screen"
  - name: "WidgetsBinding — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/WidgetsBinding-class.html"
  - name: "SchedulerBinding — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/scheduler/SchedulerBinding-class.html"
  - name: "Timeline — tài liệu Dart API"
    url: "https://api.flutter.dev/flutter/dart-developer/Timeline-class.html"
related:
  - slug: "flutter-app-size-reduction"
    title: "Thu nhỏ ứng dụng Flutter: megabyte thật sự nằm ở đâu"
  - slug: "flutter-isolates-off-main-thread"
    title: "Isolate trong Flutter: cái gì thật sự rời khỏi UI thread, cái gì thì không"
draft: false
---

"App mở mất ba giây" là một lời phàn nàn, không phải một phép đo. Ba giây tính từ đâu — từ cú chạm, từ lúc tiến trình sinh ra, từ lúc engine dựng lên, hay từ khoảnh khắc `main()` của bạn chạy? Mỗi mốc là một vấn đề khác nhau với cách sửa khác nhau, và tối ưu nhầm chỗ chính là cách một đội tiêu cả sprint để đưa thời gian khởi động từ 2,9 giây xuống 2,8 giây.

Khởi động nguội của ứng dụng Flutter có bốn giai đoạn, và chúng tách bạch được.

## Bốn giai đoạn

**1. Khởi tạo tiến trình.** Hệ điều hành tạo tiến trình, nạp file thực thi cùng các thư viện chia sẻ, rồi trao quyền cho phần runner của nền tảng. Không có gì trong code Dart của bạn ảnh hưởng tới giai đoạn này. Thứ có ảnh hưởng là kích thước binary (xem bài về kích thước ứng dụng) và, trên Android, số thư viện phải liên kết.

**2. Khởi tạo engine.** Engine Flutter khởi động, Dart VM dựng lên, và — ở bản release — snapshot AOT được ánh xạ vào bộ nhớ. Việc đăng ký plugin ở phía nền tảng diễn ra tại đây.

**3. Từ `main()` của Dart tới `runApp()`.** Code của bạn. Đây là giai đoạn bạn kiểm soát hoàn toàn, và là giai đoạn người ta lặng lẽ nhồi đầy `await`.

**4. Frame đầu tiên.** Build, layout, paint, rasterise. Người dùng nhìn thấy một cái gì đó.

Con số quan trọng với người dùng là điểm kết thúc của giai đoạn 4. Con số bạn dịch chuyển được dễ nhất là giai đoạn 3.

## Đo cho đúng

```bash
flutter run --profile --trace-startup
```

Lệnh này ghi `start_up_info.json` trong thư mục build với bốn giá trị tính bằng micro giây:

| Khoá | Ý nghĩa |
| --- | --- |
| `engineEnterTimestampMicros` | Mốc thời gian tuyệt đối lúc engine bắt đầu |
| `timeToFrameworkInitMicros` | Engine bắt đầu → framework khởi tạo xong |
| `timeToFirstFrameRasterizedMicros` | Engine bắt đầu → frame đầu tiên lên màn hình |
| `timeToFirstFrameMicros` | Engine bắt đầu → frame đầu tiên được dựng |

Khoảng cách giữa `timeToFirstFrameMicros` và `timeToFirstFrameRasterizedMicros` có tính chẩn đoán: nếu nó lớn, frame đầu của bạn đắt ở khâu *rasterise* (shader, ảnh lớn, clip phức tạp), chứ không đắt ở khâu dựng. Đó là hai cách sửa khác nhau.

Hai quy tắc để phép đo có ý nghĩa: **chế độ profile, thiết bị thật**. Bản debug chạy JIT của Dart và khởi động chậm hơn nhiều lần; máy ảo có đặc tính I/O và GPU khác với chiếc điện thoại người dùng đang cầm. Và hãy đo một lần khởi động nguội thật sự — force-stop ứng dụng trước, chứ không chỉ đưa nó xuống nền.

Để nhìn chi tiết hơn bên trong giai đoạn 3, hãy thêm sự kiện timeline của riêng bạn:

```dart
Future<void> main() async {
  Timeline.startSync('bootstrap');
  WidgetsFlutterBinding.ensureInitialized();

  Timeline.startSync('prefs');
  final prefs = await SharedPreferences.getInstance();
  Timeline.finishSync();

  Timeline.startSync('db-open');
  final db = await openDatabase();
  Timeline.finishSync();

  Timeline.finishSync();
  runApp(MyApp(prefs: prefs, db: db));
}
```

Chúng hiện lên thành các lát cắt có tên trong timeline của DevTools, và thường chấm dứt tranh cãi ngay lập tức — một trong những `await` đó gần như luôn chiếm 80% giai đoạn 3.

## Cái gì thuộc về `main()`, cái gì thì không

Kiểu hỏng mặc định là một `main()` await sáu thứ trước `runApp`. Mỗi lần await là thêm thời gian trên một màn hình trống.

Phép thử cho mỗi khoản khởi tạo rất đơn giản: **frame đầu tiên có phụ thuộc vào nó không?**

| Phải nằm trước `runApp` | Có thể để sau |
| --- | --- |
| Bất cứ thứ gì constructor của `MyApp` cần | Analytics và báo cáo crash (đăng ký handler sớm, khởi tạo lười) |
| Chế độ theme và locale đã lưu, nếu bạn không chấp nhận nháy sai một nhịp | Tải remote config |
| Kiểm tra đồng bộ "người dùng đã đăng nhập chưa" | Migration cơ sở dữ liệu cho màn hình chưa hiện |
| `WidgetsFlutterBinding.ensureInitialized()` | Đăng ký thông báo đẩy |
| | Nạp trước ảnh cho màn hình thứ ba |

Mọi thứ ở cột phải đều có thể dời ra sau frame đầu tiên:

```dart
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MyApp());

  // Sau khi frame đầu tiên đã lên màn hình.
  WidgetsBinding.instance.addPostFrameCallback((_) {
    unawaited(_initAnalytics());
    unawaited(_warmCaches());
  });
}
```

`addPostFrameCallback` chạy sau khi frame được dựng. Với công việc hoàn toàn không nên cạnh tranh với vài frame hoạt ảnh đầu tiên, `SchedulerBinding.instance.scheduleTask` với độ ưu tiên thấp sẽ hoãn nó cho tới khi bộ lập lịch rảnh.

Với những thứ thật sự phải await, hãy chạy chúng song song thay vì tuần tự:

```dart
final (prefs, db, keys) = await (
  SharedPreferences.getInstance(),
  openDatabase(),
  loadSigningKeys(),
).wait;
```

Ba lần await 60 ms nối tiếp là 180 ms; chạy song song còn 60. Một dòng này thường là khoản thắng đơn lẻ lớn nhất có thể có, vì `await` tuần tự là cách mặc định người ta viết `main()`.

Công việc đồng bộ nặng — phân tích một file JSON lớn đóng kèm, suy ra một khoá — thuộc về isolate, không thuộc về đường khởi động của luồng chính.

## Màn hình trống, và nên đặt gì lên đó

Giai đoạn 1 và 2 diễn ra trước khi bất kỳ dòng Dart nào chạy, nên không widget Flutter nào che được chúng. Thứ che được là **splash screen của nền tảng**: một launch theme trên Android, một launch storyboard trên iOS. Đó không phải mẹo vặt, đó là cơ chế của nền tảng, và nó biến "màn hình trắng trống" thành "ứng dụng đang mở".

Chi tiết quan trọng là tính liên tục. Nếu splash native hiện logo canh giữa trên nền xanh thương hiệu, thì frame Flutter đầu tiên cũng nên là logo canh giữa trên nền xanh thương hiệu — rồi mới chuyển cảnh. Một splash native cắt phựt sang một splash Flutter khác trông *chậm hơn* so với việc giữ nguyên một màn hình lâu hơn chút, vì người dùng cảm nhận cú nháy đó như một lần khởi động lại.

Một cái bẫy liên quan: ứng dụng hiện splash Flutter có hoạt ảnh của riêng nó trong đúng 1,5 giây là ứng dụng đã *cộng thêm* 1,5 giây vào thời gian khởi động. Nếu hoạt ảnh đó là bản sắc thương hiệu thì được — nhưng đừng chốt nó bằng bộ đếm giờ khi dữ liệu đã tải xong.

## Chi phí của chính frame đầu tiên

Nếu `timeToFirstFrameRasterizedMicros` lớn hơn hẳn `timeToFirstFrameMicros`, vấn đề nằm ở luồng raster.

**Biên dịch shader.** Lần đầu một shader cụ thể được cần tới, nó phải được biên dịch, và việc đó có thể làm nghẽn frame. Impeller được xây dựng chính là để xử lý nhóm giật này bằng cách tránh biên dịch shader lúc chạy cho những trường hợp nó hỗ trợ; trên backend Skia cũ, đây là nguyên nhân kinh điển của hiện tượng "lần chạy đầu của hoạt ảnh bị giật". Bạn dùng backend nào thì tuỳ nền tảng và phiên bản Flutter — hãy kiểm tra bản build của bạn thật sự dùng gì thay vì phỏng đoán.

**Màn hình đầu quá nặng.** Một màn hình chính dựng bốn mươi widget, giải mã sáu ảnh và layout một lưới phức tạp sẽ mất thời gian để hiện ra. Cách sửa phổ biến và trung thực là cố ý làm frame đầu tiên rẻ: dựng phần khung — app bar, nền, các khối skeleton — ngay lập tức, rồi lấp nội dung vào các frame kế tiếp. Mức cải thiện cảm nhận được lớn hơn mức đo được, và điều đó ổn, vì cảm nhận mới là mục tiêu thật.

**Giải mã ảnh lớn.** Giải mã một ảnh hero 4000 pixel sẽ chặn luồng. Hãy đóng gói nó ở đúng kích thước, và dùng `cacheWidth`/`cacheHeight` để bộ giải mã chỉ tạo ra đúng phần bạn hiển thị.

## Một quy trình làm việc

1. `flutter run --profile --trace-startup` trên thiết bị thật, ba lần khởi động nguội, lấy trung vị.
2. Đọc `start_up_info.json`. Xác định vấn đề của bạn nằm ở giai đoạn 3 (`timeToFrameworkInitMicros` → `timeToFirstFrameMicros`) hay giai đoạn 4 (dựng → rasterise xong).
3. Nếu là giai đoạn 3: gắn `Timeline` vào `main()`, rồi song song hoá hoặc trì hoãn.
4. Nếu là giai đoạn 4: đơn giản hoá màn hình đầu, kiểm tra kích thước giải mã ảnh, xem luồng raster trong timeline của DevTools.
5. Đo lại theo đúng cách cũ. Ghi con số vào chỗ cả đội nhìn thấy, nếu không nó sẽ tụt lại sau hai sprint.

## Câu hỏi thường gặp

**Vì sao bản debug khởi động chậm hơn nhiều thế?**

Bản debug dùng JIT của Dart, kèm service isolate, observatory và các assertion. Tỉ lệ so với release rất lớn và không tỉ lệ thuận — đừng bao giờ tinh chỉnh khởi động dựa trên phép đo ở bản debug.

**`WidgetsFlutterBinding.ensureInitialized()` có tốn nhiều không?**

Nó nhanh, và là bắt buộc trước khi bạn chạm vào platform channel (thứ mà `SharedPreferences`, các package đường dẫn và đa số plugin đều dùng). Hãy gọi nó đầu tiên trong `main()`.

**Tôi có nên nạp trước dữ liệu trong lúc splash không?**

Chỉ nạp thứ mà màn hình đầu cần. Nạp trước cho màn hình thứ hai trong lúc splash là đánh đổi một chi phí khởi động đo được lấy một lợi ích mà người dùng có thể không bao giờ chạm tới.

**Ứng dụng nhỏ hơn có khởi động nhanh hơn không?**

Nó ảnh hưởng giai đoạn 1, và quan trọng nhất trên máy cấu hình thấp cùng cache hệ thống tập tin còn nguội. Đó là hiệu ứng có thật nhưng thường là cần gạt nhỏ hơn một chuỗi `await` tuần tự trong `main()`.

**Làm sao theo dõi chỉ số này theo thời gian?**

`--trace-startup` sinh ra file máy đọc được; hãy chạy nó trong CI trên một cấu hình thiết bị cố định và assert theo ngưỡng. Một con số trên bảng theo dõi là thứ duy nhất ngăn thời gian khởi động trôi ngược lên.

---

*Các trường trong kết quả `--trace-startup`, các API binding và cơ chế splash screen mô tả ở đây được ghi trong tài liệu hiệu năng và tích hợp nền tảng của Flutter đã dẫn. Cách chia bốn giai đoạn, phép thử "frame đầu có phụ thuộc vào nó không", và lời khuyên cố ý làm frame đầu rẻ là đánh giá riêng của tôi từ việc phân tích ứng dụng theo cách này. Hành vi engine — kể cả việc renderer nào chạy trên nền tảng nào — thay đổi giữa các bản Flutter; hãy đo bản build của chính bạn ở chế độ profile trên thiết bị thật.*
