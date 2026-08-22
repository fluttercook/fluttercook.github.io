---
title: "Impeller và một frame bị giật: tìm xem 16ms đã trôi đi đâu"
description: "Impeller đã là renderer mặc định, xoá sổ luôn nhóm jank do biên dịch shader và làm phần lớn lời khuyên warmup cũ trở nên vô nghĩa. Bài này nói về phần còn lại: profile mode, sự khác nhau giữa UI thread và raster thread, và năm nguyên nhân thật sự làm vỡ frame budget — mỗi cái kèm một cách sửa."
seoDescription: "Chẩn đoán jank trong Flutter với Impeller: profile mode, DevTools Performance view, UI vs raster thread, cách sửa build, layout, saveLayer và decode ảnh."
keywords:
  - flutter bị giật lag
  - impeller hiệu năng flutter
  - devtools performance flutter
  - raster thread và ui thread flutter
  - savelayer flutter tốn kém
  - frame budget 16ms flutter
category: "Chuyên sâu"
topic: "Hiệu năng"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧩"
tags: ["Flutter", "Impeller", "Hiệu năng", "DevTools", "Profiling"]
sources:
  - name: "Impeller rendering engine — tài liệu Flutter"
    url: "https://docs.flutter.dev/perf/impeller"
  - name: "Flutter performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
  - name: "Use the Performance view — DevTools"
    url: "https://docs.flutter.dev/tools/devtools/performance"
  - name: "Improving rendering performance"
    url: "https://docs.flutter.dev/perf/rendering-performance"
  - name: "Canvas.saveLayer — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/Canvas/saveLayer.html"
  - name: "Clip enum — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/Clip.html"
  - name: "FrameTiming — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/FrameTiming-class.html"
  - name: "ResizeImage — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/painting/ResizeImage-class.html"
  - name: "flutter/flutter#114853 — bỏ --trace-skia, thay bằng --trace-graphics"
    url: "https://github.com/flutter/flutter/issues/114853"
  - name: "flutter/flutter#140310 — cache-sksl không dùng được với Impeller"
    url: "https://github.com/flutter/flutter/issues/140310"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
draft: false
---

Tester báo bug: "danh sách sản phẩm bị giật khi cuộn nhanh trên máy Pixel". Bạn tìm *flutter jank*, ba kết quả đầu tiên đều bảo chạy `flutter run --profile --cache-sksl`, lấy file SkSL rồi nhét vào bản release. Bạn làm theo. Cái flag đó không còn, hoặc bị bỏ qua, và chỗ giật vẫn nguyên vẹn.

Lời khuyên đó đúng — với Skia. Nó không đúng với app của bạn, vì app của bạn gần như chắc chắn đang render bằng Impeller, và Impeller không hề biên dịch shader lúc runtime. Tài liệu Flutter nói thẳng: Impeller "precompiles a smaller, simpler set of shaders at engine-build time so they don't compile at runtime". Không có gì để warm up cả. Quy trình `--cache-sksl` và `--bundle-sksl-path` là cơ chế riêng của Skia, và [issue #140310](https://github.com/flutter/flutter/issues/140310) tồn tại chính vì có quá nhiều người cố dùng nó với Impeller.

Vậy là cả một nhóm nguyên nhân gây jank đã biến mất. Các nhóm còn lại thì không. Một `build()` đi parse JSON vẫn chậm. Một `IntrinsicHeight` bọc quanh `Row` lớn vẫn là thêm một lượt layout. `Canvas.saveLayer` vẫn là, theo đúng chữ của tài liệu, "one of the most expensive methods in the Flutter framework". Một tấm ảnh 4032×3024 vẽ vào cái avatar 96 pixel vẫn là ý tưởng tệ. Impeller thay đổi *bạn đang gặp vấn đề nào*, chứ không phải *bạn có gặp vấn đề hay không*.

Đây là đường chẩn đoán cho những cái còn lại: lấy một phép đo tái lập được, xác định thread nào chạy lâu, rồi thu hẹp xuống tên một widget cụ thể. Sau bước đó thì mọi thứ chỉ còn là thao tác máy móc.

## Impeller lấy đi cái gì, và để lại cái gì

Mục tiêu thiết kế Impeller tự tuyên bố là chi phí có thể dự đoán được. Trích tài liệu: "Impeller compiles all shaders and reflection offline at build time. It builds all pipeline state objects upfront. The engine controls caching and caches explicitly." Chính câu đó khai tử kiểu giật ở lần chạy đầu của một animation — lần đầu user mở trang có blur hoặc gradient, frame mất 200ms vì driver GPU đang biên dịch chương trình shader.

Nó chạy ở đâu, theo tài liệu hiện tại:

| Nền tảng | Renderer | Ghi chú |
| --- | --- | --- |
| iOS | Chỉ Impeller | Tài liệu ghi "no ability to switch to Skia" |
| Android API 29+ | Impeller, mặc định | Mặc định cho iOS và Android API 29+ từ Flutter 3.27 |
| Android cũ / không Vulkan | Tự động fallback | Tài liệu: "Impeller falls back to the legacy OpenGL renderer" |
| macOS, Linux, Windows | Impeller, mặc định | "as of Flutter 3.47" |
| Web | Skia | "It might use Impeller in the future" |

Hai hệ quả thực tế. Thứ nhất, nếu bạn vẫn thấy marker **Shader compilation** trong frames chart của DevTools thì bạn không đi đường Impeller — kiểm tra lại dòng nền tảng ở bảng trên, và xem có chỗ nào trong build đang truyền `--no-enable-impeller` hoặc đặt `io.flutter.embedding.android.EnableImpeller` thành `false` trong manifest không. Thứ hai, `--trace-skia` là flag của Skia. Với Impeller nó sẽ không cho bạn bảng phân tích draw-op của Skia như ảnh chụp màn hình trong các bài blog cũ; [issue #114853](https://github.com/flutter/flutter/issues/114853) đề xuất một flag `--trace-graphics` không phụ thuộc renderer để thay thế. Impeller vẫn phát ra timeline event trên raster thread, nên tab Timeline events vẫn dùng được — chỉ là cái flag kia không còn là đòn bẩy như xưa.

## Một frame là một pipeline, và jank là câu hỏi giai đoạn nào chạy lâu

"16ms" là ngân sách cho cả pipeline, không phải cho một hàm. Ở 60Hz bạn có 16,67ms mỗi frame; trên màn 120Hz thì chỉ còn 8,33ms — đó là lý do một bug report từ người dùng máy màn hình tần số cao có thể mô tả một chỗ giật mà bạn không hề thấy trên máy mình.

Hai thread chia nhau ngân sách đó, và tài liệu định nghĩa rất rõ. **UI thread** "executes Dart code in the Dart VM… When your app creates and displays a scene, the UI thread creates a *layer tree*, a lightweight object containing device-agnostic painting commands, and sends the layer tree to the raster thread." **Raster thread** "takes the layer tree and displays it by talking to the GPU." Impeller chạy trên raster thread. Chú ý một lưu ý ngay trong tài liệu: "while the raster thread rasterizes for the GPU, the thread itself runs on the CPU" — raster thread chậm không tự động có nghĩa là vấn đề nằm ở GPU.

Bạn có thể đọc hai con số đó bằng code, và nên gắn nó vào trước cả khi mở DevTools, vì nó cho biết ngay bạn đang săn một vấn đề Dart hay một vấn đề vẽ:

```dart
import 'package:flutter/scheduler.dart';
import 'package:flutter/widgets.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SchedulerBinding.instance.addTimingsCallback((List<FrameTiming> timings) {
    for (final t in timings) {
      if (t.totalSpan > const Duration(milliseconds: 16)) {
        debugPrint('frame ${t.frameNumber} '
            'build=${t.buildDuration.inMicroseconds}us '
            'raster=${t.rasterDuration.inMicroseconds}us '
            'total=${t.totalSpan.inMicroseconds}us');
      }
    }
  });
  runApp(const MyApp());
}
```

`buildDuration` là "the duration to build the frame on the UI thread"; `rasterDuration` là "the duration to rasterize the frame on the raster thread"; `totalSpan` là toàn bộ khoảng từ vsync tới lúc raster xong. `FrameTiming` còn có `layerCacheBytes` và `pictureCacheBytes`, hai thứ sẽ có ích ở phần nói về ảnh.

## Profile mode, trên máy thật, trước khi tin bất kỳ con số nào

Số đo ở debug mode vô nghĩa với việc này. Bản debug chạy Dart bằng JIT với assertion bật và không tối ưu, bản thân framework cũng làm thêm việc — kiểm tra tính toàn vẹn của tree, in paint bounds, đủ thứ. Một widget mất 9ms ở debug có thể chỉ mất dưới 1ms ở profile.

```bash
flutter devices
flutter run --profile -d <device-id>
```

Profile mode không phục vụ được mục đích của bạn trên simulator hay emulator — bạn cần đúng GPU thật và đúng hành vi nhiệt của chiếc máy mà bug được báo trên đó. Sau đó, từ terminal đang chạy, bấm `P` để bật tắt performance overlay, hoặc mở URL DevTools mà `flutter run` in ra rồi vào view **Performance**.

Đọc overlay đúng như tài liệu mô tả: hai biểu đồ của 300 frame gần nhất, các vạch trắng cách nhau 16ms, và thanh đỏ ở những frame vượt ngân sách. Đỏ ở biểu đồ UI nghĩa là code Dart của bạn quá đắt. Đỏ ở biểu đồ raster nghĩa là scene quá phức tạp để vẽ. Đó là hai giây phân loại, và thường đủ để chọn xem đọc mục nào trong ba mục tiếp theo. Một flag nữa vẫn đáng biết: `--trace-systrace` đẩy timeline event sang trình trace của chính nền tảng (systrace trên Android, os_signpost trên iOS). Đây là thứ bạn cần khi nghi ngờ chỗ giật xảy ra hoàn toàn bên ngoài phía Dart — ví dụ một plugin đang làm việc blocking trên platform thread.

## Bật loại tracing gọi được đúng tên widget

Frames chart cho biết một frame chậm. Tab **Frame analysis** cho biết vì sao, bằng chữ: chọn một frame bị jank và DevTools hiện gợi ý về những thao tác đắt đỏ mà nó phát hiện trong frame đó. Bắt đầu từ đây — miễn phí và thường là đúng.

Khi chừng đó chưa đủ, dùng **Enhance tracing**, cái dropdown trong Performance view. Nó có ba công tắc:

- **Track widget builds** — mỗi `build()` trở thành một timeline event có nhãn là tên widget.
- **Track layouts** — mỗi lượt layout của render object thành một event.
- **Track paints** — mỗi lượt paint của render object thành một event.

Bật lên, tab Timeline events thôi ghi "Build" mà bắt đầu ghi "ProductCard.build" lồng trong "ProductList.build", kèm thời lượng. Đó là lúc việc điều tra trở nên tầm thường.

Hai lưu ý. Mấy công tắc này thêm chi phí đo đạc thật, nên con số tuyệt đối sẽ xấu đi trong lúc bật — hãy dùng chúng để tìm ra *cái tên*, rồi tắt đi và đo lại để xác nhận bản sửa. Và phạm vi của chúng là trong frame; với một đoạn code của riêng bạn trải qua nhiều frame, hãy tự gắn mốc:

```dart
import 'dart:developer' as developer;

developer.Timeline.timeSync('decodePriceHistory', () {
  history = PriceHistory.fromJson(payload);
});
```

Event đó xuất hiện trên UI thread trong tab Timeline events với thanh riêng, nằm cạnh các event của framework.

## Jank ở UI thread: build làm quá nhiều việc, layout đo hai lần

Khi **Track widget builds** đã chỉ ra một widget, chuyện chỉ còn vài dạng.

**Một build có làm việc.** Parse, sort, format, regex, khởi tạo `DateFormat` — bất cứ thứ gì không phải là "mô tả UI" — nằm trong `build()`. Nó chạy mỗi lần rebuild, và trong một animation thì đó là mỗi frame. Cách sửa không có gì thông minh: đẩy lên `initState`, một field đã memoise, hoặc một lời gọi `compute()` chạy trên isolate, rồi để `build()` chỉ đọc kết quả.

**Phạm vi rebuild quá rộng.** Một `setState` ở đầu trang sẽ rebuild cả trang. Nếu thứ thay đổi chỉ là một con số ở góc, hãy bọc riêng cái góc đó. `AnimatedBuilder` và `AnimatedWidget` nhận một `child` được build một lần và truyền qua builder mà không đụng vào:

```dart
AnimatedBuilder(
  animation: _controller,
  child: const ExpensiveProductCard(),   // built once, not per frame
  builder: (context, child) => Transform.rotate(
    angle: _controller.value * math.pi,
    child: child,
  ),
)
```

Constructor `const` làm đúng việc đó theo kiểu tĩnh: một widget `const` được canonicalise, nên framework có thể bỏ qua cả nhánh con của nó khi rebuild thay vì đi so sánh.

**Một layout đo cây hai lần.** `IntrinsicHeight` và `IntrinsicWidth` hỏi kích thước nội tại của từng con trước khi có thể layout bất cứ thứ gì — thêm một lượt duyệt nhánh con, mỗi frame. Tài liệu API của chính framework gọi nhóm widget intrinsic là tương đối đắt và khuyên tránh dùng khi có thể. Nếu bạn dùng `IntrinsicHeight` chỉ để hai card trong một `Row` cao bằng nhau, thì một `SizedBox` với chiều cao đã biết, hoặc `CrossAxisAlignment.stretch` bên trong một parent có ràng buộc, làm được việc đó với một lượt.

Danh sách dài có cách sửa tương ứng. Một `ListView.builder` mà các item cao bằng nhau thì nên khai báo ra, vì khi đó bộ máy cuộn tính được offset bằng số học thay vì phải layout từng con để biết chúng nằm đâu:

```dart
ListView.builder(
  itemExtent: 72,
  itemCount: items.length,
  itemBuilder: (context, i) => RowTile(item: items[i]),
)
```

Dùng `prototypeItem` nếu chiều cao đồng nhất nhưng bạn không muốn hardcode. Và `shrinkWrap: true` trên một list nằm trong một scrollable khác là chi phí layout tự chuốc vào người phổ biến nhất trong Flutter — nó buộc list layout toàn bộ con để tự đo mình, phá sạch ý nghĩa của `.builder`.

## Jank ở raster thread: saveLayer vẫn là lời gọi đắt nhất trong framework

Nếu màu đỏ nằm ở biểu đồ raster thì layer tree đang đắt để vẽ. Nguyên nhân áp đảo, với Impeller cũng như với Skia, là một lượt render offscreen: engine vẽ một nhánh con vào một texture riêng rồi composite texture đó ngược lại. Việc này tốn thêm một pass và rất nhiều băng thông bộ nhớ, và đó chính xác là những gì `Canvas.saveLayer` làm.

Bạn hiếm khi tự gọi nó. Tài liệu nói rõ: "even if you don't call `saveLayer` explicitly, implicit calls might happen on your behalf, for example when specifying `Clip.antiAliasWithSaveLayer` (typically as a `clipBehavior`)". `Opacity` bọc cả nhóm, `ShaderMask`, `BackdropFilter` và `ColorFiltered` là những nghi phạm quen mặt còn lại.

DevTools có sẵn một công cụ chia đôi cho việc này mà hầu như không ai đụng tới. Trong **More debugging options** có các công tắc để tắt hẳn từng loại layer: **Render Clip layers**, **Render Opacity layers**, **Render Physical Shape layers**. Tắt một cái, ghi lại, rồi nhìn thanh raster. Nếu tắt opacity layer làm chỗ giật biến mất thì bạn có câu trả lời trong khoảng ba mươi giây, không cần đọc một timeline event nào.

Các cách sửa đều cùng một ý — gộp hiệu ứng vào chính lệnh vẽ thay vì bọc cả một nhánh con trong nó.

```dart
// Offscreen pass: the subtree is drawn to a texture, then composited.
Opacity(opacity: 0.4, child: Image.asset('assets/hero.jpg'))

// No offscreen pass: alpha is folded into the image's own paint.
Image.asset('assets/hero.jpg', opacity: _fade)   // Animation<double>
```

```dart
// A clip layer, plus a full offscreen pass because of the clipBehavior.
ClipRRect(
  borderRadius: BorderRadius.circular(16),
  clipBehavior: Clip.antiAliasWithSaveLayer,
  child: ColoredBox(color: Colors.indigo, child: child),
)

// The same rounded rectangle, drawn directly. No clip, no layer.
DecoratedBox(
  decoration: BoxDecoration(
    color: Colors.indigo,
    borderRadius: BorderRadius.circular(16),
  ),
  child: child,
)
```

Nguyên tắc chung mà tài liệu đưa ra là áp opacity, clip và shadow lên từng widget riêng lẻ thay vì lên cả một nhóm ở trên cao trong cây, và tự hỏi liệu có thật sự cần hiệu ứng đó không. `Clip.antiAlias` — giá trị `clipBehavior` mặc định của phần lớn widget — rẻ hơn hẳn `Clip.antiAliasWithSaveLayer`; nếu có ai đó đổi sang biến thể `WithSaveLayer` để chữa một đường viền mảnh bị hở, hãy kiểm tra xem đường hở đó còn không.

`RepaintBoundary` là công cụ còn lại: nó cô lập một nhánh con để việc repaint nhánh đó không kéo theo hàng xóm, và cho phép raster cache giữ lại kết quả. Nhưng mỗi boundary tốn bộ nhớ GPU. Cách diễn đạt của tài liệu là chuẩn — chỉ cache "only where absolutely necessary". Bọc `RepaintBoundary` quanh từng item của list là một bug về bộ nhớ đang khoác áo bản vá hiệu năng.

## Ảnh bị decode ở sai kích thước

Nguyên nhân phổ biến cuối cùng là một tấm ảnh có kích thước decode chẳng liên quan gì tới kích thước hiển thị. Flutter decode ảnh ngoài UI thread, nên chuyện này ít khi hiện ra thành một thanh UI cao; nó hiện ra thành một cú nhảy ở đúng frame ảnh xuất hiện lần đầu, thành áp lực bộ nhớ gây GC pause về sau, và thành việc raster thread phải lấy mẫu một texture lớn hơn nhiều so với cái khung nó đang vẽ vào.

Cách sửa là decode đúng kích thước hiển thị. Cả hai dạng đều một dòng:

```dart
// Decode at 320 logical pixels wide instead of whatever the server sent.
Image.network(url, cacheWidth: 320)

// Same thing when you are holding an ImageProvider.
ResizeImage(NetworkImage(url), width: 320)
```

`cacheWidth` và `cacheHeight` kiểu `int?` và, theo tài liệu, "indicate to the engine that the image should be decoded at the specified size", chủ yếu để giảm bộ nhớ của `ImageCache`. Lưu ý chúng bị bỏ qua trên web, nơi việc decode được giao cho trình duyệt.

Với một ảnh hero mà bạn biết chắc sắp cần — trang kế tiếp trong luồng, card đầu tiên của carousel — hãy đẩy việc decode ra khỏi cái frame cần nó:

```dart
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(const AssetImage('assets/hero.jpg'), context);
}
```

Nếu bạn nghi vấn đề nằm ở image cache chứ không ở một tấm ảnh cụ thể nào, `FrameTiming.layerCacheBytes` và `pictureCacheBytes` trong callback ở trên sẽ cho thấy cache phình lên qua từng frame, và `PaintingBinding.instance.imageCache.maximumSizeBytes` cho bạn đặt trần.

## FAQ

**Impeller đã là mặc định rồi — còn cần profile nữa không?**

Có. Impeller xoá nhóm jank do biên dịch shader, đúng cái nhóm mà bạn không thể sửa từ phía Dart. Build đắt đỏ, thêm lượt layout, `saveLayer`, và ảnh decode quá khổ vẫn là việc của bạn, và tất cả đều nhìn thấy được trong đúng cái DevTools view của năm năm trước.

**Vì sao `--trace-skia` không còn cho thông tin gì hữu ích?**

Vì nó là flag của Skia còn app của bạn đang vẽ bằng Impeller. Impeller vẫn phát timeline event trên raster thread nên tab Timeline events vẫn chạy; bạn chỉ không có bảng phân tích draw-op của Skia mà flag đó sinh ra để phục vụ. Có một đề xuất đang mở, [flutter/flutter#114853](https://github.com/flutter/flutter/issues/114853), cho một flag `--trace-graphics` không phụ thuộc renderer.

**Chỗ giật chỉ xảy ra trên đúng một máy Android. Bắt đầu từ đâu?**

Kiểm tra xem máy đó có đi đường Vulkan không. Tài liệu nói Impeller fallback về renderer OpenGL cũ trên Android dưới API 29 hoặc trên máy không hỗ trợ Vulkan, và đường fallback không có cùng đặc tính. Tái hiện bằng `flutter run --profile` trên đúng máy đó, và ghi cả tên chip vào issue nếu bạn báo lỗi — tài liệu Impeller yêu cầu rõ thông tin thiết bị và chip.

**Có nên rải `RepaintBoundary` khắp nơi cho chắc?**

Không. Mỗi boundary là một layer riêng với chi phí bộ nhớ GPU riêng, và các entry raster cache mà tài liệu mô tả là "expensive to construct". Chỉ thêm một cái ở chỗ có nhánh con nhỏ animate độc lập với phần tĩnh lớn — một spinner nằm trên một trang phức tạp — rồi đo thanh raster trước và sau. Nếu con số không nhúc nhích, gỡ ra.

**Những thứ này có áp dụng cho Flutter web không?**

Một phần. Nửa thuộc UI thread thì có: build, layout và phạm vi rebuild hành xử y hệt. Nửa thuộc render thì không — web vẫn render bằng Skia chứ không phải Impeller, `cacheWidth`/`cacheHeight` bị bỏ qua vì việc decode giao cho trình duyệt, và DevTools không attach được ở profile mode trên web nên bạn phải dùng Chrome DevTools.

---

*Mọi điều ở trên về renderer mặc định, flag, định nghĩa thread và hành vi API đều lấy từ tài liệu Flutter chính thức đã liệt kê trong phần nguồn; còn thứ tự chẩn đoán — đo, tách theo thread, rồi gọi tên widget — là thói quen làm việc của tôi chứ không phải một quy trình có trong tài liệu. Renderer mặc định và độ khả dụng của các flag thay đổi giữa các bản phát hành, nên hãy đối chiếu `docs.flutter.dev/perf/impeller` với phiên bản trong `pubspec.lock` của bạn trước khi kết luận thứ gì đó đang bật hay tắt.*
