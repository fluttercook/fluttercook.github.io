---
title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
description: "Một PM của Google dựng game tic-tac-toe 3D bằng Flutter rồi công khai toàn bộ prompt. Tôi đối chiếu timestamp với lịch sử commit — và dùng chính repo đó làm bài giới thiệu Flutter: widget, Dart, hot reload, Impeller, và bốn cái bug cho thấy vì sao vẫn phải hiểu framework."
seoDescription: "Giới thiệu Flutter 2026 cho người mới: Flutter là gì, widget, Dart 3.13, hot reload, Impeller, flutter_scene, material_ui và cupertino_ui tách khỏi SDK, cài đặt từ đầu, và bài học thật từ một game 3D dựng bằng AI trong 15 phút."
keywords:
  - flutter là gì
  - học flutter từ đầu
  - flutter cho người mới bắt đầu
  - widget trong flutter
  - hot reload flutter
  - dart là gì
  - flutter_scene 3d
  - flutter 3.47
category: "Hướng dẫn"
topic: "Flutter"
level: "Cơ bản"
author: "Trung Hiếu"
publishDate: "2026-08-21"
emoji: "🐦"
tags: ["Flutter", "Dart", "Người mới", "Impeller", "3D", "AI"]
sources:
  - name: "Abdallah Shaban trên X — game dựng bằng flutter_scene"
    url: "https://x.com/AbdallahSh07/status/2090475954053513515"
  - name: "Repo flutter_scene_tic_tac_toe — toàn bộ prompt log"
    url: "https://github.com/abdallahshaban557/flutter_scene_tic_tac_toe/blob/main/PROMPTS.md"
  - name: "flutter_scene trên pub.dev"
    url: "https://pub.dev/packages/flutter_scene"
  - name: "Flutter Scene — hướng dẫn cài đặt"
    url: "https://fscene.dev/getting-started/installation/"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter 3.47.0 release notes"
    url: "https://docs.flutter.dev/release/release-notes/release-notes-3.47.0"
  - name: "Google Antigravity"
    url: "https://antigravity.google/"
  - name: "Gemini 3.7 Flash trong Antigravity"
    url: "https://antigravity.google/blog/gemini-3-7-flash-in-google-antigravity"
  - name: "Cài đặt Flutter — tài liệu chính thức"
    url: "https://docs.flutter.dev/get-started/install"
related:
  - slug: "web-tech-to-mobile-app-2026"
    title: "Dùng công nghệ web để làm app mobile: bản đồ kỹ thuật 2026"
draft: false
---

Ngày 20/08/2026, **Abdallah Shaban** — làm mảng sản phẩm tại Google, phụ trách Flutter — đăng một video game tic-tac-toe 3D: quân X và O là nhân vật có mắt, biết chớp, rơi xuống bàn cờ với hiệu ứng nảy, và khi một bên thắng thì các quân thắng đi *ăn thịt* quân thua. Anh nói dựng nó trong 15 phút, và — điểm đáng quý — **công khai toàn bộ prompt trong một repo mở**.

<figure class="tweet-embed">
<blockquote class="twitter-tweet" data-theme="dark" data-media-max-width="620"><p lang="en" dir="ltr">I built this game in 15 minutes with flutter_scene and <a href="https://twitter.com/FlutterDev">@FlutterDev</a>, using <a href="https://twitter.com/antigravity">@antigravity</a> and Gemini 3.7!</p>&mdash; Abdallah Shaban (@AbdallahSh07) <a href="https://twitter.com/AbdallahSh07/status/2090475954053513515">August 20, 2026</a></blockquote>
<script>(function(){var b=document.querySelector('figure.tweet-embed blockquote.twitter-tweet');if(b&&window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches){b.setAttribute('data-theme','light');}})();</script>
<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
<noscript><a href="https://x.com/AbdallahSh07/status/2090475954053513515"><img src="https://pbs.twimg.com/amplify_video_thumb/2090475913079373824/img/-tqL0NKGpqizib_u.jpg" alt="Game tic-tac-toe 3D dựng bằng flutter_scene" loading="lazy" /></a></noscript>
<figcaption>Video demo gốc của <a href="https://x.com/AbdallahSh07/status/2090475954053513515">Abdallah Shaban</a>. Toàn bộ prompt được công khai trong <a href="https://github.com/abdallahshaban557/flutter_scene_tic_tac_toe/blob/main/PROMPTS.md">PROMPTS.md</a> của repo.</figcaption>
</figure>

Tôi đã kiểm tra con số đó. Nó gần đúng hơn tôi nghĩ, nhưng câu chuyện thật thú vị hơn con số:

- Prompt đầu tiên: **19/08 lúc 20:27:19** (giờ −07:00).
- Commit đầu tiên, tên `tic tac toe`: **20:39:36** cùng ngày.
- ⏱️ **12 phút** từ câu lệnh đầu tới bản game chạy được đã commit.
- Nhưng bản trong video: **15 prompt, 11 commit, kết thúc lúc 23:16 — tức 2 giờ 49 phút.**

Cả hai con số đều đúng, và đặt cạnh nhau chúng là lời giới thiệu Flutter tốt nhất tôi tìm được. 12 phút đầu cho bạn thấy Flutter *nhanh* tới mức nào. 2 giờ 49 phút còn lại — gồm bốn lần báo bug — cho thấy **bạn vẫn phải hiểu framework**.

Bài này dùng chính repo đó làm giáo cụ. Toàn bộ số liệu đều đối chiếu từ nguồn gốc: prompt log, lịch sử commit, `pubspec.yaml` thật của dự án.

## Flutter là gì, nói cho gọn

Flutter là bộ công cụ của Google để viết **một** codebase rồi chạy trên **sáu** đích: iOS, Android, web, macOS, Windows, Linux. Bạn viết bằng ngôn ngữ **Dart**.

Nhưng câu đó chưa nói ra điều quan trọng nhất. Điều làm Flutter khác hẳn nằm ở chỗ này:

> **Flutter không dùng widget của hệ điều hành, và cũng không nhúng WebView. Nó mang theo engine đồ hoạ riêng và tự vẽ từng pixel lên một khung vải trống.**

Hệ quả rất lớn, và cả mặt tốt lẫn mặt xấu đều bắt nguồn từ đây:

| Vì Flutter tự vẽ… | nên bạn được | và bạn mất |
| --- | --- | --- |
| Không phụ thuộc widget hệ điều hành | Giao diện giống hệt nhau trên mọi máy, mọi phiên bản OS | Không tự động thừa hưởng thay đổi thiết kế của iOS/Android |
| Có engine riêng (Impeller) | Animation 60/120fps ổn định, và **chạy được cả engine 3D bên trong** | App nặng hơn app native cùng chức năng |
| Không phải DOM, không phải WebView | Không dính giới hạn của trình duyệt | Không tái dùng được code web sẵn có |

Cái ý ở giữa cột "được" là lý do bài này bắt đầu bằng một game 3D. Vì Flutter sở hữu toàn bộ đường ống render, người ta **dựng được một engine 3D ngay bên trong nó** — đó chính là `flutter_scene`. Không framework "đa nền tảng" nào theo hướng WebView làm nổi chuyện này; tôi đã bàn kỹ sự khác biệt đó trong [bản đồ công nghệ web làm app mobile](/vi/blog/web-tech-to-mobile-app-2026/).

## Mọi thứ là widget

Đây là khái niệm đầu tiên và cũng là khái niệm quan trọng nhất.

Trong Flutter, **widget** không chỉ là nút bấm hay ô nhập. Padding là widget. Căn giữa là widget. Màu nền là widget. Cả màn hình là widget. Ứng dụng cũng là widget.

Bạn không *chỉnh sửa* giao diện — bạn **mô tả** nó. Viết một hàm nhận vào trạng thái hiện tại và trả ra cây widget mô tả màn hình *ứng với trạng thái đó*. Khi trạng thái đổi, hàm chạy lại, Flutter so sánh cây mới với cây cũ và chỉ vẽ lại phần khác biệt.

```dart
class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Đếm số')),
      body: Center(
        child: Text('Đã bấm $_count lần'),
      ),
      floatingActionButton: FloatingActionButton(
        // setState báo cho Flutter: trạng thái đổi rồi, chạy lại build().
        onPressed: () => setState(() => _count++),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

Ba điều cần rút ra từ đoạn này, vì chúng lặp lại trong mọi app Flutter:

1. **`build()` phải rẻ và có thể gọi lại bất cứ lúc nào.** Nó có thể chạy 60 lần mỗi giây. Đừng đọc file hay gọi API trong đó.
2. **`setState()` là lời tuyên bố "dữ liệu đã đổi"**, không phải lệnh vẽ. Bạn không bao giờ ra lệnh vẽ trực tiếp.
3. **Ghép chứ không kế thừa.** Muốn thêm khoảng đệm? Bọc trong `Padding`. Muốn căn giữa? Bọc trong `Center`. Cây widget vì thế lồng sâu — đó là chuyện bình thường, không phải code tệ.

Ai từ React sang sẽ thấy quen ngay. Ai từ Android View hay UIKit sang sẽ mất vài ngày để bỏ thói quen "giữ tham chiếu tới widget rồi sửa thuộc tính của nó" — trong Flutter bạn gần như không bao giờ làm vậy.

## Dart, và vì sao nó tồn tại

Câu hỏi hợp lý: sao không dùng JavaScript hay Kotlin?

Vì Dart có một đặc điểm mà Flutter cần, và ít ngôn ngữ nào có sẵn cả hai chế độ:

- **Lúc phát triển: biên dịch JIT.** Sửa code, nạp lại vào máy ảo đang chạy trong chưa tới một giây.
- **Lúc phát hành: biên dịch AOT** ra mã máy thật. Không máy ảo diễn giải, không cần khởi động runtime.

Chính cặp này đẻ ra **hot reload** — và hot reload là lý do 12 phút kia khả thi.

Ngoài ra Dart có **null safety** bắt buộc: kiểu `String` chắc chắn có giá trị, muốn cho phép rỗng phải viết `String?`. Cả một họ lỗi null-pointer bị chặn ngay lúc biên dịch. Phiên bản đi kèm Flutter 3.47.1 là **Dart 3.13.1**.

## Hot reload: thứ bạn sẽ dùng nhiều nhất

Sửa một dòng, nhấn lưu, và giao diện đổi **trong khi app vẫn giữ nguyên trạng thái**. Bạn đang ở màn hình thứ tư sau khi đăng nhập và điền nửa cái form? Nó vẫn ở đó. Chỉ code đổi.

Đây là điểm mà người mới hay đánh giá thấp cho tới lúc thử. Nó biến việc chỉnh giao diện từ "sửa — build — bấm lại từ đầu — nhìn" (30–60 giây mỗi vòng) thành "sửa — nhìn" (dưới một giây). Với công việc tinh chỉnh giao diện, khác biệt này không phải 10%, mà là hai bậc độ lớn.

Và nó cũng chính là thứ khiến vòng lặp AI trong repo tic-tac-toe chạy nhanh như vậy: agent sửa code, hot reload đẩy thay đổi vào app đang chạy, kết quả nhìn thấy ngay. `flutter_scene` còn đẩy xa hơn — **hot reload cả file model `.glb` và material**, nên chỉnh nhân vật 3D cũng không phải khởi động lại.

Hai điều cần nhớ để khỏi bực:

- Đổi **giao diện và logic trong hàm**: hot reload ăn ngay.
- Đổi **biến toàn cục, giá trị khởi tạo `static`, hoặc `main()`**: phải **hot restart** (khởi động lại app, mất trạng thái). Đây là lúc bạn tưởng "sửa rồi mà không thấy đổi" — thường là do nhầm hai cái này.

## Đọc repo game 3D như một dự án Flutter thật

Toàn bộ game nằm gọn trong **6 file Dart, khoảng 65 KB**. Cấu trúc này rất điển hình:

```text
lib/
├── main.dart                    # điểm vào, dựng widget gốc
├── game/
│   └── game_controller.dart     # luật chơi, kiểm tra thắng, trạng thái
├── scene/
│   ├── tic_tac_toe_scene.dart   # cảnh 3D, camera, bắt chạm
│   ├── animated_piece.dart      # animation quân cờ
│   └── piece_builder.dart       # dựng hình học quân X và O
└── ui/
    └── game_overlay.dart        # bảng điểm 2D phủ lên trên
```

Điểm đáng chú ý nhất về mặt kiến trúc: **lớp giao diện 2D và cảnh 3D là hai cây widget riêng, chồng lên nhau bằng `Stack`**. Bảng điểm, lượt đi, nút bấm đều là widget Flutter bình thường — chỉ phần bàn cờ mới là 3D. Đây gần như luôn là cách đúng: đừng dựng nút bấm bằng 3D.

`pubspec.yaml` — file khai báo dependency của mọi dự án Flutter — cũng ngắn đến bất ngờ:

```yaml
environment:
  sdk: ^3.13.1

dependencies:
  flutter:
    sdk: flutter
  flutter_scene: ^0.22.2      # engine 3D
  vector_math: ^2.4.2         # toán vector cho phép chiếu tia
  hooks: ^2.2.0               # chạy bước dựng asset lúc build
```

Cái `hooks` ở cuối là thứ mới với nhiều người: Flutter giờ chạy được **hook lúc build**. `flutter_scene` dùng nó để chuyển file `.glb` sang định dạng nhị phân tối ưu ngay lúc build, thay vì phân tích cú pháp lúc chạy — lệnh `dart run flutter_scene:init` sẽ tự sinh file hook đó cho bạn.

## Bốn cái bug — và vì sao chúng là phần quan trọng nhất bài này

Trong 15 prompt, có **bốn prompt là báo lỗi**. Đây mới là chỗ đáng học, vì nó trả lời câu hỏi mà mọi người mới đang hỏi năm 2026: *nếu AI viết được thì tôi còn cần hiểu Flutter làm gì?*

**Bug 1 — chạm không đúng ô.** Bấm vào một ô mà quân không rơi đúng chỗ, trừ lần đầu. Đây là bài toán **phép chiếu tia** (ray casting): điểm chạm là toạ độ 2D trên màn hình, còn bàn cờ nằm trong không gian 3D, phải bắn một tia từ camera qua điểm đó rồi tính giao điểm với mặt phẳng bàn cờ. Không có gì "đặc trưng Flutter" ở đây cả — đây là toán đồ hoạ 3D, và nếu không biết khái niệm này thì bạn cũng không mô tả nổi lỗi cho AI sửa.

**Bug 2 — `RenderFlex overflowed`.** Cái sọc vàng đen kinh điển. Đây là **lỗi Flutter cơ bản nhất mà mọi người mới đều gặp**, nên hãy hiểu nó ngay bây giờ:

Flutter bố cục theo nguyên tắc **"ràng buộc đi xuống, kích thước đi lên"**. Widget cha truyền xuống con giới hạn chiều rộng/cao cho phép; con tự chọn kích thước trong giới hạn đó rồi báo ngược lên. Một `Row` theo mặc định để các con tự lấy kích thước tự nhiên. Nếu tổng bề ngang của chúng vượt quá chỗ có, `Row` **không** tự co lại — nó tràn, và Flutter báo lỗi thay vì âm thầm cắt mất nội dung.

Cách sửa hầu như luôn là một trong ba:

```dart
// 1. Cho con co giãn để lấp đúng chỗ còn lại
Row(children: [Expanded(child: Text(tenRatDai)), const Icon(Icons.star)])

// 2. Cho phần chữ tự xuống dòng hoặc cắt bằng dấu ba chấm
Expanded(child: Text(tenRatDai, overflow: TextOverflow.ellipsis))

// 3. Cho cuộn ngang, nếu nội dung thật sự dài hơn màn hình
SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(...))
```

Đáng chú ý: người dùng chỉ **dán nguyên thông báo lỗi** vào cho AI. Điều đó chỉ hiệu quả vì thông báo lỗi của Flutter viết cực kỹ — nó nói luôn widget nào tràn, tràn theo trục nào, và gợi ý `Expanded`. **Biết đọc thông báo lỗi Flutter là một kỹ năng, và nó không mất giá trị khi có AI.**

**Bug 3 — nhân vật quay lưng.** Quân cờ rơi xuống nhưng mặt hướng ra sau. Đây là chuyện hệ toạ độ và hướng quay — cũng là kiến thức 3D, không phải Flutter.

**Bug 4 — màn hình nhỏ bị cắt.** Trên máy màn hình nhỏ, camera cắt mất một phần bàn cờ. Đây là bài **thiết kế đáp ứng**, thứ mà app di động nào cũng phải xử lý.

Rút gọn lại: AI dựng xong bản chạy được trong 12 phút, nhưng **bốn cái bug còn lại đều đòi người dùng nhận ra vấn đề, gọi đúng tên, và mô tả được**. Trong đó có đúng một cái là kiến thức Flutter thuần (bố cục), một cái là thiết kế đáp ứng, và hai cái là toán 3D. Đó là bức tranh thật của lập trình có AI hỗ trợ hôm nay — nó nâng tốc độ gõ code, không thay được hiểu biết.

## Flutter hôm nay: bốn điều người mới cần biết ngay

Bản ổn định hiện tại là **Flutter 3.47.1 (19/08/2026)**, đi cùng Dart 3.13.1; bản 3.47.0 ra ngày 12/08/2026.

**1. Dòng import quen thuộc sắp thành di sản.** Suốt chín năm, gần như mọi file Flutter mở đầu bằng `import 'package:flutter/material.dart';`. Từ 3.47, **`material_ui` và `cupertino_ui` đã tách thành package độc lập trên pub.dev**, cả hai đều ở 1.0. Bản trong SDK vẫn chạy, nhưng **đã có lịch chính thức đánh dấu lỗi thời ở bản ổn định tháng 11**. Với người mới, điều này có nghĩa: mọi tutorial bạn đọc trên mạng lúc này vẫn đúng, nhưng dòng import của chúng sắp cũ. Có sẵn lệnh chuyển tự động:

```bash
flutter pub add material_ui cupertino_ui
dart fix --apply --code=migrate_design_widgets
```

Lý do tách không phải để cho đẹp: khi bị buộc vào SDK, bộ widget Cupertino chỉ vá lỗi được bốn lần mỗi năm, trong khi Apple đổi thiết kế bất cứ lúc nào. Tôi đã viết riêng về [cuộc chuyển đổi này](/vi/news/flutter-material-ui-cupertino-ui-migration-guide/).

**2. Impeller giờ là bộ render mặc định trên mọi nền tảng trừ web.** Đây là engine đồ hoạ mới thay cho Skia, biên dịch trước shader lúc build để không bị khựng khung hình ở lần chạy đầu. Đây cũng là nền để `flutter_gpu` và `flutter_scene` tồn tại.

**3. Yêu cầu hệ điều hành tối thiểu đã nâng.** iOS 15 trở lên, macOS 12 trở lên. Tutorial cũ ghi số thấp hơn sẽ không build được nếu không sửa cấu hình.

**4. Widget Previews đã ổn định.** Xem trước widget ngay trong IDE mà không cần chạy cả app — người mới nên bật ngay.

## Bắt đầu thật: từ số 0 tới app chạy

```bash
# 1. Cài Flutter theo hướng dẫn chính thức cho hệ điều hành của bạn:
#    https://docs.flutter.dev/get-started/install

# 2. Kiểm tra môi trường — lệnh này chỉ ra chính xác còn thiếu gì
flutter doctor

# 3. Tạo dự án mới
flutter create my_app
cd my_app

# 4. Chạy. Không truyền -d thì Flutter sẽ hỏi chọn thiết bị.
flutter run
```

`flutter doctor` là người bạn tốt nhất trong tuần đầu. Nó không chỉ báo thiếu gì mà còn in ra lệnh cần chạy để sửa. Vướng ở bước cài đặt thì gần như luôn là chưa nhận giấy phép Android SDK (`flutter doctor --android-licenses`) hoặc thiếu công cụ dòng lệnh của Xcode.

Sau khi app chạy, hãy làm đúng một việc này để hiểu vì sao người ta thích Flutter: mở `lib/main.dart`, đổi một chuỗi văn bản bất kỳ, rồi nhấn lưu. Nhìn máy ảo. Đó là hot reload.

Còn muốn chạy thử chính cái game 3D ở đầu bài:

```bash
git clone https://github.com/abdallahshaban557/flutter_scene_tic_tac_toe.git
cd flutter_scene_tic_tac_toe
flutter pub get
flutter run --enable-flutter-gpu
```

Cờ `--enable-flutter-gpu` là bắt buộc trên nền tảng native — Flutter GPU chưa bật mặc định. Chạy trên web (`flutter run -d chrome`) thì không cần cờ, vì bản web đi qua WebGL2.

## Flutter mạnh ở đâu, yếu ở đâu

Nói thẳng, vì bài giới thiệu nào chỉ khen thì đều vô dụng.

**Mạnh:**

- **Một codebase, sáu nền tảng, giao diện giống hệt nhau.** Không phải "gần giống" — giống hệt, vì Flutter tự vẽ.
- **Hot reload.** Vẫn là vòng lặp phát triển nhanh nhất trong mảng di động.
- **Animation và giao diện tuỳ biến mạnh.** Vì bạn nắm cả đường ống render, giao diện lạ không "chống lại" framework như khi làm với widget hệ điều hành.
- **Desktop và nhúng nghiêm túc**, không phải cổng phụ.

**Yếu:**

- **Kích thước app.** Phải mang theo engine, nên app Flutter luôn nặng hơn app native cùng chức năng.
- **Tích hợp sâu vào nền tảng vẫn cần code native.** Widget màn hình chính, Live Activities, App Intents — vẫn phải viết Swift/Kotlin. Flutter không xoá được yêu cầu đó.
- **Độ hài lòng với bộ widget kiểu iOS thấp nhất trong toàn hệ sinh thái** — khảo sát quý 2/2026 cho Cupertino **61%**, giảm 6 điểm, trong khi Dart 92% và framework lõi 90%. Đây chính là lý do có cuộc tách package ở trên.
- **Web vẫn là nền tảng yếu nhất.** Impeller chưa có trên web, và tải về nặng hơn hẳn một trang web thường.
- **Không tái dùng được code web sẵn có.** Nếu tài sản lớn nhất của bạn là một app web và một đội web, Flutter không giúp bạn tận dụng nó.

## Vậy còn 3D — dùng được thật chưa?

Có, với điều kiện hiểu đúng ranh giới. `flutter_scene` hiện ở **0.22.2**, do publisher đã xác minh `bdero.dev` phát hành, cần Flutter 3.47 trở lên, hỗ trợ cả sáu nền tảng (web đi qua WebGL2). Nó có nhập model glTF, ánh sáng PBR, animation xương và vật lý.

Nhưng số hiệu phiên bản vẫn bắt đầu bằng số 0, và điều đó có ý nghĩa: API còn đổi. Dùng nó cho một khối 3D bên trong app bình thường thì hợp lý; đặt cược cả một game thương mại vào nó thì hãy đọc kỹ [bài phân tích riêng về Flutter GPU và flutter_scene](/vi/news/flutter-gpu-3d-rendering-flutter-scene/) trước.

Một chi tiết nhỏ nhưng đáng chú ý trong repo tic-tac-toe: `flutter_scene` **đóng gói sẵn bộ "agent skills"** — tài liệu dạy trợ lý AI viết đúng cách dùng thư viện thay vì đoán mò, cài bằng `dart run flutter_scene:skills`. Đây là dấu hiệu của một xu hướng đang lan: package không chỉ ship code và tài liệu cho người, mà ship cả hướng dẫn cho máy.

## Câu hỏi thường gặp

**Chưa biết lập trình có học Flutter được không?**
Được, nhưng hãy học Dart trước một chút. Dart là ngôn ngữ có kiểu tĩnh, cú pháp giống Java/JavaScript/C#, học nhanh nếu đã biết một trong số đó. Cái khó với người mới không phải cú pháp mà là **tư duy khai báo**: mô tả giao diện theo trạng thái, thay vì ra lệnh sửa từng phần tử.

**Nên học Flutter hay React Native?**
Nếu đội bạn đã là đội JavaScript/React, React Native gần hơn. Nếu bắt đầu từ đầu và ưu tiên giao diện đồng nhất cùng vòng lặp phát triển nhanh, Flutter thường dễ chịu hơn. Cần nói rõ một hiểu lầm phổ biến: **cả hai đều không tái dùng được frontend web sẵn có của bạn** — chuyện đó thuộc về nhóm giải pháp khác, tôi đã phân tích trong [bài về công nghệ web làm app mobile](/vi/blog/web-tech-to-mobile-app-2026/).

**Có cần máy Mac không?**
Chỉ khi muốn build cho iOS hoặc macOS — Xcode chỉ chạy trên macOS. Học Flutter, làm app Android, web, Windows và Linux thì máy Windows hay Linux hoàn toàn đủ.

**Học bao lâu thì làm được app thật?**
Với người đã biết lập trình: khoảng một tuần để thoải mái với widget và bố cục, vài tuần nữa để nắm quản lý trạng thái, gọi mạng và điều hướng. Chỗ tốn thời gian nhất thường không phải Flutter mà là **quy trình phát hành lên hai cửa hàng**.

**AI viết được app Flutter rồi thì học làm gì?**
Hãy nhìn lại repo ở đầu bài. AI dựng bản chạy được trong 12 phút, nhưng 2 giờ 49 phút còn lại là bốn vòng người dùng phải **phát hiện lỗi, gọi đúng tên và mô tả được** — trong đó có `RenderFlex overflowed`, thứ bạn không sửa nổi nếu chưa hiểu mô hình ràng buộc bố cục của Flutter. AI làm phần gõ nhanh hơn rất nhiều. Nó chưa làm thay phần biết mình đang nhìn cái gì.

**Nên bắt đầu với `material_ui` mới hay `material.dart` trong SDK?**
Nếu bắt đầu hôm nay, hãy dùng package `material_ui` mới. Bản trong SDK vẫn chạy nhưng có lịch đánh dấu lỗi thời từ bản ổn định tháng 11, và không có lý do gì để bắt đầu bằng thứ sắp bị thay.

**Flutter có chết không, có bị Google bỏ không?**
Đây là câu hỏi hợp lý với mọi sản phẩm Google. Bằng chứng hiện tại đi ngược hướng đó: 3.47.0 và 3.47.1 ra trong tháng 8/2026, Impeller vừa thành mặc định trên desktop, bộ thiết kế được tách ra để phát hành nhanh hơn, và Google đang đưa Flutter vào chính bộ công cụ AI của mình. Đây không phải dấu hiệu của một dự án đang bị bỏ.
