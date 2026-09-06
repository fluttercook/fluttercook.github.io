---
title: "go_router và deep link: những phần mà bài quickstart bỏ qua"
description: "Khai báo route mới là nửa dễ. Redirect không lặp vô hạn, shell lồng nhau với stack điều hướng riêng, route có kiểu, và mấy tệp cấu hình nền tảng khiến một link https:// thật sự mở app — đó mới là nửa còn lại."
seoDescription: "Hướng dẫn go_router thực dụng: redirect canh đăng nhập, StatefulShellRoute cho bottom navigation, typed route với go_router_builder, và cấu hình App Links, Universal Links."
keywords:
  - go_router deep link
  - statefulshellroute ví dụ
  - go_router redirect kiểm tra đăng nhập
  - cấu hình app links universal links flutter
  - go_router builder typed route
  - deep link không mở được app flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-05"
emoji: "🔗"
tags: ["Flutter", "Navigation", "go_router", "Deep Links", "Routing"]
sources:
  - name: "go_router — pub.dev"
    url: "https://pub.dev/packages/go_router"
  - name: "Flutter — Deep linking"
    url: "https://docs.flutter.dev/ui/navigation/deep-linking"
  - name: "Flutter cookbook — Set up app links for Android"
    url: "https://docs.flutter.dev/cookbook/navigation/set-up-app-links"
  - name: "Flutter cookbook — Set up universal links for iOS"
    url: "https://docs.flutter.dev/cookbook/navigation/set-up-universal-links"
  - name: "Router — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Router-class.html"
  - name: "go_router_builder — pub.dev"
    url: "https://pub.dev/packages/go_router_builder"
related:
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
  - slug: "flutter-flavors-build-config"
    title: "Flavor trong Flutter: một codebase, ba ứng dụng, không copy-paste cấu hình"
draft: false
---

Mọi bài hướng dẫn điều hướng đều kết thúc ở cùng một chỗ: một `GoRouter` với ba route, một `context.go('/details/42')`, và ảnh chụp màn hình cho thấy nó chạy. Phần đó mất mười phút. Những phần ngốn hết phần còn lại của tuần thì chẳng ai demo — một redirect kiểm tra đăng nhập không đánh nhau với màn hình login, một bottom navigation bar mà mỗi tab giữ lịch sử riêng, và phần cấu hình nền tảng quyết định xem `https://yourapp.com/order/7` sẽ mở app của bạn hay mở Safari.

## Bảng route, và state thật sự nằm ở đâu

Bắt đầu bằng hình dạng có thể lớn lên được, tức một đối tượng router ở cấp cao nhất và **không** bị dựng lại:

```dart
final _rootKey = GlobalKey<NavigatorState>();
final _shellKey = GlobalKey<NavigatorState>();

final router = GoRouter(
  navigatorKey: _rootKey,
  initialLocation: '/feed',
  debugLogDiagnostics: true,
  routes: [ /* ... */ ],
  errorBuilder: (context, state) => NotFoundScreen(uri: state.uri),
);

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) =>
      MaterialApp.router(routerConfig: router);
}
```

Hai thứ trong đó chịu lực. `debugLogDiagnostics: true` in ra toàn bộ kết quả khớp cho mỗi lần điều hướng, biến câu hỏi "sao nó lại nhảy sang đó" từ phỏng đoán thành một dòng log — hãy bật vĩnh viễn trong bản debug. Và router sống bên ngoài `build`, vì tạo lại một `GoRouter` là vứt bỏ toàn bộ stack điều hướng; đặt nó trong hàm `build` chính là nguồn gốc của con bug "nút back của tôi ngừng hoạt động".

Tham số route có ba dạng và đều đọc từ `GoRouterState`:

```dart
GoRoute(
  path: '/order/:id',
  builder: (context, state) {
    final id = state.pathParameters['id']!;             // /order/42
    final tab = state.uri.queryParameters['tab'];       // ?tab=items
    final draft = state.extra as Draft?;                // chỉ trong bộ nhớ
    return OrderScreen(id: id, tab: tab, draft: draft);
  },
),
```

`extra` đáng được cảnh báo. Nó là một đối tượng Dart thuần truyền qua bộ nhớ — nó không sống sót qua một deep link, một lần tải lại trình duyệt, hay quá trình khôi phục tiến trình trên Android. Bất cứ thứ gì màn hình thật sự cần để render phải nằm trong path hoặc query string; `extra` chỉ dành cho những cú trao tay lạc quan mà bạn dựng lại được nếu thiếu.

## Redirect: phần hay lặp vô hạn

`redirect` chạy trước khi một route được dựng và có thể trả về một vị trí mới hoặc `null` nghĩa là "đi tiếp". Nó chạy ở cấp router tổng và ở từng route, và cả hai đều kích hoạt ở mọi lần điều hướng. Bộ canh đăng nhập kinh điển:

```dart
final router = GoRouter(
  refreshListenable: authState,       // một ChangeNotifier
  redirect: (context, state) {
    final loggedIn = authState.isLoggedIn;
    final loggingIn = state.matchedLocation == '/login';

    if (!loggedIn && !loggingIn) {
      return '/login?from=${Uri.encodeComponent(state.uri.toString())}';
    }
    if (loggedIn && loggingIn) {
      final from = state.uri.queryParameters['from'];
      return from ?? '/feed';
    }
    return null;
  },
  routes: [ /* ... */ ],
);
```

Ba chi tiết tạo ra khác biệt giữa chạy được và treo:

- **`refreshListenable`.** Không có nó, redirect chỉ được đánh giá lại khi ai đó điều hướng. Đưa cho nó một `ChangeNotifier` phát tín hiệu lúc đăng nhập và đăng xuất, router sẽ chạy lại redirect ngay khi trạng thái xác thực đổi — đó chính là thứ đá bạn ra khỏi màn hình được bảo vệ ngay lập tức khi logout.
- **Lối thoát `loggingIn`.** Redirect về `/login` trong khi đang ở `/login` là một vòng lặp vô hạn, và go_router sẽ ném lỗi vượt giới hạn redirect thay vì treo. Luôn miễn trừ chính điểm đến.
- **`matchedLocation` khác `uri`.** `matchedLocation` là đường dẫn đã khớp, không kèm query parameter. So sánh với `state.uri.toString()` sẽ vỡ ngay khi bạn thêm `?from=...`.

Với một phép kiểm tra bất đồng bộ — làm mới token, lấy feature flag — đừng `await` bên trong `redirect`. Hãy quy nó về một `Listenable` đồng bộ trước khi router hỏi tới. Một route splash đứng yên cho tới khi khởi tạo xong là hình dạng thường gặp, với redirect đẩy mọi thứ về `/splash` chừng nào `!authState.isInitialised`.

## Điều hướng lồng nhau mà vẫn giữ lịch sử từng tab

Yêu cầu thì quen thuộc: một bottom bar năm tab, mỗi tab giữ stack riêng, thanh bar đứng yên trong khi bạn push các màn hình chi tiết. `StatefulShellRoute.indexedStack` sinh ra đúng cho việc này.

```dart
StatefulShellRoute.indexedStack(
  builder: (context, state, navigationShell) =>
      ScaffoldWithNavBar(navigationShell: navigationShell),
  branches: [
    StatefulShellBranch(routes: [
      GoRoute(
        path: '/feed',
        builder: (c, s) => const FeedScreen(),
        routes: [
          GoRoute(path: 'post/:id', builder: (c, s) =>
              PostScreen(id: s.pathParameters['id']!)),
        ],
      ),
    ]),
    StatefulShellBranch(routes: [
      GoRoute(path: '/search', builder: (c, s) => const SearchScreen()),
    ]),
  ],
)
```

Shell trao cho bạn một `navigationShell` biết nhánh hiện tại và có thể chuyển nhánh:

```dart
class ScaffoldWithNavBar extends StatelessWidget {
  const ScaffoldWithNavBar({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) => Scaffold(
        body: navigationShell,
        bottomNavigationBar: NavigationBar(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: (i) => navigationShell.goBranch(
            i,
            // Chạm vào tab đang mở sẽ đưa nó về gốc.
            initialLocation: i == navigationShell.currentIndex,
          ),
          destinations: const [ /* ... */ ],
        ),
      );
}
```

Dòng `initialLocation: i == currentIndex` chính là hành vi quy ước của nền tảng mà người dùng sẽ báo lỗi nếu thiếu: chạm vào tab bạn đang đứng sẽ pop về gốc của tab đó.

Chú ý phần `routes:` lồng bên dưới `/feed` thay vì một `/post/:id` ngang hàng. Route con là thứ giữ màn hình chi tiết **bên trong** nhánh, nên bottom bar vẫn ở đó và nút back quay về feed. Một route cấp cao nhất cùng đường dẫn sẽ phủ kín màn hình — đôi khi đúng là thứ bạn muốn cho một trình xem media toàn màn hình, và đó cũng chính là lúc bạn truyền `parentNavigatorKey: _rootKey` để push lên trên shell.

## Typed route xóa sổ cả một nhóm lỗi

Đường dẫn dạng chuỗi là "kiểu chuỗi": đổi tên thì hỏng âm thầm, thiếu tham số thì crash lúc chạy. `go_router_builder` sinh phần nối dây từ các lớp có annotation:

```dart
@TypedGoRoute<OrderRoute>(path: '/order/:id')
class OrderRoute extends GoRouteData with _$OrderRoute {
  const OrderRoute({required this.id, this.tab});

  final String id;
  final String? tab;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      OrderScreen(id: id, tab: tab);
}

// Điều hướng giờ là một lời gọi constructor, kiểm tra lúc biên dịch:
const OrderRoute(id: '42', tab: 'items').go(context);
```

Đổi tên `id` là mọi chỗ gọi không biên dịch được. Quên `tab` là trình phân tích báo ngay. Cái giá là thêm một bước `build_runner` vào quy trình; lợi ích lộ ra ngay lần đầu bạn tái cấu trúc cây route trong một app có hai trăm lời gọi điều hướng.

## Làm cho một link thật sự mở được app

Đây mới là nơi phần lớn vấn đề "deep link không chạy" thật sự cư trú, và không phần nào trong đó là code Flutter.

**Android — App Links.** Thêm intent filter với `android:autoVerify="true"` cho activity chính trong `AndroidManifest.xml`, rồi host `https://yourdomain.com/.well-known/assetlinks.json` chứa tên gói và vân tay SHA-256 của **khóa ký thật sự được phát hành**. Khóa upload và khóa ký do Play quản lý là hai vân tay khác nhau, và dùng nhầm sinh ra triệu chứng phổ biến nhất: link mở app khi debug và mở trình duyệt khi lên production.

**iOS — Universal Links.** Bật capability Associated Domains với `applinks:yourdomain.com`, và host `https://yourdomain.com/.well-known/apple-app-site-association` — phục vụ với `application/json`, **không** có đuôi `.json`, qua HTTPS, không redirect. iOS có cache tệp này, nên khi thử nghiệm hãy xóa và cài lại app thay vì tin rằng chỉnh sửa của bạn đã có hiệu lực.

**Phía Flutter.** Các bản Flutter gần đây bật deep link mặc định trên cả hai nền tảng; ở bản cũ hơn bạn có thể vẫn cần `<meta-data android:name="flutter_deeplinking_enabled" android:value="true" />`. go_router sau đó nhận đường dẫn đến qua API `Router` tiêu chuẩn và đối chiếu với bảng route của bạn — không cần plugin nào cho link `https://`.

Hãy kiểm chứng bằng công cụ nền tảng thay vì bấm link trong một app chat, vì chúng thường mở bằng trình duyệt nội bộ của riêng chúng:

```bash
adb shell am start -a android.intent.action.VIEW -d "https://yourdomain.com/order/42"
```

```bash
xcrun simctl openurl booted "https://yourdomain.com/order/42"
```

Nếu app mở nhưng vào sai màn hình, vấn đề nằm ở bảng route. Nếu trình duyệt mở thay vì app, vấn đề nằm ở tệp liên kết hoặc vân tay khóa — Flutter chưa từng tham gia.

## Những thứ sẽ cắn bạn về sau

- **URL trên web mặc định có dấu `#`.** Gọi `usePathUrlStrategy()` trước `runApp` để có đường dẫn sạch, và cấu hình máy chủ trả `index.html` cho những đường dẫn lạ, nếu không thì tải lại `/order/42` sẽ nhận 404 từ server.
- **`go` khác `push`.** `go` thay thế stack theo cây route; `push` chồng thêm lên trên. Dùng `push` để chuyển tab sẽ dựng lên một stack không giới hạn, và người dùng nút back sẽ nhận ra.
- **Deep link cần đăng nhập.** Một deep link lúc khởi động nguội đến **trước** khi token của bạn được nạp. Đó đúng là lý do redirect phải dựa vào một cờ "đã khởi tạo" thay vì một đối tượng người dùng nullable.
- **`errorBuilder` là trang 404 của bạn.** Không có nó, một link gõ sai sẽ hiện trang lỗi của framework. Với `state.uri` bạn còn ghi log được người ta đang truy cập link nào.

## Câu hỏi thường gặp

**Tôi có cần package như `uni_links` hay `app_links` không?**

Không cần cho link `https://` và custom scheme mà framework đã chuyển tới `Router`. Một package đáng dùng khi bạn cần quan sát link thô bên ngoài router, hoặc xử lý những scheme mà phần tích hợp nền tảng không lo.

**Vì sao redirect của tôi chạy hai lần?**

Nó chạy cho vị trí ban đầu rồi chạy lại cho vị trí sau khi redirect — đúng như mong đợi. Nếu nó chạy rất nhiều lần thì bạn có một vòng lặp; go_router ném lỗi vượt giới hạn redirect thay vì lặp mãi, và `debugLogDiagnostics` cho thấy cả chuỗi.

**Dùng `Navigator.push` song song với go_router được không?**

Được, và nó đúng cho những thứ không có địa chỉ — một dialog, một bottom sheet, một trình xem ảnh mở từ cử chỉ. Bất cứ thứ gì người dùng có thể đánh dấu trang hoặc nhận qua link đều thuộc về bảng route.

**Làm sao giữ vị trí cuộn khi chuyển tab?**

`StatefulShellRoute.indexedStack` giữ widget của từng nhánh sống, nên vị trí cuộn được bảo toàn theo thiết kế. Nếu không được thì có thứ gì đó bên trong nhánh đang bị dựng lại từ đầu — thường là một router hoặc một controller tạo trong `build`.

**`state.matchedLocation` khác `state.fullPath` chỗ nào?**

`matchedLocation` là đường dẫn cụ thể đã khớp, với tham số đã điền. `fullPath` là mẫu, kiểu `/order/:id`. Dùng mẫu để gom nhóm số liệu, dùng đường dẫn cụ thể cho các bộ canh.

---

*Chi tiết API route lấy từ tài liệu go_router và các hướng dẫn deep link của Flutter đã dẫn ở trên; các bước cấu hình nền tảng theo đúng công thức cookbook chính thức. Việc mẫu nào đáng áp dụng — typed route, hình dạng splash-cho-tới-khi-khởi-tạo-xong, `initialLocation` khi chạm tab — là nhận định của tôi sau khi triển khai chúng. API của go_router đã đổi qua các phiên bản lớn; hãy đọc changelog cho đúng phiên bản trong `pubspec.yaml` của bạn.*
