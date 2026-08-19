---
title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
description: "Dựng vòng tròn tiến trình từ đầu bằng Container, Stack và CustomPaint — kèm phần lượng giác đứng sau startAngle và sweepAngle."
seoDescription: "Hướng dẫn CustomPaint trong Flutter: vẽ progress indicator hình tròn bằng canvas.drawArc, cách tính startAngle và sweepAngle theo radian hoặc độ. Kèm code chạy được."
keywords:
  - progress indicator tùy chỉnh flutter
  - hướng dẫn custompaint flutter
  - flutter drawarc
  - flutter custompainter
  - vòng tròn tiến trình flutter
  - vẽ canvas flutter
category: "Hướng dẫn"
topic: "CustomPaint"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2021-08-23"
updatedDate: "2026-08-19"
emoji: "🎨"
tags: ["Flutter", "CustomPaint", "Canvas", "UI", "Animation"]
canonicalSource:
  name: "trunghieu-it.blogspot.com"
  url: "https://trunghieu-it.blogspot.com/2021/08/creating-custom-progress-indicator.html"
sources:
  - name: "Canvas class — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/Canvas-class.html"
  - name: "Canvas.drawArc — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/Canvas/drawArc.html"
  - name: "StrokeCap — tài liệu Flutter"
    url: "https://api.flutter.dev/flutter/dart-ui/StrokeCap-class.html"
  - name: "Dan-Y-Ko/Flutter-Dart-Playground — banking_app_ui"
    url: "https://github.com/Dan-Y-Ko/Flutter-Dart-Playground/tree/master/flutter/ui/banking_app_ui"
draft: false
---

`CircularProgressIndicator` có sẵn của Flutter dùng ổn — cho tới khi designer đưa bạn một vòng cung bắt đầu ở vị trí 4 giờ, kết thúc ở 8 giờ và ôm lấy một cái nút. Lúc đó bạn không còn cấu hình widget nữa mà phải tự vẽ nó. Bài này dựng vòng cung đó từ đầu bằng `CustomPaint`, và quan trọng hơn là giải thích phần tính góc — chỗ hầu hết mọi người vấp lần đầu.

Bài viết giả định bạn đã quen với widget cơ bản của Flutter. Trọng tâm ở đây là phần vẽ, không phải phần dựng khung.

## Ba widget cần dùng

Chỉ ba widget làm việc thật sự:

- **`Container`** — vẽ vòng tròn viền tĩnh bên ngoài (đường "ray" mà tiến trình chạy trên đó).
- **`Stack`** — cho phép cung vẽ chồng lên vòng tròn đó thay vì nằm cạnh.
- **`CustomPaint`** — đưa cho bạn một `Canvas` để tự vẽ cung.

## Bắt đầu với vòng tròn nền

Trước khi vẽ gì, hãy đưa một vòng tròn đơn giản lên màn hình. Một `Container` với `BoxShape.circle` và viền là đủ; bọc sẵn trong `Stack` ngay từ giờ sẽ đỡ phải sửa lại ở bước sau.

```dart
import 'package:flutter/material.dart';

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
      ],
    );
  }
}
```

Kết quả là một vòng tròn viền trắng mảnh giữa nền tối. Mọi thứ từ đây trở đi được vẽ đè lên nó.

## Viết CustomPainter

Widget `CustomPaint` chỉ hay ho bằng đúng cái `CustomPainter` bạn đưa cho nó. Một painter cần ba thứ:

1. kế thừa `CustomPainter`
2. cài đặt `paint`
3. cài đặt `shouldRepaint`

`shouldRepaint` đúng như tên gọi: trả về `true` khi một instance mới của painter cần vẽ lại. Với chỉ báo tĩnh thì không có gì thay đổi giữa các lần build, nên `false` là đúng — và rẻ hơn. (Khi bắt đầu animation cho cung, hãy trả `true` hoặc so sánh các trường với `oldDelegate`.)

### Mổ xẻ phương thức paint

`paint` nhận `Canvas` để vẽ và `Size` mà nó được cấp. Canvas vẽ được hình chữ nhật, hình tròn, đường thẳng và cả path tùy ý; ở đây ta chỉ cần một cung (arc).

```dart
void paint(Canvas canvas, Size size) {
    // 2
    final paint = Paint()
      // 3
      ..color = Colors.blue
      // 4
      ..strokeCap = StrokeCap.butt
      // 5
      ..style = PaintingStyle.stroke
      // 6
      ..strokeWidth = width;

    // 7
    final center = Offset(size.width / 2, size.height / 2);

    // 8
    final radius = (size.width / 2) - (width / 2);

    // 1
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      paint,
    );
  }
```

Giải thích từng điểm:

1. **`drawArc`** nhận năm đối số. Thứ nhất là `Rect` chứa cung — `Rect.fromCircle` giữ cho nó tròn đều. Thứ hai là nơi cung bắt đầu, thứ ba là độ dài cung quét. Thứ tư (`useCenter`) quyết định hai đầu cung có nối về tâm hay không; để `false` trừ khi bạn muốn một miếng bánh. Thứ năm là `Paint`.
2. **`Paint`** giữ toàn bộ thuộc tính hiển thị của nét vẽ và được truyền vào `drawArc`.
3. **`color`** — màu nét vẽ.
4. **`strokeCap`** — kiểu bo hai đầu cung. `StrokeCap.butt` cắt phẳng; `StrokeCap.round` bo tròn, đây là kiểu đa số thiết kế cần.
5. **`style`** — `PaintingStyle.fill` tô đặc, `PaintingStyle.stroke` chỉ vẽ viền. Vòng tiến trình là viền.
6. **`strokeWidth`** — độ dày viền đó, đi kèm với `PaintingStyle.stroke`.
7. **`center`** — một nửa chiều rộng và một nửa chiều cao, để cung nằm giữa khung mà painter nhận được.
8. **`radius`** — nửa chiều rộng *trừ đi nửa độ dày nét*. Bỏ phép trừ này thì nét vẽ sẽ tràn ra mép khung và bị cắt.

Đây là toàn bộ file với painter đã ráp vào, phần tính góc vẫn được comment lại để code biên dịch và chạy được:

```dart
import 'package:flutter/material.dart';
// import 'dart:math' as math;

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
//     required this.startAngle,
//     required this.endAngle,
  }) : super(key: key);

//   final double startAngle;
//   final double endAngle;

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
        SizedBox(
          width: buttonSize,
          height: buttonSize,
          child: CustomPaint(
            painter: ProgressIndicatorPainter(
              width: borderWidth,
//               startAngle: startAngle,
//               sweepAngle: endAngle,
            ),
            child: Center(
              child: Container(
                width: buttonSize - 20.0,
                height: buttonSize - 20.0,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.done,
                    size: 30.0,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProgressIndicatorPainter extends CustomPainter {
  const ProgressIndicatorPainter({
    required this.width,
//     required this.startAngle,
//     required this.sweepAngle,
  }) : super();

  final double width;
//   final double startAngle;
//   final double sweepAngle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeCap = StrokeCap.butt
      ..style = PaintingStyle.stroke
      ..strokeWidth = width;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - (width / 2);

//     canvas.drawArc(
//       Rect.fromCircle(center: center, radius: radius),
//       startAngle,
//       sweepAngle,
//       false,
//       paint,
//     );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

Hãy giữ nguyên các dòng comment đúng vị trí — bỏ comment một nửa thì sẽ lỗi biên dịch.

## startAngle và sweepAngle thực sự là gì

Đây là phần đáng đi chậm lại.

**`startAngle`** tính bằng radian và bắt đầu từ 0 — tức vị trí 3 giờ trên đường tròn đơn vị. Điểm gây bẫy là chiều: `drawArc` quét **theo chiều kim đồng hồ**, trong khi đường tròn đơn vị bạn học ở trường chạy ngược chiều kim đồng hồ. Thay vì suy luận lại từ đầu, mẹo là cứ đọc vị trí trên đường tròn đơn vị như bình thường rồi thêm dấu âm. Muốn cung bắt đầu ở π/2 (vị trí 12 giờ)? Truyền `-π/2`.

**`sweepAngle`** không phải vị trí kết thúc — nó là độ dài. Giá trị bạn truyền được *cộng* vào `startAngle`, và tổng đó mới là nơi cung dừng. Muốn vẽ từ π/2 về 0 thì cần `startAngle: -π/2` và `sweepAngle: π/2`, vì −π/2 + π/2 = 0.

### Tính sweep cho một cung bất kỳ

Lấy vòng cung ở đầu bài: nó bắt đầu quanh 2π/3 và kết thúc quanh 11π/6 trên đường tròn đơn vị. Không có phép trừ gọn gàng nào luôn cho ra sweep khi start là góc tùy ý, nên hãy đếm cung theo từng lát:

- góc phần tư I được phủ trọn → π/2
- góc phần tư II và IV mỗi bên góp một lát π/6 → π/6 + π/6

π/6 + π/6 + π/2 = **5π/6**, đó chính là sweep. Code đầy đủ:

```dart
import 'package:flutter/material.dart';
import 'dart:math' as math;

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(
            startAngle: -2 * math.pi / 3,
            endAngle: 5 * math.pi / 6,
          ),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
    required this.startAngle,
    required this.endAngle,
  }) : super(key: key);

  final double startAngle;
  final double endAngle;

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
        SizedBox(
          width: buttonSize,
          height: buttonSize,
          child: CustomPaint(
            painter: ProgressIndicatorPainter(
              width: borderWidth,
              startAngle: startAngle,
              sweepAngle: endAngle,
            ),
            child: Center(
              child: Container(
                width: buttonSize - 20.0,
                height: buttonSize - 20.0,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.done,
                    size: 30.0,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProgressIndicatorPainter extends CustomPainter {
  const ProgressIndicatorPainter({
    required this.width,
    required this.startAngle,
    required this.sweepAngle,
  }) : super();

  final double width;
  final double startAngle;
  final double sweepAngle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeCap = StrokeCap.butt
      ..style = PaintingStyle.stroke
      ..strokeWidth = width;

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - (width / 2);

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

## Thích dùng độ hơn? Đổi ở sát chỗ vẽ

Nếu radian làm code gọi khó đọc, hãy nhận giá trị theo độ vào painter rồi đổi sang radian ngay trước `drawArc`. Không có gì khác thay đổi — vẫn các khái niệm đó, chỉ là con số dễ chịu hơn.

```dart
import 'package:flutter/material.dart';
import 'dart:math' as math;

const Color darkBlue = Color.fromARGB(255, 18, 32, 47);

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData.dark().copyWith(scaffoldBackgroundColor: darkBlue),
      debugShowCheckedModeBanner: false,
      home: const Scaffold(
        body: Center(
          child: ProgressIndicatorButton(
            startAngle: -120,
            endAngle: 150,
          ),
        ),
      ),
    );
  }
}

class ProgressIndicatorButton extends StatelessWidget {
  const ProgressIndicatorButton({
    Key? key,
    required this.startAngle,
    required this.endAngle,
  }) : super(key: key);

  final int startAngle;
  final int endAngle;

  @override
  Widget build(BuildContext context) {
    const buttonSize = 80.0;
    const borderWidth = 2.0;

    return Stack(
      children: [
        Container(
          width: buttonSize,
          height: buttonSize,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            border: Border.all(
              color: Colors.white,
              width: borderWidth,
            ),
          ),
        ),
        SizedBox(
          width: buttonSize,
          height: buttonSize,
          child: CustomPaint(
            painter: ProgressIndicatorPainter(
              width: borderWidth,
              startAngle: startAngle,
              sweepAngle: endAngle,
            ),
            child: Center(
              child: Container(
                width: buttonSize - 20.0,
                height: buttonSize - 20.0,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.done,
                    size: 30.0,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class ProgressIndicatorPainter extends CustomPainter {
  const ProgressIndicatorPainter({
    required this.width,
    required this.startAngle,
    required this.sweepAngle,
  }) : super();

  final double width;
  final int startAngle;
  final int sweepAngle;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.blue
      ..strokeCap = StrokeCap.butt
      ..style = PaintingStyle.stroke
      ..strokeWidth = width;

    final startAngleRad = startAngle * (math.pi / 180.0);
    final sweepAngleRad = sweepAngle * (math.pi / 180.0);

    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width / 2) - (width / 2);

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngleRad,
      sweepAngleRad,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => false;
}
```

## Hai ví dụ để luyện tay

Cùng quy trình, chỉ khác con số:

- **Bắt đầu ở vị trí 3 giờ.** `startAngle` là `0` (viết `0.0` trong code cũng được). Sweep phủ trọn góc phần tư IV cộng một lát π/6 của góc phần tư III: π/6 + π/2 = **4π/6**.
- **Bắt đầu ở −5π/4.** Ở góc phần tư II lấy trọn quadrant, rồi ở góc phần tư III lấy một lát π/6 và một lát π/12: π/2 + π/6 + π/12 = **3π/4**.

## Kết luận

Đếm từng lát theo góc phần tư không phải cách thanh lịch nhất để suy ra sweep angle, nhưng nó đáng tin và bạn có thể tính ngay trên giấy cạnh bản thiết kế. Khi vòng cung tĩnh đã đúng, việc thêm animation chỉ là một bước ngắn: điều khiển `sweepAngle` bằng `AnimationController`, và đổi `shouldRepaint` sang so sánh với `oldDelegate` để Flutter thực sự vẽ lại.
