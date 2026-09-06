---
title: "Tiêm phụ thuộc trong Flutter mà không cần nghi thức rườm rà"
description: "get_it, Provider, Riverpod và constructor thuần đều giải cùng một bài toán: khiến một lớp nói ra thứ nó cần thay vì tự đi lấy. Đây là thứ mỗi cách thật sự cho bạn, và quy tắc quyết định chọn cái nào."
seoDescription: "So sánh tiêm phụ thuộc trong Flutter: service locator get_it, InheritedWidget và Provider, Riverpod, tiêm qua constructor, lazy singleton, giải phóng theo phạm vi, và kiểm thử không dính trạng thái toàn cục."
keywords:
  - tiêm phụ thuộc flutter
  - get_it service locator flutter
  - provider và riverpod di flutter
  - tiêm qua constructor flutter
  - lazy singleton flutter
  - ghi đè phụ thuộc khi test flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-17"
emoji: "🧩"
tags: ["Flutter", "Architecture", "Testing", "Dart", "Patterns"]
sources:
  - name: "get_it — pub.dev"
    url: "https://pub.dev/packages/get_it"
  - name: "provider — pub.dev"
    url: "https://pub.dev/packages/provider"
  - name: "Tài liệu Riverpod"
    url: "https://riverpod.dev/"
  - name: "InheritedWidget — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/InheritedWidget-class.html"
  - name: "Kiểm thử ứng dụng Flutter — tài liệu Flutter"
    url: "https://docs.flutter.dev/testing/overview"
  - name: "injectable — pub.dev"
    url: "https://pub.dev/packages/injectable"
related:
  - slug: "flutter-state-management-decision-guide"
    title: "Chọn cách quản lý trạng thái Flutter mà không cần thánh chiến"
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
draft: false
---

Tiêm phụ thuộc có một cái tên đáng sợ cho một ý tưởng hết sức bình thường: một lớp nên được trao thứ nó cần thay vì tự dựng hoặc tự đi tìm. Toàn bộ khái niệm chỉ có vậy. Mọi thứ còn lại — container, locator, provider, mã sinh tự động — chỉ là bộ máy để giao hàng.

Lý do đáng quan tâm là kiểm thử. Viết `ApiClient()` bên trong một repository nghĩa là mọi test của repository đó đều gọi mạng thật. Truyền `ApiClient` vào nghĩa là mọi test đều truyền được bản giả. Đó là toàn bộ phần thưởng, và thế là đủ.

## Tiêm qua constructor, không cần gói nào

```dart
final class UserRepository {
  const UserRepository(this._api, this._cache);

  final ApiClient _api;
  final UserCache _cache;

  Future<User> fetch(String id) async {
    final cached = _cache.get(id);
    if (cached != null) return cached;

    final user = await _api.getUser(id);
    _cache.put(user);
    return user;
  }
}
```

Kiểm thử nó không cần framework nào:

```dart
test('trả về user từ cache mà không gọi mạng', () async {
  final api = FakeApi()..failIfCalled = true;
  final repo = UserRepository(api, UserCache()..put(knownUser));

  expect(await repo.fetch(knownUser.id), knownUser);
});
```

Mọi gói DI tồn tại để trả lời một câu hỏi mà đoạn trên không trả lời: **ai dựng đồ thị đối tượng, và đỉnh của nó nằm ở đâu?** Với ứng dụng nhỏ, câu trả lời có thể đúng nghĩa đen là `main()`. Nó hết mở rộng được khi widget nằm sâu ba tầng cần tới repository và bạn phải luồn nó qua các constructor vốn chẳng quan tâm gì.

## get_it: một service locator

```dart
final getIt = GetIt.instance;

void configureDependencies() {
  getIt
    ..registerLazySingleton<ApiClient>(() => ApiClient(baseUrl: Config.apiBase))
    ..registerLazySingleton<UserCache>(UserCache.new)
    ..registerLazySingleton<UserRepository>(
      () => UserRepository(getIt(), getIt()),
    )
    ..registerFactory<SearchController>(() => SearchController(getIt()));
}
```

Các kiểu đăng ký rất quan trọng và dễ nhầm:

| Kiểu đăng ký | Được tạo khi nào | Sống bao lâu |
| --- | --- | --- |
| `registerSingleton` | Ngay lúc đăng ký | Mãi mãi |
| `registerLazySingleton` | Ở lần `get` đầu tiên | Mãi mãi |
| `registerFactory` | Ở mỗi lần `get` | Tới khi bạn buông tham chiếu |
| `registerSingletonAsync` | Ngay lập tức, chờ được qua `allReady()` | Mãi mãi |

`registerLazySingleton` nên là mặc định của bạn. Singleton háo hức chạy constructor ngay lúc khởi động, và một client cơ sở dữ liệu hay analytics được dựng ở `main()` sẽ đo được trực tiếp trong thời gian khởi động nguội.

Đăng ký bất đồng bộ là câu trả lời cho "repository của tôi cần `SharedPreferences`, mà thứ đó là một `Future`":

```dart
getIt.registerSingletonAsync<SharedPreferences>(SharedPreferences.getInstance);
getIt.registerSingletonWithDependencies<SettingsStore>(
  () => SettingsStore(getIt<SharedPreferences>()),
  dependsOn: [SharedPreferences],
);

await getIt.allReady();
```

Cách này tốt hơn nhiều so với phương án phổ biến là biến mọi thứ phía dưới thành bất đồng bộ, hoặc dùng một biến `late` toàn cục khởi tạo trong `main()` rồi ném lỗi khó hiểu khi có ai đó đọc sớm.

**Nhược điểm thành thật**: `getIt<Thing>()` gọi từ bên trong một lớp sẽ giấu đi một phụ thuộc. Constructor của lớp không còn nói cho bạn biết nó cần gì, và một test buộc phải cấu hình container toàn cục. Kỷ luật giữ cho việc này trong tầm kiểm soát là **chỉ gọi `getIt` ở các điểm ghép nối** — trong `main()`, trong một route builder, trong `initState` của widget — rồi truyền kết quả xuống dưới như tham số constructor. Dùng vậy thì nó là locator ở rìa và là tiêm qua constructor ở mọi nơi khác.

## Provider và Riverpod: gắn phạm vi vào cây

`Provider` đặt phụ thuộc vào cây widget, thứ cho bạn một điều mà get_it về mặt cấu trúc không có: **phạm vi**.

```dart
MultiProvider(
  providers: [
    Provider<ApiClient>(create: (_) => ApiClient(), dispose: (_, c) => c.close()),
    ProxyProvider<ApiClient, UserRepository>(
      update: (_, api, __) => UserRepository(api, UserCache()),
    ),
  ],
  child: const MyApp(),
)
```

Một provider đặt trên một cây con sẽ được giải phóng khi cây con đó rời khỏi cây. Với bất cứ thứ gì có vòng đời gắn với một màn hình — một WebSocket cho phòng chat, một phiên chỉnh sửa, một cache theo phạm vi — cách này là chính xác, còn làm điều tương tự bằng locator toàn cục nghĩa là đăng ký và huỷ đăng ký thủ công, thứ mà sớm muộn sẽ có người làm sai.

Phiên bản của Riverpod bỏ luôn yêu cầu `BuildContext`, và đó là lợi thế thực dụng chính của nó:

```dart
final apiClientProvider = Provider<ApiClient>((ref) {
  final client = ApiClient();
  ref.onDispose(client.close);
  return client;
});

final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepository(ref.watch(apiClientProvider), UserCache());
});
```

Và việc ghi đè để kiểm thử là công dân hạng nhất chứ không phải một phép sửa đổi toàn cục:

```dart
ProviderScope(
  overrides: [apiClientProvider.overrideWithValue(FakeApi())],
  child: const MyApp(),
)
```

## Quy tắc tôi dùng

| Tình huống | Cách làm |
| --- | --- |
| Dịch vụ sống suốt vòng đời app (http client, cơ sở dữ liệu, logger) | Lazy singleton của `get_it`, hoặc một provider Riverpod |
| Bất cứ thứ gì gắn phạm vi với một màn hình hay một luồng | Gắn theo cây: Provider hoặc Riverpod với `autoDispose` |
| Bất cứ thứ gì một lớp cần để làm việc của nó | Tham số constructor, luôn luôn |
| Widget sâu ba tầng cần một dịch vụ | Định vị ở màn hình, rồi truyền xuống |

Sợi chỉ xuyên suốt: **định vị ở rìa, tiêm ở giữa.** Lớp nghiệp vụ phải dựng được bằng `new` mà không cần framework nào có mặt. Nếu một repository không thể khởi tạo trong một test Dart thuần mà không phải khởi tạo container, thì phụ thuộc đang nằm sai chỗ.

## Kiểm thử

Chọn cách nào thì test cũng cần đặt lại giữa các ca, nếu không trạng thái sẽ rò rỉ qua nhau:

```dart
setUp(() async {
  await getIt.reset();
  getIt.registerLazySingleton<ApiClient>(() => FakeApi());
});
```

Quên `reset()` sinh ra kiểu test hỏng tệ nhất: chạy riêng thì pass, chạy cả bộ thì fail, hoặc ngược lại, tuỳ thứ tự. Nếu bạn thấy mình đang gỡ lỗi kiểu đó, hãy kiểm tra vòng đời container trước mọi thứ khác.

## Có cần sinh mã tự động không?

`injectable` sinh mã đăng ký từ annotation. Nó xoá bỏ mã lặp và thêm vào một bước build, một file sinh phải giữ cho mới, và một thứ nữa phải giải thích cho người mới tham gia.

Với ứng dụng lớn có hàng chục dịch vụ, đánh đổi đó thường xứng đáng. Với ứng dụng bình thường có mười lăm dịch vụ, một hàm `configureDependencies()` viết tay là ba mươi dòng đọc được từ trên xuống, và đọc nó chính là cách người ta học kiến trúc. Tôi sẽ bắt đầu bằng viết tay và chỉ chuyển sang sinh mã khi file đó thật sự thành gánh nặng — mà với phần lớn ứng dụng thì điều đó không bao giờ xảy ra.

## Câu hỏi thường gặp

**Service locator có phải phản mẫu không?**

Dùng bên trong logic nghiệp vụ thì nó giấu phụ thuộc và làm rối test. Chỉ dùng ở điểm ghép nối thì đó là cách hợp lý để dựng đồ thị đối tượng. Bản thân mẫu không phải vấn đề; dùng vô tội vạ mới là.

**Nếu buộc phải chọn một, get_it hay Riverpod?**

Nếu bạn đã dùng Riverpod cho trạng thái thì dùng luôn cho phụ thuộc — một mô hình tư duy hơn hai. Nếu bạn dùng BLoC hay setState, get_it cộng tiêm qua constructor sẽ không cản đường bạn.

**Tiêm thứ cần `BuildContext` thế nào?**

Thường là bạn không nên. Hãy truyền giá trị dẫn xuất từ context (một màu của theme, một locale) thay vì chính context. Một dịch vụ giữ `BuildContext` sẽ sống lâu hơn nó và sập về sau.

**Đăng ký các bản cài đặt khác nhau theo flavor được không?**

Được — hãy rẽ nhánh trong `configureDependencies()` dựa trên cấu hình flavor. Đây là một trong những cái lợi rõ nhất của việc có một điểm ghép nối duy nhất.

**Còn phụ thuộc vòng thì sao?**

Đó là tín hiệu thiết kế, không phải vấn đề của container. Lazy singleton chỉ giúp bạn hoãn cú sập lại chứ không tránh được nó; tách phần dùng chung ra thành lớp thứ ba mới là bản sửa thật.

---

*Các kiểu đăng ký của `get_it`, API phạm vi và ghi đè của Provider cùng Riverpod, và các công cụ kiểm thử mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Quy tắc định-vị-ở-rìa, khuyến nghị mặc định dùng lazy singleton, bảng tình huống và quan điểm về sinh mã tự động là nhận định riêng của tôi từ việc duy trì ứng dụng với từng cách. API của các gói thay đổi giữa các phiên bản lớn — hãy xem changelog cho phiên bản bạn phụ thuộc.*
