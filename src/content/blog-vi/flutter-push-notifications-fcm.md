---
title: "Push notification trong Flutter: bốn trạng thái ứng dụng có thể đang ở"
description: "Chạy nổi, chạy nền, đã tắt hẳn, và 'người dùng chạm vào thông báo để mở ứng dụng' — mỗi trạng thái đưa tin nhắn đi theo một đường mã khác nhau. Phần lớn lỗi thông báo là một trong bốn trường hợp đó chưa được xử lý."
seoDescription: "Push notification trong Flutter với FCM: bốn trạng thái ứng dụng, background handler phải là hàm cấp cao nhất, notification so với data message, thiết lập APNs cho iOS, điều hướng deep link khi chạm, và cách kiểm thử."
keywords:
  - push notification flutter fcm
  - firebase messaging background handler
  - chạm thông báo deep link flutter
  - data message và notification flutter
  - thiết lập apns ios flutter
  - flutter local notifications foreground
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-21"
emoji: "🔔"
tags: ["Flutter", "Firebase", "Notifications", "Mobile", "Backend"]
sources:
  - name: "firebase_messaging — pub.dev"
    url: "https://pub.dev/packages/firebase_messaging"
  - name: "Các loại tin nhắn FCM — tài liệu Firebase"
    url: "https://firebase.google.com/docs/cloud-messaging/concept-options"
  - name: "Nhận tin nhắn trong ứng dụng Flutter — tài liệu Firebase"
    url: "https://firebase.google.com/docs/cloud-messaging/flutter/receive"
  - name: "flutter_local_notifications — pub.dev"
    url: "https://pub.dev/packages/flutter_local_notifications"
  - name: "Kênh thông báo — tài liệu Android"
    url: "https://developer.android.com/develop/ui/views/notifications/channels"
  - name: "UNUserNotificationCenter — tài liệu Apple"
    url: "https://developer.apple.com/documentation/usernotifications"
related:
  - slug: "flutter-navigation-go-router-deep-links"
    title: "go_router và deep link: những phần mà bài quickstart bỏ qua"
  - slug: "flutter-background-tasks-workmanager"
    title: "Chạy nền trong Flutter: hệ điều hành thật sự cho phép bạn chạy gì"
draft: false
---

Thông báo tới nơi. Lúc thì ứng dụng hiển thị nó, lúc thì hệ điều hành, lúc chạm vào thì mở đúng màn hình còn lúc lại quăng người dùng ra trang chủ. Hành vi trông như ngẫu nhiên cho tới khi bạn nhìn ra cấu trúc bên dưới: **cùng một tin nhắn đi theo bốn đường khác nhau tuỳ theo lúc đó ứng dụng đang làm gì.**

| Trạng thái ứng dụng | Ai hiển thị | Handler nào chạy |
| --- | --- | --- |
| Chạy nổi | Mặc định là không ai | `onMessage` |
| Chạy nền | Hệ điều hành | `onBackgroundMessage` (isolate riêng) |
| Đã tắt hẳn | Hệ điều hành | `onBackgroundMessage` (isolate riêng) |
| Được mở bằng cách chạm | — | `onMessageOpenedApp`, hoặc `getInitialMessage` nếu trước đó đã tắt hẳn |

Mọi lỗi thông báo tôi từng gỡ đều là một trong các dòng đó chưa được xử lý. Nối đủ bốn dòng thì phần lớn sự bí ẩn biến mất.

## Notification message so với data message

Trước khi vào mã, đây là phân biệt quyết định mọi thứ: một payload FCM có thể chứa khối `notification`, khối `data`, hoặc cả hai.

- **Có `notification`** — hệ điều hành tự hiển thị khi ứng dụng chạy nền hoặc đã tắt. Trên iOS, handler của bạn có thể không chạy chút nào trừ khi bạn chủ động bật thêm.
- **Chỉ có `data`** — không có gì được hiển thị tự động. Handler của bạn luôn có cơ hội chạy, và bạn tự hiển thị thứ gì đó.

Tin nhắn chỉ-data cho bạn quyền kiểm soát và lấy đi độ tin cậy: hệ điều hành được phép trì hoãn hoặc bỏ chúng khi giới hạn pin. Notification message thì tin cậy nhưng cứng nhắc. Với phần lớn ứng dụng, câu trả lời đúng là **cả hai** — một khối `notification` để người dùng chắc chắn thấy gì đó, cộng một khối `data` mang thông tin điều hướng cho cú chạm.

```json
{
  "notification": { "title": "Phản hồi mới", "body": "Alex đã trả lời bài của bạn" },
  "data": { "type": "post", "id": "1234" }
}
```

## Thiết lập, và phần bắt buộc phải ở cấp cao nhất

```dart
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // Chạy trong isolate riêng: không truy cập được state hay provider của app.
  debugPrint('Tin nhắn nền: ${message.messageId}');
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);

  runApp(const MyApp());
}
```

Hai chi tiết cỡ một dòng chú thích giấu rất nhiều đau khổ.

**Handler phải là hàm cấp cao nhất hoặc hàm static**, không phải closure và không phải phương thức của thể hiện. Nó được tra cứu theo tên và gọi trong một isolate mới.

**`@pragma('vm:entry-point')`** ngăn quá trình tree-shaking loại bỏ nó ở bản release. Không có nó, tin nhắn nền chạy hoàn hảo ở debug và im lặng không làm gì ở release — đúng kiểu lỗi lọt được ra production.

Vì handler chạy trong **isolate riêng**, nó không chia sẻ gì với ứng dụng đang chạy: không provider, không singleton, không kết nối cơ sở dữ liệu bạn mở ở chỗ khác. Nó ghi được xuống đĩa hay gọi được endpoint mạng; nó không gọi được `setState` hay đọc container Riverpod của bạn.

## Quyền và token

```dart
final class PushService {
  PushService(this._messaging);

  final FirebaseMessaging _messaging;

  Future<bool> requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    return settings.authorizationStatus == AuthorizationStatus.authorized ||
        settings.authorizationStatus == AuthorizationStatus.provisional;
  }

  Future<void> syncToken() async {
    final token = await _messaging.getToken();
    if (token != null) await _api.registerDevice(token);

    _messaging.onTokenRefresh.listen(_api.registerDevice);
  }
}
```

Hãy lắng nghe `onTokenRefresh` và coi đó là đường chính, không phải phương án dự phòng. Token có xoay vòng — khi cài lại, khi khôi phục sang máy mới, thỉnh thoảng không vì lý do nhìn thấy được — và ứng dụng chỉ đăng ký token ở lần chạy đầu sẽ tích tụ dần những người dùng lặng lẽ ngừng nhận được gì.

Hãy xin quyền vào lúc giá trị của nó hiển nhiên, đừng xin ngay lần chạy đầu. Trên iOS, hộp thoại chỉ hiện một lần: người dùng đã từ chối thì không thể hỏi lại từ trong ứng dụng, chỉ qua Cài đặt.

## Hiển thị khi ứng dụng đang chạy nổi

Mặc định, ứng dụng đang chạy nổi không hiển thị gì. Bạn tự chọn:

```dart
FirebaseMessaging.onMessage.listen((message) {
  final notification = message.notification;
  if (notification == null) return;

  _localNotifications.show(
    notification.hashCode,
    notification.title,
    notification.body,
    const NotificationDetails(
      android: AndroidNotificationDetails(
        'messages',
        'Messages',
        importance: Importance.high,
      ),
      iOS: DarwinNotificationDetails(),
    ),
    payload: jsonEncode(message.data),
  );
});
```

Id kênh Android ở đây phải khớp với một kênh bạn tạo lúc khởi động, và **thiết lập của kênh bị cố định ngay khi tạo** — đổi mức importance trong mã sau khi kênh đã tồn tại sẽ không có tác dụng cho tới khi cài lại ứng dụng. Hãy tạo kênh một cách có chủ ý, và dùng id mới nếu bạn thật sự cần hành vi khác.

Cách khác là không hiển thị gì và cập nhật giao diện trong ứng dụng. Với một ứng dụng nhắn tin mà người dùng đang mở đúng cuộc trò chuyện đó, cập nhật tại chỗ hơn hẳn một dải thông báo.

## Điều hướng khi chạm

Đây là dòng hay bị bỏ sót nhất — trường hợp ứng dụng đã tắt hẳn cần một lời gọi riêng:

```dart
Future<void> setupTapRouting(GoRouter router) async {
  void handle(RemoteMessage message) {
    final type = message.data['type'];
    final id = message.data['id'];
    if (type == 'post' && id != null) router.go('/posts/$id');
  }

  // Ứng dụng đã tắt hẳn và được khởi chạy bởi thông báo.
  final initial = await FirebaseMessaging.instance.getInitialMessage();
  if (initial != null) handle(initial);

  // Ứng dụng đang chạy nền và được thông báo đánh thức.
  FirebaseMessaging.onMessageOpenedApp.listen(handle);
}
```

`getInitialMessage` trả về khác null đúng một lần, ở lần khởi chạy do cú chạm gây ra. Hãy gọi nó sau khi router đã tồn tại nhưng trước khi frame đầu ổn định, nếu không việc điều hướng sẽ thực hiện trên một router chưa sẵn sàng.

Hãy coi payload là dữ liệu vào không đáng tin. `router.go(message.data['route'])` với đường dẫn do máy chủ cấp là một nguyên liệu để tiêm route; thay vào đó hãy ánh xạ từ một tập nhỏ các loại đã biết, như ở trên.

## Kiểm thử một cách trung thực

Bốn phép thử, đều đáng làm tay ít nhất một lần mỗi bản phát hành:

1. Chạy nổi với ứng dụng đang mở.
2. Đưa xuống nền bằng nút home, rồi chạm vào thông báo.
3. **Tắt hẳn** ứng dụng (vuốt bỏ), rồi gửi và chạm. Đây là trường hợp hay hỏng.
4. Bản release, không phải debug — lỗi `vm:entry-point` chỉ lộ ra ở đây.

Trên iOS, nhớ rằng thông báo cần máy thật với khoá APNs hợp lệ đã tải lên dự án Firebase, cộng với capability Push Notifications và Background Modes trong Xcode. Máy giả lập không nhận được push từ xa.

## Câu hỏi thường gặp

**Vì sao thông báo chạy trên Android mà không chạy trên iOS?**

Gần như luôn là cấu hình APNs: thiếu hoặc sai khoá trong Firebase console, hoặc thiếu capability trong Xcode. Mã Dart hiếm khi là thủ phạm.

**Vì sao background handler không chạy ở bản release?**

Thiếu `@pragma('vm:entry-point')`, hoặc handler không ở cấp cao nhất. Cả hai đều chạy được ở debug và hỏng ở release.

**Có chạy được việc nặng trong background handler không?**

Bạn có một khoảng thời gian ngắn và hệ điều hành mới là bên quyết định. Hãy làm mức tối thiểu — lưu payload lại, hẹn việc thật cho lần mở tới. Việc dài sẽ bị giết.

**Có nên dùng tin nhắn chỉ-data cho cập nhật ngầm không?**

Chỉ khi cập nhật đó thật sự không bắt buộc. Cả hai nền tảng đều bóp push ngầm rất mạnh, và không nền tảng nào bảo đảm giao được.

**Làm sao hết bị thông báo trùng?**

Thường do vừa để hệ điều hành hiển thị vừa tự đăng một thông báo cục bộ cho cùng một tin nhắn. Chỉ hiển thị thông báo cục bộ trong `onMessage`, nơi hệ điều hành không hiển thị gì.

---

*Bốn đường phân phối, yêu cầu `@pragma('vm:entry-point')`, ngữ nghĩa các loại tin nhắn và hành vi kênh Android mô tả ở đây đều nằm trong tài liệu Firebase và tài liệu nền tảng dẫn ở trên. Khuyến nghị gửi cả hai khối, cảnh báo coi payload là không đáng tin khi điều hướng, và danh sách bốn phép thử tay là nhận định riêng của tôi từ việc phát hành tính năng thông báo. API Flutter của FCM thay đổi giữa các phiên bản lớn — hãy đối chiếu changelog của gói với phiên bản bạn dùng.*
