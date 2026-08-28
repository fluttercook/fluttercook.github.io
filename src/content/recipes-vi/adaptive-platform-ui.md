---
title: "adaptive_platform_ui: một cây widget, iOS 26 native và Material"
package: "adaptive_platform_ui"
repo: "berkaycatak/adaptive_platform_ui"
githubUrl: "https://github.com/berkaycatak/adaptive_platform_ui"
category: "UI/Components"
stars: 235
forks: 85
lastUpdate: "2026-07-25"
pubDev: "https://pub.dev/packages/adaptive_platform_ui"
youtube: "https://www.youtube.com/results?search_query=flutter+adaptive_platform_ui+liquid+glass"
priority: "High"
phase: "P1"
trendRank: 0
description: "adaptive_platform_ui hiển thị toolbar và tab bar UIKit thật của iOS 26 kèm Liquid Glass trên iPhone mới, Cupertino trên máy cũ và Material 3 trên Android — chỉ từ một cây widget."
seoDescription: "adaptive_platform_ui là plugin Flutter với các widget thích ứng theo cả phiên bản hệ điều hành: UIToolbar và UITabBar native của iOS 26 kèm Liquid Glass, lùi về Cupertino cho iOS 18 trở xuống, Material 3 trên Android."
keywords:
  - adaptive_platform_ui
  - flutter liquid glass
  - ios 26 flutter
  - widget thích ứng flutter
  - cupertino material một codebase
  - flutter uitoolbar uitabbar
topics:
  - ui
  - ios
  - liquid-glass
summary:
  - "**adaptive_platform_ui** chọn đúng widget theo từng nền tảng *và từng phiên bản hệ điều hành* — không còn nhánh `Platform.isIOS` trong code của bạn."
  - "Trên iOS 26+ nó nhúng `UIToolbar` và `UITabBar` UIKit thật, nên bạn có Liquid Glass và cử chỉ native chứ không phải bản dựng lại."
  - "Lùi về Cupertino trên iOS 18 trở xuống, và Material 3 trên Android cùng web."
  - "**235★**, giấy phép MIT, phiên bản 0.1.111 trên pub.dev, Dart SDK `^3.9.2`."
related:
  - slug: liquid-glass-widgets
    title: "liquid_glass_widgets: hướng dẫn hoạt ảnh trong Flutter"
  - slug: forui
    title: "forui: hướng dẫn giao diện & thành phần UI trong Flutter"
  - slug: adaptive-theme
    title: "adaptive_theme: hướng dẫn giao diện & thành phần UI trong Flutter"
faq:
  - q: adaptive_platform_ui có thật sự dùng control native của iOS không?
    a: "Với toolbar và tab bar của iOS 26 thì có — đây là plugin Flutter nhúng `UIToolbar` và `UITabBar` của UIKit, nhờ vậy bạn có hiệu ứng mờ Liquid Glass thật, hành vi thu gọn khi cuộn và cách xử lý cử chỉ native chứ không phải một bản mô phỏng."
  - q: Trên iOS 18 hoặc cũ hơn thì sao?
    a: "Nó hiển thị widget Cupertino truyền thống. Việc chọn theo phiên bản diễn ra tự động — bạn đặt `useNativeToolbar: true` và gói tự quyết định lúc chạy xem thiết bị có đáp ứng được không."
  - q: Có còn phải cấu hình đa ngôn ngữ không?
    a: "Có, và nhiều người vấp chỗ này. Hãy thêm các delegate `GlobalMaterialLocalizations`, `GlobalCupertinoLocalizations` và `GlobalWidgetsLocalizations` vào `AdaptiveApp`, nếu không bộ chọn ngày giờ sẽ hiện tiếng Anh bất kể ngôn ngữ hệ thống."
  - q: Đã dùng được cho production chưa?
    a: "Hãy xem nó là hứa hẹn chứ chưa ổn định. Gói có giấy phép MIT và đang được phát triển tích cực, nhưng số phiên bản là 0.1.111 — API vẫn đang thay đổi, và việc nhúng platform view có cái giá thật về hiệu năng lẫn kiểm thử."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`adaptive_platform_ui`](https://github.com/berkaycatak/adaptive_platform_ui) cho bạn một cây widget duy nhất, hiển thị thành phần Liquid Glass native của iOS 26 trên iPhone mới, Cupertino trên máy cũ, và Material 3 trên Android. **235★**, giấy phép MIT, cập nhật lần cuối **2026-07-25**.

## adaptive_platform_ui là gì?

Flutter luôn cho phép bạn dựng giao diện Cupertino và giao diện Material, nhưng chưa bao giờ cho phép làm cả hai một cách dễ chịu trong cùng một app. Kết quả thường thấy là `Platform.isIOS ? CupertinoButton(...) : ElevatedButton(...)` rải khắp cây widget, cùng một lớp Cupertino luôn chậm hơn Apple một hai năm.

iOS 26 làm mọi thứ tệ hơn. Liquid Glass không phải một bảng màu bạn có thể phỏng theo bằng `BackdropFilter`; hiệu ứng mờ của toolbar, hành vi thu gọn khi cuộn và cách xử lý cử chỉ đều đến từ chính UIKit.

adaptive_platform_ui chọn lập trường rằng cách trung thực duy nhất để bắt kịp là nhúng control thật. Nó là một *plugin* Flutter chứ không phải thư viện widget thuần Dart, và trên iOS 26 thì `useNativeToolbar: true` đặt một `UIToolbar` thật lên màn hình — tương tự `UITabBar` cho thanh dưới, cùng với `UIButton`, `UISegmentedControl`, `UISwitch` và `UISlider`.

Ở nơi không làm được như vậy, nó hạ cấp dần: widget Cupertino trên iOS 18 trở xuống, Material 3 trên Android và web. Quyết định do gói đưa ra lúc chạy, không phải do bạn.

## Vì sao nên biết trong năm 2026

Giá trị nằm ở trục *phiên bản*, chứ không chỉ trục nền tảng. Phần lớn gói thích ứng chỉ rẽ nhánh theo `Platform.isIOS` rồi dừng lại, nghĩa là ngay khi Apple ra ngôn ngữ thiết kế mới thì giao diện "thích ứng" của bạn lại đang thích ứng với đúng phiên bản iOS sai.

API được tổ chức quanh một widget cấp ứng dụng và một nhóm nhỏ thành phần thích ứng:

```dart
AdaptiveScaffold(
  appBar: AdaptiveAppBar(
    title: 'My App',
    useNativeToolbar: true,
    actions: [
      AdaptiveAppBarAction(
        onPressed: () {},
        iosSymbol: 'gear',
        icon: Icons.settings,
      ),
    ],
  ),
  bottomNavigationBar: AdaptiveBottomNavigationBar(
    items: [
      AdaptiveNavigationDestination(icon: 'house.fill', label: 'Home'),
      AdaptiveNavigationDestination(icon: 'person.fill', label: 'Profile'),
    ],
    selectedIndex: 0,
    onTap: (index) {},
  ),
  body: YourContent(),
)
```

Để ý `iosSymbol: 'gear'` nằm cạnh `icon: Icons.settings` — bạn cung cấp cả hai, và cái phù hợp sẽ được dùng. `AdaptiveApp` nhận theme Material và Cupertino riêng biệt, hỗ trợ sáng/tối/theo hệ thống, và có hàm khởi tạo `AdaptiveApp.router()` cho go_router.

## Bắt đầu

```bash
flutter pub add adaptive_platform_ui
```

Gói cần Dart `^3.9.2`. Sau đó cấu hình các delegate đa ngôn ngữ — README nêu đây là lỗi phổ biến nhất:

```dart
import 'package:flutter_localizations/flutter_localizations.dart';

AdaptiveApp(
  localizationsDelegates: const [
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ],
  supportedLocales: const [Locale('en'), Locale('de'), Locale('tr')],
  // ...
)
```

Thiếu `GlobalCupertinoLocalizations` là mọi bộ chọn ngày và giờ sẽ hiện tiếng Anh bất kể ngôn ngữ thiết bị là gì.

## Khi nào nên dùng adaptive_platform_ui?

- ứng dụng của bạn cần cảm giác native thật sự trên iOS chứ không phải "Material bo góc"
- bạn muốn phần khung Liquid Glass của iOS 26 mà không phải tự viết code platform channel
- bạn đã mệt với việc duy trì song song hai cây widget Cupertino và Material
- bạn hỗ trợ dải phiên bản iOS rộng và muốn phần dự phòng được lo sẵn

## Điểm còn hạn chế

Nhúng view UIKit có cái giá mà một gói thuần Dart không có. Platform view được ghép ảnh theo cách khác, dễ gây khó chịu bên trong vùng cuộn và các hiệu ứng chuyển cảnh, và gần như vô hình với widget test của Flutter — bạn không thể kiểm tra một `UITabBar` từ `flutter_test`. Hãy dành thời gian kiểm chứng trên máy thật.

Phiên bản `0.1.111` không phải tín hiệu ổn định. Gói còn non, bề mặt API thì rộng, và 85 fork trên 235 sao cùng 44 issue đang mở cho thấy khá nhiều người đang tự vá ở phía họ.

Và đây là một gói nghiêng hẳn về iOS. Phía Android chỉ là Material 3 tiêu chuẩn — hoàn toàn ổn, nhưng không ai chọn thư viện này vì những gì nó làm trên Android.

## Các lựa chọn đáng so sánh

- [liquid_glass_widgets: hướng dẫn hoạt ảnh trong Flutter](/vi/recipes/liquid-glass-widgets/) — Liquid Glass vẽ bằng Dart, không dùng platform view
- [forui: hướng dẫn giao diện & thành phần UI trong Flutter](/vi/recipes/forui/) — một hệ thiết kế nhất quán thay vì native theo từng nền tảng
- [adaptive_theme: hướng dẫn giao diện & thành phần UI trong Flutter](/vi/recipes/adaptive-theme/) — chỉ đổi theme, nếu bạn chỉ cần vậy
- Bộ widget `Adaptive*` của chính Flutter — miễn phí, hẹp hơn nhiều, và không hỗ trợ iOS 26

## Câu hỏi thường gặp

### adaptive_platform_ui có thật sự dùng control native của iOS không?

Với toolbar và tab bar của iOS 26 thì có — đây là plugin Flutter nhúng `UIToolbar` và `UITabBar` của UIKit, nhờ vậy bạn có hiệu ứng mờ Liquid Glass thật, hành vi thu gọn khi cuộn và cách xử lý cử chỉ native chứ không phải một bản mô phỏng.

### Trên iOS 18 hoặc cũ hơn thì sao?

Nó hiển thị widget Cupertino truyền thống. Việc chọn theo phiên bản diễn ra tự động — bạn đặt `useNativeToolbar: true` và gói tự quyết định lúc chạy xem thiết bị có đáp ứng được không.

### Có còn phải cấu hình đa ngôn ngữ không?

Có, và nhiều người vấp chỗ này. Hãy thêm các delegate `GlobalMaterialLocalizations`, `GlobalCupertinoLocalizations` và `GlobalWidgetsLocalizations` vào `AdaptiveApp`, nếu không bộ chọn ngày giờ sẽ hiện tiếng Anh bất kể ngôn ngữ hệ thống.

### Đã dùng được cho production chưa?

Hãy xem nó là hứa hẹn chứ chưa ổn định. Gói có giấy phép MIT và đang được phát triển tích cực, nhưng số phiên bản là `0.1.111` — API vẫn đang thay đổi, và việc nhúng platform view có cái giá thật về hiệu năng lẫn kiểm thử.

## Tài nguyên & liên kết

- **GitHub:** [berkaycatak/adaptive_platform_ui](https://github.com/berkaycatak/adaptive_platform_ui)
- **pub.dev:** [adaptive_platform_ui](https://pub.dev/packages/adaptive_platform_ui)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
