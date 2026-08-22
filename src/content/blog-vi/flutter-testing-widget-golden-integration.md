---
title: "Test Flutter đỏ vì đúng lý do: widget, golden và integration"
description: "Kim tự tháp test áp vào Flutter một cách sòng phẳng: unit, widget, golden và integration mỗi lớp chứng minh được gì, vì sao pumpAndSettle là mặc định sai, vì sao golden lệch giữa máy Mac của bạn và Linux CI, và bốn nguồn gây flaky trong một bộ test Flutter."
seoDescription: "Hướng dẫn test Flutter thực dụng: widget test với pump và pumpAndSettle, golden test sống sót qua CI, integration_test, và cách dẹp test flaky."
keywords:
  - widget test flutter
  - golden test flutter ci
  - pumpandsettle và pump
  - flutter integration_test
  - test flaky flutter
  - mocktail flutter test
category: "Hướng dẫn"
topic: "Testing"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧪"
tags: ["Flutter", "Testing", "CI", "Golden Tests", "Dart"]
sources:
  - name: "Flutter — Testing Flutter apps"
    url: "https://docs.flutter.dev/testing/overview"
  - name: "Flutter — An introduction to widget testing"
    url: "https://docs.flutter.dev/cookbook/testing/widget/introduction"
  - name: "Flutter — Integration testing"
    url: "https://docs.flutter.dev/testing/integration-tests"
  - name: "WidgetTester — tài liệu API flutter_test"
    url: "https://api.flutter.dev/flutter/flutter_test/WidgetTester-class.html"
  - name: "WidgetTester.pumpAndSettle — tài liệu API flutter_test"
    url: "https://api.flutter.dev/flutter/flutter_test/WidgetTester/pumpAndSettle.html"
  - name: "WidgetTester.runAsync — tài liệu API flutter_test"
    url: "https://api.flutter.dev/flutter/flutter_test/WidgetTester/runAsync.html"
  - name: "matchesGoldenFile — tài liệu API flutter_test"
    url: "https://api.flutter.dev/flutter/flutter_test/matchesGoldenFile.html"
  - name: "LocalFileComparator — tài liệu API flutter_test"
    url: "https://api.flutter.dev/flutter/flutter_test/LocalFileComparator-class.html"
  - name: "FontLoader — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/services/FontLoader-class.html"
  - name: "mocktail trên pub.dev"
    url: "https://pub.dev/packages/mocktail"
  - name: "fake_async trên pub.dev"
    url: "https://pub.dev/packages/fake_async"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
draft: false
---

Có hai loại test đỏ. Một loại báo cho bạn biết hành vi đã đổi. Loại kia báo rằng máy đang bận, hoặc CI runner dùng font khác, hoặc ai đó vừa thêm hiệu ứng shimmer ở màn hình cách đó ba tầng. Loại thứ hai còn tệ hơn không có test, vì một team đã quen bấm "re-run pipeline" cũng là một team đã quen phớt lờ pipeline.

Flutter làm cho chuyện này dễ sai theo một kiểu rất riêng. `flutter_test` cho bạn một đồng hồ giả và một màn hình ảo — đó là món quà — nhưng API lại dâng sẵn `pumpAndSettle()`, và `pumpAndSettle()` là một vòng lặp pump frame cho đến khi không còn frame nào được lên lịch. Chĩa nó vào một progress indicator vô hạn thì nó sẽ pump suốt mười phút rồi ném lỗi. Golden test là cái bẫy còn lại: chúng thật sự là cách rẻ nhất để bắt regression về mặt hình ảnh, và cũng là thứ mà các team xóa đi sau tuần thứ ba của điệp khúc "máy tôi xanh, CI thì đỏ".

Bài này là kim tự tháp test áp vào Flutter, không kèm quảng cáo: mỗi lớp thật sự chứng minh được gì, một ví dụ chạy được cho từng lớp, rồi một phần riêng về bốn cơ chế tạo ra gần như toàn bộ flake trong Flutter.

## Mỗi lớp thật sự chứng minh được gì

Câu hỏi hữu ích không phải "nên viết loại test nào" mà là "test này vẫn xanh trong trường hợp nào mà lẽ ra nó phải đỏ".

| Lớp | Chạy ở đâu | Tốc độ | Chứng minh | Mù với |
|---|---|---|---|---|
| Unit (`test`) | Dart VM, không render | Mili giây | Logic, ca biên, máy trạng thái | Mọi thứ về cây widget và màn hình |
| Widget (`testWidgets`) | Headless, đồng hồ giả, màn hình ảo 800×600 | Vài chục ms | Đấu nối build/layout/tương tác, semantics | I/O thật, font thật, thời gian thật |
| Golden (`matchesGoldenFile`) | Như widget, cộng so sánh pixel | Vài chục ms | Regression hình ảnh ở mức pixel | Mọi thứ không nằm trong frame đã chụp |
| Integration (`integration_test`) | Thiết bị hoặc emulator thật | Vài giây đến vài phút | Plugin, platform channel, khởi động, điều hướng xuyên app | Gần như không mù gì — nên nó mới chậm |

Tỷ lệ giữa các lớp suy ra từ bảng đó, không phải từ một hình tam giác. Logic tách được ra khỏi widget thì nên test ở nơi rẻ hơn cả nghìn lần. Widget test là nơi chứa phần lớn assertion của bạn, vì phần lớn bug trong một app Flutter là bug đấu nối. Golden nên phủ một tập component nhỏ và được chọn có chủ đích. Còn integration test nên phủ đúng vài luồng mà nếu plugin hỏng thì thành sự cố production: khởi động, đăng nhập, thanh toán, và cái luồng không thể thay thế được của riêng app bạn.

## Unit test: phần lẽ ra không cần đến cây widget

Nếu quy tắc tính giá sống trong một `StatefulWidget` thì mỗi test tính giá đều tốn một lần pump. Kéo nó ra ngoài thì test trở nên nhàm chán — và nhàm chán chính là mục tiêu.

```dart
// test/pricing_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:shop/pricing.dart';

void main() {
  group('Quote.forCart', () {
    test('applies a percentage promo before shipping', () {
      final quote = Quote.forCart(
        subtotalCents: 10000,
        shippingCents: 500,
        promo: const Promo.percentage('SPRING10', 10),
      );

      expect(quote.discountCents, 1000);
      expect(quote.totalCents, 9500);
    });

    test('a discount larger than the cart clamps at zero', () {
      final quote = Quote.forCart(
        subtotalCents: 300,
        shippingCents: 0,
        promo: const Promo.fixed('OVERKILL', 900),
      );

      expect(quote.discountCents, 300);
      expect(quote.totalCents, 0);
    });
  });
}
```

Những unit test thú vị là những test dính đến thời gian. Đừng dùng delay thật cho chúng — dùng `fake_async`, nó cho bạn một zone mà bạn tự tay đẩy đồng hồ:

```dart
// test/retry_test.dart
import 'dart:async';

import 'package:fake_async/fake_async.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shop/retry.dart';

void main() {
  test('retries three times with backoff, then gives up', () {
    fakeAsync((async) {
      var attempts = 0;
      Object? failure;

      retry(
        () async {
          attempts++;
          throw TimeoutException('upstream down');
        },
        maxAttempts: 3,
        backoff: const Duration(seconds: 2),
      ).then((_) {}, onError: (Object e) => failure = e);

      async.elapse(const Duration(milliseconds: 1));
      expect(attempts, 1, reason: 'first attempt is immediate');

      async.elapse(const Duration(seconds: 30));
      expect(attempts, 3);
      expect(failure, isA<TimeoutException>());
    });
  });
}
```

Test kiểu này chạy dưới một mili giây, trong khi với timer thật thì mất nửa phút. `async.elapse` cũng báo lỗi rõ ràng nếu code của bạn để sót một timer đang chạy — đúng là loại bug bạn muốn nghe.

## Widget test là ngựa kéo, và pump là toàn bộ mẹo

`testWidgets` chạy thân test bên trong một zone `FakeAsync`. Đồng hồ là giả — nó bắt đầu từ 1 tháng 1 năm 2015 UTC — màn hình là một bề mặt ảo 800×600, và `Timer` cùng `Future.delayed` chỉ tiến khi bạn cho phép. Đó là thứ làm widget test tất định, và cũng là lý do người ta rối về chuyện phải pump bao nhiêu lần.

Đây là cơ chế, và đáng để nhớ vì nó giải thích gần hết các bug kiểu "test của tôi nhìn thấy state cũ". `tester.pump()` flush các microtask đang chờ và vẽ một frame — nhưng **chỉ vẽ nếu thật sự có frame được lên lịch**. Nên số lần pump phụ thuộc vào cái gì đang ở trên màn hình. Nếu có thứ gì đó đang chạy animation thì luôn có frame đang chờ, và một lần pump vừa chạy callback `.then` vừa vẽ kết quả. Nếu cây widget đang đứng yên thì lần pump đầu không có gì để vẽ: nó chạy callback, callback gọi `setState`, và chính lời gọi đó mới lên lịch cái frame mà lần pump *thứ hai* vẽ ra. Đừng học thuộc một con số — khi một assertion lệch đúng một trạng thái, hãy thêm một lần pump.

```dart
// test/promo_field_test.dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:shop/promo_page.dart';
import 'package:shop/quote_repository.dart';

class MockQuoteRepository extends Mock implements QuoteRepository {}

void main() {
  late MockQuoteRepository repository;

  setUp(() {
    repository = MockQuoteRepository();
  });

  Future<void> pumpPage(WidgetTester tester) {
    return tester.pumpWidget(
      MaterialApp(home: PromoPage(repository: repository)),
    );
  }

  testWidgets('shows a spinner while the code is checked, then the discount',
      (WidgetTester tester) async {
    final completer = Completer<Quote>();
    when(() => repository.applyPromo('SPRING10'))
        .thenAnswer((_) => completer.future);

    await pumpPage(tester);
    await tester.enterText(find.byType(TextField), 'SPRING10');
    await tester.tap(find.widgetWithText(FilledButton, 'Apply'));

    // One frame is enough for the loading state to reach the screen.
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    completer.complete(const Quote(discountCents: 1000, totalCents: 9500));
    // The spinner keeps a frame scheduled, so this single pump both runs the
    // .then callback and draws the result. On an idle tree it would take two.
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text(r'-$10.00'), findsOneWidget);
    verify(() => repository.applyPromo('SPRING10')).called(1);
  });
}
```

Hai chi tiết trong test đó là cố ý. Dùng `Completer` thay vì một future đã hoàn tất khiến trạng thái loading thật sự tồn tại đủ lâu để assert — với `thenAnswer((_) async => quote)` bạn đang đua với hàng đợi microtask. Và `verify(...).called(1)` bắt được bug double-submit mà không assertion giao diện nào bắt được.

Ba thói quen giữ cho widget test dễ đọc khi số lượng tăng lên. Ưu tiên finder mang tính ngữ nghĩa — `find.widgetWithText`, `find.bySemanticsLabel`, `find.byTooltip` — hơn là `find.byType` lên một widget private, vì nhóm ngữ nghĩa còn đỏ khi accessibility hỏng. Dùng `find.descendant(of: find.byType(Card), matching: find.text('Total'))` thay vì tra theo chỉ số. Và khi một widget cần màn hình lớn hơn 800×600, hãy đặt kích thước tường minh rồi đăng ký phần dọn dẹp:

```dart
tester.view.physicalSize = const Size(1600, 2400);
tester.view.devicePixelRatio = 2.0;
addTearDown(tester.view.reset);
```

`tester.runAsync` là cửa thoát hiểm cho trường hợp hiếm mà fake async bó tay: code sinh isolate hoặc chạm tới một OS thread thật — giải mã ảnh, một lời gọi `compute()`, I/O file thật. Bên trong `runAsync` zone là thật, nên bạn **không** pump được; làm việc thật xong, thoát ra, rồi mới pump.

```dart
// dart:ui as ui, package:flutter/material.dart, package:flutter/services.dart
testWidgets('renders a decoded thumbnail', (WidgetTester tester) async {
  late ui.Image image;
  await tester.runAsync(() async {
    final data = await rootBundle.load('test/fixtures/thumb.png');
    image = await decodeImageFromList(data.buffer.asUint8List());
  });

  await tester.pumpWidget(MaterialApp(home: RawImage(image: image)));
  expect(find.byType(RawImage), findsOneWidget);
});
```

Nếu một test treo và nó có dùng `runAsync`, nguyên nhân gần như luôn là một future được tạo bên trong zone giả mà zone thật không bao giờ hoàn tất được. Cách sửa là tái cấu trúc, không phải thêm `runAsync`.

## Golden vỡ trên máy người khác vì font và rasterization

Golden test là một ảnh chụp màn hình được commit vào git. `matchesGoldenFile` render `RepaintBoundary` tổ tiên gần nhất của widget khớp finder rồi so sánh từng byte với file PNG đã lưu; `flutter test --update-goldens` ghi đè các PNG đó. Đây là matcher bất đồng bộ, nên bắt buộc phải dùng với `await expectLater`.

Lý do các team bỏ golden gần như luôn là một trong ba thứ sau:

**Font.** Mặc định `flutter test` render chữ bằng một font test mà mọi glyph đều là một ô vuông đặc — tài liệu framework vẫn gọi nó là Ahem. Nó tất định, và cũng vô dụng khi cần review một golden. Thế là người ta nạp font thật, rồi app lại rơi về font *hệ thống* cho bất cứ ký tự nào mà font đã nạp không phủ — một emoji, một dấu tiếng Việt, một ký tự CJK, một icon Material. Font hệ thống khác nhau giữa macOS, Linux và Windows, nên golden cũng khác theo.

**Rasterization.** Việc khử răng cưa cho chữ và đường cong không được bảo đảm giống hệt nhau giữa các nền tảng host hay giữa các phiên bản Flutter. Nâng cấp Flutter thì golden bị vẽ lại một cách chính đáng. Có một nguồn bất định mà SDK đã dẹp hộ bạn: `flutter test` đặt `debugDisableShadows = true`, nên golden hoàn toàn không có bóng đổ. Đó cũng là lý do ảnh chụp qua `flutter drive` sẽ không bao giờ khớp với golden của `flutter test`.

**Layout trôi theo host.** Bất cứ thứ gì đọc trạng thái nền tảng — `Platform.isIOS`, locale, text scale — đều âm thầm đổi bức ảnh.

Cách chữa là một chính sách, không phải một package. Commit file font, nạp chúng cho mọi test, sinh golden trên đúng một nền tảng, và cho phép một sai số nhỏ ở chặng cuối. Tất cả nằm trong `test/flutter_test_config.dart`, file mà `flutter test` tự động nhận ra và áp cho mọi test trong cây thư mục đó.

```dart
// test/flutter_test_config.dart
import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';

Future<void> testExecutable(FutureOr<void> Function() testMain) async {
  TestWidgetsFlutterBinding.ensureInitialized();
  await _loadAppFonts();

  final current = goldenFileComparator;
  if (current is LocalFileComparator) {
    goldenFileComparator = _TolerantComparator(
      Uri.parse('${current.basedir}test.dart'),
      // 0.5% of pixels may differ before the test fails.
      precisionTolerance: 0.005,
    );
  }

  await testMain();
}

Future<void> _loadAppFonts() async {
  const families = <String, List<String>>{
    'Inter': [
      'assets/fonts/Inter-Regular.ttf',
      'assets/fonts/Inter-SemiBold.ttf',
    ],
    // Register the fallback explicitly so nothing reaches for a system font.
    'NotoSans': ['assets/fonts/NotoSans-Regular.ttf'],
  };

  for (final entry in families.entries) {
    final loader = FontLoader(entry.key);
    for (final asset in entry.value) {
      loader.addFont(rootBundle.load(asset));
    }
    await loader.load();
  }
}

class _TolerantComparator extends LocalFileComparator {
  _TolerantComparator(super.testFile, {required this.precisionTolerance});

  final double precisionTolerance;

  @override
  Future<bool> compare(Uint8List imageBytes, Uri golden) async {
    final result = await GoldenFileComparator.compareLists(
      imageBytes,
      await getGoldenBytes(golden),
    );

    if (result.passed || result.diffPercent <= precisionTolerance) {
      result.dispose();
      return true;
    }

    final error = await generateFailureOutput(result, golden, basedir);
    result.dispose();
    throw FlutterError(error);
  }
}
```

Hãy sòng phẳng về sai số: nó là con dao cùn. Ngân sách 0.5% pixel che giấu một thay đổi viền một pixel hiệu quả y hệt như che giấu khác biệt khử răng cưa. Dùng nó để hấp thụ nhiễu rasterization, đừng bao giờ dùng nó thay cho việc ghim nền tảng.

Bản thân test thì ngắn, và được gắn tag để chạy có chọn lọc:

```dart
// test/goldens/quote_card_golden_test.dart
@Tags(['golden'])
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shop/quote_card.dart';

void main() {
  testWidgets('QuoteCard with a discount', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: Center(
            child: RepaintBoundary(
              child: QuoteCard(
                quote: Quote(discountCents: 1000, totalCents: 9500),
              ),
            ),
          ),
        ),
      ),
    );

    await expectLater(
      find.byType(QuoteCard),
      matchesGoldenFile('goldens/quote_card_discount.png'),
    );
  });
}
```

Khai báo tag trong `dart_test.yaml` để runner không cảnh báo:

```yaml
# dart_test.yaml
tags:
  golden:
```

Sau đó golden chỉ chạy ở một nơi. Lập trình viên chạy `flutter test --exclude-tags golden`; job CI trên Linux — ghim đúng phiên bản Flutter đã sinh ra các file đó — chạy `flutter test --tags golden`, và sinh lại bằng `flutter test --tags golden --update-goldens` trong cùng container image. Nếu bạn muốn có sẵn biến thể theo kích thước thiết bị và báo cáo diff đẹp hơn mà không phải tự dựng, `alchemist` trên pub.dev gói sẵn mẫu này; với phần lớn app thì riêng SDK đã đủ.

## integration_test: ba bốn luồng đáng chạy thật

`integration_test` đi kèm SDK và dùng lại API `testWidgets`, nên code nhìn quen mắt. Cái đổi bên dưới mới quan trọng: `IntegrationTestWidgetsFlutterBinding` kế thừa binding *live*, không phải binding tự động. Không có đồng hồ giả. `pump()` chờ thời gian thật, plugin thật trả lời platform channel thật, và lời gọi mạng thật sự đi ra ngoài.

```yaml
# pubspec.yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  integration_test:
    sdk: flutter
```

```dart
// integration_test/checkout_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shop/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('a promo code applied on device reaches the total',
      (WidgetTester tester) async {
    app.main();
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('cart_tab')));
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('promo_field')), 'SPRING10');
    await tester.tap(find.widgetWithText(FilledButton, 'Apply'));

    // Real network, real time: poll for the result instead of guessing.
    await tester.pumpAndSettle(const Duration(milliseconds: 100));

    expect(find.textContaining(r'$95.00'), findsOneWidget);
  });
}
```

Chạy bằng `flutter test integration_test/checkout_test.dart -d <device-id>`, hoặc qua `flutter drive` khi bạn cần Firebase Test Lab hay một pipeline chụp ảnh. Giữ danh sách ngắn. Mỗi luồng thêm vào đây đều phải trả giá ở mọi pull request, và một integration test đỏ lúc được lúc không dạy team đúng cái thói quen xấu như một widget test flaky.

`IntegrationTestWidgetsFlutterBinding` còn mang theo các móc đo hiệu năng: `binding.traceAction(...)` ghi một timeline vào `reportData`, còn `binding.takeScreenshot('name')` chụp màn hình thiết bị (trên Android phải gọi `binding.convertFlutterSurfaceToImage()` trước). Đó là công cụ đúng cho một ngân sách jank khi cuộn; chúng không thay thế được lớp widget.

## Flake thật ra đến từ đâu

Gần như mọi test Flutter flaky mà tôi từng xem đều rơi vào một trong bốn nhóm sau.

**`pumpAndSettle` chĩa vào thứ không bao giờ dừng.** Hành vi được ghi rõ trong tài liệu: `pumpAndSettle` pump lặp đi lặp lại cho tới khi không còn frame nào được lên lịch, và nếu quá thời gian chờ — mặc định mười phút — nó ném lỗi. Một `CircularProgressIndicator` không xác định, một placeholder shimmer, một Lottie chạy vòng, một `AnimationController.repeat()` — bất kỳ thứ nào trong đó cũng biến nó thành mười phút treo rồi đỏ. Cách sửa là pump có chủ đích:

```dart
await tester.tap(find.byKey(const Key('submit')));
await tester.pump();                                  // loading state
await tester.pump(const Duration(milliseconds: 300)); // halfway through the transition
await tester.pump(const Duration(seconds: 1));        // past the end
```

`pumpAndSettle` còn trả về số lần nó đã pump, nên `expect(await tester.pumpAndSettle(), 3)` là một assertion thật về độ dài animation chứ không phải một cái nhún vai.

**Timer sống lâu hơn widget.** Binding tự động assert ở cuối mỗi test rằng không còn gì đang chờ, với thông báo *"A Timer is still pending even after the widget tree was disposed."* Người anh em của nó là *"was disposed with an active Ticker"*, ném ra khi một `AnimationController` tạo bằng `SingleTickerProviderStateMixin` không bao giờ được dispose. Cả hai đều là rò rỉ thật trong app của bạn mà chỉ test mới đủ khắt khe để phát hiện — hủy `Timer` và dispose controller trong `dispose()` là cả hai biến mất.

**Mạng trong test.** Binding test cài một `HttpOverrides` mà client của nó trả về phản hồi rỗng với status 400 cho mọi request, đúng là để một test không bao giờ phụ thuộc vào mạng. Nghĩa là `Image.network` render ra trạng thái lỗi chứ không phải ảnh của bạn, và mọi nhánh code gọi HTTP thật đều rẽ vào nhánh thất bại. Đừng lách bằng một client sống — hãy inject client, hoặc fake ở ranh giới repository như trong widget test phía trên. Nếu bắt buộc phải dùng ảnh thật, đưa bytes vào qua `runAsync` và một file fixture.

**Future không await.** `tester.tap` phát sự kiện con trỏ và không pump. `tester.enterText` flush microtask nhưng không vẽ frame. Code bắn một request mà không await sẽ để lại một callback hoàn tất nằm trong hàng đợi microtask, và nếu dòng tiếp theo của bạn là `expect` thì bạn đang assert lên frame trước cái frame bạn định assert. Hai quy tắc là đủ: đừng viết `unawaited(...)` trong code mà test điều khiển nếu không cho test một cách quan sát thời điểm hoàn tất, và khi một assertion lệch đúng một trạng thái, hãy thêm một `pump()` thay vì với tay lấy `pumpAndSettle()`.

Còn một nguồn thứ năm ít gặp hơn: test phụ thuộc thứ tự chạy vì chúng dùng chung một biến top-level hoặc một singleton. `setUp` nên dựng lại mọi thứ test chạm vào; `addTearDown` nên hoàn tác mọi thứ mang tính toàn cục.

## Đấu nối để CI giữ được màu xanh

```bash
# Everything except goldens — what developers run, on any OS.
flutter test --exclude-tags golden

# Goldens, on the pinned Linux image only.
flutter test --tags golden

# Regenerate goldens (same image, same Flutter version, or don't bother).
flutter test --tags golden --update-goldens

# Integration tests, against a booted device or emulator.
flutter test integration_test -d emulator-5554
```

Hai quy tắc tạo ra khác biệt giữa một bộ test được tin và một bộ test bị tắt tiếng. Thứ nhất, test flaky thì sửa hoặc xóa ngay trong ngày nó flake — không bao giờ retry, vì một annotation retry biến một race thật trong app của bạn thành độ trễ vô hình. Thứ hai, ghim phiên bản Flutter ở mọi nơi golden được sinh ra hoặc được kiểm; một lần nâng SDK làm đổi rasterization phải hiện ra thành một commit có chủ đích sinh lại các PNG, chứ không phải thành nhiễu trên một pull request chẳng liên quan.

Về mock, `mocktail` không cần sinh code và đọc mượt với closure; `mockito` cần `build_runner` và `@GenerateNiceMocks`, nhưng mock nó sinh ra thì analyzer nhìn thấy, điều mà vài team thích hơn. Chọn cái nào cũng được. Cái không ổn là mock chính widget của bạn — nếu bạn thấy mình đang làm vậy thì widget đó đang ôm quá nhiều việc, và chỗ cần sửa nằm ở `lib/`, không phải ở `test/`.

## Câu hỏi thường gặp

**Cứ dùng `pumpAndSettle` khắp nơi có được không?**
Không, và tài liệu API nói thẳng điều đó: thực hành tốt hơn là hiểu chính xác vì sao cần từng frame rồi pump đúng bấy nhiêu lần. `pumpAndSettle` che mất các regression kiểu animation khởi động trễ một frame, và biến mọi animation vô hạn thành mười phút chờ rồi đỏ. Hãy dùng nó ở đầu một integration test, nơi thời gian thật là không tránh được, và dùng pump tường minh trong widget test.

**Vì sao widget test của tôi đôi khi cần pump hai lần sau khi future hoàn tất?**
Vì `pump` flush microtask nhưng chỉ vẽ frame nếu đã có frame được lên lịch. Trên một cây widget đang đứng yên, lần pump đầu chạy `.then`/`setState` của bạn — và chính lời gọi đó mới lên lịch frame — nên lần pump thứ hai mới là lần vẽ. Nếu trên màn hình đang có animation thì luôn có frame chờ sẵn và một lần pump làm cả hai việc. Đừng học thuộc con số; khi assertion lệch một trạng thái, hãy thêm một lần pump.

**Chạy golden test trên macOS và Linux có ra cùng byte không?**
Không đáng tin cậy. Khử răng cưa cho chữ và cơ chế fallback font khác nhau theo host, nên câu trả lời thực dụng là chọn ra một nền tảng — thường là một container Linux đã ghim phiên bản, vì phần lớn CI cũng chạy ở đó — sinh ở đó, kiểm ở đó, và bỏ qua golden ở nơi khác bằng tag. Sai số trong một `LocalFileComparator` tùy chỉnh hấp thụ phần nhiễu còn lại; nó không thay được việc ghim nền tảng.

**mocktail hay mockito?**
`mocktail` nếu bạn muốn không sinh code và không cần analyzer kiểm các stub theo kiểu null safety. `mockito` nếu team bạn vốn đã chạy `build_runner` và muốn mock được sinh ra, có kiểu tĩnh. Cả hai đều đang được duy trì trên pub.dev; lựa chọn này hiếm khi quan trọng bằng việc bạn kẻ đường ranh mock ở đâu.

**Một app nên có bao nhiêu integration test?**
Ít đến mức bạn kể ra được từ trí nhớ. Chúng tồn tại để chứng minh plugin, platform channel và quá trình khởi động chạy được trên thiết bị thật — những thứ mà widget test về mặt cấu trúc không thấy được. Mọi thứ còn lại đều nhanh hơn, chính xác hơn và ít flaky hơn khi lùi xuống một lớp.

---

*Phần mô tả hành vi API ở đây — ngữ nghĩa của pump, HttpOverrides trả 400, bóng đổ bị tắt trong `flutter test`, thời gian chờ của `pumpAndSettle` — lấy từ tài liệu và mã nguồn `flutter_test`. Các khuyến nghị mang tính chính sách (một nền tảng golden duy nhất, xóa test flaky, giữ integration test ít) là quan điểm của tôi, hình thành từ việc bảo trì các bộ test chứ không từ một nghiên cứu. Bất cứ điều gì phụ thuộc phiên bản đều nên kiểm lại với tài liệu của đúng phiên bản Flutter bạn đang dùng.*
