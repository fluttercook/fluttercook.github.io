---
title: "Đa ngôn ngữ trong Flutter với file ARB: số nhiều, giống, và những chỗ cắn người"
description: "Thêm ngôn ngữ thứ hai thì dễ. Thêm ngôn ngữ thứ năm, với số nhiều đúng trong tiếng Ba Lan và định dạng ngày đúng trong tiếng Việt, mới là lúc định dạng ARB và gói intl bắt đầu có ý nghĩa."
seoDescription: "Hướng dẫn thực dụng về đa ngôn ngữ Flutter: gen_l10n và file ARB, plural/select theo ICU, placeholder và định dạng ngày, phân giải locale, RTL, và kiểm thử widget đa ngôn ngữ."
keywords:
  - đa ngôn ngữ flutter arb
  - hướng dẫn gen_l10n flutter
  - flutter intl plural select
  - localeresolutioncallback flutter
  - định dạng ngày intl flutter
  - hỗ trợ rtl flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-02"
emoji: "🌍"
tags: ["Flutter", "Đa ngôn ngữ", "i18n", "intl", "ARB"]
sources:
  - name: "Flutter — Internationalizing Flutter apps"
    url: "https://docs.flutter.dev/ui/accessibility-and-internationalization/internationalization"
  - name: "Gói intl"
    url: "https://pub.dev/packages/intl"
  - name: "DateFormat — tài liệu API intl"
    url: "https://pub.dev/documentation/intl/latest/intl/DateFormat-class.html"
  - name: "Localizations — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Localizations-class.html"
  - name: "Directionality — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Directionality-class.html"
  - name: "ICU — Formatting messages"
    url: "https://unicode-org.github.io/icu/userguide/format_parse/messages/"
related:
  - slug: "flutter-forms-validation-at-scale"
    title: "Form trong Flutter vượt khỏi ví dụ mẫu: validate bất đồng bộ, focus và autofill"
  - slug: "flutter-theming-material3-design-tokens"
    title: "Theming Material 3 trong Flutter: vai trò màu, không phải giá trị màu"
draft: false
---

Commit đa ngôn ngữ đầu tiên trong đa số ứng dụng Flutter là một `Map<String, String>` đánh khoá theo mã ngôn ngữ, tra qua một biến toàn cục. Nó chạy được với hai ngôn ngữ và một trăm chuỗi. Nó vỡ ngay lần đầu ai đó cần "1 item" so với "2 items", và vỡ nặng ngay lần đầu một người dịch hỏi `home_screen_label_2` là để làm gì.

Câu trả lời chính thức của Flutter là file ARB được `gen_l10n` biên dịch thành một class Dart sinh tự động. Phần cài đặt rất ngắn. Thứ đáng hiểu là những phần mà bài quickstart không nhắc: plural theo ICU, kiểu của placeholder, cách phân giải locale, và chuyện gì xảy ra vào ngày có người thêm tiếng Ả Rập.

## Cài đặt, một lần

```yaml
# pubspec.yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: any

flutter:
  generate: true
```

```yaml
# l10n.yaml ở thư mục gốc dự án
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
nullable-getter: false
```

`nullable-getter: false` đáng để đặt một cách có chủ ý. Với nó, `AppLocalizations.of(context)` trả về object không nullable và bạn viết `AppLocalizations.of(context).greeting` thay vì `AppLocalizations.of(context)!.greeting`. Cái giá là một lỗi lúc chạy thay vì một giá trị null nếu bạn quên khai báo delegate — mà đó chính là kiểu hỏng bạn muốn, vì nó xảy ra ngay và rất rõ ràng.

```dart
MaterialApp(
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
  home: const HomePage(),
);
```

Chuỗi sau đó lấy từ `AppLocalizations.of(context)`, vốn là một lượt tra `InheritedWidget` — nghĩa là nó cần một context nằm dưới `MaterialApp`, và nghĩa là đổi locale sẽ dựng lại mọi widget đã đọc nó.

## Định dạng ARB, vượt qua phần hiển nhiên

File ARB là JSON, trong đó mỗi khoá là một thông điệp và mỗi `@khoá` là siêu dữ liệu của nó.

```json
{
  "@@locale": "en",

  "appTitle": "FlutterCook",
  "@appTitle": {
    "description": "Hiện trên app bar và trong trình chuyển ứng dụng"
  },

  "unreadCount": "{count, plural, =0{No new messages} one{1 new message} other{{count} new messages}}",
  "@unreadCount": {
    "description": "Chữ trên huy hiệu của tab hộp thư",
    "placeholders": {
      "count": { "type": "int" }
    }
  },

  "lastSeen": "Last seen {when}",
  "@lastSeen": {
    "placeholders": {
      "when": {
        "type": "DateTime",
        "format": "yMMMd"
      }
    }
  }
}
```

Ba thứ ở đây quyết định năm tới của bạn khổ tới mức nào.

**Trên thực tế `description` không phải tuỳ chọn.** Đó là ngữ cảnh duy nhất người dịch có được. "Open" mà không có mô tả sẽ quay về dưới dạng động từ ở ngôn ngữ này và tính từ ở ngôn ngữ khác, và bạn chỉ biết khi có người dùng báo lỗi.

**`type` của placeholder quyết định chữ ký hàm sinh ra.** `int` cho bạn `int count`; `DateTime` kèm `format` cho bạn `DateTime when` và sinh sẵn lời gọi `DateFormat`. Không có kiểu thì nó là `Object` và bạn nhận `toString()` — đó là cách những chuỗi ISO thô lọt ra giao diện.

**Các nhóm số nhiều là theo từng ngôn ngữ.** Tiếng Anh dùng `one` và `other`. Tiếng Việt chỉ dùng `other`. Tiếng Ba Lan dùng `one`, `few`, `many`, `other`. Tiếng Nga và tiếng Ả Rập có bộ riêng. Viết `count == 1 ? 'item' : 'items'` trong Dart là nướng cứng ngữ pháp tiếng Anh vào code; cú pháp plural của ICU cho phép mỗi file dịch tự khai báo nhóm của nó. Đây là lý do mạnh nhất để dùng ARB thay vì một cái map.

Lời gọi sinh ra là Dart bình thường:

```dart
final l10n = AppLocalizations.of(context);
Text(l10n.unreadCount(inbox.unreadCount));
Text(l10n.lastSeen(user.lastSeenAt));
```

## `select` cho giống và các biến thể liệt kê

`plural` có một người anh em mà ít ai dùng tới:

```json
{
  "invitedYou": "{gender, select, male{He invited you} female{She invited you} other{They invited you}}",
  "@invitedYou": {
    "placeholders": { "gender": { "type": "String" } }
  }
}
```

Hãy dùng nó cho bất cứ chỗ nào cấu trúc câu thay đổi theo một giá trị, không chỉ riêng giống — gói thuê bao, trạng thái tài liệu, phương thức giao hàng. Cách thay thế là ba khoá riêng và một chuỗi `if` trong Dart, tức là đẩy một quyết định ngữ pháp vào phần code mà người dịch không với tới được.

## Số, ngày tháng và tiền tệ

`intl` định dạng những thứ này; đừng tự viết tay.

```dart
final locale = Localizations.localeOf(context).toString();

NumberFormat.currency(locale: locale, symbol: '₫').format(120000);
NumberFormat.compact(locale: locale).format(1250000);       // 1.25M / 1,25 Tr
DateFormat.yMMMMd(locale).format(order.placedAt);
DateFormat.Hm(locale).format(order.placedAt);
```

Khác biệt ở đây không chỉ là hình thức. Dấu thập phân đổi giữa `.` và `,`. Thứ tự ngày tháng khác nhau. Một số locale dùng hệ chữ số hoàn toàn khác. Một chuỗi cứng `'${d.day}/${d.month}/${d.year}'` là sai với khoảng một nửa thế giới.

Hai ghi chú thực dụng. `DateFormat` cần dữ liệu locale được khởi tạo cho bất cứ ngôn ngữ nào ngoài mặc định; trong ứng dụng Flutter, các delegate của `flutter_localizations` lo việc đó cho những locale mà ứng dụng hỗ trợ. Và hãy định dạng theo giờ **địa phương** — lưu UTC, chuyển bằng `toLocal()` ở rìa hệ thống, nếu không câu "đăng 2 giờ trước" của bạn sẽ lệch đúng bằng độ lệch múi giờ.

## Phân giải locale: chuyện gì xảy ra với `fr-CA`

`supportedLocales` là một danh sách, và thiết bị có thể báo về thứ không nằm trong đó. Cách phân giải mặc định thử khớp chính xác, rồi khớp theo ngôn ngữ, rồi lùi về phần tử đầu tiên của danh sách. Vế cuối làm nhiều người bất ngờ: một locale không được hỗ trợ sẽ nhận `supportedLocales.first`, nên **hãy đặt ngôn ngữ mặc định thật sự của bạn lên đầu**.

Khi bạn cần kiểm soát — một biến thể vùng cần ánh xạ vào một file cụ thể, hoặc ngôn ngữ do người dùng chọn được lưu trong cấu hình:

```dart
MaterialApp(
  locale: settings.overrideLocale, // null = theo thiết bị
  supportedLocales: AppLocalizations.supportedLocales,
  localeResolutionCallback: (deviceLocale, supported) {
    if (deviceLocale == null) return supported.first;
    for (final l in supported) {
      if (l.languageCode == deviceLocale.languageCode) return l;
    }
    return supported.first;
  },
);
```

Đặt `locale` tường minh sẽ ghi đè hoàn toàn thiết bị — đó là cách một bộ chọn ngôn ngữ trong ứng dụng hoạt động. Hãy lưu lại lựa chọn đó, và nhớ rằng `null` phải là một giá trị hợp lệ mang nghĩa "theo hệ thống".

## Phải-sang-trái, và nó không chỉ là lật gương

Thêm tiếng Ả Rập hay tiếng Do Thái sẽ đảo hướng bố cục. Flutter lo được phần lớn nếu bạn đã dùng các API có hướng:

| Dùng | Đừng dùng |
| --- | --- |
| `EdgeInsetsDirectional.only(start: 16)` | `EdgeInsets.only(left: 16)` |
| `AlignmentDirectional.centerStart` | `Alignment.centerLeft` |
| `BorderRadiusDirectional` | `BorderRadius` |
| `Positioned.directional(start: ...)` | `Positioned(left: ...)` |

`Row` tự đảo khi ở chế độ RTL. Đa số icon nên lật gương — mũi tên quay lại phải chỉ hướng ngược — nhưng không phải tất cả: nút play, đồng hồ, logo thì không. Dùng `Transform.flip` cho những cái cần lật, và kiểm tra phần còn lại.

Kiểm thử nó mà không cần biết ngôn ngữ đó:

```dart
Directionality(textDirection: TextDirection.rtl, child: MyScreen())
```

Bất cứ thứ gì nhìn thấy vẫn đứng yên đều là một chỗ `left`/`right` cứng.

## Kiểm thử widget đa ngôn ngữ

Một widget test không có delegate sẽ ném lỗi ngay khi có gì đó gọi `AppLocalizations.of`. Hãy cấp cho nó:

```dart
Widget wrap(Widget child, {Locale locale = const Locale('en')}) => MaterialApp(
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: child,
    );

testWidgets('huy hiệu hộp thư chia số nhiều đúng', (tester) async {
  await tester.pumpWidget(wrap(const InboxBadge(count: 1)));
  expect(find.text('1 new message'), findsOneWidget);

  await tester.pumpWidget(wrap(const InboxBadge(count: 5)));
  expect(find.text('5 new messages'), findsOneWidget);
});
```

Assert vào chuỗi tiếng Anh nguyên văn trong test là một đánh đổi: nó bắt được hồi quy thật nhưng vỡ khi câu chữ đổi. Điểm cân bằng hợp lý là assert vào giá trị đã dịch tính từ chính nguồn đó (`l10n.unreadCount(5)`), để test kiểm tra phần đấu nối chứ không kiểm tra câu chữ.

## Quy trình giữ cho người dịch còn tỉnh táo

1. **Chỉ `app_en.arb` được thêm khoá mới bằng tay.** Nó là template; trình sinh sẽ đối chiếu các file khác với nó.
2. **Đừng bao giờ tái dùng một khoá với nghĩa khác.** Bản dịch gắn với khoá; đổi chữ tiếng Anh dưới một khoá sẽ âm thầm làm mọi bản dịch của nó thành sai.
3. **Xoá khoá chết.** Một khoá cũ còn sót là một chuỗi mà người ta vẫn đang được trả tiền để dịch.
4. **Kiểm tra khoá thiếu trong CI.** `flutter gen-l10n` báo cáo các thông điệp chưa dịch; hãy ghi chúng ra file bằng `untranslated-messages-file` trong `l10n.yaml` và cho build fail nếu danh sách đó dài ra.

## Câu hỏi thường gặp

**Tôi lấy chuỗi ngoài widget, trong repository hoặc trong isolate nền được không?**

Không lấy qua `AppLocalizations.of(context)` được — nó cần context. Hoặc truyền chuỗi từ tầng UI xuống, hoặc trả về một mã lỗi rồi dịch ở nơi hiển thị. Cách thứ hai thường đúng: một repository không nên biết người dùng đọc ngôn ngữ nào.

**Còn `intl_translation` và `@@last_modified` thì sao?**

`intl_translation` là bộ công cụ cũ, tách rời, trích thông điệp từ Dart có annotation. `gen_l10n` được tích hợp sẵn trong công cụ Flutter và là thứ tài liệu hiện hành nhắm tới. `@@last_modified` là siêu dữ liệu do một số công cụ ghi vào ARB; nó vô hại.

**Đổi ngôn ngữ có phải khởi động lại ứng dụng không?**

Không. Đặt `locale` trên `MaterialApp` sẽ dựng lại nhánh đó và mọi lượt đọc `AppLocalizations.of(context)` sẽ nhận giá trị mới.

**Vì sao file sinh ra bị thiếu?**

`generate: true` phải nằm dưới `flutter:` trong `pubspec.yaml`, và file chỉ xuất hiện sau một lần build hoặc `flutter gen-l10n`. Mặc định nó nằm trong thư mục build, nên nó không có trong quản lý mã nguồn.

**File dịch nên nằm trong app hay tải từ máy chủ?**

ARB đóng gói sẵn thì đơn giản hơn, chạy được khi offline, và phát hành nguyên khối cùng đoạn code dùng nó. Chuỗi tải từ máy chủ cho phép sửa một lỗi chính tả mà không cần phát hành bản mới, đổi lại phải có trạng thái đang tải, một lớp cache và một đường dự phòng. Mặc định hãy đóng gói; chỉ thêm phần ghi đè từ xa khi nhịp phát hành thật sự đòi hỏi.

---

*Cú pháp ARB, các tuỳ chọn `l10n.yaml`, thứ tự phân giải và các API widget có hướng mô tả ở đây được ghi trong hướng dẫn quốc tế hoá của Flutter và tài liệu gói `intl` đã dẫn. Bộ quy trình, khuyến nghị assert vào chuỗi được tính ra trong test, và lập trường đóng gói-so-với-tải-từ-xa là đánh giá riêng của tôi. Hành vi công cụ thay đổi giữa các bản Flutter — hãy chạy `flutter gen-l10n --help` với SDK của bạn trước khi sao chép tuỳ chọn.*
