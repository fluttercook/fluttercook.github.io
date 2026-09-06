---
title: "Hiểu đúng về sliver: giao thức đứng sau mọi hiệu ứng cuộn trong Flutter"
description: "Sliver không phải một widget có cái tên lạ — nó là một giao thức layout với constraint và geometry riêng. Hiểu SliverConstraints và SliverGeometry rồi thì header co lại, header dính theo section hay toolbar ghim cứng đều thôi kỳ bí."
seoDescription: "Sliver trong Flutter hoạt động thế nào: CustomScrollView, SliverConstraints, SliverGeometry, SliverPersistentHeader và cách tự viết một RenderSliver."
keywords:
  - sliver trong flutter
  - customscrollview flutter
  - sliverpersistentheader ví dụ
  - sliverconstraints slivergeometry
  - flutter collapsing toolbar
  - tự viết rendersliver flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-09-06"
emoji: "🪟"
tags: ["Flutter", "Slivers", "Scrolling", "Layout", "Performance"]
sources:
  - name: "Flutter — Slivers"
    url: "https://docs.flutter.dev/ui/layout/scrolling/slivers"
  - name: "CustomScrollView — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/CustomScrollView-class.html"
  - name: "SliverConstraints — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/SliverConstraints-class.html"
  - name: "SliverGeometry — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/SliverGeometry-class.html"
  - name: "SliverPersistentHeader — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/SliverPersistentHeader-class.html"
  - name: "RenderSliver — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/rendering/RenderSliver-class.html"
related:
  - slug: "flutter-lists-performance-builder"
    title: "Vì sao ListView của bạn chậm, và bốn cách sửa thật sự có tác dụng"
  - slug: "flutter-custom-renderobject"
    title: "Khi ghép widget không còn đủ: tự viết RenderObject"
draft: false
---

Phần lớn người viết Flutter gặp sliver theo kiểu gặp một cái ổ gà: bản thiết kế đòi một header co lại khi cuộn, tìm ra `SliverAppBar`, dán vào, chạy được, và mô hình trong đầu dừng ở đó. Rồi thiết kế tiếp theo cần header dính **theo từng section**, hoặc một grid biến thành list ở nửa dưới trang, và cái đoạn code đã dán không nói được gì thêm.

Điều đáng hiểu là: sliver không phải một widget đặc biệt. Nó là một **giao thức layout khác**, chạy trong cùng framework. Widget thường hỏi "tôi được phép to cỡ nào?" và trả lời "tôi to chừng này". Sliver hỏi một câu giàu thông tin hơn nhiều — "viewport còn lại bao nhiêu chỗ, tôi đã bị cuộn qua bao xa, phần nhìn thấy của tôi là bao nhiêu?" — và trả về một câu trả lời cũng giàu tương ứng. Khi đọc được hai đối tượng đó, mọi hiệu ứng cuộn trong framework chỉ còn là biến thể nhỏ của cùng một chủ đề.

## Layout kiểu box và layout kiểu sliver

Layout Flutter thông thường là giao thức box: cha truyền xuống `BoxConstraints` (min/max theo chiều rộng và cao), con trả về một `Size`. Hai con số mỗi chiều đi vào, một kích thước đi ra. Đơn giản, và hoàn toàn không mô tả nổi một widget đang bị cuộn mất một phần khỏi đỉnh màn hình.

Sliver thay cả hai vế:

| | Giao thức box | Giao thức sliver |
| --- | --- | --- |
| Ràng buộc | `BoxConstraints` | `SliverConstraints` |
| Kết quả | `Size` | `SliverGeometry` |
| Render object | `RenderBox` | `RenderSliver` |
| Biết về việc cuộn | Không | Có |
| Layout lười được | Chỉ qua viewport | Có sẵn |

Cầu nối giữa hai thế giới là `RenderSliverToBoxAdapter` — đúng thứ mà `SliverToBoxAdapter` bọc lại — cùng các builder lười như `SliverList` và `SliverGrid`, vốn layout con kiểu box theo nhu cầu khi viewport dịch chuyển.

## Sliver được cho biết gì: `SliverConstraints`

`SliverConstraints` có hơn chục trường. Bốn trường mang phần ý tưởng:

```dart
class MyRenderSliver extends RenderSliver {
  @override
  void performLayout() {
    final SliverConstraints c = constraints;

    c.scrollOffset;      // phần đầu của sliver này đã trôi lên trên viewport bao xa
    c.remainingPaintExtent; // viewport còn lại bao nhiêu chỗ nhìn thấy được
    c.overlap;           // các sliver trước đang vẽ đè lên phần đầu của tôi bao nhiêu
    c.precedingScrollExtent; // tổng scroll extent của mọi thứ đứng trước tôi
  }
}
```

`scrollOffset` là trường mở khóa toàn bộ mô hình. Nó **không phải** vị trí cuộn của danh sách. Nó là phần của **chính sliver này** đã trôi khỏi tầm nhìn. Với sliver đầu tiên, nó bằng offset của scroll controller; với sliver thứ năm, nó bằng 0 cho tới khi bạn cuộn qua hết bốn cái trước, rồi mới bắt đầu tăng. Một sliver không bao giờ cần biết nó nằm ở đâu trong danh sách — nó chỉ được cho biết bao nhiêu phần của nó đã mất.

`remainingPaintExtent` là nửa còn lại: khoảng nhìn thấy còn trống bên dưới sliver trước. Khi nó về 0, các sliver sau được yêu cầu layout ra con số 0 — chính là sự lười biếng khiến một danh sách vô hạn vẫn rẻ.

Hai trường nữa có ích trong thực tế. `axisDirection` và `growthDirection` gộp lại thành `c.normalizedGrowthDirection`; hãy dùng `constraints.axis` thay vì mặc định là dọc, nếu không sliver của bạn sẽ vỡ trong một `CustomScrollView` nằm ngang. Còn `cacheOrigin`/`remainingCacheExtent` mô tả dải vô hình phía trên và dưới viewport mà Flutter layout sẵn để cuộn không khựng — mặc định khoảng 250 pixel logic.

## Sliver báo lại gì: `SliverGeometry`

Giá trị trả về mới là chỗ người ta hay sai, vì vài trường nghe như đồng nghĩa mà không phải:

```dart
geometry = SliverGeometry(
  scrollExtent: 300,    // tôi tiêu tốn tổng cộng bao nhiêu quãng cuộn
  paintExtent: 120,     // ngay lúc này tôi đang vẽ vào bao nhiêu phần viewport
  maxPaintExtent: 300,  // paintExtent lớn nhất tôi có thể muốn
  layoutExtent: 120,    // tôi đẩy các sliver sau xuống bao nhiêu
  hasVisualOverflow: false,
);
```

- **`scrollExtent`** là phần đóng góp của sliver vào tổng chiều dài cuộn được. Một header 300 pixel đóng góp 300, dù nó có đang hiện trên màn hình hay không.
- **`paintExtent`** là số pixel của viewport mà nó chiếm **ngay lúc này**. Nó không bao giờ được vượt `remainingPaintExtent`.
- **`layoutExtent`** mặc định bằng `paintExtent`, và là khoảng mà sliver kế tiếp bị đẩy xuống. Đặt nó **nhỏ hơn** `paintExtent` chính là toàn bộ mẹo đằng sau header ghim và header nổi: header vẫn vẽ 56 pixel toolbar trong khi nói với danh sách rằng "tôi chiếm 0 chỗ, cứ đi tiếp".

Sự bất đối xứng đó đáng để ngẫm. Một `SliverAppBar` ghim khi cuộn hết sẽ báo `paintExtent: 56, layoutExtent: 0`. Nó vẫn được vẽ, nhưng nội dung bên dưới hành xử như thể nó không tồn tại — và vì thế trượt vào bên dưới nó.

Những lỗi làm màn hình trắng gần như luôn nằm trong đối tượng này: trả `paintExtent` lớn hơn `remainingPaintExtent`, quên đặt `maxPaintExtent` (làm hỏng scrollbar và hiệu ứng overscroll), hoặc trả `SliverGeometry.zero` ở đúng frame mà sliver đang hiện.

## Trường hợp chiếm 90%: `SliverPersistentHeader`

Rất hiếm khi bạn cần tự viết `RenderSliver`. `SliverPersistentHeader` cho bạn hành vi co-và-ghim qua một delegate nhận đúng con số bạn cần:

```dart
class _SectionHeaderDelegate extends SliverPersistentHeaderDelegate {
  const _SectionHeaderDelegate({required this.title});

  final String title;

  @override
  double get minExtent => 48;

  @override
  double get maxExtent => 140;

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    final t = (shrinkOffset / (maxExtent - minExtent)).clamp(0.0, 1.0);
    return Material(
      elevation: overlapsContent ? 4 : 0,
      color: Color.lerp(
        Theme.of(context).colorScheme.surfaceContainerLow,
        Theme.of(context).colorScheme.surface,
        t,
      ),
      child: Align(
        alignment: Alignment.lerp(
          Alignment.bottomLeft, Alignment.centerLeft, t)!,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            title,
            style: TextStyle.lerp(
              Theme.of(context).textTheme.headlineMedium,
              Theme.of(context).textTheme.titleMedium,
              t,
            ),
          ),
        ),
      ),
    );
  }

  @override
  bool shouldRebuild(_SectionHeaderDelegate old) => old.title != title;
}
```

`shrinkOffset` chạy từ `0` tới `maxExtent - minExtent`. Chuẩn hóa nó về `0..1` và mọi animation bạn muốn đều là một phép `lerp`. `overlapsContent` cho biết nội dung danh sách có đang trượt bên dưới bạn hay không — đây là tín hiệu trung thực để nâng elevation, tốt hơn nhiều so với việc so sánh scroll offset trong một listener.

Rồi ghép lại:

```dart
CustomScrollView(
  slivers: [
    SliverPersistentHeader(
      pinned: true,
      delegate: _SectionHeaderDelegate(title: 'Recipes'),
    ),
    const SliverPadding(
      padding: EdgeInsets.symmetric(horizontal: 16),
      sliver: SliverList.separated(
        // ...
      ),
    ),
  ],
)
```

Chú ý là `SliverPadding` chứ không phải `Padding`. Bên trong `CustomScrollView`, mọi con trực tiếp đều phải nói giao thức sliver; bọc một sliver bằng widget box sẽ ném lỗi lúc layout với thông báo nổi tiếng khó hiểu về việc `RenderSliver` cần cha là `RenderSliver`. Các bản "vị sliver" bạn sẽ dùng tới là `SliverPadding`, `SliverOpacity`, `SliverIgnorePointer`, `SliverAnimatedOpacity`, `SliverSafeArea`, `SliverVisibility`, và `SliverMainAxisGroup` / `SliverCrossAxisGroup` khi cần gom nhóm.

## Header dính theo section, không cần package

Yêu cầu hay gặp — header ghim lại rồi bị header **kế tiếp** đẩy đi — không cần gì hơn một `SliverPersistentHeader` cho mỗi section, tất cả nằm phẳng trong một danh sách:

```dart
CustomScrollView(
  slivers: [
    for (final section in sections) ...[
      SliverPersistentHeader(
        pinned: true,
        delegate: _SectionHeaderDelegate(title: section.title),
      ),
      SliverList.builder(
        itemCount: section.items.length,
        itemBuilder: (context, i) => ItemTile(section.items[i]),
      ),
    ],
  ],
)
```

Phần đẩy đi diễn ra miễn phí. Mỗi header ghim tự kẹp mình ở đỉnh chừng nào `remainingPaintExtent` còn cho phép, và khi header kế tiếp tới nơi, nó chiếm chỗ và ép cái trước ra ngoài. Không có sự phối hợp nào giữa chúng, và không có scroll listener nào cả.

## Khi nào thì thật sự tự viết `RenderSliver`

Trường hợp đáng làm là một sliver có geometry không phải hàm của một extent duy nhất — một dải parallax, một sliver chỉ lộ ra sau một ngưỡng, một header đổi kích thước theo chính nội dung nó vẽ. Bộ khung:

```dart
class RenderFadeAwaySliver extends RenderSliverSingleBoxAdapter {
  RenderFadeAwaySliver({RenderBox? child}) : super(child: child);

  @override
  void performLayout() {
    if (child == null) {
      geometry = SliverGeometry.zero;
      return;
    }

    child!.layout(constraints.asBoxConstraints(), parentUsesSize: true);
    final double childExtent = switch (constraints.axis) {
      Axis.vertical => child!.size.height,
      Axis.horizontal => child!.size.width,
    };

    final double paintedChildSize =
        calculatePaintOffset(constraints, from: 0, to: childExtent);
    final double cacheExtent =
        calculateCacheOffset(constraints, from: 0, to: childExtent);

    geometry = SliverGeometry(
      scrollExtent: childExtent,
      paintExtent: paintedChildSize,
      cacheExtent: cacheExtent,
      maxPaintExtent: childExtent,
      hitTestExtent: paintedChildSize,
      hasVisualOverflow: childExtent > constraints.remainingPaintExtent ||
          constraints.scrollOffset > 0,
    );

    setChildParentData(child!, constraints, geometry!);
  }

  @override
  void paint(PaintingContext context, Offset offset) {
    if (child == null || geometry!.visible == false) return;
    final double t =
        (constraints.scrollOffset / geometry!.scrollExtent).clamp(0.0, 1.0);
    context.pushOpacity(
      offset, ((1 - t) * 255).round(), (ctx, o) => ctx.paintChild(child!, o));
  }
}
```

Hai hàm trợ giúp đáng đồng tiền. `calculatePaintOffset` tính xem trong khoảng `from..to` hiện có bao nhiêu phần đang nhìn thấy, dựa trên `scrollOffset` và `remainingPaintExtent`; `calculateCacheOffset` làm việc tương tự cho dải cache. Tự viết hai thứ đó là nơi các lỗi lệch một pixel sinh sống — hãy dùng chúng.

`hitTestExtent` rất dễ quên và sinh ra một lỗi cực khó hiểu: sliver hiện rõ nhưng bỏ qua thao tác chạm ở vùng đã cuộn qua. Hãy đặt nó cùng lúc với `paintExtent`.

## Vài ghi chú hiệu năng thật sự làm đổi con số

Sliver khiến sự lười biếng trở nên khả thi; nó không bắt buộc điều đó.

- **`SliverList` và `SliverList.builder`.** Constructor mặc định với `SliverChildListDelegate` dựng mọi con ngay lập tức, y hệt một `Column`. Chỉ dạng builder mới lười. `SliverGrid` cũng vậy.
- **`addAutomaticKeepAlives`.** Bật sẵn, nghĩa là một con có `AutomaticKeepAliveClientMixin` — kể cả bất cứ thứ gì chứa `TextField` — sẽ không bao giờ bị hủy khi cuộn khuất. Cố ý thì tốt cho trạng thái form; đắt đỏ nếu điều đó xảy ra với hàng trăm dòng.
- **`cacheExtent`.** Tăng nó trên `CustomScrollView` là đánh đổi bộ nhớ và thời gian build lấy độ mượt khi cuộn nhanh. Đây là một trong số ít núm vặn mà đo trước–sau trong DevTools cho câu trả lời rõ ràng.
- **Lồng scroll view.** Một `ListView` đặt trong `SliverToBoxAdapter` buộc danh sách bên trong hoặc không giới hạn, hoặc shrink-wrap — mà shrink-wrap thì layout toàn bộ con. Hãy trải phẳng thành các sliver anh em; `SliverMainAxisGroup` sinh ra để làm việc đó.

## Câu hỏi thường gặp

**Vì sao widget của tôi báo "A RenderSliver expected a RenderSliver child"?**

Bạn đặt một widget box thẳng vào danh sách `slivers:`, hoặc đặt một sliver thẳng vào trong widget box. Hãy bọc nội dung box bằng `SliverToBoxAdapter`, và dùng bản có tiền tố `Sliver` cho các wrapper như `Padding` hay `Opacity`.

**`pinned` và `floating` trên header khác nhau chỗ nào?**

`pinned` giữ lại `minExtent` pixel trên màn hình dù bạn cuộn xuống bao xa. `floating` mang header trở lại ngay khi bạn cuộn **lên**, không cần về tận đầu trang. Hai cái kết hợp được, và với `snap: true` thì việc quay lại là một animation thay vì bám theo ngón tay.

**Có bắt buộc dùng `CustomScrollView` mới xài được sliver không?**

`ListView` và `GridView` vốn đã là lớp bọc mỏng quanh một `CustomScrollView` với đúng một sliver. Bạn cần dạng tường minh ngay khi muốn hai loại sliver khác nhau trong cùng một scroll view — cũng là lúc các lớp bọc hết còn đáng dùng.

**Vì sao scrollbar của tôi sai kích thước?**

Gần như luôn là `maxPaintExtent` không phản ánh đúng cực đại thật của sliver, hoặc `scrollExtent` thay đổi mỗi frame. Scrollbar được tính từ tổng geometry, nên một sliver thiếu nhất quán sẽ lộ ra ở đó đầu tiên.

**Sliver có nằm ngang được không?**

Được — đặt `scrollDirection: Axis.horizontal` trên `CustomScrollView`. Sliver tự viết phải đọc `constraints.axis` thay vì mặc định là dọc, và không được viết cứng `size.height`.

---

*Phần chi tiết giao thức trong bài lấy từ tài liệu framework Flutter và mã nguồn thư viện `rendering` đã dẫn ở trên. Các đánh giá — khi nào đáng tự viết `RenderSliver`, và núm vặn hiệu năng nào đáng đo — là quan điểm của tôi. API sliver khá ổn định nhưng lớp widget bọc ngoài thường xuyên có thành viên mới; hãy đối chiếu tài liệu API của đúng SDK bạn đang ship.*
