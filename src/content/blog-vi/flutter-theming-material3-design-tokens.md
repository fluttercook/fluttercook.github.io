---
title: "Theming Material 3 trong Flutter: vai trò màu, không phải giá trị màu"
description: "ColorScheme.fromSeed cho bạn cả bảng màu trong một dòng, rồi mọi người lập tức ghi đè lại bằng mã hex cứng. Đây là ý nghĩa của từng vai trò, khi nào seed là công cụ sai, và cách ThemeExtension mang những token mà Material không có."
seoDescription: "Cách theming Material 3 hoạt động trong Flutter: vai trò ColorScheme, fromSeed và bảng màu tường minh, dark mode, ThemeExtension cho design token riêng, và component theme."
keywords:
  - theming material 3 flutter
  - colorscheme fromseed flutter
  - flutter themeextension token riêng
  - flutter dark mode colorscheme
  - flutter component theme cardtheme
  - vai trò màu material 3
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-04"
emoji: "🎨"
tags: ["Flutter", "Material 3", "Theming", "Design System", "UI"]
sources:
  - name: "Flutter — Material Design 3"
    url: "https://docs.flutter.dev/ui/design/material"
  - name: "ThemeData — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/material/ThemeData-class.html"
  - name: "ColorScheme.fromSeed — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/material/ColorScheme/ColorScheme.fromSeed.html"
  - name: "Material 3 — Color roles"
    url: "https://m3.material.io/styles/color/roles"
  - name: "ThemeExtension — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/material/ThemeExtension-class.html"
  - name: "TextTheme — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/material/TextTheme-class.html"
related:
  - slug: "flutter-accessibility-semantics"
    title: "Trợ năng trong Flutter: cây semantics thật sự báo cáo những gì"
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
draft: false
---

Việc chuyển sang Material 3 trong Flutter tạo ra một mô-típ rất dễ đoán. Đội ngũ gọi `ColorScheme.fromSeed(seedColor: brandPurple)`, nhìn kết quả, kết luận "đây không phải màu thương hiệu của mình", rồi quay lại truyền màu tường minh cho từng widget. Sáu tháng sau, ứng dụng có hai trăm giá trị hex cứng, dark mode là một danh sách hai trăm giá trị khác, và đổi màu thương hiệu tốn cả tuần.

Thứ bị bỏ qua chính là ý tưởng mà Material 3 được xây dựng trên đó: bạn không tô widget bằng màu, bạn gán cho nó một **vai trò**. Một `FilledButton` không có nền màu tím — nó có nền `primary` với nội dung `onPrimary`. Khi điều đó đúng trên toàn ứng dụng, bảng màu trở thành một object duy nhất mà bạn có thể thay.

## Các vai trò và mục đích của từng cái

`ColorScheme` có khoảng ba mươi thành viên. Đó không phải ba mươi lựa chọn độc lập; đó là các cặp và các họ.

| Vai trò | Dùng cho | Cặp "on" của nó |
| --- | --- | --- |
| `primary` | Hành động chính, nút filled, trạng thái active | `onPrimary` |
| `primaryContainer` | Bản nhấn nhẹ hơn của cùng ý tưởng | `onPrimaryContainer` |
| `secondary` / `tertiary` | Màu nhấn cần khác primary | `onSecondary` / `onTertiary` |
| `surface` | Mọi nền: trang, card, sheet | `onSurface` |
| `surfaceContainerLowest` … `Highest` | Độ nổi thể hiện bằng tông, không phải bóng đổ | `onSurface` |
| `error` | Trạng thái phá huỷ và không hợp lệ | `onError` |
| `outline` / `outlineVariant` | Viền và đường phân cách | — |

Tiền tố `on` chính là toàn bộ hợp đồng: **`onX` được bảo đảm đọc được trên nền `X`**. Nếu bạn tô container bằng `colorScheme.primaryContainer` và chữ bằng `colorScheme.onPrimaryContainer`, độ tương phản đã được lo — ở light mode, ở dark mode, và sau khi ai đó đổi seed.

Thứ thay đổi nhiều nhất ở Material 3 là surface. Mô hình cũ nâng độ nổi bằng bóng đổ; mô hình mới nâng bằng **tông màu**. Một dialog nằm trên trang là một surface sáng hơn (ở light mode) hoặc xám nhạt hơn (ở dark mode), không phải một cái bóng. Đó là lý do họ `surfaceContainer*` tồn tại, và là lý do `background` cùng `surfaceVariant` bị deprecated — hãy dùng `surface` và `surfaceContainerHighest`.

## Khi nào seed là đúng, khi nào không

`ColorScheme.fromSeed` chạy thuật toán màu của Material: lấy một màu, suy ra một bảng tông (tonal palette), rồi chọn các vai trò từ đó sao cho bảo đảm đạt yêu cầu tương phản. Nó thật sự tốt, và là mặc định đúng cho ứng dụng không có brand book chặt chẽ.

```dart
final lightScheme = ColorScheme.fromSeed(seedColor: const Color(0xFF6750A4));
final darkScheme = ColorScheme.fromSeed(
  seedColor: const Color(0xFF6750A4),
  brightness: Brightness.dark,
);
```

Có hai điều người ta hay hiểu sai ở đây. **Seed không phải là màu primary của bạn** — thuật toán suy ra `primary` từ tông màu của seed và hoàn toàn có thể trả về một màu khác thấy rõ, vì đúng cái seed đó có thể không đủ tương phản với `onPrimary`. Và **bạn cần hai lời gọi**, mỗi brightness một cái; bảng màu tối không phải bảng sáng bị đảo ngược.

Khi yêu cầu thương hiệu là chính xác tuyệt đối, đừng chống lại thuật toán. Hãy dựng bảng màu tường minh và để trình phân tích nhắc bạn thiếu gì:

```dart
const brandLight = ColorScheme(
  brightness: Brightness.light,
  primary: Color(0xFF0B5FFF),
  onPrimary: Color(0xFFFFFFFF),
  secondary: Color(0xFF00A37A),
  onSecondary: Color(0xFF00110B),
  error: Color(0xFFBA1A1A),
  onError: Color(0xFFFFFFFF),
  surface: Color(0xFFFDFCFF),
  onSurface: Color(0xFF1A1C1E),
  // ...
);
```

Một hướng trung gian hiệu quả trong thực tế: seed ra bảng màu, rồi `copyWith` chỉ hai hoặc ba vai trò mà thương hiệu thật sự ghim cứng. Bạn giữ được bảo đảm tương phản của thuật toán ở mọi chỗ còn lại.

Ngoài ra còn có `ColorScheme.fromImageProvider`, suy ra bảng màu từ một ảnh theo cách bất đồng bộ — hữu ích cho màn hình phát nhạc tự đổi theo ảnh bìa album, và là ý tưởng tệ cho toàn bộ ứng dụng, vì phải `await`.

## Nối vào `ThemeData` một lần duy nhất

```dart
ThemeData _theme(ColorScheme scheme) => ThemeData(
      colorScheme: scheme,
      useMaterial3: true,
      textTheme: _textTheme,
      cardTheme: CardThemeData(
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        color: scheme.surfaceContainerLow,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        filled: true,
        border: OutlineInputBorder(),
      ),
      extensions: const [AppTokens.light],
    );

MaterialApp(
  theme: _theme(lightScheme),
  darkTheme: _theme(darkScheme),
  themeMode: ThemeMode.system,
  home: const HomePage(),
);
```

Component theme là chỗ mà design system thôi làm một tài liệu và trở thành code. `filledButtonTheme` với chiều cao tối thiểu 48 pixel nghĩa là không ai phải nhớ quy tắc vùng chạm nữa. `cardTheme` với bo góc 16 pixel nghĩa là bán kính góc chỉ nằm ở một dòng, không phải hai trăm dòng.

Để ý `ThemeMode.system` — tôn trọng thiết lập của hệ điều hành là mặc định người dùng mong đợi, và vì đã có sẵn hai theme nên nó không tốn gì thêm.

## `ThemeExtension` cho những token Material không có

Mọi design system thật đều có các giá trị mà Material không có ô để chứa: màu success, gradient thương hiệu, thang khoảng cách, bảng màu cho biểu đồ. Câu trả lời sai là một file hằng số toàn cục, vì hằng số không thể thay đổi theo brightness. `ThemeExtension` mới là câu trả lời đúng:

```dart
@immutable
class AppTokens extends ThemeExtension<AppTokens> {
  const AppTokens({
    required this.success,
    required this.onSuccess,
    required this.spacingUnit,
  });

  final Color success;
  final Color onSuccess;
  final double spacingUnit;

  static const light = AppTokens(
    success: Color(0xFF116B3E),
    onSuccess: Color(0xFFFFFFFF),
    spacingUnit: 8,
  );

  static const dark = AppTokens(
    success: Color(0xFF7CDBA4),
    onSuccess: Color(0xFF00391E),
    spacingUnit: 8,
  );

  @override
  AppTokens copyWith({Color? success, Color? onSuccess, double? spacingUnit}) =>
      AppTokens(
        success: success ?? this.success,
        onSuccess: onSuccess ?? this.onSuccess,
        spacingUnit: spacingUnit ?? this.spacingUnit,
      );

  @override
  AppTokens lerp(AppTokens? other, double t) {
    if (other is! AppTokens) return this;
    return AppTokens(
      success: Color.lerp(success, other.success, t)!,
      onSuccess: Color.lerp(onSuccess, other.onSuccess, t)!,
      spacingUnit: lerpDouble(spacingUnit, other.spacingUnit, t)!,
    );
  }
}
```

Đọc nó chỉ là một dòng, và một extension khiến việc đó dễ chịu:

```dart
extension ThemeX on BuildContext {
  ColorScheme get colors => Theme.of(this).colorScheme;
  AppTokens get tokens => Theme.of(this).extension<AppTokens>()!;
}

// Container(color: context.tokens.success)
```

Cài đặt `lerp` không phải việc thừa — chính nó khiến các token riêng của bạn chuyển động mượt khi theme đổi, hệt như các thành phần dựng sẵn. Bỏ qua nó thì lúc chuyển sáng/tối, màu Material sẽ mờ chồng còn màu xanh thương hiệu của bạn thì nhảy phựt.

## Kiểu chữ, và thứ làm hỏng trợ năng

`TextTheme` của Material 3 có mười lăm style theo tên, thuộc năm họ — `display`, `headline`, `title`, `body`, `label`, mỗi họ có `Large`/`Medium`/`Small`. Định nghĩa một lần và tham chiếu theo vai trò:

```dart
Text('Tổng cộng', style: Theme.of(context).textTheme.titleMedium)
```

Quy tắc quan trọng hơn tất cả những cái trên: **đừng bao giờ đặt cỡ chữ bỏ qua thiết lập tỉ lệ chữ của người dùng**, và đừng tắt khả năng phóng chữ chỉ để layout vừa khung. Nếu một nhãn bị tràn ở mức phóng 200%, layout mới là cái sai, không phải thiết lập kia. Hãy dùng `Flexible`, dùng `FittedBox` ở nơi thật sự phù hợp, và kiểm thử ở hai đầu cực trị — thiết lập trợ năng trên cả hai nền tảng đi xa hơn nhiều so với mức mà đa số thiết kế được kiểm tra.

## Thứ tự migration để khỏi phải viết lại

Bật `useMaterial3` trên một ứng dụng đã trưởng thành sẽ đổi rất nhiều thứ cùng lúc. Trình tự giúp việc review vẫn khả thi:

1. **Bật `useMaterial3: true`** và chỉ sửa những gì hỏng về mặt hình ảnh. Hãy chờ đợi hình dáng nút, màu app bar và độ nổi thay đổi.
2. **Thay các thành viên deprecated**: `background` → `surface`, `onBackground` → `onSurface`, `surfaceVariant` → `surfaceContainerHighest`.
3. **Grep `Color(0x`** ở ngoài file theme. Mỗi kết quả hoặc là một vai trò lẽ ra bạn nên dùng, hoặc là một token thuộc về `ThemeExtension`.
4. **Đưa phần style theo từng widget vào component theme.** Một `styleFrom` lặp ở năm chỗ chính là một mục `filledButtonTheme`.
5. **Chỉ đến lúc đó** mới tinh chỉnh bảng màu. Làm bước này trước nghĩa là phải chỉnh lại sau mỗi bước sau.

## Câu hỏi thường gặp

**Tôi còn nên dùng `primarySwatch` không?**

Không. Nó thuộc mô hình Material 2 và bị đa số component Material 3 bỏ qua. Hãy dùng `ColorScheme.fromSeed`, hoặc một `ColorScheme` tường minh.

**Vì sao nút của tôi trông khác thiết kế sau khi `fromSeed`?**

Vì thuật toán chọn `primary` theo độ tương phản, không theo mức trung thành với seed. Nếu giá trị chính xác là quan trọng, hãy `copyWith(primary: ..., onPrimary: ...)` sau khi seed — và tự kiểm tra tương phản, vì bạn đã chủ động từ bỏ bảo đảm đó.

**Làm sao để một màn hình có theme khác?**

Bọc nó trong widget `Theme` với một `ThemeData` đã sửa. Mọi thứ bên dưới, kể cả dialog mở ra từ đó, sẽ nhận theme ghi đè — dialog thừa kế từ context đã mở nó.

**`ThemeExtension` có đáng cho ba màu không?**

Có, nếu ba màu đó khác nhau giữa sáng và tối. Đó chính là điểm phân biệt: hằng số thì không đổi được, extension thì đổi được, và tính an toàn kiểu nghĩa là thiếu token sẽ là lỗi biên dịch chứ không phải một sắc độ sai trên production.

**Cái gì thay thế `Theme.of(context).accentColor`?**

`colorScheme.secondary`, trong hầu hết trường hợp. Các trường màu của `ThemeData` từ thời Material 2 đã bị xoá hoặc deprecated; giờ `ColorScheme` là nguồn duy nhất.

---

*Ngữ nghĩa của các vai trò và danh sách deprecated lấy từ tài liệu Material của Flutter cùng hướng dẫn màu Material 3 đã dẫn ở trên. Thứ tự migration, cách dung hoà "seed rồi `copyWith`", và quan điểm rằng layout vỡ ở mức phóng chữ cao là lỗi layout — đó là đánh giá riêng của tôi. API widget Material thay đổi giữa các bản Flutter — hãy kiểm tra tài liệu API cho đúng SDK bạn phát hành.*
