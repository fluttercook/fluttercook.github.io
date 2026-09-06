---
title: "Fragment shader trong Flutter: cửa thoát xuống GPU và cái giá của nó"
description: "Flutter có thể nạp fragment shader GLSL và chạy trên GPU. Điều đó mở ra những hiệu ứng mà tầng widget không diễn đạt nổi — kèm theo chi phí biên dịch, việc đi dây uniform thủ công, và vài lưu ý nền tảng cần biết trước khi cam kết."
seoDescription: "Dùng fragment shader trong Flutter: FragmentProgram, uniform, khai báo flutter: shaders trong pubspec, AnimatedSampler, đầu vào sampler2D, và khi nào shader là câu trả lời sai."
keywords:
  - fragment shader flutter
  - fragmentprogram glsl flutter
  - uniform shader flutter
  - animatedsampler flutter
  - hiệu ứng gpu flutter
  - hiệu năng shader flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-25"
emoji: "🌈"
tags: ["Flutter", "Shaders", "GPU", "Graphics", "Performance"]
sources:
  - name: "Viết và dùng fragment shader — tài liệu Flutter"
    url: "https://docs.flutter.dev/ui/design/graphics/fragment-shaders"
  - name: "FragmentProgram — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/FragmentProgram-class.html"
  - name: "FragmentShader — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/dart-ui/FragmentShader-class.html"
  - name: "ShaderMask — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ShaderMask-class.html"
  - name: "CustomPainter — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/CustomPainter-class.html"
  - name: "Engine kết xuất Impeller — tài liệu Flutter"
    url: "https://docs.flutter.dev/perf/impeller"
related:
  - slug: "flutter-custom-renderobject"
    title: "Khi ghép widget không còn đủ: tự viết RenderObject"
  - slug: "flutter-custom-scroll-physics"
    title: "Scroll physics tự viết: khiến danh sách dừng đúng chỗ bạn muốn"
draft: false
---

Có một nhóm hiệu ứng thị giác mà widget đơn giản là không tạo ra được: méo ảnh theo từng pixel, gradient thủ tục tự động theo thời gian mà không cần rebuild, hiệu ứng tan biến, gợn sóng, sai lệch màu. Bạn có thể xấp xỉ vài cái trong số đó bằng đủ nhiều lớp `Transform` và `Opacity`, và kết quả sẽ vừa chậm vừa sai.

Câu trả lời của Flutter là một fragment shader GLSL được biên dịch lúc build và chạy trên GPU. Đó thật sự là một cửa thoát mạnh mẽ. Nó cũng là một mô hình lập trình khác với chi phí riêng, và phiên bản trung thực của bài này nói cả hai.

## Shader tối thiểu chạy được

Fragment shader là chương trình chạy một lần cho mỗi pixel và trả về một màu. Phương ngữ của Flutter là GLSL ES cộng một nhóm nhỏ tiện ích riêng từ `flutter/runtime_effect.glsl`.

`shaders/ripple.frag`:

```glsl
#version 460 core
#include <flutter/runtime_effect.glsl>

precision highp float;

uniform vec2 uSize;
uniform float uTime;
uniform vec4 uColor;

out vec4 fragColor;

void main() {
  vec2 uv = FlutterFragCoord().xy / uSize;
  float d = distance(uv, vec2(0.5));
  float wave = sin(d * 40.0 - uTime * 4.0) * 0.5 + 0.5;
  fragColor = uColor * wave;
}
```

Hai dòng là đặc thù Flutter và cả hai đều quan trọng. `#include <flutter/runtime_effect.glsl>` mang vào `FlutterFragCoord()`, thứ bạn phải dùng thay cho `gl_FragCoord` thô — giá trị thô không nằm trong hệ toạ độ bạn tưởng một khi các phép biến đổi của Flutter đã áp lên. Và `uSize` không tự có: Flutter không cấp uniform độ phân giải dựng sẵn, nên bạn tự truyền kích thước vào.

Khai báo nó trong `pubspec.yaml` dưới khoá `flutter:`, không phải dưới `assets:`:

```yaml
flutter:
  shaders:
    - shaders/ripple.frag
```

Chính khai báo đó kích hoạt trình biên dịch shader lúc build. Một shader đặt dưới `assets:` sẽ nạp như bytes rồi hỏng ở `FragmentProgram.fromAsset` theo kiểu trông giống lỗi thiếu file.

## Nạp và điều khiển

`FragmentProgram.fromAsset` là bất đồng bộ và trả về một program dùng để tạo các thể hiện shader:

```dart
class RipplePainter extends CustomPainter {
  RipplePainter(this.program, this.time, this.color)
      : super(repaint: null);

  final ui.FragmentProgram program;
  final double time;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final shader = program.fragmentShader()
      ..setFloat(0, size.width)   // uSize.x
      ..setFloat(1, size.height)  // uSize.y
      ..setFloat(2, time)         // uTime
      ..setFloat(3, color.r)      // uColor.r
      ..setFloat(4, color.g)
      ..setFloat(5, color.b)
      ..setFloat(6, color.a);

    canvas.drawRect(Offset.zero & size, Paint()..shader = shader);
  }

  @override
  bool shouldRepaint(RipplePainter old) =>
      old.time != time || old.color != color;
}
```

Hãy nhìn kỹ các chỉ số. **Uniform được địa chỉ hoá bằng chỉ số float phẳng, theo thứ tự khai báo, với vector bị trải phẳng.** `uSize` là `vec2` nên chiếm chỉ số 0 và 1; `uTime` là 2; `uColor` là `vec4` nên lấy 3 đến 6. Không có setter theo tên. Chèn một uniform vào giữa shader là mọi chỉ số phía dưới bị dịch — âm thầm, không lỗi biên dịch, và cho ra hiệu ứng chỉ đơn giản là sai.

Cách giảm thiểu là một khối hằng nhỏ đặt ngay cạnh mã shader:

```dart
abstract final class RippleUniforms {
  static const sizeX = 0;
  static const sizeY = 1;
  static const time = 2;
  static const colorR = 3;
}
```

Nó tốn bốn dòng và loại bỏ cả một nhóm lỗi khó tìm.

## Ghép vào widget

Nạp program một lần, ở trên cao, và animate uniform thời gian bằng một ticker:

```dart
class RippleBox extends StatefulWidget {
  const RippleBox({super.key, required this.color});
  final Color color;

  @override
  State<RippleBox> createState() => _RippleBoxState();
}

class _RippleBoxState extends State<RippleBox>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(seconds: 4),
  )..repeat();

  ui.FragmentProgram? _program;

  @override
  void initState() {
    super.initState();
    ui.FragmentProgram.fromAsset('shaders/ripple.frag').then((p) {
      if (mounted) setState(() => _program = p);
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final program = _program;
    if (program == null) return const SizedBox.expand();

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) => CustomPaint(
        painter: RipplePainter(
          program,
          _controller.value * 4,
          widget.color,
        ),
        size: Size.infinite,
      ),
    );
  }
}
```

`fromAsset` có cache theo đường dẫn asset, nên gọi nó từ nhiều widget không phải thảm hoạ — nhưng nạp một lần rồi truyền xuống vẫn sạch hơn và làm trạng thái "đang nạp thì null" hiện rõ ở một chỗ.

## Lấy mẫu chính cây widget

Cách dùng thú vị hơn là áp shader lên thứ Flutter đã vẽ sẵn — một hiệu ứng tan biến trên widget thật, chứ không phải hoa văn thủ tục. Việc đó cần uniform `sampler2D`:

```glsl
uniform sampler2D uTexture;
uniform float uProgress;

void main() {
  vec2 uv = FlutterFragCoord().xy / uSize;
  vec4 src = texture(uTexture, uv);
  float noise = fract(sin(dot(uv, vec2(12.9898, 78.233))) * 43758.5453);
  fragColor = noise < uProgress ? vec4(0.0) : src;
}
```

Sampler dùng không gian chỉ số riêng, tách khỏi float — `setImageSampler(0, image)`, không phải `setFloat`. Nhầm hai thứ này cho ra kết quả đen thui mà không báo lỗi.

Chụp cây widget con thành ảnh mới là phần lắt léo. `AnimatedSampler` trong gói `flutter_shaders` bọc sẵn cơ chế `SnapshotWidget` và là lựa chọn thực dụng; làm tay nghĩa là `RepaintBoundary` cộng `toImage`, vốn bất đồng bộ nên luôn trễ một frame.

## Cái giá phải trả

| Chi phí | Chi tiết |
| --- | --- |
| Biên dịch lần đầu | Shader được biên dịch cho GPU đích ở lần dùng đầu; Impeller biên dịch trước khi có thể, nhưng vẫn có khả năng khựng ở frame đầu |
| Không hot reload `.frag` | Sửa mã shader thường phải restart chứ không reload được |
| Gỡ lỗi | Không có `print`. Bạn gỡ lỗi bằng cách xuất giá trị ra thành màu |
| Khác biệt nền tảng | Bổ ngữ độ chính xác và hành vi số thực khác nhau giữa các GPU; hãy thử trên máy Android đời thấp thật, không chỉ giả lập |
| Web | Mức hỗ trợ phụ thuộc renderer web đang dùng; kiểm chứng trên mục tiêu trước khi thiết kế xoay quanh nó |

Cái làm khổ các đội nhất là mục thứ hai: vòng lặp thử-sai khi làm shader chậm tới mức nó nên thay đổi cách bạn làm việc — dựng hiệu ứng trong một playground shader trước, rồi port sang một lần khi đã ưng.

## Khi nào đừng dùng shader

Shader đúng cho công việc theo từng pixel trên một bề mặt liên tục. Nó sai cho:

- **Một gradient.** `LinearGradient` và họ hàng đã chạy trên GPU và đơn giản hơn nhiều.
- **Một hiệu ứng mờ.** `BackdropFilter` với `ImageFilter.blur` đã có sẵn và được tối ưu.
- **Che một widget bằng một hình dạng.** `ShaderMask` hoặc `ClipPath` xử lý được mà không cần GLSL.
- **Bất cứ thứ gì thay đổi layout.** Shader chỉ vẽ; nó không di chuyển hay định kích thước widget.

Quy tắc tôi dùng: nếu bạn mô tả được hiệu ứng bằng hình dạng và phép biến đổi, hãy dùng widget. Nếu bạn chỉ mô tả được bằng "với mỗi pixel, hãy tính…", hãy viết shader.

## Câu hỏi thường gặp

**Vì sao shader của tôi đen hoàn toàn?**

Thường nhất là uniform chưa bao giờ được set — uniform chưa set mang giá trị 0, và kích thước bằng 0 khiến mọi `uv` chia cho 0. Hãy set mọi uniform đã khai báo, kể cả cái bạn chưa animate.

**Vì sao trên máy tôi thì đúng, máy khác thì sai?**

Độ chính xác. `precision highp float` là một yêu cầu, không phải bảo đảm, và GPU di động đời thấp rất khác nhau. Tránh toạ độ có giá trị quá lớn và những phép cộng dồn số thực dài.

**Có dùng được vertex shader không?**

Runtime effect của Flutter chỉ là fragment shader. Muốn điều khiển ở mức đỉnh thì phải dùng vertices của `dart:ui` hoặc một `RenderObject` tự viết.

**Dùng shader có hao pin không?**

Một shader toàn màn hình chạy mỗi frame là công việc GPU liên tục. Hãy tạm dừng animation controller khi hiệu ứng ra khỏi màn hình hoặc ứng dụng không hoạt động — đây là cái lợi lớn nhất bạn có được.

**Kiểm thử shader thế nào?**

Golden test trên một `CustomPaint` với bộ uniform cố định bắt được hồi quy. Chúng phụ thuộc GPU, nên hãy cố định môi trường test nếu không muốn test chập chờn.

---

*API `FragmentProgram`, khai báo `flutter: shaders:` trong pubspec, `FlutterFragCoord()` và mô hình uniform chỉ số phẳng mô tả ở đây đều nằm trong tài liệu Flutter dẫn ở trên. Thói quen dùng khối hằng cho uniform, cách xếp nặng nhẹ trong bảng chi phí, và quy tắc nhận biết khi nào shader là công cụ sai là nhận định riêng của tôi khi làm hiệu ứng theo cách này. Mức hỗ trợ shader và hành vi Impeller thay đổi nhanh giữa các bản phát hành — hãy kiểm chứng trên nền tảng đích trước khi cam kết với một hiệu ứng.*
