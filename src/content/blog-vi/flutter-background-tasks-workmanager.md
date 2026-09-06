---
title: "Chạy nền trong Flutter: hệ điều hành thật sự cho phép bạn chạy gì"
description: "Android và iOS có quan điểm khác nhau, và cứng rắn như nhau, về việc chạy mã khi ứng dụng của bạn không ở phía trước. Hiểu những giới hạn đó trước khi chọn gói sẽ cứu bạn khỏi việc xây một tính năng mà nền tảng sẽ lặng lẽ từ chối thực thi."
seoDescription: "Thực thi nền trong Flutter: WorkManager và BGTaskScheduler qua gói workmanager, điểm vào isolate, ràng buộc, giới hạn của iOS, foreground service, và khi nào nên chuyển việc lên máy chủ."
keywords:
  - tác vụ nền flutter
  - gói workmanager flutter
  - điểm vào isolate nền flutter
  - bgtaskscheduler ios flutter
  - foreground service android flutter
  - đồng bộ nền định kỳ flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-19"
emoji: "⏱️"
tags: ["Flutter", "Background", "Android", "iOS", "Architecture"]
sources:
  - name: "workmanager — pub.dev"
    url: "https://pub.dev/packages/workmanager"
  - name: "WorkManager — tài liệu Android"
    url: "https://developer.android.com/topic/libraries/architecture/workmanager"
  - name: "BGTaskScheduler — tài liệu Apple"
    url: "https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler"
  - name: "Foreground service — tài liệu Android"
    url: "https://developer.android.com/develop/background-work/services/foreground-services"
  - name: "Isolate — tài liệu Dart"
    url: "https://dart.dev/language/isolates"
  - name: "Tiến trình nền — tài liệu Flutter"
    url: "https://docs.flutter.dev/packages-and-plugins/background-processes"
related:
  - slug: "flutter-isolates-off-main-thread"
    title: "Isolate trong Flutter: cái gì thật sự rời khỏi UI thread, cái gì thì không"
  - slug: "flutter-push-notifications-fcm"
    title: "Push notification trong Flutter: bốn trạng thái ứng dụng có thể đang ở"
draft: false
---

"Đồng bộ dữ liệu người dùng mười lăm phút một lần" nghe như bài toán lập lịch. Thực ra đó là cuộc thương lượng với hai hệ điều hành đã dành cả thập kỷ để giỏi hơn trong việc nói không.

Trước khi chọn gói, đáng để nói chính xác từng nền tảng thật sự cho gì, vì khoảng cách giữa chúng quyết định tính năng của bạn được phép hứa điều gì.

## Bạn thật sự được phép làm gì

| Khả năng | Android | iOS |
| --- | --- | --- |
| Chạy nền định kỳ | Có, tối thiểu ~15 phút, còn tuỳ Doze | `BGAppRefreshTask` — hệ thống quyết định khi nào, có thể là không bao giờ |
| Việc hoãn lại chạy một lần | Có, kèm ràng buộc | `BGProcessingTask`, thường vào ban đêm khi đang sạc |
| Bảo đảm chạy khi ứng dụng đã đóng | Chỉ qua foreground service kèm thông báo nhìn thấy được | Không |
| Việc chạy dài (nhiều phút) | Foreground service | Không — tác vụ nền có vài giây rồi bị đình chỉ |
| Kích hoạt từ máy chủ | Có, FCM mức ưu tiên cao | Hạn chế; push ngầm bị bóp |

Dòng làm thay đổi thiết kế là dòng thứ ba. **Trên iOS không có cách nào bảo đảm mã của bạn chạy khi ứng dụng đã đóng.** Hệ thống học thói quen sử dụng và xếp lịch các cơ hội làm mới quanh đó; người dùng ít mở ứng dụng của bạn có thể không được cơ hội nào trong nhiều ngày. Bất kỳ tính năng nào đặc tả là "phải cập nhật mỗi giờ, bất kể thế nào" đều không xây được trên cơ chế chạy nền của iOS. Nó xây được trên một máy chủ làm việc đó và một push chuyển kết quả về.

## Quy tắc isolate

Dù dùng gói nào, callback nền cũng chạy trong một **isolate mới** không có kết nối gì với trạng thái đang chạy của ứng dụng.

```dart
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((taskName, inputData) async {
    // Isolate riêng: không provider, không singleton, không kết nối đang mở.
    WidgetsFlutterBinding.ensureInitialized();

    switch (taskName) {
      case 'sync':
        final db = await openDatabase();
        try {
          await SyncService(db).runOnce();
          return true;
        } catch (e, s) {
          await logToDisk(e, s);
          return false; // Yêu cầu nền tảng thử lại theo backoff.
        } finally {
          await db.close();
        }
      default:
        return true;
    }
  });
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Workmanager().initialize(callbackDispatcher);
  runApp(const MyApp());
}
```

Ba chi tiết chịu lực:

**`@pragma('vm:entry-point')`** — không có nó thì hàm bị cắt khỏi bản release. Chạy được ở debug, im lặng không làm gì ở release. Đây là lỗi chạy nền phổ biến nhất trong Flutter.

**`WidgetsFlutterBinding.ensureInitialized()` bên trong callback** — isolate mới chưa có binding, nên mọi kênh plugin bạn đụng tới sẽ hỏng nếu thiếu dòng này.

**Giá trị boolean trả về là một hợp đồng.** Trả `false` nghĩa là báo cho nền tảng biết tác vụ đã thất bại và nên thử lại theo chính sách backoff. Trả `true` khi thất bại nghĩa là công việc bị bỏ trong im lặng.

Vì isolate là mới tinh, mọi thứ nó cần phải đến từ `inputData` (chỉ chứa kiểu nguyên thuỷ) hoặc từ đĩa. Truyền cả đồ thị đối tượng là không thể, và bất kỳ giá trị `SharedPreferences` nào bạn đọc ở đó cũng do một isolate khác ghi — không sao, nhưng hãy ý thức rằng ghi từ nền và từ tiền cảnh có thể tranh nhau.

## Lập lịch kèm ràng buộc

```dart
await Workmanager().registerPeriodicTask(
  'sync-task-id',
  'sync',
  frequency: const Duration(hours: 1),
  constraints: Constraints(
    networkType: NetworkType.connected,
    requiresBatteryNotLow: true,
  ),
  existingWorkPolicy: ExistingWorkPolicy.keep,
  backoffPolicy: BackoffPolicy.exponential,
  initialDelay: const Duration(minutes: 10),
);
```

Ràng buộc là phần người ta hay bỏ qua rồi thắc mắc vì sao người dùng phàn nàn về pin. `requiresBatteryNotLow` và `networkType` cho hệ thống gộp việc của bạn cùng việc của mọi ứng dụng khác, vừa tốt cho thiết bị vừa tăng khả năng nó thật sự được chạy.

`existingWorkPolicy: keep` quan trọng nếu bạn đăng ký ở mỗi lần khởi động — không có nó, `replace` sẽ huỷ rồi lên lịch lại mỗi lần chạy, và một tác vụ liên tục bị lên lịch lại có thể không bao giờ tới được lần thực thi đầu tiên.

`frequency` bạn yêu cầu là mức *tối thiểu*, không phải lời hứa. Một tác vụ mỗi giờ trên thiết bị đang ở Doze có thể chỉ chạy một lần qua đêm. Hãy thiết kế công việc sao cho đúng ở mọi nhịp: idempotent, tiếp tục được, và đối chiếu lại thay vì cộng dồn.

## Khi bạn thật sự cần nó chạy

Nếu công việc là thứ người dùng nhìn thấy và phải hoàn tất — tải file lên, theo dõi buổi tập, phát nhạc — thì câu trả lời trên Android là **foreground service** kèm thông báo thường trực, không phải WorkManager. Các gói như `flutter_foreground_task` bọc sẵn phần này. Thông báo nhìn thấy được không phải tuỳ chọn; đó là thoả thuận mà nền tảng đưa ra để đổi lấy việc chạy đáng tin cậy.

Các bản Android gần đây còn yêu cầu khai báo *loại* foreground service trong manifest và xin quyền tương ứng, còn Play thì soát lý do sử dụng. Hãy chọn loại một cách trung thực — khai "data sync" mà dùng cho việc khác là rủi ro bị từ chối.

Trên iOS, danh sách tương đương thì ngắn và cụ thể: phát âm thanh, cập nhật vị trí, VoIP và vài mục khác, mỗi thứ đòi background mode tương ứng và đều bị soát khi duyệt. Nếu ca sử dụng của bạn không nằm trong danh sách thì nó không tồn tại, và thiết kế vòng qua điều đó từ sớm rẻ hơn là phát hiện ra lúc nộp bài.

## Thiết kế sống được trên cả hai nền tảng

Với bất cứ thứ gì gần với "giữ dữ liệu luôn mới", hình dạng chạy được ở mọi nơi là:

1. **Máy chủ làm việc đó.** Nó biết lịch và không ngủ.
2. **Một push báo cho ứng dụng biết có thay đổi** — chỉ-data trên Android nơi độ tin cậy tốt hơn, và chấp nhận rằng iOS có thể gộp lại.
3. **Ứng dụng đồng bộ khi quay lại.** Đây là đường thật sự chạy, trên cả hai nền tảng, mọi lần.
4. **Tác vụ nền là phần tối ưu**, giúp ứng dụng mới hơn khi hệ điều hành thấy rộng rãi — không bao giờ là cơ chế mà tính năng phụ thuộc vào.

Viết theo cách đó thì việc chạy nền thất bại chỉ khiến màn hình đầu hơi cũ một chút, chứ không phải tính năng hỏng. Tôi chưa thấy thiết kế nào giả định chạy nền đáng tin trên iOS mà sống sót khi gặp người dùng thật.

## Gỡ lỗi

Mã chạy nền khó quan sát vì trình gỡ lỗi của bạn không gắn vào lúc nó chạy. Hai thứ giúp ích vượt trội:

- **Ghi log ra file, không ra console.** Hãy ghi một dòng có mốc thời gian ở đầu và cuối mỗi lần chạy nền, rồi bày ra ở một màn hình gỡ lỗi. Không có nó, bạn không phân biệt được "chưa từng được lên lịch" với "đã chạy và thất bại".
- **Ép chạy.** Trên Android, `adb shell cmd jobscheduler run -f <package> <job-id>` kích hoạt job ngay lập tức. Trên iOS, trình gỡ lỗi của Xcode có thể kích hoạt một tác vụ `BGTaskScheduler` đã đăng ký bằng lệnh debugger. Cả hai đều nhanh hơn ngồi chờ rất nhiều.

## Câu hỏi thường gặp

**Vì sao tác vụ của tôi không bao giờ chạy trên iOS?**

Nhiều khả năng là nó đang hoạt động đúng thiết kế. Hãy xác nhận background mode đã khai báo, định danh đã đăng ký trước khi khởi chạy hoàn tất, rồi kiểm thử bằng lệnh kích hoạt của Xcode thay vì ngồi chờ.

**Chạy tác vụ mỗi phút được không?**

Không. Sàn của Android là khoảng mười lăm phút cho việc định kỳ; iOS thì không nhận tham số tần suất nào cả. Một foreground service chạy liên tục được, kèm cái thông báo mà nó đòi hỏi.

**Isolate nền có dùng chung kết nối cơ sở dữ liệu của tôi không?**

Không. Hãy tự mở và tự đóng. Truy cập đồng thời từ hai isolate cần một cơ sở dữ liệu hỗ trợ điều đó — hãy kiểm tra bảo đảm của gói bạn dùng thay vì mặc định là được.

**Chạy nền có hao pin không?**

Có thể, và đó là lý do ràng buộc tồn tại. Hãy tôn trọng `requiresBatteryNotLow`, giữ mỗi lần chạy ngắn, và đừng bao giờ hỏi vòng khi một push là đủ.

**`Timer.periodic` có phải một lựa chọn không?**

Chỉ khi ứng dụng còn sống ở tiền cảnh. Nó dừng khi ứng dụng bị đình chỉ, đúng vào tình huống mà việc chạy nền sinh ra để phục vụ.

---

*Khả năng của từng nền tảng, API `workmanager`, yêu cầu `vm:entry-point` và các quy định về foreground service mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Cách đóng khung bảng khả năng, khuyến nghị thiết kế bốn bước, thói quen ghi log ra file và đánh giá rằng không thể phụ thuộc vào việc chạy nền trên iOS là nhận định riêng của tôi từ việc xây tính năng đồng bộ. Chính sách chạy nền của các nền tảng siết lại gần như ở mọi bản phát hành hệ điều hành — hãy kiểm tra giới hạn hiện hành trong tài liệu nền tảng trước khi thiết kế xoay quanh chúng.*
