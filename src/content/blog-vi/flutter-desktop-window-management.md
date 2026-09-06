---
title: "Flutter trên desktop: cửa sổ giờ là một phần của ứng dụng bạn"
description: "Trên di động, hệ điều hành sở hữu cửa sổ. Trên desktop, bạn sở hữu nó — kích thước, vị trí, giới hạn nhỏ nhất, nhiều cửa sổ, và cái nút đóng không được phép đóng. Đây là những gì thay đổi khi ứng dụng Flutter của bạn mọc ra thanh tiêu đề."
seoDescription: "Quản lý cửa sổ Flutter desktop: window_manager, kích thước tối thiểu, chặn đóng cửa sổ, biểu tượng khay hệ thống, phím tắt, menu, cân nhắc đa cửa sổ, và khác biệt bố cục cùng thao tác nhập trên desktop."
keywords:
  - quản lý cửa sổ flutter desktop
  - kích thước vị trí cửa sổ flutter
  - chặn đóng cửa sổ flutter
  - phím tắt flutter desktop
  - khay hệ thống flutter
  - thanh menu flutter desktop
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-18"
emoji: "🖥️"
tags: ["Flutter", "Desktop", "macOS", "Windows", "UI"]
sources:
  - name: "Hỗ trợ desktop cho Flutter — tài liệu Flutter"
    url: "https://docs.flutter.dev/platform-integration/desktop"
  - name: "window_manager — pub.dev"
    url: "https://pub.dev/packages/window_manager"
  - name: "Shortcuts và Actions — tài liệu Flutter"
    url: "https://docs.flutter.dev/ui/interactivity/actions-and-shortcuts"
  - name: "PlatformMenuBar — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/PlatformMenuBar-class.html"
  - name: "MenuAnchor — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/material/MenuAnchor-class.html"
  - name: "ScrollBehavior — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollBehavior-class.html"
related:
  - slug: "flutter-custom-scroll-physics"
    title: "Scroll physics tự viết: khiến danh sách dừng đúng chỗ bạn muốn"
  - slug: "flutter-accessibility-semantics"
    title: "Trợ năng trong Flutter: cây semantics thật sự báo cáo những gì"
draft: false
---

Một ứng dụng Flutter chạy được trên desktop và một ứng dụng Flutter *thuộc về* desktop là hai phần mềm khác nhau. Cái thứ nhất là bố cục điện thoại kéo giãn ra 1920 pixel. Cái thứ hai biết cửa sổ của mình có thể bị co lại tới mức phi lý, biết người dùng mong Cmd+W đóng một tab, biết chuột phải phải bật menu ngữ cảnh, và biết cuộn bằng trackpad không phải cùng một cử chỉ với kéo bằng ngón tay.

Chẳng có gì trong số này là khó. Nó chỉ là danh sách những thứ mà di động chưa bao giờ bắt bạn nghĩ tới.

## Cửa sổ có vòng đời do bạn điều khiển

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();

  const options = WindowOptions(
    size: Size(1200, 800),
    minimumSize: Size(720, 480),
    center: true,
    titleBarStyle: TitleBarStyle.normal,
  );

  await windowManager.waitUntilReadyToShow(options, () async {
    await windowManager.show();
    await windowManager.focus();
  });

  runApp(const MyApp());
}
```

`waitUntilReadyToShow` tồn tại để tránh cú loé của một cửa sổ chưa được tạo kiểu, sai kích thước, trước khi frame đầu tiên xuất hiện. Chỉ hiện cửa sổ sau khi đã cấu hình xong chính là khác biệt giữa một ứng dụng cho cảm giác native và một ứng dụng tự lắp ráp trước mắt người dùng lúc khởi chạy.

**`minimumSize` là dòng đáng giá nhất ở đây.** Không có nó, người dùng kéo cửa sổ xuống 200×100 và bố cục bạn dựng công phu sẽ ném lỗi tràn. Hãy chọn kích thước mà dưới đó ứng dụng thật sự không dùng được, rồi cưỡng chế ở tầng cửa sổ thay vì rải mã bố cục phòng thủ khắp nơi.

Khôi phục kích thước và vị trí lần trước là hành vi được mong đợi trên desktop:

```dart
Future<void> restoreWindowState() async {
  final prefs = await SharedPreferences.getInstance();
  final w = prefs.getDouble('win_w');
  final h = prefs.getDouble('win_h');
  if (w != null && h != null) {
    await windowManager.setSize(Size(w, h));
  }
  // Cố ý không khôi phục vị trí: vị trí đã lưu có thể đẩy cửa sổ ra
  // ngoài màn hình khi một màn hình bị ngắt kết nối.
}
```

Dòng chú thích đó mới là lời khuyên thật. Khôi phục vị trí mà không đối chiếu với cách bố trí màn hình hiện tại chính là cách một ứng dụng trở nên vô hình trên chiếc laptop trước đó từng cắm hai màn hình rời.

## Chặn thao tác đóng

Người dùng desktop mong được cảnh báo về công việc chưa lưu, và mong một số ứng dụng vẫn chạy tiếp khi cửa sổ đóng lại.

```dart
class _AppState extends State<App> with WindowListener {
  @override
  void initState() {
    super.initState();
    windowManager.addListener(this);
    windowManager.setPreventClose(true);
  }

  @override
  void dispose() {
    windowManager.removeListener(this);
    super.dispose();
  }

  @override
  Future<void> onWindowClose() async {
    if (!context.mounted) return;

    final hasUnsaved = context.read<DocumentModel>().isDirty;
    if (!hasUnsaved) {
      await windowManager.destroy();
      return;
    }

    final shouldClose = await showDialog<bool>(
      context: context,
      builder: (_) => const UnsavedChangesDialog(),
    );
    if (shouldClose ?? false) await windowManager.destroy();
  }
}
```

`setPreventClose(true)` cộng `destroy()` chính là mẫu: bạn nhận trách nhiệm đóng, nên mọi nhánh đáng lẽ đóng đều phải gọi `destroy()`. Quên một nhánh sẽ tạo ra ứng dụng không thoát được, và người dùng giải quyết bằng lệnh tắt cưỡng bức kèm một đánh giá xấu.

Với ứng dụng nằm ở thanh menu hay khay hệ thống, `onWindowClose` sẽ ẩn thay vì huỷ — và khi đó bạn phải cung cấp cách thoát rõ ràng từ menu khay, nếu không bạn vừa dựng lại đúng cái bẫy đó dưới hình dạng khác.

## Bàn phím là thiết bị nhập hạng nhất

Trên di động, phím tắt là thứ dễ thương. Trên desktop, thiếu nó là một khiếm khuyết.

```dart
Shortcuts(
  shortcuts: <ShortcutActivator, Intent>{
    SingleActivator(LogicalKeyboardKey.keyS, meta: true): const SaveIntent(),
    SingleActivator(LogicalKeyboardKey.keyS, control: true): const SaveIntent(),
    SingleActivator(LogicalKeyboardKey.keyF, meta: true): const FindIntent(),
  },
  child: Actions(
    actions: <Type, Action<Intent>>{
      SaveIntent: CallbackAction<SaveIntent>(onInvoke: (_) => _save()),
      FindIntent: CallbackAction<FindIntent>(onInvoke: (_) => _openFind()),
    },
    child: Focus(autofocus: true, child: child),
  ),
)
```

Đăng ký cả biến thể `meta` lẫn `control` phủ được macOS và Windows/Linux mà không cần kiểm tra nền tảng. Nó hơi dư một chút và đơn giản hơn đáng kể so với việc rẽ nhánh.

Hai điều dễ quên: **phải có thứ gì đó đang giữ focus** thì phím tắt mới nổ, nên mới có `Focus(autofocus: true)`; và thứ tự tab phải hợp lý, vì người dùng bàn phím điều hướng form của bạn bằng Tab, không phải bằng cách chạm. Hãy thử toàn bộ ứng dụng một lần chỉ bằng bàn phím — mất mười phút và tìm ra vấn đề thật.

Muốn có menu ứng dụng native trên macOS, `PlatformMenuBar` kết xuất vào đúng thanh menu hệ thống thay vì vẽ một bản nhái bên trong cửa sổ, và đó là thứ người dùng mong đợi.

## Khác biệt về thao tác nhập khiến người ta bất ngờ

| Hành vi | Di động | Desktop |
| --- | --- | --- |
| Cuộn | Kéo nội dung bằng ngón tay | Bánh xe hoặc trackpad; kéo nội dung không phải chuẩn mực |
| Menu khi nhấn giữ | Chuẩn mực | Thay vào đó người dùng mong chuột phải |
| Hover | Không tồn tại | Người dùng mong có phản hồi thị giác khi rê chuột |
| Chọn văn bản | Tay nắm và một thanh công cụ | Bấm-kéo, bấm đúp chọn từ, Cmd+A |
| Thanh cuộn | Lớp phủ thoáng qua | Được mong đợi nhìn thấy và kéo được |

Dòng đầu tiên gây ra một lỗi cụ thể: một `ListView` trên desktop không kéo chuột để cuộn được, trừ khi bạn mở rộng `ScrollBehavior` với `dragDevices` bao gồm `PointerDeviceKind.mouse`. Đó là hành vi mặc định đúng — ứng dụng desktop cuộn bằng bánh xe — nhưng nếu bạn có một carousel kéo-để-cuộn thì nó sẽ trông như bị hỏng.

Trạng thái hover cần được chú ý thật sự. `MouseRegion` và các trạng thái hover của `WidgetStateProperty` sinh ra cho việc này; một ứng dụng mà không gì phản ứng với con trỏ cho cảm giác chết cứng theo kiểu khó gọi tên nhưng dễ nhận ra.

## Nhiều cửa sổ

Câu chuyện desktop của Flutter trong lịch sử là một Flutter view cho mỗi cửa sổ, còn hỗ trợ đa cửa sổ thì đang tiến hoá. Trước khi thiết kế xoay quanh nhiều cửa sổ, hãy kiểm tra phiên bản Flutter bạn nhắm tới thật sự hỗ trợ gì thay vì mặc định, vì câu trả lời vẫn đang thay đổi và các gói lấp chỗ trống thì độ chín rất khác nhau.

Một phương án thực dụng chạy được ngay hôm nay: bố cục tab hoặc chia đôi ngay trong ứng dụng, cho người dùng khả năng tương đương mà không gánh độ phức tạp của nền tảng. Không bằng cửa sổ thật với một trình soạn thảo tài liệu — nhưng hoàn toàn đủ dùng với phần lớn ứng dụng.

## Đối mặt với thực tế phân phối

Build ra binary là phần dễ. Phát hành nó nghĩa là ký mã trên macOS cộng công chứng, một trình cài đặt và lý tưởng là một chứng chỉ ký trên Windows, và phải chọn giữa vài định dạng trên Linux. Sandbox trên macOS cũng hạn chế truy cập tệp theo cách mà bản build phát triển của bạn không gặp, nên hãy kiểm thử bộ chọn tệp và mọi đường dẫn bạn ghi vào ở bản đã sandbox, không chỉ dưới `flutter run`.

## Câu hỏi thường gặp

**Nên làm một ứng dụng cho cả di động và desktop hay hai ứng dụng?**

Một codebase, với bố cục thích ứng theo điểm ngắt và widget riêng ở chỗ thao tác thật sự khác nhau. Chia sẻ model và tầng dữ liệu mới là cái lợi; chia sẻ một cấu trúc điều hướng giữa điện thoại và màn hình 27 inch thì thường không.

**Vì sao ứng dụng mở sai kích thước ở lần chạy thứ hai?**

Trạng thái khôi phục từ phiên trước, hoặc hệ điều hành nhớ lại. Hãy đặt kích thước tường minh trong `WindowOptions` và chỉ khôi phục thứ bạn đã kiểm chứng.

**Hiện biểu tượng khay hệ thống thế nào?**

Gói `tray_manager` đi cặp với `window_manager`. Luôn kèm mục Thoát — một ứng dụng khay không có lối thoát nhìn thấy được là gánh nặng hỗ trợ.

**`MediaQuery` có chạy trên desktop không?**

Có, và nó báo kích thước cửa sổ, thứ thay đổi khi người dùng kéo co. Bố cục đọc nó theo thời gian thực chính là thứ bạn muốn; bố cục đọc một lần rồi cache thì không.

**`Platform.isMacOS` có phải cách rẽ nhánh đúng không?**

Với quy ước nền tảng thì đúng. Với khả năng hỗ trợ thì nên kiểm tra tính năng. Và nhớ rằng `Platform` ném lỗi trên web — hãy chắn bằng `kIsWeb` trước nếu mã được dùng chung.

---

*API `window_manager`, `Shortcuts`/`Actions`, `PlatformMenuBar` và mức hỗ trợ nền tảng desktop mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Lời khuyên không khôi phục vị trí cửa sổ, cách đăng ký phím tắt với cả hai phím bổ trợ, bảng khác biệt thao tác nhập và thái độ thực dụng với đa cửa sổ là nhận định riêng của tôi từ việc phát hành bản desktop. Hỗ trợ desktop của Flutter và khả năng đa cửa sổ đang tiến hoá liên tục — hãy đối chiếu với phiên bản Flutter của bạn trước khi thiết kế xoay quanh chúng.*
