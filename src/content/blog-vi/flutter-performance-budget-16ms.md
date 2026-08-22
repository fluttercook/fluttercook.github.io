---
title: "Ngân sách 16.6 ms cho mỗi frame Flutter — thay cho câu \"để sau tối ưu\""
description: "Performance không phải một buổi debug bạn xếp lịch sau khi feature lên. Nó là một ngân sách có từng khoản mục: 16.6 ms mỗi frame ở 60 Hz, 8.3 ms ở 120 Hz, chia cho UI thread và raster thread. Sáu quy tắc, code thực thi từng quy tắc, và cách đo để bạn kiểm chứng thay vì tin suông."
seoDescription: "Xem performance Flutter như ngân sách 16.6 ms mỗi frame: const constructor, phạm vi rebuild, ListView.builder, kích thước decode ảnh, saveLayer, RepaintBoundary."
keywords:
  - frame budget flutter
  - flutter 16ms mỗi frame
  - tối ưu performance flutter
  - flutter repaintboundary
  - listview builder flutter tối ưu
  - cachewidth flutter bộ nhớ ảnh
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "⏱️"
tags: ["Flutter", "Performance", "Rendering", "DevTools"]
sources:
  - name: "Flutter — Performance best practices"
    url: "https://docs.flutter.dev/perf/best-practices"
  - name: "Flutter — Dùng performance overlay"
    url: "https://docs.flutter.dev/perf/ui-performance"
  - name: "FrameTiming — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/FrameTiming-class.html"
  - name: "RepaintBoundary — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/widgets/RepaintBoundary-class.html"
  - name: "ResizeImage — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/painting/ResizeImage-class.html"
  - name: "Clip — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/Clip.html"
  - name: "ImageCache — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/painting/ImageCache-class.html"
  - name: "TimelineSummary — tài liệu API flutter_driver"
    url: "https://api.flutter.dev/flutter/flutter_driver/TimelineSummary-class.html"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
draft: false
---

"Để sau tối ưu" là kế hoạch chọn đúng phiên bản khó nhất của công việc. "Sau" nghĩa là list view đã có sáu tầng builder lồng nhau, URL ảnh đã đến từ ba service khác nhau, và không ai còn nhớ trong mười hai widget trên màn hình thì cái nào đang repaint. Bạn kết thúc bằng việc chia đôi timeline để dò, thay vì viết code.

Cách khác không cần anh hùng. Nó là một ngân sách. Một frame có một lượng thời gian cố định, thời gian đó chia cho hai thread, và mọi widget bạn viết đều tiêu một phần. Nếu bạn biết con số và biết các khoản mục, bạn có thể quyết định ngay lúc viết code là mình có đủ tiền hay không — giống hệt cách bạn quyết định một lời gọi network có được nằm trên đường đi chính hay không.

Đây là ngân sách tôi tự bắt mình tuân theo, sáu khoản mục chiếm gần hết nó, và cách đo từng khoản. Việc đo quan trọng hơn các quy tắc: một quy tắc bạn không kiểm chứng được là mê tín, và Flutter đã đủ nhiều truyền thuyết về performance rồi.

## Ngân sách là 16.6 ms, và nó chia làm hai

Màn hình 60 Hz đòi một frame mới mỗi 16.6 ms. Màn hình 120 Hz đòi mỗi 8.3 ms. Đó là toàn bộ ngân sách — không phải cho riêng code của bạn, mà cho tất cả: tick animation, các hàm `build`, layout, paint, rồi biến kết quả thành lệnh GPU.

Flutter làm việc đó trên hai thread. **UI thread** chạy Dart: tick animation, rebuild widget bẩn, layout và paint render tree, rồi tạo ra layer tree mô tả cần vẽ gì. **Raster thread** nhận layer tree đó và biến nó thành công việc GPU thật sự. Hai thread chạy theo kiểu pipeline — trong lúc raster thread rasterise frame *n*, UI thread đã có thể build frame *n+1* — nên ràng buộc không phải là tổng của chúng nằm dưới 16.6 ms. Ràng buộc là **từng thread, tính riêng, phải nằm dưới 16.6 ms**. Thread nào chậm hơn sẽ quyết định frame rate của bạn.

Phân biệt đó quyết định bạn nhìn vào đâu. Một hàm `build` cấp phát nghìn object là vấn đề của UI thread, và không lượng tinh chỉnh shader nào sửa được. Một hiệu ứng blur toàn màn hình là vấn đề của raster thread, và cắt bớt rebuild sẽ không động tới nó.

Vì bạn cần khoảng dư cho những frame không "trung bình" — cái frame vừa push route, vừa có ảnh decode xong, vừa dính một lần GC — tôi chỉ cấp một nửa:

| Tần số quét | Ngân sách frame | Mục tiêu UI thread | Mục tiêu raster thread |
|---|---|---|---|
| 60 Hz | 16.6 ms | ≤ 8 ms | ≤ 8 ms |
| 90 Hz | 11.1 ms | ≤ 5.5 ms | ≤ 5.5 ms |
| 120 Hz | 8.3 ms | ≤ 4 ms | ≤ 4 ms |

Chuyện chia đôi là lựa chọn, không phải luật. Các mức tần số quét mới là luật.

Một lưu ý về nền tảng khi bạn chọn dòng nào: trên các iPhone có ProMotion, app bị giới hạn ở 60 Hz trừ khi app khai báo tham gia. Thêm dòng này vào `ios/Runner/Info.plist` nếu bạn thật sự muốn dòng 120 Hz có hiệu lực:

```xml
<key>CADisableMinimumFrameDurationOnPhone</key>
<true/>
```

Dưới đây là sáu khoản mục, mỗi khoản kèm quy tắc và cách kiểm.

| Khoản mục | Quy tắc | Cách kiểm |
|---|---|---|
| `const` constructor | Widget nào `const` được thì phải `const` | `flutter analyze` với các lint const |
| Phạm vi rebuild | Subtree được rebuild đúng bằng subtree đã đổi | `debugPrintRebuildDirtyWidgets` |
| Danh sách | Lazy mặc định; cố định chiều cao khi có thể | Đếm số lần gọi builder |
| Ảnh | Decode theo kích thước hiển thị, không theo kích thước gốc | `debugInvertOversizedImages` |
| `saveLayer` | Không lượt offscreen nào trên nội dung cuộn | `checkerboardOffscreenLayers` |
| `RepaintBoundary` | Đặt vì một lý do bạn gọi tên được | `debugRepaintRainbowEnabled` |

## `const` là tối ưu cho phần diff, không phải sở thích code style

Phần lớn mọi người học `const` theo kiểu "linter đòi vậy". Thứ nó thật sự làm là đổi hình dạng của quá trình diff element.

Dart canonicalise các biểu thức const: hai biểu thức const cùng kiểu với cùng tham số sẽ cho ra *cùng một instance*. Nên một widget `const` trong hàm `build` không bị dựng lại ở frame sau — nó đúng là cùng một object, cấp phát một lần, dùng mãi.

Chính tính đồng nhất đó là thứ framework kiểm tra. Khi một widget cha rebuild, mỗi element con so widget mới với widget nó đang giữ. Nếu là cùng một object, element trả về ngay: không `update`, không đệ quy vào subtree đó, không làm gì cả. Bỏ `const` đi thì mỗi lần rebuild bạn có một instance mới, nên framework buộc phải đi vào so từng field dù chẳng có gì đổi.

```dart
// Instance mới mỗi lần cha rebuild; phần diff đi vào subtree này.
Padding(
  padding: EdgeInsets.all(16),
  child: Text('Total'),
)

// Một instance cho cả vòng đời chương trình; phần diff dừng ở đây.
const Padding(
  padding: EdgeInsets.all(16),
  child: Text('Total'),
)
```

Hãy thành thật về độ lớn của cái lợi: với một `Padding` thì nó bằng không. Với một row trong list có mười lăm widget con tĩnh, rebuild cho từng row trong bốn mươi row đang hiển thị lúc fling, thì nó không bằng không. Và chi phí làm đúng bằng không, vì bạn có thể bắt analyzer làm hộ.

```yaml
# analysis_options.yaml
linter:
  rules:
    - prefer_const_constructors
    - prefer_const_constructors_in_immutables
    - prefer_const_literals_to_create_immutables
    - prefer_const_declarations
```

**Cách đo:** `flutter analyze` sẽ fail build khi bạn quên một `const`. Muốn thấy tác động chứ không chỉ thấy lint, đặt `debugPrintRebuildDirtyWidgets = true` trong `main()` rồi cuộn — mọi widget được rebuild đều được in ra. Những widget bạn nghĩ là bất động thì không nên xuất hiện trong log đó.

Thứ `const` *không* làm là ngăn việc paint. Widget const vẫn được vẽ lại khi layer chứa nó repaint. Đó là khoản mục thứ sáu.

## `setState` có bán kính ảnh hưởng; hãy làm nó nhỏ lại

`setState` đánh dấu toàn bộ `State` là bẩn. Nếu `State` đó là cả trang, thì một số nguyên thay đổi sẽ rebuild cả trang. Framework làm việc này rất nhanh, và đó chính là lý do không ai để ý — cho tới khi trang mọc thêm một biểu đồ và một danh sách.

Cách sửa không phải là tránh `setState`, mà là làm cho thứ đang rebuild nhỏ lại — hoặc tách phần thay đổi thành widget riêng nhỏ, hoặc rebuild từ một listenable ngay tại chỗ dùng.

```dart
class CartBar extends StatelessWidget {
  const CartBar({super.key, required this.itemCount});

  final ValueListenable<int> itemCount;

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<int>(
      valueListenable: itemCount,
      // `child` được build một lần và truyền vào mọi lượt gọi builder.
      child: const Icon(Icons.shopping_cart),
      builder: (context, count, child) {
        return Badge(label: Text('$count'), child: child!);
      },
    );
  }
}
```

Có hai thứ đang làm việc ở đó. `ValueListenableBuilder` giữ việc rebuild nằm gọn trong builder — mọi thứ phía trên nó trong cây không bị đụng tới. Còn tham số `child` truyền một subtree *xuyên qua* builder mà không rebuild nó — `AnimatedBuilder` và `ListenableBuilder` cũng có tham số này. `AnimatedBuilder` là chỗ nó quan trọng nhất, vì một animation rebuild sáu mươi hoặc một trăm hai mươi lần mỗi giây.

```dart
AnimatedBuilder(
  animation: controller,
  child: const ExpensiveStaticContent(),   // build một lần
  builder: (context, child) => Transform.rotate(
    angle: controller.value * math.pi,
    child: child,
  ),
)
```

Nếu bạn dùng `provider`, `Selector` là cùng ý tưởng áp lên model: nó chỉ rebuild khi giá trị bạn chọn ra từ model thật sự đổi, thay vì mỗi lần `notifyListeners()`.

```dart
Selector<CartModel, int>(
  selector: (_, cart) => cart.itemCount,
  builder: (context, count, child) => Badge(label: Text('$count'), child: child!),
  child: const Icon(Icons.shopping_cart),
)
```

**Cách đo:** lại là `debugPrintRebuildDirtyWidgets`, hoặc phần theo dõi rebuild trong DevTools. Kích hoạt thay đổi state đúng một lần rồi đọc danh sách những gì đã rebuild. Nếu trong đó có widget bạn không hề đụng tới, nghĩa là listener đang gắn quá cao.

## Lazy mặc định, và cái `Column` không hề lazy

Đây là lỗi xuất hiện trong mọi buổi review performance, và nó chỉ là lỗi một dòng:

```dart
// Build, layout và paint cả 400 row. Toàn bộ. Ngay lập tức.
SingleChildScrollView(
  child: Column(
    children: [for (final r in rows) RowTile(data: r)],
  ),
)
```

Một `Column` nằm trong scroll view nhận chiều cao không giới hạn, nên nó phải layout mọi child để biết mình cao bao nhiêu. Không có cơ chế cắt theo viewport nào cứu bạn, vì với `Column` thì mọi thứ đều đang trên màn hình. Bốn mươi row còn sống được; bốn trăm row là một cú khựng thấy rõ ở frame dựng nó.

`ListView.builder` đảo ngược điều này: nó build child theo nhu cầu khi chúng tiến gần viewport, và huỷ chúng khi rời đi. Thêm `itemExtent` còn đi xa hơn — khi sliver biết mọi child cao đúng 72 logical pixel, nó tính được index nào đang hiển thị bằng số học thay vì phải layout từng child để biết, và scrollbar cùng `jumpTo` trở nên chính xác.

```dart
ListView.builder(
  itemCount: rows.length,
  itemExtent: 72,                       // hoặc prototypeItem, nếu chiều cao được suy ra
  itemBuilder: (context, index) => RowTile(data: rows[index]),
)
```

Cái bẫy họ hàng là `shrinkWrap: true`. Nó tồn tại để list tự co theo nội dung — nghĩa là phải layout *toàn bộ* child của nó, đúng thứ lazy mà bạn muốn có. Nó ổn với sáu dòng settings và sai với một feed. Khi cần một header phía trên danh sách dài, dùng sliver thay vì lồng hai scrollable:

```dart
CustomScrollView(
  slivers: [
    const SliverToBoxAdapter(child: ProfileHeader()),
    SliverFixedExtentList(
      itemExtent: 72,
      delegate: SliverChildBuilderDelegate(
        (context, index) => RowTile(data: rows[index]),
        childCount: rows.length,
      ),
    ),
  ],
)
```

**Cách đo:** đếm số lần builder được gọi. Đặt đoạn này ở đầu `itemBuilder`, mở màn hình, và kiểm tra rằng số dòng in ra xấp xỉ số row đang hiển thị cộng phần cache extent, chứ không phải độ dài của cả list.

```dart
itemBuilder: (context, index) {
  assert(() {
    debugPrint('build row $index');
    return true;
  }());
  return RowTile(data: rows[index]);
}
```

Bọc trong `assert` nghĩa là toàn bộ đoạn đó bị loại khỏi release build.

## Ảnh tốn bốn byte mỗi pixel, ở đúng kích thước bạn để nó decode

Một ảnh đã decode nằm trong bộ nhớ dưới dạng pixel thô, mỗi pixel bốn byte. Một tấm 4032 × 3024 từ camera điện thoại có khoảng 12.2 triệu pixel, tức chừng 48 MB sau khi decode — và nó tốn từng đó dù bạn hiển thị full màn hình hay trong avatar 96 px, vì mặc định là decode ở đúng độ phân giải gốc.

`ImageCache` của Flutter giữ ảnh đã decode, mặc định tối đa 1000 entry hoặc 100 MiB. Nhồi vào đó toàn ảnh chưa resize thì bạn sẽ liên tục evict rồi decode lại. Việc decode chạy ngoài UI thread, nhưng vòng xoay evict, áp lực cấp phát và lần GC kéo theo thì không.

`cacheWidth` và `cacheHeight` báo cho bộ decode biết kích thước đích. Chúng tính theo *device* pixel chứ không phải logical pixel, nên hãy nhân với device pixel ratio:

```dart
final dpr = MediaQuery.devicePixelRatioOf(context);

Image.network(
  avatarUrl,
  width: 96,
  height: 96,
  cacheWidth: (96 * dpr).round(),
)
```

Với một `ImageProvider` mà bạn truyền qua lại thay vì một widget `Image`, `ResizeImage` là cùng cơ chế đó dưới dạng lớp bọc provider:

```dart
Image(image: ResizeImage(AssetImage('assets/hero.png'), width: 640))
```

Nếu app của bạn nặng ảnh và chạy trên máy ít RAM, việc thu nhỏ chính cái cache cũng hợp lý, để một loạt ảnh lớn không chiếm trọn 100 MiB:

```dart
PaintingBinding.instance.imageCache.maximumSizeBytes = 50 << 20; // 50 MiB
```

**Cách đo:** đặt `debugInvertOversizedImages = true` (từ `package:flutter/painting.dart`). Ảnh nào decode lớn hơn đáng kể so với kích thước được vẽ ra sẽ hiển thị lộn ngược kèm log chi tiết. Không thể bỏ sót — đó chính là mục đích. DevTools cũng phơi cờ này thành một toggle trong Inspector.

## `saveLayer` là khoản chi bạn trả một cách vô tình

Phần lớn việc vẽ trong Flutter đi thẳng vào layer hiện tại. Một số hiệu ứng thì không thể: chúng cần subtree được render ra một buffer offscreen trước, rồi composite ngược lại. Đó là `saveLayer`, và nó kéo theo một lần cấp phát render target, một lượt vẽ thêm và một lần upload texture — mỗi frame, trên raster thread. Một cái trong màn hình tĩnh thì chẳng sao. Một cái nằm trong row của list là một cái cho mỗi row đang hiển thị, mỗi frame, suốt cú fling.

Những widget hay kích hoạt nó: `Opacity` phủ lên một subtree, `ShaderMask`, `ColorFilter`, `BackdropFilter`, `Text` có shader làm mờ phần tràn, và bất kỳ clip nào đặt `Clip.antiAliasWithSaveLayer` — mức mà chính tài liệu của enum đánh dấu là đắt nhất.

Các lựa chọn thay thế thường là cụ thể hơn, chứ không phải khôn ngoan hơn:

| Thay vì | Dùng | Vì sao |
|---|---|---|
| `Opacity` phủ màu đặc | alpha của chính màu đó | vẽ trong cùng một layer |
| `Opacity` phủ ảnh | `Image(color: …, colorBlendMode: BlendMode.modulate)` | phép blend nằm trong lượt vẽ ảnh |
| `ClipRRect` bọc hộp màu | `DecoratedBox` với `borderRadius` | painter tự bo góc |
| `ClipRRect` bọc ảnh | `BoxDecoration(image: DecorationImage(…), borderRadius: …)` | tương tự, clip ngay trong lượt vẽ |
| `Clip.antiAliasWithSaveLayer` | `Clip.antiAlias`, hoặc `Clip.hardEdge` | chỉ dạng đầu mới bắt buộc lượt offscreen |

Hai chi tiết đáng biết. `Opacity` với giá trị đúng bằng `0.0` hoặc `1.0` không composite gì cả — render object cắt ngắn đường đi — nên một animation opacity chỉ đắt ở khoảng giữa. Và `ClipRRect` mặc định là `Clip.antiAlias`, vốn không phải dạng saveLayer; bạn phải chỉ định `antiAliasWithSaveLayer` một cách rõ ràng, nên nếu thấy nó trong codebase thì nhiều khả năng ai đó dán vào để chữa một vệt răng cưa ở viền.

**Cách đo:** bật ô caro lên.

```dart
MaterialApp(
  checkerboardOffscreenLayers: true,     // các lượt saveLayer
  checkerboardRasterCacheImages: true,   // các layer đã cache
  home: const HomePage(),
)
```

Mọi vùng được render ra buffer offscreen sẽ bị phủ hoa văn ô caro. Cuộn list của bạn. Nếu các row bị caro, bạn đang có một lượt offscreen cho mỗi row, và đó là nơi những mili-giây raster của bạn đi mất.

## `RepaintBoundary` là một sự đánh đổi, không phải món quà miễn phí

Khi một render object cần vẽ lại, nó gọi `markNeedsPaint`, và lời gọi đó đi ngược lên cây cho tới khi gặp một repaint boundary. Mọi thứ nằm dưới boundary đó sẽ repaint. Nên trên màn hình có một cái playhead nhỏ chạy trên nền biểu đồ tĩnh nặng nề, biểu đồ cũng repaint theo — sáu mươi lần mỗi giây, một cách vô ích.

`RepaintBoundary` chặn đường đi ngược đó. Subtree của nó có layer riêng và repaint độc lập với các widget anh em.

```dart
Stack(
  children: [
    const ExpensiveStaticChart(),
    RepaintBoundary(
      child: Playhead(position: position),   // repaint một mình
    ),
  ],
)
```

Sự đánh đổi là có thật: mỗi boundary là thêm một layer, thêm một bề mặt phải cấp phát và composite. Rắc nó khắp nơi chỉ dời chi phí từ repaint sang composite và có thể làm mọi thứ tệ hơn. Nó cũng lặp lại việc bạn đã có sẵn — `ListView` và họ hàng đã tự bọc mỗi child trong một `RepaintBoundary` theo mặc định (`addRepaintBoundaries: true`), nên tự thêm quanh item của list chẳng được gì.

Quy tắc tôi dùng: thêm boundary khi bạn gọi tên được hai thứ mà nó tách ra — *cái này* chuyển động, *cái kia* nặng và tĩnh — còn không thì xoá đi.

**Cách đo:** `debugRepaintRainbowEnabled = true` vẽ một viền đổi màu quanh mỗi layer mỗi lần nó repaint. Viền đổi màu nghĩa là layer đó repaint ở frame đó. Hãy nhìn xem vùng nào nhấp nháy trong khi chỉ có một thứ đang chuyển động.

Với một boundary cụ thể, `RenderRepaintBoundary` giữ bộ đếm số lần nó vẽ cùng widget cha so với số lần vẽ độc lập, và phần diagnostics của nó in ra một nhận định bằng tiếng Anh dễ hiểu về việc boundary có đáng giá hay không:

```dart
final box = boundaryKey.currentContext!.findRenderObject()! as RenderRepaintBoundary;
debugPrint(box.toStringDeep());   // chỉ chạy trong debug build
```

## Bắt ngân sách làm fail build, thay vì dựa vào trí nhớ

Quy tắc phải nhớ là quy tắc bạn sẽ ngừng áp dụng vào tháng thứ ba. Có hai cơ chế biến ngân sách này thành thứ tự động.

Thứ nhất là một cảnh báo lúc chạy. `SchedulerBinding.addTimingsCallback` đưa cho bạn một `FrameTiming` cho mỗi frame đã hoàn tất, tách riêng thời gian build trên UI thread và thời gian raster:

```dart
import 'package:flutter/scheduler.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  assert(() {
    SchedulerBinding.instance.addTimingsCallback((timings) {
      for (final t in timings) {
        final build = t.buildDuration.inMicroseconds / 1000;
        final raster = t.rasterDuration.inMicroseconds / 1000;
        if (build > 8 || raster > 8) {
          debugPrint('over budget — build ${build}ms, raster ${raster}ms');
        }
      }
    });
    return true;
  }());
  runApp(const MyApp());
}
```

`assert` giữ nó ngoài release build. Trong debug, con số tuyệt đối bị thổi phồng — debug build không được biên dịch như release — nên hãy coi đây là một chuông báo *tương đối* và xác nhận lại bất cứ thứ gì nó bắt được ở chế độ profile.

Thứ hai là CI. Package `integration_test` và `flutter_driver` có thể ghi lại timeline cho một thao tác được viết sẵn rồi tóm tắt nó, kèm số frame đã vượt ngân sách:

```dart
final timeline = await driver.traceAction(() async {
  await driver.scroll(listFinder, 0, -3000, const Duration(seconds: 2));
});

final summary = TimelineSummary.summarize(timeline);
await summary.writeTimelineToFile('scroll_perf', pretty: true);

expect(summary.computeMissedFrameBuildBudgetCount(), 0);
```

`computeMissedFrameBuildBudgetCount` mặc định lấy ngân sách 16 ms; nó nhận một `Duration` tuỳ chọn nếu bạn đang theo dòng 120 Hz. `computeMissedFrameRasterizerBudgetCount` là bản song sinh cho raster thread, và có các hàm tính percentile để bạn assert trên p90 thay vì trên trung bình — vốn mới là thứ đáng assert, vì jank là vấn đề của phần đuôi phân phối.

Hãy chạy những bài này trên máy thật ở chế độ profile (`flutter drive --profile`). Số liệu từ simulator hay từ debug build gần như không nói gì về performance khi phát hành.

Khi có thứ gì đó thật sự vượt ngân sách, đó mới là lúc bạn mở tab Performance của DevTools, nhìn biểu đồ frame, và tìm ra thread nào cùng giai đoạn nào — nhưng ý nghĩa của cả ngân sách này là để chuyến đi đó hiếm và có mục tiêu, chứ không phải thành cách bạn phát triển hằng ngày.

## FAQ

**`const` thật sự tạo khác biệt đo được, hay chỉ là làm theo phong trào?**

Cả hai, tuỳ chỗ. Cơ chế thì có thật và rất cụ thể: một widget const là cùng một object qua mọi lần rebuild, nên phần diff element cắt ngắn thay vì đi vào subtree. Việc nó có đo được hay không phụ thuộc subtree đó bị rebuild thường xuyên đến đâu — không cảm nhận được ở màn hình settings, nhưng đáng kể với các row bị rebuild suốt cú fling. Vì các lint khiến việc áp dụng ở mọi nơi là miễn phí, bạn không cần đoán đúng chỗ nào mới đáng.

**Tôi có nên bọc mọi item của list trong `RepaintBoundary` không?**

Không, và `ListView` đã làm hộ bạn rồi — `addRepaintBoundaries` mặc định là true. Tự thêm chỉ cho bạn một layer thừa. Boundary xứng đáng ở chỗ có một vùng nhỏ đang chuyển động nằm trên nội dung tĩnh và nặng, hoặc ngược lại, và bạn nên gọi tên được cả hai nửa trước khi thêm.

**UI thread của tôi ổn nhưng raster thread vượt ngân sách. Nguyên nhân thường gặp là gì?**

Các lượt offscreen và overdraw. Tìm `saveLayer` trước — `Opacity` phủ subtree, `ShaderMask`, `BackdropFilter`, `Clip.antiAliasWithSaveLayer` — dùng `checkerboardOffscreenLayers` để phát hiện, nhất là trên nội dung đang cuộn, nơi chi phí nhân lên theo số item hiển thị. Ảnh lớn được composite ở nguyên độ phân giải và các lớp trong suốt chồng sâu là nơi tiếp theo nên nhìn tới.

**8 ms mỗi thread có quá khắt khe không?**

Đó là mục tiêu có khoảng dư, không phải yêu cầu cứng — yêu cầu cứng là mỗi thread phải nằm dưới toàn bộ ngân sách frame. Nhắm một nửa là chỗ hợp lý vì frame thật không "trung bình": một chuyển route, một ảnh decode xong và một lần thu gom rác có thể rơi cùng lúc, và nếu trạng thái bình thường của bạn đã ở 15 ms thì chẳng còn gì để hấp thụ chúng.

**Những quy tắc này có đổi với Impeller không?**

Backend render đổi mô hình chi phí ở phía raster — rõ nhất là loại bỏ các cú khựng do biên dịch shader lần đầu mà Skia từng gặp. Nó không đổi gì ở các quy tắc phía UI thread: phạm vi rebuild, tính lazy của list và kích thước decode ảnh đều ở mức framework và không phụ thuộc backend. Các lượt offscreen vẫn là thao tác thường ngày đắt nhất của raster thread.

---

*Sáu khoản mục và các cơ chế đằng sau chúng là hành vi đã được ghi trong tài liệu Flutter; riêng con số 8 ms cho mỗi thread là quy ước của tôi và bạn nên tự đặt mức của mình. Bất cứ thứ gì phụ thuộc phiên bản — kích thước cache mặc định, tên lint, vị trí các toggle trong DevTools — hãy đối chiếu với tài liệu của đúng phiên bản Flutter bạn đang dùng.*
