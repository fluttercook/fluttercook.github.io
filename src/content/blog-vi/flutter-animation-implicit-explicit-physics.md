---
title: "Ba kiểu animation trong Flutter và cách chọn đúng kiểu"
description: "Animation implicit, explicit và physics-based trong Flutter, qua cùng một tấm card dựng ba cách — kèm tham số child của AnimatedBuilder, kỷ luật dispose, và lý do animate layout không hề miễn phí."
seoDescription: "Implicit, explicit hay physics-based: AnimatedContainer, AnimationController, SpringSimulation — cùng những lỗi hay gặp khi review code Flutter animation."
keywords:
  - implicit và explicit animation flutter
  - animationcontroller dispose flutter
  - springsimulation animatewith flutter
  - tham số child animatedbuilder
  - tweenanimationbuilder flutter
  - curves animation flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🎬"
tags: ["Flutter", "Animation", "Performance", "UI"]
sources:
  - name: "Giới thiệu về animations — tài liệu Flutter"
    url: "https://docs.flutter.dev/ui/animations"
  - name: "Implicit animations — tài liệu Flutter"
    url: "https://docs.flutter.dev/ui/animations/implicit-animations"
  - name: "AnimationController — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/animation/AnimationController-class.html"
  - name: "AnimatedBuilder — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/widgets/AnimatedBuilder-class.html"
  - name: "SpringSimulation — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/physics/SpringSimulation-class.html"
  - name: "Curves — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/animation/Curves-class.html"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
draft: false
---

Flutter cho bạn ít nhất ba cách khác nhau để làm một pixel chuyển động, và tài liệu trình bày chúng như một thực đơn chứ không phải một quyết định. Kết quả là hầu hết codebase đều có đủ cả ba, chọn theo cảm hứng của người viết widget hôm đó, còn người review thì không có nguyên tắc nào để phản biện.

Có một nguyên tắc. Nó không phải "implicit dành cho những thứ đơn giản". Nó là: **ai sở hữu giá trị giữa hai frame?** Với implicit animation, framework sở hữu — bạn khai báo giá trị đích và widget tự nội suy. Với explicit animation, bạn sở hữu, thông qua một `AnimationController` do bạn tạo, điều khiển và hủy. Với physics-based thì không ai trong hai bên sở hữu cả: một `Simulation` tính giá trị từ khối lượng, vận tốc và thời gian, và bạn không được quyền quy định nó chạy bao lâu.

Để so sánh cho cụ thể, bài này dựng cùng một tương tác ba lần: một tấm card nở ra khi chạm, và có thể hất ngang ra khỏi màn hình. Đây là ví dụ tốt vì nó vừa có một *thay đổi state* (thu gọn sang mở rộng) — thứ implicit xử lý rất gọn — vừa có một *cử chỉ mang vận tốc* (cú hất), thứ implicit hoàn toàn không làm được.

## Ai sở hữu giá trị giữa hai frame

| | Giá trị đến từ | Bạn khai báo | Khi bị ngắt giữa chừng |
|---|---|---|---|
| **Implicit** | Controller nội bộ bên trong widget | Giá trị đích, duration, curve | Tự động — nhắm lại từ giá trị hiện tại |
| **Explicit** | `AnimationController` bạn giữ | Duration, curve, lúc start/stop/reverse | Bạn tự lo |
| **Physics** | Một `Simulation` (spring, friction) | Vị trí và vận tốc ban đầu, cộng thuộc tính vật liệu | Đưa vận tốc mới vào một simulation mới |

Cột cuối mới là chỗ quyết định thực sự được đưa ra. Một cú chạm lật một biến bool thì chẳng có gì thú vị để ngắt, nên implicit thắng về số dòng code. Một cú kéo mà người dùng thả ra giữa chừng thì *có*, và animation phải đi tiếp đúng từ vận tốc của ngón tay — điều mà một con số duration không diễn tả được.

## Tấm card, làm theo kiểu implicit

`AnimatedContainer` là một `Container` tự theo dõi các thuộc tính của chính nó và animate bất cứ thuộc tính nào đổi giữa hai lần build. Không thấy controller nào, cũng không có gì phải dispose.

```dart
class ImplicitCard extends StatefulWidget {
  const ImplicitCard({super.key});
  @override
  State<ImplicitCard> createState() => _ImplicitCardState();
}

class _ImplicitCardState extends State<ImplicitCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => setState(() => _expanded = !_expanded),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 320),
        curve: Curves.easeOutCubic,
        width: _expanded ? 320.0 : 200.0,
        height: _expanded ? 220.0 : 96.0,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: _expanded ? Colors.indigo.shade700 : Colors.indigo.shade400,
          borderRadius: BorderRadius.circular(_expanded ? 24.0 : 12.0),
        ),
        child: AnimatedOpacity(
          duration: const Duration(milliseconds: 320),
          opacity: _expanded ? 1.0 : 0.0,
          child: const Text('Details that only make sense when open'),
        ),
      ),
    );
  }
}
```

Hai điểm hay bị sai ở đây. Thứ nhất, `AnimatedContainer` không nhận đồng thời `color` và `decoration` — đặt màu vào bên trong `BoxDecoration`. Thứ hai, chuyện bị ngắt giữa chừng được xử lý tốt hơn bạn tưởng: khi giá trị đích đổi lúc animation đang chạy, `begin` của tween nội bộ được đặt lại bằng giá trị *đang hiển thị*, rồi controller chạy lại từ đầu. Vị trí không bao giờ nhảy. Nhưng duration thì chạy lại thật, nên một tấm card bị chạm liên tục vẫn mất trọn 320 ms tính từ chỗ nó đang ở.

Khi không có widget `Animated*` nào phủ đúng thuộc tính bạn cần, `TweenAnimationBuilder` cho bạn đúng mô hình khai báo đó trên một giá trị bất kỳ:

```dart
TweenAnimationBuilder<double>(
  tween: Tween<double>(begin: 0.0, end: _expanded ? 1.0 : 0.0),
  duration: const Duration(milliseconds: 320),
  curve: Curves.easeOutCubic,
  builder: (context, t, child) =>
      Transform.rotate(angle: t * math.pi, child: child),
  child: const Icon(Icons.expand_more),
)
```

Cái bẫy ở đây là `begin`. Nó chỉ có tác dụng ở lần build đầu tiên. Mọi lần rebuild sau đó, widget animate từ chỗ nó đang ở tới `end` mới, còn đổi `begin` thì không tạo ra khác biệt nào. Nhiều người viết `begin: _expanded ? 1 : 0` rồi ngồi cả buổi chiều tự hỏi sao không thấy gì thay đổi.

## Vẫn tấm card đó, với controller do bạn giữ

Bản explicit tốn thêm khoảng mười lăm dòng và đổi lại cho bạn một cái đồng hồ có thể chỉ tay vào: đảo chiều giữa chừng, chạy hai widget từ cùng một nguồn, đọc status, hoặc sau này giao nó cho một simulation.

```dart
// The StatefulWidget shell is identical to the one above; the State is
// where everything interesting happens.
class _ExplicitCardState extends State<ExplicitCard>
    with SingleTickerProviderStateMixin {
  static final _width = Tween<double>(begin: 200, end: 320);
  static final _height = Tween<double>(begin: 96, end: 220);
  static final _radius = Tween<double>(begin: 12, end: 24);
  static final _color =
      ColorTween(begin: Colors.indigo.shade400, end: Colors.indigo.shade700);

  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 320),
    reverseDuration: const Duration(milliseconds: 220),
  );

  late final CurvedAnimation _open = CurvedAnimation(
    parent: _controller,
    curve: Curves.easeOutCubic,
    reverseCurve: Curves.easeInCubic,
  );

  @override
  void dispose() {
    _open.dispose();
    _controller.dispose();
    super.dispose();
  }

  void _toggle() {
    final status = _controller.status;
    if (status == AnimationStatus.completed ||
        status == AnimationStatus.forward) {
      _controller.reverse();
    } else {
      _controller.forward();
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _toggle,
      child: AnimatedBuilder(
        animation: _open,
        builder: (context, child) => Container(
          width: _width.evaluate(_open),
          height: _height.evaluate(_open),
          decoration: BoxDecoration(
            color: _color.evaluate(_open),
            borderRadius: BorderRadius.circular(_radius.evaluate(_open)),
          ),
          child: Opacity(opacity: _open.value, child: child),
        ),
        // Built once, not once per frame. See the next section.
        child: const Padding(
          padding: EdgeInsets.all(16),
          child: Text('Details that only make sense when open'),
        ),
      ),
    );
  }
}
```

`vsync: this` chính là thứ ngăn animation này chạy khi widget đã ra khỏi màn hình. `SingleTickerProviderStateMixin` cấp một `Ticker` bị tắt tiếng khi `TickerMode` bao quanh bị vô hiệu hóa — đúng chuyện xảy ra với một route bị đẩy xuống dưới một route khác. Dùng `SingleTickerProviderStateMixin` cho đúng một controller; nó sẽ assert nếu bạn tạo cái thứ hai. Cần nhiều thì dùng `TickerProviderStateMixin`.

`dispose()` không phải chuyện vệ sinh, nó là chuyện đúng/sai. Một `AnimationController` giữ một `Ticker` đã đăng ký với scheduler, và bản thân nó là một `ChangeNotifier` mà widget của bạn đã subscribe. Bỏ `State` đi mà không dispose thì ticker vẫn tiếp tục xin frame cho một widget đã biến mất; ở bản debug, ticker provider sẽ assert rất ồn ào khi `State` bị dispose lúc ticker còn chạy — đó là Flutter đang báo một rò rỉ thật, không phải khó tính. `CurvedAnimation` cũng có `dispose()` — nó gắn một status listener vào parent — nên hãy khai báo field kiểu `CurvedAnimation` chứ đừng `Animation<double>`, không thì bạn không gọi được.

Nếu widget được animate nhỏ và khép kín, `AnimatedWidget` nói cùng một chuyện với ít tầng thụt lề hơn:

```dart
class _SlidingCard extends AnimatedWidget {
  const _SlidingCard({required Animation<double> offset, required this.child})
      : super(listenable: offset);

  final Widget child;
  Animation<double> get _offset => listenable as Animation<double>;

  @override
  Widget build(BuildContext context) =>
      Transform.translate(offset: Offset(_offset.value, 0), child: child);
}
```

Field `child` ở đây được parent truyền vào dưới dạng đã dựng sẵn, nên nó sống sót qua mọi lần rebuild vì đúng lý do mà `child` của `AnimatedBuilder` sống sót — framework so sánh instance của widget và bỏ qua những subtree không đổi identity.

## Hất card đi cần một simulation, không phải một duration

Giờ tới phần implicit animation không làm được. Người dùng kéo tấm card rồi thả ra ở tốc độ 1.400 logical pixel mỗi giây. Bạn truyền duration bao nhiêu? Không có con số nào cả — câu trả lời đúng là "lâu bằng đúng thời gian một vật đang đi ở tốc độ đó cần để dừng lại", và đó là một câu hỏi vật lý.

```dart
class FlingableCard extends StatefulWidget {
  const FlingableCard({super.key, this.onDismissed});
  final VoidCallback? onDismissed;
  @override
  State<FlingableCard> createState() => _FlingableCardState();
}

class _FlingableCardState extends State<FlingableCard>
    with SingleTickerProviderStateMixin {
  // The controller's value is a horizontal offset in logical pixels,
  // not a 0..1 progress value. Hence `unbounded`.
  late final AnimationController _drag =
      AnimationController.unbounded(vsync: this);

  static final _returnSpring = SpringDescription.withDampingRatio(
    mass: 1,
    stiffness: 400,
    ratio: 0.75, // under 1.0 = a little overshoot on the way back
  );

  @override
  void dispose() {
    _drag.dispose();
    super.dispose();
  }

  void _onDragUpdate(DragUpdateDetails details) {
    // Assigning to `value` stops any running simulation first.
    _drag.value += details.delta.dx;
  }

  void _onDragEnd(DragEndDetails details) {
    final velocity = details.velocity.pixelsPerSecond.dx;
    final width = MediaQuery.sizeOf(context).width;

    // Both numbers are product decisions, not framework constants.
    const dismissVelocity = 800.0;
    final dismissed =
        velocity.abs() > dismissVelocity || _drag.value.abs() > width / 3;

    if (dismissed) {
      final target = _drag.value.isNegative ? -width : width;
      // Nobody watches a card that is already leaving: a curve is fine here.
      _drag
          .animateTo(target,
              duration: const Duration(milliseconds: 180),
              curve: Curves.easeOut)
          .whenComplete(() {
        if (mounted) widget.onDismissed?.call();
      });
    } else {
      // The card comes back. This is where physics earns its keep: the
      // spring starts at the finger's exact position *and* velocity.
      _drag.animateWith(
        SpringSimulation(_returnSpring, _drag.value, 0, velocity),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onHorizontalDragUpdate: _onDragUpdate,
      onHorizontalDragEnd: _onDragEnd,
      child: AnimatedBuilder(
        animation: _drag,
        builder: (context, child) =>
            Transform.translate(offset: Offset(_drag.value, 0), child: child),
        child: const _CardBody(),
      ),
    );
  }
}
```

Ba chi tiết đáng nhớ nằm lòng.

**Đơn vị phải khớp nhau.** `details.velocity.pixelsPerSecond` tính bằng logical pixel mỗi giây. Tham số vận tốc của simulation tính bằng đơn vị *của controller* mỗi giây. Vì controller này đếm theo pixel nên bạn truyền thẳng vào được. Nếu controller của bạn chạy từ 0 tới 1 trên quãng đường 300 pixel thì phải chia cho 300 trước — và khi một cú fling cảm giác hoặc tức thì hoặc chậm như rùa, gần như luôn luôn là vì chuyện này.

**`fling()` là lối tắt, không phải trường hợp tổng quát.** `AnimationController.fling(velocity: v)` chạy một lò xo cứng có sẵn hướng về `upperBound` khi `v` dương và về `lowerBound` khi `v` âm. Rất hợp cho một toggle 0-tới-1 bị hất bằng cử chỉ, và vô dụng khi đích đến không phải một trong hai biên.

**`animateWith` trả về một `TickerFuture` vẫn hoàn tất kể cả khi bị hủy.** Dispose controller giữa chừng sẽ hủy ticker, còn future thường thì vẫn complete — nên một callback `.whenComplete` có gọi `setState` hay gọi ngược lên parent thì cần chốt `mounted` như ở trên. Dùng `.orCancel` nếu bạn muốn việc bị hủy nổi lên thành một lỗi.

Riêng với trường hợp vuốt-để-xóa trong danh sách, framework đã có sẵn `Dismissible` làm đúng toàn bộ chuyện này với `onDismissed` và ngưỡng cấu hình được. Hãy tự viết simulation khi chuyển động thực sự đặc thù, đừng viết để dựng lại một hàng danh sách.

## Tham số `child` chính là lý do AnimatedBuilder tồn tại

Builder của `AnimatedBuilder` chạy mỗi frame một lần. Ở 120 Hz nghĩa là 120 lần rebuild mỗi giây cho mọi thứ nằm bên trong nó. Đây là lỗi hiệu năng phổ biến nhất trong code animation Flutter:

```dart
// Every frame rebuilds the Column, the Text widgets, the icons, all of it.
AnimatedBuilder(
  animation: _controller,
  builder: (context, child) => Transform.scale(
    scale: _controller.value,
    child: ExpensiveCardBody(item: item),
  ),
)

// ExpensiveCardBody is constructed once. The builder wraps the same
// instance every frame, and the element layer skips it entirely.
AnimatedBuilder(
  animation: _controller,
  builder: (context, child) =>
      Transform.scale(scale: _controller.value, child: child),
  child: ExpensiveCardBody(item: item),
)
```

Cơ chế này đáng biết vì nó giải thích luôn giới hạn: khi Flutter đối chiếu cây widget, nó so widget mới với widget cũ, và một *instance giống hệt* sẽ làm quá trình cập nhật dừng ngay tại đó. `child` bạn đưa cho `AnimatedBuilder` được `State` của nó giữ lại và trả về nguyên vẹn, nên subtree đó không bao giờ bị rebuild. Mẹo này chỉ áp dụng được cho phần subtree không phụ thuộc vào giá trị animation. Nếu nửa tấm card phụ thuộc vào nó, hãy tách tấm card ra.

`ListenableBuilder` là chính widget đó tổng quát hóa cho mọi `Listenable`, còn các widget transition có sẵn — `FadeTransition`, `ScaleTransition`, `SlideTransition`, `SizeTransition`, `DecoratedBoxTransition` — làm đúng mẹo này bên trong mà không cần builder nào cả. Nếu có một transition widget phủ đúng nhu cầu, hãy dùng nó; ít bộ phận chuyển động hơn, và không ai bị cám dỗ rebuild cả thế giới.

## Animate phần paint trước khi động tới layout

`AnimatedContainer(width: ...)` trông vô hại và là đoạn code đắt nhất trong cả bài này. Đổi width sẽ đánh dấu render object bẩn ở khâu **layout**, nên mỗi frame đều phải chạy layout, rồi paint, rồi compositing. Tệ hơn, layout lan ra: một tấm card nở ra trong `Column` sẽ đẩy các widget anh em, nên parent cũng phải layout lại, và bên trong một `ListView` thì điều đó có thể có nghĩa là tính lại vị trí các item ở từng frame của animation.

`Transform.scale`, `Transform.translate`, `FadeTransition` và `DecoratedBoxTransition` không đụng gì tới layout. Chúng chỉ ảnh hưởng tới paint, nên khâu layout bị bỏ qua hoàn toàn và công việc còn lại chỉ là một ma trận hoặc một opacity layer.

Những quy tắc tôi thực sự áp dụng:

- Phản hồi khi nhấn, nhấc lên khi hover, rung, trượt vào, cross-fade → dùng transform hoặc fade. Đừng đụng tới kích thước.
- Mở rộng để *dòng chảy nội dung thật sự sắp xếp lại* → `AnimatedSize` hoặc `SizeTransition`, và chấp nhận chi phí layout, vì phóng to chữ không giống với việc để lộ ra chữ.
- Bọc subtree đang animate trong một `RepaintBoundary` để những lần repaint của nó không làm bẩn phần còn lại của màn hình. Lưu ý cái này chỉ giúp cho paint — nó không làm gì được cho một animation chạy bằng layout.
- Nếu bạn đang animate kích thước của nhiều item trong danh sách cùng lúc, đó là vấn đề thiết kế chứ không phải vấn đề của Flutter.

Một cái bẫy liên quan: widget đã mờ về opacity 0 vẫn còn nằm trong cây. Nó vẫn build, vẫn chiếm chỗ layout, và vẫn tham gia hit test trừ khi bạn bọc thêm `IgnorePointer`. "Vô hình" và "biến mất" là hai trạng thái khác nhau, và một tấm card vô hình nuốt mất cú chạm sẽ được người dùng báo lỗi là "cái nút không bấm được".

## Curve là một quyết định thiết kế, không phải giá trị mặc định

Mọi widget implicit đều mặc định `Curves.linear`, còn `CurvedAnimation` bắt bạn nêu tên một curve vì không có mặc định nào hợp lý. Chuyển động tuyến tính là dấu hiệu nhận dạng của một animation không ai suy nghĩ về nó — vật thể thật có tăng tốc và giảm tốc, và mắt người nhận ra ngay khi chúng không làm vậy.

| Tình huống | Điểm khởi đầu hợp lý |
|---|---|
| Phần tử đi vào, nở ra, vừa tới nơi | `Curves.easeOut` / `Curves.easeOutCubic` |
| Phần tử rời đi, thu lại | `Curves.easeIn` / `Curves.easeInCubic` |
| Di chuyển giữa hai vị trí đang hiện trên màn hình | `Curves.fastOutSlowIn` |
| Chuyển động emphasized theo Material 3 | `Curves.easeInOutCubicEmphasized` |
| Xác nhận vui mắt, một badge bật ra | `Curves.easeOutBack`, `Curves.elasticOut` |

Ba điều cần nhớ. Lúc vào và lúc ra thường muốn curve *khác nhau* và duration khác nhau — đó là lý do có `reverseCurve` và `reverseDuration`, và đóng nhanh hơn mở là kiểu bất đối xứng phổ biến. Thứ hai, các curve có overshoot sinh ra giá trị nằm ngoài khoảng 0 tới 1; `Opacity` assert đúng khoảng đó ở bản debug, nên một hiệu ứng mờ dùng `Curves.elasticOut` sẽ crash trong khi `FadeTransition` — vốn có kẹp giá trị — thì không. Thứ ba, đừng áp curve hai lần — một `CurvedAnimation` nuôi một tween đã `.chain` sẵn với `CurveTween` sẽ tạo ra chuyển động không ai thiết kế cả.

## Khi nào mỗi kiểu là công cụ sai

| | Dùng khi | Sai khi |
|---|---|---|
| **Implicit** | Một thuộc tính widget đổi theo state, chuyển động ngắn, không có gì khác cần đồng bộ | Bạn cần đảo chiều từ một điểm bất kỳ, điều phối nhiều widget, phản ứng với lúc kết thúc ngoài `onEnd`, hoặc đi tiếp một cử chỉ |
| **Explicit** | Nhiều thuộc tính hoặc nhiều widget dùng chung một đồng hồ, bạn cần `status`, stagger, `repeat()`, hoặc kiểm soát chính xác lúc bắt đầu và dừng | Chỉ một thuộc tính bật tắt theo bool — bạn đang viết một controller, một mixin và một `dispose` để thay cho bốn dòng |
| **Physics** | Animation đi tiếp một cử chỉ, hoặc chuyển động cần cảm giác có khối lượng — lò xo, fling, snap, rubber-band | Chuyển động có spec cố định ("300 ms ease-out"), vì thời lượng của một simulation là hệ quả của phép tính chứ không thể ra lệnh |

Chuyện này cũng lộ ra trong test. `tester.pumpAndSettle()` bơm frame cho tới khi không còn frame nào được lên lịch, nên nó chạy tốt với implicit, với explicit và cả với spring simulation — lò xo có kết thúc vì `Simulation.isDone` so sánh với một mức dung sai. Nó sẽ timeout với bất cứ thứ gì chạy bằng `repeat()`, và với một controller không ai dừng lại. Khi một widget test treo mà không rõ lý do, một animation không bao giờ kết thúc là chỗ đầu tiên nên nhìn vào.

## FAQ

**Implicit animation có chậm hơn explicit không?**

Không — bên dưới, một widget implicit chính là một `StatefulWidget` với `AnimationController` riêng, nên chi phí mỗi frame vẫn là bộ máy đó. Khác biệt về hiệu năng đến từ việc bạn animate *cái gì* (layout hay paint) và bạn rebuild bao nhiêu subtree mỗi frame, chứ không đến từ việc chọn API nào.

**Tôi có thể kết hợp cử chỉ với implicit animation không?**

Chỉ ở mức thô. Bạn có thể cập nhật state lúc thả tay rồi để `AnimatedContainer` trượt tới đích mới, nhưng animation bắt đầu ở vận tốc bằng không, nên chuyển động đứt gãy thấy rõ so với ngón tay. Bất kỳ tương tác nào cần vận tốc lúc thả tay đi tiếp đều cần một controller và một simulation.

**Dùng `TweenAnimationBuilder` hay `AnimatedOpacity` thì có phải `dispose()` không?**

Không. Những widget đó tự giữ controller bên trong và dispose cùng `State` của chính chúng. Bạn chỉ gánh nghĩa vụ dispose khi tự khởi tạo một `AnimationController`, một `CurvedAnimation`, hoặc bất cứ thứ gì đăng ký một listener hay một ticker thay bạn.

**Chọn hằng số cho lò xo thế nào cho ra cảm giác đúng?**

Bắt đầu từ `SpringDescription.withDampingRatio` thay vì đặt damping thô: ratio bằng 1.0 là tắt dần tới hạn, dừng lại mà không vọt lố; dưới 1.0 thì nảy; trên 1.0 thì bò vào chậm chạp. Sau đó chỉnh `stiffness` cho tốc độ và cứ để `mass` bằng 1 trừ khi có lý do. Chỉnh theo cảm giác trên máy thật hơn hẳn việc ngồi suy luận về mấy con số.

**Có nên tôn trọng thiết lập "giảm chuyển động" của hệ thống không?**

Có. `MediaQuery.disableAnimationsOf(context)` cho bạn biết khi người dùng đã bật nó, và một `AnimationController` tạo với `AnimationBehavior.normal` mặc định sẽ tự rút ngắn duration xuống rất nhiều khi cờ đó được bật. Chuyển động chạy bằng physics thì không được xử lý tự động, nên hãy kiểm tra cờ này và nhảy thẳng tới trạng thái cuối.

---

*Những hành vi API mô tả ở đây — việc một spring simulation kết thúc dựa trên dung sai, phép so sánh identity khiến tham số `child` có tác dụng, cái assert khoảng giá trị của `Opacity` — là cách framework hoạt động, không phải quan điểm. Các gợi ý về curve, hằng số lò xo và ngưỡng dismiss là khẩu vị, và khẩu vị của bạn có thể khác. Mọi thứ phụ thuộc phiên bản nên được đối chiếu với tài liệu API Flutter hiện hành trước khi bạn dựa vào nó.*
