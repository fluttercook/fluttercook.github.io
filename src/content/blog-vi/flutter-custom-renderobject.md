---
title: "Khi ghép widget không còn đủ: tự viết RenderObject"
description: "Thang leo từ Row/Column tới CustomPaint, CustomMultiChildLayout rồi tới RenderBox thật — kèm một layout staggered flow hoàn chỉnh đã test, với performLayout, computeDryLayout, paint, hit test và ParentData."
seoDescription: "Tự viết RenderBox trong Flutter: performLayout, computeDryLayout, paint, hitTestChildren, ParentData và markNeedsLayout vs markNeedsPaint, kèm code đầy đủ."
keywords:
  - flutter custom renderobject
  - flutter renderbox performlayout
  - multichildrenderobjectwidget ví dụ
  - flutter computedrylayout
  - containerrenderobjectmixin parentdata
  - tự viết layout flutter
category: "Chuyên sâu"
topic: "Rendering"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧩"
tags: ["Flutter", "RenderObject", "Layout", "Rendering"]
sources:
  - name: "RenderBox class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/rendering/RenderBox-class.html"
  - name: "MultiChildRenderObjectWidget class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/MultiChildRenderObjectWidget-class.html"
  - name: "ContainerRenderObjectMixin — Flutter API docs"
    url: "https://api.flutter.dev/flutter/rendering/ContainerRenderObjectMixin-mixin.html"
  - name: "ParentDataWidget class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/ParentDataWidget-class.html"
  - name: "Understanding constraints — Flutter docs"
    url: "https://docs.flutter.dev/ui/layout/constraints"
  - name: "Inside Flutter — Flutter docs"
    url: "https://docs.flutter.dev/resources/inside-flutter"
related:
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
draft: false
---

Bạn hẳn từng gặp tình huống này. Thiết kế là một feed masonry hai cột: các card cao thấp khác nhau, mỗi card mới rơi vào cột nào đang ngắn nhất, thỉnh thoảng chen một banner chiếm trọn chiều ngang. Bạn thử `Wrap` — mỗi hàng lấy chiều cao của child cao nhất, thế là hở khoảng trắng. Bạn thử hai `Column` trong một `Row` rồi tự chia danh sách — nhưng không thể chia đúng nếu chưa biết mỗi card render ra cao bao nhiêu, mà điều đó chỉ biết được sau khi layout. Bạn thử `Stack` với `Positioned`, và bây giờ bạn cần chiều cao của từng card dưới dạng con số, ngay trong build, trước khi có gì được đo.

Cái bẫy nằm ở chỗ tất cả đều là câu trả lời kiểu *ghép widget* cho một bài toán *đo đạc*. Row, Column, Stack, Wrap bản thân chúng là các render object với thuật toán layout cố định. Lồng chúng vào nhau không tạo ra thuật toán mới; nó chỉ tạo ra một cây cao hơn chạy đúng ba thuật toán cũ. Khi hình dạng bạn cần thực sự là một thuật toán khác — một quyết định đặt vị trí phụ thuộc vào kích thước đã đo của các sibling trước đó — thì lồng bao nhiêu tầng cũng không tới.

Đây là lúc bạn viết một `RenderBox`. Nó không bí hiểm như tiếng đồn: layout bên dưới gói gọn trong khoảng 120 dòng, dùng những API đã ổn định nhiều năm. Phần người ta hay làm sai lại là phần không ai nhắc tới — dry layout, intrinsics, và chọn đúng lời gọi "đánh dấu bẩn" trong setter.

Toàn bộ code ở đây được viết trên Flutter 3.44 stable, `flutter analyze` sạch, và được kiểm chứng bằng widget test khẳng định chính xác offset của từng child, kích thước dry layout và kết quả hit test.

## Cái thang: phần lớn bài toán dừng trước nấc cuối

Leo theo thứ tự. Mỗi nấc tốn công viết và công bảo trì hơn nấc dưới, và dừng sớm không phải là thỏa hiệp — với đa số layout, đó mới là câu trả lời đúng.

| Nấc | Dùng khi | Chỗ nó hết đường |
| --- | --- | --- |
| Ghép widget (`Row`, `Column`, `Stack`, `Wrap`, `LayoutBuilder`) | Hình dạng diễn đạt được bằng cách lồng nhau | Vị trí không thể phụ thuộc kích thước đã đo của sibling |
| `CustomPaint` | Bạn cần *pixel* — cung tròn, gradient, vạch chia — chứ không phải child | Nó vẽ; nó không layout child |
| `Flow` | Muốn dời chỗ các child đã có size một cách rẻ, thường là mỗi frame | `FlowDelegate.getSize` chỉ thấy constraints, không thấy child |
| `CustomMultiChildLayout` | Bạn tự đặt vị trí child dựa trên kích thước cha đã biết | Cùng giới hạn: kích thước không thể phản ánh kích thước của các child |
| `RenderBox` tự viết | Kích thước cha phụ thuộc child, hoặc bạn cần intrinsics, baseline, hit test riêng | Không giới hạn — bạn sở hữu toàn bộ thuật toán |

Dòng thứ tư mới là thứ đẩy người ta qua ranh giới. `CustomMultiChildLayout` trông như đủ cho masonry, và nó đặt card chính xác thật — nhưng chiều cao của chính nó đến từ `MultiChildLayoutDelegate.getSize(constraints)`, được gọi *trước* khi bất kỳ child nào được layout và không nhìn thấy chúng. Một masonry không tự co giãn theo nội dung thì vô dụng bên trong scroll view.

## Ba cây, nhưng bạn chỉ cần nhớ hai điều

Flutter giữ ba cây song song. Cây **Widget** là cấu hình immutable, được rebuild liên tục và vứt đi rất rẻ. Cây **Element** là tầng trung gian sống lâu, quyết định widget mới sẽ cập nhật element cũ hay thay thế nó. Cây **RenderObject** là nơi layout, paint và hit test thực sự diễn ra; nó mutable và đắt để tạo mới.

Hai hệ quả quan trọng cho code bên dưới. Thứ nhất, một `RenderObjectWidget` không *chứa* render object; nó *tạo và cấu hình* render object. `createRenderObject` chạy một lần khi element được mount. Mọi lần rebuild sau đó gọi `updateRenderObject` với đúng instance cũ — nên render object cần các field có setter, không phải final.

Thứ hai, vì render object sống sót qua các lần rebuild, đổi một field như vậy thì phải tự tay báo cho pipeline biết cái gì đã cũ. Không có gì làm hộ bạn. Đó là lý do mọi setter trong render object đều theo một khuôn: thoát nếu không đổi, gán, rồi đánh dấu bẩn.

| Lời gọi | Ý nghĩa | Trường hợp điển hình |
| --- | --- | --- |
| `markNeedsLayout()` | Kích thước hoặc vị trí đổi; paint sau đó là hệ quả kèm theo | spacing, số cột, mọi thứ đi vào `performLayout` |
| `markNeedsPaint()` | Cùng hình học, khác pixel | màu, độ dày nét, thiết lập chỉ ảnh hưởng trang trí |
| `markNeedsSemanticsUpdate()` | Mô tả accessibility đổi | label, flag |

Gọi `markNeedsLayout` trong khi `markNeedsPaint` là đủ thì bạn tốn một lượt layout thừa cho cả subtree; gọi `markNeedsPaint` trong khi cần layout thì hình học cũ nằm lì trên màn hình. Lỗi thứ hai khó phát hiện hơn nhiều, nên khi phân vân, cứ đánh dấu layout.

## Constraints đi xuống, size đi lên, cha đặt vị trí

Một câu đó chi phối tất cả. Cụ thể, trong `performLayout`:

- Cha đưa cho bạn `constraints` (một `BoxConstraints`: min/max width và height). Bạn phải tạo ra một `size` thỏa mãn nó. `constraints.constrain(someSize)` sẽ kẹp giá trị giúp bạn.
- Bạn dựng một `BoxConstraints` cho từng child rồi gọi `child.layout(childConstraints, parentUsesSize: true)`. Cờ `parentUsesSize` không phải trang trí — nó nói cho framework biết layout của bạn phụ thuộc size của child, nên khi child layout lại thì phải lan ngược lên bạn. Sai cờ này sẽ sinh ra layout cũ kỹ chỉ lộ ra trong vài thứ tự rebuild nhất định.
- Sau khi layout xong một child, bạn được phép đọc `child.size` — nhưng **chỉ khi** bạn đã truyền `parentUsesSize: true`.
- Child không bao giờ biết hay tự đặt vị trí của mình. Cha ghi vị trí đó vào `parentData.offset` của child.

Helper `ChildLayoutHelper.layoutChild` dùng bên dưới chính là `child.layout(constraints, parentUsesSize: true)` rồi trả về `child.size`, còn người anh em `ChildLayoutHelper.dryLayoutChild` là `child.getDryLayout(constraints)`. Dùng cặp này cho phép một hàm phục vụ cả layout thật lẫn dry layout, và đó là mẹo giữ cho hai đường không lệch nhau.

## Render object lá: ví dụ nhỏ nhất mà vẫn có ích

Bắt đầu với trường hợp không có child nào. `LeafRenderObjectWidget` là lớp cơ sở cho widget mà render object của nó không có child. Đây là một cây thước lấp đầy chiều ngang khả dụng và vẽ các vạch chia:

```dart
import 'dart:math' as math;

import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';

class Ruler extends LeafRenderObjectWidget {
  const Ruler({super.key, this.thickness = 24.0, this.color = const Color(0xFF546E7A)});

  final double thickness;
  final Color color;

  @override
  RenderRuler createRenderObject(BuildContext context) =>
      RenderRuler(thickness: thickness, color: color);

  @override
  void updateRenderObject(BuildContext context, RenderRuler renderObject) {
    renderObject
      ..thickness = thickness
      ..color = color;
  }
}

class RenderRuler extends RenderBox {
  RenderRuler({required double thickness, required Color color})
      : _thickness = thickness,
        _color = color;

  static const double _tickSpacing = 8.0;

  double _thickness;
  double get thickness => _thickness;
  set thickness(double value) {
    if (_thickness == value) return;
    _thickness = value;
    markNeedsLayout(); // changes the size we ask for
  }

  Color _color;
  Color get color => _color;
  set color(Color value) {
    if (_color == value) return;
    _color = value;
    markNeedsPaint(); // same size, different pixels
  }

  @override
  bool get sizedByParent => true;

  @override
  Size computeDryLayout(BoxConstraints constraints) =>
      constraints.constrain(Size(double.infinity, thickness));

  @override
  void paint(PaintingContext context, Offset offset) {
    final Paint paint = Paint()
      ..color = color
      ..strokeWidth = 1.0;
    final int tickCount = (size.width / _tickSpacing).floor();
    for (int i = 0; i <= tickCount; i++) {
      final double x = i * _tickSpacing;
      final double height = i % 5 == 0 ? size.height : size.height / 2;
      context.canvas.drawLine(offset + Offset(x, size.height - height),
          offset + Offset(x, size.height), paint);
    }
  }
}
```

Hai chi tiết đáng mang đi dùng lại. `sizedByParent => true` tuyên bố rằng size là hàm thuần của constraints đầu vào; framework khi đó gọi `computeDryLayout` từ `performResize`, và `performLayout` mặc định của `RenderBox` trở thành no-op hợp lệ, nên bạn không cần viết nó. Và `offset` trong `paint` không phải vị trí của bạn trên màn hình — nó là chỗ mà cha quyết định cho bạn vẽ. Hãy cộng nó vào mọi tọa độ. Quên nó thì widget render đúng ở góc trên bên trái màn hình và sai ở mọi nơi khác.

## Layout mà Row, Column và Stack không diễn đạt nổi

Giờ tới phần chính: các child được xếp vào N cột, mỗi child rơi vào cột đang ngắn nhất, cộng thêm banner chiếm trọn chiều ngang. Có nhiều child nghĩa là thêm ba mảnh — một lớp con của `ParentData` giữ offset cho từng child, `ContainerRenderObjectMixin` quản lý danh sách liên kết các child, và `RenderBoxContainerDefaultsMixin` cho các lượt paint và hit test mặc định.

```dart
class StaggeredFlowParentData extends ContainerBoxParentData<RenderBox> {
  bool fullWidth = false;
}

class StaggeredFlow extends MultiChildRenderObjectWidget {
  const StaggeredFlow({
    super.key,
    this.columnCount = 2,
    this.spacing = 8.0,
    super.children,
  }) : assert(columnCount > 0);

  final int columnCount;
  final double spacing;

  @override
  RenderStaggeredFlow createRenderObject(BuildContext context) {
    return RenderStaggeredFlow(columnCount: columnCount, spacing: spacing);
  }

  @override
  void updateRenderObject(
      BuildContext context, RenderStaggeredFlow renderObject) {
    renderObject
      ..columnCount = columnCount
      ..spacing = spacing;
  }
}
```

`ContainerBoxParentData<RenderBox>` đã sẵn có `offset` (từ `BoxParentData`) và `nextSibling` / `previousSibling` (từ `ContainerParentDataMixin`). Bạn kế thừa nó chỉ để thêm field riêng của mình — ở đây là một biến bool.

Phần khai báo và setter của render object:

```dart
class RenderStaggeredFlow extends RenderBox
    with
        ContainerRenderObjectMixin<RenderBox, StaggeredFlowParentData>,
        RenderBoxContainerDefaultsMixin<RenderBox, StaggeredFlowParentData> {
  RenderStaggeredFlow({required int columnCount, required double spacing})
      : assert(columnCount > 0),
        _columnCount = columnCount,
        _spacing = spacing;

  int _columnCount;
  int get columnCount => _columnCount;
  set columnCount(int value) {
    assert(value > 0);
    if (_columnCount == value) return;
    _columnCount = value;
    markNeedsLayout();
  }

  double _spacing;
  double get spacing => _spacing;
  set spacing(double value) {
    if (_spacing == value) return;
    _spacing = value;
    markNeedsLayout();
  }

  @override
  void setupParentData(RenderObject child) {
    if (child.parentData is! StaggeredFlowParentData) {
      child.parentData = StaggeredFlowParentData();
    }
  }
```

`setupParentData` được framework gọi cho từng child khi child được nhận vào. Cái guard `is!` rất quan trọng: thiếu nó, một child chuyển qua lại giữa hai cha cùng kiểu sẽ bị vứt parent data và dựng lại mỗi lần gắn vào.

## Một thuật toán, hai lối vào

`performLayout` và `computeDryLayout` phải khớp nhau, nếu không `IntrinsicHeight`, `Table` và vài sliver sẽ đo một đằng mà render một nẻo. Khác biệt duy nhất là dry layout không được phép thay đổi trạng thái — không `size =`, không ghi offset, và child được đo bằng `getDryLayout` thay vì bị layout thật. Vậy nên hãy viết thuật toán một lần với một cờ `dry`:

```dart
  double _columnWidth(double maxWidth) {
    final double available = maxWidth - spacing * (columnCount - 1);
    return math.max(0.0, available / columnCount);
  }

  Size _runLayout(BoxConstraints constraints, {required bool dry}) {
    assert(() {
      if (constraints.hasBoundedWidth) return true;
      throw FlutterError(
        'StaggeredFlow was given unbounded width.\n'
        'It divides the incoming maxWidth into columns, so it cannot be '
        'placed directly inside a horizontal ListView or an unconstrained Row. '
        'Wrap it in a SizedBox or an Expanded first.',
      );
    }());

    final ChildLayouter layoutChild =
        dry ? ChildLayoutHelper.dryLayoutChild : ChildLayoutHelper.layoutChild;
    final double width = constraints.maxWidth;
    final double columnWidth = _columnWidth(width);
    final List<double> columnBottoms = List<double>.filled(columnCount, 0.0);

    RenderBox? child = firstChild;
    while (child != null) {
      final StaggeredFlowParentData childParentData =
          child.parentData! as StaggeredFlowParentData;

      if (childParentData.fullWidth) {
        double top = 0.0;
        for (final double bottom in columnBottoms) {
          top = math.max(top, bottom);
        }
        final Size childSize =
            layoutChild(child, BoxConstraints.tightFor(width: width));
        if (!dry) {
          childParentData.offset = Offset(0.0, top);
        }
        final double next = top + childSize.height + spacing;
        for (int i = 0; i < columnCount; i++) {
          columnBottoms[i] = next;
        }
      } else {
        int target = 0;
        for (int i = 1; i < columnCount; i++) {
          if (columnBottoms[i] < columnBottoms[target]) target = i;
        }
        final Size childSize =
            layoutChild(child, BoxConstraints.tightFor(width: columnWidth));
        if (!dry) {
          childParentData.offset =
              Offset(target * (columnWidth + spacing), columnBottoms[target]);
        }
        columnBottoms[target] += childSize.height + spacing;
      }

      child = childParentData.nextSibling;
    }

    double contentHeight = 0.0;
    for (final double bottom in columnBottoms) {
      contentHeight = math.max(contentHeight, bottom);
    }
    if (contentHeight > 0.0) {
      contentHeight -= spacing; // drop the trailing gap
    }
    return constraints.constrain(Size(width, contentHeight));
  }

  @override
  void performLayout() {
    size = _runLayout(constraints, dry: false);
  }

  @override
  Size computeDryLayout(BoxConstraints constraints) {
    return _runLayout(constraints, dry: true);
  }
```

Hãy đọc kỹ dòng chảy constraints, vì đây là chỗ các layout tự viết hay vỡ. Mỗi child nhận `BoxConstraints.tightFor(width: columnWidth)` — width chặt cứng, còn height để nguyên khoảng `0..vô hạn`. Đó mới là điểm mấu chốt: child bị ép đúng bề rộng một cột và được phép cao đúng bằng nó muốn, và chính điều đó tạo ra hiệu ứng so le. Chiều cao của cha khi đó là cột cao nhất, còn chiều rộng của cha là `maxWidth` đầu vào, được kẹp qua `constraints.constrain` để không bao giờ vi phạm điều mà cha của chúng ta yêu cầu.

Nếu thuật toán của bạn thực sự không tính được nếu chưa layout child — ví dụ nó phụ thuộc baseline của child — thì đừng giả vờ có dry layout. Hãy gọi `debugCannotComputeDryLayout` bên trong một assert và trả về `Size.zero`, để việc dùng sai vỡ ồn ào ở debug thay vì đo sai âm thầm ở release.

## Paint và hit test là hai mặt của cùng bộ offset

Vì vị trí của mọi child nằm trong `parentData.offset`, cả hai lượt duyệt đều là một dòng lấy từ `RenderBoxContainerDefaultsMixin`:

```dart
  @override
  void paint(PaintingContext context, Offset offset) {
    defaultPaint(context, offset);
  }

  @override
  bool hitTestChildren(BoxHitTestResult result, {required Offset position}) {
    return defaultHitTestChildren(result, position: position);
  }
```

`defaultPaint` duyệt child theo thứ tự chèn và gọi `context.paintChild(child, childParentData.offset + offset)`. `defaultHitTestChildren` duyệt **ngược** — vẽ sau cùng thì được hit trước — và đổi tọa độ điểm chạm sang hệ của từng child qua `BoxHitTestResult.addWithPaintOffset`. Chiều ngược đó là lý do child nằm trên cùng thắng cú chạm, và cũng là thứ mà hit test viết tay hay làm sai nhất.

Chỉ tự viết hai hàm này khi bạn đã làm điều gì đó mà bản mặc định không biết: áp clip hay transform, push một layer, hoặc vẽ child sai thứ tự. Nếu đã vẽ kèm transform thì phải hit test bằng transform nghịch đảo, không thì cú chạm rơi sai chỗ.

Hai hành vi nên biết trước thay vì phát hiện khi lên production. `hitTestSelf` mặc định trả `false`, nên các khoảng trống giữa các child là trong suốt với cú chạm; trả `true` nếu cả hộp phải nuốt chúng. Và child không bị clip theo biên của bạn — nếu constraints đầu vào giới hạn chiều cao thấp hơn nội dung, `constrain` sẽ thu nhỏ `size` nhưng child vẫn vẽ tràn ra ngoài. Hãy đặt flow trong scroll view, hoặc bọc bằng `ClipRect`.

## ParentData: dữ liệu theo từng child do cha sở hữu

Cờ `fullWidth` phải nằm ở đâu đó. Nó không thể là field của widget con — child không biết mình đang nằm trong `StaggeredFlow` — và cũng không thể là tham số của widget cha, vì nó khác nhau theo từng child. `ParentData` sinh ra đúng cho việc này: một ô dữ liệu gắn trên mỗi child, do cha sở hữu và ghi, y như cách `Positioned` và `Expanded` hoạt động.

Cây cầu nối là một `ParentDataWidget`:

```dart
class StaggeredBanner extends ParentDataWidget<StaggeredFlowParentData> {
  const StaggeredBanner({super.key, required super.child});

  @override
  void applyParentData(RenderObject renderObject) {
    final StaggeredFlowParentData parentData =
        renderObject.parentData! as StaggeredFlowParentData;
    if (parentData.fullWidth) return;
    parentData.fullWidth = true;
    renderObject.parent?.markNeedsLayout();
  }

  @override
  Type get debugTypicalAncestorWidgetClass => StaggeredFlow;
}
```

Hai nghĩa vụ. `applyParentData` phải so sánh trước khi ghi, và phải đánh dấu bẩn cho *cha*, không phải child — giá trị vừa đổi là đầu vào cho thuật toán layout của cha chứ không phải của child. Và `debugTypicalAncestorWidgetClass` chính là thứ tạo ra thông báo lỗi "incorrect use of ParentDataWidget" dễ đọc khi ai đó thả `StaggeredBanner` ra ngoài `StaggeredFlow`, thay vì một lỗi ép kiểu tối nghĩa sâu trong render tree.

Cách dùng thì rất bình thường:

```dart
StaggeredFlow(
  columnCount: 2,
  spacing: 8,
  children: [
    NoteCard(height: 100),
    NoteCard(height: 40),
    StaggeredBanner(child: SectionHeader('Archive')),
    NoteCard(height: 30),
  ],
)
```

## Những hàm không ai nhắc tới cho tới lúc bị cắn

**Intrinsics mặc định bằng không.** `RenderBox.computeMinIntrinsicWidth` và họ hàng trả về `0.0` nếu bạn không override, và không có cảnh báo nào. Điều đó không sao cho tới khi ai đó bọc widget của bạn trong `IntrinsicHeight`, đặt vào một hàng `Table`, hoặc thả vào một cha không giới hạn — lúc đó nó âm thầm đo ra số không. Vì dry layout của chúng ta chính xác và không gây tác dụng phụ, phần intrinsic height có thể ủy quyền thẳng cho nó, còn intrinsic width là child rộng nhất nhân số cột cộng các khoảng cách:

```dart
  @override
  double computeMinIntrinsicWidth(double height) {
    double widest = 0.0;
    for (RenderBox? child = firstChild; child != null; child = childAfter(child)) {
      widest = math.max(widest, child.getMinIntrinsicWidth(double.infinity));
    }
    return widest * columnCount + spacing * (columnCount - 1);
  }

  @override
  double computeMaxIntrinsicWidth(double height) =>
      computeMinIntrinsicWidth(height);

  @override
  double computeMinIntrinsicHeight(double width) => width.isFinite
      ? _runLayout(BoxConstraints.tightFor(width: width), dry: true).height
      : 0.0;

  @override
  double computeMaxIntrinsicHeight(double width) =>
      computeMinIntrinsicHeight(width);
```

Bỏ bốn override này đi thì flow sẽ đo ra chiều cao bằng không khi nằm trong `IntrinsicHeight` — một widget test khẳng định kích thước render sẽ bắt lỗi ngay. Truy vấn intrinsic duyệt cả subtree và không hề rẻ, nên hãy cài đặt chúng vì tính đúng đắn, đừng vì hiệu năng.

**Baseline tách rời khỏi intrinsics.** Nếu widget của bạn cần canh chữ theo sibling dưới `CrossAxisAlignment.baseline`, hãy override `computeDistanceToActualBaseline` (và trên Flutter hiện đại, cả `computeDryBaseline` cho khớp). Masonry không có baseline có nghĩa, nên để mặc định là đúng ở đây.

**Hãy test hình học, đừng test pixel.** Widget test khẳng định layout trực tiếp được: `tester.getTopLeft(find.byKey(...))` cho offset của child, `tester.getSize(find.byType(StaggeredFlow))` cho cha, `renderObject.getDryLayout(constraints)` so với `renderObject.size` để kiểm tra dry và thật khớp nhau, và một `tapAt` vào vùng chồng lấn để kiểm tra thứ tự hit test. Bốn test kiểu đó bắt gần hết lỗi trong bài này, và chạy trong vài mili giây.

## FAQ

**Khi nào `CustomMultiChildLayout` thực sự là đủ?**
Khi kích thước của cha không phụ thuộc vào child — một mặt đồng hồ với nhãn xếp quanh vòng tròn cỡ cố định, một bong bóng chat có đuôi đặt theo một hộp đã biết, một lớp HUD phủ kín viewport. `getSize` của delegate chỉ nhận constraints, và tài liệu nói rõ kích thước trả về không thể phản ánh kích thước các child. Ngay khi bạn cần "cao bằng cột cao nhất", bạn cần một `RenderBox`.

**Có bắt buộc cài đặt `computeDryLayout` không?**
Không phải lúc nào cũng vậy, nhưng bỏ qua nó có giá của nó. Thiếu nó, `getDryLayout` rơi vào bản cài đặt mặc định — bản này ném lỗi ở debug qua `debugCannotComputeDryLayout` và trả về số không. Mọi thứ đo mang tính thăm dò — `IntrinsicHeight`, vài sliver, `Table` — sẽ hỏng hoặc đo sai. Nếu thuật toán chạy được mà không thay đổi trạng thái, hãy tách ra dùng cờ như trên; nếu thật sự không thể, hãy vỡ ồn ào thay vì trả về một con số đoán.

**Dùng package có hơn không?**
Thường là có. `flutter_staggered_grid_view` trên pub.dev bao trọn ca masonry kèm hỗ trợ sliver, và chọn nó là đúng khi layout thuộc dạng phổ thông. Hãy tự viết khi thuật toán đặc thù cho sản phẩm của bạn, khi bạn cần nó nằm trong render pipeline riêng, hoặc khi ràng buộc của một dependency không hợp với bạn. Hiểu tầng render cũng chính là thứ giúp bạn đọc source của package và đánh giá nó làm đúng hay không.

**Vì sao layout tự viết của tôi layout child hai lần?**
Thường là do `parentUsesSize`. Nếu bạn đọc `child.size` sau `child.layout(constraints)` mà không truyền `parentUsesSize: true`, framework không ghi nhận sự phụ thuộc, nên một lần layout lại của child có thể không lan ngược lên — và chỗ lệch đó lộ ra dưới dạng layout cũ hoặc lặp lại. Hãy dùng `ChildLayoutHelper.layoutChild`, nó truyền cờ giúp bạn, rồi kiểm tra xem có ancestor nào đang đo lại bạn với constraints khác nhau qua từng lượt không.

**`RenderBox` tự viết có nhanh hơn lồng widget không?**
Đôi khi, nhưng đó là lý do sai để viết nó. Gộp năm widget layout lồng nhau thành một render object đúng là bớt node cho lượt layout và paint, và hành vi `RelayoutBoundary` có thể tốt lên. Nhưng lý do thật sự là khả năng diễn đạt — một layout mà bạn không thể viết bằng cách khác. Nếu chỉ muốn nhanh, hãy đo trước bằng timeline trong DevTools; chi phí thường nằm ở chỗ khác.

---

*Code trong bài được viết và kiểm chứng trên Flutter 3.44 stable — `flutter analyze` sạch, kèm widget test khẳng định chính xác offset của child, kích thước dry layout và kết quả hit test. Cái thang leo và lời khuyên "dừng ở nấc hai" là quan điểm rút ra từ kinh nghiệm, không phải quy tắc do đội Flutter đặt ra. API tầng render có thay đổi giữa các bản lớn (`RenderObject.parent` từng đổi kiểu, dry baseline được thêm sau), nên hãy đối chiếu mọi thứ phụ thuộc phiên bản với api.flutter.dev đúng phiên bản bạn đang dùng.*
