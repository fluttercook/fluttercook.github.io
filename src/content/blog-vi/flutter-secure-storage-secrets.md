---
title: "Bí mật trong ứng dụng Flutter: cái gì lưu được, cái gì thì không"
description: "Mọi chuỗi được biên dịch vào ứng dụng đều đọc được bởi bất kỳ ai tải nó về. Chỉ một sự thật đó quyết định bí mật nào thuộc về thiết bị, bí mật nào thuộc về máy chủ, và flutter_secure_storage thật sự dùng để làm gì."
seoDescription: "Xử lý bí mật trong Flutter: vì sao dart-define không bí mật, Keychain và Keystore qua flutter_secure_storage, mẫu làm mới token, ghim chứng chỉ, và một mô hình mối đe doạ đứng vững."
keywords:
  - flutter secure storage
  - bảo mật api key flutter
  - keychain keystore flutter
  - làm mới token flutter
  - ghim chứng chỉ flutter
  - dart-define không bí mật
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🔐"
tags: ["Flutter", "Security", "Storage", "Authentication", "Mobile"]
sources:
  - name: "flutter_secure_storage — pub.dev"
    url: "https://pub.dev/packages/flutter_secure_storage"
  - name: "Keychain Services — tài liệu Apple"
    url: "https://developer.apple.com/documentation/security/keychain_services"
  - name: "Hệ thống Android Keystore — tài liệu Android"
    url: "https://developer.android.com/privacy-and-security/keystore"
  - name: "OAuth 2.0 cho ứng dụng native (RFC 8252)"
    url: "https://datatracker.ietf.org/doc/html/rfc8252"
  - name: "SecurityContext — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-io/SecurityContext-class.html"
  - name: "Thực hành bảo mật ứng dụng — tài liệu Android"
    url: "https://developer.android.com/privacy-and-security/security-tips"
related:
  - slug: "flutter-flavors-build-config"
    title: "Flavor trong Flutter: một codebase, ba ứng dụng, không copy-paste cấu hình"
  - slug: "flutter-error-handling-crash-reporting"
    title: "Xử lý lỗi trong Flutter: bắt được thứ thật sự tới tay người dùng"
draft: false
---

Hãy bắt đầu từ phần khó chịu, vì mọi thứ còn lại đều suy ra từ đó.

**Bất kỳ chuỗi nào được biên dịch vào ứng dụng đều là công khai.** Không phải "khó tìm" — mà là công khai. Một file APK là file zip; chạy `strings` trên binary đã giải nén chỉ mất vài giây. Giá trị `--dart-define`, hằng số, tên đã làm rối, khối base64: tất cả đều lấy lại được bởi bất kỳ ai đủ quyết tâm tải ứng dụng của bạn về một lần.

Đây không phải điểm yếu của Flutter. Điều đó đúng với mọi ứng dụng phía client trên mọi nền tảng. Thứ nó thay đổi là chỗ bạn kẻ ranh giới giữa "ứng dụng biết điều này" và "ứng dụng có thể hỏi xin điều này".

## Ranh giới

| Loại bí mật | Thuộc về đâu |
| --- | --- |
| Khoá API bên thứ ba gắn với hoá đơn | Chỉ ở máy chủ. Ứng dụng gọi backend của bạn, backend gọi họ |
| Khoá công khai (Stripe publishable, cấu hình Firebase, khoá Maps) | Nằm trong ứng dụng — chúng được thiết kế cho việc đó và được giới hạn phía máy chủ |
| Token phiên của người dùng | Kho an toàn trên thiết bị, vòng đời ngắn, làm mới được |
| Refresh token | Kho an toàn trên thiết bị, thu hồi được từ máy chủ |
| Khoá mã hoá dữ liệu cục bộ | Sinh hoặc dẫn xuất trên thiết bị, lưu trong Keychain/Keystore |
| Khoá ký, service account | Không bao giờ trong kho mã, không bao giờ trong ứng dụng |

Dòng Firebase làm nhiều người bất ngờ. `google-services.json` không phải bí mật — nội dung của nó nhìn thấy được trong mọi ứng dụng có kèm nó, và mô hình bảo mật của Firebase dựng trên Security Rules phía máy chủ chứ không phải trên việc giấu file cấu hình. Nếu Firestore của bạn chỉ được bảo vệ nhờ file cấu hình "bị giấu", thì nó không được bảo vệ.

Phép thử chung: nếu rò rỉ giá trị đó cho phép kẻ tấn công làm gì đó *với danh nghĩa của bạn* thay vì *danh nghĩa của họ*, thì nó không được nằm trên thiết bị.

## Dùng kho an toàn của nền tảng

`flutter_secure_storage` bọc Keychain của iOS và `EncryptedSharedPreferences` của Android sau một API duy nhất:

```dart
final class TokenStore {
  TokenStore(this._storage);

  final FlutterSecureStorage _storage;

  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  Future<void> save({
    required String access,
    required String refresh,
  }) async {
    await Future.wait([
      _storage.write(key: _accessKey, value: access),
      _storage.write(key: _refreshKey, value: refresh),
    ]);
  }

  Future<String?> readAccess() => _storage.read(key: _accessKey);
  Future<String?> readRefresh() => _storage.read(key: _refreshKey);

  Future<void> clear() => _storage.deleteAll();
}
```

Hãy cấu hình tuỳ chọn nền tảng một cách tường minh thay vì chấp nhận mặc định:

```dart
final storage = FlutterSecureStorage(
  aOptions: const AndroidOptions(encryptedSharedPreferences: true),
  iOptions: const IOSOptions(
    accessibility: KeychainAccessibility.first_unlock_this_device,
  ),
);
```

Hai lựa chọn đáng hiểu rõ.

**`first_unlock_this_device`** nghĩa là giá trị đọc được sau lần mở khoá đầu tiên kể từ khi khởi động lại, và — nửa quan trọng hơn — *không* được đưa vào iCloud Keychain hay bản sao lưu thiết bị. Một token đồng bộ sang máy thứ hai là token sống lâu hơn cái thiết bị mà người dùng tưởng họ đã thu hồi.

**`encryptedSharedPreferences: true`** trên Android dùng phần cài đặt tựa trên Keystore thay vì shared preferences thường. Không có nó, kho "an toàn" ở một số cấu hình kém an toàn hơn cái tên gợi ý khá nhiều.

## Sự bất đối xứng khi gỡ cài đặt

Một hành vi sinh ra những báo lỗi khó hiểu: trên Android, gỡ cài đặt sẽ xoá dữ liệu ứng dụng. Trên iOS, **mục Keychain có thể sống sót qua việc gỡ và cài lại**. Người dùng xoá ứng dụng để "đăng xuất và làm lại từ đầu" có thể cài lại và thấy mình vẫn đang đăng nhập, hoặc tệ hơn, đang giữ token của một tài khoản họ không còn sở hữu trên một máy đã bán lại.

Bản sửa là một dấu hiệu lần-chạy-đầu trong preferences thường, thứ *có* bị xoá:

```dart
Future<void> clearSecureStorageOnFirstRun() async {
  final prefs = await SharedPreferences.getInstance();
  if (prefs.getBool('has_run_before') ?? false) return;

  await storage.deleteAll();
  await prefs.setBool('has_run_before', true);
}
```

Gọi nó trước khi đọc bất kỳ token nào. Nó tốn một lần đọc mỗi lần khởi chạy và loại bỏ cả một nhóm lỗi phiên "không thể xảy ra".

## Token: ngắn hạn, làm mới được, thu hồi được

Phần lưu trữ là nửa dễ. Thiết kế khiến việc lưu trữ chịu được rủi ro là vòng đời access token ngắn cộng với khả năng thu hồi từ máy chủ:

```dart
final class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._store, this._api);

  final TokenStore _store;
  final AuthApi _api;

  Future<void>? _refreshInFlight;

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode != 401) return handler.next(err);

    // Gộp các lần làm mới đồng thời thành một.
    _refreshInFlight ??= _doRefresh();
    try {
      await _refreshInFlight;
    } finally {
      _refreshInFlight = null;
    }

    final token = await _store.readAccess();
    if (token == null) return handler.next(err);

    final retried = await _api.retry(err.requestOptions, token);
    handler.resolve(retried);
  }

  Future<void> _doRefresh() async {
    final refresh = await _store.readRefresh();
    if (refresh == null) return;
    final tokens = await _api.refresh(refresh);
    await _store.save(access: tokens.access, refresh: tokens.refresh);
  }
}
```

Việc gộp bằng `_refreshInFlight` không phải tối ưu hoá. Không có nó, năm request song song cùng gặp 401 sẽ kích hoạt năm lần làm mới; nếu máy chủ xoay vòng refresh token sau mỗi lần dùng thì bốn lần thất bại và người dùng bị đăng xuất. Đây là một trong những lỗi xác thực phổ biến nhất trong ứng dụng di động thực tế.

Còn với chính việc đăng nhập, RFC 8252 nói rõ: dùng trình duyệt hệ thống kèm PKCE, không dùng webview nhúng. Webview nhúng đọc được thông tin đăng nhập của người dùng, và đó chính là lý do các nhà cung cấp danh tính ngày càng từ chối hiển thị trong đó.

## Ghim chứng chỉ mua được gì và không mua được gì

Ghim chứng chỉ chặn kẻ tấn công đã cài CA tin cậy lên thiết bị đọc lưu lượng của bạn. Nó không chặn kẻ kiểm soát được thiết bị — họ có thể vá bỏ chính phép kiểm tra đó.

```dart
final client = HttpClient(
  context: SecurityContext(withTrustedRoots: false)
    ..setTrustedCertificatesBytes(pemBytes),
);
```

Nếu ghim, hãy ghim vào chứng chỉ trung gian hoặc khoá công khai thay vì chứng chỉ lá, hãy kèm ít nhất một pin dự phòng, và có một công tắc tắt từ xa. Một ứng dụng đã ghim mà chứng chỉ bị xoay vòng bất ngờ sẽ ngừng hoạt động với mọi người dùng cùng lúc, và bản sửa cần qua vòng duyệt của store. Tôi đã thấy sự cố đó; nó tệ hơn mối đe doạ mà việc ghim nhắm tới.

## Câu hỏi thường gặp

**Làm rối mã (`--obfuscate --split-debug-info`) có bảo vệ khoá của tôi không?**

Nó đổi tên định danh. Chuỗi ký tự vẫn là chuỗi ký tự. Nó nâng chi phí dịch ngược lên chút ít và tự nó không bảo vệ được gì.

**`flutter_secure_storage` có đủ cho ứng dụng offline-first chứa dữ liệu nhạy cảm không?**

Hãy lưu *khoá mã hoá* ở đó, rồi mã hoá cơ sở dữ liệu bằng khoá ấy — ví dụ SQLCipher qua `sqflite_sqlcipher`. Nhét hàng megabyte bản ghi vào Keychain không phải mục đích của nó.

**Làm sao giữ khoá bên thứ ba ngoài ứng dụng mà vẫn gọi được dịch vụ?**

Đi vòng qua backend của bạn. Ứng dụng xác thực với bạn; bạn xác thực với họ. Cách này còn cho bạn giới hạn tần suất và khả năng xoay khoá mà không cần phát hành bản mới.

**Có phát hiện được thiết bị đã root hay jailbreak không?**

Một phần, và đó là cuộc chạy đua vũ trang. Hãy coi nó như một tín hiệu để chấm điểm rủi ro trên máy chủ, đừng bao giờ coi là cổng chặn phía client mà bạn dựa vào.

**Còn kho lưu có cổng sinh trắc học thì sao?**

`IOSOptions` và `AndroidOptions` hỗ trợ yêu cầu sự hiện diện của người dùng. Đó là cải thiện thật cho các hành động giá trị cao, và cũng là chi phí ma sát thật — hãy áp cho bước xác nhận thanh toán, không áp cho mọi lần mở ứng dụng.

---

*Hành vi của Keychain và Keystore, các tuỳ chọn của `flutter_secure_storage`, hướng dẫn của RFC 8252 về OAuth cho ứng dụng native và API `SecurityContext` mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Bảng phân loại nơi-bí-mật-thuộc-về, mẫu dọn dẹp lần chạy đầu, interceptor gộp lần làm mới và cảnh báo về sự cố do ghim chứng chỉ là nhận định riêng của tôi từ việc phát hành và gỡ lỗi những hệ thống này. Mặc định bảo mật thay đổi giữa các phiên bản gói và hệ điều hành — hãy đối chiếu tuỳ chọn với đúng phiên bản bạn đang phụ thuộc.*
