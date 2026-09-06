---
title: "Scroll physics tự viết: khiến danh sách dừng đúng chỗ bạn muốn"
description: "ScrollPhysics là interface nhỏ nhất trong Flutter nhưng điều khiển thứ người dùng cảm nhận rõ nhất. Bốn phương thức quyết định danh sách sẽ snap, nảy, kháng lực hay từ chối fling — và bạn hiếm khi cần override nhiều hơn một."
seoDescription: "Cách ScrollPhysics của Flutter hoạt động: applyPhysicsToUserOffset, applyBoundaryConditions, createBallisticSimulation và tolerance — kèm physics snap hoàn chỉnh, page snapping và mặc định theo nền tảng."
keywords:
  - scrollphysics tuỳ chỉnh flutter
  - flutter danh sách snap
  - createballisticsimulation flutter
  - bouncingscrollphysics clamping flutter
  - flutter scroll spring simulation
  - pagescrollphysics flutter snap
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-26"
emoji: "🎢"
tags: ["Flutter", "Scrolling", "Physics", "Animation", "UI"]
sources:
  - name: "ScrollPhysics — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollPhysics-class.html"
  - name: "ScrollMetrics — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollMetrics-class.html"
  - name: "Simulation — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/physics/Simulation-class.html"
  - name: "ScrollSpringSimulation — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/physics/ScrollSpringSimulation-class.html"
  - name: "PageScrollPhysics — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/PageScrollPhysics-class.html"
  - name: "ScrollConfiguration — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollConfiguration-class.html"
related:
  - slug: "flutter-slivers-custom-scroll"
    title: "Hiểu đúng về sliver: giao thức đứng sau mọi hiệu ứng cuộn trong Flutter"
  - slug: "flutter-gestures-hit-testing"
    title: "Vì sao cú chạm của bạn không ăn: hit testing và đấu trường cử chỉ"
draft: false
---

Cuộn là thao tác người dùng cảm nhận nhiều nhất nhưng mô tả được ít nhất. "Nó rề rà", "nó không dừng ở chỗ tôi tưởng", "trên Android nó nảy sai". Tất cả những lời phàn nàn đó đều trỏ về một lớp nhỏ: `ScrollPhysics`.

Phần lớn lập trình viên Flutter chỉ gặp nó qua ba lớp con có tên sẵn — `BouncingScrollPhysics`, `ClampingScrollPhysics`, `NeverScrollableScrollPhysics`. Bên dưới, đó là một interface gọn với bốn điểm quyết định, và hiểu chúng biến "danh sách dừng ở chỗ kỳ quặc" từ một bí ẩn thành bản sửa hai dòng.

## Lớp này thật sự quyết định điều gì

| Phương thức | Quyết định |
| --- | --- |
| `applyPhysicsToUserOffset` | Chuyển động của ngón tay ánh xạ sang offset cuộn ra sao — độ kháng khi overscroll |
| `applyBoundaryConditions` | Từ chối bao nhiêu phần của offset được yêu cầu khi ở mép |
| `createBallisticSimulation` | Chuyện gì xảy ra sau khi nhấc tay: fling, ổn định, snap, hay không gì cả |
| `tolerance` | Khi nào một simulation được coi là kết thúc |

Cộng thêm hai thuộc tính đáng biết: `shouldAcceptUserOffset` (có kéo được không) và `minFlingVelocity` / `maxFlingVelocity` (thế nào thì tính là fling).

Ba lớp dựng sẵn khác nhau gần như hoàn toàn ở ba phương thức đầu:

- **`ClampingScrollPhysics`** — kiểu Android. `applyBoundaryConditions` từ chối mọi thứ vượt mép, tạo ra điểm dừng cứng cộng với hiệu ứng quầng sáng.
- **`BouncingScrollPhysics`** — kiểu iOS. Điều kiện biên cho phép vượt mép, `applyPhysicsToUserOffset` khiến việc đó ngày càng nặng tay, còn simulation đạn đạo bật ngược lại.
- **`NeverScrollableScrollPhysics`** — `shouldAcceptUserOffset` trả về false. Lưu ý nó chỉ chặn cuộn *của người dùng*; `ScrollController.animateTo` vẫn chạy, đúng thứ bạn cần cho một khung nhìn do chương trình điều khiển.

Bạn nhận lớp nào mặc định là tuỳ nền tảng, thông qua `ScrollConfiguration`. Đó là lý do cùng một đoạn mã cho cảm giác khác nhau trên iOS và Android — và cũng là lý do ép một kiểu cho mọi nơi là một quyết định, không phải một bản sửa lỗi.

## Ghép nối: mẫu `applyTo`

`ScrollPhysics` ghép nối qua một `parent`, và mỗi override đều được kỳ vọng gọi xuyên xuống. Đây là lý do bạn viết physics như một lớp mỏng chứ không phải bản thay thế:

```dart
class SnapScrollPhysics extends ScrollPhysics {
  const SnapScrollPhysics({required this.itemExtent, super.parent});

  final double itemExtent;

  @override
  SnapScrollPhysics applyTo(ScrollPhysics? ancestor) =>
      SnapScrollPhysics(itemExtent: itemExtent, parent: buildParent(ancestor));

  // ...
}
```

Quên `applyTo` là lỗi phổ biến nhất. Không có nó, physics của bạn bị thay thế âm thầm khi framework dựng lại chuỗi — ví dụ khi một `ScrollConfiguration` áp mặc định nền tảng — và tuỳ chỉnh của bạn có vẻ chạy ở chỗ này mà không chạy ở chỗ khác.

Cách dùng thì bình thường:

```dart
ListView.builder(
  physics: const SnapScrollPhysics(itemExtent: 120)
      .applyTo(const BouncingScrollPhysics()),
  itemExtent: 120,
  itemCount: items.length,
  itemBuilder: /* ... */,
)
```

## Một physics snap, đầy đủ

Physics tự viết được hỏi nhiều nhất là "snap vào biên của từng item". Đây là bản đầy đủ, vì các mảnh chỉ có nghĩa khi đứng cùng nhau:

```dart
class SnapScrollPhysics extends ScrollPhysics {
  const SnapScrollPhysics({required this.itemExtent, super.parent});

  final double itemExtent;

  @override
  SnapScrollPhysics applyTo(ScrollPhysics? ancestor) =>
      SnapScrollPhysics(itemExtent: itemExtent, parent: buildParent(ancestor));

  double _snapTarget(ScrollMetrics position, double velocity) {
    // Nơi cú fling sẽ tự nhiên dừng lại, rồi làm tròn về item gần nhất.
    final current = position.pixels;
    final index = (current / itemExtent).round();
    final biased = velocity.abs() < tolerance.velocity
        ? index
        : (velocity > 0 ? index + 1 : index - 1);
    return (biased * itemExtent)
        .clamp(position.minScrollExtent, position.maxScrollExtent);
  }

  @override
  Simulation? createBallisticSimulation(
    ScrollMetrics position,
    double velocity,
  ) {
    // Để parent lo phần overscroll — đừng đánh nhau với hiệu ứng bật lại.
    if (position.outOfRange) {
      return super.createBallisticSimulation(position, velocity);
    }

    final target = _snapTarget(position, velocity);
    if ((target - position.pixels).abs() < tolerance.distance) return null;

    return ScrollSpringSimulation(
      spring,
      position.pixels,
      target,
      velocity,
      tolerance: toleranceFor(position),
    );
  }

  @override
  bool get allowImplicitScrolling => false;
}
```

Ba chi tiết gánh cả đoạn mã này.

**Trả về `null` nghĩa là "dừng ở đây".** Nếu vị trí hiện tại đã nằm trong tolerance so với đích, đừng animate. Trả về một simulation kết thúc ngay lập tức sẽ tạo ra một cú giật nhỏ nhìn thấy được.

**Nhường cho `super` khi `outOfRange`.** Physics cha sở hữu hiệu ứng bật lại. Override nó nghĩa là bạn phải tự viết lò xo bật về từ trạng thái overscroll, và nó sẽ không khớp với nền tảng.

**`ScrollSpringSimulation` mang theo vận tốc đầu vào.** Truyền `velocity` xuyên qua chính là thứ khiến cú fling nhanh cảm thấy nhanh và cú nhả nhẹ cảm thấy nhẹ. Bỏ nó đi — animate tới đích với thời lượng cố định — là lý do snapping tự chế thường cho cảm giác chết cứng.

Với nội dung dạng trang, đừng viết cái này: `PageScrollPhysics` đã snap theo kích thước viewport, và `PageView` dùng nó mặc định.

## Kháng lực và điều kiện biên

Hai phương thức còn lại ít khi cần tới, nhưng khi cần thì không gì thay thế được.

```dart
class ResistantEdgePhysics extends ScrollPhysics {
  const ResistantEdgePhysics({super.parent});

  @override
  ResistantEdgePhysics applyTo(ScrollPhysics? ancestor) =>
      ResistantEdgePhysics(parent: buildParent(ancestor));

  @override
  double applyPhysicsToUserOffset(ScrollMetrics position, double offset) {
    if (position.outOfRange) {
      // Giảm một nửa chuyển động ngón tay khi đã vượt mép.
      return offset * 0.5;
    }
    return super.applyPhysicsToUserOffset(position, offset);
  }

  @override
  double applyBoundaryConditions(ScrollMetrics position, double value) {
    const maxOverscroll = 120.0;
    if (value < position.minScrollExtent - maxOverscroll) {
      return value - (position.minScrollExtent - maxOverscroll);
    }
    if (value > position.maxScrollExtent + maxOverscroll) {
      return value - (position.maxScrollExtent + maxOverscroll);
    }
    return super.applyBoundaryConditions(position, value);
  }
}
```

`applyBoundaryConditions` trả về phần thay đổi bị **từ chối**, không phải phần được cho phép. Trả về `0.0` nghĩa là "cho phép hết". Hiểu ngược chỗ này sẽ tạo ra một danh sách hoàn toàn không cuộn được, và đó là năm phút khó quên.

## Áp physics cho toàn ứng dụng

Để có cảm giác nhất quán toàn app, hãy override `ScrollConfiguration` thay vì truyền `physics:` ở khắp nơi:

```dart
class AppScrollBehavior extends MaterialScrollBehavior {
  @override
  ScrollPhysics getScrollPhysics(BuildContext context) =>
      const BouncingScrollPhysics(parent: AlwaysScrollableScrollPhysics());
}

MaterialApp(
  scrollBehavior: AppScrollBehavior(),
  home: const HomePage(),
);
```

`ScrollBehavior` cũng là nơi bạn điều khiển chỉ báo overscroll, thanh cuộn, và loại thiết bị nhập nào được phép kéo — cái cuối chính là bản sửa cho "ứng dụng desktop của tôi không kéo chuột để cuộn được", vốn là thiết lập `dragDevices` chứ không phải physics.

`AlwaysScrollableScrollPhysics` làm parent cũng đáng biết riêng: nó khiến danh sách cuộn được ngay cả khi nội dung ngắn hơn viewport, và đó là thứ khiến kéo-để-làm-mới hoạt động trên một danh sách gần như trống.

## Kiểm thử

Physics là thứ để cảm nhận chứ không phải để đọc, nhưng phần quan trọng vẫn khẳng định được:

```dart
testWidgets('cú fling dừng đúng biên item', (tester) async {
  await tester.pumpWidget(const SnapList());
  await tester.fling(find.byType(ListView), const Offset(0, -300), 800);
  await tester.pumpAndSettle();

  final position = tester
      .state<ScrollableState>(find.byType(Scrollable))
      .position;
  expect(position.pixels % 120, moreOrLessEquals(0, epsilon: 0.5));
});
```

`pumpAndSettle` chạy simulation tới khi hoàn tất, nên phép khẳng định nằm ở vị trí nghỉ — đúng thứ mà một physics snap hứa hẹn.

## Câu hỏi thường gặp

**Vì sao physics tự viết chạy ở màn hình này mà không chạy ở màn hình khác?**

Gần như luôn là thiếu hoặc sai `applyTo`. Framework dựng lại chuỗi physics ở vài chỗ, và không có `applyTo` thì lớp của bạn bị bỏ rơi.

**Có nên ép hiệu ứng nảy kiểu iOS lên Android không?**

Đó là quyết định sản phẩm, nhưng mặc định khớp nền tảng có lý do: người dùng so danh sách của bạn với mọi danh sách khác trên máy họ. Ép một kiểu duy nhất khiến app nhất quán với chính nó và lệch với nền tảng.

**Làm sao tắt cuộn tạm thời?**

`NeverScrollableScrollPhysics` cho thao tác người dùng trong khi vẫn giữ cuộn qua controller. Nếu bạn cũng muốn chặn cuộn theo chương trình thì đơn giản là đừng gọi cuộn theo chương trình — physics không phải điểm cưỡng chế cho việc đó.

**Vì sao `pumpAndSettle` bị timeout trong test cuộn?**

Thường là một simulation không bao giờ đạt tolerance — lò xo sai tham số, hoặc `createBallisticSimulation` cứ trả về simulation mới. Hãy trả `null` khi đã đủ gần.

**Có thể animate tới vị trí snap bằng controller thay vì viết physics không?**

Có, và cho một lần "snap sau hành động này" thì cách đó đơn giản hơn. Physics tự viết dành cho khi *mọi* lần nhả tay đều phải snap, tức là thuộc tính của khung cuộn chứ không phải của một thao tác.

---

*Interface `ScrollPhysics`, ngữ nghĩa của điều kiện biên, các lớp simulation và điểm móc `ScrollBehavior` mô tả ở đây đều nằm trong tài liệu Flutter API dẫn ở trên. Phần cài đặt snapping, việc nhấn mạnh phải truyền vận tốc xuyên qua, và chẩn đoán rằng một tuỳ chỉnh hỏng thường do thiếu `applyTo` là nhận định riêng của tôi khi viết physics theo cách này. Nội bộ physics thay đổi giữa các bản Flutter — hãy đối chiếu thành viên lớp với SDK của bạn trước khi sao chép.*
